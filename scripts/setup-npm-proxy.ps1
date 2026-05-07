<#
.SYNOPSIS
  Configure npm to traverse the int-ckp.cz corporate proxy
  (TLS-inspection-aware).

.DESCRIPTION
  Run ONCE per user, per notebook, before `npm install`. Idempotent.
  Per `_install/INSTALL-PLAN-SUPNB-v0.1.md` §7.

.PARAMETER ProxyUrl
  Corporate proxy URL — e.g. http://proxy.int-ckp.cz:8080
  Leave empty to skip proxy config (only sets the CA bundle).

.PARAMETER CaFile
  Path to the corporate root CA PEM bundle supplied by SecOps.
  E.g. C:\corp\ckp-root-ca.pem

.EXAMPLE
  .\setup-npm-proxy.ps1 -ProxyUrl "http://proxy.int-ckp.cz:8080" -CaFile "C:\corp\ckp-root-ca.pem"
#>
param(
  [string]$ProxyUrl = "",
  [string]$CaFile   = ""
)
$ErrorActionPreference = 'Stop'

if ($ProxyUrl) {
  Write-Host "[setup-npm-proxy] setting npm proxy = $ProxyUrl" -ForegroundColor Cyan
  npm config set proxy        $ProxyUrl
  npm config set https-proxy  $ProxyUrl
} else {
  Write-Host "[setup-npm-proxy] no -ProxyUrl provided; skipping proxy URL config" -ForegroundColor Yellow
}

if ($CaFile) {
  if (-not (Test-Path $CaFile)) { throw "[setup-npm-proxy] CA file not found: $CaFile" }
  Write-Host "[setup-npm-proxy] setting npm cafile = $CaFile" -ForegroundColor Cyan
  npm config set cafile $CaFile
} else {
  Write-Host "[setup-npm-proxy] no -CaFile provided; skipping CA bundle config" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[setup-npm-proxy] current effective config:" -ForegroundColor Cyan
npm config get proxy
npm config get https-proxy
npm config get cafile
Write-Host "[setup-npm-proxy] done — you can now run 'npm install'." -ForegroundColor Green
