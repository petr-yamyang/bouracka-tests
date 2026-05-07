# TC-CP-004 — Průvodce — výjimečné stavy a negativní konce / Wizard exceptions + negative-endings

> Pár k TC-CP-003: recoverable (OTP retry, OCR retry, server-timeout
> retry, location adjust) + irrecoverable (eligibilita, OTP exhaustion,
> mid-wizard interlock self-disclosure).

## Status

```yaml
spec_version: 0.1.0
spec_status: draft (skeleton — depth pending tst.* recon templates)
maps_to_test_target: TT-CP-R1-003, TT-CP-R1-004
release: R1
type: failure
priority: A
maps_to_flow: FLW-004
maps_to_integrations: INT-001, INT-002, INT-004, INT-005
framework_targets:
  - playwright
  - cypress
last_updated: 2026-05-05
last_updated_by: cowork-opus-cp-supin-02
```

## Reference index

- TestTarget(s):  TT-CP-R1-003 (recoverable), TT-CP-R1-004 (irrecoverable)
- Flow:           FLW-004 (recon/flows/FLW-004.md — 9 failure variants F1..F9)
- Integrations:   INT-001, INT-002, INT-004, INT-005
- Env config:     env/tst.json, env/tst-demo.json

## Skeleton notice

Each of the 9 variants (F1..F9 from FLW-004) needs its own full step
list once tst.* recon arrives. This skeleton specs the variant
catalogue + failure-class taxonomy + per-variant test-pattern sketch.

## Variant catalogue (each = sub-case)

```
Recoverable (TT-CP-R1-003):
  V1 — F2 OCR retry          (unreadable doc photo → user re-photographs
                               → second lookup succeeds)
  V2 — F3 OTP retry          (wrong OTP for driver B → re-enter correct
                               → wizard advances)
  V3 — F7 Server timeout     (transient 5xx during submit → retry → success)
  V4 — Location adjust       (wrong pin → re-pin → continue)
  V5 — SMS resend            (OTP not arriving → resend button → arrives)

Irrecoverable (TT-CP-R1-004):
  V6 — F1 invalid SPZ format (Czech pattern violation → terminate at SPZ step)
  V7 — F5 eligibility >200k  (damage > 200 000 Kč → interlock fires →
                               redirect to police-call)
  V8 — F4 location outside ČR (pin outside CZ borders → terminate)
  V9 — F6 reCAPTCHA fail     (test sets bypass token to invalid →
                               terminator + retry path)
  V10 — OTP exhaustion       (3 wrong OTPs for driver B → terminate)
  V11 — In-wizard police self-disclosure (user toggles "došlo ke zranění" →
                                          interlock fires)
  V8 — F8 mobile viewport meta missing (regression sentinel)
  V9 — F9 hamburger overlay covers submit (mobile regression)
```

## Test pattern per variant kind

### Recoverable variants (V1..V5)

```
Pre-conditions: same as TC-CP-003 PRE-1..PRE-8.
Step pattern:
  STEPs 1..K-1 — drive happy path up to the point of failure injection
  STEP K       — INJECT failure (mock-respond / fixture override)
  STEP K+1     — assert UI surfaces recoverable error in CS
  STEP K+2     — REMOVE injection (so retry succeeds)
  STEP K+3     — trigger retry (per UI affordance)
  STEP K+4     — assert wizard advanced past this step
  STEPs K+5..N — drive remainder of happy path to completion
Acceptance: state preserved across retry; final submit succeeds; e-mails
            dispatched (POST-conditions match TC-CP-003).
```

### Irrecoverable variants (V6..V11)

```
Pre-conditions: as TC-CP-003 PRE-1..PRE-7 (driver B fixtures NOT
                always required — depends on variant).
Step pattern:
  STEPs 1..K-1 — drive happy path up to the point of failure introduction
  STEP K       — INTRODUCE the irrecoverable condition (invalid SPZ
                 fixture, location-outside-CZ pin, etc.)
  STEP K+1     — assert UI surfaces terminator in CS with actionable
                 next-step
  STEP K+2     — assert wizard does NOT advance
  STEP K+3     — assert no record persisted
  STEP K+4     — assert no e-mail dispatched (poll SMTP hook for 0)
Acceptance: state recoverable for the user (can edit input and retry);
            no silent-accept; no record persistence.
```

## Test data

(skeleton — fixtures named per variant)

| Slot | Fixture ref | Used by |
|------|-------------|---------|
| invalid_spz_format | TD-CP-006 (`fixtures/shared/invalid-spz.json`) | V6 |
| over_200k_damage | TD-CP-007 (`fixtures/shared/over-200k-damage.json`) | V7 |
| outside_cz_location | TD-CP-008 (`fixtures/shared/outside-cz-location.json`) | V8 |
| wrong_otp | TD-CP-001 (existing — wrong_otp field) | V2, V10 |
| blurred_photo | `fixtures/shared/photos/op-blurred.jpg` | V1 |

## Acceptance criteria (skeleton)

For each variant:
- [AC-V<N>-1] expected error/terminator message renders in CS.
- [AC-V<N>-2] wizard behavior matches recoverable vs irrecoverable
  pattern (per §"Test pattern per variant kind").
- [AC-V<N>-3] no silent-accept; no corrupt server state; final state
  matches expected (record-persisted only on recoverable that retries
  successfully; never on irrecoverable).

## Env divergences (skeleton)

DEMO relaxes V6 (SPZ format) and V8 (location bound). The TC code
must mark these as `expectedOutcomePerEnv = {tst: "fail-shows-msg",
tst-demo: "pass-relaxed"}` and assert two distinct outcomes per env.

## Viewport applicability

All viewports run; V8/V9 specifically target mobile-only regressions.

## Failure-mode coupling (R-FAIL-1)

This IS the failure pair for TC-CP-003.

## Code-emission hints

- Group variants by failure kind: 5 recoverable in
  `core-flow-exceptions.spec.ts`, 6 irrecoverable in
  `core-flow-irrecoverable.spec.ts`. Or each variant in its own file —
  decide per dev-session preference (Cypress prefers many small files;
  Playwright handles either pattern).
- Re-use the test-pattern helpers in a `test-utils/wizard-helpers.ts`
  module — `driveHappyTo(stepK, fixtures)`, `injectFail(...)`,
  `removeInject(...)`, `expectRecoverableMsg(regex)`,
  `expectTerminator(regex)`, `pollSMTP(expected=0)`.
- Test names MUST start with `TC-CP-004 V<N> — `.

## Status

| Item | Value |
|------|-------|
| Spec | `specs/TC-CP-004-SPEC.md` |
| Spec version | 0.1.0 (skeleton) |
| Last updated | 2026-05-05 |
| Related Excel row | `02_TestCases::TC-CP-004` |
| Variants catalogued | 11 (V1..V11) |
| Frameworks ready | not yet — depth pending |
| OQs blocking | OQ-CP-14, OQ-CP-15 |
