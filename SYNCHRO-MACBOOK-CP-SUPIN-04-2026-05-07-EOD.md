# Synchro MacBook — CP-SUPIN-04 EOD — 2026-05-07

> **Adresát.** MacBook session (analytical MI-M-T context).
> **Z.** ThinkPad Opus session (governance) — full day session 2026-05-06.
> **Cíl.** Aktualizovat MacBook session s VŠEMI artefakty z dnešního dne;
> nahrazuje předchozí `SYNCHRO-MACBOOK-CP-SUPIN-04-2026-05-06.md`.

---

## §1. Za posledních 24h

ThinkPad Opus session = velký day session 33 STEP-ů (CP-SUPIN-04 STEP 1..33).
Nejvýznamnější:

### §1.1 Ranní část — DEMO Bouračka calibration

- E2E live walk completed (`flow-A1-main-tst-demo`)
- Playwright suite from scaffolding to GREEN (bring-up + a1-main + a2-alternates)
- Cypress + TestCafe parity scaffolds (CP-SUPIN-05 will exercise full)
- `BOURACKA-TESTPLAN-v0.4.0..v0.4.2.xlsx` schema migrations
- Branch tagging architecture (`applies_to_demo`, `applies_to_prod`)
- Bug naming convention `BUG-CP-{TC}-{ASSERT}` deterministic dedup

### §1.2 Odpolední část — strategic + ecosystem

- ROADMAP-4-TARGET-CS — strategic 4-target plan + MI-M-T migration roadmap
- BRANCH-HANDOFF-TEMPLATE-CS — for future Sonnet sessions
- SUPIN-ecosystem-map repo initiated (sibling to bouracka-tests)
- Bottom-up methodology + fragment-driven assembly governance
- Bouračka first system entry + X1 placeholder
- Archimate sketches at Application + Business layers
- V-model alignment doc

### §1.3 Večerní část — multi-platform + governance + 3-device + cohesion

- MULTI-PLATFORM-TESTING-STRATEGY-v0.1-CS — 6 frameworks, fitness assessment, decision matrix
- TEST-EXECUTION-SUMMARY-FORMAT-v0.1-CS — VUP-grade format spec
- Excel v0.4.2 schema: `13_TestExecutionSummary` + `14_AssertionGateResults`
- ReadyAPI/SoapUI smoke project XML + Postman collection JSON + Selenium pytest scaffolds
- GITHUB-SYNC-STRATEGY-v0.1-CS — independence from SUPIN infra; future mirror path
- `.gitignore` for both repos (ready for `git init`)
- SECOPS-COMPONENTS-CS — extensive 13-section CS audit doc for ČKP SecOps team
- COMPREHENSIVE-MIND-MAP-SUPIN-MIMT-v0.1-CS — this comprehensive mind map (with overlaps + risks + tools + lessons)
- THREE-DEVICE-PLAN-CS — ThinkPad / MacBook / HP Elite roles + sync protocol
- v0.4.6 + v0.4.7 morning deliverables
- Archive folder restructure (`bouracka - automated test suites inouts and seeders/{bouracka,DEMO bouracka,test,prod,_obsolete}`)

## §2. Klíčová methodology learnings pro MI-M-T (refresh + new)

Z předchozí synchro (2026-05-06) zachovány + 5 nových:

### §2.1 Předchozí (zachovány)

1. Branch-aware schema design — `applies_to_*` columns
2. Single-master + render-on-demand documentation
3. Deterministic bug dedup keys
4. Recovery patterns as code
5. Δ matrix as audit trail
6. Empirical preflight rules

### §2.2 Nové z dnešní odpolední/večerní části

7. **Multi-platform parallel testing strategy** — namísto premature framework decision, run parallel + collect evidence + decide based on data
8. **TestExecution Summary VUP-grade artefact** — step-by-step + assertion gate, JSON normalized + Excel persisted
9. **Bottom-up reverse engineering** as default modus operandi (nikdy neassume legacy doc je truth)
10. **Independence rule** — zero blocking dependency on customer infrastructure
11. **3-device asymmetric model** — Opus governance + Sonnet analytical + non-Claude testing ground

## §3. Co je nového ve workspace pro MacBook k vidění

| Path | Co tam je |
|------|-----------|
| `bouracka-tests/_specs/COMPREHENSIVE-MIND-MAP-SUPIN-MIMT-v0.1-CS.md` | comprehensive mind map (just authored) |
| `bouracka-tests/_specs/THREE-DEVICE-PLAN-CS.md` | 3-device plan (just authored) |
| `bouracka-tests/_specs/MULTI-PLATFORM-TESTING-STRATEGY-v0.1-CS.md` | 6-framework strategy |
| `bouracka-tests/_specs/TEST-EXECUTION-SUMMARY-FORMAT-v0.1-CS.md` | VUP-grade results format |
| `bouracka-tests/_specs/GITHUB-SYNC-STRATEGY-v0.1-CS.md` | GitHub strategy + SUPIN-isolation |
| `bouracka-tests/_specs/BUG-NAMING-CONVENTION-v0.1.md` | bug dedup |
| `bouracka-tests/_specs/BRANCHED-MASTER-DOC-PATTERN-v0.1.md` | single-master pattern |
| `bouracka-tests/_specs/ROADMAP-4-TARGET-CS.md` | 4-target gradual delivery |
| `bouracka-tests/_specs/BRANCH-HANDOFF-TEMPLATE-CS.md` | template pro Sonnet sessions |
| `bouracka-tests/_specs/TESTER-LESSONS-LEARNED-v0.1-CS.md` | empirical patterns |
| `bouracka-tests/_install/INSTALL-FROM-ZERO-v0.4-CS.md` | install guide v0.4 |
| `bouracka-tests/_install/SECOPS-COMPONENTS-CS.md` | SecOps audit doc |
| `bouracka-tests/recon/ANALYTICAL-DOC-MASTER-v0.4.md` | branched master analytical doc |
| `bouracka-tests/BOURACKA-TESTPLAN-v0.4.2.xlsx` | latest Excel master (TES sheets included) |
| `SUPIN-ecosystem-map/` | NEW SIBLING REPO — full ecosystem reverse-engineering structure |

## §4. Co MacBook má dělat (priority)

### §4.1 Číst (in this order)

1. `bouracka-tests/_specs/COMPREHENSIVE-MIND-MAP-SUPIN-MIMT-v0.1-CS.md` — overall view
2. `bouracka-tests/_specs/THREE-DEVICE-PLAN-CS.md` — your role
3. `bouracka-tests/_specs/MULTI-PLATFORM-TESTING-STRATEGY-v0.1-CS.md` — strategic framework decision
4. `SUPIN-ecosystem-map/README-CS.md` — meta-architecture
5. `bouracka-tests/_specs/ROADMAP-4-TARGET-CS.md` — 4-target plan + MI-M-T migration

### §4.2 Psát (MacBook scope)

1. **MI-M-T import contract draft** — `_specs/MIMT-IMPORT-CONTRACT-DRAFT.md` (NEW)
   - Co Bouračka v0.5+ musí emitovat (Excel format, JSON format, naming convention)
   - Co MI-M-T musí poskytovat (live workbook, validator API, runner backend)
   - Migration steps Q3 2026 → Q2 2027

2. **Methodology generalization paper** — `_specs/MIMT-METHODOLOGY-PROPOSAL-v0.1.md` (NEW)
   - Z 11 learnings → universal patterns
   - Které jsou Bouračka-specific, které generalizovatelné
   - MI-M-T governance module proposal

3. **Component module migration plan** — `_specs/MIMT-COMPONENT-MIGRATION-v0.1.md` (NEW)
   - Z `tools/*.py` které kandidáti na MI-M-T modules
   - Abstraction level needed
   - Dependency graph

### §4.3 NEpsát (Opus governance scope)

- Změny Excel schema → jen Opus (= ThinkPad)
- Změny v Bouračka tests → Sonnet branch sessions
- Změny naming convention → jen Opus

### §4.4 Sync-back

`SYNCHRO-MACBOOK-TO-OPUS-2026-05-XX.md` po dokončení iterace, s:
- Methodology export proposals
- Open questions for Opus governance
- Recommended next-iteration changes

## §5. 3-device sync status (per `THREE-DEVICE-PLAN-CS.md`)

| Device | Status (2026-05-06 EOD) |
|--------|--------------------------|
| ThinkPad | full Opus session ran; ready for morning automation tests |
| MacBook | this synchro doc is the entry; pull GitHub when ready |
| HP Elite | idle today; SUPIN VPN access window TBD |

## §6. Open governance questions for MI-M-T track

| # | Question | Owner |
|---|----------|-------|
| Q-MIMT-1 | Excel framework freeze date? | SUPIN architects + MI-M-T tech-owner |
| Q-MIMT-2 | MI-M-T live workbook readiness for Bouračka? | MI-M-T project |
| Q-MIMT-3 | Q3 2026 freeze viable? | Pete + MI-M-T |
| Q-MIMT-4 | Component module hosting (where do tools/ migrate to)? | MI-M-T |
| Q-MIMT-5 | Bouračka-specific patterns vs MI-M-T-universal patterns split? | MacBook iteration |

## §7. Status

| Item | Hodnota |
|------|---------|
| Synchro doc | `SYNCHRO-MACBOOK-CP-SUPIN-04-2026-05-07-EOD.md` |
| Datum | 2026-05-07 (EOD ThinkPad time) |
| Z | ThinkPad Opus session (Pete) |
| Pro | MacBook session (analytical MI-M-T) |
| Replaces | `SYNCHRO-MACBOOK-CP-SUPIN-04-2026-05-06.md` (předchozí) |
| Velikost změn | 33 STEP CP-SUPIN-04 + 5 nových methodology learnings |
| Status | připraveno k MacBook synchronizaci |
