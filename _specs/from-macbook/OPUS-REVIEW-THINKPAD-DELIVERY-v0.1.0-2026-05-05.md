# OPUS Review — ThinkPad CP-SUPIN-02 Delivery v0.1.0 — 2026-05-05
## Engineering review + corrections injection + TestPlan-as-live-execution-contract architecture

**Version:** v0.1.0
**Trigger:** ThinkPad task-force shipped two bundles 2026-05-05T16:24Z — `analytical-v0.1.0` (16 files, 720 KB) + `automation-v0.1.0` (72 files, 226 KB). Both received via uploads, SHA256 verified against PART-INDEX manifests.
**Audience:** the operator (Petr — to decide which corrections to apply when); the next ThinkPad Opus session (to apply the corrections injection in §6); MacBook Opus (to absorb the new vocabulary into the catalogue).
**Posture:** the delivery is *architecturally strong* — ThinkPad went further than the v0.1.1 brief in several places. This review preserves the strengths and surfaces the deltas vs catalogue v0.1.2 + the user's new "TestPlan as live execution contract" direction (2026-05-05).

---

## §1. Reading order for the operator

1. §2 — what the ThinkPad delivery is (one-page summary)
2. §3 — what's excellent (E1..E10 — preserve these on any rewrite)
3. §4 — gaps vs catalogue v0.1.2 (G1..G8 — schema-level deltas)
4. §5 — gaps vs new "TestPlan as live execution contract" direction (H1..H4 — the runtime architecture is missing)
5. §6 — TestPlan-as-live-contract architecture spec (new sheets + runtime resolution flow)
6. §7 — corrections injection (paste-ready prompt for next ThinkPad session)
7. §8 — what flows back to MacBook (catalogue + methodology + handover updates)
8. §9 — open questions returned to operator
9. §10 — status footer

---

## §2. What the ThinkPad delivery is

### §2.1 `analytical-v0.1.0-2026-05-05` — for SUPIN review

```
analytical-v0.1.0-2026-05-05/
├── 00_README-CS.md                    (placeholder; CP-SUPIN-03 fills)
├── 01_TESTPLAN-CS.md                  (placeholder)
├── 02_DIAGRAMY-AKTIVIT-CS.md          (placeholder; D00..D17 referenced)
├── 03_TESTCASE-LIST-CS.md             (placeholder; 20 R1 TCs catalogued)
├── 04_SLOVNIK-CS.md                   (placeholder)
├── 05_POKRYTI-CS.md                   (placeholder; coverage gap analysis)
├── BOURACKA-TESTPLAN-v0.1.xlsx        (12 sheets — see §3.6 for inspection)
├── MANIFEST-CS.md                     (file inventory)
└── diagrams/
    ├── tt-mindmap.{dot,pdf,png,svg}   (TestTarget mindmap, twopi layout)
    └── tc-mindmap.{dot,pdf,png,svg}   (TestCase mindmap, twopi layout)
```

**Status:** the seven CS narrative files are **placeholders** — they exist but await translation+content authoring in CP-SUPIN-03. The Excel + diagrams are real.

### §2.2 `automation-v0.1.0-2026-05-05` — for SecDev install on tester laptops

```
automation-v0.1.0-2026-05-05/
├── README-CS.md / README-EN.md       (tester operating manual)
├── INSTALL-CS.md                      (SecDev install guide)
├── MANIFEST-CS.md                     (package inventory)
├── package.json
├── BOURACKA-TESTPLAN-v0.1.xlsx        (same workbook as analytical bundle)
├── env/{tst,tst-demo,public}.json     (env configs)
├── fixtures/                          (codelists.yaml — 8 codelists; field-definitions.yaml — 121 fields; invalid-login.json)
├── playwright/                        (config + 3 page-objects + 3 spec files + reporter)
├── cypress/                           (config + 2 e2e tests + support)
├── testcafe/                          (one test file; gated)
├── scripts/                           (12 PowerShell scripts: setup-from-zero, run-all, run-{playwright,cypress,testcafe}, package-deliverable, validate-install, etc.)
├── tools/                             (build_mindmaps.py, heic-to-jpg.{ps1,sh})
├── _install/                          (SecDev install plans + ecosystem checklists + INTEGRATION-CONTRACTS contracts/)
├── _specs/                            (7 spec docs — see §3.4 for the headline ones)
└── specs/                             (7 per-TC SPEC.md files: TC-CP-001..004, 021..023 + _TC-TEMPLATE.md)
```

### §2.3 ThinkPad's session arc (per LESSONS-LEARNED-CP-SUPIN-02-v0.1.md)

- 6 revisions (rev 1 seed → rev 6 with full ecosystem).
- 26 deliverable files; 5 OQs raised, 5 OQs closed (so net 21 still open OQ-CP-NN per the lessons doc).
- 7 R1 TestTargets + 11 R2; 20 R1 TestCases.
- 121 fields catalogued (in `fixtures/field-definitions.yaml`).
- 6 mindmap renders (TT + TC; PNG / SVG / PDF).
- Full-ecosystem install plan + ~5 supporting docs.
- 22 lessons captured (§1 process + §2 architectural + §3 tooling + §4 communication + §5 domain).
- 8 anti-patterns avoided.

### §2.4 The headline architectural pivot

ThinkPad found out the SUT has **no login surface** — authentication is *implicit ID-registration* via OP/ŘP/SPZ → AISPOV (Czech registers). This invalidated the v0.1 scope §4.1 placeholder ("login happy / login failure") and drove a redesign mid-session. The 7 R1 TTs pivot around the `accidentReportStatus` state machine (`NEW / IN_PROGRESS_DRIVERS / IN_PROGRESS_VEHICLES / IN_PROGRESS_CIRCUMSTANCES / TO_SIGN / FINISHED / CANCEL / ERROR`). This is **canonical CAST decomposition**: state-machine-driven TestTarget split. Per L-ARCH-1: "for every SUT, find the canonical state machine first; let it drive the decomposition."

---

## §3. What's excellent — preserve on any rewrite

### §3.1 E1 — State-machine-driven TT decomposition (L-ARCH-1)

The pivot from "page / behaviour / component" decomposition to `state_machine_terminal_state` clusters is the textbook-correct CAST move once a state machine surfaces. The Excel column `state_machine_terminal_state` on `01_TestTargets` and `state_error_subreason` on `02_TestCases` honours this discovery in the schema.

**Action:** keep this column on TT + TC. Add a new sheet `01c_StateMachine` (per §6.5 below) to make the state diagram first-class.

### §3.2 E2 — Three install profiles (A / B / C)

Per LESSONS L-COMM-4 + L-TOOL-4: profile A (lean for colleagues running R1), B (standard QA), C (full lab). Each profile gets exactly one SecOps approval cycle. This kills the trap of overspeccing the colleague laptop. Captured in `_install/INSTALL-PLAN-FULL-ECOSYSTEM-v0.1.md` + one-page CHECKLIST.

**Action:** keep. Cross-link from CLIENT-PILOT-SUPIN AMENDMENT 4 §15.

### §3.3 E3 — Four integration strategies + hybrid recommendation

`_specs/INTEGRATION-CONTRACTS-STRATEGY-v0.1.md` is excellent: Strategy A (mock at network), B (vendor sandbox), C (synthetic + golden-master), D (SUT-side bypass). The hybrid recommendation per pyramid layer (`Layer 1..5`) is the right shape — and the per-TC class assignment table (TC-CP-001..020 mapped to Layer-4/5 strategy) is concrete enough to drive code.

**Action:** keep. Cross-reference from catalogue §2d (source-artefact derivation — integration spec rules become integration TestTarget rules per row 12 of the §2d.1 catalogue).

### §3.4 E4 — TC-spec format v0.1 (TESTCASE-SPEC-FORMAT-v0.1.md)

14 sections in fixed order; YAML status block; reference index pointing at TT/FLW/INT/SCR/KB/DIV; pre-conditions split boolean vs setup; test-data via fixture-refs (never inlined); integration touchpoints with posture per env; step list with R-CAST-2 typing + selectors + expected per step; AC traceability; viewport applicability matrix; R-FAIL-1 pair declaration; code-emission hints; validation checklist (§7) at the end. **This format is keeper-grade.**

**Action:** keep. Add 2 new sections per §6 below (FURPS+ tagging + CAST CO/KDO/KDY/KDE/JAK on TT) and 1 new validation rule.

### §3.5 E5 — TestTarget format v0.1 (TESTTARGET-LIST-FORMAT-v0.1.md)

ID convention `TT-CP-RN-MMM` honours R-STRUCT-1 (release-prefix; promotion never re-numbers; deprecation explicit). ItemBase block + R-CAST-1 fields + linkage refs + promotion rules. Validation checklist.

**Action:** keep. Extend per §6 below.

### §3.6 E6 — Excel as catalogue, MD as dev-input — two-layer model

Excel `02_TestCases.dev_spec_path` column points at `specs/TC-CP-NNN-SPEC.md`. Excel summary; MD detail. Both versioned together. The TC-spec format §1 explicitly says "Excel row = summary. MD spec = dev-session input."

**Action:** keep this two-layer model. **Promote** to three-layer per §6 below: Excel registry + MD spec + new Excel sheets `02b_TC_Parameters` + `02c_TC_Assertions` + `02d_AssertionLibrary` (the parameter+assertion grain Excel can't carry as MD prose).

### §3.7 E7 — R-CAST-2 step typing in actual test code

`playwright/tests/login.spec.ts` lines 23, 30, 32, 41, 47, 49, 53, 56 etc. have inline comments `// STEP N — kind: ...` for every step. The kind appears next to the step verb in the same line block. Cypress + TestCafe code mirrors. **Codifies the CAST point taxonomy in execution code** — this is the discipline most easily lost in real coding.

**Action:** keep. Make it a binding rule (R-CAST-2 already exists; this is the proof it's livable in code).

### §3.8 E8 — Bilingual CS+EN throughout (with CS primary)

Every TT / TC / Bug row has `item_name_cs / item_name_en` + `item_descr_cs / item_descr_en`. SPEC.md has `title_cs / title_en` per step. README CS first, EN mirror. Glossary CS column first. Per L-COMM-3: "Czech-first content for tester-facing material."

**Action:** keep. This is exactly what catalogue v0.1.1 §0 + §10 demanded, applied consistently.

### §3.9 E9 — Complete framework code skeleton

Three frameworks (Playwright + Cypress + TestCafe). Page-object pattern for Playwright (`BasePage`, `LandingPage`, `WizardGatewayPage`). Custom Excel reporter (`reporters/excel-row-writer.ts`). Bring-up smoke test. Env config per env. Fixtures separated. PowerShell launchers.

**Action:** keep. Extend per §6 with a runtime spec-loader module (the new live-contract architecture).

### §3.10 E10 — Lessons-learned doc as project memory

22 lessons across process / arch / tooling / communication / domain. 8 anti-patterns avoided. 8 next-session items. **This is exactly the discipline KB-LESSONS-LEARNED.yaml in the parent project follows** — and it should feed back into the parent KB.

**Action:** absorb the lessons into MacBook's `_config/KB-LESSONS-LEARNED.yaml` under entries `LL-CP-SUPIN-01..22`. Not optional — the parent project KB is the place these durable insights belong.

---

## §4. Gaps vs catalogue v0.1.2 (schema-level deltas — additive corrections)

Each gap below has: identifier · binding rule violated · concrete correction · column/sheet name · estimated effort.

### §4.1 G1 — No FURPS+ tagging anywhere (R-FURPS-1 violation)

**Where:** `01_TestTargets`, `02_TestCases`, future `00b_Requirements` all lack a `furps_dimensions` column.
**Why it matters:** without FURPS+ tagging, the Cartesian Requirement × FURPS+ governance (catalogue §2f) cannot run; the test base cannot be reasoned about by quality dimension.
**Correction:**
- Add column `furps_dimensions VARCHAR(40)` on `01_TestTargets`, `02_TestCases`, future `00b_Requirements`. Value = comma-separated subset of `{F,U,R,P,S,+D,+I,+N,+L,+P_phys}`.
- Update `00_README` legend (sheet header) to document the FURPS+ map per catalogue §2e.1.
- Update `_specs/TESTCASE-SPEC-FORMAT-v0.1.md` to require `furps_dimensions: [F, U]` in the YAML status block.
- Update `_specs/TESTTARGET-LIST-FORMAT-v0.1.md` likewise.
**Effort:** 1 ThinkPad session.

### §4.2 G2 — No Requirements sheet (R-DERIVE-1 partial violation)

**Where:** there is no `00b_Requirements` sheet. TTs derive directly from analytical doc artefacts (state machine + screen catalogue) without an intermediate Requirements layer.
**Why it matters:** the CAST 6-element chain `Stakeholder → Requirement → TestTarget → TestCase → TestRun → EvidenceResult` is broken at link 2. Without Requirements, you cannot do Cartesian Req × FURPS+ (the whole §2f machine), and you cannot do bidirectional traceability "for REQ-NNN, what TTs / TCs cover it?"
**Correction:**
- Add new sheet `00b_Requirements` (between `00_README` and `01_TestTargets`):

  | Column | Notes |
  |---|---|
  | id, item_code (REQ-CP-NNN), item_name_cs/en, item_descr_cs/en, item_type='requirement', item_status, severity, urgency, priority (computed) | ItemBase |
  | source_artefact_kind, source_artefact_ref, derivation_rule, source_artefact_author_role | per catalogue §2d.2 |
  | requirement_kind | functional / nfr / regulatory / business |
  | furps_dimensions | per §2e |
  | accept_criteria_md_ref | path to `requirements/REQ-CP-NNN-AC.md` for non-trivial AC |
  | impulse_ref | per R-IMPULSE-1 |
  | created_at, updated_at, notes | ItemBase tail |

- Add column `requirement_ref` on `01_TestTargets` (each TT links to ≥ 1 REQ).
- Seed Requirements from the analytical doc: each state-machine state + each gateway decision + each integration becomes 1 REQ. ~20 REQ-CP-NNN entries from R1 scope.
**Effort:** 1.5 ThinkPad sessions (1 to author the sheet structure + seed; 0.5 to retrofit the link from existing 7 R1 TTs).

### §4.3 G3 — No CAST CO/KDO/KDY/KDE/JAK matrix on TestTargets (R-CAST-3 violation)

**Where:** `01_TestTargets` has `decomposition_kind` (partially serves WHAT) but no explicit columns for CO / KDO / KDY / KDE / JAK.
**Why it matters:** R-CAST-3 binding from catalogue §2b.2. The CO/KDO/KDY/KDE/JAK matrix is the original-author 5-question decomposition; categorising every TT against it forces the analyst to think through who/when/where/how — surfaces gaps early.
**Correction:**
- Add 5 columns on `01_TestTargets`: `co_what`, `kdo_who`, `kdy_when`, `kde_where`, `jak_how`. Each a short phrase.
- Update `_specs/TESTTARGET-LIST-FORMAT-v0.1.md` §3 to include them as required.
- Update validation checklist §6.
**Effort:** 0.5 session.

### §4.4 G4 — No `impulse_ref` column anywhere (R-IMPULSE-1 violation)

**Where:** `02_TestCases` and `08_Bugs` lack `impulse_ref`. The `notes` column carries free-form reasoning but doesn't enforce the "registered impulse" discipline.
**Why it matters:** R-IMPULSE-1 binding. CAST principle "podnět" — every TC + Bug must cite a registered impulse, never a "feeling". Closes the "tester invents tests" failure mode.
**Correction:**
- Add column `impulse_ref` on `02_TestCases`, `08_Bugs`, `00b_Requirements` (when added per G2). Value = recon material ID (`SCR-NNN` / `FLW-NNN` / `INT-NNN`) OR analytical-doc-page-ref OR user-direction-date OR upstream-bug-ref.
- Validation: every row's `impulse_ref` must resolve to a real reference.
**Effort:** 0.5 session.

### §4.5 G5 — No `diligence` column on Bugs (R-DILIGENCE-1 violation)

**Where:** `08_Bugs` carries `severity` + `urgency` + `priority` (the Sev × Urg → Pri matrix) but not Diligence (CAST 3rd dim per catalogue §2c.5).
**Why it matters:** Diligence is the *care/attention* dimension separate from impact (Sev) and timing (Urg). E.g. a bug in legal-compliance text needs HIGH diligence (pedantic correction) but may be LOW severity + LOW urgency.
**Correction:**
- Add column `diligence CHAR(1)` on `08_Bugs` (and on `02_TestCases` for assertion-strictness control). Values per catalogue §3.2: `P` pedantic / `S` standard / `I` informal.
- Update `00_README` legend to document.
- Optional: pre-compute a "weighted priority" `priority_diligent = priority shifted by diligence` (Pri-A × P → A; Pri-A × I → B-).
**Effort:** 0.5 session.

### §4.6 G6 — No Plan/Schedule/Estimate split in 05_TestSets (R-PLAN-1 violation)

**Where:** `05_TestSets` collapses three concepts (the *what+why* + the *when* + the *how-much-effort*) into one row.
**Why it matters:** R-PLAN-1 binding. Plan ≠ Schedule ≠ Estimate (per catalogue §2c.2 / Vaněk Test Management canon).
**Correction:**
- Split `05_TestSets` into:
  - `05a_TestPlan` (decision: which TCs in scope; rationale; sequence)
  - `05b_TestSchedule` (calendar projection: dates per TC; slack; dependencies)
  - `05c_TestEstimate` (effort projection: hours per TC; risk factor; confidence)
- Each carries the same `iteration_label` (the join key) so a single iteration is reconstructed by joining all three.
- Migrate the existing `TS-CP-WK1` row into `05a_TestPlan` first; populate `05b_TestSchedule` from the existing `date_range`; seed `05c_TestEstimate` empty for ThinkPad to fill.
**Effort:** 1 session.

### §4.7 G7 — No Cartesian (Req × FURPS+) sheet (catalogue §2f.4 missing implementation)

**Where:** the entire `requirement_furps_cells` concept (catalogue §2f.1–§2f.5) has no Excel realisation.
**Why it matters:** without it, test base growth is *undifferentiated* (every TC just gets added) — there's no expansion-pressure metric, no dimension-neglect signal.
**Correction:**
- Add new sheet `01b_Req_FURPS_Cartesian` with columns matching catalogue §2f.4 DDL:

  | Column | Notes |
  |---|---|
  | id, requirement_ref (REQ-CP-NNN), furps_dimension (F/U/R/P/S/+D/+I/+N/+L/+P_phys), cell_status (na/pending/active/deferred), na_justification, test_case_set_ref (TS-CP-NNN), severity, urgency, priority (computed), scheduling_unit_kind (sprint/phase/iteration), scheduling_unit_ref, defer_reason, defer_until_iteration | per §2f.4 |
  | created_at, updated_at, notes | ItemBase tail |

- Add a unique-key (`requirement_ref`, `furps_dimension`) — at most one cell per pairing.
- Pre-seed: for each REQ, create one row per FURPS+ dimension; ThinkPad marks N/A or active per analytical doc evidence.
- The `09_Reports` sheet gets a new pivot view `Coverage matrix` (REQ × FURPS+ → cell colour-coded per §2f.5).
**Effort:** 1.5 sessions (sheet structure + seeding + reporting view).

### §4.8 G8 — No source-artefact derivation columns on TTs (R-DERIVE-1 partial)

**Where:** `01_TestTargets` has `related_screen_refs / related_flow_refs / related_integration_refs` (the linkage-refs partially serve), but no explicit `source_artefact_kind` / `source_artefact_ref` / `derivation_rule` / `source_artefact_author_role` per catalogue §2d.2.
**Why it matters:** R-DERIVE-1 binding. The reverse traceability (catalogue §2d.3) needs an explicit kind+ref to roll up "for UC-CP-007, what TTs derive from it?" The existing related-refs are a star-graph; a single TT may link multiple recon docs without naming WHICH artefact is the *primary* derivation source.
**Correction:**
- Add 4 columns on `01_TestTargets` per catalogue §2d.2: `source_artefact_kind` (enum from §2d.1), `source_artefact_ref`, `derivation_rule`, `source_artefact_author_role`.
- Keep `related_*` linkage columns (they remain the *secondary* refs).
- Update `_specs/TESTTARGET-LIST-FORMAT-v0.1.md` §3 + validation checklist.
**Effort:** 0.5 session.

---

## §5. Gaps vs new "TestPlan as live execution contract" direction (2026-05-05)

The user's direction: *"TestPlan document will serve as an analytical and planning/reporting base for automated tests. This must be implemented in detail including mechanism how to select test data and parameters/assetions for each automated test implemented/run on the developing automation solution for Bouračka and beyond."*

### §5.1 H1 — Excel doesn't carry runtime parameters/assertions

**Where:** parameters + assertions live only in MD specs (`specs/TC-CP-NNN-SPEC.md` §3.5–§3.7); framework code (`playwright/tests/login.spec.ts`) hand-codes them. The Excel `02_TestCases` row carries only `steps_summary = "see SPEC.md"` and `expected_summary = "see SPEC.md"`.
**Why it matters:** the user wants Excel to *drive* test data + parameter + assertion selection — i.e. framework code reads Excel at runtime, not just writes results into it. Today Excel is read-only documentation.
**Correction:** see §6 — new sheets `02b_TC_Parameters`, `02c_TC_Assertions`, `02d_AssertionLibrary` + runtime spec-loader module.

### §5.2 H2 — No assertion library

**Where:** every SPEC hand-authors its assertions (e.g. TC-CP-001 §AC-3 "exactly 1 POST to `/api/registry/driver-lookup`; response.body.first_name + last_name + dob match fixture exactly"). No reusable patterns.
**Why it matters:** without an assertion library, every new TC re-invents assertions; FURPS+ tagging on assertions becomes hand-tagged not derived; reporting can't summarise "% of perf assertions failing this iteration".
**Correction:** new sheet `02d_AssertionLibrary` (see §6.3) — catalogue of reusable assertion patterns by FURPS+ dimension; each TC's assertions reference library entries by `item_code`.

### §5.3 H3 — No data-selection mechanism

**Where:** fixtures referenced via `payload_ref` in `03_TestData` (e.g. `fixtures/shared/test-drivers.json`) but no parameter-resolution sheet — i.e. how does TC-CP-001 know to pick `tester_jeden` vs `tester_dva`? Currently hard-coded in the SPEC.
**Why it matters:** for parametric / data-driven testing (one TC × N data variants), Excel must mediate. Especially relevant for FURPS+ — a Performance variant of TC-CP-001 might need a 100-driver dataset; a Reliability variant might need an unreliable-network fixture.
**Correction:** new sheet `02b_TC_Parameters` (see §6.1) — explicit parameter-resolution layer between TC and TestData.

### §5.4 H4 — No FURPS+ → assertion-pattern mapping

**Where:** assertions are authored ad-hoc per SPEC; there's no policy "for every Performance-tagged TC, the assertion set MUST include a response-time assertion under N ms".
**Why it matters:** FURPS+ becomes a tag without meaning if no assertion-pattern policy is wired to it. The Cartesian (Req × FURPS+) governance per §2f produces TC-set candidates but doesn't specify what those TCs *test*.
**Correction:** the new `02d_AssertionLibrary` sheet has a `furps_dimension` column on every entry; the `02c_TC_Assertions` sheet links a TC to its required assertions, and a validator script (Python; runs at workbook save) enforces "for every TC tagged FURPS=P, at least one linked assertion must have furps_dimension=P". See §6.4.

---

## §6. TestPlan-as-live-execution-contract — architecture spec

This is the new architectural layer the user's direction demands. Three new sheets + one runtime module + one validator.

### §6.1 New sheet `02b_TC_Parameters` — per-TC parameter resolution

| Column | Type | Notes |
|---|---|---|
| id | INT | PK |
| item_code | VARCHAR(40) | `TCP-CP-NNN-P-MM` (parameter MM of TC NNN) |
| test_case_ref | VARCHAR(40) | FK → 02_TestCases.item_code |
| parameter_name | VARCHAR(80) | e.g. `primary_driver`, `viewport`, `expected_ocr_outcome` |
| parameter_kind | VARCHAR(20) | `fixture_ref` / `enum_value` / `range` / `derived` / `env_config` |
| parameter_source | VARCHAR(255) | depends on kind: fixture_ref → `03_TestData.item_code`; enum_value → literal value; range → `min:max:step`; derived → expression; env_config → `env.<key>` |
| variant_label | VARCHAR(40) | `default`, `mobile-320`, `perf-100users`, `unreliable-network`; defines the parametric variant of the same TC |
| furps_dimension | VARCHAR(8) | which FURPS+ dimension this variant exercises (defaults to TC's primary) |
| required | BOOL | true = required for the variant; false = optional override |
| created_at, updated_at, notes | ItemBase tail |

**Usage:** TC-CP-001 has parameters `primary_driver` (variant=default → TD-CP-002; variant=alternate → TD-CP-002b), `viewport` (variant=desktop → 1280×720; variant=mobile-320 → 320×568), etc. Framework code at runtime: query `02b_TC_Parameters WHERE test_case_ref = 'TC-CP-001' AND variant_label = 'default'` → get all parameter rows → resolve each by `parameter_kind` + `parameter_source`.

### §6.2 New sheet `02c_TC_Assertions` — per-TC assertion linkage

| Column | Type | Notes |
|---|---|---|
| id | INT | PK |
| item_code | VARCHAR(40) | `AS-CP-NNN-MM` |
| test_case_ref | VARCHAR(40) | FK → 02_TestCases.item_code |
| step_ref | VARCHAR(40) | which TC step this assertion attaches to (e.g. `TC-CP-001-S-09`) |
| assertion_library_ref | VARCHAR(40) | FK → 02d_AssertionLibrary.item_code |
| assertion_args | TEXT | JSON: `{"expected": "...", "tolerance_ms": 200, "timeout_ms": 10000}` (kind-specific) |
| furps_dimension | VARCHAR(8) | derived from library_ref by default; can be overridden |
| severity | CHAR(1) | per assertion (e.g. perf assertion may be HIGH sev even if TC overall is MED) |
| variant_label | VARCHAR(40) | which variant this assertion applies to (default = all variants) |
| created_at, updated_at, notes | ItemBase tail |

### §6.3 New sheet `02d_AssertionLibrary` — reusable assertion patterns

| Column | Type | Notes |
|---|---|---|
| id | INT | PK |
| item_code | VARCHAR(40) | `LIB-AS-NNN` |
| item_name_cs / en | VARCHAR(200) | e.g. CS: "Doba odezvy pod N ms" / EN: "Response time below N ms" |
| furps_dimension | VARCHAR(8) | which FURPS+ this pattern verifies |
| pattern_kind | VARCHAR(40) | `network-call-count` / `network-response-time` / `dom-text-match` / `dom-attribute-match` / `dom-bbox-min` / `network-status-class` / `localStorage-empty` / `accessible-name-present` / `wcag-target-size-44` / `email-poll-zero` / etc. |
| pattern_args_schema | TEXT | JSON-schema describing `assertion_args` shape this pattern expects |
| pattern_impl_playwright | TEXT | code snippet (Playwright-flavoured) the runtime substitutes |
| pattern_impl_cypress | TEXT | code snippet (Cypress-flavoured) |
| pattern_impl_testcafe | TEXT | code snippet |
| failure_message_template_cs / en | TEXT | i18n failure message |
| created_at, updated_at, notes | ItemBase tail |

Seed with 15–25 entries covering the assertion patterns already in the existing 7 SPECs.

### §6.4 New sheet `01c_StateMachine` — state machine catalogue (per L-ARCH-1)

| Column | Type | Notes |
|---|---|---|
| id | INT | PK |
| item_code | VARCHAR(40) | `SM-CP-NNN` (e.g. `SM-CP-001` = `accidentReportStatus`) |
| state_machine_name | VARCHAR(80) | `accidentReportStatus` |
| state_code | VARCHAR(40) | `NEW`, `IN_PROGRESS_DRIVERS`, `TO_SIGN`, `FINISHED`, `ERROR`, etc. |
| state_label_cs / en | VARCHAR(200) | human-readable |
| transition_from | VARCHAR(40) | source state for an inbound transition |
| transition_event | VARCHAR(80) | the event/action that fires the transition |
| transition_guard | TEXT | guard condition |
| transition_to | VARCHAR(40) | this row's `state_code` typically |
| terminal | BOOL | true if this is a terminal/leaf state |
| sub_reason | VARCHAR(80) | for ERROR-type states, the sub-reason taxonomy |
| related_tt_refs | VARCHAR(200) | comma-list of TTs that exercise this state/transition |

**Why:** L-ARCH-1 said "let the state machine drive decomposition." Surface it in the workbook, not just in `state_machine_terminal_state` text columns.

### §6.5 Runtime module `playwright/runtime/spec-loader.ts` (NEW)

**Purpose:** the bridge between Excel-as-contract and framework execution.

```typescript
// Pseudo-spec — ThinkPad implements the actual code
import * as XLSX from 'xlsx';

export interface ResolvedTestCase {
  itemCode: string;          // TC-CP-NNN
  variant: string;           // 'default' | 'mobile-320' | ...
  parameters: Record<string, any>;        // resolved per row of 02b
  assertions: ResolvedAssertion[];        // resolved per row of 02c × 02d
  preConditions: string[];   // from 02_TestCases.preconditions
  postConditions: string[];  // from 02_TestCases.postconditions
  furpsDimensions: string[]; // from 02_TestCases.furps_dimensions
  envCoverage: string[];     // from 02_TestCases.env_coverage
  viewports: number[];       // from 02_TestCases.viewport_spec
  diligence: 'P' | 'S' | 'I';
  stateMachineTerminal: string;
  devSpecPath: string;       // human-readable companion (specs/TC-CP-NNN-SPEC.md)
}

export interface ResolvedAssertion {
  itemCode: string;          // AS-CP-NNN-MM
  stepRef: string;
  patternKind: string;       // from 02d.pattern_kind
  args: Record<string, any>; // from 02c.assertion_args
  furpsDimension: string;
  severity: string;
  failureMessage: string;    // localised per env.locale
  impl: string;              // pattern_impl_playwright code snippet
}

export function loadTestCase(workbookPath: string, itemCode: string, variant: string = 'default', envLabel: string): ResolvedTestCase {
  const wb = XLSX.readFile(workbookPath);
  // 1. Find row in 02_TestCases by item_code
  // 2. Resolve parameters from 02b_TC_Parameters where test_case_ref = itemCode AND variant_label IN (variant, 'default-fallback')
  // 3. Resolve each parameter by kind:
  //    fixture_ref → load from 03_TestData → load JSON from payload_ref
  //    enum_value → use literal
  //    env_config → look up env[envLabel].<key>
  //    derived → eval expression (sandboxed)
  //    range → expand
  // 4. Resolve assertions from 02c_TC_Assertions where test_case_ref = itemCode
  //    For each, look up 02d_AssertionLibrary by assertion_library_ref to get pattern_impl
  // 5. Compose ResolvedTestCase + return
}

export function emitPlaywrightTest(rtc: ResolvedTestCase): string {
  // Generate test code from ResolvedTestCase:
  //   describe(rtc.itemCode, ...) { test(rtc.title, async () => { ... }) }
  //   wire pre-conditions, parameters, assertions
  // Used in a code-generation step OR called dynamically from a parametric test runner
}
```

**Two integration patterns:**
1. **Code-generation:** at test-build time, iterate `02_TestCases`, call `emitPlaywrightTest()`, write `playwright/tests/generated/TC-CP-NNN.spec.ts`. Generated tests are committed (the human can read them). Pro: standard test-runner discovery; Con: generated code in repo.
2. **Dynamic parametric runner:** one Playwright file `playwright/tests/spec-driven.spec.ts` reads the workbook at runtime, spawns one `test()` per TC × variant via Playwright's parametric `test.describe.configure()`. Pro: single-source workbook drives execution; Con: less obvious in IDE.

Recommended: **start with code-generation** (lower risk; clearer debugging) and add the dynamic runner once the workbook contract is stable.

### §6.6 Validator script `tools/validate-workbook.py` (NEW)

Runs at workbook-save (or pre-commit). Checks:

| Check | Reason |
|---|---|
| Every TT has `furps_dimensions`, `co_what`, `kdo_who`, `kdy_when`, `kde_where`, `jak_how`, `source_artefact_kind`, `source_artefact_ref`, `derivation_rule`, `requirement_ref` populated | G1 + G3 + G8 + G2 |
| Every TC has `furps_dimensions`, `impulse_ref` populated | G1 + G4 |
| Every TC tagged FURPS=P has ≥ 1 row in `02c_TC_Assertions` whose `02d_AssertionLibrary.furps_dimension = P` | H4 |
| Every Bug has `diligence` + `impulse_ref` populated | G5 + G4 |
| Every `01b_Req_FURPS_Cartesian` cell with `cell_status='na'` has non-empty `na_justification` | catalogue §2f.5 justification audit |
| Every `01b_Req_FURPS_Cartesian` cell pairing (`requirement_ref`, `furps_dimension`) is unique | catalogue §2f.4 unique index |
| Every `02b_TC_Parameters.parameter_source` of kind `fixture_ref` resolves to a real `03_TestData.item_code` | dangling-ref catch |
| Every `02c_TC_Assertions.assertion_library_ref` resolves to a real `02d_AssertionLibrary.item_code` | dangling-ref catch |
| Every `01_TestTargets.requirement_ref` resolves to a real `00b_Requirements.item_code` | dangling-ref catch |
| Every TC's `test_target_ref` resolves to a real `01_TestTargets.item_code` | dangling-ref catch |

Output: green = workbook ready for test execution; red = list of failed checks with row refs.

### §6.7 Updated workbook structure (final v0.2 layout)

```
00_README                  unchanged + extended legend (FURPS+, Diligence, CO/KDO/KDY/KDE/JAK)
00b_Requirements           NEW — per G2
01_TestTargets             extend with FURPS+ + CO/KDO/KDY/KDE/JAK + source_artefact_* + requirement_ref columns
01b_Req_FURPS_Cartesian    NEW — per G7
01c_StateMachine           NEW — per §6.4 (L-ARCH-1)
02_TestCases               extend with FURPS+ + impulse_ref + diligence columns
02b_TC_Parameters          NEW — per §6.1
02c_TC_Assertions          NEW — per §6.2
02d_AssertionLibrary       NEW — per §6.3
03_TestData                unchanged (already structured)
04_TestEnvironments        unchanged
05a_TestPlan               NEW (split per G6)
05b_TestSchedule           NEW (split per G6)
05c_TestEstimate           NEW (split per G6)
06_TestRuns                unchanged
07_TestRunResults          extend with `assertion_ref` + `furps_dimension_failed` columns (so a failed run records WHICH assertion / dimension)
08_Bugs                    extend with diligence + impulse_ref columns
09_Reports                 extend with FURPS+ coverage matrix view + expansion-pressure histogram + dimension-neglect signal (per catalogue §2f.5)
10_Glossary                already 63 rows — keep; add the new vocabulary terms (Diligence, CO/KDO/KDY/KDE/JAK, FURPS+) if not present
11_Changelog               unchanged + log v0.2 schema migration entry
```

Migration scripts — same Python pattern ThinkPad already uses (per L-PROC-5 lesson) — apply schema diffs to the existing v0.1 workbook to produce v0.2 without losing any existing rows.

---

## §7. Corrections injection — paste-ready prompt for next ThinkPad session

```
═══════════════════════ BEGIN PROMPT ════════════════════════════════════════
You are continuing the ThinkPad SUPIN/bouracka client-pilot campaign
under iteration CP-SUPIN-03. Inputs delivered to operator
2026-05-05T16:24Z (analytical-v0.1.0 + automation-v0.1.0) have been
reviewed by MacBook Opus. Review verdict: architecturally strong
(E1..E10 preserved); 12 schema-level + runtime-architecture gaps
(G1..G8 + H1..H4) require correction.

This iteration applies the corrections per Opus review doc
`_config/OPUS-REVIEW-THINKPAD-DELIVERY-v0.1.0-2026-05-05.md` §6 + §7.

═════════════════════════════════════════════════════════════════════════════
STEP 0 — ENVIRONMENT
═════════════════════════════════════════════════════════════════════════════
git checkout thinkpad
git pull --ff-only origin thinkpad        # bring in any operator edits
ls _config/OPUS-REVIEW-THINKPAD-DELIVERY-v0.1.0-2026-05-05.md

═════════════════════════════════════════════════════════════════════════════
STEP 1 — REQUIRED READING (this iteration)
═════════════════════════════════════════════════════════════════════════════
1. _config/OPUS-REVIEW-THINKPAD-DELIVERY-v0.1.0-2026-05-05.md
   (FULL READ — your scope for this iteration)
2. _config/VOCABULARY-CATALOGUE-CS-EN-V0.1.md  v0.1.2
   (skim §2d source-artefact derivation, §2e FURPS+, §2f Cartesian
    governance, §4.4 planning attribution — these are the conceptual
    foundations of what you're about to implement)
3. _specs/LESSONS-LEARNED-CP-SUPIN-02-v0.1.md
   (your own session memory — re-read §3 tooling lessons before
    touching the build scripts)

═════════════════════════════════════════════════════════════════════════════
STEP 2 — WORKBOOK SCHEMA UPGRADE v0.1 → v0.2
═════════════════════════════════════════════════════════════════════════════
Goal: BOURACKA-TESTPLAN-v0.1.xlsx → BOURACKA-TESTPLAN-v0.2.xlsx with
all 12 gaps closed.

  2.1  Author migration script outputs/migrate_v01_to_v02_xlsx.py
       per L-PROC-5 (script-driven; never hand-edit). Implements §6.7
       sheet additions + column extensions per G1..G8 + H1..H3.

  2.2  Sheets to ADD (5 NEW):
       - 00b_Requirements          (G2 — REQ-CP-NNN catalogue)
       - 01b_Req_FURPS_Cartesian   (G7 — Cartesian governance)
       - 01c_StateMachine          (L-ARCH-1 surfaced)
       - 02b_TC_Parameters         (H1+H3 — runtime parameters)
       - 02c_TC_Assertions         (H1+H2 — per-TC assertion linkage)
       - 02d_AssertionLibrary      (H2+H4 — reusable assertion patterns)
       - 05a_TestPlan + 05b_TestSchedule + 05c_TestEstimate
                                  (G6 — split 05_TestSets)

  2.3  Columns to ADD on existing sheets:
       - 01_TestTargets:    + furps_dimensions (G1)
                            + co_what, kdo_who, kdy_when, kde_where,
                              jak_how (G3)
                            + source_artefact_kind, source_artefact_ref,
                              derivation_rule,
                              source_artefact_author_role (G8)
                            + requirement_ref (G2 link)
       - 02_TestCases:      + furps_dimensions (G1)
                            + impulse_ref (G4)
                            + diligence (G5)
       - 07_TestRunResults: + assertion_ref + furps_dimension_failed
       - 08_Bugs:           + diligence (G5) + impulse_ref (G4)

  2.4  Seed the new sheets:
       - 00b_Requirements: derive ~20 REQ-CP-NNN entries from analytical
         doc — one per state-machine state + per gateway decision +
         per integration touchpoint. Each tagged with applicable FURPS+
         dimension(s).
       - 01b_Req_FURPS_Cartesian: for each REQ × each FURPS+ dimension,
         insert one row with cell_status = 'pending' (or 'na' with
         justification if dimension demonstrably doesn't apply).
       - 01c_StateMachine: encode `accidentReportStatus` as ~8 state
         rows + ~12 transition rows.
       - 02b_TC_Parameters: for each existing 7 R1 TCs, extract the
         hard-coded parameters from SPEC §3.5 + §3.7 into rows.
       - 02d_AssertionLibrary: extract ~15–20 assertion patterns from
         existing SPECs. Tag each by FURPS+ dimension. Author the
         playwright/cypress impl snippets per pattern.
       - 02c_TC_Assertions: for each existing 7 R1 TCs, link each
         AC + each step's assertion to a 02d entry.

  2.5  Update READMEs (00_README sheet + analytical/00_README-CS.md +
       automation/MANIFEST-CS.md) to document the new sheets + columns.

═════════════════════════════════════════════════════════════════════════════
STEP 3 — UPDATE THE TWO FORMAT SPECS
═════════════════════════════════════════════════════════════════════════════
  3.1  _specs/TESTTARGET-LIST-FORMAT-v0.2.md
       (bump version; add G1+G3+G8+G2 fields to §3 required list +
        validation checklist §6)

  3.2  _specs/TESTCASE-SPEC-FORMAT-v0.2.md
       (bump version; add furps_dimensions to YAML status block §3.2;
        add NEW §3.15 "Parameters reference" pointing to 02b rows;
        add NEW §3.16 "Assertion library refs" pointing to 02c rows;
        update validation checklist §7)

═════════════════════════════════════════════════════════════════════════════
STEP 4 — IMPLEMENT THE RUNTIME SPEC-LOADER
═════════════════════════════════════════════════════════════════════════════
  4.1  playwright/runtime/spec-loader.ts (NEW)
       per Opus review §6.5. TypeScript module that:
       - reads BOURACKA-TESTPLAN-v0.2.xlsx via SheetJS
       - resolves parameters per 02b
       - resolves assertions per 02c × 02d
       - returns ResolvedTestCase

  4.2  scripts/generate-tests.ps1 (NEW) + tools/generate_tests.py (NEW)
       Code-gen step (§6.5 pattern 1 — start here, not the dynamic
       runner). Iterates 02_TestCases, calls spec-loader, emits
       playwright/tests/generated/TC-CP-NNN.spec.ts.

  4.3  Validate: regenerate the existing 7 R1 TCs from the workbook;
       diff vs hand-coded; the generated code should produce identical
       behaviour (the hand-coded ones are reference-correct per Opus E7).

═════════════════════════════════════════════════════════════════════════════
STEP 5 — IMPLEMENT THE WORKBOOK VALIDATOR
═════════════════════════════════════════════════════════════════════════════
  5.1  tools/validate-workbook.py (NEW)
       per Opus review §6.6. All 10 checks. Run before every workbook
       commit; CI check.

  5.2  scripts/validate-workbook.ps1 wrapper.

  5.3  Run against current v0.2 workbook → all checks green; if any
       red, fix data first.

═════════════════════════════════════════════════════════════════════════════
STEP 6 — REGENERATE DELIVERY BUNDLES
═════════════════════════════════════════════════════════════════════════════
  6.1  Author scripts/package-delivery-analytical-v0.2.0.ps1 (replace
       v0.1.0 packager).

  6.2  Author scripts/package-delivery-automation-v0.2.0.ps1.

  6.3  Pack v0.2 deliverables; SHA256; PART-INDEX.

  6.4  Email to operator (Petr) — same channel as v0.1.0.

═════════════════════════════════════════════════════════════════════════════
STEP 7 — CLOSE THE LOOP
═════════════════════════════════════════════════════════════════════════════
  7.1  Update _specs/LESSONS-LEARNED-CP-SUPIN-02-v0.1.md → v0.2 with
       any new lessons from this iteration.

  7.2  Commit + push thinkpad branch with all the above:
       - migration script + new workbook
       - both updated FORMAT specs
       - spec-loader + generator + validator
       - regenerated delivery bundles
       - updated lessons learned

  7.3  In SESSION-NOTES.md under heading "CP-SUPIN-03 — schema
       upgrade + runtime contract" log:
       - which gaps closed (cite G/H IDs)
       - which gaps deferred + why
       - new OQs raised (file as OQ-CP-27..NN)
       - validator green/red state
       - next-iteration items

═════════════════════════════════════════════════════════════════════════════
RULES (binding from now — see Opus review §6 for derivations)
═════════════════════════════════════════════════════════════════════════════
R-METH-1..4 + R-STRUCT-1..2 + R-CAST-1..3 + R-VOC-1 + R-IMPULSE-1 +
R-PLAN-1 + R-DILIGENCE-1 + R-FAIL-1 + Mobile-first + Czech first
   (already binding from v0.1.1 archive)

R-DERIVE-1   NEW — every TestTarget derives from a registered
               analytical artefact (UC/BPM/SD/AD/screen/API/etc.);
               source_artefact_kind + ref + derivation_rule columns
               mandatory on 01_TestTargets.
R-FURPS-1    NEW — every Requirement and TestTarget and TestCase
               carries furps_dimensions; the Cartesian sheet
               01b_Req_FURPS_Cartesian governs test-base expansion.
R-EXPAND-1   NEW — every Cartesian cell becoming a TC-set carries
               severity + urgency tags; Pri = D cells defer with timer.
R-PLAN-2     NEW — requirement_furps_cells.scheduling_unit_kind MUST
               match projects.methodology setting (validator enforced).
R-CONTRACT-1 NEW — workbook IS the live execution contract; runtime
               spec-loader resolves parameters + assertions from Excel
               sheets; SPEC.md narrative is human companion not
               source of truth for execution.

═════════════════════════════════════════════════════════════════════════════
WHEN TO BOUNCE BACK
═════════════════════════════════════════════════════════════════════════════
File OQ + STOP if any of:
  • Existing 7 R1 TCs cannot be code-generated equivalently from
    workbook + spec-loader (architectural hole — not a fix in this
    session)
  • Validator reports a check you cannot satisfy with available data
    (e.g. Requirements seed needs more analytical-doc pages)
  • Schema migration loses data on existing rows (hard stop — never
    delete; per R-STRUCT-1 use deprecate-and-add pattern)
  • Time-budget signal: this iteration is large; if at session
    boundary you have completed STEPs 2+3 only, push that, defer
    STEPs 4+5+6 to CP-SUPIN-04.

═════════════════════════════════════════════════════════════════════════════
BEGIN — STEP 0 NOW
═════════════════════════════════════════════════════════════════════════════
═══════════════════════ END PROMPT ══════════════════════════════════════════
```

---

## §8. Flows back to MacBook (catalogue + methodology + handover)

The ThinkPad delivery surfaced material that should be absorbed into the parent project's docs:

### §8.1 Catalogue v0.1.3 candidates (flag for next vocabulary refresh)

- **`accidentReportStatus` state machine** as a worked example of L-ARCH-1 ("find the canonical state machine first") — add to catalogue §2d.1 with source_kind = "State machine diagram" and a worked example.
- **"Účastník" vs "uživatel"** legal-vocabulary distinction (LESSONS L-DOM-1) — add to catalogue §6 (SUPIN/Bouračka campaign terms) as `[NEW]` with binding.
- **Czech mobile-prefix list** (LESSONS L-DOM-2) — add to catalogue §6 as a *validation pattern* example.
- **`STATUS = 'AKT'` codelist filter** (LESSONS L-DOM-4) — add as a worked example of "FURPS+ R" assertion pattern.
- **IZS QR hand-off** (LESSONS L-DOM-5) — add to catalogue §6.

### §8.2 Methodology mapping AMENDMENT 3 candidates

- **Profile-driven install** (LESSONS L-COMM-4) — add as a Project-Environment-Discipline activity (VUP §4.3.2c "Discipline Project Environment").
- **Four-strategy integration matrix** (`INTEGRATION-CONTRACTS-STRATEGY-v0.1.md`) — add as a canonical pattern under VUP "Determine Logical Test Structure" activity.
- **Plan ≠ Schedule ≠ Estimate split** (now demonstrated in 05a/05b/05c) — promote R-PLAN-1 from draft to binding.

### §8.3 ThinkPad handover updates (next archive version v3 should include)

- The Opus review doc itself (`OPUS-REVIEW-THINKPAD-DELIVERY-v0.1.0-2026-05-05.md`).
- The corrections injection (§7) — paste-ready prompt for CP-SUPIN-03.
- New R-rules (R-DERIVE-1, R-FURPS-1, R-EXPAND-1, R-PLAN-2, R-CONTRACT-1) added to the binding-rules block.
- Catalogue v0.1.2 (already added in v2 of the archive — no change needed).

### §8.4 KB-LESSONS-LEARNED.yaml entries

- LL-CP-SUPIN-01..22 — port the 22 lessons (with the Czech / SUPIN / ČKP context) into the parent project's KB. They generalise: "find the canonical state machine first" applies to any SUT; "photo > screenshot for analytical docs" applies to any client engagement; the 4-strategy integration matrix applies to any vendor-heavy integration.

---

## §9. Open questions returned to operator

| OQ# | Sev | Urg | Pri | Question | Resolve by |
|-----|:---:|:---:|:---:|----------|------------|
| OQ-OREV-01 | A | A | A | Which archive does the corrections injection ship in — repack v3 of the ThinkPad transfer archive now (with this Opus review doc + injection added under `30_operating/`), or send the injection only via email (lighter, faster) and defer archive repack until the v0.2 schema lands? | now (operator decides) |
| OQ-OREV-02 | B | A | A | Should ThinkPad implement code-generation pattern (§6.5 pattern 1) or dynamic parametric runner (§6.5 pattern 2) FIRST? Recommended: code-gen first; dynamic runner v0.3+. Confirm. | next session |
| OQ-OREV-03 | B | A | A | The `02d_AssertionLibrary` seed needs 15–25 patterns. Should ThinkPad bootstrap from the 7 existing SPECs only (~10 patterns), or should the operator pre-author a reference pattern set (e.g. WCAG-target-size-44, response-time-under-N, etc.)? | next session |
| OQ-OREV-04 | B | B | B | The Cartesian sheet `01b_Req_FURPS_Cartesian` could become enormous (20 REQ × 10 FURPS+ = 200 rows; with variants could 5x that). Do we cap to {F,U,R,P,S} for v0.2 and add the +D/+I/+N/+L/+P_phys axis in v0.3? | next vocabulary refresh |
| OQ-OREV-05 | B | A | A | The split `05a_TestPlan` / `05b_TestSchedule` / `05c_TestEstimate` is binding per R-PLAN-1; but for the upcoming SUPNB email delivery, do we send v0.2 with the split, or freeze on v0.1 (one sheet) for the SUPIN review window and apply the split AFTER review? | now (operator decides) |
| OQ-OREV-06 | A | A | A | The 7 placeholder narrative files in `analytical-v0.1.0/` (00_README..05_POKRYTI) need CS authoring. Is this a Petr-personal task, or does ThinkPad Sonnet draft → Petr proofreads? | now (operator decides) |
| OQ-OREV-07 | C | B | C | The 8 LESSONS L-DOM-* (Czech / SUPIN / ČKP-specific) — should these flow into MacBook's `_config/VOCABULARY-CATALOGUE-CS-EN-V0.1.md` §6 (SUPIN/Bouračka campaign terms) as `[NEW]` entries, or stay under the campaign repo's `04_SLOVNIK-CS.md`? Recommendation: both; catalogue §6 takes the *canonical* CS form; campaign glossary derives. | next vocabulary refresh |

---

## §10. Status footer

| Item | Value |
|------|-------|
| Document | `OPUS-REVIEW-THINKPAD-DELIVERY-v0.1.0-2026-05-05.md` |
| Output position | `_config/OPUS-REVIEW-THINKPAD-DELIVERY-v0.1.0-2026-05-05.md` |
| Reviewed delivery | `analytical-v0.1.0-2026-05-05` (16 files, 720 KB, SHA256 D9AA2C…) + `automation-v0.1.0-2026-05-05` (72 files, 226 KB, SHA256 6FEC61…) |
| Excellents preserved | 10 (E1..E10) |
| Schema-level gaps | 8 (G1..G8) |
| Runtime-architecture gaps | 4 (H1..H4) |
| New sheets specified | 8 (00b_Requirements + 01b_Req_FURPS_Cartesian + 01c_StateMachine + 02b_TC_Parameters + 02c_TC_Assertions + 02d_AssertionLibrary + 05a/b/c TestPlan split) |
| New columns specified | 14 across 4 existing sheets |
| New runtime modules | 2 (spec-loader + generator) + 1 validator + 1 wrapper script |
| New R-rules | 5 (R-DERIVE-1, R-FURPS-1, R-EXPAND-1, R-PLAN-2, R-CONTRACT-1) |
| Corrections-injection | §7 paste-ready (≈ 7 STEP block) |
| Open questions | 7 (OQ-OREV-01..07) |
| Estimated ThinkPad effort | 1 large session (STEPs 2+3 = schema + format specs) + 1 medium (STEPs 4+5 = runtime + validator) + 0.5 (STEP 6 = repack + ship) |
| Status | v0.1 — review complete; CP-SUPIN-03 ready to consume §7 injection |

---

*OPUS-REVIEW-THINKPAD-DELIVERY-v0.1.0-2026-05-05.md — 2026-05-05 evening — MacBook CoWork session — Opus*
