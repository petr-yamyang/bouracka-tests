# Bouračka P0 Smoke — TC Ranking v0.1

**Workbook.** `BOURACKA-TESTPLAN-v0.4.3.xlsx`, sheet `02_TestCases`.
**Date.** 2026-05-13.
**Author.** Pete Y. with greedy coverage-spread selector.
**Status.** Recommendation — awaits KP confirmation.

---

## §1. Scope and intent

This document selects **12 TCs from the 19 Priority-A candidates** in v0.4.3 to constitute Kate's "P0 smoke pass" — the minimum set that, when green, gives high confidence that:

- the wizard's state machine has been exercised across all terminal states,
- every external integration (N8, zenID, AISPOV) is round-tripped at least once,
- every FURPS+ dimension declared in the workbook is touched,
- all three test types (happy, failure, regression) are represented.

If any of these 12 fail, Bouračka cannot ship to UAT. If all 12 green, run the remaining 12 (7 Priority-A not in P0, plus the 5 Priority-B) as Round 2.

**Smoke runtime estimate.** ~25 min (cypress + playwright cross-run, ~2 min average per TC, parallel across the two frameworks).

---

## §2. Method — greedy coverage-spread

For each candidate TC we compute the **marginal coverage value** it adds across five axes, weighted:

| Axis | Weight | Source column |
|------|:------:|----------------|
| State-machine terminal (`<state>::<error>`) | 3 | `state_machine_terminal_state` + `state_error_subreason` |
| External integration | 2 | `ext_ws` (split on `,` / `;`) |
| FURPS+ dimension | 2 | `furps_dimensions` |
| Impulse (dialog step) | 1 | `impulse_ref` |
| Test type | 1 | `type` |

Greedy pick: at each step, take the TC adding the most uncovered weighted dimensions. Ties broken by lower `tc_code` (alphanumeric). Algorithm terminates at target=12.

Why greedy, not exhaustive: 19 choose 12 = 50,388 combinations — feasible but unnecessary; the greedy result already achieves 100% structural coverage and produces a stable, explainable ordering.

Why weighted SM-terminal highest: Bouračka is a state-machine-driven wizard; uncovered terminal = unrun branch. Skipping one = blind spot in Kate's smoke.

---

## §3. The ranked P0 list

| Rank | TC code | Name | Type | SM terminal :: error | Integrations | FURPS+ | Impulse | Score |
|:----:|---------|------|:----:|----------------------|--------------|--------|---------|:-----:|
| 1 | **TC-CP-008** | zenID + AISPOV ROB — happy auto-fill | happy | `IN_PROGRESS_DRIVERS` | zenID, AISPOV-AB | F,P,S | `D04_step_AISPOV_ROB` | +15 |
| 2 | **TC-CP-015** | Summary → SMS-OTP both drivers — happy | happy | `FINISHED` | N8 | F,R,S,+L | `D17_step_sign_dispatch` | +10 |
| 3 | **TC-CP-019** | Outage active — CTA disabled | failure | `n/a::OUTAGE_ACTIVE` | — | F,U,+L | `D00_outage_banner` | +7 |
| 4 | **TC-CP-013** | SPZ NOK → gallery upload — recoverable | regression | `IN_PROGRESS_CIRCUMSTANCES` | zenID, AISPOV-AB | F | `D08_step_zenID_NOK` | +5 |
| 5 | **TC-CP-001** | PING SMS Gateway — happy | happy | `NEW` | N8 | F,R | `D01_step_PING` | +4 |
| 6 | **TC-CP-004** | OTP attempts exhausted (`SMS_CODE_ATTEMPTS`) | failure | `ERROR::SMS_CODE_ATTEMPTS` | N8 | F,R | `D02_step_OTP_attempts` | +4 |
| 7 | **TC-CP-005** | Phone number overused (`TELEPHONE_NUMBER_COUNT`) | failure | `ERROR::TELEPHONE_NUMBER_COUNT` | — | F,R | `D02_step_OTP_send` | +4 |
| 8 | **TC-CP-010** | AISPOV NENALEZENO ROB — negative no auto-fill | failure | `IN_PROGRESS_DRIVERS::AISPOV_ROB_NENALEZENO` | AISPOV-AB | F,S | `D04_step_AISPOV_NENALEZENO` | +4 |
| 9 | **TC-CP-016** | Sign-OTP exhaustion — negative | failure | `ERROR::SIGN_OTP_ATTEMPTS (TBC)` | N8 | F,R | `D17_step_sign_attempts` | +4 |
| 10 | **TC-CP-020** | Mid-wizard interlock self-disclosure — terminate | failure | `ERROR::ELIGIBILITY_INTERLOCK` | — | F,+L | `midwizard_interlock` | +4 |
| 11 | **TC-CP-002** | PING SMS Gateway — NOK (endpage) | failure | `n/a::PING_NOK` | N8 | F,R | `D01_step_PING` | +3 |
| 12 | **TC-CP-011** | Camera permission denied → gallery upload | regression | `IN_PROGRESS_DRIVERS` | — | F,U,+I | `D03_step_camera_perm` | +3 |

Score column shows the weighted sum of NEW dimensions this TC contributed at the moment it was picked. A monotonically falling curve is expected; the first TC always scores highest.

---

## §4. Coverage achieved with these 12

| Axis | Universe (Priority-A) | Covered by P0 | Gap |
|------|:--------------------:|:-------------:|-----|
| SM terminals (incl. error sub-reasons) | 11 | **11** | 0 ✓ |
| External integrations | 3 (N8, zenID, AISPOV-AB) | **3** | 0 ✓ |
| FURPS+ dimensions | 7 (F, R, P, S, U, +L, +I) | **7** | 0 ✓ |
| Test types | 3 (happy, failure, regression) | **3** | 0 ✓ |
| Distinct impulses | 17 | 11 | 6 (low-marginal — see §5) |

**Bottom line:** with 12 TCs, Kate's smoke is **structurally complete** across the dimensions that matter for shipping decisions. The 6 missing impulses are mostly duplications of the same step under different variant inputs — they're caught in Round 2.

---

## §5. The 7 Priority-A TCs NOT in P0 (Round-2 candidates)

These 7 didn't make P0 because their coverage contribution was already saturated. They should run in Round 2 as soon as P0 is green.

| TC code | Why deferred | Add in Round 2 because |
|---------|--------------|------------------------|
| TC-CP-003 | OTP send retry — same SM as TC-CP-005 | Validates retry backoff window separately |
| TC-CP-006 | OTP verify — same SM as TC-CP-004 | Verifies the verify-path vs the send-path |
| TC-CP-007 | DB frequency cap — `D02_step_DB_freq` | Volume-protective check |
| TC-CP-009 | OCR NOK — `D03_step_OCR_NOK` | OCR pipeline (parallel rail to zenID) |
| TC-CP-012 | SPZ → AISPOV happy — `D08_step_SPZ_AISPOV` | Vehicle-lookup happy path (TC-CP-013 is the failure variant) |
| TC-CP-014 | AISPOV vehicle missing | Vehicle-lookup negative variant |
| TC-CP-017 | Sign-dispatch submit timeout | Resilience at sign step |

---

## §6. The 5 Priority-B TCs (Round-3 only if budget)

| TC code | Note |
|---------|------|
| TC-CP-018 | E2E_full_run — caught implicitly when P0 + R2 green |
| TC-CP-021 | D12_swap_branch — branch-coverage TC, less critical |
| TC-CP-022 | D13_branch_GPS_RUIAN — needs RÚIAN integration (separate WS, lower priority) |
| TC-CP-023 | D14_radio_variants — UI radio-button variant (low risk) |
| TC-CP-024 | (TBD — verify in workbook; may be placeholder) |

---

## §7. Execution order for the smoke

Recommend Kate run P0 in **rank order**, not workbook order — TC-CP-008 first because if zenID+AISPOV happy-path is broken, all the dependent regression/failure TCs become noisy.

Suggested batches (5-min review pauses between):

| Batch | TCs | Why grouped |
|-------|-----|-------------|
| **B1 — happy core** | TC-CP-008, TC-CP-015, TC-CP-001 | If any fails, halt — happy paths must be green first |
| **B2 — error terminals** | TC-CP-004, TC-CP-005, TC-CP-010, TC-CP-016, TC-CP-020 | State-machine error coverage |
| **B3 — outage + recovery** | TC-CP-019, TC-CP-013, TC-CP-011, TC-CP-002 | Resilience scenarios |

This ordering also means a fail-fast halt at B1 saves Kate ~20 min vs running everything blindly.

---

## §8. Cross-framework execution

All 12 TCs declare `framework_targets = "playwright; cypress"`. Selenium is not declared as a target for any P0 TC, so Kate's P0 smoke is a **2-framework parallel run** — cypress and playwright invoked concurrently by the bouracka-ui dispatcher.

**Acceptance criterion** — a P0 TC is green iff **both** cypress AND playwright pass. If they diverge (cypress green, playwright red, or vice versa), that's a framework-binding bug and counts as a P0 fail with a separate FRAMEWORK-DIVERGENCE flag in the bug record.

---

## §9. Anti-thrash safeguards

Three boilerplate gates Kate should apply before running P0:

1. **Workbook check.** UI startup banner shows exactly `BOURACKA-TESTPLAN-v0.4.3.xlsx` (no v0.4.2 contamination — BUG-K-003 fix discipline).
2. **Env check.** UI About page → workbook_path and runs_dir both resolve; dispatch mode = `real` (not `mock`).
3. **TestTarget reach.** `tst.demo.bouracka.cz` resolves and answers HTTPS 200 on root. (For ext_ws-dependent TCs the integration recon harness — `recon-harness/int_recon.py` — should also be green if Kate is on SUPIN VPN.)

---

## §10. Open questions for KP

| # | Question | Default if no answer |
|---|----------|---------------------|
| Q-P0-1 | Should TC-CP-018 (E2E_full_run) be promoted into P0 as a 13th "umbrella" check? | **No** — it's caught implicitly when P0+R2 green, and adds runtime without independent coverage. |
| Q-P0-2 | Should the score-+0 tiebreaker prefer regression > failure > happy at equal-score? | **Already accidentally so** — happy=high score early because happy paths unlock more new dimensions; ties resolve via alphabetic tc_code which happens to favor sequential order. |
| Q-P0-3 | Should priority-A "draft" status be promoted to "ready" before P0 runs? | **Yes** — workbook still shows all 24 TCs as `draft`; KP should review + promote at least these 12 to `ready` before Kate's R2. |
| Q-P0-4 | Does Kate's UAT scope include `applies_to_prod=true` TCs, or demo-only? | **Demo-only for v0.1.4 smoke;** prod variants run by SUPIN colleague post-server-install. |

---

## §11. Reproducibility — how to re-rank

Re-run the selector when the workbook changes (new TCs, new SM terminals, new integrations):

```python
# pseudo-code in workbook-aware Python
tcs = openpyxl_read('02_TestCases')
A_tcs = [t for t in tcs if t.priority == 'A']
P0 = []
covered = {axis: set() for axis in ('sm','ext','furps','imp','type')}
while len(P0) < 12 and A_tcs:
    best = max(A_tcs, key=lambda t: marginal_score(t, covered))
    P0.append(best)
    for axis in covered: covered[axis] |= dimensions(best, axis)
    A_tcs.remove(best)
```

Full reference implementation: `tools/p0-ranker.py` (proposed to add for v0.1.5 — see Q-V015 follow-ups in design notes).

---

## §12. Refs

- `BOURACKA-TESTPLAN-v0.4.3.xlsx` sheet `02_TestCases` — source of truth.
- `_config/BOURACKA-UI-V0.1.5-DESIGN-NOTES-EN.md` — Test-Step entity, FR-K-001/002/003/004 (Test-Steps will enable per-step coverage on top of per-TC coverage in P0 v0.2).
- `_config/TEST-ANALYSIS-AND-DESIGN-DEEP-SESSIONS-PLAN-v0.1-EN.md` D6c — Session 2 will revisit ranking heuristic.
- `recon/integrations/INT-010-D8WS-SEDN-create.md` + `INT-011-D5WS-SEDN-lookup.md` — N8 (SEDN) integration evidence; ranks TC-CP-001/002/004/006/015/016 high for SEDN coverage.
