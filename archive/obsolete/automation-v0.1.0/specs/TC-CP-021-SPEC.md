# TC-CP-021 — Okolnosti nehody — změna pořadí vozidel / Circumstances — vehicle order swap

> Skeleton spec — surfaced as gap in `recon/COVERAGE-GAP-ANALYSIS.md`
> §2.1. Mapped to TT-CP-R1-D (Circumstances + sign + complete).
> Full step-list authored in CP-SUPIN-03 once live screenflow photos
> of D12 land.

## Status

```yaml
spec_version: 0.1.0
spec_status: draft (skeleton)
maps_to_test_target: TT-CP-R1-D
release: R1
type: regression
priority: B
maps_to_flow: D12 swimlane (recon/diagrams/extracted/ACTIVITY-DIAGRAMS-v0.1.md §12)
maps_to_integrations: none (UI-only behaviour)
framework_targets: [playwright, cypress]
last_updated: 2026-05-05
last_updated_by: cowork-opus-cp-supin-02-rev6
```

## What this TC asserts

When at D12 (Okolnosti nehody) the user clicks **ZMĚNIT POŘADÍ
VOZIDEL NA OBRÁZKU**, the system must:
1. Re-render the situational sketch with vehicles A and N visually
   swapped.
2. Persist the swapped order so it propagates to the final PDF
   (situační nákres section, F-083).
3. Allow the user to swap again if they wish (idempotent toggle).

## Acceptance criteria (skeleton)

- [AC-1] At D12, both swap-button and "Vyhovuje?" decision render correctly.
- [AC-2] Click swap → assert re-render observable in DOM (e.g.
  vehicle order reversed in the sketch SVG / image attributes).
- [AC-3] After confirm + continue → final PDF F-083 reflects the
  swapped order (assert via PDF content scan or via the persisted
  Excel field).
- [AC-4] User can swap multiple times with no state corruption.

## Coverage rationale

D12's swap branch is unlikely to be exercised by the default
TC-CP-018 E2E orchestration (which uses fixture default order). This
TC ensures the swap is genuinely tested, not assumed-OK.

## CP-SUPIN-03 actions

- [ ] Wait for live screenflow photos of D12.
- [ ] Translate the swap-button selector + the situational-sketch
      element from the photos.
- [ ] Author full step list per `_specs/TESTCASE-SPEC-FORMAT-v0.1.md`.

## Status footer

| Item | Value |
|------|-------|
| Spec | `specs/TC-CP-021-SPEC.md` |
| Spec version | 0.1.0 (skeleton) |
| Excel row | `02_TestCases::TC-CP-021` |
| Frameworks ready | not yet — depth pending live screenflow |
| OQs blocking | OQ-LIVE (waiting for live screenflow photos of D12) |
