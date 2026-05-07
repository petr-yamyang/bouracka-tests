# Integration Contracts Strategy — v0.2

> Bumps v0.1 with explicit N8 SMS Gateway entry per CP-SUPIN-03
> (synchro §3) + new Mockoon-first posture for daily test runs.

## §1. What changed since v0.1

- §6 of v0.1 carried 8 integrations; v0.2 adds **N8 SMS Gateway**
  as a first-class entry with full strategy + Mockoon profile +
  vendor request template.
- The hybrid recommendation (§3) now refers to the **02d_AssertionLibrary**
  patterns by code (LIB-AS-RELI-001 for "exactly N calls" pattern).
- New cross-reference: every integration row links to the
  `02_TestCases.notes` rows that exercise it.

## §2. v0.2 integration matrix

| INT-NNN | Name | Strategy A (mock) | Strategy B (sandbox) | Strategy C (golden-master) | Strategy D (SUT-bypass) |
|---------|------|:-----------------:|:--------------------:|:--------------------------:|:-----------------------:|
| INT-001 | reCaptcha | YES (env-config token) | Google test keys | n/a | YES (analytical p25/133) |
| INT-002 | **N8 SMS Gateway** (NEW v0.2) | YES (Mockoon — see §3) | yes — request sent | n/a | yes — needs SUPIN confirmation |
| INT-003 | SMTP | YES (Mailpit) | n/a | n/a | YES (test SMTP relay) |
| INT-004 | AISPOV (ROB+CRR+CRV) | YES (Mockoon) | likely — SUPIN owns | n/a | YES (per analytical p25/133) |
| INT-005 | Maps (Google) | YES (REST mock) | Google billing-protected | n/a | YES (manual-address fallback) |
| INT-006 | zenID WebSDK | YES (Mockoon) | yes — request sent | YES (5 photos) | YES per analytical p25/133 |
| INT-007 | zenID API | YES (Mockoon) | (same as 006) | (same) | (same) |
| INT-008 | RUIAN | YES (REST mock) | RUIAN public API | n/a | not needed (data is public) |
| INT-009 | Azure Blob outage config | YES (static JSON) | n/a (we own the config) | n/a | YES (config-driven) |
| INT-010 | Google Analytics | YES (script intercept) | Google test keys | n/a | YES (cookie-rejected) |

## §3. N8 SMS Gateway — full strategy (per synchro §3)

### §3.1 Two call patterns

| Pattern | When | Direction | Test concern |
|---------|------|-----------|--------------|
| **PING / heartbeat** | gateway-on-screen-01 entry | SUT → N8 (HTTP) | availability gate |
| **SEND OTP** | wizard step requiring phone-OTP confirmation | SUT → N8 (HTTP) → user phone (SMS) | OTP value must round-trip back to test |

### §3.2 Recommended hybrid

```
Layer 1 — service contract test     Strategy A (Mockoon — schema check)
Layer 2 — data-validation gate      Strategy A
Layer 3 — mocked-integration E2E    Strategy A  (TC-CP-001..005 in TST + DEMO)
Layer 4 — real-integration E2E      Strategy D for daily fast E2E (skip_integrations=true)
                                    Strategy B nightly (when N8 sandbox lands) for 2-3 happy/failure TCs
Layer 5 — performance/load          Strategy A only — never hammer real N8 (cost; vendor ToS)
```

### §3.3 Mockoon profile

`mockoon/n8-sms-gateway.json` — three scenarios:

```jsonc
{
  "PING_OK":    { "status": "ok", "gateway_id": "N8-MOCK-001" },
  "PING_NOK":   { "status": 503, "error": "gateway_unavailable" },
  "SEND_OTP":   { "status": "queued", "message_id": "MID-...",
                  "otp_for_test": "1234"  /* test reads this and feeds into next step */ }
}
```

The `otp_for_test` field is a Mockoon-only convention — real N8
returns no such field; the test framework reads this from the mock
response (parameter `TC-CP-005-P-01` in `02b_TC_Parameters`,
source_kind=`from-mock-response`).

### §3.4 Test-mode posture per env

| ENV | sms_gateway_mode | Notes |
|-----|------------------|-------|
| ENV-PUB (public) | n/a | dev-time only; no PING run |
| ENV-TST | mock (default) | flips to `sandbox` when N8 credentials land |
| ENV-DMO | mock (default) | flips to `sut-bypass` if SUPIN confirms `skip_integrations.sms` exists |

### §3.5 Vendor request

Sent via `_install/contracts/n8-sms-gateway-test-data-request.md`
(NEW — copy of zenID template; adapted). Tracked in
`_install/contracts/responses-log.md` as `ASK-002`.

---

## §4. Status

| Item | Value |
|------|-------|
| Document | `_specs/INTEGRATION-CONTRACTS-STRATEGY-v0.2.md` |
| Supersedes | `_specs/INTEGRATION-CONTRACTS-STRATEGY-v0.1.md` |
| Trigger | CP-SUPIN-03 (synchro §3) |
| New first-class integration | N8 SMS Gateway |
| Mockoon profile | `mockoon/n8-sms-gateway.json` (CP-SUPIN-03 STEP 4.3) |
| Status | v0.2 — binding |
