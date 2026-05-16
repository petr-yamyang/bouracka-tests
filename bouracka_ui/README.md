# bouracka-ui

Local presentation-layer UI for the Bouračka test suite. Wraps existing
test runners (Cypress / Playwright / pytest+Selenium) + the
`tools/consolidate_results.py` cross-framework consolidator. Designed as
the forerunner of the MI-M-T UI prototype.

**Scope:** four functions — pick environment, select tests, run them,
view results + file bugs JIRA-style. **No workflow logic.** Zero new
business logic. All test execution delegates to existing scripts.

**Design doc:** `_config/BOURACKA-UI-DESIGN-v0.1-2026-05-10.md` (binding
reference for v0.1 scope and API contract).

---

## Install (developer / first-time tester)

```sh
cd ~/Documents/VibeCodeProjects/SUPIN/bouracka-tests/bouracka_ui

# Option 1 — editable install for development
pip install -e ".[dev]"

# Option 2 — wheel install for distribution to testers
python -m build
pip install dist/bouracka_ui-0.1.2-py3-none-any.whl
```

## Run

```sh
bouracka-ui
# → starts FastAPI server on http://localhost:8424
# → opens browser to that URL automatically (--no-browser to suppress)
```

CLI options:

```
bouracka-ui --port 8424 \
            --workbook ../BOURACKA-TESTPLAN-v0.4.3.xlsx \
            --runs-dir  ../runs \
            --no-browser
```

## Architecture

```
Browser (vanilla JS + 3FP design tokens)
    ↕ HTTP + SSE
bouracka-ui FastAPI server
    ↕ subprocess
existing scripts:
  - npx cypress run / npx playwright test / pytest selenium/tests/
  - python tools/consolidate_results.py
    ↕ openpyxl read-only
BOURACKA-TESTPLAN-v0.4.3.xlsx   (KP-reviewed primary, since 2026-05-11)
    (only 08_Bugs sheet is appended — for "+ New Bug")
```

## Pages

| Path | Purpose |
|------|---------|
| `/run` | env picker · TC checkbox grid · framework picker · "Run selected" button · live log tail |
| `/runs` | list of past runs · sortable · click row → drill-down |
| `/results/{run_id}` | per-run drill-down · v0.1 schema envelope rendered · drift forensic · evidence links |
| `/bugs` | JIRA-style bug list · "+ New Bug" form · sortable / filterable |
| `/about` | version info · schema version · health check |

## API endpoints

See `_config/BOURACKA-UI-DESIGN-v0.1-2026-05-10.md` §3.1 for the full
contract. Quick reference:

```
GET  /api/health                schema_version + tool detection
GET  /api/envs                  list ENV-* from workbook
GET  /api/tcs                   list TCs from workbook
POST /api/runs                  trigger run (subprocess)
GET  /api/runs                  list past runs (scan runs/*.json)
GET  /api/runs/{rid}            full v0.1 envelope
GET  /api/runs/{rid}/log        SSE stream of run stdout
GET  /api/bugs                  list bugs from workbook
POST /api/bugs                  append new bug to workbook
```

## Aesthetic / design tokens

UI styling reuses tokens lifted from `mim2000-theme/style.css` (azure
baseline — Bouračka is on the MI-M-T arc per
`_config/3FP-PHASE-5-ARCH-E01-SCOPING-v0.1-2026-05-10.md` §6.4 + OQ-3FP-27).
At v0.1 the tokens are inlined in `static/design-tokens.css`. v0.1.1 will
swap to `@import` from the 3FP shared library once `library/design-tokens/`
lands per Phase-5 §6.2.

## Status

**v0.1.0 — Phase 1 (Runnable Mock).** Most endpoints return synthetic
data; UI demonstrates page layout + flow. Phase 2 wires real workbook
reads; Phase 3 wires real subprocess dispatch. See design doc §6.

## License / scope

Internal SUPIN/Bouračka delivery only. Not for public distribution.
