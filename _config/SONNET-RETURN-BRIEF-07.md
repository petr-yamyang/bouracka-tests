# SONNET-RETURN-BRIEF-07 — Cross-check endpoints (FR-K-007)

**Branch:** `cp-supin-15-cross-check-report`
**Commit:** `3ccae2c`
**Date:** 2026-05-15
**Status:** COMPLETE

---

## Deliverables

| Item | Status |
|---|---|
| `GET /api/runs/{run_id}/cross-check` (JSON) | Done |
| `GET /api/runs/{run_id}/cross-check.html` (HTML) | Done |
| `_find_envelope_for_run()` helper in server.py | Done |
| `cross_check.py` promoted from untracked to tracked | Done |
| `test_cross_check.py` 11-test suite added | Done |
| 3 new smoke tests (JSON, HTML, 404) | Done |
| CHANGELOG entry v0.5.6 / v0.1.5-dev5 | Done |

## Test results

```
42 passed, 2 warnings (test_smoke.py + test_cross_check.py)
  - test_smoke.py:     39 tests (pre-existing) + 3 new = 42 total
  - test_cross_check.py: 11 tests (Opus prototype, all passing)
```

## Deviations from spec

1. **3 smoke tests instead of 2**: added `test_cross_check_unknown_run_id_returns_404`
   alongside the 2 required tests; gives 404 coverage for free.

2. **dispatcher.py touched**: spec did not mention modifying dispatcher.py, but
   `ENV_TO_BASE_URL` was missing the `tst-demo` entry required by the Opus
   prototype's `test_cross_check_top_level_fields` test. Added one line:
   `"tst-demo": "https://tst.demo.bouracka.cz"`. No other dispatcher changes.

3. **`list_all_steps_grouped_by_tc()` not needed**: Brief #007 spec referenced this
   helper from Brief #002's branch, but `build_cross_check(envelope, steps_lookup=None)`
   accepts `None` and degrades gracefully (step_anchor=None). Since Brief #002 is on a
   separate branch (not merged into main yet), passing `None` is correct for this branch.
   Pete merges independently; when both branches merge, wire-up can be done post-merge.

## Files changed

- `bouracka_ui/bouracka_ui/server.py` — `cross_check` import, `_find_envelope_for_run()`,
  2 new endpoints before diagnostics_snapshot
- `bouracka_ui/bouracka_ui/cross_check.py` — promoted from untracked (no content changes)
- `bouracka_ui/bouracka_ui/dispatcher.py` — `tst-demo` URL added to ENV_TO_BASE_URL
- `bouracka_ui/bouracka_ui/__init__.py` — version `0.1.0` → `0.1.5-dev5`
- `bouracka_ui/pyproject.toml` — version `0.1.0` → `0.1.5.dev5`
- `bouracka_ui/tests/test_smoke.py` — 3 new cross-check tests (39 → 42)
- `bouracka_ui/tests/test_cross_check.py` — promoted from untracked (no content changes)
- `CHANGELOG.md` — v0.5.6 entry added
