# Bouračka Test Suite — Instalace od nuly — v0.4 CS

> **Audience.** Druhý a další operátor (= "follower"). Nahrazuje
> `INSTALL-FROM-ZERO-v0.3-CS.md` na základě **reálné instalace na
> ThinkPadu 2026-05-06**, která odhalila několik nečekaných gotchas.
>
> **Cíl.** Po dokončení této příručky:
> - máte funkční Python + Node + (volitelně) JRE pro PlantUML
> - umíte spustit Bouračka tooling (Excel validátor, render scripty)
> - umíte spustit Playwright bring-up smoke proti DEMO Bouračce
> - máte jasný mental model kdy použít `py` vs `python` (TLDR: vždy `py`)
>
> **Doba instalace:** 25 minut čistého času (z toho ~15 minut čekání
> na stahování Pythonu a Chromia).

---

## §0. Klíčové pravidlo (přečtěte PŘED instalací)

> ⚠ **Na Windows **VŽDY** používejte `py` místo `python`,
>    a `py -m pip` místo `pip`.**
>
> Důvod: Windows 10/11 má v `%LOCALAPPDATA%\Microsoft\WindowsApps\`
> stub binárky `python.exe` + `python3.exe`, které redirect-ují
> uživatele do Microsoft Store. Tyto stuby jsou na PATH **PŘED**
> winget Pythonem. `py.exe` (Python Launcher for Windows) na rozdíl
> od `python.exe` není zastíněný a funguje správně okamžitě po `winget install`.
>
> Stejný problém má `pip.exe` (umístěn v `Python312\Scripts\` který
> není na PATH). Proto `py -m pip ...`, ne `pip ...`.

Příklady místo `python` / `pip`:

```pwsh
# Místo: python --version
py --version

# Místo: pip install openpyxl --break-system-packages
py -m pip install openpyxl --break-system-packages

# Místo: python tools\validate_workbook.py
py tools\validate_workbook.py

# Místo: pip list
py -m pip list
```

Další gotcha: `py` (bez argumentů) zapíná **REPL** (`>>>` prompt).
Pokud chcete jen ověřit verzi, používejte `py --version`. Pokud
omylem skončíte v REPL, ven: `exit()` nebo `Ctrl+Z` + `Enter`.

---

## §1. Předpoklady

| Položka | Verze | Poznámka |
|---------|-------|----------|
| Windows | 10 / 11 | testováno na 11 24H2 |
| Administrátor | dočasně | pro `winget` instalaci runtime balíčků |
| Disk free | ≥ 5 GB | Playwright Chromium ~150 MB + ostatní |
| Internet | běžný | povolené domény: `*.npmjs.com`, `pypi.org`, `github.com`, `*.python.org`, `playwright.download.prss.microsoft.com`, `cdn.playwright.dev` |

## §2. Preflight — winget source reset

**Empirická zkušenost:** první `winget install Python.Python.3.12`
často selže s chybou *"Failed when opening source(s); try the
'source reset' command if the problem persists"*. Reset napravuje:

```pwsh
# Otevřete PowerShell jako administrátor
winget source reset --force

# Verifikace
winget source list
# Měli byste vidět: msstore + winget
```

Tento krok přeskočte **jen pokud** jste v posledních 24 h winget úspěšně
používali pro jakýkoliv jiný balíček.

## §2b. Preflight — PowerShell ExecutionPolicy

**Empirická zkušenost:** Windows defaultně má `ExecutionPolicy: Restricted`,
což blokuje VŠECHNY `.ps1` skripty. Bouračka workflow potřebuje spustit:
- `npm.ps1` (`npm` na Windows je PS skript) — typicky první co selže
- vlastní `scripts\*.ps1` v repu (run-bring-up-smoke, sanity-check atd.)

**Fix — jednou pro user-level (žádný admin):**

```pwsh
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
# Při potvrzení: Y nebo A
```

**Verifikace:**

```pwsh
Get-ExecutionPolicy -List
# Očekávaný výstup pro CurrentUser: RemoteSigned
```

**Co `RemoteSigned` znamená:**
- Lokální skripty (bouracka-tests, `npm.ps1` z lokální instalace) → běží volně
- Stažené skripty z internetu → vyžadují signaturu od důvěryhodného vydavatele
- **Bezpečný default** pro vývojářské stanice; doporučení Microsoftu

Tento krok lze přeskočit **jen pokud** ručně už máte nastavený
`RemoteSigned` (nebo méně restriktivní) — ověřte přes `Get-ExecutionPolicy`.

## §2c. Preflight — Unblock-File z e-mail/ZIP downloadu

**Empirická zkušenost (2026-05-07):** I po `Set-ExecutionPolicy RemoteSigned`
mohou skripty vyextrahované z **ZIPu staženého z e-mailu** selhávat s:

```
File C:\...\scripts\validate-install.ps1 cannot be loaded.
The file is not digitally signed.
```

To je **odlišný error** od "running scripts is disabled" (= Restricted policy).

**Příčina:** Windows přidá NTFS alternate data stream `Zone.Identifier`
ke každému souboru staženému z internetu (e-mail attachment je internet
origin). Pod `RemoteSigned` policy:
- Lokálně-vytvořené `.ps1` (např. heredoc paste) → běží volně ✓
- ZIP-extrahované `.ps1` (mají `Zone.Identifier`) → vyžadují signaturu ✗

**Fix — strip Zone.Identifier ze všech .ps1 v projektu:**

```pwsh
cd C:\TestAutomationSite
Get-ChildItem -Recurse -Filter *.ps1 | Unblock-File
# Strips ADS; po tomto všechny .ps1 běží jako lokální
```

**Verifikace:**

```pwsh
# Před Unblock-File: vrací ZoneId=3 řádek
Get-Content .\scripts\validate-install.ps1 -Stream Zone.Identifier -ErrorAction SilentlyContinue
# Po Unblock-File: nic nevrací (stream stripped)
```

**Alternativa — temporary Bypass jen pro current shell:**

```pwsh
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# Platí jen pro tuto PowerShell session; nezůstává po close
```

**Tento krok je gotcha #7 (přidáno 2026-05-07):** patří do preflight, ne
troubleshoot. Spustit po každém ZIP extract.

## §3. Runtime instalace (admin window — ~15 minut)

### §3.1 Python 3.12

```pwsh
# Stále v admin PowerShell
winget install Python.Python.3.12
# Pokud se objeví "Do you agree to all the source agreements terms? [Y] Yes [N] No:" → Y
# Stahování ~25 MB; instalace ~30 s
```

**Po skončení instalace:**

```pwsh
# OTEVŘETE NOVÝ PowerShell (jakýkoliv user-level, ne admin)
py --version
# Očekávaný výstup: Python 3.12.10
```

> ⚠ Pokud `py --version` říká *"Python was not found..."* → buď
> winget instalace skutečně selhala (zkuste znovu od §3.1), nebo
> máte korporátní AppLocker policy. V tom případě Fix 2 z §13.1
> v0.3 příručky.

### §3.2 Pip (upgrade na nejnovější verzi)

Winget Python přichází s pip 25.x; doporučujeme aktualizovat:

```pwsh
py -m pip install --upgrade pip
# "Successfully installed pip-26.x" — varování o PATH si nevšímejte
```

### §3.3 Závislosti pro Bouračka tooling

```pwsh
py -m pip install openpyxl --break-system-packages
# "Successfully installed openpyxl-3.x.x"

# Ověřit:
py -c "import openpyxl; print('openpyxl', openpyxl.__version__)"
# Očekávaný výstup: openpyxl 3.x.x
```

Flag `--break-system-packages` je potřeba na Pythonu 3.11+ na
"externally-managed" environment (PEP 668). Bezpečné — winget Python
není systémový.

### §3.4 Node.js 20 LTS

```pwsh
# Admin PowerShell
winget install OpenJS.NodeJS.LTS
```

⚠ **Po instalaci `node` NEbude fungovat v současném PowerShellu**
(PATH snapshot, viz §3.7 níže). **Otevřete nový PowerShell** nebo
refresh PATH:

```pwsh
# Nový PowerShell (preferované):
node --version          # v20.x.x  nebo  v24.x.x
npm --version           # 10.x.x  nebo  11.x.x

# NEBO inline refresh aktuální session:
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
node --version
```

### §3.5 (Volitelné) Java JRE 21 pro PlantUML

Pokud budete renderovat UML diagramy do PNG/SVG:

```pwsh
winget install Microsoft.OpenJDK.21
```

⚠ Stejný PATH snapshot problém jako u Node.js — **nový PowerShell** nebo refresh:

```pwsh
# Nový PowerShell (preferované) NEBO:
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Pak:
java --version          # openjdk 21.x

# Stáhnout PlantUML jar (do user folderu, žádný admin)
$tools = "$env:USERPROFILE\tools"
New-Item -ItemType Directory -Force -Path $tools | Out-Null
Invoke-WebRequest 'https://github.com/plantuml/plantuml/releases/download/v1.2024.7/plantuml-1.2024.7.jar' -OutFile "$tools\plantuml.jar"

# Test render
java -jar "$tools\plantuml.jar" -version
```

### §3.6 (Volitelné) Mockoon CLI pro N8 SMS Gateway mock

```pwsh
npm install -g @mockoon/cli
mockoon-cli --version
```

### §3.7 Klíčové pravidlo — PATH snapshot v PowerShell

**Empirická zkušenost:** každý `winget install <něco-co-přidává-bin-na-PATH>`
zapíše PATH do **systémového** environment (HKLM), ale **současná
PowerShell session** má PATH nasnímaný od svého spuštění a NEVÍ o
změně. Proto:

| `winget install` | Jak ovlivní | Co dělat |
|------------------|-------------|----------|
| `Python.Python.3.12` | nepřidává `python.exe` na PATH před stub; ale `py.exe` je vždy na PATH | použijte `py` (§0) |
| `OpenJS.NodeJS.LTS` | přidává `node.exe`, `npm.cmd` na systém PATH | nový shell NEBO refresh |
| `Microsoft.OpenJDK.21` | přidává `java.exe` na systém PATH | nový shell NEBO refresh |
| `Microsoft.PowerToys` | přidává PowerToys na PATH | nový shell NEBO refresh |
| (cokoliv s bin/PATH) | obecně | nový shell NEBO refresh |

**Refresh inline (bez nového shell):**

```pwsh
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

**Sanity rule:** po každé `winget install` co může něco přidat na PATH,
buď otevřete nový PowerShell, nebo proveďte tento refresh. Je to
jednořádkové; přidejte si do PowerShell profilu jako alias:

```pwsh
notepad $PROFILE
# Přidejte funkci:
function Refresh-Path { $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User") }
```

Po reload profilu (`. $PROFILE`) můžete jen psát `Refresh-Path` po každé winget instalaci.

## §4. Rozbalení distribuce

```pwsh
# Vyberte cílový adresář
$dir = "C:\bouracka-tests"
mkdir $dir -Force

# Rozbalte všechny dodané ZIPy do $dir
# Doporučené nástroje: PowerShell `Expand-Archive`, 7-Zip, Windows Explorer

cd $dir
ls
# Měli byste vidět: BOURACKA-TESTPLAN-v0.4.x.xlsx, package.json, _install\, _specs\,
# fixtures\, mockoon\, playwright\, recon\, scripts\, tools\, ...
```

**Verifikace SHA256 přílohy** (paranoidní, ale doporučené):

```pwsh
Get-FileHash bouracka-analytical-v0.4.0.zip -Algorithm SHA256
# Porovnat s hodnotou v MANIFEST-CS.md
```

## §5. Playwright + Chromium

```pwsh
cd $dir
npm install                       # ~ 60 s (~ 200 MB)
npx playwright install chromium   # ~ 3 min (~ 150 MB stahování)
npx playwright --version          # Version 1.x.x
```

> ⚠ **Pokud `npx playwright install` selže** s `Failed to download Chromium`,
> blokuje vás SecOps proxy. Otevřete ticket na allowlist těchto domén:
> `playwright.download.prss.microsoft.com`, `cdn.playwright.dev`.

## §6. 30-sekundový sanity-check

Spusťte one-shot validátor:

```pwsh
cd $dir
.\scripts\sanity-check.ps1
```

Očekávaný výstup: 7 zelených ✓ položek; exit kód 0:

```
=== Bouracka sanity-check ===

  + py launcher works
  + py -m pip works
  + openpyxl importable
  + Node + npm on PATH
  + Playwright installed
  + Excel master present (BOURACKA-TESTPLAN-v0.4.0.xlsx)
  + check_priority_matrix exit 0

Result: 7 passed, 0 failed
```

Pokud projdou **všechny 7 položek**, instalace je zdravá a můžete
přejít na §7. Pokud některé selžou, viz §6.1 (Recovery patterns)
nebo §10 (Troubleshoot).

### §6.1 Systematic bootstrap recovery (pro followers)

**Empirická zkušenost:** může se stát, že po extrakci ZIPu některé
soubory chybí (extrakt do podsložky, e-mailový scanner odstranil
`.ps1`, starší rev verze atd.). Tato sekce dává **systematický
recovery pattern** — můžete obnovit chybějící soubory **inline z
PowerShell heredoc** bez stahování čehokoliv.

#### Recovery 1 — Excel master se nenalezl

Pokud sanity-check říká *"- Excel master present"*:

```pwsh
# 1. Hledejte v podsložkách
$found = Get-ChildItem -Recurse -Filter "BOURACKA-TESTPLAN-*.xlsx" |
         Sort-Object Name -Descending | Select-Object -First 1
if ($found) {
    Write-Host "Found: $($found.FullName)"
    Copy-Item $found.FullName .   # přesunout na root
} else {
    Write-Host "Excel master není v repu — vyextrahujte z bouracka-analytical-v0.4.x.zip"
}

# 2. Re-run
.\scripts\sanity-check.ps1
```

#### Recovery 2 — `scripts\sanity-check.ps1` chybí

Vytvořit přímo z heredoc (kanonický obsah):

```pwsh
mkdir scripts -Force
@'
<#
.SYNOPSIS
  30-sekundový sanity check po instalaci — ověří 7 kritických komponent.
#>
$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$ok = 0; $fail = 0

function Check {
    param([string]$Name, [scriptblock]$Test)
    $r = & $Test
    if ($r) { Write-Host "  + $Name" -ForegroundColor Green; $script:ok++ }
    else    { Write-Host "  - $Name" -ForegroundColor Red;   $script:fail++ }
}

Write-Host ""
Write-Host "=== Bouracka sanity-check ===" -ForegroundColor Cyan
Write-Host ""

Check "py launcher works"           { (& py --version 2>&1) -match 'Python 3\.' }
Check "py -m pip works"             { & py -m pip --version *> $null; $LASTEXITCODE -eq 0 }
Check "openpyxl importable"         { & py -c "import openpyxl" *> $null; $LASTEXITCODE -eq 0 }
Check "Node + npm on PATH"          {
    ((Get-Command node -ErrorAction SilentlyContinue) -ne $null) -and
    ((Get-Command npm  -ErrorAction SilentlyContinue) -ne $null)
}
Check "Playwright installed"        {
    if (-not (Test-Path "node_modules\@playwright\test")) { return $false }
    & npx playwright --version *> $null; $LASTEXITCODE -eq 0
}

# Auto-detect Excel master (newest first)
$wb = Get-ChildItem -Filter "BOURACKA-TESTPLAN-*.xlsx" |
      Sort-Object Name -Descending | Select-Object -First 1 -ExpandProperty Name
if (-not $wb) { $wb = "BOURACKA-TESTPLAN-v0.4.0.xlsx" }
Check "Excel master present ($wb)"  { Test-Path $wb }
Check "check_priority_matrix exit 0" {
    if (-not (Test-Path $wb)) { return $false }
    if (-not (Test-Path "tools\check_priority_matrix.py")) { return $false }
    & py "tools\check_priority_matrix.py" $wb *> $null; $LASTEXITCODE -eq 0
}

Write-Host ""
Write-Host "Result: $ok passed, $fail failed" -ForegroundColor $(if ($fail -eq 0) { 'Green' } else { 'Yellow' })
exit $fail
'@ | Out-File -Encoding UTF8 .\scripts\sanity-check.ps1
.\scripts\sanity-check.ps1
```

#### Recovery 3 — `tools\check_priority_matrix.py` chybí

```pwsh
mkdir tools -Force
@'
#!/usr/bin/env python3
"""check_priority_matrix.py — verify priority = severity × urgency consistency."""
from __future__ import annotations
import sys
from pathlib import Path
import openpyxl

ROOT = Path(__file__).resolve().parent.parent

MATRIX = {
    ('A', 'A'): 'A',  ('A', 'B'): 'A',  ('A', 'C'): 'B',  ('A', 'D'): 'C',
    ('B', 'A'): 'A',  ('B', 'B'): 'B',  ('B', 'C'): 'C',  ('B', 'D'): 'D',
    ('C', 'A'): 'B',  ('C', 'B'): 'C',  ('C', 'C'): 'D',  ('C', 'D'): 'D',
    ('D', 'A'): 'C',  ('D', 'B'): 'D',  ('D', 'C'): 'D',  ('D', 'D'): 'D',
}
ITEMBASE_SHEETS = ['00b_Requirements', '01_TestTargets', '02_TestCases', '08_Bugs']

def col_of(ws, name):
    for i, c in enumerate(ws[1], 1):
        if c.value == name: return i
    return None

def check(path):
    wb_v = openpyxl.load_workbook(path, data_only=True)
    wb_f = openpyxl.load_workbook(path, data_only=False)
    violations = 0
    for sheet in ITEMBASE_SHEETS:
        if sheet not in wb_v.sheetnames: continue
        ws_v = wb_v[sheet]; ws_f = wb_f[sheet]
        sev_c = col_of(ws_v, 'severity'); urg_c = col_of(ws_v, 'urgency')
        pri_c = col_of(ws_v, 'priority'); code_c = col_of(ws_v, 'item_code')
        if not all([sev_c, urg_c, pri_c]): continue
        for r in range(2, ws_v.max_row + 1):
            sev = ws_v.cell(row=r, column=sev_c).value
            urg = ws_v.cell(row=r, column=urg_c).value
            pri_v = ws_v.cell(row=r, column=pri_c).value
            pri_f = ws_f.cell(row=r, column=pri_c).value
            if not (sev and urg): continue
            expected = MATRIX.get((sev, urg))
            if pri_v is not None and not (isinstance(pri_v, str) and pri_v.startswith('=')):
                if pri_v != expected: violations += 1
            elif isinstance(pri_f, str):
                if '<=3,"A"' in pri_f: violations += 1   # buggy formula signature
    print(f"[summary] check done, {violations} violations")
    return violations

if __name__ == '__main__':
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else next(ROOT.glob('BOURACKA-TESTPLAN-*.xlsx'))
    sys.exit(check(path))
'@ | Out-File -Encoding UTF8 .\tools\check_priority_matrix.py
```

#### Recovery 4 — `package.json` chybí (jen základní Playwright)

```pwsh
@'
{
  "name": "bouracka-tests",
  "version": "0.4.1",
  "private": true,
  "scripts": {
    "test": "playwright test"
  },
  "devDependencies": {
    "@playwright/test": "^1.45.0"
  }
}
'@ | Out-File -Encoding UTF8 .\package.json
npm install
npx playwright install chromium
```

> ⚠ **Recovery 4 vytvoří jen minimální package.json** — pro plný feature
> set (Cypress, TestCafe, MochaJS) si stáhněte plný `bouracka-tests-v0.4.x.zip`.

### §6.2 Pravidlo

Pokud sanity-check ukáže více než 3 selhání, **nepokračujte** přidáváním
custom kódu — místo toho stáhněte **čerstvý** `bouracka-automation-v0.4.x.zip`
a re-extract over your project. Recovery patterns výše jsou pro **point fixes**,
ne pro vícenásobnou regresi.

## §7. První produktivní použití

### §7.1 Odeslat smoke test proti veřejné DEMO Bouračce

```pwsh
.\scripts\run-bring-up-smoke.ps1
# Spustí Playwright proti https://demo.bouracka.cz, mobile viewport
# 1 test passed = můžete začít psát další TC
```

### §7.2 Spustit intel-probes (obohatit fixtures živými daty)

```pwsh
# Read-only probe — bezpečné, žádné zápisy do SUT
npx playwright test playwright/tests/intel-probes/01-enumeration-dump.spec.ts

# Výstup: fixtures/intel-2026-MM-DD/{enums,bundles,traces}/*.json
```

### §7.3 Otevřít master Excel s branch-aware filterem

1. Otevřete `BOURACKA-TESTPLAN-v0.4.0.xlsx` v Excelu 2016+
2. Přejděte na list `00e_BranchView` — vidíte counts per branch
3. Přejděte na `02_TestCases` — sloupce `applies_to_demo` + `applies_to_prod`
   barevně odlišené
4. Klikněte na šipku AutoFilter v záhlaví `applies_to_demo` →
   zaškrtněte JEN `TRUE` → vidíte jen DEMO-relevantní TC

### §7.4 Render branched analytického dokumentu

```pwsh
py tools\render_branch_doc.py recon\ANALYTICAL-DOC-MASTER-v0.4.md --branch demo
# Vytvoří: recon\ANALYTICAL-DOC-MASTER-v0.4-DEMO.md (jen DEMO sekce + společné)

py tools\render_branch_doc.py recon\ANALYTICAL-DOC-MASTER-v0.4.md --branch prod
# Vytvoří: recon\ANALYTICAL-DOC-MASTER-v0.4-PROD.md
```

## §8. Příprava UTF-8 BOM pro PowerShell skripty (pokud nepoužíváte PS 7)

PowerShell 5.1 čte BOM-less UTF-8 jako Windows-1252 — láme české znaky a
em-dashe. Skripty v balíčku jsou s BOM, ale po editaci v některých
editorech se BOM ztratí. Verifikace:

```pwsh
$bomCheck = [System.IO.File]::ReadAllBytes("scripts\run-bring-up-smoke.ps1")[0..2]
if ($bomCheck[0] -eq 0xEF -and $bomCheck[1] -eq 0xBB -and $bomCheck[2] -eq 0xBF) {
    "[ok] BOM ok"
} else {
    "[fail] BOM chybí — opravit:"
    "  `$content = [System.IO.File]::ReadAllText('scripts\run-bring-up-smoke.ps1')"
    "  [System.IO.File]::WriteAllText('scripts\run-bring-up-smoke.ps1', `$content, [System.Text.UTF8Encoding]::new(`$true))"
}
```

> Pokud máte k dispozici PowerShell 7+ (`pwsh.exe`), BOM problém řeší automaticky — preferujte ho.

## §9. Diagnostické skripty

| Skript | Co dělá | Spustit kdy |
|--------|---------|-------------|
| `scripts\setup-from-zero.ps1` | one-shot Profile-C install (volá §3 + §5) | poprvé na čistém stroji |
| `scripts\validate-install.ps1` | 14 zdravotních kontrol prostředí | před každým během |
| `scripts\run-bring-up-smoke.ps1` | smoke test proti DEMO | po instalaci |
| `scripts\run-all.ps1` | Playwright + Cypress + TestCafe (po instalaci) | full regression |
| `tools\test-console.ps1 status` | reportuje, jaké frameworky jsou runnable | diagnostika |

## §10. Co dělat, když něco selže — troubleshoot

| Symptom | Příčina | Řešení |
|---------|---------|---------|
| `winget install`: "Failed when opening source(s)" | winget source registr poškozený | `winget source reset --force` (§2) |
| `python --version`: "not found" po úspěšné winget instalaci | MS Store stuby na PATH před winget Pythonem | použijte `py` (§0); nebo Settings → App execution aliases → vypnout python.exe + python3.exe |
| `pip install`: "term 'pip' is not recognized" | `Scripts\` adresář není na PATH | použijte `py -m pip ...` (§0) |
| `py` zapne REPL místo verze | použili jste `py` bez argumentů | `py --version` (§0); z REPL ven `exit()` |
| `pip install`: "externally-managed-environment" | PEP 668 ochrana Pythonu 3.11+ | přidat `--break-system-packages` (§3.3) |
| `npm install`: 401 / proxy error | korporátní proxy | `npm config set proxy http://proxy:port` |
| `npx playwright install`: "Failed to download Chromium" | firewall blokuje `*.playwright.dev` | SecOps ticket na allowlist (§5) |
| PS skript: "nelze načíst, není digitálně podepsaný" | restriktivní ExecutionPolicy | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` (admin shell) |
| Mojibake (`Â`, `Ã`) v PS výstupu | BOM-less UTF-8 + PS 5.1 | viz §8 |
| `tools\render-uml.ps1`: "PlantUML chybí" | JRE / jar nenainstalovány | viz §3.5 |
| `py -m pip ...` selže s "could not find a version" | offline / DNS issue | `Test-NetConnection pypi.org -Port 443` |

## §11. Bezpečnostní poznámky

- Žádné credentials nejsou v balíčku — všechny test data jsou syntetické.
- DEMO Bouračka (`demo.bouracka.cz`) je veřejně dostupná — žádný login.
- PROD Bouračka (`bouracka.cz`) potřebuje pro reálné integrační testy
  N8 sandbox / AISPOV read-only přístup — viz `_install/contracts/`.
- `INTEL_PROBE_CREATE_REPORT=1` (intel-probes opt-in) vytvoří report
  UUID na DEMO; data se purgují podle UI copy
  (Phase 1 disclaimer §STR-013).

## §12. Co následuje (po úspěšné instalaci)

1. **Přečtěte** `recon/ANALYTICAL-DOC-MASTER-v0.4.md` — bottom-up přehled SUT
2. **Přečtěte** `recon/screenflows-live/flow-A1-main-tst-demo/flow.md` — E2E walk
3. **Studujte** UML v `recon/screenflows-live/flow-A1-main-tst-demo/uml/`
4. **Pro CP-SUPIN-05** (multi-framework srovnání): nainstalujte
   Cypress + TestCafe podle §3 a spusťte `py tools\test-console.ps1 status`
5. **Pro PROD testy** (po dodání N8 sandboxu): rozbalte
   `bouracka-suite-PROD-v0.3.0.zip` z přílohy a vyplňte
   `fixtures/tester-contacts.yaml` z template

## §13. Empirické lessons learned

Tato příručka je v0.4 — vznikla po reálné instalaci na ThinkPadu
2026-05-06, která odhalila **pět** nečekaných problémů:

1. **Winget source reset** — fresh install Windows často selže na první
   `winget install`. Reset (§2) je preflight, ne troubleshoot.
2. **PowerShell ExecutionPolicy** — Windows defaultně blokuje
   `.ps1` skripty (včetně `npm.ps1`!). Set-ExecutionPolicy (§2b) je preflight.
3. **Python.exe stub** — winget Python NENÍ na PATH před MS Store stubem.
   Universal řešení: `py.exe` launcher (§0).
4. **Pip.exe + Scripts\ stub** — stejný problém, stejné řešení: `py -m pip` (§0).
5. **PATH snapshot v PowerShell** — `winget install <bin>` aktualizuje
   systémové PATH, ale aktuální shell neví. Refresh nebo nový shell (§3.7).

Těchto pět gotchas dohromady stojí prvního operátora ~45 minut. Tato
v0.4 příručka je strukturovaná tak, aby DRUHÝ operátor je nezakopal —
§0 + preflighty (§2 + §2b) jsou první, ne v troubleshoot na konci.

## §14. Stav

| Item | Hodnota |
|------|---------|
| Příručka | `_install/INSTALL-FROM-ZERO-v0.4-CS.md` |
| Verze | v0.4 (nahrazuje v0.3) |
| Datum | 2026-05-06 |
| Audience | druhý + další operátor (follower) |
| Empirické test | proběhl 2026-05-06 na ThinkPadu Windows 11 |
| Status | doporučeno k použití pro všechny další instalace |
#!/usr/bin/env python3
"""check_priority_matrix.py — verify priority = severity x urgency consistency."""
from __future__ import annotations
import sys
from pathlib import Path
import openpyxl

ROOT = Path(__file__).resolve().parent.parent

MATRIX = {
    ('A', 'A'): 'A',  ('A', 'B'): 'A',  ('A', 'C'): 'B',  ('A', 'D'): 'C',
    ('B', 'A'): 'A',  ('B', 'B'): 'B',  ('B', 'C'): 'C',  ('B', 'D'): 'D',
    ('C', 'A'): 'B',  ('C', 'B'): 'C',  ('C', 'C'): 'D',  ('C', 'D'): 'D',
    ('D', 'A'): 'C',  ('D', 'B'): 'D',  ('D', 'C'): 'D',  ('D', 'D'): 'D',
}
ITEMBASE_SHEETS = ['00b_Requirements', '01_TestTargets', '02_TestCases', '08_Bugs']

def col_of(ws, name):
    for i, c in enumerate(ws[1], 1):
        if c.value == name: return i
    return None

def check(path):
    wb_v = openpyxl.load_workbook(path, data_only=True)
    wb_f = openpyxl.load_workbook(path, data_only=False)
    violations = 0
    rows_checked = 0
    for sheet in ITEMBASE_SHEETS:
        if sheet not in wb_v.sheetnames: continue
        ws_v = wb_v[sheet]; ws_f = wb_f[sheet]
        sev_c = col_of(ws_v, 'severity'); urg_c = col_of(ws_v, 'urgency')
        pri_c = col_of(ws_v, 'priority'); code_c = col_of(ws_v, 'item_code')
        if not all([sev_c, urg_c, pri_c]): continue
        for r in range(2, ws_v.max_row + 1):
            sev = ws_v.cell(row=r, column=sev_c).value
            urg = ws_v.cell(row=r, column=urg_c).value
            pri_v = ws_v.cell(row=r, column=pri_c).value
            pri_f = ws_f.cell(row=r, column=pri_c).value
            if not (sev and urg): continue
            rows_checked += 1
            expected = MATRIX.get((sev, urg))
            if pri_v is not None and not (isinstance(pri_v, str) and pri_v.startswith('=')):
                if pri_v != expected:
                    violations += 1
            elif isinstance(pri_f, str) and '<=3,"A"' in pri_f:
                violations += 1
    print(f"[summary] {rows_checked} rows checked, {violations} violations")
    return violations

if __name__ == '__main__':
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else next(ROOT.glob('BOURACKA-TESTPLAN-*.xlsx'))
    sys.exit(check(path))
'@ | Out-File -Encoding UTF8 .\tools\check_priority_matrix.py

# Verify:
py tools\check_priority_matrix.py
# Expected: [summary] N rows checked, 0 violations  + exit 0
```

#### Recovery 4 — `package.json` chybí (jen základní Playwright)

```pwsh
@'
{
  "name": "bouracka-tests",
  "version": "0.4.1",
  "private": true,
  "scripts": {
    "test": "playwright test"
  },
  "devDependencies": {
    "@playwright/test": "^1.45.0"
  }
}
'@ | Out-File -Encoding UTF8 .\package.json
npm install
npx playwright install chromium
```

> ⚠ **Recovery 4 vytvoří jen minimální package.json** — pro plný feature
> set (Cypress, TestCafe, MochaJS) si stáhněte plný `bouracka-tests-v0.4.x.zip`.

### §6.2 Pravidlo

Pokud sanity-check ukáže **více než 3 selhání**, **nepokračujte** přidáváním
custom kódu — místo toho stáhněte čerstvý `bouracka-automation-v0.4.x.zip`
a re-extract over your project. Recovery patterny v §6.1 jsou pro **point fixes**,
ne pro vícenásobnou regresi.

## §7. První produktivní použití

### §7.1 Smoke test proti veřejné DEMO Bouračce

```pwsh
.\scripts\run-bring-up-smoke.ps1
# Spustí Playwright proti https://demo.bouracka.cz, mobile viewport
# Očekávaný výsledek: 1 test passed
```

NEBO přímo:

```pwsh
npx playwright test playwright/tests/bring-up-smoke.spec.ts --project=chromium-mobile
```

HTML report po běhu: `playwright-report\index.html` (otevřete v prohlížeči).

### §7.2 Spustit intel-probes (obohatit fixtures živými daty)

```pwsh
# Read-only probe — žádné zápisy do SUT
npx playwright test playwright/tests/intel-probes/01-enumeration-dump.spec.ts

# Výstup: fixtures/intel-2026-MM-DD/{enums,bundles,traces}/*.json
```

Detail viz `playwright/tests/intel-probes/README-OPERATOR.md`.

### §7.3 Otevřít master Excel s branch-aware filtrem

1. Otevřete `BOURACKA-TESTPLAN-v0.4.0.xlsx` v Excelu 2016+
2. Přejděte na list `00e_BranchView` — vidíte counts per branch
3. Přejděte na `02_TestCases` — sloupce `applies_to_demo` + `applies_to_prod`
   barevně odlišené
4. Klikněte na šipku AutoFilter v záhlaví `applies_to_demo` →
   zaškrtněte JEN `TRUE` → vidíte jen DEMO-relevantní TC

### §7.4 Render branched analytického dokumentu

```pwsh
py tools\render_branch_doc.py recon\ANALYTICAL-DOC-MASTER-v0.4.md --branch demo
# Vytvoří: recon\ANALYTICAL-DOC-MASTER-v0.4-DEMO.md (jen DEMO sekce + společné)

py tools\render_branch_doc.py recon\ANALYTICAL-DOC-MASTER-v0.4.md --branch prod
# Vytvoří: recon\ANALYTICAL-DOC-MASTER-v0.4-PROD.md
```

## §8. Příprava UTF-8 BOM pro PowerShell skripty (pokud nepoužíváte PS 7)

PowerShell 5.1 čte BOM-less UTF-8 jako Windows-1252 — láme české znaky a
em-dashe. Skripty v balíčku jsou s BOM, ale po editaci v některých
editorech se BOM ztratí. Verifikace:

```pwsh
$bomCheck = [System.IO.File]::ReadAllBytes("scripts\run-bring-up-smoke.ps1")[0..2]
if ($bomCheck[0] -eq 0xEF -and $bomCheck[1] -eq 0xBB -and $bomCheck[2] -eq 0xBF) {
    "[ok] BOM ok"
} else {
    "[fail] BOM chybí — opravit:"
    "  `$content = [System.IO.File]::ReadAllText('scripts\run-bring-up-smoke.ps1')"
    "  [System.IO.File]::WriteAllText('scripts\run-bring-up-smoke.ps1', `$content, [System.Text.UTF8Encoding]::new(`$true))"
}
```

> Pokud máte k dispozici PowerShell 7+ (`pwsh.exe`), BOM problém řeší automaticky — preferujte ho.

## §9. Diagnostické skripty

| Skript | Co dělá | Spustit kdy |
|--------|---------|-------------|
| `scripts\sanity-check.ps1` | 7-check post-install verifier | po instalaci, pred každým během |
| `scripts\setup-from-zero.ps1` | one-shot Profile-C install (volá §3 + §5) | poprvé na čistém stroji |
| `scripts\validate-install.ps1` | 14 zdravotních kontrol prostředí | rozšířená diagnostika |
| `scripts\run-bring-up-smoke.ps1` | smoke test proti DEMO | po instalaci |
| `scripts\run-all.ps1` | Playwright + Cypress + TestCafe | full regression |
| `tools\test-console.ps1 status` | reportuje, jaké frameworky jsou runnable | diagnostika |

## §10. Co dělat, když něco selže — troubleshoot

| Symptom | Příčina | Řešení |
|---------|---------|---------|
| `winget install`: "Failed when opening source(s)" | winget source registr poškozený | `winget source reset --force` (§2) |
| `npm` / `.\scripts\*.ps1`: "running scripts is disabled" | ExecutionPolicy Restricted | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` (§2b) |
| `python --version`: "not found" po úspěšné winget instalaci | MS Store stuby na PATH před winget Pythonem | použijte `py` (§0); nebo Settings → App execution aliases → vypnout |
| `pip install`: "term 'pip' is not recognized" | `Scripts\` adresář není na PATH | použijte `py -m pip ...` (§0) |
| `java` / `node` / `npm`: "not recognized" těsně po winget instalaci | PATH snapshot v current shell | nový PowerShell NEBO `Refresh-Path` (§3.7) |
| `py` zapne REPL místo verze | použili jste `py` bez argumentů | `py --version`; z REPL ven `exit()` |
| `pip install`: "externally-managed-environment" | PEP 668 ochrana | přidat `--break-system-packages` (§3.3) |
| `npm install`: 401 / proxy error | korporátní proxy | `npm config set proxy http://proxy:port` |
| `npx playwright install`: "Failed to download Chromium" | firewall blokuje `*.playwright.dev` | SecOps ticket na allowlist (§5) |
| sanity-check: "Excel master present" ✗ | Excel je v podsložce / chybí | §6.1 Recovery 1 |
| sanity-check: "check_priority_matrix" ✗ | `tools\*.py` chybí (jen analytical extract) | §6.1 Recovery 3 |
| Mojibake (`Â`, `Ã`) v PS výstupu | BOM-less UTF-8 + PS 5.1 | §8 |
| `tools\render-uml.ps1`: "PlantUML chybí" | JRE / jar nenainstalovány | §3.5 |

## §11. Bezpečnostní poznámky

- Žádné credentials nejsou v balíčku — všechny test data jsou syntetické.
- DEMO Bouračka (`demo.bouracka.cz`) je veřejně dostupná — žádný login.
- PROD Bouračka (`bouracka.cz`) potřebuje pro reálné integrační testy
  N8 sandbox / AISPOV read-only přístup — viz `_install/contracts/`.
- `INTEL_PROBE_CREATE_REPORT=1` (intel-probes opt-in) vytvoří report
  UUID na DEMO; data se purgují podle UI copy.

## §12. Co následuje (po úspěšné instalaci)

1. **Přečtěte** `recon/ANALYTICAL-DOC-MASTER-v0.4.md` — bottom-up přehled SUT
2. **Přečtěte** `recon/screenflows-live/flow-A1-main-tst-demo/flow.md` — E2E walk
3. **Studujte** UML v `recon/screenflows-live/flow-A1-main-tst-demo/uml/`
4. **Pro CP-SUPIN-05** (multi-framework srovnání): nainstalujte
   Cypress + TestCafe podle §3.6+ a spusťte `py tools\test-console.ps1 status`
5. **Pro PROD testy** (po dodání N8 sandboxu): rozbalte
   `bouracka-suite-PROD-v0.3.0.zip` a vyplňte `fixtures/tester-contacts.yaml`
   z template

## §13. Empirické lessons learned

Tato příručka je v0.4 — vznikla po reálné instalaci na ThinkPadu
2026-05-06+07, která odhalila **sedm** nečekaných problémů:

1. **Winget source reset** — fresh install Windows často selže na první
   `winget install`. Reset (§2) je preflight, ne troubleshoot.
2. **PowerShell ExecutionPolicy** — Windows defaultně blokuje `.ps1`
   skripty (včetně `npm.ps1`!). Set-ExecutionPolicy (§2b) je preflight.
3. **Python.exe stub** — winget Python NENÍ na PATH před MS Store stubem.
   Univerzální řešení: `py.exe` launcher (§0).
4. **Pip.exe + Scripts\ stub** — stejný problém, stejné řešení: `py -m pip` (§0).
5. **PATH snapshot v PowerShell** — `winget install <bin>` aktualizuje
   systémové PATH, ale aktuální shell neví. Refresh nebo nový shell (§3.7).
6. **Chybějící soubory v ZIP extraktu** — buď extrakt do podsložky, nebo
   email scanner odstranil `.ps1`. Recovery patterny inline (§6.1).
7. **Zone.Identifier z e-mail/ZIP downloadu** — i pod RemoteSigned
   policy ZIP-extrahované `.ps1` vyžadují signaturu, protože mají
   NTFS ADS označující "internet origin". Fix: `Get-ChildItem -Recurse
   -Filter *.ps1 | Unblock-File` (§2c). NEW 2026-05-07.

Těchto **sedm** gotchas dohromady stojí prvního operátora ~55 minut. Tato
v0.4 příručka je strukturovaná tak, aby DRUHÝ operátor je nezakopal —
§0 + preflighty (§2 + §2b + §2c) jsou první, ne v troubleshoot na konci.

## §14. Stav

| Item | Hodnota |
|------|---------|
| Příručka | `_install/INSTALL-FROM-ZERO-v0.4-CS.md` |
| Verze | v0.4 (nahrazuje v0.3) |
| Datum | 2026-05-06 |
| Audience | druhý + další operátor (follower) |
| Empirické test | proběhl 2026-05-06 na ThinkPadu Windows 11 (Petr Žemla) |
| Sekcí | §0 + §1..§14 (14 + úvod) |
| Recovery patterny | §6.1 obsahuje 4 inline heredoc patterns |
| Status | doporučeno k použití pro všechny další instalace |
