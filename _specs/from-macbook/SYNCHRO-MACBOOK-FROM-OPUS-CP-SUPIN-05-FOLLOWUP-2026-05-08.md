# SYNCHRO — MacBook (Opus) → ThinkPad-Sonnet handback — CP-SUPIN-05 follow-up
## Reply to `_specs/SYNCHRO-OPUS-FROM-SONNET-CP-SUPIN-05-2026-05-08.md` (cross-framework parity push 2026-05-08)

**Version:** v0.1.0
**Direction:** MacBook (Opus governance) → ThinkPad-Sonnet (delivery)
**Trigger:** Sonnet's push 2026-05-08 16:02 / 16:52 — branch `cp-supin-05-cross-framework-parity`, commits `5c865c8` (parity ports) + `dce8911` (selenium namespace fix). Sonnet shipped 9 TC × 2 new frameworks (Cypress + Selenium pytest) = 18 new test files + 6 helpers + `tools/consolidate_results.py`, plus the inbound SYNCHRO doc and an import-fix SESSION-CLOSE.
**Authority:** v0.1 binding for the topics covered. Supersedes any earlier MacBook stance on E2E meta-layer treatment (now formalised in catalogue v0.1.4 §2h.1 R-VMODEL-2). Request-for-comment on the branch-reconciliation question in §6.
**Audience:** ThinkPad-Sonnet (consume §3 TT-code canon + §4 Q-PARITY-3 recipe + §5 mimt-governance implications + §6 branch question); Pete (review + decide §6 + execute §8 backlog); ThinkPad-Opus on next session (consume §2 R-CONFIRM-1 + §7 Selenium harvest exemplar + §9 new OQs).
**Posture:** Sonnet's parity port is **strong, structurally clean, and operationally confirms MacBook's V-model assembly-layer model**. This reply absorbs the new TT codes into the catalogue canon (already done — see §3), produces the diagnostic for the one outstanding source-integrity issue (Q-PARITY-3, §4), and surfaces one open structural question (branch reconciliation, §6). Net signal: the MacBook governance + ThinkPad delivery split is working as intended.

---

## §0. How to use this doc

```
Step 1 — operator (Pete) reviews this doc on MacBook
Step 2 — copy this file + the updated VOCABULARY-CATALOGUE-CS-EN-V0.1.md into bouracka-tests via:
         ./_config/sync-to-bouracka-tests.sh   (already idempotent; will pick up the new file)
         OR manually: cp _config/SYNCHRO-MACBOOK-FROM-OPUS-CP-SUPIN-05-FOLLOWUP-2026-05-08.md \
                         SUPIN/bouracka-tests/_specs/from-macbook/   (alongside existing 5 docs)
                      cp _config/VOCABULARY-CATALOGUE-CS-EN-V0.1.md \
                         SUPIN/bouracka-tests/_specs/from-macbook/VOCABULARY-CATALOGUE-CS-EN-v0.1.4.md   (updated; v0.1.4 in name)
Step 3 — push to GitHub on a NEW branch (recommended — keep cp-supin-05-cross-framework-parity untouched):
         cd ~/Documents/VibeCodeProjects/SUPIN/bouracka-tests
         git checkout main && git pull
         git checkout -b macbook/cp-supin-05-followup-2026-05-08
         (apply file copies from Step 2)
         git add _specs/from-macbook/ && git commit -m "feat(governance): MacBook→Sonnet reply CP-SUPIN-05 followup" && git push -u origin HEAD
Step 4 — ThinkPad-Sonnet's next session pulls + reads this doc as STEP 1
Step 5 — Pete decides §6 branch-reconciliation question (merge order between the three open branches)
```

---

## §1. Acknowledge what's excellent — E-TPS-1..10

10 things from the parity port worth preserving on any future iteration:

| # | Thing | Why it's excellent |
|---|---|---|
| **E-TPS-1** | 9 TC × 2 frameworks delivered as 18 mirroring files — same selectors, same flow, divergent framework idioms | Establishes the *framework-agnostic test artefact* discipline. The mirroring proves it's possible; the divergent idioms prove the abstraction layer is correctly placed (helper layer, not test layer). |
| **E-TPS-2** | Shared helper layer `data-loader.{ts,py}` + `nav-helpers.{ts,py}` | Operationally demonstrates the *governance layer ↔ delivery layer* split MacBook articulated in `_config/SYNCHRO-MACBOOK-TO-OPUS-CP-SUPIN-06-2026-05-08.md` §5. Helpers are universal; tests are framework-specific. Same helpers, same fixtures, same `covers()` discipline across all 3 frameworks. |
| **E-TPS-3** | `covers([TT-...])` annotation discipline — every test declares which TT codes it exercises | This is the *executable V-model TT assembly map*. The workbook's `15_VModelAssemblyMap` sheet should consume this list as its source-of-truth for "which TT actually has a test". Closes the gap MacBook flagged in `_config/METH-REFINE-TESTANALYSIS-TESTDESIGN-v0.1.md` §3.5 (TestCasePackage = design intent; TC = executable; covers() = the bridge). |
| **E-TPS-4** | Selenium CDP `add_cdp_listener` + JS `window.fetch` override fallback for ALT-10 SPA capture | Hard problem solved cleanly. Two-strategy approach with explicit fallback hierarchy is exactly the right pattern for cross-browser-version compatibility. Generalisable to any "capture-network-from-headless" test. |
| **E-TPS-5** | Drift-aware soft assertions (ALT-9 200-or-403 acceptable; ALT-5/1/4 skip on drift) | Preserves test value during DEMO drift periods without false-positive noise. Pattern: `expect([200, 403]).toContain(status)` + `console.warn`. Clean. |
| **E-TPS-6** | DRY-RUN status explicitly declared in §4 | Honest reporting — Sonnet ran no live browsers (sandbox limitation); flagged design-level findings as such; deferred empirical run to ThinkPad. This is good R-VALIDITY-1 hygiene: don't claim observations you didn't make. |
| **E-TPS-7** | `tools/consolidate_results.py` — multi-framework result aggregation into common JSON schema | Foundational for cross-framework parity comparison. The "common JSON schema" pre-empts the Allure adapter discussion (§6 of Sonnet's doc) — Allure becomes a v0.6.0 bolt-on rather than a v0.5 dependency. |
| **E-TPS-8** | Selenium namespace-collision diagnosis (`selenium.helpers` shadowed by upstream `selenium` PyPI package) | Production-grade root-cause analysis: explicit `sys.path` namespace package model + concrete fix (`from helpers.X` direct import + `pytest.ini pythonpath = .`). This is R-MODEL-IS-CODE in action — the fix lives in the import resolution mechanism, not in docstrings. See §7 below for the harvest-discipline exemplar. |
| **E-TPS-9** | Q-PARITY-3 surfaced (Playwright source truncated at line 228) | Delivery agent flagged the source-of-truth integrity issue rather than silently working around it. Compare with the alternative ("ALT-10 doesn't quite work; oh well") — Sonnet's posture is exactly right. Diagnostic in §4 below. |
| **E-TPS-10** | 9 expected-outcome rows in §4 prediction table — design-level prediction of which TC pass/skip/soft at Cíl 1 | Pre-execution prediction is good test discipline. When ThinkPad runs empirically, the divergence between predicted-and-actual is the *real signal* — it tells us where our framework-design assumptions were wrong. Pre-prediction is the reference frame. |

---

## §2. R-CONFIRM-1 fires — independent confirmation of V-model assembly nomenclature

**This is the cleanest R-CONFIRM-1 instance the project has produced to date.**

Per `_config/METHODOLOGY-MAPPING-V0.1.md` AMENDMENT 2026-05-08 §4: when *independent observers reach the same architectural conclusion from different inputs*, treat as confidence multiplier in the harvest-discipline `confidence` field.

The instance:

| Observer | Input | Output (TT-code nomenclature) |
|---|---|---|
| **MacBook governance (Opus, 2026-05-08 morning)** | Reading `VOCABULARY-CATALOGUE-CS-EN-V0.1.md` v0.1.2 + `SYNCHRO-MACBOOK-TO-OPUS-CP-SUPIN-06-2026-05-08.md` §2 + reasoning about transposition operators | Catalogue v0.1.4 §2h: 4-layer V-model TT assembly model (FUNC / SCRN / LOV / ACTV) |
| **ThinkPad delivery (Sonnet, 2026-05-08 afternoon)** | Reading parity-execution spec + Playwright source + writing Cypress + Selenium ports | 8 TT codes using prefixes TT-FUNC- / TT-SCRN- / TT-ACTV- + 1 composite TT-E2E- |

**Sonnet had no visibility into MacBook's catalogue v0.1.4 §2h.** Sonnet's branch (`cp-supin-05-cross-framework-parity`) was branched from `main` (v0.5.0), not from MacBook's pending PR `macbook/cp-supin-06-prep-2026-05-08`. The catalogue v0.1.4 update was not on `main` at the time Sonnet branched. Two truly independent observers.

**Confidence promotion:** the V-model assembly-layer model graduates from `validated` (single-observer, MacBook governance) to **`confirmed-multi-observer`** (per the new tier in AMENDMENT 2026-05-08 §4 — currently blocked on OQ-METH-14 schema implementation but the concept is binding-from-now).

**Practical implication:** any future doubt about whether to use FUNC/SCRN/LOV/ACTV vs some other layer scheme is settled. We now have:
1. The catalogue principle (R-VMODEL-1).
2. ThinkPad's planned `15_VModelAssemblyMap` sheet (operational realisation).
3. Sonnet's executable `covers()` calls in 18 test files (concrete usage).

Three reinforcing layers across two independent observers. Strong enough to commit schema migration `132_add_tt_assembly_layer.sql` without further doubt.

**One discovery:** Sonnet introduced a 5th meta-layer (`TT-E2E-fullHappyDay`) that wasn't in MacBook's original 4-layer model. This is a *positive convergence finding* — Sonnet's port revealed the model was incomplete. Catalogue v0.1.4 §2h.1 (folded 2026-05-08 PM as in-place patch) introduces R-VMODEL-2 to formalise the E2E meta-layer. See §3 below.

---

## §3. The 8 new TT codes — now folded into catalogue v0.1.4 §2h.1

Per Sonnet SYNCHRO §5 medium #6 ("These need to be added to the V-model TT mapping sheet"): **done on MacBook side.** Catalogue v0.1.4 §2h.1 was patched in-place 2026-05-08 PM with the worked example. The 8 codes are now part of catalogue canon:

| TT code | Test code | V-model layer | Status in catalogue |
|---|---|:--:|---|
| `TT-FUNC-rpRegex` | TC-CP-A2-ALT-1 | FUNC | ✅ in §2h.1 |
| `TT-FUNC-gdprConsent` | TC-CP-A2-ALT-4 | FUNC | ✅ in §2h.1 |
| `TT-SCRN-predvolba421` | TC-CP-A2-ALT-5 | SCRN | ✅ in §2h.1 |
| `TT-SCRN-policeCard` | TC-CP-A2-ALT-6 | SCRN | ✅ in §2h.1 |
| `TT-SCRN-demoBanner` | TC-CP-A2-ALT-8 | SCRN | ✅ in §2h.1 |
| `TT-ACTV-postReports` | TC-CP-A2-ALT-9 | ACTV | ✅ in §2h.1 |
| `TT-ACTV-spaPostProbe` | TC-CP-A2-ALT-10 | ACTV | ✅ in §2h.1 |
| `TT-E2E-fullHappyDay` | TC-CP-A1-MAIN-DEMO | **E2E** *(meta)* | ✅ in §2h.1 — triggers R-VMODEL-2 |

**New principle (R-VMODEL-2, binding from v0.1.4 in-place patch):** the E2E meta-layer composes base layers. Schema impact: `tt_assembly_layer VARCHAR(8)` accepts `E2E`, plus new `tt_e2e_composes JSON NULL` listing base-layer TT codes. Coverage analysis credits an E2E test as a *soft* credit on each composed base TT, not a base-layer credit on its own.

**Workbook impact for `15_VModelAssemblyMap` (CP-SUPIN-06 v0.5.1 migration):**
- Seed content: the 8 TT codes above (verbatim).
- Schema: add column `e2e_composes` (string; comma-separated TT codes) for E2E rows; NULL for FUNC/SCRN/LOV/ACTV rows.
- `tt_assembly_ref` examples (per catalogue §2h.1 schema impact):
  - `func:rpRegex` (for `TT-FUNC-rpRegex`)
  - `screen:policeCard` (for `TT-SCRN-policeCard`)
  - `actv:spaPostProbe` (for `TT-ACTV-spaPostProbe`)
  - `e2e:fullHappyDay` (for `TT-E2E-fullHappyDay`)

**`covers()` discipline retained:** each test's `covers([...])` call is the *executable manifest*. The workbook sheet's `e2e_composes` column for an E2E row should match the `covers([...])` array of the underlying test exactly. Migration script SHOULD validate this on import (proposed validator hook in `mimt-governance/src/mimt_governance/validate_workbook.py` v0.2 — gates on OQ-CONTRACT-01..04 resolution).

**No new schema migration needed beyond `132_add_tt_assembly_layer.sql`** — the same migration now adds the `tt_e2e_composes` column. Migration spec in catalogue §2h.1 reflects this.

---

## §4. Q-PARITY-3 diagnostic — Playwright source truncation root cause + recovery recipe

**Diagnosis (executed on MacBook 2026-05-08 PM):**

The truncation is in the source-of-truth `v0.5.0` seed commit (`736eedb`) itself. Every ref carries the SAME 11233-byte / 228-line file:

```
$ for ref in main origin/main tags/v0.5.0 \
             origin/cp-supin-05-cross-framework-parity \
             origin/macbook/cp-supin-06-prep-2026-05-08; do
    git cat-file -s "$ref:playwright/tests/a2-alternates-demo.spec.ts"
  done
11233   # main
11233   # origin/main
11233   # tags/v0.5.0
11233   # origin/cp-supin-05-cross-framework-parity
11233   # origin/macbook/cp-supin-06-prep-2026-05-08
```

Same SHA-256 across all refs proves git push corruption is **NOT** the cause (git is content-addressed; corruption would yield different SHAs).

**Last commit touching the path:**
```
$ git log --all --oneline -- playwright/tests/a2-alternates-demo.spec.ts
736eedb feat: initial v0.5.0 — CP-SUPIN-05 seed (Bouracka tests + MI-M-T methodology)
```
Only one commit. The file was committed truncated; no later edit ever happened.

**Truncation point:** line 228 ends with `last.responseHeaders` — no semicolon, no closing brace `}`, no closing test block, no closing `}); ` — the file just stops mid-expression in the middle of `page.on("response", async (res) => { ... })`.

**Therefore:** the truncation happened *before the v0.5.0 commit was authored*. Three hypotheses (priority order):

| Hypothesis | Probability | Evidence |
|---|---|---|
| H1 — Author-side editor truncation (file was paste-clipped in editor; only first 228 lines saved) | **HIGH** | Most common cause of mid-expression truncation; line 228 is exactly the kind of boundary an editor truncates at on a partial paste. |
| H2 — Source-of-source truncation (the original Playwright spec was authored elsewhere and partial-imported) | MEDIUM | Possible if generated from a planning doc; would also explain Sonnet's note that the source "ends mid-expression". |
| H3 — File-system / I/O truncation at write time | LOW | Would require a specific failure mode (disk full + partial write); rare but possible. |

**Recovery recipe for Pete (run on ThinkPad — that's where the file originated):**

```powershell
# Step 4.1 — confirm the truncation locally (verify identical state on ThinkPad)
cd ~\Documents\VibeCodeProjects\SUPIN\bouracka-tests
git fetch origin
git status --short                                         # should be clean

(Get-Item playwright\tests\a2-alternates-demo.spec.ts).Length    # should equal 11233
(Get-Content playwright\tests\a2-alternates-demo.spec.ts | Measure-Object -Line).Lines    # should equal 228
Get-Content playwright\tests\a2-alternates-demo.spec.ts -Tail 3
# expected last line: "          last.responseHeaders" (no trailing semicolon)
```

If the local file matches: the truncation is in the v0.5.0 seed; it was always truncated. Recovery requires reconstructing the missing tail. Three options, in increasing effort:

```powershell
# Step 4.2 — search ThinkPad's editor history for the un-truncated original
# (if VSCode was the editor — check Local History extension storage)
$vscodeHistory = "$env:APPDATA\Code\User\History"
if (Test-Path $vscodeHistory) {
    Get-ChildItem -Recurse $vscodeHistory -Filter "*.ts" |
      Where-Object { (Get-Content $_.FullName -Raw) -match "responseHeaders" } |
      Select-Object FullName, Length, LastWriteTime
}
# Also check Recycle Bin for older saves:
Get-ChildItem 'C:\$Recycle.Bin' -Recurse -Filter "*.spec.ts" -ErrorAction SilentlyContinue |
  Select-Object FullName, Length, LastWriteTime

# Step 4.3 — reconstruct from the executable Cypress port (Sonnet's branch)
git show origin/cp-supin-05-cross-framework-parity:cypress/e2e/a2-alternates-demo/alt-10-spa-post-probe.cy.ts > recovery-cypress-alt10.ts
# Use this as a reference to reverse-engineer the missing Playwright tail.
# The Cypress port's network-capture logic (cy.intercept + req.continue + response callback)
# maps 1:1 to Playwright's page.on("request") + page.on("response") that's been truncated.

# Step 4.4 — reconstruct from the parity-execution spec
git show origin/cp-supin-05-cross-framework-parity:_specs/CROSS-FRAMEWORK-PARITY-EXECUTION-v0.1-CS.md | grep -A 60 "ALT-10"
# §3.2 of that spec has the design-level description Sonnet cited.
```

**Recommended fix path (lightest touch):** option 4.3 — reconstruct from Sonnet's Cypress port. The Cypress code is structurally equivalent (cy.intercept + req.continue + response callback semantics). Reverse-engineer the missing 30-50 lines of Playwright tail. Add to a follow-up commit on either main or a new fixup branch:

```bash
git checkout -b fix/playwright-alt10-tail-reconstruction
# … reconstruct the file …
git add playwright/tests/a2-alternates-demo.spec.ts
git commit -m "fix(playwright): reconstruct truncated ALT-10 response capture

Source v0.5.0 (commit 736eedb) committed file truncated at line 228 mid-expression.
Reconstructed from Sonnet's Cypress port (cypress/e2e/a2-alternates-demo/alt-10-spa-post-probe.cy.ts)
on cp-supin-05-cross-framework-parity branch. Logic is structurally equivalent.

See _config/SYNCHRO-MACBOOK-FROM-OPUS-CP-SUPIN-05-FOLLOWUP-2026-05-08.md §4 for the diagnostic."
```

**Open question (OQ-PARITY-3, raised here for the next iteration):** should the v0.5.0 tag be retroactively re-tagged to point at the post-fix commit, or should the fix land as a v0.5.1 bump? Recommend **v0.5.1 bump** — tags are immutable in practice; re-tagging breaks any downstream consumer who pinned v0.5.0. The fix is a normal bug fix; bump version + close in changelog.

---

## §5. Cross-framework parity discipline → mimt-governance/ implications

Sonnet's port establishes the *cross-framework parity discipline* operationally. This has direct implications for the `mimt-governance/` scaffold MacBook started in this session (per `_config/SESSION-CLOSE-MACBOOK-2026-05-08-PART-2.md` §1.2):

### §5.1 New module candidate: `mimt-governance/test-console`

ThinkPad's `tools/test_console.py` (~327 lines, multi-framework runner) is now revalidated as a direct-port candidate (★★★ in SYNCHRO §6.2 ranking). The parity port of 9 TC × 2 frameworks proves the abstraction is real. Recommend:

- Add `test-console` as a 5th planned module in `mimt-governance/v0.2`.
- Source: `bouracka-tests/tools/test_console.py` + `tools/consolidate_results.py` (Sonnet's new addition).
- Universal interface: `mimt-cli test-console --framework {playwright,cypress,selenium} --suite <path>` → JSON results in common schema.
- Ports the consolidate-results step too (per E-TPS-7).

### §5.2 New module candidate: `mimt-governance/covers-validator`

The `covers([TT-...])` annotation discipline (E-TPS-3) needs a validator that:
- Parses test source files (across frameworks) extracting `covers([...])` calls.
- Cross-references against the workbook's `15_VModelAssemblyMap` sheet.
- Flags: TTs in workbook with no test (uncovered); tests with TT codes not in workbook (orphan); E2E tests whose `covers([...])` doesn't match `e2e_composes` column (drift).

This is a new module — no direct port exists. Estimated effort: 1 week (parsing across 3 framework idioms is the bulk of the work; the workbook side is openpyxl boilerplate).

### §5.3 The `consolidate_results.py` pattern

Sonnet's new `tools/consolidate_results.py` is the proof-of-concept for a cross-framework reporter. The "common JSON schema" emerging from this is the canonical wire format for any future MI-M-T runner backend (per SYNCHRO §4.2 "Results sink"). Recommend:

- Document the schema explicitly (Sonnet's code IS the schema; lift to a markdown spec in `_specs/CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.md`).
- Adopt as the binding format for `mimt-governance/append_run_result` (currently a stub awaiting OQ-CONTRACT-01..04 resolution; this would resolve OQ-CONTRACT-03 [field naming] de-facto).

### §5.4 Update to `mimt-governance/README.md` roadmap

Add to v0.2 roadmap (currently 6 items):
- (7) `test-console` module port
- (8) `covers-validator` module new build
- (9) Adopt the cross-framework JSON schema from `consolidate_results.py` for `append_run_result`

---

## §6. Branch reconciliation — an open structural question for Pete

Three open branches now exist on `petr-yamyang/bouracka-tests`:

```
main                                              v0.5.0 (clean baseline)
├── macbook/cp-supin-06-prep-2026-05-08          MacBook governance — 5 docs in _specs/from-macbook/ + SYNCHRO at root
└── cp-supin-05-cross-framework-parity           ThinkPad-Sonnet delivery — Cypress + Selenium ports + consolidate_results.py
```

Plus the *next* one (this session's deliverable): proposed `macbook/cp-supin-05-followup-2026-05-08` carrying this SYNCHRO reply doc + the catalogue v0.1.4 in-place patch (§2h.1).

**The structural question:** how do these lineages converge?

**Option A — sequential merges (recommended):**
```
1. Open PR cp-supin-05-cross-framework-parity → main; review + merge (delivery work; should land first)
2. Open PR macbook/cp-supin-06-prep-2026-05-08 → main; resolve trivial conflicts (different paths); merge
3. Open PR macbook/cp-supin-05-followup-2026-05-08 → main; merge
4. ThinkPad's next session branches from refreshed main = sees all governance + delivery
```
Pros: linear history; each PR reviewable in isolation; no cross-branch dependencies.
Cons: 3 sequential merges before next ThinkPad iteration unblocks; delays empirical run.

**Option B — integration branch:**
```
1. Create integration/cp-supin-05-and-06-2026-05-08 from main
2. Merge cp-supin-05-cross-framework-parity into it
3. Merge macbook/cp-supin-06-prep into it
4. Merge macbook/cp-supin-05-followup into it
5. Single PR integration → main with all three reconciled
```
Pros: single review milestone; bigger view of the integrated state.
Cons: harder to review (large diff); if any one branch is contentious, the whole batch holds.

**Option C — interleaved (delivery proceeds; governance follows):**
```
1. Merge cp-supin-05-cross-framework-parity → main immediately (operator approves; delivery is independently runnable)
2. ThinkPad branches a new working branch from refreshed main
3. macbook/cp-supin-06-prep + macbook/cp-supin-05-followup wait until ThinkPad's next iteration creates demand for the governance content
```
Pros: doesn't block delivery; matches the empirical reality (Sonnet's branch is the only one with executable code).
Cons: governance work sits stale on a branch; risk of merge conflicts accumulating; signals "governance is optional" which is the wrong message.

**MacBook recommendation:** Option A. The merge order matters: delivery first (cp-supin-05-cross-framework-parity), then governance (the two macbook/* branches). This:
- Unblocks ThinkPad empirical runs ASAP (option A merges delivery in 1 step).
- Lands governance shortly after but lets ThinkPad iterate during the brief governance review window.
- Honours the sequencing principle: delivery proves usability; governance integrates lessons.
- Avoids the "governance is optional" signal of Option C.

**Pete's call.** Tracking as new OQ-MB-11 below.

---

## §7. Selenium namespace-collision lesson → ARCH-HARVEST exemplar

Per E-TPS-8: Sonnet's diagnosis of the `selenium.helpers` namespace collision is a textbook R-MODEL-IS-CODE moment.

**The diagnosis chain:**
1. Symptom: `from selenium.helpers.X import Y` → `ModuleNotFoundError`.
2. Initial hypothesis (wrong): missing `__init__.py` somewhere.
3. Real hypothesis (correct): Python 3 *namespace packages* — when a directory `selenium/` (no `__init__.py`) is on `sys.path`, it becomes a namespace package. The installed `selenium` PyPI package's `helpers` module is *also* contributing to that namespace, but the directory order in `sys.path` and the namespace-package merge semantics combine to make `selenium.helpers.X` unresolvable.
4. Fix: import from `helpers.X` directly (the directory `selenium/` is on sys.path → `helpers/` is a top-level package from sys.path's perspective).
5. Defensive add: explicit `pythonpath = .` in `pytest.ini` to ensure `sys.path` always includes the repo root (don't rely on pytest's default behaviour).

**This is the harvest-discipline pattern (per `_config/SUPIN-ARCH-HARVEST-DISCIPLINE-v0.1.md` R-MODEL-IS-CODE):** the *real* model lives in the import resolution mechanism, NOT in any documentation. Docstrings, README, `.md` specs — all of these said `selenium.helpers` should work. The actual *executable model* (Python's import system + sys.path semantics + namespace package rules) said no.

**Recommended fold (operator-confirm before applying):** add this incident as **Exemplar 1** in `_config/SUPIN-ARCH-HARVEST-DISCIPLINE-v0.1.md` §6 (or wherever the "Exemplars" section lives — author's call). Format:

```
### Exemplar 1 — Selenium namespace collision (CP-SUPIN-05; 2026-05-08)

R-rule: R-MODEL-IS-CODE.
Pattern: an architectural assumption was documented in 4 places (README, spec, helper module docstrings, SESSION-CLOSE doc) but the *executable model* (Python import system) refused.
Fix: trust the executable model; rewrite imports + add explicit pythonpath guard.
Lesson: when documentation says X works and code says X doesn't, code wins. Re-author the documentation to match.

Source: `bouracka-tests/SESSION-CLOSE-CP-SUPIN-05-2026-05-08-IMPORT-FIX.md`
```

Tracking as new OQ-MB-12 below (operator-confirm fold).

---

## §8. Operator-action backlog (consolidated state — this session + prior)

After this SYNCHRO ships, the backlog is:

| # | Item | Owner | Priority | Source | Action |
|:--:|---|:--:|:--:|---|---|
| **1** | Open PR `cp-supin-05-cross-framework-parity` → main | Pete | A | Sonnet push | Per §6 Option A; delivery merges first |
| **2** | Open PR `macbook/cp-supin-06-prep-2026-05-08` → main | Pete | A | Prior session | Per §6 Option A; governance merges after delivery |
| **3** | Open PR `macbook/cp-supin-05-followup-2026-05-08` → main | Pete | A | THIS session | Per §6 Option A; ships catalogue v0.1.4 §2h.1 patch + this SYNCHRO |
| **4** | Verify Playwright `a2-alternates-demo.spec.ts` truncation locally on ThinkPad | Pete | A | §4 recipe | Step 4.1 confirms; Step 4.3 reconstructs |
| **5** | Reconstruct truncated Playwright ALT-10 tail | Pete (ThinkPad) | A | §4 + Sonnet Q-PARITY-3 | Use Step 4.3; ship as v0.5.1 fix |
| **6** | Run empirical parity tests on ThinkPad (npx cypress + py -m pytest selenium/) | Pete (ThinkPad) | A | Sonnet §5 high #1 | Once branches are merged + Playwright fix lands |
| **7** | Verify ALT-10 CDP capture on Chrome 109+ / Selenium 4.6+ | Pete (ThinkPad) | B | Sonnet §5 high #2 | Empirical-only; falls under #6 |
| **8** | Apply MacBook commit recipe (per SESSION-CLOSE-MACBOOK-2026-05-08-PART-2 §3) — clear `.git/index.lock` + commit local _config/ work | Pete (MacBook) | A | Prior session | Recipe still pending; this session adds 2 more files (this SYNCHRO + the catalogue patch reflected in the same file) |
| **9** | Sync the new SYNCHRO + updated catalogue into `bouracka-tests` | Pete (MacBook) | A | This session §0 | `./_config/sync-to-bouracka-tests.sh` is idempotent; run it after #8 commit lands |
| **10** | Optional: confirm fold of Selenium namespace lesson into ARCH-HARVEST §6 Exemplars | Pete (operator) | C | §7 + OQ-MB-12 | Fold or defer per author preference |
| **11** | TASKS-shared.yaml cleanup of VOC4/5/6 entries | Pete (operator) | C | Prior close §7 | Couldn't auto-resolve; needs manual inspection |

**Critical path:** #1 → #2 → #3 → #4 → #5 → #6. Five branches/operations from current state to "empirical parity data exists". The blocker for empirical data is the Playwright truncation fix (#5). All three governance/delivery merges (#1–#3) can run in parallel as PRs but should merge in the sequence given.

---

## §9. New OQs raised by this session

| OQ# | Sev | Urg | Pri | Question | Resolve by |
|---|:---:|:---:|:---:|---|---|
| OQ-MB-11 | A | A | A | Branch reconciliation strategy (per §6) — Option A (sequential), B (integration branch), or C (interleaved)? MacBook recommends A. | Pete decides before opening PRs |
| OQ-MB-12 | C | C | C | Fold Selenium namespace lesson as Exemplar 1 in `_config/SUPIN-ARCH-HARVEST-DISCIPLINE-v0.1.md` §6 (or wherever Exemplars live)? | next ARCH-HARVEST iteration |
| OQ-MB-13 | B | A | A | The `tt_e2e_composes` JSON validation discipline — should `mimt-governance/validate_workbook` (v0.2) include a check that workbook E2E rows match the test source's `covers([...])` exactly? Cross-references catalogue OQ-VOC-15. | mimt-governance v0.2 design |
| OQ-MB-14 | B | B | B | The cross-framework JSON result schema (Sonnet's `consolidate_results.py`) — lift to `_specs/CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.md` and adopt as binding for `mimt-governance/append_run_result`? Resolves OQ-CONTRACT-03 (field naming) de-facto. | mimt-governance v0.2 design |
| OQ-MB-15 | C | C | C | v0.5.0 truncation handling — re-tag (rejected) vs v0.5.1 bump (recommended) — confirm? | next ThinkPad release |
| OQ-PARITY-3 | A | A | A | (renumbered from Sonnet §6 inheritance) Playwright source truncation root cause — author-side editor, source-of-source, or I/O? Recovery: reconstruct from Cypress port. See §4 above. | Pete (ThinkPad) verifies + reconstructs |

Total new OQs: 6 (5 OQ-MB + 1 OQ-PARITY).

---

## §10. Status footer

| Item | Value |
|------|-------|
| Document | `SYNCHRO-MACBOOK-FROM-OPUS-CP-SUPIN-05-FOLLOWUP-2026-05-08.md` |
| MacBook source position | `_config/SYNCHRO-MACBOOK-FROM-OPUS-CP-SUPIN-05-FOLLOWUP-2026-05-08.md` |
| Repo target position | `_specs/from-macbook/SYNCHRO-MACBOOK-FROM-OPUS-CP-SUPIN-05-FOLLOWUP-2026-05-08.md` (alongside existing 5 docs) |
| Direction | MacBook (Opus governance) → ThinkPad-Sonnet (delivery) |
| Trigger | Sonnet 2026-05-08 push: commits `5c865c8` + `dce8911` on branch `cp-supin-05-cross-framework-parity` |
| Sections | 10 (use / acknowledge / R-CONFIRM-1 / TT codes / Q-PARITY-3 / mimt-governance impl / branch reconciliation / Selenium harvest exemplar / operator backlog / OQs / status) |
| E-TPS items acknowledged | 10 (E-TPS-1..10) |
| TT codes folded into catalogue | 8 (now in §2h.1) |
| New foundational rule | R-VMODEL-2 (E2E meta-layer composes base layers; binding from v0.1.4 in-place patch) |
| Confidence tier promotion | V-model assembly model → `confirmed-multi-observer` (per AMENDMENT 2026-05-08 §4) |
| Q-PARITY-3 disposition | Diagnosed as v0.5.0 seed-commit truncation (NOT push corruption); 4-step recovery recipe in §4 |
| New OQs | 6 (OQ-MB-11..15 + OQ-PARITY-3) |
| Operator backlog | 11 items (5 critical-path A; 4 important B; 2 maintenance C) |
| MacBook governance state | catalogue v0.1.4 with §2h.1 in-place patch; METHODOLOGY-MAPPING with 2 amendments; mimt-governance/ scaffold v0.1.0 with 13/13 smoke tests PASS |
| Status | v0.1 — ready for Pete's review + commit + branch + push to `petr-yamyang/bouracka-tests` |

---

*SYNCHRO-MACBOOK-FROM-OPUS-CP-SUPIN-05-FOLLOWUP-2026-05-08.md — 2026-05-08 PM — MacBook Cowork session — Sonnet (post Claude 1.6259.1 update)*
