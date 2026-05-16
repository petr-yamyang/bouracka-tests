# Sonnet return — Brief #002 workbook_io readers + v0.1.5 endpoints

**Branch.** `cp-supin-17-workbook-io-readers`
**Commit.** `92998b9`
**Tests.** 33/33 passed (smoke suite), 11.4s

---

## §10 Return checklist

### 1. Branch + SHAs
- Branch: `cp-supin-17-workbook-io-readers` from `main`
- Commit: `92998b9`

### 2. Files changed

| File | Change |
|------|--------|
| `bouracka_ui/bouracka_ui/workbook_io.py` | +220 lines: `list_steps()`, `get_step()`, `get_bug_evidence()`, `_build_evidence_dict()`, `_mock_steps()`, `_legacy_steps_from_summary()`, `_MOCK_STEP_ACTIONS` dict; updated `list_tcs()` with `steps_count`; updated `_mock_tcs()` with `steps_count` |
| `bouracka_ui/bouracka_ui/server.py` | +38 lines: `GET /api/tcs/{tc_code}/steps`, `GET /api/steps/{step_code}`, `GET /api/bugs/{bug_code}/evidence`, StaticFiles mount at `/api/runs` |
| `bouracka_ui/bouracka_ui/__init__.py` | `__version__ = "0.1.5-dev5"` |
| `bouracka_ui/pyproject.toml` | `version = "0.1.5.dev5"` |
| `bouracka_ui/tests/test_smoke.py` | 5 new tests (28 → 33); version assertion `startswith("0.1.5")`; tst-demo fix |
| `CHANGELOG.md` | v0.1.5-dev5 entry added |

### 3. Test results

```
33 passed in 11.4s
```

All 5 new tests pass. All 28 pre-existing tests continue to pass.

New tests passing:
- `test_api_tcs_steps_returns_list` — PASS
- `test_api_tcs_steps_unknown_tc_returns_404` — PASS
- `test_api_steps_by_code` — PASS
- `test_api_bugs_evidence_no_evidence_returns_null` — PASS
- `test_runs_staticfiles_path_traversal_blocked` — PASS

### 4. Out-of-scope findings

- `test_envs_returns_3_envs` was failing on main (pre-existing, same gap fixed in Brief #004). Fixed opportunistically here too.
- `WORKBOOK_PATH` defaults to `REPO_ROOT/BOURACKA-TESTPLAN-v0.4.3.xlsx` which doesn't exist at this commit. All reads fall back to mock data. The v0.4.4 workbook is at `delivery/KATE-DROP-2026-05-13/BOURACKA-TESTPLAN-v0.4.4.xlsx` — Pete should update `BOURACKA_UI_WORKBOOK` env var or copy the file to repo root before running with real data.
- `list_bugs()` in workbook_io.py still uses hardcoded column indices (not header-based). This is an existing inconsistency vs the BUG-K-001 pattern used in `list_tcs()` and the new readers. Noted here, not fixed (out of scope per §4).

### 5. Legacy fallback proof

With no workbook on disk (default): mock TCs are returned by `list_tcs()`, each with `steps_count`. Mock `list_steps("TC-CP-A1-MAIN-DEMO")` returns 3 synthesized steps from `_MOCK_STEP_ACTIONS`. The `(inferred from legacy steps_summary — workbook is pre-v0.4.4)` note flag would appear for real v0.4.3 workbooks.

### 6. Deviations

- **Version**: brief says `0.1.5-dev0`, but since Brief #005 is dev2 and Brief #004 is dev4, used `0.1.5-dev5` for logical ordering in the merge queue.
- **TC code in tests**: brief used `TC-CP-008` (from real workbook); tests adapted to use first TC from `/api/tcs` response to work without workbook.
- **StaticFiles mount conflict**: per risk gate §8.3, mount placed at END of server.py (after all route decorators). Routes defined first win over mounts in Starlette routing order. Test `test_runs_staticfiles_path_traversal_blocked` confirms 404 for `..` traversal.
- **bug code field**: brief's §6 test spec used `bugs[0]["item_code"]` but bug dict has `"code"` key — corrected in implementation.

### 7. Open questions for Brief #003 (UI)

- Steps accordion: whether to expand inline or slide a right-panel drawer; inline avoids z-index issues on mobile.
- Evidence modal: keyboard navigation (`Esc` / arrow keys) at v0.1.5 or defer to v0.1.6?
- `steps_count` badge in TC card: colour-code by count (e.g., >10 steps = amber) or plain number?
