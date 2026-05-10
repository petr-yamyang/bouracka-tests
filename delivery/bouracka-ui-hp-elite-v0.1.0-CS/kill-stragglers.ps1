# kill-stragglers.ps1 — cleanup helper for bouracka-ui
# Usage: .\kill-stragglers.ps1
#
# What it does:
#   1. Finds any process listening on TCP port 8424 (bouracka-ui's default).
#   2. Kills it (Stop-Process -Force).
#   3. Removes leading-tilde orphan directories in .venv/Lib/site-packages
#      (pip's half-cleaned-up uninstall markers when previous installs hit
#      Access Denied on locked .pyd files).
#   4. Reports what it did.
#
# Safe to run repeatedly — no-ops gracefully if there's nothing to clean.
# Does NOT require admin rights for any of the above operations.
#
# References:
#   - TROUBLESHOOTING.md §1, §2 — symptoms this script addresses
#   - KB-041 in the parent VibeCodeProjects KB — git/process collision pattern

$ErrorActionPreference = "Stop"
$bouracka_port = 8424

# ─── Step 1: kill any process holding port 8424 ────────────────────────────
Write-Host ""
Write-Host "[kill-stragglers] Step 1/3 — checking TCP port $bouracka_port..." -ForegroundColor Cyan

$conn = Get-NetTCPConnection -LocalPort $bouracka_port -State Listen -ErrorAction SilentlyContinue
if ($conn) {
    $conn | ForEach-Object {
        $procId = $_.OwningProcess
        $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "  Killing $($proc.ProcessName) (PID $procId) holding port $bouracka_port" -ForegroundColor Yellow
            Stop-Process -Id $procId -Force
        }
    }
    Start-Sleep -Seconds 1
    $still = Get-NetTCPConnection -LocalPort $bouracka_port -State Listen -ErrorAction SilentlyContinue
    if ($still) {
        Write-Host "  WARNING: something still listens on $bouracka_port. May need a reboot." -ForegroundColor Red
    } else {
        Write-Host "  Port $bouracka_port is free now." -ForegroundColor Green
    }
} else {
    Write-Host "  Port $bouracka_port is already free." -ForegroundColor Green
}

# ─── Step 2: clean up pip orphan directories ───────────────────────────────
Write-Host ""
Write-Host "[kill-stragglers] Step 2/3 — checking .venv\Lib\site-packages for pip orphans..." -ForegroundColor Cyan

# Look for .venv either in current dir or in the script's directory.
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$candidates = @(
    (Join-Path (Get-Location) ".venv\Lib\site-packages"),
    (Join-Path $scriptDir   ".venv\Lib\site-packages"),
    (Join-Path $scriptDir   "..\bouracka_ui\.venv\Lib\site-packages")
)

$venvSite = $null
foreach ($c in $candidates) {
    if (Test-Path $c) { $venvSite = $c; break }
}

if ($venvSite) {
    Write-Host "  venv site-packages: $venvSite" -ForegroundColor Gray
    $orphans = Get-ChildItem $venvSite -Directory -ErrorAction SilentlyContinue | Where-Object Name -like "~*"
    if ($orphans) {
        $orphans | ForEach-Object {
            Write-Host "  Removing orphan: $($_.Name)" -ForegroundColor Yellow
            try {
                Remove-Item $_.FullName -Recurse -Force -ErrorAction Stop
                Write-Host "    OK" -ForegroundColor Green
            } catch {
                Write-Host "    FAILED — file still locked. Reboot may be needed." -ForegroundColor Red
            }
        }
    } else {
        Write-Host "  No orphan directories found." -ForegroundColor Green
    }
} else {
    Write-Host "  No .venv found in expected locations — skipping orphan cleanup." -ForegroundColor Gray
    Write-Host "    (This is fine if you haven't created a venv yet, or you're in a different folder.)" -ForegroundColor Gray
}

# ─── Step 3: report ────────────────────────────────────────────────────────
Write-Host ""
Write-Host "[kill-stragglers] Step 3/3 — done." -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. If you were trying to reinstall: pip install --force-reinstall bouracka_ui-0.1.0-py3-none-any.whl"
Write-Host "  2. If you were trying to start the server: bouracka-ui"
Write-Host ""
