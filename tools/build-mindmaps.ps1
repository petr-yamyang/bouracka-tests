<#
.SYNOPSIS
  Build TT + TC mindmap diagrams from BOURACKA-TESTPLAN-v0.1.xlsx.

.DESCRIPTION
  Wrapper around tools/build_mindmaps.py that handles Windows-side
  prerequisites: confirms Python + openpyxl + Graphviz, then runs the
  Python script. Outputs land in recon/diagrams/.

.EXAMPLE
  # from C:\Users\vitez\Documents\VibeCodeProjects\SUPIN\bouracka-tests
  .\tools\build-mindmaps.ps1
#>
# NOTE: deliberately NOT using $ErrorActionPreference='Stop' — native
# commands (python, dot) writing to stderr would otherwise terminate
# the script even when their exit code is 0.
$ErrorActionPreference = 'Continue'

# Always cd to the repo root (this script's parent of parent)
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
Write-Host "[build-mindmaps] cwd = $root" -ForegroundColor Cyan

# 1. Pick a Python — try py launcher (Win-standard) then python / python3
$pyCmd = $null
foreach ($cand in @('py', 'python', 'python3')) {
  if (Get-Command $cand -ErrorAction SilentlyContinue) { $pyCmd = $cand; break }
}
if (-not $pyCmd) {
  Write-Host "[FAIL] No Python found on PATH." -ForegroundColor Red
  Write-Host "       Install: winget install Python.Python.3.12 --scope user" -ForegroundColor Yellow
  exit 1
}
$pyVer = (& $pyCmd --version 2>&1) -join ' '
Write-Host "[build-mindmaps] python = $pyCmd ($pyVer)" -ForegroundColor Cyan

# 2. Ensure openpyxl — capture stderr to a variable so PowerShell
#    doesn't decorate it as an error record.
$null = & $pyCmd -c "import openpyxl" 2>&1
if ($LASTEXITCODE -ne 0) {
  Write-Host "[build-mindmaps] installing openpyxl (per-user)..." -ForegroundColor Yellow
  $pipOut = & $pyCmd -m pip install --user --quiet openpyxl 2>&1
  if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] could not pip install openpyxl:" -ForegroundColor Red
    $pipOut | ForEach-Object { Write-Host "       $_" -ForegroundColor DarkRed }
    exit 1
  }
  Write-Host "[build-mindmaps] openpyxl installed." -ForegroundColor Green
} else {
  Write-Host "[build-mindmaps] openpyxl present." -ForegroundColor Cyan
}

# 3. Ensure Graphviz 'dot'
$dotCmd = Get-Command dot -ErrorAction SilentlyContinue
if (-not $dotCmd) {
  Write-Host "[FAIL] Graphviz 'dot' is not on PATH." -ForegroundColor Red
  Write-Host "       Install:  winget install Graphviz" -ForegroundColor Yellow
  Write-Host "  