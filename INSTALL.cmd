@echo off
REM ────────────────────────────────────────────────────────────────────────────
REM INSTALL.cmd — first-time setup wrapper for HP Elite (SUPNB001)
REM ────────────────────────────────────────────────────────────────────────────
REM Double-click this file (or run from cmd.exe). Launches PowerShell with
REM ExecutionPolicy Bypass for THIS process only — no system-wide change.
REM No need to Unblock-File first — Bypass overrides Zone.Identifier blocks.
REM ────────────────────────────────────────────────────────────────────────────

setlocal
cd /d "%~dp0"
echo.
echo === bouracka-tests v0.4.9 — INSTALL ===
echo Working dir: %CD%
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup-from-zero.ps1"
set EXITCODE=%ERRORLEVEL%
echo.
echo === INSTALL exit code: %EXITCODE% ===
echo.
pause
exit /b %EXITCODE%
