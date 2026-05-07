# CP-SUPIN-05 — strategický plán + delivery roadmap — v0.1 CS

> **Trigger.** 2026-05-07 EOD: Pete consolidated 5 directions from CP-SUPIN-04
> EOD post-deployment review. Need unified plan + phased delivery.
>
> **Vstupy.** CP-SUPIN-04 closure: DEMO Bouračka public Cíl 1 covered, drift
> empirically characterized (forensic z HP Elite trace), 6 frameworks
> scaffolded, Excel v0.4.2 s TES sheets, 4-target gradual delivery roadmap.
>
> **Východisko.** Working seed for DEMO automated coverage system.
> **Cíl iterace.** Promote calibration to Cíl 2 + cross-framework parity +
> V-model assembly-level TT mapping + introduce coverage gates gradually.

---

## §1. Kde teď stojíme (CP-SUPIN-04 closure status)

### §1.1 Co máme

| Kategorie | Stav | Detail |
|-----------|------|--------|
| **DEMO recon** | ✅ DONE | 4-phase wizard mapped, 9 integrations catalogued, 26-row Δ matrix |
| **Playwright suite** | ✅ GREEN+drift | bring-up + a1-main + 8 alternates + 2 intel-probes |
| **Cypress smoke** | ✅ scaffold | parita pro bring-up; full suite TBD |
| **TestCafe smoke** | ✅ scaffold | parita pro bring-up; full suite TBD |
| **Selenium pytest** | ✅ scaffold | parita pro bring-up; full suite TBD |
| **ReadyAPI/SoapUI** | ✅ scaffold | smoke project XML; doc deklaruje primary B/E |
| **Postman** | ✅ scaffold | 1 collection; secondary B/E |
| **Excel TestPlan** | ✅ v0.4.2 | 28 TT, 49 TC, branch tagging, TES sheets, bug dedup |
| **Bug naming** | ✅ formalised | `BUG-CP-{TC}-{ASSERT}` deterministic dedup |
| **Branched master doc** | ✅ pattern | single-master + render-by-branch |
| **DEMO drift handling** | ✅ characterized | forensic trace HP Elite 2026-05-07 → reCAPTCHA-v3 score H5 |
| **Strategic governance** | ✅ 8 docs | ROADMAP, BRANCH-HANDOFF, MULTI-PLATFORM, TES, GITHUB, MIND-MAP, 3-DEVICE, BUG-NAMING + EMAIL-DELIVERABILITY (10 total) |
| **HP Elite runtime** | ✅ confirmed | <test-runner-host> install + run successful via pure-Python orchestrator |

### §1.2 Co chybí (vstup do CP-SUPIN-05)

| Mezera | Důsledek | Priority |
|--------|----------|----------|
| Cíl 2 (`tst.demo.bouracka.cz`) live testing | Nelze potvrdit zda DEMO drift je SUPIN-wide nebo specifický | ★★★ |
| Cross-framework parita beyond bring-up | Nelze evidence-based porovnat 6 frameworks | ★★ |
| Sdílená test-data napříč frameworks | Duplicita, drift mezi frameworks | ★★ |
| V-model assembly-level TT mapping | Nelze tvrdit "TC pokrývá tento element/LoV" | ★★★ |
| Strict coverage rule | Nelze auditovat completeness vs SUT | ★★ |
| Bug-route UI fix navržený SUPIN devs | "Vypršela platnost" je misleading | ★ |

## §2. Pět směrů z konsolidace

### §2.1 Směr 1 — Cíl 2 enablement (`tst.demo.bouracka.cz`)

**Cíl.** Promote calibration kit z Cíl 1 (DEMO public) na Cíl 2 (DEMO test
inside SUPIN net).

**Implikace.**
- Tester nastaví `BOURACKA_BASE=https://tst.demo.bouracka.cz` před `py bouracka.py test`
- Suite poběží stejné spec files; očekávané výsledky stejné jako na DEMO public
  (Δ matrix má `applies_to_demo: both` pro většinu TC)
- **Otevřená otázka:** je drift na POST /api/reports rovněž na tst.demo nebo jen
  na demo public? Pokud rovněž → drift je SUPIN-wide; pokud ne → drift je
  isolated na public-DEMO env

**Deliverable.** `_specs/CIL-2-ENABLEMENT-CS.md` (nový, viz §4.1).

### §2.2 Směr 2 — Cross-framework parity (Playwright + Cypress + TestCafe + Selenium)

**Cíl.** Stejný TC code napříč 4 frameworks, sdílená test-data, konsistentní
assertion semantics.

**Aktuální stav (CP-SUPIN-04 STEP 26).** Pouze `bring-up-smoke` má parity.
A1-main + 8 alternates jen v Playwright.

**Plán fází.**
- **Fáze 1** (CP-SUPIN-05): port `a2-alternates` na Cypress + TestCafe + Selenium;
  unified test data layer
- **Fáze 2** (CP-SUPIN-06): port `a1-main-happy-day` na všechny 4 frameworks;
  reporter consolidation (jediný JSON output schema)
- **Fáze 3** (CP-SUPIN-07): formal cross-framework comparison report + framework
  fitness verdict

**Deliverable.** `_specs/CROSS-FRAMEWORK-DATA-SHARING-CS.md` (nový, viz §4.2).

### §2.3 Směr 3 — Gradual TestPlan adjustment

**Princip.** Excel TestPlan je živý dokument. Ne každá změna v test sources
automaticky bumpuje Excel. Schema bumps jsou opatrně.

**Plánované adjustmenty pro CP-SUPIN-05:**
1. **`15_VModelAssemblyMap`** sheet (Schema bump v0.4.3) — viz §2.4
2. **`16_CoverageMatrix`** sheet (Schema bump v0.5.0) — viz §2.5
3. Přidat sloupce `tt_assembly_layer` a `tc_coverage_strict` do existujících sheetů
4. Update `00c_VersionSanityRules` na nové requirement

**Deliverable.** Migration script `tools/migrate_to_v0_5_0_assembly_coverage.py`.

### §2.4 Směr 4 — V-model assembly-level TestTarget mapping

**Princip.** V-model decomposition vyžaduje TT mapping na úrovni assembly
(integrace komponent), ne jen flow level.

**Bouračka assembly-level TT taxonomie:**

```
TT-FUNC-*     Funkcionality (use case capabilities)
              např. TT-FUNC-001 — Vyplnění záznamu o nehodě
                   TT-FUNC-002 — Ověření účastníků (OTP)
                   TT-FUNC-003 — Sběr dokumentů (manuální + zenID)
                   TT-FUNC-004 — Foto-evidence škod
                   TT-FUNC-005 — Podpis a finalizace záznamu

TT-SCRN-*     Screens (UI obrazovky + elementy)
              např. TT-SCRN-rozcestnik         /formular/
                   TT-SCRN-informace           /formular/informations
                   TT-SCRN-overeni             /verification
                   TT-SCRN-dokumenty           /documents/<rid>/
                   TT-SCRN-dokumenty-manual    /documents/<rid>/manual
                   TT-SCRN-recap               /documents/<rid>/recap
                   ...

TT-LOV-*      Lists of Values (codelists, enumerations)
              např. TT-LOV-insurance           /api/enumerations/insuranceCompanies (215+ items)
                   TT-LOV-vehicleBrands        /api/enumerations/vehicleBrands (200+ items)
                   TT-LOV-licenseCategories    protected (8 enums celkem 403)
                   TT-LOV-prefix-cs            CZ phone +420 prefix dropdown
                   TT-LOV-prefix-sk            SK phone +421 prefix dropdown
                   ...

TT-ACTV-*     Active elements (behavior triggers)
              např. TT-ACTV-CTA-vyplnit        button "VYPLNIT ZÁZNAM"
                   TT-ACTV-OTP-input           4-digit OTP boxes (React-controlled)
                   TT-ACTV-checkbox-GDPR       GDPR consent checkbox (PUT /reporter gate)
                   TT-ACTV-autocomplete-RUIAN  ČÚZK address autocomplete
                   TT-ACTV-autocomplete-brand  vehicle brand autocomplete
                   TT-ACTV-photo-capture       camera/upload (Phase 3)
                   TT-ACTV-sign-tablet         touch signature canvas (Phase 4)
                   ...
```

**Cross-link.** Existující `02_TestTargets` sheet udržuje flow-driven TT
(TT-001 .. TT-028). Nový `15_VModelAssemblyMap` přidá assembly-level TT a
poskytne traceability matrix mezi assembly-TT × flow-TT × screens.

**Deliverable.** `_specs/VMODEL-ASSEMBLY-TT-MAPPING-v0.1-CS.md` (nový, viz §4.3)
+ Excel sheet `15_VModelAssemblyMap`.

### §2.5 Směr 5 — Strict coverage rule introduction

**Princip.** Coverage rule = každý TT musí být pokryt alespoň jedním passing TC.
Aktuálně: informational. Cíl: gated-by-CI.

**Phase-in plán.**

| Phase | Trigger | Coverage rule | Action |
|-------|---------|---------------|--------|
| **0 (now)** | CP-SUPIN-05 STEP 1 | informační | annotate `tc_coverage_strict=false` v Excelu, jen tracking |
| **1** | CP-SUPIN-05 mid | warning | tools/coverage_audit.py vyhodí RED na uncovered TT, ale nezablokuje deploy |
| **2** | CP-SUPIN-06 | gating per-TT-class | TT-FUNC-* MUSÍ být covered, ostatní soft |
| **3** | CP-SUPIN-07 | gating all | release blocked dokud uncovered TT > 0 |

**Důvod gradual.** Premature gate by zablokoval delivery dříve než máme
broad-enough TC base. Test base se ladí společně s coverage rule, ne před.

**Deliverable.** `_specs/COVERAGE-RULE-STRATEGY-v0.1-CS.md` (nový, viz §4.4).

## §3. Co ne-iterujeme v CP-SUPIN-05

Aby iterace byla focused:
- **NE**: ReadyAPI/SoapUI rozšíření beyond smoke (čekáme na ČKP IT B/E přístup)
- **NE**: PROD test (Cíl 3) — čeká na N08 sandbox + AISPOV access
- **NE**: PROD prelive (Cíl 4) — out of scope pro pilot
- **NE**: SUPIN-ecosystem-map fragments beyond Bouračka — until X1 fragment z ČKP IT
- **NE**: MI-M-T methodology export — to je MacBook session scope

## §4. Deliverable per directiom

### §4.1 Cíl 2 enablement guide

`_specs/CIL-2-ENABLEMENT-CS.md` — sections:
- §1 Předpoklad: HP Elite v SUPIN VPN se reach na tst.demo.bouracka.cz
- §2 Postup: `set BOURACKA_BASE=https://tst.demo.bouracka.cz; py bouracka.py test`
- §3 Očekávané rozdíly vs Cíl 1 (Δ matrix sub-set)
- §4 Drift detection convention — pokud tst.demo má /error/timeout, drift je SUPIN-wide
- §5 Per-framework smoke check (Playwright + Cypress + TestCafe + Selenium)
- §6 Sync-back protocol — Pete posílá `bouracka-results-...zip` zpět z HP Elite

### §4.2 Cross-framework data sharing

`_specs/CROSS-FRAMEWORK-DATA-SHARING-CS.md` — sections:
- §1 Single source of truth: `fixtures/test-data/*.yaml`
- §2 Per-framework loader pattern (TS for Playwright/Cypress/TestCafe; Python for Selenium)
- §3 TC code alignment — `TC-CP-A2-ALT-1` musí mít stejný název napříč 4 frameworks
- §4 Assertion semantics map — která assertion library v každém frameworku
- §5 Reporter consolidation — výstup do common JSON schema → `tools/append_test_run_result.py`
- §6 Migration plan — fáze 1: bring-up (DONE) → fáze 2: alternates → fáze 3: full E2E

### §4.3 V-model assembly-level TT mapping

`_specs/VMODEL-ASSEMBLY-TT-MAPPING-v0.1-CS.md` — sections:
- §1 Princip: V-model decomposition Acceptance ↔ BPM ↔ Functional ↔ Screen ↔ Element
- §2 Naming convention: TT-{FUNC|SCRN|LOV|ACTV}-{slug}
- §3 Initial catalog (~80 TT items, prefilled z DEMO recon)
- §4 Cross-link na existing TT-001..TT-028 (flow-driven)
- §5 Excel sheet `15_VModelAssemblyMap` schema (12 sloupců)

### §4.4 Coverage rule strategy

`_specs/COVERAGE-RULE-STRATEGY-v0.1-CS.md` — sections:
- §1 Princip: TT × TC coverage matrix
- §2 Phase-in (4 fáze, viz §2.5 výše)
- §3 Audit script: `tools/coverage_audit.py`
- §4 Excel sheet `16_CoverageMatrix` schema (8 sloupců)
- §5 Reporter integration: Playwright reporter pushuje TC outcome → coverage update

## §5. Phased delivery — co kdy odejde

### §5.1 v0.5.0 (immediate, this session)

| Item | Type | Status |
|------|------|--------|
| Drift guard fix v0.4.10 (a1-main + a2-alt) | bugfix | ✅ done in workspace |
| `_specs/CP-SUPIN-05-PLAN-CS.md` (this doc) | strategic | ✅ this iteration |
| `_specs/CIL-2-ENABLEMENT-CS.md` | new | this iteration |
| `_specs/CROSS-FRAMEWORK-DATA-SHARING-CS.md` | new | this iteration |
| `_specs/VMODEL-ASSEMBLY-TT-MAPPING-v0.1-CS.md` | new | this iteration |
| `_specs/COVERAGE-RULE-STRATEGY-v0.1-CS.md` | new | this iteration |
| `fixtures/test-data/` skeleton | scaffold | this iteration |
| `tools/coverage_audit.py` skeleton | scaffold | this iteration |
| Updated `recon/DRIFT-2026-05-07-DEMO-POST-REPORTS-CS.md` | recon | ✅ already done |
| Excel — keep at v0.4.2 (no schema bump yet) | unchanged | reason: nedopečené plány by neměly bumpovat schema |
| Single ZIP scanner-friendly v0.5.0 | release | ship at end |

### §5.2 v0.5.1 (next iteration, after first Cíl 2 round)

| Item | Type |
|------|------|
| Excel `15_VModelAssemblyMap` sheet | schema bump → v0.5.0 |
| Excel `16_CoverageMatrix` sheet | schema bump → v0.5.0 |
| Migration script `tools/migrate_to_v0_5_0_assembly_coverage.py` | tool |
| Cypress port of a2-alternates | test |
| TestCafe port of a2-alternates | test |
| Selenium port of a2-alternates | test |
| Initial coverage_audit.py run | report |

### §5.3 v0.6.0 (mid-CP-SUPIN-05)

| Item | Type |
|------|------|
| Cypress + TestCafe + Selenium ports of a1-main-happy-day | test |
| Reporter consolidation (common JSON output) | tool |
| Coverage rule — soft warnings (Phase 1) | gate |
| First evidence-based cross-framework comparison | report |

### §5.4 v0.7.0 (CP-SUPIN-05 close)

| Item | Type |
|------|------|
| Coverage rule — gating per-TT-class (Phase 2) | gate |
| MI-M-T migration plan v1 (z MacBook session) | governance |
| Cíl 3 sandbox dependency review | escalation |

### §5.5 CP-SUPIN-06 PARALLEL TRACK — `mimt-harness` + `mimt-simple` extracts

Per Pete decision 2026-05-07 mid-session (viz `_specs/MIMT-NATIVE-AUTOMATION-ASSESSMENT-v0.1-CS.md` v0.2 §6).

**Track B — `mimt-harness/` (full VUP model, MI-M-T-coupled):**

| Item | Trigger | Effort |
|------|---------|--------|
| New repo `mimt-harness/` (sibling to `bouracka-tests/`) | CP-SUPIN-06 STEP 1 | 2 days scaffold |
| Extract `tools/{coverage_audit,preship_audit,append_test_run_result}.py` | CP-SUPIN-06 STEP 2 | 3 days |
| Extract `playwright/{helpers,reporters}/` | CP-SUPIN-06 STEP 3 | 3 days |
| Extract `bouracka.py` → `mimt-harness/runtime/orchestrator-template.py` | CP-SUPIN-06 STEP 4 | 2 days |
| Extract methodology specs into `mimt-harness/docs/` | CP-SUPIN-06 STEP 5 | 2 days |
| `bouracka-tests` re-imports `../mimt-harness` (relative) | CP-SUPIN-06 STEP 6 | 2 days |
| **TOTAL Track B** | — | **~2 weeks** |

**Track C — `mimt-simple/` (OSS community, simplified model):**

| Item | Trigger | Effort |
|------|---------|--------|
| New repo `mimt-simple/` (separate public, MIT/Apache 2.0) | CP-SUPIN-06