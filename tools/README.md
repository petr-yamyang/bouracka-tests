# tools/ — script library

> Helper scripts that read from the canonical sources
> (`BOURACKA-TESTPLAN-v0.1.xlsx`, `fixtures/*.yaml`, photo folders) and
> emit derivative artefacts (mindmaps, JPGs, activity diagrams,
> coverage reports). All scripts run from the repo root, work on
> Windows (PowerShell wrappers) + macOS / Linux (Python / bash
> equivalents), and require no admin rights.

## Inventory

| Tool | Reads from | Emits to | Purpose | Profile |
|------|-----------|----------|---------|:-------:|
| `heic-to-jpg.ps1` / `heic-to-jpg.sh` | any HEIC folder | JPG folder | Batch HEIC → JPG conversion (resize + quality control) for ingestion of analytical-doc photos | A |
| `build_mindmaps.py` + `build-mindmaps.ps1` | `BOURACKA-TESTPLAN-v0.1.xlsx` | `recon/diagrams/{tt,tc}-mindmap.{png,svg,pdf}` | One-page TT + TC mindmaps; color-coded by priority | A |
| `build_activity_diagrams.py` *(arrives in CP-SUPIN-02 rev 7)* | extracted Mermaid sources under `recon/diagrams/extracted/` | rendered PNG/SVG per screen | Render swimlane activity diagrams | B |
| `validate_tc_coverage.py` *(planned CP-SUPIN-03)* | activity-diagram Mermaid + Excel `02_TestCases` | `recon/COVERAGE-GAP-ANALYSIS.md` | Cross-check that every diagram branch has ≥ 1 TC | B |
| `validate-install.ps1` (in `scripts/`) | system | JSON to `runs/` | Per-profile install validation | A/B/C |
| `setup-npm-proxy.ps1` (in `scripts/`) | env vars | npm config | Configure npm for corp proxy + CA bundle | A |

## Prerequisites table

| Tool | Python | openpyxl | Graphviz | ImageMagick | Notes |
|------|:------:|:--------:|:--------:|:-----------:|-------|
| `heic-to-jpg.*` | ✗ | ✗ | ✗ | ✓ | needs `libheif` on Linux |
| `build_mindmaps.*` | ≥ 3.9 | ✓ | ✓ | ✗ | |
| `build_activity_diagrams.*` | ≥ 3.9 | ✗ | ✓ (Mermaid via mmdc OR PlantUML via JRE) | ✗ | mmdc preferred (no JRE) |
| `validate_tc_coverage.*` | ≥ 3.9 | ✓ | ✗ | ✗ | reads Excel + Mermaid sources |
| `validate-install.ps1` | ✗ | ✗ | ✗ | ✗ | pure PowerShell |

## Common runs

```powershell
# Convert a new batch of analytical-doc photos
.\tools\heic-to-jpg.ps1 `
  -Source 'C:\Users\vitez\Documents\VibeCodeProjects\SUPIN\analyticke vstupy' `
  -Destination .\recon\photos

# Re-render TT + TC mindmaps after Excel edit
.\tools\build-mindmaps.ps1

# (Future) Render activity diagrams + coverage gap report
.\tools\build_activity_diagrams.ps1
.\tools\validate_tc_coverage.ps1
```

## Install prerequisites once per laptop

```powershell
# Per-user, no admin
winget install Python.Python.3.12 --scope user
winget install Graphviz
winget install ImageMagick.ImageMagick
# close + reopen PowerShell so PATH refreshes
python -m pip install --user openpyxl pyyaml
```

## Tool conventions (binding for new contributors)

1. **Self-relative paths.** Every script computes `ROOT = Path(__file__).resolve().parent.parent`
   so it works from any cwd as long as the tree structure is intact.
2. **Friendly pre-flight.** Every script's first lines check
   prerequisites and print actionable hints (`Install: winget install …`)
   before failing.
3. **`$ErrorActionPreference = 'Continue'` in PowerShell wrappers.**
   Native commands writing to stderr would otherwise crash the script
   spuriously.
4. **No hidden Excel writes.** Tools READ Excel; they don't modify
   it. The Excel master is single-source-of-truth; rebuild via
   `outputs/rev*_xlsx.py` (CP-SUPIN history).
5. **Idempotent.** Re-running produces the same output. Skipped-files
   counters reported.
6. **Markdown-friendly outputs.** PNG/SVG/PDF/MD/YAML — any text
   format can land directly in the wiki/repo without conversion.

## When to write a new tool here

Promote an ad-hoc script to `tools/` when:

- It's been used in **≥ 2 sessions** OR
- Its output is **a deliverable** (committed file, artefact for SecOps,
  diagram for a stakeholder) OR
- A **colleague might run it** independently from the operator.

Sketches and one-shots stay in the operator's `outputs/` scratchpad.
Promotion = move + write a `tools/README.md` row + add a PowerShell
wrapper if the audience runs Windows.

## workbook-v0.4.3-to-v0.4.4.py

One-shot, idempotent workbook schema patcher.  Upgrades
`BOURACKA-TESTPLAN-v0.4.3.xlsx` to `v0.4.4`:

- Creates sheet `02e_TestSteps` by splitting `02_TestCases.steps_summary`
- Adds `steps_count` column to `02_TestCases`
- Validates `02c_TC_Assertions.step_id` FK; reports orphans (does not modify)
- Adds `evidence_*` columns to `08_Bugs`; migrates `screenshot_ref` / `trace_ref`
- Appends a changelog row to `11_Changelog`
- Writes a timestamped PATCH-REPORT to `tools/patcher-reports/`

**Quick start:**

```powershell
# inspect what the patcher would do (no write)
python tools/workbook-v0.4.3-to-v0.4.4.py --dry-run -v

# apply the patch
python tools/workbook-v0.4.3-to-v0.4.4.py -v

# custom paths
python tools/workbook-v0.4.3-to-v0.4.4.py `
    --source path/to/BOURACKA-TESTPLAN-v0.4.3.xlsx `
    --dest   path/to/BOURACKA-TESTPLAN-v0.4.4.xlsx `
    -v
```

**Exit codes:** 0 = clean, 1 = warnings (orphans / KP-review flags), 2 = input error, 3 = write error.

**Prerequisites:** `pip install openpyxl`

**Tests:**

```powershell
pytest tools/tests/ -v -m "not integration"    # fast (synthetic fixture, <5s)
pytest tools/tests/ -v -m integration          # slow (real workbook, manual)
```

**Fixture regeneration:** `python tools/tests/fixtures/make_synthetic_fixture.py`

---

## Status

| Item | Value |
|------|-------|
| Tools current | 5 ready + 2 planned |
| Coverage | photo conversion · mindmap rendering · install validation · proxy setup · workbook schema patch |
| Audience | operator + 2 colleagues + SecOps |
| Status | v0.3 — workbook patcher added in CP-SUPIN-07 |
