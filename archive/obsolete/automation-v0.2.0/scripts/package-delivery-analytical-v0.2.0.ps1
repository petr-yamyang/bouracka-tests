<#
.SYNOPSIS
  Assemble the ANALYTICAL delivery package v0.2.0 for SUPIN review.

.DESCRIPTION
  CP-SUPIN-03 successor to v0.1.0. Includes:
   - 7 CS narrative docs (00_README, 01_TESTPLAN, 02_DIAGRAMY-AKTIVIT,
     03_TESTCASE-LIST, 04_SLOVNIK, 05_POKRYTI, MANIFEST) seeded from
     synchro §6 templates
   - Excel v0.2 (21 sheets, 288 formulas, 0 errors)
   - rendered mindmaps (TT + TC × 3 formats each)

.EXAMPLE
  .\scripts\package-delivery-analytical-v0.2.0.ps1
#>
param(
  [string]$Version = "0.2.0"
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
Write-Host "[package-analytical] cwd = $root  version = $Version" -ForegroundColor Cyan

$delivery = Join-Path $root "delivery\analytical-v$Version"
if (Test-Path $delivery) { Remove-Item -Recurse -Force $delivery }
New-Item -ItemType Directory -Force -Path $delivery | Out-Null

# Source seeders are committed under delivery/analytical-v0.2.0-seeders/ (synchro §6)
$seedersDir = Join-Path $root "delivery\analytical-v0.2.0-seeders"
if (Test-Path $seedersDir) {
  Get-ChildItem $seedersDir -File -Filter '*.md' |
    ForEach-Object { Copy-Item $_.FullName $delivery -Force }
  Write-Host "[OK] copied $((Get-ChildItem $seedersDir -File -Filter '*.md').Count) seeders" -ForegroundColor Green
} else {
  Write-Host "[WARN] seeders folder not found: $seedersDir" -ForegroundColor Yellow
}

# Excel v0.2
if (Test-Path "$root\BOURACKA-TESTPLAN-v0.2.xlsx") {
  Copy-Item "$root\BOURACKA-TESTPLAN-v0.2.xlsx" "$delivery\BOURACKA-TESTPLAN-v0.2.xlsx" -Force
  Write-Host "[OK] copied Excel v0.2" -ForegroundColor Green
}

# Rendered mindmaps
$diagDest = Join-Path $delivery "diagrams"
New-Item -ItemType Directory -Force -Path $diagDest | Out-Null
Get-ChildItem "$root\recon\diagrams" -File -Filter "*-mindmap.*" -ErrorAction SilentlyContinue |
  ForEach-Object { Copy-Item $_.FullName $diagDest -Force }
$mmCount = (Get-ChildItem $diagDest -File).Count
Write-Host "[OK] copied $mmCount mindmap files" -ForegroundColor Green

# Summary
$totalSize = (Get-ChildItem $delivery -Recurse -File | Measure-Object -Property Length -Sum).Sum
Write-Host ""
Write-Host "[OK] analytical v$Version delivery: $delivery" -ForegroundColor Green
Write-Host "     total size: $([math]::Round($totalSize/1KB,1)) KB" -ForegroundColor Green
exit 0
