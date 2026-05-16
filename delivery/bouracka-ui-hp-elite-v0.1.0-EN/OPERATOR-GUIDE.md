# Bouračka UI v0.1.0 — Operator Guide (EN)

**Audience:** testers who will use bouracka-ui day-to-day to drive Cypress / Playwright / Selenium runs against bouracka.cz environments.
**Prerequisite:** completed install per `INSTALL-HP-ELITE.txt`.

---

## §1. Daily workflow at a glance

The expected loop:

1. Start the UI: `bouracka-ui` (or `bouracka-ui --no-browser` if you don't want auto-open).
2. Pick env + framework(s) + TC subset on the **Run** page.
3. Click **Run selected**, watch live log.
4. When the run finishes, you land on **Results** — review the verdict matrix.
5. For any failure, click **+ bug** in the row → fills in the Bugs form with TC/env/run already wired up.
6. Optional: export a **trace bundle** ZIP from the Results page header (for sharing the full run state with another tester or for archival).

Stop the server with **Ctrl+C** in the PowerShell window when you're done.

---

## §2. Pages — what they do

### 2.1 `/run` — Pick + dispatch

- **Environment** selector — dropdown maps to the workbook's `04_TestEnvironments` sheet (ENV-DMO / ENV-TST / ENV-PUB). The base URL (`demo.bouracka.cz`, `tst.bouracka.cz`, `www.bouracka.cz`) shows below the dropdown.
- **Framework(s)** — `all` runs Cypress + Playwright + Selenium sequentially (slower; useful for cross-framework parity checks). Single-framework runs are faster.
- **Test cases grid** — filtered by env. Each row shows TC code + severity pill (A/B/C/X) + priority. Tick the boxes for the TCs you want to run. **Select all** / **Clear** buttons are above the grid.
- **Run selected** kicks off the dispatch. The **Live log** card unfolds and streams stdout from each framework as it executes.

### 2.2 `/results/<run_id>` — Verdict matrix + bug-file shortcut

After a run finishes, you land here automatically. The page shows:

- **Summary chips:** total TCs, pass/fail/skip counts, soft-pass count, strict + drift-aware pass-rate, parity-divergence count.
- **Verdict matrix:** one row per TC × one column per framework. Cells show `pass` / `fail` / `skip-drift` / `skip-other` / `soft-pass` / `error` / `missing`. Parity status column tells you whether all frameworks agreed.
- **Drift forensic card** (only visible if drift was detected) — shows the type (e.g. `recaptcha-v3`), affected TCs, and notes.
- **+ bug** link in each failed row — opens the Bugs form with TC / run-id / env already pre-filled. Quicker than typing them by hand.
- **Export bundle** / **Export bundle (full)** buttons in the header — produce a ZIP with envelope + manifest + logs (+ videos and traces for the "full" variant) for transferring runs between machines without GitHub.

**If you land here while the run is still in flight** (e.g. you opened the URL from a bookmark, or the dispatch took longer than expected), the page shows a "running" status pill and auto-polls every 2 s until the envelope is ready. Just leave the tab open and it transitions to the full results view automatically. (BUG-BUI-002 fix as of v0.1.0.)

### 2.3 `/runs` — Past runs list

- One row per past run (sorted newest first). Shows started_at, env, total/pass/fail/skip counts, parity-divergence count, and run_id.
- Click any row to drill into its results page.
- **Env filter** + **Last NN runs** + **Refresh** controls at the top.
- **⬆ Import bundle** lets you bring in a trace-bundle ZIP from another machine (e.g. HP Elite air-gap workflow). Once imported, it appears in this list.
- **⬇ Diagnostics** downloads a no-run diagnostics snapshot (health + system info + tool versions). Useful when reporting "the UI isn't working" — attach this snapshot to your bug report.

### 2.4 `/bugs` — Bug tracker (writes back into the workbook)

- One row per bug from the `08_Bugs` sheet of the workbook.
- **Status filter** (open/closed/investigating) + **Severity filter** (A/B/C/X) at top.
- **+ New Bug** opens an inline form. Required fields: Title + Severity. Auto-filled if you arrived via `+ bug` on a failed result row.
- Filing a bug appends a row to the workbook directly. If Excel has the workbook open, you'll get a 409 with "Workbook locked" — close Excel and retry.

### 2.5 `/about` — Tool availability + health check

The most useful page when something isn't working. It shows:

- Server + schema versions.
- Workbook path + whether it's found.
- Runs directory.
- Tool availability: npx, python, consolidator (`tools/consolidate_results.py`). **Anything red means dispatch will fall back to mock mode or skip that framework.**

---

## §3. Dispatch modes — real vs mock

By default, bouracka-ui auto-detects available tooling:

- **Real mode:** invokes `npx cypress run`, `npx playwright test`, `pytest selenium/tests/`, then `tools/consolidate_results.py` to merge results.
- **Mock mode:** synthesizes fake results (1 fail on ALT-4 cypress, 1 skip-drift on ALT-1, etc.) — useful for demos and UI iteration without actually running browsers.

Force mock mode for a session via env var (PowerShell):

```powershell
$env:BOURACKA_UI_DISPATCH_MODE = "mock"
bouracka-ui
```

To return to real mode: `Remove-Item Env:BOURACKA_UI_DISPATCH_MODE` and restart the server.

---

## §4. Trace bundles (HP Elite air-gap workflow)

When you can't push results to GitHub or share via a network drive (typical SUPIN HP Elite scenario), trace bundles are the way out.

**Export** (on the source machine):
1. Open `/results/<run_id>` for the run you want to share.
2. Click **⬇ Export bundle** (lightweight: envelope + logs + manifest, ~50 KB) or **⬇ Export bundle (full)** (includes videos + Cypress traces, multiple MB).
3. Save the ZIP. Filename: `trace-bundle-run-...-<7hex>.zip`.
4. Move to the target machine via USB / email / Slack / etc.

**Import** (on the target machine):
1. Open `/runs`.
2. Click **⬆ Import bundle**.
3. Pick the ZIP.
4. Page auto-navigates to the imported run's results.

The import is idempotent (re-importing the same bundle is a no-op) and validated (rejects ZIPs missing `manifest.json` or with a different `bundle_format_version`).

---

## §5. Bug-file conventions

When you click `+ bug` on a failed result row, the form opens with TC + env + run pre-filled. Fill in:

- **Title (English)** — short and descriptive. Example: `TC-CP-A2-ALT-1 cypress: reCAPTCHA blocks submit at step 3`.
- **Severity** — A (critical: blocks all testing), B (high: blocks a flow), C (low: cosmetic / edge), X (undefined / triage).
- **Linked TC code** — pre-filled. Leave it.
- **Reproduction steps** — terse numbered list works fine.
- **Expected / Actual** — short paragraphs. The verdict matrix already captures pass/fail, so this is for the human-readable context.

The bug code (`BUG-NNN`) is auto-assigned by the workbook (next free integer in the `08_Bugs` sheet).

---

## §6. Stopping cleanly

**Always Ctrl+C** the server in the PowerShell window before closing the window. If you just close the window without Ctrl+C, the uvicorn worker subprocess may linger and keep port 8424 + the websockets DLL locked — preventing the next start (and the next `pip install`).

If that does happen, run `kill-stragglers.ps1` (bundled with this package). See TROUBLESHOOTING.md §1 for the recipe.

---

## §7. What lives where on disk

```
C:\bouracka-ui\
├── .venv\                              ← virtual environment (don't touch)
├── bouracka_ui-0.1.0-py3-none-any.whl  ← the installable wheel
├── BOURACKA-TESTPLAN-v0.4.3.xlsx       ← workbook (data source: TCs, envs, bugs)
├── runs\                               ← envelope JSONs land here
│   └── cross-framework-demo-2026-05-11.json
├── imported-bundles\                   ← trace bundles imported via /runs page
├── INSTALL-HP-ELITE.txt
├── OPERATOR-GUIDE.md                   ← this file
├── TROUBLESHOOTING.md
├── kill-stragglers.ps1
└── SHA256SUMS.txt
```

The workbook is the **source of truth** for TCs, envs, and bugs. The `runs/` directory is the **execution history**. Both should be backed up periodically (USB stick is fine).

---

## §8. Reporting issues with bouracka-ui itself

If something in the UI is broken (not just a test failure), file it as a **BUG-BUI-NNN** through the Bugs page. Include:

- What you clicked.
- What you expected.
- What happened.
- The diagnostics snapshot (`/runs` → ⬇ Diagnostics) attached if possible.

These reach me (Pete) and feed into the next bouracka-ui release.

---

## §9. Navigation note — in-app Back button

The header has a **← Back** button to the left of the page-nav links. It uses the SPA's own history stack via `window.history.back()`, which is more predictable than the browser's Back arrow with hash routing. Use the in-app Back button by preference.

## §10. Version history

- **v0.1.1** (2026-05-11 evening) — air-gap distribution. Same UI code as v0.1.0. Packaging-only iteration:
  - Bundled wheelhouse: all Python deps shipped as pre-downloaded wheels alongside the main wheel
  - Air-gap install recipe: `pip install --no-index --find-links=.\wheelhouse <wheel>`
  - Python-version-tagged ZIP filenames (`-py310` / `-py311` / `-py312`)
  - INSTALL/TROUBLESHOOTING refreshed for air-gap pattern + 4 documented pip-error variants
  - KB-042 lesson captured for future SUPIN-air-gapped Python deliverables
  - requires-python bumped 3.9 → 3.10 (matches what we actually test on)

- **v0.1.0** (2026-05-11 daytime) — first release. Includes:
  - BUG-BUI-001: Windows NTFS filename safety for run_ids
  - BUG-BUI-002: 202 in-flight semantics + UI polling (no transient "Run not found")
  - BUG-BUI-003: Provenance card dynamically retitled to "Live log" / "Dispatch log" by state
  - BUG-BUI-004: REPO_ROOT auto-detect from CWD (fixes wheel-install dispatch) + in-app Back button + multi-cause dispatch-failed message + `pytest-json-report` runtime dep

End of OPERATOR-GUIDE.md
