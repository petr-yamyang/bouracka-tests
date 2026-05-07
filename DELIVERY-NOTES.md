# DELIVERY-NOTES — bouracka-tests v0.1.0

**Iteration:** CP-SUPIN-02 — deep public recon + Excel TestPlan v0.1 seeded.
**Date:** 2026-05-05
**Author:** Cowork Opus task-force on the SUPIN/bouracka campaign.

> This file accompanies `bouracka-tests-v0.1.0.zip`. It is what the user
> (Petr) forwards to the SUPIN tester, and what the tester reads first.

---

## 1. What's in this deliverable (NEW / REPLACED / UNCHANGED — per R-STRUCT-1)

### NEW

- `bouracka-tests/` folder skeleton per CLIENT-PILOT-SUPIN-V0.1.md §8.
- 11-sheet `BOURACKA-TESTPLAN-v0.1.xlsx` per scope §5.1 / §5.2:
  - 6 candidate TestTargets (TT-CP-001..006) with R-CAST-1 tagging
    (decomposition_kind + component/behaviour ref + coverage_basis).
  - 4 TestCases (TC-CP-001..004) with viewport_spec, env_coverage,
    framework_targets, R-FAIL-1 pairing (001↔002 + 003↔004).
  - 4 TestData rows; 1 TestSet (Week-1); 3 TestEnvironments (TST + DMO
    + PUB-dev).
  - Empty TestRuns, TestRunResults, Bugs sheets ready for first
    execution + reporter writes.
  - Reports sheet with auto-pivot formulas (per-env pass rate, per-TC
    trend, bug aging by priority).
  - Glossary CS↔EN, Changelog.
- Playwright + Cypress + TestCafe scaffolds for **TC-CP-001** and
  **TC-CP-002** (the re-scoped wizard-entry happy/failure pair — see
  OQ-CP-12). Every step carries an inline R-CAST-2 comment
  (control_point / trigger_point / data_collection_point / assertion).
- Skeleton specs for TC-CP-003 + TC-CP-004 with `test.skip()` + reason
  pointing at OQ-CP-14 + OQ-CP-15.
- PowerShell launchers: `run-playwright.ps1`, `run-cypress.ps1`,
  `run-testcafe.ps1`, `run-all.ps1`, `package-results.ps1`,
  `package-deliverable.ps1`.
- README-CS.md + README-EN.md (Czech-first per C-6).
- `recon/` folder with PUBLIC-recon material (SITEMAP +
  TEST-TARGET-CANDIDATES + 4 SCR-NNN + 5 FLW-NNN + 5 INT-NNN);
  confidential subfolders gitignored per scope §7.
- `env/` config: `public.json` (full selectors + expected values),
  `tst.json` + `tst-demo.json` (inherit from public; carry
  divergence-overrides + hook URLs once user-supplied).
- `.gitignore` + `package.json` + `fixtures/invalid-login.json`.

### REPLACED

- `TC-CP-001/002` original placeholders ("Přihlášení platnými/neplatnými
  údaji") → re-scoped per OQ-CP-12 to wizard-entry happy + police-call
  branch failure. Original placeholder rows in CLIENT-PILOT-SUPIN §4.1
  remain authoritative until OQ-CP-12 closes; this deliverable
  documents the recon-driven mapping in
  `recon/TEST-TARGET-CANDIDATES.md` and in `02_TestCases.notes`.

### UNCHANGED

- The 6 binding rules from the archive: R-METH-1..4, R-STRUCT-1/2,
  R-CAST-1/2, R-FAIL-1, R-PR-* (priority matrix), Czech-first,
  mobile-first.
- The 10-iteration plan CP-SUPIN-01..10 in CLIENT-PILOT-SUPIN §9.

## 2. SHA256 + size of the deliverable zip

> Filled by `package-deliverable.ps1` at zip time:

```
SHA256 (filled at packaging): ____________________________________________
Size:   ___ KB
```

## 3. Tester instructions (TL;DR)

```powershell
cd C:\Tests\bouracka-tests
npm install
npx playwright install chromium
.\scripts\run-all.ps1 -Env tst
.\scripts\package-results.ps1 -Tester "<surname>"
# email back the resulting bouracka-results-YYYY-MM-DD-<surname>.zip
```

Full instructions: `README-CS.md` (Czech) / `README-EN.md` (English).

## 4. Open questions blocking next iteration (CP-SUPIN-03)

| OQ | Pri | Question | Blocks |
|----|:---:|----------|--------|
| OQ-CP-11 | A | Add `bouracka.cz` + `*.supin.cz` to Cowork sandbox egress allowlist? | recon depth on subsequent ThinkPad runs |
| OQ-CP-12 | A | Re-scope TC-CP-001/002 confirmation: gateway smoke + police-branch (RECOMMENDED) vs SMS-OTP signing vs wait-for-tst-recon? | TC-CP-001/002 framework code |
| OQ-CP-14 | A | reCAPTCHA posture in `tst.*` — bypass token, mock, or real-challenge? | TC-CP-003/004 framework code |
| OQ-CP-15 | A | tst.* recon templates (full set per scope §6.2) — when does user begin filling? | TC-CP-003/004 implementation depth |

## 5. Where this fits in the v0.2 cycle

- CP-SUPIN-02 closes here.
- CP-SUPIN-03 = Playwright impl of TC-CP-001/002 + Excel reporter
  (1 session). Pre-condition: OQ-CP-12 closes.
- CP-SUPIN-04 = Cypress impl of same (1 session).
- CP-SUPIN-05 = TestCafe impl (gated; only if Gate 1 demands).
- CP-SUPIN-06 = Playwright TC-CP-003/004 (1 session). Pre-condition:
  OQ-CP-14 + OQ-CP-15 close.
- CP-SUPIN-07 = Cypress TC-CP-003/004 (1 session).
- CP-SUPIN-08 = `bouracka-tests-v0.1.zip` packaged + emailed (this is
  the week-end deliverable target per scope §9).

## 6. Verification checklist (passed before this delivery)

- [x] Excel `recalc.py` returns `total_errors: 0`, `total_formulas: 36`.
- [x] R-CAST-1 — every TT carries `decomposition_kind` + ref + `coverage_basis`.
- [x] R-CAST-2 — every TC framework spec carries inline step-kind comments
      (Playwright 18 / Cypress 16 / TestCafe 13 step-tagged comments).
- [x] R-FAIL-1 — TC-CP-001↔002, TC-CP-003↔004 paired.
- [x] Mobile-first — all 4 TCs carry viewport_spec `320/375/414/1024/1512`.
- [x] R-METH-1..4 — methodology-neutral labels (TestSet uses
      `WorkPackage-CP-SUPIN-W19`, not "Sprint" / "Epic").
- [x] R-STRUCT-1 — this NEW/REPLACED/UNCHANGED block present.
- [x] CS-first — README-CS, glossary CS column, all flow-step copy CS.
- [x] Confidentiality — `recon/bugs/` + `recon/divergences/` gitignored.

## 7. Known limitations of v0.1

- `TC-CP-003/004` are **skeleton** specs only; depth lands when
  OQ-CP-14 + OQ-CP-15 close.
- Excel reporters are **scaffold** — they buffer to JSONL today; the
  JSONL → workbook merge ships in CP-SUPIN-03 to avoid xlsx-write
  contention.
- `env/tst.json` + `env/tst-demo.json` carry **null** placeholders
  for `recaptcha_bypass_token`, hook URLs and registry stub URLs —
  these are populated OOB by user when the tst.* envs are
  recon'd.
- Public bouracka.cz wizard interior was **deliberately not driven**
  past `/formular` to avoid bot-detection blow-back on production.

---

*Delivery notes — generated as part of CP-SUPIN-02 close.*
