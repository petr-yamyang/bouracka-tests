@echo off
REM ────────────────────────────────────────────────────────────────────────────
REM RUN-TESTS.cmd — execute the Playwright test suite + package results
REM ────────────────────────────────────────────────────────────────────────────
REM Run AFTER INSTALL.cmd has succeeded once.
REM Double-click or invoke from cmd. ExecutionPolicy Bypass for this process.
REM Output:
REM   - playwright-report\index.html (HTML)
REM   - test-results\<run>\*.json   (per-test artefacts)
REM   - bouracka-results-YYYY-MM-DD-<surname>.zip  (mail back to Pete)
REM ────────────────────────────────────────────────────────────────────────────

setlocal
cd /d "%~dp0"
echo.
echo === bouracka-tests v0.4.9 — RUN-TESTS ===
echo Working dir: %CD%
echo Target:      %BOURACKA_BASE%
if "%BOURACKA_BASE%"=="" echo (defaulting to https://demo.bouracka.cz)
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\run-all-and-package.ps1" %*
set EXITCODE=%ERRORLEVEL%
echo.
echo === RUN-TESTS exit code: %EXITCODE% ===
echo.
pause
exit /b %EXITCODE%
