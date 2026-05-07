<#
.SYNOPSIS
  Assemble the AUTOMATION FRAMEWORK delivery package for SecDev install.

.DESCRIPTION
  Per the user direction: "automation framework must be as
  self-contained as possible — installable by SecDev with no other
  reference".

  Output: delivery/automation-v0.1.0/ with the framework code +
  TestPlan Excel + the SecDev one-stop install guide
  (INSTALL-CS.md) + lockfile-driven reproducible install +
  setup-from-zero.ps1.

  Excludes: recon/ (working materials), photos, secrets, runs/,
  delivery/ (avoid recursion), node_modules.

.PARAMETER Version
  Semver of the delivery (default 0.1.0).

.PARAMETER IncludeOfflineNpmCache
  If set, additionally pre-fetch all npm dependencies into
  .npm-offline-cache\ inside the package so SecDev can install
  WITHOUT network access. Adds ~50–100 MB to the package.
  Requires Node + npm on the operator's machine when running this
  packager.

.EXAMPLE
  .\scripts\package-delivery-automation-v0.1.0.ps1 -Version 0.1.0
#>
param(
  [string]$Version = "0.1.0",
  [switch]$IncludeOfflineNpmCache
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
Write-Host "[package-automation] cwd = $root  version = $Version" -ForegroundColor Cyan

$delivery = Join-Path $root "delivery\automation-v$Version"
if (Test-Path $delivery) { Remove-Item -Recurse -Force $delivery }
New-Item -ItemType Directory -Force -Path $delivery | Out-Null

# ── What goes IN (curated for self-containment) ─────────────────────────────
$files = @(
  'package.json',
  'package-lock.json',     # may not exist yet — tolerated
  'README-CS.md',
  'README-EN.md',
  '.gitignore',
  'BOURACKA-TESTPLAN-v0.1.xlsx',
  '_install\INSTALL-CS.md'        # SecDev one-stop guide; PROMOTED to root
)
$dirs = @(
  'env',
  'fixtures',                     # non-secret; secrets/ is gitignored anyway
  'playwright',
  'cypress',
  'testcafe',
  'scripts',
  'tools',
  '_install',                     # full install plan suite (CS+EN)
  '_specs',                       # spec format docs (so dev sessions work)
  'specs'                         # per-TC SPEC.md (so dev sessions read them)
)

foreach ($f in $files) {
  $src = Join-Path $root $f
  if (Test-Path $src) {
    $dstParent = Split-Path (Join-Path $delivery $f) -Parent
    if (-not (Test-Path $dstParent)) { New-Item -ItemType Directory -Force -Path $dstParent | Out-Null }
    Copy-Item $src (Join-Path $delivery $f) -Force
  }
}

# Promote INSTALL-CS.md to the package root for visibility
if (Test-Path "$root\_install\INSTALL-CS.md") {
  Copy-Item "$root\_install\INSTALL-CS.md" "$delivery\INSTALL-CS.md" -Force
  Write-Host "[OK] promoted INSTALL-CS.md to package root" -ForegroundColor Green
}

foreach ($d in $dirs) {
  $src = Join-Path $root $d
  if (Test-Path $src) {
    Copy-Item -Recurse $src (Join-Path $delivery $d) -Force
  }
}

# Sanitise — defence in depth even if the source doesn't have these
foreach ($pattern in @('node_modules','runs','secrets','*.log','.~lock*')) {
  Get-ChildItem -Path $delivery -Recurse -Force -Filter $pattern -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
}

# ── Optional: offline npm cache ─────────────────────────────────────────────
if ($IncludeOfflineNpmCache) {
  $npm = Get-Command npm -ErrorAction SilentlyContinue
  if (-not $npm) {
    Write-Host "[WARN] -IncludeOfflineNpmCache set but npm not on PATH; skipping cache step." -ForegroundColor Yellow
  } else {
    Write-Host "[package-automation] pre-fetching npm dependencies (≈ 2–5 min)..." -ForegroundColor Cyan
    Push-Location $delivery
    try {
      $cacheDir = Join-Path $delivery ".npm-offline-cache"
      New-Item -ItemType Directory -Force -Path $cacheDir | Out-Null
      # Use npm pack to put each resolved tarball into the cache
      npm install --pack-destination "$cacheDir" --ignore-scripts --no-save 2>&1 | Out-Null
      Get-ChildItem $cacheDir -Filter '*.tgz' |
        ForEach-Object { Write-Host "[OK] cached $($_.Name)" -ForegroundColor Green }
      $cnt = (Get-ChildItem $cacheDir -Filter '*.tgz').Count
      Write-Host "[OK] $cnt offline tarball(s) in .npm-offline-cache\" -ForegroundColor Green
    } finally {
      Pop-Location
    }
  }
}

# ── MANIFEST-CS.md (entry point for SecDev) ─────────────────────────────────
$mfBody = @"
# MANIFEST — bouracka-tests automatizace v$Version — CS

> **Co tento balíček obsahuje:** plnou automatizační framework sadu —
> kód (Playwright/Cypress/TestCafe), testovací plán (Excel), všechny
> instalační dokumenty, validační skripty, smoke test. **Samostatný
> balíček** — instalovatelný SecDev týmem bez odkazů na jiné zdroje.
>
> **Cíl:** SUPNB001 + SUPNB002 + SUPNB003 (HP EliteBook G11 class,
> Win 11 Enterprise 25H2).

## Co dělat — krok za krokem

### 1. Rozbalte balíček

Balíček dorazil v ZIP dílech. Postup v
``_install/EMAIL-DELIVERY-GUIDE-CS.md``.

### 2. Otevřete instalační průvodce

```
INSTALL-CS.md   ← v kořeni balíčku, hlavní dokument pro SecDev
```

Průvodce vás provede:
- Co musí povolit SecOps (firewall allowlist + AppLocker pravidla)
- Co stáhnout (Node.js MSI nebo winget)
- Jeden příkaz pro instalaci (``setup-from-zero.ps1``)
- Diagnostiku selhání

### 3. Spuštění one-command setup

Po přípravě prostředí:

```powershell
cd C:\Users\<vy>\bouracka-tests
.\scripts\setup-from-zero.ps1
```

Cca 8–12 minut. Konec hlásí ``[OK] sada je nainstalována a otestována``.

### 4. Předání testerovi

Po zelené kontrole je sada připravená. Tester se řídí ``README-CS.md``
v kořeni balíčku.

## Obsah balíčku — strom

```
bouracka-tests/                              ← top-level kontejner
├── INSTALL-CS.md                            ← SecDev hlavní průvodce
├── README-CS.md                             ← README pro testera
├── README-EN.md                             ← README pro testera (EN)
├── package.json                             ← deklarace závislostí
├── package-lock.json                        ← uzamčené verze
$(if ($IncludeOfflineNpmCache) {
"├── .npm-offline-cache/                      ← offline npm balíčky"
})
├── BOURACKA-TESTPLAN-v0.1.xlsx              ← TestPlán + TC List (12 listů)
├── env/                                     ← konfigurace prostředí
├── fixtures/                                ← testovací data (bez secrets)
├── playwright/                              ← Playwright framework
├── cypress/                                 ← Cypress framework
├── testcafe/                                ← TestCafe framework
├── scripts/                                 ← všechny .ps1 skripty
├── tools/                                   ← pomocné nástroje
├── _install/                                ← všechny instalační dokumenty
├── _specs/                                  ← formální specifikace
└── specs/                                   ← per-TC SPEC.md soubory
```

## Co tento balíček NEOBSAHUJE

- Recon materiály, fotografie, drift logy — interní pracovní materiály
  (jsou v samostatném balíčku ``analytical-v$Version`` pro recenzi).
- ``node_modules/`` — instaluje se ``npm ci`` z ``package-lock.json``.
- ``runs/`` — výsledky testů, vznikají během provozu.
- ``secrets/`` — citlivá testovací data; dodává se odděleně OOB.
- Playwright Chromium binárka (~600 MB) — stahuje
  ``npx playwright install chromium`` během setup.

## Síťové požadavky pro instalaci

Detail v ``INSTALL-CS.md`` §1.1. Stručně:
- ``registry.npmjs.org`` (npm balíčky)
- ``cdn.playwright.dev`` (Chromium binárka)
- ``github.com`` (občas)

## Síťové požadavky pro provoz

Detail v ``INSTALL-CS.md`` §1.1. Stručně:
- ``tst.bouracka.cz`` + ``tst.demo.bouracka.cz`` (testovací prostředí)
- ``*.supin.cz``, ``*.ckp.cz`` (CDN + integrace)

## Reportování problémů

E-mail: ``petr.yamyang@gmail.com``
Subjekt: ``[BOURACKA-TESTS INSTAL] <konkrétní problém>``

## Verze

| Položka | Hodnota |
|---------|---------|
| Verze | v$Version |
| Datum sestavení | $(Get-Date -Format 'yyyy-MM-dd') |
| Sestavil | $env:USERNAME na $env:COMPUTERNAME |
| Offline npm cache | $(if ($IncludeOfflineNpmCache) {'ANO (pre-fetched tarbally)'} else {'NE (online install vyžadován)'}) |
| Stav | v0.1 — připraveno pro SecDev |
"@
$mfBody | Out-File -FilePath (Join-Path $delivery "MANIFEST-CS.md") -Encoding utf8

# ── Summary ─────────────────────────────────────────────────────────────────
Write-Host ""
$totalSize = (Get-ChildItem $delivery -Recurse -File | Measure-Object -Property Length -Sum).Sum
$totalCount = (Get-ChildItem $delivery -Recurse -File).Count
Write-Host "[OK] automation delivery: $delivery" -ForegroundColor Green
Write-Host "     total: $totalCount files, $([math]::Round($totalSize/1MB,2)) MB" -ForegroundColor Green
Write-Host ""
Write-Host "[next] Email-package via:" -ForegroundColor Cyan
Write-Host "       .\scripts\package-email-volumes.ps1 -SourceDir '$delivery' -OutDir <wherever>" -ForegroundColor Cyan
exit 0
