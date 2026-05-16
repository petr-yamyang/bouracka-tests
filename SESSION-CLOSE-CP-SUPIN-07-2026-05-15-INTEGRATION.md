# Session close — CP-SUPIN-07 · v0.1.5 integration + Kate ship (2026-05-15)

**Operator:** Pete Y. + Claude Opus 4.7
**Branch:** `v0.1.5-integration`
**Final HEAD:** `499b00e` (post-cleanup, post-reship)
**Integration tag:** `v0.1.5-integration-2026-05-15` (proposed move from `54b802c` → `499b00e`)
**Test status at close:** 60 passed, 1 deselected (`http_e2e` family-B, by design). Multiple identical pytest runs across the session — consistently 60/60.
**Shipped to Kate:** `delivery/KATE-DROP-2026-05-15.zip` (24.22 MB, SHA256 `a7774cad99a55d10736dc1aa09a461e1a26f25fcdd4e1702472bbeab3901850c`)

---

## §1 — What landed

Seven overnight Sonnet briefs merged into `v0.1.5-integration` plus five follow-up commits (docs, cleanup, retroactive UI work, ship provenance, refresh after WT-truth swap).

### M1–M7 integration chain (original goal)

| Brief | Branch | Merge commit | Headline |
|---|---|---|---|
| #004 | `cp-supin-13-hotfix-bundle` | `bbd27e5` | Dispatcher BUG-K-009/010/012 hotfix bundle |
| #005 | `cp-supin-11-mock-dispatch-e2e` | `01bd0c5` | 13-test mock-dispatch e2e shield |
| #002 | `cp-supin-17-workbook-io-readers` | `2233a27` | workbook_io readers + 4 endpoints + `SUPPLEMENTAL_ENVS` |
| #006 | `cp-supin-14-int-probe-expansion` | `283ff63` | int_recon.py → 11 targets / 7 probe types |
| #007 | `cp-supin-15-cross-check-report` | `95279bc` | `/api/runs/{rid}/cross-check[.html]` + 11-test suite |
| #001 | `cp-supin-07-v0.1.5-patcher` | `42e6edd` | Workbook patcher v0.4.3→v0.4.4 |
| #001b | `cp-supin-09-v0.4.4-data-migration` | `90ff756` | Patcher `--source-data` row migration |

### Documentation & cleanup commits (this session)

| Commit | Headline |
|---|---|
| `c5523d4` | chore(.gitignore) — cypress/screenshots Windows MAX_PATH unblock (between M5 and M6) |
| `54b802c` | docs — v0.1.5 integration release notes + comprehensive-release-notes rule |
| `decf298` | docs(delivery) — Kate v0.1.5.dev5 ship provenance (delta CS + SHA256) |
| `b206a6b` | feat(ui+cli) — **retroactive** v0.1.3 Block 1+2 UI + v0.1.4 BUG-K-003 CLI fix |
| `44966b4` | chore — uncommitted tweaks (cypress demo env, consolidate_results, env config, READMEs) |
| `b4f083d` | docs(delivery) — HP-Elite v0.1.0 drop doc updates (CS+EN, 8 files) + gitignore drop artefacts |
| `b373a8d` | chore(delivery) — prune obsolete artefacts (v0.4.2 workbook, EMAIL/EXCEL/PRIORITY notes, v0.1.0 packager) |
| `499b00e` | docs(delivery) — refresh Kate ship manifest (re-built wheel after WT-truth swap) |

---

## §2 — What shipped to Kate

`delivery/KATE-DROP-2026-05-15.zip` — 24.22 MB total, containing:

| Inner artefact | Size | SHA256 (first 16) |
|---|---|---|
| `bouracka-ui-hp-elite-v0.1.5.dev5-EN-multi-abi.zip` | 11.9 MB | `0ae5647f9be05742…` |
| `bouracka-ui-hp-elite-v0.1.5.dev5-CS-multi-abi.zip` | 11.9 MB | `7af1856b930fd777…` |
| `bouracka-tests-source-v0.5.7.zip` | 1.5 MB | `3993c6e6dc9ba5e0…` |
| `BOURACKA-TESTPLAN-v0.4.4.xlsx` | 100 KB | `0d5b57c12a22a5a8…` |
| `KATE-FROM-ZERO-INSTALL-CS.md` | 13 KB | `83a798fa70473009…` |
| `KATE-V0.1.5-DELTA-CS.md` *(NEW — operator delta for v0.1.4 → v0.1.5.dev5)* | 9 KB | `127d0c238bd59aa3…` |

Two ship cycles ran this session:
1. **First ship** (mid-session): SHA `D77EB64C…09129`. Built before the WT-truth cleanup — wheel source was an unknown mix of HEAD's M3–M7 work and uncommitted v0.1.3/v0.1.4 UI work.
2. **Final ship** (post-cleanup): SHA `a7774cad…1850c`. Built after HEAD captured the full source — wheel is reproducible from `HEAD` alone.

If the first SHA was mailed anywhere, supersede with the second.

---

## §3 — Mid-session discoveries

### 3.1 v0.1.3/v0.1.4 work was never committed (retroactive find)

The CHANGELOG documented v0.1.3 Block 1 (TES presentation enrichment, F-01..F-06) + Block 2 (bug edit/retest form) + v0.1.4 BUG-K-003 (CLI workbook visibility) as shipped. The actual file commits for these never landed on this branch. Found only in the working tree (485-line addition in `app.js`, 51 in `index.html`, 36 in `cli.py`) during the post-ship cleanup pass. Committed retroactively as `b206a6b`.

**Implication:** every prior wheel build of v0.1.3/v0.1.4 either included these features only because the building host had them in the WT, or shipped without them. Reproducibility from git history alone was not given for those versions until this session.

### 3.2 Windows-git merge writer occasionally truncates files mid-string

Hit twice during the session:
- After M2 amend: `pyproject.toml`, `__init__.py`, `test_smoke.py`, `CHANGELOG.md` — truncated mid-string from a prior notepad save.
- After M5 merge: `dispatcher.py` (431→413 lines) and `test_smoke.py` (520→506 lines) — truncated by git's merge writer in non-conflicting regions of the file.

Detection: bash-side `wc -l` against branch-tip blob after each merge; reconstruction from clean blobs.

**Mitigation already encoded:** §6.3 of `RELEASE-NOTES-v0.1.5-INTEGRATION-2026-05-15-EN.md` documents the pattern + reproduction recipe.

### 3.3 `.git/*.lock` files held by Windows

Bash (Linux sandbox over the mount) could not unlink lockfiles created by Windows-side git operations. Every git write op from PowerShell needed:
```powershell
Get-ChildItem .git -Recurse -Filter *.lock | Remove-Item -Force
```
as a defensive prelude.

### 3.4 PowerShell argument parsing quirks

- `git reset --keep HEAD@{1}` — fails because `@{...}` is hashtable syntax. Use `'HEAD@{1}'` quoted or the raw SHA.
- `Get-Content | Measure-Object -Line` undercounts line counts by 15–20% on these files. Bash `wc -l` is authoritative.

### 3.5 Brief #006 + Brief #007 authors skipped CHANGELOG

Brief #006 had no CHANGELOG entry at all. Brief #007 had a partial entry (Scope IN only). Both enhanced per the new comprehensive-release-notes rule.

---

## §4 — New operating rule established

`_config/RELEASE-NOTES-RULE-v0.1-EN.md` (committed as part of `54b802c`):

> Every release/integration deliverable must include the five sections:
> §2.1 Scope IN · §2.2 Scope OUT / Deferred · §2.3 Regression candidates · §2.4 Cross-brief dependencies · §2.5 Known issues at ship.

Applied retroactively to Briefs #001, #001b, #005, #006, #007 in CHANGELOG. Inherited going forward by all Sonnet briefs and integration tags.

---

## §5 — Tag state at close

```
v0.1.5-dev5-integration      -> bbd27e5  (M1 only — historical marker)
v0.1.5-integration-2026-05-15 -> 499b00e  (proposed move from 54b802c — captures the post-cleanup, reshipped final state)
```

The misleading `v0.1.5-dev6-integration` tag (which had been pointing at M2-only `01bd0c5`) was deleted earlier in the session. No new dev6/dev7/dev8/dev9 tags created — those names appear only in CHANGELOG milestone slots, by merge order, not as git refs.

---

## §6 — Parked / open

### 6.1 Untracked items still in WT (intentionally parked)

~40 untracked items remain in the working tree, including:
- `_config/` — Sonnet brief design docs (SONNET-BRIEF-001..009, SONNET-OVERNIGHT-SUMMARY, OVERNIGHT-SONNET-DISPATCH, BOURACKA-UI-V0.1.5-DESIGN-NOTES). These are this session's source-of-truth design docs; committing them is a separate task.
- `_db/discovery/` — Oracle ERD discovery scripts (10 SQL files + master runbook). Separate Brief.
- `_install/contracts/sedn-d{5,8}ws-test-data-request.md` — INT-010/011 contracts.
- `_specs/SONNET-HANDOFF-PROMPT-CROSS-FRAMEWORK-PARITY-v0.1.md`, `_specs/SUPIN-INTERNAL-companion/DIAGNOSTICS-PLAYBOOK-SUPIN-INTERNAL-2026-05-12-STARTER.md`, `_specs/TEST-TARGET-ATTRIBUTE-MODEL-v0.1.md`, `_specs/V-MODEL-TESTTARGET-DECOMPOSITION-v0.1.md`.
- `archive/BOURACKA-TESTPLAN-v0.4.2.xlsx` — moved from repo root.
- `bouracka_ui/bouracka_ui/dwh/` — Oracle Repository skeleton (forerunner of `OracleRepository` swap-in boundary per `BOURACKA-DATA-STORE-EVOLUTION-PLAN`).
- `delivery/KATE-DROP-2026-05-15/MANIFEST.txt` and the rest of that drop folder (some already committed).
- `delivery/PETE-HP-ELITE-DROP-2026-05-13/*` and `delivery/SUPIN-SERVER-DROP-2026-05-13/*` artefacts from prior drops.
- Several PowerShell scripts: `delivery/package-hp-elite-v0.1.5-multi-abi.ps1`, `delivery/package-test-suite-v0.5.7.ps1`, `delivery/RESTAGE-DROPS-MULTI-ABI.ps1`, `delivery/VERIFY-AND-SHIP-V0.1.4-MULTI-ABI.ps1`.
- `recon/integrations/INT-010-D8WS-SEDN-create.md`, `recon/integrations/INT-011-D5WS-SEDN-lookup.md`, `recon/integrations/examples/`.
- `runs/` (runtime artefacts — should be gitignored), `selenium-report/` (likewise), `tools/patcher-reports/`.
- Multiple top-level session-close docs from prior sessions (SESSION-CLOSE-CP-SUPIN-05/06).

**Recommendation for next session:** topic-group these into 4–6 chore commits before pushing. Especially worth tracking: `_config/` (the brief design docs — knowledge artefacts), the v0.1.5 packager scripts, and the SEDN INT-010/011 contracts.

### 6.2 Known regression in workbook_io tests (now non-blocking)

The original "regression-detection sentinel" — `test_envs_returns_envs` expecting 4 envs while the API only returns 3 — was resolved by M3 superseding the test (renamed `test_envs_returns_3_envs` with corrected expectations). Pre-existing concern about `SUPPLEMENTAL_ENVS` schema validation noted in CHANGELOG dev5 entry for Brief #002 follow-up.

### 6.3 Pre-existing test warnings (unchanged from session start)

2 × `PytestUnraisableExceptionWarning` in `test_post_run_rejects_empty_tcs` + `test_get_runs_unknown_id_404`. FastAPI TestClient asyncio teardown on Windows + Python 3.10. Cosmetic; cure is in upstream or test-fixture redesign. Documented in `RELEASE-NOTES-v0.1.5-INTEGRATION-2026-05-15-EN.md` §6.1.

---

## §7 — Handoff to next session (CP-SUPIN-08)

Recommended sequence for whoever picks up:

1. **`git pull origin v0.1.5-integration && git fetch --tags`** — pick up this session's work.
2. **Verify ship:** unpack `delivery/KATE-DROP-2026-05-15.zip` in a clean dir, `pip install` the CS wheel + wheelhouse, run smoke. Confirm `server_version: 0.1.5-dev5` from `/api/health`. **If you've already received feedback from Kate, this is the moment to compare.**
3. **Working-tree cleanup pass 2:** commit the parked items per §6.1 in 4–6 topic groups. `_config/` design docs go first (they're knowledge artefacts you'll want git-trackable for future grep).
4. **Brief #003 (TC discovery from workbook):** queued, no branch yet. Next major feature work.
5. **Brief #008 (release engineering):** turn `v0.1.5.dev5` into a proper `v0.1.5` (no dev suffix) by writing a v0.1.5 runbook, doing the ABI matrix re-verify on HP Elite, and tagging `v0.1.5`. Drops the "internal-dev only" caveat from Kate's deliveries.
6. **Add the 9 regression-candidate tests** listed in §7 of `RELEASE-NOTES-v0.1.5-INTEGRATION-2026-05-15-EN.md`.

### Files to read first

- `RELEASE-NOTES-v0.1.5-INTEGRATION-2026-05-15-EN.md` — master integration release notes
- `_config/RELEASE-NOTES-RULE-v0.1-EN.md` — operating rule for all future deliverables
- `CHANGELOG.md` top 9 entries — per-brief detail with Scope OUT, regression candidates, known issues
- `delivery/KATE-DROP-2026-05-15/KATE-V0.1.5-DELTA-CS.md` — what shipped to Kate and why

---

**Pete Y. · 2026-05-15 · session close**
