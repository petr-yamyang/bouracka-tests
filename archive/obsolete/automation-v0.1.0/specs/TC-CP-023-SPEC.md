# TC-CP-023 — Určení viníka nehody — všechny radio varianty / Fault attribution — all radio variants

> Skeleton spec — surfaced as gap in `recon/COVERAGE-GAP-ANALYSIS.md`
> §2.3. Mapped to TT-CP-R1-D.

## Status

```yaml
spec_version: 0.1.0
spec_status: draft (skeleton)
maps_to_test_target: TT-CP-R1-D
release: R1
type: regression
priority: B
maps_to_flow: D14 swimlane (ACTIVITY-DIAGRAMS-v0.1.md §14)
maps_to_integrations: none (UI-only; persists to PDF F-112)
framework_targets: [playwright, cypress]
last_updated: 2026-05-05
last_updated_by: cowork-opus-cp-supin-02-rev6
```

## What this TC asserts

D14 is a radio-button screen where the user attributes fault. The
radio is integer(2)-typed per F-112 with codelist `CL-VINIK-NEHODY`.
Likely values (per inferred CS): účastník A | účastník N | žádný
z účastníků | neurčeno.

Each variant must:
1. Be selectable in the UI.
2. Persist the chosen value through state transition
   `IN_PROGRESS_CIRCUMSTANCES` → next step.
3. Appear verbatim in the final PDF under "Kdo zavinil nehodu?".

This TC parameterises across all 4 variants in a loop.

## Acceptance criteria (skeleton)

- [AC-1] For each variant V in {A, N, žádný, neurčeno}:
  - drive D14 → click radio for V → assert checked
  - click POKRAČOVAT → assert advance to next state
  - eventually verify F-112 in PDF/data-export contains V verbatim
- [AC-2] No variant causes the wizard to terminate or error.
- [AC-3] Re-selecting a different variant before continue clears the
  prior selection (radio mutual exclusion).

## CP-SUPIN-03 actions

- [ ] Live screenflow of D14 to confirm exact 4 radio labels.
- [ ] Pull the codelist values from `fixtures/codelists.yaml::CL-VINIK-NEHODY`
      once the Číselníky tab is photographed.
- [ ] Author parameterised step list (one `test.describe` per variant
      OR one `for` loop in the test body).

## Status footer

| Item | Value |
|------|-------|
| Spec | `specs/TC-CP-023-SPEC.md` |
| Spec version | 0.1.0 (skeleton) |
| Excel row | `02_TestCases::TC-CP-023` |
| Frameworks ready | not yet |
| OQs blocking | OQ-LIVE (D14 photos), OQ-CL-VINIK (codelist values) |
