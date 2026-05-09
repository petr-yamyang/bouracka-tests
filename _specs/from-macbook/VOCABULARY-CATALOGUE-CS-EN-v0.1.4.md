# Bilingual Vocabulary Catalogue — CS ↔ EN — v0.1
## Testing · Analytical · Architectural · Methodology · MI-M-T product · 3-fold-path content terms

**Version:** v0.1.4 (2026-05-08 — initial release adds coverage-gating phase-in §2f.6, decoupled-versioning policy §2g, V-model TestTarget assembly-layer transposition basis §2h; folds in convergence findings + ThinkPad-contributed patterns from `_config/SYNCHRO-MACBOOK-TO-OPUS-CP-SUPIN-06-2026-05-08.md` §2. **In-place patch later 2026-05-08:** §2h.1 worked example added — folds 8 TT codes from Sonnet's CP-SUPIN-05 cross-framework parity push (commit `5c865c8` on `cp-supin-05-cross-framework-parity` branch); introduces R-VMODEL-2 + E2E meta-layer; preserves v0.1.4 number since §2h.1 is in-place expansion under existing §2h.) Skips v0.1.3 — catalogue jumped directly to v0.1.4 per the SYNCHRO-driven scope. Earlier v0.1.2 (2026-05-03 evening) added analytical-source-artefact → TestTarget derivation discipline (§2d), FURPS+ quality dimensions canonical CS rendering (§2e), Cartesian Requirement × FURPS+ test-base expansion governance (§2f), and methodology-aware planning attribution (§4.4 — Waterfall release · UP iteration · Agile sprint/epic/release)
**Trigger:** user direction 2026-05-03 (evening Opus session) — collect, assess, and lock the bilingual vocabulary that drives improvements to the MI-M-T product, 3-fold-path pages, and the SUPIN/Bouračka automated test base. Czech equivalents are needed both for content authoring (mim2000.cz, zemla.cz, bodyterapie.com Czech locale) and for the SUPIN tester audience (Czech-first per `CLIENT-PILOT-SUPIN-V0.1.md` AMENDMENT 2 §C-6).
**Authority:** binding from now for all CS-locale rendering across the project. EN remains the canonical authoring language for code + scope docs; CS is the preferred user-facing language for client deliverables.
**Sources synthesised (with workspace paths where applicable):**
- **DVA-2016** (Dušan Vaněk, *Analýza a návrhy v modelech architektury podniku, část III — Integrace*, slides 2–14) — `uploads/DVA - Analyza a navrhy v modelech architektury podniku - III cast integrace.pptx`
- **VUP — Versatile Unified Process** (Vaněk + Kukol, Raiffeisen BANK adaptation, 2007) — `Testing - resources/testing/DV/VUP/_VUP/` (HTML EARoot export from Enterprise Architect; full discipline + activity + artifact + role catalogue; **canonical** for the UP CS rendering in §4.3)
- **CAST framework — original presentation** (Dušan Vaněk, *Test01-02-2 Framework CAST*, Adastra Apliqua 2006) — `Testing - resources/testing/DV/prezentace TM/Test Elements/Test01-02-2 (T-IC) Framework CAST.ppt` — **canonical** for the CAST CS rendering in §3
- **Test Management presentation** (Dušan Vaněk, *Test03-01-1 Test Management*, 2006/2009) — `Testing - resources/testing/DV/prezentace TM/Test03-01-1 (T-III ) Test Management.ppt` — canonical for §1 Test Management vocabulary; introduces Diligence (péče/pozornost/pečlivost) as 3rd assessment dimension alongside Severity + Urgency
- **Test Plan templates (CZ)** (Vaněk, 2009) — `Testing - resources/testing/DV/prezentace TM/Test Plan/ADA_TST_TMPL.Test_Plan_*_CZ.{xls,mpp}` (4 files: rozcestník, goals_and_objectives, measurements_and_traceability, estimation_and_scheduling)
- **CAST FileList + ValueList engine** (the original Excel storage engine) — `Testing - resources/testing/mereni/Test02-01-1 (T-II ) Mereni v overovani kvality - pomocne soubory/engine FL-CAST FileList and ValueList.xls` — canonical source for CAST item/list field structure (the basis for our `ItemBase` block)
- **IIR Testing Training December 2009** — `Testing - resources/testing/IIR školení prosinec 2009/` — kit with Requirement spec / Test Lab Config / Test plan Mindmapa / Test Case List / Test plan excel / Test Evaluation Summary
- ISTQB Czech glossary (Czech-and-Slovak Testing Board canonical terms)
- Standard Czech SW engineering terminology (ČSN ISO/IEC 25010; ČSN ISO/IEC 12207)
- Project-specific reframings (MI-M-T expansion; Testing Overdose; About stars, quarks and bowl of Tea; bouračka domain)

> **VUP authority note (2026-05-03 — supersedes earlier guess in v0.1):** VUP = **Versatile Unified Process** (Raiffeisen BANK Czech adaptation, authored by Dušan Vaněk + Vladan Kukol, 2007). Earlier draft of this catalogue speculated VUP = "Vícestupňový". That was wrong — corrected here. VUP material lives at `Testing - resources/testing/DV/VUP/_VUP/` as Enterprise Architect HTML export with full discipline + activity + artifact + role taxonomy. §4.3 below now uses VUP CS rendering as the **canonical** UP terminology for this project (overriding the generic RUP CS canon).

---

## §0. How to use this catalogue

For every artefact (scope doc, theme content, test report, page copy, code comment) where a CS-locale rendering is needed:
1. **Find the EN term** in §1–§7 below.
2. **Use the listed CS rendering** (column "Czech preferred").
3. If multiple CS renderings are listed (column "Czech variants"), pick the *preferred* one unless context dictates otherwise; the variants are documented to avoid back-and-forth in proofreading.
4. If the term doesn't exist here yet, **add it** in the appropriate §; flag with `[NEW]` so it surfaces in the next vocabulary review.
5. For cross-MI-M-T-system fields (column names, value-list entries, status enums) — keep the EN canonical form in code/schema; render the CS in UI labels via the translation layer (`inc/translations.php` or equivalent).

**Naming discipline (binding):**
- EN form is the *identifier*; CS form is the *label*. They are not interchangeable.
- Translation tables (`inc/translations.php`, `i18n/cs.json`, etc.) are the only place where EN→CS mapping lives in code.
- This catalogue is the *editorial reference* for those translation tables (and for prose).

---

## §1. Testing core terms

| EN canonical | CS preferred | CS variants / notes | Source |
|---|---|---|---|
| Test | Test | (avoid "zkouška" — too colloquial) | ISTQB CZ |
| Testing | Testování | Activity noun | ISTQB CZ |
| Test case | Testovací případ | Sometimes "testovací scénář" — but reserve "scénář" for higher-level; here = TC | ISTQB CZ |
| Test scenario | Testovací scénář | Higher-level than TC; used for end-to-end flows | ISTQB CZ |
| Test step | Krok testu | "Krok testovacího případu" if disambiguation needed | ISTQB CZ |
| Test data | Testovací data | | ISTQB CZ |
| Test environment | Testovací prostředí | | ISTQB CZ |
| Test set | Testovací sada | "Testová sada"; CAST uses MasterTestSet → "Hlavní testovací sada" | CAST + ISTQB CZ |
| Iteration test set | Iterační testovací sada | "Sprintová testovací sada" if Agile context | CAST |
| Test target | Testový cíl | "Cíl testování" — avoid (too generic); "Předmět testu" — sometimes preferred for behavioural targets | CAST |
| Test plan | Testovací plán | "Plán testů" | ISTQB CZ |
| Test design | Návrh testů | (DESIGN as activity); "Test design" = often left in EN in CZ literature | ISTQB CZ |
| Test analysis | Analýza testů | "Testová analýza" | ISTQB CZ |
| Test execution | Vykonání testů | "Provedení testů"; "Spuštění testů" — for an automated context | ISTQB CZ |
| Test run | Testovací běh | "Běh testů" | ISTQB CZ |
| Test result | Výsledek testu | | ISTQB CZ |
| Test report | Testová zpráva | "Zpráva z testování"; for executive audience: "Souhrnná zpráva o testování" | ISTQB CZ |
| Test coverage | Pokrytí testy | "Testové pokrytí" | ISTQB CZ |
| Test suite | Sada testů | (interchangeable with "Test set" in CS) | ISTQB CZ |
| Smoke test | Smoke test | (Czech literature retains EN; "rychlý ověřovací test" — descriptive, rare) | ISTQB CZ |
| Regression test | Regresní test | | ISTQB CZ |
| Sanity test | Sanity test | (EN retained in CZ literature) | ISTQB CZ |
| End-to-end test | End-to-end test (E2E) | "Test od začátku do konce" — descriptive | ISTQB CZ |
| Integration test | Integrační test | | ISTQB CZ |
| Unit test | Jednotkový test | "Unit test" — common in CZ codebases | ISTQB CZ |
| Acceptance test | Akceptační test | "Přejímací test" — formal/CSN | ISTQB CZ |
| Exploratory test | Exploratorní testování | "Průzkumné testování" | ISTQB CZ |
| Mutation test | Mutační test | | ISTQB CZ |
| Performance test | Výkonový test | "Test výkonnosti" | ISTQB CZ |
| Load test | Zátěžový test | "Test zatížení" | ISTQB CZ |
| Stress test | Stresový test | | ISTQB CZ |
| Security test | Bezpečnostní test | | ISTQB CZ |

---

## §2. Defect / issue terms

| EN canonical | CS preferred | CS variants / notes | Source |
|---|---|---|---|
| Defect | Závada | "Vada"; "Chyba" — overloaded; "Defekt" — formal | ISTQB CZ |
| Bug | Chyba | "Bug" — common in CZ codebases; "závada" for formal report | ISTQB CZ |
| Error | Omyl | (a human mistake that produces a defect) | ISTQB CZ |
| Failure | Selhání | (an observed deviation; what users see) | ISTQB CZ |
| Fault | Vada | (a defect in code/spec) | ISTQB CZ |
| Issue | Problém | "Otázka" — when issue = open question; "Záležitost" — administrative | ISTQB CZ |
| Change request | Požadavek na změnu | "Změnový požadavek" — formal | ISTQB CZ |
| Severity | Závažnost | (impact) | ISTQB CZ |
| Priority | Priorita | (urgency-of-fix) | ISTQB CZ |
| Urgency | Naléhavost | | per `_config/PRIORITY-MATRIX-GOVERNANCE-v0.1.md` |
| Attention | Pozornost | (CAST-specific; "Vyžadovaná pozornost") | CAST |
| Repeatability | Reprodukovatelnost | "Opakovatelnost" — when bug always reproduces | ISTQB CZ |
| Triage | Triáž | "Třídění" — descriptive | ISTQB CZ |
| Root cause | Hlavní příčina | "Kořenová příčina" — direct translation; "Skutečná příčina" — vernacular | ISTQB CZ |
| Workaround | Náhradní řešení | "Obejití"; EN often retained | ISTQB CZ |
| Hotfix | Hotfix | (EN retained in CZ practice) | ISTQB CZ |
| Regression | Regrese | | ISTQB CZ |

---

## §2b. CAST framework — canonical Czech vocabulary (from Vaněk 2006 original)

Harvested from `Testing - resources/testing/DV/prezentace TM/Test Elements/Test01-02-2 (T-IC) Framework CAST.ppt`. These are the *original-author* Czech renderings — they take precedence over any external glossary where they conflict.

### §2b.1 CAST mission + decomposition

| EN canonical | CS preferred (Vaněk canonical) | Notes |
|---|---|---|
| Framework for CAST | Framework pro CAST | (the title) |
| Test entity repository | Úložiště entit testování | (canonical CAST term — used everywhere) |
| Test entity management | Management entit testování | |
| Test entity configuration | Konfigurace entit testování | "pro potřeby etapy a iterace" — for needs of stage and iteration |
| Stage / phase | Etapa | (CAST distinguishes "etapa" = waterfall-style major phase from "iterace" = within-stage iteration) |
| Iteration | Iterace | per VUP §4.3 |
| Support for test implementation and execution | Podpora implementace a vykonání testů | |
| Analysis, summarisation, reporting of test process and results | Analýza, sumarizace a reporting procesu testování a výsledků testů | |

### §2b.2 The CAST decomposition matrix — CO / KDO / KDY / KDE / JAK

CAST adds the following beyond standard test tools:

| EN | CS preferred | English equivalent in framework | Question word |
|---|---|---|---|
| TestAnalysis support | Podpora analýzy testování | identifies WHAT to test | **CO** (WHAT) |
| TestStrategy support | Podpora strategického testování | identifies WHO does it, WHEN, WHERE | **KDO / KDY / KDE** (WHO/WHEN/WHERE) |
| TestDesign support | Podpora designu testů | identifies HOW to test | **JAK** (HOW) |

> **Binding rule** (R-CAST-3 — promote alongside R-CAST-1/2 in next governance update): use the CO/KDO/KDY/KDE/JAK decomposition explicitly when categorising new MI-M-T entities or recon items. This is the original CAST author's canonical 5-question decomposition.

### §2b.3 CAST artefact-sequence (the canonical chain)

Per Vaněk slide "Návaznosti artefaktů testování" — the testing artefact links/dependencies:

| EN canonical | CS preferred | Description |
|---|---|---|
| Test Target List | Test Target List | "vše, CO se dá testovat" — everything THAT CAN BE tested; sourced from System Requirements + Use Case Model |
| Test Strategy List | Test Strategy List | Per-target-or-group strategy: WHO/WHEN/WHERE + test types |
| Test Cases | Test Cases | The "central control element" of testing (centrální řídící prvek); end of TestAnalysis; start of TestDesign |
| Test Scripts | Test Scripts | Sub-entities for executing a TC |
| Test Data | Test Data | Sub-entity |
| Test Procedures | Test Procedures | Sub-entity |
| Test Components | Test Components | Sub-entity (test-only components) |
| Test Environment | Test Environment | Sub-entity |
| Iteration Test Set | Iteration Test Set | Configured TestCaseList per stage/iteration → executed |

### §2b.4 CAST principles (the foundational rules)

| EN principle | CS preferred (Vaněk canonical) | Note |
|---|---|---|
| Everything originates from a registered impulse, not from "feeling" | Vše vzniká „na základě evidovaného podnětu" a ne na základě „pocitu" | **podnět** = impulse / stimulus — the canonical CAST trigger concept |
| Every item of any entity may contain child items | U každé položky jakékoliv entity se předpokládá, že může obsahovat dceřiné položky | hierarchical decomposition is a foundational pattern |
| Codes + paths (classes + their hierarchy) yield unique addressability across the framework | Prací s kódy a cestami (třídy a jejich hierarchie) je možno docílit stavu, kdy je každý element jednoznačně identifikovatelný v rámci celého frameworku | basis for `item_code` + `intern_tree_path` + `extern_tree_path` columns in MI-M-T schema |
| Different access patterns to the storage structures must be supported | Umožnit různé přístupy ke strukturám dat v úložištích | per-role / per-user views |
| All storages are unified — knowing one means knowing the others | Veškerá úložiště dat jsou unifikována – znalost jednoho úložiště dává znalost i ostatních úložišť | the basis for `ItemBase` block (the same 35 columns across every entity table) |
| Storages derive from one main template (which spawns the entity template) | Úložiště vycházejí z jedné hlavní šablony (ze které se vytvoří šablona entity) | template inheritance |
| Unified item-identification + description fields | Unifikovaná pole identifikace a popisu položky | (BB-1 base columns: `id`, `item_code`, `item_name`, `item_descr`, ...) |
| Unified item-management fields | Unifikovaná pole managementu položky | (`item_status`, `submitter_id`, `item_manager_id`, `item_submit_date`, ...) |
| 1+ entity-specific description fields | 1 a více polí pro popis položky v rámci šablony entity | (the per-table specific columns) |
| Unified "custom" fields in groups: descriptive | Unifikovaná „custom" pole — uživatelské atributy doplňující popis | (CAST `UsrDescrAttr[0-5]` slots) |
| Unified "custom" fields in groups: control + decision | Uživatelské atributy podporující rozhodnutí a řízení položek | (CAST `UsrCtrlAttr[0-5]` slots) |
| Unified "custom" fields in groups: correlation definition | Uživatelské atributy pro definici korelací položek | (CAST `Correlation` + `OblgtCorrWith…` slots) |
| Framework easily + rapidly extendable with new managed entity storages from the main template | Framework je snadno (a rychle) rozšiřitelný o další potřebná úložiště řízených entit vytvořením z hlavní šablony | the rationale for our `test_procedures`, `test_components`, `test_users`, `test_workload_models` deferred-but-templated tables |
| Value lists managed centrally vs locally | Hodnoty řízené číselníky: centrální (unifikované) — lokální (upravené) | maps to MI-M-T `value_lists` + `value_list_items` |
| Views on data per role or user | Pohledy na data dle rolí či uživatelů | the basis for `permission_tier` + `role_in_process` views |
| History of record changes | Historie změn záznamů | the basis for `item_status_history` + audit trail |
| The way of working leads to decision-making, not "guessing" | Způsob práce vede k rozhodování a ne k „tipování" | the framework's operational philosophy |
| The framework avoids "imposing" process changes from SW or UI limitations | Framework se snaží vyvarovat „vnucování" změn procesu testování, které jsou vyvolány omezeními použitého SW řešení a omezeními způsobu ovládání | guard against tool-driven distortion |
| Instead it imposes a systematic way of thinking and approach to control | „Vnucuje systematický způsob myšlení a přístup k řízení" | the positive-side mandate |

---

## §2c. Test Management vocabulary (from Vaněk 2006/2009 Test03-01-1)

Harvested from `Testing - resources/testing/DV/prezentace TM/Test03-01-1 (T-III ) Test Management.ppt`.

### §2c.1 Test Manager role definitions (4 facets)

| Facet (EN) | Facet (CS) |
|---|---|
| Test Management as control activities in the testing process domain | Test Management jako řídící aktivity v procesním oboru testování |
| Test Management as administration of test elements and testing | Test Management jako správa elementů testů a testování |
| Test Management as the Test Manager role's ability to correctly decide and lead | Test Management jako schopnosti role Test Manager správně rozhodovat a řídit |
| Test Management as the Test Manager role's ability to act socially + psychologically in the team and its surroundings | Test Management jako schopnosti role Test Manager sociálně a psychologicky působit v týmu testování a v jeho okolí |

### §2c.2 Plan / schedule / estimate distinction (Vaněk's three-way separation — binding)

| EN | CS preferred | Distinction note |
|---|---|---|
| Plan | Plán | Decision about what + how + sequence |
| Schedule (timeline) | Harmonogram | Time-axis projection of the plan; **harmonogram ≠ plán** (a schedule is not a plan) |
| Estimate | Odhad | Projection of effort/duration with confidence; **plán ≠ odhad** (a plan is not an estimate) |

> **Binding governance rule** (R-PLAN-1, draft): MI-M-T artefacts that talk about "planning" must distinguish all three. The Excel TestPlan template (`BOURACKA-TESTPLAN-vN.M.xlsx`) gets three separate sheets if any of the three is present: `05a_TestPlan` / `05b_TestSchedule` / `05c_TestEstimate`. (Currently `05_TestSets` collapses them; refine in next iteration.)

### §2c.3 Test Plan kinds (Vaněk distinction)

| EN | CS preferred | Notes |
|---|---|---|
| General Test Plan | Obecný testovací plán | Static; covers everything stable across cycles |
| Cycle Test Plan | Cyklový testovací plán | Per-cycle; replannable |

### §2c.4 Stakeholder needs vs wants (Vaněk's needs/wants distinction)

| EN | CS preferred | Notes |
|---|---|---|
| Stakeholder | Zákazník procesu testování / Stakeholder | "zákazníci a stakeholders procesu testování" |
| Need (genuine) | Potřeba | "potřeby, které kdo má směrem k testování" |
| Want (desire, not a need) | Chtíč | Vaněk explicitly: "vyčistěte je od přání, které nejsou potřebami – od „chtíčů"" — clean wants out of needs |

### §2c.5 Diligence — the third assessment dimension (Vaněk canonical)

CAST's three-dimensional priority assessment (per Vaněk Test Management slide "Co vítězí, Urgency nebo Severity?"):

| EN | CS preferred | Notes |
|---|---|---|
| Urgency (degree of urgency) | Urgency / míra naléhavosti | per `_config/PRIORITY-MATRIX-GOVERNANCE-v0.1.md` §1 — already in our matrix |
| Severity (degree of severity, risk if unmet) | Severity / míra závažnosti, rizika při nesplnění | per matrix — already in our matrix |
| Diligence (degree of attention, carefulness, care) | Diligence / míra pozornosti, pečlivosti, péče | the **third** dimension Vaněk introduces — currently rendered as "Attention" in our schema; canonical CAST term is **Diligence** (CS: Pozornost / Pečlivost / Péče) |

> **Promote in next governance pass:** the project's `attention_*` columns should be renamed `diligence_*` to honour the canonical CAST term. Current `attention` → `diligence` is a v0.2.x migration. Until then, document the mapping: project's "Attention" = CAST's "Diligence".

### §2c.6 Test Manager wisdom (Vaněk principles — quotable)

| EN | CS (Vaněk original) |
|---|---|
| Don't plan things you don't yet know — plan how you'll get to know them | Neplánuj věci, které zatím neznáš ...plánuj, jak se dobereš k jejich poznání a k jejich řešení |
| No battle plan survives first contact with the enemy | Žádný plán bitvy nepřežije první srážku s nepřítelem |
| When you don't know where you're sailing, no wind is good for you | Když nevíš, kam pluješ, není ti žádný vítr dobrý |
| Focus your testing effort — and refine the focus | Zaměřuj své úsilí v testování ...a zaměření zpřesňuj |
| Adapt prepared test sets to the current cycle's needs — and pick only the most necessary | Přizpůsob připravené sady testů potřebám aktuálního cyklu testování ...a vyber jen to nejnutnější |
| Track testing elements + related elements — and evaluate them | Sleduj elementy testování a elementy související ...a vyhodnocuj je |
| Don't wait to publish info — and use even unfavourable info to calm stakeholders (involve them with information) | Nečekej se zveřejněním informací ...a i nepříznivými informacemi uklidňuj stakeholders (informacemi je zapoj do dění) |
| A late decision is as if it weren't | Pozdní rozhodnutí jako by nebylo |
| A bad decision — wish it weren't | Špatné rozhodnutí kéž by nebylo |

These are excellent candidates for the *Testing Overdose* blog (per `MIM2000-BLOG-REORG-V0.1.md` §2.1) editorial seed.

---

## §2d. Analytical-source-artefact ↔ TestTarget derivation (binding)

> **Foundational principle (R-DERIVE-1, binding from v0.1.2):** A TestTarget is *derived from an analytical artefact*, not invented. Every TestTarget row carries `source_artefact_kind` + `source_artefact_ref` + `derivation_rule`. If no analytical artefact backs a candidate TestTarget, it must first be filed as a missing-artefact issue (typically against the analyst — Business Analyst / System Analyst / UX Designer / API Designer); the TestTarget enters scope only after the analytical input lands. This closes the "tester invents tests from feeling" failure mode and aligns with the CAST principle "podnět" (impulse) per §2b.4.

### §2d.1 Source artefact kinds — canonical catalogue

| Source kind (EN) | Source kind (CS) | Author role | Typical notation | TestTarget derivation rule |
|---|---|---|---|---|
| Use Case (UC) | Případ užití | Business / System Analyst | UML use-case diagram + UC specification (actor, goal, precondition, main flow, alternative flows, postcondition) | 1 TestTarget per UC + 1 per alternative flow + 1 per exception path |
| Business Process Model (BPM, BPMN) | Model byznys procesu | Business Analyst | BPMN 2.0 (pools, lanes, tasks, gateways, events) | 1 TestTarget per task + 1 per gateway decision branch + 1 per event-trigger handling |
| Sequence diagram (UML SD) | Sekvenční diagram | System Analyst / Designer | UML 2.x sequence (lifelines, messages, fragments) | 1 TestTarget per message exchange + 1 per opt/alt/loop fragment + 1 per response branch |
| Activity diagram (UML AD) | Activity diagram / Diagram aktivit | Analyst / Designer | UML 2.x activity (actions, decisions, forks, joins, swimlanes) | 1 TestTarget per action node + 1 per decision branch + 1 per fork/join coordination |
| State machine diagram (UML SM) | Stavový diagram | System Analyst | UML 2.x state machine (states, transitions, events, guards) | 1 TestTarget per state transition + 1 per guarded transition (per guard outcome) |
| Class / data model | Třídní / datový model | Data Architect | UML class diagram + ERD | 1 TestTarget per CRUD operation per entity + 1 per relationship-cardinality constraint + 1 per derived attribute |
| Screen design (mockup / wireframe / Figma) | Návrh obrazovky (maketa / drátěný model / Figma) | UX Designer | Figma / Sketch / hand mockup | 1 TestTarget per screen + 1 per interactive element (button, field, link, dropdown) + 1 per layout-state (loading / empty / error / populated) + 1 per viewport (mobile / tablet / desktop) |
| Form spec | Specifikace formuláře | Analyst / Designer | inline doc + screen + validation rules | 1 TestTarget per field + 1 per validation rule (required, format, range, cross-field) + 1 per submission outcome (success / each error class) |
| API interface (OpenAPI / contract) | API rozhraní (OpenAPI / kontrakt) | API Designer | OpenAPI 3.x / GraphQL schema / WSDL | 1 TestTarget per endpoint × method + 1 per response-status class (2xx, 4xx, 5xx) + 1 per documented schema variant |
| Integration / data-flow spec (DTO / DSO / DDO) | Integrační / datová specifikace (DTO/DSO/DDO) | Integration Architect | per DVA-2016 §5 | 1 TestTarget per data-flow direction + 1 per orchestration choreography hop + 1 per fire-&-forget vs request-response pattern |
| Non-functional requirement (NFR) | Nefunkční požadavek (NFP) | Architect / PM | text spec + measurable threshold | 1 TestTarget per NFR (one per FURPS+ dimension that the NFR addresses); see §2e + §2f |
| Architecture decision record (ADR) | Záznam architektonického rozhodnutí (ADR) | Architect | markdown ADR per Michael Nygard convention | 1 TestTarget per architecturally-significant decision that has runtime-observable consequences |
| Configuration / deployment unit | Konfigurace / jednotka nasazení | DevOps / Architect | per VUP §4.3.2c "Deployment Unit" / "Deployment Plan" | 1 TestTarget per deployment-unit smoke-readiness check + 1 per config-item validation |
| Build artefact | Build / sestavení | DevOps | per VUP §4.3.2c "Build" | 1 TestTarget per build smoke check |
| Glossary entry | Glosář / slovník | (this catalogue) | per VUP §4.3.2c "Glossary" | (terminology audit; meta-test: do all UI labels resolve to glossary entries?) |
| Existing defect / known issue | Existující závada / známý problém | (regression history) | per `08_Bugs` registry | 1 regression-TestTarget per fixed bug to prevent recurrence (R-FAIL-1 inverse) |
| Production telemetry / observed incident | Produkční telemetrie / pozorovaný incident | SRE / Operator | log lines, error reports, user feedback | 1 TestTarget per recurring incident pattern |

### §2d.2 Derivation columns on `test_targets` (schema impact)

Per R-DERIVE-1 the `test_targets` table gains 4 columns:

| Column | Type | CS label | Notes |
|---|---|---|---|
| `source_artefact_kind` | VARCHAR(40) | Druh zdrojového artefaktu | Enum sourced from §2d.1 — value-list `source_artefact_kinds` |
| `source_artefact_ref` | VARCHAR(255) | Odkaz na zdrojový artefakt | Path / URL / Figma frame ID / OpenAPI operationId / UC ID |
| `derivation_rule` | VARCHAR(80) | Pravidlo odvození | Per §2d.1 right column (e.g. "1 TT per UC alternative flow") |
| `source_artefact_author_role` | VARCHAR(40) | Role autora zdrojového artefaktu | Business Analyst / System Analyst / UX Designer / API Designer / Architect / SRE |

Migration `123_add_source_artefact_to_test_targets.sql` (queued for v0.2.x).

### §2d.3 Reverse traceability (binding)

Each analytical artefact MUST be reachable from its derived TestTargets. Reporting must answer: "for UC-CP-007, what TestTargets exist and what is their last verdict?" This is the **bidirectional traceability** that VUP §4.3.2c "Define Evaluation and Traceability" activity demands.

A summary view (`v_artefact_coverage`) ships in v0.2.x: per-source-artefact + per-FURPS+-dimension TestTarget count + verdict roll-up.

---

## §2e. FURPS+ quality dimensions (canonical Czech)

The FURPS+ taxonomy (Grady & Caswell 1992; ISO/IEC 25010 superset) is the binding quality-dimension catalogue for this project. Every Requirement carries one or more FURPS+ tags; every TestTarget addresses one or more FURPS+ dimensions; every TestCase verifies one or more FURPS+ dimensions on its TestTarget.

### §2e.1 FURPS+ canonical table

| Letter | EN canonical | CS preferred | CS variants / notes | Examples of measurable thresholds |
|---|---|---|---|---|
| **F** | Functionality | Funkcionalita | "Funkční vlastnost"; "Funkční chování" | feature presence; correctness against spec; data integrity; security |
| **U** | Usability | Použitelnost | "Uživatelská přívětivost"; "Ergonomie" | task-completion time; error rate per task; help-doc lookups; accessibility (WCAG); aesthetics |
| **R** | Reliability | Spolehlivost | "Bezporuchovost" — formal | MTBF; MTTR; availability %; failure rate; recoverability; fault tolerance |
| **P** | Performance | Výkonnost | "Výkonnostní vlastnost" | response time; throughput; concurrency; resource utilisation (CPU / mem / IO / network); scalability |
| **S** | Supportability | Udržovatelnost / Podporovatelnost | "Servisovatelnost"; "Podpora provozu" | maintainability; testability; deployability; configurability; localisation; observability |
| **+ (D)** | Design constraints | Designová omezení | "Omezení návrhu" | language/runtime constraints; architectural-style constraints; coding standards |
| **+ (I)** | Implementation constraints | Implementační omezení | "Omezení implementace" | required tools/libraries; team capability constraints |
| **+ (N)** | Interface constraints | Omezení rozhraní | "Omezení interakce s externími systémy" | required integration points; contract conformance |
| **+ (P_phys)** | Physical constraints | Fyzická omezení | "Hardware / prostorová / energetická omezení" | device, form-factor, power |
| **+ (L)** | Legal / regulatory | Právní / regulatorní | "Právní vyhovění"; "Regulatorní vyhovění (compliance)" | GDPR; sector regulation; license terms |

### §2e.2 FURPS+ ↔ ISO/IEC 25010 quick map

| FURPS+ | ISO/IEC 25010 product-quality characteristic |
|---|---|
| F | Functional Suitability (functional completeness / correctness / appropriateness) |
| U | Usability (appropriateness recognisability, learnability, operability, user error protection, UI aesthetics, accessibility) |
| R | Reliability (maturity, availability, fault tolerance, recoverability) |
| P | Performance Efficiency (time behaviour, resource utilisation, capacity) |
| S | Maintainability (modularity, reusability, analysability, modifiability, testability) + Portability (adaptability, installability, replaceability) |
| +D/+I | (Constraints — not part of 25010 product-quality model proper; covered as design/implementation rationale) |
| +N | Compatibility (co-existence, interoperability) |
| +P_phys | (Out of scope for 25010 software-quality; relevant for embedded / IoT) |
| +L | Security (confidentiality, integrity, non-repudiation, accountability, authenticity) — partial; legal/compliance is broader |

### §2e.3 FURPS+ enum on `requirements` + `test_targets` + `test_cases`

Migration `124_add_furps_to_requirements_targets_cases.sql`:

```
ALTER TABLE requirements    ADD COLUMN furps_dimensions VARCHAR(40);  -- comma-separated subset of {F,U,R,P,S,+D,+I,+N,+L,+P_phys}
ALTER TABLE test_targets    ADD COLUMN furps_dimensions VARCHAR(40);  -- subset addressed
ALTER TABLE test_cases      ADD COLUMN furps_dimensions VARCHAR(40);  -- subset verified
```

CS UI labels via translation tables. The Excel `00_README` legend documents the FURPS+ map.

---

## §2f. Cartesian governance — Requirement × FURPS+ → TestCase set expansion

> **Foundational principle (R-FURPS-1, binding from v0.1.2):** for every Requirement the test base is *expanded by Cartesian product* against the applicable FURPS+ dimensions. Each cell of the matrix Requirement × FURPS+ is one of: (a) a TestCase set scoped for that dimension, (b) explicitly N/A with a written justification, or (c) deferred (with the prioritised when). No cell is silent.
>
> **Foundational principle (R-EXPAND-1, binding from v0.1.2):** every cell that becomes a TestCase set MUST carry Severity + Urgency tags. The Sev × Urg → Pri matrix (per `_config/PRIORITY-MATRIX-GOVERNANCE-v0.1.md`) computes the Priority. Test base growth is *prioritised growth* — never an undifferentiated explosion. The reporting layer must surface "expansion pressure" (count of pending cells per Pri-class) so that operator can rebalance.

### §2f.1 The Cartesian matrix template

For each Requirement REQ-NNN:

|              | F | U | R | P | S | +D | +I | +N | +L | +P_phys |
|--------------|---|---|---|---|---|----|----|----|----|---------|
| REQ-NNN.F    | TC-set-F | — | — | — | — | — | — | — | — | — |
| REQ-NNN.U    | — | TC-set-U | — | — | — | — | — | — | — | — |
| REQ-NNN.R    | — | — | TC-set-R | — | — | — | — | — | — | — |
| (etc.)       | | | | | | | | | | |

In practice the matrix collapses to a single row per Requirement listing per-dimension TC-set IDs (or N/A + reason).

### §2f.2 Expansion governance flow

```
   Requirement enters scope
            ↓
   For each FURPS+ dimension:
       Is dimension applicable to this Requirement?
            ├── YES → propose TC-set candidate
            │          ↓
            │       Tag candidate with Severity (impact if dimension fails)
            │       Tag candidate with Urgency (when must this fail-mode be detected by)
            │       Compute Priority via Sev × Urg → Pri matrix
            │          ↓
            │       Pri ∈ {A,B,C} → enter test base; Pri = D → defer with timer
            └── NO  → mark cell N/A with one-line justification
            ↓
   Reporting roll-up surfaces:
     • Coverage: for REQ-NNN, how many FURPS+ dimensions have non-empty TC-sets?
     • Expansion pressure: count of pending Pri-A/B candidates not yet implemented
     • Justification audit: % of N/A cells with valid one-line reason
```

### §2f.3 Methodology binding (overlay)

The Cartesian matrix is methodology-agnostic at the rows/columns level; the *scheduling* of the resulting TC-sets follows the project's methodology (per §4 + §4.4):

| Methodology | TC-set scheduling unit | Cartesian-cell attribution |
|---|---|---|
| Agile | Sprint (within Epic, within Release) | Each TC-set cell pinned to a Sprint; Pri-A cells in early sprints, Pri-B in mid, Pri-C in stabilisation, Pri-D in backlog |
| Waterfall | Phase (Test sub-phase or per-Phase Gate) | Pri-A cells executed in primary Test Phase; Pri-B/C in regression sub-phase; Pri-D parked for next Release |
| UP / VUP | Iteration (within Phase, attached to Discipline Test activities) | Pri-A cells in earliest Construction iterations; Pri-B/C across remaining iterations; Pri-D parked for next Iteration Plan revision |
| Hybrid | per `methodology_blend` JSON | Cells attributed to whichever scheduling unit applies under the blend rule |

### §2f.4 Schema impact

Migration `125_add_furps_cartesian_governance.sql`:

```
CREATE TABLE requirement_furps_cells (
  id INT PRIMARY KEY,
  requirement_id INT NOT NULL REFERENCES requirements(id),
  furps_dimension VARCHAR(8) NOT NULL,    -- F | U | R | P | S | +D | +I | +N | +L | +P_phys
  cell_status VARCHAR(20) NOT NULL,       -- na | pending | active | deferred
  na_justification VARCHAR(500),          -- required if cell_status='na'
  test_case_set_id INT REFERENCES iteration_test_sets(id),  -- the TC-set produced from this cell
  severity CHAR(1) NOT NULL,              -- A/B/C/X
  urgency  CHAR(1) NOT NULL,              -- A/B/C/X
  priority CHAR(1) NOT NULL,              -- A/B/C/D (computed)
  scheduling_unit_kind VARCHAR(20),       -- sprint | phase | iteration | (per methodology)
  scheduling_unit_ref  VARCHAR(80),       -- sprint id / phase id / iteration id
  defer_reason VARCHAR(255),              -- required if cell_status='deferred'
  defer_until_iteration VARCHAR(40),
  created_at TIMESTAMP, updated_at TIMESTAMP
);
CREATE UNIQUE INDEX uq_req_furps ON requirement_furps_cells (requirement_id, furps_dimension);
```

### §2f.5 Reporting view (`v_furps_coverage`)

The reporting layer (per `_config/METHODOLOGY-MAPPING-V0.1.md` §4.5) surfaces:

| Report | Purpose |
|---|---|
| Coverage matrix | per Requirement × per FURPS+ dimension — colour-coded (green = active; amber = pending; red = pending Pri-A; grey = N/A justified; black = N/A unjustified) |
| Expansion pressure | count of pending cells per Pri-class; histogram per Sprint/Phase/Iteration |
| Justification audit | list of N/A cells lacking justification |
| Dimension neglect | FURPS+ dimensions with low coverage across the project's Requirements (signal that a quality angle is being systematically overlooked) |

### §2f.6 Coverage gating phase-in (NEW v0.1.4 — supersedes strict-from-day-1)

> **Foundational principle (R-DESIGN-1, reframed v0.1.4):** the Cartesian-cell coverage governance defined in §2f is enforced *progressively*, not strict-from-day-1. The validator's `coverage_rule_phase` setting per project gates how strictly missing-cell justification is enforced. This reframes (and supersedes) the strict-by-default reading of R-FURPS-1 + R-EXPAND-1 in v0.1.2 — gating ramps up as the TC base matures rather than blocking from the first commit.
>
> **Source convergence:** the 4-phase model is adopted from ThinkPad CP-SUPIN-05 `_specs/COVERAGE-RULE-STRATEGY-v0.1-CS.md`, which independently arrived at the same shape from delivery experience. MacBook governance accepts the phase-in as the operationally correct path — see `_config/SYNCHRO-MACBOOK-TO-OPUS-CP-SUPIN-06-2026-05-08.md` §2.2 row 3 ("ADOPT THINKPAD'S PHASE-IN").

The four enforcement phases:

| Phase | Trigger to advance | Validator behaviour | Gating scope | CS label |
|:--:|---|---|---|---|
| 0 — informational | new project | emits coverage report; no enforcement | none | informativní |
| 1 — soft warn | first TT base settles (≈ 20 TCs in scope) | warns on N/A cells lacking justification; commits proceed | advisory only | varovné upozornění |
| 2 — per-class gating | coverage > 60 % on Pri-A cells | BLOCKS commit if any Pri-A cell is undocumented (N/A without reason or pending without due-iteration) | Pri-A cells only | dílčí blokace |
| 3 — strict | release-candidate maturity | BLOCKS commit if any Pri-A *or* Pri-B cell is undocumented; Pri-C/D advisory | Pri-A + Pri-B | striktní blokace |

Schema impact (migration `131_add_coverage_rule_phase.sql`):

```
ALTER TABLE projects
  ADD COLUMN coverage_rule_phase TINYINT NOT NULL DEFAULT 0,
  ADD COLUMN coverage_rule_phase_set_at TIMESTAMP NULL,
  ADD COLUMN coverage_rule_phase_set_by VARCHAR(80) NULL;
-- 0 = informational (default for new projects)
-- 1 = soft warn
-- 2 = per-class gating (Pri-A)
-- 3 = strict (Pri-A + Pri-B)
```

Phase-advance discipline: the phase number SHALL only advance, never regress. A regression (e.g. v3 → v2) requires explicit ADR with stakeholder sign-off, captured in `coverage_rule_phase_regression_log` (sister table; not yet schema-modelled).

Reporting addition: `v_coverage_gating_state` view exposes per-project current phase + count of cells that would block at next phase advance + recommended next phase based on current coverage (advisory for the operator).

**Closes OQ-MB-04** (per SYNCHRO-MACBOOK-TO-OPUS §8). **Closes the strict-from-day-1 stance from v0.1.2.**

---

## §2g. Decoupled-versioning policy — independent tracks for schema, content, toolchain, release (NEW v0.1.4)

> **Foundational principle (R-DECOUPLED-1, binding from v0.1.4 — adopted from ThinkPad's universal pattern in CP-SUPIN-04/05):** components in a multi-deliverable project SHALL version independently along four tracks. The user-visible product release version is a *composite* — it pins specific schema/content/toolchain versions but does not constrain their independent evolution between releases. This supersedes any tacit assumption that everything in a project moves on a single SemVer.
>
> **Source:** ThinkPad's empirical practice in the bouračka-tests repo (see `_specs/from-macbook/SYNCHRO` reconciliation §2 row 5; the policy is universal — applies to any multi-deliverable project, not just Bouračka).

The four version tracks:

| Track | What it versions | Cadence | Example label |
|---|---|---|---|
| **Schema** | Excel workbook structure (sheets, columns, formulas) OR DB schema (tables, indexes, constraints) | bumps when shape changes | workbook `v0.4.2` → `v0.5.1`; DB schema `D-09` → `D-10` |
| **Content** | Rows in workbook (TC catalogue, recon entries, bug rows); seed-data in DB | bumps with each commit that adds/edits rows | content `2026-05-07` (date-tagged) |
| **Toolchain** | Validators, CLI tools, migration scripts | independent SemVer per tool | `validate_workbook v0.3.1`; `preship_audit v0.1` |
| **Release** | The user-visible bundle (`bouracka-tests-v0.5.0.zip`; `mim2000-theme-v1.16.0.zip`) — pins specific schema + content + toolchain versions | per delivery milestone | `v0.5.0` (pins schema v0.4.2 + content 2026-05-07 + toolchain set) |

Cross-track coupling rules (binding):
- A release SHALL declare the exact pinned versions of all three feeding tracks in its release manifest.
- Schema bumps that break content layout SHALL ship with a migration script (toolchain track) that auto-upgrades content; manual content rewrites are an anti-pattern.
- Toolchain SHALL be backward-compatible across at least one schema-major version (e.g. validator v0.3.x SHALL accept both schema v0.4 and v0.5 inputs).

Schema impact (Bouračka workbook): the existing `bumpworkbook_version.py` already implements this pattern; add a release-manifest JSON shape per release that explicitly pins all three tracks. No DB migration on the MI-M-T side — this is a project-discipline rule, not a data shape.

Application targets:
- `bouracka-tests/` (already practising this implicitly; formalise the manifest)
- mim2000/zemla/bodyterapie theme releases (theme version + content version + helper-script version)
- MI-M-T product itself once it ships (PHP layer + Python layer + DB schema as three tracks)

---

## §2h. V-model TestTarget assembly layer — transposition basis sister to FURPS+ (NEW v0.1.4)

> **Foundational principle (R-VMODEL-1, binding from v0.1.4):** the FURPS+ Cartesian (§2f) is *one* transposition basis on the requirement space — same requirements sliced by quality dimension. The V-model TestTarget assembly layer is the *sister* basis — same requirements sliced by abstraction layer (the V-model's right-hand side). Both bases are non-redundant; for richer coverage analysis, every TT carries both an `furps_dimensions` array AND a `tt_assembly_layer` discriminator.
>
> **Source convergence:** the 4-layer assembly model is adopted from ThinkPad CP-SUPIN-05 `_specs/VMODEL-ASSEMBLY-TT-MAPPING-v0.1-CS.md`. Independent confirmation (per SYNCHRO §2.1 row 1) that MacBook's Cartesian governance and ThinkPad's V-model assembly model are *operationally equivalent transposition operators on different bases* — different cuts, same requirement space.

The four assembly layers (V-model right-hand side, bottom-up):

| Layer code | EN canonical | CS preferred | Granularity | When this is the right basis |
|:--:|---|---|---|---|
| **FUNC** | Functional behaviour | Funkční chování | one business function (e.g. "submit accident report") | when the requirement specifies a behaviour the system must perform; the test asks "does it do the thing?" |
| **SCRN** | Screen / page | Obrazovka / stránka | one UI screen or page route | when the requirement is layout/navigation/render-driven; the test asks "is the screen correct?" |
| **LOV** | List-of-values | Seznam hodnot | one codelist (dropdown options, enum table content) | when the requirement constrains a value set (mobile prefix list, OP regex, ČKP codelists); the test asks "are the allowed values right?" |
| **ACTV** | Activity / workflow step | Aktivita / krok pracovního postupu | one process activity in a multi-step workflow | when the requirement defines a step in a longer sequence; the test asks "does this step transition correctly given inputs?" |

The two bases compose: every TT carries both `furps_dimensions` (which quality dimension(s) the TT addresses — F/U/R/P/S/+D/+I/+N/+L/+P_phys) AND `tt_assembly_layer` (which abstraction layer the TT operates at — FUNC/SCRN/LOV/ACTV). A coverage view that pivots on (`furps_dimension` × `tt_assembly_layer`) is richer than either alone:

| | FUNC | SCRN | LOV | ACTV |
|---|---|---|---|---|
| F (Functionality) | core BAU TTs | render correctness | codelist completeness | step transitions |
| U (Usability) | task completion rate | layout · accessibility | codelist label clarity | step error recovery |
| R (Reliability) | error-recovery TTs | rerender stability | codelist staleness | step idempotency |
| P (Performance) | function latency | render time | codelist fetch latency | step throughput |
| S (Supportability) | logging on the function | screen telemetry | codelist refresh hooks | step audit trail |

Most cells will be empty for any given Requirement; the matrix's value is in surfacing *which* are populated and which legitimately N/A — same governance as §2f, just on the second basis.

### §2h.1 Worked example — R-CONFIRM-1 instance from CP-SUPIN-05 cross-framework parity (NEW v0.1.4 — folded 2026-05-08 from `_specs/SYNCHRO-OPUS-FROM-SONNET-CP-SUPIN-05-2026-05-08.md` §5 medium #6)

> **R-CONFIRM-1 fires here (per `_config/METHODOLOGY-MAPPING-V0.1.md` AMENDMENT 2026-05-08 §4):** ThinkPad-Sonnet's CP-SUPIN-05 cross-framework parity port (commit `5c865c8` on branch `cp-supin-05-cross-framework-parity`, 2026-05-08 16:02) introduced 8 new TT codes using the FUNC/SCRN/LOV/ACTV/E2E nomenclature *independently of MacBook governance work*. Sonnet branched from `main` (v0.5.0), not from MacBook's `macbook/cp-supin-06-prep-2026-05-08` PR — so MacBook's catalogue v0.1.4 §2h was NOT visible during the port. Independent observers reaching the same nomenclature is operational confirmation that the 4-layer (+ E2E meta-layer) model is right.

The 8 TT codes from the port (mapping to V-model assembly layers):

| TT code | Test code | V-model layer | What it tests | Source spec section |
|---|---|:--:|---|---|
| `TT-FUNC-rpRegex` | TC-CP-A2-ALT-1 | **FUNC** | ŘP regex validation as a functional behaviour | parity-execution §4.A.ALT-1 |
| `TT-FUNC-gdprConsent` | TC-CP-A2-ALT-4 | **FUNC** | GDPR consent gate as functional pre-condition | parity-execution §4.A.ALT-4 |
| `TT-SCRN-predvolba421` | TC-CP-A2-ALT-5 | **SCRN** | Slovak prefix dropdown render + selection | parity-execution §4.A.ALT-5 |
| `TT-SCRN-policeCard` | TC-CP-A2-ALT-6 | **SCRN** | "Škoda přesahuje 200 000 Kč" police-card accordion | parity-execution §4.A.ALT-6 |
| `TT-SCRN-demoBanner` | TC-CP-A2-ALT-8 | **SCRN** | DEMO branch banner static visibility | parity-execution §4.A.ALT-8 |
| `TT-ACTV-postReports` | TC-CP-A2-ALT-9 | **ACTV** | POST `/api/reports` workflow step (drift-aware soft assertion) | parity-execution §4.A.ALT-9 |
| `TT-ACTV-spaPostProbe` | TC-CP-A2-ALT-10 | **ACTV** | SPA-driven POST capture (network probe activity) | parity-execution §4.A.ALT-10 |
| `TT-E2E-fullHappyDay` | TC-CP-A1-MAIN-DEMO | **E2E** *(meta)* | Full 15-phase happy-day journey (composes FUNC + SCRN + ACTV across the workflow) | parity-execution §3 + §4.A1 |

> **5th meta-layer introduced (R-VMODEL-2, binding from v0.1.4):** in addition to the 4 base layers (FUNC/SCRN/LOV/ACTV — *one* layer per TT), the **E2E meta-layer** denotes TTs that *span* multiple base layers as a single composite test. E2E TTs are not peers of the base layers; they are *composition operators* on them. Schema impact: the `tt_assembly_layer` column SHALL accept `E2E` as an additional value, and a sister column `tt_e2e_composes` (nullable JSON array) SHALL list the base-layer TT codes the E2E test composes (so coverage analysis can debit/credit appropriately — an E2E test counts as a soft credit on each composed base TT, not as a base-layer credit on its own).

`covers()` annotation discipline (per Sonnet's port pattern in `cypress/support/data-loader.ts` + `selenium/helpers/data_loader.py`): each test SHALL declare which TT codes it covers via a per-framework `covers([...])` decorator/call. The covers list is the *executable manifest* of the V-model TT assembly map. Workbook v0.5.1 `15_VModelAssemblyMap` sheet pulls this list from the test source as its content seed.

| Layer | Examples from CP-SUPIN-05 port | Cross-axis FURPS+ overlap (typical) |
|:--:|---|---|
| FUNC | rpRegex, gdprConsent | F (validation), R (regex correctness across edge cases) |
| SCRN | policeCard, predvolba421, demoBanner | F (render), U (label clarity) |
| LOV | (none in this port — but ALT-5 dropdown values map here on a deeper port) | F (codelist completeness), R (codelist staleness) |
| ACTV | postReports, spaPostProbe | F (activity executes), P (activity latency), R (activity idempotency under drift) |
| E2E *(meta)* | fullHappyDay | F + U + P composed across the journey; flakiness signal aggregates here |

Schema impact (migration `132_add_tt_assembly_layer.sql` — extended for E2E meta-layer):

```
ALTER TABLE test_targets
  ADD COLUMN tt_assembly_layer VARCHAR(8) NULL,    -- FUNC | SCRN | LOV | ACTV | E2E (nullable for legacy)
  ADD COLUMN tt_assembly_ref   VARCHAR(120) NULL,  -- e.g. "screen:policeCard" / "actv:spaPostProbe" / "e2e:fullHappyDay"
  ADD COLUMN tt_e2e_composes   JSON NULL;          -- only for tt_assembly_layer='E2E'; array of TT-codes composed
CREATE INDEX ix_tt_assembly_layer ON test_targets (tt_assembly_layer);
```

Bouračka workbook impact: ThinkPad's planned `15_VModelAssemblyMap` sheet (per `_specs/CP-SUPIN-05-PLAN-CS.md` §5.2) is the operational realisation of this principle. MacBook's complementary `01a_AnalysisTransposition` sheet (per `_config/METH-REFINE-TESTANALYSIS-TESTDESIGN-v0.1.md` §6.1) is the FURPS+-axis transposition. Both sheets land together in workbook v0.5.1 per SYNCHRO §2.2 row 1 ("DO BOTH"). The 8 TT codes above are seed content for `15_VModelAssemblyMap` — verbatim from Sonnet's executable port.

---

## §3. CAST · MI-M-T core entities (the static layer)

Per `_config/METHODOLOGY-MAPPING-V0.1.md` §1: these are **methodology-agnostic**.

| EN canonical | CS preferred | CS variants / notes | MI-M-T table |
|---|---|---|---|
| Stakeholder | Zainteresovaná strana | "Aktér" (when role-driven); "Stakeholder" — common in EN-loanword codebases | (users with role) |
| Requirement | Požadavek | "Akceptační kritérium" if expressed as criterion | requirements.yaml |
| Test target | Testový cíl | per §1 | test_targets |
| Test case | Testovací případ | per §1 | test_cases |
| Test step | Krok testu | per §1 | test_case_phases / steps |
| Test data | Testovací data | per §1 | test_data |
| Test procedure | Testovací postup | "Postup testu" | test_procedures (deferred) |
| Test component | Testová komponenta | (component used only for testing; not part of product) | test_components (deferred) |
| Test environment | Testovací prostředí | per §1 | test_environments |
| Test user | Testový uživatel | (simulated user identity; ≠ real user) | test_users (deferred) |
| Test workload | Testová zátěž | "Zátěžový model" | test_workload_models (deferred) |
| Master test set | Hlavní testovací sada | "Hlavní sada testů"; "Knihovna testů" — descriptive | iteration_test_sets (the master is one type) |
| Iteration test set | Iterační testovací sada | "Sprintová sada" (Agile); "Fázová sada" (Waterfall) | iteration_test_sets |
| Test run | Testovací běh | per §1 | test_runs |
| Test run result | Výsledek testovacího běhu | "Výsledek testu" — for individual case-in-run | test_run_results |
| Evidence | Doklad | "Důkaz" — formal/legal; "Doklad o vykonání testu" — full | item_attachments + history |
| Item status | Stav položky | "Stav" — short form | item_status |
| Item code | Kód položky | "Identifikátor položky"; "ID" — informal | item_code |

### §3.1 12-state lifecycle (item_status enum) — CS labels

| EN canonical | CS preferred | Notes |
|---|---|---|
| new | nová | feminine "položka" → "nová"; if "stav" → "nový" |
| in-analysis | v analýze | "analyzuje se" — verb form |
| confirmed | potvrzená | "schválená" — when context = approval |
| in-progress | rozpracovaná | "v práci"; "probíhá" |
| implemented | implementovaná | "hotová" — colloquial |
| verifying | ověřuje se | "ve verifikaci" |
| passed | prošla | "úspěšně dokončená" |
| failed | selhala | "neuspěla" |
| closed | uzavřená | "ukončená"; "vyřízená" |
| cancelled | zrušená | "stornovaná" — formal |
| duplicate | duplikát | "duplicitní" — adjective form |
| deferred | odložená | "posunutá" |

### §3.2 Severity / priority / attention enums — CS labels

| EN | CS | Notes |
|----|----|----|
| Severity A (major) | Závažnost A (kritická) | "kritická" / "vysoká" |
| Severity B (standard) | Závažnost B (standardní) | "běžná" |
| Severity C (minor) | Závažnost C (drobná) | "nízká"; "kosmetická" if cosmetic |
| Severity X (undefined) | Závažnost X (nedefinovaná) | |
| Priority H (high) | Priorita H (vysoká) | per CAST H/M/L; project uses A/B/C per Sev × Urg matrix |
| Priority M (medium) | Priorita M (střední) | |
| Priority L (low) | Priorita L (nízká) | |
| Attention P (pedantic) | Pozornost P (pedantická) | per CAST attention scale |
| Attention S (standard) | Pozornost S (standardní) | |
| Attention I (informal) | Pozornost I (neformální) | |
| Priority A (computed) | Priorita A (kritická) | per `PRIORITY-MATRIX-GOVERNANCE` matrix |
| Priority B (computed) | Priorita B (standardní) | |
| Priority C (computed) | Priorita C (nízká) | |
| Priority D (undefined) | Priorita D (nedefinovaná) | |

---

## §4. Methodology layer — Agile · Waterfall · Unified Process (CS canonical)

Per `_config/METHODOLOGY-MAPPING-V0.1.md` — these are *process-layer* concepts; they MUST NOT be substituted for CAST static entities (R-METH-1).

### §4.1 Agile

| EN | CS preferred | CS variants / notes |
|---|---|---|
| Initiative | Iniciativa | "Záměr"; "Program" |
| Epic | Epic | (CZ Agile retains EN; "Eposové téma" — academic, not used) |
| Story | Story | (CZ Agile retains EN; "Uživatelský příběh" — formal) |
| Task | Úloha | "Úkol"; "Task" — common in CZ codebases |
| Subtask | Podúloha | "Podúkol" |
| Sprint | Sprint | (EN retained universally) |
| Sprint planning | Plánování sprintu | "Sprint planning" — also common |
| Sprint review | Sprint review | "Hodnocení sprintu" |
| Sprint retrospective | Retrospektiva sprintu | "Retro" — colloquial |
| Backlog | Backlog | "Zásobník úloh" — academic |
| Product owner | Vlastník produktu | "Product owner" — universal |
| Scrum master | Scrum master | (EN universal) |
| Definition of done | Definice hotovosti | "DoD" — common |
| Definition of ready | Definice připravenosti | "DoR" |
| Velocity | Rychlost (velocity) | (EN retained) |
| Story point | Story point | (EN retained) |
| Burndown | Burndown | "Spalovací graf" — descriptive, rarely used |

### §4.2 Waterfall

| EN | CS preferred | CS variants / notes |
|---|---|---|
| Waterfall (model) | Vodopádový model | "Waterfall" — also retained |
| Phase | Fáze | (the Waterfall block) |
| Sub-phase | Podfáze | |
| Gate | Brána | "Milník" — when gate = decision milestone; ČSN form: "Schvalovací brána" |
| Gate review | Bránová kontrola | "Schválení brány" |
| Deliverable | Výstup | "Předávaný výstup"; "Deliverable" — common |
| Milestone | Milník | (universal) |
| Sign-off | Schválení | "Akceptace" |
| Requirements (phase) | Specifikace požadavků | "Fáze požadavků" |
| Design (phase) | Návrh | "Fáze návrhu" |
| Implementation (phase) | Implementace | |
| Testing (phase) | Testování | per §1 |
| Deployment (phase) | Nasazení | |
| Maintenance (phase) | Údržba | "Provoz a údržba" |

### §4.3 Unified Process (UP / VUP — Versatile Unified Process) — Vaněk + Kukol canon

> **Source:** `Testing - resources/testing/DV/VUP/_VUP/` — Enterprise Architect HTML export, Vaněk + Kukol 2007 (Raiffeisen BANK adaptation). VUP is **the** authoritative Czech UP rendering for this project — it overrides any generic RUP translation. VUP includes a fully developed Test Discipline (which the v0.2 cycle's Track NUM + CLIENT-PILOT-SUPIN inherit).

#### §4.3.1 UP phases (4 canonical)

| EN | CS preferred | CS variants / notes |
|---|---|---|
| Inception | Zahájení | "Iniciace" — if user prefers; "Počátek" — informal |
| Elaboration | Rozpracování | "Návrhová fáze" — descriptive |
| Construction | Konstrukce | "Budování"; "Realizace" |
| Transition | Předání | "Nasazení" — overlaps with Waterfall; "Předávací fáze" — disambiguated |

#### §4.3.2 UP iterations + workflows (disciplines)

| EN | CS preferred | CS variants / notes |
|---|---|---|
| Iteration | Iterace | (universal) |
| Workflow (UP discipline) | Disciplína | "Pracovní postup" — direct translation; UP/RUP literature settled on "Disciplína" |
| Activity | Aktivita | "Činnost" |
| Artifact | Artefakt | "Výstupní artefakt"; "Pracovní produkt" — RUP-specific |
| Business modeling | Modelování byznysu | "Modelování obchodních procesů" |
| Requirements (workflow) | Požadavky | (workflow name; same as the activity) |
| Analysis & design | Analýza a návrh | |
| Implementation | Implementace | |
| Test (workflow) | Testování | |
| Deployment | Nasazení | |
| Configuration & change management | Správa konfigurací a změn | |
| Project management | Řízení projektu | |
| Environment | Prostředí | (UP-specific: tooling + infrastructure) |

#### §4.3.2b VUP Disciplines — the actual 10 disciplines from VUP HTML

VUP defines **10 disciplines** (per `EARoot/.../Disciplines/*.htm`):

| # | EN canonical (VUP) | CS preferred | Notes |
|---|---|---|---|
| 1 | Discipline Business Modeling | Disciplína Modelování byznysu | scope of business processes |
| 2 | Discipline Requirements | Disciplína Požadavky | needs → requirements; Use Cases; vision |
| 3 | Discipline Design | Disciplína Návrh | architecture; analysis & design |
| 4 | Discipline Implementation | Disciplína Implementace | code; build; integration |
| 5 | Discipline Test | Disciplína Test | the full test workflow — Aim Test, Compile Master Test Set, Execute Cycle Test Set, Exit Test Cycle, etc. |
| 6 | Discipline Deployment | Disciplína Nasazení | production rollout |
| 7 | Discipline Configuration | Disciplína Konfigurace | configuration management; baselines |
| 8 | Discipline Issue Management (Change Management) | Disciplína Správa změn (Issue Management) | the change-control workflow |
| 9 | Discipline Process Controlling | Disciplína Řízení procesu | meta-discipline: controlling the development process itself |
| 10 | Discipline Project Management | Disciplína Řízení projektu | classical PM discipline |
| (env) | Discipline Project Environment | Disciplína Prostředí projektu | tooling + workspace |

#### §4.3.2c VUP Test Discipline — activities + artifacts (canonical names)

From `EARoot/.../Discipline Test/*.htm`. These are the canonical activities the test workflow contains:

| EN (VUP canonical) | CS preferred (Vaněk-style) | Notes |
|---|---|---|
| Aim Test | Cílit test / Zaměřit testování | per Test Management slide "zaměřuj své úsilí" |
| Audit Test Process | Auditovat proces testování | quality of the test process itself |
| Capture a Common Vocabulary | Zachytit společný slovník | the activity that PRODUCES this catalogue |
| Compile Master Test Set | Sestavit hlavní testovací sadu | builds the Master Test Set from TestCases |
| Define Test Approach Scheme | Definovat schéma testovacího přístupu | high-level approach |
| Define Evaluation and Traceability | Definovat hodnocení a sledovatelnost | metrics + traceability matrix |
| Design Test Elements | Navrhnout testovací elementy | the actual TC + Script + Data + Procedure + Component design |
| Design Test Lab | Navrhnout testovací laboratoř | environment + tooling design |
| Design Testability Elements | Navrhnout elementy testovatelnosti | designing the testability of the system itself |
| Determine Logical Test Structure | Určit logickou strukturu testů | hierarchy of test artefacts |
| Estimate and Schedule Tests | Odhadnout a naplánovat testy | per §2c.2 distinction (estimate ≠ plan ≠ schedule) |
| Evaluate Test Results and Quality of Test Process | Vyhodnotit výsledky testů a kvalitu procesu testování | combined: result evaluation + meta-evaluation |
| Execute Cycle Test Set | Vykonat cyklovou testovací sadu | the actual test execution |
| Exit Test Cycle | Ukončit testovací cyklus | gate decision: when to stop the cycle |
| Identify Test Targets and Tested Product Units | Identifikovat testové cíle a testované produktové jednotky | the TestAnalysis activity |
| Implement Test Elements | Implementovat testovací elementy | code/script the designed elements |
| Implement Test Lab | Implementovat testovací laboratoř | provision environment |
| Implement Testability Elements | Implementovat elementy testovatelnosti | hooks built into the SUT |
| Improve Estimation and Scheduling of Tests | Zlepšit odhady a plán testů | iterate on §2c.2 over time |

VUP **artefact** types observed:

| EN (VUP canonical) | CS preferred | MI-M-T mapping |
|---|---|---|
| Bill of Materials | Soupis položek (BoM) | (related to release content) |
| Build | Build / Sestavení | the artefact `build_under_test` ref in `test_runs` |
| Code-based Coverage Summary | Souhrn pokrytí kódu | reporting metric |
| Context Sensitive Help | Kontextová nápověda | (UI artefact) |
| Cycle Test Set | Cyklová testovací sada | maps to MI-M-T `iteration_test_sets` |
| Deployment Plan | Plán nasazení | release artefact |
| Deployment Unit | Jednotka nasazení | release artefact |
| Developer Test | Test vývojáře | unit test artefact |
| Developer Test Log | Záznam testů vývojáře | test_run_results subset |
| End User Support Material | Podpůrné materiály pro koncové uživatele | docs |
| Execution Test Data Set | Sada vykonávacích testovacích dat | maps to MI-M-T `test_data` (exec phase) |
| Expected Test Data Set | Sada očekávaných testovacích dat | the expected-results data |
| Glossary | Slovník | a vocabulary artefact (this catalogue is one!) |
| Installation Artifacts | Instalační artefakty | release artefact |
| Installation Guide | Instalační příručka | docs |
| Integration Build Plan | Plán integračního buildu | build pipeline |
| Master Test Set | Hlavní testovací sada | maps to MI-M-T `iteration_test_sets` (master is one type) |

VUP **role** types observed (Process-* roles per Discipline Test):

| EN (VUP) | CS preferred | Notes |
|---|---|---|
| Process Creator | Tvůrce procesu | who designed the process |
| Process Owner | Vlastník procesu | who is accountable for it |
| Process Performer | Vykonavatel procesu | who runs it |
| Process Specialist | Specialista procesu | subject-matter expert |

VUP **test labs** observed (per `EARoot/.../*Lab*.htm`):

| EN (VUP) | CS preferred |
|---|---|
| Common Test Lab | Společná testovací laboratoř |
| Design Test Lab | Návrhová testovací laboratoř |
| Development Lab | Vývojová laboratoř |
| Development Patch Test Lab | Laboratoř pro patch-testy ve vývoji |

VUP **principles** (the "10 Key Test Principles" — VUP file titled exactly that) — to be enumerated in v0.1.x once the corresponding HTML's body text is unpacked.

### §4.4 Methodology-aware planning attribution (where TC-sets get scheduled)

Cross-reference for §2f.3 — the *scheduling unit* for any TestCase set produced by Cartesian Requirement × FURPS+ expansion is determined by the project's methodology:

| Methodology | Top-level planning unit | Mid-level | Leaf-level (where TC-sets attach) | CS canonical | Notes |
|---|---|---|---|---|---|
| Agile | Release | Epic | Sprint | Vydání → Epic → Sprint | TC-sets pinned to Sprints; Pri-A early sprints; Pri-D in product backlog |
| Waterfall | Release / Project | Phase (Requirements / Design / Test / Deploy) | Test sub-phase OR Gate Review | Vydání → Fáze → (Test sub-phase / Schvalovací brána) | TC-sets executed in Test Phase; Pri-A blocks Gate exit |
| UP / VUP | Phase (Inception / Elaboration / Construction / Transition) | Iteration | Discipline Test activity (per §4.3.2c) | Etapa → Iterace → Aktivita disciplíny Test | TC-sets per Iteration; Pri-A in earliest Construction iterations |
| Hybrid | per `methodology_blend` JSON | per blend | per blend | (mixed) | Operator chooses per-cell where the TC-set lives |

> **Binding note (R-PLAN-2, draft alongside R-PLAN-1):** the `requirement_furps_cells.scheduling_unit_kind` column (per §2f.4) MUST match the project's `projects.methodology` setting — a project tagged 'agile' cannot have cells with `scheduling_unit_kind='phase'`. Validation enforced at insert time.

#### §4.3.3 UP phase-boundary reviews (LCO / LCA / IOC / PR)

| EN | CS preferred | Phase boundary |
|---|---|---|
| LCO — Life-Cycle Objectives | Cíle životního cyklu | end of Inception |
| LCA — Life-Cycle Architecture | Architektura životního cyklu | end of Elaboration |
| IOC — Initial Operational Capability | Počáteční provozní způsobilost | end of Construction |
| PR — Product Release | Vydání produktu | end of Transition |

---

## §5. Architecture · Integration · Data-flow terms (DVA-2016 canon)

From DVA-2016 (Dušan Vaněk) — the user's authoritative Czech enterprise-architecture vocabulary.

| EN canonical | CS preferred | CS variants / notes |
|---|---|---|
| Consumer | Konzument | (per DVA slide 2) |
| Provider | Poskytovatel | (per DVA slide 2) |
| Data flow | Tok dat | (per DVA slide 3) |
| Data Transfer Object (DTO) | DTO — datový přenosový objekt | (DVA slide 3 + 14) — "datový objekt k přenosu" |
| Data Stored Object (DSO) | DSO — datový uchovávaný objekt | (DVA slide 14) — "datový objekt k uložení" |
| Data Delivery Object (DDO) | DDO — datový dodávkový objekt | (DVA slide 2 + 14) — "datový objekt k dodání" |
| Functionality | Funkcionalita | "Funkčnost" — descriptive |
| System feature | Funkce systému | "Vlastnost systému"; "Feature" — EN retained |
| Foreign system | Cizí systém | (DVA slide 3) |
| Owns the database | Vlastní databázi | (DVA slide 3) |
| Completes (DTO) | Sestavuje (DTO) | "Vyplňuje DTO" — alternative; per DVA "completes" |
| Utilises (DTO) | Používá (DTO) | "Spotřebovává DTO"; "Konzumuje DTO" |
| Trigger | Spuštění | "Trigger" — EN retained in CZ practice |
| Trigger by time | Časem spuštěné | "Naplánované spuštění" |
| Trigger by condition | Podmínkou spuštěné | "Spuštění při podmínce" |
| Trigger by request | Žádostí spuštěné | "Spuštění na vyžádání" |
| Request | Žádost / požadavek | "Request" — EN retained |
| Response | Odpověď | (universal) |
| Request-response | Žádost-odpověď | "Synchronní výměna" |
| Fire & forget | Fire & forget | "Pošli a zapomeň" — descriptive; "Asynchronní notifikace" — formal (per DVA slide 4) |
| Orchestrated (data flow) | Orchestrovaný | "Orchestrace" — noun (per DVA slide 4) |
| Choreographed (data flow) | Choreografovaný | "Choreografie" — noun; "Choreograf" — the orchestrating service (per DVA slide 4) |
| Cooperation pattern | Vzor spolupráce | "Paterny spolupráce" (per DVA slide 5 — note: "paterny" = anglicism for "patterns") |
| ECB pattern (Entity-Control-Boundary) | ECB vzor (Entita-Řízení-Hranice) | (per DVA slide 11 — "vzdálená podobnost s ECB konceptem") |
| Microservice | Mikroslužba | "Microservice" — EN retained |
| Adapter | Adaptér | "Konektor" — for connector-as-such; |
| Connector | Konektor | (universal) |
| Integration | Integrace | |
| Endpoint | Koncový bod | "Endpoint" — EN retained universally |
| API | API | (universal) |
| REST | REST | (universal) |
| SOAP | SOAP | (universal) |
| Webhook | Webhook | (universal) |
| Contract (interface) | Kontrakt | "Smlouva" — too legal; "Rozhraní" — for interface-as-such |
| Schema | Schéma | (universal) |
| Mapping | Mapování | |

---

## §6. SUPIN / Bouračka campaign terms (project-specific)

| EN canonical | CS preferred | CS variants / notes |
|---|---|---|
| Bouračka | Bouračka | (Czech colloquial for "fender bender" / "car crash"; product name; lowercase first letter when not at sentence start) |
| Test environment (TEST) | Testovací prostředí (TEST) | full URL `tst.bouracka.cz` |
| Test environment (DEMO) | Demo prostředí (DEMO) | full URL `tst.demo.bouracka.cz`; "DEMO pro autoškoly" — descriptive |
| Driving school | Autoškola | (universal) |
| Tester | Tester | "Testovač" — formal; "Testerka" — feminine |
| QA engineer | QA inženýr | "Inženýr kvality"; "QA inženýrka" — feminine |
| Test analyst | Test analytik | "Analytik testování"; feminine "analytička" |
| Test designer | Test designer | (EN retained); "Návrhář testů" — descriptive |
| Test executor | Vykonavatel testu | "Tester provádějící běh"; for an automated context: "Spouštěč testů" |
| Damage report | Hlášení škody | (likely Bouračka primary user-journey; "Nahlášení nehody" — alternative) |
| Driver | Řidič | feminine "Řidička" |
| Licence plate | Registrační značka (RZ) | "SPZ" — historical/colloquial |
| Insurance company | Pojišťovna | |
| Service partner | Servisní partner | "Smluvní servis" |
| Quote / estimate | Cenová nabídka | "Kalkulace" |
| Browser-based application | Aplikace v prohlížeči | "Webová aplikace" — broader; "Web app" — EN retained |
| Mobile-first | Mobile-first | "Mobilní zařízení primárně" — descriptive; EN retained |
| Touch target | Cíl dotyku | "Klikací plocha" — vernacular; rarely used in CZ web docs |
| Viewport | Viewport | (EN retained universally) |
| Responsive design | Responzivní design | |

---

## §7. MI-M-T product · 3-fold-path content terms

| EN canonical | CS preferred | Notes |
|---|---|---|
| MI-M-T | MI-M-T | (acronym retained in both languages) |
| Meta Informed/Inferred/Integrated Measurement (which do) Testing | Meta-informované/odvozené/integrované měření, jež provádí Testování | (per `MANIFEST.yaml` mi_m_t.full_name; CS rendering for About-page footers) |
| Methodology for Integrated Manual Testing | Metodologie pro integrované manuální testování | (legacy / historical reference only — superseded; appears only in supersession notes) |
| Three-mode deployment | Tři režimy nasazení | per `OPUS-CYCLE-v0.2-MASTER.md` §1.2 |
| Mode 1 — Replacement | Režim 1 — Náhrada | (replaces JIRA / Redmine / ADO) |
| Mode 2 — Integrator | Režim 2 — Integrátor | (overlay on existing tracker — current PoC target) |
| Mode 3 — LLM TDD | Režim 3 — TDD s LLM | "TDD s podporou LLM"; "Deterministická testovací báze pro LLM" — descriptive |
| Testbase | Testovací báze | "Testbase" — EN retained in technical contexts |
| WorkPackage / Work Package | Pracovní balíček | (per R-METH-4 — preferred neutral term for static work units) |
| Initiative | Iniciativa | (alternative neutral term per OQ-METH-06) |
| Programme of Work | Pracovní program | "Program prací" — formal |
| 3-fold-path | Trojí cesta | (project name retains EN form; "trojí cesta" used in CS prose only; per `CLAUDE.md` "Mind/Spirit/Body") |
| Mind | Mysl | (per CLAUDE.md topology) |
| Spirit | Duch | "Duchovno" — adjectival form |
| Body | Tělo | (universal) |
| Buddhadharma | Buddhadharma | (term retained; Sanskrit-derived; not translated) |
| Zen | Zen | (universal) |
| Vajrayana | Vajrayána | (with diacritic; Czech transliteration) |
| Calibration | Kalibrace | (universal) |
| Calibrated physics result | Kalibrovaný fyzikální výsledek | per `PHYSICS-CALIBRATION-MODELS-v0.1.md` |
| Toy model | Toy model | (EN retained; "ukázkový model" — descriptive) |
| Upcoming model | Připravovaný model | (per zemla-theme philosophy page) |
| Testing Overdose — Measurement and Testing | Předávkování testováním — Měření a testování | (per `MIM2000-BLOG-REORG-V0.1.md` §2.1 + §5.1) |
| About stars, quarks and bowl of Tea | O hvězdách, kvarcích a misce čaje | (per `MIM2000-BLOG-REORG-V0.1.md` §2.2 + §5.1) |
| Field notes | Polní poznámky | "Postřehy z praxe" — vernacular |
| Stories and questions | Příběhy a otázky | (per blog tagline §5.1) |
| Technological spacetime | Technologický časoprostor | (per blog tagline §5.1) |

---

## §8. Process / governance terms (used in handovers, OQ logs, retrospectives)

| EN canonical | CS preferred | CS variants / notes |
|---|---|---|
| Handover | Předání | "Handover" — EN retained for code/sessions |
| Iteration | Iterace | per §4.3.2 |
| Iteration plan | Plán iterací | "Iterační plán" |
| Open question (OQ) | Otevřená otázka (OO) | "OQ-NNN" identifier retained in EN form |
| Bounce-back | Vrácení k řešení | "Eskalace" — when severity demands |
| Retrospective | Retrospektiva | per §4.1 |
| Daily brief | Denní brief | "Denní souhrn"; "Stand-up" — Agile |
| Stand-up | Stand-up | "Krátké ranní jednání" — descriptive |
| Session-notes | Zápisy ze sezení | "Notes" — informal |
| Commit | Commit | (EN retained) |
| Push | Push | (EN retained) |
| Pull request | Pull request (PR) | "Žádost o sloučení" — descriptive, formal |
| Merge | Merge | "Sloučení" |
| Rebase | Rebase | (EN retained) |
| Branch | Větev | "Branch" — EN universal in CZ codebases |
| Repository | Repozitář | "Repo" — informal |
| Workspace | Pracovní prostor | "Workspace" — EN universal |
| Devices (MacBook / ThinkPad) | Zařízení (MacBook / ThinkPad) | (universal) |
| Operator | Operátor | "Provozovatel" — formal; in this project: the human (Petr) |
| Discipline rule (R-NNN) | Pravidlo disciplíny | rule identifier R-NNN retained EN |
| Discipline | Disciplína | per UP §4.3.2 |
| Vocabulary discipline | Slovníková disciplína | per R-METH-4 |
| Methodology mapping | Metodické mapování | "Mapování metodik" |
| Replacement vs addition | Nahrazení vs přidání | per R-STRUCT-1 |
| Migration vs duplication | Migrace vs duplikace | per R-STRUCT-2 |
| TestAnalysis | Analýza testů | per §1 + AMENDMENT to SUPIN scope |
| TestDesign | Návrh testů | per §1 + AMENDMENT |
| Control point | Řídicí bod | "Bod řízení" |
| Trigger point | Spouštěcí bod | "Bod spuštění"; "Trigger" — EN retained |
| Data collection point | Bod sběru dat | "Bod záchytu dat"; "Bod pozorování" — broader |
| Assertion | Asercie | "Aserce"; "Tvrzení" — too generic; in tests: "Kontrolní podmínka" — descriptive |

---

## §9. ISTQB-aligned glossary subset (for tester-facing reports)

Subset of ISTQB Czech glossary entries most likely to appear in SUPIN tester-facing materials:

| EN | CS (ISTQB-aligned) |
|----|----|
| Pre-condition | Předpoklad |
| Post-condition | Důsledek (testu) |
| Expected result | Očekávaný výsledek |
| Actual result | Skutečný výsledek |
| Test basis | Testovací základ |
| Test charter | Testovací mandát (exploratory) |
| Test logging | Záznam průběhu testu |
| Test progress report | Zpráva o průběhu testování |
| Test summary report | Souhrnná zpráva o testování |
| Risk-based testing | Testování založené na riziku |
| Equivalence partitioning | Rozklad na ekvivalenční třídy |
| Boundary value analysis | Analýza hraničních hodnot |
| Decision table | Rozhodovací tabulka |
| State transition (test design) | Přechod stavů |
| Use case (test design) | Případ užití |
| Pairwise testing | Testování ve dvojicích |

---

## §10. Application targets (where this catalogue must be applied)

When the next iterations touch these artefacts, the CS rendering follows this catalogue:

| Target | Where CS applies | Apply by iteration |
|---|---|---|
| `mim2000-theme/inc/translations.php` | All UI labels (nav, blog page titles, card text per `MIM2000-ALPHA-V0.2.md` + `MIM2000-BLOG-REORG-V0.1.md`) | MIM-02, BLOG-02 |
| `zemla-theme/inc/translations.php` | Philosophy page hook block strings (per `ZEMLA-PHILOSOPHY-PAGE-REWORK-v0.1.md` §4.4) | PHIL-02 |
| `bodyterapie-theme/inc/translations.php` | All UI labels per `GRAPHICAL-COMPONENTS-MANUAL-v0.1.md` §5 | GRX-BOD-01 |
| `bouracka-tests/BOURACKA-TESTPLAN-vN.M.xlsx` | Sheet headers, column headers, value-list dropdowns (status / type / priority); test case names + steps + expected results | CP-SUPIN-02..08 (every TC entry) |
| `bouracka-tests/README-CS.md` | Tester-facing operating manual | CP-SUPIN-08 |
| `bouracka-tests/recon/**` | Recon templates (already CS-first per `CLIENT-PILOT-SUPIN-RECON-TEMPLATES-LIGHT-V0.1.md`) | CP-SUPIN-02 onwards |
| MI-M-T frontend (when shipped per `MI-M-T-V0.2-POC-ONPREM-SCOPE.md` §5) | All UI labels; status/severity/priority chip text | PoC-07/08 |
| MI-M-T API responses | EN canonical (no change); CS rendering happens in the frontend | n/a |

---

## §11. Open vocabulary questions

| OQ# | Sev | Urg | Pri | Question | Resolve by |
|-----|:---:|:---:|:---:|----------|------------|
| OQ-VOC-01 | C | C | C | ~~VUP-specific terms — when user supplies VUP materials, amend §4.3 (UP CS canon) with VUP-preferred terms~~ | **CLOSED** 2026-05-03 — VUP materials located at `Testing - resources/testing/DV/VUP/_VUP/`; §2b + §2c + §4.3.2b + §4.3.2c added with canonical Vaněk renderings |
| OQ-VOC-08 | B | A | A | "Attention" → "Diligence" rename (per §2c.5 — CAST canonical is Diligence; current MI-M-T schema uses Attention). Migration `112_rename_attention_to_diligence.sql` — when? | next METH iteration |
| OQ-VOC-09 | B | B | B | Three-way distinction Plan / Schedule / Estimate (per §2c.2 — Vaněk binding). Excel TestPlan workbook currently has `05_TestSets` only; should split into `05a_TestPlan` / `05b_TestSchedule` / `05c_TestEstimate`. When? | CP-SUPIN-02 review |
| OQ-VOC-10 | C | B | C | "10 Key Test Principles" — VUP HTML file titled exactly that exists; need to unpack body text and add to §4.3.2c-bis as canonical | next vocabulary refresh |
| OQ-VOC-02 | B | B | B | "WorkPackage / Work Package / Pracovní balíček" — confirm "Pracovní balíček" is the preferred CS rendering vs "Pracovní paket" or "Pracovní jednotka" | next user review |
| OQ-VOC-03 | C | B | C | "Testing Overdose" — confirm CS rendering "Předávkování testováním" feels right (vs "Testovací předávkování" — more literal) | BLOG-02 user review |
| OQ-VOC-04 | C | B | C | "Stars, Quarks and Tea" — confirm CS "O hvězdách, kvarcích a misce čaje" (proposed); literal "miska" vs "šálek" — user preference | BLOG-02 user review |
| OQ-VOC-05 | B | B | B | Bouračka primary user-journey CS naming — likely "Hlášení škody" / "Nahlášení nehody" / "Žádost o nabídku" — confirm after CP-SUPIN-02 deep recon | CP-SUPIN-02 |
| OQ-VOC-06 | C | C | C | UP phase names — "Zahájení / Rozpracování / Konstrukce / Předání" preferred CS canon; if VUP uses different terms, amend | when VUP materials arrive |
| OQ-VOC-07 | B | B | B | Mode 3 CS rendering — "Režim 3 — TDD s LLM" feels OK but "TDD s podporou LLM" is clearer for non-technical readers; pick one for public-facing copy | next user review for blog/page copy |
| OQ-VOC-11 | B | A | A | §2f.6 phase-advance criteria — current text says "coverage > 60 % on Pri-A cells" triggers phase 2. Confirm the threshold (60 % vs 75 % vs 80 %) — ThinkPad's COVERAGE-RULE-STRATEGY may have a different number. Reconcile during CP-SUPIN-06 review. | CP-SUPIN-06 |
| OQ-VOC-12 | B | B | B | §2g release-manifest JSON shape — propose a binding schema. Candidate fields: `release_version`, `pinned_schema`, `pinned_content_date`, `pinned_toolchain[]`, `compat_back_to_schema`. Confirm with ThinkPad's existing manifest practice. | next release of bouracka-tests |
| OQ-VOC-13 | B | A | A | §2h `tt_assembly_ref` format — propose `<layer>:<slug>` (e.g. `screen:report-form`). Confirm slug rules; cross-check against ThinkPad workbook entries in `15_VModelAssemblyMap` once it lands. | v0.5.1 schema migration |
| OQ-VOC-14 | C | B | C | The (FURPS+ × V-model) cross matrix in §2h — should this become a binding reporting view (`v_furps_vmodel_coverage`), or stay analytical? Adds ~50 cells per Requirement; risk of empty-cell noise overshadowing signal. | post v0.5.1 reporting design |
| OQ-VOC-15 | B | A | A | E2E meta-layer `tt_e2e_composes` JSON shape (per §2h.1 R-VMODEL-2) — proposed: `["TT-FUNC-rpRegex", "TT-SCRN-policeCard", ...]` flat array. Confirm the array elements are TT codes (executable manifest entries from `covers()` calls) and not wider abstract layer references. Cross-check with Sonnet's `covers()` discipline. | CP-SUPIN-06 |

---

## §12. Status footer

| Item | Value |
|------|-------|
| Document | `VOCABULARY-CATALOGUE-CS-EN-V0.1.md` |
| Output position | `_config/VOCABULARY-CATALOGUE-CS-EN-V0.1.md` |
| Sections | 17 (testing core / defects / CAST framework canon / Test Management canon / source-artefact derivation / FURPS+ / Cartesian governance + coverage gating phase-in / decoupled-versioning policy / V-model TT assembly layer / CAST entities + lifecycle / methodology + VUP discipline / DVA architecture / SUPIN-Bouračka / MI-M-T-3FP / process-governance / ISTQB subset / application targets / OQs) |
| Total terms catalogued | ≈ 380 (v0.1.2 ≈ 360 + v0.1.4 additions: phase enums + decoupled-versioning track names + V-model layer codes + cross-axis matrix labels) |
| Sources synthesised | 9 (8 from v0.1.2 + ThinkPad CP-SUPIN-04/05 deliverables: COVERAGE-RULE-STRATEGY + VMODEL-ASSEMBLY-TT-MAPPING + decoupled-versioning empirical pattern, all reconciled via SYNCHRO-MACBOOK-TO-OPUS-CP-SUPIN-06-2026-05-08) |
| Open vocabulary questions | 15 (OQ-VOC-01 closed; -02..-07 open from v0.1.0; -08..-10 added v0.1.1; -11..-14 added v0.1.4 for §2f.6 / §2g / §2h reconciliation; -15 added in-place 2026-05-08 PM for §2h.1 E2E meta-layer JSON shape) |
| Foundational rules introduced/reframed v0.1.4 | R-DESIGN-1 reframed (phased gating supersedes strict-from-day-1); R-DECOUPLED-1 introduced (4-track versioning); R-VMODEL-1 introduced (V-model assembly layer as transposition basis sister to FURPS+); R-VMODEL-2 introduced (E2E meta-layer composes base layers; in-place patch §2h.1 post Sonnet CP-SUPIN-05 push) |
| Cross-references | `_config/SYNCHRO-MACBOOK-TO-OPUS-CP-SUPIN-06-2026-05-08.md` §2 (convergence reconciliation); `_config/METH-REFINE-TESTANALYSIS-TESTDESIGN-v0.1.md` §3 + §6 (Package + transposition); planned `_config/METHODOLOGY-MAPPING-V0.1.md` AMENDMENT 3 (formalises §2f.6/§2g/§2h in methodology layer) |
| First application iterations | CP-SUPIN-02 (Bouračka tester materials) + MIM-02 (mim2000.cz) + BLOG-02 (blog reorg) + ThinkPad delivery 2026-05-03 PM; CP-SUPIN-06 v0.5.1 schema migration consumes §2f.6 + §2h |
| Status | v0.1.4 — binding; second-pass cross-artefact application required (METHODOLOGY-MAPPING AMENDMENT 3 + the v0.5.1 unified-transposition migration on Bouračka side); next refresh = OQ-VOC-11..14 resolution + Bouračka recon harvest after CP-SUPIN-06 |

---

*VOCABULARY-CATALOGUE-CS-EN-V0.1.md — 2026-05-03 — MacBook CoWork session — Opus*
