# Ranní e-mail balíček 2026-05-07 — pro ThinkPad

> **Příjemce.** ThinkPad (= SUPIN Windows notebook station = stanice na které
> právě pracujeme), Pete + případní další testeři.
> **Odesílatel.** Pete (osobní e-mail) → SUPIN tester e-mail / interní backup.
> **Cíl.** Ranní deploy ze 2 ZIPů; očekávaný čas full setup ~ 45 minut
> (instalace 30 min + sanity-check + první test 15 min).

---

## §1. Co posílám (2 přílohy, 1 e-mail)

| Příloha | Velikost | Obsah | SHA256 |
|---------|----------|-------|--------|
| `bouracka-analytical-v0.4.5.zip` | 287 KB | analytický balíček (test plan, UML, Δ matice, recon, lessons learned, roadmap) — pro SUPIN review | `ac44b48651f1af10ff30f0a082ed473072180c5134bb195165260b1efe8e2f4e` |
| `bouracka-automation-v0.4.5.zip` | 1.59 MB | runnable automation suite (Playwright + Cypress + TestCafe + tools) — pro testery | `86626c413f2f2192579ae538012b832e7fcf0147cd25b080fe6e7bf45b0faaac` |

**Celkem:** ~1.9 MB. Vejde se do jednoho e-mailu i přes přísné scannery.

## §2. Co je nového v0.4.5 vs předchozí instalace na ThinkPadu

| Téma | Co je nového |
|------|--------------|
| **Install guide** | v0.4 (nahrazuje v0.3) — 5 empirických gotchas přesunutých z troubleshoot do **preflight** sekcí (winget reset, PowerShell ExecutionPolicy, py launcher, py -m pip, PATH snapshot) |
| **Sanity check** | `scripts\sanity-check.ps1` — 7-check post-install verifier; auto-detekuje verzi master Excelu |
| **Recovery patterny** | install guide §6.1 — 4 inline heredoc patterns pro obnovu chybějících souborů (sanity-check.ps1, check_priority_matrix.py, package.json, missing Excel master) |
| **Cookie banner handling** | `playwright/helpers/page-helpers.ts` — `dismissCookieBanner()` reusable helper; všechny TC volají STEP 0 |
| **Test pipeline** | bring-up smoke + full E2E happy-day + 8 alternates VŠECHNY GREEN proti DEMO Bouračce |
| **Cypress + TestCafe parity** | bring-up smoke port pro multi-framework comparison |
| **Bug naming** | `_specs/BUG-NAMING-CONVENTION-v0.1.md` — `BUG-CP-{TC_CODE}-{ASSERT_CODE}` deduplication; nikdy duplicitní rows |
| **Excel v0.4.1** | branch tagging na všech ItemBase listech + bug dedup schema (11 nových sloupců na 08_Bugs) |
| **Strategic docs** | ROADMAP-4-TARGET-CS, BRANCH-HANDOFF-TEMPLATE-CS, SYNCHRO-MACBOOK-CP-SUPIN-04 |

## §3. Postup ranní instalace (operátor)

### §3.1 Pokud máte předchozí TestAutomationSite\

```pwsh
cd C:\TestAutomationSite

# Backup předchozí stav (pro jistotu)
Compress-Archive -Path . -DestinationPath ..\TestAutomationSite-backup-$(Get-Date -Format yyyy-MM-dd).zip -CompressionLevel Optimal

# Verifikace SHA256 nového ZIP
Get-FileHash bouracka-automation-v0.4.5.zip -Algorithm SHA256
# očekávaný: 86626c413f2f2192579ae538012b832e7fcf0147cd25b080fe6e7bf45b0faaac

# Extract over existing — jen souboru s novou verzí
Expand-Archive -Path ..\bouracka-automation-v0.4.5.zip -DestinationPath ..\automation-v0.4.5 -Force
# Pak postupně copy z automation-v0.4.5\... do C:\TestAutomationSite\
# (nebo úplně nahradit — nechcete-li zachovat lokální experimentální changes)
```

### §3.2 Pokud děláte fresh install

Postupujte podle `INSTALL-FROM-ZERO-v0.4-CS.md` (je v ZIPu):

1. **§2 + §2b preflight** — winget source reset + ExecutionPolicy
2. **§3 runtime** — Python 3.12 + Node 20 LTS + JRE 21 + Mockoon CLI
3. **§4** — extract `bouracka-tests-v0.4.5.zip`
4. **§5** — `npm install` + `npx playwright install chromium`
5. **§6** — `.\scripts\sanity-check.ps1` → očekávaný 7/7 pass
6. **§7** — první produktivní použití (smoke test + full E2E)

Empiricky ověřený čas: ~45 minut (vs ~80 minut na v0.3).

### §3.3 Po sanity-check 7/7 pass

```pwsh
# Smoke (8 s)
$env:BOURACKA_BASE = "https://demo.bouracka.cz"
npx playwright test playwright/tests/bring-up-smoke.spec.ts `
  --config=playwright/playwright.config.ts `
  --project=public-mobile-375

# Full E2E happy day (~2.5 min)
npx playwright test playwright/tests/a1-main-happy-day-demo.spec.ts `
  --config=playwright/playwright.config.ts `
  --project=public-mobile-375

# Alternates (~1 min)
npx playwright test playwright/tests/a2-alternates-demo.spec.ts `
  --config=playwright/playwright.config.ts `
  --project=public-mobile-375
```

Pokud všechno green → instalace + suite stable → můžete pokračovat
s rozšiřováním coverage per `TESTER-LESSONS-LEARNED-v0.1-CS.md`.

## §4. Co dělat, když něco selže

Postupujte podle `INSTALL-FROM-ZERO-v0.4-CS.md`:
- §6.1 Recovery patterny pro chybějící soubory
- §10 Troubleshoot table pro známé patterns
- §13 Empirical lessons learned pro context proč ten gotcha existuje

Pokud nestandardní problém: pošlete screenshot z PowerShellu na sync-back
e-mail; Opus session na ThinkPadu / iPhone screenshot decode-flow funguje.

## §5. Pro SUPIN review

`bouracka-analytical-v0.4.5.zip` obsahuje:

- `00_README-CS.md` — cover note
- `BOURACKA-TESTPLAN-v0.4.1.xlsx` — kompletní test plan (28 TT, 49 TC, branch tagging, bug dedup schema)
- `recon/ANALYTICAL-DOC-MASTER-v0.4.md` — branched master analytical doc
- `recon/DELTA-DEMO-vs-PROD-v0.1.md` — 26-row Δ matrix (8 confirmed)
- `recon/integrations/INT-001..INT-009.md` — 9 integrací (4 nové: Azure outage, Google Maps, /api/reports, ČÚZK RUIAN)
- `_specs/ROADMAP-4-TARGET-CS.md` — strategic 4-target plan + MI-M-T migration roadmap
- `_specs/BUG-NAMING-CONVENTION-v0.1.md` — dedup convention
- `_specs/BRANCHED-MASTER-DOC-PATTERN-v0.1.md` — single-master-multi-view
- `_specs/TESTER-LESSONS-LEARNED-v0.1-CS.md` — empirical patterns
- `INSTALL-FROM-ZERO-v0.4-CS.md` — installation guide
- `EXCEL-VERSIONING-FIX-CS.md` + `PRIORITY-MATRIX-BUGFIX-CS.md` — bugfix advisories
- `MANIFEST-CS.md` — soubory + SHA256

## §6. Pro MacBook (analytical MI-M-T session)

`SYNCHRO-MACBOOK-CP-SUPIN-04-2026-05-06.md` (v obou ZIPech) shrnuje:

1. Top-line CP-SUPIN-04 deliveries
2. Klíčové methodology learnings pro MI-M-T (branch-aware schema, single-master pattern, bug dedup, recovery-as-code, Δ matrix, empirical preflight)
3. Strategic findings (live SUT > stale doc, 4-target gradual delivery, multi-framework parity)
4. Co MacBook session má dělat (číst, psát MI-M-T contract, sync-back protokol)

## §7. Stav

| Item | Hodnota |
|------|---------|
| E-mail šablona | `delivery/EMAIL-MORNING-2026-05-07-CS.md` |
| Verze | v0.4.5 |
| Příloha 1 | analytical-v0.4.5.zip (287 KB) |
| Příloha 2 | automation-v0.4.5.zip (1.59 MB) |
| Velikost celkem | ~1.9 MB (1 e-mail OK) |
| Datum | 2026-05-07 (ranní rozvoz) |
| Připraveno k odeslání | ANO |
