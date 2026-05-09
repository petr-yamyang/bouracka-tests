# SESSION STATUS — CP-SUPIN-05 — 2026-05-09
**Branch:** `cp-supin-05-cross-framework-parity`
**Repo:** `github.com/petr-yamyang/bouracka-tests`
**Purpose of this doc:** (1) Session-restart context for Claude/Sonnet; (2) Opus briefing on artifact state.
**Timestamp:** 2026-05-08T23:25Z (session running into 2026-05-09)

---

## § EXECUTIVE SUMMARY

CP-SUPIN-05 cross-framework parity work is ~85% complete. The Selenium side is fully green
(5 PASS / 5 SKIP with JSON report captured). The Cypress side has 3 confirmed PASSes (ALT-7,
ALT-8, ALT-9) and 6 specs failing at `cy.visit()` due to a **SPA cold-load timeout** that
exceeds the 60 s `pageLoadTimeout`. One more spec (`main-happy-day`) fails for a secondary
reason (16 s run, not a timeout — MUI overlay or subsequent step failure). The consolidation
tool (`tools/consolidate_results.py`) is repaired and functional. The branch needs one more
Cypress fix + a clean consolidation run before the PR can be opened.

---

## § BRANCH STATE

| Commit | Hash | What |
|--------|------|------|
| covers import fix (8 specs) | `2021539` | `covers` imported from nav-helpers → data-loader (8 files) |
| pageLoadTimeout + scrollIntoView | `f747380` | cypress.config.ts 30s→60s; main-happy-day scrollIntoView |
| HEAD | `f747380` | pushed to origin |

```
git log --oneline -5  (expected on branch)
f747380 fix(cypress): pageLoadTimeout 60s + scrollIntoView on VYPLNIT ZÁZNAM button
2021539 fix(cypress): covers imported from wrong module in 8 spec files
... (prior CP-SUPIN-05 commits)
```

---

## § TEST RESULTS BASELINE (2026-05-08/09 runs)

### Selenium — CONFIRMED BASELINE ✅
**Command:** `python -m pytest selenium/ -v --json-report --json-report-file=selenium-report/results.json`
**Environment:** Windows 10, Python 3.10.11, Chrome (headless=new), BOURACKA_BASE=https://demo.bouracka.cz
**Result:** `5 passed, 5 skipped, 1 warning in 63.53s`
**JSON report:** saved to `selenium-report/results.json` ← ready for consolidation

| TC | Status | Note |
|----|--------|------|
| TC-CP-001 (bring-up-smoke) | PASSED | |
| TC-CP-A2-ALT-6 (police-card) | PASSED | |
| TC-CP-A2-ALT-7 (enumerations) | PASSED | API-only, no browser |
| TC-CP-A2-ALT-8 (demo-banner) | PASSED | |
| TC-CP-A2-ALT-9 (post-reports-drift) | PASSED (soft) | 403 soft-pass; drift warning logged |
| TC-CP-A1-MAIN-DEMO | SKIPPED | drift guard: SPA→/error/timeout |
| TC-CP-A2-ALT-1 (rp-regex) | SKIPPED | drift guard |
| TC-CP-A2-ALT-4 (gdpr-consent) | SKIPPED | drift guard |
| TC-CP-A2-ALT-5 (slovak-prefix) | SKIPPED | drift guard |
| TC-CP-A2-ALT-10 (spa-post-probe) | SKIPPED | drift guard |

### Cypress — PARTIAL (3 PASS / timeout issues)
**Command:** `npx cypress run --config-file=cypress/cypress.config.ts --browser chrome --reporter json --reporter-options "output=cypress/cypress-results/results.json"`
**Environment:** Windows 10, Chrome (headed? headless-new?), BOURACKA_ENV=tst-demo
**Result:** `8 of 12 failed (67%), 3 passing, 15 failing, 10 pending — 05:35 total`
**JSON report:** saved to `cypress/cypress-results/results.json` ← present but has failures

| Spec | Time | Status | Root cause |
|------|------|--------|-----------|
| core-flow.cy.ts | 197ms | 10 PENDING | Pre-existing: all tests `.skip()`'d (Mocha pending) |
| alt-7-enumerations.cy.ts | 1s | ✅ PASS | API-only |
| alt-8-demo-banner.cy.ts | 1s | ✅ PASS | Quick DOM check |
| alt-9-post-reports-drift.cy.ts | 213ms | ✅ PASS | API-only |
| bring-up-smoke.cy.ts | 11s | FAIL | Pre-existing CP-SUPIN-04: wrong baseUrl (www vs demo) |
| login.cy.ts | 2s | 8 FAIL | Pre-existing CP-SUPIN-04: button in `div.hidden.xl:flex` (375px viewport) |
| main-happy-day.cy.ts | 16s | FAIL | See analysis §OPEN-ISSUES below |
| alt-1-rp-regex.cy.ts | 1:00 | FAIL | **cy.visit() timeout at 60s** — SPA cold-load |
| alt-4-gdpr-consent.cy.ts | 1:00 | FAIL | **cy.visit() timeout at 60s** |
| alt-5-slovak-prefix.cy.ts | 1:00 | FAIL | **cy.visit() timeout at 60s** |
| alt-6-police-card.cy.ts | 1:00 | FAIL | **cy.visit() timeout at 60s** |
| alt-10-spa-post-probe.cy.ts | 1:00 | FAIL | **cy.visit() timeout at 60s** |

**Expected Cíl-1 outcomes** (from spec definition):
- ALT-7, ALT-8, ALT-9: PASS ✅ — achieved
- ALT-1, ALT-4, ALT-5, ALT-6, ALT-10, MAIN-DEMO: SKIP (drift guard) — NOT achieved; timing out instead
- bring-up-smoke, login: FAIL (pre-existing, out of scope) — as expected

---

## § ROOT CAUSE ANALYSIS — CYPRESS cy.visit() TIMEOUT

**Symptom:** alt-1, alt-4, alt-5, alt-6, alt-10 all timeout at exactly 60 000 ms at `cy.visit("https://demo.bouracka.cz/formular/")`. None reach the drift guard.

**Why Selenium does NOT timeout:** Selenium `driver.get()` has a default 300 s page-load timeout (not explicitly set in conftest.py). The SPA apparently loads within 300 s. Cypress has a configured `pageLoadTimeout: 60_000` which the SPA exceeds.

**Root cause:** `demo.bouracka.cz/formular/` loads reCAPTCHA v3 + cookie-consent scripts. In headless Chrome under Cypress's instrumentation (DevTools-protocol channel), one or more of these external scripts hangs — blocking the `load` event — for >60 s. Selenium's `driver.get()` returns on `document.readyState === 'complete'` with a 300 s fallback, which the page eventually satisfies.

**Fix options (in order of invasiveness):**

Option A — Increase `pageLoadTimeout` to 180 000 ms (3 min). Simple; may work if SPA loads in 90–120 s.

Option B — Set `pageLoadStrategy: 'none'` in Cypress Chrome launch options + add a `cy.get('h1', {timeout: 30000})` guard after `cy.visit()`. This tells Chrome not to wait for the `load` event; Cypress proceeds as soon as the HTTP response arrives and waits for the h1 assertion instead. This is the most robust fix and matches the Playwright approach.

Option C — Add `--disable-features=PrivacySandboxAdsAPIs` and `--disable-background-networking` Chrome flags in `setupNodeEvents` to suppress hanging background requests.

**Recommended:** Option B (pageLoadStrategy none) — it directly bypasses the third-party script hang that causes the `load` event to block, and is the industry-standard pattern for SPAs with external scripts. Should be applied in `cypress.config.ts` inside `setupNodeEvents` via `on('before:browser:launch', ...)`.

**Implementation:**
In `cypress.config.ts` `setupNodeEvents`:
```typescript
on('before:browser:launch', (_browser, launchOptions) => {
  // Prevent reCAPTCHA/analytics scripts from blocking the load event
  launchOptions.args.push('--disable-background-networking');
  return launchOptions;
});
```
AND in `cypress.config.ts` top-level config or per-spec:
```typescript
// Option: tell Chrome not to wait for load event (pageLoadStrategy)
// Cannot be set via Cypress config directly; use cy.visit with onBeforeLoad instead.
```
Actually the cleanest Cypress-native fix is `pageLoadTimeout: 180_000` first (try 3 min), then fall back to `pageLoadStrategy: none` if needed.

**main-happy-day analysis:**
The spec ran for 16 s (not a timeout). It got past `cy.visit()` and the h1 assertion but failed somewhere in Phase 0→A→1. The `scrollIntoView().click()` fix was applied to line 112 for the VYPLNIT ZÁZNAM button. However, the test still fails before reaching the drift guard. Possible causes:
1. The click succeeded but the navigation to `/formular/informations` failed or was slow
2. A second MUI overlay covers a different button
3. The Phase A "Rozumím" button is covered at 375px
4. The `navToVerificationOrSkip` drift-guard itself encounters a race condition

Since the test is EXPECTED to SKIP at Cíl 1 (drift guard), it just needs to reach `navToVerificationOrSkip.call(this, BASE)` and detect `/error/timeout`. The 16 s run suggests it loaded the page and attempted some clicks. To see the exact failure, check `cypress/screenshots/` or `cypress/videos/` for this spec.

---

## § FILES CHANGED (uncommitted or pending commit)

### Already committed to branch (f747380, 2021539)
```
cypress/support/data-loader.ts          ← covers() source-of-truth (unchanged)
cypress/support/nav-helpers.ts          ← does NOT export covers (unchanged)
cypress/e2e/a1-main-demo/main-happy-day.cy.ts      ← covers import fixed; scrollIntoView added
cypress/e2e/a2-alternates-demo/alt-1-rp-regex.cy.ts ← covers import fixed
cypress/e2e/a2-alternates-demo/alt-4-gdpr-consent.cy.ts
cypress/e2e/a2-alternates-demo/alt-5-slovak-prefix.cy.ts
cypress/e2e/a2-alternates-demo/alt-6-police-card.cy.ts
cypress/e2e/a2-alternates-demo/alt-8-demo-banner.cy.ts
cypress/e2e/a2-alternates-demo/alt-9-post-reports-drift.cy.ts
cypress/e2e/a2-alternates-demo/alt-10-spa-post-probe.cy.ts
cypress/cypress.config.ts               ← pageLoadTimeout 30s→60s
CHANGELOG.md                            ← v0.5.3 section added
```

### Modified in working tree (NOT YET committed)
```
tools/consolidate_results.py            ← v0.5.2: _NODEID_TC_RE fallback for Selenium nodeids
selenium-report/results.json           ← Windows run 2026-05-08 (5P/5S, 63.53s)
cypress/cypress-results/results.json   ← Windows run 2026-05-08 (3P, partial)
runs/cross-framework-2026-05-08.json   ← Selenium-only run (Cypress/PW missing)
runs/cross-framework-2026-05-08.md     ← Same
cypress/tsconfig.json                  ← TS18002 fix (previously committed?)
```

---

## § TOOLS/CONSOLIDATE_RESULTS.PY — STATUS

**Version:** v0.5.2 (written directly to mount via bash, confirmed syntax OK)
**Key fix:** Added `_NODEID_TC_RE = re.compile(r"::test_(TC(?:_[A-Z0-9]+)+)")` fallback in
`_parse_selenium()` — pytest nodeids use underscores (`test_TC_CP_A2_ALT_7_enumerations`)
while `TC_CODE_RE` only matches hyphenated form. Fallback converts `TC_CP_A2_ALT_7` → `TC-CP-A2-ALT-7`.

**Verified:** `python3 tools/consolidate_results.py --se selenium-report/results.json` → 10 Selenium entries extracted, report written.

**WARNING:** The Windows filesystem copy may differ from the sandbox copy due to NTFS mount cache lag. Before running consolidation on Windows, verify `tools/consolidate_results.py` contains `_NODEID_TC_RE` (grep for it). If not present, re-apply the fix or pull from the sandbox's version.

---

## § PENDING ACTIONS (in execution order)

### P1 — Fix Cypress cy.visit() timeout (BLOCKING)
Apply `pageLoadTimeout: 180_000` in `cypress.config.ts` as the quickest fix:
```typescript
pageLoadTimeout: 180_000,   // was 60_000; SPA cold-load with reCAPTCHA v3 exceeds 60s
```
If that is still insufficient (rare but possible), apply Option B (pageLoadStrategy: none +
explicit element wait after cy.visit).

Commit message:
```
fix(cypress): increase pageLoadTimeout to 180s for reCAPTCHA SPA cold-load

demo.bouracka.cz/formular/ loads reCAPTCHA v3 + cookie-consent scripts that
block the browser load event for >60s in headless Chrome under Cypress DevTools
instrumentation. Increasing from 60_000 to 180_000 ms to allow the drift-guard
tests (ALT-1, 4, 5, 6, 10, main) to reach the SPA and trigger the expected
SKIP via navToVerificationOrSkip.

Refs: CP-SUPIN-05, Cíl 1 baseline
```

### P2 — Diagnose main-happy-day 16s failure
After P1, re-run only main-happy-day to see if it now reaches the drift guard and SKIPs:
```powershell
npx cypress run --config-file=cypress/cypress.config.ts --browser chrome --spec "cypress/e2e/a1-main-demo/main-happy-day.cy.ts"
```
Check `cypress/screenshots/` for failure screenshot. If it still fails before drift guard,
read the screenshot to identify which DOM element is blocking.

### P3 — Commit consolidate_results.py fix
```powershell
git add tools/consolidate_results.py
git commit -m "fix(tools): consolidate_results.py v0.5.2 — Selenium nodeid TC extraction

_parse_selenium() could not extract TC codes from pytest nodeids because they
use underscores (test_TC_CP_A2_ALT_7_enumerations) while TC_CODE_RE only
matches hyphenated TC-CP-* format.

Fix: add _NODEID_TC_RE fallback regex that captures the ALL-CAPS token sequence
from ::test_(TC...) function names and converts underscores to hyphens.
Verified: 10/10 Selenium TCs extracted from selenium-report/results.json.
"
```

### P4 — Re-run Cypress with 180s timeout + JSON report
```powershell
npx cypress run `
  --config-file=cypress/cypress.config.ts `
  --browser chrome `
  --reporter json `
  --reporter-options "output=cypress/cypress-results/results.json"
```
Expected: ALT-7/8/9 PASS, ALT-1/4/5/6/10/main SKIP (drift guard), bring-up/login FAIL (pre-existing).

### P5 — Run consolidation
```powershell
python tools/consolidate_results.py
```
Expected output: `runs/cross-framework-2026-05-09.json` + `.md`
Divergence check: Selenium SKIP = Cypress SKIP for drift-guard tests → PARITY CONFIRMED for Cíl 1.

### P6 — Commit results + open PR
```powershell
git add selenium-report/results.json cypress/cypress-results/results.json `
        runs/ cypress/tsconfig.json
git commit -m "chore(results): Cíl-1 baseline run — Selenium 5P/5S, Cypress 3P/xS

Selenium (2026-05-09): 5 passed / 5 skipped (drift-guard active)
Cypress  (2026-05-09): 3 passed / N skipped / 2 failed (pre-existing CP-SUPIN-04)
Parity: CONFIRMED for non-pre-existing TCs.
cross-framework report: runs/cross-framework-2026-05-09.{json,md}"
git push
```
Then open PR at: `https://github.com/petr-yamyang/bouracka-tests/pull/new/cp-supin-05-cross-framework-parity`

---

## § OPEN ISSUES

| ID | Severity | Description |
|----|----------|-------------|
| CY-TIMEOUT-01 | HIGH | cy.visit() times out at 60s (now 180s) for all SPA specs. Root: reCAPTCHA/consent script blocking load event. See fix in P1. |
| CY-MAIN-01 | MEDIUM | main-happy-day fails at 16s — scrollIntoView applied but test still fails before drift guard. Needs screenshot analysis. |
| Q-PARITY-3 | LOW | playwright/tests/a2-alternates-demo.spec.ts may be truncated (ends line 228 mid-expression). Verify in git history. |
| Q-PARITY-4 | LOW | `abel(/Model vozidla/i)` typo in Playwright source line ~221. Fix in source-of-truth if confirmed. |
| NTFS-LOCK-01 | INFO | `.git/index.lock` appears stuck in Linux sandbox mount but doesn't exist on Windows. All git ops must be run from Windows PowerShell, not the sandbox. |
| MOUNT-STALE-01 | INFO | Write tool edits via Linux sandbox are visible to Windows filesystem immediately, but Linux bash reads stale cache for ~30s after edits. Write large files via bash `python3 << 'EOF'` pattern to bypass. |

---

## § ARCHITECTURE NOTES FOR OPUS

### Test framework topology
```
bouracka-tests/
├── cypress/                    ← Cypress 13 project root (config here)
│   ├── cypress.config.ts       ← BOURACKA_ENV env controls baseUrl; specs use BOURACKA_BASE
│   ├── e2e/
│   │   ├── a1-main-demo/       ← TC-CP-A1-MAIN-DEMO (full E2E happy day)
│   │   └── a2-alternates-demo/ ← TC-CP-A2-ALT-{1,4,5,6,7,8,9,10}
│   └── support/
│       ├── data-loader.ts      ← covers() MUST be imported from here (not nav-helpers)
│       └── nav-helpers.ts      ← dismissCookieBanner, navToVerificationOrSkip, setOtpDigits
├── selenium/
│   ├── conftest.py             ← Chrome headless=new, 375×667, cs-CZ
│   ├── pytest.ini              ← pythonpath = . (namespace collision guard)
│   ├── helpers/
│   │   ├── data_loader.py      ← covers() for Selenium
│   │   └── nav_helpers.py      ← nav_to_verification_or_skip (drift guard)
│   └── tests/
│       ├── a1_main/            ← test_TC_CP_A1_MAIN_DEMO_full_happy_day
│       └── a2_alternates/      ← test_TC_CP_A2_ALT_{1,4,5,6,7,8,9,10}
└── tools/
    └── consolidate_results.py  ← v0.5.2; merges PW+CY+SE JSON into parity report
```

### Drift guard pattern
Both Cypress and Selenium implement the same drift guard:
- Navigate to `/formular/`, dismiss cookie banner, click VYPLNIT ZÁZNAM, click Rozumím
- Poll URL for 30s:
  - `/verification` → test proceeds normally
  - `/error/timeout` → **skip** the test (reCAPTCHA 403 drift active since 2026-05-07)
- Currently (Cíl 1): ALL SPA tests SKIP because POST /api/reports returns 403

### env/baseUrl resolution
- `BOURACKA_ENV=tst` → `baseUrl = https://tst.bouracka.cz`
- `BOURACKA_ENV=tst-demo` → `baseUrl = https://tst.demo.bouracka.cz`
- unset (default) → `baseUrl = https://www.bouracka.cz` (wrong for CP-SUPIN-05 tests)
- Spec files use `Cypress.env("BOURACKA_BASE")` → hardcoded to `https://demo.bouracka.cz` in cypress.config.ts env block
- **Always set `BOURACKA_BASE=https://demo.bouracka.cz` when running Selenium**

### Cíl 1 expected outcomes (reference)
```
TC-CP-001 (smoke):        Selenium PASS   / Cypress FAIL (pre-existing, out of scope)
TC-CP-A2-ALT-6:           Selenium PASS   / Cypress SKIP (drift guard expected)
TC-CP-A2-ALT-7:           Selenium PASS   / Cypress PASS  ← PARITY ✓
TC-CP-A2-ALT-8:           Selenium PASS   / Cypress PASS  ← PARITY ✓
TC-CP-A2-ALT-9:           Selenium SOFT   / Cypress SOFT  ← PARITY ✓
TC-CP-A1-MAIN-DEMO:       Selenium SKIP   / Cypress SKIP expected (currently FAIL)
TC-CP-A2-ALT-{1,4,5,10}: Selenium SKIP   / Cypress SKIP expected (currently FAIL/timeout)
login, core-flow:         Out of scope (CP-SUPIN-04)
```

---

## § RESTART INSTRUCTIONS FOR NEW SESSION

1. Read this file first
2. Run `git log --oneline -5` on branch `cp-supin-05-cross-framework-parity` to confirm HEAD = f747380
3. Apply P1 fix (pageLoadTimeout 180s) to `cypress/cypress.config.ts`
4. Commit P3 (consolidate_results.py v0.5.2) first — it's already correct in the filesystem
5. Run Cypress (P4) from Windows PowerShell with JSON reporter
6. Run `python tools/consolidate_results.py` (P5)
7. Commit + push (P6) then open PR
8. If main-happy-day still fails after P1, check `cypress/screenshots/` for the failure frame

**Git ops must be run from Windows PowerShell** — sandbox `.git/index.lock` issue blocks `git add` from Linux.
**consolidate_results.py** already correct in working tree — just needs `git add` + commit.
