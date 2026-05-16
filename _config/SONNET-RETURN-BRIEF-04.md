# Sonnet return — Brief #004 hotfix bundle

**Branch.** `cp-supin-13-hotfix-bundle`
**Commit.** `29ef836`
**Tests.** 32/32 passed (smoke suite), 3.70s

---

## §10 Return checklist

### 1. Branch + SHAs
- Branch: `cp-supin-13-hotfix-bundle` from `main`
- Commit: `29ef836`

### 2. Files changed

| File | Change |
|------|--------|
| `bouracka_ui/bouracka_ui/dispatcher.py` | Added `UI_ENV_TO_CONSOLIDATOR_TIER` dict + `normalize_env_for_consolidator()` fn; replaced `"--env", env` with `"--env", normalize_env_for_consolidator(env)` in `cons_cmd` |
| `bouracka_ui/bouracka_ui/__init__.py` | `__version__ = "0.1.5-dev4"` |
| `bouracka_ui/pyproject.toml` | `version = "0.1.5.dev4"` |
| `bouracka_ui/tests/test_smoke.py` | Added 4 F-4 tests; bumped version assertion to `0.1.5-dev4`; updated `test_envs_returns_3_envs` to include `tst-demo` |
| `delivery/KATE-V0.1.4-REINSTALL-CS.md` | Added `§1.0 Předpoklady` table (Node.js + selenium) before existing §1 |
| `delivery/SUPIN-SERVER-INSTALL-FROM-ZERO-CS.md` | Added Node.js + selenium rows to existing §1 prereq table |
| `delivery/PETE-HP-ELITE-DROP-2026-05-13/PETE-V0.1.4-ALIGN-CS.md` | Same §1.0 prereq table as Kate runbook |
| `CHANGELOG.md` | Added `v0.1.5-dev4` entry |

### 3. Test results

```
32 passed in 3.70s
```

All 4 new F-4 tests pass; all 28 pre-existing smoke tests pass.

### 4. Consolidator `--env` verification

`test_dispatcher_real_mode_normalizes_env_in_consolidator` confirms: when `run_async` is called with `env="tst-demo"`, the captured `cons_cmd` contains `--env demo` (not `--env tst-demo`). The test monkeypatches `_run_subprocess` to capture all subprocess calls, then finds the consolidator invocation by path substring and asserts `argv[env_idx + 1] == "demo"`.

### 5. F-2 outcome (BUG-K-012)

**Outcome A.** `workbook_io.py` has no `append_test_run` function and `server.py`'s `/api/runs` POST handler writes nothing to the `06_TestRuns` sheet. Runs are persisted exclusively as `runs/cross-framework-*.json` envelope files. Kate's "TestRuns overwrite" observation is caused by the v0.4.3→v0.4.4 patcher not preserving operator-added rows — scope of Brief #001b. Documented in CHANGELOG.

### 6. Out-of-scope findings

- `test_envs_returns_3_envs` was already failing on main (pre-existing) because `tst-demo` is returned by `/api/envs` but was not in the test's expected set. Fixed opportunistically.
- `dispatcher.py` line 123: `base_url = ENV_TO_BASE_URL.get(env, "https://demo.bouracka.cz")` — the fallback URL is hardcoded `demo.bouracka.cz`. For unknown env labels this is misleading. Out of scope.

### 7. Deviations

None. All three F-items implemented exactly as specified.

### 8. Open questions

- Should `tst-demo` be added to `consolidate_results.py`'s `--env` accepted values (as a passthrough alias for `demo`)? Or is the dispatcher-side normalization sufficient long-term? Current approach is correct for now.
