# Major dev session plan — v0.1.5 (hotfix folded in)

**Date.** 2026-05-14.
**Author.** Pete Y. + Opus 4.7.
**Status.** Strategic baseline. Replaces the v0.1.4.1 hotfix lane.
**Trigger.** Two days of rapid Kate ping-pong (BUG-K-001..K-013) revealed that small ship → bug → patch → re-ship cycle is **costing us more time than a single coherent push would**. Pause, build properly, ship once.

---

## §1. Strategic shift — why we stop the ping-pong

Last 48 hours: **10 bugs surfaced from Kate alone** (K-001 through K-013, with K-008/009/010/011/012/013 still open). Pattern: ship → Kate hits one thing → we hotfix → re-ship → Kate hits the next thing → repeat.

That pattern has three costs:

1. **Each cycle burns ~2h on packaging + dispatch + Kate-side reinstall** (verified by VERIFY-AND-SHIP runtime + restage time).
2. **Each contaminated/incomplete ship can lose tester data** — BUG-K-008 (Kate's BUG-002 overwritten) is the canonical example.
3. **The hotfix scope keeps creeping** — v0.1.4.1 was 1 line; with K-009/010/012 it's now 3 fixes; if we ship that, K-013 still blocks anything useful from happening.

**Decision (Pete, 2026-05-14):** stop shipping to Kate. Build v0.1.5 properly — including all currently-open hotfix work — and test it end-to-end here (sandbox) and on Pete's ThinkPad (mocks) before any Kate dispatch. Kate stays on the multi-ABI v0.1.4 + v0.4.4 workbook she has now; she can't run real cypress/playwright because of BUG-K-009 prereqs anyway, so she's effectively paused regardless.

---

## §2. Scope — what v0.1.5 will contain at ship time

### 2.1 Folded-in hotfix work (was: v0.1.4.1)

| Bug | Fix scope |
|-----|-----------|
| BUG-K-009 | Doc-only: KATE-V0.1.4-REINSTALL-CS.md §1 prereq section (Node 20+, `npm install` per framework, `pip install selenium`) |
| BUG-K-010 | Code: `dispatcher.py` env-label normalization (`tst-demo` → `--env demo --env-url https://tst.demo.bouracka.cz`) |
| BUG-K-012 | Code: `workbook_io` / `server.py` POST `/api/runs` — append new row to `06_TestRuns` instead of overwriting |

### 2.2 New features (v0.1.5 design notes)

| FR | Source | Sonnet brief |
|----|--------|--------------|
| FR-K-001 | Bug ↔ TC ↔ Step traceability (Test-Step as first-class entity) | Brief #002 already drafted |
| FR-K-002 | TC step preview accordion | Brief #002 + #003 chain |
| FR-K-003 | Human-readable run console | Brief #002 |
| FR-K-004 | Bug → screenshot/video evidence | Brief #002 + dispatcher artefact-copy work |

### 2.3 New v0.1.5 work added today (this plan)

| ID | Title | Why |
|----|-------|-----|
| FR-K-005 | **Mock-mode dispatch validation** — exercise the full dispatch+consolidate+envelope chain without needing cypress/playwright/selenium installed. Strict gate before any real-mode dispatch ships. | Today we can't validate the dispatch path without going through Kate. Mock mode + integration tests close that gap. |
| FR-K-006 | **Integration probe expansion** — beyond D8WS/D5WS, add probes for AISPOV (vehicle reg), zenID (identity verification), RÚIAN (address validation), N8 (SMS gateway). Reuse `int_recon.py` pattern. | We have one probe (INT-010/INT-011 / `int_recon.py`); SUPIN integration is wider than that. Recon harness becomes the way we validate environment health before any test run. |
| FR-K-007 | **TestRun cross-check reports** — extend `tools/consolidate_results.py` to produce a cross-framework agreement matrix (cypress + playwright + selenium ran TC-CP-008; did all three agree on pass/fail? which assertions differed?). | Cross-framework dispatch is the WHOLE POINT of bouracka. Without explicit cross-check, multiple frameworks just run, no comparative value. |
| **FR-K-008** | **Audit/Inspection mode** — second execution rail: select 1 TC + 1 framework + 1 env, watch test execute slow-mo in headed browser, split-pane log on `/audit` page, save video/slideshow via native PowerShell folder picker. Audit runs NEVER write to `06_TestRuns`. | Tester observability — debug what a test actually does, frame-by-frame. Critical for KP review of new specs. Pete added 2026-05-14; design + Brief #009 locked. |
| BUG-K-011 | **Workbook patcher data migration** | Brief #001b drafted. Lives in v0.1.5 because Kate's recovery needs it. |
| BUG-K-013 | **TC discovery from workbook (Option A)** | Brief #003 drafted. Major architectural change; depends on Brief #002 first. |

### 2.3a Consolidation rule — in-flight Sonnet work folds in

**Added 2026-05-15:** Any Sonnet Code session work currently in flight at the time of this plan **must be reviewed and folded into v0.1.5 release**, not left as separate-version artefacts. No mid-release branching. This applies specifically to:

- Brief #001 (workbook patcher v0.4.3 → v0.4.4) — already merged in repo state
- Any other brief Sonnet has been dispatched on in parallel sessions Pete may have started

Discipline: when Sonnet returns, Pete reviews in Opus 4.7 session AND confirms which brief output is in flight; then the merge target is the v0.1.5 integration branch, not a separate hotfix branch.

### 2.4 What's OUT of scope for v0.1.5 (defer to v0.1.6+)

- Inline step editor in UI (FR-K-002 v0.1.5 ships read-only step preview).
- Step-level parameters (`02b_TC_Parameters.scope = "step"`).
- Auto-attach screenshots/traces to bugs (manual evidence linkage for v0.1.5).
- Multi-tenant locking on shared workbook (Oracle migration territory).
- Selenium custom listener for step-level emission (cypress + playwright cover ~90% of Kate's flows).
- Air-gap install with bundled Node + npm packages (current model: install needs internet for `npm install`).

---

## §3. Test discipline — sandbox + ThinkPad mocks before any Kate ship

### 3.1 Sandbox capability (this Linux env)

What we CAN test in the sandbox:

- Python tests against workbook readers (`workbook_io.list_*`)
- Workbook patcher tests (Brief #001b style — fixture-driven)
- bouracka-ui server import + basic smoke (run uvicorn against bind-only)
- `int_recon.py` self-test against unreachable targets (graceful FAIL verdicts)
- All openpyxl-level workbook integrity checks
- Cross-framework consolidator dry runs against synthetic inputs

What we CAN'T test in sandbox:

- Actual cypress / playwright / selenium dispatch (no Node, no browsers)
- Network-bound integration probes against SUPIN-internal IPs (172.16.x.x unreachable)
- Multi-process locking
- HP Elite-specific filesystem behaviors (cp1250 encoding, path lengths)

### 3.2 ThinkPad mock capability

What runs on Pete's ThinkPad:

- Full venv install + bouracka-ui server start (VERIFY-AND-SHIP gate, proven)
- **Mock dispatch mode** (`BOURACKA_UI_DISPATCH_MODE=mock`) — bouracka-ui returns deterministic fake results without invoking cypress/etc. Tests the dispatch + consolidate + envelope chain end-to-end.
- Workbook lifecycle: patcher → reader → UI → bug edit → re-read
- Real dispatch (cypress + playwright + selenium) — once Pete installs Node + frameworks on ThinkPad (BUG-K-009 prereqs apply to him too; he just hasn't hit them yet because he hasn't been running real-mode dispatch)
- Integration probes against SUPIN VPN if connected (D8WS/D5WS reachable from Pete's box when VPN active)

### 3.3 Test ladder (must pass each gate before ship)

```
Gate 0: sandbox (this Linux env)
  - workbook_io: 33+ pytest tests green
  - workbook patcher (v0.4.3 → v0.4.4 + v0.4.4 → v0.4.5): both green, idempotent, data-migration mode green
  - server import smoke
  - int_recon.py: self-tests green, graceful FAIL on unreachable targets

Gate 1: ThinkPad mock dispatch
  - VERIFY-AND-SHIP all phases green (proven pattern)
  - NEW: mock dispatch with BOURACKA_UI_DISPATCH_MODE=mock produces envelope
  - NEW: envelope has correct cross-framework structure
  - NEW: bug edit + retest workflow round-trip green
  - NEW: TC binding column reads correctly (post-Brief-#003)

Gate 2: ThinkPad real dispatch (Pete installs Node + frameworks)
  - cypress single-spec dispatch produces real JSON output
  - playwright single-spec dispatch produces real JSON output
  - selenium single-test dispatch produces real JSON output
  - consolidate_results.py produces v0.1 envelope with all 3 frameworks
  - cross-check report (FR-K-007) compares 3 frameworks for same TC

Gate 3: Pete HP Elite VPN-connected integration smoke
  - int_recon.py probes D8WS-STD/TST + D5WS-STD/TST: all 4 healthy
  - NEW: probes for AISPOV / zenID / RÚIAN / N8 (FR-K-006) all healthy
  - integration smoke run: TC requiring D8WS write + D5WS read completes

Gate 4: Kate ship readiness
  - Kate runbook covers Node + selenium pip prereqs
  - Multi-ABI ZIP + v0.4.5 workbook bundled
  - Patcher-data-migration runbook step included (so Kate's bugs are preserved)
  - All previous BUG-K-* documented as resolved with verification evidence
```

**Discipline:** no Kate ship until Gates 0-3 all green AND I've personally verified the ZIP contents pass BUG-K-003/006 gates (we now have the post-flight gate that does this automatically).

---

## §4. Development phases — ordered

### Phase 1: Sonnet implements existing Briefs #002 + #003 (this week)

Dispatch to Sonnet in Code session, in this order:

1. **Brief #002** — workbook_io readers + new endpoints (`list_steps`, `get_step`, `get_bug_evidence` + `/api/tcs/{tc}/steps` etc.)
2. **Brief #003** — TC discovery from workbook + v0.4.4 → v0.4.5 patcher (Option A binding columns)
3. **Brief #001b** — patcher data migration (independent of #002 + #003)

Each returns to Opus 4.7 for review before merging.

### Phase 2: Hotfix code goes in here (Opus 4.7, ~1h)

Hand-edit (or Sonnet brief #004 if it grows):

- `dispatcher.py` env mapping (BUG-K-010): ~5 lines
- `workbook_io.append_test_run` / server.py `/api/runs` POST (BUG-K-012): TBD by code read, likely 10-20 lines
- KATE-V0.1.4-REINSTALL-CS.md → KATE-V0.1.5-RELEASE-CS.md §1 prereq section (BUG-K-009): ~30 lines

### Phase 3: New v0.1.5 work (mock dispatch + integrations + reports)

#### 3a. FR-K-005 mock dispatch validation (this session + Sonnet brief #005)

Build a `tests/test_mock_dispatch_e2e.py` that:
- Starts bouracka-ui server in subprocess with `BOURACKA_UI_DISPATCH_MODE=mock`
- POSTs to `/api/runs` to trigger a mock dispatch
- Polls `/api/runs/{run_id}` until done
- Verifies the envelope was produced
- Verifies envelope schema matches `_specs/CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.md`

Mock mode already exists in `dispatcher.py` (per design doc); we just need to harden it + write the e2e test.

#### 3b. FR-K-006 integration probe expansion (Sonnet brief #006)

Extend `int_recon.py` to support multiple integration targets via `targets.json` entries:

```json
{
  "target_id": "N8-STD",
  "url": "http://172.16.1.x:port/n8-sms-gateway/",
  "expected_role": "STD",
  "expected_service": "N8 (SMS gateway for OTP)",
  "probe_types": ["tcp_connect", "http_head", "wsdl_get", "soap_fault_elicit"]
},
{
  "target_id": "AISPOV-STD",
  "url": "...",
  ...
}
```

Build probes for: N8 (SMS gateway), zenID (identity verification), AISPOV-AB (vehicle registry), RÚIAN (address validation). Each gets STD + TST entries when SUPIN reveals the endpoints.

Open question: do we have those endpoints documented anywhere? Need to ask Michal Ciberej or check recon docs INT-001..INT-009 — we have 9 prior recon docs that probably cover most of these.

#### 3c. FR-K-007 TestRun cross-check reports (Sonnet brief #007)

Extend `tools/consolidate_results.py` to produce:

```json
{
  "run_id": "...",
  "tcs": [
    {
      "tc_code": "TC-CP-008",
      "framework_verdicts": {
        "cypress": "pass",
        "playwright": "pass",
        "selenium": "skip"
      },
      "agreement": "consensus",  // or "divergence" / "partial"
      "assertion_diff": [...],   // what assertions differed across frameworks
      "evidence_links": {
        "cypress": "runs/.../cypress/screenshot.png",
        ...
      }
    }
  ],
  "summary": {
    "total_tcs": 12,
    "all_pass": 8,
    "all_fail": 1,
    "divergence": 2,
    "partial_coverage": 1
  }
}
```

Plus a human-readable HTML rendering. UI exposes it via `/api/runs/{id}/cross-check`.

### Phase 4: v0.1.5 wheel build + Kate Round-3

Once Phases 1-3 land + Gate 3 green:

- Bump `__version__` → `0.1.5`
- Run multi-ABI packager + restage scripts (proven)
- Build VERIFY-AND-SHIP gate for v0.1.5 (extension of v0.1.4 gate)
- Kate runbook updated for v0.1.5 install + workbook v0.4.5 + Node + selenium prereqs
- Ship one coherent bundle, not three patches

---

## §5. Revised Sonnet brief queue

Order of dispatch to Sonnet:

| # | Brief | Status | Blocked by |
|---|-------|--------|-----------|
| Brief #001 | Workbook patcher v0.4.3 → v0.4.4 | **Merged in repo** | — |
| Brief #002 | workbook_io readers + endpoints | Drafted, ready to dispatch | — |
| Brief #003 | TC discovery from workbook (Option A) | Drafted, ready to dispatch | #002 |
| Brief #001b | Patcher row-level data migration | Drafted, ready to dispatch | — (parallel) |
| Brief #004 | Hotfix bundle (BUG-K-009/010/012) | **To draft** | — |
| Brief #005 | Mock-mode dispatch e2e test (FR-K-005) | **To draft** | #002 |
| Brief #006 | Integration probe expansion (FR-K-006) | **To draft** | — |
| Brief #007 | Cross-check reports (FR-K-007) | **To draft** | #002 |
| Brief #008 | v0.1.5 wheel build + Kate Round-3 release notes | **To draft** | All above |

Likely sequence with Opus reviews in between:

```
Brief #002 → review → merge
Brief #001b → review → merge  (in parallel with #002 if Pete uses two Code sessions)
Brief #004 (hotfix) → review → merge
Brief #003 → review → merge  (depends on #002 list_tcs shape)
Brief #005 → review → merge
Brief #006 → review → merge
Brief #007 → review → merge
Brief #008 → ship to Kate
```

Estimated effort: ~25-30 Sonnet-hours total. With Pete reviewing in Opus 4.7 between, ~2-3 calendar days of focused work.

---

## §6. What goes back to Kate when

| Trigger | What Kate receives |
|---------|--------------------|
| **Now** | Nothing new. She runs what she has (v0.1.4 multi-ABI + v0.4.4 workbook) in mock-mode-equivalent (i.e., bug edit / TC list / workbook navigation work, but she can't dispatch real frameworks without Node). |
| **After Brief #001b lands** | If Kate sends her current workbook back, Pete runs the data-migration patcher to recover her bugs into v0.4.5 schema (done offline by Pete, not by Kate). |
| **After Phase 4 / Gate 3** | Kate Round-3 ship: v0.1.5 wheel + v0.4.5 workbook + updated runbook with prereqs. One coherent bundle. |

Between now and Round-3, Kate keeps testing what she can: workbook editing, bug filing in v0.4.4, UI navigation. Real dispatch deferred until v0.1.5.

---

## §7. Definition of done — v0.1.5 ships when

- [ ] All 4 Sonnet briefs (#002, #003, #001b, #004) returned, reviewed, merged
- [ ] FR-K-005 mock-mode dispatch passes e2e test
- [ ] FR-K-006 expanded integration probes documented (endpoints may not exist yet — that's OK, structure is in place)
- [ ] FR-K-007 cross-check report generates for a mock-mode 3-framework run
- [ ] Phase 1 Gate 0 + Phase 2 Gate 1 + Phase 3 Gate 2 all green on Pete's ThinkPad
- [ ] Phase 3 Gate 3 green when Pete has SUPIN VPN active (real D8WS/D5WS probes pass)
- [ ] KATE-V0.1.5-RELEASE-CS.md authored + verified BUG-K-008 recovery procedure included
- [ ] VERIFY-AND-SHIP-V0.1.5-MULTI-ABI.ps1 extends the v0.1.4 gate with the new tests
- [ ] All currently-open BUG-K-* (008, 009, 010, 011, 012, 013) have resolution evidence in CHANGELOG.md

---

## §8. Risks + mitigations

| Risk | Mitigation |
|------|-----------|
| Brief #003 introduces UI churn that breaks workflows Kate hasn't shown us yet | Mock-mode e2e test (FR-K-005) catches before Kate sees |
| FR-K-007 cross-check requires assertion-library refactor we haven't planned | Scope tightly: just framework verdict agreement first, assertion-diff is v0.1.6 |
| Pete VPN unavailable when Gate 3 is needed | Sandbox + mock covers Gates 0-2; Gate 3 stays a precondition before Kate ship but isn't a Phase 3 blocker |
| Kate gets impatient | Counter-message: we already shipped 3 versions in 3 days and each lost her data once. Coherent v0.1.5 is faster overall AND preserves her work. |
| Sonnet brief drift across 4+ briefs causes merge conflicts | Brief order forces sequential dispatch with Opus review gates between; conflicts caught early |

---

## §9. Refs

- `_config/BOURACKA-UI-V0.1.5-DESIGN-NOTES-EN.md` — feature spec for FR-K-001..K-004
- `_config/SONNET-BRIEF-002-WORKBOOK-IO-AND-V015-ENDPOINTS.md` — ready
- `_config/SONNET-BRIEF-003-TC-DISCOVERY-FROM-WORKBOOK.md` — ready
- `_config/SONNET-BRIEF-001B-PATCHER-DATA-MIGRATION.md` — ready
- `_config/TC-DISCOVERY-DESIGN-v0.1-EN.md` — Option A decision rationale
- `recon/integrations/INT-001..INT-011.md` — existing integration recon docs (basis for FR-K-006 probe expansion)
- `_specs/CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.md` — envelope schema for FR-K-005 + FR-K-007
