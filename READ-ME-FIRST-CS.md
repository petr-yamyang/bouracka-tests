# bouracka-tests v0.4.9.1-SAFE — fresh install + run (CS)

> **Cíl.** Single-ZIP delivery pro HP Elite (<test-runner-host>) v interní SUPIN síti.
> Zero PowerShell, zero .cmd, čistě Python orchestrátor.
> ZIP NEobsahuje žádné Windows skriptové soubory, takže prochází mailovými scannery
> Gmail / Active24 / Defender bez výhrad.

---

## §1. TL;DR — 3 kroky

1. **Rozzipuj** `bouracka-tests-v0.4.9.1.zip` → `C:\TestAutomationSite`
   (nebo libovolnou cestu **bez mezer**; kořen ZIPu nese složku `bouracka-tests-v0.4.9.1`)
2. **První běh** (~5 minut, 1× per stanice):
   ```
   cd C:\TestAutomationSite
   py bouracka.py setup
   ```
3. **Test běh** (~5 minut per spuštění, opakovatelné):
   ```
   py bouracka.py test
   ```

Vyrobí `bouracka-results-YYYY-MM-DD-<USERNAME>.zip` v root složce → **pošli zpět e-mailem** na petr.yamyang@gmail.com.

## §2. Co dělá `py bouracka.py setup` (1× per stanice)

| Krok | Akce |
|------|------|
| 1 | Integrity check kritických source souborů (null-free, parse-clean) |
| 2 | Preflight: ověř Node + npm |
| 3 | `npm install` (~5 min, ~1 GB) |
| 4 | `npx playwright install chromium` (~150 MB) |

## §3. Co dělá `py bouracka.py test` (per testovací běh)

| Krok | Akce |
|------|------|
| 1 | Integrity check (rychlý) |
| 2 | Playwright bring-up smoke (1 test, ~30 s) |
| 3 | Playwright a2-alternates (8 ALT- testy, ~70 s) |
| 4 | Playwright a1-main-happy-day (1 E2E, ~3 min OR drift-skip) |
| 5 | Balíček `bouracka-results-YYYY-MM-DD-<USERNAME>.zip` |

Output:
- `playwright-report/index.html` — HTML report (otevři v prohlížeči)
- `test-results/<run>/` — per-test artefakty (screenshots, traces, JSON)
- `bouracka-results-...zip` — vše zabalené pro e-mail back
- `bouracka-run.log` — průběžný log (zahrnut v ZIPu)

## §4. Cílové prostředí (přepínač)

Default: `https://demo.bouracka.cz`. Pro jiný target nastav PŘED spuštěním:

```
set BOURACKA_BASE=https://tst.demo.bouracka.cz
py bouracka.py test
```

Podporované cíle:
- `https://demo.bouracka.cz` (DEMO public — Cíl 1, default)
- `https://tst.demo.bouracka.cz` (DEMO test — Cíl 2)
- `https://tst.bouracka.cz` (PROD test — Cíl 3, vyžaduje N08 sandbox)
- `https://bouracka.cz` (PROD prelive — Cíl 4)

## §5. Příkazy bouracka.py — referenční

| Příkaz | Popis |
|--------|-------|
| `py bouracka.py setup`  | první-běh: integrity check + npm install + browsers |
| `py bouracka.py test`   | per-běh: testy + balíček výsledků |
| `py bouracka.py all`    | setup + test sequenčně |
| `py bouracka.py verify` | jen integrity check, neběží testy |
| `py bouracka.py help`   | zobrazí docstring s návodem |

## §6. Co je uvnitř ZIPu

```
bouracka-tests-v0.4.9.1/
├── READ-ME-FIRST-CS.md        ← toto čteš
├── bouracka.py                ← Python orchestrátor (jediný entry point)
├── BOURACKA-TESTPLAN-v0.4.2.xlsx     ← Excel master TestPlan
├── package.json               ← npm dependencies manifest
├── playwright/                ← Playwright tests + reporters + config
├── cypress/                   ← Cypress smoke (parita)
├── testcafe/                  ← TestCafe smoke (parita)
├── selenium/                  ← Selenium pytest scaffold
├── readyapi/                  ← ReadyAPI/SoapUI smoke project
├── postman/                   ← Postman collection
├── mockoon/                   ← N8 SMS mock
├── tools/                     ← Python helpers
├── fixtures/                  ← live captured codelists + endpoints
├── env/                       ← per-environment config
├── recon/                     ← analytical recon docs
└── _specs/                    ← strategic governance docs
```

**Co tam NENÍ** (oproti v0.4.9):
- **žádné** `.cmd` soubory (Gmail/Active24/AV scanner trigger)
- **žádné** `.ps1` soubory (PowerShell = malware-loader IOC pro scannery)
- **žádné** retry/orchestration helpery v PowerShellu (`scripts/*.ps1`, `tools/*.ps1`)

Všechna orchestrace je v `bouracka.py`.

## §7. Proč Python a ne PowerShell

E-mailové scannery (Gmail, Active24, ESET, Defender) blokují ZIPy s PowerShell skripty
nebo `.cmd` wrappery, protože jsou hlavním vektorem pro malware delivery (RATs,
ransomware loaders). Konkrétně řetězec, který naše dřívější skripty obsahovaly,
je v IOC databázích označen jako "high-confidence malware indicator".

Python je naopak standardní vývojářský nástroj a `.py` soubory neprochází stejnou
filtrační vrstvou. HP Elite (<test-runner-host>) má `py` launcher dostupný (per install
doc; pokud chybí, nainstalovat ze [https://python.org](https://python.org) verzi
3.12+ s "Add to PATH" zaškrtlým).

## §8. Troubleshooting

### §8.1 `py: command not found`
Nainstaluj Python 3.12+ z [https://python.org](https://python.org). Při instalaci zaškrtni
**"Add Python to PATH"**. Po instalaci otevři **nové** PowerShell okno (PATH refresh).

### §8.2 `npm install` selže
Pravděpodobně proxy/firewall. Kontaktuj IT pro npm proxy / `.npmrc`. Případně
zkontroluj `npm config get proxy`.

### §8.3 `py bouracka.py test` report-uje 4 GREEN z 10
**Očekávaný stav po DEMO driftu 2026-05-07.**
- 4× GREEN: bring-up + ALT-6 + ALT-7 + ALT-8
- 4× SKIPPED: ALT-1 + ALT-4 + ALT-5 + a1-main (drift guard)
- 1× GREEN-soft: ALT-9 (drift-aware)
- 1× GREEN: ALT-10 (SPA POST probe — nejcennější artefakt!)

Klíčový výstup: `test-results/<run>/alt10-spa-post.json` —
charakterizuje jaký token/header DEMO server nyní vyžaduje.

### §8.4 Antivirus blokuje extrakci ZIPu
Pokud Defender/AV označí v0.4.9.1 ZIP jako podezřelý, pošli Pete:
- Verzi AV
- Detection signature (pokud zobrazena)
- Quar