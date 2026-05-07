# Multi-platform automated testing strategy — v0.1 CS

> **Trigger.** CP-SUPIN-04 STEP 32 (2026-05-06): Pete direction —
> "parallel implementation of automated testsuits in different platforms
> relevant to gather and test real problems… ReadyAPI SoapUI, less
> frequented but also important Postman. Selenium must be considered for
> more robust automation. Immediate expansion of B/E tests orchestrated."
>
> **Audience.** SUPIN testovací tým + governance + MI-M-T projekt.
> **Cíl.** Definovat strategy proč paralelně provozujeme **6 testovacích
> platforem** napříč F/E + B/E + cross-layer + mock vrstvou.

---

## §1. Strategický důvod paralelní platformy

V SUPIN ekosystému je řada systémů různého charakteru — F/E heavy
(Bouračka), B/E heavy (X1+ s SOAP/REST), event-driven (potenciálně
budoucí), batch (potenciálně). **Žádná jediná testing platform
neoptimalizuje pro všechny.**

Strategy: **paralelně provozovat 6 platforem**, každou na to, k čemu
je nejvhodnější. Po N iteracích na reálných systémech vznikne
**evidence-based assessment** — která platforma je pro SUPIN ekosystém
long-term winner per layer / per use case.

## §2. 6 platforem + jejich primary use case

```
   ┌──────────────────────────────────────────────────────────────────┐
   │  F/E layer — browser-driven UX testing                           │
   │    Playwright   ★ primary       (modern, MS-backed, intel-rich)  │
   │    Cypress      ↓ secondary     (DX-friendly, good for SPA dev)  │
   │    TestCafe     ↓ secondary     (no-WebDriver, simple setup)     │
   ├──────────────────────────────────────────────────────────────────┤
   │  B/E layer — service contract + behavior testing                 │
   │    ReadyAPI/SoapUI ★ primary    (SOAP+REST, SUPIN první volba)   │
   │    Postman      ↓ secondary     (REST + lightweight scripting)   │
   │    Selenium     ↓ alt           (cross-language, robust mature)  │
   ├──────────────────────────────────────────────────────────────────┤
   │  Cross-layer — full E2E with B/E observation                     │
   │    Selenium WebDriver                                             │
   │    (when need to assert F/E + B/E payloads in single test)       │
   ├──────────────────────────────────────────────────────────────────┤
   │  Mock layer — service virtualization                             │
   │    Mockoon  ★ for SUPIN testing                                  │
   │    (already in use; used to mock N8 SMS Gateway etc.)            │
   └──────────────────────────────────────────────────────────────────┘
```

## §3. Per-platform fitness assessment

### §3.1 Playwright (primary F/E)

| Aspekt | Hodnocení |
|--------|-----------|
| **F/E test capability** | ★★★★★ — best-in-class for modern SPAs (React, Vite, Vue) |
| **B/E test capability** | ★★★ — `request` fixture handles REST, but not first-class for SOAP |
| **DX (developer experience)** | ★★★★ — TypeScript-first, codegen, trace viewer |
| **Maturity** | ★★★★ — Microsoft-backed, active 2020+ |
| **SUPIN ekosystém fit** | F/E heavy systems (Bouračka, future X-front) |
| **Adoption v SUPIN today** | new — tato CP-SUPIN-04 iterace je první nasazení |
| **Recommendation** | ★ primary F/E framework |

### §3.2 Cypress (secondary F/E)

| Aspekt | Hodnocení |
|--------|-----------|
| **F/E test capability** | ★★★★ — excellent for SPA DX, real-time reload |
| **B/E test capability** | ★★ — `cy.request()` exists but not really suitable |
| **DX** | ★★★★★ — interactive runner is best in class |
| **Maturity** | ★★★★ — Cypress.io company, active 2017+ |
| **SUPIN fit** | F/E for active development, less for CI regression |
| **Adoption v SUPIN** | TBD — testing parity with Playwright |
| **Recommendation** | secondary; consider for active dev, not regression |

### §3.3 TestCafe (secondary F/E)

| Aspekt | Hodnocení |
|--------|-----------|
| **F/E test capability** | ★★★ — solid, no WebDriver needed |
| **B/E test capability** | ★ — minimal |
| **DX** | ★★★ — Selector + ClientFunction model is clean |
| **Maturity** | ★★★★ — DevExpress, active 2016+ |
| **SUPIN fit** | F/E quick smokes, less for full E2E |
| **Adoption v SUPIN** | TBD — testing parity |
| **Recommendation** | tertiary; backup option |

### §3.4 ReadyAPI / SoapUI (★ primary B/E)

| Aspekt | Hodnocení |
|--------|-----------|
| **F/E test capability** | × — nehodí se |
| **B/E test capability** | ★★★★★ — ABSOLUTNÍ HVĚZDA pro SOAP/REST |
| **DX** | ★★★ — desktop GUI; XML-based project files; assertion library extensive |
| **Maturity** | ★★★★★ — SmartBear, používané ČR enterprise od 2010s |
| **SUPIN fit** | **B/E systems with SOAP** (X1, vendor SOAP services) — **first choice in SUPIN collective per Pete** |
| **Adoption v SUPIN** | already used — testers familiar |
| **Recommendation** | ★ primary B/E framework. Open-source SoapUI = free; ReadyAPI = paid premium tier |

**Notes pro SUPIN integration:**
- SoapUI/ReadyAPI projects = `.xml` files (version controllable)
- Headless run: `testrunner.sh` (Linux) / `testrunner.bat` (Windows)
- JUnit XML output → easily integrable s našim test_console.py
- ČKP collective expertise = nejmenší ramp-up cost

### §3.5 Postman (secondary B/E)

| Aspekt | Hodnocení |
|--------|-----------|
| **F/E test capability** | × |
| **B/E test capability** | ★★★★ — solid for REST; lightweight for SOAP |
| **DX** | ★★★★ — excellent UI; scripting via JS |
| **Maturity** | ★★★★★ — Postman Inc. since 2014 |
| **SUPIN fit** | REST APIs, OpenAPI-driven systems |
| **Adoption v SUPIN** | "less frequented but also important" per Pete |
| **Recommendation** | secondary B/E — rapid iteration + collections share-able |

### §3.6 Selenium (alt B/E + cross-layer)

| Aspekt | Hodnocení |
|--------|-----------|
| **F/E test capability** | ★★★★ — mature, but more verbose than Playwright |
| **B/E test capability** | ★★★ — via SeleniumGrid + custom stack |
| **DX** | ★★ — verbose API |
| **Maturity** | ★★★★★ — industry default since ~2004; battle-tested |
| **SUPIN fit** | When need cross-language (Java/Python) or robust corp adoption |
| **Adoption v SUPIN** | "Must be considered for more robust automation" per Pete |
| **Recommendation** | alt — pro robustní + cross-language scenarios; less for rapid F/E iteration |

## §4. Layer × Platform allocation matrix

| Test úroveň | Bouračka (F/E heavy) | X1+ (B/E heavy) | Cross-system |
|-------------|----------------------|-----------------|--------------|
| **Acceptance (UC)** | Playwright primary | Selenium (cross-language) | TBD |
| **System** | Playwright primary | ReadyAPI primary | Selenium |
| **Integration** | Playwright + Mockoon | ReadyAPI + Postman | Selenium + Mockoon |
| **Unit / contract** | (limited; framework agnostic) | ReadyAPI assertions | Postman tests |

## §5. Orchestration approach

### §5.1 `tools/test_console.py` (existing scaffold)

Nyní rozpoznává: Playwright, Cypress, TestCafe.

Rozšíření v této iteraci na **6 frameworks**:

```pwsh
py tools\test_console.py status
# Aktualizovaný výstup:
#   ✓  playwright  (installed)
#   ✓  cypress     (installed)
#   ✓  testcafe    (installed)
#   ✓  readyapi    (installed)        ← NEW — detekce ready-api-cli or testrunner.bat
#   ✓  postman     (installed)        ← NEW — detekce newman
#   ✓  selenium    (installed)        ← NEW — detekce python -c "import selenium"
```

### §5.2 Cross-platform run + aggregation

```pwsh
py tools\test_console.py run --env DEMO_PROD --frameworks all
# Spustí všechny 6 frameworks proti DEMO Bouracka, agregate results
# do TestExecution Summary v Excelu

py tools\test_console.py compare --tcs TC-CP-001..010
# Porovná verdict per framework; ukáže kde Playwright says PASS ale
# ReadyAPI says FAIL (= legitimate cross-layer divergence)
```

## §6. Implementation phases

### §6.1 CP-SUPIN-04 STEP 32 (this iteration — minimum viable)

- [x] Strategy doc (this file)
- [x] TestExecution Summary format spec
- [x] Excel schema migration (13_TestExecutionSummary + 14_AssertionGateResults)
- [ ] ReadyAPI bring-up smoke project (.xml) — TBD this iteration
- [ ] Postman collection scaffolding — TBD
- [ ] Selenium Python script scaffolding — TBD
- [ ] `tools/test_console.py` rozšíření — TBD

### §6.2 CP-SUPIN-05 (next iteration)

- ReadyAPI/SoapUI full bring-up suite parity with Playwright
- Postman collection import → SoapUI auto-export pipeline
- Selenium Python full smoke + first happy-day port
- Cross-platform run aggregation v `test_console.py`
- VUP-style TestExecution Summary auto-export pro SUPIN review

### §6.3 CP-SUPIN-06+ (per branch Sonnet sessions)

- Per branch (DEMO/test/PROD) framework allocation finalised
- Multi-framework regression CI pipeline
- Framework-specific MI-M-T module proposals

## §7. Decision matrix — kdy který framework

| Scenario | Doporučený framework |
|----------|----------------------|
| F/E SPA happy-day E2E | Playwright |
| F/E quick smoke after deploy | Cypress (interactive) nebo Playwright |
| F/E developer-active rapid iteration | Cypress (live runner) |
| B/E SOAP service contract | ReadyAPI/SoapUI |
| B/E REST API regression | Postman + Newman OR ReadyAPI |
| B/E REST API combinatorial input | ReadyAPI (data-driven) |
| Cross-layer F/E + B/E single test | Selenium WebDriver |
| Mock external service | Mockoon |
| Performance / load testing | (TBD — JMeter, K6, Gatling — out of scope CP-SUPIN-04) |

## §8. Component dependencies

| Framework | Runtime | Disk install | License |
|-----------|---------|--------------|---------|
| Playwright | Node.js 20 | ~350 MB | Apache 2.0 |
| Cypress | Node.js 20 | ~500 MB | MIT |
| TestCafe | Node.js 20 | ~80 MB | MIT |
| ReadyAPI | Java JRE 11+ | ~500 MB | Commercial (paid) |
| SoapUI (free tier) | Java JRE 11+ | ~250 MB | EUPL |
| Postman desktop | (standalone) | ~600 MB | Free w/ acct OR Newman = Node.js 20, ~50 MB |
| Selenium (Python) | Python 3.10+ | ~30 MB | Apache 2.0 |
| Mockoon CLI | Node.js 20 | ~50 MB | MIT |

**Total disk impact pokud full stack:** ~2.5 GB across all frameworks.
SecOps doc `SECOPS-COMPONENTS-CS.md` v0.2 must be updated to reflect this.

## §9. Status

| Item | Hodnota |
|------|---------|
| Strategy doc | `_specs/MULTI-PLATFORM-TESTING-STRATEGY-v0.1-CS.md` |
| Verze | v0.1 |
| Datum | 2026-05-06 |
| Audience | SUPIN testing collective + governance |
| Status | strategy locked; implementation phased |
