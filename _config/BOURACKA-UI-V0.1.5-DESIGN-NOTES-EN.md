# Bouračka UI v0.1.5 — Design Notes

**Version.** v0.1 (2026-05-13) — pre-implementation design baseline.
**Scope.** Bundle 2 (Tester UX + auditability) per Kate Round-1 feedback fold-in.
**Status.** Design baseline. Implementation begins after Kate Round-1 verdict on v0.1.4.
**Author.** Pete Y., with KP-review pending on §3 schema and §6 migration.

---

## 1. Bundle 2 scope — three features

| ID | Title | Why now | Driver |
|----|-------|---------|--------|
| **FR-K-001** | Bug ↔ TC ↔ Step traceability | Kate cannot tell which step of a TC the bug fired on; bug-report quality suffers and retest after fix wastes 5–10 min per bug walking the TC blindly. | Round-1 |
| **FR-K-002** | TC step preview in UI | Tester opens TC card → only sees free-text `steps_summary`. Cannot preview individual steps' actions/expected without opening the workbook. | Round-1 |
| **FR-K-003** | Human-readable run console | Live run JSON dump is unreadable; testers want a "what's happening now" view (step N of M, current verdict, last assertion). | Round-1 |
| **FR-K-004** | Bug → screenshot/video evidence | Bug record shows WHAT failed (step ref) but not HOW IT LOOKED. Tester re-investigating a fix has to re-run the TC just to see the visual. Pair-rail with FR-K-001 — together they make bug records self-contained. | Round-1 follow-up |

FR-K-001/002/003 share an architectural prerequisite: **Test-Step as a first-class entity** (§3 below).
FR-K-004 adds a parallel prerequisite: **a small artefact store + a stable URL scheme for visual evidence** (§4a below).

---

## 2. The schema debt we're paying off

v0.4.3 workbook state, post-archaeology (`python3 openpyxl` dump 2026-05-13):

- `02_TestCases.steps_summary` (col T/19) is **free-text prose**. One cell, no structure, no per-step expected.
- `02c_TC_Assertions.step_id` (col 2) is a **foreign key to nothing.** The column exists, presumably populated as `tc_ref + ordinal` strings, but the target entity (sheet `02e_TestSteps`) does not exist.
- `08_Bugs.linked_tc_ref` (col 14) AND `08_Bugs.tc_ref` (col 28) — **two TC references** in the same row. Legacy duplication. No `linked_step_ref` column at all.

This is the kind of "the FK exists but the table doesn't" debt that gets paid the moment a feature requests it. FR-K-001 is that moment.

---

## 3. Proposed schema — promote Test-Step to first-class

### 3.1 New sheet — `02e_TestSteps`

| Column | Type | Notes |
|--------|------|-------|
| `id` | int (PK) | autoincrement |
| `step_code` | string | `STP-<tc_code>-<NN>`, e.g. `STP-TC-LOGIN-01-03` |
| `tc_ref` | FK → 02_TestCases.item_code | mandatory |
| `ordinal` | int | 1-based, gap-free per TC |
| `action_cs` / `action_en` | string | what the tester (or framework) does |
| `expected_cs` / `expected_en` | string | observable post-condition |
| `framework_hint` | string | `cypress`, `playwright`, `selenium`, or `*` (all). Empty = all (per BUG-K-001 tolerance rule) |
| `assertion_lib_ref` | FK → 02d_AssertionLibrary.library_code | optional, points at canonical assertion if exists |
| `is_decision_point` | bool | step branches workflow (state-machine integration) |
| `comments_KP_en` | string | KP-review column |
| `created_at` / `updated_at` | datetime | audit |
| `notes` | string | freeform |

### 3.2 Re-wire existing references

| Sheet | Change |
|-------|--------|
| `02_TestCases` | Keep `steps_summary` as **denormalized** preview — generated from 02e rows at workbook-save time. New column `steps_count` (int) sourced from COUNTIF(02e!tc_ref, A2). |
| `02c_TC_Assertions` | `step_id` now FK → `02e_TestSteps.step_code` (was dangling). Validate referential integrity on workbook load. |
| `08_Bugs` | Deprecate `tc_ref` (col 28). Keep `linked_tc_ref` (col 14). **Add `linked_step_ref`** → FK → `02e_TestSteps.step_code`. Nullable (bugs may be TC-level not step-level). |
| `02b_TC_Parameters` | No change; params remain TC-scoped (step-scoped params can be v0.2 if anyone asks). |

### 3.3 Backward compatibility

- v0.1.4 readers ignore the new sheet (openpyxl tolerates unknown sheets); UI continues to work but offers no step-preview.
- v0.1.5 readers use `02e_TestSteps` if present, fall back to splitting `steps_summary` by newline if absent (legacy mode, documented as "best-effort").
- Workbook upgrade path: a one-shot patcher (`tools/workbook-v0.4.3-to-v0.4.4.py`) splits `steps_summary` into ordered rows, generates `step_code`, leaves manual editing for KP review.

---

## 4. FR-K-001 — Bug ↔ TC ↔ Step traceability

### 4.1 UX

- Bug-edit form gets a third dropdown after TC selection: **"On which step?"** (populated from `02e_TestSteps WHERE tc_ref = <selected TC>`). Optional; default empty = TC-level bug.
- TC card shows **"N open bugs"** badge, expandable to a per-step heatmap when steps exist.
- Run console (FR-K-003) clicking on a step opens **"file new bug against this step"** prefilled.

### 4.2 API surface (v0.1.5 additions to bouracka_ui.server)

```
GET  /api/tcs/{tc_code}/steps                    -> list step entities
GET  /api/steps/{step_code}                      -> single step + linked bugs + assertion
POST /api/bugs                                   -> body.linked_step_ref optional
GET  /api/bugs?linked_tc_ref=...&linked_step_ref=...
```

### 4.3 Persistence rule

When user marks a bug against step `STP-X-03`, the existing workbook row in `08_Bugs` gets updated atomically:
- `linked_tc_ref = X`
- `linked_step_ref = STP-X-03`
- `tc_ref` (deprecated col 28) blanked
- `updated_at = now()`

ROW_VERSION discipline (per Oracle ERD §4) applies once we migrate; for v0.1.5 staying on XLSX, optimistic concurrency is "last write wins on the file lock". Documented limitation.

---

## 4a. FR-K-004 — Bug ↔ screenshot/video evidence

### 4a.1 What the harness already captures

| Framework | Screenshot on fail | Video of test run | Trace |
|-----------|:---:|:---:|:---:|
| Cypress   | yes — `cypress/screenshots/<spec>/<test>.png` | yes — `cypress/videos/<spec>.mp4` (all tests, configurable) | no native |
| Playwright | yes — `test-results/<test>/test-failed-*.png` | yes — `test-results/<test>/video.webm` (when configured) | yes — `trace.zip` |
| Selenium  | not by default — needs explicit `driver.save_screenshot()` per step | no native | no |

v0.1.4 dispatcher already runs harnesses and writes `runs/<run-id>/` under repo root, but **artefacts are scattered across per-framework folders** with no canonical naming and no link from the bug record.

### 4a.2 Canonical artefact store

Introduce `runs/<run-id>/artefacts/<tc_code>/<step_code>/` as the single canonical landing zone, copied from per-framework output dirs by the dispatcher right after the run completes.

```
runs/r-2026-05-14-cypress-001/
├── result.json                              # run-level cross-framework envelope
├── artefacts/
│   ├── TC-LOGIN-FAIL-01/
│   │   ├── STP-TC-LOGIN-FAIL-01-03/
│   │   │   ├── screenshot.png               # captured at moment of failure
│   │   │   ├── video.mp4                    # whole TC video (links from each step)
│   │   │   ├── dom-snapshot.html            # cypress only, if enabled
│   │   │   └── console.log                  # browser console for that step
│   │   └── STP-TC-LOGIN-FAIL-01-04/
│   │       └── (no failure, no screenshot)
│   └── TC-RESET-PWD-01/
│       └── ...
└── trace.zip                                # playwright only, run-level
```

**Naming guarantees** — collision-free across reruns: each `run-id` is unique, so artefact paths are immutable forever (golden for bug retests months later).

### 4a.3 New `08_Bugs` columns (schema delta)

| Column | Type | Notes |
|--------|------|-------|
| `evidence_screenshot_path` | string | relative path from repo root, e.g. `runs/r-2026-05-13-cypress-007/artefacts/TC-LOGIN-FAIL-01/STP-TC-LOGIN-FAIL-01-03/screenshot.png` |
| `evidence_video_path` | string | nullable; same scheme |
| `evidence_trace_path` | string | nullable; playwright `trace.zip` |
| `evidence_capture_kind` | enum | `auto-from-fail` / `manual-tester` / `none` |
| `evidence_capture_at` | datetime | when artefacts were frozen (= run end time) |

`screenshot_ref` (existing col 36) and `trace_ref` (existing col 37) — deprecated in favour of typed paths above. Patcher migrates legacy values.

### 4a.4 UI surface

In bug card, below the step linkage block:

```
Evidence
─────────────────────────────────────
Screenshot:   [thumb 120×80]  ← click → modal viewer
              captured at fail step STP-TC-LOGIN-FAIL-01-03
              (run r-2026-05-13-cypress-007, 2026-05-13T14:32)

Video:        [▶ play inline]  ← seeks to step boundary
              cypress whole-TC video, 47s

Trace:        [download trace.zip]   (Playwright only)
```

Modal viewer: keyboard-driven (←/→ between steps in same TC, Esc to close), shows screenshot + step description side-by-side. No new JS dependency — vanilla `<dialog>` element + `<img>` + `<video>` tags.

### 4a.5 New API surface

```
GET  /api/bugs/{bug_code}/evidence
       -> { screenshot_url, video_url, trace_url,
            captured_at, step_ref, run_ref }
GET  /api/runs/{run_id}/artefacts/{tc}/{step}/screenshot.png
       -> static file serve from runs/<id>/artefacts/... (read-only)
GET  /api/runs/{run_id}/artefacts/{tc}/{step}/video.mp4
       -> static file serve with HTTP Range support (for video seeking)
```

FastAPI's `StaticFiles` does most of this for free; the only custom work is the resolver that maps `bug_code` → artefact paths via `08_Bugs.evidence_*_path`.

### 4a.6 Privacy / cleanup discipline

- Screenshots may capture **test data** that mirrors production shapes (real-looking names, emails, addresses). For shared workbooks: artefacts live under `runs/` which is gitignored; bouracka-ui server hosts them locally over LAN, never published.
- **Retention policy** — v0.1.5 ships with **infinite retention** (cheap discipline: keep everything; total artefact volume per run is ~50 MB worst case for full E2E). v0.1.6 adds a `--purge-runs-older-than 90d` housekeeper if disk pressure shows up.

### 4a.7 Cross-framework dispatcher work

The dispatcher (bouracka_ui/bouracka_ui/dispatcher.py — current v0.1.4 hook stub) needs three new responsibilities:

1. **Detect framework output paths post-run** — cypress puts files in different places than playwright; well-known per-framework patterns.
2. **Copy + rename into canonical layout** — atomic, with sha256 in run manifest so we know nothing was tampered with.
3. **Update `08_Bugs.evidence_*_path` for bugs that were auto-filed during the run.**

Selenium specifically needs the harness side to call `driver.save_screenshot()` in a `try/except` wrapper per step — see §6.3 risk gate; if too costly, selenium runs land with `evidence_capture_kind = none` and the bug carries TC-level note only.

---

## 5. FR-K-002 — TC step preview

### 5.1 UI

TC detail card grows a **"Steps"** accordion below the existing `steps_summary` blob:

```
TC: TC-LOGIN-OK-01
  Preconditions: user has account, demo env reachable
  Steps:
    1. [Action] Navigate to /login
       [Expected] Login form visible (state: LOGIN_FORM)
       [Assertion] LOGIN_FORM_VISIBLE (lib: cypress + playwright)
    2. [Action] Type valid credentials, click "Sign in"
       [Expected] Redirect to /dashboard within 3s (state: LOGGED_IN)
       [Assertion] DASHBOARD_LOADED
    3. ...
  Expected: dashboard reachable
  Framework targets: cypress, playwright
```

### 5.2 Read-only in v0.1.5

Editing steps in v0.1.5 is **out of scope** — testers edit `02e_TestSteps` directly in Excel. v0.1.6 may add an inline step editor, gated on whether KP wants tester-side step authoring (governance question).

---

## 6. FR-K-003 — Human-readable run console

### 6.1 Problem

Today: `/api/runs/{id}` returns raw JSON, surfaces as `<pre>` in the UI. Testers see:
```
{"run_id":"r-2026-05-13-cypress-001","status":"RUNNING","current_tc":"TC-LOGIN-OK-01","frame":...}
```
…which is not "what's happening" to a non-engineer.

### 6.2 Target rendering

```
▶ Run r-2026-05-13-cypress-001                    [RUNNING — 4m12s]
  Framework: cypress    Env: tst.demo.bouracka.cz
  ─────────────────────────────────────────────────────
  TC-LOGIN-OK-01      ✓ PASS  (12s, 3/3 steps)
  TC-LOGIN-FAIL-01    ✓ PASS  (8s, 4/4 steps)
  TC-RESET-PWD-01     ⟳ RUNNING
    Step 2 of 5: Click "Forgot password" link
    Last assertion: PWD_RESET_FORM_VISIBLE — PASS (1.2s ago)
  TC-SIGNUP-OK-01     · queued
  TC-SIGNUP-FAIL-01   · queued
```

### 6.3 Implementation

- New endpoint `GET /api/runs/{id}/console` returns pre-rendered HTML fragment (server-side templated) — keeps client JS minimal.
- Polling every 2s via `EventSource` or `fetch` loop (Server-Sent Events nice-to-have, polling acceptable for v0.1.5).
- Step granularity requires the harness to emit step events. **Open question:** cypress reports test-block granularity natively, playwright via `--reporter=json`, selenium needs custom listener. See §8 Open questions.

---

## 7. Cross-cutting — Oracle ERD v0.1 implications

When the Oracle migration lands (Phase 4 of `BOURACKA-DWH-DEV-PLAN-v0.1`), Test-Step becomes its own table:

```
TEST_STEPS (
  step_id          NUMBER PRIMARY KEY,
  step_code        VARCHAR2(64) UNIQUE NOT NULL,
  tc_id            NUMBER NOT NULL REFERENCES TEST_CASES(tc_id),
  ordinal          NUMBER NOT NULL,
  action_cs        VARCHAR2(2000),
  action_en        VARCHAR2(2000),
  expected_cs      VARCHAR2(2000),
  expected_en      VARCHAR2(2000),
  framework_hint   VARCHAR2(32),
  assertion_lib_id NUMBER REFERENCES ASSERTION_LIBRARY(id),
  is_decision_point NUMBER(1),
  row_version      NUMBER DEFAULT 0,
  created_at       TIMESTAMP DEFAULT SYSTIMESTAMP,
  updated_at       TIMESTAMP DEFAULT SYSTIMESTAMP,
  comments_kp_en   VARCHAR2(2000),
  CONSTRAINT uk_test_step_tc_ord UNIQUE (tc_id, ordinal)
)
```

Update Oracle ERD `_config/BOURACKA-ORACLE-ERD-v0.1-EN.md` to include this entity in v0.2 of the ERD.

Indices: `(tc_id, ordinal)` for step preview; `(step_code)` for bug lookup.

---

## 8. Open questions for KP review

| # | Question | Default if no answer |
|---|----------|---------------------|
| Q-V015-1 | Should `step_code` use `STP-<tc>-<NN>` or `<tc>-S<NN>`? Both visible in TC card. | `STP-<tc>-<NN>` (more grep-friendly across logs) |
| Q-V015-2 | When a TC has 5 steps and a tester marks bug against step 3 → if KP later inserts a new step between 2 and 3, do step_codes renumber or stay frozen? | **Stay frozen** — codes are immutable post-creation; `ordinal` mutable, `step_code` not. |
| Q-V015-3 | Selenium step granularity needs custom listener. Is that scope-creep for v0.1.5 or v0.1.6? | **Defer to v0.1.6** — cypress + playwright cover ~90% of Kate's flows, selenium can fall back to TC-level reporting until then. |
| Q-V015-4 | Should step-level bugs auto-tag with the assertion that failed? | **Yes if** the run console captured the assertion ID; **no** if step was manual. |
| Q-V015-5 | Workbook patcher splits `steps_summary` by `\n` — but some TCs have multi-line single-step prose. Manual KP cleanup unavoidable? | **Yes** — patcher emits "best-effort split + flag for review" markers; KP walks them once. ~50 TCs × ~30s each = 25 min. |
| Q-V015-6 | FR-K-004 evidence path is a workbook string — but the underlying file lives under `runs/`. If a tester deletes a run folder, the bug card breaks. Policy? | **Server detects missing artefact and shows "(evidence not on disk)"** badge; bug card stays readable. v0.1.6 may add "evidence orphan" report. |
| Q-V015-7 | Should the screenshot modal allow annotation (draw arrow, add note) and save as a new artefact? | **No for v0.1.5** — read-only viewer. v0.1.6+ once Kate hits the limit. |
| Q-V015-8 | Video files for cypress can hit 30–80 MB per run. Acceptable on shared workbook? | Per-run yes (each run is its own folder). Cumulative — v0.1.6 housekeeper handles. |

---

## 9. Implementation order (when Kate's Round-1 verdict lands)

```
v0.1.5 build sequence (estimated 3 dev-days; was 2 before FR-K-004):

Day 1 morning:  tools/workbook-v0.4.3-to-v0.4.4.py patcher
                + 02e_TestSteps sheet template
                + 08_Bugs evidence_* column additions
                + Q-V015-* surfaced for KP review

Day 1 afternoon: KP review of patcher output (parallel) +
                bouracka_ui.workbook_io reads 02e_TestSteps with legacy fallback
                + dispatcher.copy_artefacts_to_canonical(run_id) helper

Day 2 morning:  /api/tcs/{tc}/steps endpoint
                + TC card "Steps" accordion (FR-K-002)
                + bug-edit form step dropdown (FR-K-001)
                + /api/bugs/{code}/evidence resolver (FR-K-004)

Day 2 afternoon: /api/runs/{id}/console templated view (FR-K-003)
                + StaticFiles route for artefacts (FR-K-004)
                + smoke tests for the 4 new endpoints
                + smoke test for workbook patcher idempotency

Day 3 morning:  Bug card evidence block (modal viewer, FR-K-004 UI)
                + cross-framework dispatcher tweak: copy on run completion
                + smoke test for at least 1 artefact roundtrip

Day 3 afternoon: v0.1.5 wheel build + HP Elite ZIP build
                + KATE-V0.1.5-RELEASE-CS.md (delta from v0.1.4)
                + smoke 28→38 tests assertion bump
```

Risk gate: §6.3 step-emission from harnesses. If selenium can't be made to emit step events in 1 hour, ship v0.1.5 with selenium-runs falling back to TC-level reporting (per Q-V015-3 default).

---

## 10. What's deferred to v0.1.6+

- Inline step editor in UI (currently tester edits XLSX → patcher round-trip)
- Step-level parameters (`02b_TC_Parameters.scope = "step"` instead of just TC)
- Step-level screenshots/traces auto-attach to bugs
- Multi-tenant locking on shared workbook (still single-tenant in v0.1.x, multi-tenant lands with Oracle migration)
- Selenium custom listener for step granularity

---

## 11. Refs

- Kate Round-1 feedback bundle — captured in v0.1.4 fix notes
- `_config/BOURACKA-DATA-STORE-EVOLUTION-PLAN-v0.1-EN.md` §2 (Test-Step as first-class is on the evolution roadmap)
- `_config/BOURACKA-ORACLE-ERD-v0.1-EN.md` (target ERD will include TEST_STEPS table in v0.2 of ERD doc)
- `_config/TEST-ANALYSIS-AND-DESIGN-DEEP-SESSIONS-PLAN-v0.1-EN.md` §D6c (Session 2 deep-session topic FR-K-001/002 deeper architectural review)
- `bouracka_ui/bouracka_ui/workbook_io.py` — reader to extend with `list_steps()` analogous to `list_tcs()`
- `bouracka_ui/bouracka_ui/static/design-tokens.css` — UI styling tokens for new accordion
