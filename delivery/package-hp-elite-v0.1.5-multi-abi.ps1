# package-hp-elite-v0.1.4-multi-abi.ps1
# ------------------------------------------------------------------------------
# Produces ONE ZIP per language that works on Python 3.10, 3.11, AND 3.12
# (win_amd64). BUG-K-005 prevention: multi-ABI wheelhouse means pip auto-selects
# the matching wheel at install time regardless of the target machine's Python
# version. No more "py310 mismatch" silent failures.
#
# Supersedes:
#   - package-hp-elite-v0.1.0.ps1            (per-ABI, requires correct flag)
#   - package-hp-elite-all-abis-v0.1.2.ps1   (3 ABIs, 3 separate ZIPs)
#
# Usage (run from bouracka-tests/ root, no params needed):
#   .\delivery\package-hp-elite-v0.1.4-multi-abi.ps1
#
# What it does:
#   1. Validates the freshly-built wheel exists at bouracka_ui/dist/.
#   2. Validates BOURACKA-TESTPLAN-*.xlsx exists in repo root (sanity only;
#      workbook is NOT included in ZIP per BUG-K-003 governance).
#   3. Builds ONE wheelhouse/ folder containing wheels for cp310 + cp311 + cp312.
#   4. Sanity-checks each critical C-extension dep has wheels for ALL 3 ABIs.
#   5. Writes wheelhouse/README-MULTI-ABI.txt documenting supported ABIs.
#   6. Copies wheel + wheelhouse into both delivery/bouracka-ui-hp-elite-v0.1.0-{EN,CS}/.
#   7. Generates SHA256SUMS.txt for each delivery folder.
#   8. Produces:
#        delivery/bouracka-ui-hp-elite-v0.1.4-EN-multi-abi.zip
#        delivery/bouracka-ui-hp-elite-v0.1.4-CS-multi-abi.zip
#   9. Prints final SHA256 + size of each ZIP.
#
# ZIP size: ~16-18 MB (was ~6 MB for single-ABI). The extra 10-12 MB is the
# cost of bundling httptools/watchfiles/websockets/pydantic_core/pyyaml for
# all three Python versions. Worth it: zero ABI-mismatch tickets.
#
# Pre-requisite: you have just run 'python -m build' in bouracka_ui/.
# Pre-requisite: pytest is green (28/28 on v0.1.4 or 33/33 on v0.1.5).
# Pre-requisite: a Python environment with pip is on PATH (any version 3.10+).

$ErrorActionPreference = "Stop"

$repoRoot = (Get-Location).Path
$delivery = Join-Path $repoRoot "delivery"
$en = Join-Path $delivery "bouracka-ui-hp-elite-v0.1.0-EN"
$cs = Join-Path $delivery "bouracka-ui-hp-elite-v0.1.0-CS"

# Distribution version + supported Python ABIs
$distVersion  = "v0.1.5"
$wheelVersion = "0.1.5"
$supportedAbis = @("310", "311", "312")

Write-Host ""
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host "  HP Elite distribution packager - bouracka-ui $distVersion" -ForegroundColor Cyan
Write-Host "  MULTI-ABI build (cp310 + cp311 + cp312) -- Fix C, BUG-K-005" -ForegroundColor Cyan
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host ""

# --- Step 1: validate inputs ----------------------------------------------
$wheelPath = Join-Path $repoRoot "bouracka_ui\dist\bouracka_ui-$wheelVersion-py3-none-any.whl"
if (-not (Test-Path $wheelPath)) {
    Write-Host "FATAL: wheel not found at $wheelPath" -ForegroundColor Red
    Write-Host "       Run 'python -m build' in bouracka_ui/ first." -ForegroundColor Red
    Write-Host "       (Check pyproject.toml + __init__.py both say version $wheelVersion.)" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] wheel found: $wheelPath" -ForegroundColor Green

$workbookCandidates = Get-ChildItem $repoRoot -Filter "BOURACKA-TESTPLAN-*.xlsx" -ErrorAction SilentlyContinue
if (-not $workbookCandidates) {
    Write-Host "WARN: no BOURACKA-TESTPLAN-*.xlsx in repo root (governance: workbook not bundled anyway)" -ForegroundColor Yellow
}
else {
    $workbook = ($workbookCandidates | Sort-Object Name)[-1].FullName
    Write-Host "[OK] workbook sighted (not bundled): $(Split-Path -Leaf $workbook)" -ForegroundColor Green
}

if (-not (Test-Path $en)) { Write-Host "FATAL: $en does not exist" -ForegroundColor Red; exit 1 }
if (-not (Test-Path $cs)) { Write-Host "FATAL: $cs does not exist" -ForegroundColor Red; exit 1 }
Write-Host "[OK] both delivery folders exist" -ForegroundColor Green

# --- Step 1.5: BUG-K-006 prevention — clean staging of stale artefacts ----
# Old EN/CS staging folders accumulate workbooks + old-wheel versions from
# earlier builds. Compress-Archive grabs everything, so we must clean first.
Write-Host ""
Write-Host "[1.5/8] Cleaning staging folders of stale artefacts (BUG-K-006 prevention)..." -ForegroundColor Cyan
foreach ($folder in @($en, $cs)) {
    # Remove any workbook (NEVER ship workbook in ZIP per BUG-K-003 governance)
    $staleWorkbooks = Get-ChildItem $folder -Filter "BOURACKA-TESTPLAN-*.xlsx" -ErrorAction SilentlyContinue
    foreach ($w in $staleWorkbooks) {
        Write-Host "  [-] removing stale workbook from staging: $($w.Name)" -ForegroundColor Yellow
        Remove-Item $w.FullName -Force
    }
    # Remove any wheel that isn't the current $wheelVersion
    $staleWheels = Get-ChildItem $folder -Filter "bouracka_ui-*-py3-none-any.whl" -ErrorAction SilentlyContinue |
                   Where-Object { $_.Name -ne "bouracka_ui-$wheelVersion-py3-none-any.whl" }
    foreach ($whl in $staleWheels) {
        Write-Host "  [-] removing stale wheel from staging: $($whl.Name)" -ForegroundColor Yellow
        Remove-Item $whl.FullName -Force
    }
    # Remove any prior SHA256SUMS.txt (will be regenerated fresh)
    $oldSums = Join-Path $folder "SHA256SUMS.txt"
    if (Test-Path $oldSums) { Remove-Item $oldSums -Force }
}
Write-Host "[OK] staging folders cleaned" -ForegroundColor Green

# --- Step 2: build the MULTI-ABI wheelhouse -------------------------------
Write-Host ""
Write-Host "[2/8] Building multi-ABI wheelhouse (cp$($supportedAbis -join ' + cp'))..." -ForegroundColor Cyan

$wheelhouseStage = Join-Path $delivery "_wheelhouse-stage-multi-abi"
if (Test-Path $wheelhouseStage) { Remove-Item $wheelhouseStage -Recurse -Force }
New-Item -ItemType Directory -Path $wheelhouseStage | Out-Null

foreach ($abi in $supportedAbis) {
    Write-Host ""
    Write-Host "  --- cp$abi pass ---" -ForegroundColor White
    $pipArgs = @(
        "download",
        "-d", $wheelhouseStage,
        "--platform", "win_amd64",
        "--python-version", $abi,
        "--only-binary=:all:",
        $wheelPath,
        "uvicorn[standard]>=0.27",
        "pytest>=8.0",
        "pytest-json-report>=1.5"
    )
    & pip @pipArgs
    if ($LASTEXITCODE -ne 0) {
        Write-Host "FATAL: pip download failed for cp$abi (exit $LASTEXITCODE)" -ForegroundColor Red
        Write-Host "       Most likely: no internet access on this machine." -ForegroundColor Red
        Write-Host "       Wheelhouse build needs PyPI reach on the BUILDING machine." -ForegroundColor Red
        Write-Host "       Less likely: cp$abi not yet supported by one of our deps." -ForegroundColor Red
        exit 1
    }
    Write-Host "  [OK] cp$abi pass complete" -ForegroundColor Green
}

$wheelCount = (Get-ChildItem $wheelhouseStage -Filter *.whl).Count
$wheelhouseSize = [math]::Round((Get-ChildItem $wheelhouseStage -Filter *.whl | Measure-Object Length -Sum).Sum / 1MB, 1)
Write-Host ""
Write-Host "[OK] multi-ABI wheelhouse built: $wheelCount wheels, $wheelhouseSize MB" -ForegroundColor Green

# --- Step 3: sanity-check critical C-extension deps for ALL 3 ABIs --------
Write-Host ""
Write-Host "[3/8] Verifying critical C-extension wheels present for all ABIs..." -ForegroundColor Cyan

$criticalDeps = @("httptools", "watchfiles", "websockets", "pyyaml", "pydantic_core")
$missing = @()
foreach ($dep in $criticalDeps) {
    foreach ($abi in $supportedAbis) {
        $found = Get-ChildItem $wheelhouseStage -Filter "$dep*cp$abi*.whl" -ErrorAction SilentlyContinue
        if (-not $found) {
            $missing += "${dep}@cp${abi}"
        }
        else {
            Write-Host "  [OK] $dep cp$abi : $($found[0].Name)" -ForegroundColor Green
        }
    }
}
if ($missing.Count -gt 0) {
    Write-Host ""
    Write-Host "FATAL: critical wheels missing: $($missing -join ', ')" -ForegroundColor Red
    Write-Host "       Multi-ABI install will fail on the target machine." -ForegroundColor Red
    Write-Host "       Check pip download output above for the cp-ABI that failed." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] all critical wheels present for cp$($supportedAbis -join ' + cp')" -ForegroundColor Green

# --- Step 4: write wheelhouse README documenting multi-ABI ----------------
Write-Host ""
Write-Host "[4/8] Writing wheelhouse README..." -ForegroundColor Cyan

$readmePath = Join-Path $wheelhouseStage "README-MULTI-ABI.txt"
$readmeContent = @"
bouracka-ui $distVersion -- multi-ABI wheelhouse
================================================

This wheelhouse contains Python wheels for the following Python ABIs on
win_amd64. pip's resolver will automatically pick the matching wheel at
install time based on your Python version.

Supported Python versions:
  - 3.10  (cp310, win_amd64)
  - 3.11  (cp311, win_amd64)
  - 3.12  (cp312, win_amd64)

Total wheels in this directory: $wheelCount
Total size: $wheelhouseSize MB

Install (offline, from this wheelhouse):
  pip install --no-index --find-links="<path-to-this-folder>" \
              "<path-to>/bouracka_ui-$wheelVersion-py3-none-any.whl"

If your Python is OUTSIDE 3.10-3.12, pip will fail with:
  "Could not find a version that satisfies the requirement httptools>=..."
  "from versions: none"
This is an ABI mismatch, not a missing wheel. Either:
  (a) install Python 3.10/3.11/3.12 alongside what you have, or
  (b) request a wheelhouse rebuild from Pete with your specific ABI.

Built at: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Build host: $env:COMPUTERNAME
Builder: $env:USERNAME
"@
$readmeContent | Out-File -FilePath $readmePath -Encoding utf8
Write-Host "[OK] $readmePath" -ForegroundColor Green

# --- Step 5: copy wheel + wheelhouse into both delivery folders -----------
Write-Host ""
Write-Host "[5/8] Copying wheel + wheelhouse into delivery folders..." -ForegroundColor Cyan
Copy-Item $wheelPath $en -Force
Copy-Item $wheelPath $cs -Force

# Wheelhouse: drop into wheelhouse/ subfolder of each language delivery
foreach ($folder in @($en, $cs)) {
    $whdest = Join-Path $folder "wheelhouse"
    if (Test-Path $whdest) { Remove-Item $whdest -Recurse -Force }
    Copy-Item $wheelhouseStage $whdest -Recurse -Force
}
Write-Host "[OK] done" -ForegroundColor Green

# --- Step 6: generate SHA256SUMS for each folder --------------------------
Write-Host ""
Write-Host "[6/8] Writing SHA256SUMS.txt..." -ForegroundColor Cyan

foreach ($folder in @($en, $cs)) {
    $sumsPath = Join-Path $folder "SHA256SUMS.txt"
    $topFiles = Get-ChildItem $folder -File | Where-Object { $_.Name -ne "SHA256SUMS.txt" }
    $whFiles = Get-ChildItem (Join-Path $folder "wheelhouse") -File -ErrorAction SilentlyContinue
    $allFiles = @() + $topFiles + $whFiles
    $lines = @()
    foreach ($f in ($allFiles | Sort-Object FullName)) {
        $rel = $f.FullName.Substring($folder.Length + 1).Replace("\", "/")
        $h = Get-FileHash $f.FullName -Algorithm SHA256
        $lines += ("{0}  {1}" -f $h.Hash.ToLower(), $rel)
    }
    $lines | Out-File -FilePath $sumsPath -Encoding ascii
    Write-Host "[OK] $sumsPath ($($lines.Count) entries)" -ForegroundColor Green
}

# --- Step 7: package each delivery folder into a ZIP ----------------------
Write-Host ""
Write-Host "[7/8] Building multi-ABI ZIPs..." -ForegroundColor Cyan
$zipEN = Join-Path $delivery "bouracka-ui-hp-elite-$distVersion-EN-multi-abi.zip"
$zipCS = Join-Path $delivery "bouracka-ui-hp-elite-$distVersion-CS-multi-abi.zip"
if (Test-Path $zipEN) { Remove-Item $zipEN -Force }
if (Test-Path $zipCS) { Remove-Item $zipCS -Force }
Compress-Archive -Path "$en\*" -DestinationPath $zipEN -CompressionLevel Optimal
Compress-Archive -Path "$cs\*" -DestinationPath $zipCS -CompressionLevel Optimal
Write-Host "[OK] $zipEN" -ForegroundColor Green
Write-Host "[OK] $zipCS" -ForegroundColor Green

# --- Step 7.5: BUG-K-006 post-flight — verify ZIPs are clean --------------
# Inspect each built ZIP to confirm no stale workbooks + exactly ONE wheel.
Write-Host ""
Write-Host "[7.5/8] Post-flight: verifying ZIPs are BUG-K-003 + BUG-K-006 clean..." -ForegroundColor Cyan
Add-Type -AssemblyName System.IO.Compression.FileSystem
$contamination = $false
foreach ($zipPath in @($zipEN, $zipCS)) {
    $zipName = Split-Path -Leaf $zipPath
    $z = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
    try {
        $workbookEntries = $z.Entries | Where-Object { $_.FullName -match "BOURACKA-TESTPLAN-.+\.xlsx$" }
        $wheelEntries = $z.Entries | Where-Object { $_.FullName -match "^bouracka_ui-[^/\\]+-py3-none-any\.whl$" -and $_.FullName -notmatch "wheelhouse" }
        if ($workbookEntries) {
            Write-Host "  [FATAL] $zipName contains workbook(s):" -ForegroundColor Red
            $workbookEntries | ForEach-Object { Write-Host "    - $($_.FullName)" -ForegroundColor Red }
            $contamination = $true
        }
        if ($wheelEntries.Count -ne 1) {
            Write-Host "  [FATAL] $zipName contains $($wheelEntries.Count) top-level wheels (expected 1):" -ForegroundColor Red
            $wheelEntries | ForEach-Object { Write-Host "    - $($_.FullName)" -ForegroundColor Red }
            $contamination = $true
        } else {
            $w = $wheelEntries[0].FullName
            if ($w -ne "bouracka_ui-$wheelVersion-py3-none-any.whl") {
                Write-Host "  [FATAL] $zipName top-level wheel is $w (expected bouracka_ui-$wheelVersion-py3-none-any.whl)" -ForegroundColor Red
                $contamination = $true
            } else {
                Write-Host "  [OK] $zipName : 0 workbooks, 1 wheel ($w)" -ForegroundColor Green
            }
        }
    } finally {
        $z.Dispose()
    }
}
if ($contamination) {
    Write-Host ""
    Write-Host "FATAL: contamination detected in built ZIP(s). Halting before drop staging." -ForegroundColor Red
    Write-Host "       Inspect $en and $cs staging folders, clean manually, re-run packager." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] both ZIPs pass BUG-K-003 + BUG-K-006 hygiene gate" -ForegroundColor Green

# --- Step 8: report final SHA256 + size of each ZIP -----------------------
Write-Host ""
Write-Host "[8/8] Final ZIP SHA256 (for email body / GitHub Release / MANIFEST):" -ForegroundColor Cyan
$hEN = Get-FileHash $zipEN -Algorithm SHA256
$hCS = Get-FileHash $zipCS -Algorithm SHA256
$szEN = (Get-Item $zipEN).Length
$szCS = (Get-Item $zipCS).Length
Write-Host ""
Write-Host "  EN (multi-ABI): $($hEN.Hash.ToLower())" -ForegroundColor White
Write-Host "      $zipEN" -ForegroundColor Gray
Write-Host "      $([math]::Round($szEN/1MB,2)) MB" -ForegroundColor Gray
Write-Host ""
Write-Host "  CS (multi-ABI): $($hCS.Hash.ToLower())" -ForegroundColor White
Write-Host "      $zipCS" -ForegroundColor Gray
Write-Host "      $([math]::Round($szCS/1MB,2)) MB" -ForegroundColor Gray
Write-Host ""
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host "  DONE. Multi-ABI air-gap-ready ZIPs are in $delivery." -ForegroundColor Cyan
Write-Host "        These ZIPs work on Python 3.10/3.11/3.12 -- no -PythonVersion flag needed." -ForegroundColor Cyan
Write-Host "        Next: re-stage drop folders with these new ZIPs (see re-stage runbook)." -ForegroundColor Cyan
Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host ""
