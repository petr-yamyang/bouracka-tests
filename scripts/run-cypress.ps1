<#
.SYNOPSIS
  Run Cypress suite for bouracka-tests.

.PARAMETER Env
  tst | tst-demo | public  (default: tst)

.EXAMPLE
  .\run-cypress.ps1 -Env tst
#>
param(
  [ValidateSet("tst","tst-demo","public")]
  [string]$Env = "tst"
)
$ErrorActionPreference = "Stop"
$env:BOURACKA_ENV = $Env

Write-Host "[run-cypress] env = $Env" -ForegroundColor Cyan
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
  npx cypress run --config-file cypress/cypress.config.ts
  $exit = $LASTEXITCODE
} finally {
  Pop-Location
}
exit $exit
