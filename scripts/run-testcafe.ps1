<#
.SYNOPSIS
  Run TestCafe suite for bouracka-tests (fallback per Gate 1).

.PARAMETER Env
  tst | tst-demo | public  (default: tst)

.EXAMPLE
  .\run-testcafe.ps1 -Env tst
#>
param(
  [ValidateSet("tst","tst-demo","public")]
  [string]$Env = "tst"
)
$ErrorActionPreference = "Stop"
$env:BOURACKA_ENV = $Env

Write-Host "[run-testcafe] env = $Env" -ForegroundColor Cyan
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
  npx testcafe chrome:headless "testcafe/tests/**/*.test.ts" --config-file testcafe/.testcaferc.json
  $exit = $LASTEXITCODE
} finally {
  Pop-Location
}
exit $exit
