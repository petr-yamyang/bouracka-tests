# Bouračka UI v0.1.0 — Troubleshooting (EN)

If something isn't working, find the symptom below and follow the recipe. If nothing matches, attach a diagnostics snapshot (`/runs` page → ⬇ Diagnostics) and email Pete.

---

## §1. Port 8424 already in use / "Errno 10048" on startup

**Symptom:**

```
ERROR: [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8424)
```

**Why:** an earlier `bouracka-ui` process is still running. Most common cause: closing the PowerShell window without Ctrl+C first — the uvicorn worker subprocess survives and keeps holding the port.

**Fix:** run the bundled `kill-stragglers.ps1`:

```powershell
.\kill-stragglers.ps1
```

Or do it manually:

```powershell
# Find what's holding 8424
Get-NetTCPConnection -LocalPort 8424 -State Listen -ErrorAction SilentlyContinue |
  ForEach-Object {
    $p = Get-Process -Id $_.OwningProcess
    Write-Host "Killing $($p.ProcessName) (PID $($p.Id))"
    Stop-Process -Id $p.Id -Force
  }

# Sanity check — should now return nothing
Get-NetTCPConnection -LocalPort 8424 -State Listen -ErrorAction SilentlyContinue
```

Then re-run `bouracka-ui`.

---

## §2. `pip install` fails with "Access Denied" on a .pyd file

**Symptom:**

```
ERROR: Could not install packages due to an OSError: [WinError 5]
Access denied: '...\.venv\Lib\site-packages\~-bsockets\speedups.cp310-win_amd64.pyd'
(in Czech: Přístup byl odepřen)
```

The `~-bsockets` or `~ttptools` prefix on the directory name means pip's previous install attempt left a half-cleaned-up orphan. The .pyd file is held by a process that won't release it.

**Fix:** kill the holder + delete the orphan.

```powershell
# 1. Kill the holding process (typically the old bouracka-ui server)
.\kill-stragglers.ps1

# 2. Delete the orphans (the leading-tilde directories)
$venvSite = ".\.venv\Lib\site-packages"
Get-ChildItem $venvSite -Directory | Where-Object Name -like "~*" | Remove-Item -Recurse -Force

# 3. Retry the install
pip install --force-reinstall bouracka_ui-0.1.0-py3-none-any.whl
```

If `Remove-Item` still complains about Access Denied after the kill, reboot Windows (last resort but reliable).

---

## §3. Results page shows "Run not found: run-..." for a long time

**Behaviour:** the UI was navigating you to `/results/<run_id>` before the run had finished writing its envelope to disk.

**Status in v0.1.0:** **fixed.** The results page now polls every 2 s and shows a "running" status pill until the envelope arrives. If you see "Run not found" persistently for more than 90 s, something else is wrong — see §4.

If you have a build older than v0.1.0 and can't upgrade, the workaround is: wait 30-60 s, then click the Reload link on the page.

---

## §4. Run starts, but dispatch fails silently (no envelope ever produced)

**Symptom:** results page shows `dispatch failed — no envelope produced`. Or you see this with "Run not found" if you're on a v0.0.x build.

The dispatch-failed view in v0.1.0+ now lists the four most common candidate causes inline; pick the one that matches your log:

**(a) Framework binary missing on PATH.** `npx` / `cypress` / `playwright` not installed. Log shows `tooling not found: [WinError 2]`.
- Install Node.js 18+ from nodejs.org → restart PowerShell → restart bouracka-ui.
- For Cypress: from repo root: `npm install cypress --save-dev`
- For Playwright: `npm install @playwright/test --save-dev; npx playwright install`

**(b) pytest plugin missing.** `pytest-json-report` not in the venv. Log shows `unrecognized arguments: --json-report`.
- v0.1.0+ wheel auto-installs `pytest-json-report` as a runtime dependency. If you somehow still hit this, run `pip install pytest-json-report` in the venv.

**(c) Repo root mis-detected.** bouracka-ui can't locate `tools/consolidate_results.py`. Log shows the consolidator script path pointing inside `.venv/` or some other wrong directory.
- v0.1.0+ wheel auto-detects the repo root by walking up from CWD looking for the `tools/consolidate_results.py` marker. If detection still fails, override via env var:

   ```powershell
   $env:BOURACKA_UI_REPO_ROOT = "C:\Users\you\path\to\bouracka-tests"
   bouracka-ui
   ```

**(d) No test specs matched.** Your TC selection produces a glob that doesn't resolve to any spec files on disk.
- Verify that `cypress/e2e/**/*<tc-token>*.cy.ts` (or the playwright/selenium equivalent) actually exists for the TC you selected.

**Universal fallback — mock mode** (for demos / UI iteration without real browsers):

```powershell
$env:BOURACKA_UI_DISPATCH_MODE = "mock"
bouracka-ui
```

Open `/about` in the UI to inspect tool availability (npx / python / consolidate_results all listed with green/red status).

---

## §5. "Workbook locked" (HTTP 409) when filing a bug

**Symptom:** clicking "File bug" gives `409 Workbook locked (Excel open?)`.

**Why:** Excel has the `BOURACKA-TESTPLAN-*.xlsx` file open. `openpyxl` can't write while it's exclusively locked.

**Fix:** close the workbook in Excel and retry. No data is lost.

---

## §6. Tests fail with "selector not found" or similar — but I just ran them yesterday and they passed

**Likely cause:** drift. The bouracka.cz pages may have been redeployed with new selectors, reCAPTCHA versions, etc.

**What to do:**

1. Check the **drift forensic** card on the Results page (if visible).
2. If a drift pattern is detected (`recaptcha-v3` is the common one), the affected TCs will be flagged `skip-drift` automatically — that's not a regression in your code, it's a known limitation.
3. If TCs marked `fail` aren't drift-related, file a bug per §5 of OPERATOR-GUIDE.md.

---

## §7. Browser opens to a blank page / 502 / cannot connect

**Symptom:** you ran `bouracka-ui` but the auto-opened browser shows "This site can't be reached" or similar.

**Checks:**

1. PowerShell window — is the server actually running? Look for `INFO: Application startup complete.` and `Uvicorn running on http://127.0.0.1:8424`.
2. If the server reports Errno 10048, see §1.
3. If the server started fine but the browser can't connect, check firewall: corporate firewalls sometimes block loopback ports >1024. Try a different port:

   ```powershell
   bouracka-ui --port 18424
   ```

   ...and open http://127.0.0.1:18424/ manually.

---

## §8. "Loading…" forever on the Run page

**Symptom:** the `/run` page shows "Loading TCs…" and never proceeds.

**Why:** the workbook can't be opened (path wrong, corrupt, or Excel has an exclusive lock).

**Fix:**

1. Open `/about` and look at the **workbook** row. If red → wrong path or file missing.
2. Check `BOURACKA-TESTPLAN-*.xlsx` is in the same folder as the wheel (or pass `--workbook PATH` to override).
3. Close any open Excel instance holding the file.
4. Open browser DevTools (F12) → Console tab → look for the actual error from the failed API call.

---

## §9. After `git pull`, tests behave differently

This guide is shipped with a frozen wheel — pulling new code in the bouracka-tests repo does NOT affect the installed bouracka-ui binary. To pick up new bouracka-ui changes, you need a new wheel.

If you're a developer co-located with this install (i.e. you have the repo cloned), do:

```powershell
cd <bouracka-tests>\bouracka_ui
python -m build
pip install --force-reinstall dist\bouracka_ui-*.whl
```

---

## §10. Anything else

Attach a **diagnostics snapshot** to your bug report:

1. Open `/runs` in the UI.
2. Click **⬇ Diagnostics** (top right).
3. Save the resulting ZIP.
4. Attach it to your bug report (or send to Pete via email).

It contains: server health, workbook path + tool availability, OS info, recent server log lines, no PII.

---

## §11. Air-gap pip install failures (SUPIN HP Elite + similar)

**Symptom A — `getaddrinfo failed`:**

```
WARNING: Retrying ... Failed to establish a new connection: [Errno 11001] getaddrinfo failed
ERROR: Could not find a version that satisfies the requirement fastapi>=0.110
ERROR: No matching distribution found for fastapi>=0.110
```

**Why:** the install machine has no PyPI egress (SUPIN policy). Pip tried to download FastAPI from the internet and got DNS-resolution failure.

**Fix:** install MUST use `--no-index --find-links=<wheelhouse-path>`. Re-read INSTALL-HP-ELITE.txt §4. Concrete command:

```powershell
pip install --no-index `
  --find-links="C:\TestAutomationSite\wheelhouse" `
  "C:\TestAutomationSite\bouracka_ui-0.1.1-py3-none-any.whl"
```

The `--no-index` flag is what makes this air-gap-safe. Without it, pip will still try PyPI even if local wheels exist.

---

**Symptom B — `Could not find a version ... ; extra == "standard"`:**

```
ERROR: Could not find a version that satisfies the requirement httptools>=0.6.3; extra == "standard"
```

**Why:** the wheelhouse is missing wheels for optional extras. pip <24 doesn't reliably follow `uvicorn[standard]` extras from a local wheel's metadata. Wheelhouse was built without explicit enumeration.

**Fix:** rebuild the wheelhouse on ThinkPad with explicit extra enumeration:

```powershell
pip download -d wheelhouse `
  --platform win_amd64 --python-version 312 --only-binary=:all: `
  dist\bouracka_ui-0.1.1-py3-none-any.whl `
  "uvicorn[standard]>=0.27" `
  "pytest>=8.0" `
  "pytest-json-report>=1.5"
```

The packager script `delivery/package-hp-elite-v0.1.0.ps1` does this automatically in v0.1.1+.

---

**Symptom C — `Could not find a version ... cp310-cp310-win_amd64.whl` won't install:**

**Why:** wheelhouse contains cp310 wheels (Python 3.10 ABI) but target machine has a different Python version. C-extension wheels (httptools, watchfiles, websockets, pyyaml, pydantic-core) are ABI-locked.

**Fix:** check `python --version` on target. Match the wheelhouse `-pyNNN` ZIP suffix to it:

```powershell
python --version
# Python 3.12.10  →  use bouracka-ui-hp-elite-v0.1.1-EN-py312.zip
# Python 3.11.x   →  use ...-py311.zip
# Python 3.10.x   →  use ...-py310.zip
```

If you have the wrong wheelhouse, ask Pete to rebuild on ThinkPad:

```powershell
.\delivery\package-hp-elite-v0.1.0.ps1 -PythonVersion 312
```

---

**Symptom D — `WARNING: Location '.\wheelhouse' is ignored ... lacks a specific scheme`:**

**Why:** pip on some Windows configurations doesn't reliably resolve `.\wheelhouse` as a local-directory `--find-links` target.

**Fix:** use an ABSOLUTE path. Always:

```powershell
pip install --no-index --find-links="C:\TestAutomationSite\wheelhouse" "C:\TestAutomationSite\bouracka_ui-0.1.1-py3-none-any.whl"
```

(see KB-042 for the full lesson on air-gap Python packaging quirks)

---

## Appendix A — Known limitations

- **v0.1.0** ships with MOCK fallback when tooling is missing — this is intentional, but means you can have a green-looking results page without any browsers actually running. Check `/about` to confirm real-mode dispatch.
- **Per-framework retry** is not yet supported. If Cypress flakes out, you re-run the whole TC set.
- **Concurrent runs** are not supported. Only one dispatch at a time; subsequent POST /api/runs while a run is in flight will succeed but logs interleave.
- **No authentication** — the UI listens on `127.0.0.1` only (loopback). Don't expose it on a public interface.

End of TROUBLESHOOTING.md
