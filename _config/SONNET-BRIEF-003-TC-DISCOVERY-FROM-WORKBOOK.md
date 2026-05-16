# Sonnet brief — BRIEF-003: TC discovery from workbook (Option A)

**Target Claude.** Sonnet 4.6 in Claude Code (terminal, stateless).
**Issued by.** Opus 4.7 session (Pete Y. + Claude), 2026-05-14.
**Branch.** `cp-supin-10-tc-discovery-from-workbook` (create from current `main` head).
**Estimated effort.** ~4–5 hours of Sonnet time across 4 sub-areas.
**Reviewer.** Pete in Opus 4.7 session, after Sonnet returns the checklist in §10.
**Blocked by.** Briefs #001 + #002 merged.

---

## 1. Goal in one paragraph

The bouracka-ui currently enumerates Test Cases by walking the cypress/playwright/selenium spec filesystem and presenting filesystem-derived labels (`TC-CP-A1-MAIN-DEMO`, `TC-CP-A2-ALT-1..10`) in the UI dropdown. Kate's workbook owns the authoritative TC list with codes `TC-CP-001..024 + TC-CP-NEW-*`. These two universes never met → Kate dispatched against codes that don't exist in `02_TestCases`, with no traceability back to her workbook-authored test plan. This brief asks you to make the workbook authoritative: bump the schema with three per-framework binding columns, switch the server's TC source from filesystem walk to workbook read, and surface unbound specs in `/api/about` as orphans. After this lands, Kate selects "TC-CP-008" in the dropdown and the dispatcher invokes whichever specs the workbook says implement TC-CP-008 across cypress / playwright / selenium.

---

## 2. Spec — read this BEFORE coding

Open and read in full:

1. `_config/TC-DISCOVERY-DESIGN-v0.1-EN.md` — the design contract. §3 Option A, §5 my reasoning, §6 question defaults, §7 implementation outline.
2. `_config/BOURACKA-UI-V0.1.5-DESIGN-NOTES-EN.md` — broader v0.1.5 context, FR-K-001/002/003/004 alignment.
3. `_config/SONNET-BRIEF-001-WORKBOOK-PATCHER-V0.4.3-TO-V0.4.4.md` — patcher pattern you'll mirror.
4. `bouracka_ui/bouracka_ui/dispatcher.py` — current spec-glob construction (the code that changes).
5. `bouracka_ui/bouracka_ui/workbook_io.py` — `list_tcs()` returns dict shape; you'll extend.
6. `bouracka_ui/bouracka_ui/server.py` — find the `/api/tcs` endpoint + `/api/runs` POST handler (dispatch entry).
7. `bouracka_ui/bouracka_ui/static/app.js` — TC selection dropdown rendering (you'll update).
8. `BOURACKA-TESTPLAN-v0.4.4.xlsx` `02_TestCases` sheet — current 39-column layout reference.

When this brief and the design doc disagree, this brief wins (it implements the design's chosen Option A).

---

## 3. Inputs / outputs

### Inputs

- Repo state with v0.4.4 workbook + bouracka-ui v0.1.4-multi-abi shipped.
- Decision: **Option A from TC-DISCOVERY-DESIGN §3.1** — workbook columns.
- Open question defaults applied:
  - Q-K-013-1: Option A
  - Q-K-013-2: 3 separate columns (no JSON-in-cell)
  - Q-K-013-3: Combined v0.4.4 → v0.4.5 patcher (TC binding columns + any other v0.4.5 schema work — for now just the binding columns; Test-Step v0.1.5 reads come from the existing v0.4.4 schema)
  - Q-K-013-4: Empty binding for chosen TC + framework → **warn but skip**, partial coverage is real
  - Q-K-013-5: Keep legacy descriptive spec names; do NOT rename

### Outputs

1. `BOURACKA-TESTPLAN-v0.4.5.xlsx` (repo root) — patched workbook with binding columns.
2. `tools/workbook-v0.4.4-to-v0.4.5.py` — new patcher (mirrors `v0.4.3-to-v0.4.4.py` pattern).
3. Modified `bouracka_ui/` — readers, dispatcher, server endpoints, UI dropdown.
4. New tests in `tools/tests/` + `bouracka_ui/tests/`.
5. CHANGELOG.md updated with v0.1.5-dev1 entry.

---

## 4. File boundaries — what you may touch

### Create

- `tools/workbook-v0.4.4-to-v0.4.5.py` — new patcher, ~25 KB, mirror Brief #001 pattern.
- `tools/tests/test_workbook_v0.4.4_to_v0.4.5_patcher.py` — focused tests, ~10 tests.
- `tools/tests/fixtures/synthetic-v0.4.4-mini.xlsx` — fixture, generated programmatically.
- `_config/BOURACKA-UI-V0.1.5-DESIGN-NOTES-EN.md` — APPEND a new §12 "TC-binding columns" subsection (do NOT rewrite §3–§11).
- `tools/patcher-reports/.gitkeep` — already exists, no-op.

### Modify

- `bouracka_ui/bouracka_ui/workbook_io.py` — extend `list_tcs()` to surface binding columns; keep all existing keys (additive contract).
- `bouracka_ui/bouracka_ui/dispatcher.py` — replace mechanical glob-from-TC-code with binding-column read.
- `bouracka_ui/bouracka_ui/server.py` — extend `/api/tcs` response + add `/api/about/orphan-specs` endpoint.
- `bouracka_ui/bouracka_ui/static/app.js` — switch TC dropdown source.
- `bouracka_ui/bouracka_ui/static/index.html` — minor: ensure /about page renders the new orphan-specs section.
- `bouracka_ui/tests/test_smoke.py` — add 6 new tests (count grows from current to current+6).
- `bouracka_ui/bouracka_ui/__init__.py` → `__version__ = "0.1.5-dev1"`.
- `bouracka_ui/pyproject.toml` → `version = "0.1.5.dev1"`.
- `CHANGELOG.md` — append v0.1.5-dev1 entry.

### DO NOT touch

- `BOURACKA-TESTPLAN-v0.4.4.xlsx` — read-only canonical source.
- `tools/workbook-v0.4.3-to-v0.4.4.py` — predecessor patcher; do NOT modify.
- `_config/TC-DISCOVERY-DESIGN-v0.1-EN.md` — read-only spec.
- `_config/SONNET-BRIEF-001*.md` — read-only briefs.
- `delivery/` — shipped artefacts.
- `recon/` — out of scope.

If you find a bug in `dispatcher.py` env-mapping (BUG-K-010 — UI sends `tst-demo`, consolidator rejects), **note it in checklist item 6 and do NOT fix it here**. That's the v0.1.4.1 hotfix lane. Mention it; don't drift scope.

---

## 5. Functional requirements

### F-1. New patcher `tools/workbook-v0.4.4-to-v0.4.5.py`

CLI surface mirrors v0.4.3→v0.4.4 patcher (`--source`, `--dest`, `--dry-run`, `--report-only`, `-v`).

**Schema delta** — add three columns to the right of existing `02_TestCases` columns:

| Column | Type | Notes |
|--------|------|-------|
| `cypress_spec_glob` | string | e.g. `cypress/e2e/a1-main-demo/main-happy-day.cy.ts` OR a comma-separated list for multi-spec TCs. Empty = "no cypress coverage for this TC" |
| `playwright_grep` | string | e.g. `TC-CP-008\|main-happy-day` (pipe-OR of patterns for `playwright test --grep`). Empty = no playwright coverage |
| `selenium_pytest_k` | string | e.g. `TC_CP_008 or main_happy_day` (pytest's `-k` expression). Empty = no selenium coverage |

All three default to empty for existing rows (KP fills them in a one-time chore). Add a `comments_KP_en` marker `(KP: fill TC binding columns)` to flag KP-review needed.

**`11_Changelog` append** — one row noting v0.4.4 → v0.4.5 schema-patch, summary "Added cypress_spec_glob, playwright_grep, selenium_pytest_k binding columns to 02_TestCases."

**Idempotency** — same discipline as Brief #001: re-run on already-patched workbook is a no-op (detect columns already present, skip).

### F-2. `workbook_io.list_tcs()` extension

Each returned TC dict gains three new keys:

```python
{
    "code": "TC-CP-008",
    ...existing keys...
    "cypress_spec_glob": "cypress/e2e/a1-main-demo/main-happy-day.cy.ts",
    "playwright_grep": "TC-CP-008|main-happy-day",
    "selenium_pytest_k": "TC_CP_008 or main_happy_day",
}
```

If the source workbook is v0.4.4 (no binding columns) → those keys are returned as empty strings (legacy fallback, same BUG-K-001 tolerance pattern).

### F-3. `dispatcher.py` change — read bindings from workbook, not from glob construction

**Today:** for chosen TC codes, dispatcher constructs `cypress/e2e/**/*<tc-lowercased>*.cy.ts` glob mechanically. That's where `TC-CP-A1-MAIN-DEMO` came from — it's parsed out of the spec FILENAME, not the workbook.

**New behavior:**

```python
def build_cypress_spec_arg(tcs: list[dict]) -> str:
    """Combine cypress_spec_glob values for chosen TCs into a comma-separated --spec arg."""
    globs = [tc["cypress_spec_glob"] for tc in tcs if tc.get("cypress_spec_glob")]
    return ",".join(globs)

def build_playwright_grep_arg(tcs: list[dict]) -> str:
    """OR-join playwright_grep values."""
    patterns = [tc["playwright_grep"] for tc in tcs if tc.get("playwright_grep")]
    return "|".join(patterns)

def build_selenium_pytest_k_arg(tcs: list[dict]) -> str:
    """OR-join selenium_pytest_k expressions."""
    exprs = [tc["selenium_pytest_k"] for tc in tcs if tc.get("selenium_pytest_k")]
    return " or ".join(f"({e})" for e in exprs)
```

**Warn-but-skip (Q-K-013-4 default):** if user picks `TC-CP-008` + framework `cypress` but TC-CP-008's `cypress_spec_glob` is empty, log a structured warning and **skip cypress invocation for that TC**. Do NOT halt the whole run. Other framework/TC combos that have bindings continue.

**Empty all-frameworks for all chosen TCs** → halt with structured "no specs to invoke" error before any framework runs.

### F-4. `server.py` — extend `/api/tcs` + add `/api/about/orphan-specs`

`/api/tcs` already returns the TC list. With F-2's extension, the binding columns flow through automatically — verify they appear in the JSON response.

New endpoint:

```
GET /api/about/orphan-specs
```

Response:

```json
{
  "cypress_orphans": [
    "cypress/e2e/legacy-only-cypress-spec.cy.ts"
  ],
  "playwright_orphans": [...],
  "selenium_orphans": [...],
  "summary": {
    "cypress_specs_on_disk": 25,
    "cypress_specs_bound_to_tc": 20,
    "cypress_orphans": 5
  }
}
```

**Discovery logic:**

- Walk `<REPO_ROOT>/cypress/e2e/` recursively for `*.cy.ts` files.
- For each spec, check whether ANY workbook TC has `cypress_spec_glob` that matches (literal substring match, or glob-aware fnmatch).
- Orphan = on-disk-but-not-bound. List relative path from `REPO_ROOT`.
- Same logic for playwright (`playwright/tests/`, `*.spec.ts`) and selenium (`selenium/tests/`, `*.py`).
- Cache result per `WORKBOOK_PATH` mtime; recompute on workbook change.

### F-5. UI `app.js` — switch TC dropdown source

**Today:** the TC dropdown is populated from some filesystem-discovery code (find the function that reads spec files and builds the option list).

**New behavior:** the TC dropdown calls `GET /api/tcs` and renders one option per row, value = `code`, label = `code — name_en` (e.g., `TC-CP-008 — zenID + AISPOV ROB — happy auto-fill`). When a framework filter is active (`framework=cypress`), the dropdown filters TCs where `framework_targets` contains the chosen framework AND `<framework>_spec_glob` (or `_grep` or `_pytest_k`) is non-empty.

If the user picks a TC where the framework binding is empty, show a small badge `(no cypress coverage)` next to the option (advisory; doesn't disable the option, because the user might want to dispatch other frameworks for that same TC).

### F-6. `/about` page renders orphan specs

In the existing `/about` page (`static/index.html` route), add a collapsible section "Orphan specs (on disk but not bound to TC):" that calls `/api/about/orphan-specs` and lists each.

### F-7. Version bumps + CHANGELOG

- `bouracka_ui/bouracka_ui/__init__.py`: `__version__ = "0.1.5-dev1"`
- `bouracka_ui/pyproject.toml`: `version = "0.1.5.dev1"` (PEP 440 form)
- `CHANGELOG.md`: append `## v0.1.5-dev1 (2026-05-14)` section noting:
  - Workbook v0.4.5 binding columns added
  - `workbook_io.list_tcs()` returns binding columns
  - Dispatcher reads workbook bindings instead of constructing globs
  - UI dropdown switched from filesystem to workbook source
  - `/api/about/orphan-specs` endpoint added
  - BUG-K-013 resolved

### F-8. KP one-time chore (NOT yours — Pete will do)

Once the v0.4.5 patcher runs, KP needs to walk ~25 spec files and bind each to a workbook TC row. **Do NOT auto-bind based on heuristics** (e.g., filename → TC code guess). Leave the columns empty + flagged for KP. Pete operates this step manually.

---

## 6. Idempotency

- v0.4.4 → v0.4.5 patcher re-run on already-v0.4.5 workbook: no-op.
- `workbook_io.list_tcs()` legacy fallback: if reading v0.4.4 (no binding cols), returns empty-string binding values. Test must prove this.
- `/api/about/orphan-specs` is read-only; cache per mtime.

---

## 7. CLI surface — patcher

```
python tools/workbook-v0.4.4-to-v0.4.5.py
    [--source PATH]    default: BOURACKA-TESTPLAN-v0.4.4.xlsx in repo root
    [--dest PATH]      default: BOURACKA-TESTPLAN-v0.4.5.xlsx in repo root
    [--dry-run]
    [--report-only]
    [-v]

Exit codes: same as v0.4.3 → v0.4.4 patcher
```

---

## 8. Test plan

### Patcher tests — `tools/tests/test_workbook_v0.4.4_to_v0.4.5_patcher.py` (~10 tests)

1. `test_three_binding_columns_added_to_02_TestCases`
2. `test_existing_rows_get_empty_binding_values_with_kp_marker`
3. `test_patcher_idempotent_on_already_patched_workbook`
4. `test_11_changelog_appended_with_v0.4.5_row`
5. `test_dry_run_no_dest_written`
6. `test_source_unchanged_after_patch`
7. `test_report_includes_kp_review_count` — count of rows still needing KP binding
8. `test_patcher_preserves_all_other_sheets_byte_identical` — except 02_TestCases and 11_Changelog
9. `test_patcher_preserves_user_data_rows` — bugs / runs / results — same as v0.4.3 → v0.4.4 (Brief #001 §F-2 → §F-5 still apply)
10. `@pytest.mark.integration test_patches_real_v0.4.4_workbook` — count of TCs preserved, count of KP-review markers added

### Server smoke tests — extend `bouracka_ui/tests/test_smoke.py` (~6 new tests)

```python
def test_api_tcs_returns_binding_columns():
    """F-2: /api/tcs JSON includes cypress_spec_glob, playwright_grep, selenium_pytest_k keys."""

def test_api_tcs_binding_empty_on_v0.4.4_workbook():
    """Legacy fallback: when workbook is v0.4.4 (no binding cols), keys are empty strings, no crash."""

def test_dispatcher_skips_framework_with_empty_binding():
    """F-3: pick a TC + framework where binding is empty → that framework is skipped with warning, others run."""

def test_dispatcher_halts_when_all_bindings_empty_for_chosen_tcs():
    """F-3: no specs to invoke → halt with structured error before any framework runs."""

def test_api_about_orphan_specs_endpoint():
    """F-4: GET /api/about/orphan-specs returns the 3-framework summary structure."""

def test_orphan_specs_empty_when_all_bound():
    """When workbook bindings cover all on-disk specs, orphan lists are empty."""
```

---

## 9. Risk gates — STOP and report

1. **`bouracka_ui/static/app.js` is too large to refactor safely.** The current TC dropdown might be intertwined with other event handlers. If you can't isolate the change to <50 lines, halt and ask Pete.
2. **The existing dispatcher.py spec-glob construction is more sophisticated than my F-3 sketch.** It may have special-case handling for run-level overrides, env-specific specs, etc. Halt if your refactor would lose existing behavior.
3. **`/api/about` route doesn't currently exist.** If it's a SPA route handled by `static/index.html` alone, adding `/api/about/orphan-specs` is fine. If it's a real server endpoint with non-trivial state, halt and ask.
4. **Workbook v0.4.5 already in repo root** (from some other dev work). If `BOURACKA-TESTPLAN-v0.4.5.xlsx` exists when you start, halt + ask Pete which version is canonical.
5. **More than 5 orphan specs found** in the integration test against real v0.4.4 workbook. That's a normal state (KP hasn't done the binding chore yet) — report the count + which specs, but don't halt.
6. **A workbook TC has `framework_targets = "playwright; cypress"` but `cypress_spec_glob` empty and `playwright_grep` empty.** That's the same TC being "intended for cypress + playwright" but with no actual bindings. Report it in PATCH-REPORT as an inconsistency; KP needs to either fill the bindings or drop the framework_targets.

---

## 10. Return checklist

1. Branch name + commit SHA(s).
2. Files changed (created / modified) with line counts.
3. Test results — `pytest tools/tests/ -v` + `pytest bouracka_ui/tests/ -v -m "not integration"` full pass list.
4. Integration test output — paste the v0.4.5 patcher report §1 summary (TC count, KP-review markers, etc.).
5. Curl output:
   ```
   curl http://127.0.0.1:8424/api/tcs/TC-CP-008
   curl http://127.0.0.1:8424/api/about/orphan-specs
   ```
   Both with the local server running against fresh-patched v0.4.5.
6. Out-of-scope findings — including the BUG-K-010 env-mapping bug you'll see in dispatcher.py (note it; don't fix it here).
7. Deviations from this brief with justifications.
8. Open questions for the chain — likely Pete's KP-binding chore brief, and the v0.1.5 wheel release brief.

---

## 11. Don't-go-beyond markers

- **Do not implement the KP-binding chore.** Spec → TC binding is manual KP work. You leave the columns empty + flagged.
- **Do not change spec filenames.** Per Q-K-013-5, keep their descriptive names.
- **Do not modify `tools/workbook-v0.4.3-to-v0.4.4.py`.** Predecessor patcher stays as-is.
- **Do not fix BUG-K-010 dispatcher env-mapping.** Out of scope; flag it.
- **Do not add a "binding editor" UI.** TC bindings are authored in Excel. Future UI editor is v0.1.6+.
- **Do not "improve" the orphan-specs heuristics with fuzzy matching.** Literal substring + fnmatch only.

---

## 12. Quick-reference: spec sections by file/line

| Brief item | Spec ref |
|------------|----------|
| §F-1 three binding columns | TC-DISCOVERY-DESIGN §3.1 Option A |
| §F-3 warn-but-skip empty binding | TC-DISCOVERY-DESIGN §6 Q-K-013-4 default |
| §F-5 UI dropdown source switch | TC-DISCOVERY-DESIGN §7 step 3 |
| §F-6 /about orphan specs | TC-DISCOVERY-DESIGN §5 tradeoff mitigation |
| §F-8 KP one-time chore | TC-DISCOVERY-DESIGN §5 tradeoff "30-min one-time chore" |
| Q-K-013-1 through 5 defaults | TC-DISCOVERY-DESIGN §6 table |

---

## 13. Acceptance — when is this brief "done"?

- All patcher tests + smoke tests pass.
- Integration patcher run against real v0.4.4 produces v0.4.5 with the 3 new columns present + 49 KP-review markers.
- Local server starts, `/api/tcs/TC-CP-008` returns binding columns (likely empty pre-KP), `/api/about/orphan-specs` returns the 3-framework lists.
- UI dropdown smoke (Pete tests manually) — picks TC-CP-008, no cypress invocation because binding empty, warn message visible.
- Branch has clean commits.
- Return checklist §10 pasted to Pete.

Then Pete reviews; next downstream work is the **KP one-time binding chore** (Pete + KP walk the ~25 specs and fill `cypress_spec_glob` / `playwright_grep` / `selenium_pytest_k` in Excel; ~30 min).

Then the v0.1.5 wheel can be built and shipped with TC-discovery working against workbook bindings.

---

**End of BRIEF-003.**
