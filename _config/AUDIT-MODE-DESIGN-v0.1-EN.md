# Audit/Inspection mode for Test Runs — design v0.1 (FR-K-008)

**Date.** 2026-05-14.
**Authors.** Pete Y. + Opus 4.7.
**Status.** Design locked. Q-K-008-1..5 answered. Ready to translate to Sonnet Brief #009.
**Triggering use case.** Tester selects ONE test, ONE framework, watches it execute in slow motion with step-by-step annotations on a side panel, optionally saves the recording as video or slideshow. Pure observability — no impact on test sets, no result writes.

---

## 1. What we're building

A second execution rail in bouracka-ui alongside the regular dispatch path. Where regular runs are **about measurement** (verdict, parity, evidence for reports), audit runs are **about observation** (slow-motion playback, real-time annotation, optional recording, no metrics impact).

**Selection model — three parameters, always exactly one each:**

1. **TC code** — one workbook-authored test case (e.g., `TC-CP-008`)
2. **Framework** — one of cypress / playwright / selenium
3. **Environment** — one of demo / tst-demo / tst / uat / prod-readonly **(required selection — environment determines which deployment the test runs against; same TC produces different observability evidence depending on env)**

Never multi-TC, never multi-framework, never multi-env in a single audit run.

**Window layout**: two separate OS windows side-by-side. Window 1 = bouracka-ui audit page (step list + action log + controls). Window 2 = the framework's own visible browser (cypress headed, playwright headed, selenium with visible driver). Tester arranges them as they like.

**Slow-motion**: framework-level 2-second delay between actions (fixed in v0.1.5; configurable in v0.1.6 per Q-K-008-4).

**Controls**: ⏸ Pause (freezes playback) + ⏹ Stop (kills the audit run, preserves partial recording). Step-forward/back deferred to v0.1.6 per Q-K-008-5.

**Output**: at run end, tester chooses Save as Video (native MP4 from framework) or Save as Slideshow (per-step PNG sequence + HTML page with caption). Native Win folder picker via PowerShell shell-out (Q-K-008-2).

**Persistence**: artefacts written to `runs/audit/<audit_run_id>/`. NEVER written to `06_TestRuns` workbook sheet. Browsable via `/api/audit/runs` listing endpoint.

---

## 2. Five decisions locked in

| Q | Decision | Rationale |
|---|----------|-----------|
| Q-K-008-1 | Left-pane step labels from `02e_TestSteps` (workbook). Current-step highlight from runtime events. Spec-file parse = fallback when 02e empty. | Workbook owns human-language plan; runtime tells us where we are. |
| Q-K-008-2 | Native Win folder picker via PowerShell shell-out from bouracka-ui server. Fallback: default folder `runs/audit/<id>/` if PS dialog unavailable. | Bouracka-ui is local-only on HP Elite; native dialog is best UX. |
| Q-K-008-3 | Two separate OS windows side-by-side. bouracka-ui in its window, framework's headed browser in another window. | Cross-origin iframe impractical; programmatic window placement fragile. Manual layout works fine for tester. |
| Q-K-008-4 | Fixed 2-second slow-mo in v0.1.5. Configurable in v0.1.6. | Ship simpler, iterate on real usage data. |
| Q-K-008-5 | Pause + Stop only in v0.1.5. Step-forward/back deferred to v0.1.6. | Pause/Stop are framework-agnostic process control; step-back requires browser-state snapshot management = big lift. |

---

## 3. Architecture

```
┌─────────────────────────── Tester's HP Elite ───────────────────────────┐
│                                                                          │
│  ┌────────────────────────────┐    ┌────────────────────────────────┐   │
│  │  Browser tab 1 (Window 1)  │    │  Window 2 — framework browser  │   │
│  │  http://127.0.0.1:8424/    │    │  Cypress/Playwright/Selenium   │   │
│  │  /audit                    │    │  in HEADED mode, slow-mo=2s    │   │
│  │                            │    │                                │   │
│  │  Left:  step list          │    │  ┌──────────────────────────┐  │   │
│  │  Right: action log         │    │  │ test target site         │  │   │
│  │  Top:   Pause ⏸  Stop ⏹    │    │  │ tst.demo.bouracka.cz     │  │   │
│  │  Footer: status            │    │  │ executing audit run ...  │  │   │
│  └──────────────┬─────────────┘    │  └──────────────────────────┘  │   │
│                 │                  └────────────────┬───────────────┘   │
│                 │ SSE step events                   │ webdriver / cypress proto
│                 │                                   │                   │
│                 ▼                                   ▼                   │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  bouracka-ui server  (127.0.0.1:8424, FastAPI, uvicorn)          │   │
│  │  ┌────────────────────────┐    ┌─────────────────────────────┐  │   │
│  │  │ regular dispatcher     │    │ audit_dispatcher.py (NEW)   │  │   │
│  │  │ (run_async)            │    │  - launches headed framework│  │   │
│  │  │  → writes envelope     │    │  - sets BOURACKA_AUDIT_*    │  │   │
│  │  │  → /api/runs           │    │  - tails step events to SSE │  │   │
│  │  └────────────────────────┘    │  - writes runs/audit/<id>/  │  │   │
│  │                                └─────────────────────────────┘  │   │
│  │  /api/audit/runs (POST + GET list + GET stream + control + save) │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

Audit runs flow through a **parallel dispatch path** (`audit_dispatcher.py`) that never touches `dispatcher.run_async` or `consolidate_results.py`. Strict separation of execution rails.

---

## 4. Data model — AuditRun entity

```python
# Server-side in-memory registry shape (also written to runs/audit/<id>/manifest.json)
{
  "audit_run_id": "audit-2026-05-14T15-32-08Z-9f4c1d2",
  "tc_code": "TC-CP-008",
  "framework": "cypress",                # cypress | playwright | selenium
  "env_label": "tst-demo",
  "env_url": "https://tst.demo.bouracka.cz",
  "slow_mo_ms": 2000,                    # fixed v0.1.5
  "status": "pending" | "running" | "paused" | "stopped" | "done" | "error",
  "started_at": "2026-05-14T15:32:08Z",
  "ended_at": null,                      # populated on terminal states
  "duration_ms": null,
  "step_progress": {
    "current_step_idx": 3,
    "total_steps": 7,
    "current_step_label": "Click 'VYPLNIT ZÁZNAM' button",
    "current_step_status": "running" | "passed" | "failed"
  },
  "events": [                            # append-only event log
    {"ts": "...", "type": "step_start", "step_idx": 0, "label": "Navigate to /"},
    {"ts": "...", "type": "step_end", "step_idx": 0, "status": "passed"},
    {"ts": "...", "type": "assertion", "label": "page contains '...'", "status": "passed"},
    ...
  ],
  "artefacts": {
    "video_path": null,                  # populated when tester saves
    "slideshow_dir": null,
    "screenshots_per_step": [...]
  },
  "save_decision": null                  # "video" | "slideshow" | "discard" | null
}
```

**Persisted shape:** identical JSON, written to `runs/audit/<audit_run_id>/manifest.json` after run completion. Plus accompanying `events.jsonl` (one event per line, append-only during run), optional `video.mp4`, optional `slideshow/step-NN.png` + `slideshow/index.html`.

---

## 5. Server-side surface

### 5.1 New endpoints

```
POST   /api/audit/runs              — start audit run
       body: {tc: "TC-CP-008", framework: "cypress", env: "tst-demo"}
       — ALL THREE fields required; 422 if any missing or empty
       — env must be one of: demo, tst-demo, tst, uat, prod-readonly
       — framework must be one of: cypress, playwright, selenium
       — tc must exist in 02_TestCases.item_code (validated server-side)
       returns: {audit_run_id, status: "pending"}

GET    /api/audit/runs              — list audit runs (most recent first)
       returns: [{audit_run_id, tc, framework, status, started_at, duration_ms}, ...]

GET    /api/audit/runs/{id}         — full AuditRun entity
       returns: AuditRun dict

GET    /api/audit/runs/{id}/stream  — SSE stream of step events
       Server-Sent Events, MIME text/event-stream
       events: step_start, step_end, assertion, paused, resumed, stopped, done

POST   /api/audit/runs/{id}/control — pause / resume / stop
       body: {action: "pause" | "resume" | "stop"}
       returns: {status: <new status>}

POST   /api/audit/runs/{id}/save    — save artefacts to tester-selected folder
       body: {format: "video" | "slideshow" | "discard", folder_path: "C:\\..."}
       returns: {written_path, bytes_written}
       Server-side: if folder_path empty/unavailable, fall back to runs/audit/<id>/

GET    /api/audit/folder-picker     — server-side dialog (PowerShell shell-out)
       Opens Win native folder picker via System.Windows.Forms.FolderBrowserDialog.
       returns: {selected_path: "C:\\..."} or {selected_path: null} if cancelled
```

### 5.2 New dispatch module — `bouracka_ui/bouracka_ui/audit_dispatcher.py`

```python
"""Audit-mode dispatcher — separate rail from dispatcher.run_async.

Launches headed framework with slow-mo. Tails step events to SSE.
NEVER writes to 06_TestRuns. NEVER produces v0.1 envelope.
Persists only to runs/audit/<id>/.
"""

class AuditDispatcher:
    async def start(self, audit_run_id, tc, framework, env, slow_mo_ms): ...
    async def control(self, audit_run_id, action): ...   # pause/resume/stop
    async def save(self, audit_run_id, format, folder_path): ...
    def list_runs(self) -> list[dict]: ...
    def get_run(self, audit_run_id) -> dict: ...
    async def stream_events(self, audit_run_id): ...     # SSE generator

# Framework-specific harness modules
def _start_cypress_headed(tc_spec_glob, env_url, slow_mo_ms) -> subprocess.Popen: ...
def _start_playwright_headed(tc_grep, env_url, slow_mo_ms) -> subprocess.Popen: ...
def _start_selenium_headed(tc_pytest_k, env_url, slow_mo_ms) -> subprocess.Popen: ...
```

---

## 6. Client-side surface — `/audit` page

### 6.1 Route + layout

New route `/audit` in app.js. Pre-launch picker + three-section runtime layout:

**Pre-launch picker (shown when no audit run active):**

```
┌──────────────────────────────────────────────────────────────────────┐
│ Start an audit run — select all three:                               │
│                                                                       │
│   Test Case:    [TC-CP-008 — zenID + AISPOV ROB...    ▼]             │
│   Framework:    ○ cypress   ○ playwright   ○ selenium                │
│   Environment:  ○ demo   ○ tst-demo   ○ tst   ○ uat   ○ prod-readonly│
│                                                                       │
│   Slow-mo:      2 seconds (fixed, configurable in v0.1.6)            │
│                                                                       │
│                                            [▶ Start audit run]       │
└──────────────────────────────────────────────────────────────────────┘
```

All three radios must be selected before `[▶ Start audit run]` activates.
TC dropdown is filtered by binding columns (e.g., cypress radio active →
only TCs with non-empty `cypress_spec_glob` appear, per Brief #003 logic).

**Runtime layout (shown after run starts):**

```
┌──────────────────────────────────────────────────────────────────────┐
│ Audit run header:                                                    │
│   TC-CP-008 · cypress · tst-demo · running · 00:00:14                │
│   [⏸ Pause]  [⏹ Stop]  [💾 Save (when done)]                        │
├─────────────────────────┬────────────────────────────────────────────┤
│ Left pane (40%)         │ Right pane (60%)                           │
│ Step sequence:          │ Action log (auto-scroll):                  │
│   1. ✓ Navigate to /    │   [15:32:08] step_start #1 Navigate to /   │
│   2. ✓ Click "BEGIN"    │   [15:32:10] step_end   #1 passed          │
│ → 3. ▶ Type credentials │   [15:32:10] step_start #2 Click "BEGIN"   │
│   4.   Click "SUBMIT"   │   [15:32:12] assertion    "BEGIN btn visible" passed  │
│   5.   Verify dashboard │   [15:32:12] step_end   #2 passed          │
│   6.   Logout           │   [15:32:12] step_start #3 Type credentials│
│   7.   Verify logout    │   [15:32:14] (typing... 4 chars left)      │
│                         │                                            │
│ (steps from 02e_TestSteps; current step ▶, completed ✓, pending blank) │
└─────────────────────────┴────────────────────────────────────────────┘
```

### 6.2 SSE consumption

```javascript
const sse = new EventSource(`/api/audit/runs/${runId}/stream`);
sse.addEventListener('step_start', (e) => updateCurrentStep(JSON.parse(e.data)));
sse.addEventListener('step_end', (e) => markStepDone(JSON.parse(e.data)));
sse.addEventListener('assertion', (e) => appendLog(JSON.parse(e.data)));
sse.addEventListener('done', (e) => { sse.close(); showSavePrompt(); });
```

### 6.3 Save-prompt modal

When run reaches `done` status:

```
┌─────────────────────────────────────┐
│ Audit run complete — save artefacts?│
│                                     │
│   ○ Save as Video (MP4, ~12 MB)     │
│   ○ Save as Slideshow (PNG+HTML)    │
│   ○ Discard (don't save anything)   │
│                                     │
│   Folder: [..............] [Browse] │
│                                     │
│            [Cancel]  [Save]         │
└─────────────────────────────────────┘
```

`[Browse]` → POST to `/api/audit/folder-picker` → returns `selected_path` → writes into the text field.

---

## 7. Framework-specific slow-motion hooks

### 7.1 Cypress

`cypress.config.ts` reads `BOURACKA_AUDIT_SLOW_MO_MS` env var, applies via `defaultCommandTimeout` + custom command-wrapper:

```typescript
// cypress.config.ts (additive)
const auditSlowMoMs = parseInt(process.env.BOURACKA_AUDIT_SLOW_MO_MS || "0", 10);
if (auditSlowMoMs > 0) {
  Cypress.Commands.overwrite('then', (originalFn, ...args) => {
    cy.wait(auditSlowMoMs, { log: false });
    return originalFn(...args);
  });
}
```

Plus invoke with `cypress run --headed --no-exit` so the browser stays visible.

### 7.2 Playwright

Native support — passes through:

```python
# audit_dispatcher.py
subprocess.Popen([
  "npx", "playwright", "test",
  "--grep", tc_grep,
  "--headed",
  "--workers", "1",
  "--reporter", "json",
], env={"PWDEBUG": "0", "PLAYWRIGHT_SLOW_MO": str(slow_mo_ms), ...})
```

(Playwright's `slowMo` is configured in `playwright.config.ts`; we add a clause:
`use: { slowMo: parseInt(process.env.PLAYWRIGHT_SLOW_MO || "0", 10) }`)

### 7.3 Selenium

Wraps WebDriver with sleep-between-calls:

```python
# selenium/conftest.py — additive
import os, time
from selenium import webdriver

class AuditSlowMoDriver:
    def __init__(self, driver, slow_mo_ms):
        self._driver = driver
        self._delay_s = slow_mo_ms / 1000
    def __getattr__(self, name):
        attr = getattr(self._driver, name)
        if callable(attr):
            def wrapped(*a, **kw):
                result = attr(*a, **kw)
                time.sleep(self._delay_s)
                return result
            return wrapped
        return attr

@pytest.fixture
def driver():
    raw = webdriver.Chrome()  # headed by default
    slow_mo = int(os.environ.get("BOURACKA_AUDIT_SLOW_MO_MS", "0"))
    return AuditSlowMoDriver(raw, slow_mo) if slow_mo > 0 else raw
```

---

## 8. Persistence layout

```
runs/audit/<audit_run_id>/
├── manifest.json                   # full AuditRun entity
├── events.jsonl                    # one JSON event per line, append-only
├── video.mp4                       # only if save_decision == "video"
├── slideshow/                      # only if save_decision == "slideshow"
│   ├── step-00.png
│   ├── step-01.png
│   ├── ...
│   └── index.html                  # generated: each step + screenshot + label
└── browser-log.txt                 # captured stdout from cypress/playwright/selenium subprocess
```

`audit_run_id` format: `audit-<ISO-Z-timestamp-with-dashes>-<7hexchars>`, parallels regular `run-...` IDs.

---

## 9. Workflow

```
1. Tester on /run page picks TC-CP-008, ticks "Audit mode" checkbox → /audit redirect (or directly navigates to /audit)
2. /audit pre-launch picker: select TC (dropdown) + framework (radio) + environment (radio) → POST /api/audit/runs
3. Server launches headed framework subprocess + opens SSE channel
4. Window 2 (framework browser) appears side-by-side with bouracka-ui
5. Step events stream → left pane updates current step indicator, right pane logs actions
6. Tester observes; assertions highlight as they pass/fail
7. (Optional) Tester clicks ⏸ Pause → server sends SIGSTOP equivalent to framework process
8. Tester clicks ▶ Resume → SIGCONT equivalent
9. Run completes naturally OR tester clicks ⏹ Stop
10. Save prompt: tester picks Video / Slideshow / Discard
11. If Video/Slideshow + Browse: PowerShell folder picker fires from server
12. Server writes artefacts to chosen folder (or fallback runs/audit/<id>/)
13. Tester closes /audit tab, returns to /run
```

---

## 10. Out of scope (defer to v0.1.6+)

- Configurable slow-mo speed (currently fixed 2s)
- Step-forward / step-back debugger controls
- Multi-test or multi-framework audit (always exactly 1+1)
- Audit run comparison view (run TC-CP-008 in cypress AND playwright as audit, compare side by side)
- Audit-run-to-bug-file integration (FR-K-001 step linkage in audit; possible but bundle separately)
- Mobile viewport audit (responsive testing)
- Audit run scheduling / replay from saved manifest
- Bandwidth-limited / throttled execution mode (Chrome DevTools throttling integration)

---

## 11. Refs

- FR-K-008 task in tracker
- `_config/MAJOR-DEV-SESSION-PLAN-v0.1.5-EN.md` — slots into Phase 3 alongside FR-K-005/006/007
- `_specs/CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.md` — Audit runs do NOT use this schema; separate manifest format defined in §4
- `bouracka_ui/bouracka_ui/dispatcher.py` — regular dispatch path; audit_dispatcher.py is parallel
- Sonnet Brief #009 (next) — formal implementation dispatch
