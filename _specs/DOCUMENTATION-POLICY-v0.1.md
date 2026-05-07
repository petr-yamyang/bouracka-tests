# Documentation Policy — Language + Source-of-Truth Layering — v0.1

> **Trigger.** User direction 2026-05-05 (post-rev-7): the analytical
> document we've been mining is **obsolete** vs the live tst.* envs;
> direct screenflow photos will land as the new ground truth.
> Documentation handed to SUPIN stakeholders must be **strictly Czech**
> for review.
>
> **Audience.** Future contributors writing any artefact in the repo;
> SUPIN reviewers reading SUPIN-facing material.

---

## §1. Language policy (binding)

### §1.1 Two audiences → two language tracks

| Audience | Track | Languages | Examples |
|----------|-------|-----------|----------|
| **SUPIN stakeholders** (architects, QA leads, SecOps, ČAP review board) | **CS-only** | Czech only | Activity diagrams; test plan summary; install guide for SecOps; delivery cover note; user/tester guides |
| **Internal contributors** (operator, ThinkPad sessions, MacBook sessions, future automation engineers) | **Bilingual CS+EN** (CS primary) | Czech primary, English mirror in cells/blocks | Excel `01_TestTargets` / `02_TestCases` (`item_name_cs` + `item_name_en` columns); `recon/integrations/INT-*.md`; `_specs/*.md`; lessons-learned |
| **Vendors / external** (zenID, CDNs, Microsoft, ChatBot tooling) | **EN** when written by us | English primary | Vendor request templates (already drafted bilingually); SecOps allowlist requests; OSS issue reports |

**Rule of thumb.** If a SUPIN stakeholder will read the artefact during
review or operations, write it in CS. If only the operator + automation
will read it, bilingual CS-first is fine.

### §1.2 What "CS-only" means in practice

- **Body text:** 100 % Czech, with diacritics, formal/professional
  register.
- **Labels in diagrams:** node labels, decision diamond questions,
  subgraph titles all CS.
- **Code identifiers may stay in EN.** `accidentReportStatus`,
  `IN_PROGRESS_DRIVERS`, `TC-CP-001`, `INT-002` — these are program
  contracts; keep verbatim. CS gloss is OK as a parenthetical
  ("accidentReportStatus = stav hlášení").
- **External terms.** Where the SUT itself uses a non-CS term
  (REST, JSON, OCR, AISPOV, RUIAN, ZenID), keep verbatim — these are
  proper-noun-grade in the Czech IT register.
- **Numeric/date formats.** Czech locale: `DD.MM.YYYY`,
  decimal-comma, thousands-non-breaking-space (`200 000 Kč`).

### §1.3 What "bilingual CS+EN" means in practice

- Every entity row carries an `_cs` field AND an `_en` field
  (e.g. `item_name_cs` / `item_name_en` already in Excel).
- Markdown sections that are content-heavy: CS first, EN second
  if helpful, but EN never replaces CS.
- TC SPEC.md files: CS-first acceptance criteria; EN-translation
  allowed for code-emission-hint comments.

### §1.4 Where to put each artefact

```
SUPIN-facing (CS-only)
└── delivery/<version>/                     ← assembled per release
    ├── 01_TESTPLAN-CS.md                   ← SUPIN review document
    ├── 02_DIAGRAMY-AKTIVIT-CS.md           ← CS-only activity diagrams
    ├── 03_INSTALL-GUIDE-SECOPS-CS.md       ← CS install plan for SecOps
    ├── 04_SLOVNIK-CS.md                    ← CS-only glossary
    ├── 05_PRIRUCKA-TESTERA-CS.md           ← Tester guide (already CS)
    └── bouracka-tests-vX.Y.Z.zip           ← runnable code

Internal (bilingual)
├── _specs/                                 ← format specs, lessons learned
├── recon/                                  ← intelligence, screen recons
├── fixtures/                               ← YAML catalogues (CS-first)
└── BOURACKA-TESTPLAN-v0.1.xlsx             ← canonical Excel
```

## §2. Source-of-truth layering (binding)

Four tiers, ordered by trust. Higher tier wins on conflict.

> **Revision 2026-05-06 (CP-SUPIN-04 STEP 6):** DEMO went public.
> Tier 2 splits into 2a (DEMO live, scrape-capable) and 2b (PROD/tst live,
> photo-only). Most observation work can now run against DEMO directly;
> PROD-Bouračka stays the integration-fidelity reference for the deltas
> documented in `recon/DELTA-DEMO-vs-PROD-v0.1.md`.

```
TIER 3  — Test execution evidence                ▲ highest trust
   ↳ recon/screenflows-live/runs/                  actual SUT behaviour
   ↳ network traces, SMS captures, e-mail          captured at tester time
     dispatches captured at run time

TIER 2b — PROD/tst live (photo + colleague)      ▲
   ↳ recon/screenflows-live/D00..D17/              what tst.bouracka.cz
   ↳ recon/screenflows-live/flow-…-tst/            actually shows
   ↳ photographed by user / SUPIN colleagues       (integration-fidelity
     (no public/anonymous reach)                    truth: real N8, real
                                                    AISPOV, real ZID)

TIER 2a — DEMO live (publicly reachable as of 2026-05-06) ▲
   ↳ demo.bouracka.cz/formular/ (entry point)      cheapest accurate
   ↳ recon/screenflows-live/flow-…-tst-demo/       ground truth for
   ↳ scrape, screenshot, DOM/network capture       UI shape, copy,
     directly from this session or browser          state machine,
                                                    validation rules
                                                    (caveat: integration
                                                    payloads diverge from
                                                    PROD per delta matrix)

TIER 1  — Analytical document (legacy)           ▲ lowest trust
   ↳ recon/ANALYTICAL-DOC-INTELLIGENCE-v*.md       authored mid-2025 for
   ↳ recon/diagrams/extracted/ACTIVITY-…           MVP release 07/2025;
     -v0.1.md                                      stale vs live
```

**Why DEMO sits *below* PROD on the trust ladder despite being more
accessible.** DEMO is for public showcase; integrations are stubbed or
sandboxed (N8 SMS gateway notably differs — see delta matrix). For
pure UX/UI/state/validation behaviour, DEMO is generally faithful
because it's the same web bundle. For anything crossing the wire to
N8/AISPOV/ZID/CRR/CRV/ROB, only PROD/tst observation is authoritative.

### §2.1 Drift-handling rules

When Tier 1 + (any Tier 2) disagree:
1. **Tier 2 wins.** Edit the Tier 1 document with a footnote
   `~~old text~~ → new text (per live screenflow <ref>; drift
   recorded YYYY-MM-DD)`.
2. Add a row to `recon/SCREENFLOW-DRIFT-LOG.md`.
3. If the change affects a TC SPEC, rev-bump that SPEC's
   `spec_version` and note the source.
4. Re-render any affected activity diagram (Tier 1 source) and
   commit alongside.

When Tier 2a (DEMO) + Tier 2b (PROD/tst) disagree:
1. **Both stand** — the divergence is itself the artefact.
2. Append a row to `recon/DELTA-DEMO-vs-PROD-v0.1.md` with:
   integration / screen / field / observed value on DEMO / observed
   value on PROD / known-or-suspected cause.
3. The affected TC gets a `flagged_env_specific` annotation in
   `02_TestCases::env_constraints`. If both envs need separate
   coverage, fork into `<TC>-DEMO` and `<TC>-PROD` variants.

When Tier 2 + Tier 3 disagree:
1. **Tier 3 wins** — execution evidence is reality.
2. Update the live-screenflow photo (request a new shot if needed)
   and the Tier 2 derivative.
3. If the Tier 3 evidence indicates a bug, file via Bug-template
   into Excel `08_Bugs`.

When Tier 1 has nothing to say (silence) and Tier 2 surfaces a new
behaviour:
1. The behaviour is **real** — Tier 2 stands.
2. Add to the screen recon (`recon/screens/SCR-NNN.md`).
3. If it implies a new TC, add to `02_TestCases`.

### §2.2 Why three tiers (vs the previous single source)

The previous CP-SUPIN-02 cycle treated the analytical doc as
authoritative because it was all we had. The doc was authored ~mid-2025
for the July 2025 MVP release; it is now (relative to the rolling-tst
deployment) about 9–10 months old. Realistically, the SUT has had
post-launch refinements:
- New error sub-reasons not in the doc.
- UI-string copy-edits.
- Possibly new screens for edge cases (insurance partner-specific
  flows, etc.).
- Validation rule tightening based on field experience.

The three-tier model lets us:
- Keep Tier 1's *historical analysis* (12-step process diagram, state
  machine, integration catalogue) as the foundation.
- Layer Tier 2 *live truth* on top — the SUPIN colleague photographs
  what tst.bouracka.cz actually shows today.
- Validate via Tier 3 *execution evidence* when the test suite runs
  against tst.* and either confirms Tier 2 or surfaces a discrepancy.

## §3. The CP-SUPIN-03 deliverable package

### §3.1 What goes into `delivery/v0.1.0/`

| # | File | Lang | Purpose | Source |
|---|------|------|---------|--------|
| 1 | `00_README-CS.md` | CS | Cover note for SUPIN reviewer | NEW |
| 2 | `01_TESTPLAN-CS.md` | CS | High-level test plan summary; R1 scope; deliverables list | derived from `recon/TEST-TARGET-CANDIDATES.md` |
| 3 | `02_DIAGRAMY-AKTIVIT-CS.md` | CS | All 18 D00..D17 activity diagrams in CS | re-cast from `recon/diagrams/extracted/ACTIVITY-DIAGRAMS-v0.1.md` |
| 4 | `03_INSTALL-PRO-SECOPS-CS.md` | CS | Install plan for SecOps approval | translated from `_install/INSTALL-PLAN-SUPNB-v0.1.md` |
| 5 | `04_SLOVNIK-CS.md` | CS | CS-only glossary | derived from `recon/cs-locale-reference/CALIBRATION-CORPUS-v0.1.md` §1b |
| 6 | `05_PRIRUCKA-TESTERA-CS.md` | CS | Tester runbook | already exists as `README-CS.md` |
| 7 | `06_POKRYTI-CS.md` | CS | Coverage gap summary | derived from `recon/COVERAGE-GAP-ANALYSIS.md` |
| 8 | `bouracka-tests-v0.1.0.zip` | n/a | Runnable code | assembled by `scripts/package-deliverable.ps1` |
| 9 | `bouracka-tests-v0.1.0.zip.SHA256` | n/a | Integrity | derived |
| 10 | `MANIFEST.md` | CS | What's in the zip + how to validate | NEW |

### §3.2 What's runnable on day one (the smoke)

A single Playwright test against **public** `bouracka.cz` (so any
laptop reaches it; no SUPIN intranet needed) that:
- Opens landing page
- Asserts title contains `Bouračka`
- Asserts primary CTA `VYPLNIT ZÁZNAM` is visible
- Clicks the CTA
- Asserts URL ends `/formular`
- Asserts reCAPTCHA badge visible
- Runs at mobile viewport `375 × 667` per AMENDMENT 2

This is the **bring-up smoke** — its purpose is NOT to test bouracka,
it is to test the **install + framework + tester pipeline**. If it
runs green on <test-runner-host>, the operator knows the kit is alive. If it
fails, the failure mode is environment (PATH / proxy / firewall),
not SUT.

Spec file: `playwright/tests/bring-up-smoke.spec.ts`. Authored as part
of CP-SUPIN-03 prep.

### §3.3 What stays internal (NOT in delivery)

- `_specs/` — format specs, lessons learned, contracts strategy
- `recon/` — intelligence, integration recons, drift logs
- `fixtures/` — secrets folder (gitignored anyway)
- `outputs/` — operator scratchpad
- `tools/` — script library (operator-side workflow)

## §4. Screenflow ingestion convention (Tier 2)

When new screenflow photos arrive: