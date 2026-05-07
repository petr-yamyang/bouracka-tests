# TC-CP-022 — Místo nehody — větvení GPS vs manuální adresa / Accident location — GPS vs manual-address branch

> Skeleton spec — surfaced as gap in `recon/COVERAGE-GAP-ANALYSIS.md`
> §2.2. Mapped to TT-CP-R1-D.

## Status

```yaml
spec_version: 0.1.0
spec_status: draft (skeleton)
maps_to_test_target: TT-CP-R1-D
release: R1
type: regression
priority: B
maps_to_flow: D13 swimlane (ACTIVITY-DIAGRAMS-v0.1.md §13)
maps_to_integrations: INT-005 (Maps), INT-008 (RUIAN)
framework_targets: [playwright, cypress]
last_updated: 2026-05-05
last_updated_by: cowork-opus-cp-supin-02-rev6
```

## What this TC asserts

D13 has two parallel branches for accident-location capture:
1. **GPS branch** — invokes INT-005 Google Maps; persists F-061 +
   F-062 (lat/lon).
2. **Manual-address branch** — invokes INT-008 RUIAN autocomplete;
   persists F-063..F-069 (street, č.p., č.o., obec, PSČ, RUIAN id,
   text).

Each branch has different network calls, different field
persistence, different validation. Both must be exercised
independently to catch single-branch regressions.

## Acceptance criteria (skeleton)

- [AC-1] **GPS branch:** drive D13 → grant geolocation permission →
  assert exactly 1 outbound call to Maps geocoder; assert response
  lat/lon in expected ČR bounding box; F-061 + F-062 populated;
  F-063..F-069 NOT populated.
- [AC-2] **Manual-address branch:** drive D13 → type address → assert
  RUIAN autocomplete fires per-keystroke; select suggestion; assert
  F-063..F-069 populated; F-061 + F-062 NOT populated; INT-005 NOT
  invoked.
- [AC-3] Both branches end at D14 with state `IN_PROGRESS_CIRCUMSTANCES`.

## CP-SUPIN-03 actions

- [ ] Live screenflow photos of D13 needed for selector exactness.
- [ ] Decide whether to use Playwright's geolocation override or
      Mockoon-stub the Maps endpoint for deterministic GPS branch.
- [ ] Author full step list × 2 sub-cases.

## Status footer

| Item | Value |
|------|-------|
| Spec | `specs/TC-CP-022-SPEC.md` |
| Spec version | 0.1.0 (skeleton) |
| Excel row | `02_TestCases::TC-CP-022` |
| Frameworks ready | not yet |
| OQs blocking | OQ-LIVE (D13 photos), OQ-MAP (geocoder mock decision) |
