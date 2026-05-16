# Sonnet brief — BRIEF-001: workbook patcher v0.4.3 → v0.4.4

**Target Claude.** Sonnet 4.6 in Claude Code (terminal, stateless).
**Issued by.** Opus 4.7 session (Pete Y. + Claude), 2026-05-13.
**Branch.** `cp-supin-07-v0.1.5-patcher` (create from current `main` head).
**Estimated effort.** ~2–3 hours of Sonnet time.
**Reviewer.** Pete in Opus 4.7 session, after Sonnet returns the checklist in §10.

---

## 1. Goal in one paragraph

Bouračka v0.1.4 workbook `BOURACKA-TESTPLAN-v0.4.3.xlsx` has a latent schema debt: `02c_TC_Assertions.step_id` is a foreign key with no target table, and `08_Bugs` lacks step-level + visual-evidence linkage. The v0.1.5 design promotes **Test-Step** to a first-class entity (new sheet `02e_TestSteps`) and adds typed evidence columns to `08_Bugs`. This brief asks you to write a one-shot, idempotent patcher script `tools/workbook-v0.4.3-to-v0.4.4.py` that performs the schema upgrade in place on a copy of the workbook, plus a smoke-test suite that proves the patcher does what it claims and doesn't break readers.

---

## 2. Spec — read this BEFORE coding

Open and read these sections **in full** (they are the contract):

1. `_config/BOURACKA-UI-V0.1.5-DESIGN-NOTES-EN.md` §2 (schema debt inventory)
2. `_config/BOURACKA-UI-V0.1.5-DESIGN-NOTES-EN.md` §3 (Test-Step entity schema + re-wires)
3. `_config/BOURACKA-UI-V0.1.5-DESIGN-NOTES-EN.md` §4a.3 (08_Bugs evidence columns)
4. `_config/BOURACKA-UI-V0.1.5-DESIGN-NOTES-EN.md` §8 (open questions Q-V015-1..8 — your defaults are listed there)

When the spec and this brief disagree, the **spec wins** unless this brief explicitly overrides. Anywhere the spec says "TBD by KP", apply the default listed there and emit a marker (see §6 below).

---

## 3. Inputs / outputs

### Inputs

- Source workbook: `BOURACKA-TESTPLAN-v0.4.3.xlsx` (repo root). DO NOT modify in place.
- Sheets that exist today (do not recreate): `00_README`, `00b_Requirements`, `00c_VersionSanityRules`, `01_TestTargets`, `00e_BranchView`, `01b_Req_FURPS_Cartesian`, `01c_StateMachine`, `02_TestCases`, `02b_TC_Parameters`, `02c_TC_Assertions`, `02d_AssertionLibrary`, `03_TestData`, `05a_TestPlan`, `05b_TestSchedule`, `05c_TestEstimate`, `04_TestEnvironments`, `05_TestSets_DEPRECATED`, `06_TestRuns`, `07_TestRunResults`, `13_TestExecutionSummary`, `14_AssertionGateResults`, `08_Bugs`, `09_Reports`, `10_Glossary`, `11_Changelog`, `01d_PrioritySevUrgMatrix`.

### Outputs

1. `BOURACKA-TESTPLAN-v0.4.4.xlsx` (repo root) — the patched workbook.
2. `tools/patcher-reports/PATCH-REPORT-v0.4.3-to-v0.4.4-<YYYYMMDD-HHMMSS>.md` — human-readable summary of what changed, what was flagged, what needs KP review.
3. Updated `11_Changelog` sheet in the new workbook with a row noting the patch event.

---

## 4. File boundaries — what you may touch

### Create

- `tools/workbook-v0.4.3-to-v0.4.4.py` — the patcher.
- `tools/tests/test_workbook_patcher.py` — pytest module.
- `tools/tests/fixtures/synthetic-v0.4.3-mini.xlsx` — a tiny synthetic workbook (3 TCs, 2 bugs, no protected sheets) for fast deterministic testing. **Generate this fixture programmatically** in a helper script so we can regenerate it; don't hand-author the binary XLSX.
- `tools/tests/conftest.py` — pytest fixtures.
- `tools/patcher-reports/.gitkeep` — empty file so the dir exists.

### Modify

- `tools/README.md` — append a section "## workbook-v0.4.3-to-v0.4.4.py" describing usage.
- `.gitignore` — add `tools/patcher-reports/PATCH-REPORT-*.md` (the dated reports are run artefacts, not source).

### DO NOT touch

- `bouracka_ui/` — anything under here is server code and out of scope for this brief.
- `BOURACKA-TESTPLAN-v0.4.3.xlsx` — source workbook is read-only.
- `_config/` — the design docs are the spec; you read them, you don't edit them.
- `delivery/` — these are shipped artefacts; out of scope.
- `recon/` — recon docs are out of scope.

If you find a bug in `bouracka_ui/workbook_io.py` while researching the schema, **do not fix it** — file it back to Pete in your return checklist (§10 item 6).

---

## 5. Functional requirements

### F-1. New sheet `02e_TestSteps`

Create with this exact column order (header row 1):

```
id | step_code | tc_ref | ordinal | action_cs | action_en
   | expected_cs | expected_en | framework_hint | assertion_lib_ref
   | is_decision_point | comments_KP_en | created_at | updated_at | notes
```

Populate by walking each row in `02_TestCases` and splitting `steps_summary` (col T/19) by newline (`\r\n`, `\n`, or `\r`). Each non-empty line becomes one step row:

- `id` = autoincrement starting at 1
- `step_code` = `STP-<tc_code>-<NN>` where NN is the 2-digit ordinal (Q-V015-1 default; `01`, `02`, ...)
- `tc_ref` = the TC's `item_code` (col B/1)
- `ordinal` = the 1-based line index within that TC
- `action_cs` = the raw line, stripped of leading/trailing whitespace
- `action_en` = empty (KP will translate)
- `expected_cs` / `expected_en` = empty (KP will fill or harvest from `expected_summary`)
- `framework_hint` = empty (means "all", per BUG-K-001 tolerance rule)
- `assertion_lib_ref` = empty
- `is_decision_point` = `FALSE`
- `comments_KP_en` = `(machine-split — KP review needed)` for steps split from multi-line `steps_summary`; empty when `steps_summary` was a single line or already structured
- `created_at` = patcher run timestamp
- `updated_at` = same as `created_at`
- `notes` = `(generated by workbook-v0.4.3-to-v0.4.4.py)`

**Edge case — TC has empty steps_summary.** Emit a single placeholder step row with `action_cs = "(no steps_summary in source workbook)"` and `comments_KP_en = "(KP: define steps for this TC)"`.

**Edge case — TC has steps_summary that is itself empty after split (all-whitespace lines).** Same as above placeholder.

**Edge case — `steps_summary` has many lines (>20).** Emit them all; flag the TC in the PATCH-REPORT under "TCs with >20 steps (review needed)".

### F-2. Update `02_TestCases`

Add a new column to the right: `steps_count` (Integer). Set per TC to the number of rows generated in `02e_TestSteps` with `tc_ref = <tc_code>`. **Do not delete `steps_summary`** — keep it as denormalized preview per design §3.2; future writes will update it from `02e` at workbook-save time (out of scope for this brief).

### F-3. Update `02c_TC_Assertions`

For each row where `step_id` is **non-empty**, verify that the value matches an existing `step_code` in `02e_TestSteps`. Maintain a list of orphans and report them in the PATCH-REPORT under "Orphan references — `02c_TC_Assertions.step_id` not found in 02e".

**Do NOT modify the orphan rows.** Just report. KP decides whether to relink, delete, or backfill.

If `step_id` is empty in 02c (most rows), leave it empty — those are TC-scoped assertions, not step-scoped.

### F-4. Update `08_Bugs` — add columns

Append the following columns to the right (preserve existing column order so existing readers don't break):

| New column name | Type | Default for existing rows |
|-----------------|------|---------------------------|
| `linked_step_ref` | string | empty (TC-level bug, no step ref) |
| `evidence_screenshot_path` | string | migrate from `screenshot_ref` (col 36) if non-empty, else empty |
| `evidence_video_path` | string | empty |
| `evidence_trace_path` | string | migrate from `trace_ref` (col 37) if non-empty, else empty |
| `evidence_capture_kind` | enum string | `manual-tester` if `screenshot_ref` or `trace_ref` was non-empty, else `none` |
| `evidence_capture_at` | datetime | empty |

**Do NOT delete `screenshot_ref` or `trace_ref`** in this patcher pass — readers expecting them must continue to work until v0.1.5 ships. They become "soft-deprecated" — document this in the PATCH-REPORT.

**Do NOT modify `tc_ref` (col 28) or `linked_tc_ref` (col 14)** — the deprecation rewire happens in a later patcher (v0.4.4 → v0.4.5), not this one.

### F-5. Append `11_Changelog` row

Append one row with:

- `date` = patcher run timestamp
- `version` = `v0.4.4`
- `change_type` = `schema-patch`
- `summary` = `Added 02e_TestSteps; added evidence columns to 08_Bugs; added steps_count to 02_TestCases; soft-deprecated screenshot_ref + trace_ref in 08_Bugs.`
- `author` = `workbook-v0.4.3-to-v0.4.4.py`

Match the existing `11_Changelog` column order — read row 1 to discover it.

### F-6. Generate PATCH-REPORT-*.md

Write to `tools/patcher-reports/PATCH-REPORT-v0.4.3-to-v0.4.4-<YYYYMMDD-HHMMSS>.md` with sections:

- §1 Summary (counts: TCs scanned, steps generated, bugs migrated, orphans found, KP-review flags)
- §2 TCs needing KP step-cleanup (TCs with `comments_KP_en` markers in their generated step rows)
- §3 TCs with >20 steps (cap-exceeded)
- §4 TCs with empty `steps_summary` (placeholder rows generated)
- §5 Orphan `02c_TC_Assertions.step_id` values (with row numbers)
- §6 Bugs migrated from legacy `screenshot_ref` / `trace_ref` to evidence_* columns
- §7 Idempotency stamp: SHA256 of the v0.4.3 source + SHA256 of the v0.4.4 output
- §8 What was NOT done (deprecation rewires, KP translations, etc.)

---

## 6. Idempotency requirements

The patcher **must** be safe to re-run on a workbook that has already been patched.

- If `02e_TestSteps` already exists, do **not** recreate it. Instead, verify that the existing rows match what a fresh run would produce (by `step_code`). Report mismatches in PATCH-REPORT §1 under "Idempotency drift" — do not auto-overwrite.
- If `steps_count` column already exists in `02_TestCases`, recompute and overwrite values (safe — derived data).
- If `08_Bugs` already has `linked_step_ref` etc. columns, do not append duplicates. Recompute migration values only for rows where the typed columns are empty AND the legacy `screenshot_ref`/`trace_ref` are non-empty.
- The `11_Changelog` should get **one new row per patcher run** (re-runs append; this is intentional audit trail).

Test for idempotency: running the patcher twice in a row on the same v0.4.3 input must produce the same v0.4.4 (except for the changelog row count and the report timestamps). The smoke test §8 enforces this.

---

## 7. CLI surface

```
python tools/workbook-v0.4.3-to-v0.4.4.py [--source PATH] [--dest PATH]
                                          [--dry-run] [--report-only] [-v]

  --source     Path to source workbook. Default: BOURACKA-TESTPLAN-v0.4.3.xlsx in repo root.
  --dest       Path to dest workbook.   Default: BOURACKA-TESTPLAN-v0.4.4.xlsx in repo root.
  --dry-run    Run the analysis but don't write the dest workbook. Still writes the PATCH-REPORT.
  --report-only  Re-emit only the PATCH-REPORT from the existing dest (no schema work). Useful for
                 regenerating a report from a v0.4.4 already on disk.
  -v / --verbose  Print per-TC progress to stderr.

Exit codes:
  0 — success (no orphans, no >20-step warnings)
  1 — success with warnings (orphans or >20-step or KP-review markers present)
  2 — input validation failure (source missing, malformed)
  3 — output write failure (permission, disk)
```

Pete will run with `--dry-run` first to inspect the PATCH-REPORT before letting the patcher write.

---

## 8. Test plan — `tools/tests/test_workbook_patcher.py`

Write **at least these tests** (add more if you find gaps):

1. `test_02e_TestSteps_created_with_expected_columns()` — sheet exists, column order matches §F-1.
2. `test_each_TC_gets_at_least_one_step_row()` — count `02e_TestSteps` rows per `tc_ref`; assert ≥ 1 for every `02_TestCases.item_code`.
3. `test_step_code_format_STP_dash_TC_dash_NN()` — regex `^STP-.+-\d{2}$` on every step_code.
4. `test_ordinals_are_gapless_per_tc()` — for each TC, ordinals are `1..N` with no holes.
5. `test_steps_count_column_matches_02e_row_count()` — `02_TestCases.steps_count` agrees with `len(02e WHERE tc_ref=...)`.
6. `test_08_bugs_has_new_columns()` — `linked_step_ref`, `evidence_screenshot_path`, `evidence_video_path`, `evidence_trace_path`, `evidence_capture_kind`, `evidence_capture_at` all present.
7. `test_legacy_screenshot_ref_migrated()` — for bug rows with non-empty `screenshot_ref` in v0.4.3, the v0.4.4 row has matching `evidence_screenshot_path` AND `evidence_capture_kind = 'manual-tester'`.
8. `test_legacy_screenshot_ref_preserved()` — the v0.4.4 still contains `screenshot_ref` and `trace_ref` columns with their original values (soft-deprecation).
9. `test_changelog_row_appended()` — new row with `version = 'v0.4.4'` and `change_type = 'schema-patch'`.
10. `test_idempotent_when_run_twice()` — patch a synthetic workbook, then patch the OUTPUT again; second output's `02e_TestSteps`, `steps_count`, and bug evidence columns are byte-identical to first output's (except changelog row count + run timestamps).
11. `test_dry_run_does_not_write_dest()` — `--dry-run` produces report but no `--dest` file on disk.
12. `test_orphan_02c_step_id_reported_not_modified()` — inject a synthetic orphan; assert it appears in PATCH-REPORT §5 AND the `02c_TC_Assertions` row in the dest is byte-identical to source.
13. `test_empty_steps_summary_produces_placeholder()` — synthetic TC with empty `steps_summary` gets one placeholder step with `(KP: define steps...)` marker.

**Use the synthetic fixture from `tools/tests/fixtures/synthetic-v0.4.3-mini.xlsx`**, not the real v0.4.3 workbook — tests must be fast (<5 s total) and deterministic.

Also include **one slow integration test** marked `@pytest.mark.integration` that patches the real `BOURACKA-TESTPLAN-v0.4.3.xlsx` and asserts:
- 24 TCs → at least 24 step rows in 02e (one per TC)
- 4 Priority-A TCs cited in `_config/BOURACKA-P0-SMOKE-TC-RANKING-v0.1-EN.md` §3 ranks 1–4 (`TC-CP-008`, `TC-CP-015`, `TC-CP-019`, `TC-CP-013`) each have step rows generated
- No idempotency drift on second run

Skip the integration test by default (`pytest -m "not integration"`); Pete runs it manually before commit.

---

## 9. Risk gates — STOP and report back to Pete if you hit any of these

1. **Schema-spec ambiguity.** If reading the v0.1.5 design notes leaves a column type, default, or behaviour genuinely undefined (not "TBD by KP" — those have defaults you apply), stop and ask. Do not invent.
2. **More than 30% of TCs end up flagged for KP step-cleanup.** That suggests the splitting heuristic is wrong for this workbook's style; stop and discuss with Pete.
3. **Orphan rate in `02c_TC_Assertions.step_id` exceeds 5 rows.** That suggests the FK convention is different from `STP-<tc>-NN` and our default is wrong.
4. **openpyxl raises an error reading the real workbook.** Some sheets may have merged cells, frozen panes, or charts that the read_only mode doesn't tolerate; raise the actual error to Pete with the sheet name.
5. **Synthetic fixture generator can't reproduce the real workbook's column layout for `08_Bugs`** (which has 39 columns including some that look legacy-duplicated like `linked_tc_ref` and `tc_ref`). Confirm the fixture mirrors the real layout before relying on the tests.

Any of these → halt, write what you have to a WIP branch, return the checklist in §10 marked as "BLOCKED — see item N".

---

## 10. Return checklist — paste this back to Pete when done

Pete needs the following at handoff time:

1. **Branch name + commit SHA(s)** you created.
2. **Files changed** — list (created / modified / deleted) with line counts.
3. **Test results** — `pytest tools/tests/ -v` output, plus the integration test result run manually.
4. **PATCH-REPORT excerpt** — paste the §1 Summary block from a real run against the v0.4.3 workbook.
5. **Idempotency proof** — sha256 of the first v0.4.4 output AND the second v0.4.4 output from running the patcher twice (should match except for changelog row count).
6. **Any bugs / surprises found that are OUT OF SCOPE for this brief.** Bouračka-ui code that looks wrong, schema oddities you noticed but didn't fix, design-doc gaps. Don't fix them — list them.
7. **Deviations from this brief** — anywhere you did something different than spec, with one-sentence justification each.
8. **Open questions** for Pete to decide before next Sonnet brief (likely the implementation of `bouracka_ui/workbook_io.py::list_steps()`).

---

## 11. Don't-go-beyond markers

- **Do not implement `bouracka_ui/workbook_io.py::list_steps()`** even though the spec mentions it. That's the next brief.
- **Do not add API endpoints** even if you read about them in §4.2 / §4a.5. Out of scope.
- **Do not modify the UI** (`bouracka_ui/static/`). Out of scope.
- **Do not bump `bouracka_ui/__init__.py` version.** That happens in the v0.1.5 wheel build brief, later.
- **Do not implement the dispatcher artefact-copy logic** (FR-K-004). Out of scope.
- **Do not "improve" the design notes** if you spot something. Note it in checklist item 6 instead.

The point of this brief is to deliver the **workbook schema migration** as one unblocking, reviewable, mergeable piece. Everything downstream (UI, server, dispatcher) builds on top of v0.4.4 once it's stable. Keep this PR small.

---

## 12. Quick-reference: spec sections by file/line

If you want to verify any decision in this brief against the source spec:

| Brief item | Spec ref |
|------------|----------|
| §F-1 column list | DESIGN-NOTES §3.1 table |
| §F-1 step_code format | DESIGN-NOTES §3.1 + Q-V015-1 default (§8) |
| §F-1 placeholder for empty steps_summary | DESIGN-NOTES §8 Q-V015-5 default |
| §F-3 do-not-modify orphans | DESIGN-NOTES §3.2 "Validate referential integrity on workbook load" |
| §F-4 evidence column list | DESIGN-NOTES §4a.3 table |
| §F-4 soft-deprecation of `screenshot_ref` / `trace_ref` | DESIGN-NOTES §4a.3 last paragraph |
| §6 idempotency | not explicitly in spec; brief decision (operationally critical) |
| §7 CLI surface | brief decision (consistent with `package-hp-elite-v0.1.0.ps1` style) |
| §11 don't-go-beyond | this brief defines scope; spec is broader |

---

## 13. Acceptance — when is this brief "done"?

Done = all of the following are true:

- `tools/workbook-v0.4.3-to-v0.4.4.py` exists and is invocable per §7.
- `pytest tools/tests/ -v -m "not integration"` reports all passing.
- Manual integration run against real `BOURACKA-TESTPLAN-v0.4.3.xlsx` produces `BOURACKA-TESTPLAN-v0.4.4.xlsx` with at least 24 step rows and a valid PATCH-REPORT.
- Idempotency proof in §10 item 5 matches.
- Branch `cp-supin-07-v0.1.5-patcher` has clean commits with conventional messages (`feat:`, `test:`, `docs:`).
- Return checklist §10 pasted to Pete.

Then Pete reviews in Opus 4.7 session, points out anything that needs adjustment, and gives merge thumbs-up (or sends a revision brief).

---

**End of BRIEF-001. Welcome to the v0.1.5 build, Sonnet.**
