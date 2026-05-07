# TC-CP-003 — Průvodce — happy end-to-end / Wizard happy E2E

> Po ID-autentizaci happy: telefony → poškození foto → místo → SMS-OTP
> oba řidiči → submit → 2× e-mail s podepsaným PDF.

## Status

```yaml
spec_version: 0.1.0
spec_status: draft (skeleton — depth pending tst.* recon templates)
maps_to_test_target: TT-CP-R1-002
release: R1
type: happy
priority: A
maps_to_flow: FLW-003
maps_to_integrations: INT-001, INT-002, INT-003, INT-004, INT-005
framework_targets:
  - playwright
  - cypress
last_updated: 2026-05-05
last_updated_by: cowork-opus-cp-supin-02
```

## Reference index

- TestTarget(s):  TT-CP-R1-002
- Flow:           FLW-003 (recon/flows/FLW-003.md — 24 typed steps)
- Integrations:   INT-001 (reCAPTCHA), INT-002 (SMS), INT-003 (SMTP),
                  INT-004 (registry), INT-005 (maps)
- Screens:        SCR-002 + SCR-007..SCR-012 (recon pending tst.*)
- Known issues:   none
- Divergences:    DIV-CP-003..DIV-CP-006 (multiple — see env divergences)
- Env config:     env/tst.json, env/tst-demo.json

## Skeleton notice

This spec is **skeleton-grade** in v0.1. The wizard interior depth
(STEPs 11..24 per FLW-003) is not yet recon'd because:

1. Per user direction 2026-05-05: public driving against
   `tst.bouracka.cz` is not allowed; recon happens via
   user-supplied recon-template emails (Phase A).
2. Per OQ-CP-14: reCAPTCHA posture in tst.* must be confirmed first.
3. Per OQ-CP-15: tst.* recon templates for SMS-OTP hook URL,
   SMTP hook URL, and the per-step UI element shapes are pending.

## Pre-conditions

### Boolean conditions

- [PRE-1] env reachable.
- [PRE-2] reCAPTCHA bypass token configured.
- [PRE-3] Registry stub healthy.
- [PRE-4] SMS hook URL configured: `env.sms_hook_url` resolves AND
        `GET <hook>/healthz` returns 200.
- [PRE-5] SMTP hook URL configured similarly.
- [PRE-6] Maps geocoder stub healthy (or manual-address fallback ready).
- [PRE-7] All TC-CP-001 fixtures present (TD-CP-002 + TD-CP-003 +
         photo placeholders).
- [PRE-8] Driver-B fixture present: TD-CP-004 (`tester_dva`) with valid
         OP/ŘP/SPZ entries in the registry stub.

### Setup steps

1. As TC-CP-001 setup steps 1..4.
2. Pre-warm SMS hook: `GET <env.sms_hook_url>/healthz` → assert 200.
3. Pre-warm SMTP hook: `GET <env.smtp_hook_url>/healthz` → assert 200.
4. Optionally pre-warm maps stub.

## Test data

| Slot | Fixture ref | Notes |
|------|-------------|-------|
| primary_driver | TD-CP-002 | as TC-CP-001 |
| primary_vehicle | TD-CP-003 | as TC-CP-001 |
| secondary_driver | TD-CP-004 (`fixtures/shared/test-drivers.json::tester_dva`) | second driver — required for both-drivers SMS-OTP |
| secondary_vehicle | TD-CP-005 (`fixtures/shared/test-vehicles.json::2YY_0002`) | second vehicle |
| accident_location | `fixtures/shared/locations/prague-vaclavske.json` | within ČR; geocodable |

## Integration touchpoints

| Integration | Env: tst | Env: tst-demo | Test posture |
|-------------|----------|---------------|--------------|
| INT-001 reCAPTCHA | bypass_token | bypass_or_disabled | as TC-CP-001 |
| INT-002 SMS — request OTP | real-stub | fixed-OTP "0000" | poll hook for latest OTP after each request |
| INT-002 SMS — validate OTP | real-stub | fixed-OTP "0000" | submit OTP; assert response valid:true |
| INT-003 SMTP | hook | hook | poll for 2 messages after submit |
| INT-004 registry (driver+vehicle ×2) | real-stub | real-stub-or-skipped | as TC-CP-001 ×2 (both drivers) |
| INT-005 maps geocoder | real-stub | skipped or stubbed | use manual-address fallback |

## Steps

### STEPs 1..20 — re-use TC-CP-001 STEPs 1..20 (ID-auth happy)

This TC is a **continuation** of TC-CP-001. Either:
- (A) Implementation re-uses the page-object methods authored for
  TC-CP-001 to drive STEPs 1..20.
- (B) The framework code declares TC-CP-001 a precondition fixture
  (Playwright `test.use` / Cypress `before`) and starts at STEP 21
  in fresh authenticated state.

Decision: (B) when fixtures persist cleanly across tests; (A) until
then. Default to (A) in CP-SUPIN-03 first impl.

### STEPs 21..N — wizard interior

```
STEP 21 — telefonní čísla obou účastníků
STEP 22 — driver B's ID-auth happy (re-runs the same auto-fill pattern
          for the second driver)
STEP 23 — poškození foto (vehicle A)
STEP 24 — poškození foto (vehicle B)
STEP 25 — místo nehody (manual-address path; geocoder via stub)
STEP 26 — review summary (data_collection + assertion that all auto-fills
          render)
STEP 27 — request SMS-OTP for driver A
STEP 28 — read OTP from SMS hook
STEP 29 — enter OTP for driver A
STEP 30 — assert driver A signed
STEP 31..34 — repeat 27..30 for driver B
STEP 35 — submit
STEP 36 — control_point: server response (success → completion screen)
STEP 37 — assertion: completion screen + record-id rendered
STEP 38 — data_collection: poll SMTP hook (2 messages within N seconds)
STEP 39 — assertion: both messages received with PDF attached;
          subject contains record-id; recipients match driver fixtures
```

Each STEP above will be expanded to the full v0.1.0 step-record
format once user-supplied recon templates land. Until then, this
skeleton notes the intent.

## Post-conditions

- [POST-1] One record persisted server-side; record-id captured.
- [POST-2] Two e-mails dispatched.
- [POST-3] Browser context closed.

## Acceptance criteria

(skeleton — to expand)

- [AC-1] All ID-auth ACs from TC-CP-001 pass for BOTH drivers.
- [AC-2] At STEP 30 + 34, both drivers signed indication renders.
- [AC-3] At STEP 36, server returned success.
- [AC-4] At STEP 37, completion screen + record-id visible.
- [AC-5] At STEP 39, two e-mails received with PDF + correct
  recipients.

## Env divergences

(skeleton — full table after recon)

| Step | TST behaviour | DEMO behaviour |
|------|---------------|----------------|
| STEPs 27..34 (SMS-OTP) | live OTP via hook | fixed OTP `0000` |
| STEPs 7..18 (registry, both drivers) | full lookup | manual entry possible |
| STEP 38 (PDF) | clean PDF | watermarked "DEMO ONLY" |

## Viewport applicability

All four viewports run; on mobile, file-upload steps may diverge if the
SUT exposes camera-capture vs disk-upload differently — pending recon.

## Failure-mode coupling (R-FAIL-1)

Pairs with TC-CP-004 (failure envelope) per
`specs/TC-CP-004-SPEC.md`.

## Code-emission hints

- Re-use page objects from TC-CP-001 for STEPs 1..20.
- Author NEW page objects for the wizard interior:
  - `WizardDriverInfoPage.ts` (STEPs 21–22)
  - `WizardDamagePhotosPage.ts` (STEPs 23–24)
  - `WizardLocationPage.ts` (STEP 25)
  - `WizardReviewPage.ts` (STEP 26)
  - `WizardSignPage.ts` (STEPs 27–34)
  - `WizardCompletionPage.ts` (STEPs 35–37)
- SMS hook polling: prefer a `pollUntil()` helper with exponential
  backoff (start 500 ms, max 5 s, total timeout 30 s).
- SMTP hook polling: same pattern.
- Test name MUST start with `TC-CP-003 — `.

## Status

| Item | Value |
|------|-------|
| Spec | `specs/TC-CP-003-SPEC.md` |
| Spec version | 0.1.0 (skeleton) |
| Last updated | 2026-05-05 |
| Related Excel row | `02_TestCases::TC-CP-003` |
| Frameworks ready | not yet — depth pending |
| OQs blocking | OQ-CP-14, OQ-CP-15 (high-priority blockers); CP-SUPIN-06 cannot start until these close |
