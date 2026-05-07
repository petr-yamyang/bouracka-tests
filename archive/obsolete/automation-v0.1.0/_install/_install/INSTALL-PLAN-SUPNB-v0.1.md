# Install Plan — bouracka-tests on SUPNB-class notebooks — v0.1

> **Audience.** ČKP/SUPIN SecOps + the operator (Petr) + the two
> colleagues who'll run the test suites independently from their own
> Windows notebooks.
>
> **Goal.** Settle exactly what is installed on the operator's primary
> notebook (`SUPNB001`) and the two colleague notebooks (assumed
> identical class, same OU, same baseline image). One pass through this
> doc gives SecOps the bill-of-materials, the network allowlist, the
> privilege footprint, and the verification script — sufficient to
> approve a deployment ticket.
>
> **Decision baked in:** ship **Playwright only** for R1; Cypress kept
> in repo as fallback **but not installed by default** (saves ~400 MB
> per laptop and removes one set of browser binaries from the SecOps
> review). Rationale in §3.

## §1. Target hardware + OS (verified from photos IMG_1061 + IMG_1062)

| Item | Value |
|------|-------|
| Model | HP EliteBook 6 G11 14" Notebook AI PC |
| Device name (primary) | `SUPNB001` |
| Domain FQDN | `SUPNB001.int-ckp.cz` (domain-joined) |
| Processor | Intel Core Ultra 5 225U (1.50 GHz) |
| Architecture | x64 |
| RAM | 16.0 GB (15.4 GB usable; 5600 MT/s) |
| Storage | 477 GB total / **367 GB free** at survey |
| OS | **Windows 11 Enterprise**, version **25H2**, build **26200.8246** |
| OS install date | 02.02.2026 |
| Locale | Czech (CES) |
| Pen / touch | not supported (irrelevant for tests) |
| Pattern | colleague notebooks `SUPNB002` + `SUPNB003` assumed identical class + GPO |

**Implications**:
- 367 GB free → disk is not a constraint; full Playwright install is
  ~1 GB.
- Win 11 Enterprise 25H2 is fully supported by Playwright + Cypress +
  Node.js LTS — no version-pin gymnastics.
- Domain-joined → Group Policy / AppLocker / WDAC may apply. We
  recommend **per-user installs** (AppData) to avoid needing local-admin
  privileges (see §5).
- ČKP corporate proxy likely enforces TLS inspection on egress; the
  allowlist in §6 covers what's needed.

## §2. Bill of materials (the only software installed)

### §2.1 Operator + colleague notebooks (identical install)

| # | Component | Version pin | Purpose | Per-user install? | Source URL |
|---|-----------|-------------|---------|-------------------|------------|
| 1 | **Node.js LTS** | 20.x (≥ 20.18) or 22.x | JavaScript runtime + npm | YES (per-user MSI option) | https://nodejs.org/dist/v20.18.1/node-v20.18.1-x64.msi |
| 2 | **bouracka-tests** repo | v0.1.0 | The test suite itself; npm-managed dependencies | YES (under `%USERPROFILE%\bouracka-tests`) | delivered as `bouracka-tests-v0.1.0.zip` over corporate channel |
| 3 | **Playwright** + **Chromium** browser binary | `@playwright/test ^1.50.0` + Chromium 132+ pinned by Playwright | E2E test runner; bundles its own Chromium (no system-Chrome dependency) | YES (under `%USERPROFILE%\AppData\Local\ms-playwright`) | `npm install` + `npx playwright install chromium` |

That's the entire BoM. **No other binaries; no system services; no
scheduled tasks; no kernel drivers.** Everything else
(scripts, configs, fixtures) is plain text inside `bouracka-tests/`.

### §2.2 Optional, behind a flag (NOT installed by default)

| Flag | Component | Triggered by | Notes |
|------|-----------|--------------|-------|
| `--with-cypress` | Cypress + binary | `npm run install:cypress` | Adds ~400 MB. Only if Gate 1 ranking shifts. |
| `--with-webkit` | Playwright WebKit binary | `npx playwright install webkit` | Adds ~110 MB. Required only when Safari coverage is exercised; defer until R2. |
| `--with-firefox` | Playwright Firefox binary | `npx playwright install firefox` | Adds ~85 MB. Defer until cross-browser pass. |

### §2.3 Disk footprint

```
Node.js (per-user, AppData\Local\nodejs)              ~ 80 MB
bouracka-tests + node_modules (after npm install)     ~ 200 MB
Playwright Chromium binary                            ~ 600 MB
                                                      --------
                                                      ~ 880 MB    (R1 baseline)

(optional)
Cypress + binary                                      ~ 400 MB    →  ~ 1.3 GB
Playwright WebKit                                     ~ 110 MB    →  ~ 1.4 GB
Playwright Firefox                                    ~  85 MB    →  ~ 1.5 GB
```

880 MB on a 367 GB free disk = **0.24 % footprint** — easy SecOps yes.

## §3. Why Playwright-only for R1 (the design call)

| Factor | Playwright | Cypress | TestCafe |
|--------|------------|---------|----------|
| Bundles own browser binary (no system-Chrome contention) | YES | YES | NO (uses installed Chrome) |
| Microsoft-backed → easier ČKP/SUPIN-vendor-risk approval | YES | (Cypress.io commercial) | (DevExpress) |
| WebKit support → covers SUT requirement Safari ≥ 16 | YES | NO | partial |
| Per-user install footprint | ~0.7 GB | ~0.4 GB add-on | ~80 MB but needs system Chrome |
| Trace + video + screenshot OOTB | YES | YES | YES |
| Mobile-viewport projects (the SUT is mobile-only) | first-class | secondary | secondary |
| One CLI command to run everything | `npx playwright test` | `npx cypress run` | `npx testcafe …` |

**Conclusion.** Playwright is the smallest, simplest BoM that covers
the SUT's mobile-only + Safari requirements. **Cypress and TestCafe
stay in the repo as fallbacks** behind opt-in flags; SecOps only needs
to approve the Playwright-only baseline now.

## §4. Network egress allowlist (the SecOps decision document)

For the **install** + **first-run** + **ongoing CI-style runs against
`tst.bouracka.cz`**, these outbound HTTPS hosts must be reachable from
SUPNB notebooks:

### §4.1 Install-time only (one-shot, can be revoked after deployment)

| Host | Purpose | Port |
|------|---------|------|
| `nodejs.org` | Node.js installer download (manual download by SecOps once) | 443 |
| `registry.npmjs.org` | npm package registry (metadata + tarballs) | 443 |
| `cdn.playwright.dev` | Playwright browser-binary CDN (primary) | 443 |
| `playwright.azureedge.net` | Playwright browser-binary CDN (legacy fallback) | 443 |
| `playwright.download.prss.microsoft.com` | Playwright browser-binary CDN (newer Microsoft path) | 443 |
| `objects.githubusercontent.com` | a few npm packages publish releases to GitHub | 443 |
| `github.com` | same | 443 |

### §4.2 Run-time (ongoing — the only durable allowlist need)

| Host | Purpose | Port |
|------|---------|------|
| `tst.bouracka.cz` | Test environment (R1 primary target) | 443 |
| `tst.demo.bouracka.cz` | DEMO test environment | 443 |
| `*.supin.cz` (specifically `ecdn.supin.cz`) | CDN assets the SUT pulls; also where AISPOV may live | 443 |
| `*.ckp.cz` (specifically `www.ckp.cz`) | static doc PDFs the SUT links to | 443 |
| `www.google.com/recaptcha/*` | reCAPTCHA challenge | 443 |
| `www.gstatic.com/recaptcha/*` | reCAPTCHA scripts | 443 |
| `www.google-analytics.com` | GA pixel (optional — can stay blocked if telemetry rejected) | 443 |

### §4.3 Hosts NOT needed (SecOps can leave blocked)

- `npmjs.com` (browse UI; not for installs)
- `chocolatey.org`, `winget-pkgs` (we don't use chocolatey/winget for the
  Node install — see §5 path B)
- All third-party proxy/aggregator npm registries
- `download.cypress.io` (only if Cypress is enabled — defer)

**SecOps deliverable:** the §4.2 list is the "always-on" set the
firewall should permit on these 3 notebooks. §4.1 is one-shot for
install day; can be temp-allowed and revoked after.

## §5. Privilege footprint (no admin rights needed)

The recommended path is **per-user**, no local-admin escalation.

### §5.1 Path A — winget (preferred if available on Win 11 Enterprise)

If `winget` is enabled by GPO on the int-ckp.cz domain:

```powershell
# As the user (NOT admin)
winget install --id OpenJS.NodeJS.LTS --scope user --silent --accept-package-agreements --accept-source-agreements
```

Single line. Installs Node 20 LTS to `%LOCALAPPDATA%\Microsoft\WinGet\Packages\…`
+ creates per-user PATH entry. No admin token requested.

### §5.2 Path B — Manual MSI (if winget is blocked)

SecOps downloads `node-v20.18.1-x64.msi` once from `https://nodejs.org/dist/v20.18.1/`,
verifies the SHA256 (published on the same page), and pushes to the 3
notebooks via SCCM/Intune as a per-user install with parameter:

```cmd
msiexec /i node-v20.18.1-x64.msi /qn ALLUSERS=2 INSTALLDIR="%LOCALAPPDATA%\nodejs"
```

`ALLUSERS=2` = "install per-user; PATH updated for this user only;
no admin needed". Recommended for SUPNB-class fleet.

### §5.3 Path C — Standalone ZIP (if MSI is also blocked)

Node.js publishes a portable ZIP at the same URL family:
`node-v20.18.1-win-x64.zip`. Unzip into `%USERPROFILE%\nodejs\` and
prepend to user PATH. **Zero installer**. SecOps just needs to allow
the user to write into their own AppData (default Windows 11 behaviour).

### §5.4 Playwright + bouracka-tests install

After Node is on PATH (any of the three paths above), the user runs
**once**:

```powershell
cd %USERPROFILE%\bouracka-tests
npm install
npx playwright install chromium
```

These commands write only to `%USERPROFILE%\bouracka-tests\node_modules`
and `%USERPROFILE%\AppData\Local\ms-playwright\`. **Both are
user-writable; no admin escalation.** Total install time ≈ 4 min on a
healthy network.

## §6. AppLocker / WDAC compatibility

If the int-ckp.cz fleet enforces AppLocker rules typical of an HP
EliteBook enterprise image:

- Node.js (`node.exe`) lives under `%LOCALAPPDATA%\…` — usually permitted
  by **default** AppLocker rules for user-writable paths because the
  publisher signature is OpenJS Foundation / OpenJS Org (Code Signing).
  If AppLocker is in **deny-by-default** mode, SecOps adds one rule:
  *Allow signed binaries by OpenJS Foundation, path
  `%LOCALAPPDATA%\nodejs\*`.*
- Playwright browser binaries are signed by Microsoft Corporation —
  same logic; one rule for path
  `%LOCALAPPDATA%\ms-playwright\*` if needed.
- npm-installed packages are JavaScript text — no native binary; no
  AppLocker hit.

## §7. Group-Policy / corporate-proxy gotchas

| Gotcha | Mitigation |
|--------|------------|
| Corporate TLS-inspection proxy injects its own root CA → `npm install` fails with `UNABLE_TO_VERIFY_LEAF_SIGNATURE` | `npm config set cafile "C:\path\to\corp-root-ca.pem"` (per-user) — PEM provided by SecOps. Documented in `scripts/setup-npm-proxy.ps1`. |
| Proxy requires explicit address | `npm config set proxy http://proxy.int-ckp.cz:8080` + `https-proxy` likewise. |
| GPO sets `executionPolicy = AllSigned` | Ship the `.ps1` files signed (low effort) OR run them as `pwsh -ExecutionPolicy Bypass -File run-all.ps1`. Documented in `README-CS.md`. |
| Domain-joined fileshare scanning blocks `node_modules` (very large file count) | Add an exclusion path `%USERPROFILE%\bouracka-tests\node_modules` in Defender / corporate AV. SecOps preset. |

## §8. Per-notebook deployment workflow (replicable across SUPNB001/002/003)

Same script on each laptop. Tester-friendly happy-path:

```
SecOps gives Operator a one-time deployment kit:
  1. node-v20.18.1-x64.msi  (or use winget if path A)
  2. bouracka-tests-v0.1.0.zip   (the suite zip)
  3. setup-npm-proxy.ps1         (if corp-proxy CA is needed)
  4. validate-install.ps1        (sanity check)

Operator (or SecOps automation):
  a. msiexec /i node-…msi /qn ALLUSERS=2 INSTALLDIR="%LOCALAPPDATA%\nodejs"
     ↳ closes + reopens shell so PATH refreshes
  b. Expand-Archive bouracka-tests-v0.1.0.zip -DestinationPath "%USERPROFILE%\"
  c. cd "%USERPROFILE%\bouracka-tests"
  d. (if proxy CA) .\scripts\setup-npm-proxy.ps1
  e. npm install
  f. npx playwright install chromium
  g. .\scripts\validate-install.ps1
       → outputs JSON summary of what's installed + status

If validate-install.ps1 status == "OK":
  ↳ run a smoke scenario:
     .\scripts\run-playwright.ps1 -Env tst -Project tst-mobile-375
  ↳ check the playwright-report\ folder; if green, deployment is good.
```

Replicate identically on `SUPNB002` + `SUPNB003`. Same kit; same
sequence; same expected output. SecOps signs off once for the kit,
not three times.

## §9. Validation script (PowerShell — included in the kit)

```powershell
# scripts/validate-install.ps1
$result = [ordered]@{
  hostname    = $env:COMPUTERNAME
  user        = $env:USERNAME
  os_version  = (Get-CimInstance Win32_OperatingSystem).Version
  node        = (node --version 2>$null)
  npm         = (npm --version 2>$null)
  playwright  = (npx playwright --version 2>$null)
  pw_browsers = (Get-ChildItem "$env:LOCALAPPDATA\ms-playwright" -Directory `
                  -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name)
  reachable_tst        = (Test-NetConnection tst.bouracka.cz -Port 443 -InformationLevel Quiet)
  reachable_tst_demo   = (Test-NetConnection tst.demo.bouracka.cz -Port 443 -InformationLevel Quiet)
  reachable_npmjs      = (Test-NetConnection registry.npmjs.org -Port 443 -InformationLevel Quiet)
  reachable_pw_cdn     = (Test-NetConnection cdn.playwright.dev -Port 443 -InformationLevel Quiet)
}
$result | ConvertTo-Json -Depth 4
$bad = @($result.GetEnumerator() | Where-Object {
   ($_.Key -like 'reachable_*' -and $_.Value -ne $true) -or
   ($_.Key -in @('node','npm','playwright') -and -not $_.Value)
})
if ($bad.Count -gt 0) {
  Write-Host "[FAIL] $($bad.Count) checks failed" -ForegroundColor Red
  exit 1
} else {
  Write-Host "[OK] all checks pass" -ForegroundColor Green
  exit 0
}
```

Output is machine-readable JSON + a green/red final line. SecOps can
collect the JSON across the 3 laptops to confirm consistency.

## §10. Uninstall procedure (clean rollback)

```powershell
# As the user
cd "%USERPROFILE%"
Remove-Item -Recurse -Force bouracka-tests
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\ms-playwright"
# Then either:
#   winget uninstall OpenJS.NodeJS.LTS --scope user
# or:
#   msiexec /x {Node-MSI-product-code} /qn
```

Total cleanup: ~880 MB freed; **no registry detritus**, no leftover
services. Can be run by the user.

## §11. SecOps approval checklist

Tick once across all 3 notebooks:

- [ ] BoM reviewed (§2): only Node LTS + Playwright + the suite.
- [ ] Network allowlist updated per §4.2 (run-time set on the
      firewall) and §4.1 temporarily for install day.
- [ ] AppLocker rule for `%LOCALAPPDATA%\nodejs\*` and
      `%LOCALAPPDATA%\ms-playwright\*` — needed only if AppLocker is
      deny-by-default.
- [ ] Defender exclusion: `%USERPROFILE%\bouracka-tests\node_modules`.
- [ ] Corp-proxy CA PEM provided to operator (if TLS-inspection on).
- [ ] Validation script (§9) returned `[OK]` on all 3 laptops.

After all six are checked, the suite is ready for the first SUPIN
tester run.

## §12. Future iterations + what changes

| Trigger | Change |
|---------|--------|
| Need to test Safari ≥ 16 | `npx playwright install webkit` (+110 MB, no extra SecOps allowlist; uses same CDN) |
| Need cross-browser parity | Add Firefox: `npx playwright install firefox` (+85 MB) |
| Cypress comparison work | `npm run install:cypress` flag — only then add `download.cypress.io` to §4.1 |
| MI-M-T DOCK-EXCEL adapter ships (v0.3) | No SUPNB change; the adapter runs on dev side |

## §13. Status

| Item | Value |
|------|-------|
| Document | `_install/INSTALL-PLAN-SUPNB-v0.1.md` |
| Target laptops | SUPNB001 (operator) + SUPNB002 + SUPNB003 (colleagues; assumed identical class) |
| OS baseline | Windows 11 Enterprise 25H2 build 26200.8246 |
| BoM size | 3 components (Node + Playwright + suite) |
| Disk footprint | ~880 MB per laptop (R1 baseline) |
| Admin rights required | NO (per-user installs) |
| Network allowlist | 7 install-time hosts + 7 run-time hosts |
| Validation | `scripts/validate-install.ps1` (JSON output + green/red exit) |
| Status | v0.1 — ready to hand to SecOps |

---

*Authored as CP-SUPIN-02 rev 5 deliverable; lives under
`bouracka-tests/_install/` so it ships with the suite zip.*
