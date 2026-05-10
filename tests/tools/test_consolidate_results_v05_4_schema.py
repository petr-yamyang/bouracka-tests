"""
Tests for tools/consolidate_results.py v0.5.4 — v0.1 schema conformance.

Validates that:
  - The output envelope matches CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.md §2 shape
  - Producer-side assertions (§5.1) all pass on a synthetic 3-framework run
  - Pivot from flat per-(fw,tc) → nested per-TC verdicts is correct
  - parity_status computation per §3.4 is correct (agree / divergence / not-applicable)
  - summary computation per §3.6 is correct
  - skip-drift vs skip-other distinction works via DRIFT-* marker prefix
  - Soft-pass marker (TC-CP-A2-ALT-9) propagates correctly

Usage:
  cd ~/Documents/VibeCodeProjects/SUPIN/bouracka-tests
  python3 -m pytest tests/tools/test_consolidate_results_v05_4_schema.py -v
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import pytest

# Make tools/ importable
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import consolidate_results as cr  # noqa: E402


# ──────────────────────────────────────────────────────────────────────────
# Fixture data — synthetic per-framework JSON outputs
# ──────────────────────────────────────────────────────────────────────────

PLAYWRIGHT_FIXTURE = {
    "suites": [
        {"title": "cíl 1 — happy day",
         "specs": [
             {"title": "TC-CP-A1-MAIN-DEMO main happy day",
              "tests": [
                  {"title": "TC-CP-A1-MAIN-DEMO",
                   "results": [{"status": "passed", "duration": 1234,
                                "attachments": [{"name": "trace", "path": "trace.zip",
                                                 "contentType": "application/zip"}]}],
                   "annotations": []},
              ]},
             {"title": "TC-CP-A2-ALT-7 enumerations",
              "tests": [
                  {"title": "TC-CP-A2-ALT-7",
                   "results": [{"status": "passed", "duration": 800}],
                   "annotations": []},
              ]},
             {"title": "TC-CP-A2-ALT-9 reports drift",
              "tests": [
                  {"title": "TC-CP-A2-ALT-9",
                   "results": [{"status": "passed", "duration": 1500}],
                   "annotations": []},
              ]},
             {"title": "TC-CP-A2-ALT-1 rp regex",
              "tests": [
                  {"title": "TC-CP-A2-ALT-1",
                   "results": [{"status": "skipped", "duration": 50}],
                   "annotations": [{"type": "skip",
                                    "description": "DRIFT-RECAPTCHA-V3:correlation_id=abc-1234"}]},
              ]},
         ]},
    ]
}

CYPRESS_FIXTURE = {
    "results": [
        {"fullTitle": "cíl 1",
         "tests": [
             {"fullTitle": "TC-CP-A1-MAIN-DEMO main happy day",
              "state": "passed", "duration": 1567,
              "screenshots": [{"path": "screen-tc-a1.png"}]},
             {"fullTitle": "TC-CP-A2-ALT-7 enumerations",
              "state": "passed", "duration": 750},
             {"fullTitle": "TC-CP-A2-ALT-9 drift",
              "state": "passed", "duration": 1480},
             {"fullTitle": "TC-CP-A2-ALT-1 rp regex",
              "state": "pending", "duration": 0,
              "err": {"message": "DRIFT-RECAPTCHA-V3:correlation_id=abc-1234"}},
         ]},
    ]
}

SELENIUM_FIXTURE = {
    "tests": [
        {"nodeid": "tests/a1_main/test_main_happy_day.py::test_TC_CP_A1_MAIN_DEMO",
         "outcome": "passed", "duration": 1.18},
        {"nodeid": "tests/a2_alternates/test_alt_7_enumerations.py::test_TC_CP_A2_ALT_7",
         "outcome": "passed", "duration": 0.92},
        {"nodeid": "tests/a2_alternates/test_alt_9_post_reports_drift.py::test_TC_CP_A2_ALT_9",
         "outcome": "passed", "duration": 1.40},
        {"nodeid": "tests/a2_alternates/test_alt_1_rp_regex.py::test_TC_CP_A2_ALT_1",
         "outcome": "skipped", "duration": 0.05,
         "setup": {"longrepr": "DRIFT-RECAPTCHA-V3:correlation_id=abc-1234"}},
    ]
}


@pytest.fixture
def fixture_dir(tmp_path: Path) -> Path:
    pw_dir = tmp_path / "playwright-report"
    pw_dir.mkdir()
    (pw_dir / "results.json").write_text(json.dumps(PLAYWRIGHT_FIXTURE))

    cy_dir = tmp_path / "cypress" / "cypress-results"
    cy_dir.mkdir(parents=True)
    (cy_dir / "results.json").write_text(json.dumps(CYPRESS_FIXTURE))

    se_dir = tmp_path / "selenium-report"
    se_dir.mkdir()
    (se_dir / "results.json").write_text(json.dumps(SELENIUM_FIXTURE))

    return tmp_path


@pytest.fixture
def run_consolidate(fixture_dir: Path) -> dict:
    """Run the tool against fixtures; return the parsed envelope."""
    out_dir = fixture_dir / "runs"
    rc = cr.main([
        "--env", "demo",
        "--env-url", "https://demo.bouracka.cz",
        "--run-id", "run-2026-05-10T12-00-00Z-abcdef0",
        "--pw", str(fixture_dir / "playwright-report" / "results.json"),
        "--cy", str(fixture_dir / "cypress" / "cypress-results" / "*.json"),
        "--se", str(fixture_dir / "selenium-report" / "results.json"),
        "--out-dir", str(out_dir),
        "--trigger", "manual",
    ])
    assert rc in (0, 1), f"main returned {rc} (expected 0 PASS-parity or 1 DIVERGENCE)"
    json_files = list(out_dir.glob("cross-framework-demo-*.json"))
    assert len(json_files) == 1, f"expected 1 JSON output, got {len(json_files)}"
    return json.loads(json_files[0].read_text())


# ──────────────────────────────────────────────────────────────────────────
# §1. Top-level envelope shape per schema §2.1
# ──────────────────────────────────────────────────────────────────────────

def test_envelope_has_all_required_top_level_fields(run_consolidate):
    env = run_consolidate
    required = {"schema_version", "run_id", "env", "started_at", "ended_at",
                "duration_ms", "frameworks", "results", "summary", "host",
                "reporter"}
    assert required <= set(env.keys()), f"missing: {required - set(env.keys())}"


def test_schema_version_pinned(run_consolidate):
    assert run_consolidate["schema_version"] == "1.0"


def test_run_id_format(run_consolidate):
    assert re.match(r"^run-\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z-[0-9a-f]{7}$",
                    run_consolidate["run_id"])


def test_env_in_enum(run_consolidate):
    assert run_consolidate["env"] in ("demo", "tst", "uat", "prod-readonly", "prod-writable")


def test_frameworks_sorted_dedup(run_consolidate):
    fws = run_consolidate["frameworks"]
    assert fws == sorted(set(fws)), f"frameworks not sorted/dedup: {fws}"
    assert set(fws) == {"playwright", "cypress", "selenium"}


def test_started_at_le_ended_at(run_consolidate):
    assert run_consolidate["started_at"] <= run_consolidate["ended_at"]


# ──────────────────────────────────────────────────────────────────────────
# §2. Per-TC results pivot per schema §2.2 + §3.2
# ──────────────────────────────────────────────────────────────────────────

def test_results_pivoted_to_per_tc(run_consolidate):
    """4 TCs × 3 frameworks → 4 result entries (not 12)."""
    assert len(run_consolidate["results"]) == 4


def test_each_result_has_required_keys(run_consolidate):
    required = {"tc_code", "verdicts", "parity_status", "duration_ms",
                "evidence", "covered_tt", "error_messages",
                "framework_specific_notes"}
    for r in run_consolidate["results"]:
        assert required <= set(r.keys()), \
            f"{r['tc_code']}: missing {required - set(r.keys())}"


def test_verdict_values_in_canonical_enum(run_consolidate):
    canon = {"pass", "fail", "skip-drift", "skip-other", "soft-pass",
             "error", "missing"}
    for r in run_consolidate["results"]:
        for fw, v in r["verdicts"].items():
            assert v in canon, f"{r['tc_code']}.{fw}: {v!r} not in {canon}"


# ──────────────────────────────────────────────────────────────────────────
# §3. parity_status computation per schema §3.4
# ──────────────────────────────────────────────────────────────────────────

def test_parity_agree_when_all_frameworks_pass(run_consolidate):
    by_tc = {r["tc_code"]: r for r in run_consolidate["results"]}
    # TC-CP-A1-MAIN-DEMO: all 3 fws PASS → agree
    assert by_tc["TC-CP-A1-MAIN-DEMO"]["parity_status"] == "agree"
    assert by_tc["TC-CP-A2-ALT-7"]["parity_status"] == "agree"


def test_parity_agree_for_soft_pass_consistency(run_consolidate):
    """Soft-pass collapses to pass for parity check (§3.5)."""
    by_tc = {r["tc_code"]: r for r in run_consolidate["results"]}
    # TC-CP-A2-ALT-9: all 3 fws PASS but soft-pass marker → still agree
    assert by_tc["TC-CP-A2-ALT-9"]["parity_status"] == "agree"


def test_parity_agree_for_skip_drift_consistency(run_consolidate):
    by_tc = {r["tc_code"]: r for r in run_consolidate["results"]}
    # TC-CP-A2-ALT-1: all 3 fws skip-drift → agree
    r1 = by_tc["TC-CP-A2-ALT-1"]
    assert r1["parity_status"] == "agree"
    assert all(v == "skip-drift" for v in r1["verdicts"].values()), \
        f"expected all skip-drift, got {r1['verdicts']}"


# ──────────────────────────────────────────────────────────────────────────
# §4. Soft-pass enforcement per schema §3.2 (soft_pass_reason required)
# ──────────────────────────────────────────────────────────────────────────

def test_soft_pass_marker_propagates(run_consolidate):
    by_tc = {r["tc_code"]: r for r in run_consolidate["results"]}
    r9 = by_tc["TC-CP-A2-ALT-9"]
    assert all(v == "soft-pass" for v in r9["verdicts"].values()), \
        f"ALT-9 should be all soft-pass, got {r9['verdicts']}"
    assert r9["soft_pass_reason"], \
        "soft_pass_reason must be set when verdict is soft-pass"


# ──────────────────────────────────────────────────────────────────────────
# §5. skip-drift vs skip-other distinction per schema §4.4
# ──────────────────────────────────────────────────────────────────────────

def test_drift_marker_classified_as_skip_drift(run_consolidate):
    by_tc = {r["tc_code"]: r for r in run_consolidate["results"]}
    r1 = by_tc["TC-CP-A2-ALT-1"]
    # All 3 fws have DRIFT-RECAPTCHA-V3 in skip reason → skip-drift
    for fw, v in r1["verdicts"].items():
        assert v == "skip-drift", f"{fw}: expected skip-drift, got {v!r}"


# ──────────────────────────────────────────────────────────────────────────
# §6. Summary computation per schema §3.6
# ──────────────────────────────────────────────────────────────────────────

def test_summary_counts(run_consolidate):
    s = run_consolidate["summary"]
    assert s["total_tcs"] == 4
    assert s["passed"] == 3            # MAIN-DEMO + ALT-7 + ALT-9 (soft-pass counts as pass)
    assert s["failed"] == 0
    assert s["skipped"] == 1           # ALT-1
    assert s["drift_skip_count"] == 1  # ALT-1
    assert s["soft_passed"] == 1       # ALT-9
    assert s["parity_pass_count"] == 4
    assert s["parity_divergence_count"] == 0


def test_pass_rate_computation(run_consolidate):
    s = run_consolidate["summary"]
    assert s["pass_rate_strict"] == 0.75            # 3/4
    assert s["pass_rate_drift_aware"] == 1.0        # (3+1)/4


# ──────────────────────────────────────────────────────────────────────────
# §7. Drift forensic synthesis per schema §2.5
# ──────────────────────────────────────────────────────────────────────────

def test_drift_forensic_populated(run_consolidate):
    df = run_consolidate.get("drift_forensic")
    assert df is not None
    assert df["active"] is True
    assert df["drift_type"] == "recaptcha-v3"
    assert "TC-CP-A2-ALT-1" in df["affected_tcs"]
    assert df["trigger_correlation"] == "abc-1234"


# ──────────────────────────────────────────────────────────────────────────
# §8. Host + reporter provenance per schema §2.4 + §2.6
# ──────────────────────────────────────────────────────────────────────────

def test_host_populated(run_consolidate):
    h = run_consolidate["host"]
    assert h["os"], "host.os must be non-empty"
    assert h["host"], "host.host must be non-empty"


def test_reporter_populated(run_consolidate):
    r = run_consolidate["reporter"]
    assert r["command"], "reporter.command must be non-empty"
    assert r["trigger"] in ("manual", "ci", "scheduled", "api")


# ──────────────────────────────────────────────────────────────────────────
# §9. Producer-side validation hook (schema §5.1) — this would have raised
#      AssertionError in main() if the envelope were noncompliant; the
#      fixture passing main() with rc∈{0,1} confirms validation succeeded.
# ──────────────────────────────────────────────────────────────────────────

def test_validate_envelope_does_not_raise(run_consolidate):
    """Re-run validate_envelope on the parsed JSON; should pass cleanly."""
    cr._validate_envelope(run_consolidate)


# ──────────────────────────────────────────────────────────────────────────
# §10. Markdown digest also written
# ──────────────────────────────────────────────────────────────────────────

def test_markdown_digest_written(fixture_dir, run_consolidate):
    md_files = list((fixture_dir / "runs").glob("cross-framework-demo-*.md"))
    assert len(md_files) == 1
    txt = md_files[0].read_text()
    assert "Bouračka demo" in txt
    assert "schema v1.0" in txt
    assert "TC-CP-A1-MAIN-DEMO" in txt
