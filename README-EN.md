# bouracka-tests — Tester guide (EN)

Automated test suite for `tst.bouracka.cz` and `tst.demo.bouracka.cz`.
Ship version: `v0.1.0` (CP-SUPIN-02 seed; first executable wizard scenarios
land in `v0.1.1`).

## 1. Tester-laptop prerequisites

| Item | Version | Note |
|------|---------|------|
| Windows | 10 / 11 | x64 |
| Node.js | ≥ 18.x (20 LTS recommended) | no admin install needed if Node already present |
| npm | ≥ 9 | bundled with Node |
| Chrome / Chromium | ≥ 132 | Playwright installs its own binary |
| PowerShell | 5.1 / 7+ | Windows native |
| Network | reach `tst.bouracka.cz`, `tst.demo.bouracka.cz` from inside SUPIN |

## 2. First run

```powershell
# 1. Extract the zip somewhere (e.g. C:\Tests\bouracka-tests)
cd C:\Tests\bouracka-tests

# 2. Install dependencies (one-time)
npm install
npx playwright install chromium

# 3. Run all three frameworks against TST
.\scripts\run-all.ps1 -Env tst

# 4. Bundle results for return e-mail
.\scripts\package-results.ps1 -Tester "your-surname"
```

Output: `bouracka-results-YYYY-MM-DD-your-surname.zip` — return to author.
SHA256 in `SHA256SUMS-*.txt` next to the zip.

## 3. Single-framework run

```powershell
.\scripts\run-playwright.ps1 -Env tst
.\scripts\run-cypress.ps1    -Env tst-demo
.\scripts\run-testcafe.ps1   -Env tst
```

`-Env` options: `tst` | `tst-demo` | `public` (`public` is dev-time only —
hard-real production scenarios are never executed).

## 4. What's in v0.1 deliverable

- Folder layout per scope §8 — three frameworks + shared env config + fixtures.
- Excel TestPlan `BOURACKA-TESTPLAN-v0.1.xlsx` — 11 sheets, ItemBase columns,
  Sev × Urg → Pri.
- Playwright + Cypress + TestCafe scenarios for **TC-CP-001** (wizard entry —
  happy) and **TC-CP-002** (police-call branch — failure pair).
- Skeleton specs for **TC-CP-003** + **TC-CP-004** (full wizard end-to-end) —
  implementation pending user-supplied tst.* recon templates (OQ-CP-15) and
  reCAPTCHA-posture decision (OQ-CP-14).

## 5. Mobile-first — viewport sweep

Each Playwright run sweeps 4 viewports per env:
- desktop (1280×720)
- mobile-320 (320×568)
- mobile-375 (375×667)
- mobile-414 (414×896)

Cypress viewport via `cy.viewportPreset()` helper (see
`cypress/support/e2e.ts`).

## 6. Top 5 likely errors and fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `npm install` timeout | proxy/firewall blocks registry.npmjs.org | `npm config set proxy http://...` |
| `npx playwright install` fails | admin restriction | ensure write access to `%LOCALAPPDATA%\ms-playwright`; allow `cdn.playwright.dev` |
| `Cypress not found` | binary not downloaded | `npx cypress install` |
| Test fails: `tst.bouracka.cz` not reachable | not on SUPIN network or VPN down | `Test-NetConnection tst.bouracka.cz -Port 443` |
| reCAPTCHA challenge shows in `tst.*` | bypass token not configured | set `env/tst.json::recaptcha_bypass_token` from OOB e-mail |

## 7. Confidentiality

- This suite carries **no** sensitive data. Real tester credentials, IDs,
  document photos etc. arrive OOB (e-mail) and live in `fixtures/secrets/`
  (gitignored). Delete `secrets/` after iteration close.
- Result archives may include personalised data (screenshots, network logs);
  review before returning.

## 8. Contact

`info@bouracka.cz` (operator — ČKP).
Suite author: Petr Žemla (OOB contact).
