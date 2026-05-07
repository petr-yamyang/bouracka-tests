<#
.SYNOPSIS
  Bundle the latest run artefacts into a tester→ThinkPad delivery zip.

.DESCRIPTION
  Per CLIENT-PILOT-SUPIN-V0.1.md §6 — delivery model.
  Produces bouracka-results-YYYY-MM-DD.zip with:
   - playwright-report/   (HTML report)
   - cypress/screenshots/ + cypress/videos/ (if present)
   - testcafe-report/     (if present)
   - runs/<latest>/       (JSONL + Excel sheet update copy)
  SHA256 written to the zip filename and to a SHA256SUMS file.

.PARAMETER Tester
  Tester shortname appended to the run-folder ID (e.g. "jana").
#>
param(
  [string]$Tester = "tester"
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$today = Get-Date -Format "yyyy-MM-dd"
$runId = "$today-$Tester"
$zipPath = Join-Path $root "bouracka-results-$runId.zip"

Push-Location $root
try {
  if (Test-Path $zipPath) { Remove-Item $zipPath -Force }
  $stage = Join-Path $env:TEMP "bouracka-results-stage-$([guid]::NewGuid())"
  New-Item -ItemType Directory -Path $stage | Out-Null

  foreach ($dir in @("playwright-report","cypress","testcafe-report","runs")) {
    $src = Join-Path $root $dir
    if (Test-Path $src) {
      Copy-Item -Recurse -Force $src $stage
    }
  }
  # always include the latest Excel TestPlan
  if (Test-Path "BOURACKA-TESTPLAN-v0.1.xlsx") {
    Copy-Item "BOURACKA-TESTPLAN-v0.1.xlsx" $stage
  }

  Compress-Archive -Path "$stage\*" -DestinationPath $zipPath -Force
  Remove-Item -Recurse -Force $stage

  $hash = (Get-FileHash $zipPath -Algorithm SHA256).Hash
  "$hash  $(Split-Path $zipPath -Leaf)" | Out-File -FilePath (Join-Path $root "SHA256SUMS-$runId.txt") -Encoding utf8
  Write-Host "[OK] $zipPath  SHA256=$hash" -ForegroundColor Green
} finally {
  Pop-Location
}
