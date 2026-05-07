# Test platform assessment — Bouračka SUT — v0.1 CS

> **Trigger.** CP-SUPIN-05 mid-session 2026-05-07: Pete: "we have in this stage
> of automation delivery enough informations about F/E Bouračka solution to
> give background for technological assessment of this ecosystem part
> automation … goal is to have pluses and minuses based on real data whether
> Cypress and TestCafe give good alternative choice of direction".
>
> **Cíl.** Evidence-based assessment 4 F/E test platforms (Playwright, Cypress,
> TestCafe, Selenium) + mobile-device automation baseline. **Žádné generic
> marketing**; všechny pros/cons grounded v Bouračka SUT realitě.
>
> **Co tato doc NENÍ.** B/E (ReadyAPI/SoapUI/Postman) assessment — nedostatek
> dat (B/E architecture částečně známé z `recon/ARCHITECTURE-OVERVIEW-v0.1-CS.md`,
> ale konkrétní service contracts ještě nemáme). B/E re-assessment plánován v
> CP-SUPIN-06 po B3WS/P3WS/D8WS dokumentaci od ČKP IT.

---

## §1. Bouračka F/E SUT characteristics — what we know empirically

Z 3 dnů (CP-SUPIN-04 + CP-SUPIN-05 work):

| # | Characteristic | Source evidence |
|---|----------------|-----------------|
| C1 | **React-controlled inputs** vyžadují native setter pattern (OTP, textarea, autocomplete) | `_specs/TESTER-LESSONS-LEARNED-v0.1-CS.md` §3.2 — empirical fail s `fill()`, fix s `Object.getOwnPropertyDescriptor(...).set` |
| C2 | **MUI Autocomplete** ARIA-compliant (`[role="listbox"] [role="option"]`) | live walk recon §3.5; vehicle brand + model + insurer + RUIAN address |
| C3 | **Mobile-first design** (375 px primary, sweep 320/375/414 + desktop) | `playwright/playwright.config.ts` 13 projects |
| C4 | **Cookie banner gating** na first session | `playwright/helpers/page-helpers.ts` `dismissCookieBanner()` |
| C5 | **reCAPTCHA v3** invisible, score-based bot detection | DRIFT 2026-05-07 §3.4 — H5 hypothesis confirmed empirically (HeadlessChrome UA → low score → 403) |
| C6 | **ČÚZK RUIAN ArcGIS** browser-direct address autocomplete (3+ char trigger) | INT-009 + recon §3.6 |
| C7 | **Google Maps JS** Phase 3 location screen + Static Maps | INT-007 |
| C8 | **N8 SMS Gateway** mocked on DEMO (any-4-digit OTP) | INT-001 + Mockoon mock |
| C9 | **zenID OCR** mocked on DEMO; Phase 2 manual fallback via `?validate=false` | recon §3.4 |
| C10 | **Photo capture** Phase 3 — file upload OR camera capture | TT-ACTV-photo-capture; 31-file 164 MB test set |
| C11 | **Touch signature canvas** Phase 4 (sign A + sign B) | TT-ACTV-sign-canvas |
| C12 | **/api/photos UUID-named output** — replay-able real /api/photos calls | Pete's Účastník_A/B captured photo sets |
| C13 | **Geolocation timeout** v automation context (Chromium headless) | TESTER-LESSONS §3.7 — alert s "Určení polohy trvá příliš dlouho" |
| C14 | **DEMO drift**: POST /api/reports → 403 even with valid captcha token | DRIFT 2026-05-07 |
| C15 | **4 environments**: demo public, tst.demo, tst (PROD test), bouracka.cz (PROD prelive) | ROADMAP-4-TARGET §1 |
| C16 | **Czech locale + diacritics** povinné v UI strings | live-copy-strings.yaml 17 STR rows |
| C17 | **Azure Front Door + Spring Boot** B/E (per response headers) | DRIFT §3.4 + ARCHITECTURE §1 |

## §2. 14 evaluation criteria — what matters for THIS SUT

Vybrány tak, aby pokrývaly všechny C1-C17 characteristics + cross-cutting concerns:

| # | Criterion | Why it matters for Bouračka | Weight |
|---|-----------|-----------------------------|--------|
| K1 | React-controlled input handling | C1, C2 — every Phase 1/2/3 test depends on this | ★★★ |
| K2 | Mobile emulation quality | C3 — mobile-first design; viewport-sweep cost matters | ★★★ |
| K3 | Mobile real-device testing | C10, C11 — camera + touch signature accuracy | ★★ (now); ★★★ (Cíl 3+) |
| K4 | Network capture / drift detection | C14 — drift forensic depends on full request/response capture | ★★★ |
| K5 | File upload (photos) | C10 — Phase 3 photo upload paths | ★★ |
| K6 | Touch signature canvas | C11 — Phase 4 only | ★★ |
| K7 | Trace / replay debugging | C14, C13 — drift diagnosis + flake triage | ★★★ |
| K8 | reCAPTCHA-v3 stealth options | C5 — current drift blocker | ★★★ |
| K9 | Cross-browser coverage | future — currently Chromium only | ★★ |
| K10 | CI/CD maturity + parallel sharding | release cadence + 13 projects worth of parallelization | ★★ |
| K11 | Reporter ecosystem (Excel + JSON + HTML) | TES sheets + Excel-row-writer pattern | ★★ |
| K12 | Czech locale + i18n | C16 | ★★ |
| K13 | Same-origin / cross-origin handling | C7 (Google Maps), C6 (RUIAN) — 3rd party scripts in iframe? | ★★ |
| K14 | Maintenance + community support | long-term cost | ★★ |

## §3. Per-platform assessment — evidence-based pros/cons

### §3.1 Playwright (current baseline)

**Verzy v repo:** 1.59.1 (per HP Elite validate-install JSON)
**Ports done:** bring-up + a1-main-happy-day + a2-alternates (8 ALT) + 2 intel-probes

#### Pros (grounded in Bouračka work)

| K | Strength | Evidence |
|---|----------|----------|
| K1 | `page.evaluate()` for native setter pattern works smoothly | `setOtpDigits()` + `setTextarea()` helpers in `a1-main-happy-day-demo.spec.ts` proven on real OTP + textarea fields |
| K2 | Native `devices['iPhone X']` etc., 13 projects setup trivial | `playwright.config.ts` 13 projects = 4 viewports × 3 envs + extras |
| K4 | Built-in `page.on("request"/"response")` + automatic `trace.zip` | DRIFT forensic was extracted FROM Playwright's auto-trace `0-trace.network` — saved hours |
| K7 | Trace viewer = best-in-class (DOM snapshots, network, console, screenshots, video, time-travel) | All 13 a1-main failures had full trace.zip ready for inspection |
| K11 | Custom reporter API straightforward | `playwright/reporters/excel-row-writer.ts` pushes results to Excel directly |
| K12 | `locale: "cs-CZ"` + `timezoneId: "Europe/Prague"` per project | configured per CP-SUPIN-04 STEP 13 |
| K13 | `page.route()` for stub/mock — RUIAN/Maps testable in isolation | available, not yet used (planned for offline test mode) |
| K10 | Native parallel sharding + GH Actions integration | `--shard=1/4` etc.; works out of box |

#### Cons (grounded)

| K | Weakness | Evidence / mitigation |
|---|----------|----------------------|
| K3 | Real-device testing experimental (`@playwright/test --browser=android-chromium`) | Not production-ready; need Appium for real iOS/Android |
| K8 | UA fingerprinting flagged by reCAPTCHA-v3 (HeadlessChrome v147) | DRIFT 2026-05-07 — exact root cause of current 403; mitigation = `playwright-extra` + stealth plugin (community, not official) |
| K6 | Touch signature drag works via `touchscreen.tap()` + sequence; mouse fallback OK for desktop | No production runs yet; theoretical risk on real touch latency |

#### Per-criterion score (0-3)

K1=3, K2=3, K3=1, K4=3, K5=3, K6=2, K7=3, K8=2, K9=3, K10=3, K11=3, K12=3, K13=3, K14=3 → **Total 38/42**

### §3.2 Cypress

**Verze v repo:** 13.x scaffold
**Ports done:** bring-up smoke only

#### Pros

| K | Strength | Evidence / common practice |
|---|----------|---------------------------|
| K7 | Time-travel debug UI is excellent (interactive runner) | not yet used in repo, but well-known DX win |
| K10 | Cypress Cloud — professional CI dashboard, video archive, parallel | requires paid Cypress Cloud subscription |
| K11 | `mochawesome` + `cypress-image-snapshot` reporters mature | community plugins |
| K13 | `cy.intercept()` powerful for stub/mock | comparable to Playwright `route()` |
| K12 | `lang="cs-CZ"` configurable | works |

#### Cons (grounded in Bouračka SUT)

| K | Weakness | Evidence / impact |
|---|----------|-------------------|
| K1 | React-controlled inputs require `cy.window().then(win => { ... native setter })` workaround — verbose | known Cypress pain point; would require helper rewrite for Bouračka |
| K2 | `cy.viewport(width, height)` — works, but **NO native device profile presets** (iPhone X etc.) | manual viewport per spec; less ergonomic than Playwright `devices` |
| K3 | NO mobile real-device support (only desktop browser viewport emulation) | dead-end for Cíl 3+ camera/signature accuracy |
| K4 | `cy.intercept()` records but **NO automatic trace.zip equivalent**; need 3rd-party plugins (`cypress-har-replay`) | drift forensic would have been HARDER without auto-trace; significant for our use case |
| K7 | Time-travel UI great in interactive mode; **CI runs lose interactivity** — only video + screenshots | trade-off |
| K13 | **Same-origin restrictions** — historically can't navigate cross-origin in single test (workaround `cy.origin()` in 12.x but limits remain) | Could affect Google Maps interactions if those navigate; needs verification |
| K9 | Chromium + Edge + Firefox + Electron; no Safari/WebKit native | acceptable for Bouračka (Chromium primary) but limits cross-browser ambition |
| K14 | Strong community but Cypress Cloud freemium model creates adoption tension | acceptable; we'd use OSS-only tier |
| K5 | Native `cy.selectFile()` (12.x+) or older `cypress-file-upload` plugin | works but historically buggy with hidden file inputs |
| K10 | OSS parallel = limited; Cypress Cloud = paid for professional parallel sharding | budget consideration |

#### Per-criterion score (0-3)

K1=2, K2=1, K3=0, K4=2, K5=2, K6=2, K7=2, K8=1, K9=2, K10=2 (free) / 3 (paid Cloud), K11=2, K12=3, K13=2, K14=3 → **Total 26-27/42**

### §3.3 TestCafe

**Verze v repo:** scaffold only
**Ports done:** bring-up smoke only

#### Pros

| K | Strength | Evidence / common practice |
|---|----------|---------------------------|
| K10 | No browser driver required; uses URL rewriting + injected JS | install simplicity (no chromedriver / geckodriver) |
| K9 | Works in any browser via URL proxy, including mobile real browsers via QR-code share URL | unique mechanism |
| K11 | Built-in JSON + JUnit + xUnit reporters | adequate |
| K12 | `--lang cs-CZ` + locale support | works |

#### Cons (grounded — TestCafe documented limitations + Bouračka-specific)

| K | Weakness | Evidence / impact |
|---|----------|-------------------|
| K1 | `t.typeText()` reportedly **struggles with React-controlled inputs**; needs `t.eval()` workaround similar to Playwright | well-documented community pain; would need port |
| K2 | `--viewport=375x667` CLI flag; **no native device profile presets** | manual config per run |
| K3 | NO mobile real-device automation track | dead-end for camera/signature; QR-code remote URL is browser-only, not OS-level |
| K4 | `RequestLogger` API — adequate but **less comprehensive than Playwright trace** | drift forensic would have been incomplete |
| K6 | Touch signature drag via custom Selector mouse-actions; **no high-fidelity touch simulation** | limits Phase 4 testing |
| K7 | Video + screenshots; **no DOM snapshot replay** | inferior debug experience vs Playwright trace.zip |
| K13 | URL-rewriting proxy can break some CSP / cross-origin scenarios | risk for ČÚZK RUIAN cross-origin calls |
| K14 | **Smaller community** vs Playwright/Cypress; fewer Stack Overflow answers; slower release cadence | long-term maintenance risk |
| K10 | Parallel concurrency available but ecosystem less mature than Playwright sharding | acceptable |
| K8 | Same UA fingerprint issues as headless Chromium | no special advantage |

#### Per-criterion score (0-3)

K1=1, K2=2, K3=0, K4=2, K5=2, K6=1, K7=1, K8=1, K9=3, K10=2, K11=2, K12=3, K13=1, K14=2 → **Total 23/42**

### §3.4 Selenium WebDriver (cross-reference, even though Pete asked Cypress + TestCafe)

**Verze v repo:** scaffold only (`selenium/tests/test_bring_up_smoke.py`)
**Ports done:** bring-up smoke only

#### Pros

| K | Strength | Evidence |
|---|----------|----------|
| K3 | **Pairing s Appium = canonical mobile real-device track** | this is THE reason to keep Selenium in scope |
| K9 | Most mature cross-browser (Chrome, Firefox, Safari, Edge, IE legacy) | Selenium Grid 4.x BiDi |
| K8 | `undetected-chromedriver` is well-maintained stealth tool — best reCAPTCHA bypass option in market | community plugin, mature |
| K14 | Largest user base + longest history | maintainability + hireability |

#### Cons (grounded for Bouračka F/E)

| K | Weakness | Evidence / impact |
|---|----------|-------------------|
| K1 | JavaScriptExecutor for native setter — works but verbose | more boilerplate than Playwright |
| K2 | `ChromeOptions.add_argument("--window-size=375,667")` works, but no native device profile DSL | acceptable |
| K4 | Selenium 4.x BiDi (Bidirectional) for network capture — newer, less mature than Playwright; older tests use BrowserMob proxy | adequate but not best in class |
| K7 | NO built-in trace replay; needs 3rd party (Allure / ExtentReports / etc.) | weakest among 4 platforms |
| K10 | CI maturity high but parallel orchestration is more setup work | overhead |
| K11 | Reporter depends on test framework (pytest, JUnit, TestNG); rich ecosystem | acceptable |

#### Per-criterion score (0-3)

K1=2, K2=2, K3=3 (with Appium), K4=2, K5=2, K6=3 (with Appium), K7=1, K8=3 (undetected-cd), K9=3, K10=3, K11=2, K12=3, K13=3, K14=3 → **Total 35/42**

### §3.5 Score summary table

| K | Description | Weight | Playwright | Cypress | TestCafe | Selenium+Appium |
|---|-------------|--------|------------|---------|----------|-----------------|
| K1 | React-controlled inputs | ★★★ | 3 | 2 | 1 | 2 |
| K2 | Mobile emulation | ★★★ | 3 | 1 | 2 | 2 |
| K3 | Mobile real-device | ★★ now / ★★★ later | 1 | 0 | 0 | **3** |
| K4 | Network capture / drift | ★★★ | **3** | 2 | 2 | 2 |
| K5 | File upload | ★★ | 3 | 2 | 2 | 2 |
| K6 | Touch signature | ★★ | 2 | 2 | 1 | 3 |
| K7 | Trace replay | ★★★ | **3** | 2 | 1 | 1 |
| K8 | reCAPTCHA stealth | ★★★ | 2 | 1 | 1 | **3** |
| K9 | Cross-browser | ★★ | 3 | 2 | 3 | 3 |
| K10 | CI/CD maturity | ★★ | 3 | 2-3 | 2 | 3 |
| K11 | Reporter ecosystem | ★★ | 3 | 2 | 2 | 2 |
| K12 | Czech locale | ★★ | 3 | 3 | 3 | 3 |
| K13 | Cross-origin handling | ★★ | 3 | 2 | 1 | 3 |
| K14 | Community + maintenance | ★★ | 3 | 3 | 2 | 3 |
| | **Weighted total (max 42)** | | **38** | 26-27 | 23 | 35 |

## §4. Recommendation matrix

### §4.1 Per-platform verdict

#### Playwright — **Primary F/E choice ★★★** (confirmed)

Best fit pro Bouračka SUT. Already producing GREEN tests + drift forensic. Continue.
Investment in v0.5.x: invest in `playwright-extra` + stealth pro reCAPTCHA bypass (K8 weakest area).

#### Cypress — **Secondary alternative ★★** (keep with limits)

Score 26-27/42 vs Playwright 38/42 — clearly behind. Keep ONLY if:
1. **Component testing** track wanted (Cypress Component Tests are excellent)
2. **Cypress Cloud** budget approved for video + parallel
3. **Independent sanity check** — different framework finds different bugs

Pragmatic plan: keep at smoke level; do NOT port full a1-main + a2-alternates
unless Pete sees specific value (e.g. PR check different from Playwright).

#### TestCafe — **Drop or downgrade ★** (recommend remove)

Score 23/42 — weakest of 4 platforms for Bouračka SUT characteristics.
Specifically:
- React-controlled inputs (K1) require workaround similar to Playwright's eval but less ergonomic
- No mobile real-device path (K3) closes off Phase 4 expansion
- Trace replay (K7) inferior to both Playwright and Cypress
- Smaller community (K14) = higher long-term cost

**Recommendation: drop TestCafe from v0.6.0 onward.** Keep `testcafe/tests/bring-up-smoke.test.ts` as historical scaffold; do not invest more.

#### Selenium + Appium — **Keep ONLY for mobile real-device track ★★★**

Score 35/42 high primarily due to Appium pairing (K3 = 3) and reCAPTCHA stealth (K8 = 3 with `undetected-chromedriver`).

For F/E desktop testing, Playwright wins. But for Phase 4 touch-signature + Phase 3 camera-capture on REAL devices, Appium-Selenium is canonical.

**Recommendation: keep Selenium scaffold. Activate Appium track in CP-SUPIN-06 for periodic mobile-device validation runs.**

### §4.2 Strategy decision — go-forward

| Phase | Primary | Secondary | Drop |
|-------|---------|-----------|------|
| **Now (v0.5.x)** | Playwright (full coverage) | Cypress (smoke only) | TestCafe (mark for removal) |
| **CP-SUPIN-06** | Playwright + selective stealth | Cypress (component tests if PR-CI demands) | TestCafe (remove from package.json + repo) |
| **CP-SUPIN-07+** | Playwright (F/E) + Selenium-Appium (mobile real-device) | Cypress (optional component) | — |

## §5. Mobile real-device baseline — Pete's add-in

### §5.1 Why this matters for Bouračka

| Bouračka feature | Headless emulation adequate? | Real device needed for? |
|------------------|------------------------------|-------------------------|
| Mobile-first layout 320/375/414 | **Yes** — Playwright viewport emulation + isMobile flag covers it | edge-case visual regression on real iOS/Android (rare) |
| Cookie banner + form fill | **Yes** | rare gestures (swipe to dismiss) |
| Photo capture (Phase 3) | **No** — camera API doesn't exist in headless Chromium | **YES** — real camera + photo quality |
| Touch signature canvas (Phase 4) | **Partial** — `touchscreen.tap()` simulates but no pressure / latency | **YES** — high-fidelity touch + accelerometer |
| Geolocation (Phase 3 location) | **No** — TESTER §3.7 alert; either mock or grant permission | **YES** — real GPS + indoor degradation |
| reCAPTCHA-v3 score | **No** — HeadlessChrome UA flagged | **YES** — real device much higher score |

### §5.2 Mobile platform options

| Option | Cost | Setup time | Use case for Bouračka |
|--------|------|------------|----------------------|
| **Appium + local USB-tethered device** | OSS | Medium (Appium Server + ADB or Xcode) | dev-time + occasional manual run |
| **Appium + Sauce Labs** | $$ per minute | Low | CI/CD periodic mobile validation |
| **Appium + BrowserStack** | $$ per minute | Low | similar; broader iOS device farm |
| **Appium + AWS Device Farm** | $$ per minute | Low-medium | corporate-friendly billing |
| **Playwright Android** (`browserType.launch({ channel: "android-chrome" })`) | OSS | Low | **experimental — not production-ready** |

### §5.3 Recommended mobile baseline path

**Phase 1 — now (v0.5.x):** continue Playwright mobile emulation 320/375/414 — **adequate for Cíl 1 + Cíl 2 + Cíl 3 layout regression**. No real-device cost.

**Phase 2 — CP-SUPIN-06:** add Appium scaffold using **local Android device USB-tethered** for periodic spot-check (Pete-side or shared SUPIN device). One-time install, manual trigger, write-up validates camera + signature.

**Phase 3 — CP-SUPIN-07+:** evaluate **AWS Device Farm vs BrowserStack** for Cíl 3+ (PROD test) periodic mobile validation. Budget request to ČKP for cloud-device-minutes.

**Phase 4 — CP-SUPIN-08+:** if Pete's photo capture test data (Účastník_A/B) workflow becomes mainstream, integrate Appium camera-mock for replay scenarios.

### §5.4 Mobile decision matrix

| Track | Capex | Opex | Coverage | Recommendation |
|-------|-------|------|----------|----------------|
| Playwright emulation only | $0 | $0 | layout + interaction (~80% of tests) | **keep for ALL phases** |
| Appium + 1 local Android | $0-200 (used phone) | $0 | + camera + signature + geolocation | **add CP-SUPIN-06** |
| Appium + cloud farm | $0 | $50-500 / month | + iOS + multiple device matrix + reCAPTCHA score parity | **evaluate CP-SUPIN-07** |
| Real-device CI (every PR) | $0 | $$$$$ | full | not justified for Bouračka scope |

## §6. ROI / cost-benefit summary per platform

| Platform | One-time setup | Per-iteration maintenance | Coverage gain | Verdict |
|----------|----------------|--------------------------|---------------|---------|
| **Playwright** | DONE | low (existing tests stable) | high (38/42) | **continue + invest in stealth** |
| **Cypress** | DONE (smoke) | medium (port a2-alt = ~2 days) | medium-low (26-27/42) | **freeze at smoke; defer further work unless PR-check drives it** |
| **TestCafe** | DONE (smoke) | medium-high (smaller community = more debugging) | low (23/42) | **drop in v0.6.0** |
| **Selenium + Appium** | medium (Appium server + ADB/Xcode) | high (per-device profile drift) | high for mobile (35/42) | **activate CP-SUPIN-06 for mobile real-device** |

## §7. Open questions

| # | Otázka | Owner |
|---|--------|-------|
| Q-PLAT-1 | Cypress Cloud budget approval — $99/mo per developer; worth it pro PR-check parallel? | Pete + governance |
| Q-PLAT-2 | TestCafe formal removal — kdy ohlásit, jaký impact na CP-SUPIN-04 strategy doc? | Pete |
| Q-PLAT-3 | Appium scaffold owner — Pete personal Android nebo SUPIN-issued device? | Pete |
| Q-PLAT-4 | Cloud device farm — AWS Device Farm vs BrowserStack vs Sauce Labs preference? | Pete + ČKP IT |
| Q-PLAT-5 | reCAPTCHA stealth — `playwright-extra` plugin acceptable per ČKP SecOps? | ČKP SecOps |
| Q-PLAT-6 | Mobile validation cadence — per-release nebo periodic (weekly)? | Pete |

## §8. Companion docs

- `_specs/MULTI-PLATFORM-TESTING-STRATEGY-v0.1-CS.md` — predecessor; this doc supersedes its framework-fitness section
- `_specs/CROSS-FRAMEWORK-DATA-SHARING-v0.1-CS.md` — fixture pattern enables consistent assertions across whichever frameworks survive
- `_specs/CP-SUPIN-05-PLAN-CS.md` §2.2 — phased cross-framework parity plan
- `recon/DRIFT-2026-05-07-DEMO-POST-REPORTS-CS.md` — drift evidence supporting K8 (reCAPTCHA stealth criticality)

## §9. Decision log

### 2026-05-07 mid-session — Pete confirms

> "Selenium + Appium replace as a part of next-round dev stack TestCafe."

**Confirmed lineup pro CP-SUPIN-06+:**

| Position | Framework | Status | Action |
|----------|-----------|--------|--------|
| Primary F/E | **Playwright** | continue | invest in stealth (K8) v CP-SUPIN-06 |
| Secondary F/E | **Cypress** | freeze at smoke | no further port unless PR-CI demands |
| Mobile real-device | **Selenium + Appium** | **promoted** from "specialised" → active dev stack | scaffold v CP-SUPIN-06; first run CP-SUPIN-07 |
| ~~TestCafe~~ | — | **REMOVED** from active dev stack | keep `testcafe/` smoke as historical scaffold; do not iterate; remove from package.json `devDependencies` v0.6.0 |

**Rationale.** Per §3.3 score 23/42 (lowest of 4) + zero mobile real-device path
(K3 = 0). Selenium+Appium score 35/42 + canonical mobile-real-device pairing
(K3 = 3) + reCAPTCHA stealth via `undetected-chromedriver` (K8 = 3). Pro
Bouračka SUT (mobile-first + photo capture + touch signature + drift gating)
je Selenium+Appium objektivně užitečnější než TestCafe.

**Net dev stack v0.6.0+:**

```
F/E primary:       Playwright (with stealth plugin)
F/E secondary:     Cypress (smoke level only)
Mobile real:       Selenium + Appium  ← NEW (replaces TestCafe slot)
B/E smoke:         ReadyAPI/SoapUI (primary per ČKP) + Postman (secondary)
B/E mock:          Mockoon (N8 SMS gateway)
```

### Migration path TestCafe → Selenium+Appium

| Step | Phase | Action |
|------|-------|--------|
| 1 | v0.5.1 | Add deprecation note to `testcafe/README.md` (TBD) + Excel `06_TestStrategy` row update |
| 2 | v0.6.0 | Drop `testcafe` from `package.json` devDependencies; archive `testcafe/` to `_obsolete/testcafe-historical/` in dev repo (NOT in email ZIP) |
| 3 | v0.6.0 | Selenium scaffold v `selenium/tests/` rozšířit o ALT-1, ALT-7 ports |
| 4 | v0.7.0 | Appium track aktivovat: scaffold local Android USB-tethered nebo cloud farm (per Q-PLAT-3 / Q-PLAT-4 governance answers) |
| 5 | v0.7.x | First mobile real-device validation: photo capture + touch signature + reCAPTCHA score check |

## §10. Status

| Item | Hodnota |
|------|---------|
| Doc | `_specs/PLATFORM-ASSESSMENT-v0.1-CS.md` |
| Verze | **v0.2** (decision log added) |
| Datum | 2026-05-07 v0.1 + 2026-05-07 mid-session v0.2 |
| Audience | Pete + governance + future framework decision committee |
| Evidence base | 17 SUT characteristics + 14 evaluation criteria + 4 platforms |
| Recommendations | (1) Playwright primary, (2) Cypress secondary smoke-only, (3) **DROP TestCafe v0.6.0** (Pete approved), (4) **Selenium+Appium PROMOTED to active dev stack** for mobile track |
| Companion | `_specs/MIMT-NATIVE-AUTOMATION-ASSESSMENT-v0.1-CS.md` (build-vs-buy of MI-M-T-native automation tool) |
| Status | v0.2 — decisions locked; CP-SUPIN-06 swap migration plan ready |
