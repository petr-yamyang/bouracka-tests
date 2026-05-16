# Sonnet brief — BRIEF-007: TestRun cross-check report (FR-K-007)

**Target Claude.** Sonnet 4.6 in Claude Code (terminal, stateless).
**Issued by.** Opus 4.7 session, 2026-05-15.
**Branch.** `cp-supin-15-cross-check-report`.
**Estimated effort.** ~4 hours.
**Reviewer.** Pete in Opus 4.7 session.
**Blocked by.** Brief #002 (server endpoints) + Brief #005 (envelope shape stable + validated).

---

## 1. Goal in one paragraph

Cross-framework dispatch is the WHOLE POINT of bouracka: run a single TC against cypress + playwright + selenium, see how they compare. The current v0.1 envelope ALREADY has `parity_status` (`agree` / `divergence` / `not-applicable`) per TC. But there's no aggregate cross-check view, no human-readable rendering, no easy answer to "did this run reveal cross-framework divergence?" This brief adds: (1) a server-side cross-check aggregator that walks an envelope's `results[]` and emits a `cross_check` summary block; (2) an HTML rendering of that block for tester review; (3) a new endpoint `/api/runs/{run_id}/cross-check` that returns the cross-check view of an existing run. NEVER modifies the envelope schema — the cross-check is a derived projection.

---

## 2. Spec — read this BEFORE coding

1. `bouracka_ui/bouracka_ui/dispatcher.py` `_build_mock_envelope` (line ~318) + `_summarize` — current envelope shape including `parity_status` field
2. `bouracka_ui/tests/test_mock_dispatch_e2e.py` — envelope validator + Family A direct-call tests; you reuse `assert_envelope_valid` to test cross-check on the envelopes it produces
3. `_specs/CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.md` — envelope schema doc; cross-check is a SEPARATE projection, doesn't change envelope
4. `tools/consolidate_results.py` — real-mode consolidator that produces the envelope; you may need a tiny extension here to ensure parity computation matches mock's behavior

---

## 3. Inputs / outputs

### Inputs

- v0.1 envelope produced by either mock or real dispatch
- Workbook (for 02e_TestSteps step labels, optional)

### Outputs

- `bouracka_ui/bouracka_ui/cross_check.py` — new module (~300 lines)
- New endpoint `GET /api/runs/{run_id}/cross-check` returning JSON
- New endpoint `GET /api/runs/{run_id}/cross-check.html` returning rendered HTML
- 6 new tests
- CHANGELOG entry v0.1.5-dev5

---

## 4. File boundaries

### Create

- `bouracka_ui/bouracka_ui/cross_check.py` — aggregator + HTML renderer (vanilla Python, no jinja)
- `bouracka_ui/bouracka_ui/static/cross-check.css` — styling for HTML render (~50 lines)
- `bouracka_ui/tests/test_cross_check.py` — 6 new tests

### Modify

- `bouracka_ui/bouracka_ui/server.py` — add 2 endpoints
- `bouracka_ui/bouracka_ui/__init__.py` → `__version__ = "0.1.5-dev5"`
- `bouracka_ui/pyproject.toml` → `0.1.5.dev5`
- `CHANGELOG.md` — entry

### DO NOT touch

- `dispatcher.py` — envelope produced unchanged
- `consolidate_results.py` — out of scope unless parity logic is missing; if so, only ADD `parity_status` field, don't change anything else
- `_specs/CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.md` — schema is authoritative

---

## 5. Functional requirements

### F-1. `cross_check.py` aggregator

```python
"""Cross-framework agreement projection over a v0.1 envelope.

Given an envelope, produces a 'cross_check' dict summarizing how the
frameworks agreed/disagreed per TC. Pure function; does not modify envelope.
"""

def build_cross_check(envelope: dict, steps_lookup: dict | None = None) -> dict:
    """
    Args:
      envelope: v0.1 envelope (from runs/cross-framework-*.json or in-memory)
      steps_lookup: optional {tc_code: [step_dict, ...]} from workbook_io.list_steps

    Returns:
      {
        "run_id": "...",
        "env": "...",
        "frameworks": [...],
        "total_tcs": N,
        "agreement_summary": {
          "all_agreed": int,         # parity_status == "agree" across all TCs
          "divergence": int,
          "not_applicable": int,
          "missing_coverage": int    # TCs where one framework reported "missing"
        },
        "divergent_tcs": [
          {
            "tc_code": "...",
            "verdicts": {"cypress": "fail", "playwright": "pass", "selenium": "pass"},
            "differing_frameworks": ["cypress"],   # those that didn't match the majority
            "majority_verdict": "pass",            # mode of non-missing verdicts
            "step_anchor": {                       # if steps_lookup provided
              "step_code": "STP-TC-CP-008-03",
              "step_label": "Click VYPLNIT ZÁZNAM"
            } or None,
            "error_messages": {"cypress": "...", "playwright": null, ...}
          },
          ...
        ],
        "tc_full_matrix": [
          {
            "tc_code": "...",
            "verdicts": {...},
            "parity_status": "...",
            "soft_pass_reason": "..." or null
          },
          ...
        ]
      }
    """
```

Behavior rules:

- `parity_status = "agree"` → contributes to `all_agreed`
- `parity_status = "divergence"` → goes into `divergent_tcs` list with majority analysis
- Any TC with `"missing"` verdict for any framework → `missing_coverage++`
- Soft-pass treated as pass for parity arithmetic (already done in dispatcher's `_normalize_for_parity`)
- `step_anchor` derived from error message text matching `02e_TestSteps.action_*` (heuristic; if no match, return null)

### F-2. HTML renderer

```python
def render_cross_check_html(cross_check: dict) -> str:
    """Produce a standalone HTML page with cross-check view.

    Layout:
      [Header]  run_id · env · timestamp
      [Summary stats]  pie/bars for agree/divergence/missing/total
      [Divergent TCs section]  table with TC code, verdicts per framework
                               (cells color-coded), step anchor, error msgs
      [Full matrix section]    every TC + verdicts (collapsible)

    No external deps — inline CSS, no JS frameworks. ~200 lines of HTML.
    """
```

Color coding:
- pass: green
- soft-pass: light green
- fail: red
- skip-drift: orange
- skip-other: yellow
- error: dark red
- missing: gray

### F-3. New endpoints

```python
@app.get("/api/runs/{run_id}/cross-check")
async def get_cross_check_json(run_id: str):
    """Return cross-check projection of the run's envelope as JSON."""
    envelope_path = _find_envelope_for_run(run_id)
    if not envelope_path:
        raise HTTPException(404, f"envelope not found for run {run_id}")
    envelope = json.loads(envelope_path.read_text())
    steps_lookup = workbook_io.list_all_steps_grouped_by_tc(WORKBOOK_PATH)
    return cross_check.build_cross_check(envelope, steps_lookup)

@app.get("/api/runs/{run_id}/cross-check.html", response_class=HTMLResponse)
async def get_cross_check_html(run_id: str):
    """Same projection, rendered as HTML."""
    data = await get_cross_check_json(run_id)
    return cross_check.render_cross_check_html(data)
```

### F-4. 6 new tests

```python
def test_cross_check_all_agree():
    """3 TCs, all 3 frameworks pass → all_agreed=3, divergent_tcs=[]"""

def test_cross_check_with_divergence():
    """ALT-4 scenario: cypress fail, others pass → divergent_tcs has 1 entry"""

def test_cross_check_missing_coverage():
    """TC ran only cypress (playwright/selenium=missing) → missing_coverage++"""

def test_cross_check_step_anchor_resolved():
    """Error msg matches a workbook step → step_anchor populated"""

def test_cross_check_step_anchor_unresolved():
    """No matching step → step_anchor=None (no crash)"""

def test_cross_check_html_renders_without_dependencies():
    """HTML output is valid standalone HTML (parseable by html.parser); no external <script>/<link> tags."""
```

### F-5. CHANGELOG + version

```
__version__ = "0.1.5-dev5"
```

CHANGELOG v0.1.5-dev5:

- FR-K-007: cross-framework agreement projection
- New `cross_check.py` module — pure-function projection from envelope to agreement view
- New `/api/runs/{id}/cross-check` (JSON) + `/cross-check.html` (HTML) endpoints
- 6 new tests; smoke count: prev → prev+6

---

## 6. Idempotency

- Pure function — same envelope → same cross-check, always.
- HTML render also pure — same input → same output (modulo no timestamps; if needed, generate `<meta http-equiv="cached"...>` from envelope's `started_at`).

---

## 7. Risk gates

1. **Envelope schema drift** between mock and real consolidator — if `parity_status` is in mock but consolidate_results.py doesn't emit it, halt. The cross-check NEEDS this field. Fix consolidate_results.py to emit it (one-line addition mirroring mock logic).
2. **No workbook available** at runtime — `steps_lookup` is None, `step_anchor` always None — that's acceptable, not a halt.
3. **Soft-pass + skip semantics ambiguity** — clarify with Pete if soft-pass + pass = "agree" or "divergence-but-soft". My default: treat soft-pass as pass for parity (matches dispatcher).
4. **HTML render too large** — if cross-check has 500 TCs, HTML page might be >1 MB. Cap full_matrix render at top 100; link to JSON for rest. Halt + ask if higher cap needed.

---

## 8. Don't-go-beyond

- Don't modify the envelope schema — cross_check is a projection, not an extension
- Don't add JS to HTML render — keep it static-renderable + email-safe
- Don't persist cross-check JSON to disk — recompute on demand from envelope
- Don't add `assertion_diff` field (full assertion-level comparison) — that's v0.1.6; this brief just does TC-level
- Don't change `parity_status` semantics — already established in dispatcher

---

## 9. Return checklist

1. Branch + SHAs
2. Files changed
3. Test results (all green incl. existing mock dispatch tests)
4. Curl outputs:
   - `curl http://127.0.0.1:8424/api/runs/<run_id>/cross-check` (JSON) — paste verbatim
   - `curl http://127.0.0.1:8424/api/runs/<run_id>/cross-check.html | head -100` (HTML head)
5. Screenshot OR text-diff of HTML render against a sample envelope with 3 TCs + 1 divergence
6. Out-of-scope findings
7. Deviations
8. Open questions for Brief #008 (release engineering)

---

## 10. Acceptance

- 6 new tests pass + existing tests stay green
- Both endpoints return valid JSON / HTML on real envelopes
- HTML renders without external dependencies (no CDN, no fonts)
- `__version__` = `0.1.5-dev5`
- CHANGELOG updated
- Branch ready for merge

---

**End of BRIEF-007.**
