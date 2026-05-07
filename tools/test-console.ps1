<#
.SYNOPSIS
  Wrapper for tools/test_console.py — multi-framework test runner +
  aggregator.

.DESCRIPTION
  Per CP-SUPIN-04 L-WORK-8+9. Forwards args to the Python CLI;
  ensures Python + openpyxl are present.

.EXAMPLE
  .\tools\test-console.ps1 status
  .\tools\test-console.ps1 run --env tst --frameworks playwright
  .\tools\test-console.ps1 run --env tst --tcs TC-CP-001,TC-CP-005
  .\tools\test-console.ps1 report --since 2026-05-06
  .\tools\test-console.ps1 compare --tcs TC-CP-001..TC-CP-005
#>
$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

# Pre-flight
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command python3 -ErrorAction SilentlyContinue }
if (-not $py) { $py = Get-Command py -ErrorAction SilentlyContinue }
if (-not $py) {
  Write-Host "[FAIL] Python not on PATH. Install Python 3.10+ first." -ForegroundColor Red
  exit 1
}

# Forward all args
& $py.Source "$PSScriptRoot\test_console.py" @args
exit $LASTEXITCODE
