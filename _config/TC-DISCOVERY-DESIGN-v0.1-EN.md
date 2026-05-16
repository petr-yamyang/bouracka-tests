# TC discovery — design decision (BUG-K-013 resolution)

**Author.** Opus 4.7 session (Pete Y. + Claude), 2026-05-14.
**Status.** Design baseline. Awaits Pete decision before Sonnet Brief #003 is drafted.
**Triggering bug.** BUG-K-013 — Kate observed: "Seznam TC pro všechny ENV a frameworks je odlišný než v původní verzi."
**Severity.** P1 — UI workflow disconnect from workbook test plan. Not a crash, but breaks the workbook-as-source-of-truth contract.

---

## 1. The disconnect, in one paragraph

Kate's bouracka-ui dispatch sent TC codes `TC-CP-A1-MAIN-DEMO`, `TC-CP-A2-ALT-1..10`. These do NOT exist in any of our workbooks (v0.2 through v0.4.4). The workbooks contain `TC-CP-001..024` plus `TC-CP-NEW-V..Y`. The A1/A2/ALT codes match the **cypress folder/file naming**: `cypress/e2e/a1-main-demo/`, `cypress/e2e/a2-alternates-demo/alt-1-rp-regex.cy.ts`, etc. So **the UI is enumerating TCs from the filesystem walk of the cypress source tree, not from `02_TestCases` in the workbook**. The workbook is treated as a status-tracking sheet, not as the authoritative test plan that drives dispatch.

This means:

- Kate authors / KP reviews TCs in the workbook with codes `TC-CP-008` etc.
- The UI dropdown shows `TC-CP-A1-MAIN-DEMO` etc. (filesystem-derived).
- Dispatch invokes specs by filesystem path. The workbook's TC codes are never used to drive dispatch.
- After a run, results are written back keyed by... whichever ID the consolidator picked. Almost certainly the spec-derived ID, not the workbook one.

Kate's complaint is correct. The workbook isn't authoritative; it's parallel.

---

## 2. Two design choices feeding the disconnect

### 2.1 Discovery axis

Where does the UI get the list of TCs from?

- **WORKBOOK** — read `02_TestCases.item_code`. Authoritative, schema-owned, KP-reviewed.
- **FILESYSTEM** — walk `cypress/e2e/`, `playwright/tests/`, `selenium/tests/`. Reflects what specs are actually present + runnable.

### 2.2 Dispatch-binding axis

Once the user picks "TC-CP-008", how does the framework know which spec to run?

- **NAME CONVENTION** — file/folder names match TC codes (`cypress/e2e/TC-CP-008.cy.ts` or `cypress/e2e/TC-CP-008/main.cy.ts`).
- **METADATA TABLE** — workbook (or external file) maps TC code → glob/grep/-k expression. Specs are free to use any names.
- **TAG-IN-SPEC** — specs declare their TC binding inline (`it('[TC-CP-008] main happy day', ...)`) and the dispatcher greps for the tag.

---

## 3. Three viable options

### Option A — workbook owns TC list; spec-binding via workbook columns (KP-authored)

Add three columns to `02_TestCases`:

```
cypress_spec_glob       e.g. "cypress/e2e/a1-main-demo/main-happy-day.cy.ts"
playwright_grep         e.g. "TC-CP-008|main-happy-day"
selenium_pytest_k       e.g. "TC_CP_008 or main_happy_day"
```

**Discovery:** UI reads `02_TestCases.item_code` for the dropdown.
**Dispatch:** UI takes the picked TC codes → builds framework invocations from the binding columns → invokes.

**Pros:**

- Workbook is single source of truth. KP can author TCs without touching code.
- Spec files can keep their natural English names.
- Adding a new TC: row in workbook + KP fills the binding column for whichever framework(s) implement it.
- Cross-framework one-TC-N-specs is natural (TC binds to a list of specs per framework).
- Migration: existing specs unchanged; just populate the binding columns.

**Cons:**

- Adds 3 columns to `02_TestCases` (schema bump → v0.4.5).
- Manual maintenance: every new spec needs its row's column updated by KP.
- If a spec exists but its TC row is missing, the spec is undispatchable (unless we add a "discovered but unbound specs" debug view).

### Option B — rename specs to match TC codes (filesystem reflects workbook)

Rename:
```
cypress/e2e/a1-main-demo/main-happy-day.cy.ts   →   cypress/e2e/TC-CP-008.cy.ts
cypress/e2e/a2-alternates-demo/alt-1-rp-regex.cy.ts  →   cypress/e2e/TC-CP-009.cy.ts
... etc.
```

**Discovery:** UI walks filesystem AND/OR reads workbook — they match by construction.
**Dispatch:** filename = TC code → trivial glob.

**Pros:**

- No metadata table needed; one-to-one mapping.
- Spec names are self-documenting in test runner logs.
- Easy refactor — script + rename.

**Cons:**

- Lossy: `main-happy-day` and `alt-1-rp-regex` are descriptive; `TC-CP-008` is opaque. Adding a `# Description: ...` header doesn't help when reading test run logs.
- One-TC-N-specs requires sub-numbering (`TC-CP-008.1.cy.ts`, etc.) — clunky.
- Cross-framework: cypress + playwright + selenium each need their own file named after the TC. If you forget one framework, the TC silently lacks coverage there. (Same problem exists today, but it's at least visible by filesystem listing.)
- A KP rename of TC-CP-008 → TC-CP-NEW-V means renaming files in 3 framework trees + their imports + their reporter mappings.

### Option C — workbook owns TC list; spec-binding via separate config file

Add a new file `_config/TC-TO-SPEC-MAP.yaml` (or similar):

```yaml
TC-CP-008:
  cypress:  "cypress/e2e/a1-main-demo/main-happy-day.cy.ts"
  playwright: "TC-CP-008|main-happy-day"
  selenium: "TC_CP_008 or main_happy_day"
TC-CP-009:
  cypress:  "cypress/e2e/a2-alternates-demo/alt-1-rp-regex.cy.ts"
  ...
```

**Discovery:** UI reads `02_TestCases.item_code`.
**Dispatch:** UI reads `_config/TC-TO-SPEC-MAP.yaml` for the binding.

**Pros:**

- Single file to author; no workbook schema bump.
- YAML diffs cleanly in PRs (workbook diff is messy).
- Easy to extend with per-framework env constraints, override-args, etc.

**Cons:**

- Workbook is no longer single source — KP has to update workbook AND yaml. Two places to drift.
- Tester edits workbook in Excel but can't easily edit yaml.
- Adds a dependency: PyYAML in the bouracka-ui wheelhouse (currently we have pyyaml from uvicorn[standard], so no new dep actually — just plumbing).

---

## 4. Comparison matrix

| Criterion | Option A (workbook columns) | Option B (rename specs) | Option C (yaml map) |
|---|:---:|:---:|:---:|
| Workbook is authoritative for TCs | ✓ | ✓ (by sync) | ✓ |
| Single source of truth | ✓ | ✓ | ✗ (yaml + workbook) |
| KP can author in Excel | ✓ | ✓ (but no binding info) | ✗ (yaml needs editor) |
| Easy to add new TC | ✓ | rename + 3 frameworks | ✓ |
| Easy to rename existing TC | column update | rename across 3 trees | yaml key update |
| Spec name descriptive | ✓ | ✗ (TC code only) | ✓ |
| Cross-framework one-TC-N-specs | ✓ (list in column) | ✗ (sub-numbering) | ✓ (list in yaml) |
| Schema bump | YES (v0.4.5) | NO | NO |
| Diff-friendly | NO (xlsx) | YES (rename ops) | YES (yaml) |
| Risk if TC-CP-008 row missing | spec undispatchable | filesystem still has spec | spec undispatchable |
| Aligns with Kate's workbook-as-truth view | ✓ | partial | ✓ |

---

## 5. Recommendation: Option A

**Workbook owns everything KP authors. Spec-binding columns live next to the TC row.** Reasons:

1. **Kate's mental model = workbook-as-source-of-truth** — she's authored bugs against TC codes, she expects to dispatch by those same codes. Option A keeps the workbook as the single thing she opens to see "what tests do we have, in what state."
2. **KP authors test cases in Excel anyway** — column-based binding fits the existing workflow. Adding three columns to a sheet with 38 columns is not a big lift.
3. **Cross-framework cleanly handled** — one TC row, three framework bindings, no rename storm.
4. **Schema bump v0.4.4 → v0.4.5 is already coming** for FR-K-001 (Test-Step entity) and the deprecation rewires we deferred from Brief #001. Adding `cypress_spec_glob` / `playwright_grep` / `selenium_pytest_k` in the same v0.4.5 bump is essentially free.
5. **Option B's rename is destructive** — once we rename cypress files to TC codes, we lose the human-readable spec names from test reports, which Kate also reads.
6. **Option C splits the source** — KP has to remember to update both Excel and yaml. Eventually they drift.

**Tradeoffs accepted:**

- Filesystem-only specs (no TC row) become undispatchable. We mitigate by adding a `/about` page section: "discovered specs with no TC binding" — a debug view that lists orphans.
- KP has to walk the existing ~25 specs once and bind each to a TC row. ~30 min one-time chore.

---

## 6. Open questions for Pete

| # | Question | My recommended default |
|---|----------|------------------------|
| Q-K-013-1 | A vs B vs C? | **A** (per §5) |
| Q-K-013-2 | If A: should the binding columns be split per-framework (3 cols) or single `frameworks_spec_binding` JSON cell? | **3 columns** — easier to read in Excel, no JSON-in-cell discipline needed |
| Q-K-013-3 | If A: workbook v0.4.5 bumps in same patcher as Test-Step entity, or separate? | **Same patcher** — combined v0.4.4 → v0.4.5 single hop |
| Q-K-013-4 | What does dispatch do if `cypress_spec_glob` is empty for a chosen TC + cypress framework? | Skip silently? halt with warning? warn in /about? My default: **warn but skip** — partial coverage is real |
| Q-K-013-5 | What about LEGACY A1/A2/MAIN-DEMO spec names — keep them or rename? | **Keep** — they're descriptive; spec filenames don't need to be TC codes if Option A |

---

## 7. Implementation outline (becomes Sonnet Brief #003 after Pete picks)

If Option A approved, the implementation steps:

1. **Workbook v0.4.5 patcher** — extends `tools/workbook-v0.4.4-to-v0.4.5.py` (or extends 0.4.3→0.4.4 patcher) to add 3 binding columns to `02_TestCases`. KP-review markers added per row.
2. **Server-side change** — `bouracka_ui.workbook_io.list_tcs()` returns binding columns. `bouracka_ui.dispatcher` reads them instead of constructing globs from TC codes mechanically.
3. **UI dropdown** — switch source from filesystem walk to workbook TC codes. Single biggest user-visible change.
4. **/about page** — add "discovered specs without workbook binding" debug section.
5. **Smoke test** — dispatch with a TC that has all 3 bindings filled → all 3 frameworks invoke. Dispatch with a TC that has only cypress binding → only cypress runs, others skip with warning.
6. **KP one-time chore** — walk the existing specs + populate binding columns for the ~25 TC rows that have spec coverage today.

---

## 8. What does NOT change

- Cypress / playwright / selenium spec files themselves stay where they are, named what they are.
- Workbook `02_TestCases` retains all existing columns; we only add 3.
- TC numbering scheme `TC-CP-NNN` stays.
- The cross-framework consolidator stays — it joins on TC code, which it already does (and the binding mechanism just makes sure the right specs were invoked per TC).

---

## 9. Refs

- BUG-K-013 task — `[mcp__claude-cli__TaskGet 63]` (or equivalent task tracker entry)
- Kate's feedback doc — `uploads\Kate s tests results.docx` 2026-05-14
- `_config/BOURACKA-UI-V0.1.5-DESIGN-NOTES-EN.md` — v0.1.5 broader feature roadmap
- `_config/SONNET-BRIEF-001-WORKBOOK-PATCHER-V0.4.3-TO-V0.4.4.md` — previous workbook patcher (will be extended in v0.4.4 → v0.4.5)
- `bouracka_ui/bouracka_ui/dispatcher.py` — current spec-glob construction (the code that will change)

---

## 10. Decision request

Pete: tick one and I draft Sonnet Brief #003 against your choice.

- [ ] Option A — workbook columns
- [ ] Option B — rename specs to TC codes
- [ ] Option C — separate yaml map
- [ ] Other / hybrid — describe
