# Bouračka UI — instalace na SUPIN server (from zero)

**Verze.** v0.1.4 (2026-05-13).
**Pro.** SUPIN ops kolega instalující bouracka-ui na server uvnitř SUPIN infrastruktury (Windows Server / Linux RHEL).
**Časová náročnost.** ~30 minut + příprava serveru (závisí na SUPIN politikách).
**Cílový stav.** bouracka-ui běží jako služba/daemon na serveru, dostupný více testerům přes SUPIN-internal síť.

---

## §1. Předpoklady ze strany SUPIN IT

| Co potřebujeme | Standardní hodnoty / pozn. |
|----------------|----------------------------|
| Server s Windows Server 2019+ NEBO RHEL 8+ / Ubuntu 22.04+ | jeden VM stačí; multi-tester ~3-5 souběžných readů, max 1-2 zapisující |
| Python 3.10 / 3.11 / 3.12 (jedno z) | předem nainstalovaný systemový Python; ne Microsoft Store edice |
| Node.js 20+ LTS | pro npx → cypress + playwright; `node --version` musí vrátit 20.x+; service account musí mít přístup k npm cache |
| selenium python (`pip install selenium`) | selenium webdriver; ověř `python -c "import selenium"` pod service accountem |
| Síťová dostupnost ze stran testerů (HP Elite) na server | TCP port 8424 (bouracka-ui native port) nebo 443/80 přes reverse proxy |
| Síťová dostupnost ze serveru na test-target prostředí | `demo.bouracka.cz` veřejně; `tst.demo.bouracka.cz`, `tst.bouracka.cz` SUPIN-internal; SUPIN VPN nepotřebné pokud server JE uvnitř SUPIN |
| Síťová dostupnost ze serveru na RDS.INT-CKP.CZ (pro budoucí Oracle DWH integraci) | 172.16.1.104:1521; relevantní jen po Phase 4 DWH dev planu |
| Service account (Windows) nebo systemd user (Linux) pod kterým bouracka-ui poběží | navrhuji `bouracka-svc` nebo `bouracka` |
| Read+write přístup do data adresáře (workbook + runs/) | `C:\bouracka\` resp. `/var/lib/bouracka/` |
| Firewall pravidlo umožňující inbound TCP na zvoleném portu | per SUPIN security policy |
| Optional: TLS certifikát pro https | per SUPIN-CA; přes reverse proxy (nginx / IIS / Apache) |

---

## §2. Architektura instalace

```
                  ┌─────────────────────────────────────────────────────┐
                  │            SUPIN-internal síť                       │
                  │                                                     │
   Tester HP      │    ┌─────────────────┐         ┌────────────────┐  │
   Elite (Kate    │    │ SUPIN server    │         │ test-target    │  │
   etc.)          │    │                 │         │  - demo        │  │
        │         │    │ bouracka-ui     │ HTTPS   │  - tst.demo    │  │
        ├─SUPIN───┤    │ FastAPI :8424   │ ◄─────► │  - tst         │  │
        │ VPN     │    │ python venv     │         │                │  │
        │ TCP     │    │ workbook XLSX   │         └────────────────┘  │
        └─https───┼──► │ runs/ JSONs     │                              │
                  │    │                 │                              │
                  │    │ (reverse proxy: │                              │
                  │    │  nginx/IIS/Apache│                             │
                  │    │  TLS termination)│                             │
                  │    └─────────────────┘                              │
                  │                                                     │
                  └─────────────────────────────────────────────────────┘
```

**Pozn.** v0.1.x je single-tenant — všichni testeři sdílí jeden FastAPI proces + jeden workbook. Multi-tenant + auth + per-user write konflikty jsou plánováno na v0.2+ při Oracle migraci (viz `_config/BOURACKA-DATA-STORE-EVOLUTION-PLAN-v0.1-EN.md`).

---

## §3. Instalace — Windows Server

### §3.1 Stáhni instalační balíček

Z mé sdílené Google Drive složky `bouracka-ui-v0.1.4-SUPIN-server`:

| Soubor | Velikost | Účel |
|--------|----------|------|
| `bouracka-ui-hp-elite-v0.1.4-CS-py310.zip` (nebo py311/py312 dle Python verze na serveru) | ~6 MB | UI balíček s wheelhouse |
| `bouracka-tests-source-v0.5.6.zip` | ~1.3 MB | test-suite zdroj (cypress/playwright/selenium kód) |
| `SHA256SUMS.txt` | ~1 KB | kontrolní součty |
| `MANIFEST-KATE-DROP-2026-05-13.txt` | ~3 KB | metainfo |

Ověř SHA256.

### §3.2 Pre-flight kontroly

```powershell
# Python verze (jedna ze tří podporovaných)
python --version

# Místo na disku — minimum 2 GB volných pro venv + wheelhouse + runs/ + workbook
Get-PSDrive C | Select Used, Free

# Dostupnost test-target endpointů ze serveru
Test-NetConnection demo.bouracka.cz -Port 443 -InformationLevel Quiet     # public
Test-NetConnection tst.demo.bouracka.cz -Port 443 -InformationLevel Quiet # SUPIN-internal
Test-NetConnection tst.bouracka.cz -Port 443 -InformationLevel Quiet      # SUPIN-internal

# Příští kolo: dostupnost na Oracle RDS pro budoucí DWH integraci
Test-NetConnection 172.16.1.104 -Port 1521 -InformationLevel Quiet
```

Všechny relevantní `True`. Pokud `tst.demo` / `tst` ze serveru nedostupné, kontaktuj SUPIN IT — server musí mít přístup do testovacích podsítí.

### §3.3 Vytvoř install adresář + service account

```powershell
# Adresářová struktura
New-Item -ItemType Directory C:\bouracka -Force | Out-Null
New-Item -ItemType Directory C:\bouracka\app -Force | Out-Null
New-Item -ItemType Directory C:\bouracka\data -Force | Out-Null
New-Item -ItemType Directory C:\bouracka\logs -Force | Out-Null
New-Item -ItemType Directory C:\bouracka\backup -Force | Out-Null

# Service account (per SUPIN policy)
# Buď: AD service account `SUPIN\bouracka-svc`
# Nebo: lokální Windows user `.\bouracka-svc` (PowerShell jako Admin):
# New-LocalUser -Name bouracka-svc -NoPassword -AccountNeverExpires
# Add-LocalGroupMember -Group "Log on as a service" -Member bouracka-svc

# Nastav ACL — service account vlastní C:\bouracka\
icacls C:\bouracka /grant "bouracka-svc:(OI)(CI)F" /T
```

### §3.4 Rozbal UI + test-suite

```powershell
cd C:\bouracka\app
Expand-Archive C:\Downloads\bouracka-ui-hp-elite-v0.1.4-CS-py310.zip . -Force
Expand-Archive C:\Downloads\bouracka-tests-source-v0.5.6.zip .\tests-source -Force

# Workbook PŘESUŇ z app rootu do dedikovaného data adresáře
Move-Item C:\bouracka\app\BOURACKA-TESTPLAN-v0.4.3.xlsx C:\bouracka\data\BOURACKA-TESTPLAN-v0.4.3.xlsx

# Ověř že workbook je jen na jednom místě (BUG-K-003 prevence)
Get-ChildItem -Recurse C:\bouracka -Filter "BOURACKA-TESTPLAN-*.xlsx"
# Očekávané: jen C:\bouracka\data\BOURACKA-TESTPLAN-v0.4.3.xlsx
```

### §3.5 Vytvoř Python venv + nainstaluj bouracka-ui

```powershell
cd C:\bouracka\app
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --no-index --find-links="C:\bouracka\app\wheelhouse" "C:\bouracka\app\bouracka_ui-0.1.4-py3-none-any.whl"

# Smoke check
bouracka-ui --help
```

### §3.6 Vytvoř service-startup config

`C:\bouracka\app\service-config.ps1`:

```powershell
# bouracka-ui service config
# Loaded by NSSM / Task Scheduler / SrvAny wrapper

$env:BOURACKA_UI_WORKBOOK = "C:\bouracka\data\BOURACKA-TESTPLAN-v0.4.3.xlsx"
$env:BOURACKA_UI_RUNS_DIR = "C:\bouracka\data\runs"
$env:BOURACKA_UI_REPO_ROOT = "C:\bouracka\app\tests-source"
$env:BOURACKA_UI_DISPATCH_MODE = "real"   # change to "mock" pro initial smoke

# Run bouracka-ui bound na všechny rozhraní (server sdílí přes LAN)
C:\bouracka\app\.venv\Scripts\bouracka-ui.exe `
    --host 0.0.0.0 `
    --port 8424 `
    --no-browser
```

### §3.7 Nainstaluj jako Windows service (NSSM doporučený)

```powershell
# Stáhni NSSM z https://nssm.cc/release/nssm-2.24.zip
# Rozbal nssm.exe do C:\bouracka\app\

cd C:\bouracka\app
.\nssm.exe install bouracka-ui PowerShell.exe `
    "-ExecutionPolicy Bypass -NoProfile -File C:\bouracka\app\service-config.ps1"
.\nssm.exe set bouracka-ui ObjectName .\bouracka-svc
.\nssm.exe set bouracka-ui AppDirectory C:\bouracka\app
.\nssm.exe set bouracka-ui Start SERVICE_AUTO_START
.\nssm.exe set bouracka-ui AppStdout C:\bouracka\logs\bouracka-ui.stdout.log
.\nssm.exe set bouracka-ui AppStderr C:\bouracka\logs\bouracka-ui.stderr.log
.\nssm.exe set bouracka-ui AppRotateFiles 1
.\nssm.exe set bouracka-ui AppRotateBytes 10485760    # 10 MB rotation
.\nssm.exe set bouracka-ui Description "Bouracka UI v0.1.4 - test cockpit"

# Start
Start-Service bouracka-ui
Get-Service bouracka-ui
```

### §3.8 Firewall pravidlo

```powershell
# Allow inbound TCP 8424 from SUPIN-internal subnet (172.16.0.0/12 typical SUPIN range; ověř s SUPIN IT)
New-NetFirewallRule `
    -DisplayName "Bouracka UI HTTP" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 8424 `
    -Action Allow `
    -Profile Domain `
    -RemoteAddress 172.16.0.0/12,10.0.0.0/8
```

### §3.9 Reverse proxy + TLS (volitelně ale doporučeno)

Pokud IIS je standard SUPIN reverse proxy:

```
Site: bouracka.supin.local (požádej DNS o A-záznam)
Binding: HTTPS :443 (certifikát ze SUPIN CA)
URL Rewrite → http://localhost:8424
```

Pokud nginx:

```nginx
server {
    listen 443 ssl;
    server_name bouracka.supin.local;
    ssl_certificate /etc/nginx/certs/bouracka.crt;
    ssl_certificate_key /etc/nginx/certs/bouracka.key;
    location / {
        proxy_pass http://127.0.0.1:8424;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
        # SSE pro live log streaming
        proxy_buffering off;
        proxy_read_timeout 300s;
    }
}
```

---

## §4. Instalace — Linux RHEL 8+ / Ubuntu 22.04+

### §4.1 Předpoklady

```bash
# Python 3.10 nebo novější
python3 --version

# pip + venv
sudo dnf install python3-pip python3-venv  # RHEL
sudo apt install python3-pip python3-venv  # Ubuntu

# git (pro budoucí update)
sudo dnf install git  # nebo apt
```

### §4.2 Service user + adresáře

```bash
sudo useradd --system --home /var/lib/bouracka --shell /bin/bash bouracka
sudo mkdir -p /var/lib/bouracka/{app,data,logs,backup}
sudo chown -R bouracka:bouracka /var/lib/bouracka
sudo chmod 750 /var/lib/bouracka
```

### §4.3 Rozbal balíčky

```bash
cd /tmp
unzip ~/Downloads/bouracka-ui-hp-elite-v0.1.4-CS-py310.zip -d bouracka-ui
unzip ~/Downloads/bouracka-tests-source-v0.5.6.zip        -d bouracka-tests
sudo mv bouracka-ui/*           /var/lib/bouracka/app/
sudo mv bouracka-tests          /var/lib/bouracka/app/tests-source/
sudo mv /var/lib/bouracka/app/BOURACKA-TESTPLAN-v0.4.3.xlsx /var/lib/bouracka/data/
sudo chown -R bouracka:bouracka /var/lib/bouracka

# Ověř single-workbook (BUG-K-003 fix)
find /var/lib/bouracka -name "BOURACKA-TESTPLAN-*.xlsx"
# Očekávané: jen /var/lib/bouracka/data/BOURACKA-TESTPLAN-v0.4.3.xlsx
```

### §4.4 Venv + install

```bash
sudo -u bouracka bash -c '
    cd /var/lib/bouracka/app
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --no-index --find-links=/var/lib/bouracka/app/wheelhouse \
        /var/lib/bouracka/app/bouracka_ui-0.1.4-py3-none-any.whl
    bouracka-ui --help
'
```

### §4.5 Systemd unit

`/etc/systemd/system/bouracka-ui.service`:

```ini
[Unit]
Description=Bouracka UI v0.1.4 - test cockpit
After=network.target

[Service]
Type=simple
User=bouracka
Group=bouracka
WorkingDirectory=/var/lib/bouracka/app
Environment="BOURACKA_UI_WORKBOOK=/var/lib/bouracka/data/BOURACKA-TESTPLAN-v0.4.3.xlsx"
Environment="BOURACKA_UI_RUNS_DIR=/var/lib/bouracka/data/runs"
Environment="BOURACKA_UI_REPO_ROOT=/var/lib/bouracka/app/tests-source"
Environment="BOURACKA_UI_DISPATCH_MODE=real"
ExecStart=/var/lib/bouracka/app/.venv/bin/bouracka-ui --host 0.0.0.0 --port 8424 --no-browser
Restart=on-failure
RestartSec=10s
StandardOutput=append:/var/lib/bouracka/logs/stdout.log
StandardError=append:/var/lib/bouracka/logs/stderr.log

# Hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/var/lib/bouracka

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable bouracka-ui
sudo systemctl start bouracka-ui
sudo systemctl status bouracka-ui
sudo journalctl -u bouracka-ui -f   # live log tail
```

### §4.6 Firewall (firewalld / ufw)

```bash
# RHEL firewalld
sudo firewall-cmd --permanent --add-port=8424/tcp
sudo firewall-cmd --reload

# Ubuntu ufw
sudo ufw allow from 172.16.0.0/12 to any port 8424
sudo ufw reload
```

### §4.7 Reverse proxy + TLS (volitelně)

Stejný nginx pattern jako v §3.9.

---

## §5. Verifikace instalace (Windows i Linux)

```bash
# Z testerského HP Elite na SUPIN VPN
curl -k https://bouracka.supin.local/api/health
# Nebo přímo:
curl http://<server-ip>:8424/api/health

# Očekávaná odpověď:
# {
#   "server_version": "0.1.4",
#   "schema_version": "1.0",
#   "workbook_path": "/var/lib/bouracka/data/BOURACKA-TESTPLAN-v0.4.3.xlsx",
#   "workbook_exists": true,
#   "runs_dir": "/var/lib/bouracka/data/runs",
#   "runs_dir_exists": true,
#   "tools": { "python": true, "npx": true, "consolidate_results": true }
# }
```

## §6. Bezpečnostní pozn.

- **bouracka-ui v0.1.x nemá auth** — kdokoli na síti kdo dosáhne port 8424 / proxy URL může číst+psát testy a bugy. Multi-tester použití OK uvnitř SUPIN-internal sítě (důvěryhodná zóna), ale NEexponovat na public internet.
- **workbook obsahuje testovací data + bug repository** — citlivost dle SUPIN klasifikace (LOW pro Bouračka; HIGH pro budoucí MI-M-T projekty).
- **HTTPS doporučeno** pokud cesta tester→server prochází přes router/switch infrastrukturu.
- **Audit log** stdout/stderr/journal — zachová které IP-tester dělal jaký /api/runs POST. Pro forenzní analýzu.

## §7. Update na novější verzi

Postup minimal-downtime update:

```bash
# Linux
sudo systemctl stop bouracka-ui

cd /var/lib/bouracka/app
sudo -u bouracka rm -rf .venv wheelhouse bouracka_ui-*.whl
unzip /tmp/bouracka-ui-hp-elite-vX.Y.Z-CS-py310.zip -d /tmp/new-ui
sudo cp /tmp/new-ui/* /var/lib/bouracka/app/
sudo chown -R bouracka:bouracka /var/lib/bouracka/app

sudo -u bouracka bash -c '
    cd /var/lib/bouracka/app
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --no-index --find-links=wheelhouse bouracka_ui-*.whl
'

sudo systemctl start bouracka-ui
```

Test-suite source updaty stejně do `/var/lib/bouracka/app/tests-source/` (přepsat).

Workbook NIKDY nepřepisovat — jen migrovat dle release notes (`CHANGELOG.md`).

## §8. Kontakt

Pete Y. (`petr.yamyang@gmail.com`).

---

End of SUPIN server install runbook v0.1.4.
