<#
.SYNOPSIS
  Bundle the dev-side deliverable (bouracka-tests-vX.Y.Z.zip) for SUPIN tester.

.DESCRIPTION
  Per CLIENT-PILOT-SUPIN-V0.1.md §6 + scope §7 — Phase A delivery (email zip).
  Excludes confidential recon/, gitignored fixtures, node_modules, runs/.
  Produces the zip + SHA256 for the email handoff.

.PARAMETER Version
  Semver like 0.1.0 (default: 0.1.0).

.EXAMPLE
  .\package-deliverable.ps1 -Version 0.1.0
#>
param(
  [string]$Version = "0.1.0"
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$zipName = "bouracka-tests-v$Version.zip"
$zipPath = Join-Path $root $zipName

Push-Location $root
try {
  if (Test-Path $zipPath) { Remove-Item $zipPath -Force }

  $stage = Join-Path $env:TEMP "bouracka-tests-stage-$([guid]::NewGuid())"
  New-Item -ItemType Directory -Path $stage | Out-Null

  $include = @(
    "package.json","README-CS.md","README-EN.md","DELIVERY-NOTES.md",
    ".gitignore","BOURACKA-TESTPLAN-v0.1.xlsx",
    "env","fixtures","playwright","cypress","testcafe","scripts"
  )
  foreach ($item in $include) {
    if (Test-Path (Join-Path $root $item)) {
      Copy-Item -Recurse -Force (Join-Path $root $item) $stage
    }
  }
  # Sanitise: remove gitignored sub-folders that may have slipped in
  Get-ChildItem -Path $stage -Recurse -Force -Directory `
    -Include "node_modules","secrets" -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force

  Compress-Archive -Path "$stage\*" -DestinationPath $zipPath -Force
  Remove-Item -Recurse -Force $stage

  $hash = (Get-FileHash $zipPath -Algorithm SHA256).Hash
  "$hash  $zipName" | Out-File -FilePath (Join-Path $root "SHA256SUMS-deliverable-v$Version.txt") -Encoding utf8
  Write-Host "[OK] $zipPath  SHA256=$hash" -ForegroundColor Green
  Write-Host "[OK] write the SHA256 line above into DELIVERY-NOTES.md before emailing." -ForegroundColor Yellow
} finally {
  Pop-Location
}
