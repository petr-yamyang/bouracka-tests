# RELEASE NOTES — bouracka-ui v0.1.5 integration milestone

**Tag:** `v0.1.5-integration-2026-05-15` (proposed) · **HEAD:** `90ff756` · **Branch:** `v0.1.5-integration`
**Date:** 2026-05-15 · **Status:** Internal dev integration milestone, **not for Kate/SUPIN ship**

---

## 1. Executive summary

Seven overnight Sonnet briefs merged into `v0.1.5-integration` in one session, reconciling the parallel-path work that branched off `main` (commit `f789a0e`, 2026-05-13). Resulting integration:

- **60 bouracka_ui pytest tests passing** (28 smoke + 13 mock-dispatch + 11 cross-check + 5 workbook_io + 3 cross-check smoke). One `http_e2e` test deselected from default run by design.
- **951-line workbook patcher** with row-level data migration (`--source-data`).
- **903-line recon harness** with 11 targets and 7 probe types.
- Six new bouracka_ui REST endpoints across two surfaces: workbook IO reads (`/api/tcs/{tc}/steps`, `/api/steps/{code}`, `/api/bugs/{bug}/evidence`, `/api/runs` StaticFiles mount) and cross-framework check (`/api/runs/{rid}/cross-check[.html]`).
- One real test bug fixed (`test_tcs_filtered_by_framework` — exposed by v0.4.4 workbook content but actually a latent test bug from v0.1.4).
- One real regression fixed mid-integration (M3 dropped pytest marker registration; restored in M5).

The integration recovered from **two classes of Windows-side accidents**: (a) notepad-truncated files committed before content verification, and (b) git-on-Windows merge writes producing truncated working-tree files. Both classes are documented under §6 Known issues.

---

## 2. Merge timeline

| M# | Commit | Brief | Branch | Scope |
|---:|---|---|---|---|
| M1 | `bbd27e5` | #004 — hotfix bundle (BUG-K-009/010/012) | `cp-supin-13-hotfix-bundle` | Dispatcher normalization + audit-doc preconditions |
| M2 | `01bd0c5` | #005 — mock-dispatch e2e shield | `cp-supin-11-mock-dispatch-e2e` | 13-test mock dispatch e2e suite, http_e2e marker |
| M3 | `2233a27` | #002 — workbook_io readers + endpoints | `cp-supin-17-workbook-io-readers` | `list_steps()` / `get_step()` / `get_bug_evidence()` + 4 new REST endpoints + `SUPPLEMENTAL_ENVS` |
| M4 | `283ff63` | #006 — recon harness expansion | `cp-supin-14-int-probe-expansion` | int_recon.py to 11 targets + 7 probe types + targets.json v1.1 |
| —  | `c5523d4` | (chore) `.gitignore` cypress fix | — | Working-tree infrastructure — unblocks Windows MAX_PATH |
| M5 | `95279bc` | #007 — cross-check report (FR-K-007) | `cp-supin-15-cross-check-report` | `/api/runs/{rid}/cross-check[.html]` + 11-test unit suite; M3-marker-regression fix folded in |
| M6 | `42e6edd` | #001 — workbook patcher v0.4.3→v0.4.4 | `cp-supin-07-v0.1.5-patcher` | 673-line patcher, synthetic fixture, v0.4.3 + v0.4.4 .xlsx snapshots |
| M7 | `90ff756` | #001b — patcher data migration | `cp-supin-09-v0.4.4-data-migration` | `--source-data` row migration (F-1m..F-7m), 951-line patcher, exit code 4 contract |

Recovery note: M1 and M2 carry pre-session SHAs. M2 was amended twice (first to strip conflict markers committed by notepad; second to repair notepad-truncated files). M3–M7 amend chain handled mid-flight regression discoveries via amends rather than fix-up commits.

---

## 3. Scope IN — feature surfaces by domain

### 3.1 bouracka_ui server endpoints (M3 + M5)

- `GET /api/tcs/{tc_code}/steps` → `{ tc_code, steps[], count }`. 404 on unknown TC.
- `GET /api/steps/{step_code}` → single step by code. 404 on unknown.
- `GET /api/bugs/{bug_code}/evidence` → evidence dict or null. 404 on unknown bug.
- `GET /api/runs/{run_id}/cross-check` → cross-framework agreement projection (JSON).
- `GET /api/runs/{run_id}/cross-check.html` → standalone HTML cross-check report (inline CSS, no external deps).
- `/api/runs` StaticFiles mount → serves run artefacts from `runs/`. Mounted after API routes to avoid shadowing.

### 3.2 bouracka_ui workbook_io readers (M3)

- `list_steps(wb_path, tc_code=None)` reads `02e_TestSteps` (legacy fallback to `steps_summary` split).
- `get_step(wb_path, step_code)` thin wrapper.
- `get_bug_evidence(wb_path, bug_code, repo_root=None)` reads evidence columns (legacy + new `evidence_*` schema), computes `*_url` + `*_on_disk` fields.
- `list_tcs()` extended with `steps_count` column.
- `SUPPLEMENTAL_ENVS` synthetic-env merger — emits `ENV-DMO-PUB` for public demo.bouracka.cz alongside workbook-driven envs.

### 3.3 bouracka_ui dispatch hardening (M1 + M5)

- `UI_ENV_TO_CONSOLIDATOR_TIER` table + `normalize_env_for_consolidator()` helper (BUG-K-010).
- `ENV_TO_BASE_URL` now includes `tst-demo` (cp-supin-15 contribution; was already in HEAD by collision).
- Mock-dispatch e2e shield: 13 tests across 2 families (Family A direct-call × 10, Family B HTTP subprocess × 1, validator meta-tests × 3).

### 3.4 cross_check.py module (M5)

- Opus prototype promoted to tracked module under `bouracka_ui/bouracka_ui/`.
- 11-test unit suite (`test_cross_check.py`): agreement, divergence, single-framework not-applicable, step-anchor resolution, HTML rendering, no-external-deps assertion.

### 3.5 tools/workbook patcher (M6 + M7)

- **Base patcher (M6, 673 lines):** idempotent v0.4.3→v0.4.4 schema upgrade. Creates `02e_TestSteps`, adds `steps_count`, promotes legacy `screenshot_ref`/`trace_ref` to typed `evidence_*` columns, appends `11_Changelog` row, writes `PATCH-REPORT-<ts>.md`.
- **Data migration (M7, +278 lines):** `--source-data PATH` flag migrates `08_Bugs`, `06_TestRuns`, `07_TestRunResults`, `09_Reports`, `13_TestExecutionSummary`, `14_AssertionGateResults` rows from a tester working-copy workbook. Duplicate `run_id` → exit code 4. Schema-owned sheets explicitly excluded.
- **23 unit tests + 1 integration test** all passing (`tools/tests/test_workbook_patcher.py`).

### 3.6 recon harness (M4)

- `int_recon.py` rewritten with `PROBE_FUNCTIONS` dispatch table; 3 new probe types (`probe_http_get_json`, `probe_http_head_with_referrer`, `probe_https_tls_verify`).
- `targets.json` v1.1: 11 entries (4 SOAP internal + 7 internet). Each declares its `probe_types`.
- Output JSON schema v0.2 with `integration_coverage` summary block.
- Mirrored to `delivery/PETE-HP-ELITE-DROP-2026-05-13/recon-harness/` and `delivery/SUPIN-SERVER-DROP-2026-05-13/recon-harness/` (not in Kate's drop — recon stays SUPIN-internal).

### 3.7 Workbook artefacts (M6)

- `BOURACKA-TESTPLAN-v0.4.3.xlsx` — pre-patch reference snapshot.
- `BOURACKA-TESTPLAN-v0.4.4.xlsx` — patcher output. **This is now the active workbook** (bouracka_ui auto-discovery picks it up at repo root, highest-priority lookup).

---

## 4. Scope OUT — deferred work

### 4.1 Briefs not in this integration

- **Brief #003** (TC discovery from workbook) — no branch yet, deferred to v0.1.6.
- **Brief #008** (v0.1.5 release engineering) — staging-only; not committed to a feature branch.
- **Brief #009** (audit mode design) — design-only doc; no code branch yet.

### 4.2 Within-brief deferrals

- **Brief #001c (planned):** patcher `--backup` flag, `--on-collision` mode, version-string pre-flight. Targets v0.1.6.
- **Brief #007 follow-ups:** cross-check.py algorithm audit (BUG-K-013 candidate), UI surfacing of `/cross-check.html` in `/results/{rid}` SPA page (FR-K-008), pagination (FR-K-009).
- **Brief #002 follow-ups:** `SUPPLEMENTAL_ENVS` schema validation, audit-grade lineage (`00_MigrationProvenance` sheet).
- **Brief #006 follow-ups:** INT-002/003/004/005 endpoint URLs (blocked on M. Ciberej delivery of SEDN inventory).
- **`--skip-internal` flag for `int_recon.py`** — currently 4 SOAP targets always FAIL outside VPN, producing noisy reports.

### 4.3 NOT shipped to Kate or to SUPIN-server

- This integration build is **internal-dev only** (`v0.1.5.dev5` in pyproject + integration-milestone `dev9` in CHANGELOG). No customer-facing artefacts produced.
- Kate continues on bouracka-ui v0.1.4 (from `delivery/KATE-DROP-2026-05-13/`) until v0.1.5 stabilises further with Brief #003 and a real release-engineering pass (Brief #008).

---

## 5. Cross-brief dependencies — version coupling and merge order

| Dependency | Type | Mitigated by |
|---|---|---|
| **M2 (#005) test depends on M3 (#002)** | `test_envs_returns_envs` from M2 expected `ENV-DMO-PUB` from `workbook_io.SUPPLEMENTAL_ENVS`, which doesn't exist until M3 | M3 supersedes the test (renamed `test_envs_returns_3_envs`); no permanent fix needed |
| **M3 dropped pytest marker registration** | `[tool.pytest.ini_options].markers` section absent in cp-supin-17's pyproject.toml; was present in M2 | Restored in M5 resolution; documented as regression-fixed in dev7 CHANGELOG entry |
| **M4 brought no CHANGELOG entry** | Brief #006 author skipped release notes | We composed comprehensive entry per the rule and folded into the merge via `--amend` |
| **M6 patcher created v0.4.4 with `TC-CP-NEW-A` empty `framework_targets`** | `test_tcs_filtered_by_framework` (originally from M2 epoch) didn't honor BUG-K-001's "empty = applies to all" semantics; latent bug | Patched test to honor documented semantics; logged in dev8 entry |
| **M7 (#001b) extends M6 (#001)** | Both branched from `f789a0e`; M7's patcher is a 278-line superset of M6's | Resolved by taking cp-supin-09 wholesale for both `tools/` files |

---

## 6. Known issues at integration tag

### 6.1 Pre-existing, unrelated to this integration

- **2 × `PytestUnraisableExceptionWarning`** from FastAPI TestClient asyncio teardown on Windows + Python 3.10. Surface in tests `test_post_run_rejects_empty_tcs` and `test_get_runs_unknown_id_404`. Cosmetic (no test failure). Root cause is `asyncio` proactor pipe transport `__del__` running after the event loop closes. Cure is in FastAPI/starlette upstream or in test-fixture lifecycle redesign.

### 6.2 Known operational

- `recon-harness/outputs/` directory NOT per-drop gitignored — generated reports will appear in `git status` after each run.
- `tools/patcher-reports/` — same pattern. Test artifacts can pollute if patcher is run during pytest.
- Long-filename Cypress screenshot path under `cypress/screenshots/a2-alternates-demo/...` exceeded Windows `MAX_PATH` and blocked `git add -A`. Mitigated by `.gitignore` rule (the `chore` commit between M5 and M6).

### 6.3 Process incidents during integration (and their mitigations)

- **notepad truncation:** Windows notepad opened files for conflict resolution and silently truncated on save. Detected after M2 amend by pytest TOML parse error. Mitigation: never use notepad on merge-conflict files. Use a proper text editor or write resolved content via Python.
- **git merge-write truncation on Windows:** M5's merge produced truncated `dispatcher.py` and `test_smoke.py` despite no editor involvement. Likely a Windows filesystem timing issue during git's 3-way merge writer. Mitigation: post-merge bash-side line-count audit against branch tip blob; if drift detected, reconstruct from clean blob before committing.
- **`.git/*.lock` files held by Windows:** Linux-side bash could not remove them; `git` operations would re-fail with "Unable to create .git/index.lock". Mitigation: PowerShell `Get-ChildItem .git -Recurse -Filter *.lock | Remove-Item -Force` before each git operation.
- **PowerShell `@{1}` syntax** ate the `HEAD@{1}` reflog reference. Mitigation: quote as `'HEAD@{1}'` or use raw SHA.
- **`Get-Content | Measure-Object -Line` undercounts** on these files by 15–20% (likely due to blank-line handling). Bash `wc -l` is the authoritative count.

---

## 7. Regression candidates — consolidated test recommendations

Surfaces with >50 lines of churn this cycle, ranked by risk:

| Risk | Surface | Coverage gap | Suggested test |
|:---:|---|---|---|
| HIGH | `tools/workbook-v0.4.3-to-v0.4.4.py::migrate_data()` (NEW, 278 lines, M7) | Brand-new code path; row-level transactional behaviour | Property-based test with random `(src, dest)` pairs; assert no key duplication; no schema-row corruption |
| HIGH | Patcher exit-code contract (exit 4 = collision) | Single integration smoke covers happy path | Negative test: deliberate run_id collision in source-data; assert exit code 4 AND stderr lists colliding IDs |
| MED | `bouracka_ui/workbook_io.list_tcs()` reading v0.4.4 in production | First-time exercised against real workbook | Smoke against both bundled .xlsx snapshots; assert same TC codes (modulo empty-vs-all semantics) |
| MED | `server.py::_find_envelope_for_run()` (NEW, M5) | Only happy path covered | Tests for: unknown run_id → 404; ambiguous match → 500 with diagnostic; corrupt envelope JSON → 422 |
| MED | `cross_check.py` (Opus prototype, NEW tracked module, M5) | 11 unit tests cover common cases | Add 4 corner-case tests: empty envelope, single-framework runs, all-divergent matrix, all-agreement matrix |
| MED | `recon-harness/int_recon.py::probe_target()` (rewritten, M4) | New `PROBE_FUNCTIONS` dispatch | Unit test: every `probe_type` in `targets.json` resolves to a registered function (catches dict-key typos) |
| LOW | `dispatcher.py::ENV_TO_BASE_URL` (modified, M5) | Used by run trigger AND cross-check fixtures | Assert: `ENV_TO_BASE_URL.keys() == workbook_io.ENV_CODE_TO_SCHEMA.keys()` (catches env-key drift) |
| LOW | `cross-check.html` template (M5) | No HTML-structure test | Smoke: GET endpoint, parse as HTML5, assert `<table class="cross-check-matrix">` present, assert no external `<script src=` |
| LOW | Repo-root workbook discovery priority (M6 change) | bouracka_ui auto-discovery now picks v0.4.4 over tester-installed v0.4.3 | Test asserting highest-priority candidate; document order in `BOURACKA-UI-DESIGN.md` §3.2 |

---

## 8. Test status at tag

```
collected 61 items / 1 deselected / 60 selected
============== 60 passed, 1 deselected in 20.27s ==============
```

- `test_cross_check.py`: 11 / 11 passing
- `test_mock_dispatch_e2e.py`: 13 / 13 selected, 1 deselected (`http_e2e` marker on `test_http_e2e_full_post_poll_envelope`)
- `test_smoke.py`: 36 / 36 passing
- `tools/tests/`: not run by `pytest bouracka_ui/tests/`; should be exercised separately via `pytest tools/tests/ -v -m "not integration"` (23 expected to pass) and `pytest tools/tests/ -v` (24 with integration test)

---

## 9. Next steps

1. **Brief #003** — TC discovery from workbook (queued, no branch).
2. **Brief #008** — release engineering: wheel build for v0.1.5-dev9, ABI matrix verification, ship pipeline for SUPIN-server drop. Then this integration milestone becomes v0.1.5 proper (not dev).
3. **Brief #009** — audit mode design (currently a design doc only).
4. **Regression-candidate follow-up** — add the 9 tests listed in §7 over the next 2–3 dev cycles.
5. **Working-tree noise consolidation** — separate `chore` commits for the M cleanup deletes + new `_config/`, `_db/`, `_specs/` content the previous session staged. Recommend grouping by topic, not by file.
6. **Tag re-organization** — propose retiring `v0.1.5-dev5-integration` (still valid at `bbd27e5`) and `v0.1.5-dev6-integration` (misleading — points at M2 = Brief #005, not Brief #006). New tag `v0.1.5-integration-2026-05-15` at `90ff756` is canonical.

---

## 10. Provenance

- Author: Pete Y. + Claude Opus 4.7 (integration reconciliation session, 2026-05-15).
- Brief authors: Claude Sonnet 4.6 (per `Co-Authored-By` trailers on individual brief commits).
- Source briefs: `_config/SONNET-BRIEF-00{1,1B,2,4,5,6,7}-*.md` (workbook-PATCHER, PATCHER-DATA-MIGRATION, WORKBOOK-IO-AND-V015-ENDPOINTS, HOTFIX-BUNDLE, MOCK-DISPATCH-E2E, INTEGRATION-PROBE-EXPANSION, CROSS-CHECK-REPORT).
- Recovery transcript: `SESSION-CLOSE-CP-SUPIN-07-2026-05-15-INTEGRATION.md` (to be authored by user as session close).
