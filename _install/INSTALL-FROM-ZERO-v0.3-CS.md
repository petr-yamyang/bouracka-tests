# Bouračka Test Suite — Instalace od nuly — v0.3 CS

> **Audience.** První operátor / SecOps / DevOps, který spouští tento balíček
> na **čistém** Windows 11 notebooku (ThinkPad) s dočasným administrátorským
> oprávněním. Předpokládá se Profile-C: nepodnikový stroj s povolenou
> instalací software.
>
> **Cíl.** Po dokončení této příručky:
> - máte nainstalovaný kompletní ekosystém (Python + Node + Java/JRE pro PlantUML)
> - máte zprovozněnou Playwright (primární framework)
> - máte volitelně připravenou Cypress + TestCafe (CP-SUPIN-05)
> - umíte spustit `bring-up smoke` test (TC-CP-001) proti DEMO
> - umíte spustit intel-probes (TC-CP-INTEL-*) pro obohacení artefaktů
>
> **Doba instalace:** ~30 minut čistého času (z toho ~10 minut čekání na stahování).

---

## §1. Předpoklady

| Položka | Verze | Poznámka |
|---------|-------|----------|
| Windows | 10/11 | testováno na 11 24H2 |
| Administrátor | dočasně | nutný pro `winget` instalaci |
| Disk free | ≥ 5 GB | Playwright Chromium je objemný |
| Internetový přístup | běžný | povolené domény: `*.npmjs.com`, `pypi.org`, `github.com`, `playwright.download.prss.microsoft.com`, `cdn.playwright.dev` |

> **Pokud SecOps blokuje** některé domény, otevřete ticket s allowlist
> seznamem (viz `_install/SECOPS-ALLOWLIST.md` — pokud existuje, nebo
> sestavte z této příručky).

## §2. Instalace runtime — Profile-C (admin window)

### §2.1 Python 3.10+

```pwsh
# Otevřete PowerShell jako administrátor
winget install Python.Python.3.12

# Verifikace (nový PS terminál po instalaci)
python --version          # očekáváno: Python 3.12.x

# Instalace openpyxl pro práci s Excel
pip install openpyxl --break-system-packages
```

### §2.2 Node.js 20 LTS

```pwsh
winget install OpenJS.NodeJS.LTS

# Verifikace
node --version            # očekáváno: v20.x.x
npm --version             # očekáváno: 10.x.x
```

### §2.3 Java JRE 21 (pro PlantUML — volitelné)

```pwsh
winget install Microsoft.OpenJDK.21

# Verifikace
java --version            # očekáváno: openjdk 21.x

# Stáhnout PlantUML jar
$tools = "$env:USERPROFILE\tools"
New-Item -ItemType Directory -Force -Path $tools | Out-Null
Invoke-WebRequest 'https://github.com/plantuml/plantuml/releases/download/v1.2024.7/plantuml-1.2024.7.jar' -OutFile "$tools\plantuml.jar"
```

> Pokud JRE neinstalujete, fallback na Mermaid renderer (mermaid-cli)
> přes `npm install -g @mermaid-js/mermaid-cli` a převést `.puml` zdroje
> ručně do `.mmd`. Plný PlantUML doporučujeme.

### §2.4 (Volitelné) Mockoon CLI pro N8 SMS Gateway mock

```pwsh
npm install -g @mockoon/cli

# Verifikace
mockoon-cli --version
```

## §3. Rozbalení balíčku

```pwsh
# 1. Stáhněte soubory z e-mailu (ZIP volumes do jedné složky)
# 2. Spojte volumes (pokud bylo více částí):
$dir = "C:\bouracka-tests"
mkdir $dir
# Postupně rozbalte VŠECHNY ZIP části do $dir
# (PowerShell nebo 7-Zip funguje stejně)

cd $dir
```

> **Verifikace SHA256.** Pro každý ZIP volume v balíčku je v `MANIFEST-CS.md`
> kontrolní součet. Po rozbalení:
>
> ```pwsh
> Get-FileHash <soubor>.zip -Algorithm SHA256
> ```

## §4. Příprava UTF-8 BOM pro PowerShell skripty

Důležité: PowerShell 5.1 čte BOM-less UTF-8 jako Windows-1252, což láme
české znaky a em-dashe. Skripty v balíčku jsou s BOM, ale po editaci
v některých editorech se může BOM ztratit. Verifikace:

```pwsh
$bomCheck = [System.IO.File]::ReadAllBytes("scripts\run-bring-up-smoke.ps1")[0..2]
if ($bomCheck[0] -eq 0xEF -and $bomCheck[1] -eq 0xBB -and $bomCheck[2] -eq 0xBF) {
    "[ok] BOM přítomen"
} else {
    "[fail] BOM chybí — připojte ručně:"
    "  `$content = [System.IO.File]::ReadAllText('scripts\run-bring-up-smoke.ps1')"
    "  [System.IO.File]::WriteAllText('scripts\run-bring-up-smoke.ps1', `$content, [System.Text.UTF8Encoding]::new(`$true))"
}
```

## §5. Instalace Playwright + Chromium

```pwsh
cd $dir\bouracka-tests   # tam, kde je package.json
npm install              # ~2 minuty
npx playwright install chromium  # ~3 minuty (stahuje ~150 MB)

# Verifikace
npx playwright --version  # očekáváno: Version 1.x.x
```

## §6. (Volitelné) Cypress + TestCafe

Pokud chcete být připraveni na CP-SUPIN-05 multi-framework srovnání:

```pwsh
npm install --save-dev cypress testcafe
npx cypress verify
npx testcafe --version
```

## §7. První spuštění — bring-up smoke

```pwsh
cd $dir\bouracka-tests

# Bring-up smoke (TC-CP-001) proti veřejné DEMO Bouračce
.\scripts\run-bring-up-smoke.ps1

# Nebo přímo Playwright:
npx playwright test playwright/tests/bring-up-smoke.spec.ts --project=chromium-mobile
```

**Očekávaný výstup:**
- 1 test passed (rozcestník + reCAPTCHA badge + CTA "VYPLNIT ZÁZNAM")
- Report v `playwright-report/`
- Screenshoty v `test-results/`

> Pokud test selže s `net::ERR_*`, zkontrolujte:
> - `BOURACKA_BASE` env var (default `https://demo.bouracka.cz`)
> - Síťovou dostupnost: `Test-NetConnection demo.bouracka.cz -Port 443`
> - SecOps proxy: `npm config get proxy`

## §8. Spuštění intel-probes (CP-SUPIN-04 STEP 14)

Tyto testy obohacují artefaktovou sadu reálnými daty z DEMO:

```pwsh
# Read-only probes (žádné zápisy do SUT)
npx playwright test playwright/tests/intel-probes/01-enumeration-dump.spec.ts

# Detail viz playwright/tests/intel-probes/README-OPERATOR.md

# Opt-in (vytváří 1 report UUID; data se purgují)
$env:INTEL_PROBE_CREATE_REPORT = "1"
npx playwright test playwright/tests/intel-probes/02-codelist-scrape.spec.ts
$env:INTEL_PROBE_CREATE_REPORT = ""
```

**Očekávaný výstup:**
- `fixtures/intel-2026-MM-DD/enums/{insuranceCompanies,vehicleBrands}.json` — plné payloady
- `fixtures/intel-2026-MM-DD/bundles/bundle-findings.json` — Zod schéma + regex hits + CS copy strings
- `fixtures/intel-2026-MM-DD/traces/rozcestnik.json` — síťový trace pro rozcestník
- `fixtures/intel-2026-MM-DD/codelists-from-dom/license-categories.json` — DOM-scrape číselníku ŘP

## §9. Spuštění validace test-planu

```pwsh
# Validátor sešitu (10 kontrol)
python tools/validate_workbook.py BOURACKA-TESTPLAN-v0.3.xlsx

# Očekávaný výstup: 10/10 ✓
```

## §10. Spuštění render-uml (PlantUML → PNG + SVG)

```pwsh
# Renderování všech UML v jedné flow složce
.\tools\render-uml.ps1 -FlowFolder recon\screenflows-live\flow-A1-main-tst-demo

# Generuje PNG + SVG vedle .puml zdrojů
```

## §11. Mockoon profil pro N8 SMS Gateway (pro PROD testování)

```pwsh
# Nastartovat mock server
mockoon-cli start --data mockoon\n8-sms-gateway.json --port 3001

# V druhém terminálu:
$env:N8_BASE = "http://localhost:3001"
npx playwright test playwright/tests/core-flow.spec.ts --project=chromium-mobile
```

## §12. Diagnostické skripty

| Skript | Co dělá |
|--------|---------|
| `scripts/setup-from-zero.ps1` | rychlá one-shot instalace (volá kroky §2 + §5) |
| `scripts/validate-install.ps1` | 14 zdravotních kontrol prostředí |
| `scripts/run-all.ps1` | Playwright + Cypress + TestCafe (po instalaci) |
| `tools/test-console.ps1 status` | reportuje, jaké frameworky jsou aktuálně runnable |

## §13. Co dělat, když něco selže

| Symptom | Pravděpodobná příčina | Řešení |
|---------|------------------------|---------|
| `python: command not found` | Microsoft Store stub | viz §13.1 níže — KLASICKÝ PROBLÉM |
| `python --version` po `winget install` stále hlásí "not found" | App Execution Aliases stuby na PATH před winget Pythonem | viz §13.1 |
| `npm install` 401 | korporátní proxy | `npm config set proxy http://proxy:port` |
| Playwright: `Failed to download Chromium` | firewall blokuje `*.playwright.dev` | otevřete SecOps ticket; allowlist |
| PS skript: `nelze načíst, není digitálně podepsaný` | ExecutionPolicy | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` (admin shell) |
| Mojibake (`Â`) v PS výstupu | BOM-less UTF-8 | viz §4 |
| `tools/render-uml.ps1`: PlantUML chybí | JRE / jar | viz §2.3 |
| `winget install ...` "Failed when opening source(s)" | winget cache / source registr | `winget source reset --force` (admin shell) → retry |

### §13.1 KLASICKÝ PROBLÉM — Python "not found" po úspěšné winget instalaci

**Symptom:** Po úspěšném `winget install Python.Python.3.12` (vidíte
"Successfully installed") stále:

```
PS> python --version
Python was not found; run without arguments to install from the Microsoft Store
```

**Příčina:** Windows 10/11 má v `%LOCALAPPDATA%\Microsoft\WindowsApps\`
**stub binárky** `python.exe` + `python3.exe`, které redirect uživatele
do Microsoft Store. Tyto stuby jsou na PATH **PŘED** winget Pythonem
(který je v `%LOCALAPPDATA%\Programs\Python\Python312\`), takže kliknutí
na `python` stále aktivuje stub.

**Tři opravy — zkuste v tomto pořadí:**

#### Oprava 1 (rychlá, bez nutnosti změnit PATH): použijte `py` launcher

Winget Python install obsahuje `py.exe` — oficiální Python Launcher pro
Windows, který stub obchází:

```pwsh
py --version              # mělo by tisknout: Python 3.12.10
py -3.12 --version
py -m pip install openpyxl --break-system-packages
```

Pro skripty Bouračky: nahraďte `python` za `py`:

```pwsh
py tools\validate_workbook.py
py tools\check_priority_matrix.py BOURACKA-TESTPLAN-v0.4.0.xlsx
py tools\bump_workbook_version.py
py tools\fix_priority_matrix.py
```

Volitelně přidat alias do PowerShell profilu:

```pwsh
notepad $PROFILE
# Vložte:
Set-Alias -Name python -Value py -Scope Global
Set-Alias -Name python3 -Value py -Scope Global
```

#### Oprava 2 (nejčistší, jednorázová): vypněte App Execution Aliases

1. Stiskněte <kbd>Win</kbd> → napište **"Manage app execution aliases"** → Enter
2. Najděte řádek **"App Installer — python.exe"** → přepnout na **OFF**
3. Najděte řádek **"App Installer — python3.exe"** → přepnout na **OFF**
4. Zavřete PowerShell + otevřete nový
5. `python --version` → nyní by mělo zobrazit `Python 3.12.10`

Tato oprava je dlouhodobá; po ní funguje `python` přímo.

#### Oprava 3 (pokud 1+2 nepomohly): manuálně přidat na PATH

```pwsh
# 1. Ověřte, kam winget Python instaloval
$pyDir = "$env:LOCALAPPDATA\Programs\Python\Python312"
Test-Path "$pyDir\python.exe"   # mělo by tisknout: True

# 2. Přidat na PATH (user-level, persistuje mezi sessions)
$old = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$pyDir;$pyDir\Scripts;$old", "User")

# 3. Zavřít + otevřít PowerShell, pak ověřit
python --version
```

Klíčem je, že `$pyDir;$pyDir\Scripts` je PŘED zbytkem PATH (a tedy
před `WindowsApps` stuby).

#### Verifikační test po oprave

```pwsh
py --version                                                    # 3.12.10
py -m pip install openpyxl --break-system-packages              # bez chyb
py -c "import openpyxl; print(openpyxl.__version__)"            # 3.x.x
py tools\check_priority_matrix.py BOURACKA-TESTPLAN-v0.4.0.xlsx # exit 0
```

Pokud všechny 4 kroky projdou, jsou Python skripty plně funkční.

#### §13.1.1 Pip má stejný PATH problém — vždy používejte `py -m pip`

**Symptom:** Po `python -m pip install --upgrade pip` (přes full path)
přijde varování:

> WARNING: The scripts pip.exe, pip3.12.exe and pip3.exe are installed
> in `C:\Users\…\Python312\Scripts` which is not on PATH.

A pak `pip install ...` (bez `py -m`) selže:

> The term 'pip' is not recognized as the name of a cmdlet…

**Příčina:** Stejný princip jako §13.1 — `Scripts\` adresář winget Pythonu
není automaticky přidán na PATH (jen `python.exe` v hlavním adresáři).

**Doporučené řešení (bez PATH editu):** vždy invokovat pip přes
`py -m pip`, ne přes bare `pip`:

```pwsh
# OK — funguje:
py -m pip install openpyxl --break-system-packages
py -m pip list
py -m pip install --upgrade <package>

# Nefunguje, dokud není Scripts\ na PATH:
pip install openpyxl
```

Tato konvence funguje konzistentně i pro:
- `py -m venv venv` (vytvoření virtualenvu)
- `py -m pytest tests/` (spuštění pytestu)
- `py -m black tools/` (formátování)

**Trvalé řešení (volitelné):** přidat `Scripts\` na PATH:

```pwsh
$scripts = "$env:LOCALAPPDATA\Programs\Python\Python312\Scripts"
$old = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$scripts;$old", "User")
# Restart PowerShell — bare `pip` nyní funguje
```

#### §13.1.2 Pozor na entry do REPL místo verze

`py --version` → tiskne verzi, vrací se do PS prompt ✓
`py -3.12 --version` → tiskne verzi 3.12, vrací se ✓
`py` nebo `py -3.12` (BEZ `--version` nebo `-m`) → **ZAPÍNÁ Python REPL**
(prompt `>>>`)

V REPL nepoužívejte shell příkazy — `py -m pip install ...` na REPL
prompt vyhodí `SyntaxError: invalid syntax`. Z REPL ven: `exit()` nebo
Ctrl+Z + Enter.

## §14. Bezpečnostní poznámky

- Žádné credentials nejsou v balíčku — všechny test-data jsou syntetické.
- DEMO Bouračka je veřejně dostupná; tyto testy nevyžadují žádný login.
- PROD Bouračka (`bouracka.cz`) potřebuje pro reálné integrační testy
  N8 sandbox / AISPOV read-only přístup — viz §4 v `00_README-CS.md`.
- `INTEL_PROBE_CREATE_REPORT=1` vytvoří report UUID na DEMO — data se
  purgují automaticky podle UI copy "Pokud nedojde k závěrečnému
  oboustrannému potvrzení, všechna zadaná data včetně kontaktů budou
  smazána bez uložení."

## §15. Dále

- Studujte `recon/ANALYTICAL-DOC-INTELLIGENCE-v0.3.md` pro analytický
  bottom-up přehled SUT.
- Studujte `recon/screenflows-live/flow-A1-main-tst-demo/flow.md` pro
  detail E2E průchodu.
- Studujte UML diagramy v `uml/` (po renderu).
- Pro CP-SUPIN-05 (multi-framework srovnání): vyplňte
  `tools/test-console.ps1 run --env tst --frameworks playwright,cypress,testcafe`.

## §16. Status

| Item | Hodnota |
|------|---------|
| Příručka | `_install/INSTALL-FROM-ZERO-v0.3-CS.md` |
| Verze | v0.3 |
| Datum | 2026-05-06 |
| Audience | první operátor; SecOps |
| Status | nahrazuje `_install/INSTALL-CS.md` (v0.2) — ten v archive/obsolete/ |
