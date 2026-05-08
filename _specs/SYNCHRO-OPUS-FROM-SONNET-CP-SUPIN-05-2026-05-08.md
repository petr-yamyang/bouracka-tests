# SYNCHRO — Opus ← Sonnet handback (CP-SUPIN-05)
**Date:** 2026-05-08  
**Branch:** `feature/cross-framework-parity` (or equivalent working branch)  
**Session:** Sonnet single-context session (continuation from prior Opus context)  
**Spec ref:** `_specs/CROSS-FRAMEWORK-PARITY-EXECUTION-v0.1-CS.md`

---

## 1. What was ported (TC × framework matrix)

| TC code | Playwright (src) | Cypress | Selenium pytest |
|---------|-----------------|---------|----------------|
| TC-CP-A1-MAIN-DEMO | ✅ source | ✅ ported | ✅ ported |
| TC-CP-A2-ALT-1 | ✅ source | ✅ ported | ✅ ported |
| TC-CP-A2-ALT-4 | ✅ source | ✅ ported | ✅ ported |
| TC-CP-A2-ALT-5 | ✅ source | ✅ ported | ✅ ported |
| TC-CP-A2-ALT-6 | ✅ source | ✅ ported | ✅ ported |
| TC-CP-A2-ALT-7 | ✅ source | ✅ ported | ✅ ported |
| TC-CP-A2-ALT-8 | ✅ source | ✅ ported | ✅ ported |
| TC-CP-A2-ALT-9 | ✅ source | ✅ ported | ✅ ported |
| TC-CP-A2-ALT-10 | ✅ source (truncated) | ✅ ported | ✅ ported |

**Total:** 9 TC × 2 new frameworks = **18 new test files** + 6 shared helper files.

---

## 2. New files delivered

### Shared infrastructure (Phase 0 — scaffold)

| File | Purpose |
|------|---------|
| `cypress/cypress.config.ts` | Rewritten — adds `loadFixture` + `recordDrift` tasks |
| `cypress/support/data-loader.ts` | `loadFixture<T>()` + `covers()` + TS interfaces |
| `cypress/support/nav-helpers.ts` | `dismissCookieBanner`, `navToVerificationOrSkip`, `setOtpDigits` |
| `selenium/conftest.py` | `driver()` fixture (mobile-emulated Chrome 375×667) + `base_url()` |
| `selenium/helpers/data_loader.py` | `load_fixture()` + `covers()` annotation |
| `selenium/helpers/nav_helpers.py` | `dismiss_cookie_banner`, `nav_to_verification_or_skip`, `set_otp_digits`, `set_react_input` |

### Phase A — Cypress (4 files)

```
cypress/e2e/a2-alternates-demo/alt-7-enumerations.cy.ts
cypress/e2e/a2-alternates-demo/alt-8-demo-banner.cy.ts
cypress/e2e/a2-alternates-demo/alt-6-police-card.cy.ts
cypress/e2e/a2-alternates-demo/alt-5-slovak-prefix.cy.ts
```

### Phase A — Selenium (4 files)

```
selenium/tests/a2_alternates/test_alt_7_enumerations.py
selenium/tests/a2_alternates/test_alt_8_demo_banner.py
selenium/tests/a2_alternates/test_alt_6_police_card.py
selenium/tests/a2_alternates/test_alt_5_slovak_prefix.py
```

### Phase B — Cypress (4 files)

```
cypress/e2e/a2-alternates-demo/alt-9-post-reports-drift.cy.ts
cypress/e2e/a2-alternates-demo/alt-10-spa-post-probe.cy.ts
cypress/e2e/a2-alternates-demo/alt-1-rp-regex.cy.ts
cypress/e2e/a2-alternates-demo/alt-4-gdpr-consent.cy.ts
```

### Phase B — Selenium (4 files)

```
selenium/tests/a2_alternates/test_alt_9_post_reports_drift.py
selenium/tests/a2_alternates/test_alt_10_spa_post_probe.py
selenium/tests/a2_alternates/test_alt_1_rp_regex.py
selenium/tests/a2_alternates/test_alt_4_gdpr_consent.py
```

### Full E2E — Cypress + Selenium (2 files)

```
cypress/e2e/a1-main-demo/main-happy-day.cy.ts
selenium/tests/a1_main/test_main_happy_day.py
```

### Tooling (1 file)

```
tools/consolidate_results.py
```

---

## 3. What was easy / hard / failed

### Easy ✅

- **ALT-7** (pure API): Trivial port to `cy.request()` and `requests.Session()`. No DOM needed.
- **ALT-8** (DEMO banner): Static text visibility. One-liner each.
- **ALT-6** (accordion): Straightforward click + text assertion. Minor Cypress `.or()` fallback adaptation.
- **ALT-9** (drift-aware API): Clean port — `cy.request(failOnStatusCode: false)` + `warnings.warn()` pattern.

### Medium ★★

- **ALT-5** (Slovak dropdown): Needs `navToVerificationOrSkip` — drift guard wires correctly in Cypress via `this.skip()` + Mocha function() context constraint. Selenium XPath for Předvolba label needed translate() trick for Czech diacritics.
- **ALT-4** (GDPR negative): Cypress `cy.intercept()` doesn't directly support "assert not called" — solved with closure boolean flag pattern.
- **ALT-1** (ŘP regex): Long flow through OTP verification. `setOtpDigits` / `set_otp_digits` helper reused cleanly.

### Hard ★★★

- **ALT-10** (SPA network capture): Playwright source file truncated at line 228 — ALT-10 body incomplete. Reconstructed from spec §3.2 + partial source. Cypress uses `cy.intercept()` with `req.continue()` response callback. Selenium uses dual strategy: CDP `Network.enable` + `add_cdp_listener` (Selenium 4.6+) with JS `window.fetch` override fallback. Both strategies accumulated into `all_captured` list.
- **A1-MAIN-DEMO full E2E**: 15-phase flow, RUIAN autocomplete, React-controlled inputs throughout, two per-vehicle helper sub-flows. Playwright source had typo `abel(/Model vozidla/i)` (missing `await page.getL`) — corrected in both ports.

### Structural decision: duplicate Phase 0+A click chain in A1-MAIN-DEMO

The A1-MAIN-DEMO Playwright test runs Phase 0 (VYPLNIT ZÁZNAM) and Phase A (Rozumím) inline **before** calling `navToVerification`. Cypress port mirrors this but then calls `navToVerificationOrSkip` as the drift poll step (the click chain was already done). Selenium port inlines the 30s URL poll directly after the Rozumím click — same semantics.

---

## 4. Concrete framework-divergence findings (empirical — DRY-RUN)

> **IMPORTANT:** All tests are DRY-RUN status. No live browser execution occurred in the sandbox (no Cypress/Chrome/ChromeDriver installed in the Linux sandbox). The following findings are **design-level**, not empirical from actual runs. Empirical data requires ThinkPad execution.

### Expected outcomes at Cíl 1 (demo.bouracka.cz) — per drift status

| TC | Playwright | Cypress | Selenium | Notes |
|----|-----------|---------|----------|-------|
| TC-CP-A2-ALT-7 | ✅ passed | ✅ passed | ✅ passed | Pure API — drift irrelevant |
| TC-CP-A2-ALT-8 | ✅ passed | ✅ passed | ✅ passed | Static text — drift irrelevant |
| TC-CP-A2-ALT-6 | ✅ passed | ✅ passed | ✅ passed | No SPA nav — drift irrelevant |
| TC-CP-A2-ALT-9 | 🟡 soft | 🟡 soft | 🟡 soft | 200 or 403 accepted |
| TC-CP-A2-ALT-10 | depends | depends | depends | Probe — captures whatever fires |
| TC-CP-A2-ALT-5 | ⏭ skip | ⏭ skip | ⏭ skip | navToVerification drift |
| TC-CP-A2-ALT-1 | ⏭ skip | ⏭ skip | ⏭ skip | navToVerification drift |
| TC-CP-A2-ALT-4 | ⏭ skip | ⏭ skip | ⏭ skip | navToVerification drift |
| TC-CP-A1-MAIN-DEMO | ⏭ skip | ⏭ skip | ⏭ skip | navToVerification drift |

No divergences expected at Cíl 1 — all frameworks have identical skip/pass/soft patterns.

### Known design differences (not divergences)

| Area | Playwright | Cypress | Selenium |
|------|-----------|---------|----------|
| OTP setter | `page.evaluate()` native setter | `cy.window()` native setter | `execute_script()` native setter |
| Skip mechanism | `test.skip(true, reason)` | `this.skip()` (Mocha ctx) | `pytest.skip(reason)` |
| Network capture (ALT-10) | `page.on('request')` + `page.on('response')` | `cy.intercept()` + `req.continue()` | CDP `add_cdp_listener` + JS fetch override |
| PUT monitor (ALT-4) | `page.on('response')` closure | `cy.intercept()` boolean flag | JS XHR + fetch override |
| Drift artefact | `testInfo.attach()` | `cy.task('recordDrift')` → JSONL | `RUNS_DIR/alt9-selenium-response.txt` |

---

## 5. Recommendations for Opus v0.5.1 / v0.6.0

### High priority

1. **Execute on ThinkPad** to get real empirical parity data. Run sequence:
   ```
   npx cypress run --browser chromium --spec "cypress/e2e/**/*.cy.ts" --reporter json \
     --reporter-options "output=cypress/cypress-results/results.json"
   py -m pytest selenium/ -v --json-report --json-report-file=selenium-report/results.json
   py tools/consolidate_results.py
   ```

2. **Verify ALT-10 CDP capture** on Chrome 109+ with Selenium 4.6+. If `add_cdp_listener` raises `AttributeError`, fall back to JS-only fetch capture — already coded.

3. **Playwright source integrity** — `playwright/tests/a2-alternates-demo.spec.ts` is truncated at 228 lines (ends mid-expression `last.responseHeaders`). The full ALT-10 response-header capture logic is missing from the file. Request Pete to check if the file was accidentally truncated in git push or if it's a line-ending encoding artifact.

### Medium priority

4. **ALT-6 police card** — Cypress `cy.contains(/přesahuje/)` fallback logic has an extra `.find()` step that won't work on text nodes. Simplified to `cy.contains(/Škoda.*přesahuje.*200\s*000\s*Kč/i)` with `cy.get('body').then()` guard — validate live.

5. **A1-MAIN-DEMO address autocomplete** — RUIAN `/api/streets` response may vary between Cíl 1 and Cíl 2. The `.first()` listbox option click is intentionally greedy. On Cíl 2 with richer data, validate that the first option is a usable address.

6. **`covers()` TT codes** — new codes introduced in this port:
   - `TT-SCRN-policeCard` (ALT-6)
   - `TT-SCRN-predvolba421` (ALT-5)
   - `TT-SCRN-demoBanner` (ALT-8)
   - `TT-ACTV-postReports` (ALT-9)
   - `TT-ACTV-spaPostProbe` (ALT-10)
   - `TT-FUNC-rpRegex` (ALT-1)
   - `TT-FUNC-gdprConsent` (ALT-4)
   - `TT-E2E-fullHappyDay` (A1-MAIN-DEMO)
   These need to be added to the V-model TT mapping sheet (`_specs/VMODEL-ASSEMBLY-TT-MAPPING-v0.1-CS.md`).

### Low priority

7. **Cypress 13.x strict-mode** — `cy.contains()` with multiple matches will throw in strict mode. Added `.first()` safeguards throughout. If strict-mode errors appear on run, add explicit `.first()` calls to failing selectors.

8. **Selenium `set_react_input`** — exported from `nav_helpers.py` but the Selenium `conftest.py` doesn't import it. It's imported directly by each test that needs it. Verify the import path resolves after `PYTHONPATH=.` is set (or via `conftest.py`'s `selenium/` root in `sys.path`).

---

## 6. Open questions inherited from spec

| # | Question | Status |
|---|---------|--------|
| Q-PARITY-2 | Selenium BiDi vs selenium-wire? | Resolved: CDP `add_cdp_listener` primary + JS fetch override fallback. No selenium-wire dependency added. |
| Q-PARITY-3 | Playwright source truncation | NEW — needs Pete to verify git file integrity |
| Q-PARITY-4 | Cíl 2 access | Pete-side — blocked |
| Q-PARITY-5 | Allure consolidation | Deferred — common JSON schema implemented, Allure adapter can be a v0.6.0 add-on |

---

## 7. Commit checklist

- [ ] `git add cypress/ selenium/ tools/consolidate_results.py _specs/SYNCHRO* CHANGELOG.md`
- [ ] Commit message: `feat(cp-supin-05): cross-framework parity ports — Cypress + Selenium 10 TC × 2 frameworks`
- [ ] Push branch + open PR to main
- [ ] Pete reviews + validates on ThinkPad before merge

---

_End of SYNCHRO doc — Sonnet → Opus handback 2026-05-08_
