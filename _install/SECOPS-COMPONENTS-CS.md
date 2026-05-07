# Bouračka — Komponenty instalované na testerských noteboocích — pro SecOps review — v0.1 CS

> **Adresát.** SecOps tým ČKP, IT bezpečnost, governance.
> **Účel.** Detailní audit-grade popis VŠECH komponent, které tester
> nebo automatizační skript instaluje na pracovní stanici (notebook)
> v rámci Bouračka testing rollout. Podklad pro security approval +
> allowlist konfiguraci proxy/firewall.
>
> **Status.** v0.1 — připraveno pro SecOps review před prvním rollout
> na další testerské stanice (po prvním proven testu na ThinkPadu Petra
> Žemly 2026-05-06).

---

## §1. Executive summary

Bouračka testing kit instaluje na tester stanici **6 hlavních komponent**
(Python runtime, Node.js runtime, Java JRE, automatizační frameworky,
podpůrné nástroje), všechny **veřejně dostupné z trusted sources**.
Žádný proprietární software, žádný custom installer, žádné kernel-level
ovladače. Kompletní instalace probíhá **v user-space** (kromě počáteční
runtime instalace přes `winget`, která vyžaduje admin window).

| Komponenta | Zdroj | Typ | Admin nutný? |
|------------|-------|-----|--------------|
| Python 3.12 | python.org via winget | runtime | ANO (jednorázově) |
| Node.js 20 LTS | nodejs.org via winget | runtime | ANO (jednorázově) |
| OpenJDK 21 | Microsoft via winget | runtime | ANO (jednorázově) |
| Playwright + Chromium | npm registry | test framework | NE (user-space) |
| Cypress | npm registry | test framework | NE (user-space) |
| TestCafe | npm registry | test framework | NE (user-space) |
| Mockoon CLI | npm registry | mock server | NE (user-space) |
| PlantUML | github.com/plantuml | diagram tool | NE (user-space) |
| openpyxl + Python deps | PyPI | Python libs | NE (user-space) |

## §2. Sources of all installed software

### §2.1 Trusted publishers

Všechny komponenty pocházejí z **trustovaných veřejných zdrojů**:

| Zdroj | URL | Účel | Typ trustu |
|-------|-----|------|------------|
| Microsoft winget repo | `winget.azureedge.net` | runtime installers | MS-signed; Windows 10/11 native package manager |
| python.org | `python.org`, `pypi.org`, `files.pythonhosted.org` | Python runtime + libraries | PSF Foundation; SHA256-verified |
| Node.js Foundation | `nodejs.org`, `dist.nodejs.org` | Node runtime | OpenJS Foundation; signed releases |
| Microsoft OpenJDK | `microsoft.com/openjdk`, `aka.ms/download-jdk` | Java JRE | MS-signed |
| npm registry | `registry.npmjs.org`, `*.npmjs.com` | npm packages | npm Inc. (GitHub subsidiary) |
| Playwright CDN | `cdn.playwright.dev`, `playwright.download.prss.microsoft.com` | Chromium browser binary | MS-signed |
| GitHub | `github.com`, `objects.githubusercontent.com` | PlantUML jar | GitHub-hosted; signed releases |

### §2.2 Network allowlist (firewall / proxy)

SecOps musí povolit následující domény na tester stanici během instalace
+ pro běžné testy:

#### Pro instalaci (jednorázové, admin window)

| Domain | Účel | Frekvence |
|--------|------|-----------|
| `*.winget.azureedge.net` | winget repo | jednorázově při winget install |
| `*.python.org`, `*.pypi.org`, `*.pythonhosted.org` | Python + PyPI | jednorázově |
| `*.nodejs.org`, `*.dist.nodejs.org` | Node | jednorázově |
| `aka.ms/download-jdk`, `*.microsoft.com` | OpenJDK download | jednorázově |
| `*.npmjs.com`, `registry.npmjs.org` | npm packages | každý `npm install` |
| `cdn.playwright.dev` | Chromium binary | jednorázově |
| `playwright.download.prss.microsoft.com` | Chromium binary | jednorázově |
| `*.githubusercontent.com`, `github.com` | PlantUML jar (volitelné) | jednorázově |

#### Pro běh testů (denně)

| Domain | Účel | Frekvence |
|--------|------|-----------|
| `demo.bouracka.cz` | DEMO testing target | každý běh |
| `tst.demo.bouracka.cz` | DEMO test (firewall-gated) | každý běh proti DEMO test |
| `bouracka.cz`, `tst.bouracka.cz` | PROD/PROD-test (po dodání přístupů) | každý běh proti PROD |
| `ags.cuzk.cz` | RUIAN address geocoding (Bouračka volá přímo z prohlížeče) | autocomplete trigger |
| `maps.googleapis.com` | Google Maps (Bouračka SUT) | mapy v Phase 3 |
| `bourackaodstavky78861.z6.web.core.windows.net` | Azure outage feed (Bouračka SUT) | každý mount route |
| `www.google.com/recaptcha/*` | reCAPTCHA v3 | invisible captcha |

> **Poznámka:** ČÚZK + Google Maps + reCAPTCHA volá Bouračka SUT, ne
> testovací nástroj. Pokud SecOps blokne tyto domény, Bouračka
> přestane fungovat — testy by detekovaly funkční regression jako
> environmental block.

## §3. Detailed component inventory

### §3.1 Python 3.12

- **Source:** `winget install Python.Python.3.12` (= python.org installer)
- **Install path:** `%LOCALAPPDATA%\Programs\Python\Python312\`
- **Privileges needed:** admin (jednorázově pro winget)
- **Disk:** ~150 MB (Python core) + ~50 MB (libraries — openpyxl, pillow_heif, etc.)
- **Network during runtime:** přístup na `pypi.org` pro `pip install` (cca 5 MB transit)
- **Risk profile:** standard Python install. PSF-signed. Open source PSF License.
- **Used for:** validátor sešitu, konzole testů, Excel manipulation, ad-hoc skripty

### §3.2 Node.js 20 LTS

- **Source:** `winget install OpenJS.NodeJS.LTS` (= nodejs.org installer)
- **Install path:** `C:\Program Files\nodejs\`
- **Privileges needed:** admin (jednorázově)
- **Disk:** ~100 MB Node + ~200 MB node_modules (per project)
- **Network during runtime:** `npmjs.org` pro `npm install` (cca 200 MB transit první install)
- **Risk profile:** standard Node install. OpenJS-Foundation. MIT/BSD licence napříč.
- **Used for:** Playwright/Cypress/TestCafe runtime, mockoon-cli

### §3.3 OpenJDK 21 (volitelné)

- **Source:** `winget install Microsoft.OpenJDK.21` (= MS-signed)
- **Install path:** `C:\Program Files\Microsoft\jdk-21.x.x-hotspot\`
- **Privileges needed:** admin (jednorázově)
- **Disk:** ~330 MB
- **Network during runtime:** žádný (offline tool)
- **Risk profile:** Microsoft Build of OpenJDK. GPL+CE licence.
- **Used for:** PlantUML rendering. **VOLITELNÉ** — operátor přeskočí pokud nepotřebuje UML diagram render.

### §3.4 Playwright + Chromium

- **Source:** npm package `@playwright/test` + Chromium binary z `cdn.playwright.dev`
- **Install path:** `node_modules/@playwright/test` (cca 200 MB) + `%LOCALAPPDATA%\ms-playwright\chromium-*` (cca 150 MB)
- **Privileges needed:** žádné (user-space)
- **Disk:** ~350 MB total
- **Network during runtime:** test target (např. demo.bouracka.cz)
- **Risk profile:** Microsoft-maintained framework. Apache 2.0 licence.
- **Used for:** primary E2E test framework. Headless Chromium = standard browser engine.

### §3.5 Cypress (volitelné)

- **Source:** npm package `cypress`
- **Install path:** `node_modules/cypress` + `%USERPROFILE%\AppData\Local\Cypress\Cache\`
- **Privileges needed:** žádné
- **Disk:** ~500 MB (Electron-based, includes own Chromium copy)
- **Network during runtime:** test target
- **Risk profile:** Cypress.io company. MIT licence.
- **Used for:** secondary framework — for CP-SUPIN-05 multi-framework srovnání. **VOLITELNÉ**.

### §3.6 TestCafe (volitelné)

- **Source:** npm package `testcafe`
- **Install path:** `node_modules/testcafe`
- **Privileges needed:** žádné
- **Disk:** ~80 MB
- **Network during runtime:** test target
- **Risk profile:** DevExpress company. MIT licence.
- **Used for:** secondary framework — pro CP-SUPIN-05 srovnání. **VOLITELNÉ**.

### §3.7 Mockoon CLI (volitelné)

- **Source:** npm package `@mockoon/cli`
- **Install:** globally via `npm install -g @mockoon/cli`
- **Privileges needed:** žádné (user-global npm install)
- **Disk:** ~50 MB
- **Network during runtime:** žádný (čistě localhost mock server)
- **Risk profile:** Mockoon (open-source company). MIT licence.
- **Used for:** mock SOAP/REST endpoints na localhost (např. N8 SMS Gateway mock pro PROD-test). **VOLITELNÉ**.

### §3.8 PlantUML jar (volitelné)

- **Source:** `github.com/plantuml/plantuml/releases/.../plantuml-1.2024.7.jar` (cca 12 MB)
- **Install path:** `%USERPROFILE%\tools\plantuml.jar` (manual download)
- **Privileges needed:** žádné
- **Disk:** ~12 MB
- **Network during runtime:** žádný (offline jar)
- **Risk profile:** open-source GPL projekt. JAR file je signed by PlantUML team.
- **Used for:** rendering UML diagramů z .puml zdrojů. **VOLITELNÉ**.

## §4. Test artifacts created on disk

Při běhu testů se vytváří následující soubory:

| Cesta | Obsah | Velikost (typ) | Cleanup |
|-------|-------|----------------|---------|
| `test-results/` | screenshots, videos, traces z failed testů | ~50 MB / run | manual nebo `npx playwright test --reporter=list` cleanup |
| `playwright-report/` | HTML report | ~5 MB / run | auto-overwrite na další run |
| `node_modules/` | npm dependencies | ~200 MB | persistent; smaže `npm install` |
| `fixtures/intel-YYYY-MM-DD/` | intel-probe outputs (codelists JSON, network traces) | ~5 MB / run | manuál |
| `*.xlsx` | Excel master test plan | ~100 KB | persistent |

**Citlivá data v artefaktech:**
- Screenshots/videa mohou zachytit DEMO test data (synthetic personas — není problém)
- Network traces obsahují URL parametry vč. `magicKey` z ČÚZK (public service, ne sensitive)
- **Žádné credentials** — žádný login, žádné API keys (kromě veřejně-viditelných reCAPTCHA + Maps keys, které jsou přímo v Bouračka SUT bundle)

## §5. Privileges + scope analysis

### §5.1 Co potřebuje admin window

JEDNORÁZOVĚ:
- `winget install Python.Python.3.12`
- `winget install OpenJS.NodeJS.LTS`
- `winget install Microsoft.OpenJDK.21` (volitelné)
- `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` (jednorázové, ale CurrentUser scope = bez admin OK)

PO INSTALACI: žádný admin nutný. Všechny `npm install`, `pip install`,
`npx playwright install chromium`, atd. fungují user-level.

### §5.2 Co NESmí kit dělat

- ❌ Modify system files (registry, system32, drivers)
- ❌ Install kernel-level drivers
- ❌ Open inbound network ports (testovací framework je outbound-only)
- ❌ Persist auto-start services
- ❌ Auto-update bez user interakce (npm/pip default je on-demand)

### §5.3 Co kit dělá (informational)

- ✅ Outbound HTTP/HTTPS k allowlisted domains (test target + dependency mirrors)
- ✅ Localhost ports (Mockoon: 3001; Playwright UI: 9323) — jen pokud uživatel explicitně spustí
- ✅ User-space disk write (test results, node_modules)
- ✅ Clipboard read (Playwright může simulate paste — ale jen v rámci browser kontextu)

## §6. Data residency + GDPR

### §6.1 Test data

VŠECHNA testovací data jsou **synthetická**:
- Telefonní čísla: `608 000 001`, `608 000 002` (placeholders, nikdy neposíláme reálné SMS na DEMO)
- OP / ŘP čísla: `123 456 789`, `987 654 321` (synthetic)
- Adresy: `Václavské nám. 50, Unhošť` (real RUIAN-resolvable, ale neidentifikuje testera)
- E-maily: `demo-test-A@example.com` / `demo-test-B@example.com` (RFC 2606 reserved)

### §6.2 Outbound data flow

| Kam | Co | Trvání |
|-----|----|--------|
| ČÚZK (`ags.cuzk.cz`) | autocomplete query (např. "Václavské") + user IP | per request |
| Google Maps (`maps.googleapis.com`) | viewport coords + user IP | per request |
| reCAPTCHA (`google.com`) | user behaviour signals + IP | invisible v3 |
| Bouračka SUT (`demo.bouracka.cz`) | form data, OTP codes (synthetic), … | per test |

**Žádný outbound data flow neobsahuje PII operátora.** Synthetic test data
nejsou PII (RFC 2606 reserved emails, placeholder phones).

### §6.3 Persisted data

- Test results na disku (synthetic data, žádné PII)
- Browser cookies pro Bouračka domain (po test-end smazány Playwright `--reset` — pokud nakonfigurováno)

## §7. Code provenance + supply chain

| Komponenta | Source code | Auditable? |
|------------|-------------|------------|
| Python | github.com/python/cpython | ANO — open source |
| Node.js | github.com/nodejs/node | ANO |
| OpenJDK | github.com/openjdk/jdk | ANO |
| Playwright | github.com/microsoft/playwright | ANO |
| Cypress | github.com/cypress-io/cypress | ANO |
| TestCafe | github.com/DevExpress/testcafe | ANO |
| Mockoon | github.com/mockoon/mockoon | ANO |
| PlantUML | github.com/plantuml/plantuml | ANO |
| Bouracka tests | (this repo) | governance: Pete + SUPIN/ČKP review |

Žádné closed-source nebo non-auditable komponenty.

### §7.1 Transitive dependencies (npm)

`npm install` vytahuje ~600 transitive dependencies z npm registry.
Většina jsou utility libraries (chalk, lodash, glob, ...). Policy:

- **Audit:** `npm audit` se spouští automaticky při `npm install`.
  Aktuální známá zranitelnost level: **5 (1 moderate, 4 high)** — všechny
  v Playwright transitive deps; non-blocking, čeká na Playwright minor bump.
- **Renovate / Dependabot:** TBD pro CI integraci.
- **No automatic upgrades** — `npm install` instaluje exactly co je
  v `package-lock.json`. SecOps může auditovat lockfile před deploy.

### §7.2 Python deps

`pip install` vytahuje pouze `openpyxl` (+ jeho deps: `et-xmlfile`).
Auditable, MIT licence.

## §8. Allowlist v korporátní síti — kompletní seznam

```
# Pre-flight (jednorázové, instalace)
*.winget.azureedge.net
*.python.org
*.pypi.org
*.pythonhosted.org
*.nodejs.org
*.dist.nodejs.org
aka.ms/download-jdk
*.microsoft.com (openjdk.microsoft.com, learn.microsoft.com)
*.npmjs.com
registry.npmjs.org
cdn.playwright.dev
playwright.download.prss.microsoft.com
github.com
*.githubusercontent.com
objects.githubusercontent.com

# Runtime (denní)
demo.bouracka.cz
tst.demo.bouracka.cz   (po dodání VPN přístupu)
bouracka.cz            (pro PROD prelive testy)
tst.bouracka.cz        (po dodání VPN přístupu)
ags.cuzk.cz            (Bouračka SUT volá z prohlížeče)
maps.googleapis.com    (Bouračka SUT)
bourackaodstavky78861.z6.web.core.windows.net  (Bouračka outage feed)
www.google.com/recaptcha/*  (Bouračka reCAPTCHA)
```

## §9. Security testing posture (z testing repu)

### §9.1 Known weaknesses to triage

Aktuální `npm audit` reportuje 5 zranitelností v transitive deps:
- 1 moderate severity
- 4 high severity

Všechny v Playwright transitive deps (rimraf, fstream, glob, lodash.isequal,
uuid, inflight). **Non-blocking** pro test execution. Plánovaný fix:
upgrade Playwright na nejnovější minor po jejich release.

### §9.2 No known SecOps blockers

Žádný komponent v kit nemá:
- Known CVE blocking installation
- Known supply chain compromise
- Privacy escalation risk

## §10. Approval gate checklist (pro SecOps reviewer)

| # | Check | Status |
|---|-------|--------|
| 1 | All sources from trusted publishers (winget/PyPI/npm/GitHub releases) | ✅ |
| 2 | No proprietary or unaudited components | ✅ |
| 3 | All licenses are open source compatible (MIT/Apache/BSD/GPL+CE) | ✅ |
| 4 | No kernel-level / driver-level installations | ✅ |
| 5 | No persistent services / auto-start | ✅ |
| 6 | All data is synthetic; no PII outbound | ✅ |
| 7 | No credentials stored in repo | ✅ |
| 8 | Network allowlist documented + minimal | ✅ |
| 9 | Transitive dependency audit reviewed | ⚠ 5 known issues, non-blocking |
| 10 | Cleanup procedure documented (test-results, node_modules) | ✅ |

## §11. Onboarding flow (operator-facing)

1. SecOps schválí + nakonfiguruje firewall allowlist (§8)
2. Operátor obdrží **temporary admin window** (~30 min) pro winget install
3. Operátor projde `INSTALL-FROM-ZERO-v0.4-CS.md` (parallel-document)
4. Po instalaci: admin window se ukončí; všechny další operace user-space
5. Operátor spustí `scripts\sanity-check.ps1` → 7/7 pass = ready
6. První test: `scripts\run-bring-up-smoke.ps1` proti DEMO Bouračka

Detail postupu pro operátora viz `INSTALL-FROM-ZERO-v0.4-CS.md`.

## §12. Companion documents

- `_install/INSTALL-FROM-ZERO-v0.4-CS.md` — operátorská instalační příručka
- `_specs/TESTER-LESSONS-LEARNED-v0.1-CS.md` — empirical guide pro testery
- `_specs/ROADMAP-4-TARGET-CS.md` — strategic 4-target plan
- `EXCEL-VERSIONING-FIX-CS.md` + `PRIORITY-MATRIX-BUGFIX-CS.md` — bugfix advisories

## §13. Stav

| Item | Hodnota |
|------|---------|
| Dokument | `_install/SECOPS-COMPONENTS-CS.md` |
| Verze | v0.1 |
| Datum | 2026-05-06 |
| Audience | SecOps tým ČKP |
| Status | připraveno k SecOps review |
| Companion | parallel s INSTALL-FROM-ZERO-v0.4-CS.md (operátor) |
| Reviewer akce | schválit allowlist + admin window pro každého nového testera |
