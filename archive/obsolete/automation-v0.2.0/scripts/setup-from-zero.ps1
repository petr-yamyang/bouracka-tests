<#
.SYNOPSIS
  One-command SecDev install: from raw bouracka-tests/ folder to a
  green bring-up smoke against public bouracka.cz.

.DESCRIPTION
  Executes the full install dance:
    1. Verify Node.js ≥ 18 + npm on PATH.
    2. npm ci (reproducible install per package-lock.json).
    3. npx playwright install chromium.
    4. validate-install.ps1 — full pre-flight.
    5. run-bring-up-smoke.ps1 — one Playwright spec; ~30 s.

  Halts on first failure with a clear pointer to the diagnostic.
  Idempotent — safe to re-run.

  Documented in CS at _install/INSTALL-CS.md (the SecDev guide).

.EXAMPLE
  .\scripts\setup-from-zero.ps1
#>
$ErrorActionPreference = 'Continue'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
Write-Host "[setup-from-zero] cwd = $root" -ForegroundColor Cyan

# ── Step 1 — Node.js + npm ──────────────────────────────────────────────────
$node = Get-Command node -ErrorAction SilentlyContinue
$npm  = Get-Command npm  -ErrorAction SilentlyContinue
if (-not $node -or -not $npm) {
  Write-Host "[FAIL] Node.js or npm not on PATH." -ForegroundColor Red
  Write-Host "       Per _install/INSTALL-CS.md §3.1 — install Node 20 LTS per-user," -ForegroundColor Yellow
  Write-Host "       then close + reopen PowerShell so PATH refreshes." -ForegroundColor Yellow
  exit 1
}
$nodeVer = (& node --version 2>&1)
Write-Host "[setup-from-zero] node = $nodeVer / npm = $(& npm --version 2>&1)" -ForegroundColor Cyan

# ── Step 2 — npm ci (reproducible) ──────────────────────────────────────────
if (-not (Test-Path "$root\package-lock.json")) {
  Write-Host "[setup-from-zero] no package-lock.json → falling back to 'npm install'..." -ForegroundColor Yellow
  npm install
} else {
  Write-Host "[setup-from-zero] running 'npm ci' (≈ 2–5 min)..." -ForegroundColor Cyan
  npm ci
}
if ($LASTEXITCODE -ne 0) {
  Write-Host "[FAIL] npm install/ci failed (exit $LASTEXITCODE)." -ForegroundColor Red
  Write-Host "       Common causes (per _install/INSTALL-CS.md §4):" -ForegroundColor Yellow
  Write-Host "       - registry.npmjs.org unreachable (firewall) — SecOps allowlist" -ForegroundColor Yellow
  Write-Host "       - corp TLS-inspection without CA — run scripts\setup-npm-proxy.ps1" -ForegroundColor Yellow
  exit $LASTEXITCODE
}

# ── Step 3 — Playwright Chromium ────────────────────────────────────────────
$pwBrowsers = "$env:LOCALAPPDATA\ms-playwright"
$chromiumOk = $false
if (Test-Path $pwBrowsers) {
  $chromiumOk = (Get-ChildItem -Path $pwBrowsers -Directory -ErrorAction SilentlyContinue |
                   Where-Object { $_.Name -like 'chromium*' }).Count -gt 0
}
if (-not $chromiumOk) {
  Write-Host "[setup-from-zero] running 'npx playwright install chromium' (≈ 1–2 min)..." -ForegroundColor Cyan
  npx playwright install chromium
  if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Playwright Chromium install failed (exit $LASTEXITCODE)." -ForegroundColor Red
    Write-Host "       cdn.playwright.dev or playwright.azureedge.net unreachable?" -ForegroundColor Yellow
    Write-Host "       Check SecOps allowlist (_install/INSTALL-CS.md §1.1)." -ForegroundColor Yellow
    exit $LASTEXITCODE
  }
} else {
  Write-Host "[setup-from-zero] Playwright Chromium already present." -ForegroundColor Cyan
}

# ── Step 4 — validate-install.ps1 ───────────────────────────────────────────
Write-Host ""
Write-Host "[setup-from-zero] running validate-install.ps1 ..." -ForegroundColor Cyan
& "$root\scripts\validate-install.ps1"
$valEc = $LASTEXITCODE
if ($valEc -ne 0) {
  Write-Host ""
  Write-Host "[FAIL] validate-install reported issues (exit $valEc)." -ForegroundColor Red
  Write-Host "       JSON dump in: $root\runs\" -ForegroundColor Yellow
  Write-Host "       Review the [FAIL] lines above and fix per _install/INSTALL-CS.md §4." -ForegroundColor Yellow
  exit $valEc
}

# ── Step 5 — bring-up-smoke ─────────────────────────────────────────────────
Write-Host ""
Write-Host "[setup-from-zero] running bring-up-smoke (Playwright; ~30 s) ..." -ForegroundColor Cyan
& "$root\scripts\run-bring-up-smoke.ps1"
$smokeEc = $LASTEXITCODE

Write-Host ""
if ($smokeEc -eq 0) {
  Write-Host "[OK] sada je nainstalována a otestována; můžete předat testerovi." -ForegroundColor Green
  Write-Host "[OK] kit installed + tested; ready for tester handoff." -ForegroundColor Green
} else {
  Write-Host "[FAIL] bring-up-smoke red (exit $smokeEc)." -ForegroundColor Red
  Write-Host "       NOT a bouracka regression — environment problem (proxy/firewall/cert)." -ForegroundColor Yellow
  Write-Host "       Open trace: npx playwright show-report ..\playwright-report" -ForegroundColor Yellow
}
exit $smokeEc
