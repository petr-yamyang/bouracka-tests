# Bouračka UI — reinstall na v0.1.4 multi-ABI + workbook v0.4.4

**Verze.** v0.1.4 multi-ABI (2026-05-14) + workbook v0.4.4.
**Pro.** Kate — reinstall na HP Elite (předchozí stav: v0.1.4 -py310 nebo v0.1.2).
**Časová náročnost.** ~10 minut.
**Co se mění oproti minulé verzi:**

- **NOVÝ ZIP** — `bouracka-ui-hp-elite-v0.1.4-CS-multi-abi.zip` (cca 12 MB, větší o ABI wheels pro 3.11/3.12). Funguje na Python 3.10 / 3.11 / 3.12 bez rozdílu (BUG-K-005 fix — minulý ZIP padal na `httptools from versions: none` při ABI mismatch).
- **NOVÝ workbook** — `BOURACKA-TESTPLAN-v0.4.4.xlsx`. Přibyl list `02e_TestSteps` (entita Test-Step, příprava pro v0.1.5). Současné UI ho ignoruje, nepoškodí nic — ověřeno kompatibilním testem.
- 3 opravy z prvního kola (BUG-K-001 framework filter, BUG-K-002 bug edit, BUG-K-003 workbook startup banner) ze ZIP zůstávají platné.

---

## §1.0 Předpoklady (MUSÍ být nainstalované před spuštěním)

| Co | Verze | Proč | Jak |
|----|-------|------|-----|
| Python | 3.10 / 3.11 / 3.12 (jedno z) | bouracka-ui běhové prostředí | Stáhni z python.org → installer s defaulty (**NE** Microsoft Store edice) |
| Node.js | 20+ LTS | npx → cypress + playwright | Stáhni z nodejs.org → „LTS" → installer s defaulty |
| Cypress + Playwright deps | per package.json | framework runtime | `cd tests-source\cypress && npm install` + `cd ..\playwright && npm install && npx playwright install chromium` (vyžaduje internet) |
| selenium python | `pip install selenium` | selenium webdriver | Po `pip install bouracka_ui-...whl` ve venv automaticky přidáno; ověř `python -c "import selenium"` |

> **Bez Node.js** → cypress/playwright nepoběží (WinError 2 / `[tooling not found]`).
> **Bez selenium pip** → selenium suite hodí `ImportError` při loadu conftest.py.

---

## §1. Co se opravilo

| Tvůj nález | Stav |
|------------|------|
| Po výběru jednotlivého frameworku (cypress / playwright / selenium) v dropdownu byl seznam TC prázdný | ✓ opraveno |
| Nemožnost otevřít existující bug a změnit Status / další pole | ✓ opraveno — kliknutí na řádek bugu otevře edit form |
| Bugy „mizely“ — `C:\TestAutomationSite\BOURACKA-TESTPLAN-v0.4.3.xlsx` byl prázdný, ale `tests-source\BOURACKA-TESTPLAN-v0.4.3.xlsx` měl data | ✓ opraveno — JEDEN platný workbook v UI rootu; test-suite ZIP už workbook neobsahuje |

Plus: bouracka-ui teď při startu **explicitně vypíše do konzole cestu k workbooku, který používá** — kontroluj ten řádek a v Excelu otevírej jen tento jeden soubor.

---

## §2. Postup reinstallu

### §2.1 Zastav běžící bouracka-ui (pokud běží)

V PowerShell okně kde běží bouracka-ui: **Ctrl+C**. Pokud zůstanou „zombíci“:

```powershell
Get-NetTCPConnection -LocalPort 8424 -State Listen -ErrorAction SilentlyContinue |
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
```

### §2.2 Zálohuj svůj workbook (důležité — obsahuje BUG-002 který jsi založila)

```powershell
# Z UI rootu zálohuj workbook do C:\TestAutomationSite-backup\
$timestamp = Get-Date -Format "yyyy-MM-dd-HHmm"
New-Item -ItemType Directory C:\TestAutomationSite-backup -Force | Out-Null
Copy-Item C:\TestAutomationSite\tests-source\BOURACKA-TESTPLAN-v0.4.3.xlsx "C:\TestAutomationSite-backup\BOURACKA-TESTPLAN-v0.4.3-tests-source-$timestamp.xlsx"
Copy-Item C:\TestAutomationSite\BOURACKA-TESTPLAN-v0.4.3.xlsx "C:\TestAutomationSite-backup\BOURACKA-TESTPLAN-v0.4.3-uiroot-$timestamp.xlsx"
```

Obě verze ulož do bezpečí. Ten z `tests-source\` má tvé bugy (BUG-002 atd.) — ten je důležitý.

### §2.3 Smaž starou v0.1.2 instalaci

```powershell
cd C:\TestAutomationSite

# Zlikviduj venv (Python balíčky se přeinstalují čerstvě)
Remove-Item .venv -Recurse -Force -ErrorAction SilentlyContinue

# Zlikviduj starý wheelhouse + wheel z v0.1.2
Remove-Item wheelhouse -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item bouracka_ui-0.1.2-py3-none-any.whl -Force -ErrorAction SilentlyContinue

# Zlikviduj starý workbook v UI rootu (prázdný, fakticky bez dat; data byla v tests-source kopii)
Remove-Item BOURACKA-TESTPLAN-v0.4.3.xlsx -Force -ErrorAction SilentlyContinue

# Test-suite source může zůstat (cypress/playwright/selenium soubory jsou stále potřeba)
# Ale workbook uvnitř tests-source MUSÍŠ odstranit — to je ta nadbytečná kopie z v0.5.6
Remove-Item tests-source\BOURACKA-TESTPLAN-v0.4.3.xlsx -Force -ErrorAction SilentlyContinue
```

### §2.4 Stáhni v0.1.4 multi-ABI z Google Drive

Z mé sdílené Drive složky (aktualizovaná původní složka — pošlu ti nový link mailem) stáhni TŘI soubory:

- `bouracka-ui-hp-elite-v0.1.4-CS-multi-abi.zip` (~12 MB)
  sha256: `e4a98d8016df8bc3b1e6bbaddcf8e6948917f71ac22fbdef38887333df092af5`
- `bouracka-tests-source-v0.5.6.zip` (~1.3 MB, beze změny)
- **`BOURACKA-TESTPLAN-v0.4.4.xlsx`** (~100 KB, NOVĚ — workbook se schema upgrade)

Ověř SHA256 oproti `SHA256SUMS.txt` ve složce.

### §2.5 Rozbal v0.1.4

```powershell
cd C:\TestAutomationSite

# UI balíček do rootu
Expand-Archive ..\Downloads\bouracka-ui-hp-elite-v0.1.4-CS-multi-abi.zip . -Force

# Test-suite source do tests-source (přepiš starou)
Expand-Archive ..\Downloads\bouracka-tests-source-v0.5.6.zip .\tests-source -Force

# NOVÝ workbook — umísti PŘÍMO do UI rootu (NIKDY do tests-source!)
Copy-Item ..\Downloads\BOURACKA-TESTPLAN-v0.4.4.xlsx C:\TestAutomationSite\

# Pokud máš v UI rootu ještě starý v0.4.3 workbook, smaž ho — UI by mohlo
# vybrat špatný (vybírá alfabeticky nejvyšší, takže v0.4.4 vyhraje, ale
# čistší stav = jen jeden workbook):
Remove-Item C:\TestAutomationSite\BOURACKA-TESTPLAN-v0.4.3.xlsx -Force -ErrorAction SilentlyContinue

# Ověř že workbook je JEN na jednom místě
Get-ChildItem -Recurse -Filter "BOURACKA-TESTPLAN-*.xlsx"
# Očekávané: pouze C:\TestAutomationSite\BOURACKA-TESTPLAN-v0.4.4.xlsx
```

### §2.6 Obnov venv + nainstaluj v0.1.4 z multi-ABI wheelhouse

```powershell
cd C:\TestAutomationSite

# Tvoje Python verze už nehraje roli — wheelhouse má wheels pro 3.10/3.11/3.12.
# Pokud nejsi jistá co máš, ověř:
python --version

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --no-index --find-links="C:\TestAutomationSite\wheelhouse" "C:\TestAutomationSite\bouracka_ui-0.1.4-py3-none-any.whl"

# Smoke check
bouracka-ui --help
```

Pokud `pip install` selže s "Could not find a version that satisfies httptools..." → to je BUG-K-005 který jsme PRÁVĚ TÍMTO ZIPEM opravili. Ověř, že jsi rozbalila `-multi-abi.zip` (NE starý `-py310.zip`) a opakuj. SHA256 wheelhouse složky musí mít wheels pro cp310 + cp311 + cp312.

### §2.7 Obnov svůj BUG-002 do nového workbooku (volitelné)

Pokud chceš zachovat BUG-002 v novém workbooku, otevři zálohu:

```
C:\TestAutomationSite-backup\BOURACKA-TESTPLAN-v0.4.3-tests-source-<timestamp>.xlsx
```

Najdi list `08_Bugs`, zkopíruj řádek BUG-002 a vlož ho do nového:

```
C:\TestAutomationSite\BOURACKA-TESTPLAN-v0.4.4.xlsx → list 08_Bugs
```

**Pozn.** `08_Bugs` ve v0.4.4 má 6 nových sloupců napravo (`linked_step_ref`, `evidence_*`) — když kopíruješ řádek z v0.4.3, tyhle zůstanou prázdné, což je v pořádku. Stávající `screenshot_ref` a `trace_ref` zůstávají (soft-deprecated).

**DŮLEŽITÉ:** Excel musí být před spuštěním bouracka-ui zavřený (workbook lock).

Alternativně tě nechám zaregistrovat BUG-002 znovu přes UI — chvíli to trvá, ale je čisté.

---

## §3. Verifikace v0.1.4 — 3 rychlé kontroly

### §3.1 Start s viditelnou cestou k workbooku

```powershell
$env:BOURACKA_UI_REPO_ROOT = "C:\TestAutomationSite\tests-source"   # pro dispatch
bouracka-ui --no-browser
```

V konzoli uvidíš:

```
[bouracka-ui] starting on http://127.0.0.1:8424/
[bouracka-ui] repo root:  C:\TestAutomationSite\tests-source
[bouracka-ui] workbook:   C:\TestAutomationSite\BOURACKA-TESTPLAN-v0.4.4.xlsx
[bouracka-ui] WARNING: open ONLY this workbook in Excel for bug review;
[bou