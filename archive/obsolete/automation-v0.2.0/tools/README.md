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
.\tools\build_activity_diagra