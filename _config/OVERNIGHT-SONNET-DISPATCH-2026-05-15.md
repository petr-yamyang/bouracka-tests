# Overnight Sonnet dispatch package — v0.1.5 build

**Date.** 2026-05-15.
**Target.** Claude Sonnet 4.6 in Claude Code (terminal, fresh session).
**Operator.** Pete will start this session before sleep; Sonnet runs unattended; Pete reviews on wake.
**Goal.** Maximum forward progress on the v0.1.5 brief stack without Pete being available to triage. Strict guardrails prevent destructive drift.

---

## Read this whole file before starting any brief

This is your master plan for the overnight session. It tells you which briefs to dispatch yourself on, in what order, with what guardrails, and what to do when you get stuck. Pete is asleep — there's no quick check-in available. Act conservatively.

---

## 1. The brief stack (order matters)

Run in this exact order. Each brief lives in `_config/SONNET-BRIEF-<NN>-<name>.md`. Read the brief, work it, commit, move on.

| Order | Brief | Path | Expected effort | Why this order |
|:---:|---|---|:---:|---|
| 1 | #005 mock dispatch e2e (the shield) | `_config/SONNET-BRIEF-005-MOCK-DISPATCH-E2E.md` | 2h | Anchors test infrastructure for everything else. Opus prototype exists at `bouracka_ui/tests/test_mock_dispatch_e2e.py` with 6 passing tests; you harden + extend. |
| 2 | #004 hotfix bundle (K-009/010/012) | `_config/SONNET-BRIEF-004-HOTFIX-BUNDLE.md` | 2h | Surgical 3-fix bundle. Doc + env-mapping + TestRuns append. Independent of others. |
| 3 | #006 integration probe expansion | `_config/SONNET-BRIEF-006-INTEGRATION-PROBE-EXPANSION.md` | 3h | Extends `int_recon.py` to cover INT-001..009. Pure additive, low risk. |
| 4 | #002 workbook_io readers + endpoints | `_config/SONNET-BRIEF-002-WORKBOOK-IO-AND-V015-ENDPOINTS.md` | 3h | Adds `list_steps`, `get_step`, `get_bug_evidence` + 4 endpoints. Required by #007. |
| 5 | #007 cross-check report | `_config/SONNET-BRIEF-007-CROSS-CHECK-REPORT.md` | 4h | **OPUS PROTOTYPE EXISTS** at `bouracka_ui/bouracka_ui/cross_check.py` (~280 lines) + `bouracka_ui/tests/test_cross_check.py` (11 passing tests). You wire the 2 endpoints + extend tests. Drift risk near-zero because the function lives. |
| 6 | #001b patcher row-level data migration | `_config/SONNET-BRIEF-001B-PATCHER-DATA-MIGRATION.md` | 3h | Extends v0.4.3 → v0.4.4 patcher with `--source-data` flag. Tools-only; no bouracka_ui touch. |

**DO NOT** run Briefs #003 (TC discovery, UI churn), #009 (audit mode, 8-10h, biggest unknown), or #008 (release engineering, must come last) in this overnight session — they require Pete review and the audit-mode brief is too big. Stop at brief #6.

If you finish all 6 in less than 17 hours, **DO NOT** start #003 or #009 — instead, stop, summarise progress in §6, and leave Pete the morning review queue.

---

## 2. Hard rules — no exceptions

### 2.1 One branch per brief

For each brief, create a separate git branch from current `main` head:

```
Brief #5  →  cp-supin-11-mock-dispatch-e2e
Brief #4  →  cp-supin-13-hotfix-bundle
Brief #6  →  cp-supin-14-int-probe-expansion
Brief #2  →  cp-supin-17-workbook-io-readers
Brief #7  →  cp-supin-15-cross-check-report
Brief #1b →  cp-supin-09-v0.4.4-data-migration
```

Each branch produces clean commits. **No cross-branch merges**. Pete merges them in the morning.

### 2.2 When you finish a brief

1. Run the brief's tests; they MUST pass.
2. Commit with conventional message: `feat(scope): summary` for new code, `fix(scope): summary` for bugs.
3. Tag the commit with a note: `git notes add -m "Brief #N — see _config/SONNET-BRIEF-N-*.md §13 acceptance"`.
4. Push to remote IF a remote is configured (else stay local).
5. Write a one-page completion report at `_config/SONNET-RETURN-BRIEF-<NN>.md` with the §10 return checklist filled in.
6. Move to next brief in §1.

### 2.3 When you get stuck

Halt rules — if ANY of these trigger, **STOP THE BRIEF, do not improvise**:

- Brief's §9 risk gate fires (each brief lists 4-7 named conditions)
- Existing tests fail after your change (regression — not progress)
- A required file from the brief doesn't exist (e.g., a predecessor brief didn't land properly)
- You're about to modify a file the brief's §4 says "DO NOT touch"
- You're about to write more than 50 lines into a single function (probably architectural drift)
- You can't make a test pass after 30 minutes of trying

Halt protocol:

1. Commit current WIP to the brief's branch with message: `wip(scope): HALT — <reason>`.
2. Write `_config/SONNET-HALT-BRIEF-<NN>.md` explaining what blocked you in plain English (3-5 paragraphs). Include the exact error, the file/line, what you tried, why you stopped.
3. Move to the NEXT brief in §1. Do not stay stuck.

### 2.4 Things you must never do

- **Never** modify `_config/AUDIT-MODE-DESIGN-v0.1-EN.md`, `_config/TC-DISCOVERY-DESIGN-v0.1-EN.md`, `_config/MAJOR-DEV-SESSION-PLAN-v0.1.5-EN.md`, or any `SONNET-BRIEF-*.md`. These are read-only specs.
- **Never** modify `BOURACKA-TESTPLAN-*.xlsx` workbooks except through the v0.4.3 → v0.4.4 patcher (Brief #001 already merged) or the patcher you're extending in #001b.
- **Never** modify `delivery/` ZIPs or scripts. They're shipped artefacts.
- **Never** modify `dispatcher.py` outside Brief #004's exact patch scope (env normalization). The dispatcher is shared infrastructure.
- **Never** ship a Kate-bound build. Brief #008 is the release brief, and you're not running it.
- **Never** push to `main` directly. All work goes to `cp-supin-*` branches for Pete's review.

---

## 3. Setup commands (run first thing)

Before starting Brief #5, run these one-liners:

```bash
cd C:\Users\vitez\Documents\VibeCodeProjects\SUPIN\bouracka-tests
git status   # confirm clean tree
git checkout main 2>nul || git checkout master 2>nul
git pull --rebase 2>nul   # may fail if no remote — OK
```

Confirm:

- `bouracka_ui/bouracka_ui/__init__.py` reads `__version__ = "0.1.5-dev2"` (post-Brief-#005-prototype state)
- `BOURACKA-TESTPLAN-v0.4.4.xlsx` exists in `delivery/KATE-DROP-2026-05-13/` (proves Brief #001 landed)
- `bouracka_ui/tests/test_mock_dispatch_e2e.py` exists (Opus prototype) and contains direct-call tests
- `bouracka_ui/bouracka_ui/cross_check.py` exists (Opus prototype, 280 lines)
- `bouracka_ui/tests/test_cross_check.py` exists with 11 tests

If any of these are missing, halt the session with `_config/SONNET-HALT-SETUP.md` describing which precondition fails.

---

## 4. Per-brief quick-reference (don't reread the full brief file — these are the highlights)

### Brief #005 — mock dispatch e2e shield

**File:** `_config/SONNET-BRIEF-005-MOCK-DISPATCH-E2E.md`
**Branch:** `cp-supin-11-mock-dispatch-e2e`
**Key truth:** Opus prototype already passes 6 tests (Family A direct-call). Family B (HTTP subprocess) failed in sandbox on httpx SOCKS env quirk. Your job:

1. Fix Family B with `httpx.Client(trust_env=False)` so it ignores any system proxy env vars
2. Add 4 more tests per §F-1 (soft-pass, skip-drift, summary counts, env-url match)
3. Add 3 negative meta-tests per §8 (test the tests)
4. Bump version to `0.1.5-dev2` (already at this; leave alone unless brief explicit)
5. Run full suite: `pytest bouracka_ui/tests/ -v` → all green, including Family B with marker

Stop if: the prototype's 6 tests fail before you touch them (means upstream regression).

### Brief #004 — hotfix bundle

**File:** `_config/SONNET-BRIEF-004-HOTFIX-BUNDLE.md`
**Branch:** `cp-supin-13-hotfix-bundle`
**Key truth:** 3 surgical fixes:

1. **BUG-K-010** — `dispatcher.py`: locate the `--env <env>` arg to consolidator subprocess. Add `UI_ENV_TO_CONSOLIDATOR_TIER` mapping. Use `normalize_env_for_consolidator(env)` before `--env`. ~5 lines of code.
2. **BUG-K-012** — investigate first. Look in `server.py /api/runs` POST and `workbook_io`. Brief §5 outlines two outcomes (A: workbook untouched, no fix; B: append fix needed). Take whichever outcome reality presents.
3. **BUG-K-009** — doc-only. Add `§1.0 Předpoklady` section to 3 install runbooks per Brief §F-3.

Plus 4 tests + version bump → `0.1.5-dev4`.

Stop if: the F-1 dispatcher location is genuinely not findable (grep for `--env` and `consolidate`).

### Brief #006 — integration probe expansion

**File:** `_config/SONNET-BRIEF-006-INTEGRATION-PROBE-EXPANSION.md`
**Branch:** `cp-supin-14-int-probe-expansion`
**Key truth:** Extends `delivery/SUPIN-SERVER-DROP-2026-05-13/recon-harness/int_recon.py`. Add 3 new probe types (`http_get_json`, `http_head_with_referrer`, `https_tls_verify`). Add 7 new targets to `targets.json` from INT-001..009. Update README-CS.md with probe-type matrix.

No tests added (recon harness is operator-side). Sandbox smoke: run `python int_recon.py probe-all` against unreachable SUPIN IPs + reachable internet targets; expect FAIL/PASS split.

Stop if: the int_recon.py current structure surprises you (e.g., probe functions don't follow the function-per-probe pattern Brief assumes).

### Brief #002 — workbook_io readers + endpoints

**File:** `_config/SONNET-BRIEF-002-WORKBOOK-IO-AND-V015-ENDPOINTS.md`
**Branch:** `cp-supin-17-workbook-io-readers`
**Key truth:** Add 3 new reader functions to `workbook_io.py` (`list_steps`, `get_step`, `get_bug_evidence`). Add 4 new endpoints to `server.py` (`/api/tcs/{tc}/steps`, `/api/steps/{step}`, `/api/bugs/{bug}/evidence`, `/api/runs/*` static files). Update smoke tests 28→33. Version → `0.1.5-dev0` (wait — Brief #005 already pushed to dev2; you go to dev3 or dev4 here as appropriate based on the chain).

Stop if: `02e_TestSteps` sheet doesn't exist in the v0.4.4 workbook (Brief #001 patcher may not have actually landed).

### Brief #007 — cross-check report

**File:** `_config/SONNET-BRIEF-007-CROSS-CHECK-REPORT.md`
**Branch:** `cp-supin-15-cross-check-report`
**KEY TRUTH:** **OPUS PROTOTYPE EXISTS AND IS GREEN.** `bouracka_ui/bouracka_ui/cross_check.py` (~280 lines, working) + `bouracka_ui/tests/test_cross_check.py` (11 tests, all passing in sandbox). Your job is ONLY:

1. Wire 2 endpoints in `server.py`:
   - `GET /api/runs/{run_id}/cross-check` → JSON
   - `GET /api/runs/{run_id}/cross-check.html` → HTML
2. Helper `_find_envelope_for_run(run_id)` in server.py — walk `runs/` dir for matching envelope file.
3. 2 new endpoint smoke tests (mirroring existing test_smoke.py pattern).
4. CHANGELOG entry.

**DO NOT modify cross_check.py module logic.** It's proven. Only add to it if you find a missing helper.

Stop if: cross_check.py tests fail (means upstream regression; not your fault, halt).

### Brief #001b — patcher row-level data migration

**File:** `_config/SONNET-BRIEF-001B-PATCHER-DATA-MIGRATION.md`
**Branch:** `cp-supin-09-v0.4.4-data-migration`
**Key truth:** Extend `tools/workbook-v0.4.3-to-v0.4.4.py` with `--source-data PATH` flag. Migrate `08_Bugs`, `06_TestRuns`, `07_TestRunResults`, `09_Reports`, `13_TestExecutionSummary`, `14_AssertionGateResults` rows from a separate source-data workbook. NEVER touch schema sheets (02_TestCases etc.).

Plus 10 tests using a synthetic fixture. No bouracka_ui changes.

Stop if: the existing v0.4.3 → v0.4.4 patcher has a different structure than Brief #001b assumes (read the patcher first, adapt).

---

## 5. Test discipline

After every brief:

```bash
pytest bouracka_ui/tests/ -v -c /dev/null   # bypass any local pyproject quirks
```

This must show all-green for the brief's added tests AND all previous tests still green (regression check). If a previous test fails, your change broke something — halt the brief.

For Brief #001b, run:

```bash
pytest tools/tests/ -v
```

---

## 6. End-of-session protocol (when you stop)

When you've finished all 6 briefs OR run out of time OR halted twice, write `_config/SONNET-OVERNIGHT-SUMMARY-2026-05-15.md` with:

```markdown
# Overnight Sonnet session summary — 2026-05-15

## What landed
- Brief #N: branch <name>, commit <SHA>, tests <pass/fail count>
- ...

## What halted (and why)
- Brief #N: halted at <step>, see SONNET-HALT-BRIEF-N.md

## What was NOT attempted
- Brief #N: not reached this session (out of time / dependency unmet)

## Open questions for Pete review
- Q1: ...
- Q2: ...

## Recommended next-session order
- Pick up at Brief #N
- Then ...

## Total Sonnet time consumed
- Estimated NN hours across NN briefs.
```

Then STOP. Do not start a new brief. Do not retry a halted one without Pete's go-ahead.

---

## 7. Communication artifacts Pete will read in the morning

When Pete wakes, he reviews IN THIS ORDER:

1. `_config/SONNET-OVERNIGHT-SUMMARY-2026-05-15.md` (the meta — what happened)
2. Any `_config/SONNET-HALT-BRIEF-<NN>.md` (the blockers)
3. Each `_config/SONNET-RETURN-BRIEF-<NN>.md` (the completion reports, briefs that landed)
4. `git log --oneline --all` (the actual commits)

So make sure all three are present, accurate, and brief.

---

## 8. Specific rules for the prototype-anchored briefs

### Brief #005 anchor

Pete's prototype at `bouracka_ui/tests/test_mock_dispatch_e2e.py`:
- Has 6 direct-call tests (Family A) — proven 3.35s green
- Has 1 HTTP test (Family B) — fails in sandbox due to httpx SOCKS env quirk
- Validators are correct; trust them

DO add: 4 more direct-call tests, 3 negative meta-tests, fix Family B with `trust_env=False`.
DO NOT add: complex new validators, new envelope schema fields, alternate dispatch paths.

### Brief #007 anchor

Pete's prototype at `bouracka_ui/bouracka_ui/cross_check.py`:
- 280 lines, pure-function design
- `build_cross_check(envelope, steps_lookup)` → projection dict
- `render_cross_check_html(cc)` → standalone HTML string
- 11 passing tests in `bouracka_ui/tests/test_cross_check.py`

DO: wire 2 server.py endpoints, add `_find_envelope_for_run` helper, write 2 endpoint smoke tests.
DO NOT: modify cross_check.py's logic, change the projection schema, add JS to the HTML, refactor the HTML renderer.

---

## 9. Final reminder

Pete is asleep. You have full autonomy on the 6 briefs. You have hard guardrails on what you CAN'T touch. When stuck → halt that brief, write the halt note, move to next. Do not invent fixes the briefs didn't ask for.

The bouracka-ui codebase is already proven to work; your additions are additive. Do not refactor existing code that works just because you think it could be cleaner. Pete's a pragmatic engineer; he reviews diffs, and small clean diffs review faster than big elegant ones.

Good luck. Go.

---

**End of OVERNIGHT-SONNET-DISPATCH-2026-05-15.**
