# Methodology Refinement — TestAnalysis + TestDesign + TestCasePackage — v0.1
## Crisper definitions surfaced by the Bouračka TestPlan xlsx study + VUP review; binding for MI-M-T + SUPIN delivery

**Version:** v0.1.0
**Trigger:** operator finding 2026-05-07 — studying the Bouračka TestPlan xlsx deliverable (per ThinkPad's analytical-v0.1.0 + automation-v0.1.0 outputs) alongside the VUP material at `/Users/petryamyang/Documents/Testing - resources/testing/DV/VUP/_VUP/` revealed that the catalogue v0.1.2 definitions of **TestAnalysis** and **TestDesign** are *too thin*. The actual operational meaning is sharper: TestAnalysis is a *transposition operator*; TestDesign is a *coverage operator*; and there's a missing intermediate entity (**TestCasePackage**) between TestTargets and TestCases.
**Authority:** v0.1 binding from now; updates `VOCABULARY-CATALOGUE-CS-EN-V0.1.md` to v0.1.3 (additive); updates `METHODOLOGY-MAPPING-V0.1.md` AMENDMENT 2 (to be added); impacts the live Bouračka v0.2 workbook (per SYNCHRO + N8 + ARCH-HARVEST docs already shipped to ThinkPad).
**Audience:** Petr (review the refinement before it propagates); ThinkPad Sonnet (consume §9 paste-ready addendum to fold into CP-SUPIN-03 + the MI-M-T schema iteration); MacBook Sonnet (catalogue update + methodology AMENDMENT 2 authoring).
**Posture:** the catalogue v0.1.2 had TestAnalysis = "Analýza testů" + TestDesign = "Návrh testů" — bare nouns. The Bouračka workbook revealed both deserve **process-level definitions** with explicit input → output transformations. This doc supplies those definitions, demonstrates them on the Bouračka case, and propagates the consequences across the existing v0.2 deliverable chain.

---

## §0. Reading order

1. `_config/VOCABULARY-CATALOGUE-CS-EN-V0.1.md` v0.1.2 (esp. §1 testing core, §2b CAST canon, §2e FURPS+, §2f Cartesian governance)
2. `_config/METHODOLOGY-MAPPING-V0.1.md` (esp. §1 the principle, §3.3 UP/VUP)
3. `_config/CLIENT-PILOT-SUPIN-V0.1.md` AMENDMENT 3 (the FURPS+ + Cartesian binding that already exists)
4. `_config/OPUS-REVIEW-THINKPAD-DELIVERY-v0.1.0-2026-05-05.md` §6.1–§6.3 (the workbook sheets `02b_TC_Parameters` + `02c_TC_Assertions` + `02d_AssertionLibrary` — the Package-related infrastructure already half-specified)
5. **This document** (the refinement)

---

## §1. The discovery — what the Bouračka TestPlan xlsx revealed

ThinkPad's v0.1.0 Bouračka workbook has 7 R1 TestTargets + 20 R1 TestCases + 4 hand-written TC SPECs (TC-CP-001..004). When studied alongside the VUP "Compile Master Test Set" + "Design Test Elements" activities, three operational-level realities surfaced that the catalogue v0.1.2 vocabulary doesn't crisply capture:

### §1.1 Reality 1 — TestAnalysis is a *transposition*, not a *decomposition*

The catalogue's §1 entry "Test analysis | Analýza testů | (DESIGN as activity)" reads as decomposition (break a thing into parts). But what actually happens during analysis is closer to a **basis change**:

- Inputs: a matrix of `Requirements × FURPS+ dimensions` (per catalogue §2f Cartesian governance) — the "what we have to verify" axis crossed with the "in which quality dimension" axis.
- Output: groups of TestTargets — each group corresponds to one *cell* (or compatible-cluster of cells) of the matrix.

The transformation is:

```
TestAnalysis : (Requirements × FURPS+) ──transpose──→ TestTargetGroups

  where each TestTargetGroup carries:
    - the Requirement(s) it derives from
    - the FURPS+ dimension(s) it addresses
    - the analytical-source-artefact(s) supporting derivation (per R-DERIVE-1)
    - one or more TestTargets (the actual elements that can be tested against)
```

This is not "break Requirement R-NNN into 5 sub-tasks" — it's "for each (R-NNN, dimension d) pair, produce the TestTarget set that addresses *that quality dimension of that requirement*". The existing 7 Bouračka TTs implicitly do this — but the workbook doesn't show the *transposition step*; it shows only the result. The refinement makes the step first-class.

### §1.2 Reality 2 — TestDesign is a *coverage* operator, not a *one-to-one* mapping

The catalogue's §1 entry "Test design | Návrh testů | (DESIGN as activity)" likewise reads thin. What actually happens during design is:

- Input: a set of TestTargets.
- Output: a set of TestCases such that **every TestTarget has ≥ 1 TestCase covering it** (with multiplicity allowed — one TC may cover multiple TTs; one TT may need multiple TCs).
- The decision unit is the **TestCasePackage** — a coherent bundle of TCs that *together* cover one or more TTs (a Package is the "story we tell about how this TT class is verified").

The transformation is:

```
TestDesign : TestTargetGroups ──cover──→ TestCasePackages ──unfold──→ TestCases

  where each TestCasePackage carries:
    - the TestTarget(s) it covers
    - the FURPS+ dimension(s) inherited from those TTs
    - a coverage-rationale narrative (why these TCs together suffice)
    - 1 or more TestCases (the executable elements)
    - happy/failure/regression/smoke type-balance per R-FAIL-1
    - a coverage_completeness score (0..1) — auto-computed from FURPS+ × TT × TC matrix
```

The Bouračka v0.1.0 workbook has an `02_TestCases` sheet but no Package layer. This made it hard to answer questions like *"are TC-CP-001 and TC-CP-002 a happy/failure pair, or are they unrelated?"* — the answer exists in the SPECs (in the §3.12 R-FAIL-1 fields) but not as a first-class queryable row. The refinement promotes this to a sheet.

### §1.3 Reality 3 — A new entity `TestCasePackage` is needed

A TestCasePackage:
- Aggregates TestCases that share a coverage purpose (e.g. "everything that verifies the implicit-ID-auth happy-path branch of TT-CP-R1-A1")
- Carries Sev/Urg/Pri (computed from constituent TCs; aggregated by max — a Package is as urgent as its most-urgent TC)
- Carries FURPS+ dimensions (union of constituent TCs)
- Has a coverage-rationale narrative (1–3 sentences)
- Maps to one or more TestTargets (M:N junction)

In Bouračka v0.1.0, the implicit Packages are visible by reading §3.12 of each SPEC ("This pairs with TC-CP-002 per R-FAIL-1") — but they're not modelled. **A Package is the unit operators reason about when they ask "what does it take to consider TT-CP-R1-A1 covered?"** That's a real-life mental object; making it a first-class schema entity surfaces and operationalises it.

---

## §2. TestAnalysis — formal redefinition

### §2.1 Definition (binding from v0.1)

**TestAnalysis** is the process of translating + transposing a 2D matrix of `(Requirements × applicable-FURPS+-dimensions)` into 1D groups of TestTargets. Each TestTargetGroup represents one cell or one compatible-cluster of cells in the matrix.

### §2.2 Process steps

```
INPUT: Requirements catalogue (REQ-NNN entries with furps_dimensions tags)
       FURPS+ taxonomy (per catalogue §2e: F, U, R, P, S, +D, +I, +N, +L, +P_phys)

STEP 1 — Build the Cartesian matrix
         For each Requirement R, for each FURPS+ dimension d:
            cell(R, d) =
               - active   : populate with TestTarget candidates
               - na       : justify (one-line; per R-FURPS-1)
               - deferred : plan when

STEP 2 — Cluster compatible cells
         Cells that share a source-artefact + a behaviour share a TestTargetGroup.
         e.g. (REQ-CP-005, F) + (REQ-CP-005, R) — both addressing the
         "implicit-ID-auth" behaviour from same UC source — can share a TT-group.

STEP 3 — Produce TestTargets per group
         For each TestTargetGroup, derive 1+ TestTargets per:
            - decomposition_kind (page / behaviour / component / integration / regression / smoke)
            - source_artefact (per R-DERIVE-1)
            - CO/KDO/KDY/KDE/JAK matrix (per R-CAST-3)

STEP 4 — Validate coverage
         Every active cell of the input matrix must be reachable from at
         least one resulting TestTarget. Validator script
         (`tools/validate-analysis-transposition.py`) enforces this.

OUTPUT: TestTarget catalogue (TT-NNN entries linked back to source REQ × FURPS+ cells)
```

### §2.3 Worked example — Bouračka R1

Pre-analysis (the hidden state in v0.1.0):

| REQ | F | U | R | P | S |
|---|:---:|:---:|:---:|:---:|:---:|
| REQ-CP-001 (gateway entry + SMS-PING) | active | active | active | (deferred) | (na — no S-dimension content) |
| REQ-CP-002 (implicit-ID-auth) | active | active | active | (deferred) | (active — error-message i18n) |
| REQ-CP-003 (police-call interlock) | active | active | (na — pure interlock; no R) | (na) | (na) |
| ... | | | | | |

Post-analysis (what becomes the TT catalogue):

```yaml
- TT-CP-R1-A1: Vstupní brána a SMS-PING
    derived_from_cells:
      - (REQ-CP-001, F)   # functional gateway behaviour
      - (REQ-CP-001, R)   # gateway availability under N8 dependency
    ...
- TT-CP-R1-A2: Implicit-ID-auth happy
    derived_from_cells:
      - (REQ-CP-002, F)
      - (REQ-CP-002, U)   # auto-fill UX
    ...
```

The transposition lets the operator see immediately: *"REQ-CP-001 has an open R-cell that landed in TT-CP-R1-A1; if R-cell weren't covered, validator flags missing TT for that pair."* The coverage logic becomes mechanically checkable instead of trusting that "all important things got tests."

### §2.4 R-rule (binding from v0.1)

> **R-ANALYSIS-1** (binding): TestAnalysis MUST produce a transposition matrix joining `requirements × furps+ dimensions → TestTarget groups`. Validator script enforces every active cell maps to ≥ 1 TestTarget; every TestTarget cites ≥ 1 source cell. Deferred / NA cells are explicit (justified) — never silent.

### §2.5 Schema impact

New table `analysis_transposition` (between `01b_Req_FURPS_Cartesian` per Opus review §6.1 and `01_TestTargets`):

```sql
CREATE TABLE analysis_transposition (
  id INT PRIMARY KEY,
  group_code VARCHAR(40) UNIQUE,           -- e.g. 'ATG-CP-A1'
  group_name VARCHAR(200),
  test_target_ref VARCHAR(40),             -- FK → 01_TestTargets.item_code
  requirement_ref VARCHAR(40),             -- FK → 00b_Requirements.item_code
  furps_dimension VARCHAR(8),              -- F | U | R | P | S | +D...
  cluster_rationale VARCHAR(500),          -- why these REQ × FURPS+ cells share a TT-group
  source_artefact_ref VARCHAR(255),
  created_at TIMESTAMP, updated_at TIMESTAMP, notes TEXT
);
CREATE INDEX ix_atg_tt ON analysis_transposition (test_target_ref);
CREATE INDEX ix_atg_req_furps ON analysis_transposition (requirement_ref, furps_dimension);
```

Excel realisation: new sheet `01a_AnalysisTransposition` between `01_TestTargets` and `01b_Req_FURPS_Cartesian` in the Bouračka workbook v0.3.

---

## §3. TestDesign — formal redefinition

### §3.1 Definition (binding from v0.1)

**TestDesign** is the process of producing a coverage `TestTargets → TestCasePackages → TestCases`, such that every TestTarget is covered by ≥ 1 Package, and every Package is unfolded into ≥ 1 TestCase. The Package is the *unit of design intent* — TCs are the *implementation*.

### §3.2 Process steps

```
INPUT: TestTarget catalogue (TT-NNN entries from TestAnalysis output)

STEP 1 — Group TestTargets into design contexts
         Targets that share a behavioural surface + FURPS+ profile + viewport-class
         share a design context. e.g. all TTs touching "happy-path implicit-ID-auth"
         share one design context.

STEP 2 — Produce TestCasePackages per context
         For each design context, author one or more Packages:
            - happy Package (the canonical positive flow)
            - failure Package (the failure pairs per R-FAIL-1)
            - regression Package (post-bug-fix sentinels)
            - smoke Package (the "is it alive" minimal subset)

STEP 3 — Unfold each Package into TestCases
         A Package contains 1+ TestCases. Each TC is concrete + executable
         (per the existing TC-spec format).

STEP 4 — Validate coverage
         Every TestTarget reachable from ≥ 1 TC via Package linkage.
         Validator script (`tools/validate-design-coverage.py`) enforces.

OUTPUT: TestCasePackage catalogue + TestCase catalogue
```

### §3.3 Worked example — Bouračka R1

Pre-design (Bouračka v0.1.0, implicit Packages):

```
TT-CP-R1-A1 (Vstupní brána + SMS-PING)
  ├── TC-CP-001 (PING happy)
  └── TC-CP-002 (PING NOK / negative)
```

The Package is implicit ("the SMS-PING gateway behaviour Package") and exists only in the SPEC §3.12 prose. R-FAIL-1 is honoured but not modelled.

Post-design (refined; Package made first-class):

```yaml
- TPC-CP-A1-HAPPY:
    name: SMS-PING gateway — happy path Package
    test_target_refs: [TT-CP-R1-A1]
    furps_dimensions: [F, R]
    rationale: |
      Validates the gateway-availability gate works in the happy direction:
      PING returns OK; wizard advances. Includes both web (desktop) and
      mobile (320/375/414) viewports.
    test_case_refs: [TC-CP-001]
    coverage_completeness: 0.5   # only happy; failure-pair under TPC-CP-A1-FAIL
    severity: A
    urgency: A
    priority: A    # computed from constituents

- TPC-CP-A1-FAIL:
    name: SMS-PING gateway — failure / negative-ending Package
    test_target_refs: [TT-CP-R1-A1]
    furps_dimensions: [F, R]
    rationale: |
      Validates the gateway-availability gate's failure mode: PING returns
      NOK or 503; SUT enters ERROR.smsGatewayUnavailable terminal state;
      no record persisted; user sees CS error message matching glossary regex.
    test_case_refs: [TC-CP-002]
    coverage_completeness: 0.5
    severity: A
    urgency: A
    priority: A

- TPC-CP-A1-PERF:
    name: SMS-PING gateway — performance Package (deferred R2)
    test_target_refs: [TT-CP-R1-A1]
    furps_dimensions: [P]
    rationale: |
      Validates < 200 ms PING response time per N8 contract SLO.
    test_case_refs: [TC-CP-N8-PERF-01]   # introduced by N8 contract analysis §9
    coverage_completeness: 1.0           # full P-dimension covered
    severity: B
    urgency: B
    priority: B
```

Now the operator can ask: *"is TT-CP-R1-A1 fully covered?"* — answer = sum of `coverage_completeness` across linked Packages. If < 1.0 across some FURPS+ dimension, flag.

### §3.4 R-rule (binding from v0.1)

> **R-DESIGN-1** (binding): TestDesign MUST produce TestCasePackages between TestTargets and TestCases. Each TestCase belongs to exactly one Package; each Package covers ≥ 1 TestTarget. Coverage is computed mechanically: for every (TestTarget × FURPS+-dimension) pair tagged active, ≥ 1 Package covers it. Validator enforces.

### §3.5 Schema impact

New table `test_case_packages`:

```sql
CREATE TABLE test_case_packages (
  id INT PRIMARY KEY,
  item_code VARCHAR(40) UNIQUE,           -- 'TPC-CP-A1-HAPPY'
  item_name_cs VARCHAR(200),
  item_name_en VARCHAR(200),
  rationale_cs TEXT,
  rationale_en TEXT,
  type VARCHAR(20),                       -- happy | failure | regression | smoke | perf | usability
  furps_dimensions VARCHAR(40),           -- comma-list
  severity CHAR(1),                       -- aggregated max from TCs
  urgency CHAR(1),
  priority CHAR(1),                       -- computed
  coverage_completeness FLOAT,            -- 0..1; auto-computed
  release VARCHAR(10),                    -- R1 | R2 | R3+
  state_machine_terminal_state VARCHAR(40),
  created_at TIMESTAMP, updated_at TIMESTAMP, notes TEXT
);

CREATE TABLE package_test_targets (        -- M:N
  package_id INT REFERENCES test_case_packages(id),
  test_target_ref VARCHAR(40),
  PRIMARY KEY (package_id, test_target_ref)
);

CREATE TABLE package_test_cases (          -- 1:N (a TC belongs to exactly one Package)
  test_case_id INT REFERENCES test_cases(id),
  package_id INT REFERENCES test_case_packages(id),
  PRIMARY KEY (test_case_id)
);
```

Excel realisation: new sheet `02e_TestCasePackages` (between `02d_AssertionLibrary` and `03_TestData`).

The existing `02_TestCases.test_target_ref` column becomes secondary (kept for backwards compatibility); the canonical chain is `TC → Package → TT`, not `TC → TT` directly.

---

## §4. Vocabulary catalogue updates — v0.1.3

### §4.1 §1 testing core — entry refinements

```
| EN canonical | CS preferred | CS variants / notes | Source |
|---|---|---|---|
| Test analysis | Analýza testů | the transposition operator (Requirements × FURPS+) → TestTargetGroups; per R-ANALYSIS-1 | ISTQB CZ + this v0.1.3 refinement |
| Test design | Návrh testů | the coverage operator (TestTargets) → (TestCasePackages → TestCases); per R-DESIGN-1 | ISTQB CZ + this v0.1.3 refinement |
```

### §4.2 §3 CAST entities — new row

```
| EN canonical | CS preferred | MI-M-T table |
|---|---|---|
| Test case package | Balíček testovacích případů | test_case_packages |
| Test target group | Skupina testových cílů | analysis_transposition |
```

### §4.3 §3.2 enums — new Package-type enum

```
| EN | CS | Notes |
|---|---|---|
| Package type: happy | Typ balíčku: happy | (positive coverage) |
| Package type: failure | Typ balíčku: failure | (negative-ending coverage; per R-FAIL-1 partner of happy) |
| Package type: regression | Typ balíčku: regression | (post-bug sentinel) |
| Package type: smoke | Typ balíčku: smoke | (minimal-subset) |
| Package type: perf | Typ balíčku: perf | (FURPS+ P only) |
| Package type: usability | Typ balíčku: usability | (FURPS+ U only) |
```

### §4.4 §11 Open vocabulary questions — closure of an OQ

```
| OQ-VOC-08 | B | A | A | "Attention" → "Diligence" rename | next METH iteration → DEFERRED to METH AMENDMENT 2 (lands together with this refinement) |
```

### §4.5 v0.1.3 release note

Add to catalogue §12 status footer:
- v0.1.3 (2026-05-07) — TestAnalysis + TestDesign redefined as transposition + coverage operators; new entity TestCasePackage; new R-ANALYSIS-1 + R-DESIGN-1 binding rules.

---

## §5. Methodology mapping AMENDMENT 2

The existing AMENDMENT (v0.1.1 catalogue integration) covered VUP canon + Diligence + Plan/Schedule/Estimate + CAST decomposition matrix + impulse + glossary-as-artefact. AMENDMENT 2 adds:

> **AMENDMENT 2 2026-05-07 (TestAnalysis + TestDesign refinement):**
>
> 1. **TestAnalysis is the transposition operator** `(Requirements × FURPS+) → TestTargetGroups`. Per `_config/METH-REFINE-TESTANALYSIS-TESTDESIGN-v0.1.md` §2. New schema table `analysis_transposition`. Validator enforces every active cell of the Req × FURPS+ matrix maps to ≥ 1 TestTarget. Binding rule R-ANALYSIS-1.
>
> 2. **TestDesign is the coverage operator** `TestTargets → TestCasePackages → TestCases`. Per same doc §3. New schema table `test_case_packages`. The TestCasePackage is the *unit of design intent*; TCs are implementations. Validator enforces every (TestTarget × FURPS+ dim) active pair is covered by ≥ 1 Package. Binding rule R-DESIGN-1.
>
> 3. **VUP Test Discipline activity refinement** (`_config/VOCABULARY-CATALOGUE-CS-EN-V0.1.md` §4.3.2c): the activity *"Identify Test Targets and Tested Product Units"* now operationally encompasses TestAnalysis (transposition) per §2; the activity *"Design Test Elements"* operationally encompasses TestDesign (coverage) per §3. Both activities promoted from "do this" to "execute this operator with binding rule".
>
> 4. **Bouračka v0.2 workbook** gains 2 new sheets: `01a_AnalysisTransposition` (between `01_TestTargets` and `01b_Req_FURPS_Cartesian`) + `02e_TestCasePackages` (between `02d_AssertionLibrary` and `03_TestData`).
>
> 5. **MI-M-T schema** gains 2 new tables (`analysis_transposition` + `test_case_packages`) + 2 new junction tables (`package_test_targets`, `package_test_cases`). Migrations `126_add_analysis_transposition.sql` + `127_add_test_case_packages.sql` queued for v0.3.x.

---

## §6. Impact on the SUPIN/Bouračka v0.2 deliverable

The v0.2 deliverable currently in flight (per SYNCHRO + N8 + ARCH-HARVEST docs already shipped to ThinkPad) needs these updates BEFORE morning consumption — otherwise ThinkPad lands a v0.2 workbook missing the new layer.

### §6.1 Workbook structure update (supersedes Opus review §6.7)

Final v0.2 layout — additions in **bold**:

```
00_README                  unchanged + extended legend (FURPS+, Diligence, CO/KDO/KDY/KDE/JAK, Package type)
00b_Requirements           NEW — per Opus review G2
01_TestTargets             extend with FURPS+ + CO/KDO/KDY/KDE/JAK + source_artefact_* + requirement_ref columns
**01a_AnalysisTransposition  NEW — per AMENDMENT 2 §2 (transposition operator output)**
01b_Req_FURPS_Cartesian    NEW — per Opus review G7
01c_StateMachine           NEW — per L-ARCH-1 + Opus review §6.4
02_TestCases               extend with FURPS+ + impulse_ref + diligence + package_ref columns
                           (`package_ref` NEW per AMENDMENT 2 §3 — every TC belongs to a Package)
02b_TC_Parameters          NEW — per Opus review §6.1
02c_TC_Assertions          NEW — per Opus review §6.2
02d_AssertionLibrary       NEW — per Opus review §6.3
**02e_TestCasePackages      NEW — per AMENDMENT 2 §3 (coverage operator output)**
03_TestData                unchanged
04_TestEnvironments        unchanged + sms_gateway_mode column (per N8 §3.4)
05a_TestPlan / 05b_TestSchedule / 05c_TestEstimate  per Opus review G6
06_TestRuns                unchanged
07_TestRunResults          extend per Opus review §6.7
08_Bugs                    extend with diligence + impulse_ref (per Opus review)
09_Reports                 extend per Opus review + add Package-coverage view + Transposition-coverage view
10_Glossary                 unchanged
11_Changelog               unchanged
```

Net effect: 9 → 11 NEW sheets in v0.2. Add validation script logic for the 2 new tables.

### §6.2 R1 TestCasePackage seeding (for ThinkPad)

For Bouračka v0.2, seed `02e_TestCasePackages` with these initial entries:

| Package code | Name | Type | TT covered | TCs |
|---|---|:--:|---|---|
| TPC-CP-A1-HAPPY | SMS-PING gateway happy | happy | TT-CP-R1-A1 | TC-CP-001 |
| TPC-CP-A1-FAIL | SMS-PING gateway negative-ending | failure | TT-CP-R1-A1 | TC-CP-002 |
| TPC-CP-A1-OTP-HAPPY | SMS OTP send + verify happy | happy | TT-CP-R1-A1 | TC-CP-005 |
| TPC-CP-A1-OTP-FAIL | SMS OTP wrong-code + expired | failure | TT-CP-R1-A1 | TC-CP-005-NOK, TC-CP-005-EXP |
| TPC-CP-A1-CONTRACT | N8 contract test | smoke | TT-CP-R1-A1 | TC-CP-N8-CONTRACT-01 |
| TPC-CP-A1-PERF | SMS-PING perf | perf | TT-CP-R1-A1 | TC-CP-N8-PERF-01 |
| TPC-CP-A1-INTERLOCK | Police-call interlock 7 conditions | happy | TT-CP-R1-A?? | TC-CP-003 |
| TPC-CP-A1-INTERLOCK-NEG | Interlock negative branch | failure | TT-CP-R1-A?? | TC-CP-004 |
| TPC-CP-R1-DEEPER | Deeper-wizard skeleton | (mixed) | TT-CP-R1-A2..A7 | TC-CP-006..020 (skeleton) |

So R1 has roughly 9 Packages covering the 7 R1 TTs — average 1.3 Packages per TT, which gives the happy/failure pair cleanly.

---

## §7. Impact on MI-M-T design (broader than Bouračka)

This is the scope-broadening the operator flagged: the refinement applies to MI-M-T whole, not just Bouračka.

### §7.1 The MI-M-T data model gains 2 first-class entities

`analysis_transposition` and `test_case_packages` become first-class MI-M-T entities — same template as `test_cases` / `test_targets` (per VUP CAST framework principle: "every entity uses ItemBase block" — so both tables get the standard ItemBase columns).

### §7.2 The MI-M-T API surface adds 2 endpoint families

New REST endpoints (per `_config/MI-M-T-D03-JIRA-CONTRACT.md` style):

```
GET  /api/v1/projects/{pid}/transposition-groups
GET  /api/v1/projects/{pid}/transposition-groups/{atg-id}
POST /api/v1/projects/{pid}/transposition-groups
PUT  /api/v1/projects/{pid}/transposition-groups/{atg-id}

GET  /api/v1/projects/{pid}/test-case-packages
GET  /api/v1/projects/{pid}/test-case-packages/{tpc-id}
POST /api/v1/projects/{pid}/test-case-packages
PUT  /api/v1/projects/{pid}/test-case-packages/{tpc-id}
GET  /api/v1/projects/{pid}/test-case-packages/{tpc-id}/coverage   # computed coverage_completeness
```

Mode 1 (Replacement for JIRA/Redmine) needs these endpoints to round out feature parity with JIRA's "Test Plan + Test Cycle" entities (which conceptually map to Package + Run).

### §7.3 The MI-M-T reporting layer gains 2 new report types

- **Coverage matrix** (Requirement × FURPS+ × TestTarget × Package × TestCase) — the full chain visualised; gaps surfaced.
- **Package-balance report** — per Package, ratio of happy / failure / regression / smoke; flags imbalanced packages (e.g. all-happy with no failure pair = R-FAIL-1 violation).

### §7.4 The MI-M-T DOCK-EXCEL adapter (v0.3+) gains 2 new sheet importers

- `01a_AnalysisTransposition` → `analysis_transposition` table
- `02e_TestCasePackages` → `test_case_packages` + junctions

So the Bouračka workbook → MI-M-T import path stays mechanical even with the new layer.

---

## §8. ThinkPad addendum — paste-ready into the morning email

To be appended to the SYNCHRO file's §10 prompt, AFTER the N8 addendum (§17 of N8-CONTRACT) and AFTER the harvest addendum (§11 of ARCH-HARVEST), BEFORE `═══ END PROMPT ═══`.

```
═════════════════════════════════════════════════════════════════════════════
ADDENDUM 3 (per _config/METH-REFINE-TESTANALYSIS-TESTDESIGN-v0.1.md)
═════════════════════════════════════════════════════════════════════════════
Operator finding 2026-05-07 (after studying Bouračka v0.1.0 workbook +
VUP material): TestAnalysis is the *transposition operator*
(Requirements × FURPS+) → TestTargetGroups; TestDesign is the *coverage
operator* TestTargets → TestCasePackages → TestCases. New entity
TestCasePackage sits between TT and TC. Two new R-rules + two new
schema tables.

This addendum lands in CP-SUPIN-03 alongside Addendums 1 (N8) + 2
(harvest) — same iteration; no separate session.

═════════════════════════════════════════════════════════════════════════════
STEP 4M — METH REFINEMENT WIRING
═════════════════════════════════════════════════════════════════════════════
4M.1  ADD 2 NEW sheets to the v0.2 workbook (extending the §2.2 list
      from synchro):
        - 01a_AnalysisTransposition (between 01_TestTargets and
          01b_Req_FURPS_Cartesian)
        - 02e_TestCasePackages (between 02d_AssertionLibrary and
          03_TestData)

      Schema for both per §2.5 + §3.5 of the METH-REFINE doc. ItemBase
      columns first; entity-specific after.

4M.2  ADD column package_ref to 02_TestCases. Every TC must belong to
      exactly one Package. Validator enforces.

4M.3  Seed 01a_AnalysisTransposition:
      For each existing 7 R1 TT, derive the Req × FURPS+ cells it
      covers; insert one ATG-CP-NNN row per (TT, REQ, FURPS+) triple.
      Cluster_rationale narrative supplied by ThinkPad based on
      analytical-doc evidence.

4M.4  Seed 02e_TestCasePackages with the 9 R1 Packages per §6.2 of
      METH-REFINE. Set coverage_completeness for each Package; for
      R1-DEEPER skeleton, mark coverage_completeness=0.1 with note
      "skeleton; recon-pending".

4M.5  Update tools/validate-workbook.py (per Opus review §6.6) with 4
      new checks:
       - every active 01b_Req_FURPS_Cartesian cell maps to ≥ 1
         01a_AnalysisTransposition row (R-ANALYSIS-1)
       - every 01a row references a real REQ + furps_dim + TT
       - every TC has a non-null package_ref pointing to a real
         02e_TestCasePackages row (R-DESIGN-1)
       - every (TT, FURPS+ dimension) pair active is covered by ≥ 1
         Package via 02e + junction tables

4M.6  Update _specs/TESTCASE-SPEC-FORMAT-v0.2.md status block §3.2:
      ADD field package_ref to YAML status block. Bump to v0.3 if
      already at v0.2.

4M.7  Update _specs/TESTTARGET-LIST-FORMAT-v0.2.md §3:
      ADD field requirement_furps_cells (list of REQ × FURPS+ pairs the
      TT covers). Bump to v0.3.

4M.8  File new OQs (per §11 of METH-REFINE doc) into the OQ ledger.

4M.9  Update lessons-learned doc with: "L-METH-1 — TestAnalysis +
      TestDesign needed crisper definitions; revealed by workbook
      study; refinement landed in v0.2 cycle."

═════════════════════════════════════════════════════════════════════════════
NEW R-RULES (binding from now)
═════════════════════════════════════════════════════════════════════════════
R-ANALYSIS-1   TestAnalysis is the transposition operator;
                 every active (Req × FURPS+) cell maps to ≥ 1 TestTarget;
                 deferred / NA cells are explicit.
R-DESIGN-1     TestDesign is the coverage operator; every TC belongs
                 to exactly one Package; every (TT × FURPS+ dim) active pair
                 is covered by ≥ 1 Package.

═════════════════════════════════════════════════════════════════════════════
WHEN TO BOUNCE BACK
═════════════════════════════════════════════════════════════════════════════
- Existing 7 R1 TTs cannot all be cleanly transposed from REQ × FURPS+
  cells (might mean the seed Requirements set is incomplete; file OQ
  + propose REQ additions)
- Existing 20 R1 TCs cannot all be cleanly grouped into the 9 proposed
  Packages (might mean Package-set needs expansion; iterate with operator
  before committing)
═════════════════════════════════════════════════════════════════════════════
```

---

## §9. Open questions

| OQ# | Sev | Urg | Pri | Question | Resolve by |
|-----|:---:|:---:|:---:|----------|------------|
| OQ-METH-R-01 | A | A | A | Should existing v0.1.0 TT/TC IDs change with the refinement? Recommendation: NO — keep IDs; add Package layer additively; backwards-compatible | CP-SUPIN-03 morning |
| OQ-METH-R-02 | B | A | A | Coverage-completeness computation — auto-derived from FURPS+ × TT × TC matrix, or manually specified by Package author? Recommendation: auto-derived as first-pass; manually overridable for nuanced cases | CP-SUPIN-03 |
| OQ-METH-R-03 | B | B | B | Package-type enum stability — synchro proposes 6 types (happy/failure/regression/smoke/perf/usability); is this enough, or add reliability/security/legal? | METH iteration v0.2 |
| OQ-METH-R-04 | C | B | C | The MI-M-T schema migrations `126_add_analysis_transposition.sql` + `127_add_test_case_packages.sql` — author now or after Bouračka v0.2 settles? Recommendation: after Bouračka v0.2 lands; schema implementation follows the spreadsheet realisation | next MI-M-T iteration |
| OQ-METH-R-05 | A | A | A | Is the "transposition" framing crisp enough to communicate to non-Opus collaborators (Sonnet sessions; future contributors)? Recommendation: produce a 1-page diagram summarising R-ANALYSIS-1 + R-DESIGN-1 in v0.2 of THIS doc | next METH iteration |

---

## §10. Acceptance gate

This refinement closes when ALL of:

1. Catalogue v0.1.3 update authored (per §4)
2. Methodology AMENDMENT 2 authored (per §5)
3. ThinkPad addendum (§8) folded into SYNCHRO morning email (so CP-SUPIN-03 lands the workbook with the new sheets)
4. Petr review + green-light
5. New R-rules (R-ANALYSIS-1, R-DESIGN-1) added to the binding-rules block of all relevant docs
6. The `01a_AnalysisTransposition` + `02e_TestCasePackages` sheets seeded by ThinkPad in CP-SUPIN-03 v0.2 deliverable

---

## §11. Status footer

| Item | Value |
|------|-------|
| Document | `METH-REFINE-TESTANALYSIS-TESTDESIGN-v0.1.md` |
| Output position | `_config/METH-REFINE-TESTANALYSIS-TESTDESIGN-v0.1.md` |
| Trigger | operator finding 2026-05-07 from Bouračka workbook + VUP study |
| Refinement scope | TestAnalysis = transposition; TestDesign = coverage; new entity TestCasePackage |
| New binding rules | 2 (R-ANALYSIS-1, R-DESIGN-1) |
| New schema tables | 2 (analysis_transposition, test_case_packages) + 2 junctions |
| New Excel sheets | 2 (01a_AnalysisTransposition, 02e_TestCasePackages) |
| Catalogue version | v0.1.2 → v0.1.3 (additive) |
| Methodology mapping | AMENDMENT 2 (lands alongside this doc) |
| Bouračka v0.2 impact | 2 new sheets + package_ref column on 02_TestCases + 4 new validator checks + 9 seeded Packages |
| MI-M-T schema impact | 2 new tables + migrations 126/127 queued for v0.3.x |
| ThinkPad addendum | §8 — paste-ready into SYNCHRO morning email (parallel to physics phase 4 readiness) |
| Open questions | 5 (OQ-METH-R-01..05) |
| Acceptance gate | §10 (6 criteria) |
| Status | v0.1 — refinement landed; ready for Petr review + ThinkPad consumption |

---

*METH-REFINE-TESTANALYSIS-TESTDESIGN-v0.1.md — 2026-05-07 — MacBook CoWork session — Opus*
