# Sonnet brief — BRIEF-001b: patcher row-level data migration

**Target Claude.** Sonnet 4.6 in Claude Code (terminal, stateless).
**Issued by.** Opus 4.7 session (Pete Y. + Claude), 2026-05-14.
**Branch.** `cp-supin-09-v0.4.4-data-migration` (create from `main` head).
**Estimated effort.** ~3–4 hours of Sonnet time.
**Reviewer.** Pete in Opus 4.7 session, after Sonnet returns the checklist in §10.
**Blocked by.** Brief #001 already merged (workbook-v0.4.3-to-v0.4.4.py exists, schema-patches v0.4.4).

---

## 1. Goal in one paragraph

Kate filed bugs and ran tests in her local workbook (v0.4.3). When she upgraded to v0.4.4, those user-entered rows did not carry over — the schema-only patcher created new sheets and columns but never migrated user data. Kate's rule from 2026-05-14: **"intentional deletion is OK, version-transition data loss is NOT OK."** This brief asks you to extend `tools/workbook-v0.4.3-to-v0.4.4.py` with row-level migration: given a separate "source data workbook" (Kate's working copy with her bugs / runs / results), copy every user-entered row into the freshly-patched dest workbook, preserving codes, timestamps, and assertion history. Schema reference still comes from the canonical repo-side v0.4.3 source; user data comes from the tester's copy.

---

## 2. Spec — read this BEFORE coding

Open and read in full:

1. `_config/BOURACKA-UI-V0.1.5-DESIGN-NOTES-EN.md` — §3 (Test-Step entity) and §4a (evidence columns)
2. `_config/SONNET-BRIEF-001-WORKBOOK-PATCHER-V0.4.3-TO-V0.4.4.md` — the parent brief; this one EXTENDS it, does not replace
3. `tools/workbook-v0.4.3-to-v0.4.4.py` — your starting point
4. `tools/tests/test_workbook_patcher.py` — current test suite; you'll add to it
5. `BOURACKA-TESTPLAN-v0.4.4.xlsx` (repo root) — current patcher output, no user data
6. A sample input workbook with user data — you'll generate one programmatically (see §3)

If spec and this brief disagree, the **spec wins** unless this brief explicitly overrides. The Sonnet Brief #001 §F-1 to §F-6 patcher contract still applies; this brief adds §F-1m to §F-7m on top.

---

## 3. Inputs / outputs

### Inputs

- **Schema-source workbook**: `BOURACKA-TESTPLAN-v0.4.3.xlsx` (repo root) — the canonical pre-patch reference. Used to derive new sheet/column layout. Same as Brief #001.
- **NEW: Data-source workbook**: the tester's working copy with their entered bugs/runs/results. Passed via `--source-data PATH`. Default: same as schema-source (i.e., no data migration if flag omitted — preserves Brief #001 behavior).
- Dest workbook: `BOURACKA-TESTPLAN-v0.4.4.xlsx` (repo root) — produced by patcher.

### Outputs

1. `BOURACKA-TESTPLAN-v0.4.4.xlsx` (repo root) — patched + data-migrated.
2. `tools/patcher-reports/PATCH-REPORT-v0.4.3-to-v0.4.4-<YYYYMMDD-HHMMSS>.md` — extended report covering both schema patches AND data migration.
3. Updated `11_Changelog` sheet with TWO rows: one for the schema patch (existing), one for the data migration (new).

---

## 4. File boundaries — what you may touch

### Create

- `tools/tests/fixtures/synthetic-v0.4.3-with-user-data.xlsx` — synthetic fixture with bugs/runs/results filled in (~5 bugs, ~3 runs, ~5 run results); generate programmatically.

### Modify

- `tools/workbook-v0.4.3-to-v0.4.4.py` — add `--source-data` CLI flag + new migration phase. Existing F-1 to F-6 behavior MUST remain unchanged when `--source-data` is omitted.
- `tools/tests/test_workbook_patcher.py` — add 10+ new tests covering migration scenarios.

### DO NOT touch

- `bouracka_ui/` — server code; out of scope.
- `BOURACKA-TESTPLAN-v0.4.3.xlsx` — read-only canonical reference.
- `_config/` — specs.
- `delivery/` — shipped artefacts.

---

## 5. Functional requirements (extending Brief #001 §F-1..§F-6)

### F-1m. CLI: `--source-data PATH` flag

Default: omitted → behavior identical to Brief #001 (schema patch only, no data migration). When provided, must point at an .xlsx file that the patcher will read user data from.

Schema source remains `--source` (or auto-detect).

### F-2m. Migrate `08_Bugs` rows

For every row in source-data's `08_Bugs` sheet where `item_code` is non-empty:

- Read the row.
- Map the row's columns to the v0.4.4 schema (new columns from F-4 of Brief #001 get empty defaults; existing columns map by header name, NOT by index).
- Append to dest's `08_Bugs` sheet.
- If a row with matching `item_code` already exists in dest, **prefer the source-data row** (overwrite dest's empty row that came from schema-source). Report this in PATCH-REPORT under "Bug rows replaced by user data".

**Legacy column migration** (per Brief #001 §F-4):

- `screenshot_ref` non-empty → also write to `evidence_screenshot_path`, set `evidence_capture_kind = "manual-tester"`.
- `trace_ref` non-empty → also write to `evidence_trace_path`, set `evidence_capture_kind = "manual-tester"`.

### F-3m. Migrate `06_TestRuns` rows

Same pattern as F-2m for `06_TestRuns`. Preserve `run_id`, `run_timestamp`, `triggered_by`, `framework_targets`, `env`, all status fields. New columns get empty defaults.

If source-data has duplicate `run_id` values → halt with §9 risk gate 6.

### F-4m. Migrate `07_TestRunResults` rows

Same pattern. Preserve all assertion history, exit codes, durations. Critical for audit.

### F-5m. Migrate `09_Reports` + `13_TestExecutionSummary` + `14_AssertionGateResults`

Same pattern. These are aggregation sheets but may contain manual annotations. Preserve verbatim.

### F-6m. Do NOT migrate `02_TestCases`, `02e_TestSteps`, `02d_AssertionLibrary`, `00_README`, `10_Glossary`, `11_Changelog`

These are schema/canonical sheets owned by the repo. Source-data's versions are ignored (could be older/stale). Dest gets schema-source content for these.

### F-7m. PATCH-REPORT extension

Add new sections:

- §9: Data migration summary (counts by sheet)
- §10: Bug rows with legacy `screenshot_ref` / `trace_ref` migrated to typed evidence columns
- §11: Row-code collisions (source-data row replaced dest schema-source row) — should always be the case for migrated rows; report it
- §12: Sheets explicitly NOT migrated and why (§F-6m list)

---

## 6. Idempotency requirements

- Running patcher twice with the same `--source-data` produces byte-identical dest workbook (except for changelog audit-trail rows + report timestamps).
- Running patcher with `--source-data X` then again with `--source-data Y` (different data sources): dest gets Y's data overwriting X's. Document this as the expected behavior; it's not a merge.
- Running with `--source-data` omitted after a prior run with `--source-data` set: dest data is **wiped back to schema-only**. This is the "reset" path. Document clearly.

---

## 7. CLI surface (updated)

```
python tools/workbook-v0.4.3-to-v0.4.4.py
    [--source PATH]              schema source (default: BOURACKA-TESTPLAN-v0.4.3.xlsx)
    [--dest PATH]                output (default: BOURACKA-TESTPLAN-v0.4.4.xlsx)
    [--source-data PATH]         NEW: tester's workbook with user data to migrate
    [--dry-run]                  analysis only, no write
    [--report-only]              re-emit report from existing dest
    [-v]                         verbose

Exit codes:
  0 — success (no warnings)
  1 — success with warnings (orphans, KP-review flags, row-code collisions normal in migration)
  2 — input validation failure (source / source-data missing or malformed)
  3 — output write failure
  4 — NEW: data migration integrity failure (duplicate run_ids, schema mismatch)
```

---

## 8. Test plan additions to `tools/tests/test_workbook_patcher.py`

```python
def test_source_data_flag_default_off()
    # patcher run WITHOUT --source-data behaves identically to Brief #001
    # (data sheets in dest = empty, schema patches present)

def test_migrate_08_bugs_basic()
    # synthetic source-data has 3 bug rows; dest has 0 → after migration, dest has 3

def test_migrate_screenshot_ref_to_evidence_typed()
    # source-data bug with screenshot_ref="runs/x.png" →
    # dest row has evidence_screenshot_path="runs/x.png", evidence_capture_kind="manual-tester",
    # ALSO retains legacy screenshot_ref column (soft-deprecation, per Brief #001 §F-4)

def test_migrate_06_test_runs_preserves_all_columns()
    # every column value in source-data run row appears in dest row, in the new column layout

def test_migrate_07_test_run_results_preserves_assertion_history()

def test_duplicate_run_id_in_source_data_halts()
    # source-data has 2 rows with same run_id → patcher halts with exit 4

def test_data_source_omitted_then_provided_then_omitted_resets()
    # demonstrate the "reset" idempotency rule

def test_schema_sheets_NOT_overwritten_by_source_data()
    # source-data has different 02_TestCases content → dest 02_TestCases comes from schema-source

def test_migrate_with_no_data_in_source_is_noop()
    # source-data has 0 user rows → patcher succeeds, dest has 0 user rows, no PATCH-REPORT warnings

def test_report_section_9_through_12_present()
    # PATCH-REPORT contains the 4 new sections when --source-data used

@pytest.mark.integration
def test_kate_realistic_scenario()
    # Synthetic "Kate" workbook with 5 bugs + 3 runs + 8 results →
    # patched dest has all migrated + schema in place + idempotent on re-run
```

---

## 9. Risk gates — STOP and report if you hit any

1. **Source-data workbook has columns we don't recognize** (i.e., schema-source has a column the source-data lacks, or vice versa). Halt with detailed column-diff report.
2. **Duplicate primary keys in source-data** (duplicate `item_code` in 08_Bugs or duplicate `run_id` in 06_TestRuns). Halt; require user to deduplicate.
3. **Source-data has a row referencing `linked_step_ref = STP-X-NN` where that step_code does NOT exist in dest's 02e_TestSteps.** This is an orphan. Migrate the row but flag in PATCH-REPORT.
4. **Source-data has bug count > 1000 rows or run count > 500.** Probably wrong input. Halt and ask Pete.
5. **`--source-data` and `--source` point to the same file.** That's a no-op data migration but signals user confusion. Warn but proceed.
6. **Duplicate run_id in source-data** (per F-3m). Halt.
7. **`evidence_*` columns in source-data already populated (not just legacy `screenshot_ref`).** This means source-data was already in v0.4.4 schema. Migration should still work (header-based mapping), but log it.

---

## 10. Return checklist

1. Branch name + commit SHA(s) you created.
2. Files changed (created / modified) with line counts.
3. Test results — `pytest tools/tests/ -v` full pass list.
4. Synthetic Kate scenario integration test output — paste the PATCH-REPORT §9 (data migration summary block) verbatim.
5. Idempotency proof — two re-runs against same source-data produce byte-identical workbooks (except changelog + timestamps).
6. Out-of-scope findings.
7. Deviations from this brief with one-sentence justifications.
8. Open questions for the NEXT step in the chain — likely Pete's manual run against Kate's actual workbook (if/when she sends it).

---

## 11. Don't-go-beyond markers

- **Do not modify `bouracka_ui/`** — completely out of scope.
- **Do not modify the schema patches from Brief #001** (F-1 through F-6) — extension only, not replacement.
- **Do not add support for v0.4.4 → v0.4.5 migration** — that's a future patcher version.
- **Do not auto-fetch Kate's actual workbook** — synthetic fixtures only. Pete will run against real data after review.
- **Do not "improve" the changelog row format** — match the existing pattern from Brief #001.

---

## 12. Quick-reference: spec sections by file/line

| Brief item | Spec ref |
|------------|----------|
| §F-2m bug migration + screenshot_ref → typed | Brief #001 §F-4 + DESIGN §4a.3 |
| §F-3m run preservation | brief decision (Kate's discipline 2026-05-14) |
| §F-6m schema-vs-data separation | brief decision (schema owned by repo, data owned by tester) |
| §6 reset semantics | brief decision (no merge-mode) |
| Risk gates 1, 2, 6 | brief decision (data integrity primacy) |

---

## 13. Acceptance — when is this brief "done"?

- All new tests in §8 pass.
- Integration test against synthetic-with-user-data fixture produces correctly-migrated v0.4.4.
- Manual run against repo's v0.4.3 with `--source-data` pointed at any tester workbook produces verifiable migration.
- Branch has clean commits with conventional messages.
- Return checklist §10 pasted to Pete.

After Pete reviews, the next downstream work is Pete running this against Kate's actual workbook (once she sends it back) to restore her BUG-002 and any other bugs into the v0.4.4 schema. Sonnet does NOT touch real customer data; Pete operates that step manually under Opus oversight.

---

**End of BRIEF-001b.**
