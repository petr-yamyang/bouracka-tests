# Sonnet brief — BRIEF-002: workbook_io readers + v0.1.5 endpoints

**Target Claude.** Sonnet 4.6 in Claude Code (terminal, stateless).
**Issued by.** Opus 4.7 session (Pete Y. + Claude), 2026-05-13.
**Branch.** `cp-supin-08-v0.1.5-readers` (create from the merged head of `cp-supin-07-v0.1.5-patcher` — i.e., AFTER Brief #001 merges).
**Estimated effort.** ~3–4 hours of Sonnet time.
**Reviewer.** Pete in Opus 4.7 session, after Sonnet returns the checklist in §10.
**Blocked by.** Brief #001 merged + `BOURACKA-TESTPLAN-v0.4.4.xlsx` exists in repo root.

---

## 1. Goal in one paragraph

With v0.4.4 workbook in hand (Brief #001's output), teach `bouracka_ui.workbook_io` to read the new `02e_TestSteps` entity, surface `steps_count` from `02_TestCases`, and resolve bug evidence paths from `08_Bugs.evidence_*`. Then expose four read endpoints on the FastAPI server so the v0.1.5 UI (next brief) has the data it needs. Keep a legacy fallback path so the readers still work against a v0.4.3 workbook (TCs return inferred steps from splitting `steps_summary` on newlines, bugs return empty evidence). Smoke-test count grows from 28 → 33.

---

## 2. Spec — read this BEFORE coding

Open and read these sections **in full**:

1. `_config/BOURACKA-UI-V0.1.5-DESIGN-NOTES-EN.md` §3 (the Test-Step schema you'll be reading)
2. `_config/BOURACKA-UI-V0.1.5-DESIGN-NOTES-EN.md` §4 (FR-K-001 API surface)
3. `_config/BOURACKA-UI-V0.1.5-DESIGN-NOTES-EN.md` §4a.5 (FR-K-004 API surface)
4. `_config/BOURACKA-UI-V0.1.5-DESIGN-NOTES-EN.md` §5 (FR-K-002 read-only steps)
5. The existing `bouracka_ui/bouracka_ui/workbook_io.py` — your starting point. Mirror its `_column_map` / `_safe_get` pattern when adding readers.
6. The existing `bouracka_ui/bouracka_ui/server.py` — read top-to-bottom to learn FastAPI patterns, error envelope shape, JSON response style.
7. `bouracka_ui/tests/test_smoke.py` — your starting point for the new tests.

When the spec and this brief disagree, the **spec wins** unless this brief explicitly overrides.

---

## 3. Inputs / outputs

### Inputs

- Workbook: `BOURACKA-TESTPLAN-v0.4.4.xlsx` (repo root, produced by Brief #001's patcher).
- Existing `bouracka_ui/bouracka_ui/` package.
- Existing run artefacts (none yet shipped from real runs — for testing, generate a synthetic `runs/r-test-001/artefacts/TC-CP-001/STP-TC-CP-001-01/screenshot.png` fixture).

### Outputs

- Updated `workbook_io.py` with three new readers.
- Updated `server.py` with four new endpoints.
- New test file or extended test_smoke.py with five new tests.
- Updated `bouracka_ui/__init__.py` __version__ → `0.1.5-dev0` (NOT a full v0.1.5 wheel — that's a later brief).
- Updated `CHANGELOG.md` with v0.1.5-dev0 entry.

---

## 4. File boundaries — what you may touch

### Create

- `bouracka_ui/tests/test_workbook_io_steps.py` — focused tests for the new readers.
- `bouracka_ui/tests/fixtures/synthetic-v0.4.4-mini.xlsx` — small fixture (mirror Brief #001's `synthetic-v0.4.3-mini.xlsx` plus the patcher's output schema). Generate programmatically.
- `bouracka_ui/tests/fixtures/runs/r-test-001/artefacts/TC-CP-001/STP-TC-CP-001-01/screenshot.png` — 1×1 transparent PNG, just for path-resolve tests.

### Modify

- `bouracka_ui/bouracka_ui/workbook_io.py` — add readers; do NOT change existing function signatures (other modules import them).
- `bouracka_ui/bouracka_ui/server.py` — add endpoints; do NOT change existing endpoints' response shapes.
- `bouracka_ui/bouracka_ui/__init__.py` — bump `__version__` to `"0.1.5-dev0"`.
- `bouracka_ui/tests/test_smoke.py` — add the five new smoke tests at the end; do NOT delete or weaken existing ones (the v0.1.4 `server_version=="0.1.4"` assertion becomes `server_version.startswith("0.1.5")`).
- `bouracka_ui/pyproject.toml` — bump `version = "0.1.5.dev0"`. PEP 440 format.
- `CHANGELOG.md` (repo root) — append v0.1.5-dev0 section.

### DO NOT touch

- `tools/` — Brief #001's work; out of scope here.
- `_config/` — specs, out of scope.
- `delivery/` — shipped artefacts; out of scope.
- `bouracka_ui/bouracka_ui/static/` — UI is the NEXT brief.
- `bouracka_ui/bouracka_ui/dispatcher.py` — FR-K-004 artefact-copy logic is the brief AFTER UI.
- `recon/`, `recon-harness/` — out of scope.

If you find a bug in existing `workbook_io.py` (e.g., a `_safe_get` edge case), **note it in checklist item 6** and do not silently fix it — it may have downstream consumers.

---

## 5. Functional requirements

### F-1. New reader `list_steps(tc_code: str | None = None) -> list[dict]`

Add to `workbook_io.py`. Pattern after the existing `list_tcs()` reader.

**Behavior**:

- If `tc_code` is None → return all steps across all TCs, sorted by `(tc_ref, ordinal)`.
- If `tc_code` is given → return only steps for that TC, sorted by `ordinal`.
- Use header-based column lookup (`_column_map`) — do NOT hardcode column indexes.
- Each returned dict has keys: `id`, `step_code`, `tc_ref`, `ordinal`, `action_cs`, `action_en`, `expected_cs`, `expected_en`, `framework_hint`, `assertion_lib_ref`, `is_decision_point`, `comments_KP_en`, `created_at`, `updated_at`, `notes`.

**Legacy fallback when `02e_TestSteps` sheet does NOT exist**:

- Read `02_TestCases.steps_summary` for the requested TC(s).
- Split by newline; for each non-empty line, synthesize a dict with `step_code = f"STP-{tc_code}-{ordinal:02d}"`, `action_cs = line`, all other fields empty/null.
- Set `notes = "(inferred from legacy steps_summary — workbook is pre-v0.4.4)"`.
- This is the BUG-K-001 tolerance pattern — never crash, always return something readable.

### F-2. Update `list_tcs()` to surface `steps_count`

Add `steps_count` key to each returned TC dict. Source:

- Primary: `02_TestCases.steps_count` column if present in workbook.
- Fallback when column missing (v0.4.3 workbook): count newline-split lines in `steps_summary`, return that integer.

Do NOT change any other keys in the existing return dict — downstream consumers depend on the current schema.

### F-3. New reader `get_step(step_code: str) -> dict | None`

Return the single step record matching `step_code`, or `None` if not found. Reuse `list_steps()` internally; this is a thin convenience wrapper.

### F-4. New reader `get_bug_evidence(bug_code: str) -> dict | None`

Return the visual-evidence record for a bug:

```python
{
    "bug_code": "BUG-K-001",
    "linked_tc_ref": "TC-CP-008",
    "linked_step_ref": "STP-TC-CP-008-03",   # or None
    "evidence_screenshot_path": "runs/r-2026-05-13-cypress-007/artefacts/TC-CP-008/STP-TC-CP-008-03/screenshot.png",
    "evidence_video_path": None,
    "evidence_trace_path": None,
    "evidence_capture_kind": "auto-from-fail",
    "evidence_capture_at": "2026-05-13T14:32:11+02:00",
    "screenshot_url": "/api/runs/r-2026-05-13-cypress-007/artefacts/TC-CP-008/STP-TC-CP-008-03/screenshot.png",
    "video_url": None,
    "trace_url": None,
    "screenshot_on_disk": True,    # actual file exists check
    "video_on_disk": False,
    "trace_on_disk": False,
}
```

`*_url` fields are built from `*_path` by prepending `/api/`. `*_on_disk` fields are computed by checking if the file exists on disk relative to `REPO_ROOT`. If a bug has no evidence at all, return None (not an empty dict).

Legacy fallback when `evidence_*` columns don't exist in `08_Bugs`: check legacy `screenshot_ref` and `trace_ref` columns; if non-empty, return a dict with `evidence_capture_kind = "manual-tester"` and `*_on_disk` computed.

### F-5. New endpoint `GET /api/tcs/{tc_code}/steps`

Returns list of step dicts (from F-1). 404 if TC doesn't exist. Empty list `[]` is valid (TC has no steps).

Response envelope (consistent with existing `/api/tcs`):

```json
{
  "tc_code": "TC-CP-008",
  "steps": [ {...}, {...} ],
  "count": 5
}
```

### F-6. New endpoint `GET /api/steps/{step_code}`

Returns single step dict. 404 if step doesn't exist.

### F-7. New endpoint `GET /api/bugs/{bug_code}/evidence`

Returns the evidence dict from F-4. 404 if bug doesn't exist. 200 with `null` body if bug exists but has no evidence (not 404 — the bug is real, the evidence is just absent).

### F-8. New StaticFiles route `/api/runs`

Serve files from the `runs/` directory at the repo root. Use FastAPI's `StaticFiles`. Must support HTTP Range headers (for video seeking). Mount at `/api/runs` so the URL `/api/runs/r-XYZ/artefacts/TC-X/STP-X-01/screenshot.png` resolves to `<REPO_ROOT>/runs/r-XYZ/artefacts/TC-X/STP-X-01/screenshot.png`.

Security gate: the StaticFiles mount must NOT allow `..` path traversal escape from `runs/`. FastAPI's `StaticFiles` handles this by default but verify with a smoke test (§F-13).

If `<REPO_ROOT>/runs/` doesn't exist yet (no runs have happened), still mount the route — it will just 404 every request. Don't crash on import.

### F-9. Update `__version__` to `0.1.5-dev0`

In both `bouracka_ui/__init__.py` (string `__version__`) and `bouracka_ui/pyproject.toml` (PEP 440 → `0.1.5.dev0`). They differ by a dot — that's intentional, PEP 440 vs human-readable.

### F-10. Update CHANGELOG.md

Append a `## v0.1.5-dev0 (2026-05-13)` section with:

- New `list_steps()`, `get_step()`, `get_bug_evidence()` workbook readers
- New endpoints: `GET /api/tcs/{tc_code}/steps`, `GET /api/steps/{step_code}`, `GET /api/bugs/{bug_code}/evidence`
- New StaticFiles mount: `/api/runs/*` for evidence artefact serving
- Legacy fallback paths preserved for pre-v0.4.4 workbooks
- Smoke tests: 28 → 33

Mark as "dev0 — not for Kate, not for SUPIN. Internal-only build for v0.1.5 development."

---

## 6. Smoke test additions (28 → 33)

Add these five to `bouracka_ui/tests/test_smoke.py`:

```python
def test_api_tcs_steps_returns_list(client):
    """F-5: GET /api/tcs/{tc}/steps returns list of steps for known TC."""
    r = client.get("/api/tcs/TC-CP-008/steps")
    assert r.status_code == 200
    j = r.json()
    assert j["tc_code"] == "TC-CP-008"
    assert isinstance(j["steps"], list)
    assert j["count"] == len(j["steps"])
    assert j["count"] >= 1   # post-patcher TCs always have ≥1 step

def test_api_tcs_steps_unknown_tc_returns_404(client):
    """F-5: unknown tc_code returns 404."""
    r = client.get("/api/tcs/TC-DOES-NOT-EXIST/steps")
    assert r.status_code == 404

def test_api_steps_by_code(client):
    """F-6: GET /api/steps/{step_code} returns single step."""
    # First learn a real step_code by listing
    r = client.get("/api/tcs/TC-CP-008/steps").json()
    step_code = r["steps"][0]["step_code"]
    r2 = client.get(f"/api/steps/{step_code}")
    assert r2.status_code == 200
    assert r2.json()["step_code"] == step_code

def test_api_bugs_evidence_no_evidence_returns_null(client):
    """F-7: bug with no evidence returns 200 + null body."""
    # Workbook may have zero bugs; if so skip
    bugs = client.get("/api/bugs").json()
    if not bugs:
        pytest.skip("workbook has no bugs to test evidence resolver")
    bug_code = bugs[0]["item_code"]
    r = client.get(f"/api/bugs/{bug_code}/evidence")
    assert r.status_code in (200, 404)   # 200+null OR 404 acceptable per spec

def test_runs_staticfiles_path_traversal_blocked(client):
    """F-8: StaticFiles must reject .. escapes."""
    r = client.get("/api/runs/../../../etc/passwd")
    assert r.status_code in (404, 403)
```

Also update the existing version assertion:

```python
def test_health_endpoint_reports_version(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    j = r.json()
    # was: assert j["server_version"] == "0.1.4"
    assert j["server_version"].startswith("0.1.5")
```

---

## 7. Run-locally CLI smoke (do this before pasting back the checklist)

```bash
# from bouracka_ui/
pip install -e .
pytest tests/ -v
bouracka-ui --no-browser &
sleep 2
curl -s http://127.0.0.1:8424/api/health | python -m json.tool
curl -s http://127.0.0.1:8424/api/tcs/TC-CP-008/steps | python -m json.tool
curl -s http://127.0.0.1:8424/api/steps/STP-TC-CP-008-01 | python -m json.tool
# kill the bg server
```

If any of those curl outputs looks wrong (wrong keys, wrong status), fix BEFORE handoff. Don't paste a checklist with broken endpoints.

---

## 8. Risk gates — STOP and report if you hit any of these

1. **Schema-spec ambiguity.** Same rule as Brief #001.
2. **`02e_TestSteps` sheet missing AND legacy fallback can't synthesize steps for a TC** (e.g., `steps_summary` is also empty). Don't return an empty list silently — emit a structured warning to server logs.
3. **`StaticFiles` mount conflicts with an existing route** on `/api/runs`. Don't shadow existing endpoints.
4. **Performance** — if `list_steps()` against the real v0.4.4 workbook takes more than 200 ms for a single TC, stop and discuss. The reader is called on every TC card render.
5. **CHANGELOG.md has a non-standard format** that doesn't match your append pattern. Match the existing top-of-file convention; don't reformat the whole file.
6. **`bouracka_ui/__init__.py` has no `__version__` attribute** today. If so, ADD one. Don't infer from pyproject only.

Any of these → halt on a WIP branch, return §10 marked "BLOCKED — see item N".

---

## 9. Don't-go-beyond markers

- **Do not implement the UI** (step accordion, evidence modal, run console). That's Brief #003.
- **Do not implement dispatcher artefact-copy** (FR-K-004 §4a.7). That's Brief #004.
- **Do not implement step-emission listeners** for the harnesses. Deferred to v0.1.6.
- **Do not build a v0.1.5 wheel or HP Elite ZIP.** That's the final brief in the v0.1.5 chain.
- **Do not modify the dispatch logic** (real vs mock).
- **Do not "improve" `list_tcs()` beyond adding `steps_count`** — it's a stable contract.

---

## 10. Return checklist — paste back to Pete when done

1. **Branch name + commit SHA(s)** you created.
2. **Files changed** — list (created / modified) with line counts.
3. **Test results** — `pytest bouracka_ui/tests/ -v` output, full pass list.
4. **Curl smoke output** — paste the four `curl ... | json.tool` blocks from §7.
5. **Legacy-fallback proof** — run the readers against v0.4.3 workbook (rename v0.4.4 aside temporarily); confirm `/api/tcs/TC-CP-008/steps` still returns inferred steps with `notes` flag. Paste the response.
6. **Any bugs / surprises found that are OUT OF SCOPE** — see §4 closing paragraph.
7. **Deviations from this brief** with one-sentence justifications.
8. **Open questions** for Brief #003 (UI implementation). Likely candidates: which CSS approach for the accordion; whether the evidence modal should support keyboard navigation v0.1.5 or defer.

---

## 11. Quick-reference: spec sections by file/line

| Brief item | Spec ref |
|------------|----------|
| §F-1 list_steps schema | DESIGN-NOTES §3.1 table |
| §F-1 legacy fallback | brief decision (BUG-K-001 tolerance pattern) |
| §F-2 steps_count | DESIGN-NOTES §3.2 (denormalized preview) |
| §F-4 evidence dict shape | DESIGN-NOTES §4a.3 + §4a.5 |
| §F-5/6/7 endpoint shape | DESIGN-NOTES §4.2 + §4a.5 |
| §F-8 StaticFiles security | DESIGN-NOTES §4a.5 (Range support); brief decision (traversal check) |

---

## 12. Acceptance — when is this brief "done"?

- All 33 smoke tests pass (`pytest bouracka_ui/tests/ -v`).
- §7 curl smoke produces sensible output for all 4 endpoints.
- Legacy fallback (§F-1) demonstrated against v0.4.3.
- `__version__` reads `0.1.5-dev0` from `/api/health`.
- CHANGELOG.md has the v0.1.5-dev0 entry.
- Branch `cp-supin-08-v0.1.5-readers` has clean commits.
- Return checklist §10 pasted to Pete.

Then Pete reviews in Opus 4.7 session. Likely follow-ups: Brief #003 (UI for FR-K-001/002/004), Brief #004 (dispatcher artefact-copy for FR-K-004), Brief #005 (v0.1.5 wheel + HP Elite ZIP + Kate release notes).

---

**End of BRIEF-002.**
