<#
.SYNOPSIS
  Assemble the AUTOMATION FRAMEWORK delivery package v0.2.0 for SecDev install.

.DESCRIPTION
  CP-SUPIN-03 successor to v0.1.0. Adds:
   - Excel v0.2 (21 sheets including 9 new + FURPS+ Cartesian + state machine)
   - playwright/runtime/spec-loader.ts
   - tools/generate_tests.py + tools/validate_workbook.py
   - mockoon/n8-sms-gateway.json
   - new TC-CP-005-SPEC.md
   - format-spec v0.2 docs
   - Mockoon CLI runtime expectation in INSTALL-CS

.EXAMPLE
  .\scripts\package-delivery-automation-v0.2.0.ps1
#>
param(
  [string]$Version = "0.2.0"
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
Write-Host "[package-automation] cwd = $root  version = $Version" -ForegroundColor Cyan

$delivery = Join-Path $root "delivery\automation-v$Version"
if (Test-Path $delivery) { Remove-Item -Recurse -Force $delivery }
New-Item -ItemType Directory -Force -Path $delivery | Out-Null

$files = @(
  'package.json', 'package-lock.json',
  'README-CS.md', 'README-EN.md', '.gitignore',
  'BOURACKA-TESTPLAN-v0.2.xlsx',
  '_install\INSTALL-CS.md'
)
$dirs = @(
  'env', 'fixtures',
  'playwright', 'cypress', 'testcafe',
  'scripts', 'tools',
  '_install', '_specs', 'specs',
  'mockoon'
)

foreach ($f in $files) {
  $src = Join-Path $root $f
  if (Test-Path $src) {
    $dst = Join-Path $delivery $f
    $dstParent = Split-Path $dst -Parent
    if (-not (Test-Path $dstParent)) { New-Item -ItemType Directory -Force -Path $dstParent | Out-Null }
    Copy-Item $src $dst -Force
  }
}

if (Test-Path "$root\_install\INSTALL-CS.md") {
  Copy-Item "$root\_install\INSTALL-CS.md" "$delivery\INSTALL-CS.md" -Force
}

foreach ($d in $dirs) {
  $src = Join-Path $root $d
  if (Test-Path $src) {
    Copy-Item -Recurse $src (Join-Path $delivery $d) -Force
  }
}

# Sanitise
foreach ($pattern in @('node_modules','runs','secrets','*.log','.~lock*')) {
  Get-ChildItem -Path $delivery -Recurse -Force -Filter $pattern -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
}

# MANIFEST-CS.md
$mfBody = @"
# MANIFEST -- bouracka-tests automatizace v$Version -- CS

> Plná automatizační framework sada v0.2.0 (CP-SUPIN-03). Nově obsahuje:
> - Excel v0.2 (21 listů včetně 9 nových: 00b_Requirements, 01b_Req_FURPS_Cartesian,
>   01c_StateMachine, 02b/c/d_TC_*, 05a/b/c_TestPlan/Schedule/Estimate)
> - playwright/runtime/spec-loader.ts (R-CONTRACT-1 — workbook is the live execution contract)
> - tools/generate_tests.py + tools/validate_workbook.py
> - mockoon/n8-sms-gateway.json (N8 SMS Gateway mock — INT-002)
> - format-spec v0.2 dokumenty
> - nový TC-CP-005-SPEC.md (SMS-OTP send + verify)

## Co dělat -- jak v v0.1, ale s NEW step pro Mockoon

Po instalaci podle INSTALL-CS.md, pro spuštění N8 mock:

``\`\`\`powershell
npm install -g @mockoon/cli
mockoon-cli start --data .\mockoon\n8-sms-gateway.json --port 8025
``\`\`\`

Smoke test bring-up je nezávislý (proti veřejné bouracka.cz),
ale kompletní R1 testy potřebují běžící Mockoon profil.

## Validace workbooku

``\`\`\`powershell
python tools\validate_workbook.py
``\`\`\`

10 checků; všechny musí být zelené před spuštěním testů.

## Verze

| Položka | Hodnota |
|---------|---------|
| Verze | v$Version |
| Datum sestavení | $(Get-Date -Format 'yyyy-MM-dd') |
| Sestavil | $env:USERNAME na $env:COMPUTERNAME |
| Schémická migrace z v0.1 | per tools/rev7_xlsx_v02_migration.py |
| Stav | v0.2 -- připraveno pro SecDev |
"@
$mfBody | Out-File -FilePath (Join-Path $delivery "MANIFEST-CS.md") -Encoding utf8

# Summary
$totalSize = (Get-ChildItem $delivery -Recurse -File | Measure-Object -Property Length -Sum).Sum
$totalCount = (Get-ChildItem $delivery -Recurse -File).Count
Write-Host ""
Write-Host "[OK] automation v$Version delivery: $delivery" -ForegroundColor Green
Write-Host "     total: $totalCount files, $([math]::Round($totalSize/1MB,2)) MB" -ForegroundColor Green
exit 0
