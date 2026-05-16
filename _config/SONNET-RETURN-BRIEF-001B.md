# SONNET-RETURN-BRIEF-001B — Patcher data migration (Brief #001b)

**Branch:** `cp-supin-09-v0.4.4-data-migration`
**Commit:** `ce16502`
**Date:** 2026-05-15
**Status:** COMPLETE

---

## §10 Return checklist

### 1. Branch + commit

- Branch: `cp-supin-09-v0.4.4-data-migration`
- Commit: `ce16502`

### 2. Files changed

| File | Change | Lines |
|------|--------|-------|
| `tools/workbook-v0.4.3-to-v0.4.4.py` | Created (from patcher branch + extensions) | 1,055 |
| `tools/tests/test_workbook_patcher.py` | Created (from patcher branch + 10+ new tests) | 712 |
| `tools/tests/conftest.py` | Created (from patcher branch) | 36 |
| `tools/tests/fixtures/make_synthetic_fixture.py` | Created (from patcher branch) | 215 |
| `tools/tests/fixtures/make_synthetic_user_data_fixture.py` | Created (new) | 148 |
| `tools/tests/fixtures/synthetic-v0.4.3-mini.xlsx` | Created (binary fixture) | — |
| `tools/tests/fixtures/synthetic-v0.4.3-with-user-data.xlsx` | Created (binary fixture) | — |
| `CHANGELOG.md` | v0.5.7 entry added | +28 |

### 3. Test results — `pytest tools/tests/ -v -m "not integration"`

```
23 passed, 2 deselected, 2 warnings in 5.30s
```

All 13 original Brief #001 tests + 10 new Brief #001b tests pass.

### 4. Kate scenario §9 (data migration summary)

```
## §9 Data migration summary

Source-data: `tools/tests/fixtures/synthetic-v0.4.3-with-user-data.xlsx`

| Sheet | Rows migrated | Schema rows replaced |
|-------|---------------|----------------------|
| `08_Bugs` | 5 | 2 |
| `06_TestRuns` | 3 | 0 |
| `07_TestRunResults` | 5 | 0 |
| `09_Reports` | 1 | 0 |
| `13_TestExecutionSummary` | 1 | 0 |
| `14_AssertionGateResults` | 2 | 0 |
```

08_Bugs: 2 schema rows (BUG-SYN-001, BUG-SYN-002) replaced by 5 Kate rows.
Other data sheets were stubs → 0 schema rows replaced; 3/5/1/1/2 user rows appended.

### 5. Idempotency proof

`test_data_source_omitted_then_provided_then_omitted_resets` and
`test_kate_realistic_scenario` (integration) both run the patcher twice and
verify identical row counts. Byte-level identity not tested (changelog timestamps
differ on each run, as per brief §6).

### 6. Out-of-scope findings

- `tools/tests/fixtures/make_synthetic_fixture.py` (the mini fixture generator)
  was not previously tracked in `main` — it lived only on `cp-supin-07-v0.1.5-patcher`.
  This brief promotes it to tracked.
- Stub-sheet schema adoption (new behavior): when a dest sheet has no real column
  layout (just `["(stub)"]`), the patcher adopts source-data's column schema.
  This is not explicitly specified in the brief but is required for 06_TestRuns /
  07_TestRunResults to work when schema-source has stub sheets.

### 7. Deviations from spec

1. **`07_TestRunResults` / `09_Reports` / `13_TES` / `14_AGR` — no explicit PK dup-check.**
   Brief only requires dup-check for `08_Bugs` (item_code) and `06_TestRuns` (run_id).
   The other sheets have `pk_col=None` in `DATA_MIGRATION_SHEETS` and are not validated.
   Consistent with brief §9 risk gates 2 and 6 (no others).

2. **Stub-sheet adoption not explicitly specified.**
   Brief §F-3m through §F-5m says "same pattern" as §F-2m. But `06_TestRuns` is a
   stub in the mini fixture (only `["(stub)"]` header), so header-mapped migration
   cannot work without first replacing the stub header. The implementation detects
   stub sheets via `_is_stub_sheet()` and adopts source-data's schema. This matches
   the spirit of "preserve verbatim" from §F-5m.

3. **Second `11_Changelog` row uses version `v0.4.4-data` (not `v0.4.4`).**
   Brief §3 says "two rows: one for schema patch, one for data migration." Using
   `v0.4.4-data` to distinguish the two entries from the same patching run.

### 8. Open questions for next step

1. Kate's actual workbook: once she sends the real file, Pete should run:
   ```
   python tools/workbook-v0.4.3-to-v0.4.4.py \
     --source BOURACKA-TESTPLAN-v0.4.3.xlsx \
     --dest BOURACKA-TESTPLAN-v0.4.4.xlsx \
     --source-data /path/to/kate-working-copy.xlsx \
     -v
   ```
   Verify §9 of PATCH-REPORT shows expected row counts before accepting.

2. Kate's workbook may have `evidence_*` columns already populated (risk gate 7).
   The patcher handles this (§F-2m: typed columns only filled from legacy if empty),
   but Pete should review the PATCH-REPORT §10 to verify.

3. If Kate's workbook has bugs from the canonical mini fixture (BUG-SYN-001 etc.),
   those will be "replaced" collisions (§11). This is expected behavior.
