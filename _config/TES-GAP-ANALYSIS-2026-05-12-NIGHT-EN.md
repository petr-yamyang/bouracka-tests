# TES Presentation Layer — Gap Analysis — Day 1A — 2026-05-12 night (EN)

**Status.** Day 1A deliverable per `_config/TEST-ANALYSIS-AND-DESIGN-DEEP-SESSIONS-PLAN-v0.1-EN.md` urgent-track redirect. Cowork-authored during the post-Kate-dispatch night session; awaits Pete review in the morning before Days 2-3 implementation.
**Trigger.** Pete 2026-05-12: *"focus on bouracka now is paramount, need to be resolved within 2-3 days in any time cost"* + *"both backend incomplete AND UI presentation thin"*.
**Method.** Read the binding schema spec, the backend consolidator end-to-end, and the frontend renderer end-to-end. Identify each (consume × emit) gap. Categorize by impact, effort, and Pete-decision-needed.
**Scope.** TES presentation only. Integration enablement (N8/AISPOV/zenID) is a separate track.

---

## §1. Files examined

| File | Role | Status |
|------|------|--------|
| `_specs/CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.md` | Binding wire format (v1.0) | Spec end-to-end read |
| `tools/consolidate_results.py` v0.5.4 | Backend envelope emitter | All 8 sections read |
| `bouracka_ui/bouracka_ui/static/app.js` | Frontend renderer (vanilla JS SPA) | `renderResults*` family + supporting fns read |
| `bouracka_ui/bouracka_ui/server.py` | FastAPI route handlers for `/api/runs/*` | Inspected route 91 onward (REPO_ROOT resolution + endpoint contracts) |
| `bouracka_ui/bouracka_ui/dispatcher.py` | Subprocess orchestrator → consolidate_results.py | Full read |
| `bouracka_ui/bouracka_ui/trace_bundle.py` | Bundle export/import + evidence handling | Read referenced sections |

---

## §2. Backend state (consolidate_results.py v0.5.4)

The backend is **more complete than the "incomplete" framing suggests**, but has specific identifiable gaps. What it does well:

| Capability | Implemented | Where |
|-----------|-------------|-------|
| Pivot flat-per-(fw,TC) → nested-per-TC | YES | `_pivot_to_nested()` lines 304-359 |
| Compute parity_status per schema §3.4 | YES | `_compute_parity_status()` lines 293-301 |
| Compute summary per schema §3.6 | YES | `_compute_summary()` lines 362-404 |
| Capture host info (os, hostname, git) | YES | `_capture_host()` lines 431-450 |
| Drift forensic synthesis from DRIFT-* markers | YES | `_synthesize_drift_forensic()` lines 590-626 |
| Producer-side validation per schema §5.1 | YES | `_validate_envelope()` lines 473-498 |
| Markdown digest output | YES | `_write_md()` lines 521-583 |
| Run-id generation per Windows-safe regex | YES | `_generate_run_id()` lines 415-428 |
| Env auto-inference from URL | YES | `_infer_env_from_url()` lines 453-466 |
| Soft-pass marker handling | YES | `SOFT_PASS_MARKERS` set + `_map_status()` |
| Per-fw skip reason → skip-drift / skip-other classification | YES | `_classify_skip()` lines 104-113 |

### §2.1 Backend gaps

| # | Gap | Impact | Effort | Decision-needed? |
|---|-----|--------|--------|-------------------|
| **B-01** | **`drift_forensic.drift_type` taxonomy limited** — recognizes only `recaptcha-v3`, `recaptcha-v2`, `rate-limit` (lines 607-617). BUG-CY-001 IPC-114 (Chromium renderer kill on Cypress headed mode) NOT in taxonomy. Same-origin connection-pool drift not in taxonomy. | MEDIUM — drift is misclassified as default `recaptcha-v3` | LOW — add 2-3 enum entries + pattern matching | NO (taxonomy expansion is mechanical) |
| **B-02** | **Selenium evidence sparse** — `_parse_selenium()` (lines 232-276) extracts only `screenshot_ref`; `video_ref` and `trace_ref` always null. Selenium does have `selenium-wire` capability (per `conftest.py` comment) — traces are recoverable. | MEDIUM — Kate can't drill from a Selenium failure to a trace | MEDIUM — needs `selenium-wire` opt-in + trace serialization | YES — opt-in feature; Pete decides whether to add for v0.1.3 |
| **B-03** | **Cypress trace_ref always null** — `_parse_cypress()` (lines 191-228) hardcodes `trace_ref: None`. Cypress does generate `cypress-runner-results.json` with command-log traces; not currently consumed. | LOW-MEDIUM — Cypress failures can be debugged from video + screenshot; trace_ref adds value but isn't blocking | MEDIUM | NO (clear improvement) |
| **B-04** | **`host.tool_versions` left as None** — `_capture_host()` (line 437) hardcodes `tool_versions: None`. Per schema §3.7 these are optional, but their absence means cross-host run comparison can't account for tool version differences. | LOW — informational | LOW — `subprocess.check_output(['npx', 'cypress', '--version'], ...)` per fw | NO |
| **B-05** | **No previous-run comparison** — each envelope is standalone. No diff vs prior run on same env. Schema doesn't require it; not in v0.1 but obvious extension. | LOW for v0.1.3; MEDIUM-HIGH for trend tracking | MEDIUM — needs scan of `runs/` for prior envelope on same env | YES — Pete decides if this lands in v0.1.3 or v0.1.4 |
| **B-06** | **Markdown digest thin** — `_write_md()` produces basic table + failure list + drift block + provenance. No evidence-link list, no per-fw duration breakdown, no covered-TT summary. | LOW-MEDIUM — MD digest is secondary to UI presentation | LOW-MEDIUM — additive sections | NO |
| **B-07** | **No assertion-level data propagation** — `14_AssertionGateResults` sheet exists but consolidator doesn't read it. Schema §1 says "out of scope" but Pete asked for it as a v0.1.1 extension. | MEDIUM — drill-down to assertion level is high value for failure triage | MEDIUM-HIGH — needs workbook read + envelope schema extension (v1.1 candidate) | YES — Pete decides scope (v0.1.3 vs v0.1.4) |
| **B-08** | **Empty fixture path** when frameworks fail to produce output — `_parse_playwright/_parse_cypress/_parse_selenium` warn but return []. Resulting envelope has all `verdicts.<fw> = missing`. Frontend currently handles this but the user sees "missing × 3" with no explanation. | LOW — edge case; usually resolved by re-running | LOW — add a `parse_warnings: [...]` informational field to envelope | NO |

---

## §3. Frontend state (app.js renderResults family)

The frontend `renderResults()` dispatches to three sub-renderers based on response status:
- `renderResultsInFlight()` — HTTP 202 with status + log_lines
- `renderResultsDispatchFailed()` — HTTP 200 with status=done but envelope_path=None
- `renderResultsFullEnvelope()` — HTTP 200 with full envelope

The full-envelope renderer produces:
- Title (Run + rid)
- Summary chip-strip (8 chips: TCs, Pass, Fail, Skip, Soft, Strict, Drift-aware, Diverge)
- Pill bar with env + frameworks + start→end + duration_ms
- Verdict matrix: TC × fw cells + parity column + bug-file link
- Drift forensic card (conditionally shown when `drift_forensic.active`)
- Provenance card (schema_version, host, git, reporter)

### §3.1 Frontend gaps

| # | Gap | Impact | Effort | Decision-needed? |
|---|-----|--------|--------|-------------------|
| **F-01** | **No error message on fail/error cells** — verdict matrix renders `<span class="pill verdict-fail">fail</span>` but `error_messages.<fw>` is in the envelope and unused. Kate has to export the trace bundle to see WHY a TC failed. | **HIGH** — primary friction for failure triage | LOW — title attribute or click-expand row | NO (clear improvement) |
| **F-02** | **No evidence links rendered** — `evidence.<fw>.{trace_ref, screenshot_ref, video_ref}` are in the envelope but the matrix shows verdict only. No clickable link to screenshot / video / trace. | **HIGH** — Kate sees a failure but can't see what it looked like | LOW-MEDIUM — render evidence icons per cell or per row | NO |
| **F-03** | **No per-framework duration breakdown** — envelope has `duration_ms` per fw per TC, plus run-level aggregate. UI shows only run-level. | MEDIUM — Kate can't tell which fw is slow on a given TC | LOW — additional column per fw in matrix or expandable row | NO |
| **F-04** | **No matrix filter / sort** — large run with 49 TCs displays unfiltered, unsorted. Kate scrolls through everything to find failures. | MEDIUM-HIGH — usability for larger runs | MEDIUM — JS sort + filter on a vanilla-JS table | NO |
| **F-05** | **Drift forensic card is thin** — shows type + affected TCs + notes + correlation. No visual correlation trail (which TC triggered first, which followed). No BUG-CY-001 narrative integration. | MEDIUM — drift situations are recurring and need richer storytelling | MEDIUM — additional rendering logic + narrative templates | NO (mechanical) |
| **F-06** | **No per-TC drill-down panel** — clicking a TC code does nothing. There's no expand/collapse UX showing `covered_tt`, `framework_specific_notes`, full error_messages, evidence links per fw. | **HIGH** — drilling down is the natural failure-triage UX | MEDIUM — modal or accordion row | NO |
| **F-07** | **No comparison to previous run** — pairs with B-05. UI shows current envelope only; no "this run vs prior run on same env" delta widget. | LOW-MEDIUM for v0.1.3; HIGH for trend tracking | MEDIUM (depends on B-05 backend support) | YES — coordinates with B-05 |
| **F-08** | **No assertion-level breakdown** — pairs with B-07. UI doesn't render assertion details because envelope doesn't carry them. | MEDIUM-HIGH for failure triage | MEDIUM (depends on B-07 backend support) | YES — coordinates with B-07 |
| **F-09** | **Provenance card is data-dump** — shows raw key:value pairs. Could be grouped (Host / Git / Reporter sections), shown collapsed by default. Minor cosmetic. | LOW | LOW | NO |
| **F-10** | **No coverage-rule phase indicator** — per `_specs/COVERAGE-RULE-STRATEGY-v0.1-CS.md` there's a Phase 0..3 gating concept. UI doesn't show what phase this env is operating under. | LOW for now; MEDIUM as Cíl-2 enables strict gating | LOW — small badge based on env enum | NO |
| **F-11** | **`framework_specific_notes` unused** — envelope carries this string per (TC, fw) but UI doesn't render it. Useful for surfacing raw selenium status ("timed_out", "interrupted") that doesn't fit the canonical 7-verdict enum. | LOW-MEDIUM | LOW — additional micro-pill on cells where notes is non-empty | NO |
| **F-12** | **Bug-file link doesn't auto-include error context** — clicking "+ bug" opens `/bugs?tc=X&run=Y` with prefill in sessionStorage, but the prefill is `{tc, run, env}` only — not the error_messages content. Kate has to re-type the error. | MEDIUM | LOW — extend prefill with error+evidence | NO |

---

## §4. Schema-spec compliance — verdict

Does the backend emit envelopes that conform to schema v0.1 §3? Per my read: **YES, with minor caveats**.

| Field | Schema requirement | Backend emits | Status |
|-------|---------------------|---------------|--------|
| `schema_version` | exactly `"1.0"` | `SCHEMA_VERSION = "1.0"` | ✓ |
| `run_id` | regex per §3.1 | `_generate_run_id()` + validator | ✓ |
| `env` | enum per §3.1 | `ENV_ENUM` + auto-inference | ✓ |
| `env_url` | optional URL or null | `--env-url` flag, fallback to `--base-url` | ✓ |
| `started_at`/`ended_at` | ISO-8601 UTC w/ Z | `_utc_now_iso()` | ✓ |
| `duration_ms` | ended-started in ms | computed line 688-691 | ✓ |
| `frameworks` | sorted, deduplicated, ≥1 | `sorted({r["framework"] for r in flat})` | ✓ |
| `results[]` | per §3.2 schema | `_pivot_to_nested()` produces correct shape | ✓ |
| `results[].verdicts` | enum per §3.3 | `_map_status()` produces canonical 7-enum | ✓ |
| `results[].parity_status` | computed per §3.4 | `_compute_parity_status()` | ✓ |
| `results[].duration_ms` | per-fw object | populated | ✓ |
| `results[].evidence` | per-fw {trace, screenshot, video} | all 3 fields always present (null where applicable) | ✓ |
| `results[].covered_tt` | dedup'd, sorted | `sorted(covered_tt_set)` | ✓ |
| `results[].error_messages` | per-fw first-line | populated | ✓ |
| `results[].framework_specific_notes` | per-fw raw status if non-canonical | populated | ✓ |
| `results[].viewport` | default `"375x667"` | first non-null per-fw viewport | ✓ |
| `results[].bug_ref` | nullable | always `None` (no auto-bug-link) | ✓ (schema-compliant; B-07 would extend) |
| `results[].soft_pass_reason` | required if any soft-pass | auto-populated for SOFT_PASS_MARKERS TCs | ✓ |
| `summary.*` | computed per §3.6 | `_compute_summary()` | ✓ |
| `host.*` | os, host, optional git + tool_versions | os+host+git populated; tool_versions=None (B-04) | ✓ (schema-compliant) |
| `drift_forensic` | nullable; or per §3.7 | `_synthesize_drift_forensic()` produces correct shape | ✓ (taxonomy limited per B-01) |
| `reporter.*` | command, trigger, ci_run_id, operator | populated | ✓ |
| Producer validation | §5.1 assertions | `_validate_envelope()` runs assertions | ✓ |

**Conclusion:** the envelope is **schema-conformant**. The "backend incomplete" framing is more accurately "backend produces compliant envelope but with some fields under-utilized (B-01..B-08)".

---

## §5. Gap priorities — recommendation for v0.1.3 scope

Pete's acceptance bar = "Full presentation enrichment — all 8+ gaps". Mapping the 20 identified gaps (8 backend + 12 frontend) to v0.1.3 vs v0.1.4:

### §5.1 v0.1.3 scope (Days 2-3) — recommended 12 items

**Day 2 backend (5 items):**
- **B-01** — drift_forensic taxonomy expansion (BUG-CY-001 IPC-114, same-origin-pool drift)
- **B-03** — Cypress trace_ref wiring from cypress-runner-results.json
- **B-04** — `host.tool_versions` capture
- **B-06** — Markdown digest enrichment (evidence list, per-fw duration table)
- **B-08** — `parse_warnings: [...]` informational field for empty-fixture cases

**Day 3 frontend (7 items):**
- **F-01** — Error messages on fail cells (title attribute + click-expand)
- **F-02** — Evidence link rendering (icons per cell, click to bundle)
- **F-03** — Per-framework duration breakdown (expandable row per TC)
- **F-04** — Matrix filter/sort (verdict, parity, fw filter; TC code sort)
- **F-05** — Drift forensic richer card (correlation trail visual)
- **F-06** — Per-TC drill-down panel (accordion expand per row)
- **F-09** — Provenance card grouped sections (small cosmetic win)

### §5.2 v0.1.4 candidates (defer)

- **B-02** — Selenium video/trace via selenium-wire (opt-in feature; needs Pete decision on selenium-wire dependency)
- **B-05** + **F-07** — Previous-run comparison (pairs across backend+frontend; bigger feature)
- **B-07** + **F-08** — Assertion-level propagation (schema v1.1 extension; needs Pete decision on scope)
- **F-10** — Coverage-rule phase indicator (low priority until Cíl-2)
- **F-11** — `framework_specific_notes` micro-pill (LOW impact; can wait)
- **F-12** — Bug-file prefill with error context (after F-01 lands, this is a natural extension)

### §5.3 Effort estimates per day

| Day | Items | Cowork+Pete pair-work | Cowork alone | Pete review |
|-----|-------|------------------------|--------------|--------------|
| Day 2 backend | 5 items | 3 hours (B-01, B-03, B-08 + integration testing) | 2 hours (B-04, B-06 — mechanical) | 1 hour review |
| Day 3 frontend | 7 items | 5 hours (F-01, F-02, F-04, F-06 — UX-critical) | 2 hours (F-03, F-05, F-09 — additive) | 1 hour review |

Total: 6 hours active pair-work + 4 hours Cowork-alone + 2 hours Pete review = ~10 hours over 2 days.

---

## §6. Quick wins implementable tonight (Day 1A bonus)

The following gaps require **zero Pete-decision** and are mechanical fixes I can land tonight after writing this gap analysis. If you wake up and they're already on disk, that's bonus headstart:

| Gap | Why safe to land tonight | Estimated effort |
|-----|---------------------------|------------------|
| **B-01 (partial)** — add BUG-CY-001 IPC-114 to drift_type taxonomy | Pattern-matching addition; doesn't change envelope shape | 15 min |
| **B-04** — `host.tool_versions` best-effort capture | Additive optional field per schema §3.7 | 20 min |
| **B-08** — `parse_warnings` field for empty-fixture cases | Additive informational field | 15 min |
| **F-09** — Provenance card grouped sections | Pure cosmetic; UI-side only | 15 min |

If I implement these tonight: ~1 hour of work, all schema-compliant, all reversible. **I'll defer the riskier items (B-02, B-05, B-07, F-01..F-08) until you've reviewed this doc.**

---

## §7. Open questions for Pete (morning review)

| OQ | Question | Default recommendation |
|----|----------|------------------------|
| OQ-TES-01 | Land B-02 (Selenium video/trace via selenium-wire) in v0.1.3 or defer? | Defer to v0.1.4 — adds dependency, not blocking for Kate |
| OQ-TES-02 | Land B-07 (assertion-level data) in v0.1.3 or defer? | Defer to v0.1.4 — schema v1.1 candidate; bigger surface |
| OQ-TES-03 | Land B-05/F-07 (previous-run comparison) in v0.1.3 or defer? | Defer to v0.1.4 — useful but not Kate-blocking |
| OQ-TES-04 | F-06 drill-down UX — modal overlay or inline accordion? | Inline accordion — matches existing matrix style; lower friction |
| OQ-TES-05 | F-04 filter UX — sidebar or toolbar above matrix? | Toolbar above matrix — minimal layout change |
| OQ-TES-06 | F-02 evidence rendering — clickable icons per cell or per row? | Per-cell icons (more granular; matches user's mental model of "this fw's evidence for this TC") |
| OQ-TES-07 | Day 2 implementation order — backend-first then frontend, or pair-wise feature-by-feature? | Backend-first then frontend — clearer testability; v0.1.3 wheel can ship even if Day 3 frontend slips |
| OQ-TES-08 | Should v0.1.3 trigger a re-ship to Kate, or wait for v0.1.4 with the broader feature set? | Re-ship to Kate after v0.1.3 — she gets the failure-triage UX (F-01, F-02, F-06) which is highest immediate value |

---

## §8. Cross-references

- `_specs/CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.md` — binding wire format
- `_config/BOURACKA-TES-PRESENTATION-LAYER-DESIGN-v0.1-2026-05-09.md` — design doc (referenced but not on this machine; MacBook-only)
- `tools/consolidate_results.py` v0.5.4 — backend emitter
- `bouracka_ui/bouracka_ui/static/app.js` — frontend renderer
- `_config/TEST-ANALYSIS-AND-DESIGN-DEEP-SESSIONS-PLAN-v0.1-EN.md` — sets the priority context

---

End of v0.1 night gap analysis. Pete's morning review → decisions → Day 2 starts.
