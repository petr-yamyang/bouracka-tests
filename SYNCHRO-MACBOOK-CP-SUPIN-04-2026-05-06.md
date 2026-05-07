# Synchro MacBook ← ThinkPad — CP-SUPIN-04 — 2026-05-06

> **Adresát.** MacBook session (analytical MI-M-T context).
> **Z.** ThinkPad Opus session (governance + Bouračka calibration).
> **Cíl.** Předat MacBook session úplný snapshot toho, co se v CP-SUPIN-04
> stalo — methodology, artefakty, lessons learned, MI-M-T-relevant
> findings.

---

## §1. Top-line

CP-SUPIN-04 = první kalibrační iterace. Stojí na třech pilířích:

1. **Live SUT recon** — DEMO Bouračka šel public → bottom-up reverse
   analysis end-to-end (replaces stale ~10-month-old analytical doc)
2. **Branched master architecture** — single Excel + single MD master
   doc s `applies_to_demo` / `applies_to_prod` columns + `<!-- B:* -->`
   markers; per-branch slim verze rendered na demand
3. **Empirical install lessons** — 6 install-time gotchas zachycených
   po reálném 1st-operator install na ThinkPadu; recovery patterns
   doc-as-code v install guide

## §2. Co je v repu pro MacBook (key artifacts)

```
_specs/
  ROADMAP-4-TARGET-CS.md                 ← strategic 4-target plan + MI-M-T migration
  BRANCH-HANDOFF-TEMPLATE-CS.md          ← template pro Sonnet sessions
  BRANCHED-MASTER-DOC-PATTERN-v0.1.md    ← single-master-multi-view pattern
  BUG-NAMING-CONVENTION-v0.1.md          ← BUG-CP-{TC_CODE}-{ASSERT_CODE} dedup
  TESTER-LESSONS-LEARNED-v0.1-CS.md      ← test-author empirical guide
  DOCUMENTATION-POLICY-v0.1.md           ← Tier 1/2a/2b/3 source-of-truth
  LESSONS-LEARNED-CP-SUPIN-04-WORKING.md ← during-session reference
  *-format spec...

_install/
  INSTALL-FROM-ZERO-v0.4-CS.md           ← refreshed CS install guide; 5 preflighted gotchas

recon/
  ANALYTICAL-DOC-INTELLIGENCE-v0.3.md    ← bottom-up rebuilt from live walks
  ANALYTICAL-DOC-MASTER-v0.4.md          ← branched master doc
  DELTA-DEMO-vs-PROD-v0.1.md             ← 26 row Δ matrix, 8 confirmed
  DEMO-PUBLIC-LIVE-2026-05-06.md         ← DEMO public going-live capture
  integrations/
    INT-001 reCAPTCHA, INT-002 N8 SMS, INT-003/4 AISPOV CRR/CRV, INT-005 zenID,
    INT-006 Azure outage feed (NEW), INT-007 Google Maps (NEW),
    INT-008 internal /api/reports REST (NEW), INT-009 ČÚZK RUIAN (NEW)
  screenflows-live/
    flow-A1-main-tst-demo/
      flow.md                            ← end-to-end live walk record
      uml/{use-case,activity,sequence}.puml  ← VUP-compliant UML

playwright/
  tests/
    bring-up-smoke.spec.ts               ← TC-CP-001, GREEN
    a1-main-happy-day-demo.spec.ts       ← TC-CP-A1-MAIN-DEMO, full E2E
    a2-alternates-demo.spec.ts           ← 8 alternates (validation, codelists)
    intel-probes/                        ← read-only API recon (CP-SUPIN-04 STEP 14)
  helpers/page-helpers.ts                ← dismissCookieBanner, waitForSpaHydration
  reporters/excel-row-writer.ts          ← UPSERT do 07_TestRunResults
  playwright.config.ts                   ← 4 projects × matrix viewports

cypress/e2e/bring-up-smoke.cy.ts         ← parity with Playwright
testcafe/tests/bring-up-smoke.test.ts    ← parity with Playwright

fixtures/
  codelists-live-2026-05-06.yaml         ← 5 živé codelisty (insurance 13, brands 275, ŘP 17, damage 8, movement 18)
  api-endpoints-live-2026-05-06.yaml     ← 23 internal + 6 third-party endpointů
  live-copy-strings.yaml                 ← 17 STR-* verbatim CS strings pro asserce

tools/
  check_priority_matrix.py               ← validátor matrix
  bump_workbook_version.py               ← version + computed values
  migrate_to_v04_branch_tagging.py       ← branch columns
  migrate_08bugs_v04_1.py                ← bug dedup schema
  fix_priority_matrix.py                 ← priority formula bugfix
  render_branch_doc.py                   ← branched MD slicer
  append_test_run_result.py              ← Excel UPSERT z reporter
  test_console.py                        ← multi-framework runner

scripts/
  sanity-check.ps1                       ← 7-check post-install verifier
  run-bring-up-smoke.ps1                 ← updated for /formular/ + cookies
  ...

BOURACKA-TESTPLAN-v0.4.1.xlsx            ← master with branch tagging + bug dedup
BOURACKA-TESTPLAN-v0.4.0.xlsx            ← prior (delete after MacBook syncs)
```

## §3. Klíčové methodology learnings pro MI-M-T

### §3.1 Branch-aware schema design

**Pattern:** každá ItemBase entita (Requirement / TestTarget / TestCase / Bug)
má boolean `applies_to_*` columns derivované z primárního branch tag
(`env_constraints` na TC, manuálně-set jinde).

```
ItemBase
  ├── env_constraints: ENUM[both, demo-only, prod-only, both-with-adapter]
  ├── applies_to_demo: BOOL  (derived)
  ├── applies_to_prod: BOOL  (derived)
  └── applies_to_pre_live: BOOL  (future col, post v0.6)
```

**Use case v MI-M-T:** stejný princip pro multi-tenant / multi-environment
SaaS testing. Single master record + boolean tags per dimension.

### §3.2 Single-master + render-on-demand documentation

**Pattern:** master MD/DOCX má branch markers `<!-- B:DEMO --> ... <!-- /B -->`.
Render skript slice-uje na per-branch slim view.

**Use case v MI-M-T:** customer-specific documentation generated z univerzálního
master. Žádné copy-paste duplikáty, žádný drift.

### §3.3 Deterministic bug dedup keys

**Pattern:** ID = `BUG-{TC_CODE}-{ASSERT_CODE}`. Same defect = same ID =
UPSERT, never new row. Counters track first/last seen + occurrences.

**Use case v MI-M-T:** essential pro long-running test suites kde stejný
defect failuje napříč retries / envs / dnů. Eliminuje noisy backlogy.

### §3.4 Recovery patterns as code

**Pattern:** install guide má `Recovery 1..4` with **inline heredoc**
content paste — operator může obnovit ztracený soubor bez stahování.

**Use case v MI-M-T:** distribuce-resilient docs. Email scanner stripne
.ps1 / .py? Recovery section umožní obnovit z heredoc.

### §3.5 Δ matrix as audit trail

**Pattern:** environment-specific behaviour rozdíly tracked v matici se
`confidence` (confirmed / expected / unknown / legacy). 1 řádek = 1 Δ.
TC získává `env_constraints` + adaptér mode (mock / real).

**Use case v MI-M-T:** any multi-env testing — staging, beta, GA — má
Δ matici jako governance-grade artefakt.

### §3.6 Empirical preflight rules

**Pattern:** install guide má sekce `§2 Preflight A` + `§2b Preflight B`
PŘED main-flow §3. Each preflight = empirically-discovered gotcha
(winget reset, ExecutionPolicy). Promote troubleshoot patterns z §10
do main-flow když měříme že 80%+ operators je hit.

**Use case v MI-M-T:** všechny SDK / installation guides. Empirical-first,
not aspirational-first.

## §4. Klíčové strategic findings pro MacBook session

### §4.1 Live SUT > stale analytical doc

Original analytical document byl ~mid-2025 (10 měsíců starý). Bottom-up
reverse z `demo.bouracka.cz` po jeho zveřejnění (2026-05-05) odhalila
**11 explicitních oprav** vs původní doc:

- Wizard taxonomy: 18 screens (doc) vs 4 phases × ~22 sub-screens (reality)
- Auth: implicit via existing IDs (doc) vs anonymous + phone-OTP (reality)
- Codelists: enumerated in doc but mostly different actual values
- Architectural stack: not specified (doc) vs Vite + React + Zod + TanStack Query (reality)
- ČÚZK RUIAN integration: nezmiňován (doc) vs critical (reality)

**MI-M-T impact:** treat existing analytical docs jako **starting hypothesis**,
ne **truth**. Plan reverse-from-live as default modus operandi.

### §4.2 4-target gradual delivery

Detail viz `_specs/ROADMAP-4-TARGET-CS.md`. Bouračka má 4 target environments,
každý s vlastní integrací posture:

```
demo-public ← demo-tst    ← prod-tst   ← prelive
(mocked)    (mocked twin)  (real test)  (read-only)
```

**MI-M-T impact:** MI-M-T musí podporovat per-environment integration adapter
swapping (Mockoon / sandbox / real / read-only) bez touch test code.
Současný `env_constraints` column + parametrizace baseURL pattern je první
draft tohoto.

### §4.3 Multi-framework parity test

CP-SUPIN-05 má vybrat 1 framework z {Playwright, Cypress, TestCafe} pro
long-term Bouračka. Decision matrix:
- Test stability across runs
- Authoring ergonomics  
- CI integration
- Recon-friendliness (network panel access)
- Browser support
- Community

Všechny 3 frameworks mají bring-up-smoke parity v repu jako kalibrační test.

**MI-M-T impact:** MI-M-T runner backend musí být framework-agnostic.
Můj `tools/test_console.py` je první draft (status / run / report / compare
sub-commands across frameworks).

## §5. Open blockers pro CP-SUPIN-05+

| # | Blocker | Resolution path |
|---|---------|-----------------|
| 1 | N08-test SMS sandbox | OQ-CP-27 → ČKP IT |
| 2 | AISPOV-test sandbox (CRR/CRV/ROB) | ČKP IT |
| 3 | zenID test-keys | ČKP IT |
| 4 | tst.bouracka.cz firewall ip-allowlist pro tester laptop | SecOps |
| 5 | reCAPTCHA bypass token pro automated runs | OQ-CP-XX |
| 6 | Real ČKP-tester contact pro Δ ověření DEMO vs PROD | TBD |

Detail viz `_install/contracts/n8-sms-gateway-test-data-request.md` (vendor
request template).

## §6. Co MacBook session má dělat dál

### §6.1 Číst (důrazně doporučeno)

1. `_specs/ROADMAP-4-TARGET-CS.md` — strategic context
2. `recon/ANALYTICAL-DOC-MASTER-v0.4.md` — bottom-up SUT analysis
3. `recon/screenflows-live/flow-A1-main-tst-demo/flow.md` — E2E walkthrough
4. `_specs/TESTER-LESSONS-LEARNED-v0.1-CS.md` — empirical patterns
5. `BOURACKA-TESTPLAN-v0.4.1.xlsx` — kompletní test plan

### §6.2 Psát / iterovat (pokud MacBook má kapacitu)

1. **MI-M-T import contract draft** — co Bouračka v0.5 musí emitovat aby
   bylo MI-M-T import-ready
2. **Testing methodology generalization** — z Bouračka-specific patterns
   na universal SUPIN/MI-M-T patterns
3. **Component module proposals** — jaké tools z `tools/` jsou kandidáti
   na MI-M-T module migration

### §6.3 NEpsát (Opus governance scope)

- Změny Excel schema
- Změny v Bouračka tests (let Sonnet branches handle that)
- Změny naming convention

### §6.4 Sync-back

Po MacBook iteraci:
1. `SYNCHRO-MACBOOK-TO-OPUS-{DATE}.md` v repu
2. Pull požadavek na Opus governance pro methodology updates
3. Bolder MI-M-T proposals jako separate `_specs/MIMT-*.md` files

## §7. Stav

| Item | Hodnota |
|------|---------|
| Synchro doc | `SYNCHRO-MACBOOK-CP-SUPIN-04-2026-05-06.md` |
| Datum | 2026-05-06 (večer ThinkPad time) |
| Z | Pete + ThinkPad Opus session |
| Pro | MacBook session (analytical MI-M-T) |
| Velikost ekosystému | ~50 souborů + 8 ZIP packages + 1 Excel master |
| Celková delta vs CP-SUPIN-03 | branch tagging + 6 install gotchas + bug dedup + 5-track suite expansion |
| Status | připraveno k MacBook synchronizaci |
