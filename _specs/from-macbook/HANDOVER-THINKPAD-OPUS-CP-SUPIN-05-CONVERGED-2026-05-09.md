# Handover — ThinkPad-Opus analytical session — CP-SUPIN-05 converged state — 2026-05-09

**Version:** v0.1.0
**Direction:** MacBook (Sonnet, post Claude 1.6259.1 update) → ThinkPad-Opus (analytical, next session)
**Trigger:** ThinkPad-Sonnet's parallel dev session shipped 5 commits (parity ports + 2 fixes + Cíl-1 baseline) over the period 2026-05-08 16:02 → 2026-05-09 00:58 while MacBook governance work ran. ThinkPad-Opus is opening next; this doc is its session-start primer.
**Authority:** non-binding (handover, not governance); a *map* of the converged state with explicit reading order + recommended analytical priorities. Defers to operator (Pete) on all branch-merge decisions and to ThinkPad-Opus on which OQs to pick up first.
**Audience:** ThinkPad-Opus (primary — read this first); Pete (secondary — review the consolidated operator-action backlog in §6 + §8); future Sonnet sessions on either side (tertiary — for cross-stream visibility).
**Posture:** the project is in a *good* state. Three independent observers (MacBook governance Opus AM, ThinkPad-Sonnet PM, empirical Selenium runtime overnight) have converged on consistent results across the V-model nomenclature, the cross-framework parity model, and the drift-guard predictions. The OQ queue is large (~120 across all streams) but every item has either an external dependency, a clear next-iteration plan, or a low-priority defer. Nothing operationally blocked.

---

## §0. How to use this doc

```
Step 0 (NOW — first 5 minutes of the ThinkPad-Opus session)
   → read THIS file end to end (~10 min reading time)

Step 1 (next 10 min — orient on the bouracka-tests repo state)
   → cd ~/Documents/VibeCodeProjects/SUPIN/bouracka-tests
   → git fetch origin
   → git log --all --oneline --decorate --graph -25
   → confirm 3 active branches + tag v0.5.0 visible (per §1 below)

Step 2 (next 20 min — read the inbound + outbound governance docs in priority order)
   → 1. _config/SYNCHRO-MACBOOK-FROM-OPUS-CP-SUPIN-05-FOLLOWUP-2026-05-08.md  (MacBook governance reply to Sonnet)
   → 2. bouracka-tests/_specs/SYNCHRO-OPUS-FROM-SONNET-CP-SUPIN-05-2026-05-08.md  (Sonnet inbound — original parity push)
   → 3. bouracka-tests/SESSION-CLOSE-CP-SUPIN-05-2026-05-08-IMPORT-FIX.md  (Sonnet's session close — now contains Cíl-1 baseline)
   → 4. bouracka-tests/CHANGELOG.md  (v0.5.1 / v0.5.2 / v0.5.3 entries — concise narrative of last 24h)
   → 5. _config/VOCABULARY-CATALOGUE-CS-EN-V0.1.md §2h + §2h.1  (V-model TT assembly canon — referenced everywhere)

Step 3 (next 15 min — read the catalogue + methodology recent amendments)
   → _config/METHODOLOGY-MAPPING-V0.1.md AMENDMENT 2026-05-08  (formalises catalogue v0.1.4)
   → _config/METH-REFINE-TESTANALYSIS-TESTDESIGN-v0.1.md  (TestCasePackage discipline)

Step 4 (decide what to do — see §8 below for recommended priorities)
```

---

## §1. State of the world at 2026-05-09 — branch landscape + commit graph

### §1.1 Repository-of-record: `petr-yamyang/bouracka-tests`

```
main                                              v0.5.0 baseline (commit 736eedb, 2026-05-07)

Branches on origin (ordered by recency of last commit):

cp-supin-05-cross-framework-parity                ThinkPad-Sonnet delivery (2026-05-08 16:02 → 2026-05-09 00:58)
  f747380  fix(cypress): pageLoadTimeout 60s + scrollIntoView VYPLNIT ZÁZNAM         00:58:57
  2021539  fix(cypress): resolve covers import — data-loader not nav-helpers (8)     00:41:34
  7cf9865  docs: record Selenium Cíl-1 baseline — 5 PASS 5 SKIP                      00:07:11
  dce8911  fix(selenium): resolve selenium.helpers namespace collision; pytest.ini   2026-05-08 16:52
  5c865c8  feat(cp-supin-05): cross-framework parity ports — Cypress + Selenium       2026-05-08 16:02

macbook/cp-supin-06-prep-2026-05-08               MacBook governance (PR pending — operator action)
  f8ac550  feat(governance): MacBook→Opus sync CP-SUPIN-06 prep                       2026-05-08 15:00

(proposed) macbook/cp-supin-05-followup-2026-05-09   NOT YET PUSHED — to carry MacBook's CP-SUPIN-05 follow-up arc
  (would carry: catalogue v0.1.4 §2h.1 in-place patch + SYNCHRO-MACBOOK-FROM-OPUS reply)
```

### §1.2 MacBook-side `_config/` state (uncommitted; ready to commit per recipe in `_config/SESSION-CLOSE-MACBOOK-2026-05-08-PART-2.md` §3)

```
~/Documents/VibeCodeProjects/                       branch: macbook  (HEAD: 455ad7a — pre-arc)
  Modified (3):
    .gitignore                                       — security gap fix (credentials.yaml + _archive/)
    CLAUDE.md                                        — handoff block updated
    _config/METHODOLOGY-MAPPING-V0.1.md              — AMENDMENT 2026-05-08 added

  Untracked (new, intended for commit):
    Multi-day Opus session (Part 1):
      _config/PHYSICS-CALIBRATION-EXTENSION-v0.2.md
      _config/SUPIN-N8-CONTRACT-ANALYSIS-v0.1.md
      _config/SUPIN-ARCH-HARVEST-DISCIPLINE-v0.1.md
      _config/METH-REFINE-TESTANALYSIS-TESTDESIGN-v0.1.md
      _config/OPUS-REVIEW-THINKPAD-DELIVERY-v0.1.0-2026-05-05.md
      _config/SYNCHRO-MACBOOK-TO-OPUS-CP-SUPIN-06-2026-05-08.md
      _config/SYNCHRO-THINKPAD-CP-SUPIN-03-2026-05-06.md
      _config/CLIENT-PILOT-SUPIN-V0.1.md
      _config/CLIENT-PILOT-SUPIN-FUTURE-REPO-STRUCTURE-V0.1.md
      _config/CLIENT-PILOT-SUPIN-RECON-TEMPLATES-LIGHT-V0.1.md
      _config/CLIENT-PILOT-SUPIN-RECON-TEMPLATES-V0.1.md
      _config/HANDOVER-CLIENT-PILOT-THINKPAD-V0.1.md
      _config/SESSION-CLOSE-MACBOOK-2026-05-08.md
      _config/sync-to-bouracka-tests.sh                 (bash; with OOM-kill bugfix from Part 2)
      3-fold-path/backlog/KH-SIM-PUBLIC-EXTENSION-v0.2.md
      3-fold-path/backlog/PHYSICS-NEW-SOLVERS-v0.1.md
      3-fold-path/backlog/PIL-07-EP00-RUN-READINESS-v0.1.md
      (4th 3-fold-path/backlog/ doc — see Part 2)

    Post Claude 1.6259.1 update (Part 2):
      _config/VOCABULARY-CATALOGUE-CS-EN-V0.1.md       (v0.1.4 incl. §2h.1 in-place patch from Part 3)
      _config/SESSION-CLOSE-MACBOOK-2026-05-08-PART-2.md
      mimt-governance/                                  (10 files; ~1100 LOC; 13/13 smoke tests PASS)

    CP-SUPIN-05 follow-up (Part 3):
      _config/SYNCHRO-MACBOOK-FROM-OPUS-CP-SUPIN-05-FOLLOWUP-2026-05-08.md

    THIS FILE (Part 4 — converged-state handover):
      _config/HANDOVER-THINKPAD-OPUS-CP-SUPIN-05-CONVERGED-2026-05-09.md
```

### §1.3 What this means in practice

**The bouracka-tests repo IS the reconciliation point.** Three streams of work need to converge there:

| Stream | Source | Currently lives |
|---|---|---|
| Sonnet delivery (parity ports + Cíl-1 baseline) | ThinkPad bouracka-tests working tree | ✅ pushed to `origin/cp-supin-05-cross-framework-parity` |
| MacBook governance Part 1 (CP-SUPIN-06 prep) | MacBook bouracka-tests working tree | ✅ pushed to `origin/macbook/cp-supin-06-prep-2026-05-08`; PR not opened |
| MacBook governance Parts 2+3+4 (post-update + follow-up + this handover) | MacBook _config/ working tree | ⚠ NOT YET committed locally; recipe in PART-2 §3 |

**Critical operator action sequence (per SYNCHRO §6 Option A — recommended path):**

```
1. Pete: clear ~/Documents/VibeCodeProjects/.git/index.lock + run PART-2 §3 commit recipe
2. Pete: push Parts 2+3+4 → create new branch macbook/cp-supin-05-followup-2026-05-09 + push
3. Pete: open 3 PRs in this order:
   (a) cp-supin-05-cross-framework-parity → main           [delivery first]
   (b) macbook/cp-supin-06-prep-2026-05-08 → main          [governance batch 1]
   (c) macbook/cp-supin-05-followup-2026-05-09 → main      [governance batch 2 — references batch 1]
4. ThinkPad-Opus (next session — i.e. THIS session): branches off refreshed main when (a-c) merged
```

---

## §2. Empirical Cíl-1 baseline — Selenium 5 PASS / 5 SKIP confirmed

Per CHANGELOG v0.5.2 entry (commit `7cf9865`, 2026-05-09 00:07): the first empirical run of the Selenium suite at Cíl 1 (demo.bouracka.cz) on Pete's ThinkPad (Windows 10, Python 3.10.11):

```
5 passed, 5 skipped, 1 warning in 65.47s
```

| TC | Status | Evidence |
|---|:---:|---|
| `test_TC_CP_001_bring_up_smoke` | PASS | `GET /` → HTTP 200 |
| `TC-CP-A2-ALT-6` | PASS | Police accordion: 3 bullets visible + `tel:158` link present |
| `TC-CP-A2-ALT-7` | PASS | Enumerations API: ≥10 companies, ≥200 brands, 8×403 expected |
| `TC-CP-A2-ALT-8` | PASS | DEMO banner Δ11 + Δ22 strings visible |
| `TC-CP-A2-ALT-9` | PASS (soft) | POST /api/reports → 403 drift; `UserWarning` issued; 200-or-403 contract honoured |
| `TC-CP-A2-ALT-10` | SKIP | Drift guard: SPA routed to `/error/timeout` |
| `TC-CP-A2-ALT-1` | SKIP | (same drift guard) |
| `TC-CP-A2-ALT-4` | SKIP | (same drift guard) |
| `TC-CP-A2-ALT-5` | SKIP | (same drift guard) |
| `TC-CP-A1-MAIN-DEMO` | SKIP | (same drift guard — full happy-day cannot reach Phase 1 under reCAPTCHA-v3 403) |

**ALT-9 drift payload captured (per CHANGELOG):**
```json
{
  "correlationId": "54a6e0a3-...",
  "status": 403,
  "error": "Forbidden",
  "path": "/reports"
}
```

This is gold-standard *evidence* of the drift forensic captured cleanly. The test didn't fail; it warned, attached the payload, and continued. Exactly the right behaviour.

---

## §3. R-CONFIRM-1 second instance — pre-execution prediction matched empirical reality

The first R-CONFIRM-1 instance (V-model nomenclature convergence) was documented in `_config/SYNCHRO-MACBOOK-FROM-OPUS-CP-SUPIN-05-FOLLOWUP-2026-05-08.md` §2 — independent observers reaching the same architectural conclusion.

**This is a different flavour: prediction-vs-empirical-reality alignment.** Sonnet's SYNCHRO §4 ("Expected outcomes at Cíl 1 — per drift status") published these *pre-execution* predictions on 2026-05-08 ~14:xx (before any browsers ran):

| TC | Predicted | Observed (per §2 above) | Match |
|---|---|---|:--:|
| ALT-7 | passed | PASS | ✓ |
| ALT-8 | passed | PASS | ✓ |
| ALT-6 | passed | PASS | ✓ |
| ALT-9 | soft (200 or 403) | PASS soft (403) | ✓ |
| ALT-10 | depends (probe captures whatever fires) | SKIP via drift guard | ✓ (drift guard activated as designed) |
| ALT-5 | skip on drift | SKIP | ✓ |
| ALT-1 | skip on drift | SKIP | ✓ |
| ALT-4 | skip on drift | SKIP | ✓ |
| A1-MAIN-DEMO | skip on drift | SKIP | ✓ |

**9/9 match.** The pre-execution prediction is the *reference frame* against which the empirical run is judged. A 9/9 match means the test design's drift-guard logic operationally maps to reality.

**Governance interpretation (per AMENDMENT 2026-05-08 §4 / R-CONFIRM-1):** the second instance is an *internal* convergence (one observer's design vs the same observer's empirical run), but it confirms the *design discipline* is correct rather than the *external model*. Both are valuable. Worth folding into the harvest-discipline doc as Exemplar 2 (alongside the Selenium namespace lesson — Exemplar 1).

This is also concrete evidence that the test code's `covers([TT-...])` annotations are *actually executable*, not just documentation. The `covers([])` calls compile, run, and the V-model TT assembly map can now be hydrated from real test execution.

---

## §4. What's still pending — empirical + source-integrity items

### §4.1 Cypress empirical run (still pending)

CHANGELOG v0.5.3 (commit `2021539`) and the timeout/scrollIntoView fix (commit `f747380`) were both **code-review fixes**, not empirically validated. Sonnet caught them via:
- v0.5.3: `covers` import was from `nav-helpers` (wrong) — should be `data-loader`. Fixed in 8 spec files. Webpack would have raised `TypeError: (0, nav_helpers_1.covers) is not a function` at runtime.
- v0.5.4 (de facto, no version bumped): `pageLoadTimeout 30s → 60s` (cold-load exceeds 30s in headless Chrome on demo.bouracka.cz) + `scrollIntoView()` on the VYPLNIT ZÁZNAM button (375px mobile viewport has a MUI Typography element overlapping the button at z-order).

**Recommended next analytical step (ThinkPad-Opus):**

```powershell
cd ~/Documents/VibeCodeProjects/SUPIN/bouracka-tests
git checkout cp-supin-05-cross-framework-parity
git pull

# Verify Chrome is installed
Get-Command chrome.exe                              # if not found, install

# Run Cypress headless
npx cypress run --browser chrome --reporter json `
  --reporter-options "output=cypress/cypress-results/results.json"

# Expected outcome (per the same drift-guard + framework-parity pattern as Selenium):
#   PASS: ALT-7, ALT-8, ALT-6, ALT-9 (soft 200|403)
#   SKIP: ALT-10, ALT-1, ALT-4, ALT-5, A1-MAIN-DEMO
#   ~ same 5 PASS / 5 SKIP shape

# Then consolidate
python tools/consolidate_results.py
```

If Cypress diverges from Selenium at Cíl 1, that's a new analytical finding. The most likely divergence sources (per Sonnet SYNCHRO §4 design-differences table): network capture mechanics on ALT-10, GDPR consent intercept on ALT-4. Both are *known design differences*, not framework bugs — but they could surface as different SKIP-vs-PASS-vs-fail behaviour under load.

### §4.2 Q-PARITY-3 — Playwright `a2-alternates-demo.spec.ts` truncation

Diagnosis (per `_config/SYNCHRO-MACBOOK-FROM-OPUS-CP-SUPIN-05-FOLLOWUP-2026-05-08.md` §4):
- Same SHA-256 / size 11233 bytes / 228 lines across all 5 refs (`main`, `tags/v0.5.0`, all 3 active branches).
- Truncation is in the v0.5.0 seed commit `736eedb` itself.
- Hypothesis: author-side editor truncation pre-commit. NOT a git push corruption.
- Recovery: reconstruct from Sonnet's structurally-equivalent Cypress port (`cypress/e2e/a2-alternates-demo/alt-10-spa-post-probe.cy.ts`).
- Recipe: see SYNCHRO §4 above.

**Recommended analytical step (ThinkPad-Opus, light):** verify hypothesis on ThinkPad — search VSCode local history for un-truncated original; check Recycle Bin. If found, ship as `v0.5.4` fix on a new fixup branch. If not found, reconstruct from Cypress port.

### §4.3 Q-PARITY-4 — `a1-main-happy-day-demo.spec.ts` "abel(/Model vozidla/i)" — DISCREPANCY FLAGGED

Sonnet's CHANGELOG v0.5.1 entry says:
> *"Fixed — Playwright source typo (documented, not changed): `playwright/tests/a1-main-happy-day-demo.spec.ts` line ~221: `abel(/Model vozidla/i)` is a typo for `await page.getLabel(...)` — corrected in both Cypress and Selenium ports."*

**Empirical verification (MacBook 2026-05-09 AM):** the actual published file at `origin/cp-supin-05-cross-framework-parity:playwright/tests/a1-main-happy-day-demo.spec.ts` has 319 lines / 19038 bytes; lines 215-230 contain clean Phase-3 `setTextarea` + `getByRole` + `Pokračovat` / `radio` calls; **no `abel(...)` typo present**. Searched the whole file for `abel\|Model voz\|getL[a-z]*el` — no match.

Possible explanations:
1. Sonnet's local working tree (ThinkPad) had a different state than the committed source. Some uncommitted edit may have been visible to Sonnet during the port but never reached origin.
2. The reference is to a different file (perhaps a draft `.spec.ts.bak` not visible on origin).
3. Sonnet's notes from a memory of an earlier authoring step that was already corrected.

**Recommended analytical step (ThinkPad-Opus):** check Pete's ThinkPad working tree — `git status playwright/`, `find playwright -name "*.bak"`, `Get-ChildItem $env:APPDATA\Code\User\History` — for evidence of the typo's previous existence. Outcome:
- If found in local-history: confirms hypothesis 1, mark Q-PARITY-4 closed-as-historical
- If not found: ask Sonnet directly during next ThinkPad-Sonnet session what file/line they were referring to

### §4.4 Cíl-2 access (`tst.demo.bouracka.cz`) — external block

All 5 SKIPs at Cíl 1 are due to reCAPTCHA-v3 403 drift. Cíl 2 is the staging environment without the reCAPTCHA gate. Once Pete has access (per CLAUDE.md handoff §2 external waits), the SKIP set should drop to zero (or the divergences become real signal, not noise).

### §4.5 The HOLDS — non-CP-SUPIN work still forbidden

Per CLAUDE.md handoff: deferred 3-fold-path items (CC-005, CC-006, AUTH-004, ARCH-E01) and mim2000 v1.10.0 prep remain on hold until SUPIN/Bouračka sync arc fully reconciles (operator confirms PRs merged). ThinkPad-Opus should NOT pick these up before the 3 PRs land.

---

## §5. MacBook governance state — summary of what landed in the multi-day arc

### §5.1 Catalogue v0.1.4 (was v0.1.2; in-place §2h.1 patch later 2026-05-08)

`_config/VOCABULARY-CATALOGUE-CS-EN-V0.1.md` — 1031 lines, 17 sections.

Foundational rules introduced in v0.1.4:
- **R-DESIGN-1 reframed** — phased coverage gating supersedes strict-from-day-1 (§2f.6, 4 phases)
- **R-DECOUPLED-1** — 4-track versioning policy (schema / content / toolchain / release) (§2g)
- **R-VMODEL-1** — V-model assembly layer as transposition basis sister to FURPS+ (§2h, 4 layers FUNC/SCRN/LOV/ACTV)
- **R-VMODEL-2** — E2E meta-layer composes base layers (§2h.1, in-place patch — folds 8 TT codes from Sonnet's port)

Cross-axis matrix (FURPS+ × V-model) documented; 5×4 = 20 cells (worked example in §2h table; OQ-VOC-14 questions binding-vs-analytical for the reporting view).

### §5.2 METHODOLOGY-MAPPING with 2 amendments

`_config/METHODOLOGY-MAPPING-V0.1.md` — 427 lines, 2 amendments:

**AMENDMENT 2026-05-03 (v0.1.1)** — earlier session:
1. VUP canonical UP rendering bound
2. Diligence (not Attention) as 3rd assessment dimension
3. Plan ≠ Schedule ≠ Estimate distinction
4. CAST CO/KDO/KDY/KDE/JAK matrix on `test_targets`
5. CAST "podnět" (impulse) canonical
6. Catalogue is a VUP Glossary artefact

**AMENDMENT 2026-05-08 (v0.1.2)** — this multi-day arc:
1. Cartesian ↔ V-model duality (R-DUALITY-1)
2. Coverage gating phase-in (R-DESIGN-1 reframed)
3. TestCasePackage / TestCase split (R-PACKAGE-1) — TPC vs TC layers
4. Operational confirmation pattern (R-CONFIRM-1)
5. Decoupled-versioning policy (R-DECOUPLED-1 doctrinal)
6. Catalogue v0.1.1 → v0.1.4 cross-reference update

### §5.3 mimt-governance/ scaffold v0.1.0

`~/Documents/VibeCodeProjects/mimt-governance/` — pip-installable Python package; ~1100 LOC; 13/13 smoke tests PASS.

| Module | Status |
|---|---|
| `preship_audit` | REAL PORT — universal email-deliverability gate |
| `validate_priority` | REAL PORT — Sev × Urg → Pri matrix validator + optional `--with-diligence` per catalogue §2c.5 |
| `render_branched_doc` | STUB — awaiting `applies_to_*` grammar formalisation post CP-SUPIN-06 |
| `append_run_result` | STUB — awaiting OQ-CONTRACT-01..04 resolution + reporter-contract stability |

CLI: `mimt-cli {preship-audit | validate-priority | render-branched-doc | append-run-result}`. Roadmap to v0.2 (per `_config/SYNCHRO-MACBOOK-FROM-OPUS-CP-SUPIN-05-FOLLOWUP-2026-05-08.md` §5): add `test-console` (port `bouracka-tests/tools/test_console.py`); add `covers-validator` (new build); adopt cross-framework JSON schema from Sonnet's `consolidate_results.py`.

### §5.4 SESSION-CLOSE chain

| Doc | Coverage |
|---|---|
| `SESSION-CLOSE-MACBOOK-2026-05-08.md` | Multi-day Opus arc (Part 1) — physics + methodology + harvest + initial SUPIN sync |
| `SESSION-CLOSE-MACBOOK-2026-05-08-PART-2.md` (with §A addendum) | Post Claude 1.6259.1 update (Part 2) + CP-SUPIN-05 follow-up (Part 3 in §A); has the operator commit recipe in §3 |
| THIS DOC (Part 4 — converged-state handover) | The reconciled view + analytical priorities for the next ThinkPad-Opus session |

---

## §6. Three-branch reconciliation — current state + recommended sequence

Per `_config/SYNCHRO-MACBOOK-FROM-OPUS-CP-SUPIN-05-FOLLOWUP-2026-05-08.md` §6 — Option A (sequential merges) recommended:

| Step | PR | Source branch → target | Status | Notes |
|:--:|:--:|---|:--:|---|
| 1 | (a) | `cp-supin-05-cross-framework-parity` → `main` | NOT YET OPENED | Delivery first — independently runnable; merge unblocks ThinkPad iteration |
| 2 | (b) | `macbook/cp-supin-06-prep-2026-05-08` → `main` | NOT YET OPENED (since 2026-05-08 morning) | Governance batch 1 — 5 docs in `_specs/from-macbook/` + SYNCHRO at root |
| 3 | (c) | `macbook/cp-supin-05-followup-2026-05-09` → `main` | BRANCH NOT YET CREATED | Governance batch 2 — depends on (b) being merged for clean rebase; carries Parts 2+3+4 |

**Operator decision tree (per SYNCHRO §6):**

| If Pete prefers | Go with | Comment |
|---|:--:|---|
| Linear history; per-PR review | Option A (sequential) | Recommended — current default |
| Single big-batch review | Option B (integration branch) | Only if reviewer prefers seeing reconciled state |
| Delivery now, governance later | Option C (interleaved) | Risks "governance optional" signal |

---

## §7. OQ queue — consolidated state across all streams

| Source | Total open | Critical (Pri-A) | Notes |
|---|:--:|:--:|---|
| OQ-VOC-* (catalogue) | 14 open / 1 closed | 4 (-08, -09, -11, -13) | -01 closed; -11 + -13 + -15 added v0.1.4; -15 added in-place §2h.1 patch |
| OQ-METH-* (methodology) | 14 | 5 (-07, -08, -11, -12, -13) | -11..-14 added by AMENDMENT 2026-05-08 |
| OQ-MB-* (MacBook governance) | 15 | 5 (-01, -02, -04, -07, -11, -13) | -11..-15 added by SYNCHRO 2026-05-08 |
| OQ-PARITY-* (parity work) | 4 | 1 (-3) | -3 diagnosed; -4 newly flagged in §4.3 above |
| OQ-CONTRACT-* (MI-M-T import contract) | 4 | 1 (-01) | -01..-04 from SYNCHRO §4.4; gate on Phase 1 design |
| OQ-N8-* (SUPIN N8 contract) | 10 | (mixed) | per `_config/SUPIN-N8-CONTRACT-ANALYSIS-v0.1.md` §16 |
| OQ-ARCH-* (harvest discipline) | 25 | (mixed) | per `_config/SUPIN-ARCH-HARVEST-DISCIPLINE-v0.1.md` §8 §2.2 |
| OQ-PHYS-* (physics) | ~20 | (mixed) | physics arc — gated on ThinkPad implementation; ~3+ weeks out |
| **Total** | **~106 open** | **~17 critical** | All have either external dependency or clear next-iteration |

**Top-priority items for ThinkPad-Opus to pick up now (subset of ~17 critical):**

1. **OQ-MB-11** (A/A/A): branch reconciliation strategy — Pete picks Option A/B/C. Discussed §6 above.
2. **OQ-PARITY-3** (A/A/A): Playwright `a2-alternates-demo.spec.ts` reconstruction. Recipe in SYNCHRO §4. Light analytical work + ship as v0.5.4.
3. **OQ-PARITY-4** (newly flagged §4.3): the "abel(/Model vozidla/i)" discrepancy. Investigate ThinkPad working tree.
4. **OQ-MB-02** (A/A/A): Bouračka workbook v0.5.1 schema migration combining `01a_AnalysisTransposition` + `15_VModelAssemblyMap` + `16_CoverageMatrix` + `02e_TestCasePackages` + 7 column extensions.
5. **OQ-VOC-15** (B/A/A): `tt_e2e_composes` JSON shape — propose `["TT-FUNC-rpRegex", ...]` flat array; cross-check with Sonnet's `covers()` calls.

---

## §8. Recommended next-session ThinkPad-Opus analytical priorities

In execution order. Each item's effort estimate is a rough guide.

### §8.1 Priority A (must land in this session)

| # | Item | Effort | Rationale |
|:--:|---|:--:|---|
| 1 | Read this doc + reading order in §0 step 2 + §0 step 3 | 30 min | Orientation. ThinkPad-Opus needs to see the converged state before deciding anything. |
| 2 | Verify Pete's ThinkPad working tree state (per §4.3 — search for the alleged abel typo's history) | 30 min | Either closes Q-PARITY-4 cleanly OR refines it for next ThinkPad-Sonnet session. |
| 3 | Run Cypress empirically at Cíl 1 (per §4.1 recipe) | 1 h | Closes the empirical loop on cross-framework parity; either confirms 5 PASS / 5 SKIP shape or surfaces real divergences. |
| 4 | Run `python tools/consolidate_results.py` to merge Selenium + Cypress results | 5 min | Tests Sonnet's consolidator end-to-end; produces first cross-framework parity report at Cíl 1. |
| 5 | If Cypress diverges from Selenium: document the divergence in a new note `_specs/CIL-1-PARITY-DIVERGENCES-2026-05-09.md` | 1 h | Real signal — feeds back into mimt-governance `coverage-validator` design. |

### §8.2 Priority B (preferred; if time)

| # | Item | Effort | Rationale |
|:--:|---|:--:|---|
| 6 | Reconstruct Playwright ALT-10 tail per Q-PARITY-3 SYNCHRO §4 recipe | 1.5 h | Restores source-of-truth integrity; ships as `v0.5.4` on a new fixup branch. |
| 7 | Author Bouračka workbook v0.5.1 schema migration plan (`migrate_to_v0_5_1_unified_transposition.py`) per SYNCHRO §2.2 row 1 + OQ-MB-02 | 2 h | The unified transposition migration that lands `01a_AnalysisTransposition` + `15_VModelAssemblyMap` + `16_CoverageMatrix` + `02e_TestCasePackages` + 7 column extensions in one move. |
| 8 | Lift the cross-framework JSON schema from `tools/consolidate_results.py` into `_specs/CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.md` per OQ-MB-14 | 1 h | De-facto resolves OQ-CONTRACT-03; binding format for future MI-M-T runner backend. |
| 9 | Fold Selenium namespace-collision lesson as Exemplar 1 in `_config/SUPIN-ARCH-HARVEST-DISCIPLINE-v0.1.md` §6 per OQ-MB-12 | 30 min | Concrete R-MODEL-IS-CODE example; preserves the diagnosis pattern. |
| 10 | Fold prediction-vs-empirical-reality as Exemplar 2 in same harvest doc | 30 min | The 9/9 match per §3 above; concrete R-CONFIRM-1 example (different flavour from the V-model nomenclature). |

### §8.3 Priority C (deferred; opportunity-driven)

| # | Item | Trigger to pick up |
|:--:|---|---|
| 11 | Schema migration `133_add_test_case_packages.sql` per OQ-METH-13 | Once OQ-MB-02 schema migration plan is approved |
| 12 | Schema migration `131_add_coverage_rule_phase.sql` (catalogue §2f.6) | Once OQ-MB-04 phase-advance criteria confirmed |
| 13 | Empirical Cíl-2 run when access lands | External wait |
| 14 | OQ-MB-13: `tt_e2e_composes` validation hook in mimt-governance v0.2 | mimt-governance v0.2 design starts |

---

## §9. Cross-references map — where things live

```
~/Documents/VibeCodeProjects/                              [MacBook parent monorepo]
├── _config/
│   ├── CLAUDE.md                                          [boot — read first]
│   ├── VOCABULARY-CATALOGUE-CS-EN-V0.1.md                 [v0.1.4 — vocab + R-rules canon]
│   ├── METHODOLOGY-MAPPING-V0.1.md                        [methodology + 2 amendments]
│   ├── METH-REFINE-TESTANALYSIS-TESTDESIGN-v0.1.md        [TestCasePackage discipline]
│   ├── SUPIN-N8-CONTRACT-ANALYSIS-v0.1.md                 [SUPIN platform pattern]
│   ├── SUPIN-ARCH-HARVEST-DISCIPLINE-v0.1.md              [R-HARVEST-1..R-MODEL-IS-CODE]
│   ├── OPUS-REVIEW-THINKPAD-DELIVERY-v0.1.0-2026-05-05.md [historical context]
│   ├── SYNCHRO-MACBOOK-TO-OPUS-CP-SUPIN-06-2026-05-08.md  [outbound sync — pushed]
│   ├── SYNCHRO-MACBOOK-FROM-OPUS-CP-SUPIN-05-FOLLOWUP-2026-05-08.md  [outbound governance reply — pending push]
│   ├── SESSION-CLOSE-MACBOOK-2026-05-08.md                [Part 1 close]
│   ├── SESSION-CLOSE-MACBOOK-2026-05-08-PART-2.md         [Parts 2+3 close + §A addendum]
│   ├── HANDOVER-THINKPAD-OPUS-CP-SUPIN-05-CONVERGED-2026-05-09.md   [THIS file — Part 4]
│   ├── sync-to-bouracka-tests.sh                          [idempotent sync; OOM-bug fixed]
│   ├── credentials.yaml                                   [GITIGNORED — never commit]
│   └── (5 CLIENT-PILOT-SUPIN-* + HANDOVER-CLIENT-PILOT-THINKPAD docs)
├── 3-fold-path/
│   └── backlog/
│       ├── KH-SIM-PUBLIC-EXTENSION-v0.2.md
│       ├── PHYSICS-CALIBRATION-EXTENSION-v0.2.md
│       ├── PHYSICS-NEW-SOLVERS-v0.1.md
│       └── PIL-07-EP00-RUN-READINESS-v0.1.md
├── mimt-governance/                                       [universal governance toolkit]
│   ├── pyproject.toml                                     [mimt-cli script]
│   ├── README.md                                          [module map]
│   ├── src/mimt_governance/
│   │   ├── preship_audit.py                               [REAL PORT]
│   │   ├── validate_priority.py                           [REAL PORT]
│   │   ├── render_branched_doc.py                         [STUB]
│   │   ├── append_run_result.py                           [STUB]
│   │   └── cli.py
│   └── tests/test_smoke.py                                [13/13 PASS]
├── SUPIN/bouracka-tests/                                  [GITIGNORED nested clone]
└── _archive/                                              [GITIGNORED — local only]


petr-yamyang/bouracka-tests/                              [bouracka-tests repo]
├── main                                                   [v0.5.0 baseline]
├── cp-supin-05-cross-framework-parity                     [Sonnet — 5 commits — pushed]
│   ├── playwright/tests/
│   │   ├── a1-main-happy-day-demo.spec.ts                 [319 lines — Q-PARITY-4 discrepancy in §4.3]
│   │   └── a2-alternates-demo.spec.ts                     [228 lines — Q-PARITY-3 truncation]
│   ├── cypress/
│   │   ├── cypress.config.ts                              [pageLoadTimeout 60s post f747380]
│   │   ├── e2e/a1-main-demo/main-happy-day.cy.ts          [scrollIntoView fix post f747380]
│   │   ├── e2e/a2-alternates-demo/alt-{1,4,5,6,7,8,9,10}.cy.ts
│   │   └── support/{data-loader,nav-helpers}.ts
│   ├── selenium/
│   │   ├── pytest.ini                                     [pythonpath = .]
│   │   ├── conftest.py
│   │   ├── helpers/{data_loader,nav_helpers}.py
│   │   ├── tests/a1_main/test_main_happy_day.py
│   │   └── tests/a2_alternates/test_alt_{1,4,5,6,7,8,9,10}.py
│   ├── tools/
│   │   ├── consolidate_results.py                         [NEW in 5c865c8]
│   │   ├── preship_audit.py                               [origin of mimt-governance port]
│   │   ├── check_priority_matrix.py                       [origin of mimt-governance port]
│   │   ├── render_branch_doc.py                           [origin of stub]
│   │   ├── append_test_run_result.py                      [origin of stub]
│   │   └── (other tools)
│   ├── _specs/SYNCHRO-OPUS-FROM-SONNET-CP-SUPIN-05-2026-05-08.md  [inbound from Sonnet]
│   ├── SESSION-CLOSE-CP-SUPIN-05-2026-05-08-IMPORT-FIX.md         [now contains Cíl-1 baseline]
│   └── CHANGELOG.md                                       [v0.5.1 / v0.5.2 / v0.5.3]
└── macbook/cp-supin-06-prep-2026-05-08                    [MacBook — 1 commit — pushed; PR pending]
    ├── SYNCHRO-MACBOOK-TO-OPUS-CP-SUPIN-06-2026-05-08.md
    └── _specs/from-macbook/{5 governance docs}
```

---

## §10. Status footer

| Item | Value |
|------|-------|
| Document | `HANDOVER-THINKPAD-OPUS-CP-SUPIN-05-CONVERGED-2026-05-09.md` |
| Output position | `_config/HANDOVER-THINKPAD-OPUS-CP-SUPIN-05-CONVERGED-2026-05-09.md` |
| Direction | MacBook (Sonnet, post Claude 1.6259.1 update) → ThinkPad-Opus (analytical, next session) |
| Trigger | ThinkPad-Sonnet's converged state — 5 commits over 16h spanning 2026-05-08 16:02 → 2026-05-09 00:58 |
| Sections | 11 (orientation / branch landscape / Cíl-1 baseline / R-CONFIRM-1 prediction / what's pending / governance state / branch reconciliation / OQ queue / analytical priorities / cross-references map / footer) |
| Empirical Cíl-1 result | 5 PASS / 5 SKIP — drift guard confirmed; 9/9 match with Sonnet's pre-execution prediction |
| New foundational rules introduced | None (handover; references existing) |
| New OQs flagged | 1 (OQ-PARITY-4 split out from Sonnet's CHANGELOG mention) |
| Recommended priorities | 5 priority-A (orientation + investigation + Cypress run + consolidation + divergence doc) + 5 priority-B (Playwright reconstruction + workbook migration + JSON schema + 2 harvest exemplars) + 4 priority-C (deferred) |
| OQ queue total | ~106 open / ~17 critical across all streams |
| Branch landscape | 3 branches active on origin (`main` v0.5.0; `cp-supin-05-cross-framework-parity`; `macbook/cp-supin-06-prep-2026-05-08`); 1 proposed (`macbook/cp-supin-05-followup-2026-05-09`) |
| Critical-path operator action | Run PART-2 §3 commit recipe; create proposed branch (c); open 3 PRs in sequence |
| Status | v0.1 — ready for ThinkPad-Opus consumption + Pete's review of operator-action sequence in §1.3 |

---

*HANDOVER-THINKPAD-OPUS-CP-SUPIN-05-CONVERGED-2026-05-09.md — 2026-05-09 AM — MacBook Cowork session — Sonnet (post Claude 1.6259.1 update; CP-SUPIN-05 follow-up Part 4)*
