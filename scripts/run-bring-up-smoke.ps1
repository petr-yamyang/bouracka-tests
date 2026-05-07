<#
.SYNOPSIS
  Run the bring-up smoke test against public bouracka.cz.

.DESCRIPTION
  Validates that the operator's notebook can run a Playwright test
  end-to-end. Does NOT require SUPIN intranet, test creds, or any
  integration mocks. Should complete in < 30 seconds on a healthy
  setup.

  GREEN  → kit is alive; CP-SUPIN-03 R1 work can begin.
  RED    → environment problem (Node / Playwright / browser binary /
           corp-proxy / firewall) — see playwright-report\ for trace.

.EXAMPLE
  cd $env:USERPROFILE\bouracka-tests   # OR …\Documents\VibeCodeProjects\SUPIN\bouracka-tests
  .\scripts\run-bring-up-smoke.ps1
#>
$ErrorActionPreference = 'Continue'

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
Write-Host "[bring-up-smoke] cwd = $root" -ForegroundColor Cyan

# Pre-flight: Node + Playwright present
$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) {
  Write-Host "[FAIL] Node.js not found on PATH." -ForegroundColor Red
  Write-Host "       Install per _install/INSTALL-PLAN-SUPNB-v0.1.md §5" -ForegroundColor Yellow
  exit 1
}

if (-not (Test-Path "$root\node_modules\@playwright\test")) {
  Write-Host "[bring-up-smoke] node_modules missing — running 'npm install'..." -ForegroundColor Yellow
  npm install
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if (-not (Test-Path "$env:LOCALAPPDATA\ms-playwright")) {
  Write-Host "[bring-up-smoke] Playwright browsers missing — installing chromium..." -ForegroundColor Yellow
  npx playwright install chromium
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Write-Host "[bring-up-smoke] running…" -ForegroundColor Cyan
Write-Host ""

# Run only the bring-up spec; chromium project; no Cypress / TestCafe needed
# CRITICAL: --config points at the SUBFOLDER playwright.config.ts where projects are defined.
# Without --config, Playwright looks in CWD root and finds no projects → 'Available projects: ""' error.
npx playwright test playwright/tests/bring-up-smoke.spec.ts `
  --config=playwright/playwright.config.ts `
  --project=public-mobile-375 `
  --reporter=list

$ec = $LASTEXITCODE

Write-Host ""
if ($ec -eq 0) {
  Write-Host "[OK] bring-up-smoke green — kit is alive." -ForegroundColor Green
  Write-Host "     Trace + screenshots (if any) in: $root\..\playwright-report\" -ForegroundColor Green
} else {
  Write-Host "[FAIL] bring-up-smoke red — environment problem, NOT a SUT regression." -ForegroundColor Red
  Write-Host "       Open trace: npx playwright show-report ..\playwright-report" -ForegroundColor Yellow
  Write-Host "       Common causes: corp proxy CA not configured, firewall blocking www.bouracka.cz," -ForegroundColor Yellow
  Write-Host "                      cdn.playwright.dev unreachable, browser binary missing." -ForegroundColor Yellow
}
exit $ec
