# Cíl 2 enablement — promoce kit z DEMO public na DEMO test — v0.1 CS

> **Cíl 2.** `https://tst.demo.bouracka.cz` — DEMO test environment uvnitř
> ČKP/SUPIN intranet, dostupný **pouze** z HP Elite (<test-runner-host>) v korporátní síti.
>
> **Cíl této doc.** Ucelený postup jak přepnout existující kit z Cíl 1 (DEMO
> public, `demo.bouracka.cz`) na Cíl 2 (DEMO test) bez re-instalace, plus
> drift-detection convention pro porovnání obou environments.

---

## §1. Předpoklady

| # | Předpoklad | Stav (2026-05-07) |
|---|------------|-------------------|
| P1 | HP Elite (<test-runner-host>) má v0.4.9.1-SAFE / v0.5.0 nainstalováno | ✅ ověřeno (bouracka-results-2026-05-07-<runner>.zip) |
| P2 | HP Elite je v ČKP intranet | ✅ ověřeno (validate-install: `reachable_tst_demo: true`) |
| P3 | tst.demo.bouracka.cz odpovídá z HP Elite | ✅ ověřeno (HEAD check passes) |
| P4 | Tester credentials (pokud Cíl 2 vyžaduje basic auth nebo SSO) | TBD — Pete koordinuje s ČKP DEMO ops |

## §2. Postup přepnutí (5 minut)

### §2.1 Set BOURACKA_BASE → tst.demo.bouracka.cz

```cmd
cd C:\TestAutomationSite
set BOURACKA_BASE=https://tst.demo.bouracka.cz
py bouracka.py test
```

Žádná reinstalace, žádný npm install znovu. Stejný spec files, stejné fixtures.

### §2.2 Per-framework parameter override (až bude cross-framework parita full)

| Framework | Override mechanism |
|-----------|--------------------|
| Playwright | `BOURACKA_BASE=...` env var (existing) |
| Cypress | `CYPRESS_baseUrl=https://tst.demo.bouracka.cz` env var |
| TestCafe | `--app=https://tst.demo.bouracka.cz` CLI flag |
| Selenium | `BOURACKA_BASE=...` env var (Python helpers respect it) |

`bouracka.py` v0.5.x přidá unifikovaný flag `--target` pro per-run override:

```cmd
py bouracka.py test --target=tst-demo
# alias for: BOURACKA_BASE=https://tst.demo.bouracka.cz
```

## §3. Očekávané rozdíly Cíl 1 vs Cíl 2

Per existing Δ matrix (`recon/DELTA-DEMO-vs-PROD-v0.1.md`), Cíl 2 sdílí
většinu chování s Cíl 1 (oba jsou DEMO branche), ale liší se v některých aspektech.

### §3.1 Pravděpodobně **stejné** (oba DEMO)

| Aspekt | Hodnota |
|--------|---------|
| 4-phase wizard structure | identický |
| OTP mock (any 4-digit OK) | identický |
| zenID mock | identický |
| AISPOV mock | identický |
| reCAPTCHA test key | identický |
| Codelist endpoints (8 protected, 2 public) | identické |
| DEMO banner present | identický (Δ11 + Δ22) |

### §3.2 Možná **odlišné**

| Aspekt | Cíl 1 (DEMO public) | Cíl 2 (DEMO test) | Implikace |
|--------|---------------------|-------------------|-----------|
| Network reachability | internet | intranet only | nelze testovat z ThinkPad/MacBook |
| Auth gating | none | possibly basic-auth nebo SSO | tester credentials needed |
| Release cadence | rolling | možná static / per release window | drift exists až po release |
| **POST /api/reports drift** | confirmed 2026-05-07 (403) | **TO BE TESTED** | klíčová otázka iterace |

### §3.3 Kritická otázka pro CP-SUPIN-05

> **Q1: Je drift na POST /api/reports rovněž na tst.demo.bouracka.cz, nebo jen
> na demo.bouracka.cz public?**

**Pokud rovněž na tst.demo:** drift je SUPIN-wide (možná globální threshold
zvednutí na backend captcha verification). Implikuje že Cíl 3 (tst.bouracka.cz)
+ Cíl 4 (bouracka.cz prelive) také mají drift — testing strategy musí adaptovat.

**Pokud jen na DEMO public:** drift je environment-specific (možná DEMO public
měla auto-redeploy a tst.demo zaostává). Méně urgent eskalace, ale klíč pro
debug.

**Test postup pro Q1:**

```cmd
cd C:\TestAutomationSite
set BOURACKA_BASE=https://tst.demo.bouracka.cz
py bouracka.py test
```

Pokud:
- `bring-up-smoke.spec.ts` GREEN (jako na Cíl 1) — environment alive
- `a1-main-happy-day-demo.spec.ts` SKIPPED-with-rationale (drift) — drift confirmed na tst.demo
- `a1-main-happy-day-demo.spec.ts` PASSED — drift jen na public DEMO; tst.demo nezasaženo

Pošli `bouracka-results-...zip` zpět e-mailem; analýza najde detail v `0-trace.network`.

## §4. Per-framework smoke parita check

CP-SUPIN-04 STEP 26 zaved scaffold pro Cypress + TestCafe + Selenium ale
spustil je jen proti Cíl 1. Pro Cíl 2 spuštění (manuálně, dokud nemá `bouracka.py`
multi-framework runner v0.6.0):

### §4.1 Playwright (default)

```cmd
set BOURACKA_BASE=https://tst.demo.bouracka.cz
py bouracka.py test
```

### §4.2 Cypress smoke

```cmd
set BOURACKA_BASE=https://tst.demo.bouracka.cz
set CYPRESS_baseUrl=%BOURACKA_BASE%
npx cypress run --spec cypress/e2e/bring-up-smoke.cy.ts
```

### §4.3 TestCafe smoke

```cmd
set BOURACKA_BASE=https://tst.demo.bouracka.cz
npx testcafe chromium:headless testcafe/tests/bring-up-smoke.test.ts --app=%BOURACKA_BASE%
```

### §4.4 Selenium smoke

```cmd
set BOURACKA_BASE=https://tst.demo.bouracka.cz
py -m pytest selenium/tests/test_bring_up_smoke.py -v
```

Očekávané: všechny 4 GREEN proti tst.demo (smoke je "page loads + CTA visible",
to nezávisí na POST /api/reports drifu).

## §5. Drift detection convention

Když Cíl 2 dá jiný výsledek než Cíl 1:

### §5.1 Pojmenování driftu

`DRIFT-{date}-{environment}-{symptom}-{component}-CS.md`

Příklady:
- `DRIFT-2026-05-07-DEMO-POST-REPORTS-CS.md` (existing — Cíl 1)
- `DRIFT-2026-05-08-TST-DEMO-OTP-MOCK-CS.md` (hypothetical — Cíl 2 OTP behavior changed)

### §5.2 Doc structure (per drift)

Každý drift doc musí mít:
- §1 Symptomy (live evidence)
- §2 Hypotézy (root cause candidates)
- §3 Forensic data (trace excerpts, response shapes)
- §4 Dopad na test sadu (what changes per impacted TC)
- §5 Plán resolution
- §6 Action items + status table

Template: copy z `recon/DRIFT-2026-05-07-DEMO-POST-REPORTS-CS.md`.

### §5.3 Excel `08_Bugs` integration

Confirmed driftů (po validation z ČKP DEMO ops nebo dev) se přidává jako bug do
`08_Bugs` sheet s:
- `bug_id` = `BUG-CP-DRIFT-{slug}` např. `BUG-CP-DRIFT-DEMO-POST-REPORTS-403`
- `applies_to_demo: true`, `applies_to_demo_test: true/false` (per evidence)
- `applies_to_prod: ?` (TBD until Cíl 3 enables)
- `recon_link` = relative path do `recon/DRIFT-...md`

## §6. Sync-back protocol

### §6.1 Pete na HP Elite (běh)

```cmd
cd C:\TestAutomationSite
set BOURACKA_BASE=https://tst.demo.bouracka.cz
py bouracka.py test
# vyrobí: bouracka-results-YYYY-MM-DD-<runner>.zip
```

### §6.2 Sync-back e-mailem

Pete e-mailem pošle ZIP zpět na **petr.yamyang@gmail.com** s subject:
`Cíl 2 first run — bouracka v0.5.0 — YYYY-MM-DD`

Tělo e-mailu krátce:
- Verze kitu
- Cíl env
- Stav (GREEN / RED s drift / RED s neznámou chybou)
- Otázky pro Pete (Opus session)

### §6.3 Opus session zpracuje

- Extrahuje `playwright-report/data/*.zip` traces
- Hledá POST /api/reports v `0-trace.network`
- Comparison s Cíl 1 baseline (`bouracka-results-2026-05-07-<runner>.zip`)
- Update Δ matrix + drift docs
- Bumps fixture version pokud potřeba

### §6.4 Iterate

Pokud potřebné, Opus session vyrobí v0.5.x patch (drift fix, helper update,
fixture refresh) → ship single-ZIP scanner-friendly → Pete znovu na HP Elite.

## §7. Q&A pro Pete (před Cíl 2 první run)

| # | Otázka | Default | Pete confirms? |
|---|--------|---------|----------------|
| Q-CIL2-1 | Je tst.demo.bouracka.cz reachable z HP Elite? | ✅ ano (per validate-install) | already done |
| Q-CIL2-2 | Vyžaduje tst.demo basic-auth nebo SSO? | předp. ne | TBD |
| Q-CIL2-3 | Test data — stejní účastníci A+B s phone +420 608 000 001/002? | předp. ano | TBD |
| Q-CIL2-4 | OTP mock — accept any 4-digit? | předp. ano | TBD |
| Q-CIL2-5 | Maintenance window — kdy NE-spouštět testy? | TBD | TBD |
| Q-CIL2-6 | Owner contact pro tst.demo issues | ČKP DEMO ops | TBD |

## §8. Status

| Item | Hodnota |
|------|---------|
| Doc | `_specs/CIL-2-ENABLEMENT-v0.1-CS.md` |
| Verze | v0.1 |
| Datum | 2026-05-07 EOD |
| Cíl readiness | environment reachable; first run plánován |
| Predicted result | **drift confirmed** s ~70% pravděpodobností (per H5 hypothesis) |
| Status | ready for first Cíl 2 run; čeká na Q-CIL2 confirmation z Pete strany |
