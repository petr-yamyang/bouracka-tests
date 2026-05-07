# Cross-framework parity execution — Sonnet branch session handoff — v0.1 CS

> **Trigger.** CP-SUPIN-05 mid-session 2026-05-07 — Pete:
> "Playwright is well ahead of all other automation platform test suit
> implementation. Now we have good enough reference test set and also TestPlan
> as proved source of truth so let's start — maybe by Sonnet session would be
> good enough — implementation of test suits on 2 other platforms to fit same
> scope and see directly results and advantages/disadvantages on real case".
>
> **Cíl tohoto handoff doc.** Detailní executable instrukce pro Sonnet branch
> session, aby autonomně portovala plný Playwright suite na **Cypress** +
> **Selenium pytest**, dosáhla parity, a sebrala výsledky pro evidence-based
> platform comparison.
>
> **Audience.** Sonnet branch session (in-context), Pete (governance),
> Cypress/Selenium developers.
> **Pre-read.**
> 1. `_specs/PLATFORM-ASSESSMENT-v0.1-CS.md` v0.2 (decision log + scoring)
> 2. `_specs/CROSS-FRAMEWORK-DATA-SHARING-v0.1-CS.md` (fixture pattern)
> 3. `_specs/MIMT-NATIVE-AUTOMATION-ASSESSMENT-v0.1-CS.md` v0.2 (B+C strategy)
> 4. `playwright/tests/{bring-up-smoke,a1-main-happy-day-demo,a2-alternates-demo}.spec.ts` (source of truth)

---

## §1. Scope a non-scope

### §1.1 Scope (DO)

- **Cypress** — port full a1-main-happy-day + a2-alternates (8 ALT- variants); already has bring-up smoke
- **Selenium pytest** — same as above; already has bring-up smoke
- **Shared fixture loader** — implement `data-loader.ts` (Cypress) + `data_loader.py` (Selenium) per `_specs/CROSS-FRAMEWORK-DATA-SHARING-v0.1-CS.md`
- **Drift guard port** — same URL polling pattern as Playwright `navToVerification` v2
- **Results consolidation** — common JSON output schema → `tools/consolidate_results.py`
- **Run against Cíl 1 (DEMO public) + Cíl 2 (tst.demo)** — once Pete confirms Cíl 2 access

### §1.2 NOT in scope (don't do)

- Modify Playwright spec files (those are the source-of-truth reference)
- Modify Excel TestPlan schema
- Touch TestCafe (frozen — drop in v0.6.0 per platform decision)
- Touch ReadyAPI / Postman (B/E framework, separate iteration)
- Implement mobile real-device (Selenium+Appium) — that's CP-SUPIN-07, this is just F/E pytest
- Author new TC; only port existing 9 (3 specs × 1 + 8 ALT- = 10 actually, count below)

## §2. Test inventory — TCs to port

| TC code | Playwright source | Cypress target | Selenium target | Difficulty |
|---------|-------------------|----------------|-----------------|------------|
| **TC-CP-001** | `playwright/tests/bring-up-smoke.spec.ts` | `cypress/e2e/bring-up-smoke.cy.ts` ✅ existing | `selenium/tests/test_bring_up_smoke.py` ✅ existing | done |
| **TC-CP-A1-MAIN-DEMO** | `playwright/tests/a1-main-happy-day-demo.spec.ts` | `cypress/e2e/a1-main-happy-day-demo.cy.ts` NEW | `selenium/tests/test_a1_main_happy_day_demo.py` NEW | ★★★ HARD |
| **TC-CP-A2-ALT-1** | `playwright/tests/a2-alternates-demo.spec.ts` | `cypress/e2e/a2-alternates-demo/alt-1-rp-regex.cy.ts` NEW | `selenium/tests/a2_alternates/test_alt_1_rp_regex.py` NEW | ★★ med |
| **TC-CP-A2-ALT-4** | (same file, line ~118) | `.../alt-4-gdpr-consent.cy.ts` NEW | `.../test_alt_4_gdpr_consent.py` NEW | ★★ med |
| **TC-CP-A2-ALT-5** | (same file, line ~134) | `.../alt-5-slovak-prefix.cy.ts` NEW | `.../test_alt_5_slovak_prefix.py` NEW | ★ easy |
| **TC-CP-A2-ALT-6** | (same file, line ~140) | `.../alt-6-police-card.cy.ts` NEW | `.../test_alt_6_police_card.py` NEW | ★ easy |
| **TC-CP-A2-ALT-7** | (same file, line ~158) | `.../alt-7-enumerations.cy.ts` NEW | `.../test_alt_7_enumerations.py` NEW | ★ easy (pure API) |
| **TC-CP-A2-ALT-8** | (same file) | `.../alt-8-demo-banner.cy.ts` NEW | `.../test_alt_8_demo_banner.py` NEW | ★ easy |
| **TC-CP-A2-ALT-9** | (same file) | `.../alt-9-post-reports-drift.cy.ts` NEW | `.../test_alt_9_post_reports_drift.py` NEW | ★★ med (drift-aware) |
| **TC-CP-A2-ALT-10** | (same file) | `.../alt-10-spa-post-probe.cy.ts` NEW | `.../test_alt_10_spa_post_probe.py` NEW | ★★★ HARD (network capture parity) |

**Total = 10 TCs × 2 frameworks = 20 ports** (8 of which already done as smoke = 12 net new).

## §3. Recommended port order (low-effort first → drift-dependent last)

### §3.1 Phase A — easy wins (no SPA navigation needed)

Order: ALT-7 → ALT-8 → ALT-6 → ALT-5

| TC | Why easy | What to verify |
|----|----------|----------------|
| ALT-7 | pure API (`request.get`); no UI | enumerations endpoints return expected codelist + protected return 403 |
| ALT-8 | static text on rozcestnik | DEMO banner visible |
| ALT-6 | accordion expand → assert text | "Kdy volat Policii" card opens, 3 bullets visible, `tel:158` link present |
| ALT-5 | dropdown click → option visible | "+421" Slovak prefix discoverable in dropdown |

**Estimated effort per TC per framework:** 30-60 minutes once first one works.

**Acceptance:** all 4 GREEN on both Cypress + Selenium against DEMO public.

### §3.2 Phase B — drift-aware (SPA navigation but drift-guard exits)

Order: ALT-9 → ALT-10 → ALT-1 → ALT-4

| TC | Why medium | What to verify |
|----|------------|----------------|
| ALT-9 | direct API POST; expect 200 OR 403; capture response body | drift characterization works in framework's HTTP client |
| ALT-10 | SPA-driven flow; capture network event for POST /api/reports | framework's network capture + attachment |
| ALT-1 | Phase 2 ŘP regex negative; needs full navToVerification + drift skip | framework can react to URL change OR fall through to drift-skip cleanly |
| ALT-4 | Phase 1 GDPR negative; needs PUT /reporter network observer | framework's per-test network listener |

**Estimated effort per TC per framework:** 1-2 hours each given drift-guard helper.

**Acceptance:** ALT-9 GREEN-soft (200 OR 403), ALT-10 produces alt10 artefact, ALT-1/ALT-4 SKIPPED-with-rationale on Cíl 1 (where drift active).

### §3.3 Phase C — full E2E (the hard one)

Order: TC-CP-A1-MAIN-DEMO last

| TC | Why hard | What to verify |
|----|----------|----------------|
| A1-MAIN | full happy-day E2E: Phase 0 → A → 1 → 2 → 2.5 → 3 → 4 → /success; multiple React-controlled inputs (OTP, textarea, autocompletes); multi-screen sequence with retries possible | framework can drive 150+ second flow with drift-guard skip |

**Estimated effort per framework:** 1-2 days given previous helpers shaped.

**Acceptance:** SKIPPED-with-rationale on Cíl 1 (drift active) — same as Playwright; framework completes drift-skip in < 30s.

## §4. Shared fixture loader pattern (must implement first)

Per `_specs/CROSS-FRAMEWORK-DATA-SHARING-v0.1-CS.md` §4, before any port:

### §4.1 Cypress — `cypress/support/data-loader.ts`

```typescript
// cypress/support/data-loader.ts — NEW
import * as YAML from "yaml";
const fixturesRoot = "../../fixtures/test-data";

export function loadFixture<T = any>(name: string): T {
  // Cypress quirk: cy.fixture() loads from cypress/fixtures/, not arbitrary path
  // Workaround: cy.task plugin to read from project-root fixtures/
  return cy.task("loadFixture", `${name}.yaml`) as any;
}

// cypress/plugins/index.ts — register the task
const fs = require("fs");
const path = require("path");
const yaml = require("yaml");
module.exports = (on, config) => {
  on("task", {
    loadFixture(name) {
      const p = path.resolve(__dirname, "../../fixtures/test-data", name);
      return yaml.parse(fs.readFileSync(p, "utf-8"));
    }
  });
};
```

### §4.2 Selenium pytest — `selenium/helpers/data_loader.py`

```python
# selenium/helpers/data_loader.py — NEW
from pathlib import Path
import yaml

FIXTURES_ROOT = Path(__file__).resolve().parents[2] / "fixtures" / "test-data"

def load_fixture(name: str) -> dict:
    p = FIXTURES_ROOT / f"{name}.yaml"
    with open(p, encoding="utf-8") as h:
        return yaml.safe_load(h)
```

Both **MUST be in place before any TC port begins**.

## §5. Drift guard port — pattern transfer

Playwright source (already in `playwright/tests/a2-alternates-demo.spec.ts:43`):

```typescript
async function navToVerification(page, testInfo?: any) {
  await page.goto(`${BASE}/formular/`, { waitUntil: "networkidle", timeout: 30_000 });
  await dismissCookieBanner(page);
  await page.getByRole("button", { name: /vyplnit záznam/i }).first().click();
  await page.getByRole("button", { name: /Rozumím/i }).click();
  // POLL the URL until we see either /verification or /error/timeout — 30s budget
  const deadline = Date.now() + 30_000;
  let resolved: "verification" | "error-timeout" | "deadline" = "deadline";
  while (Date.now() < deadline) {
    const url = page.url();
    if (/\/verification/.test(url)) { resolved = "verification"; break; }
    if (/\/error\/timeout/.test(url)) { resolved = "error-timeout"; break; }
    await page.waitForTimeout(500);
  }
  if (resolved === "error-timeout") {
    test.skip(true, "DEMO drift 2026-05-07 v2 …");
  }
  await expect(page).toHaveURL(/\/verification/, { timeout: 5_000 });
}
```

### §5.1 Cypress port pattern

```typescript
// cypress/support/nav-helpers.ts
export function navToVerificationOrSkip(): Cypress.Chainable {
  cy.visit(`${Cypress.env('BOURACKA_BASE') || 'https://demo.bouracka.cz'}/formular/`);
  dismissCookieBanner();
  cy.findByRole("button", { name: /vyplnit záznam/i }).first().click();
  cy.findByRole("button", { name: /Rozumím/i }).click();

  // Poll URL — use cy.url with retry; standard Cypress assertion handles retries
  return cy.url({ timeout: 30_000 }).then((url) => {
    if (/\/error\/timeout/.test(url)) {
      cy.log("DEMO drift v2: routed to /error/timeout — skipping with rationale");
      cy.task("recordDrift", { url, ts: new Date().toISOString() });
      // Cypress doesn't have native test.skip(); use Mocha context.skip()
      return cy.wrap(null).then(function () { (this as any).skip(); });
    }
    return cy.url().should("match", /\/verification/);
  });
}
```

### §5.2 Selenium port pattern

```python
# selenium/helpers/nav_helpers.py
import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def nav_to_verification_or_skip(driver, base_url):
    driver.get(f"{base_url}/formular/")
    dismiss_cookie_banner(driver)
    driver.find_element(By.XPATH, "//button[contains(., 'VYPLNIT ZÁZNAM')]").click()
    WebDriverWait(driver, 15).until(EC.url_contains("/informations"))
    driver.find_element(By.XPATH, "//button[contains(., 'Rozumím')]").click()

    # Poll URL — 30s budget
    deadline = time.time() + 30
    while time.time() < deadline:
        url = driver.current_url
        if "/verification" in url:
            break
        if "/error/timeout" in url:
            pytest.skip(
                f"DEMO drift 2026-05-07 v2: routed to /error/timeout. "
                f"Hypothesis: reCAPTCHA-v3 score below threshold for HeadlessChrome UA. URL: {url}"
            )
        time.sleep(0.5)
    assert "/verification" in driver.current_url, f"Expected /verification, got {driver.current_url}"
```

## §6. Per-framework gotchas to expect

### §6.1 Cypress

| Gotcha | Workaround |
|--------|-----------|
| React-controlled inputs (OTP) | `cy.window().then(win => { /* native setter pattern */ })` — same pattern as Playwright `page.evaluate` |
| Same-origin restrictions on cross-origin calls | Use `cy.origin()` 12.x+ if RUIAN/Maps tests need cross-domain navigation |
| File upload | `cy.selectFile()` (12.x+); for hidden inputs use `{ action: 'select' }` |
| Per-test network listener | `cy.intercept('POST', '/api/reports', (req) => { /* capture */ })` — equivalent to Playwright `page.on('request')` |
| Skip-with-rationale | `this.skip()` in Mocha context, not `test.skip()` |
| Multi-tab / multi-browser | Cypress doesn't support cross-tab — none of our tests need it (single-page SPA) |

### §6.2 Selenium

| Gotcha | Workaround |
|--------|-----------|
| React-controlled inputs | `driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', {bubbles: true}))", input_el, value)` |
| Headless flag | `chrome_options.add_argument("--headless=new")` (Chrome 109+); legacy `--headless` deprecated |
| Wait patterns | Use `WebDriverWait` + `expected_conditions`, NOT `time.sleep()` |
| Network capture | Selenium 4 BiDi: `driver.devtools.send_command("Network.enable")` + listener. Or use [`selenium-wire`](https://pypi.org/project/selenium-wire/) for simpler API. |
| File upload | `element.send_keys("/path/to/file")` for hidden file inputs |
| reCAPTCHA stealth | Use [`undetected-chromedriver`](https://pypi.org/project/undetected-chromedriver/) — best-in-class stealth; preserves WebDriver API |

## §7. Acceptance criteria

### §7.1 Per-TC acceptance

Each ported TC MUST:

1. **Same TC code** in test title (`TC-CP-001`, `TC-CP-A2-ALT-7`, …)
2. **Same `covers()` annotation** pointing to same TT codes (e.g. `covers("TT-LOV-vehicleBrands")`)
3. **Same fixture data** loaded via `loadFixture()` — no inline string duplication
4. **Same expected outcome** as Playwright counterpart (PASS / FAIL / SKIP)
5. **Drift guard** if applicable — `test.skip()` / `pytest.skip()` / `this.skip()` with same rationale text

### §7.2 Per-framework acceptance

| Framework | Run command | Expected outcome (Cíl 1) |
|-----------|-------------|--------------------------|
| Cypress | `npx cypress run --browser chromium` | 4 GREEN + 4 SKIPPED + 1 GREEN-soft + 1 GREEN (probe) = same as Playwright |
| Selenium | `py -m pytest selenium/tests/ -v` | same |

### §7.3 Cross-framework consistency check

Run `tools/consolidate_results.py` (NEW; see §8) — output must show:

```json
{
  "cils": "1 (demo.bouracka.cz)",
  "frameworks": {
    "playwright": { "passed": 5, "skipped": 4, "soft_passed": 1 },
    "cypress":    { "passed": 5, "skipped": 4, "soft_passed": 1 },
    "selenium":   { "passed": 5, "skipped": 4, "soft_passed": 1 }
  },
  "tcs_with_divergence": []     ← MUST be empty for parity claim
}
```

Any TC that PASSES on Playwright but FAILS on Cypress (or vice versa) is a
**framework-divergence** finding — investigate + document separately.

## §8. Result consolidation tool — `tools/consolidate_results.py`

NEW Python tool to be authored by Sonnet branch session:

```python
#!/usr/bin/env python3
"""
consolidate_results.py — merge per-framework test outputs into single comparison JSON.

Reads:
  - playwright-report/results.json
  - cypress/cypress-results/cypress-results.json
  - selenium-report/results.json (pytest-json-report plugin output)

Writes:
  - runs/cross-framework-{date}.json
  - runs/cross-framework-{date}.md (human-readable summary)
"""
# (full impl by Sonnet — pattern from tools/coverage_audit.py)
```

Schema per TC (common JSON):

```json
{
  "tc_code": "TC-CP-A2-ALT-7",
  "framework": "playwright|cypress|selenium",
  "status": "passed|failed|skipped|soft_passed",
  "duration_ms": 12345,
  "env": "https://demo.bouracka.cz",
  "viewport": "375x*",
  "covered_tt": ["TT-LOV-insuranceCompanies", "TT-LOV-vehicleBrands"],
  "error_message": null,
  "trace_ref": "test-results/.../trace.zip",
  "framework_specific_notes": "..."
}
```

## §9. Sonnet session execution plan (suggested 4 working days)

### Day 1 — preparatory + Cypress easy wins

- [ ] Read pre-read list (§ above)
- [ ] Implement `cypress/support/data-loader.ts` + plugin task
- [ ] Verify smoke `bring-up-smoke.cy.ts` GREEN against DEMO public
- [ ] Port ALT-7 (API only) → run GREEN
- [ ] Port ALT-8 (static text) → run GREEN
- [ ] Port ALT-6 (accordion) → run GREEN
- [ ] Port ALT-5 (dropdown) → run GREEN
- [ ] **End-of-day**: 4 of 8 ALT-* GREEN on Cypress

### Day 2 — Cypress drift-aware + a1-main + Selenium prep

- [ ] Implement Cypress `nav-helpers.ts` with drift guard
- [ ] Port ALT-9 (drift-aware) → GREEN-soft
- [ ] Port ALT-10 (SPA probe) → GREEN
- [ ] Port ALT-1, ALT-4 (drift-skip path) → SKIPPED on Cíl 1
- [ ] Begin Selenium prep: `selenium/helpers/data_loader.py` + `nav_helpers.py`
- [ ] **End-of-day**: Cypress 100% parity confirmed

### Day 3 — Selenium full ports

- [ ] Port ALT-7 → ALT-8 → ALT-6 → ALT-5 (Phase A) — should be quick once helpers in place
- [ ] Port ALT-9 (drift-aware) — Selenium 4 BiDi for response capture
- [ ] Port ALT-10 (SPA probe) — `selenium-wire` for request capture if BiDi insufficient
- [ ] Port ALT-1, ALT-4 (drift-skip)
- [ ] **End-of-day**: 8 of 8 ALT-* parity on Selenium

### Day 4 — TC-CP-A1-MAIN-DEMO + consolidation

- [ ] Port full a1-main-happy-day to Cypress (will mostly drift-skip on Cíl 1)
- [ ] Port full a1-main-happy-day to Selenium
- [ ] Author `tools/consolidate_results.py`
- [ ] Run all 3 frameworks against Cíl 1 → consolidated report
- [ ] If Pete confirms Cíl 2 access: same against Cíl 2
- [ ] Author summary doc `_specs/CROSS-FRAMEWORK-PARITY-RESULTS-v0.1-CS.md`
- [ ] Update Pete with finding: which TCs diverge per framework, real evidence-based pros/cons

## §10. Hand-back to Opus session

Sonnet session sync-back when done:

1. **Commit branch** with all changes per `_specs/GIT-SYNC-CHECKLIST-v0.1-CS.md` commit message conventions
2. **Author** `SYNCHRO-OPUS-FROM-SONNET-CP-SUPIN-05-{date}.md` with:
   - What was ported (TC × framework matrix)
   - What was easy / hard / failed
   - Concrete framework-divergence findings (if any)
   - Recommendations for v0.5.1 / v0.6.0 priorities
3. **Update** `PLATFORM-ASSESSMENT-v0.1-CS.md` v0.3 with empirical scores
4. **Update** `CHANGELOG.md` with the parity-port entries

## §11. Open questions

| # | Otázka | Owner |
|---|--------|-------|
| Q-PARITY-1 | Cypress version — 13.x latest, or pin to 12.x for stability? | Sonnet starts with 13.x default |
| Q-PARITY-2 | Selenium 4 BiDi vs `selenium-wire` for network capture? | Sonnet evaluate empirically; pick whichever works |
| Q-PARITY-3 | If Cypress + Selenium reveal a Playwright bug → file as new bug? | yes — log via `BUG-CP-{TC}-FRAMEWORK-DIVERGENCE-{slug}` |
| Q-PARITY-4 | Cíl 2 (tst.demo) access — Pete confirms before Day 4 | Pete |
| Q-PARITY-5 | Reporter consolidation — invent new schema or follow Allure? | Common JSON per §8; Allure later |

## §12. Status

| Item | Hodnota |
|------|---------|
| Doc | `_specs/CROSS-FRAMEWORK-PARITY-EXECUTION-v0.1-CS.md` |
| Verze | v0.1 |
| Datum | 2026-05-07 mid-session |
| Audience | Sonnet branch session + Pete + Cypress/Selenium devs |
| Estimated total effort | 4 working days (Sonnet single session) |
| Blocking deps | (1) GitHub repo pushed (Pete-side), (2) Sonnet session start trigger |
| Acceptance | parity for 10 TC × 2 frameworks + consolidated report + framework-divergence audit |
| Companion | `_specs/PLATFORM-ASSESSMENT-v0.1-CS.md` v0.2 (will become v0.3 with empirical data) |
| Status | handoff ready; awaiting Sonnet session start |
