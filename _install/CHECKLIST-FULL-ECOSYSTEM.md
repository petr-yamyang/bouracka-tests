# Checklist — Full-Ecosystem Install (printable, one-page)

> Companion to `_install/INSTALL-PLAN-FULL-ECOSYSTEM-v0.1.md`. Use as
> a one-page tick-sheet during install or SecOps approval review. Each
> tick is binary; no partial credit.

---

## Per-laptop fact-sheet (fill in)

```
Notebook hostname:       ____________________________
Domain FQDN:             ____________________________
OS build (incl. 26200.x): ____________________________
Free disk (GB at start): ____________________________
Profile target (A/B/C):  ____________________________
Operator running install: ____________________________
SecOps approver:         ____________________________
Date:                    ____________________________
```

---

## Phase 1 — SecOps prerequisites (one-time per fleet)

- [ ] **Network allowlist applied** — install-time set
      (registry.npmjs.org, cdn.playwright.dev, playwright.azureedge.net,
       playwright.download.prss.microsoft.com, github.com,
       objects.githubusercontent.com, nodejs.org;
       + Profile B: download.cypress.io;
       + Profile C: adoptium.net, repo1.maven.org, dl.eviware.com)
- [ ] **Network allowlist applied** — run-time set
      (tst.bouracka.cz, tst.demo.bouracka.cz, *.supin.cz, *.ckp.cz,
       www.google.com/recaptcha/*, www.gstatic.com/recaptcha/*)
- [ ] **Loopback** — Profile B/C only — confirm 127.0.0.1 ports 1025,
      1080, 8025, 8080 not blocked by Defender Firewall outbound rules
- [ ] **AppLocker rules** added if deny-by-default
      (`%LOCALAPPDATA%\nodejs\*`, `%LOCALAPPDATA%\ms-playwright\*`;
       + Profile B/C: `%USERPROFILE%\tools\*`)
- [ ] **Defender exclusions** added
      (`%USERPROFILE%\bouracka-tests\node_modules`,
       `%USERPROFILE%\bouracka-tests\runs\*`)
- [ ] **Corp-proxy CA bundle** delivered to operator (PEM file, path
      noted in fact-sheet)

## Phase 2 — Operator install (per laptop)

### 2A — Profile A baseline (every laptop)

- [ ] Node 20 LTS installed via chosen path (winget / MSI / portable ZIP)
- [ ] `node --version` → ≥ 20.18
- [ ] `npm --version` → ≥ 10
- [ ] `bouracka-tests-v0.1.0.zip` extracted to `%USERPROFILE%\bouracka-tests\`
- [ ] (if proxy CA needed) `.\scripts\setup-npm-proxy.ps1` run with
      ProxyUrl + CaFile arguments
- [ ] `npm install` completes without error
- [ ] `npx playwright install chromium` completes without error
- [ ] `.\scripts\validate-install.ps1 -Profile A` returns `[OK]`

### 2B — Profile B add-on (SUPNB002, SUPNB003, optional on <test-runner-host>)

- [ ] `npm run install:cypress` completes
- [ ] `npx cypress install` completes (binary downloaded)
- [ ] `npm install --no-save testcafe@^3.7.0` completes
- [ ] `npm install --no-save newman@^6.2.0` completes
- [ ] `npm install --no-save @mockoon/cli@^9` completes
- [ ] **k6** downloaded + extracted to `%USERPROFILE%\tools\k6\` →
      `k6.exe version` returns ≥ 0.55
- [ ] **Mailpit** downloaded + extracted to `%USERPROFILE%\tools\mailpit\`
      → `mailpit version` returns ≥ 1.21
- [ ] PATH updated to include both `%USERPROFILE%\tools\k6\` and
      `%USERPROFILE%\tools\mailpit\`
- [ ] `.\scripts\validate-install.ps1 -Profile B` returns `[OK]`

### 2C — Profile C add-on (<test-runner-host> only by default)

- [ ] **Eclipse Temurin JRE 21** extracted to `%USERPROFILE%\tools\jre21\`
- [ ] `java -version` returns 21.x; signature verified Eclipse Foundation
- [ ] **SoapUI Open Source 5.7.x** extracted to `%USERPROFILE%\tools\soapui\`
- [ ] `soapui.bat --help` runs without error (uses local JRE)
- [ ] **MockServer 5.15.x** jar at `%USERPROFILE%\tools\mockserver\mockserver.jar`
- [ ] `java -jar mockserver.jar -serverPort 1080 -logLevel WARN` starts
      and binds 127.0.0.1:1080 only (not 0.0.0.0)
- [ ] (optional) Postman desktop installed per-user via MSI
- [ ] `.\scripts\validate-install.ps1 -Profile C` returns `[OK]`

## Phase 3 — End-to-end pipeline smoke (operator only, after install)

- [ ] OOB fixtures bundle delivered → extracted to
      `fixtures\secrets\`
- [ ] `.\scripts\run-contracts.ps1 -Env tst` exits 0 (Layer 1)
- [ ] `.\scripts\seed-validate.ps1 -Env tst` produces
      `fixtures\validated\tst\*.json` files (Layer 2)
- [ ] `.\scripts\run-mocked.ps1 -Env tst` exits 0 (Layer 3)
- [ ] `.\scripts\run-e2e.ps1 -Env tst` exits 0 (Layer 4 — TC-CP-001..020)
- [ ] `.\scripts\run-perf-smoke.ps1 -Env tst` exits 0 (Layer 5)
- [ ] `.\scripts\package-results.ps1 -Tester "petr"` produces
      `bouracka-results-YYYY-MM-DD-petr.zip` with SHA256

## Phase 4 — SecOps sign-off

- [ ] All Phase 1 ticks present.
- [ ] Phase 2A ticks present on all 3 laptops.
- [ ] Phase 2B ticks present on SUPNB002, SUPNB003, and (if elevated)
      <test-runner-host>.
- [ ] Phase 2C ticks present on <test-runner-host>.
- [ ] Phase 3 ticks present (smoke pipeline ran clean).
- [ ] Validation JSONs from all 3 laptops collected; per-profile
      diff is empty.
- [ ] **Signed off by SecOps:** ____________________ (date) __________

---

## Fail / partial / NA notes

```
(record any partial-credit items, environmental quirks, or NA-with-reason here)
```
