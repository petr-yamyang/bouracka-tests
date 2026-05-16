# TestAnalysis + TestDesign deep sessions — preparation plan v0.1 (EN)

**Status.** Strategic preparation for two implementation-independent deep methodology sessions. Not the sessions themselves — those are scheduled separately. This doc fixes the scope, inputs, expected outputs, and reductive-vs-full split for both sessions.

**Predecessor v0.1 docs (binding inputs).**
- `_specs/from-macbook/METH-REFINE-TESTANALYSIS-TESTDESIGN-v0.1.md` — TestAnalysis = transposition operator; TestDesign = coverage operator; TestCasePackage as new entity
- `_specs/V-MODEL-TESTTARGET-DECOMPOSITION-v0.1.md` — current-state inventory + 3-level V-model layering proposal + REQ→TT traceability gap analysis
- `_specs/from-macbook/VOCABULARY-CATALOGUE-CS-EN-v0.1.4.md` — terminology + FURPS+ Cartesian governance (§2e, §2f)
- `_specs/from-macbook/SUPIN-ARCH-HARVEST-DISCIPLINE-v0.1.md` — Track 2 (ArchiMate / BPMN / UML / ERD) as first-class peer to Track 1 testing
- `_config/BOURACKA-DATA-STORE-EVOLUTION-PLAN-v0.1-EN.md` — Bouračka B/E reductive instantiation of MI-M-T patterns

**Sibling pilots under MI-M-T.**
- `FOURIER-FOUNDATIONS-WORKING-SPEC-v0.2-EN.md` — top-down pilot for cross-pattern validation

**Owner.** Pete Y.
**Authored.** 2026-05-12, post-Kate-drop dispatch.
**Audience.** Pete (session lead); MI-M-T backend architect (consumer of the full output); Bouračka-side dev iteration owner (consumer of the reductive subset for workbook edits).

---

## §1. Strategic frame

Pete 2026-05-12, paraphrased:

> *"Deep session to work out test-analytical — Test Target identification, attributes, mapping, decomposition, coverage — all based on VUP and extended by algebraic and UML patterns. Then session for TestDesign — how to cover specific Test Target by 1..n testcases and formalise that, eventually connect with test-data class equivalence mapping. These are independent on implementation. Reductive sub-set will land into Bouračka — SUPIN Excel B/E, full will be implemented in MI-M-T backend. In parallel also see Oracle DB as a future implementation tasks which we need to think of and prepare our patterns in Bouračka B/E to it."*

This translates to **three parallel work streams**, with clean separations:

```
┌────────────────────────────────────────────────────────────────────────────────────┐
│ STREAM A — Methodology (THIS DOC's scope)                                          │
│ Implementation-INDEPENDENT.                                                         │
│                                                                                     │
│   Deep Session 1 — TestAnalysis (TT identification + decomposition)                │
│   Deep Session 2 — TestDesign  (TT → 1..n TCs + data-class equivalence)            │
│                                                                                     │
│   Output: methodology v0.2 docs binding for both Bouračka and MI-M-T.              │
└─────────────────────────────────┬──────────────────────────────────────────────────┘
                                  ↓ reductive subset           ↓ full
┌──────────────────────────────────┴──────┐  ┌──────────────────┴───────────────────┐
│ STREAM B — Bouračka instantiation        │  │ STREAM C — MI-M-T B/E instantiation  │
│ Implementation-DEPENDENT (Excel/Oracle). │  │ Implementation-DEPENDENT (Postgres+   │
│                                          │  │ Mongo dev; Oracle shadow at SUPIN).  │
│ ~Carries the subset operationally        │  │ ~Carries the full richness            │
│   - 02_TestCases sheet enriched          │  │   - relational schema for TT/TC/Pkg  │
│   - REQ→TT traceability rows filled      │  │   - state-machine sub-tables         │
│   - TestCasePackage sheet added?         │  │   - test-data class equivalence DB   │
│   - workbook v0.4.x bumped (frozen at    │  │   - coverage-completeness compute    │
│     v0.4.4 per data-store plan M1)       │  │   - UI on top                         │
└──────────────────────────────────────────┘  └──────────────────────────────────────┘
                                  ↓                              ↓
                            STREAM D — Kate field feedback (continuous)
                            Reactive iterations on detail-tech level.
                            Not gating; runs in parallel.
```

The deep sessions produce **methodology artefacts** (v0.2 of METH-REFINE + V-MODEL + new docs). Streams B and C consume those artefacts independently. Stream D feeds operational signal back into the methodology when it surfaces.

---

## §2. Methodology stack — four source pillars × three target layers

The deep sessions are **synthesis work**, not from-scratch authoring. Four
already-established pillars feed into three target methodology layers. The
v0.2 outputs are what emerges when these inputs are processed through
algebra + UML rigor.

### §2.1 Four source pillars (binding inputs to both sessions)

Pete 2026-05-12: *"based on combination of arch and analytics, requirement
analysis and already established VUP conceptual framework"*.

| Pillar | Existing artefacts (binding) | What it brings to the sessions | Pillar owner |
|--------|------------------------------|---------------------------------|--------------|
| **P1 — Architecture** | `_specs/from-macbook/SUPIN-ARCH-HARVEST-DISCIPLINE-v0.1.md`; the Bouračka–IS ČKP diagram (S1); ArchiMate / BPMN / UML / ERD harvest discipline | The architectural lens. Test Targets live in a context of components, integrations, data flows, deployment topology. Without P1, TTs float without anchoring. | Track 2 harvest |
| **P2 — Analytics** | `_specs/from-macbook/METH-REFINE-TESTANALYSIS-TESTDESIGN-v0.1.md`; `_specs/V-MODEL-TESTTARGET-DECOMPOSITION-v0.1.md`; the operational findings from CP-SUPIN-02..05 workbook iterations | Operator-level reality: TestAnalysis = transposition, TestDesign = coverage, TestCasePackage as new entity. The 28-TT + 49-TC inventory + REQ→TT traceability gap analysis. The "what actually happens at the bench" voice. | Pete + prior Cowork/Opus passes |
| **P3 — Requirement analysis** | `00b_Requirements` sheet (20 REQs); `01b_Req_FURPS_Cartesian` matrix (200 cells = 20 REQs × 10 FURPS+ dimensions); KP review enrichment (`comments_KP_en`, `env`, `ext_ws`) | The "what we have to verify" axis. The REQ × FURPS+ matrix is the input to TestAnalysis's transposition operator. Without P3, there is nothing to transpose. | Pete (operator); KP (domain reviewer) |
| **P4 — VUP conceptual framework** | Vaněk-Vaněk-Kukol body of work (`/Users/petryamyang/Documents/Testing - resources/testing/DV/VUP/_VUP/`); `_specs/from-macbook/VOCABULARY-CATALOGUE-CS-EN-v0.1.4.md` (§2b CAST canon, §2e FURPS+, §2f Cartesian governance); `_config/METHODOLOGY-MAPPING-V0.1.md` §3.3 (UP/VUP mapping); CAST + FURPS+ extensions already authored | The conceptual baseline: vocabulary (TestPlan, TestAnalysis, TestDesign, TestCase, TestTarget, ...), activities (Compile Master Test Set, Design Test Elements, Determine Coverage), coverage matrix discipline, equivalence-class-testing technique. The methodology we **extend**, not replace. | VUP (external authority); Pete's CAST + FURPS+ + Cartesian extensions on top |

**Important.** These pillars are **inputs** — the deep sessions do not
modify them. What the sessions produce is the v0.2 synthesis that consumes
all four pillars coherently. If a session reveals a pillar gap (e.g. a P3
REQ is mis-classified, or a P1 architectural diagram is stale), the gap is
logged back to the pillar owner — it doesn't get fixed inside the synthesis
doc.

### §2.2 Three target methodology layers (what the synthesis produces)

The synthesis layers VUP (workflow) × Algebra (formal semantics) × UML
(structural/behavioural modelling) over the four pillars:

| Layer | Role | Provides |
|-------|------|----------|
| **VUP workflow** (P4 extended) | Foundation / process scaffold | The activities (Compile Master Test Set → Design Test Elements → Determine Coverage) and their input/output contracts |
| **Algebra** (new in v0.2) | Formal-semantics rigor | Set-theoretic and lattice-theoretic operations on TTs/TCs/coverage; equivalence relations on test-data classes; combinatorial coverage algebra |
| **UML** (P1 extended) | Structural / behavioural modeling | Class diagrams for entity taxonomy; state machines for behaviour; activity for flow; sequence for integration; use-case for REQ traceability |

The three layers are **complementary, not competing**:

- **VUP workflow** answers "what step are we in?"
- **Algebra** answers "what is mathematically true about coverage?"
- **UML** answers "what is the structural/behavioural shape we're testing?"

A Test Target identified via VUP transposition (§2 of METH-REFINE v0.1) is
**also** a member of a coverage lattice (algebra) **and** a node in a UML
class taxonomy (modelling). All three views agree by construction. When
they disagree, that's the signal to revisit the relevant pillar.

### §2.3 How the four pillars synthesize into the target

| Pillar | Feeds Session 1 (TestAnalysis) by... | Feeds Session 2 (TestDesign) by... |
|--------|--------------------------------------|--------------------------------------|
| **P1 Architecture** | UML class taxonomy for TT subtypes (§3.5); integration-boundary clarity (component vs subsystem vs system TTs); the activity/flow shape that justifies FlowSegmentTT as orthogonal axis | Sequence + activity diagrams (which TCs trace which integration steps); ERD anchor for TC parameters that map to component-state fields |
| **P2 Analytics** | Operator-tested TT attribute schema (§3.3 builds on it); REQ→TT traceability gap to close (V-MODEL v0.1 §2.2 → §3.6); the 5-level V-model elevation of V-MODEL v0.1's 3-level | TestCasePackage entity (METH-REFINE v0.1 §4 → §4.3 here); the existing 49-TC inventory + coverage-gap inventory; TC-composition R-FAIL-1 lifted to package level |
| **P3 Requirement analysis** | The 20 REQs × 10 FURPS+ = 200-cell Cartesian matrix as input to TestAnalysis's transposition (§3 of METH-REFINE v0.1) | FURPS+ dimension inheritance through to TC level (which TC addresses which dimension); equivalence-class partitioning per FURPS-F per REQ |
| **P4 VUP conceptual framework** | The activity "Compile Master Test Set" the session operates within; vocabulary (CAST, FURPS+, Cartesian) the session reuses; the coverage-matrix discipline that governs §3.6 | The activity "Design Test Elements" the session formalises; equivalence-class-testing technique (VUP canon) extended into §4.5 partition algebra |

Without P3, Session 1 has nothing to transpose.
Without P4, Sessions 1 and 2 lack the workflow grammar.
Without P1, the target taxonomy floats free of architectural reality.
Without P2, the operator's lived experience isn't reflected.

**All four pillars together is mandatory.** Any pillar absent or stale
weakens the synthesis. If a pillar update is needed before the sessions
(e.g. P3 needs a missing REQ added, P1 needs an integration diagram
refresh), that work is **prerequisite**, not in-session work.

### §2.4 Pillar readiness checklist (gating Session 1)

Before Session 1 starts, confirm each pillar is at usable state:

| Pillar | Readiness check | Owner if not ready |
|--------|-----------------|---------------------|
| P1 Architecture | ArchiMate-style top-level diagram exists (even if hand-drawn); integration topology map is reasonably current | Track 2 harvest cycle |
| P2 Analytics | METH-REFINE v0.1 + V-MODEL v0.1 both readable; workbook v0.4.4 frozen | Bouračka workbook owner |
| P3 Requirement analysis | All 20 REQs have FURPS+ dimensions tagged; `01b_Req_FURPS_Cartesian` is consistent with `00b_Requirements`; KP review applied | Pete (post Phase-2 patch) |
| P4 VUP framework | Vocabulary v0.1.4 accessible; relevant VUP source pages (Compile Master Test Set, Design Test Elements) re-read by session lead | Pete pre-session |

If any pillar fails its readiness check, **delay the session** until the
pillar is brought to readiness. Don't run a methodology synthesis on
half-set inputs — the output will encode the gap.

---

## §3. Deep Session 1 — TestAnalysis

**Scope.** Test Target identification, attributes, mapping, decomposition, coverage.
**Implementation-independent.** Output is binding for both Bouračka and MI-M-T.
**Estimated duration.** 3-5 hours focused.
**Produces.** `_specs/METH-REFINE-TESTANALYSIS-TESTDESIGN-v0.2.md` + `_specs/V-MODEL-TESTTARGET-DECOMPOSITION-v0.2.md` + new doc `_specs/TEST-TARGET-ATTRIBUTE-MODEL-v0.1.md`.

### §3.1 Pre-session inputs (read before)

1. METH-REFINE v0.1 §1 (the discovery), §2 (TestAnalysis formal redefinition), §6 (TestCasePackage entity)
2. V-MODEL-TESTTARGET-DECOMPOSITION v0.1 — entire doc
3. VOCABULARY-CATALOGUE v0.1.4 §2e (FURPS+) + §2f (Cartesian governance) + §1 (testing-core terms)
4. Workbook v0.4.3 (or v0.4.4 if Phase-2 has landed by session time): sheets `00b_Requirements`, `01_TestTargets`, `01b_Req_FURPS_Cartesian`, `01c_StateMachine`, `01d_PrioritySevUrgMatrix`
5. SUPIN-ARCH-HARVEST-DISCIPLINE v0.1 §1 (two-track frame) — TestAnalysis is Track 1's interface to Track 2's UML/ArchiMate

### §3.2 Session agenda

| § | Topic | Duration | Output |
|---|-------|----------|--------|
| A1 | Confirm TestAnalysis = transposition operator (lock METH-REFINE v0.1 §2) | 15 min | Agreement in v0.2 |
| A2 | Test Target **attribute model** — what does a TT *carry*? | 45 min | New doc `TEST-TARGET-ATTRIBUTE-MODEL-v0.1.md` §3.3 below |
| A3 | Test Target **decomposition algebra** — what operations apply? | 60 min | v0.2 §3.4 below |
| A4 | Test Target **UML class taxonomy** — class hierarchy + composition rules | 60 min | v0.2 §3.5 below |
| A5 | **Coverage algebra** — coverage as lattice; meet/join; completeness measure | 45 min | v0.2 §3.6 below |
| A6 | **REQ → TT traceability** mechanics — fill the gap V-MODEL v0.1 §2.2 identified | 45 min | Plan + reductive subset specified |
| A7 | Reductive subset → Bouračka Excel B/E + full → MI-M-T B/E | 30 min | §3.7 below; binding split |
| A8 | Wrap + sequence to Session 2 | 15 min | Agreed handoff package |

Total ≈ 5 hours. Splittable into two 2.5-hour halves if needed.

### §3.3 Test Target attribute model — proposed for session A2

A TestTarget is a **typed entity** with these attributes (proposal — session locks final):

```
TestTarget := {
  identity:
    id                : opaque-unique (e.g. TT-CP-R1-A1)
    name_cs / name_en : human-readable
    aliases           : optional list of historical names

  classification:
    v_model_level     : enum { L0-Business, L1-System, L2-Subsystem, L3-Component, L4-Unit }
                        — extends V-MODEL v0.1 §3's 3-level into 5-level for MI-M-T
    decomposition_kind: enum { page, behavior, component, integration, regression, smoke,
                                flow-segment, codelist, identifier }
                        — already proposed in METH-REFINE v0.1 §2.2 STEP 3
    cast_dim          : { CO, KDO, KDY, KDE, JAK }   — R-CAST-3 facets present

  derivation:
    source_artefacts  : list — analytical doc page refs, recon screen IDs, REQs, etc.
    requirement_refs  : list — REQ-* ids backing this TT (REQ→TT traceability)
    furps_dimensions  : list — F, U, R, P, S, +D, +I, +N, +L, +P_phys
    derivation_method : enum { transposition, recon-derived, contract-derived,
                                model-derived, regression-derived }
    confidence        : enum { HIGH, MEDIUM, LOW }                — per harvest discipline
    last_validated_at : date

  state-behavior (if applicable):
    state_machine_ref : optional FK to 01c_StateMachine entry
    initial_state     : optional
    accepted_states   : optional list
    transitions       : optional list

  coverage:
    coverage_status   : enum { uncovered, partial, sufficient, exhaustive }
    coverage_metric   : float [0..1] — computed by algebra of §3.6
    package_refs      : list of TestCasePackage ids
    tc_count_direct   : int
    tc_count_inherited: int (via package membership)

  lifecycle:
    item_status       : enum { proposed, active, deprecated, retired }
    severity / urgency / priority : per 01d_PrioritySevUrgMatrix

  governance:
    owner             : person / role
    review_cadence    : enum { weekly, sprint, release, ad-hoc }
    cross_pilot_export: bool — does this TT pattern export to MI-M-T?
}
```

Some attributes are **mandatory** (id, v_model_level, decomposition_kind, source_artefacts, derivation_method). Some are **optional** (state_machine_ref, aliases). Coverage attributes are **computed**, not authored.

### §3.4 Test Target decomposition algebra — proposed for session A3

Decomposition is an operation `D : TT → TT_subset` producing a partition (or covering set) of finer-grained TTs. Algebraic properties:

```
1. Refinement is partial order  (TT_a ⊑ TT_b iff TT_a is a refinement of TT_b)
   - reflexive, transitive, antisymmetric
   - induces a lattice with top = whole-system TT, bottom = leaf-unit TTs

2. Decomposition kinds compose:
   - page-decomp ∘ behavior-decomp = behavior-at-page-level (commutative iff well-modeled)
   - component-decomp ∘ integration-decomp = integration-at-component-level

3. Source preservation:
   - if TT_a ⊑ TT_b, then source_artefacts(TT_a) ⊆ source_artefacts(TT_b)
   - (a refinement cites no source the parent doesn't cite, by construction)

4. FURPS+ inheritance:
   - if TT_a ⊑ TT_b, then furps(TT_a) ⊆ furps(TT_b)
   - (a refinement addresses dimensions the parent addresses; never more)

5. Coverage propagates upward:
   - coverage(TT_b) = aggregate(coverage(TT_a) for all TT_a ⊑ TT_b)
   - aggregate function: weighted-min for strict, weighted-mean for soft

6. Orthogonal decomposition dimensions:
   - V-MODEL level × FURPS+ × CAST(R-CAST-3) × decomposition_kind  — 4D matrix
   - Each TT occupies one (or compatible-cluster) cell in this 4D matrix
   - Coverage is reached when every active cell is at coverage_status >= sufficient
```

The lattice structure is what makes coverage measurement **algebraic** rather than ad-hoc counting. Coverage isn't "we have N TCs" — it's "we cover this region of the lattice up to this depth in this dimension".

### §3.5 Test Target UML class taxonomy — proposed for session A4

```
                       ┌─────────────────────────┐
                       │     TestTarget          │
                       │  (abstract)             │
                       │  +id, +v_model_level    │
                       └─────────────────────────┘
                                  △
            ┌─────────────────────┼────────────────────┬────────────────────┐
            │                     │                    │                    │
┌───────────────────┐  ┌────────────────────┐  ┌─────────────────┐  ┌──────────────┐
│ BusinessTT (L0)   │  │ SystemTT (L1)      │  │ SubsystemTT (L2)│  │ ComponentTT  │
│ business rule,    │  │ end-to-end flow,   │  │ integration of  │  │ (L3) +       │
│ regulation,       │  │ E2E scenario,      │  │ 2-N components, │  │ UnitTT (L4)  │
│ KPI               │  │ user journey       │  │ subsystem       │  │ leaf unit    │
└───────────────────┘  └────────────────────┘  └─────────────────┘  └──────────────┘
                                  △
                                  │ (composition — flow segments)
                       ┌─────────────────────────┐
                       │    FlowSegmentTT        │
                       │ (orthogonal to V-level) │
                       │ activity-diagram-shape  │
                       └─────────────────────────┘
                                  △
            ┌─────────────────────┼────────────────────┐
            │                     │                    │
   ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐
   │ PhaseTT        │  │ CodelistTT     │  │ IdentifierTT       │
   │ (PHASE-0..4)   │  │ (data surface) │  │ (Police/IZS code,  │
   │ — current      │  │ — current      │  │ etc.)              │
   │ Bucket 3 TTs   │  │ Bucket 3 TT    │  │ — current Bucket 3 │
   └────────────────┘  └────────────────┘  └────────────────────┘
```

Notes:
- The **multiple-inheritance shape** (FlowSegmentTT orthogonal to V-level) resolves V-MODEL v0.1 §3's "mid-V vs flow-decomposition tension" — Phase/Codelist/Identifier TTs are flow segments, not V-level entries; the model accommodates both axes.
- Each concrete TT subclass has **subclass-specific required attributes** (e.g. PhaseTT requires `flow_predecessor_refs`).
- The taxonomy is **closed for v1.0** — no new TT subclasses without bumping the methodology version.

### §3.6 Coverage algebra — proposed for session A5

Coverage is a function `Cov : TT × set-of-TCs → [0, 1]` with these properties:

```
Cov is:
  - monotonic       : adding a TC never decreases coverage
  - saturated       : Cov(TT, TCs) ≤ 1 always; reaching 1 means "exhaustive per current model"
  - composable      : Cov(TT_b) = aggregate(Cov(TT_a) for TT_a ⊑ TT_b)
  - dimension-aware : Cov(TT, FURPS+ d) is per-dimension; total Cov is multi-dim aggregate

Coverage levels (per R-DESIGN-1 / COVERAGE-RULE-STRATEGY v0.1):
  - Phase 0: informational      — TC count only, no gating
  - Phase 1: soft               — divergence reported, not blocking
  - Phase 2: gating per-class   — strict for FURPS-F + FURPS-R; soft elsewhere
  - Phase 3: strict             — full multi-dim coverage gates release

Equivalence class coverage (preview for Session 2):
  - For a TT addressing FURPS-F (functional), the test-data domain partitions
    into equivalence classes (by VUP "Determine Test Cases" technique +
    boundary-value analysis)
  - Cov(TT_func, TCs) = |{eq-classes hit by TCs}| / |{eq-classes total}|
  - Boundary-value sub-coverage = TCs hitting class boundaries
```

The algebra is **rigorous enough to be machine-checked** (algorithm: walk the TT lattice; for each leaf-TT, compute Cov from its TC set; aggregate upward per composition rules; flag any cell below threshold).

### §3.7 Reductive subset (Bouračka) vs full (MI-M-T)

Not every methodology pattern lands in Bouračka's Excel B/E. The split:

| Pattern | Bouračka (reductive) | MI-M-T (full) |
|---------|---------------------|---------------|
| TT identification + attributes (§3.3) | All mandatory attrs in `01_TestTargets`; optional attrs deferred | All attrs as separate columns / sub-tables |
| V-model 5-level taxonomy (§3.4) | `requirement_kind` column populated (was None) + new `v_model_level` column | Class hierarchy native; subclass-specific attrs in subtables |
| FlowSegmentTT taxonomy (§3.5) | Existing PHASE-* TTs retained as-is in `01_TestTargets`; documented as FlowSegment subclass via comment | Native subtype; first-class M:N with V-level TTs |
| Decomposition algebra (§3.4) | Manual — operator's discipline; spot-checked in review | Algorithmic — graph computation over relational schema |
| Coverage algebra (§3.6) | Manual aggregate via `09_Reports` sheet; Phase 0 informational only | Full machine-computed; Phase 0→3 gating per release |
| State machine sub-modeling | `01c_StateMachine` sheet (already exists) | Sub-table with FK to TT; transitions as M:N |
| REQ→TT traceability | `requirement_ref` column on `01_TestTargets` populated | Native M:N junction table |
| Confidence / last_validated_at | Out of scope for Bouračka workbook | Native — per harvest discipline |

**Bouračka design principle for Stream B**: only patterns that pay off operationally within Cíl-1..3 timeframe land in the Excel workbook. Everything heavier waits for MI-M-T B/E.

---

## §4. Deep Session 2 — TestDesign

**Scope.** How to cover a Test Target by 1..n TestCases. Formalisation. Test-data class equivalence mapping.
**Implementation-independent.** Output is binding for both Bouračka and MI-M-T.
**Estimated duration.** 3-5 hours focused.
**Prerequisite.** Session 1 outputs locked.
**Produces.** v0.2 of METH-REFINE (TestDesign section) + new doc `_specs/TEST-DATA-CLASS-EQUIVALENCE-v0.1.md`.

### §4.1 Pre-session inputs

1. METH-REFINE v0.1 §3 (TestDesign formal redefinition), §4 (TestCasePackage entity)
2. Session 1 outputs (TT attribute model + decomposition algebra + coverage algebra)
3. Workbook v0.4.x: sheets `02_TestCases`, `02b_TC_Parameters`, `02c_TC_Assertions`, `02d_AssertionLibrary`, `03_TestData`
4. VOCABULARY-CATALOGUE v0.1.4 §1 (test-case-related terms) + §2b (CAST canon)
5. VUP material on "Design Test Elements" + "Determine Coverage" (Pete's local: `/Users/petryamyang/Documents/Testing - resources/testing/DV/VUP/_VUP/`)

### §4.2 Session agenda

| § | Topic | Duration | Output |
|---|-------|----------|--------|
| D1 | Confirm TestDesign = coverage operator (lock METH-REFINE v0.1 §3) | 15 min | Agreement in v0.2 |
| D2 | TestCasePackage **attribute model** + invariants | 45 min | §4.3 below |
| D3 | TT → 1..n TC **mapping algebra** — function vs relation; multiplicities | 60 min | §4.4 below |
| D4 | Test-data **class equivalence** — partition algebra; boundary values | 60 min | §4.5 below (new doc) |
| D5 | TC composition rules (happy/failure/regression/smoke balance) | 45 min | §4.6 below |
| D6 | Assertion library + parameterisation (linking `02c_TC_Assertions` ↔ `02d_AssertionLibrary`) | 30 min | Refined contract |
| **D6b** | **Test-Step as first-class entity** (FR-K-001+002 from Kate Round-1) — TestCase ↔ 1..N TestSteps with action+expected; bug→TC→step traceability; UI step-preview modal | **45 min** | **New `02e_TestSteps` sheet schema; bug.linked_step_ref field; v0.1.5 implementation contract** |
| **D6c** | **Audit-grade visibility design (STRAT-K-001)** — what "audit-grade" means for Bouračka run results; at-a-glance vs click-to-drill UX layering; which evidence fields MUST always be visible vs reveal-on-demand; impact on TES presentation v0.2 + Oracle ERD `BCKA_TEST_RUN_RESULTS` column design | **60 min** | **`_config/BOURACKA-AUDIT-VISIBILITY-DESIGN-v0.1.md` outline; agenda for separate implementation session** |
| D7 | Reductive subset → Bouračka Excel B/E + full → MI-M-T B/E | 30 min | §4.7 below; binding split |
| D8 | Wrap + integration with Session 1 outputs | 15 min | Combined v0.2 ready for adoption |

Total ≈ **7 hours** (extended from 5h to fold in Kate Round-1 outputs). Can be split into two ~3.5h halves if calendar permits.

### §4.3 TestCasePackage attribute model — proposed for D2

```
TestCasePackage := {
  identity:
    id                  : opaque-unique (e.g. PKG-CP-R1-A1-AUTH)
    name_cs / name_en   : human-readable
    coverage_narrative  : 1-3 sentence rationale

  composition:
    target_refs         : list of TT ids — what this package covers (M:N)
    tc_refs             : list of TC ids — what this package contains (1:N)
    package_kind        : enum { happy-set, failure-set, regression-set,
                                  smoke-set, mixed-balanced }

  inheritance (from constituent TCs):
    furps_dimensions    : union of constituent TCs' FURPS+ dimensions
    severity / urgency / priority : aggregated (max for severity, max for urgency)
    framework_targets   : intersection of constituent TCs' framework-targets
                          — package can only run where ALL constituent TCs run

  coverage:
    coverage_contribution : { tt_ref → contribution-score [0..1] }
                            — per-TT contribution of this package
    completeness        : float [0..1] — combined with other packages targeting same TT,
                                          does it close coverage?

  lifecycle:
    item_status         : enum { proposed, active, deprecated }
    governance          : owner, review cadence
}

Invariants:
  - A package's target_refs must be non-empty
  - A package's tc_refs must be non-empty
  - At least one happy-set + one failure-set package must target every active TT
    (R-FAIL-1 lifted to package level)
  - Package's framework_targets is intersection, not union (cf. note above)
```

### §4.4 TT → 1..n TC mapping algebra — proposed for D3

```
The mapping is a relation, not a function:
  cover : TT × TC → bool

Multiplicities:
  - 1 TT : N TCs   — common (a TT has multiple TCs covering different paths)
  - 1 TC : M TTs   — common (a TC covers an integrated scenario crossing TTs)
  - N TT : M TCs   — through TestCasePackage layer (the M:N junction)

Algebraic properties:
  - reflexive on TC set: every TC covers something (else it's orphan, BUG-* fire)
  - left-total on active TT set: every active TT has at least one covering TC
    (otherwise coverage_status = uncovered, gating fires per phase)

Function-like projections (computed):
  - TT.tc_count         := |{TC : cover(TT, TC)}|
  - TC.tt_count         := |{TT : cover(TT, TC)}|
  - PKG.tc_set          := tc_refs(PKG)
  - PKG.tt_coverage_set := {TT : ∃ TC ∈ PKG.tc_set with cover(TT, TC)}

Composition with package layer:
  cover-via-package : TT × PKG → contribution-score
  where contribution-score ∈ [0..1]
        sum over packages covering same TT can exceed 1 (overlapping coverage)
        coverage(TT) = saturating-sum (capped at 1) over package contributions
```

### §4.5 Test-data class equivalence — proposed for D4 (new doc)

This is the heaviest piece. New doc `_specs/TEST-DATA-CLASS-EQUIVALENCE-v0.1.md` captures it; here's the kernel:

```
For each input domain D of a TT addressing FURPS-F (functional):
  - Partition D into equivalence classes EC_1, EC_2, ..., EC_n
    such that any two elements of the same class produce equivalent system behavior
    (per VUP "equivalence class testing")
  - Identify boundary elements between classes: BVAL_ij (between EC_i and EC_j)
  - Identify "invalid" classes: EC_inv_k (inputs the system must reject)

Algebraic structure:
  - The set of equivalence classes forms a partition (disjoint, complete)
  - The partition lattice ordering: refinement of partitions
    (a finer partition is more rigorous; less rigorous is coarser)

Coverage metric for FURPS-F:
  ec_coverage(TT) := |{EC : ∃ TC hitting EC}| / |{EC total}|
  bval_coverage(TT) := |{BVAL : ∃ TC hitting BVAL}| / |{BVAL total}|
  invalid_coverage(TT) := |{EC_inv : ∃ TC hitting EC_inv}| / |{EC_inv total}|

Composite FURPS-F coverage:
  Cov_F(TT) = 0.5 * ec_coverage + 0.3 * bval_coverage + 0.2 * invalid_coverage
  (weights tunable per organization / risk profile)

Examples on Bouračka data:
  - TT-CP-R1-A1 (Wizard entry + SMS-Gateway PING)
    input domain: phone numbers
    EC: valid CZ (+420), valid SK (+421), valid AT (+43), other valid intl,
         invalid format, valid format but unreachable, blocked
    BVAL: +420[0-9]{9}, length boundaries, leading-zero edge cases
    EC_inv: empty, letters, control chars, "+xxxxxxxxx" placeholders
```

### §4.6 TC composition rules — proposed for D5

```
For each TT, at minimum (per R-FAIL-1 lifted to package level):
  - 1 happy-path TC          (FURPS-F + S baseline)
  - 1 failure-path TC        (rejection / error handling)
  - 1 regression TC          (against known bug-fixed behavior; bumps on each bug closure)
  - 1 smoke TC               (fast-running; reach + render check)

For each TT addressing FURPS-P (performance):
  - 1 load TC                 (baseline)
  - 1 endurance TC            (extended duration)
  - 1 spike TC                (burst input)

For each TT addressing FURPS-U (usability):
  - 1 viewport-coverage TC    (per viewport in coverage matrix)
  - 1 keyboard-only TC        (accessibility)

A TestCasePackage that satisfies R-FAIL-1 for its TT(s) is a "balanced" package
(package_kind = "mixed-balanced"). Unbalanced packages get coverage penalty
in §3.6 computation.
```

### §4.7 Reductive subset (Bouračka) vs full (MI-M-T)

| Pattern | Bouračka (reductive) | MI-M-T (full) |
|---------|---------------------|---------------|
| TestCasePackage entity (§4.3) | New sheet `02e_TestCasePackages` (when v0.4.x unfreezes for v0.5+) OR pkg-id column on `02_TestCases` | Native relational table; FK to TC + M:N to TT |
| TT → 1..n TC mapping (§4.4) | `test_target_ref` on `02_TestCases` (already exists); package as comment | Native M:N junction table |
| Test-data class equivalence (§4.5) | YAML in `fixtures/test-data/*-classes.yaml`; computed coverage manual via spreadsheet | Native ECPartition + BoundaryValue tables; computed via SQL |
| TC composition R-FAIL-1 (§4.6) | Spot-check at code review; flag in `09_Reports` | Algorithmic check; gating on missing-balance |
| Assertion library (§4.6) | `02d_AssertionLibrary` sheet (exists) | Native catalog table; assertion-parameter join |

---

### §4.8 Test-Step as first-class entity (D6b output preview)

Per Pete 2026-05-13 Kate Round-1 decision: Test-Step graduates from "implicit thing inside a TC's prose" to **first-class entity** so that:

1. Bug records can pinpoint exactly which step failed (FR-K-001)
2. The bouracka-ui /run page can preview each step before execution (FR-K-002)
3. The run console can render `TC#1 step#3 → OK` granularity (FR-K-003)

Proposed shape:

```
TestStep := {
  identity:
    step_id          : opaque-unique (e.g. STEP-CP-A1-001-03)
    tc_code          : FK to TestCase
    step_order       : integer (1-based; order within TC)

  content:
    action_cs        : free-text — what tester does
    action_en        : free-text — same in English
    expected_cs      : free-text — expected outcome
    expected_en      : free-text — same
    screen_state_id  : optional (D00..D18 per KP review acceptance criteria style)
    parameter_refs   : list of 02b_TC_Parameters codes used in this step
    assertion_refs   : list of 02c_TC_Assertions codes verified here

  lifecycle:
    item_status      : proposed / live / deprecated
    created_at / updated_at / created_by / updated_by
}
```

Workbook v0.4.5 candidate adds sheet `02e_TestSteps`. Bug record gains `linked_step_ref` column. Oracle ERD gains `BCKA_TEST_STEPS` table (junction-ish: PK on (tc_id, step_order) or surrogate id). The deep session locks the final shape.

### §4.9 Audit-grade visibility (D6c output preview)

STRAT-K-001 from Kate Round-1: Pete expressed "doubt on findings done by Kate" because audit-grade detail wasn't visible by default. The session designs a 3-layer presentation:

| Layer | When operator sees it | Content |
|-------|------------------------|---------|
| **Layer 1 — At a glance** | Default `/results/{rid}` page load | Summary chip-strip (already shipped v0.1.3) + verdict matrix one-line-per-TC (`TC#1 - OK / TC#2 - NOK → Bug#n step#m`) per FR-K-003 |
| **Layer 2 — TC drill-down** | Click TC code → accordion expand (already shipped v0.1.3 F-06) | Per-fw breakdown + evidence links + error_messages |
| **Layer 3 — Step + assertion forensic** | Click step within TC drill-down | Step-level: which assertions in the step ran, which passed/failed, with actual-vs-expected diff, screenshot at that moment, network trace if available |

Layer 3 is what makes results "auditable" — every assertion every step every TC is reachable from a single starting click. Currently Layer 3 doesn't exist; v0.1.3 stops at Layer 2.

The session also designs the Oracle storage for Layer 3 evidence — joins `BCKA_TEST_RUN_RESULTS` (per-TC) with `BCKA_ASSERTION_GATE_RESULTS` (per-assertion) per ERD §10 v0.2 roadmap. The schema decisions made in D6c land directly into ERD v0.2.

---

## §5. Cross-session coordination

### §5.1 Handoff from Session 1 to Session 2

Session 1 produces:
- Locked TT attribute model
- Locked TT decomposition algebra
- Locked coverage algebra (TT-side)

Session 2 consumes:
- TT attribute model → drives TC mapping requirements
- Coverage algebra → extends to TC + Package layers
- TT-FURPS+ mapping → drives equivalence-class partitioning

The handoff package is a single document: combined v0.2 of METH-REFINE + V-MODEL outputs from Session 1, frozen before Session 2 starts.

### §5.2 What if Sessions reveal METH-REFINE v0.1 errors?

METH-REFINE v0.1 is binding from 2026-05-07, but a v0.2 supersedes. If Session 1 or 2 reveals errors in v0.1's formalisation:
- Patch in v0.2 with clear "supersedes" note
- Don't retroactively rewrite v0.1 (audit trail intact)
- Update consumers (Bouračka workbook discipline, MI-M-T B/E plans) per v0.2

---

## §6. Oracle DB compatibility planning (per data-store-evolution plan)

Per `_config/BOURACKA-DATA-STORE-EVOLUTION-PLAN-v0.1-EN.md`:

- Every TT attribute (§3.3) and every Package attribute (§4.3) is a candidate Oracle column.
- Decomposition algebra (§3.4) needs **recursive query support** in Oracle (`CONNECT BY` or recursive CTE — both supported 11g+).
- Coverage algebra (§3.6) is **computable in SQL** if the lattice is materialised; consider materialised views for big TTs.
- Test-data class equivalence (§4.5) maps cleanly to relational tables `BCKA_EC_PARTITION` + `BCKA_BVAL` + `BCKA_INVALID_EC`.
- TestCasePackage is a junction table with attributes — Oracle's table-with-FKs pattern; no special features needed.

**Implication for Bouračka Excel**: when designing v0.5+ workbook (post-data-store unfreeze), avoid sheet shapes that don't map cleanly to relational structure. Specifically:
- Cell ranges with multiple semantic meanings → split into separate columns
- Long free-text in computed cells → move to dedicated table
- Cross-sheet formula chains → minimise; prefer derived columns computed by `tools/`

---

## §7. Sequencing + scheduling

| Step | Trigger | Estimated date |
|------|---------|----------------|
| Kate v0.1.2 confirms install works | Kate's first install + smoke test | Within 1-3 days of 2026-05-12 |
| Phase-2 patcher fixed against real workbook schema | post-Kate-PASS | Within 1 week |
| Workbook freezes at v0.4.4 | Phase-2 lands | Within 2 weeks |
| **Deep Session 1 (TestAnalysis)** | Workbook frozen + Pete blocks 4-5 hours | Within 3-4 weeks |
| Session 1 outputs reviewed + adopted | post-Session 1, ~1 week | +1 week after Session 1 |
| **Deep Session 2 (TestDesign)** | Session 1 outputs locked + Pete blocks 4-5 hours | ~1 week after Session 1 review |
| Combined v0.2 adopted into Bouračka workbook | Stream B owner | ~2 weeks after Session 2 |
| MI-M-T B/E architect consumes for schema design | when MI-M-T B/E sprint cycle aligns | Async — likely Q3 2026 |

---

## §8. Open questions for Pete

| OQ | Question | Default |
|----|----------|---------|
| OQ-MTH-1 | Run sessions in-person, remote with Cowork, or hybrid? | Cowork-assisted, like prior strategic sessions |
| OQ-MTH-2 | Two separate sessions or one consolidated 8-10 hour mega-session? | Two separate — handoff between is valuable |
| OQ-MTH-3 | Czech-language outputs in parallel to English? | Defer — start English-only, translate to CS for SUPIN consumption when needed |
| OQ-MTH-4 | Should Fourier-Foundations team observe the sessions (for MI-M-T pattern import)? | Defer until Fourier v0.2.0 has shipped |
| OQ-MTH-5 | V-model 5-level (§3.4) vs 3-level (V-MODEL v0.1 §3) — which lands? | 5-level — fits MI-M-T richness; 3-level was a Bouračka reduction |
| OQ-MTH-6 | Algebra rigor level — informal (English prose) or formal (LaTeX math)? | Mostly prose with selected LaTeX where it pays off — match METH-REFINE v0.1 style |
| OQ-MTH-7 | Should test-data class equivalence get its own session (Session 3) or stay folded into Session 2? | Folded; if Session 2 over-runs, spin off as Session 3 |
| OQ-MTH-8 | UML notation source — PlantUML in `_specs/uml/`? Mermaid inline in MD? Both? | Both — PlantUML for class diagrams, Mermaid inline for state/flow |

---

## §9. Living-doc protocol

This doc bumps version when:
- A session lands (v0.1 → v0.2 with session outputs folded in)
- An OQ-MTH-* resolves
- Stream B or C surfaces operational signals requiring methodology revision

---

End of v0.1.
