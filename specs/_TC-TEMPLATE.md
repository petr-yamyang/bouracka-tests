# TC-CP-NNN — Title (CS) / Title (EN)

> One-line abstract (≤ 25 words).

## Status

```yaml
spec_version: 0.1.0
spec_status: draft
maps_to_test_target: TT-CP-RN-MMM
release: R1
type: happy
priority: A
maps_to_flow: FLW-NNN
maps_to_integrations: INT-NNN
framework_targets:
  - playwright
  - cypress
last_updated: 2026-05-05
last_updated_by: <session-id>
```

## Reference index

- TestTarget(s):  TT-CP-RN-MMM
- Flow:           FLW-NNN
- Integrations:   INT-NNN
- Screens:        SCR-NNN
- Known issues:   none
- Divergences:    none
- Env config:     env/tst.json, env/tst-demo.json

## Pre-conditions

### Boolean conditions
- [PRE-1] …

### Setup steps
1. …

## Test data

| Slot | Fixture ref | Notes |
|------|-------------|-------|

## Integration touchpoints

| Integration | Env: tst | Env: tst-demo | Test posture |
|-------------|----------|---------------|--------------|

## Steps

### STEP 1
```yaml
id: TC-CP-NNN-S-01
kind: trigger_point
title_cs: …
title_en: …
selector: |
  …
input: |
  …
expected: |
  …
viewport_applicability: all
env_divergence:
  tst: same as default
  tst-demo: same as default
integration_touchpoint: none
recovery: none
notes: |
  …
```

## Post-conditions

- [POST-1] …

## Acceptance criteria

- [AC-1] …

## Env divergences

| Step | TST behaviour | DEMO behaviour |
|------|---------------|----------------|

## Viewport applicability

| Viewport | Run? | Skipped steps |
|----------|------|---------------|
| desktop (1280×720) | YES | none |
| mobile-320 (320×568) | YES | none |
| mobile-375 (375×667) | YES | none |
| mobile-414 (414×896) | YES | none |

## Failure-mode coupling (R-FAIL-1)

Pairs with: TC-CP-NNN.

## Code-emission hints

- …

## Status

| Item | Value |
|------|-------|
| Spec | `specs/TC-CP-NNN-SPEC.md` |
| Spec version | 0.1.0 |
| Last updated | 2026-05-05 |
| Related Excel row | `02_TestCases::TC-CP-NNN` |
| Frameworks ready | playwright, cypress |
| OQs blocking | … |
