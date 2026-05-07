# Git sync checklist — first push + MacBook pull — v0.1 CS

> **Trigger.** CP-SUPIN-05 mid-session 2026-05-07: Pete: "give good
> documentation and code delta to GitHub repo to be able fully synchronise
> with MacBook now and enable another session with updated documents".
>
> **Cíl.** Připravit kompletní git-ready stav repo + step-by-step commit plan
> + MacBook clone/pull verification + post-pull sanity steps.
>
> **Předpoklad.** Žádný GitHub remote ještě není inicializovaný (per
> CP-SUPIN-04 STEP 33 carry-over Q-4 "GitHub repo creation by Pete").

---

## §1. Stav repo před prvním pushem

### §1.1 Co je v workspace

```
SUPIN/                                          ← Pete's workspace root (NOT git repo)
├── bouracka-tests/                             ← THIS will become a git repo
│   ├── .gitignore                              ← already in place
│   ├── CHANGELOG.md                            ← NEW (this session)
│   ├── package.json                            ← npm dependencies
│   ├── bouracka.py                             ← Python orchestrator
│   ├── READ-ME-FIRST-CS.md
│   ├── BOURACKA-TESTPLAN-v0.4.2.xlsx           ← latest Excel
│   ├── _install/                               ← install guides + SecOps
│   ├── _specs/                                 ← strategic governance docs
│   ├── recon/                                  ← analytical recon
│   ├── playwright/                             ← Playwright tests + reporters
│   ├── cypress/                                ← Cypress smoke
│   ├── testcafe/                               ← TestCafe smoke
│   ├── selenium/                               ← Selenium pytest
│   ├── readyapi/                               ← ReadyAPI smoke
│   ├── postman/                                ← Postman collection
│   ├── mockoon/                                ← N8 mock
│   ├── scripts/                                ← PowerShell helpers (dev-only, not in email ZIP)
│   ├── tools/                                  ← Python helpers
│   ├── fixtures/                               ← test data + codelists
│   ├── env/                                    ← per-env config
│   └── specs/                                  ← per-TC spec MD files
├── SUPIN-ecosystem-map/                        ← sibling architectural repo (separate git)
├── bouracka - automated test suites inouts and seeders/  ← email archive (NOT in git)
└── analyticke vstupy/                          ← Pete's local raw inputs (NOT in git)
```

### §1.2 Co MUSÍ být v `.gitignore` (verify)

```gitignore
# OS / IDE
.DS_Store
Thumbs.db
.~lock.*

# Node
node_modules/
npm-debug.log*

# Python
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/

# Test outputs (locally generated, not committed)
test-results/
playwright-report/
runs/
delivery/

# Email pickup folder (lives in sibling, not in repo, but defense-in-depth)
*.zip
!fixtures/**/*.zip                              # but allow ZIP fixtures if any

# Editor temp
*.swp
*.tmp

# Python virtualenvs
venv/
.venv/
env/.python-version                              # but env/*.json IS committed (per-env config)
```

Stávající `.gitignore` v repo zkontrolovat + případně doplnit.

### §1.3 Co NESMÍ jít na public GitHub

| Item | Důvod | Mitigation |
|------|-------|------------|
| `analyticke vstupy/test-data-snippets/` | 164 MB photos, citizen-test-data | NIKDY v git; per-host distribuce |
| `bouracka - automated test suites inouts and seeders/` | email archive, redundant | sibling adresář, mimo repo root |
| `BOURACKA-TESTPLAN-v0.{1..4.1}.xlsx` | superseded; jen v0.4.2 stačí | exclude staré Excel verze v `.gitignore` nebo přesunout do `_obsolete/` |
| Plné test-results / traces | velké, lokální | `.gitignore` |
| `.~lock.*` Excel lock files | Windows artifact | `.gitignore` |

## §2. Commit plan (10 logical commits)

Doporučené rozdělení do 10 atomických commit-ů, abychom v MacBook session měli
čisté git log:

### §2.1 Commit 1 — initial scaffold (CP-SUPIN-02 foundation)

```bash
git init
git add .gitignore CHANGELOG.md README-CS.md README-EN.md DELIVERY-NOTES.md
git add package.json
git add _specs/TESTCASE-SPEC-FORMAT-v*.md _specs/TESTTARGET-LIST-FORMAT-v*.md
git add _specs/RELEASE-CONTEXT-v0.1.md _specs/DOCUMENTATION-POLICY-v0.1.md
git add _specs/RECON-INPUT-EXTENSIONS-v0.2.md
git add _specs/INTEGRATION-CONTRACTS-STRATEGY-v*.md
git add specs/ env/

git commit -m "chore(scaffold): initial bouracka-tests scaffold + format specs

Per CP-SUPIN-02. Folder skeleton + governance specs + per-environment config.

* Format specs locked: TestCase + TestTarget + RECON-INPUT extensions
* Per-env config: tst / tst-demo / public
* Per-TC spec MDs (TC-CP-001..005, 021..023)
* Scaffold from CLIENT-PILOT-SUPIN-V0.1.md scope"
```

### §2.2 Commit 2 — Playwright suite (the working tests)

```bash
git add playwright/
git commit -m "feat(playwright): full Playwright suite — bring-up + a1-main + 8 alternates

* bring-up-smoke.spec.ts — pipeline alive against DEMO Bouracka rozcestnik
* a1-main-happy-day-demo.spec.ts — full E2E happy-day (~150s budget)
  with drift guard v2 (URL polling 30s budget) for /error/timeout
* a2-alternates-demo.spec.ts — 8 ALT variants:
  ALT-1 RP regex, ALT-4 GDPR, ALT-5 +421, ALT-6 200000Kc card,
  ALT-7 enumerations, ALT-8 DEMO banner,
  ALT-9 POST /api/reports drift-aware,
  ALT-10 SPA-driven POST probe (NEW)
* helpers/page-helpers.ts — dismissCookieBanner, waitForSpaHydration
* reporters/excel-row-writer.ts — Playwright reporter writing
  to BOURACKA-TESTPLAN.xlsx 07_TestRunResults sheet
* playwright.config.ts — 13 projects (3 envs x 4 viewports + extras)"
```

### §2.3 Commit 3 — cross-framework parity (smoke level)

```bash
git add cypress/ testcafe/ selenium/ readyapi/ postman/ mockoon/
git commit -m "feat(cross-framework): smoke parity for Cypress/TestCafe/Selenium/ReadyAPI/Postman

Per _specs/MULTI-PLATFORM-TESTING-STRATEGY-v0.1-CS.md.

* cypress/e2e/bring-up-smoke.cy.ts — Cypress port of bring-up
* testcafe/tests/bring-up-smoke.test.ts — TestCafe port
* selenium/tests/test_bring_up_smoke.py — Selenium pytest port
* readyapi/projects/bouracka-bring-up-smoke-soapui-project.xml — SoapUI smoke
* postman/collections/bouracka-bring-up-smoke.json — Postman collection
* mockoon/n8-sms-gateway.json — N8 SMS Mockoon mock for DEMO

A1-main + alternates ports planned for v0.5.1 (Cypress) /
v0.6.0 (TestCafe + Selenium)."
```

### §2.4 Commit 4 — install + scripts (PowerShell tooling, dev-only)

```bash
git add scripts/ _install/
git commit -m "feat(install): full PowerShell install kit + 7 preflighted gotchas

* scripts/setup-from-zero.ps1 — installer
* scripts/sanity-check.ps1 — 7-component env validator
* scripts/run-{playwright,cypress,testcafe}.ps1 — per-framework runners
* scripts/run-all.ps1 + run-all-and-package.ps1 — orchestration
* scripts/package-{deliverable,results,email-volumes}.ps1 — packaging
* scripts/extract-email-volumes.ps1 — recipient-side extract
* scripts/validate-install.ps1 — environment JSON dump
* scripts/setup-npm-proxy.ps1 — corp proxy helper
* _install/INSTALL-FROM-ZERO-v0.4-CS.md — install guide with 7 gotchas
* _install/SECOPS-COMPONENTS-CS.md — 13-section CS audit doc
* _install/EMAIL-DELIVERY-GUIDE-CS.md — email-side recipient guide

NOTE: PowerShell scripts are dev-only — they are NOT shipped in
email-bound ZIPs (per _specs/EMAIL-DELIVERABILITY-RULES-v0.1-CS.md).
For email shipping, bouracka.py is the entry point."
```

### §2.5 Commit 5 — Python tooling

```bash
git add tools/
git commit -m "feat(tools): Python tooling library — Excel + reporter + audit + migration

* tools/append_test_run_result.py — Playwright reporter Excel UPSERT helper
* tools/validate_workbook.py — 10 invariant checks on Excel TestPlan
* tools/check_priority_matrix.py — priority = severity x urgency audit
* tools/bump_workbook_version.py — semver bump + materialize formulas
* tools/coverage_audit.py — TT x TC coverage matrix audit (Phase 0 informational)
* tools/preship_audit.py — pre-email ZIP gate (forbidden ext + IOC scan)
* tools/migrate_to_v03.py — v0.2 -> v0.3 schema migration
* tools/migrate_to_v04_branch_tagging.py — branch-tagging migration
* tools/migrate_08bugs_v04_1.py — bug dedup schema
* tools/migrate_to_v04_2_tes.py — TES sheets schema
* tools/render_branch_doc.py — render-by-branch master doc
* tools/build_mindmaps.py + tools/render-uml.ps1 + tools/heic-to-jpg.{ps1,sh}
* tools/test_console.py + tools/test-console.ps1 — multi-framework console
* tools/generate_tests.py — code-gen from TC spec MDs
* tools/fix_priority_matrix.py — priority matrix bugfix"
```

### §2.6 Commit 6 — fixtures + test data

```bash
git add fixtures/
git commit -m "feat(fixtures): live recon fixtures + cross-framework test data

* fixtures/codelists.yaml + codelists-live-2026-05-06.yaml — codelist data
* fixtures/api-endpoints-live-2026-05-06.yaml — 23+ API endpoints
* fixtures/live-copy-strings.yaml — 17 STR rows from live recon
* fixtures/field-definitions.yaml — Phase 2/3 field definitions
* fixtures/invalid-login.json — negative-path data
* fixtures/test-data/test-participants.yaml — Adam + Beata + A_specimen (NEW)
* fixtures/test-data/test-vehicles.yaml — SKODA Octavia + VW Golf
* fixtures/test-data/test-photos.yaml — refs to local-only photo collection
* fixtures/test-data/README-CS.md — governance + per-host distribution

Photos themselves (164 MB, 31 files) NOT in repo — staged in
analyticke vstupy/test-data-snippets/ and distributed per-host
(USB / SUPIN intranet share / cloud)."
```

### §2.7 Commit 7 — recon (analytical + drift)

```bash
git add recon/
git commit -m "feat(recon): bottom-up analytical doc + drift forensic + architecture

* recon/ANALYTICAL-DOC-MASTER-v0.4.md — branched master analytical doc
* recon/ANALYTICAL-DOC-INTELLIGENCE-v0.{1,2,3}.md — bottom-up rebuilds
* recon/DELTA-DEMO-vs-PROD-v0.1.md — 26-row environment delta matrix
* recon/DEMO-PUBLIC-LIVE-2026-05-06.md — DEMO public live walk record
* recon/DRIFT-2026-05-07-DEMO-POST-REPORTS-CS.md — drift forensic
  (full POST /api/reports trace from HP Elite + reCAPTCHA-v3 H5 hypothesis)
* recon/ARCHITECTURE-OVERVIEW-v0.1-CS.md — 8 numbered flows + IS CKP map
* recon/integrations/INT-001..INT-009 — per-integration docs
* recon/screens/ — screen-level recon
* recon/screenflows-live/ — live walk recordings
* recon/diagrams/ — UML + mindmaps
* recon/cs-locale-reference/ — CS locale calibration
* recon/uml-templates/, flows/, divergences/, raw/, bugs/, screens/

Includes Pete's first iPhone photo session ingestion (IMG_*) processed via
heic-to-jpg.{ps1,sh}; transcripts under recon/raw/."
```

### §2.8 Commit 8 — strategic governance specs

```bash
git add _specs/
git commit -m "feat(specs): strategic governance docs — CP-SUPIN-04 + 05

* _specs/CP-SUPIN-05-PLAN-CS.md — strategic 5-stream consolidation
* _specs/VMODEL-ASSEMBLY-TT-MAPPING-v0.1-CS.md — V-model TT taxonomy
* _specs/CROSS-FRAMEWORK-DATA-SHARING-v0.1-CS.md — fixture pattern
* _specs/COVERAGE-RULE-STRATEGY-v0.1-CS.md — phased coverage gating
* _specs/CIL-2-ENABLEMENT-v0.1-CS.md — tst.demo.bouracka.cz switchover
* _specs/EMAIL-DELIVERABILITY-RULES-v0.1-CS.md — forbidden ext + IOC patterns
* _specs/MULTI-PLATFORM-TESTING-STRATEGY-v0.1-CS.md — 6-framework strategy
* _specs/TEST-EXECUTION-SUMMARY-FORMAT-v0.1-CS.md — VUP-grade format
* _specs/GITHUB-SYNC-STRATEGY-v0.1-CS.md — independence rule
* _specs/COMPREHENSIVE-MIND-MAP-SUPIN-MIMT-v0.1-CS.md — Mermaid mindmap
* _specs/THREE-DEVICE-PLAN-CS.md v0.2 — HP Elite <test-runner-host> reclassification
* _specs/ROADMAP-4-TARGET-CS.md — 4-target gradual delivery
* _specs/BRANCH-HANDOFF-TEMPLATE-CS.md — Sonnet branch session template
* _specs/BUG-NAMING-CONVENTION-v0.1.md — deterministic dedup
* _specs/BRANCHED-MASTER-DOC-PATTERN-v0.1.md — single-master pattern
* _specs/TESTER-LESSONS-LEARNED-v0.1-CS.md v0.2 — w/ email-deliverability
* _specs/LESSONS-LEARNED-CP-SUPIN-{02,03,04}.md — per-iteration wrap-ups"
```

### §2.9 Commit 9 — Excel TestPlan + entry points

```bash
git add BOURACKA-TESTPLAN-v0.4.2.xlsx
git add bouracka.py READ-ME-FIRST-CS.md
git commit -m "feat(excel,entry): Excel v0.4.2 TestPlan + bouracka.py entry point

* BOURACKA-TESTPLAN-v0.4.2.xlsx — current Excel master with
  13_TestExecutionSummary + 14_AssertionGateResults sheets,
  branch tagging, bug dedup, priority matrix
* bouracka.py — pure-Python orchestrator (setup/test/all/verify/help)
  scanner-friendly (no PS, no IOC strings, no .cmd)
* READ-ME-FIRST-CS.md — three-step tester workflow

Excel earlier versions (v0.1..v0.4.1) excluded — superseded by v0.4.2."
```

### §2.10 Commit 10 — sync + session-close docs

```bash
git add SYNCHRO-MACBOOK-CP-SUPIN-*.md
git add SESSION-CLOSE-CP-SUPIN-*.md
git commit -m "docs(sync): MacBook synchros + session close — CP-SUPIN-04 + 05

* SYNCHRO-MACBOOK-CP-SUPIN-04-2026-05-06.md (initial)
* SYNCHRO-MACBOOK-CP-SUPIN-04-2026-05-07-EOD.md (revision)
* SYNCHRO-MACBOOK-CP-SUPIN-05-2026-05-07-EOD.md (latest)
* SESSION-CLOSE-CP-SUPIN-04-2026-05-06-EOD.md
* SESSION-CLOSE-CP-SUPIN-05-2026-05-07-EOD.md

These are point-in-time snapshots; latest two represent current state."
```

## §3. First push to GitHub — **CONFIRMED public repo**

### §3.1 Remote already exists (Pete confirmed 2026-05-07 mid-session)

```
https://github.com/petr-yamyang/bouracka-tests
```

**Visibility: PUBLIC.** Pre-push scrub items in `_specs/PUBLIC-VISIBILITY-AUDIT-v0.1-CS.md` §4 must be DONE.

### §3.2 Pre-push scrub status (this session)

| Item | Status |
|------|--------|
| LICENSE (MIT) added at repo root | ✅ DONE |
| .gitignore updated (excludes archive/, delivery/, runs/, INSTALL-PLAN-SUPNB, SECOPS-COMPONENTS, recon/raw/, older Excel) | ✅ DONE |
| `_specs/THREE-DEVICE-PLAN-CS.md` scrubbed (`<test-runner-host>` → `<test-runner-host>`, `<test-runner-user>` → `<test-runner-user>`) | ✅ DONE |
| `_specs/CIL-2-ENABLEMENT-v0.1-CS.md` scrubbed (same) | ✅ DONE |
| `_specs/CP-SUPIN-05-PLAN-CS.md` scrubbed | ✅ DONE |
| `_specs/DOCUMENTATION-POLICY-v0.1.md` scrubbed | ✅ DONE |
| `recon/DRIFT-2026-05-07-DEMO-POST-REPORTS-CS.md` correlation-id + azure-ref redacted | ✅ DONE |
| Top-level `README.md` (English, OSS-friendly) | ✅ DONE |

**Pete decision pending:** §2.2 of audit doc — keep concrete ČKP infrastructure names (AISPOV/B3WS/P3WS/D8WS/SEDN) in `recon/ARCHITECTURE-OVERVIEW-v0.1-CS.md`, or abstract them. **Default = KEEP CONCRETE** (already public via Pete's shared diagram). Override before push if you want abstracts.

### §3.3 Push commands (from ThinkPad)

```bash
cd C:\Users\vitez\Documents\VibeCodeProjects\SUPIN\bouracka-tests

# Initialize git
git init
git config user.email "petr.yamyang@gmail.com"
git config user.name "Petr Yamyang"

# Run the 10 atomic commits per §2.1..§2.10 below

# After all 10 commits present, verify
git log --oneline | head -15

# Add remote + first push
git remote add origin https://github.com/petr-yamyang/bouracka-tests.git
git branch -M main
git push -u origin main

# Tag the v0.5.0 milestone
git tag -a v0.5.0 -m "CP-SUPIN-05 seed — v0.5.0
* Drift guard v2 (URL polling)
* Email scanner pivot complete (PS -> Python)
* CP-SUPIN-05 strategic plan + 5 governance docs
* Architecture overview from Pete diagram (8 numbered flows, scrubbed)
* SPECIMEN OP MRZ test data
* Pre-ship audit + coverage audit Phase 0 scaffolds
* Platform assessment with TestCafe -> Selenium+Appium swap
* MI-M-T native automation B+C parallel strategy

Pre-ship audit on bouracka-tests-v0.5.0.zip: PASS
SHA256: 5543993b00d98f091d4b1b60f289d09da1a39489956809a09dee654a7a920de8"

git push origin v0.5.0
```

### §3.4 Post-push GitHub Settings (recommended)

After first push lands successfully, in repo Settings:

1. **Settings > Security > Code security and analysis:**
   - ✅ Enable Dependabot alerts
   - ✅ Enable Dependabot security updates
   - ✅ Enable Secret scanning
   - ✅ Enable Push protection (blocks future credential leaks at push time)
2. **Settings > Branches > Branch protection rules:**
   - Add rule for `main`: require pull request reviews + status checks (when CI configured later)
3. **Settings > Pages:** optional — host docs site if `mimt-simple` documentation needs it later
4. **Description + Topics:** add at top of repo:
   - Description: "Test suite + governance methodology for Bouračka.cz; reference implementation of MI-M-T testing model"
   - Topics: `playwright` `cypress` `selenium` `appium` `test-automation` `czech` `insurance` `mimt` `e2e-testing`

Tag the milestone:

```bash
git tag -a v0.5.0 -m "CP-SUPIN-05 seed — v0.5.0
* Drift guard v2
* Email scanner pivot complete (PS -> Python)
* CP-SUPIN-05 strategic plan + 5 new governance docs
* Architecture overview from Pete diagram (8 numbered flows)
* SPECIMEN OP MRZ test data
* Pre-ship audit script
* Coverage audit Phase 0 scaffold

Pre-ship audit