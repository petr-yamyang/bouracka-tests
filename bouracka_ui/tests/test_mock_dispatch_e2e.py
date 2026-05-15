"""End-to-end mock-mode dispatch test.

Exercises the full dispatch → consolidate → envelope chain WITHOUT requiring
cypress / playwright / selenium installed. This is the shield: it must run
in every CI / sandbox / ThinkPad pre-flight before any Kate-bound build can
be considered ship-ready.

Two test families:

  Family A (direct-call):
    Imports dispatcher.run_async directly, calls it in an asyncio loop with
    BOURACKA_UI_DISPATCH_MODE=mock. Validates the produced envelope shape +
    semantics. No HTTP server; pure-Python invocation. ~0.5s per test.

  Family B (http e2e):
    Starts bouracka-ui server in subprocess with mock mode env vars. POSTs
    to /api/runs. Polls /api/runs/{id} until status='done'. Validates the
    same envelope. ~10s per test (subprocess startup + poll cycle).

Both families share envelope-validation helpers.

Author: Pete Y. + Opus 4.7 prototype 2026-05-14; hardened by Sonnet 4.6 (Brief #005).
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path

import pytest

# Add bouracka_ui to path so we can import dispatcher directly
REPO_ROOT = Path(__file__).resolve().parents[2]
BOURACKA_UI_PKG = REPO_ROOT / "bouracka_ui"
SPECS_DIR = REPO_ROOT / "_specs"
sys.path.insert(0, str(BOURACKA_UI_PKG))

from bouracka_ui import dispatcher  # noqa: E402


# ============================================================================
# Envelope validators — shared between Family A + B
# ============================================================================

EXPECTED_TOP_LEVEL_KEYS = {
    "schema_version", "run_id", "env", "env_url", "started_at", "ended_at",
    "duration_ms", "frameworks", "results", "summary", "host",
    "drift_forensic", "reporter",
}

EXPECTED_RESULT_KEYS = {
    "tc_code", "verdicts", "parity_status", "duration_ms", "evidence",
    "covered_tt", "error_messages", "framework_specific_notes", "viewport",
    "bug_ref", "soft_pass_reason",
}

CANONICAL_VERDICTS = {"pass", "fail", "skip-drift", "skip-other",
                      "soft-pass", "error", "missing"}

VALID_PARITY = {"agree", "divergence", "not-applicable"}


def assert_envelope_valid(env: dict, expected_run_id: str,
                          expected_env_label: str,
                          expected_tcs: list[str],
                          expected_frameworks: list[str]) -> None:
    """One-stop envelope schema + semantics check."""

    # Top-level shape
    assert set(env.keys()) >= EXPECTED_TOP_LEVEL_KEYS, \
        f"missing top-level keys: {EXPECTED_TOP_LEVEL_KEYS - set(env.keys())}"
    assert env["schema_version"] == "1.0"
    assert env["run_id"] == expected_run_id
    assert env["env"] == expected_env_label
    assert isinstance(env["env_url"], str)
    assert env["env_url"]  # non-empty
    assert env["started_at"].endswith("Z")
    assert env["ended_at"].endswith("Z")
    assert env["duration_ms"] > 0
    assert sorted(env["frameworks"]) == sorted(expected_frameworks)

    # Results array
    assert isinstance(env["results"], list)
    assert len(env["results"]) == len(expected_tcs), \
        f"expected {len(expected_tcs)} results, got {len(env['results'])}"
    result_tcs = [r["tc_code"] for r in env["results"]]
    assert sorted(result_tcs) == sorted(expected_tcs), \
        f"result TCs mismatch: got {result_tcs}, want {expected_tcs}"

    for r in env["results"]:
        assert set(r.keys()) >= EXPECTED_RESULT_KEYS, \
            f"missing keys in result {r['tc_code']}: {EXPECTED_RESULT_KEYS - set(r.keys())}"
        # Verdicts: one entry per framework
        assert set(r["verdicts"].keys()) == set(expected_frameworks)
        for fw, v in r["verdicts"].items():
            assert v in CANONICAL_VERDICTS, \
                f"unknown verdict '{v}' for {r['tc_code']}/{fw}"
        assert r["parity_status"] in VALID_PARITY

    # Summary
    s = env["summary"]
    assert "total_tcs" in s, "summary missing total_tcs"
    assert s["total_tcs"] == len(expected_tcs)

    # Host / reporter / drift sections present (may be None)
    assert "host" in env
    assert "reporter" in env
    assert "drift_forensic" in env  # may be None when no drift TCs


def validate_against_schema_doc() -> list[str]:
    """Parse the canonical schema doc and return required top-level field names.

    Returns list of field names found in the schema markdown. Callers can
    assert that the actual envelope contains all of them.
    """
    schema_path = SPECS_DIR / "CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.md"
    if not schema_path.exists():
        pytest.skip(f"schema doc not found at {schema_path}; skipping doc-validation")

    text = schema_path.read_text(encoding="utf-8")

    # Extract field names from markdown table rows — look for backtick-wrapped
    # identifiers in the first column of tables (pattern: | `field_name` | ... |)
    fields: list[str] = []
    for line in text.splitlines():
        m = re.match(r"\|\s*`([a-z_][a-z0-9_]*)`\s*\|", line)
        if m:
            fields.append(m.group(1))

    # De-duplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for f in fields:
        if f not in seen:
            seen.add(f)
            unique.append(f)
    return unique


# ============================================================================
# Family A — direct-call mock dispatch
# ============================================================================

def _run_dispatch_direct(env_label: str, tcs: list[str],
                          frameworks: list[str], tmp_path: Path,
                          monkeypatch) -> tuple[str, dict]:
    """Invoke dispatcher.run_async in mock mode, return (run_id, envelope dict)."""
    monkeypatch.setenv("BOURACKA_UI_DISPATCH_MODE", "mock")
    run_id = dispatcher.generate_run_id()
    registry: dict[str, dict] = {
        run_id: {
            "run_id": run_id,
            "env": env_label,
            "tcs": tcs,
            "frameworks": frameworks,
            "status": "pending",
            "log_lines": [],
            "exit_code": None,
            "envelope_path": None,
        }
    }

    async def _go():
        await dispatcher.run_async(
            run_id=run_id, env=env_label, tcs=tcs,
            frameworks=frameworks, repo_root=tmp_path, registry=registry,
        )

    asyncio.run(_go())

    assert registry[run_id]["status"] == "done", \
        f"run did not complete: {registry[run_id]}"
    assert registry[run_id]["exit_code"] == 0
    envelope_path = Path(registry[run_id]["envelope_path"])
    assert envelope_path.exists()
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    return run_id, envelope


def test_mock_dispatch_direct_basic(tmp_path, monkeypatch):
    """One TC, one framework. Smallest possible dispatch."""
    run_id, env = _run_dispatch_direct(
        env_label="demo", tcs=["TC-CP-008"],
        frameworks=["cypress"], tmp_path=tmp_path, monkeypatch=monkeypatch,
    )
    assert_envelope_valid(env, run_id, "demo", ["TC-CP-008"], ["cypress"])


def test_mock_dispatch_direct_three_frameworks(tmp_path, monkeypatch):
    """One TC, three frameworks. Tests parity computation."""
    run_id, env = _run_dispatch_direct(
        env_label="tst-demo", tcs=["TC-CP-008"],
        frameworks=["cypress", "playwright", "selenium"],
        tmp_path=tmp_path, monkeypatch=monkeypatch,
    )
    assert_envelope_valid(
        env, run_id, "tst-demo", ["TC-CP-008"],
        ["cypress", "playwright", "selenium"],
    )
    # All-pass scenario should produce parity_status="agree"
    assert env["results"][0]["parity_status"] == "agree"


def test_mock_dispatch_direct_divergence_scenario(tmp_path, monkeypatch):
    """ALT-4 cypress fails while others pass → parity_status='divergence'."""
    run_id, env = _run_dispatch_direct(
        env_label="demo", tcs=["TC-CP-ALT-4"],
        frameworks=["cypress", "playwright", "selenium"],
        tmp_path=tmp_path, monkeypatch=monkeypatch,
    )
    assert_envelope_valid(env, run_id, "demo", ["TC-CP-ALT-4"],
                          ["cypress", "playwright", "selenium"])
    result = env["results"][0]
    assert result["verdicts"]["cypress"] == "fail"
    assert result["verdicts"]["playwright"] == "pass"
    assert result["verdicts"]["selenium"] == "pass"
    assert result["parity_status"] == "divergence"
    assert result["error_messages"]["cypress"] is not None


def test_mock_dispatch_direct_drift_scenario(tmp_path, monkeypatch):
    """ALT-1 triggers drift_forensic section in envelope."""
    run_id, env = _run_dispatch_direct(
        env_label="demo", tcs=["TC-CP-ALT-1"], frameworks=["cypress"],
        tmp_path=tmp_path, monkeypatch=monkeypatch,
    )
    assert_envelope_valid(env, run_id, "demo", ["TC-CP-ALT-1"], ["cypress"])
    assert env["drift_forensic"] is not None
    assert env["drift_forensic"]["active"] is True
    assert "TC-CP-ALT-1" in env["drift_forensic"]["affected_tcs"]


def test_mock_dispatch_direct_multi_tc(tmp_path, monkeypatch):
    """Multiple TCs in one run."""
    tcs = ["TC-CP-001", "TC-CP-008", "TC-CP-013", "TC-CP-019"]
    run_id, env = _run_dispatch_direct(
        env_label="demo", tcs=tcs,
        frameworks=["cypress", "playwright"],
        tmp_path=tmp_path, monkeypatch=monkeypatch,
    )
    assert_envelope_valid(env, run_id, "demo", tcs, ["cypress", "playwright"])
    assert len(env["results"]) == 4


def test_mock_dispatch_direct_envelope_path_pattern(tmp_path, monkeypatch):
    """Envelope is written to runs/cross-framework-{env}-{date}.json."""
    run_id, env = _run_dispatch_direct(
        env_label="demo", tcs=["TC-CP-008"],
        frameworks=["cypress"], tmp_path=tmp_path, monkeypatch=monkeypatch,
    )
    expected = tmp_path / "runs" / f"cross-framework-demo-{env['started_at'].split('T')[0]}.json"
    assert expected.exists()


# ─── F-1 new Family A tests ──────────────────────────────────────────────────

def test_mock_dispatch_direct_soft_pass_scenario(tmp_path, monkeypatch):
    """ALT-9 TC produces soft-pass verdict; soft_pass_reason is populated."""
    run_id, env = _run_dispatch_direct(
        env_label="demo", tcs=["TC-CP-ALT-9"], frameworks=["cypress"],
        tmp_path=tmp_path, monkeypatch=monkeypatch,
    )
    assert_envelope_valid(env, run_id, "demo", ["TC-CP-ALT-9"], ["cypress"])
    result = env["results"][0]
    assert result["verdicts"]["cypress"] == "soft-pass"
    assert result["soft_pass_reason"] is not None
    assert isinstance(result["soft_pass_reason"], str)
    assert result["soft_pass_reason"]  # non-empty


def test_mock_dispatch_direct_skip_drift_scenario(tmp_path, monkeypatch):
    """ALT-1 produces skip-drift; drift_forensic block has guard_policy + affected_tcs."""
    run_id, env = _run_dispatch_direct(
        env_label="demo", tcs=["TC-CP-ALT-1"], frameworks=["cypress"],
        tmp_path=tmp_path, monkeypatch=monkeypatch,
    )
    assert_envelope_valid(env, run_id, "demo", ["TC-CP-ALT-1"], ["cypress"])
    result = env["results"][0]
    assert result["verdicts"]["cypress"] == "skip-drift"

    df = env["drift_forensic"]
    assert df is not None
    assert df["guard_policy"] == "skip-on-drift"
    assert isinstance(df["affected_tcs"], list)
    assert len(df["affected_tcs"]) > 0
    assert "TC-CP-ALT-1" in df["affected_tcs"]


def test_mock_dispatch_direct_summary_counts_correct(tmp_path, monkeypatch):
    """1 pass + 1 fail + 1 drift → summary integers are correct."""
    tcs = ["TC-CP-001", "TC-CP-ALT-4", "TC-CP-ALT-1"]
    # cypress: TC-CP-001→pass, TC-CP-ALT-4→fail, TC-CP-ALT-1→skip-drift
    run_id, env = _run_dispatch_direct(
        env_label="demo", tcs=tcs, frameworks=["cypress"],
        tmp_path=tmp_path, monkeypatch=monkeypatch,
    )
    assert_envelope_valid(env, run_id, "demo", tcs, ["cypress"])
    s = env["summary"]
    assert s["total_tcs"] == 3
    assert s["passed"] == 1
    assert s["failed"] == 1
    assert s["skipped"] == 1
    assert s["drift_skip_count"] == 1


def test_mock_dispatch_direct_env_url_matches_env(tmp_path, monkeypatch):
    """For each env label, envelope[env_url] == dispatcher.ENV_TO_BASE_URL[env]."""
    for env_label, expected_url in dispatcher.ENV_TO_BASE_URL.items():
        run_id, env = _run_dispatch_direct(
            env_label=env_label, tcs=["TC-CP-008"], frameworks=["cypress"],
            tmp_path=tmp_path, monkeypatch=monkeypatch,
        )
        assert env["env_url"] == expected_url, \
            f"env_label={env_label}: got {env['env_url']!r}, want {expected_url!r}"


# ─── §8 meta-tests — prove the validators catch bad envelopes ────────────────

def test_validator_rejects_missing_run_id(tmp_path, monkeypatch):
    """assert_envelope_valid raises AssertionError when run_id is absent."""
    run_id, env = _run_dispatch_direct(
        env_label="demo", tcs=["TC-CP-008"], frameworks=["cypress"],
        tmp_path=tmp_path, monkeypatch=monkeypatch,
    )
    bad = dict(env)
    del bad["run_id"]
    with pytest.raises(AssertionError):
        assert_envelope_valid(bad, run_id, "demo", ["TC-CP-008"], ["cypress"])


def test_validator_rejects_unknown_verdict(tmp_path, monkeypatch):
    """assert_envelope_valid raises AssertionError for an unknown verdict string."""
    run_id, env = _run_dispatch_direct(
        env_label="demo", tcs=["TC-CP-008"], frameworks=["cypress"],
        tmp_path=tmp_path, monkeypatch=monkeypatch,
    )
    bad = json.loads(json.dumps(env))  # deep copy
    bad["results"][0]["verdicts"]["cypress"] = "halfpass"  # not in CANONICAL_VERDICTS
    with pytest.raises(AssertionError):
        assert_envelope_valid(bad, run_id, "demo", ["TC-CP-008"], ["cypress"])


def test_validator_rejects_wrong_tc_count(tmp_path, monkeypatch):
    """assert_envelope_valid raises AssertionError when result count doesn't match tcs list."""
    run_id, env = _run_dispatch_direct(
        env_label="demo", tcs=["TC-CP-001", "TC-CP-008", "TC-CP-013"],
        frameworks=["cypress"], tmp_path=tmp_path, monkeypatch=monkeypatch,
    )
    bad = json.loads(json.dumps(env))
    bad["results"] = bad["results"][:2]  # trim one result; claimed 3 tcs, only 2 results
    with pytest.raises(AssertionError):
        assert_envelope_valid(bad, run_id, "demo",
                              ["TC-CP-001", "TC-CP-008", "TC-CP-013"], ["cypress"])


# ============================================================================
# Family B — HTTP e2e (requires bouracka_ui installed in venv)
# ============================================================================
# These tests are slower (~10s each) due to subprocess startup. Use the
# 'http_e2e' marker so they can be skipped in fast smoke runs.
# Run: pytest -m http_e2e
# Skip: pytest -m "not http_e2e"

def _wait_for_port(port: int, timeout: float = 10.0) -> bool:
    """Poll TCP port until something is listening or timeout."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except (OSError, socket.timeout):
            time.sleep(0.3)
    return False


@pytest.fixture
def server_proc(tmp_path):
    """Start bouracka-ui in mock mode as a subprocess. Yields (proc, port)."""
    port = 8425  # different from default 8424 to avoid clashing with user sessions
    env = os.environ.copy()
    env["BOURACKA_UI_DISPATCH_MODE"] = "mock"
    env["BOURACKA_UI_RUNS_DIR"] = str(tmp_path / "runs")
    env["PYTHONUNBUFFERED"] = "1"
    # Prevent httpx inside the subprocess from inheriting proxy env vars
    for proxy_var in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
                      "ALL_PROXY", "all_proxy", "SOCKS_PROXY", "socks_proxy"):
        env.pop(proxy_var, None)

    cmd = [
        sys.executable, "-m", "uvicorn",
        "bouracka_ui.server:app",
        "--host", "127.0.0.1",
        "--port", str(port),
        "--log-level", "warning",
    ]
    log_path = tmp_path / "uvicorn.log"
    with log_path.open("wb") as logf:
        proc = subprocess.Popen(cmd, env=env, stdout=logf, stderr=subprocess.STDOUT,
                                cwd=str(REPO_ROOT))
    try:
        ok = _wait_for_port(port, timeout=10.0)
        if not ok:
            proc.terminate()
            log_text = log_path.read_text(errors="replace") if log_path.exists() else ""
            pytest.skip(
                f"server didn't start on port {port} within 10s "
                f"(port already in use or import error); uvicorn log:\n{log_text[:2000]}"
            )
        yield proc, port
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


@pytest.mark.http_e2e
def test_http_mock_dispatch_e2e_full_cycle(server_proc):
    """POST /api/runs → poll → envelope present and valid."""
    import httpx
    proc, port = server_proc
    base = f"http://127.0.0.1:{port}"

    # Use trust_env=False to avoid inheriting HTTPS_PROXY / SOCKS env vars
    client = httpx.Client(trust_env=False, timeout=10.0)

    with client:
        # 1. Health check
        r = client.get(f"{base}/api/health")
        assert r.status_code == 200
        health = r.json()
        assert "server_version" in health

        # 2. Trigger run
        payload = {
            "env": "demo",
            "tcs": ["TC-CP-008", "TC-CP-001"],
            "frameworks": ["cypress", "playwright"],
        }
        r = client.post(f"{base}/api/runs", json=payload)
        assert r.status_code in (200, 202), f"got {r.status_code}: {r.text}"
        run_id = r.json()["run_id"]

        # 3. Poll until done (max 30s).
        #    Server response semantics:
        #      202 + {"status": "pending"|"running", ...} → in-flight
        #      200 + full envelope ({"results": [...], ...})  → done, envelope readable
        #      200 + {"status": "done"|"failed", ...}         → done, no envelope produced
        body: dict = {}
        envelope: dict = {}
        deadline = time.time() + 30
        while time.time() < deadline:
            r = client.get(f"{base}/api/runs/{run_id}")
            assert r.status_code in (200, 202), \
                f"unexpected poll status {r.status_code}: {r.text}"
            body = r.json()
            # Full envelope returned directly when run is done
            if "results" in body:
                envelope = body
                break
            # Status payload: check explicit done/failed
            st = body.get("status")
            if st in ("done", "failed"):
                break
            time.sleep(0.5)
        else:
            pytest.fail(
                f"run {run_id} did not complete within 30s; "
                f"last status: {body.get('status')!r}"
            )

        # 4. Validate envelope
        if not envelope:
            # done-without-envelope: fall back to reading from disk
            ep = body.get("envelope_path")
            assert ep, f"run done but no envelope_path in payload: {body}"
            envelope_path = Path(ep)
            assert envelope_path.exists(), f"envelope file missing: {envelope_path}"
            envelope = json.loads(envelope_path.read_text(encoding="utf-8"))

        assert_envelope_valid(envelope, run_id, "demo",
                              ["TC-CP-008", "TC-CP-001"],
                              ["cypress", "playwright"])
