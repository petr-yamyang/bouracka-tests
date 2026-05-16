# Sonnet brief — BRIEF-009: Audit/Inspection mode (FR-K-008)

**Target Claude.** Sonnet 4.6 in Claude Code (terminal, stateless).
**Issued by.** Opus 4.7 session (Pete Y. + Claude), 2026-05-15.
**Branch.** `cp-supin-12-audit-mode` (create from current `main` head — coordinate with Sonnet's in-flight branches; do not collide).
**Estimated effort.** ~8–10 hours of Sonnet time across server + UI + 3 framework hooks.
**Reviewer.** Pete in Opus 4.7 session, after Sonnet returns §10 checklist.
**Blocked by.** Brief #002 (workbook_io readers — for `02e_TestSteps` reading) AND Brief #003 (binding columns + `list_tcs` filter logic). Audit run dispatch reads the same binding columns as regular dispatch.

---

## 1. Goal in one paragraph

Build a second execution rail in bouracka-ui called **Audit/Inspection mode**: tester picks exactly one TC + one framework + one environment, watches the test execute in slow motion in a separate framework-owned browser window, sees real-time step progress + assertion log in bouracka-ui's `/audit` page, optionally saves the recording as video or slideshow to a tester-selected folder via a native Windows folder picker. Audit runs **never** write to `06_TestRuns`, never produce a v0.1 envelope, never affect any test-set metrics. Pure observability. Implementation lives in `audit_dispatcher.py` (parallel to `dispatcher.py`), `/audit` route in app.js, and three framework-specific slow-mo hooks (cypress / playwright / selenium).

---

## 2. Spec — read this BEFORE coding

Open and read in full:

1. **`_config/AUDIT-MODE-DESIGN-v0.1-EN.md`** — the authoritative design contract. All five Q-K-008-* decisions locked in there.
2. `bouracka_ui/bouracka_ui/dispatcher.py` — regular dispatcher; you mirror its async + registry pattern but do NOT modify it.
3. `bouracka_ui/bouracka_ui/server.py` — current endpoint patterns; you add audit endpoints in the same style.
4. `bouracka_ui/bouracka_ui/workbook_io.py` — `list_tcs()` returns binding columns post-Brief-#003; you use those to construct framework-specific invocations.
5. `bouracka_ui/bouracka_ui/static/app.js` — current UI routing; you add `/audit` route in same style.
6. `_config/SONNET-BRIEF-003-TC-DISCOVERY-FROM-WORKBOOK.md` — binding columns reference; audit-mode dispatch reads same columns.

When design doc and this brief disagree, **the design doc wins**. Note any drift in §10 item 6.

---

## 3. Inputs / outputs

### Inputs

- Repo state with Brief #002 + Brief #003 merged (workbook_io has `list_steps`, `list_tcs` returns binding columns, `02e_TestSteps` exists in v0.4.5 workbook).
- bouracka_ui v0.1.5-dev2 or later (post-Brief #005 + #003).
- Framework prereqs assumed: Node installed (for cypress/playwright), Python selenium package installed in venv. If absent, audit mode falls back to MOCK with prominent banner (see §F-12).

### Outputs

1. `bouracka_ui/bouracka_ui/audit_dispatcher.py` — new module, ~600 lines.
2. New endpoints in `bouracka_ui/bouracka_ui/server.py` — 6 new routes per §5 of design.
3. `/audit` route + components in `bouracka_ui/bouracka_ui/static/app.js` + `static/index.html` + `static/style.css`.
4. Framework hooks: 1 cypress config addition, 1 playwright config addition, 1 selenium conftest extension.
5. New tests in `bouracka_ui/tests/test_audit_mode_e2e.py` (mirrors the FR-K-005 pattern).
6. `runs/audit/.gitkeep` so the directory exists.
7. CHANGELOG.md v0.1.5-dev3 entry.

---

## 4. File boundaries

### Create

- `bouracka_ui/bouracka_ui/audit_dispatcher.py` — parallel dispatcher
- `bouracka_ui/tests/test_audit_mode_e2e.py` — mirrors `test_mock_dispatch_e2e.py` pattern
- `bouracka_ui/tests/fixtures/synthetic-audit-events.jsonl` — sample event log for unit tests
- `runs/audit/.gitkeep` — empty marker
- `bouracka_ui/bouracka_ui/static/audit.css` — IF audit-specific styles grow > 100 lines, extract here; otherwise inline in style.css

### Modify

- `bouracka_ui/bouracka_ui/server.py` — add 6 endpoints per §5.1 of design doc
- `bouracka_ui/bouracka_ui/static/app.js` — add `/audit` route + pre-launch picker + runtime split-pane
- `bouracka_ui/bouracka_ui/static/index.html` — add `<div id="audit-root">` mount point
- `bouracka_ui/bouracka_ui/static/style.css` — audit-page styles
- `bouracka_ui/bouracka_ui/__init__.py` — `__version__ = "0.1.5-dev3"`
- `bouracka_ui/pyproject.toml` — `version = "0.1.5.dev3"`
- `cypress/cypress.config.ts` — slow-mo hook reads `BOURACKA_AUDIT_SLOW_MO_MS` env var
- `playwright/playwright.config.ts` — `use.slowMo = parseInt(process.env.PLAYWRIGHT_SLOW_MO || "0", 10)`
- `selenium/conftest.py` — wrap WebDriver with `AuditSlowMoDriver` when `BOURACKA_AUDIT_SLOW_MO_MS` set
- `CHANGELOG.md` — append v0.1.5-dev3 entry

### DO NOT touch

- `bouracka_ui/bouracka_ui/dispatcher.py` — regular dispatcher; audit is PARALLEL not extension
- `tools/consolidate_results.py` — audit runs never go through consolidator
- `BOURACKA-TESTPLAN-v0.4.4.xlsx` / `v0.4.5.xlsx` — read-only canonical workbooks
- `_config/AUDIT-MODE-DESIGN-v0.1-EN.md` — read-only spec
- `delivery/` — out of scope
- `recon/` — out of scope

If you find a bug in `dispatcher.py` env-mapping (BUG-K-010), note in §10 item 6 — DO NOT fix here (separate hotfix brief).

---

## 5. Functional requirements

### F-1. `audit_dispatcher.py` skeleton

Module structure (matches §5.2 of design):

```python
class AuditDispatcher:
    _registry: dict[str, dict]  # audit_run_id → AuditRun entity (in-memory)
    _processes: dict[str, subprocess.Popen]  # audit_run_id → subprocess handle
    _event_queues: dict[str, asyncio.Queue]  # audit_run_id → SSE event queue

    async def start(self, tc, framework, env, slow_mo_ms=2000) -> str: ...
    async def control(self, audit_run_id, action) -> dict: ...   # pause/resume/stop
    async def save(self, audit_run_id, format, folder_path) -> dict: ...
    def list_runs(self) -> list[dict]: ...
    def get_run(self, audit_run_id) -> dict | None: ...
    async def stream_events(self, audit_run_id): ...   # async generator → SSE

# Module-level helpers
def generate_audit_run_id() -> str: ...
def _start_cypress_headed(spec_glob, env_url, slow_mo_ms, audit_run_id) -> subprocess.Popen: ...
def _start_playwright_headed(grep, env_url, slow_mo_ms, audit_run_id) -> subprocess.Popen: ...
def _start_selenium_headed(pytest_k, env_url, slow_mo_ms, audit_run_id) -> subprocess.Popen: ...
def _open_powershell_folder_dialog() -> str | None: ...   # native Win folder picker
```

`audit_run_id` format: `audit-<ISO-Z-timestamp-with-dashes>-<7hexchars>`, e.g. `audit-2026-05-15T15-32-08Z-9f4c1d2`.

### F-2. Three-way selection validation (server)

`POST /api/audit/runs` payload must have `tc`, `framework`, `env`. Validate **all three** are present and within allowed sets:

- `tc` ∈ `workbook_io.list_tcs()` codes (404 if not)
- `framework` ∈ `{"cypress", "playwright", "selenium"}` (422 if not)
- `env` ∈ `{"demo", "tst-demo", "tst", "uat", "prod-readonly"}` (422 if not)
- The TC's binding column for the chosen framework MUST be non-empty (422 with message "no `<framework>` binding for TC `<tc>`" if empty)

Return 422 errors with structured JSON `{detail: "...", missing: [...]}` so the UI can highlight which field is invalid.

### F-3. Slow-mo enforcement

Server sets framework-specific env vars before subprocess launch:

| Framework | Env var |
|-----------|---------|
| cypress | `BOURACKA_AUDIT_SLOW_MO_MS=2000` |
| playwright | `PLAYWRIGHT_SLOW_MO=2000` |
| selenium | `BOURACKA_AUDIT_SLOW_MO_MS=2000` |

Plus `BOURACKA_AUDIT_RUN_ID=<id>` for all frameworks (used by harness to emit events to a per-run event file). Plus standard env injection from regular dispatcher (`BOURACKA_BASE`, `PLAYWRIGHT_BASE_URL` etc.) — REUSE the helper from `dispatcher._build_env_inject` (do not duplicate logic; import).

### F-4. Step event emission

Each framework harness writes step events to `runs/audit/<audit_run_id>/events.jsonl` as one JSON object per line. Server tails this file and pushes events to SSE clients.

Event schema:

```json
{"ts": "2026-05-15T15:32:08.123Z", "type": "step_start", "step_idx": 0, "label": "Navigate to /"}
{"ts": "2026-05-15T15:32:10.456Z", "type": "step_end", "step_idx": 0, "status": "passed", "duration_ms": 2333}
{"ts": "2026-05-15T15:32:10.500Z", "type": "assertion", "label": "page title contains 'Bouracka'", "status": "passed"}
{"ts": "2026-05-15T15:32:15.100Z", "type": "paused"}
{"ts": "2026-05-15T15:32:18.200Z", "type": "resumed"}
{"ts": "2026-05-15T15:33:04.999Z", "type": "done", "status": "completed"}
```

Cypress harness emits via custom plugin `cypress/audit-event-emitter.js`. Playwright via custom reporter `playwright/audit-reporter.ts`. Selenium via conftest hook + per-step `time.sleep` + event-file writer.

### F-5. SSE endpoint `/api/audit/runs/{id}/stream`

```python
@app.get("/api/audit/runs/{audit_run_id}/stream")
async def stream_audit_events(audit_run_id: str):
    # Use sse-starlette (already in deps)
    async def event_generator():
        async for event in audit_dispatcher.stream_events(audit_run_id):
            yield {"event": event["type"], "data": json.dumps(event)}
    return EventSourceResponse(event_generator())
```

Client consumes via `EventSource` per §6.2 of design.

### F-6. Pause/resume/stop control

`POST /api/audit/runs/{id}/control` body `{action: "pause"|"resume"|"stop"}`:

- **pause**: Send `SIGSTOP` (POSIX) or `psutil.suspend()` (Windows) to the framework subprocess. Status → `"paused"`. Emit `paused` event.
- **resume**: Send `SIGCONT` / `psutil.resume()`. Status → `"running"`. Emit `resumed` event.
- **stop**: `subprocess.terminate()` → wait 5s → `subprocess.kill()` if still alive. Status → `"stopped"`. Emit `stopped` event. Preserve partial events.jsonl + any captured artefacts.

**Locked decision (Pete 2026-05-15):** add `psutil` to `bouracka_ui/pyproject.toml` dependencies. Cross-platform implementation:

```python
import psutil
p = psutil.Process(proc.pid)
p.suspend()   # pause — works on Windows + POSIX
p.resume()    # resume
p.terminate(); p.wait(timeout=5)   # graceful stop
if p.is_running():
    p.kill()   # force kill if terminate didn't take
```

This adds ~250 KB to the multi-ABI wheelhouse (acceptable noise vs current 11 MB). psutil is well-maintained, ABI-clean (pure C-ext wheel per ABI, available in cp310/cp311/cp312 win_amd64). Update `pyproject.toml` `dependencies = [..., "psutil>=5.9"]` AND the multi-ABI packager's `criticalDeps` sanity-check list to include psutil (so we catch missing wheels at build time).

### F-7. Save artefacts endpoint

`POST /api/audit/runs/{id}/save` body `{format: "video"|"slideshow"|"discard", folder_path: "..."}`:

- If `format == "discard"`: server deletes `runs/audit/<id>/video.mp4` if exists, leaves manifest + events.jsonl; returns `{written_path: null, bytes_written: 0}`.
- If `format == "video"`: requires framework's native video output. Cypress: `cypress/videos/<spec>.mp4` already exists. Playwright: `test-results/<test>/video.webm`. Selenium: NO native video in v0.1.5 → return 501 with message "selenium video not supported in v0.1.5; use slideshow". Move/copy to `folder_path/<audit_run_id>.mp4` (or `.webm` for playwright).
- If `format == "slideshow"`: extract per-step screenshots from framework output; generate `index.html` with screenshot+caption per step. Copy to `folder_path/<audit_run_id>/`.
- Fallback if `folder_path` empty or invalid: write to `runs/audit/<id>/` (server-side default).

### F-8. Folder picker endpoint

`GET /api/audit/folder-picker` — opens native Windows folder dialog via PowerShell:

```python
import subprocess
ps_script = """
Add-Type -AssemblyName System.Windows.Forms
$dialog = New-Object System.Windows.Forms.FolderBrowserDialog
$dialog.Description = "Select folder to save audit run artefacts"
if ($dialog.ShowDialog() -eq "OK") { Write-Output $dialog.SelectedPath }
"""
result = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script],
                         capture_output=True, text=True, timeout=120)
path = result.stdout.strip() if result.returncode == 0 and result.stdout else None
return {"selected_path": path}
```

On non-Windows platforms or PowerShell not on PATH: return `{"selected_path": null}` with status 200. UI then defaults to text-input.

### F-9. `/audit` page UI

Three states:

1. **Pre-launch picker** (default state — no active audit run):
   - TC dropdown populated from `/api/tcs`, filtered by selected framework's binding column non-empty
   - Framework radio (cypress / playwright / selenium)
   - Environment radio (demo / tst-demo / tst / uat / prod-readonly)
   - `[▶ Start audit run]` button disabled until all 3 selected
   - On click: POST `/api/audit/runs` → navigate to runtime state with `audit_run_id`

2. **Runtime state** (during run):
   - Header: TC code · framework · env · status · elapsed time
   - Left pane (40% width): step list (from `02e_TestSteps` for the TC) with current step indicated by ▶
   - Right pane (60% width): action log (auto-scroll, latest at bottom)
   - Controls: `[⏸ Pause]` `[⏹ Stop]` `[💾 Save (disabled until done)]`
   - SSE connection live → update step list + log

3. **Post-run state** (status = done | stopped | error):
   - Save modal: 3 radio (video / slideshow / discard) + folder input + `[Browse]` button (opens picker via F-8) + `[Save]` / `[Cancel]`
   - After save: navigate back to pre-launch picker

### F-10. Framework hooks

#### Cypress (cypress.config.ts)

```typescript
// Audit slow-mo + step emission
const auditSlowMoMs = parseInt(process.env.BOURACKA_AUDIT_SLOW_MO_MS || "0", 10);
const auditRunId = process.env.BOURACKA_AUDIT_RUN_ID || "";

if (auditSlowMoMs > 0 && auditRunId) {
  // (Plugin file: cypress/plugins/audit-event-emitter.js)
  // Subscribes to cypress:before:run, command:start, command:end, test:after:run
  // Writes JSONL events to runs/audit/<id>/events.jsonl
  // After each cy.* command, await ${auditSlowMoMs}ms
  setupNodeEvents(on, config) {
    require('./audit-event-emitter')(on, config, auditRunId);
  }
}
```

Plugin file creates the `runs/audit/<id>/` directory if missing and opens events.jsonl in append mode.

#### Playwright (playwright.config.ts)

```typescript
use: {
  slowMo: parseInt(process.env.PLAYWRIGHT_SLOW_MO || "0", 10),
  // ...existing config
},
reporter: process.env.BOURACKA_AUDIT_RUN_ID
  ? [['./audit-reporter.ts', { auditRunId: process.env.BOURACKA_AUDIT_RUN_ID }]]
  : 'json',
```

Custom reporter `playwright/audit-reporter.ts` implements `onTestBegin`, `onStepBegin`, `onStepEnd`, `onTestEnd`. Writes JSONL.

#### Selenium (selenium/conftest.py)

```python
import os, json, time
from datetime import datetime, timezone
from pathlib import Path

AUDIT_RUN_ID = os.environ.get("BOURACKA_AUDIT_RUN_ID", "")
SLOW_MO_MS = int(os.environ.get("BOURACKA_AUDIT_SLOW_MO_MS", "0"))
AUDIT_EVENTS_PATH = (
    Path(os.environ.get("BOURACKA_UI_REPO_ROOT", "."))
    / "runs" / "audit" / AUDIT_RUN_ID / "events.jsonl"
    if AUDIT_RUN_ID else None
)

def _emit(event_type, **kwargs):
    if AUDIT_EVENTS_PATH is None:
        return
    AUDIT_EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    event = {"ts": datetime.now(timezone.utc).isoformat() + "Z",
             "type": event_type, **kwargs}
    with AUDIT_EVENTS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

@pytest.fixture
def driver():
    raw = webdriver.Chrome()  # default headed
    if SLOW_MO_MS > 0:
        return AuditSlowMoDriver(raw, SLOW_MO_MS / 1000)
    return raw

class AuditSlowMoDriver:
    """Wraps webdriver to sleep + emit events after each call."""
    # ... (implementation per design §7.3)
```

### F-11. Tests (`bouracka_ui/tests/test_audit_mode_e2e.py`)

Mirror the FR-K-005 pattern. At minimum:

1. `test_post_audit_run_requires_three_params` — missing tc / framework / env → 422
2. `test_post_audit_run_with_invalid_framework_value` → 422
3. `test_post_audit_run_with_invalid_env_value` → 422
4. `test_post_audit_run_with_tc_without_binding_for_framework` → 422
5. `test_audit_run_lifecycle_in_mock_mode` — start (BOURACKA_UI_DISPATCH_MODE=mock returns canned events) → stream events → stop → save discard
6. `test_audit_run_save_video_writes_to_target_folder` — synthetic source video.mp4 in fixtures, save copies it
7. `test_audit_run_save_slideshow_generates_html_index` — output dir has index.html + step-N.png files
8. `test_audit_run_save_discard_leaves_no_artefacts_at_target` — folder remains empty
9. `test_audit_run_does_not_write_to_06_test_runs` — workbook 06_TestRuns row count unchanged
10. `test_audit_run_does_not_produce_envelope` — no `runs/cross-framework-*.json` created

Plus the existing 7+ tests from FR-K-005 stay green (don't break regular dispatch).

### F-12. Mock fallback when frameworks not installed

If `BOURACKA_UI_DISPATCH_MODE=mock` is set OR npx/python tooling unavailable, `audit_dispatcher.start()` runs a synthetic event sequence (canned step_start/step_end events with 2s delays between) and writes a fake `video.mp4` (1-byte placeholder) for save-flow testing. This lets the e2e tests run in sandbox without real browsers.

UI shows banner: `⚠ AUDIT-MOCK mode active — no real browser opened`.

### F-13. Version bumps + CHANGELOG

```
__version__ = "0.1.5-dev3"     # bouracka_ui/__init__.py
version = "0.1.5.dev3"         # pyproject.toml
```

CHANGELOG.md v0.1.5-dev3 section:

- FR-K-008: Audit/Inspection mode for test runs
- New module `audit_dispatcher.py` (parallel rail to regular dispatcher)
- 6 new endpoints `/api/audit/*`
- New `/audit` page with three-way selection (TC + framework + env)
- Framework slow-mo hooks: cypress / playwright / selenium
- Native PowerShell folder picker for artefact save
- Audit runs do NOT write to `06_TestRuns` (no test-set impact)

---

## 6. Idempotency

- Repeated `POST /api/audit/runs` for the SAME tc+framework+env starts NEW audit runs each time (no run-id reuse).
- Concurrent audit runs allowed? **Recommend NO for v0.1.5** — only one audit run at a time per server. Subsequent POSTs while one is running return 409 Conflict with `{active_run_id: "..."}`.
- Stopped run can be restarted (new audit_run_id).
- Save can be called only once per audit_run_id; second call returns 409 with existing artefact path.

---

## 7. CLI surface

No CLI changes. All audit interaction via HTTP API + browser UI.

---

## 8. Test plan

Per §F-11 above. Plus:

- All previous tests (especially `test_mock_dispatch_e2e.py` Family A + B) MUST stay green — audit mode is additive, regular dispatch unchanged.
- Smoke gate: `pytest bouracka_ui/tests/ -v -m "not http_e2e"` runtime stays under 10 seconds even with new audit tests added.
- Manual e2e: Pete on ThinkPad runs `pytest bouracka_ui/tests/test_audit_mode_e2e.py -v` AND opens `/audit` in browser, runs at least one real cypress audit against a TC, validates save→video roundtrip.

---

## 9. Risk gates — STOP and report

1. **Cypress plugin file (`cypress/plugins/audit-event-emitter.js`) doesn't fit the existing plugin convention.** Halt; show Pete the existing cypress.config.ts before adding the plugin.
2. **Playwright custom reporter signature changed in playwright 1.40+** — verify against installed playwright version; halt if API incompatible.
3. **Selenium `AuditSlowMoDriver` __getattr__ wrapping breaks existing tests** — namespace collisions, fixture interaction. Run selenium suite before declaring done; halt if regressions.
4. **`psutil.suspend()` not in deps** — flagged in §F-6. Decide: add psutil to wheelhouse OR ship 501 on Windows pause. Confirm with Pete before either path.
5. **`/audit` route conflicts with existing SPA route** — check app.js for existing `/audit` path. If exists, halt.
6. **PowerShell folder picker hangs the server** — folder dialog is modal and could block the event loop. Run in `asyncio.to_thread(...)` to isolate. If still hangs in test, halt.
7. **events.jsonl tail-read race** — server reads events.jsonl while harness writes. On Windows, file locks may prevent simultaneous read+write. Use append-only-no-lock pattern (open in `a` mode with O_APPEND, server uses inotify-style polling). If race observed, halt with reproducer.

---

## 10. Return checklist

1. Branch name + commit SHA(s).
2. Files changed (created / modified) with line counts.
3. Test results — `pytest bouracka_ui/tests/ -v` full pass list, including new test_audit_mode_e2e.
4. Manual e2e proof from Pete's ThinkPad — required: paste 3 SSE event excerpts captured during a real cypress audit against TC-CP-008 in tst-demo env.
5. Folder picker proof — screenshot or text showing the PowerShell dialog opening on ThinkPad.
6. Out-of-scope findings (include the BUG-K-010 env-mapping bug if observed).
7. Deviations from this brief with justifications.
8. Open questions — likely Q-K-008-pause-windows (psutil vs 501) needs Pete decision before merge.

---

## 11. Don't-go-beyond markers

- **Do not modify `dispatcher.py`** — audit is parallel rail
- **Do not modify `consolidate_results.py`** — audit doesn't go through consolidator
- **Do not write to `06_TestRuns`** — explicit rule
- **Do not implement step-forward/back controls** — v0.1.6
- **Do not implement configurable slow-mo speed** — v0.1.6
- **Do not implement multi-test or multi-framework audit** — Pete explicitly excluded
- **Do not implement bug-from-audit linkage** — bundle separately (Brief #009b candidate)
- **Do not "improve" the regular dispatcher** while you're in there
- **Do not modify workbook patcher / workbook_io** — those are Briefs #001b/#003 territory
- **Do not auto-install Node or selenium** in install runbook — BUG-K-009 is doc-only fix in Brief #004

---

## 12. Quick-reference

| Brief item | Spec ref |
|------------|----------|
| Three-way selection (TC+framework+env) | DESIGN §1 + §6.1 pre-launch picker |
| AuditRun data model | DESIGN §4 |
| 6 server endpoints | DESIGN §5.1 |
| Two-window layout | DESIGN §3 + §6 |
| Slow-mo per framework | DESIGN §7 |
| Persistence layout | DESIGN §8 |
| Workflow steps 1-13 | DESIGN §9 |

---

## 13. Acceptance — done when

- All §F-11 tests pass + previous tests stay green
- Manual ThinkPad e2e proof in §10 item 4 supplied by Pete
- `__version__` reads `0.1.5-dev3`
- CHANGELOG has v0.1.5-dev3 entry
- Branch has clean commits
- Return checklist §10 pasted

After Pete reviews, this lands in v0.1.5 release alongside Briefs #002, #003, #001b, #004, #005, #006, #007. v0.1.5 Kate-ship happens after ALL briefs return + Gate 0..3 of MAJOR-DEV-SESSION-PLAN green.

---

**End of BRIEF-009.**
