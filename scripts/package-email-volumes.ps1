<#
.SYNOPSIS
  Split any folder into email-shippable ZIP volumes (≤ 5 MB each).

.DESCRIPTION
  Produces numbered, stand-alone ZIPs that merge cleanly when each is
  extracted to the same parent folder. Zero 7-zip dependency — pure
  PowerShell + Compress-Archive. Each part can be opened with Windows
  Explorer "Extract All...".

  The output preserves the source folder's relative path structure
  inside each ZIP, prefixed by a top-level container folder named
  after -BaseName. So extracting any part creates:

    <DestDir>/<BaseName>/<file's-relative-path>

  Multiple parts extracted to the same DestDir merge naturally — they
  all share the same top-level container.

  Algorithm:
    1. Walk SourceDir → list all files with relative paths + sizes.
    2. Sort largest-first.
    3. Greedy bin-pack into ≤ MaxBytes chunks (default 4.5 MB to leave
       headroom for ZIP headers below the 5 MB email cap).
    4. Per chunk: stage files into a temp folder mirroring the path
       structure, then Compress-Archive to part NN-of-MM.zip.
    5. Write a PART-INDEX.txt listing all parts + SHA256 + file counts
       + extraction order.

  If a single file exceeds MaxBytes the script aborts with a clear
  error (the file would need 7-zip multi-volume splitting; out of
  scope for the email-friendly path).

.PARAMETER SourceDir
  Folder to package (REQUIRED).

.PARAMETER OutDir
  Where to write the parts + index (REQUIRED).

.PARAMETER BaseName
  Top-level container folder name written inside each ZIP. Recipient
  extracts each part into the same DestDir; all parts share this
  parent so extraction merges. Default: source folder name + date.

.PARAMETER MaxBytes
  Max bytes per part (default 4500000 = 4.5 MB).

.EXAMPLE
  .\scripts\package-email-volumes.ps1 `
    -SourceDir 'C:\Users\vitez\Documents\VibeCodeProjects\SUPIN\bouracka-tests' `
    -OutDir 'C:\Users\vitez\Desktop\bouracka-email-parts'

.EXAMPLE
  # Pack a different folder (e.g. analytical photos) for shipping
  .\scripts\package-email-volumes.ps1 `
    -SourceDir 'C:\Users\vitez\Documents\VibeCodeProjects\SUPIN\analyticke vstupy' `
    -OutDir 'C:\Users\vitez\Desktop\analyticke-vstupy-email' `
    -BaseName 'analyticke-vstupy-2026-05-05'
#>
param(
  [Parameter(Mandatory = $true)] [string]$SourceDir,
  [Parameter(Mandatory = $true)] [string]$OutDir,
  [string]$BaseName = "",
  [int]$MaxBytes = 4500000
)
$ErrorActionPreference = 'Continue'

# ── Validate inputs ─────────────────────────────────────────────────────────
$src = (Resolve-Path $SourceDir).Path
if (-not (Test-Path $src -PathType Container)) {
  Write-Host "[FAIL] SourceDir not found or not a directory: $SourceDir" -ForegroundColor Red
  exit 1
}
if (-not $BaseName) {
  $leaf = Split-Path $src -Leaf
  $BaseName = "$leaf-$(Get-Date -Format 'yyyy-MM-dd')"
}
if (-not (Test-Path $OutDir)) {
  New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
}
$OutDir = (Resolve-Path $OutDir).Path

Write-Host "[package-email-volumes] source   = $src" -ForegroundColor Cyan
Write-Host "[package-email-volumes] outdir   = $OutDir" -ForegroundColor Cyan
Write-Host "[package-email-volumes] basename = $BaseName" -ForegroundColor Cyan
Write-Host "[package-email-volumes] max/part = $([math]::Round($MaxBytes/1MB,2)) MB" -ForegroundColor Cyan

# ── Inventory ───────────────────────────────────────────────────────────────
$srcFull = $src.TrimEnd('\') + '\'
$files = Get-ChildItem -Path $src -Recurse -File -Force |
  Where-Object {
    -not ($_.FullName -match '\\node_modules\\') -and
    -not ($_.FullName -match '\\\.git\\')        -and
    -not ($_.FullName -match '\\runs\\')         -and
    -not ($_.Name -like '.~lock*')
  } |
  ForEach-Object {
    $rel = $_.FullName.Substring($srcFull.Length)
    [pscustomobject]@{
      Full = $_.FullName
      Rel  = $rel
      Len  = $_.Length
    }
  }
$totalBytes = ($files | Measure-Object -Property Len -Sum).Sum
$totalCount = $files.Count
Write-Host "[package-email-volumes] inventory: $totalCount files, $([math]::Round($totalBytes/1MB,2)) MB" -ForegroundColor Cyan

# Single-file-too-large check
$tooBig = $files | Where-Object { $_.Len -gt $MaxBytes }
if ($tooBig) {
  Write-Host "[FAIL] These files exceed MaxBytes ($MaxBytes) on their own:" -ForegroundColor Red
  $tooBig | ForEach-Object { Write-Host "       $([math]::Round($_.Len/1MB,2)) MB  $($_.Rel)" -ForegroundColor Red }
  Write-Host "       Use 7-zip multi-volume split for these, or raise MaxBytes (mailbox-permitting)." -ForegroundColor Yellow
  exit 1
}

# ── Bin-pack (largest-first first-fit) ──────────────────────────────────────
$bins = New-Object System.Collections.Generic.List[psobject]
$current = [pscustomobject]@{ Files = @(); Size = 0L }
$sorted = $files | Sort-Object Len -Descending
foreach ($f in $sorted) {
  if (($current.Size + $f.Len) -gt $MaxBytes -and $current.Files.Count -gt 0) {
    $bins.Add($current)
    $current = [pscustomobject]@{ Files = @(); Size = 0L }
  }
  $current.Files += $f
  $current.Size  += $f.Len
}
if ($current.Files.Count -gt 0) { $bins.Add($current) }
$M = $bins.Count
Write-Host "[package-email-volumes] -> $M part(s)" -ForegroundColor Cyan

# ── Per-bin: stage + compress ───────────────────────────────────────────────
# Clean any prior parts so a re-run produces a clean set
Get-ChildItem -Path $OutDir -Filter "$BaseName-part-*-of-*.zip" -ErrorAction SilentlyContinue |
  Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path $OutDir -Filter "$BaseName-PART-INDEX.txt"  -ErrorAction SilentlyContinue |
  Remove-Item -Force -ErrorAction SilentlyContinue

$indexLines = @()
$indexLines += "# bouracka — email-volume manifest"
$indexLines += "# base   : $BaseName"
$indexLines += "# parts  : $M"
$indexLines += "# files  : $totalCount"
$indexLines += "# bytes  : $totalBytes ($([math]::Round($totalBytes/1MB,2)) MB)"
$indexLines += "# packed : $(Get-Date -Format 'yyyy-MM-ddTHH:mm:ss')"
$indexLines += ""
$indexLines += "# How to extract (Windows Explorer or PowerShell):"
$indexLines += "#   1. Save ALL of the *-part-*-of-*.zip files into one folder."
$indexLines += "#   2. EITHER run: .\scripts\extract-email-volumes.ps1 -SourceDir <that folder> -DestDir <target>"
$indexLines += "#   3. OR right-click each ZIP in Explorer → Extract All... → choose the same target."
$indexLines += "#   The parts share a top-level '$BaseName' folder so they merge naturally."
$indexLines += ""
$indexLines += "# Part roster (extract in any order; each is stand-alone):"

for ($i = 0; $i -lt $M; $i++) {
  $bin = $bins[$i]
  $partIdx  = ($i + 1).ToString("00")
  $totalIdx = $M.ToString("00")
  $partName = "$BaseName-part-$partIdx-of-$totalIdx.zip"
  $partPath = Join-Path $OutDir $partName

  # Stage in a temp dir so Compress-Archive sees the right relative paths
  $stage = Join-Path $env:TEMP "email-vol-stage-$([guid]::NewGuid())"
  $stageRoot = Join-Path $stage $BaseName
  New-Item -ItemType Directory -Force -Path $stageRoot | Out-Null

  foreach ($f in $bin.Files) {
    $dst = Join-Path $stageRoot $f.Rel
    $dstParent = Split-Path $dst -Parent
    if (-not (Test-Path $dstParent)) { New-Item -ItemType Directory -Force -Path $dstParent | Out-Null }
    Copy-Item -LiteralPath $f.Full -Destination $dst -Force
  }

  # Compress (fastest mode keeps roughly 1:1 with payload size; for our
  # text-heavy payload Optimal would be smaller but slower — and we have
  # headroom under 5 MB anyway)
  Compress-Archive -Path "$stageRoot" -DestinationPath $partPath -Force -CompressionLevel Fastest
  $partSize = (Get-Item $partPath).Length
  if ($partSize -gt 5MB) {
    Write-Host "[WARN] $partName is $([math]::Round($partSize/1MB,2)) MB — exceeds 5 MB email cap" -ForegroundColor Yellow
    Write-Host "       Lower -MaxBytes and re-run." -ForegroundColor Yellow
  }

  $sha = (Get-FileHash $partPath -Algorithm SHA256).Hash
  $indexLines += "$partIdx/$totalIdx  $([math]::Round($partSize/1KB,1).ToString().PadLeft(8)) KB   sha256=$sha   $partName   ($($bin.Files.Count) files)"

  Write-Host "[OK] $partName  $([math]::Round($partSize/1KB,1)) KB  ($($bin.Files.Count) files)  sha256=$($sha.Substring(0,16))…" -ForegroundColor Green

  Remove-Item -Recurse -Force $stage
}

$indexPath = Join-Path $OutDir "$BaseName-PART-INDEX.txt"
$indexLines | Out-File -FilePath $indexPath -Encoding utf8

Write-Host ""
Write-Host "[OK] manifest: $indexPath" -ForegroundColor Green
Write-Host "[OK] $M part(s) in: $OutDir" -ForegroundColor Green
Write-Host ""
Write-Host "[next] Send all $M part(s) + the PART-INDEX.txt as separate email attachments." -ForegroundColor Cyan
Write-Host "       Recipient: see _install/EMAIL-DELIVERY-GUIDE-CS.md (or run extract-email-volumes.ps1)." -ForegroundColor Cyan
exit 0
