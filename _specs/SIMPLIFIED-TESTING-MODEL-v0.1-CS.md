# Simplified testing model — `mimt-simple` for OSS community — v0.1 CS

> **Trigger.** CP-SUPIN-05 mid-session 2026-05-07 — Pete:
> "C variant to create long term solution which would be offered as a part of
> MI-M-T to the community also as stand alone solution **based on simplified
> model — not full flatch VUP-based testing model but simple accessible to
> the developers without deeper knowledge of testing discipline**".
>
> **Cíl.** Definovat zjednodušený testovací model pro OSS community —
> developer-accessible, low-barrier-to-entry, žádný požadavek na předchozí
> znalost VUP / V-model / formal testing methodology.
>
> **Companion.** `_specs/MIMT-NATIVE-AUTOMATION-ASSESSMENT-v0.1-CS.md` v0.2
> §6.2 Track C; `_specs/VMODEL-ASSEMBLY-TT-MAPPING-v0.1-CS.md` (full VUP-based
> model — superset of this simple model).

---

## §1. Audience + design constraints

### §1.1 Audience persona

**Devín** (jméno fiktivní), 28 let, full-stack developer, 3 roky zkušeností:
- Zná Playwright základy (umí napsat `test("login works", async ({ page }) => { ... })`)
- Nezná V-model, VUP, ISTQB, BDD/ATDD, nepoužívá Excel pro test plan
- Chce **5-line annotation** přidat do existing testů a dostat coverage report
- **Žádné Excel sheet authoring** — markdown nebo YAML stačí
- **Žádné phased gating** — test buď projde nebo ne
- **Žádné formal "TestTarget enumeration"** — TT je prostě "thing under test", developer vymyslí podle situace
- **Žádné per-environment branching** — má jeden environment (dev nebo staging), pokud má víc, pochopí to ad-hoc
- Cíl: **30 minut learning curve od `npm install mimt-simple` k prvnímu coverage reportu**

### §1.2 Co `mimt-simple` NENÍ

- NENÍ to nový framework — používá Playwright/Cypress/Selenium pod-down
- NENÍ to plný MI-M-T model — to je pro `mimt-harness` (Track B)
- NENÍ to certifikační proces — žádné ISTQB conformance
- NENÍ to test plan management tool — `xlsx` je out of scope pro simple version

### §1.3 Co `mimt-simple` JE

- **Coverage tracking layer** nad existing test framework
- **Test data sharing convention** (single-source YAML)
- **Reporter** s hezkým HTML output (one file)
- **30-minute getting-started** path
- **Unique selling point**: "tests document themselves and emit coverage map"

## §2. Model elements — full VUP vs simplified comparison

### §2.1 TestTarget — drop the 4-layer split

| Aspekt | Full VUP-based (mimt-harness) | Simplified (mimt-simple) |
|--------|------------------------------|--------------------------|
| TT layers | 4 (FUNC / SCRN / LOV / ACTV) | **1 — just "TT"** |
| Naming | `TT-FUNC-001` / `TT-SCRN-rozcestnik` / atd. | `TT-<slug>` např. `TT-login`, `TT-cart-checkout`, `TT-payment` |
| Required fields | tt_code, tt_layer, tt_label_cs, tt_label_en, tt_url_pattern, tt_api_endpoint, tt_widget_role, tt_phase, tt_env_constraints, tt_priority, tt_owner, tt_notes | **3 — name, optional description, optional URL/path** |
| Source format | Excel sheet `15_VModelAssemblyMap` | **YAML or markdown** |

**`mimt-simple` example TT definition (`tts.yaml`):**

```yaml
- name: TT-login
  description: User login flow with username + password
  url: /login

- name: TT-cart-checkout
  description: Cart checkout incl. payment
  url: /cart/checkout

- name: TT-search
  description: Search bar + result list
```

That's it. No layer, no env, no priority, no language split.

### §2.2 Coverage — drop the strength enum

| Aspekt | Full VUP (mimt-harness) | Simplified (mimt-simple) |
|--------|-------------------------|--------------------------|
| Strength values | full / partial / indirect / none | **boolean — covered or not** |
| Source format | Excel sheet `16_CoverageMatrix` (8 cols) | **inline test annotation** |
| Multiple TCs per TT | tracked separately | **deduplicated by TT name** |
| Per-framework binding | tracked | not tracked (single framework run) |

**`mimt-simple` example test annotation (Playwright):**

```typescript
import { test } from "@playwright/test";
import { covers } from "mimt-simple";

test("user can login with valid credentials", async ({ page }) => {
  covers("TT-login");           // 5-line annotation
  await page.goto("/login");
  await page.fill('[name=email]', 'demo@example.com');
  await page.fill('[name=password]', 'demo123');
  await page.click('button[type=submit]');
  await expect(page).toHaveURL('/dashboard');
});
```

Coverage report = list of all TTs from `tts.yaml` with `covered: true|false` per TT, based on whether ANY test called `covers(TT-name)` and the test PASSED.

### §2.3 Coverage rule — drop phased gating

| Aspekt | Full VUP (mimt-harness) | Simplified (mimt-simple) |
|--------|-------------------------|--------------------------|
| Phases | 4 (informational → soft → gating per-class → strict) | **1 — informational only** |
| CI gate | available via `--enforce` | **not available; report only** |
| Per-layer thresholds | configurable (FUNC=100, SCRN=90, LOV=80) | **single percentage** |

**`mimt-simple` CI usage:**

```yaml
# .github/workflows/test.yml
- run: npx playwright test
- run: npx mimt-simple coverage-report
  # Just generates ./mimt-coverage.html — never fails build
```

Optional later: `npx mimt-simple coverage-report --min=80` — fails if < 80%
covered. **One number, not 4 phases.**

### §2.4 Bug naming — drop deterministic dedup

| Aspekt | Full VUP (mimt-harness) | Simplified (mimt-simple) |
|--------|-------------------------|--------------------------|
| Bug ID | `BUG-CP-{TC_CODE}-{ASSERT_CODE}` deterministic | **free-form OR auto from `test name + first line of error`** |
| Dedup | mandatory enforced via Excel | **best-effort hash; user can override** |
| Tracking | `08_Bugs` sheet, occurrences counter, first/last seen | **simple JSON log; no occurrences tracking** |

**Why drop?** Most OSS projects use GitHub Issues / Jira / Linear for bugs.
Don't compete with them — just dump test failures as JSON for ingest.

### §2.5 Test data sharing — keep but simplify

| Aspekt | Full VUP (mimt-harness) | Simplified (mimt-simple) |
|--------|-------------------------|--------------------------|
| Format | YAML in `fixtures/test-data/*.yaml` | **same — keep this design (already simple)** |
| Loaders | per-framework (TS + Python) | **TS for now; Python in v0.2** |
| Structure | nested objects with `_meta` | **same** |

This is the ONE area where the full VUP model is already accessible enough.
No simplification needed; just port the existing YAML loader pattern.

### §2.6 Drift detection — drop framework-specific

| Aspekt | Full VUP (mimt-harness) | Simplified (mimt-simple) |
|--------|-------------------------|--------------------------|
| Drift docs | per-environment Δ matrix + drift recon docs | **NOT in v0.1 simple** |
| URL polling helper | `drift-guard.ts` shipped | **NOT in v0.1 simple** |
| Recovery patterns | `test.skip()` with rationale | **just standard Playwright skip** |

**Rationale:** drift detection is advanced topic. Most OSS users have one
environment. Pin this for `mimt-harness` Track B; keep `mimt-simple` lean.

### §2.7 Pre-ship audit — DROP

`preship_audit.py` is corporate-email-deliverability concern. OSS users push
to npm/PyPI/GitHub Releases — no email-scanner gates needed.

**`mimt-simple` does NOT include preship_audit.**

### §2.8 Reporter — keep ONE simple HTML output

| Aspekt | Full VUP (mimt-harness) | Simplified (mimt-simple) |
|--------|-------------------------|--------------------------|
| Output formats | Excel + JSON + HTML + status badge SVG | **HTML + JSON only** |
| Excel integration | mandatory `excel-row-writer.ts` | **NOT shipped** |
| Status badge | SVG generation | **shipped — single PNG/SVG for README** |
| Per-test artifact links | trace.zip, screenshot, video | **only screenshot + test name** |

`mimt-simple coverage-report` produces:
- `mimt-coverage.html` — single self-contained HTML page (Tailwind via CDN);
  TT list with green checkmarks / red X
- `mimt-coverage.json` — machine-readable for CI / external dashboards
- `mimt-coverage-badge.svg` — copy into README.md

## §3. API surface — `mimt-simple` v0.1

### §3.1 Installation

```bash
npm install --save-dev mimt-simple        # Node ecosystem
# OR
pip install mimt-simple                    # Python ecosystem (Selenium pytest)
```

### §3.2 TypeScript / JavaScript API

```typescript
import { covers, loadFixture, getCoverageReport } from "mimt-simple";

// Annotate any test with TT bindings
test("...", async ({ page }) => {
  covers("TT-login");                       // single TT
  covers(["TT-login", "TT-rememberMe"]);   // multiple TTs
  // ... your test code
});

// Load fixtures from YAML
const users = loadFixture("test-users").users;

// CLI:
//   npx mimt-simple coverage-report     -> generates ./mimt-coverage.{html,json,badge.svg}
//   npx mimt-simple coverage-report --min=80   -> fails build if < 80% TTs covered
//   npx mimt-simple init                -> creates ./tts.yaml + ./fixtures/ scaffold
```

### §3.3 Python API

```python
from mimt_simple import covers, load_fixture, get_coverage_report

def test_login(driver):
    covers("TT-login")
    # ... selenium test code

# CLI: same as above, just `mimt-simple-py`
```

### §3.4 Repo structure (consumer view)

```
my-app/
├── tests/
│   ├── login.spec.ts          ← imports `covers` from mimt-simple
│   └── ...
├── fixtures/
│   └── test-users.yaml         ← single source of truth
├── tts.yaml                    ← TT enumeration (developer-defined)
├── package.json
└── (after run: mimt-coverage.html, mimt-coverage.json, mimt-coverage-badge.svg)
```

That's the entire onboarding shape.

## §4. Developer 30-minute path

### §4.1 Minute 0-5 — install + init

```bash
cd my-app
npm install --save-dev mimt-simple
npx mimt-simple init
# creates: tts.yaml, fixtures/test-users.yaml.example, mimt-simple.config.json
```

### §4.2 Minute 5-15 — define TTs

Open `tts.yaml`, list 5-10 TTs developer cares about:

```yaml
- TT-login
- TT-search
- TT-cart-add
- TT-cart-checkout
- TT-payment
```

### §4.3 Minute 15-25 — annotate existing tests

Open existing Playwright spec, add 1-2 lines per test:

```typescript
import { test, expect } from "@playwright/test";
import { covers } from "mimt-simple";

test("user logs in", async ({ page }) => {
  covers("TT-login");
  // existing test code unchanged
});
```

### §4.4 Minute 25-30 — run + view report

```bash
npx playwright test
npx mimt-simple coverage-report
# Open mimt-coverage.html in browser
```

Result: HTML page showing 5 TTs with coverage status (green = covered by ≥1
passing test, red = not covered).

## §5. Migration path — when developer outgrows simple

When `mimt-simple` user wants more (e.g., per-environment strategy, multi-
framework, drift detection, formal coverage gating), **upgrade path to
`mimt-harness`** is direct:

| Need | Upgrade to |
|------|-----------|
| Per-environment strategy | `mimt-harness` env-aware decorators |
| Coverage strength tracking | `mimt-harness` 4-strength enum |
| Coverage gating in CI | `mimt-harness` Phase 2/3 |
| Drift detection | `mimt-harness` drift-guard helpers |
| Excel TestPlan reporting | `mimt-harness` Excel reporter |
| Multi-framework runner | `mimt-harness` reporter consolidator |
| Bug deterministic dedup | `mimt-harness` BUG-{TC}-{ASSERT} pattern |

`mimt-simple` and `mimt-harness` share **same TT name space** — annotations
written for simple work in harness too. No rewrite, just config swap.

## §6. Differentiation from existing OSS tools

### §6.1 vs Cucumber / Gherkin

- Cucumber emphasizes BDD scenarios in plain English; high learning curve
  for non-developers; tooling overhead
- `mimt-simple` is just annotations + a coverage tracker; zero new DSL

### §6.2 vs Allure / ReportPortal

- Allure / ReportPortal are full-featured reporting platforms; require
  server setup, dashboard, integrations
- `mimt-simple` is one HTML file output; no server, no dashboard

### §6.3 vs Playwright's built-in coverage

- Playwright tracks **CODE coverage** (lines/branches hit)
- `mimt-simple` tracks **TEST TARGET coverage** (which features have tests
  pointing at them) — completely different concept

### §6.4 vs Cypress Component Tests

- Cypress component tests are unit-test-like for components
- `mimt-simple` is a meta-layer over E2E tests indicating WHAT they cover

## §7. Roadmap — `mimt-simple` v0.1 → v1.0

| Version | Trigger | Deliverable |
|---------|---------|-------------|
| **v0.1.0** | CP-SUPIN-06 mid | TS API + CLI + HTML report + scaffold; Playwright integration |
| **v0.2.0** | CP-SUPIN-06 close | Python API + Selenium pytest integration |
| **v0.3.0** | CP-SUPIN-07 | Cypress integration + minimal documentation site |
| **v0.5.0** | CP-SUPIN-08 | First stable release; npm + PyPI publish |
| **v1.0.0** | future | Full OSS launch with docs site, Discord, GitHub Discussions |

## §8. Repo strategy

`mimt-simple` lives in **separate public repo** from `bouracka-tests`:

- `github.com/petr-yamyang/mimt-simple` (or whatever org Pete chooses)
- MIT or Apache-2.0 license
- npm + PyPI release pipeline
- Zero ČKP-specific references; pure OSS

`bouracka-tests` becomes one of multiple **reference impls**:
- README links to "Powered by mimt-simple" badge
- `bouracka-tests` README adds usage example showing how it's annotated

## §9. Open questions

| # | Otázka | Owner |
|---|--------|-------|
| Q-SIMP-1 | License — MIT vs Apache 2.0? Both OSS-compatible; Apache 2.0 more enterprise-friendly | Pete + governance |
| Q-SIMP-2 | Repo organization — pod `petr-yamyang` (personal) nebo MI-M-T org? | Pete |
| Q-SIMP-3 | Naming — "mimt-simple" / "mimt-lite" / "mimt-essentials" / "mimt-starter"? | branding |
| Q-SIMP-4 | Documentation site host — GitHub Pages, Vercel, Mintlify? | Pete |
| Q-SIMP-5 | TT name regex — strict (`^TT-[a-z0-9-]+$`) or lenient (`^TT-.+$`)? | dev |
| Q-SIMP-6 | Coverage report visualization — tree view, flat list, both? | UX |
| Q-SIMP-7 | Test failures handling — skip-with-rationale support v simple, nebo just hard-fail? | dev |

## §10. Status

| Item | Hodnota |
|------|---------|
| Doc | `_specs/SIMPLIFIED-TESTING-MODEL-v0.1-CS.md` |
| Verze | v0.1 |
| Datum | 2026-05-07 mid-session |
| Audience | Pete + governance + future OSS community + MI-M-T product team |
| Companion | `_specs/MIMT-NATIVE-AUTOMATION-ASSESSMENT-v0.1-CS.md` v0.2 §6.2 (Track C) |
| Implementation start | CP-SUPIN-06 (parallel s mimt-harness Track B) |
| Repo target | NEW separate `mimt-simple` repo (public, MIT / Apache 2.0 TBD) |
| Status | spec ready; CP-SUPIN-06 implementation start trigger pending Pete |
