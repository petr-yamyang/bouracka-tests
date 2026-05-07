<#
.SYNOPSIS
  Assemble the SUPIN-facing delivery package for bouracka-tests v0.1.0.

.DESCRIPTION
  Produces delivery/v0.1.0/ with the CS-only documentation set + the
  runnable suite zip + checksums + manifest. Per
  _specs/DOCUMENTATION-POLICY-v0.1.md §3.

  What goes in:
    01..06 — CS-only docs derived from internal recon + specs
    bouracka-tests-v0.1.0.zip + .SHA256
    MANIFEST-CS.md

.PARAMETER Version
  Semver of the delivery (default 0.1.0).

.EXAMPLE
  .\scripts\package-delivery-v0.1.0.ps1 -Version 0.1.0
#>
param(
  [string]$Version = "0.1.0"
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
Write-Host "[package-delivery] cwd = $root  version = $Version" -ForegroundColor Cyan

$delivery = Join-Path $root "delivery\v$Version"
if (Test-Path $delivery) { Remove-Item -Recurse -Force $delivery }
New-Item -ItemType Directory -Force -Path $delivery | Out-Null

# 1. Build the suite zip first (same logic as scripts/package-deliverable.ps1
#    but writes into delivery/v$Version/)
$zipName = "bouracka-tests-v$Version.zip"
$zipPath = Join-Path $delivery $zipName
$stage = Join-Path $env:TEMP "bouracka-tests-stage-$([guid]::NewGuid())"
New-Item -ItemType Directory -Path $stage | Out-Null

$include = @(
  'package.json', 'README-CS.md', 'README-EN.md', '.gitignore',
  'BOURACKA-TESTPLAN-v0.1.xlsx',
  'env', 'fixtures', 'playwright', 'cypress', 'testcafe',
  'scripts', 'tools', '_install', '_specs', 'specs'
)
foreach ($i in $include) {
  if (Test-Path (Join-Path $root $i)) {
    Copy-Item -Recurse -Force (Join-Path $root $i) $stage
  }
}
# Sanitise: nuke any node_modules, secrets, runs that slipped in
Get-ChildItem -Path $stage -Recurse -Force -Directory `
  -Include 'node_modules','secrets','runs' -ErrorAction SilentlyContinue |
  Remove-Item -Recurse -Force

Compress-Archive -Path "$stage\*" -DestinationPath $zipPath -Force
Remove-Item -Recurse -Force $stage

# Compute SHA256
$hash = (Get-FileHash $zipPath -Algorithm SHA256).Hash
"$hash  $zipName" | Out-File -FilePath (Join-Path $delivery "$zipName.SHA256") -Encoding utf8
Write-Host "[OK] $zipName  SHA256=$hash" -ForegroundColor Green

# 2. Stub CS-only documentation files (CP-SUPIN-03 fills them).
#    For now we emit placeholders that link to the internal sources.
$docs = @(
  @{ name = "00_README-CS.md";              src = "delivery/v$Version/MANIFEST-CS.md (sibling)";                  title = "Úvodní průvodce" },
  @{ name = "01_TESTPLAN-CS.md";            src = "recon/TEST-TARGET-CANDIDATES.md + 02_TestCases sheet";          title = "Testovací plán Bouračka v$Version" },
  @{ name = "02_DIAGRAMY-AKTIVIT-CS.md";    src = "recon/diagrams/extracted/ACTIVITY-DIAGRAMS-v0.1.md (CS-mirror)"; title = "Diagramy aktivit (D00..D17)" },
  @{ name = "03_INSTALL-PRO-SECOPS-CS.md";  src = "_install/INSTALL-PLAN-SUPNB-v0.1.md (translated)";              title = "Instalační průvodce pro SecOps" },
  @{ name = "04_SLOVNIK-CS.md";             src = "recon/cs-locale-reference/CALIBRATION-CORPUS-v0.1.md §1b";       title = "Slovník pojmů" },
  @{ name = "05_PRIRUCKA-TESTERA-CS.md";    src = "README-CS.md (kořen)";                                          title = "Příručka pro testera" },
  @{ name = "06_POKRYTI-CS.md";             src = "recon/COVERAGE-GAP-ANALYSIS.md (CS-mirror)";                    title = "Pokrytí — analýza mezer" }
)

foreach ($d in $docs) {
  $body = @"
# $($d.title)

> **Status:** placeholder — vyplněno v rámci CP-SUPIN-03.
> **Zdroj pro CS překlad:** `$($d.src)`.
> **Jazyk:** výhradně čeština pro recenzi SUPIN stakeholdery.
>
> Tento soubor je součástí `delivery/v$Version/` balíčku, který se předává
> SUPIN k revizi. Interní zdroj se nachází v repozitáři pod cestou výše.

## TODO pro CP-SUPIN-03

- [ ] Přeložit obsah ze zdrojového souboru do češtiny.
- [ ] Doplnit odkazy na konkrétní sekce zdrojového dokumentu.
- [ ] Validovat proti `_specs/DOCUMENTATION-POLICY-v0.1.md` §1.2 (CS-only pravidla).
- [ ] Recenzovat (Petr) před odesláním.

---

*Vygenerováno automaticky pomocí `scripts/package-delivery-v$Version.ps1` 2026-MM-DD.*
"@
  $body | Out-File -FilePath (Join-Path $delivery $d.name) -Encoding utf8
}

# 3. MANIFEST-CS.md — top-level index (CS)
$manifestBody = @"
# MANIFEST — bouracka-tests v$Version delivery — CS

> Tento manifest popisuje obsah dodávky `bouracka-tests-v$Version.zip`
> a doprovodné dokumentace. Předáno SUPIN k revizi v souladu s
> politikou stanovenou v interním dokumentu
> ``_specs/DOCUMENTATION-POLICY-v0.1.md`` (jazyk = výhradně čeština
> pro recenzi).

## Obsah balíčku

| # | Soubor | Účel | Recenzent |
|---|--------|------|-----------|
| 00 | ``00_README-CS.md`` | Úvodní průvodce | SUPIN architekt |
| 01 | ``01_TESTPLAN-CS.md`` | Testovací plán Bouračka v$Version | SUPIN architekt + QA lead |
| 02 | ``02_DIAGRAMY-AKTIVIT-CS.md`` | Diagramy aktivit D00..D17 | SUPIN QA + analytik |
| 03 | ``03_INSTALL-PRO-SECOPS-CS.md`` | Instalační průvodce pro SecOps | ČKP SecOps |
| 04 | ``04_SLOVNIK-CS.md`` | Slovník pojmů | všichni |
| 05 | ``05_PRIRUCKA-TESTERA-CS.md`` | Příručka pro testera | tester (Petr + kolegové) |
| 06 | ``06_POKRYTI-CS.md`` | Analýza pokrytí — mezery | SUPIN QA + Petr |
| –  | ``bouracka-tests-v$Version.zip`` | Spustitelný kód testovací sady | tester |
| –  | ``bouracka-tests-v$Version.zip.SHA256`` | Kontrolní součet | tester |

## Spuštění bring-up smoke testu (po instalaci)

```powershell
cd %USERPROFILE%\bouracka-tests
.\scripts\run-bring-up-smoke.ps1
```

Tento jeden test ověří, že notebook + nainstalovaná sada + pipeline
jsou funkční. Test běží proti **veřejné** ``www.bouracka.cz`` —
nepotřebuje VPN do SUPIN intranetu, neexponuje žádné testovací
prostředí. Doba běhu: cca 30 sekund. Výsledek: zelený = sada je živá;
červený = problém v prostředí (Node, Playwright, proxy, firewall) —
nikdy ne regrese aplikace Bouračka.

## Zpětná vazba k revizi

E-mail: petr.yamyang@gmail.com
Subjekt: ``[BOURACKA-TESTS REVIZE v$Version] <téma>``

## Status

| Položka | Hodnota |
|---------|---------|
| Verze balíčku | v$Version |
| Datum sestavení | $(Get-Date -Format 'yyyy-MM-dd') |
| SHA256 zipu | $hash |
| Jazyk | výhradně čeština |
| Cílová revize | SUPIN stakeholders |
| Stav | k revizi |

---

*Sestaveno pomocí ``scripts/package-delivery-v$Version.ps1``.*
"@

$manifestBody | Out-File -FilePath (Join-Path $delivery "MANIFEST-CS.md") -Encoding utf8

# 4. Summary
Write-Host ""
Write-Host "[OK] delivery package assembled at: $delivery" -ForegroundColor Green
Get-ChildItem $delivery |
  Sort-Object Name |
  Format-Table Name, @{N='Type';E={if ($_.PSIsContainer) {'dir'} else {'file'}}}, @{N='KB';E={[math]::Round($_.Length/1KB,1)}} -AutoSize

Write-Host ""
Write-Host "[next] CP-SUPIN-03 fills the CS placeholders 00..06 with translated content." -ForegroundColor Cyan
exit 0
