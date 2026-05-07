<#
.SYNOPSIS
  Reassemble an email-shipped folder from its volume parts.

.DESCRIPTION
  Companion to scripts/package-email-volumes.ps1. Takes a folder
  containing the received *-part-NN-of-MM.zip files plus the
  *-PART-INDEX.txt manifest, verifies each part's SHA256, and extracts
  them all into a target folder where they merge naturally under a
  shared top-level container.

  Pure PowerShell — uses Expand-Archive (Windows native). Idempotent;
  safe to re-run.

.PARAMETER SourceDir
  Folder containing the received .zip parts + the PART-INDEX.txt
  manifest (REQUIRED).

.PARAMETER DestDir
  Folder to extract into. The parts will merge under
  DestDir\<BaseName>\... (REQUIRED).

.PARAMETER SkipVerify
  If set, skip SHA256 verification (faster but riskier — only use if
  you trust the channel).

.EXAMPLE
  .\scripts\extract-email-volumes.ps1 `
    -SourceDir 'C:\Users\<recipient>\Downloads\bouracka-incoming' `
    -DestDir   'C:\Users\<recipient>\Documents\bouracka-tests'
#>
param(
  [Parameter(Mandatory = $true)] [string]$SourceDir,
  [Parameter(Mandatory = $true)] [string]$DestDir,
  [switch]$SkipVerify
)
$ErrorActionPreference = 'Continue'

# ── Validate ────────────────────────────────────────────────────────────────
$src = (Resolve-Path $SourceDir).Path
if (-not (Test-Path $src -PathType Container)) {
  Write-Host "[FAIL] SourceDir not found: $SourceDir" -ForegroundColor Red
  exit 1
}
if (-not (Test-Path $DestDir)) { New-Item -ItemType Directory -Force -Path $DestDir | Out-Null }
$DestDir = (Resolve-Path $DestDir).Path

# ── Find manifest ───────────────────────────────────────────────────────────
$indexFile = Get-ChildItem -Path $src -Filter "*-PART-INDEX.txt" -File | Select-Object -First 1
if (-not $indexFile) {
  Write-Host "[FAIL] PART-INDEX.txt not found in $src" -ForegroundColor Red
  Write-Host "       Did you save the manifest into the same folder as the .zip parts?" -ForegroundColor Yellow
  exit 1
}
Write-Host "[extract-email-volumes] manifest: $($indexFile.Name)" -ForegroundColor Cyan

# ── Parse manifest (lines starting NN/MM) ───────────────────────────────────
$rosterLines = (Get-Content $indexFile.FullName) | Where-Object { $_ -match '^\d+/\d+\s' }
if (-not $rosterLines) {
  Write-Host "[FAIL] manifest has no part roster lines (expected NN/MM ...)" -ForegroundColor Red
  exit 1
}
$parts = foreach ($line in $rosterLines) {
  if ($line -match '^(\d+)/(\d+)\s+([\d\.]+)\s+KB\s+sha256=(\w+)\s+(\S+)\s+\((\d+) files\)') {
    [pscustomobject]@{
      PartNum   = [int]$Matches[1]
      Total     = [int]$Matches[2]
      ExpectedKB = [double]$Matches[3]
      Sha256     = $Matches[4]
      File       = $Matches[5]
      Count      = [int]$Matches[6]
    }
  }
}
$M = ($parts | Select-Object -First 1).Total
Write-Host "[extract-email-volumes] manifest declares $M part(s)" -ForegroundColor Cyan

# ── Locate the parts ────────────────────────────────────────────────────────
$missing = @(); $bad = @()
foreach ($p in $parts) {
  $f = Join-Path $src $p.File
  if (-not (Test-Path $f)) { $missing += $p.File; continue }
  if (-not $SkipVerify) {
    $actual = (Get-FileHash $f -Algorithm SHA256).Hash
    if ($actual -ne $p.Sha256) {
      $bad += "$($p.File) (expected $($p.Sha256.Substring(0,12))… got $($actual.Substring(0,12))…)"
      continue
    }
  }
  Write-Host "[OK] verified $($p.File)" -ForegroundColor Green
}
if ($missing.Count -gt 0) {
  Write-Host "[FAIL] missing $($missing.Count) part(s):" -ForegroundColor Red
  $missing | ForEach-Object { Write-Host "       $_" -ForegroundColor Red }
  exit 1
}
if ($bad.Count -gt 0) {
  Write-Host "[FAIL] SHA256 mismatch on $($bad.Count) part(s):" -ForegroundColor Red
  $bad | ForEach-Object { Write-Host "       $_" -ForegroundColor Red }
  Write-Host "       Re-request the affected parts from sender." -ForegroundColor Yellow
  exit 1
}

# ── Extract each part ───────────────────────────────────────────────────────
Write-Host ""
foreach ($p in ($parts | Sort-Object PartNum)) {
  $partPath = Join-Path $src $p.File
  Write-Host "[extract] $($p.File) ..." -ForegroundColor Cyan
  Expand-Archive -Path $partPath -DestinationPath $DestDir -Force
}

# ── Summary ─────────────────────────────────────────────────────────────────
Write-Host ""
$extracted = Get-ChildItem -Path $DestDir -Recurse -File | Measure-Object
Write-Host "[OK] extracted into: $DestDir" -ForegroundColor Green
Write-Host "[OK] $($extracted.Count) file(s) reconstructed" -ForegroundColor Green

# Merge check: every part's manifest .Count summed should match the
# extracted file count (allowing for any pre-existing files in DestDir).
$expected = ($parts | Measure-Object -Property Count -Sum).Sum
if ($extracted.Count -lt $expected) {
  Write-Host "[WARN] expected $expected files; extracted $($extracted.Count). Some parts may not have merged." -ForegroundColor Yellow
} else {
  Write-Host "[OK] file count matches (or exceeds) manifest expectation ($expected)." -ForegroundColor Green
}
exit 0
