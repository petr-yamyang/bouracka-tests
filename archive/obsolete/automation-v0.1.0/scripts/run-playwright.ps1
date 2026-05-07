<#
.SYNOPSIS
  Run Playwright suite for bouracka-tests.

.DESCRIPTION
  Per CLIENT-PILOT-SUPIN-V0.1.md §8 + AMENDMENT 2 mobile-first.
  Drives the projects defined in playwright/playwright.config.ts.

.PARAMETER Env
  tst | tst-demo | public  (default: tst)

.PARAMETER Project
  Optional project filter — passed verbatim to Playwright --project.
  Examples: tst-desktop, tst-mobile-375, tst-demo-mobile-414

.EXAMPLE
  .\run-playwright.ps1 -Env tst
  .\run-playwright.ps1 -Env tst-demo -Project tst-demo-mobile-375

.NOTES
  Run from bouracka-tests/ root. Requires Node ≥ 18 + npm install completed.
#>
param(
  [ValidateSet("tst","tst-demo","public")]
  [string]$Env = "tst",
  [string]$Project = ""
)

$ErrorActionPreference = "Stop"
$env:BOURACKA_ENV = $Env

Write-Host "[run-playwright] env = $Env" -ForegroundColor Cyan
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
  $args = @("playwright","test","--config=playwright/playwright.config.ts")
  if ($Project) { $args += "--project=$Project" }
  npx @args
  $exit = $LASTEXITCODE
} finally {
  Pop-Location
}
exit $exit
