<#
.SYNOPSIS
  Validate the bouracka-tests install footprint on a SUPNB notebook.

.DESCRIPTION
  Per `_install/INSTALL-PLAN-SUPNB-v0.1.md` §9. Outputs JSON summary +
  a green/red final line. Run after `npm install` + `npx playwright
  install chromium`.

.OUTPUTS
  Exit code 0 on full pass; 1 on any check failure.
  JSON written to stdout; same content also saved to runs/<date>-validate.json.

.EXAMPLE
  .\scripts\validate-install.ps1
#>
$ErrorActionPreference = 'Continue'

function Test-Host([string]$Hostname, [int]$Port = 443) {
  try {
    return (Test-NetConnection -ComputerName $Hostname -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue)
  } catch { return $false }
}

function Get-VersionOrNull([string]$Cmd) {
  try {
    $out = & $env:ComSpec /c "$Cmd 2>nul"
    if ($LASTEXITCODE -eq 0 -and $out) { return ($out | Select-Object -First 1) }
  } catch { }
  return $null
}

$pwBrowsersDir = Join-Path $env:LOCALAPPDATA 'ms-playwright'
$pwBrowsers = @()
if (Test-Path $pwBrowsersDir) {
  $pwBrowsers = Get-ChildItem -Path $pwBrowsersDir -Directory -ErrorAction SilentlyContinue |
                  Select-Object -ExpandProperty Name
}

$result = [ordered]@{
  hostname             = $env:COMPUTERNAME
  user                 = $env:USERNAME
  os_caption           = (Get-CimInstance Win32_OperatingSystem).Caption
  os_version           = (Get-CimInstance Win32_OperatingSystem).Version
  os_build             = (Get-CimInstance Win32_OperatingSystem).BuildNumber
  arch                 = $env:PROCESSOR_ARCHITECTURE
  free_gb              = [math]::Round((Get-PSDrive -Name C).Free / 1GB, 1)
  node                 = Get-VersionOrNull 'node --version'
  npm                  = Get-VersionOrNull 'npm --version'
  playwright           = Get-VersionOrNull 'npx playwright --version'
  pw_browsers          = $pwBrowsers
  reachable_tst        = Test-Host 'tst.bouracka.cz' 443
  reachable_tst_demo   = Test-Host 'tst.demo.bouracka.cz' 443
  reachable_npmjs      = Test-Host 'registry.npmjs.org' 443
  reachable_pw_cdn     = Test-Host 'cdn.playwright.dev' 443
  reachable_pw_msft    = Test-Host 'playwright.download.prss.microsoft.com' 443
  reachable_recaptcha  = Test-Host 'www.google.com' 443
}

$json = $result | ConvertTo-Json -Depth 5
Write-Output $json

# Persist for SecOps collection
$root = Split-Path -Parent $PSScriptRoot
$runsDir = Join-Path $root 'runs'
if (-not (Test-Path $runsDir)) { New-Item -ItemType Directory -Force -Path $runsDir | Out-Null }
$logFile = Join-Path $runsDir ("{0}-validate-{1}.json" -f (Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'), $env:COMPUTERNAME)
$json | Out-File -FilePath $logFile -Encoding utf8

# Evaluate
$missing = @()
foreach ($k in 'node','npm','playwright') {
  if ([string]::IsNullOrWhiteSpace($result.$k)) { $missing += "$k missing" }
}
foreach ($k in 'reachable_tst','reachable_tst_demo','reachable_npmjs','reachable_pw_cdn') {
  if ($result.$k -ne $true) { $missing += "$k unreachable" }
}
if ($result.pw_browsers -notcontains 'chromium-1148' -and -not ($result.pw_browsers | Where-Object { $_ -like 'chromium*' })) {
  $missing += 'playwright chromium browser not installed'
}

Write-Host ""
if ($missing.Count -eq 0) {
  Write-Host "[OK] all checks pass" -ForegroundColor Green
  Write-Host "[OK] log saved: $logFile" -ForegroundColor Green
  exit 0
} else {
  Write-Host "[FAIL] $($missing.Count) check(s) failed:" -ForegroundColor Red
  $missing | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
  Write-Host "[FAIL] log saved: $logFile" -ForegroundColor Red
  exit 1
}
