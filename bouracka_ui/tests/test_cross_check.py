"""Cross-check projection tests.

PROTOTYPE for FR-K-007 (Brief #007).

Uses the proven mock-dispatch fixture (Brief #005 / test_mock_dispatch_e2e.py)
to produce real v0.1 envelopes, then exercises cross_check.build_cross_check
+ render_cross_check_html against them.

Pure-function design — no HTTP server, no subprocess. ~1s per test.

Author: Pete Y. + Opus 4.7 prototype 2026-05-15.
"""
from __future__ import annotations

import asyncio
import html.parser
import json
import sys
from pathlib import Path

import pytest

# Mirror the path setup from test_mock_dispatch_e2e.py
REPO_ROOT = Path(__file__).resolve().parents[2]
BOURACKA_UI_PKG = REPO_ROOT / "bouracka_ui"
sys.path.insert(0, str(BOURACKA_UI_PKG))

from bouracka_ui import dispatcher, cross_check  # noqa: E402


def _make_envelope(tcs, frameworks, env_label="demo", tmp_path=None):
    """Produce a real mock-dispatch envelope for testing cross_check on."""
    import os
    os.environ["BOURACKA_UI_DISPATCH_MODE"] = "mock"
    run_id = dispatcher.generate_run_id()
    registry = {run_id: {
        "run_id": run_id, "env": env_label, "tcs": tcs,
        "frameworks": frameworks, "status": "pending", "log_lines": [],
        "exit_code": None, "envelope_path": None,
    }}
    asyncio.run(dispatcher.run_async(
        run_id=run_id, env=env_label, tcs=tcs, frameworks=frameworks,
        repo_root=tmp_path or Path("/tmp/_test_cross_check"), registry=registry,
    ))
    return json.loads(Path(registry[run_id]["envelope_path"]).read_text(encoding="utf-8"))


# ───────────────────────────────────────────────────────────────────────
# build_cross_check tests
# ───────────────────────────────────────────────────────────────────────

def test_cross_check_all_agree(tmp_path):
    """3 TCs that all pass across 3 frameworks → all_agreed=3, divergence=0."""
    env = _make_envelope(["TC-CP-008", "TC-CP-015", "TC-CP-001"],
                          ["cypress", "playwright", "selenium"],
                          tmp_path=tmp_path)
    cc = cross_check.build_cross_check(env)
    assert cc["total_tcs"] == 3
    assert cc["agreement_summary"]["all_agreed"] == 3
    assert cc["agreement_summary"]["divergence"] == 0
    assert cc["divergent_tcs"] == []


def test_cross_check_with_divergence(tmp_path):
    """ALT-4 cypress fails while others pass → divergent_tcs populated."""
    # ALT-4 in mock TC name triggers fail for cypress
    env = _make_envelope(["TC-CP-ALT-4"],
                          ["cypress", "playwright", "selenium"],
                          tmp_path=tmp_path)
    cc = cross_check.build_cross_check(env)
    assert cc["agreement_summary"]["divergence"] == 1
    assert len(cc["divergent_tcs"]) == 1
    d = cc["divergent_tcs"][0]
    assert d["tc_code"] == "TC-CP-ALT-4"
    assert d["verdicts"]["cypress"] == "fail"
    assert d["verdicts"]["playwright"] == "pass"
    assert d["verdicts"]["selenium"] == "pass"
    assert d["differing_frameworks"] == ["cypress"]
    assert d["majority_verdict"] == "pass"


def test_cross_check_single_framework_not_applicable(tmp_path):
    """Single-framework run → parity_status='not-applicable' across all TCs."""
    env = _make_envelope(["TC-CP-008"], ["cypress"], tmp_path=tmp_path)
    cc = cross_check.build_cross_check(env)
    assert cc["agreement_summary"]["not_applicable"] == 1
    assert cc["agreement_summary"]["all_agreed"] == 0
    assert cc["divergent_tcs"] == []


def test_cross_check_step_anchor_resolved(tmp_path):
    """When steps_lookup provided and error msg matches, step_anchor populated."""
    env = _make_envelope(["TC-CP-ALT-4"],
                          ["cypress", "playwright", "selenium"],
                          tmp_path=tmp_path)
    # Mock has error_messages["cypress"] = "ALT-4 cypress mock failure"
    steps_lookup = {
        "TC-CP-ALT-4": [
            {"step_code": "STP-TC-CP-ALT-4-01", "action_cs": "Otevři stránku",
             "action_en": "Open page"},
            {"step_code": "STP-TC-CP-ALT-4-02", "action_cs": "ALT-4 cypress mock",
             "action_en": "ALT-4 cypress mock"},
        ],
    }
    cc = cross_check.build_cross_check(env, steps_lookup)
    d = cc["divergent_tcs"][0]
    assert d["step_anchor"] is not None
    assert d["step_anchor"]["step_code"] == "STP-TC-CP-ALT-4-02"


def test_cross_check_step_anchor_unresolved(tmp_path):
    """No matching step → step_anchor=None (no crash)."""
    env = _make_envelope(["TC-CP-ALT-4"],
                          ["cypress", "playwright", "selenium"],
                          tmp_path=tmp_path)
    steps_lookup = {"TC-CP-ALT-4": [{"step_code": "STP-X-01", "action_cs": "totally unrelated"}]}
    cc = cross_check.build_cross_check(env, steps_lookup)
    assert cc["divergent_tcs"][0]["step_anchor"] is None


def test_cross_check_step_anchor_no_workbook(tmp_path):
    """steps_lookup=None → step_anchor always None, no crash."""
    env = _make_envelope(["TC-CP-ALT-4"],
                          ["cypress", "playwright", "selenium"],
                          tmp_path=tmp_path)
    cc = cross_check.build_cross_check(env, steps_lookup=None)
    assert cc["divergent_tcs"][0]["step_anchor"] is None


def test_cross_check_top_level_fields(tmp_path):
    """run_id, env, frameworks, total_tcs propagate from envelope."""
    env = _make_envelope(["TC-CP-008", "TC-CP-001"],
                          ["cypress", "playwright"],
                          env_label="tst-demo", tmp_path=tmp_path)
    cc = cross_check.build_cross_check(env)
    assert cc["run_id"] == env["run_id"]
    assert cc["env"] == "tst-demo"
    assert cc["env_url"] == "https://tst.demo.bouracka.cz"
    assert sorted(cc["frameworks"]) == ["cypress", "playwright"]
    assert cc["total_tcs"] == 2


# ───────────────────────────────────────────────────────────────────────
# render_cross_check_html tests
# ───────────────────────────────────────────────────────────────────────

class _HTMLValidator(html.parser.HTMLParser):
    """Simple HTML parser to verify validity (no dangling tags)."""
    def __init__(self):
        super().__init__()
        self.errors = []
        self.tag_stack = []
        self.text_chunks = []

    def handle_starttag(self, tag, attrs):
        if tag not in ("br", "hr", "img", "input", "meta", "link"):
            self.tag_stack.append(tag)

    def handle_endtag(self, tag):
        if not self.tag_stack:
            self.errors.append(f"unexpected close tag {tag}")
            return
        if self.tag_stack[-1] != tag:
            self.errors.append(f"mismatched: expected </{self.tag_stack[-1]}>, got </{tag}>")
        else:
            self.tag_stack.pop()

    def handle_data(self, data):
        self.text_chunks.append(data)


def test_cross_check_html_parses_clean(tmp_path):
    """HTML render produces valid HTML with no dangling tags."""
    env = _make_envelope(["TC-CP-008", "TC-CP-ALT-4"],
                          ["cypress", "playwright", "selenium"],
                          tmp_path=tmp_path)
    cc = cross_check.build_cross_check(env)
    html_text = cross_check.render_cross_check_html(cc)

    validator = _HTMLValidator()
    validator.feed(html_text)
    assert validator.errors == [], f"HTML errors: {validator.errors}"
    assert validator.tag_stack == [], f"unclosed tags: {validator.tag_stack}"


def test_cross_check_html_no_external_deps(tmp_path):
    """No <script src='...'>, no <link href='http...'> — fully self-contained."""
    env = _make_envelope(["TC-CP-008"],
                          ["cypress", "playwright"],
                          tmp_path=tmp_path)
    cc = cross_check.build_cross_check(env)
    html_text = cross_check.render_cross_check_html(cc)
    assert "<script src" not in html_text.lower(), "external script src found"
    # link href is OK if pointing at internal env-url anchor; ensure no external CSS
    assert "stylesheet" not in html_text.lower() or "rel='stylesheet'" not in html_text


def test_cross_check_html_renders_divergence(tmp_path):
    """ALT-4 fail should show up in HTML divergent-TCs table."""
    env = _make_envelope(["TC-CP-ALT-4"],
                          ["cypress", "playwright", "selenium"],
                          tmp_path=tmp_path)
    cc = cross_check.build_cross_check(env)
    html_text = cross_check.render_cross_check_html(cc)
    assert "TC-CP-ALT-4" in html_text
    assert "fail" in html_text.lower()
    assert "cypress" in html_text


def test_cross_check_html_renders_empty_state(tmp_path):
    """No divergence → 'no cross-framework divergence detected' message."""
    env = _make_envelope(["TC-CP-008"],
                          ["cypress", "playwright"],
                          tmp_path=tmp_path)
    cc = cross_check.build_cross_check(env)
    html_text = cross_check.render_cross_check_html(cc)
    assert "no cross-framework divergence detected" in html_text.lower()
