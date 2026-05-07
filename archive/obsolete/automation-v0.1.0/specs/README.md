# specs/ — TestCase development specs

> Per `_specs/TESTCASE-SPEC-FORMAT-v0.1.md`.

Each `TC-CP-NNN-SPEC.md` here is the formal **dev-session input** for
that TestCase — self-sufficient enough that a Sonnet automated dev
session can pick it up and emit framework code (Playwright / Cypress /
TestCafe) directly, without iterative back-and-forth on selectors,
expected values, env divergences, viewport applicability, fixtures, or
acceptance criteria.

## Inventory

| TC | Spec | Status | Maps to TT |
|----|------|--------|------------|
| TC-CP-001 | [TC-CP-001-SPEC.md](TC-CP-001-SPEC.md) | draft (full) | TT-CP-R1-001 |
| TC-CP-002 | [TC-CP-002-SPEC.md](TC-CP-002-SPEC.md) | draft (full) | TT-CP-R1-001 + TT-CP-R1-004 |
| TC-CP-003 | [TC-CP-003-SPEC.md](TC-CP-003-SPEC.md) | draft (skeleton) | TT-CP-R1-002 |
| TC-CP-004 | [TC-CP-004-SPEC.md](TC-CP-004-SPEC.md) | draft (skeleton; 11 variants catalogued) | TT-CP-R1-003 + TT-CP-R1-004 |

## Authoring a new TC spec

1. Copy `_TC-TEMPLATE.md` → `TC-CP-NNN-SPEC.md`.
2. Fill all 14 sections per `_specs/TESTCASE-SPEC-FORMAT-v0.1.md` §3.
3. Run the §7 validation checklist.
4. Add the Excel row in `02_TestCases` and set its `dev_spec_path`
   column to `specs/TC-CP-NNN-SPEC.md`.
5. Note in `11_Changelog`.

## Promoting a skeleton spec to full

1. When the missing recon material lands (user template, OQ
   resolution), update the spec's status to `draft (full)`.
2. Bump `spec_version` (additive change → patch bump; structural
   change → minor bump).
3. Update `last_updated` + `last_updated_by`.
4. Re-run the validation checklist.
5. Note in changelog.

## Skeleton specs

A spec marked `draft (skeleton)` carries enough structure to plan
coding effort but NOT enough to drive code emission directly. Skeletons
are useful as:

- Coverage estimates for iteration planning.
- Slots that recon materials fill into.
- Communication artefacts to the user / colleague: "here's what we
  need from you to take this from skeleton → full."

A skeleton MUST list its blocking OQs in the Status footer.

## Validation status across all specs

Run from repo root:

```powershell
# CP-SUPIN-03+ — implement scripts/validate-tc-specs.ps1 to run §7
# checklist across all specs/TC-CP-*-SPEC.md and report fails
.\scripts\validate-tc-specs.ps1
```

For now (CP-SUPIN-02), validation is by-eye against the §7 checklist.
