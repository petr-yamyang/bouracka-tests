# TC-CP-005 — SMS-OTP odeslání + ověření / SMS-OTP send + verify

> NEW v0.2 per CP-SUPIN-03 STEP 4.3 step 5 + synchro §3.4 step 5.
> Mapped to TT-CP-R1-A1 (SMS Gateway PING gate) → TT-CP-R1-A2
> (Phone-OTP verification).

## Status

```yaml
spec_version: 0.2.0
spec_status: draft (full)
maps_to_test_target: TT-CP-R1-A2
release: R1
type: happy
priority: A
furps_dimensions: [F, R]
requirement_ref: REQ-CP-002
impulse_ref: D02_step_OTP_send
diligence: happy
maps_to_flow: D02 swimlane (recon/diagrams/extracted/ACTIVITY-DIAGRAMS-v0.1.md §3)
maps_to_integrations: INT-002 N8 SMS Gateway
framework_targets: [playwright, cypress]
parameter_refs: [TC-CP-005-P-01, TC-CP-005-P-02, TC-CP-005-P-03]
assertion_refs: [TC-CP-005-S-03, TC-CP-005-S-06]
last_updated: 2026-05-06
last_updated_by: cowork-opus-cp-supin-03
```

## Reference index

- TestTarget: TT-CP-R1-A2 (Phone-OTP participant verification)
- Flow: D02 swimlane
- Integration: INT-002 N8 SMS Gateway (Mockoon profile by default)
- Mockoon: `mockoon/n8-sms-gateway.json` scenarios `SEND_OTP_OK` + `VALIDATE_OTP_VALID`
- Vendor request: `_install/contracts/n8-sms-gateway-test-data-request.md`

## What this TC asserts

The SMS Gateway integration's two test-relevant call patterns work
end-to-end:
1. SUT issues SEND OTP request to N8 → receives a queued response
2. Test framework reads the OTP value from the mock's
   `otp_for_test` field
3. Test enters the OTP into the SUT
4. SUT issues VALIDATE OTP request → N8 returns valid:true
5. SUT advances state machine

## Pre-conditions

- [PRE-1] env reachable; `env.sms_gateway_mode = 'mock'`
- [PRE-2] Mockoon CLI running on `localhost:8025` with
  `mockoon/n8-sms-gateway.json` profile loaded
- [PRE-3] `fixtures/shared/test-drivers.json` has `tester_jeden.phone`
  and `tester_dva.phone`
- [PRE-4] `01_Potvrzení účastníků nehody` already passed (TC-CP-001)
  → app is at screen 02 with `accidentReportStatus = NEW`

## Test data (Tier A — per `02b_TC_Parameters`)

| Slot | Param ID | Source | Default |
|------|----------|--------|---------|
| otp_value | TC-CP-005-P-01 | from-mock-response (Mockoon SEND_OTP_OK::otp_for_test) | 1234 |
| phone_a | TC-CP-005-P-02 | fixture-ref (test-drivers.json::tester_jeden.phone) | +420 608 323 999 |
| phone_n | TC-CP-005-P-03 | fixture-ref (test-drivers.json::tester_dva.phone) | +420 608 323 888 |

## Steps

```yaml
- id: TC-CP-005-S-01
  kind: trigger_point
  title_cs: Vyplnit telefonní číslo účastníka A
  selector: env.selectors.phone_a_input
  input: param[TC-CP-005-P-02]   # phone_a
  expected: input value persists
  furps: F

- id: TC-CP-005-S-02
  kind: trigger_point
  title_cs: Klik na ODESLAT KÓD
  selector: env.selectors.send_otp_button
  expected: SUT issues POST to N8 send endpoint
  furps: F

- id: TC-CP-005-S-03
  kind: assertion
  title_cs: Přesně 1 SEND_OTP volání zachyceno
  assertion_lib: LIB-AS-RELI-001  # network-call-count-exact
  expected: page.routes captured exactly 1 POST to /api/v1/sms/send
  furps: R

- id: TC-CP-005-S-04
  kind: data_collection_point
  title_cs: Načíst otp_for_test z mock response
  selector: response body
  expected: otp_for_test field present in JSON; equals "1234"
  furps: F

- id: TC-CP-005-S-05
  kind: trigger_point
  title_cs: Zadat OTP do pole + klik OVĚŘIT
  selector: env.selectors.otp_input + env.selectors.verify_button
  input: param[TC-CP-005-P-01]   # otp_value (resolved at runtime)
  furps: F

- id: TC-CP-005-S-06
  kind: assertion
  title_cs: VALIDATE_OTP vrátí valid:true
  assertion_lib: LIB-AS-FUNC-004  # value-equals-fixture
  expected: response.body.valid === true
  furps: F

- id: TC-CP-005-S-07
  kind: assertion
  title_cs: Stav postoupil na IN_PROGRESS_DRIVERS (po obou účastnících)
  expected: accidentReportStatus = 'IN_PROGRESS_DRIVERS'
  furps: F
  notes: "tento step se opakuje smyčkově pro účastníka N (S-01..S-06 znovu)"
```

## Post-conditions

- [POST-1] DB record created with both phones verified
- [POST-2] `accidentReportStatus = 'IN_PROGRESS_DRIVERS'`
- [POST-3] No real SMS sent (Mockoon mode)

## Acceptance criteria

- [AC-1] Mockoon serves the SEND_OTP scenario (status 200 + otp_for_test)
- [AC-2] SUT reads + accepts otp_for_test as the user-input OTP
- [AC-3] VALIDATE_OTP returns valid:true for `1234`
- [AC-4] State machine advances to IN_PROGRESS_DRIVERS
- [AC-5] Exactly 2 SEND_OTP + 2 VALIDATE_OTP calls (one per
  participant) — exercises LIB-AS-RELI-001

## Env divergences

| ENV | sms_gateway_mode | OTP source |
|-----|------------------|------------|
| ENV-TST | mock (default) | Mockoon `1234` |
| ENV-TST | sandbox (when ASK-002 lands) | N8 sandbox mode value |
| ENV-DMO | mock or sut-bypass | Mockoon `1234` or SUT default |

## Failure-mode coupling (R-FAIL-1)

This is a happy TC. Pairs with TC-CP-005-NOK (LATER — failure variant
when ASK-002 surfaces the EX_CHYBA error envelope from real N8).

## Code-emission hints

- Mockoon must be running BEFORE test invocation (in
  `playwright.config.ts::globalSetup` or via Playwright `webServer`
  config option pointing at `mockoon-cli start --data ./mockoon/n8-sms-gateway.json --port 8025`).
- Use Playwright's `page.route('**/api/v1/sms/**', …)` for capturing
  SUT calls + asserting count (LIB-AS-RELI-001 pattern).
- Read mock response via `page.waitForResponse` to grab `otp_for_test`
  before entering it into the next step.
- TC name must start with `TC-CP-005 — ` (Excel reporter convention).

## Status

| Item | Value |
|------|-------|
| Spec | `specs/TC-CP-005-SPEC.md` |
| Spec version | 0.2.0 (full per v0.2 format) |
| Excel rows | `02_TestCases::TC-CP-005` + 3 in `02b_TC_Parameters` + 2 in `02c_TC_Assertions` |
| Frameworks ready | playwright (Mockoon mode) + cypress (Mockoon mode) |
| OQs blocking | OQ-CP-27 (N8 sandbox/skip — for Layer 4 strategy B/D in addition to Mockoon) |
