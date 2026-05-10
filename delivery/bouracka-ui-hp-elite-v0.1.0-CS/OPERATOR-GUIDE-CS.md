# Bouračka UI v0.1.0 — Příručka pro operátora (CS)

**Cílová skupina:** testeři, kteří budou bouracka-ui každodenně používat k řízení Cypress / Playwright / Selenium běhů proti prostředím bouracka.cz.
**Předpoklad:** dokončená instalace podle `INSTALL-HP-ELITE-CS.txt`.

---

## §1. Každodenní workflow v kostce

Očekávaná smyčka:

1. Spusťte UI: `bouracka-ui` (nebo `bouracka-ui --no-browser`, pokud nechcete automaticky otevírat prohlížeč).
2. Vyberte prostředí + framework(y) + podmnožinu TC na stránce **Run**.
3. Klikněte na **Run selected**, sledujte živý log.
4. Po dokončení běhu se dostanete na **Results** — projděte verdiktovou matici.
5. Pro každé selhání klikněte v řádku na **+ bug** → vyplní formulář Bugs s předvyplněným TC/env/run.
6. Volitelně: exportujte **trace bundle** ZIP z hlavičky stránky Results (pro sdílení kompletního stavu běhu s jiným testerem nebo pro archivaci).

Server zastavte **Ctrl+C** v okně PowerShellu, až s tím skončíte.

---

## §2. Stránky — k čemu slouží

### 2.1 `/run` — Výběr + spuštění

- **Environment** dropdown — mapuje na list `04_TestEnvironments` workbooku (ENV-DMO / ENV-TST / ENV-PUB). Base URL (`demo.bouracka.cz`, `tst.bouracka.cz`, `www.bouracka.cz`) se zobrazí pod dropdownem.
- **Framework(s)** — `all` spustí Cypress + Playwright + Selenium sekvenčně (pomalejší; užitečné pro cross-framework parity kontroly). Single-framework běhy jsou rychlejší.
- **Mřížka test casů** — filtrovaná podle prostředí. Každý řádek ukazuje kód TC + pilulku severity (A/B/C/X) + prioritu. Zaškrtněte boxy u TC, které chcete spustit. **Select all** / **Clear** tlačítka jsou nad mřížkou.
- **Run selected** spustí dispatch. Karta **Live log** se rozbalí a streamuje stdout z každého frameworku, jak se vykonává.

### 2.2 `/results/<run_id>` — Verdiktová matice + zkratka pro založení bugu

Po dokončení běhu se sem dostanete automaticky. Stránka ukazuje:

- **Summary chipsy:** celkem TC, pass/fail/skip, soft-pass, strict + drift-aware pass-rate, parity-divergence count.
- **Verdiktová matice:** jeden řádek na TC × jeden sloupec na framework. Buňky zobrazují `pass` / `fail` / `skip-drift` / `skip-other` / `soft-pass` / `error` / `missing`. Sloupec Parity status říká, zda se všechny frameworky shodly.
- **Karta Drift forensic** (viditelná jen když byl detekován drift) — ukáže typ (např. `recaptcha-v3`), dotčené TC a poznámky.
- **+ bug** odkaz v každém failed řádku — otevře formulář Bugs s předvyplněným TC / run-id / env. Rychlejší než ručně psát.
- **Export bundle** / **Export bundle (full)** tlačítka v hlavičce — vyrobí ZIP s envelopem + manifestem + logy (+ video a trace pro „full" variantu) pro přenos běhů mezi stroji bez GitHubu.

**Pokud se sem dostanete, když běh ještě probíhá** (např. otevřete URL z bookmarku nebo dispatch trval déle, než jste očekávali), stránka zobrazí pilulku statusu "running" a auto-pollne každé 2 s, dokud není envelope připravený. Stačí nechat záložku otevřenou a stránka automaticky přejde na plné zobrazení výsledků. (Oprava BUG-BUI-002 v v0.1.0.)

### 2.3 `/runs` — Seznam minulých běhů

- Jeden řádek na minulý běh (seřazeno nejnovějším). Ukazuje started_at, env, total/pass/fail/skip počty, parity-divergence count a run_id.
- Klikněte na libovolný řádek pro detail výsledků.
- Filtr **Env** + **Last NN runs** + **Refresh** kontroly nahoře.
- **⬆ Import bundle** umožňuje načíst trace-bundle ZIP z jiného stroje (např. air-gap workflow HP Elite). Po importu se objeví v tomto seznamu.
- **⬇ Diagnostics** stáhne no-run diagnostický snapshot (health + system info + tool versions). Užitečné při hlášení „UI nefunguje" — připojte tento snapshot k bug reportu.

### 2.4 `/bugs` — Tracker bugů (zapisuje zpět do workbooku)

- Jeden řádek na bug z listu `08_Bugs` workbooku.
- **Filtr status** (open/closed/investigating) + **filtr severity** (A/B/C/X) nahoře.
- **+ New Bug** otevře inline formulář. Povinná pole: Title + Severity. Auto-vyplněno, pokud jste sem přišli přes `+ bug` z failed result řádku.
- Založení bugu přidá řádek přímo do workbooku. Pokud Excel má workbook otevřený, dostanete 409 s „Workbook locked" — zavřete Excel a zkuste znovu.

### 2.5 `/about` — Dostupnost nástrojů + health check

Nejužitečnější stránka, když něco nefunguje. Zobrazuje:

- Verze serveru + schématu.
- Cestu k workbooku + zda je nalezen.
- Adresář runs.
- Dostupnost nástrojů: npx, python, consolidator (`tools/consolidate_results.py`). **Cokoli červené znamená, že dispatch padne do mock mode nebo přeskočí ten framework.**

---

## §3. Dispatch módy — real vs mock

Defaultně bouracka-ui auto-detekuje dostupné nástroje:

- **Real mode:** vyvolá `npx cypress run`, `npx playwright test`, `pytest selenium/tests/`, pak `tools/consolidate_results.py` k sloučení výsledků.
- **Mock mode:** syntetizuje falešné výsledky (1 fail na ALT-4 cypress, 1 skip-drift na ALT-1 atd.) — užitečné pro demo a iteraci UI bez skutečného spouštění prohlížečů.

Vynutit mock mode pro session přes env proměnnou (PowerShell):

```powershell
$env:BOURACKA_UI_DISPATCH_MODE = "mock"
bouracka-ui
```

Návrat do real mode: `Remove-Item Env:BOURACKA_UI_DISPATCH_MODE` a restart serveru.

---

## §4. Trace bundle (air-gap workflow HP Elite)

Když nemůžete push výsledků na GitHub nebo sdílet přes síťový disk (typický scénář SUPIN HP Elite), trace bundly jsou cesta ven.

**Export** (na zdrojovém stroji):
1. Otevřete `/results/<run_id>` pro běh, který chcete sdílet.
2. Klikněte na **⬇ Export bundle** (lightweight: envelope + logy + manifest, ~50 KB) nebo **⬇ Export bundle (full)** (zahrnuje video + Cypress trace, několik MB).
3. Uložte ZIP. Filename: `trace-bundle-run-...-<7hex>.zip`.
4. Přeneste na cílový stroj přes USB / email / Slack atd.

**Import** (na cílovém stroji):
1. Otevřete `/runs`.
2. Klikněte na **⬆ Import bundle**.
3. Vyberte ZIP.
4. Stránka auto-navigates na výsledky importovaného běhu.

Import je idempotentní (re-import stejného bundlu je no-op) a validovaný (odmítne ZIPy bez `manifest.json` nebo s jiným `bundle_format_version`).

---

## §5. Konvence pro zakládání bugů

Když kliknete `+ bug` z failed result řádku, formulář se otevře s předvyplněným TC + env + run. Vyplňte:

- **Title (English)** — krátký a popisný. Příklad: `TC-CP-A2-ALT-1 cypress: reCAPTCHA blocks submit at step 3`.
- **Severity** — A (kritická: blokuje všechno testování), B (vysoká: blokuje flow), C (nízká: kosmetická / okrajová), X (nedefinovaná / triage).
- **Linked TC code** — předvyplněno. Nechte.
- **Reproduction steps** — stručný číslovaný seznam stačí.
- **Expected / Actual** — krátké odstavce. Verdiktová matice už zachycuje pass/fail, takže tohle je pro lidsky čitelný kontext.

Kód bugu (`BUG-NNN`) je auto-přidělen workbookem (další volné celé číslo v listu `08_Bugs`).

---

## §6. Čisté zastavení

**Vždy Ctrl+C** server v okně PowerShellu předtím, než to okno zavřete. Pokud okno jen zavřete bez Ctrl+C, uvicorn worker subproces může přežít a držet port 8424 + websockets DLL zamčené — což zabrání dalšímu startu (a dalšímu `pip install`).

Pokud se to stane, spusťte `kill-stragglers.ps1` (přibalený v balíčku). Recept viz TROUBLESHOOTING-CS.md §1.

---

## §7. Co kde žije na disku

```
C:\bouracka-ui\
├── .venv\                              ← virtual environment (nehrabat)
├── bouracka_ui-0.1.0-py3-none-any.whl  ← instalační wheel
├── BOURACKA-TESTPLAN-v0.4.2.xlsx       ← workbook (datový zdroj: TC, prostředí, bugy)
├── runs\                               ← envelope JSON sem padají
│   └── cross-framework-demo-2026-05-11.json
├── imported-bundles\                   ← trace bundly importované přes /runs
├── INSTALL-HP-ELITE-CS.txt
├── OPERATOR-GUIDE-CS.md                ← tento soubor
├── TROUBLESHOOTING-CS.md
├── kill-stragglers.ps1
└── SHA256SUMS.txt
```

Workbook je **zdrojem pravdy** pro TC, prostředí a bugy. Adresář `runs/` je **historie provádění**. Oboje by mělo být periodicky zálohováno (USB stick stačí).

---

## §8. Hlášení problémů s bouracka-ui samotnou

Pokud je něco v UI rozbité (ne jen test failure), založte to jako **BUG-BUI-NNN** přes stránku Bugs. Zahrňte:

- Co jste klikli.
- Co jste očekávali.
- Co se stalo.
- Diagnostický snapshot (`/runs` → ⬇ Diagnostics) připojený, pokud možno.

Dojdou ke mně (Pete) a budou zpracovány do dalšího vydání bouracka-ui.

---

## §9. Historie verzí

- **v0.1.0** (2026-05-10) — první vydání. Obsahuje opravu BUG-BUI-001 (Windows NTFS filename safety pro run_id) a opravu BUG-BUI-002 (202 in-flight sémantika + UI polling pro zabránění přechodným „Run not found" stránkám).

Konec OPERATOR-GUIDE-CS.md
