# Bouračka UI v0.1.0 — Diagnostický playbook (CS)

**Cílová skupina:** testeři na HP Elite SUPNB001 (nebo jiném testovacím notebooku), kteří potřebují diagnostikovat problémy, které nejsou zjevně chybou UI — drift, neshody integrací, network egress, certifikační důvěra, mock-vs-live nejednoznačnosti.
**Doprovodné dokumenty:** `OPERATOR-GUIDE-CS.md` (jak používat UI) a `TROUBLESHOOTING-CS.md` (co dělat, když UI samotné nefunguje). Tento playbook je třetí pilíř: **co dělat, když nefunguje systém kolem UI.**
**Optimalizováno pro:** přenos ThinkPad ↔ HP Elite je labour-intensive (pouze e-mail, ≤5 MB volumes podle IOC packaging pravidel). Každá sekce níže říká, jak strukturovaně zachytit nález, který se vejde do jednoho nebo dvou e-mailů.

**Confidence tagy používané v §3 a §4** (přečtěte si nejdřív):

- ⌖ — **známé**, zachyceno v analytických dokumentech CP-SUPIN-03..04
- ◯ — **odvozeno**, nejlepší odhad z reconu; ověřit při prvním kontaktu
- ✗ — **gap**, zatím nezachyceno; tester musí doplnit přes DELTA-REPORT (§7)

---

## §1. System fingerprint — co zachytit při prvním kontaktu

`bouracka-ui` exponuje `/api/diagnostics/snapshot` (na stránce `/runs` → tlačítko ⬇ Diagnostics). Vyrobí ZIP obsahující:

| Položka | Co ukazuje | Proč na tom záleží |
|---------|------------|---------------------|
| `manifest.json` | Verze bundlu + timestamp + run_id (pokud nějaký) | Jednoznačně identifikuje snapshot; cituj tento hash při zpětném e-mailu |
| `health.json` | Verze serveru + schema + cesta workbooku + cesta runs-dir | Potvrzuje, že instalace správně vyřešila REPO_ROOT (hledej `bouracka-tests/` v cestách, NIKOLI `.venv/`) — viz BUG-BUI-004 |
| `system/system.json` | OS verze, hostname, Python verze, volné místo | Baseline pro kompatibilitní kontroly |
| `system/tool-versions.txt` | Stav detekce `npx`, `node`, `python`, `pytest`, `consolidate_results.py` | Cokoli červené → viz §3 co selže |
| `system/health.json` | Snapshot dostupnosti nástrojů (npx / playwright / cypress / consolidator detection) | Stejná data jako stránka `/about`, zachycena do bundlu |
| `server-log.txt` (posledních 5000 řádek) | Nedávný stderr serveru | Obsahuje startup zprávy + jakékoli tracebacky |
| `README.md` | Self-describing layout bundlu | Pete může re-import bez kontextu |

**Kdy ho pořídit:** před prvním TST během na novém stroji, po jakémkoli „tohle je divné" momentu, když e-mailuješ Petovi otázku ohledně chování. Bundle je `~50 KB`, hluboko pod 5 MB IOC-aware e-mailovým limitem.

---

## §2. Network reachability matrix — podle prostředí

Každé prostředí vyžaduje specifickou sadu egress cest. Selhání dosažení jakéhokoli povinného cíle produkuje charakteristický symptom v logu bouracka-ui. Použij tabulku k mapování symptom → pravděpodobná root cause.

> **Two-tier confidentiality split:** SUPIN-interní hostnames / IPs / cert detaily / mock URLs **záměrně nejsou v tomto dokumentu**. Žijí v **SUPIN-interním companionu** (`DIAGNOSTICS-PLAYBOOK-SUPIN-INTERNAL.md`, udržováno Petem ze šablony v `_specs/SUPIN-INTERNAL-companion/`), který se distribuuje přes SUPIN-controlled secure channels — přímé předání, šifrovaný USB nebo SUPIN-interní e-mail. **NIKDY nežádej o SUPIN-interní companion přes externí e-mailový relay.** `<FILL-IN-LOCAL>` placeholdery níže jsou švy, kde se dvě úrovně propojují: čti tento veřejný dokument + cross-reference stejně číslovaný řádek v interním companionu. Pokud companion na HP Elite nemáš, požádej Peta přes SUPIN-interní kanál.

| Env | Cíl (role) | Proč | Jak ověřit (PowerShell) | Symptom při zablokování |
|-----|------------|------|--------------------------|--------------------------|
| DEMO | `demo.bouracka.cz` (veřejný, HTTPS 443) | Primární DEMO provoz | `Test-NetConnection demo.bouracka.cz -Port 443` | Cypress / Playwright connect-timeout |
| DEMO | `www.google.com/recaptcha/api2` (HTTPS) | Načítání reCAPTCHA challenge | `Test-NetConnection www.google.com -Port 443` | reCAPTCHA se nikdy nevyřeší; submit formuláře visí |
| DEMO | `fonts.googleapis.com` (HTTPS, volitelné) | Web fonty; web se načte i bez | — | Pouze kosmetické |
| TST | `tst.bouracka.cz` (intranet, HTTPS 443) | Primární TST provoz; vyžaduje SUPIN LAN / VPN | `Test-NetConnection tst.bouracka.cz -Port 443` | Connection refused / timeout = NEJSI na správné síti |
| TST | `<FILL-IN-LOCAL>` — IS ČKP API host | Reálný ČKP backend integration | naplň `_local-config.txt` | 5xx na POST /api/reports |
| TST | `<FILL-IN-LOCAL>` — AISPOV API host | Driver license lookup | naplň `_local-config.txt` | TC krok „verify driver" visí |
| TST | `<FILL-IN-LOCAL>` — zenID host | Skenování ID dokumentů | naplň `_local-config.txt` | „Cannot upload ID" chyba u photo kroku |
| TST | `<FILL-IN-LOCAL>` — N8 SMS gateway | SMS verifikace telefonu | naplň `_local-config.txt` | SMS code pole zůstává prázdné; timeout |
| UAT | (stejný tvar jako TST, jiné hosty) | — | naplň `_local-config.txt` | — |
| PROD | `www.bouracka.cz` (veřejný, HTTPS 443, ČTECÍ pouze testy) | Produkční read-only smoke | `Test-NetConnection www.bouracka.cz -Port 443` | Stejné jako DEMO |

**Konvence `_local-config.txt`** — vytvořte tento soubor v kořeni bouracka-tests (NIKOLI committovat do gitu) a naplň `<FILL-IN-LOCAL>` placeholdery pro konkrétní instalaci testera. Formát:

```
# _local-config.txt — local-only env-specific hostnames
# Do NOT commit. Každý notebook testera má své vlastní hodnoty.
TST_CKP_API_HOST=...
TST_AISPOV_HOST=...
TST_ZENID_HOST=...
TST_N8_SMS_HOST=...
UAT_...=...
```

Tento soubor je čten testovacími skripty přes standardní env-var loading pattern. Přidej ho do `.gitignore`, pokud tam ještě není (v v0.1.0+ je).

---

## §3. Integration contracts — live vs mock podle prostředí

DEMO prostředí je **podstatně mockováno**. TST je „real-ish" — některé backendy jsou live (staging), některé jsou stále mockované. PROD je plně live, ale read-only pro testování. Tato tabulka je empirický záznam z CP-SUPIN-03..04 reconu. **Legenda tagů v §0.**

| Integrace | DEMO | TST | UAT | PROD | Poznámky |
|-----------|------|-----|-----|------|----------|
| **IS ČKP report API** (POST /api/reports) | ⌖ mockováno přes Mockoon — přijímá libovolný payload, vrací success | ⌖ live (staging ČKP API) — schema-validuje, vrací reálné bug-IDs | ◯ live (UAT staging) | ⌖ live (PROD), read-only access přes testy | DEMO mock přijímá garbage; TST odmítá malformované payloady → reálné schema testování se děje tady |
| **AISPOV driver lookup** | ⌖ mockováno — vrací fixture řidiče podle vstupního ID patternu | ◯ live staging — reálný DB lookup; může odmítnout neznámá IDs | ✗ gap — ověřit při prvním TST→UAT průchodu | ⌖ live | TC-CP-A1 + ALT-2/3 cesta potřebuje real-ish driver IDs v TST |
| **zenID ID-document scan** | ⌖ stubováno — file upload akceptován, žádné skutečné OCR | ◯ live staging zenID — dělá reálné OCR; může selhat u špatných fotek | ✗ gap | ⌖ live | DEMO photo-skip TCs prochází triviálně; TST photo TCs vyžadují čitelné fotky |
| **N8 SMS gateway** | ⌖ no-op — SMS-code pole se auto-vyplní `123456` | ◯ live N8 staging — reálné SMS odesláno na testovací telefony | ✗ gap | ⌖ live | TST: vyžaduje reálné test SIM karty; konfiguruj `TST_N8_TEST_PHONES=...` |
| **reCAPTCHA v3** | ◯ zapnuto některé dny, vypnuto jiné (DEMO drift) | ⌖ zapnuto (KB-CY-001 známý zdroj driftu) | ◯ pravděpodobně zapnuto | ⌖ zapnuto | Hlavní zdroj driftu — viz §4 |
| **Cookie banner** | ⌖ přítomný při prvním loadu; dismissable | ⌖ přítomný | ◯ přítomný | ⌖ přítomný | Auto-dismissed Cypressem/Playwrightem ve v0.4.7+ |
| **Mockoon mock server** | ⌖ běží lokálně během testů; porty `:3000`/`:3001` | ✗ N/A — TST používá reálné backendy | ✗ N/A | ✗ N/A | Pokud Mockoon neběží v DEMO, testy selhávají s `ECONNREFUSED` na mock endpointech |

**Kde jsou gapy (✗ řádky):** UAT prostředí je nejméně prozkoumáno; TST má hodně `◯`, protože jsme zatím nepustili live. **Pete zmíněná TST integration session je to, co tyto gapy uzavře.** Zachyť každý `◯ → ⌖ (verified live)` nebo `◯ → ✗ (broken, file BUG-*)` nález pomocí §7 DELTA-REPORT.

---

## §4. Známé drift patterny — symptom katalog

Když testy selhávají způsobem, který NENÍ reálná regrese, je to obvykle drift. Bouracka-ui má vestavěnou drift forensic, která některé z těchto automaticky flagne (verdict = `skip-drift`). Jiné vyžadují manuální rozpoznání.

| Drift pattern | Symptom v test logu | Root cause | Očekávaná reakce | Reference |
|---------------|---------------------|------------|-------------------|-----------|
| **reCAPTCHA v3 invisible-challenge** | Submit formuláře visí v kroku „submit"; tlačítko `submit` zůstává disabled; žádná změna DOM po >5s | Google challenge triggered; Cypress to neumí vyřešit | `verdict = skip-drift`; NEzakládat BUG; zkontrolovat drift forensic card na stránce výsledků | KB-040 / BUG-CY-001 IPC-114 evidence |
| **AISPOV mock vrací neočekávanou fixture** | Driver-lookup krok uspěje, ale vrácená data neodpovídají vstupnímu ID | Mockoon fixture out-of-date s TC očekáváními | Aktualizovat Mockoon fixture nebo TC očekávání | CP-SUPIN-03 STEP 4 + analyticke vstupy/ snippets |
| **zenID stub bypassed** | Photo upload uspěje s jakýmkoli souborem (i neimage) | DEMO mód přeskakuje reálné OCR | Očekáváno na DEMO. Na TST, pokud projde stejné, eskalovat. | CP-SUPIN-04 STEP 5 delta matrix |
| **N8 SMS auto-code `123456`** | SMS-code pole už vyplněné při dosažení | DEMO no-op gateway | Očekáváno na DEMO. Na TST/UAT musí přijít z reálného SMS. | CP-SUPIN-04 STEP 5 |
| **DEMO POST /api/reports 403** | ALT-9 selže s 403 Forbidden | DEMO API endpoint vypnutý některé dny | `verdict = skip-drift`; zaznamenat den výskytu | ALT-9 diagnosis 2026-05-XX |
| **Page error timeout chain** | a1-main / ALT-1/4/5 selhávají v „navigate to /error/timeout" | DEMO routing quirk | Aplikovat v0.4.7 timeout-handler fix; pokud přetrvává, eskalovat | `/error/timeout chain` diagnosis |
| **Cookie banner blokuje click** | První klik na jakékoli formulářové pole mine; banner zachytí | Banner ještě neodmítnutý | Pre-test cookie-banner-dismiss běží automaticky v v0.4.7+ | CP-SUPIN-04 STEP 23 |
| **TC selector strict-mode violation** | „ALT-6 200 000 Kč selector matches 2+ elements" | DEMO vykreslil více cenových štítků | Použít `.first()` nebo přísnější selektor | KB-CY-002 (existující) |

**Přidávání nového drift patternu:** pokud objevíš opakovaný failure, který není v této tabulce, zachyť přes §7 DELTA-REPORT. Pete to vrátí do tohoto katalogu v další iteraci balíčku.

---

## §5. Diagnostické nástroje — v pořadí priority

Když něco selže, choď tímto žebříkem shora dolů. Zastav se na první úrovni, která dá jasnou odpověď.

1. **Stránka `/about` v bouracka-ui** — okamžitý snapshot dostupnosti nástrojů. `npx` červený? Cypress nepůjde dispatchovat. `consolidate_results` červený? REPO_ROOT špatně detekován → viz TROUBLESHOOTING §4 (c).
2. **Log tail stránky výsledků (dispatch-failed view)** — seznam čtyř kandidátů příčin tě dovede ke správné root cause pro většinu selhání (viz TROUBLESHOOTING §4).
3. **`/api/diagnostics/snapshot` ZIP** — pořiď při jakémkoli „tohle je divné" momentu. ~50 KB. Přilož k e-mailu při eskalaci.
4. **Browser DevTools — Network tab** — pro jakoukoli HTTP-úrovňovou záhadu: které requesty letěly, status kódy, response časy, CORS preflighty. F12 → Network → reprodukuj problém → screenshot nebo „Save all as HAR".
5. **Browser DevTools — Console tab** — pro JS chyby. Bouracka-ui SPA loguje API errors do console.
6. **Trace bundle export (lightweight)** — Stránka výsledků → ⬇ Export bundle. Dá envelope + log + manifest v jednom ZIPu. Pošli e-mailem Petovi; on `/api/bundles/import`-ne na ThinkPadu a má plný kontext za 30 sekund.
7. **Trace bundle export (full)** — totéž, ale přidá video + Cypress trace.zip. Několik MB; může narazit na IOC packaging limit; rozděl do volumes (viz EMAIL-DELIVERABILITY-RULES, pokud se posílá zvlášť).
8. **IPC-114 Chromium diagnostic methodology** — last resort pro tvrdohlavé Cypress hangs. Spusť Cypress headed, otevři Chrome DevTools, inspect IPC channel 114 pro same-origin persistent connection state. Dokumentováno v BUG-CY-001 Round-4 evidence parked at `_specs/`.

---

## §6. Pre-flight checklist — před prvním TST během na novém notebooku

Projdi tento seznam jednou per notebook (nebo per významnou změnu SUPIN sítě). Odškrtni každou položku, jak ji potvrdíš.

- [ ] Notebook na SUPIN LAN nebo VPN (`ipconfig` ukazuje očekávaný interní subnet)
- [ ] `Test-NetConnection tst.bouracka.cz -Port 443` uspěje
- [ ] Každý `<FILL-IN-LOCAL>` cíl v §2 řádku dosažitelný (spusť test pro každý řádek)
- [ ] Certifikační důvěra: otevři `https://tst.bouracka.cz` v prohlížeči, žádný cert-error interstitial
- [ ] `_local-config.txt` naplněn všemi vyžadovanými env-specific hostnames
- [ ] `bouracka-ui` spuštěné, na stránce `/about` všechny nástroje zelené (nebo žluté s dokumentovaným `BOURACKA_UI_DISPATCH_MODE=mock` override, pokud real dispatch není potřeba)
- [ ] Diagnostics snapshot pořízen + uložen jako baseline (uložit jako `baseline-snapshot-YYYY-MM-DD.zip` někam — dokazuje „takhle vypadalo 'funkční'", kdybys potřeboval A/B-srovnání později)
- [ ] Jeden DEMO smoke test run úspěšný (TC-CP-A1-MAIN-DEMO) pro potvrzení UI plumbingu před zaměřením na TST
- [ ] Jeden TST smoke test run — zaznamenat exit kódy per framework + jakékoli drift forensic flagy
- [ ] Pokud cokoli v běhu se liší od §3 kontraktu pro TST, **DELTA-REPORT to** (další sekce) — nepředpokládej, že je to „v pohodě, asi flaky test"

---

## §7. Delta-capture — jak efektivně poslat nález zpět na ThinkPad

### §7.1 Pro TC failures — trace bundle (in-band, preferováno)

Trace bundle export je tvůj default channel. Zachycuje envelope + log + manifest + (volitelně) video v self-describing ZIPu, který si Pete může `/api/bundles/import`-nout pro reprodukci na ThinkPadu.

Kroky:
1. Reprodukuj selhání (nebo použij existující failed run z `/runs`)
2. Na stránce výsledků klikni na **⬇ Export bundle** (lightweight; ~50 KB) nebo **⬇ Export bundle (full)**, pokud videa/trace pomohou
3. Pošli ZIP e-mailem Petovi. **Předmět:** `bouracka-ui delta — <env> — <TC-code> — <YYYY-MM-DD>`
4. **Tělo:** jeden odstavec — co jsi očekával vs. co jsi pozoroval. Není potřeba opakovat obsah envelopu; bundle ho má.

**Latence:** Pete importuje bundle, vidí plný stav běhu, žádné upřesňující round-trip pro běžný případ.

### §7.2 Pro non-TC nálezy — DELTA-REPORT plain-text šablona

Trace bundly nezachycují: chybějící flows v testplanu, nedokumentované chování integrací, certifikační / network / proxy gaps, UAT/PROD env gaps z §3. Pro ty použij tuto plain-text šablonu. **Ulož jako `DELTA-REPORT-YYYY-MM-DD-NN.txt`** (NN = pořadové číslo) a pošli zpět Petovi.

```
========================================================================
DELTA-REPORT v0.1
========================================================================
date_local:    YYYY-MM-DD HH:MM (CEST/CET)
tester:        <vaše jméno>
machine:       HP Elite SUPNB001 | other: <hostname>
network:       SUPIN LAN | VPN | external
env:           DEMO | TST | UAT | PROD-READONLY
TC code:       TC-CP-...   (nebo N/A, pokud nejde o TC failure)
playbook ref:  §X DIAGNOSTICS-PLAYBOOKu, kterému to odporuje (pokud nějaký)

------------------------------------------------------------------------
CO JSEM POZOROVAL:
------------------------------------------------------------------------
<plain text, 2-10 vět. Buď konkrétní. Cituj přesné chybové zprávy,
 timestampy, HTTP status kódy, jména integrací.>

------------------------------------------------------------------------
CO JSEM OČEKÁVAL (podle §X playbooku nebo TC-XXX expected behaviour):
------------------------------------------------------------------------
<plain text, 2-5 vět. Cituj zdroj očekávání.>

------------------------------------------------------------------------
REPRODUKČNÍ KROKY:
------------------------------------------------------------------------
1. <akce>
2. <akce>
3. <akce>

------------------------------------------------------------------------
PŘILOŽENÉ EVIDENCE (X co platí):
------------------------------------------------------------------------
[ ] bouracka-ui diagnostics snapshot ZIP (filename: ...)
[ ] trace bundle (lightweight) (filename: ...)
[ ] trace bundle (full) (filename: ...)
[ ] screenshot(y) (filenames: ...)
[ ] browser DevTools Network HAR export (filename: ...)
[ ] cypress video file (filename: ...)
[ ] cypress trace.zip (filename: ...)
[ ] žádné — pouze live observation

------------------------------------------------------------------------
HYPOTÉZA (volitelné, váš nejlepší odhad ohledně root cause):
------------------------------------------------------------------------
<plain text, 1-3 věty. OK být tentative — Pete to upřesní na ThinkPad
 straně. Příklady: „smells like cert trust issue", „AISPOV fixture
 out-of-date", „TST má reCAPTCHA zapnutou tam, kde DEMO neměl".>

------------------------------------------------------------------------
URGENCE (X jednu):
------------------------------------------------------------------------
[ ] blocking — nemůžu pokračovat v žádném testování, dokud se nevyřeší
[ ] high   — blokuje toto TC, ale ostatní TCs pokračují
[ ] medium — produkuje špatnou odpověď, ale neblokuje
[ ] low    — kosmetické / nice to fix, až se to hodí

========================================================================
```

**Latence:** jeden e-mailový round-trip; Pete vrátí nález do §3 / §4 v další iteraci balíčku.

### §7.3 Velikost e-mailu — IOC-aware packaging

Podle existujících SUPIN email scanner pravidel (EMAIL-DELIVERABILITY-RULES, samostatný dokument):
- Jeden e-mail ≤ 5 MB
- ZIP přílohy preferovány před loose soubory
- Vyhnout se filenames triggering AV heuristiky (`patch`, `exploit`, `inject` atd.)
- Více nálezů v jedné session → batch do jednoho e-mailu + jednoho parent ZIPu, pokud total < 5 MB

Trace-bundle lightweight (~50 KB) + diagnostics snapshot (~30 KB) + DELTA-REPORT.txt (~5 KB) snadno vejde do jednoho e-mailu.

---

## §8. Eskalační matice

Single-line edit per řádek, když se kontakty přiřadí. Default na „Peta" pro všechno.

| Failure class | Symptom hint | Primary contact | Backup | Notes |
|---------------|--------------|-----------------|--------|-------|
| Bouračka-UI bug | UI samotné nefunguje; ne testovací data | Pete (`petr.yamyang@gmail.com`) | — | Založ BUG-BUI-NNN přes UI Bugs stránku, pokud přístupné |
| Test data drift (reCAPTCHA, AISPOV mock atd.) | Verdict `skip-drift` nebo neočekávaná mock response | Pete | — | DELTA-REPORT §7 |
| Síť / cert / proxy | `Test-NetConnection` selže nebo cert-error interstitial | `<FILL-IN: SUPIN SecOps>` | Pete | Pravděpodobně potřebuje SUPIN-interní access change |
| ČKP backend down (TST/UAT/PROD) | 5xx na POST /api/reports napříč více TCs | `<FILL-IN: ČKP API ops>` | Pete | Zachyť timestamp + diagnostic snapshot |
| AISPOV backend down | Driver lookup visí napříč více TCs | `<FILL-IN: AISPOV ops>` | Pete | DELTA-REPORT + timestamp |
| zenID backend down | ID upload krok selhává napříč více TCs | `<FILL-IN: zenID ops>` | Pete | DELTA-REPORT + sample file |
| N8 SMS gateway down | SMS kód nikdy nedorazí napříč více TCs | `<FILL-IN: N8 ops nebo telco>` | Pete | DELTA-REPORT + test phone number |
| HP Elite hardware / OS | Nenabootí / pip install selhává / WSL issues | `<FILL-IN: SUPIN IT>` | Pete | Přilož `system/system.json` z diagnostics |
| Cokoli nejednoznačné | Nevíš, do které kategorie | Pete | — | Default route; Pete triaguje |

---

## §9. Glosář

| Termín | Význam |
|--------|--------|
| **AISPOV** | Driver / vehicle insurance database (SUPIN interní) |
| **bundle** | Trace-bundle ZIP exportovaný přes `/api/runs/{rid}/bundle` |
| **DELTA-REPORT** | Plain-text finding template per §7.2 |
| **DEMO** | `demo.bouracka.cz` — veřejné, většinou mockované prostředí |
| **drift** | Test failure, který není reálná regrese; obvykle env-state nebo mock-fixture mismatch |
| **envelope** | v0.1 cross-framework results JSON psaný `tools/consolidate_results.py` |
| **IS ČKP** | Interní report systém (SUPIN-interní akronym) |
| **mockoon** | Lokální mock-server framework používaný v DEMO módu |
| **N8** | SMS verifikační gateway |
| **PROD** | `www.bouracka.cz` — produkce, read-only pro testy |
| **REPO_ROOT** | bouracka-ui auto-detekované umístění bouracka-tests/ (viz BUG-BUI-004) |
| **skip-drift** | Verdict přiřazený, když drift forensic detekoval známý-drift pattern |
| **TST** | `tst.bouracka.cz` — intranet testovací prostředí s real-ish backendy |
| **UAT** | User-acceptance test prostředí (mezi TST a PROD) |
| **zenID** | Skenování ID dokumentů + OCR service |

Konec DIAGNOSTICS-PLAYBOOK-CS.md
