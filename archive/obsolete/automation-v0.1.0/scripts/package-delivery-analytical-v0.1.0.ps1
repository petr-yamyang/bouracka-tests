<#
.SYNOPSIS
  Assemble the ANALYTICAL delivery package for SUPIN review.

.DESCRIPTION
  Per the user direction: "delivery contains only analytical
  artefacts — diagrams + draft of specification + testplan, no source
  photos or working materials".

  Output: delivery/analytical-v0.1.0/  with CS-only docs + Excel +
  rendered mindmap diagrams. Fits in ONE 5 MB email.

  Audience: SUPIN stakeholders (architect, QA lead, ČAP review board).

.PARAMETER Version
  Semver of the delivery (default 0.1.0).

.EXAMPLE
  .\scripts\package-delivery-analytical-v0.1.0.ps1 -Version 0.1.0
#>
param(
  [string]$Version = "0.1.0"
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
Write-Host "[package-analytical] cwd = $root  version = $Version" -ForegroundColor Cyan

$delivery = Join-Path $root "delivery\analytical-v$Version"
if (Test-Path $delivery) { Remove-Item -Recurse -Force $delivery }
New-Item -ItemType Directory -Force -Path $delivery | Out-Null

# 1. The CS-only documentation files (CP-SUPIN-03 fills concrete content;
#    we ship structured stubs here so the CS authors have a clear template)
$docs = @{
  "00_README-CS.md"           = "delivery/analytical/00_README-CS.md (CS author fills)"
  "01_TESTPLAN-CS.md"         = "delivery/analytical/01_TESTPLAN-CS.md (CS author fills)"
  "02_DIAGRAMY-AKTIVIT-CS.md" = "delivery/analytical/02_DIAGRAMY-AKTIVIT-CS.md (CS-mirror of recon/diagrams/extracted/ACTIVITY-DIAGRAMS-v0.1.md)"
  "03_TESTCASE-LIST-CS.md"    = "delivery/analytical/03_TESTCASE-LIST-CS.md (catalogue of 20 R1 TCs in CS)"
  "04_SLOVNIK-CS.md"          = "delivery/analytical/04_SLOVNIK-CS.md (from recon/cs-locale-reference/CALIBRATION-CORPUS-v0.1.md §1b)"
  "05_POKRYTI-CS.md"          = "delivery/analytical/05_POKRYTI-CS.md (CS-mirror of recon/COVERAGE-GAP-ANALYSIS.md)"
}

# Source files to copy verbatim
$copyVerbatim = @{
  "BOURACKA-TESTPLAN-v0.1.xlsx" = (Join-Path $root "BOURACKA-TESTPLAN-v0.1.xlsx")
}
$copyDirs = @{
  "diagrams" = (Join-Path $root "recon\diagrams")
}

# Stubs for the 6 CS docs (CP-SUPIN-03 fills with translated content)
foreach ($d in $docs.Keys) {
  $body = @"
# $($d -replace '\.md$' -replace '_', ' ' -replace '-', ' ')

> **Status:** placeholder pro CS překlad — vyplněno v CP-SUPIN-03.
> **Zdroj:** ``$($docs[$d])``
> **Jazyk:** výhradně čeština (pro recenzi SUPIN stakeholdery).
>
> Tento soubor je součástí ``delivery/analytical-v$Version/`` balíčku
> pro SUPIN. Interní zdroj je v repozitáři pod cestou výše.

## Co tento dokument obsahuje (až bude vyplněn)

(seznam sekcí podle zdrojového dokumentu — viz $($docs[$d]) v repozitáři)

## TODO pro CP-SUPIN-03

- [ ] Přeložit obsah ze zdroje do češtiny.
- [ ] Validovat dle ``_specs/DOCUMENTATION-POLICY-v0.1.md`` §1.2.
- [ ] Recenzovat (Petr) před odesláním.

---

*Vygenerováno automaticky pomocí ``scripts/package-delivery-analytical-v$Version.ps1`` $(Get-Date -Format 'yyyy-MM-dd').*
"@
  $body | Out-File -FilePath (Join-Path $delivery $d) -Encoding utf8
}

# Copy Excel + rendered diagrams
foreach ($f in $copyVerbatim.Keys) {
  if (Test-Path $copyVerbatim[$f]) {
    Copy-Item $copyVerbatim[$f] (Join-Path $delivery $f) -Force
    Write-Host "[OK] copied $f" -ForegroundColor Green
  } else {
    Write-Host "[WARN] missing source: $($copyVerbatim[$f])" -ForegroundColor Yellow
  }
}
foreach ($d in $copyDirs.Keys) {
  if (Test-Path $copyDirs[$d]) {
    # Copy only the rendered outputs (PNG/SVG/PDF), not the .dot sources
    $destSub = Join-Path $delivery $d
    New-Item -ItemType Directory -Force -Path $destSub | Out-Null
    Get-ChildItem -Path $copyDirs[$d] -File -Filter "*-mindmap.*" -ErrorAction SilentlyContinue |
      ForEach-Object { Copy-Item $_.FullName $destSub -Force }
    $count = (Get-ChildItem $destSub -File).Count
    Write-Host "[OK] copied $count file(s) → $d/" -ForegroundColor Green
  }
}

# 2. MANIFEST-CS.md — top-level index
$mfBody = @"
# MANIFEST — bouracka-tests analytická dodávka v$Version — CS

> Tento balíček obsahuje **pouze analytické artefakty** pro SUPIN
> recenzi: diagramy, návrh specifikace, testovací plán a katalog
> testovacích případů. Neobsahuje zdrojové fotografie, pracovní
> materiály ani spustitelný kód — ten je v samostatném balíčku
> ``automation-v$Version``.
>
> **Jazyk:** výhradně čeština (per ``_specs/DOCUMENTATION-POLICY-v0.1.md`` §1.2).

## Obsah

| Soubor | Účel |
|--------|------|
| ``00_README-CS.md`` | Úvod a pokyny pro recenzenty |
| ``01_TESTPLAN-CS.md`` | Testovací plán Bouračka v$Version |
| ``02_DIAGRAMY-AKTIVIT-CS.md`` | Diagramy aktivit D00..D17 |
| ``03_TESTCASE-LIST-CS.md`` | Katalog testovacích případů (R1) |
| ``04_SLOVNIK-CS.md`` | Slovník pojmů |
| ``05_POKRYTI-CS.md`` | Analýza pokrytí — mezery |
| ``BOURACKA-TESTPLAN-v0.1.xlsx`` | Testovací plán v Excelu (12 listů) |
| ``diagrams/tt-mindmap.{png,svg,pdf}`` | Mindmapa testovacích cílů |
| ``diagrams/tc-mindmap.{png,svg,pdf}`` | Mindmapa testovacích případů |

## Formát

- Markdown (``.md``) — čitelný v jakémkoliv prohlížeči/editoru.
- Excel (``.xlsx``) — Microsoft Excel, LibreOffice Calc.
- Mindmapy: PNG (rastrové) + SVG (vektorové) + PDF (tisk).

## Co tento balíček NEOBSAHUJE

- Spustitelný kód (Playwright/Cypress/TestCafe) — viz ``automation-v$Version``
- Zdrojové fotografie analytického dokumentu — interní pracovní materiál
- Recon poznámky, drift logy, test fixtures, secrets — interní

## Zpětná vazba k recenzi

E-mail: ``petr.yamyang@gmail.com``
Subjekt: ``[BOURACKA-TESTS RECENZE v$Version] <téma>``

## Verze a datum

| Položka | Hodnota |
|---------|---------|
| Verze | v$Version |
| Datum sestavení | $(Get-Date -Format 'yyyy-MM-dd') |
| Sestavil | $env:USERNAME na $env:COMPUTERNAME |
| Stav | k revizi |
"@
$mfBody | Out-File -FilePath (Join-Path $delivery "MANIFEST-CS.md") -Encoding utf8

# Summary
Write-Host ""
$totalSize = (Get-ChildItem $delivery -Recurse -File | Measure-Object -Property Length -Sum).Sum
Write-Host "[OK] analytical delivery: $delivery" -ForegroundColor Green
Write-Host "     total size: $([math]::Round($totalSize/1KB,1)) KB" -ForegroundColor Green
Write-Host ""
Write-Host "[next] Email-package via:" -ForegroundColor Cyan
Write-Host "       .\scripts\package-email-volumes.ps1 -SourceDir '$delivery' -OutDir <wherever>" -ForegroundColor Cyan
exit 0
