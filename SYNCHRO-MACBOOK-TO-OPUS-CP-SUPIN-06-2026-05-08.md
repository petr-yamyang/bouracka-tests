# Synchro MacBook → Opus (ThinkPad) — CP-SUPIN-06 prep — 2026-05-08
## MacBook governance reply to ThinkPad's v0.5.0 deliverables; reconciles convergence + divergence; ships the 3 requested MIMT-* drafts inline

**Version:** v0.1.0
**Trigger:** GitHub sync 2026-05-08 — MacBook pulled `petr-yamyang/bouracka-tests` v0.5.0 (ThinkPad's CP-SUPIN-04 + 05 deliverables) and now responds with the corresponding governance work that ran on MacBook in parallel (catalogue v0.1.2, N8 contract analysis, harvest discipline, methodology refinement, OPUS-REVIEW). This doc bridges the two streams so CP-SUPIN-06 starts from a single shared baseline.
**Authority:** v0.1 binding; supersedes any earlier MacBook→ThinkPad messages on overlapping topics; is itself a request-for-comment from Opus governance to ThinkPad Opus + Pete.
**Audience:** ThinkPad Opus (consume §6 + §7 + §8 + §9 to inform CP-SUPIN-06 decisions); Pete (review + green-light + push to `petr-yamyang/bouracka-tests` per §10); future Sonnet sessions on either side (consume §3 catalogue + §4 + §5 MIMT-* drafts).
**Posture:** ThinkPad's CP-SUPIN-04 + 05 work is **architecturally strong** and converges substantively with MacBook governance work that ran in parallel — this is a *good* outcome (independent confirmation rather than divergent paths). This doc surfaces the convergence, names the few real divergences, and ships the 3 MIMT-* drafts ThinkPad explicitly requested (per `SYNCHRO-MACBOOK-CP-SUPIN-04-2026-05-07-EOD.md` §4.2 + `SYNCHRO-MACBOOK-CP-SUPIN-05-2026-05-07-EOD.md` §4).

---

## §0. How to use this doc

```
Step 1 — operator (Pete) pulls the cloned repo: ~/Documents/VibeCodeProjects/SUPIN/bouracka-tests
Step 2 — copy this file + 4 MacBook _config/ docs into the repo per §10 instructions
Step 3 — commit + push to origin/main (or to a new branch if Pete prefers staged review)
Step 4 — ThinkPad Opus pulls + reads this doc as STEP 1 of CP-SUPIN-06
Step 5 — CP-SUPIN-06 morning starts with the unified baseline
```

---

## §1. Acknowledge ThinkPad CP-SUPIN-04 + 05 — what's excellent

10 things worth preserving on any future iteration:

| # | Thing | Why it's excellent |
|---|---|---|
| **E-TP-1** | `bouracka.py` pure-Python orchestrator | Closes the email-deliverability scanner block in one move; pattern is generalisable to any corporate-target test kit; `tools/preship_audit.py` is the gate that should exist in MI-M-T (and was listed in catalogue §10 application targets but never implemented). |
| **E-TP-2** | `recon/ARCHITECTURE-OVERVIEW-v0.1-CS.md` with 8 numbered data flows | This independently validates the SUPIN platform pattern hypothesis MacBook articulated in `SUPIN-N8-CONTRACT-ANALYSIS-v0.1.md` §2 + §15. AISPOV-as-façade, IS ČKP internal map (SEDN/B3WS/P3WS), register fan-out (AIS ČKP → ROB / CRŘ via ISSS) — all confirmed. |
| **E-TP-3** | `_specs/VMODEL-ASSEMBLY-TT-MAPPING-v0.1-CS.md` (TT-FUNC/SCRN/LOV/ACTV 4-layer) | This is *operationally equivalent* to MacBook's Cartesian (Req × FURPS+) → TestTargetGroups transposition (per `METH-REFINE-TESTANALYSIS-TESTDESIGN-v0.1.md` §2). Different basis, same concept. See §2.1 for reconciliation. |
| **E-TP-4** | `_specs/COVERAGE-RULE-STRATEGY-v0.1-CS.md` (4-phase introduction) | Mirrors MacBook's R-DESIGN-1 coverage operator (per METH-REFINE §3) but with the practical phase-in strategy MacBook didn't think through. **Better than what MacBook shipped on the gating-pace question.** |
| **E-TP-5** | `_specs/EMAIL-DELIVERABILITY-RULES-v0.1-CS.md` + decoupled-versioning policy | Both are universal patterns (not Bouračka-specific). MacBook will fold the decoupled-versioning into catalogue v0.1.4. |
| **E-TP-6** | `_specs/CROSS-FRAMEWORK-DATA-SHARING-v0.1-CS.md` (single-source YAML + per-framework loaders) | Generalisable to any multi-framework test kit. Adopt as MIMT module candidate (see §6.2 below). |
| **E-TP-7** | DEMO drift forensic + reCAPTCHA-v3 score-based bot detection hypothesis | The HP Elite trace capture + 5-hypothesis triage is gold-standard analytical work. Should ship as an exemplar in the harvest discipline doc next iteration. |
| **E-TP-8** | `_specs/THREE-DEVICE-PLAN-CS.md` (ThinkPad/MacBook/HP Elite asymmetric model) | This is the operational topology matching MacBook's stage 0/1/2 + topology A/B model (per `OPUS-CYCLE-v0.2.1-STAGES-ADDENDUM`). Exact alignment. |
| **E-TP-9** | `_specs/MIMT-NATIVE-AUTOMATION-ASSESSMENT-v0.1-CS.md` (build-vs-buy on MI-M-T own framework) | Variants A/B/C analysis is exactly the kind of strategic call MI-M-T needs. MacBook accepts the verdict (Variant A ruled out; B + C parallel tracks). See §5 below. |
| **E-TP-10** | `bouracka-tests-v0.5.0.zip` (657 KB, SHA256 `5543993b…`, pre-ship audit PASS) | Tangible, runnable, scanner-clean deliverable in operator hands. The thing that makes everything else real. |

---

## §2. Convergence + divergence — where MacBook and ThinkPad agree, complement, or differ

### §2.1 Convergence — independently confirmed concepts

| MacBook concept | ThinkPad concept | Convergence |
|---|---|---|
| Catalogue v0.1.2 §2f Cartesian governance (Req × FURPS+) | `VMODEL-ASSEMBLY-TT-MAPPING` 4-layer (FUNC/SCRN/LOV/ACTV) | **EQUIVALENT.** Both are *transposition operators* on the requirement space; FURPS+ slices by quality dimension, V-model slices by abstraction layer. Use BOTH bases for richer coverage analysis (each TT carries `furps_dimensions` AND `tt_assembly_layer`). |
| METH-REFINE R-DESIGN-1 (TestDesign = coverage operator; TestCasePackage entity) | `COVERAGE-RULE-STRATEGY` (4-phase introduction) | **COMPLEMENTARY.** MacBook supplies the *what* (Package as design intent); ThinkPad supplies the *how* (gating-pace phase-in). Adopt both. |
| SUPIN-N8-CONTRACT §2 (SUPIN platform pattern: URL pattern + X-SUPIN header + mTLS + `/fake/`) | `recon/ARCHITECTURE-OVERVIEW` 8 numbered flows + IS ČKP map | **CONFIRMED.** Independent observers reaching the same architecture from different inputs (Postman+OpenAPI+ReadyAPI vs live recon). High confidence. |
| ARCH-HARVEST R-HARVEST-1 (provenance + confidence + last_validated) | ThinkPad's bottom-up live recon practice (DEMO public 2026-05-05) | **OPERATIONAL CONFIRMATION.** ThinkPad ran the discipline in practice without formally adopting R-HARVEST-1 tags. Recommend retroactively tagging the recon docs. |
| METH-REFINE R-ANALYSIS-1 (transposition mandatory; cells map to TTs) | `VMODEL-ASSEMBLY-TT-MAPPING` ~70 prefilled items | **OPERATIONAL CONFIRMATION.** ThinkPad executed the transposition without naming it that. The 70 TT items are the *output* of an implicit Cartesian. |

### §2.2 Divergence — three real differences

| Topic | MacBook position | ThinkPad position | Resolution |
|---|---|---|---|
| **Workbook schema next-bump priority** | METH-REFINE §6.1 proposed sheets `01a_AnalysisTransposition` + `02e_TestCasePackages` | Per `CP-SUPIN-05-PLAN-CS.md` §5.2: `15_VModelAssemblyMap` + `16_CoverageMatrix` planned for v0.5.1 | **DO BOTH.** ThinkPad's `15_VModelAssemblyMap` is the V-model transposition output; add MacBook's `01a_AnalysisTransposition` as the FURPS+-keyed transposition output (sister sheet). `16_CoverageMatrix` is the Package-coverage view; align with `02e_TestCasePackages` so they share `package_ref`. Recommend ThinkPad authors a single migration script `migrate_to_v0_5_1_unified_transposition.py` that adds all 4 sheets together. |
| **TestCasePackage naming** | METH-REFINE §3.5 used `TPC-CP-A1-HAPPY` (TPC prefix) | ThinkPad workbook + recon use `TC-CP-A1-MAIN-DEMO` (TC prefix) | **TPC stays; TC stays.** They're different layers. TC = individual case (executable). TPC = Package (design intent grouping ≥ 1 TC). Naming hygiene: rename ThinkPad's `a1-main-happy-day-demo.spec.ts` to map cleanly: TPC-CP-A1-MAIN-DEMO contains TC-CP-A1-MAIN-DEMO-001 (the single happy E2E) + TC-CP-A1-MAIN-DEMO-NOK-001 (drift case). Already aligned per E-TP-3 above. |
| **Coverage gating pace** | MacBook METH-REFINE: validator enforces from v0.2 (strict from day 1) | ThinkPad COVERAGE-RULE-STRATEGY: 4-phase informational → soft → gating per-class → strict | **ADOPT THINKPAD'S PHASE-IN.** ThinkPad's gradual approach is more realistic; MacBook's strict-from-day-1 would block delivery before TC base is broad enough. Catalogue v0.1.4 will reframe R-DESIGN-1 to allow phased enforcement (binding *eventually*; phase per project's coverage-rule-phase setting). |

### §2.3 Complementary — MacBook adds, ThinkPad adds

| Layer | MacBook contributes (not in ThinkPad's repo) | ThinkPad contributes (not in MacBook's _config/) |
|---|---|---|
| Vocabulary | `VOCABULARY-CATALOGUE-CS-EN-V0.1.md` v0.1.2 (~360 terms; FURPS+ canonical CS; CAST §2b; Test Management §2c; VUP §4.3.2c; SUPIN §6) | `_specs/VMODEL-ASSEMBLY-TT-MAPPING` 4-layer taxonomy CS labels; ~70 prefilled TTs ready for assembly-map seeding |
| Architecture | `SUPIN-ARCH-HARVEST-DISCIPLINE-v0.1.md` (R-HARVEST-1 + R-VALIDITY-1 + R-CONSISTENCY-1 + R-MODEL-IS-CODE; provenance/confidence/decay framework) | `recon/ARCHITECTURE-OVERVIEW-v0.1-CS.md` (8 flows + IS ČKP map + 6 component additions: AIS ČKP, ROB, CRŘ via ISSS, B3WS, P3WS, SEDN, D8WS) |
| Integration | `SUPIN-N8-CONTRACT-ANALYSIS-v0.1.md` (full N8 contract + SUPIN platform pattern + 7 forward-looking assertion library entries) | `mockoon/n8-sms-gateway.json` (the actual mock; runnable) + 9 `recon/integrations/INT-001..009` docs |
| Methodology | `METH-REFINE-TESTANALYSIS-TESTDESIGN-v0.1.md` (transposition + coverage operators; TestCasePackage entity; R-ANALYSIS-1 + R-DESIGN-1) | `_specs/CP-SUPIN-05-PLAN-CS.md` (5-stream consolidation + phased delivery v0.5.0 → v0.7.0) |
| Tooling | (specs only — no Python tools yet) | `tools/preship_audit.py` v0.1 + `tools/coverage_audit.py` v0.1 + 8 migration scripts |
| Testing | (no executable tests) | Playwright `a1-main` + 8 `a2-alternates` + Cypress/TestCafe/Selenium scaffolds + 9 TC SPECs |

**Net pattern:** MacBook ships the **formal vocabulary + architectural discipline + methodology spec** (governance layer); ThinkPad ships the **operational artefacts + executable code + live recon** (delivery layer). They co-evolve cleanly.

---

## §3. MacBook outputs propagated into the SUPIN repo

The following 5 docs from MacBook's `_config/` should land in the SUPIN repo for ThinkPad consumption. Recommend committing under `_specs/from-macbook/` (sibling to existing `_specs/`) so origin is clear.

| # | MacBook source | Target in SUPIN repo | Purpose |
|:--:|---|---|---|
| 1 | `_config/VOCABULARY-CATALOGUE-CS-EN-V0.1.md` (v0.1.2) | `_specs/from-macbook/VOCABULARY-CATALOGUE-CS-EN-v0.1.2.md` | Bilingual canonical vocabulary; binding for all CS rendering |
| 2 | `_config/SUPIN-N8-CONTRACT-ANALYSIS-v0.1.md` | `_specs/from-macbook/SUPIN-N8-CONTRACT-ANALYSIS-v0.1.md` | N8 contract + SUPIN platform pattern + 7 LIB-AS-N8-* assertion patterns |
| 3 | `_config/SUPIN-ARCH-HARVEST-DISCIPLINE-v0.1.md` | `_specs/from-macbook/SUPIN-ARCH-HARVEST-DISCIPLINE-v0.1.md` | Dual-track discipline (testing + arch-harvest); R-HARVEST-1..R-MODEL-IS-CODE |
| 4 | `_config/METH-REFINE-TESTANALYSIS-TESTDESIGN-v0.1.md` | `_specs/from-macbook/METH-REFINE-TESTANALYSIS-TESTDESIGN-v0.1.md` | TestAnalysis = transposition; TestDesign = coverage; TestCasePackage entity |
| 5 | `_config/OPUS-REVIEW-THINKPAD-DELIVERY-v0.1.0-2026-05-05.md` | `_specs/from-macbook/OPUS-REVIEW-THINKPAD-DELIVERY-v0.1.0-2026-05-05.md` | Original Opus review of ThinkPad v0.1.0 — historical context |

Once these 5 + this synchro doc are in the repo, ThinkPad has full visibility into MacBook's reasoning chain.

---

## §4. MIMT-IMPORT-CONTRACT-DRAFT — what Bouračka v0.5+ must emit, what MI-M-T must provide

**Per ThinkPad request:** `SYNCHRO-MACBOOK-CP-SUPIN-04-2026-05-07-EOD.md` §4.2 item 1.

### §4.1 Direction — Bouračka → MI-M-T (write-side)

The Bouračka workbook (currently `BOURACKA-TESTPLAN-v0.4.2.xlsx`) emits these entities to MI-M-T:

| Entity | Source sheet | MI-M-T target table | Cadence |
|---|---|---|---|
| Requirements | `00b_Requirements` (NEW per Opus review G2 — not yet in v0.4.2) | `requirements` | per workbook commit |
| TestTargets (flow-driven) | `02_TestTargets` (28 items) | `test_targets` | per workbook commit |
| TestTargets (assembly-level) | `15_VModelAssemblyMap` (planned v0.5.1; ~70 items) | `test_targets` (with `tt_assembly_layer` discriminator) | per workbook commit |
| Cartesian (Req × FURPS+) | `01b_Req_FURPS_Cartesian` (NEW per Opus review G7 — not yet in v0.4.2) | `requirement_furps_cells` | per workbook commit |
| AnalysisTransposition | `01a_AnalysisTransposition` (NEW per METH-REFINE — not yet in v0.4.2) | `analysis_transposition` | per workbook commit |
| StateMachine | `01c_StateMachine` (NEW per Opus review §6.4 — not yet in v0.4.2) | `state_machines` + `state_transitions` | per workbook commit |
| TestCases | `02_TestCases` (49 items) | `test_cases` | per workbook commit |
| TestCaseParameters | `02b_TC_Parameters` (NEW per Opus review §6.1 — not yet in v0.4.2) | `test_case_parameters` | per workbook commit |
| TestCaseAssertions | `02c_TC_Assertions` (NEW per Opus review §6.2 — not yet in v0.4.2) | `test_case_assertions` | per workbook commit |
| AssertionLibrary | `02d_AssertionLibrary` (NEW per Opus review §6.3 — not yet in v0.4.2) | `assertion_library` | per workbook commit (includes 7 LIB-AS-N8-* per N8-CONTRACT) |
| TestCasePackages | `02e_TestCasePackages` (NEW per METH-REFINE §3 — not yet in v0.4.2) | `test_case_packages` + junctions | per workbook commit |
| CoverageMatrix | `16_CoverageMatrix` (planned v0.5.1) | `coverage_view` (computed) | computed; not stored |
| TestData | `03_TestData` | `test_data` | per workbook commit |
| TestEnvironments | `04_TestEnvironments` | `test_environments` | per workbook commit |
| TestPlan / TestSchedule / TestEstimate | `05a_TestPlan` / `05b_TestSchedule` / `05c_TestEstimate` (per Opus review G6) | `test_plans` / `test_schedules` / `test_estimates` | per workbook commit |
| TestRuns | `06_TestRuns` | `test_runs` | per Playwright run |
| TestRunResults | `07_TestRunResults` | `test_run_results` | per TC execution |
| Bugs | `08_Bugs` | `bug_reports` | per bug logged |
| TestExecutionSummary | `13_TestExecutionSummary` (ThinkPad v0.4.2) | `test_execution_summaries` | per Playwright run |
| AssertionGateResults | `14_AssertionGateResults` (ThinkPad v0.4.2) | `assertion_gate_results` | per assertion fired |

**Format:** Excel (xlsx) is canonical write format. JSON (per-sheet export) is the wire format for the MI-M-T DOCK-EXCEL adapter (per `MI-M-T-V0.2-POC-ONPREM-SCOPE.md` v0.3+).

### §4.2 Direction — MI-M-T → Bouračka (read-side)

MI-M-T provides these services consumable from the Bouračka project:

| Service | What it returns | Bouračka use case |
|---|---|---|
| Live workbook view | Current Excel state on the server | Tester pulls latest TC catalogue without manual file transfer |
| Validator API (`POST /api/v1/validate-workbook`) | Pass/fail + violation list | Pre-ship gate (replaces / extends `tools/preship_audit.py`) |
| Runner backend (`POST /api/v1/projects/{pid}/runs`) | RunId | Trigger Playwright run from MI-M-T frontend |
| Results sink (`POST /api/v1/runs/{rid}/results`) | Acknowledgement | Playwright reporter pushes results to MI-M-T (replaces / extends `tools/append_test_run_result.py`) |
| Coverage view (`GET /api/v1/projects/{pid}/coverage`) | Coverage matrix | "Are we ready to release?" answer |
| Drift reporter (`POST /api/v1/runs/{rid}/drift`) | Acknowledgement | DEMO drift forensic capture (per ThinkPad pattern) |

### §4.3 Migration timeline

| Phase | When | Bouračka state | MI-M-T state |
|---|---|---|---|
| Phase 0 (now) | CP-SUPIN-05 / 06 | Excel v0.4.2; tools-driven local validation | MI-M-T PoC schema D-09 PASS; not yet exposed |
| Phase 1 | CP-SUPIN-07 (~Q3 2026) | Excel v0.5.x → JSON export every commit; manual upload to MI-M-T staging | MI-M-T staging accepts JSON imports via DOCK-EXCEL adapter |
| Phase 2 | Q4 2026 | Excel becomes derivative; MI-M-T live workbook is canonical | MI-M-T live workbook + validator API + runner backend exposed to authorised partners |
| Phase 3 | Q2 2027 | Bouračka tooling reads/writes via MI-M-T API; Excel becomes a generated view for stakeholder review only | MI-M-T full multi-tenant; Bouračka is one of N projects |

### §4.4 Open contract questions

| OQ# | Question | Decision needed by |
|---|---|---|
| OQ-CONTRACT-01 | Excel-as-canonical vs JSON-as-canonical for the wire format — recommend JSON (lossless; tooling-friendly) with Excel as derived view | Phase 1 design |
| OQ-CONTRACT-02 | Authentication for the read-side API — partner cert (per SUPIN platform pattern) or OAuth2/OIDC (per existing Keycloak)? Recommend OAuth2/OIDC for MI-M-T (broader applicability than SUPIN-specific cert) | Phase 1 design |
| OQ-CONTRACT-03 | Field naming — Bouračka uses CS labels in some places (`item_name_cs`); MI-M-T schema uses EN canonical. Confirm: CS labels stay in workbook; EN identifier is the wire format. | Phase 1 design |
| OQ-CONTRACT-04 | Versioning — calendar (per SUPIN N8 platform pattern `/2025/01/`) vs SemVer (per kh-sim). Recommend calendar for MI-M-T API surface. | Phase 1 design |

---

## §5. MIMT-METHODOLOGY-PROPOSAL — generalising 11 patterns into universal vs Bouračka-specific

**Per ThinkPad request:** `SYNCHRO-MACBOOK-CP-SUPIN-04-2026-05-07-EOD.md` §4.2 item 2 + `SYNCHRO-MACBOOK-CP-SUPIN-05-2026-05-07-EOD.md` §3.

### §5.1 The 11 patterns from ThinkPad lessons learned

| # | Pattern | Universal? | MI-M-T module candidate |
|---|---|:---:|:---:|
| 1 | Branch-aware schema design (`applies_to_*` columns) | ★★★ universal | YES — schema-templating module |
| 2 | Single-master + render-on-demand documentation | ★★★ universal | YES — doc-generation module |
| 3 | Deterministic bug dedup keys (`BUG-{TC}-{ASSERT}`) | ★★★ universal | YES — bug-management module |
| 4 | Recovery patterns as code (heredoc inline) | ★★★ universal | YES — onboarding-resilience module |
| 5 | Δ matrix as audit trail | ★★★ universal | YES — environment-governance module |
| 6 | Empirical preflight rules | ★★★ universal | YES — onboarding-resilience module (same as #4) |
| 7 | Multi-platform parallel testing strategy | ★★★ universal | YES — framework-agnostic runner module |
| 8 | TestExecution Summary VUP-grade artefact | ★★★ universal | YES — reporting module |
| 9 | Bottom-up reverse engineering as default modus operandi | ★★★ universal | NO (process discipline; not a module) |
| 10 | Independence rule (zero blocking dependency on customer infra) | ★★★ universal | NO (deployment discipline) |
| 11 | 3-device asymmetric model | ★★ context-dependent | PARTIAL — multi-environment session orchestration module |

### §5.2 Plus: 8 patterns MacBook contributes

| # | Pattern | Source | Universal? | MI-M-T module candidate |
|---|---|---|:---:|:---:|
| 12 | FURPS+ as Cartesian-expansion governance dimension | catalogue §2e + §2f | ★★★ universal | YES — quality-governance module |
| 13 | Source-artefact derivation (R-DERIVE-1) | catalogue §2d | ★★★ universal | YES — provenance module |
| 14 | Diligence as 3rd assessment dimension | catalogue §2c.5 | ★★ universal | PARTIAL — priority-governance enrichment |
| 15 | Plan ≠ Schedule ≠ Estimate (Vaněk distinction) | catalogue §2c.2 | ★★★ universal | YES — planning module |
| 16 | TestAnalysis = transposition operator | METH-REFINE §2 | ★★★ universal | YES — methodology module |
| 17 | TestDesign = coverage operator + TestCasePackage | METH-REFINE §3 | ★★★ universal | YES — methodology module (same as #16) |
| 18 | SUPIN platform integration pattern | N8-CONTRACT §2 | ★★ context-dependent (any large-org-hosted platform) | PARTIAL — integration-pattern catalogue (1st entry: SUPIN; future: AISPOV-style; future: other client platforms) |
| 19 | Architectural-harvest dual-track discipline | ARCH-HARVEST | ★★★ universal | YES — model-governance module |

### §5.3 Combined module map for MI-M-T

11 (ThinkPad) + 8 (MacBook) = 19 patterns; 14 are MI-M-T module candidates. Grouped:

```
MI-M-T modules (proposed for v0.4 architecture):

├── governance/
│   ├── methodology               # patterns 16, 17 (Test analysis + design ops; Package entity)
│   ├── quality-dimensions        # pattern 12 (FURPS+ Cartesian)
│   ├── provenance                # pattern 13 (R-DERIVE-1)
│   ├── planning                  # pattern 15 (Plan/Schedule/Estimate split)
│   ├── coverage                  # patterns 7, 8 (multi-platform + TES)
│   ├── bug-management            # pattern 3 (deterministic dedup)
│   ├── environment               # pattern 5 (Δ matrix)
│   └── model-validity            # pattern 19 (R-VALIDITY-1)
├── runner/
│   ├── framework-agnostic        # pattern 7 (multi-platform parity)
│   └── multi-session-orchestrator # pattern 11 (3-device asymmetric)
├── packaging/
│   ├── deliverability-gate       # ThinkPad's preship_audit.py — universal
│   └── recovery-resilient        # patterns 4, 6 (heredoc + preflight)
├── reporting/
│   ├── tes-vup                   # pattern 8 (TES format)
│   └── coverage-matrix           # pattern 12 + 17
├── integration-patterns/
│   ├── supin-platform            # pattern 18 (1st entry; expandable catalogue)
│   └── (future: aispov-pattern, other-platform-pattern)
├── doc-generation/
│   └── branched-master-render    # patterns 1, 2
└── onboarding-resilience/
    └── (patterns 4, 6 — install-time recovery + empirical preflight)
```

### §5.4 Bouračka-specific specialisations (do NOT generalise)

These ARE Bouračka-specific; should NOT become MI-M-T modules:

- Czech-locale validations (mobile prefix list, OP/ŘP regexes, ČKP-specific codelists)
- Bouračka domain entities (Účastník, Záznam DN, integrations INT-001..009)
- Bouračka state machine (`accidentReportStatus` 8-state machine)
- DEMO-vs-PROD branch tagging (project-instance specific)
- N8 SMS Gateway specifics (vendor-specific; lives in `integration-patterns/supin-platform` as a reference example only)

### §5.5 Migration plan — module by module

| Module | Source | Estimated effort | Sequence |
|---|---|:--:|:--:|
| `methodology` | METH-REFINE + V-model TT mapping | 2 weeks | 1st (foundation for others) |
| `quality-dimensions` | FURPS+ catalogue + sensitivity sweeps | 1 week | 2nd |
| `coverage` | COVERAGE-RULE-STRATEGY + TestCasePackage | 2 weeks | 3rd |
| `provenance` | R-DERIVE-1 + Δ matrix | 1 week | 4th |
| `runner` | bouracka.py + multi-platform | 3 weeks | 5th |
| `packaging` | preship_audit + recovery patterns | 1 week | 6th |
| `reporting` | TES + coverage matrix | 2 weeks | 7th |
| `integration-patterns/supin-platform` | N8-CONTRACT §2 + §15 | 1 week | 8th |
| `doc-generation` | branched-master + recovery heredoc | 2 weeks | 9th |
| `onboarding-resilience` | preflight + recovery | 1 week | 10th |

**Total:** ~16 weeks for all 10 modules. Sequenceable; can run in parallel.

---

## §6. MIMT-COMPONENT-MIGRATION — `tools/*.py` migration candidates

**Per ThinkPad request:** `SYNCHRO-MACBOOK-CP-SUPIN-05-2026-05-07-EOD.md` §4 item 3.

### §6.1 ThinkPad's `tools/` inventory (post-v0.5.0)

| Tool | Lines (est) | Purpose | MI-M-T candidate? |
|---|:---:|---|---|
| `preship_audit.py` | ~150 | ZIP scan for forbidden ext + IOC strings | ★★★ direct port |
| `coverage_audit.py` v0.1 | ~200 | TT × TC coverage matrix audit | ★★★ direct port (extend with FURPS+ axis) |
| `validate_workbook.py` | ~300 | Excel schema + content validation | ★★★ direct port (extend with R-rules from MacBook) |
| `bump_workbook_version.py` | ~80 | Version + computed values | ★★ universal pattern; abstract |
| `check_priority_matrix.py` | ~100 | Sev × Urg → Pri matrix validator | ★★★ direct port (already binding governance) |
| `fix_priority_matrix.py` | ~80 | Priority formula bugfix utility | ★ Bouračka-specific bugfix; not a module |
| `migrate_to_v03.py` | ~200 | v0.2 → v0.3 schema migration | ★★ pattern; abstract into versioned-migration template |
| `migrate_to_v04_branch_tagging.py` | ~150 | branch columns | ★★ same pattern |
| `migrate_to_v04_2_tes.py` | ~150 | TES sheets addition | ★★ same pattern |
| `migrate_08bugs_v04_1.py` | ~120 | Bug dedup schema | ★★ same pattern |
| `render_branch_doc.py` | ~150 | Branched MD slicer | ★★★ direct port (doc-generation module) |
| `append_test_run_result.py` | ~100 | Excel UPSERT from reporter | ★★★ direct port (reporting module) |
| `generate_tests.py` | (TBD) | TC code generation from spec | ★★ partial port; depends on framework-agnostic runner |
| `test_console.py` | (TBD) | Multi-framework runner | ★★★ direct port (runner module) |
| `build_mindmaps.py` | ~100 | Graphviz mindmap rendering | ★ Bouračka-specific tooling; keep in repo |

### §6.2 Direct-port candidates (★★★) — 7 tools

These should land in the MI-M-T `tools/` (or rename to `governance-cli/`) with minimal modification:

1. `preship_audit.py` → `mimt-cli/preship-audit` (universal email-deliverability gate)
2. `coverage_audit.py` → `mimt-cli/coverage-audit` (extend with FURPS+ + Package axes)
3. `validate_workbook.py` → `mimt-cli/validate-workbook` (extend with all MacBook R-rules)
4. `check_priority_matrix.py` → `mimt-cli/validate-priority` (extend with Diligence dimension)
5. `render_branch_doc.py` → `mimt-cli/render-branched-doc` (universal doc-generation)
6. `append_test_run_result.py` → `mimt-cli/append-run-result` (with API-mode that posts to MI-M-T runner backend)
7. `test_console.py` → `mimt-cli/test-console` (framework-agnostic runner CLI)

### §6.3 Pattern-abstraction candidates (★★) — 5 tools

These embody patterns; abstract before porting:

1. Migration scripts (4 of them): abstract into `mimt-cli/schema-migrate <from-version> <to-version>` reading versioned migration steps from `migrations/` dir
2. `bump_workbook_version.py`: abstract into `mimt-cli/version-bump`

### §6.4 Bouračka-specific (★) — keep in `bouracka-tests/tools/`

`fix_priority_matrix.py`, `build_mindmaps.py`. They're project-instance utilities, not platform tools.

### §6.5 Effort estimate

- ★★★ direct ports: 1 week (per tool average, due to interface stabilisation + tests)
- ★★ pattern abstractions: 2 weeks total
- **Total:** 9-10 weeks of work; can parallelise to ~4 calendar weeks with 2-3 contributors.

---

## §7. Q-MIMT-1..5 governance questions answered

| Q | Question | MacBook governance answer |
|---|---|---|
| **Q-MIMT-1** | Excel framework freeze date — kdy stop schema bumps? | Recommend **freeze after CP-SUPIN-06** (i.e. v0.6.x is the last schema-bumping version; v0.7.x onward only adds rows + columns within existing sheets; new sheets become breaking changes requiring proposal + review). Rationale: by v0.6 we'll have all four "next-bump" sheets landed (`01a_AnalysisTransposition` + `15_VModelAssemblyMap` + `16_CoverageMatrix` + `02e_TestCasePackages`); enough for MI-M-T migration to begin. |
| **Q-MIMT-2** | MI-M-T live workbook readiness pro Bouračka migration? | Per `MI-M-T-V0.2-POC-ONPREM-SCOPE.md`: D-09 portability pass closed; PHP route audit identifies 5 missing CRUD routes for `/api/v1/projects` (T6 gap). Realistic readiness: **Q1 2027** for staging exposure; **Q2 2027** for production-like multi-tenant. The 16-week module-migration plan in §5.5 is the critical path. |
| **Q-MIMT-3** | Q3 2026 freeze viable? | **NO. Q1 2027 realistic; Q3 2026 too early** because (a) modules per §5 not yet built; (b) MI-M-T PHP layer has 5 CRUD-route gaps; (c) Bouračka v0.6 schema additions still pending. Recommend communicate Q1 2027 to stakeholders. |
| **Q-MIMT-4** | Component module hosting (where do `tools/` migrate to)? | Recommend **single `mimt-governance/` package** with `mimt-cli` entry-point (Python; pip-installable; CLI commands per §6.2). Hosted at `petr-yamyang/mimt-governance` (private until v0.4 closes; public from v0.5). Bouračka's `tools/` becomes a thin wrapper that pip-installs `mimt-governance` and calls `mimt-cli` commands. Migration timeline: 9-10 weeks per §6.5. |
| **Q-MIMT-5** | Bouračka-specific patterns vs MI-M-T-universal patterns split? | Per §5 above: 14 of 19 patterns are universal (MI-M-T module candidates); 5 are Bouračka-specific (Czech-locale, ČKP integrations, state machine, branch tagging, vendor specifics). This split is now formalised; honour it in all future module decisions. |

---

## §8. New OQs — MacBook → ThinkPad / Pete

| OQ# | Sev | Urg | Pri | Question | Resolve by |
|-----|:---:|:---:|:---:|----------|------------|
| OQ-MB-01 | A | A | A | Pull the 5 MacBook docs into the SUPIN repo per §3 — operator decides location: `_specs/from-macbook/` (recommended; clear origin) or merge into `_specs/` directly | this push |
| OQ-MB-02 | A | A | A | Reconcile `15_VModelAssemblyMap` (ThinkPad's transposition) + `01a_AnalysisTransposition` (MacBook's transposition) — implement BOTH per §2.2; ThinkPad authors single migration script `migrate_to_v0_5_1_unified_transposition.py` | CP-SUPIN-06 STEP 2 |
| OQ-MB-03 | B | A | A | TestCasePackage `02e_TestCasePackages` sheet — author per METH-REFINE §3.5 in v0.5.1 OR defer to v0.6.0 with the bigger schema bump? Recommendation: bundle with v0.5.1 (no point landing 4 sheets across 2 releases) | CP-SUPIN-06 STEP 2 |
| OQ-MB-04 | A | A | A | Coverage gating phase-in cadence — adopt ThinkPad's 4-phase approach. MacBook's R-DESIGN-1 reframed in catalogue v0.1.4 to allow `coverage_rule_phase` per project (0=informational..3=strict). What phase does Bouračka start at? Recommendation: Phase 1 (warning) for v0.5.1; Phase 2 (per-class gating) at v0.6 | CP-SUPIN-06 |
| OQ-MB-05 | B | B | B | The 5 forward-looking assertion library entries from N8-CONTRACT §11.2 (LIB-AS-N8-001..007) — fold into `02d_AssertionLibrary` when that sheet lands. Confirm naming convention `LIB-AS-N8-NNN` is preserved | v0.5.1 schema migration |
| OQ-MB-06 | C | B | C | Repository topology — current single `bouracka-tests` repo, planned future `mimt-harness/` + `mimt-simple/` per `MIMT-NATIVE-AUTOMATION-ASSESSMENT-v0.1-CS.md` §6. Plus MacBook proposes `mimt-governance/` per §6.4. Three repos plus this one = four. Worth a topology diagram + rationale doc | post CP-SUPIN-06 |
| OQ-MB-07 | A | A | A | The drift forensic on POST /api/reports — MacBook reading suggests it's a *bot detection signal*, but worth verifying whether it's **product behaviour** (intended) or **deployment artefact** (a misconfiguration we can fix). MacBook hypothesis: deployment artefact (Azure Front Door reCAPTCHA-v3 threshold tuned too aggressively for E2E test traffic). Forward this to ČKP IT alongside the Q-ARCH-4 thread | next ČKP IT exchange |
| OQ-MB-08 | B | A | A | Bouračka workbook v0.5.1 should fold the SUPIN platform pattern from N8-CONTRACT §2 into `04_TestEnvironments` as a column `platform_pattern_ref` — a string identifier pointing to a pattern catalogue entry. Future SUPIN integrations (AISPOV when it lands) inherit from the same pattern automatically | v0.5.1 schema migration |
| OQ-MB-09 | C | C | C | The harvest-discipline R-rules (R-HARVEST-1 + R-VALIDITY-1 + R-CONSISTENCY-1 + R-MODEL-IS-CODE) — recommend ThinkPad retroactively tag the existing `recon/integrations/INT-001..009` docs with the provenance/confidence/last_validated metadata. Cost: ~30 min per doc; ~5 hours total | post CP-SUPIN-06; opportunity-driven |
| OQ-MB-10 | B | B | B | The `tools/preship_audit.py` IOC scanner — MacBook proposes adding `from-macbook/*.md` files to the scan whitelist (they may contain literal IOC examples in `§1.2 String IOCs` that the current scanner would flag). Verify the runtime-built `chr()`-concat pattern handles this gracefully | first time MacBook docs go through preship-audit |

---

## §9. Recommended CP-SUPIN-06 priorities

Combining ThinkPad's open threads (per `SESSION-CLOSE-CP-SUPIN-05-2026-05-07-EOD.md` §3) + MacBook's new OQs (§8 above):

### §9.1 HIGH — must land in CP-SUPIN-06

| # | Item | Owner | Est |
|---|---|---|:--:|
| 1 | Pull MacBook docs into SUPIN repo per §3 | Pete | 5 min |
| 2 | Read this synchro + the 5 MacBook docs (esp. METH-REFINE + N8-CONTRACT) | ThinkPad Opus | 1 h |
| 3 | Schema migration v0.4.2 → v0.5.1 unified per OQ-MB-02 + OQ-MB-03 — adds 4 new sheets (`01a_AnalysisTransposition` + `15_VModelAssemblyMap` + `16_CoverageMatrix` + `02e_TestCasePackages`) + 7 column extensions | ThinkPad Sonnet | 4 h |
| 4 | Validator extension per OQ-MB-04 (R-rules from MacBook reframed for phased coverage gating) | ThinkPad Sonnet | 2 h |
| 5 | Resolve drift status — HP Elite Cíl 2 run results when they arrive | Pete + HP Elite | (external) |

### §9.2 MEDIUM — preferred for CP-SUPIN-06

| # | Item | Owner | Est |
|---|---|---|:--:|
| 6 | Cypress port of `a2-alternates` (per CP-SUPIN-05-PLAN §5.2) | ThinkPad Sonnet | 6 h |
| 7 | TestCafe port of `a2-alternates` | ThinkPad Sonnet | 4 h |
| 8 | Scaffold `mimt-governance/` repo (per Q-MIMT-4 + §6.4) — initial 4 directly portable tools | MacBook Sonnet | 1 day |
| 9 | Methodology-track AMENDMENT 3 in `_config/METHODOLOGY-MAPPING-V0.1.md` (fold the convergence findings from §2 here) | MacBook Opus | 2 h |
| 10 | MacBook publishes `MIMT-MODULE-MIGRATION-v0.1.md` — full version of the module decomposition in §5 + §6 | MacBook Opus | 1 day |

### §9.3 LOW — deferred or opportunity-driven

| # | Item | Owner |
|---|---|---|
| 11 | `recon/diagrams/architecture-overview.png` — Pete drops the original PNG | Pete |
| 12 | Retroactive R-HARVEST-1 tagging of `recon/integrations/INT-001..009` per OQ-MB-09 | ThinkPad Sonnet |
| 13 | New INT docs (INT-010..015 for AIS ČKP, ROB, CRŘ via ISSS, B3WS, P3WS, SEDN, D8WS — placeholders ready in ARCHITECTURE-OVERVIEW) | ThinkPad Sonnet |
| 14 | Architecture revision for `bouracka-tests` itself — e.g. `from-macbook/` vs merging into `_specs/` | Pete decision |

---

## §10. Operator commit/push instructions (MacBook → GitHub)

The cloned repo is at `~/Documents/VibeCodeProjects/SUPIN/bouracka-tests/`. Pete commits these from MacBook:

```bash
cd ~/Documents/VibeCodeProjects/SUPIN/bouracka-tests

# Optional: branch off main for staged review (recommended)
git checkout -b macbook/cp-supin-06-prep-2026-05-08
# OR commit directly to main if pushing as governance:
# git checkout main

# Create the from-macbook subdirectory
mkdir -p _specs/from-macbook

# Copy the 5 MacBook governance docs
cp ~/Documents/VibeCodeProjects/_config/VOCABULARY-CATALOGUE-CS-EN-V0.1.md \
   _specs/from-macbook/VOCABULARY-CATALOGUE-CS-EN-v0.1.2.md
cp ~/Documents/VibeCodeProjects/_config/SUPIN-N8-CONTRACT-ANALYSIS-v0.1.md \
   _specs/from-macbook/SUPIN-N8-CONTRACT-ANALYSIS-v0.1.md
cp ~/Documents/VibeCodeProjects/_config/SUPIN-ARCH-HARVEST-DISCIPLINE-v0.1.md \
   _specs/from-macbook/SUPIN-ARCH-HARVEST-DISCIPLINE-v0.1.md
cp ~/Documents/VibeCodeProjects/_config/METH-REFINE-TESTANALYSIS-TESTDESIGN-v0.1.md \
   _specs/from-macbook/METH-REFINE-TESTANALYSIS-TESTDESIGN-v0.1.md
cp ~/Documents/VibeCodeProjects/_config/OPUS-REVIEW-THINKPAD-DELIVERY-v0.1.0-2026-05-05.md \
   _specs/from-macbook/OPUS-REVIEW-THINKPAD-DELIVERY-v0.1.0-2026-05-05.md

# Copy this synchro doc into the repo root (alongside other SYNCHRO-MACBOOK-* files)
cp ~/Documents/VibeCodeProjects/_config/SYNCHRO-MACBOOK-TO-OPUS-CP-SUPIN-06-2026-05-08.md \
   ./SYNCHRO-MACBOOK-TO-OPUS-CP-SUPIN-06-2026-05-08.md

# Verify the preship-audit doesn't trip on the new files (per OQ-MB-10)
# This may flag false-positives on the catalogue + N8 contract docs (they contain literal IOC examples in prose)
py tools/preship_audit.py . 2>&1 | tail -20

# If preship audit fails on the from-macbook/ docs:
#   Option A: add `_specs/from-macbook/` to the scanner whitelist (per OQ-MB-10)
#   Option B: rewrite the IOC examples in the catalogue to use the chr()-concat technique ThinkPad uses
# Recommend Option A: the catalogue docs are governance-only, never email-shipped

# Stage everything
git add _specs/from-macbook/ SYNCHRO-MACBOOK-TO-OPUS-CP-SUPIN-06-2026-05-08.md

# Commit with descriptive message
git commit -m "feat(governance): MacBook→Opus sync CP-SUPIN-06 prep

Pulls 5 MacBook _config/ docs into _specs/from-macbook/:
- VOCABULARY-CATALOGUE-CS-EN-v0.1.2 (~360 terms; FURPS+; Cartesian governance)
- SUPIN-N8-CONTRACT-ANALYSIS-v0.1 (platform pattern; 7 LIB-AS-N8-* assertion patterns)
- SUPIN-ARCH-HARVEST-DISCIPLINE-v0.1 (R-HARVEST-1..R-MODEL-IS-CODE)
- METH-REFINE-TESTANALYSIS-TESTDESIGN-v0.1 (transposition + coverage operators)
- OPUS-REVIEW-THINKPAD-DELIVERY-v0.1.0-2026-05-05 (historical context)

Plus SYNCHRO-MACBOOK-TO-OPUS-CP-SUPIN-06-2026-05-08.md at repo root:
- §1 acknowledges ThinkPad's E-TP-1..10 excellents
- §2 reconciles convergence (5 items) + divergence (3 items) + complementary (6 layers)
- §4 MIMT-IMPORT-CONTRACT-DRAFT (write + read directions; migration timeline)
- §5 MIMT-METHODOLOGY-PROPOSAL (19 patterns; 14 universal modules)
- §6 MIMT-COMPONENT-MIGRATION (15 tools; 7 direct ports)
- §7 Q-MIMT-1..5 governance answers
- §8 10 new OQ-MB-* questions back to ThinkPad
- §9 CP-SUPIN-06 priorities (5 HIGH + 5 MEDIUM + 4 LOW)
- §10 these instructions

CP-SUPIN-06 morning starts here."

# Push
git push -u origin macbook/cp-supin-06-prep-2026-05-08
# OR if direct to main:
# git push origin main

# If branch was used: open a PR from this branch back into main on GitHub.
# ThinkPad pulls the branch, reads, and either merges or works in-branch.
```

**Alternative (lighter-weight) — push directly to main without branching:**

If Pete prefers the direct path (no PR review), substitute `git checkout main` for the branch step and `git push origin main` for the push step.

---

## §11. What ThinkPad Opus does first when it pulls

```
Step 1 — git pull origin main  (or fetch the branch)
Step 2 — read SYNCHRO-MACBOOK-TO-OPUS-CP-SUPIN-06-2026-05-08.md (this doc) FIRST
Step 3 — skim the 5 docs in _specs/from-macbook/ (focus on:
         - METH-REFINE §2 + §3 + §6 + §7 — critical for v0.5.1 schema work
         - SUPIN-N8-CONTRACT §11.2 — for assertion library pattern seeding
         - VOCABULARY-CATALOGUE §1 + §2b + §2c + §3 + §6 — for any CS rendering
         - ARCH-HARVEST §3 + §4 — if doing fresh recon
         - OPUS-REVIEW for context)
Step 4 — execute CP-SUPIN-06 priorities §9 in priority order
Step 5 — at session close, write SYNCHRO-MACBOOK-CP-SUPIN-06-2026-05-NN-EOD.md
         responding with progress + new OQs
```

---

## §12. Status footer

| Item | Value |
|------|-------|
| Document | `SYNCHRO-MACBOOK-TO-OPUS-CP-SUPIN-06-2026-05-08.md` |
| MacBook source position | `_config/SYNCHRO-MACBOOK-TO-OPUS-CP-SUPIN-06-2026-05-08.md` |
| Repo target position | `bouracka-tests/SYNCHRO-MACBOOK-TO-OPUS-CP-SUPIN-06-2026-05-08.md` (repo root) |
| Trigger | GitHub sync 2026-05-08; ThinkPad shipped v0.5.0 with substantial governance work + asked for 3 MIMT-* drafts |
| MacBook docs propagated | 5 (catalogue + N8-CONTRACT + ARCH-HARVEST + METH-REFINE + OPUS-REVIEW) |
| Sections | 12 |
| Convergence points | 5 (Cartesian↔V-model; coverage; SUPIN platform; harvest discipline; transposition) |
| Divergence points | 3 (workbook schema priority; Package naming; coverage gating pace) |
| Complementary layers | 6 (vocabulary; arch; integration; methodology; tooling; testing) |
| MIMT-* drafts inline | 3 (IMPORT-CONTRACT §4; METHODOLOGY-PROPOSAL §5; COMPONENT-MIGRATION §6) |
| Q-MIMT answers | 5 (Q-MIMT-1..5) |
| New OQs | 10 (OQ-MB-01..10) |
| CP-SUPIN-06 priorities | 14 (5 HIGH + 5 MEDIUM + 4 LOW) |
| Operator instructions | §10 (commit + push) |
| Status | v0.1 — ready for Pete to review + commit + push to `petr-yamyang/bouracka-tests` |

---

*SYNCHRO-MACBOOK-TO-OPUS-CP-SUPIN-06-2026-05-08.md — 2026-05-08 — MacBook CoWork session — Opus*
