<#
.SYNOPSIS
  30-sekundový sanity check po instalaci — ověří 7 kritických komponent.

.DESCRIPTION
  Per CP-SUPIN-04 STEP 22. Auto-detects nejnovější Excel master,
  hodí ne-nulový exit kód při jakékoliv chybě, vypisuje 7-položkový report.

.EXAMPLE
  .\scripts\sanity-check.ps1
#>
$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$ok = 0; $fail = 0

function Check {
    param([string]$Name, [scriptblock]$Test)
    $r = & $Test
    if ($r) { Write-Host "  + $Name" -ForegroundColor Green; $script:ok++ }
    else    { Write-Host "  - $Name" -ForegroundColor Red;   $script:fail++ }
}

Write-Host ""
Write-Host "=== Bouracka sanity-check ===" -ForegroundColor Cyan
Write-Host ""

Check "py launcher works"           { (& py --version 2>&1) -match 'Python 3\.' }
Check "py -m pip works"             { & py -m pip --version *> $null; $LASTEXITCODE -eq 0 }
Check "openpyxl importable"         { & py -c "import openpyxl" *> $null; $LASTEXITCODE -eq 0 }
Check "Node + npm on PATH"          {
    ((Get-Command node -ErrorAction SilentlyContinue) -ne $null) -and
    ((Get-Command npm  -ErrorAction SilentlyContinue) -ne $null)
}
Check "Playwright installed"        {
    if (-not (Test-Path "node_modules\@playwright\test")) { return $false }
    & npx playwright --version *> $null; $LASTEXITCODE -eq 0
}

# Auto-detect newest Excel master (sortuje sestupně podle jména — v0.4.0 > v0.3.2 > v0.3 > v0.2)
$wb = Get-ChildItem -Filter "BOURACKA-TESTPLAN-*.xlsx" |
      Sort-Object Name -Descending | Select-Object -First 1 -ExpandProperty Name
if (-not $wb) { $wb = "BOURACKA-TESTPLAN-v0.4.0.xlsx" }   # placeholder pro report

Check "Excel master present ($wb)"  { Test-Path $wb }
Check "check_priority_matrix exit 0" {
    if (-not (Test-Path $wb)) { return $false }
    if (-not (Test-Path "tools\check_priority_matrix.py")) { return $false }
    & py "tools\check_priority_matrix.py" $wb *> $null; $LASTEXITCODE -eq 0
}

Write-Host ""
Write-Host "Result: $ok passed, $fail failed" -ForegroundColor $(if ($fail -eq 0) { 'Green' } else { 'Yellow' })
Write-Host ""

if ($fail -gt 0) {
    Write-Host "Co dál:" -ForegroundColor Yellow
    Write-Host "  - Pokud chybí py / openpyxl / Node: viz INSTALL-FROM-ZERO-v0.4-CS.md §3" -ForegroundColor Gray
    Write-Host "  - Pokud chybí Playwright: npm install + npx playwright install chromium" -ForegroundColor Gray
    Write-Host "  - Pokud chybí Excel master nebo skript: viz §6.1 (Recovery patterns)" -ForegroundColor Gray
    Write-Host "  - Plný troubleshoot: §10 v install guide" -ForegroundColor Gray
}
exit $fail
