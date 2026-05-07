# run-all-and-package.ps1
# ────────────────────────────────────────────────────────────────────────────
# Per CP-SUPIN-04 v0.4.9. Bundled inside RUN-TESTS.cmd.
# Runs:
#   1. Integrity check (all critical source files null-free + parse-clean)
#   2. Playwright bring-up smoke
#   3. Playwright a2-alternates (8 ALT- tests)
#   4. Playwright a1-main-happy-day (single E2E)
#   5. Packages results into bouracka-results-YYYY-MM-DD-<surname>.zip
# ────────────────────────────────────────────────────────────────────────────

$ErrorActionPreference = "Continue"  # don't abort on test failure
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
Write-Host "[run-all] root = $root" -ForegroundColor Cyan

# ── 1. Integrity check ────────────────────────────────────────────────────
Write-Host ""
Write-Host "[1/5] Integrity check on critical source files..." -ForegroundColor Cyan
$check = @(
  ".\playwright\tests\bring-up-smoke.spec.ts",
  ".\playwright\tests\a2-alternates-demo.spec.ts",
  ".\playwright\tests\a1-main-happy-day-demo.spec.ts",
  ".\playwright\reporters\excel-row-writer.ts",
  ".\scripts\sanity-check.ps1"
)
$bad = 0
foreach ($f in $check) {
  if (-not (Test-Path $f)) {
    Write-Host ("       MISSING  {0}" -f $f) -ForegroundColor Red
    $bad++
    continue
  }
  $bytes = [System.IO.File]::ReadAllBytes($f)
  $nullCount = ($bytes | Where-Object { $_ -eq 0 }).Count
  $ok = ($nullCount -eq 0)
  if (-not $ok) { $bad++ }
  $status = if ($ok) { "OK " } else { "BAD" }
  $color  = if ($ok) { "Green" } else { "Red" }
  Write-Host ("       {0}  {1,-58} {2,7} bytes  nulls={3}" -f $status, $f, $bytes.Length, $nullCount) -ForegroundColor $color
}
if ($bad -gt 0) {
  Write-Host "[run-all] $bad file(s) corrupt — abort." -ForegroundColor Red
  exit 2
}

# ── 2. Bring-up smoke ──────────────────────────────────────────────────────
Write-Host ""
Write-Host "[2/5] Bring-up smoke..." -ForegroundColor Cyan
& npx playwright test --config=playwright\playwright.config.ts playwright\tests\bring-up-smoke.spec.ts
$smokeExit = $LASTEXITCODE
Write-Host "       exit=$smokeExit" -ForegroundColor (if ($smokeExit -eq 0) { "Green" } else { "Yellow" })

# ── 3. Alternates (8 ALT- tests) ───────────────────────────────────────────
Write-Host ""
Write-Host "[3/5] Alternates (ALT-1..ALT-10)..." -ForegroundColor Cyan
& npx playwright test --config=playwright\playwright.config.ts playwright\tests\a2-alternates-demo.spec.ts
$altExit = $LASTEXITCODE
Write-Host "       exit=$altExit" -ForegroundColor (if ($altExit -eq 0) { "Green" } else { "Yellow" })

# ── 4. Main happy day (will skip with rationale if DEMO drift) ─────────────
Write-Host ""
Write-Host "[4/5] A1 main happy day (drift-aware skip)..." -ForegroundColor Cyan
& npx playwright test --config=playwright\playwright.config.ts playwright\tests\a1-main-happy-day-demo.spec.ts
$a1Exit = $LASTEXITCODE
Write-Host "       exit=$a1Exit" -ForegroundColor (if ($a1Exit -eq 0) { "Green" } else { "Yellow" })

# ── 5. Package results ─────────────────────────────────────────────────────
Write-Host ""
Write-Host "[5/5] Packaging results..." -ForegroundColor Cyan
$today = Get-Date -Format "yyyy-MM-dd"
$surname = $env:USERNAME -replace '[^A-Za-z0-9]', ''
$resultZip = "$root\bouracka-results-$today-$surname.zip"
if (Test-Path $resultZip) { Remove-Item -Force $resultZip }

$bundleDirs = @()
if (Test-Path "$root\test-results")     { $bundleDirs += "$root\test-results" }
if (Test-Path "$root\playwright-report") { $bundleDirs += "$root\playwright-report" }

if ($bundleDirs.Count -gt 0) {
  Compress-Archive -Path $bundleDirs -DestinationPath $resultZip -Force
  $sz = (Get-Item $resultZip).Length
  Write-Host "       wrote: $resultZip ($([math]::Round($sz/1KB)) KB)" -ForegroundColor Green
  Write-Host "       sha256: $((Get-FileHash $resultZip -Algorithm SHA256).Hash)" -ForegroundColor Gray
} else {
  Write-Host "       no test-results / playwright-report dirs to bundle" -ForegroundColor Yellow
}

$worstExit = ($smokeExit, $altExit, $a1Exit | Measure-Object -Maximum).Maximum
Write-Host ""
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Green
Write-Host " Suite complete. worst-exit = $worstExit" -ForegroundColor Green
Write-Host " Mail back: $resultZip" -ForegroundColor Green
Write-Host " Most useful single artefact:" -ForegroundColor Green
Write-Host "   test-results\<run>\alt10-spa-post.json   (DEMO drift probe)" -ForegroundColor Green
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Green
exit $worstExit
