# package-hp-elite-v0.1.0.ps1 — assembles both HP Elite distribution ZIPs.
#
# Usage (run from bouracka-tests/ root):
#   .\delivery\package-hp-elite-v0.1.0.ps1
#
# What it does:
#   1. Validates that the freshly-built wheel exists at bouracka_ui/dist/.
#   2. Validates that BOURACKA-TESTPLAN-*.xlsx exists in repo root.
#   3. Copies wheel + workbook into both delivery/bouracka-ui-hp-elite-v0.1.0-{EN,CS}/.
#   4. Generates SHA256SUMS.txt for each delivery folder.
#   5. Produces delivery/bouracka-ui-hp-elite-v0.1.0-EN.zip
#                delivery/bouracka-ui-hp-elite-v0.1.0-CS.zip
#   6. Prints the final SHA256 of each ZIP for record-keeping.
#
# Pre-requisite: you have just run `python -m build` in bouracka_ui/.
# Pre-requisite: pytest is green (25/25).

$ErrorActionPreference = "Stop"

$repoRoot = (Get-Location).Path
$delivery = Join-Path $repoRoot "delivery"
$en = Join-Path $delivery "bouracka-ui-hp-elite-v0.1.0-EN"
$cs = Join-Path $delivery "bouracka-ui-hp-elite-v0.1.0-CS"

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  HP Elite distribution packager — bouracka-ui v0.1.0" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ─── Step 1: validate inputs ───────────────────────────────────────────────
$wheelGlob = Join-Path $repoRoot "bouracka_ui\dist\bouracka_ui-0.1.0-py3-none-any.whl"
if (-not (Test-Path $wheelGlob)) {
    Write-Host "FATAL: wheel not found at $wheelGlob" -ForegroundColor Red
    Write-Host "       Run 'python -m build' in bouracka_ui/ first." -ForegroundColor Red
    exit 1
}
$wheelPath = $wheelGlob
Write-Host "✓ wheel found: $wheelPath" -ForegroundColor Green

$workbookCandidates = Get-ChildItem $repoRoot -Filter "BOURACKA-TESTPLAN-*.xlsx" -ErrorAction SilentlyContinue
if (-not $workbookCandidates) {
    Write-Host "FATAL: no BOURACKA-TESTPLAN-*.xlsx found in repo root $repoRoot" -ForegroundColor Red
    exit 1
}
# Pick the highest-versioned one (lexical sort puts v0.4.2 after v0.4.1)
$workbook = ($workbookCandidates | Sort-Object Name)[-1].FullName
Write-Host "✓ workbook chosen: $(Split-Path -Leaf $workbook)" -ForegroundColor Green

if (-not (Test-Path $en)) { Write-Host "FATAL: $en doesn't exist" -ForegroundColor Red; exit 1 }
if (-not (Test-Path $cs)) { Write-Host "FATAL: $cs doesn't exist" -ForegroundColor Red; exit 1 }
Write-Host "✓ both delivery folders exist" -ForegroundColor Green

# ─── Step 2: copy wheel + workbook into both delivery folders ──────────────
Write-Host ""
Write-Host "[2/5] Copying wheel + workbook into delivery folders..." -ForegroundColor Cyan
Copy-Item $wheelPath $en -Force
Copy-Item $wheelPath $cs -Force
Copy-Item $workbook $en -Force
Copy-Item $workbook $cs -Force
Write-Host "  ✓ done" -ForegroundColor Green

# ─── Step 3: generate SHA256SUMS for each folder ───────────────────────────
function Write-Sha256Sums($folder) {
    $sumsPath = Join-Path $folder "SHA256SUMS.txt"
    $files = Get-ChildItem $folder -File | Where-Object { $_.Name -ne "SHA256SUMS.txt" } | Sort-Object Name
    $sums = $files | ForEach-Object {
        $h = Get-FileHash $_.FullName -Algorithm SHA256
        "{0}  {1}" -f $h.Hash.ToLower(), $_.Name
    }
    $sums | Out-File -FilePath $sumsPath -Encoding ascii
    Write-Host "  ✓ $sumsPath ($($files.Count) entries)" -ForegroundColor Green
}
Write-Host ""
Write-Host "[3/5] Writing SHA256SUMS.txt..." -ForegroundColor Cyan
Write-Sha256Sums $en
Write-Sha256Sums $cs

# ─── Step 4: package each delivery folder into a ZIP ───────────────────────
Write-Host ""
Write-Host "[4/5] Building ZIPs..." -ForegroundColor Cyan
$zipEN = Join-Path $delivery "bouracka-ui-hp-elite-v0.1.0-EN.zip"
$zipCS = Join-Path $delivery "bouracka-ui-hp-elite-v0.1.0-CS.zip"
if (Test-Path $zipEN) { Remove-Item $zipEN -Force }
if (Test-Path $zipCS) { Remove-Item $zipCS -Force }
Compress-Archive -Path "$en\*" -DestinationPath $zipEN -CompressionLevel Optimal
Compress-Archive -Path "$cs\*" -DestinationPath $zipCS -CompressionLevel Optimal
Write-Host "  ✓ $zipEN" -ForegroundColor Green
Write-Host "  ✓ $zipCS" -ForegroundColor Green

# ─── Step 5: report final SHA256 of each ZIP ───────────────────────────────
Write-Host ""
Write-Host "[5/5] Final ZIP SHA256 (for the GitHub Release / email body):" -ForegroundColor Cyan
$hEN = Get-FileHash $zipEN -Algorithm SHA256
$hCS = Get-FileHash $zipCS -Algorithm SHA256
$szEN = (Get-Item $zipEN).Length
$szCS = (Get-Item $zipCS).Length
Write-Host ""
Write-Host "  EN: $($hEN.Hash.ToLower())" -ForegroundColor White
Write-Host "      $zipEN" -ForegroundColor Gray
Write-Host "      $([math]::Round($szEN/1KB,1)) KB" -ForegroundColor Gray
Write-Host ""
Write-Host "  CS: $($hCS.Hash.ToLower())" -ForegroundColor White
Write-Host "      $zipCS" -ForegroundColor Gray
Write-Host "      $([math]::Round($szCS/1KB,1)) KB" -ForegroundColor Gray
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  DONE. Email-ready ZIPs are in $delivery." -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
