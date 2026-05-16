# Bouračka UI — From-zero install runbook pro Kate (HP Elite, SUPIN)

**Verze runbooku:** v0.1.5 (2026-05-15)
**Cílový stroj:** SUPIN HP EliteBook, stejné bezpečnostní úrovně jako Petův HP Elite
**Cílový stav:** plně funkční bouracka-ui běžící na http://127.0.0.1:8424, schopný spustit smoke test
**Časová náročnost:** ~25 minut čistého času (instalace + smoke test + bug-filing rehearsal)
**Síťový egress potřebný na cíli:** ŽÁDNÝ. Vše air-gap.

---

## §0. Co Kate dostala (Kate drop, 2026-05-15)

Čtyři ZIP balíčky + tento runbook + manifest. Vše v jedné SUPIN-controlled dodávce (USB nebo SUPIN-interní email relé).

| Č. | Artefakt | Účel | Kdy otevřít |
|----|----------|------|-------------|
| 1 | `bouracka-ui-hp-elite-v0.1.5-CS-multi-abi.zip` (jeden balíček, funguje na Python 3.10/3.11/3.12) | Hlavní UI balíček, air-gap-ready | **První.** Vyberte variantu odpovídající Vaší Python verzi (viz §2). |
| 2 | `bouracka-tests-source-v0.5.7.zip` | Zdrojový strom testovací sady (Cypress + Playwright + Selenium + workbook v0.4.4 + fixtures). Pro real-mode dispatch. | Druhé. Rozbalte vedle UI instalace. |
| 3 | `bouracka-tes-outputs-2026-05-15.zip` | Historické cross-framework reporty (Cíl-1 baseline 5P/5S) + binding schema spec | Třetí (volitelně). Pro inspekci minulých běhů bez nutnosti je opakovat. |
| 4 | `bouracka-diagnostics-supin-internal-2026-05-15.zip` | SUPIN-internal diagnostics companion (Pete pre-populated PUBLIC drift; SUPIN-secret bity Pete vyplní před dodávkou) | Pouze pokud nastane situace, kdy public DIAGNOSTICS-PLAYBOOK-CS.md nestačí. |
| — | `MANIFEST.txt + SHA256SUMS.txt` | SHA256 + velikosti všech ZIPů | Před instalací — ověřte integritu. |
| — | `KATE-FROM-ZERO-INSTALL-CS.md` (tento soubor) | Vy ho čtete | Teď. |


### §0.1 — Co je nové ve v0.1.5 (oproti v0.1.4, kterou jste měla naposledy)

Tato verze přináší **5 viditelných změn** v UI + workbooku. Žádná z nich nemění Váš instalační postup, ale stojí za to o nich vědět:

1. **Workbook se posunul na v0.4.4** (z v0.4.3). Přibyl list `02e_TestSteps` (krok-po-kroku rozpad testcase), sloupec `steps_count` na `02_TestCases`, a typované sloupce `evidence_*` na `08_Bugs` (původní `screenshot_ref`/`trace_ref` zůstávají kvůli zpětné kompatibilitě).

2. **Nový REST endpoint `GET /api/runs/{rid}/cross-check[.html]`** — cross-framework agreement report. Po doběhnutí runu klikněte na výsledkové stránce `Cross-framework check` pro JSON nebo `Stáhnout HTML` pro samostatný report, který můžete poslat e-mailem.

3. **3 další endpointy pro krok-po-krok detail**: `/api/tcs/{tc}/steps`, `/api/steps/{step_code}`, `/api/bugs/{bug}/evidence`. Postupně se napojí na UI v dalších verzích — zatím dostupné jen přes přímé volání pro Vaše recon.

4. **Nové prostředí `ENV-DMO-PUB`** v drop-downu (vedle ENV-PUB, ENV-TST, ENV-DMO). Public demo.bouracka.cz, supplemental-merged. Pro Vaše Cíl-2 smoke je užitečné, ale není povinné.

5. **CLI startup nyní explicitně ukazuje cestu k workbooku** — když spustíte `python -m bouracka_ui`, hned na druhé řádce vidíte `[bouracka-ui] workbook: C:\TestAutomationSite\BOURACKA-TESTPLAN-v0.4.4.xlsx`. Pomáhá to v případě, že máte více kopií workbooku (BUG-K-003 fix).

**Co se nezměnilo:** instalační kroky (§1..§5), Python virtual environment, port 8424, bug-filing workflow, governance "jeden workbook v kořeni instalace". Pokud jste na v0.1.4 a chcete jen v0.1.5 změny, stačí re-install per §4.

---

## §1. Před začátkem — sanity check Vaší HP Elite

Otevřete PowerShell (NE jako admin) a spusťte:

```powershell
# Pythonová verze (rozhodující pro výběr ZIPu)
python --version

# Místo na disku (potřeba ~500 MB pro celý ecosystem)
Get-PSDrive C | Select-Object Used, Free

# Verze PowerShellu (potřeba 5.1+; HP Elite typicky 5.1)
$PSVersionTable.PSVersion

# Síť (test že nemáme egress na PyPI — to je očekávané; chceme jistotu, že air-gap je aktivní)
Test-NetConnection pypi.org -Port 443 -InformationLevel Quiet
# Očekávaná odpověď: False  (nebo timeout) — to znamená, že air-gap funguje
```

**Pokud Python není nainstalovaný:** nainstalujte Python 3.12 z python.org (nebo z SUPIN-managed software repository). Při instalaci zaškrtněte „Add Python to PATH". Po instalaci znovu spusťte `python --version`.

**Pokud `Test-NetConnection pypi.org` projde** (vrátí True): air-gap NENÍ aktivní. To není blokující pro instalaci, ale informujte SUPIN SecOps — pravděpodobně je VPN nebo proxy nesprávně nastavena.

---

## §2. Výběr správné varianty ZIPu (Python ABI matching)

| Vaše `python --version` ukáže... | Vyberte ZIP |
|----------------------------------|-------------|
| `Python 3.10.x` | `bouracka-ui-hp-elite-v0.1.5-CS-multi-abi.zip` |
| `Python 3.11.x` | `bouracka-ui-hp-elite-v0.1.5-CS-multi-abi.zip` |
| `Python 3.12.x` | `bouracka-ui-hp-elite-v0.1.5-CS-multi-abi.zip` |
| Jiná verze | STOP — kontaktujte Peta (`petr.yamyang@gmail.com`). Pete přestaví wheelhouse pro Vaši verzi za ~30 s. |

**Důvod tří variant:** Python wheely pro C-rozšíření (httptools, watchfiles, pydantic_core, atd.) jsou ABI-specifické. Wheel pro cp310 se nenainstaluje na cp312. Documented jako KB-042 v CHANGELOG.

---

## §3. Ověření integrity ZIPů (SHA256 z manifestu)

Otevřete `MANIFEST.txt + SHA256SUMS.txt` a porovnejte SHA256 každého ZIPu, který budete extrahovat:

```powershell
# Pro Váš vybraný UI ZIP (příklad: py312):
Get-FileHash bouracka-ui-hp-elite-v0.1.5-CS-multi-abi.zip -Algorithm SHA256

# Output: hash hodnota — porovnejte se zápisem v MANIFEST.txt + SHA256SUMS.txt
```

Pokud SHA256 neodpovídá: NEINSTALUJTE. Kontaktujte Peta. ZIP byl po cestě poškozen nebo modifikován.

---

## §4. Instalace bouracka-ui (~5 minut)

### 4.1 Rozbalení

```powershell
# Vytvořte pracovní adresář (doporučeno)
New-Item -ItemType Directory -Path C:\TestAutomationSite -Force | Out-Null
cd C:\TestAutomationSite

# Rozbalte UI ZIP (příklad pro py312)
Expand-Archive ..\Downloads\bouracka-ui-hp-elite-v0.1.5-CS-multi-abi.zip . -Force

# Ověřte obsah
Get-ChildItem
# Očekávané: bouracka_ui-0.1.5-py3-none-any.whl, wheelhouse/,
#            BOURACKA-TESTPLAN-v0.4.4.xlsx, INSTALL-HP-ELITE-CS.txt,
#            OPERATOR-GUIDE-CS.md, TROUBLESHOOTING-CS.md,
#            DIAGNOSTICS-PLAYBOOK-CS.md, kill-stragglers.ps1, SHA256SUMS.txt
```

### 4.2 Python virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
# Prompt se změní na "(.venv) PS C:\TestAutomationSite>"
```

Pokud `Activate.ps1` selže s „execution of scripts is disabled":

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
# Potvrďte Y. Pak znovu Activate.ps1.
```

### 4.3 Instalace wheelu z lokálního wheelhouse

```powershell
pip install --no-index `
  --find-links="C:\TestAutomationSite\wheelhouse" `
  "C:\TestAutomationSite\bouracka_ui-0.1.5-py3-none-any.whl"
```

**Klíčové:**
- `--no-index` — zakazuje pipu kontaktovat PyPI (potvrzuje air-gap)
- `--find-links=<absolutní cesta>` — ukazuje na lokální wheelhouse
- Cesta k wheelu musí být **absolutní** (pip na Windows je citlivý na `.\`)

Očekávaný výstup: ~28 balíčků „Successfully installed". Včetně `bouracka-ui-0.1.2`, `fastapi`, `uvicorn`, `openpyxl`, `sse-starlette`, `python-multipart`, `pytest`, `pytest-json-report` a tranzitivních deps.

### 4.4 Smoke check instalace

```powershell
bouracka-ui --help
# Očekávané: banner s nápovědou, parametry --port, --workbook, --runs-dir, --no-browser, --reload
```

Pokud `bouracka-ui` není nalezen jako příkaz: venv pravděpodobně není aktivován. Spusťte `.\.venv\Scripts\Activate.ps1` znovu.

---

## §5. Rozbalení testovací sady (~2 minuty)

```powershell
cd C:\TestAutomationSite
Expand-Archive ..\Downloads\bouracka-tests-source-v0.5.7.zip .\tests-source -Force

# Ověřte
Get-ChildItem .\tests-source
# Očekávané (v0.5.7+): cypress/, playwright/, selenium/, tools/, fixtures/,
#            _specs/, _install/, recon/ (filtrované), BUILD-STAMP.txt,
#            README.md
# POZOR: BOURACKA-TESTPLAN-v0.4.4.xlsx je v `tests-source/` NEPŘÍTOMNÝ
# počínaje v0.5.6 (BUG-K-003 fix). Jediný platný workbook je v UI install
# rootu: `C:\TestAutomationSite\BOURACKA-TESTPLAN-v0.4.4.xlsx`. bouracka-ui
# četí + zapisuje právě a pouze do tohoto souboru.
```

**Cypress a Playwright** mají Node.js dependencies. Pokud chcete je spouštět real-mode (NE mock), bude potřeba:
- Node.js 18+ nainstalovaný (z nodejs.org nebo SUPIN-managed software repo)
- `npm install` uvnitř `tests-source/cypress/` a `tests-source/playwright/`
- `npx playwright install` (stáhne browser binaries — vyžaduje internetový egress, jednorázově)

**Selenium** funguje out-of-the-box z UI wheelhouse — pytest+selenium+webdriver-manager jsou už nainstalované.

---

## §6. První běh — smoke test v mock módu (~3 minuty)

Mock mode prokáže, že UI plumbing funguje, BEZ nutnosti instalovat Cypress/Playwright/Selenium runners. Po této kontrole budete vědět, že problém (pokud nějaký nastane v real módu) leží v runnerech, ne v UI samotném.

V terminálu s aktivovaným venv:

```powershell
$env:BOURACKA_UI_DISPATCH_MODE = "mock"
# Real-mode dispatch potřebuje znát kde je test-suite source pro spawn
# cypress / playwright / selenium subprocesů. Workbook je VŽDY v UI rootu
# (BUG-K-003 fix v v0.1.4) — repo_root jen ukazuje na tests-source pro dispatch:
$env:BOURACKA_UI_REPO_ROOT = "C:\TestAutomationSite\tests-source"
bouracka-ui --no-browser
```

**Pozor — single-source-of-truth workbook (BUG-K-003 fix, v0.1.4+):**

Bouračka UI má JEDEN authoritative workbook na vaší HP Elite:

```
C:\TestAutomationSite\BOURACKA-TESTPLAN-v0.4.4.xlsx   ← jediný platný
```

Když chcete zkontrolovat založené bugy v Excelu, otevřete VŽDY tento soubor.
Pokud byste viděli další `BOURACKA-TESTPLAN-*.xlsx` kdekoliv jinde (např.
`tests-source/` z předchozích verzí balíčku), jsou to staré reference-only
kopie — UI je nepoužívá a nikdy do nich nezapíše.

Při startu bouracka-ui vypíše do konzole konkrétní cestu k workbooku, který
používá. Ten řádek si přečtěte hned po `bouracka-ui` startu:

```
[bouracka-ui] workbook:   C:\TestAutomationSite\BOURACKA-TESTPLAN-v0.4.4.xlsx
[bouracka-ui] ⚠  open ONLY this workbook in Excel for bug review;
```

Server se rozběhne na `http://127.0.0.1:8424/`. Otevřete URL v prohlížeči (Edge nebo Chrome — Firefox v poslední verzi taky).

V prohlížeči:

1. Stránka **Run tests**: nechte „ENV-DMO — Demo (demo.bouracka.cz)" a framework „all"
2. Sjeďte dolů, zaškrtněte **TC-CP-A1-MAIN-DEMO** (nebo TC-CP-001 bring-up-smoke)
3. Klikněte **Run selected**
4. Po ~3 s se objeví výsledková matice se syntetickými výsledky. Cross-framework verdict = `agree`. To je očekávané v mock módu.

UI plumbing potvrzeno. Zastavte server přes Ctrl+C.

---

## §7. První bug-filing rehearsal (~2 minuty)

V real distribuci budete zakládat bugy proti workbook v0.4.4. Otestujme to teď:

```powershell
bouracka-ui --no-browser
# (mock mode by měl být ještě nastavený z §6 — pokud ne, znovu:
#  $env:BOURACKA_UI_DISPATCH_MODE = "mock")
```

V prohlížeči:

1. Stránka **Bugs** → **+ New Bug**
2. Vyplňte:
   - Summary: `Smoke from Kate's HP Elite — install validation`
   - Severity: `low`
   - Status: `closed`
   - Description: `Bug-filing rehearsal per KATE-FROM-ZERO-INSTALL-CS.md §7. Smoke install successful. No actual bug.`
3. Klikněte **Submit**.
4. **Důležité:** Excel s `BOURACKA-TESTPLAN-v0.4.4.xlsx` MUSÍ být zavřený (jinak openpyxl write selže s `WorkbookLockedError 409`).

Bug se zapíše do `08_Bugs` listu workbooku s auto-incremented kódem `BUG-XXX`. Otevřete workbook ručně v Excelu pro ověření.

Po ověření smažte rehearsal bug ručně z workbooku (nebo ho ponechte se statusem `closed` jako trail).

---

## §8. Real-mode dispatch (kdy budete připraveni)

Až budete chtít skutečné běhy proti `demo.bouracka.cz`:

```powershell
Remove-Item Env:BOURACKA_UI_DISPATCH_MODE
# BOURACKA_UI_REPO_ROOT necháme — ukazuje na tests-source
bouracka-ui --no-browser
```

Cíl 1 (DEMO `demo.bouracka.cz`) baseline = 5P/5S (5 testů passed, 5 drift-skip). Pokud uvidíte jiný výsledek, zkontrolujte:

- **Síť** — máte dosah na `demo.bouracka.cz`? `Test-NetConnection demo.bouracka.cz -Port 443`
- **Drift stav** — `DEMO-POST-REPORTS-403` drift je očekávaný. Viz DIAGNOSTICS-PLAYBOOK §3 a SUPIN-internal companion §5.
- **Workbook lock** — Excel zavřený? `Get-ChildItem .~lock.* -Force` v workbook adresáři by neměl nic vrátit.

---

## §9. Eskalace + reportování problémů zpět

Pokud něco selže způsobem, který tato runbook nepokrývá:

1. **Trace bundle export** — uvnitř UI běhu, stránka `/runs` → vybraný běh → **Export trace bundle**. Stáhne ZIP s logy + screenshoty + envelope.json.
2. **Diagnostics snapshot** — pokud UI samotné nereaguje: v jiném okně PowerShellu `curl http://127.0.0.1:8424/api/diagnostics/snapshot > snapshot.json` (no-run state dump).
3. **DELTA-REPORT** — vyplňte šablonu z DIAGNOSTICS-PLAYBOOK-CS.md §7.2 a pošlete:
   - Pete (`petr.yamyang@gmail.com`) — pro UI samotné / drift / parity questions
   - SUPIN SecOps — pro cert / network / proxy issues (kontakty v SUPIN-internal companion §6)

---

## §10. Odinstalace (až bude potřeba)

```powershell
# Deaktivace + smazání venv
deactivate
Remove-Item .venv -Recurse -Force

# Celá pracovní složka — pokud chcete čistý odchod
cd ..
Remove-Item C:\TestAutomationSite -Recurse -Force
```

Nic globálně nainstalováno není (vše uvnitř venv). Žádný registr modifikován, žádné systémové komponenty.

---

## §11. Checklist před hlášením úspěchu

- [ ] §1: HP Elite preflight prošel (Python ≥3.10, místo na disku, air-gap potvrzen)
- [ ] §2: Vybrán správný ZIP variant pro Vaši Python ABI
- [ ] §3: SHA256 všech používaných ZIPů odpovídá manifestu
- [ ] §4.4: `bouracka-ui --help` ukazuje banner
- [ ] §5: tests-source rozbalen, obsah ověřen
- [ ] §6: smoke test v mock módu ukázal verdikt matrix
- [ ] §7: rehearsal bug napsán do workbooku (pak smazán nebo closed)
- [ ] §9 (volitelně): Trace bundle export funguje na rehearsal běhu

Po odškrtnutí celého §11: pošlete Petovi krátký mail „Kate from-zero install: PASS" s případnými poznámkami. Tím je Kate v provozu.

---

**Konec runbooku.** Verze 2026-05-15 (v0.1.5).
