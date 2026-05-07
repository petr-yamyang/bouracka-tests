# How-To — Full Ecosystem in One Page

> Read once, follow once. Every command runs as the regular user; no
> admin rights anywhere.

## A. The 30-second mental model

```
<test-runner-host> (operator)        →  Profile C  (full lab)
SUPNB002, SUPNB003 (peers) →  Profile B  (everything except SoapUI GUI + JRE)

Same scripts everywhere. Each script auto-detects what's installed
and skips layers it can't run.
```

## B. The five-layer test pyramid (what runs in what order)

```
1.  Contracts        Newman + node-soap         "Are services responding correctly?"
2.  Data-validate    seed-validate.ps1           "Do our fixtures still match registry data?"
3.  Mocked E2E       Playwright + Mockoon        "Does the SUT handle service-mock variants?"
4.  Real E2E         Playwright + Cypress + …    "Does the SUT work end-to-end against tst.*?"
5.  Performance      k6                          "How fast is it under load?"

Each layer gates the next. Each writes a JSON gate-file.
Stop on first failure (default), or use -ContinueOnFail.
```

## C. Install in 12 lines (Profile C — operator)

```powershell
# (Assumes lean Profile A done per INSTALL-PLAN-SUPNB-v0.1.md.)
cd "$env:USERPROFILE\bouracka-tests"
npm run install:cypress                                          # +Cypress
npm install --no-save testcafe@^3.7.0 newman@^6.2.0 @mockoon/cli@^9  # +TestCafe +Newman +Mockoon
mkdir "$env:USERPROFILE\tools" -Force | Out-Null
Invoke-WebRequest 'https://github.com/grafana/k6/releases/download/v0.55.0/k6-v0.55.0-windows-amd64.zip' -OutFile "$env:USERPROFILE\tools\k6.zip"
Expand-Archive "$env:USERPROFILE\tools\k6.zip" -DestinationPath "$env:USERPROFILE\tools\"
Invoke-WebRequest 'https://github.com/axllent/mailpit/releases/download/v1.21.0/mailpit-windows-amd64.zip' -OutFile "$env:USERPROFILE\tools\mailpit.zip"
Expand-Archive "$env:USERPROFILE\tools\mailpit.zip" -DestinationPath "$env:USERPROFILE\tools\mailpit\"
# (Profile C extras — JRE + SoapUI + MockServer per HOW-TO-INSTALL-SOAP.md)
$env:PATH = "$env:USERPROFILE\tools\k6;$env:USERPROFILE\tools\mailpit;$env:PATH"
.\scripts\validate-install.ps1 -Profile C   # expect [OK] Profile C
```

## D. Run the full pipeline (one command)

```powershell
.\scripts\run-pipeline.ps1 -Env tst -Profile C
# Stops at first layer failure. Use -ContinueOnFail to push through.
# Each layer's JSON gate-file lands in runs/<date>/gate-<N>.json.
```

Or per-layer (interactive debugging):

```powershell
.\scripts\run-contracts.ps1   -Env tst         # ~ 1–2 min
.\scripts\seed-validate.ps1   -Env tst         # ~ 30–60 s
.\scripts\run-mocked.ps1      -Env tst         # ~ 3–5 min
.\scripts\run-e2e.ps1         -Env tst         # ~ 10–15 min
.\scripts\run-perf-smoke.ps1  -Env tst         # ~ 3 min
```

## E. Package + send results

```powershell
.\scripts\package-results.ps1 -Tester "petr"
# → bouracka-results-YYYY-MM-DD-petr.zip + SHA256SUMS-…txt
```

## F. Common run combinations

```powershell
# E2E only (skip contracts/perf — fast iteration during dev work)
.\scripts\run-e2e.ps1 -Env tst -SkipFixtureGate

# Contract layer only (when service-side regression suspected)
.\scripts\run-contracts.ps1 -Env tst -OnlyIntegration INT-004-aispov

# Perf-only ramp (after E2E confirms green)
.\scripts\run-perf.ps1 -Env tst -Scenario load -MaxVUs 10 -Duration 10m

# Mock-only run (when tst.* is unreachable but you want to validate the SUT against synthetic data)
.\scripts\run-mocked.ps1 -Env tst -OnlyIntegration INT-004-aispov,INT-002-sms-gateway
```

## G. Common diagnostic scenarios

| Symptom | Probable cause | First thing to try |
|---------|----------------|--------------------|
| `npm install` hangs / fails with cert error | corp proxy TLS-inspection | `.\scripts\setup-npm-proxy.ps1 -ProxyUrl "..." -CaFile "..."` |
| `npx playwright install` 403/timeout | install-time host not allowlisted | check `cdn.playwright.dev` and `playwright.download.prss.microsoft.com` reachability |
| Layer 1 contracts pass but Layer 4 E2E fails on TC-CP-008 | fixture drift OR SUT regression | re-run Layer 2 `seed-validate`; if fixture invalid → contact tester for new ID; if valid → genuine SUT regression |
| Mockoon won't start on 8025 | port collision | `Get-NetTCPConnection -LocalPort 8025`; kill the squatter or use `-Port 8026` |
| k6 perf p95 spike | back-end slow OR SUPNB CPU saturated | re-run with `--summary-trend-stats="min,max,avg,p(95),p(99)"`; check Task Manager during run |
| SoapUI launches with empty workspace | first-run wizard | open workspace `%USERPROFILE%\bouracka-tests\contracts\soapui-workspace.xml` |
| Validation script shows `pw_browsers: []` | playwright install didn't run or wrote elsewhere | re-run `npx playwright install chromium`; verify `%LOCALAPPDATA%\ms-playwright` populated |

## H. Tearing it all down

```powershell
# Per-profile reverse:
Remove-Item -Recurse -Force "$env:USERPROFILE\bouracka-tests"
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\ms-playwright"
Remove-Item -Recurse -Force "$env:USERPROFILE\tools"
# Then either: winget uninstall OpenJS.NodeJS.LTS --scope user
#           or: msiexec /x {Node-LTS-MSI-product-code} /qn
```

Total disk freed: 2.6 GB (Profile C) / 1.7 GB (B) / 0.9 GB (A).
No registry detritus. No leftover services.

---

*one page · printable · pin it next to the keyboard*
