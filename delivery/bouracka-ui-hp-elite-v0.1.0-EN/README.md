# Bouračka UI v0.1.2 — HP Elite Distribution (EN, Kate drop 2026-05-12)

**Start here:** open `INSTALL-HP-ELITE.txt` and follow the steps in order.

## Documents in this package

| File | What it's for | When to read it |
|------|---------------|-----------------|
| `INSTALL-HP-ELITE.txt` | Install steps from a fresh laptop to a working `bouracka-ui --help` | **first**, once per laptop |
| `OPERATOR-GUIDE.md` | Day-to-day workflow: run tests, file bugs, export bundles | after first successful install |
| `TROUBLESHOOTING.md` | Recipes for known UI failure modes (port in use, locked DLLs, dispatch issues, etc.) | when the UI itself breaks |
| `DIAGNOSTICS-PLAYBOOK.md` | What to check when the SYSTEM around the UI misbehaves: network reachability, integration mock-vs-live deltas, drift catalog, pre-flight TST checklist, DELTA-REPORT template for shipping findings back | for any "this isn't an obvious UI bug" moment |
| `kill-stragglers.ps1` | Helper script: kills stuck servers + cleans pip orphans | when troubleshooting tells you to |
| `SHA256SUMS.txt` | Checksums for integrity verification | optional, before install on security-sensitive machines |
| `bouracka_ui-0.1.2-py3-none-any.whl` | The installable wheel | referenced by INSTALL-HP-ELITE.txt step 4 |
| `wheelhouse/` | ~28 .whl files, pre-downloaded dependencies (air-gap install) | used by INSTALL step 4 |
| `BOURACKA-TESTPLAN-v0.4.3.xlsx` | Test workbook (TCs / envs / bugs) — KP-reviewed primary | referenced by the UI; don't touch directly |

## Quick sanity check

If you've already done the install and just want to confirm everything still works:

```powershell
cd C:\bouracka-ui
.\.venv\Scripts\Activate.ps1
bouracka-ui --help
```

You should see the usage banner. If you don't — `TROUBLESHOOTING.md` §1 (port in use) or §2 (pip access denied) usually covers it.

## What's new in v0.1.0

- First release of bouracka-ui as a presentation layer over the test runners.
- Cross-framework dispatch: Cypress + Playwright + Selenium from a single screen.
- Bug filing writes back into the Excel workbook.
- Trace bundle export/import for HP Elite air-gap workflow (no GitHub required).
- Diagnostics snapshot endpoint for "the UI isn't working" reports.
- **BUG-BUI-001 fix:** run_ids use Windows-safe filename format (no `:` chars).
- **BUG-BUI-002 fix:** Results page polls every 2 s while a run is in flight — no more transient "Run not found" pages.

## Authoring + maintenance

Pete Y. (petr.yamyang@gmail.com).
