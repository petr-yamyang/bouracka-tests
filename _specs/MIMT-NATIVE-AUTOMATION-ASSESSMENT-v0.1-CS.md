# MI-M-T native automation tool — build-vs-buy — v0.1 CS

> **Trigger.** CP-SUPIN-05 mid-session 2026-05-07: Pete: "whether would make
> sense to start here development of own simple automation tool suit as a
> native part of MI-M-T engine and fallback scenario choice for F/E
> automations such as the one now developed for Bouračka (simple benchmark)".
>
> **Cíl.** Strukturované build-vs-buy assessment, založené na realitách MI-M-T
> projektu (vlastní engine, vlastní methodology, vlastní customer-facing IP)
> + realitách Bouračka case (mature Playwright suite already running, drift
> dependent on commercial framework's headless UA fingerprint).
>
> **Companion.** `_specs/PLATFORM-ASSESSMENT-v0.1-CS.md` (which 4 frameworks
> are promising for F/E test automation as commercial/OSS choices).
> **Tato doc** se ptá: *should MI-M-T have its OWN automation tool too?*

---

## §1. Use case framing

### §1.1 Co by "MI-M-T native automation tool" znamenalo

Tři distinct interpretace, každá s velmi different scope:

| Variant | Scope | Example precedent |
|---------|-------|-------------------|
| **A — full framework** | Vlastní browser automation library (DOM access, network capture, screenshots, waits, selectors) | Cypress / Playwright / TestCafe — ~5+ years dev, 10+ engineers |
| **B — thin adapter / harness** | Lightweight wrapper nad existing framework, codifies MI-M-T conventions (TT binding, coverage, drift detection, reporter) | `bouracka.py` orchestrator pattern, generalized |
| **C — model-only + adapters** | MI-M-T owns model (TT/TC/coverage); ships PLUGIN adapters for each framework (PW, CY, SE) | Cucumber / Gauge — frame test runner agnostic |

Pete's framing ("simple automation tool suit") + the "fallback scenario choice"
context suggests Variant B nebo C. Variant A is almost certainly out of scope
(see §3 cost analysis).

### §1.2 Trigger pro "fallback" scenario

Pete explicitly: "fallback scenario choice for F/E automations". Specific
situations kde commercial framework selže a fallback by se hodil:

1. **Commercial framework je blocked v ČKP corporate AV** (.npm reach, dependency vulnerability, license audit) — fallback potřebuje žádné OSS deps
2. **Commercial framework drifts incompatibilně** (e.g., Playwright 2.x breaks our 1.x conventions) — fallback ekosystém pod kontrolou
3. **Customer SecOps blokuje konkrétní framework** (e.g., reCAPTCHA-stealth plugin = social engineering IOC, can't ship) — fallback bez stealth
4. **MI-M-T model evolution překročí framework adapters** (např. multi-agent orchestration s state-handoff) — vlastní runtime přizpůsobitelný
5. **Specific Bouračka-like SUT charakteristiky** (Czech locale + N8 mock + reCAPTCHA + RUIAN) zabudované defaults

Z těchto, **case 1 a 3 jsou skutečně realistic risks pro corporate ČKP-like
deployments**. Case 2 a 4 jsou méně urgent (řešitelné adaptérem). Case 5 je
luxury, ne necessity.

## §2. Variant A — full framework build

### §2.1 Pros

| # | Pro | Strength |
|---|-----|----------|
| A-1 | **Total IP control** — žádný upstream vendor surprise | ★★★ |
| A-2 | **Customizovatelné na MI-M-T model 1:1** — žádný adapter friction | ★★★ |
| A-3 | **MI-M-T differentiation value** — "comes with own automation" v marketingu | ★★ |
| A-4 | **Žádné OSS dependency churn** — uzavřený stack, snadnější pro corp SecOps audit | ★★ |
| A-5 | **Cs-locale-first** patterns, Czech-specific conventions baked in | ★ |
| A-6 | **Predictable behavior** — unit-tested controlled stack | ★★ |
| A-7 | **Survives Playwright/Cypress maintenance crises** | ★★ |

### §2.2 Cons (the killers)

| # | Con | Severity |
|---|-----|----------|
| A-1 | **Massive dev cost** — Playwright má 6+ years × 100+ contributors; vážná odhady 10+ engineer-years pro production-ready browser automation | ★★★★★ |
| A-2 | **Browser API churn** — Chromium CDP, WebDriver BiDi, Firefox Marionette — protocols se mění; full-time maintainers nutní | ★★★★ |
| A-3 | **Bug surface** — vlastní framework bude mít bugs které Playwright's millions of users už našly a vyřešili | ★★★★ |
| A-4 | **Cross-browser nákladné** — Chromium + Firefox + WebKit + Safari = vlastní WebDriver impl per engine | ★★★★ |
| A-5 | **Mobile real-device téměř nemožné** — Appium dělalo 8+ let, je to celý SubProject | ★★★★★ |
| A-6 | **Reinventing wheels** — selektory, waits, screenshots, traces, network capture, file upload — všechno už solved | ★★★★ |
| A-7 | **Talent acquisition impossible** — testeři znají Playwright/Cypress, ne MI-M-T proprietary framework | ★★★★ |
| A-8 | **No community** — bez Stack Overflow / GitHub issues / extensions ecosystem | ★★★ |
| A-9 | **CI/CD ecosystem missing** — žádné GH Actions plug-in, žádný Allure adapter, žádné Sauce Labs / BrowserStack integration | ★★★★ |
| A-10 | **Opportunity cost** — každá engineer-hour na frameworku není na MI-M-T model nebo TestPlan content | ★★★★★ |
| A-11 | **Customer adoption resistance** — "use our proprietary thing" vs. "use industry standard" — sales friction | ★★★ |
| A-12 | **Security review burden** — corp SecOps musí auditovat custom code místo widely-vetted Playwright | ★★★ |

### §2.3 Variant A verdict

**STRONG NO.** Konflikt mezi A-1..A-12 cons a pouze 7 pros (z nichž A-3 a
A-5 marginal) je extrémní. Žádný racionální investment case.

Žádná open-source successful "we built our own browser automation framework"
exists outside well-funded ecosystem players (Microsoft, Google, Cypress.io
Inc., Smartbear). Teams that try (BrowserStack/Sauce Labs internal projects)
either pivot to wrappers nebo abandon.

## §3. Variant B — thin MI-M-T harness over Playwright (recommended path)

### §3.1 Co by harness obsahoval

Tenká vrstva nad Playwright (or whichever framework wins per
`PLATFORM-ASSESSMENT-v0.1-CS.md`), kódifikuje MI-M-T conventions:

```
mimt-harness/
├── annotations/
│   ├── covers.ts                ← @covers(TT-FUNC-002, TT-SCRN-overeni) decorator/comment parser
│   └── env-aware.ts              ← @env(both|demo-only|prod-only) per-test gate
├── data-loaders/
│   ├── ts/                       ← Playwright + Cypress + TestCafe loader
│   └── py/                       ← Selenium + Appium + Mockoon loader
├── reporters/
│   ├── excel-row-writer.ts       ← (existing) Playwright → BOURACKA-TESTPLAN.xlsx UPSERT
│   ├── coverage-binder.ts        ← Phase 2+ coverage assertion (TT × TC)
│   └── consolidated-json.ts      ← unified JSON across frameworks → Excel
├── helpers/
│   ├── drift-guard.ts            ← URL polling pattern (CP-SUPIN-04 EOD fix)
│   ├── react-controlled-input.ts ← native setter helpers
│   ├── cookie-banner.ts          ← privacy-default reject helper
│   └── mui-autocomplete.ts       ← `[role="listbox"]` pattern
├── audits/
│   ├── coverage_audit.py         ← (existing) Phase 0..3 introduction
│   ├── preship_audit.py          ← (existing) email-deliverability gate
│   └── workbook_validator.py     ← (existing) Excel invariant checks
└── runtime/
    ├── bouracka.py               ← (existing) per-SUT orchestrator template
    └── mimt_orchestrator.py      ← generalized; per-SUT subclass
```

### §3.2 Pros

| # | Pro | Strength |
|---|-----|----------|
| B-1 | **Already 80% built** — `bouracka.py`, `excel-row-writer.ts`, `coverage_audit.py`, `preship_audit.py`, helpers/ — z 3 dní práce hotové | ★★★ |
| B-2 | **MI-M-T-conventions codified** — TT mapping, coverage, drift, reporter patterns | ★★★ |
| B-3 | **Vendor neutrality** — pokud Playwright zmizí, harness se port-uje na Cypress/Selenium za týden | ★★★ |
| B-4 | **Customer onboarding** — testeři znají Playwright; harness jen přidává MI-M-T conventions; krátká learning curve | ★★ |
| B-5 | **Sells MI-M-T methodology + sample harness** — customer dostane runnable starter | ★★★ |
| B-6 | **Maintenance manageable** — ~5-10K LoC; jeden developer udrží | ★★★ |
| B-7 | **CI/CD ecosystem dědí** — uses Playwright's GH Actions, traces, etc. | ★★★ |
| B-8 | **Low risk IP** — žádné claims about beating Playwright; just "MI-M-T conventions on top" | ★★ |
| B-9 | **Bouračka case = first reference impl** — every choice tested in real customer scenario | ★★★ |

### §3.3 Cons

| # | Con | Severity |
|---|-----|----------|
| B-1 | **Couples MI-M-T to Playwright (or chosen primary)** — vendor lock-in light | ★★ |
| B-2 | **Adapter port per new framework** — adding Cypress/Selenium support = additional code | ★★ |
| B-3 | **Cross-framework data sharing convention vyžaduje per-framework loaders** — already designed but not yet implemented | ★★ |
| B-4 | **MI-M-T positioning ambiguity** — is harness part of MI-M-T or "starter kit"? | ★ |
| B-5 | **Maintenance effort still non-zero** — 5-10K LoC stále vyžaduje attention | ★★ |

### §3.4 Variant B verdict

**STRONG YES.** Většina práce už hotová z Bouračka case. Net effort to
generalize ~2-4 weeks of refactoring (extract from `bouracka-tests/` repo to
`mimt-harness/` repo). High ROI, low risk.

## §4. Variant C — model-only + per-framework adapters (Cucumber-style)

### §4.1 Co by C obsahoval

MI-M-T owns:
- **Model** — TT taxonomy, TC schema, coverage matrix, bug naming, env tagging
- **Excel TestPlan** as canonical format
- **Live workbook API** (future MI-M-T server)

MI-M-T ships:
- **Playwright adapter** — adds `@covers` to Playwright tests, ships reporter, fixture loader
- **Cypress adapter** — same pattern
- **Selenium+Appium adapter** — same
- **(future) Code-gen** — TC spec MD → Playwright/Cypress/Selenium spec scaffold

### §4.2 Pros

Stejné jako Variant B, plus:

| # | Pro | Strength |
|---|-----|----------|
| C-1 | **Customer choice of framework** — "use Playwright if you like, or Cypress, or Selenium" | ★★★ |
| C-2 | **Long-term framework agnostic** — Playwright successor in 2030 can plug into MI-M-T | ★★★ |
| C-3 | **Per-framework selling point** — different consultancies prefer different stacks | ★★ |

### §4.3 Cons

Plus oproti Variant B:

| # | Con | Severity |
|---|-----|----------|
| C-1 | **Multiple adapters = multiple maintenance burden** — divisible by team size | ★★★ |
| C-2 | **Lowest-common-denominator design** — features exist in PW but not CY = harness can't expose; coverage suffers | ★★ |
| C-3 | **Onboarding documentation 4× scope** — install + sample-run guide per framework | ★★ |
| C-4 | **Test results consolidation harder** — different report formats; we already started solving with `consolidate_results.py` plan | ★★ |

### §4.4 Variant C verdict

**MODERATE YES, ale not now.** Aspiration goal pro CP-SUPIN-08+ kdy MI-M-T
pivot z internal toolkit na productized offering. Until then, Variant B
(Playwright-coupled harness) je pragmatičtější.

## §5. Decision matrix

| Criterion | Weight | Variant A (full) | Variant B (thin harness) | Variant C (model + adapters) |
|-----------|--------|------------------|--------------------------|------------------------------|
| Effort to MVP | ★★★ | -5 (5+ years) | +3 (already 80%) | +1 (months per adapter) |
| MI-M-T positioning | ★★★ | +3 differentiates | +2 toolset/starter | +3 platform |
| Customer adoption | ★★★ | -3 sales friction | +2 standard PW + extras | +2 framework choice |
| Long-term flexibility | ★★ | +3 total control | +0 PW-coupled | +3 framework agnostic |
| Talent availability | ★★★ | -3 proprietary | +2 PW+conventions | +2 PW or CY or SE |
| Bug surface / risk | ★★ | -3 high | +1 leverage PW | +1 leverage PW+adapters |
| Maintenance cost | ★★★ | -3 dedicated team | +1 1 dev | +0 1 dev × N frameworks |
| Bouračka case fit | ★★★ | 0 (would replace existing PW) | +3 (already aligned) | +2 (would refactor) |
| **Weighted total** | | **−25 (strong NO)** | **+22 (strong YES)** | **+17 (yes, but later)** |

## §6. Recommendation

### §6.1 Decision 2026-05-07 mid-session — Pete confirmed parallel B + C

> **Pete (verbatim):** "choice is clear-start with B to fit the bill with
> release of MI-M-T which is already within a reach and continue immediately
> with C variant to create long term solution which would be offered as a part
> of MI-M-T to the community also as stand alone solution based on simplified
> model — not full flatch VUP-based testing model but simple accessible to the
> developers without deeper knowledge of testing discipline."

Two parallel tracks, **NOT sequential**:

#### Track B — `mimt-harness/` extract for MI-M-T release

- Strategic alignment: MI-M-T launch within reach → harness needed NOW
- Couples to Playwright; Bouračka is first reference impl
- Internal MI-M-T positioning; full VUP-based testing model (TT × TC ×
  coverage × drift × pre-ship gates)
- **Effort:** 2-4 weeks, single developer
- **Trigger:** CP-SUPIN-06 start

#### Track C — `mimt-simple/` OSS community offering with simplified model

- Strategic alignment: MI-M-T differentiation in OSS community
- Per-framework adapters (Playwright, Cypress, Selenium+Appium)
- **Simplified model** — viz `_specs/SIMPLIFIED-TESTING-MODEL-v0.1-CS.md`:
  - ONE TT layer (no FUNC/SCRN/LOV/ACTV split)
  - Coverage = boolean (no strength enum)
  - Coverage rule = informational (no phased gating)
  - Markdown / YAML specs (no Excel required)
  - 30-minute learning curve for developer who already knows Playwright
- **Effort:** 4-8 weeks parallel with B, single developer
- **Trigger:** CP-SUPIN-06 start (parallel track)

### §6.2 Distribution model

```
                    ┌──────────────────────────────────────┐
                    │  MI-M-T platform (commercial)        │
                    │                                      │
                    │  ├─ uses Track B mimt-harness        │
                    │  │   (full VUP model + strict gates) │
                    │  │                                   │
                    │  └─ ships Track C mimt-simple        │
                    │      (OSS community offering)        │
                    └────────────────┬─────────────────────┘
                                     │
                  ┌──────────────────┼─────────────────────┐
                  ▼                  ▼                     ▼
       ┌──────────────────┐ ┌─────────────────┐ ┌────────────────────┐
       │ MI-M-T customers │ │ OSS community   │ │ Standalone usage   │
       │ (full toolset)   │ │ (mimt-simple)   │ │ outside MI-M-T     │
       └──────────────────┘ └─────────────────┘ └────────────────────┘
```

Net: MI-M-T ships BOTH; OSS community consumes only Track C (lower barrier);
MI-M-T customers get Track B + B-only features.

### §6.3 Never (any horizon)

**Variant A — full framework build.** No realistic ROI; no investment.

## §7. Migration plan — extract `mimt-harness/` from Bouračka case

### §7.1 Phase 1 (CP-SUPIN-06)

- Create `mimt-harness/` repo (sibling to `bouracka-tests/` and `SUPIN-ecosystem-map/`)
- Move tools/audits/helpers/reporters per §6.1
- Define stable API surface: `from mimt_harness import bouracka, BaseOrchestrator, ...`
- Keep `bouracka-tests/` operational throughout — initially imports from local
  `../mimt-harness/` via relative path; later from PyPI/npm package

### §7.2 Phase 2 (CP-SUPIN-07)

- Publish `mimt-harness` to private npm + PyPI registry (corp-internal)
- Bouračka tests import from registry version
- Versioned (semver) — harness independent of consumer
- First non-Bouračka consumer pilot (likely first X1 fragment per SUPIN-ecosystem-map)

### §7.3 Phase 3 (CP-SUPIN-08+)

- Variant C transition — Cypress + Selenium adapters in `mimt-harness`
- Documentation for per-framework choice
- Public OSS release? (TBD per MI-M-T productization decision)

## §8. Open questions

| # | Otázka | Owner |
|---|--------|-------|
| Q-NATIVE-1 | MI-M-T productization timeline — kdy harness becomes customer-facing? | governance + business |
| Q-NATIVE-2 | License model — proprietary vs OSS pro mimt-harness? | governance + legal |
| Q-NATIVE-3 | Repo split timing — kdy extract z `bouracka-tests/` → `mimt-harness/`? | Pete + dev |
| Q-NATIVE-4 | Naming — "mimt-harness" / "mimt-runtime" / "mimt-sdk"? | branding |
| Q-NATIVE-5 | Phase 3 (Variant C) trigger — customer demand or strategic decision? | governance |

## §9. Companion + cross-references

- `_specs/PLATFORM-ASSESSMENT-v0.1-CS.md` v0.2 — which 4 frameworks are
  promising; this doc adds: should we build our own?
- `_specs/CP-SUPIN-05-PLAN-CS.md` §3 — what's NOT in CP-SUPIN-05 scope; this
  doc proposes harness extract for CP-SUPIN-06
- `_specs/COMPREHENSIVE-MIND-MAP-SUPIN-MIMT-v0.1-CS.md` — MI-M-T project context
- `bouracka-tests/bouracka.py` — existing orchestrator (MI-M-T harness seed)
- `bouracka-tests/tools/{coverage_audit,preship_audit}.py` — extraction candidates

## §10. Status

| Item | Hodnota |
|------|---------|
| Doc | `_specs/MIMT-NATIVE-AUTOMATION-ASSESSMENT-v0.1-CS.md` |
| Verze | **v0.2** (Pete confirmed parallel B + C strategy 2026-05-07 mid-session) |
| Datum | 2026-05-07 v0.1 + 2026-05-07 mid-session v0.2 |
| Audience | Pete + governance + MI-M-T tech-owner + future OSS community |
| Recommendation v0.2 | **Variant A REJECTED**; **Variant B (mimt-harness) + Variant C (mimt-simple) IN PARALLEL** for CP-SUPIN-06; both ship as part of MI-M-T |
| Effort estimate | B: 2-4 weeks; C: 4-8 weeks; PARALLEL (single developer can split if focused, OR two developers parallel) |
| Trigger | CP-SUPIN-06 start (now imminent) |
| Companion | `_specs/SIMPLIFIED-TESTING-MODEL-v0.1-CS.md` (Track C model spec) |
| Status | v0.2 — decisions locked; CP-SUPIN-06 ready to start |
