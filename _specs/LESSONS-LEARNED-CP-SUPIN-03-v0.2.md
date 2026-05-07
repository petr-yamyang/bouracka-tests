# Lessons Learned — CP-SUPIN-03 — v0.2 (additive over v0.1)

> Adds CP-SUPIN-03 lessons over the CP-SUPIN-02 v0.1 baseline.
> v0.1 lessons remain valid; this file captures what the schema-upgrade
> + runtime-contract iteration surfaced.

## §1. New process lessons

### L-PROC-7 — Synchro file = the right channel for cross-session handoff

The MacBook Opus session 2026-05-05 evening produced a comprehensive
synchro file (`SYNCHRO-THINKPAD-CP-SUPIN-03-2026-05-06.md`) with:
- 7 operator decisions locked (OQ-OREV-01..07)
- 5 new OQs raised with sev/urg/pri
- Full N8 SMS Gateway strategy
- 10-item input gap inventory
- 7 creative CS-narrative seeders
- Paste-ready prompt for the consuming session

**Action for next campaign:** every cross-session handoff that crosses
a sleep boundary should produce a synchro file of this shape. The
consuming session's first 30 min reads it; that's grounding.

### L-PROC-8 — Operator decisions resolve OQs in batches

The 7 OQ-OREV-* decisions in synchro §1 were all resolved in one
operator-evening pass. Batching review-OQs reduces context-switch
cost vs single-OQ ping-pong.

**Action:** structure review-OQ raises so they can be batch-resolved
(one decision per OQ; binary or short-list of options; no open-ended
"please ponder"-class questions).

### L-PROC-9 — Best-newest-shape ships immediately; no review window freeze

Per OQ-OREV-05 decision: ship v0.2 with the 05a/b/c split immediately
to SUPIN, no v0.1 freeze + review window. Iterating is faster than
two-stage review-then-improve cycles. SUPIN reviews the *current*
shape; we never apologise for improving the artefact between iterations.

## §2. New architectural lessons

### L-ARCH-6 — The workbook IS the live execution contract (R-CONTRACT-1)

The most consequential v0.2 architectural shift: parameters and
assertions live in Excel sheets (`02b_TC_Parameters`,
`02c_TC_Assertions × 02d_AssertionLibrary`), not in source code.
Tests read them at runtime via `playwright/runtime/spec-loader.ts`.

**Why this matters:**
- Editing a test parameter doesn't require code review; it's a
  one-cell Excel edit.
- The assertion library is reusable across TCs — write a pattern
  once, reference it from many TCs.
- The catalogue is the diff target — when SUPIN reviews a delta,
  they review Excel, not git diffs.
- Code-generation builds against this contract; if the contract
  doesn't change, regenerated code is identical.

### L-ARCH-7 — FURPS+ Cartesian surfaces dimensional gaps before TC authoring

The 200-cell Cartesian (`01b_Req_FURPS_Cartesian`) makes it
visually obvious where coverage is thin. The P (Performance) row
is 15 % active and the U (Usability) row 20 % — these become the
prioritised gaps to close in CP-SUPIN-04+.

Pre-Cartesian, these gaps were invisible. The matrix forces the
question "for THIS requirement, in THIS dimension, what's our
position?".

### L-ARCH-8 — State machine is the canonical TT decomposition axis (re-confirmed)

L-ARCH-1 from CP-SUPIN-02 said this; CP-SUPIN-03 made it formal by
adding `01c_StateMachine` as a workbook sheet. The state machine
is now query-able + cross-referenceable from TT rows.

## §3. New tooling lessons

### L-TOOL-10 — Validator script catches schema regressions immediately

`tools/validate_workbook.py` (10 checks) flagged the 3 backfill gaps
within seconds of running against the migrated workbook. Without it
the gaps would have shipped silent.

**Action:** every workbook commit goes through validator-gate. CI
target: validator green before any package script runs.

### L-TOOL-11 — `unhashable type: 'StyleProxy'` from openpyxl when copying font references

When renaming Excel header cells in openpyxl, **don't** assign
`new_cell.font = old_cell.font` — that triggers a deep-copy bug for
StyleProxy objects across rows. Just update the value; the existing
styling is preserved automatically.

```python
# WRONG:
ws.cell(row=1, column=col, value="new").font = ws.cell(row=1, column=col).font
# RIGHT:
ws.cell(row=1, column=col).value = "new"   # styling stays
```

### L-TOOL-12 — Mockoon profile JSON is an under-documented but capable format

The `n8-sms-gateway.json` profile uses Mockoon's rules engine to
return different responses based on query params (`PING_NOK` when
`?force=nok`) or body content (`SEND_OTP_422_EX_CHYBA` when
phone=INVALID). This lets one profile cover happy + multiple failure
modes without separate stub instances.

## §4. New domain-specific lessons

### L-DOM-6 — N8 is the SMS Gateway vendor (per operator note 2026-05-05)

Surfaced during synchro §3. N8 likely supports a `TEST` mode but
no public docs; vendor request `_install/contracts/n8-sms-gateway-test-data-request.md`
sent to surface either sandbox credentials OR confirmation of the
SUT-side `skip_integrations.sms` flag.

### L-DOM-7 — `otp_for_test` is a Mockoon-only convention

Real N8 returns no such field. The Mockoon mock invents it for the
test framework to read + feed back into the next step. When Strategy
B (real N8 sandbox) lands, the test code branches on
`env.sms_gateway_mode`:
- mock → read `otp_for_test` from response
- sandbox → poll N8's test-mode webhook OR use deterministic OTP
- sut-bypass → use SUT's local-deterministic OTP

## §5. What's still open (for CP-SUPIN-04)

1. **GAP-1** — Pages 43–133 of analytical doc (Petr photo batch).
2. **GAP-2** — tst.bouracka.cz screen-recon Template 1 fills.
3. **GAP-4** — N8 SMS Gateway sandbox / `skip_integrations.sms`
   confirmation (OQ-CP-27 — vendor request sent).
4. **GAP-5** — reCAPTCHA bypass token for tst.* (OQ-CP-14).
5. **GAP-6** — Synthetic OP/ŘP/SPZ photos (OQ-CP-23).
6. **GAP-7** — AISPOV WSDL/OpenAPI (OQ-CP-22).
7. **CS-only activity diagrams pass** — defer until live screenflow lands.
8. **Per-TC SPEC.md authoring v0.2 format upgrade** — TC-CP-001..004
   currently full; TC-CP-005 full (NEW); TC-CP-006..023 still skeletons.
9. **Code-gen step-list emission** — current `tools/generate_tests.py` is
   a proof-of-life that resolves params + assertions; CP-SUPIN-04 emits
   the per-step Playwright/Cypress code inline using snippets from
   `02d_AssertionLibrary`.
10. **Performance dimension TCs** — P row of FURPS+ Cartesian is at
    15 %; first 3 perf TCs for AISPOV registry recommended.

## §6. Status

| Item | Value |
|------|-------|
| Document | `_specs/LESSONS-LEARNED-CP-SUPIN-03-v0.2.md` |
| Iteration | CP-SUPIN-03 |
| New lessons | 9 (3 process + 3 architectural + 3 tooling + 2 domain) |
| Open items | 10 (input-blocked or deferred) |
| Status | v0.2 — read at start of CP-SUPIN-04 |
