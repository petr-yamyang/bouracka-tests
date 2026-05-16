# Sonnet brief — BRIEF-005: mock-mode dispatch e2e test

**Target Claude.** Sonnet 4.6 in Claude Code (terminal, stateless).
**Issued by.** Opus 4.7 session (Pete Y. + Claude), 2026-05-14.
**Branch.** `cp-supin-11-mock-dispatch-e2e` (create from current `main` head).
**Estimated effort.** ~2 hours of Sonnet time (light — most work already prototyped).
**Reviewer.** Pete in Opus 4.7 session, after Sonnet returns the checklist in §10.
**Blocked by.** Nothing — this brief stands alone and ships independently.

---

## 1. Goal in one paragraph

Build the **shield** that prevents Kate ping-pong: an end-to-end test that exercises the full dispatch → consolidate → envelope chain in **mock mode**, without requiring cypress / playwright / selenium installed. After this lands, every code change to `dispatcher.py`, `workbook_io.py`, `server.py`, or the consolidator gets validated by this test before any Kate-bound build is considered ship-ready. Opus has already built a working prototype at `bouracka_ui/tests/test_mock_dispatch_e2e.py` — 6 direct-call tests pass in 3.35s in a Linux sandbox. Your job: harden the prototype, add the HTTP e2e family (one subprocess-based test that proves the network path works), register the pytest marker, and integrate the new tests into the existing CI smoke gate (28 tests → 35+ tests).

---

## 2. Spec — read this BEFORE coding

Open and read in full:

1. **`bouracka_ui/tests/test_mock_dispatch_e2e.py`** — the working prototype. This is your starting point. Treat it as design-by-example.
2. `bouracka_ui/bouracka_ui/dispatcher.py` — particularly `_run_mock`, `_build_mock_envelope`, `_mock_verdict` (lines ~274-380). The envelope schema you validate against comes from here.
3. `bouracka_ui/bouracka_ui/server.py` — `/api/runs` POST handler (~line 210), `/api/runs/{run_id}` GET handler (~line 299).
4. `_specs/CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.md` — the canonical v0.1 envelope schema. Cross-check your validators against this; if there's drift, ask Pete.
5. `_config/MAJOR-DEV-SESSION-PLAN-v0.1.5-EN.md` §3.3 Gate 1 — describes what this test gates.

When the prototype and the schema doc disagree, **the schema doc is authoritative** — note any drift in §10 item 6.

---

## 3. Inputs / outputs

### Inputs

- Working prototype: `bouracka_ui/tests/test_mock_dispatch_e2e.py` (~280 lines, runs green for direct-call).
- bouracka_ui v0.1.4 code in repo (dispatcher + server + workbook_io).
- pytest 9.0+ already in test runtime.
- httpx + uvicorn deps (already in wheelhouse).

### Outputs

1. Hardened `bouracka_ui/tests/test_mock_dispatch_e2e.py` with both families green.
2. Registered `http_e2e` marker in `bouracka_ui/pyproject.toml` or `conftest.py`.
3. Optional: helper module `bouracka_ui/tests/_envelope_validators.py` if validators grow beyond 100 lines and warrant extraction.
4. Updated `bouracka_ui/tests/test_smoke.py` smoke-count assertion (if it checks total test count).
5. CHANGELOG.md entry under v0.1.5-dev2.

---

## 4. File boundaries — what you may touch

### Create

- `bouracka_ui/tests/conftest.py` — IF it doesn't exist; add pytest marker registration here. If it exists, modify it.
- `bouracka_ui/tests/_envelope_validators.py` — OPTIONAL extraction of validators if the test file grows past ~400 lines.

### Modify

- `bouracka_ui/tests/test_mock_dispatch_e2e.py` — harden + extend per §5.
- `bouracka_ui/pyproject.toml` — register `http_e2e` marker (preferred location).
- `bouracka_ui/tests/test_smoke.py` — IF it has a count assertion like `assert len(tests) == 28`, bump it; otherwise leave alone.
- `bouracka_ui/bouracka_ui/__init__.py` — bump `__version__` to `0.1.5-dev2`.
- `bouracka_ui/pyproject.toml` — `version = "0.1.5.dev2"`.
- `CHANGELOG.md` — append v0.1.5-dev2 entry.

### DO NOT touch

- `bouracka_ui/bouracka_ui/dispatcher.py` — read-only; your tests validate it, they don't change it.
- `bouracka_ui/bouracka_ui/server.py` — read-only same reason.
- `bouracka_ui/bouracka_ui/workbook_io.py` — out of scope.
- `tools/` — out of scope.
- `_config/` — read-only specs.
- `delivery/` — out of scope.
- `_specs/` — read-only.

If you find a bug in `dispatcher.py` (BUG-K-010 env mapping is known to live there — UI sends `tst-demo` and consolidator chokes), **note it in checklist item 6 and DO NOT fix it here**. That's Brief #004's lane.

---

## 5. Functional requirements (extending what the prototype already does)

### F-1. Harden Family A direct-call tests

The 6 existing direct-call tests pass. Extend with:

- `test_mock_dispatch_direct_soft_pass_scenario` — ALT-9 TC produces `soft-pass` verdict; envelope's `soft_pass_reason` field is populated.
- `test_mock_dispatch_direct_skip_drift_scenario` — ALT-1 produces `skip-drift` verdict; verify the `drift_forensic` block (`guard_policy: "skip-on-drift"`, `affected_tcs` non-empty).
- `test_mock_dispatch_direct_summary_counts_correct` — for a deterministic mix of TCs (1 pass + 1 fail + 1 drift), envelope `summary` block contains correct integer counts.
- `test_mock_dispatch_direct_env_url_matches_env` — for each env label (demo / tst-demo / tst / uat / prod-readonly), `envelope["env_url"]` matches `dispatcher.ENV_TO_BASE_URL[env]`.

### F-2. Implement Family B HTTP e2e (currently failed in sandbox)

The prototype has Family B sketched but it failed due to an httpx SOCKS proxy issue in the sandbox env. Make it work:

- Fix the httpx call to NOT inherit the sandbox's HTTPS_PROXY / SOCKS env vars. Use `httpx.Client(trust_env=False)` or pass `proxies={}` explicitly.
- Use a high port (8425) to avoid clashing with developer-side bouracka-ui sessions on 8424.
- Subprocess startup: pipe stdout/stderr to log file in tmp_path, poll `/api/health` until ready (max 10s).
- Polling pattern: `/api/runs/{run_id}` every 0.5s, max 30s total.
- Verify envelope file at the path returned by `body["envelope_path"]`.

If subprocess fails to bind port (e.g., port already in use), `pytest.skip()` with the bound process info — don't fail the suite for environmental reasons.

### F-3. Register `http_e2e` marker

The prototype emits a warning: `PytestUnknownMarkWarning: Unknown pytest.mark.http_e2e`. Register it in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
markers = [
    "http_e2e: slow HTTP subprocess tests; skipped in default run",
]
```

Default test run: `pytest -m "not http_e2e"` runs Family A only (~3s).
Full test run: `pytest` runs both families (~15s).
HTTP only: `pytest -m http_e2e` runs Family B only.

### F-4. Validator helpers — share between Family A and B

The prototype has `assert_envelope_valid` as a module function. If you extract to `_envelope_validators.py`, import it into the test file. Keep validators ≤ 200 lines total.

Add a `validate_against_schema_doc()` function that cross-references `_specs/CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.md` — parses the markdown to extract required field names, then asserts the envelope has them all. If schema doc has more fields than the envelope produces, that's an envelope bug worth flagging in §10.

### F-5. Version bump + CHANGELOG entry

```
__version__ = "0.1.5-dev2"  (bouracka_ui/bouracka_ui/__init__.py)
version = "0.1.5.dev2"      (bouracka_ui/pyproject.toml)
```

CHANGELOG v0.1.5-dev2 section bullets:

- Added `bouracka_ui/tests/test_mock_dispatch_e2e.py` — mock-mode dispatch shield (10+ tests across 2 families)
- Registered `http_e2e` pytest marker
- Sanity gate: dispatch chain now validated without external framework deps

---

## 6. Idempotency

- `pytest bouracka_ui/tests/` runs cleanly on repeated invocations (no leftover server process, no shared port conflicts, no leftover envelope files in `runs/`).
- `tmp_path` fixture isolates each test's `runs/` directory.
- Subprocess server is torn down via try/finally even on test failure.

---

## 7. CLI surface

No CLI changes — tests are invoked via pytest.

```
pytest bouracka_ui/tests/                       # ~5s, runs everything
pytest bouracka_ui/tests/ -m "not http_e2e"     # ~3s, fast smoke
pytest bouracka_ui/tests/ -m http_e2e           # ~10s, HTTP only
pytest bouracka_ui/tests/test_mock_dispatch_e2e.py -v   # this file only
```

---

## 8. Test plan — meta-test (test the tests)

Hard rule: every test in `test_mock_dispatch_e2e.py` must have at least one **negative assertion** that proves the validator catches a malformed envelope. Add:

- `test_validator_rejects_missing_run_id` — feed `assert_envelope_valid` an envelope minus `run_id` → should AssertionError
- `test_validator_rejects_unknown_verdict` — verdict `"halfpass"` (not in CANONICAL_VERDICTS) → should AssertionError
- `test_validator_rejects_wrong_tc_count` — 3 tcs requested, 2 results in envelope → should AssertionError

These prove the validator isn't silently accepting bad envelopes — a classic test-the-tests trap.

---

## 9. Risk gates — STOP and report if you hit any

1. **`assert_envelope_valid` fails on real mock output** for an envelope key combination Opus didn't anticipate. Halt, dump the envelope JSON, ask Pete to clarify expected shape.
2. **subprocess uvicorn fails to start** in Family B for reasons OTHER than port conflict (e.g., import error, missing dep). Halt; capture the stderr log; ask Pete.
3. **`_specs/CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.md` has fields the envelope doesn't produce** — that's an envelope-side bug, not a test bug. Halt + flag.
4. **Test runtime > 30 seconds for Family A** (the fast suite). Optimize or split before merging.
5. **Random test failures across multiple runs** — investigate flakiness; mocked subprocess timing is usually the culprit. If you can't make it deterministic in 30 min, mark the offending test with `@pytest.mark.flaky` AND open a follow-up task.

---

## 10. Return checklist

1. Branch name + commit SHA(s).
2. Files changed (created / modified) with line counts.
3. Test results — paste the full `pytest bouracka_ui/tests/ -v` output (should show all green, both Family A and B).
4. Test runtime breakdown — "Family A: X seconds, Family B: Y seconds, total: Z seconds".
5. Out-of-scope findings — including the BUG-K-010 env-mapping issue you'll see in dispatcher.py (note; don't fix).
6. Deviations from this brief with one-sentence justifications.
7. Open questions for the chain — likely something like "should we add a `pytest --mock-dispatch-only` CLI flag for CI?" — surface but don't implement.

---

## 11. Don't-go-beyond markers

- **Do not modify dispatcher.py** to fix bugs you observe. Note them only.
- **Do not implement real-mode (cypress/playwright/selenium) e2e tests** — that's a future brief.
- **Do not add Selenium-specific test paths** beyond what the prototype validates.
- **Do not add property-based testing (Hypothesis)** — overkill for this shield.
- **Do not refactor dispatcher.py** to make tests easier — leave it alone, work with the API as-is.
- **Do not add CI yaml** (GitHub Actions / etc.) — separate brief.

---

## 12. Quick-reference: spec sections by file/line

| Brief item | Spec ref |
|------------|----------|
| Envelope schema validation | dispatcher.py `_build_mock_envelope` (lines ~320-380) |
| Verdict canonicalization | dispatcher.py `_to_canonical` (line ~376) |
| Parity computation rules | dispatcher.py `_build_mock_envelope` (lines ~333-340) |
| Drift forensic trigger | dispatcher.py `_build_mock_envelope` (lines ~363-371) — ALT-1 substring match |
| `_run_mock` flow | dispatcher.py lines 274-308 |
| `/api/runs` POST contract | server.py line ~210 |
| `/api/runs/{run_id}` GET contract | server.py line ~299 |

---

## 13. Acceptance — when is this brief "done"?

- All Family A tests green (`pytest -m "not http_e2e"`) in <5s.
- All Family B tests green (`pytest -m http_e2e`) in <15s.
- `http_e2e` marker registered, zero PytestUnknownMarkWarning.
- Validator meta-tests prove validators reject bad envelopes.
- `__version__` reads `0.1.5-dev2`.
- CHANGELOG has the v0.1.5-dev2 entry.
- Branch has clean commits with conventional messages.
- Return checklist §10 pasted to Pete with all proof items.

Then Pete reviews; next downstream work is Brief #007 (cross-check reports) which will REUSE this envelope-validation harness to test the cross-check extension.

---

**End of BRIEF-005.**
