<#
.SYNOPSIS
  Run all three frameworks for bouracka-tests.

.DESCRIPTION
  Sequential execution: Playwright → Cypress → TestCafe.
  Aggregate exit code: 0 if all pass; otherwise the highest non-zero code.

.PARAMETER Env
  tst | tst-demo | public  (default: tst)

.PARAMETER SkipFramework
  Optional comma-separated list to skip: playwright | cypress | testcafe

.EXAMPLE
  .\run-all.ps1 -Env tst
  .\run-all.ps1 -Env tst -SkipFramework "testcafe"
#>
param(
  [ValidateSet("tst","tst-demo","public")]
  [string]$Env = "tst",
  [string]$SkipFramework = ""
)
$ErrorActionPreference = "Continue"
$skip = @($SkipFramework -split "," | ForEach-Object { $_.Trim().ToLower() }) | Where-Object { $_ }

$results = @{}

if (-not ($skip -contains "playwright")) {
  Write-Host "`n=== Playwright ===" -ForegroundColor Yellow
  & "$PSScriptRoot\run-playwright.ps1" -Env $Env
  $results["playwright"] = $LASTEXITCODE
}
if (-not ($skip -contains "cypress")) {
  Write-Host "`n=== Cypress ===" -ForegroundColor Yellow
  & "$PSScriptRoot\run-cypress.ps1" -Env $Env
  $results["cypress"] = $LASTEXITCODE
}
if (-not ($skip -contains "testcafe")) {
  Write-Host "`n=== TestCafe ===" -ForegroundColor Yellow
  & "$PSScriptRoot\run-testcafe.ps1" -Env $Env
  $results["testcafe"] = $LASTEXITCODE
}

Write-Host "`n=== Summary ===" -ForegroundColor Cyan
$results.GetEnumerator() | ForEach-Object {
  $status = if ($_.Value -eq 0) { "PASS" } else { "FAIL ($($_.Value))" }
  Write-Host "$($_.Key) -> $status"
}
$worst = ($results.Values | Measure-Object -Maximum).Maximum
exit $worst
