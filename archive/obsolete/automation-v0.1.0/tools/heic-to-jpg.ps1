<#
.SYNOPSIS
  Batch-convert HEIC photos to JPG for ingestion by the test toolchain.

.DESCRIPTION
  Reads every *.HEIC in the source folder, writes resized JPG into the
  destination folder. Skips files already present (idempotent — safe to
  re-run when new photos arrive).

  Requires ImageMagick on Windows:
    winget install ImageMagick.ImageMagick

  After install, restart the shell so 'magick' is on PATH.

.PARAMETER Source
  Source folder containing *.HEIC files.

.PARAMETER Destination
  Destination folder for *.jpg outputs.

.PARAMETER MaxWidth
  Resize so the longer dimension does not exceed this value (default 1800).

.PARAMETER Quality
  JPEG quality 1-100 (default 82 — good for OCR-quality reading).

.EXAMPLE
  .\tools\heic-to-jpg.ps1 -Source 'C:\Users\vitez\Documents\VibeCodeProjects\SUPIN\analyticke vstupy' `
                          -Destination .\recon\photos
#>
param(
  [Parameter(Mandatory = $true)] [string]$Source,
  [Parameter(Mandatory = $true)] [string]$Destination,
  [int]$MaxWidth = 1800,
  [int]$Quality = 82
)
$ErrorActionPreference = 'Continue'

if (-not (Test-Path $Source)) {
  Write-Host "[FAIL] source folder not found: $Source" -ForegroundColor Red
  exit 1
}
$mag = Get-Command magick -ErrorAction SilentlyContinue
if (-not $mag) {
  Write-Host "[FAIL] ImageMagick 'magick' is not on PATH." -ForegroundColor Red
  Write-Host "       Install:  winget install ImageMagick.ImageMagick" -ForegroundColor Yellow
  Write-Host "       Then close + reopen this PowerShell window so PATH refreshes." -ForegroundColor Yellow
  exit 1
}

if (-not (Test-Path $Destination)) {
  New-Item -ItemType Directory -Force -Path $Destination | Out-Null
}

$converted = 0; $skipped = 0; $failed = 0
$heicFiles = Get-ChildItem -Path $Source -Filter '*.HEIC' -File
Write-Host "[heic-to-jpg] found $($heicFiles.Count) HEIC files in $Source" -ForegroundColor Cyan

foreach ($f in $heicFiles) {
  $outPath = Join-Path $Destination ($f.BaseName + '.jpg')
  if (Test-Path $outPath) {
    $skipped++
    continue
  }
  & magick $f.FullName -resize "$($MaxWidth)x$($MaxWidth)>" -quality $Quality $outPath 2>&1 | Out-Null
  if ($LASTEXITCODE -eq 0 -and (Test-Path $outPath)) {
    $converted++
    $kb = [math]::Round((Get-Item $outPath).Length / 1KB, 1)
    Write-Host "[OK] $($f.Name) -> $($f.BaseName).jpg  $kb KB" -ForegroundColor Green
  } else {
    $failed++
    Write-Host "[FAIL] $($f.Name)" -ForegroundColor Red
  }
}

Write-Host ""
Write-Host "[heic-to-jpg] converted=$converted  skipped=$skipped  failed=$failed" -ForegroundColor Cyan
exit ($(if ($failed -gt 0) { 1 } else { 0 }))
