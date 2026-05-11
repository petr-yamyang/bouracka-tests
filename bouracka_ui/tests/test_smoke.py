"""Smoke tests for bouracka-ui Phase 1 (Runnable Mock).

Verifies all 9 endpoints respond and return shapes consistent with the API
contract in `_config/BOURACKA-UI-DESIGN-v0.1-2026-05-10.md` §3.1.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Make the package importable from the repo even when not pip-installed
PKG_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PKG_ROOT))

from bouracka_ui.server import app  # noqa: E402

client = TestClient(app)


# ──────────────────────────────────────────────────────────────────────────
# §1. Index + static
# ──────────────────────────────────────────────────────────────────────────

def test_index_loads():
    r = client.get("/")
    assert r.status_code == 200
    assert "Bouračka UI" in r.text


def test_static_css_loads():
    r = client.get("/static/style.css")
    assert r.status_code == 200
    assert "design-tokens" in r.text


def test_static_design_tokens_loads():
    r = client.get("/static/design-tokens.css")
    assert r.status_code == 200
    assert "--c-primary" in r.text


# ──────────────────────────────────────────────────────────────────────────
# §2. /api/health
# ──────────────────────────────────────────────────────────────────────────

def test_health_returns_versions():
    r = client.get("/api/health")
    assert r.status_code == 200
    j = r.json()
    assert j["schema_version"] == "1.0"
    assert j["server_version"] == "0.1.0"
    assert "tools" in j


# ──────────────────────────────────────────────────────────────────────────
# §3. /api/envs
# ──────────────────────────────────────────────────────────────────────────

def test_envs_returns_3_envs():
    r = client.get("/api/envs")
    assert r.status_code == 200
    j = r.json()
    assert len(j) >= 3
    codes = {e["code"] for e in j}
    assert {"ENV-PUB", "ENV-TST", "ENV-DMO"} <= codes
    schema_envs = {e["schema_env"] for e in j}
    assert schema_envs <= {"demo", "tst", "uat", "prod-readonly", "prod-writable"}


# ──────────────────────────────────────────────────────────────────────────
# §4. /api/tcs
# ──────────────────────────────────────────────────────────────────────────

def test_tcs_returns_list():
    r = client.get("/api/tcs")
    assert r.status_code == 200
    j = r.json()
    assert len(j) > 0
    for tc in j:
        assert "code" in tc
        assert tc["code"].startswith("TC-")


def test_tcs_filtered_by_env_demo():
    r = client.get("/api/tcs?env=demo")
    assert r.status_code == 200
    j = r.json()
    # All returned TCs should be applies_to_demo
    for tc in j:
        if tc.get("applies_to_demo") is False:
            pytest.fail(f"{tc['code']} should not appear for env=demo")


def test_tcs_filtered_by_framework():
    r = client.get("/api/tcs?framework=cypress")
    assert r.status_code == 200
    j = r.json()
    for tc in j:
        targets = (tc.get("framework_targets") or "").lower()
        assert "cypress" in targets, f"{tc['code']}: framework_targets={targets}"


# ──────────────────────────────────────────────────────────────────────────
# §5. /api/runs POST + GET (mock dispatch happens async)
# ──────────────────────────────────────────────────────────────────────────

def test_post_run_returns_run_id():
    r = client.post("/api/runs", json={
        "env": "demo",
        "tcs": ["TC-CP-A1-MAIN-DEMO"],
        "frameworks": ["all"],
    })
    assert r.status_code == 200
    j = r.json()
    assert "run_id" in j
    import re
    # BUG-BUI-001: ':' in time portion → use '-' (Windows NTFS filename safety;
    # see dispatcher.py RUN_ID_RE + generate_run_id()).
    assert re.match(r"^run-\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z-[0-9a-f]{7}$", j["run_id"])


def test_post_run_rejects_missing_env():
    r = client.post("/api/runs", json={"tcs": ["TC-CP-A1-MAIN-DEMO"]})
    assert r.status_code == 422


def test_post_run_rejects_empty_tcs():
    r = client.post("/api/runs", json={"env": "demo", "tcs": []})
    assert r.status_code == 422


def test_get_runs_list_responds():
    r = client.get("/api/runs?limit=10")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_runs_unknown_id_404():
    r = client.get("/api/runs/run-2026-01-01T00-00-00Z-abcdef0")
    assert r.status_code == 404


# ──────────────────────────────────────────────────────────────────────────
# §5.1 BUG-BUI-002 — GET /api/runs/{rid} status-aware semantics (202/200/404)
# ──────────────────────────────────────────────────────────────────────────

def test_get_run_in_flight_returns_202():
    """Run in registry but envelope_path not set → 202 with status payload."""
    import bouracka_ui.server as srv
    rid = "run-2026-05-10T22-30-00Z-deadbee"
    srv._RUN_REGISTRY[rid] = {
        "run_id": rid, "env": "demo", "tcs": ["TC-CP-A1-MAIN-DEMO"],
        "frameworks": ["cypress"], "status": "running",
        "started_at": "2026-05-10T22:30:00Z",
        "log_lines": ["[bouracka-ui] starting run", "=== cypress ==="],
        "exit_code": None, "envelope_path": None,
    }
    try:
        r = client.get(f"/api/runs/{rid}")
        assert r.status_code == 202, r.text
        j = r.json()
        assert j["run_id"] == rid
        assert j["status"] == "running"
        assert j["envelope_ready"] is False
        assert j["log_tail"] == ["[bouracka-ui] starting run", "=== cypress ==="]
        assert j["env"] == "demo"
        assert j["frameworks"] == ["cypress"]
    finally:
        srv._RUN_REGISTRY.pop(rid, None)


def test_get_run_done_no_envelope_returns_200_status_payload():
    """Run finished but no envelope (dispatch failure) → 200 with status payload, not full envelope."""
    import bouracka_ui.server as srv
    rid = "run-2026-05-10T22-31-00Z-faded00"
    srv._RUN_REGISTRY[rid] = {
        "run_id": rid, "env": "demo", "tcs": ["TC-CP-A1-MAIN-DEMO"],
        "frameworks": ["cypress"], "status": "done",
        "started_at": "2026-05-10T22:31:00Z",
        "log_lines": ["[cypress] tooling not found"],
        "exit_code": 127, "envelope_path": None,
    }
    try:
        r = client.get(f"/api/runs/{rid}")
        assert r.status_code == 200, r.text
        j = r.json()
        # Status payload, not full envelope (no 'results' key)
        assert j["status"] == "done"
        assert "results" not in j
        assert j["envelope_ready"] is False
        assert j["exit_code"] == 127
    finally:
        srv._RUN_REGISTRY.pop(rid, None)


def test_resolve_repo_root_env_var_wins(tmp_path, monkeypatch):
    """BUG-BUI-004: BOURACKA_UI_REPO_ROOT env var is an explicit override that
    always wins, regardless of CWD or __file__ heuristics."""
    import bouracka_ui.server as srv
    monkeypatch.setenv("BOURACKA_UI_REPO_ROOT", str(tmp_path))
    result = srv._resolve_repo_root()
    assert result == tmp_path


def test_resolve_repo_root_finds_marker_from_cwd(tmp_path, monkeypatch):
    """BUG-BUI-004: with no env override, _resolve_repo_root walks up from CWD
    looking for the tools/consolidate_results.py marker. Critical for
    wheel-install scenarios where __file__ lives in .venv/Lib/site-packages/."""
    import bouracka_ui.server as srv
    # Build a fake repo with the canonical marker
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "consolidate_results.py").write_text("# fake")
    monkeypatch.delenv("BOURACKA_UI_REPO_ROOT", raising=False)
    monkeypatch.chdir(tmp_path)
    result = srv._resolve_repo_root()
    assert result == tmp_path


def test_resolve_repo_root_finds_workbook_marker(tmp_path, monkeypatch):
    """BUG-BUI-004: BOURACKA-TESTPLAN-*.xlsx in CWD also counts as a marker."""
    import bouracka_ui.server as srv
    (tmp_path / "BOURACKA-TESTPLAN-v0.4.2.xlsx").write_text("fake")
    monkeypatch.delenv("BOURACKA_UI_REPO_ROOT", raising=False)
    monkeypatch.chdir(tmp_path)
    result = srv._resolve_repo_root()
    assert result == tmp_path


def test_get_run_done_with_envelope_returns_200_full(tmp_path, monkeypatch):
    """Run completed with envelope on disk → 200 with full v0.1 envelope (has 'results')."""
    import bouracka_ui.server as srv
    rid = "run-2026-05-10T22-32-00Z-c0ffee0"
    envelope = {
        "schema_version": "1.0", "run_id": rid, "env": "demo",
        "env_url": "https://demo.bouracka.cz",
        "started_at": "2026-05-10T22:32:00Z", "ended_at": "2026-05-10T22:32:30Z",
        "duration_ms": 30000, "frameworks": ["cypress"],
        "results": [{"tc_code": "TC-CP-A1-MAIN-DEMO",
                     "verdicts": {"cypress": "pass"},
                     "parity_status": "not-applicable",
                     "duration_ms": {"cypress": 1234},
                     "evidence": {"cypress": {"trace_ref": None,
                                              "screenshot_ref": None,
                                              "video_ref": None}},
                     "covered_tt": [], "error_messages": {"cypress": None},
                     "framework_specific_notes": {"cypress": ""},
                     "viewport": "375x667", "bug_ref": None,
                     "soft_pass_reason": None}],
        "summary": {"total_tcs": 1, "passed": 1, "failed": 0, "skipped": 0,
                    "soft_passed": 0, "drift_skip_count": 0,
                    "parity_pass_count": 0, "parity_divergence_count": 0,
                    "pass_rate_strict": 1.0, "pass_rate_drift_aware": 1.0},
        "host": {"os": "test", "host": "smoke", "git_commit": None,
                 "git_branch": None, "tool_versions": None},
        "drift_forensic": None,
        "reporter": {"command": "smoke", "trigger": "manual",
                     "ci_run_id": None, "operator": "test"},
    }
    ep = tmp_path / "cross-framework-demo-2026-05-10.json"
    ep.write_text(__import__("json").dumps(envelope), encoding="utf-8")
    srv._RUN_REGISTRY[rid] = {
        "run_id": rid, "env": "demo", "tcs": ["TC-CP-A1-MAIN-DEMO"],
        "frameworks": ["cypress"], "status": "done",
        "started_at": "2026-05-10T22:32:00Z",
        "log_lines": ["[bouracka-ui] DONE"], "exit_code": 0,
        "envelope_path": str(ep), "summary": envelope["summary"],
    }
    try:
        r = client.get(f"/api/runs/{rid}")
        assert r.status_code == 200, r.text
        j = r.json()
        assert "results" in j  # full envelope, not status payload
        assert j["run_id"] == rid
        assert j["summary"]["passed"] == 1
    finally:
        srv._RUN_REGISTRY.pop(rid, None)


# ──────────────────────────────────────────────────────────────────────────
# §6. /api/bugs
# ──────────────────────────────────────────────────────────────────────────

def test_bugs_list_returns_array():
    r = client.get("/api/bugs")
    assert r.status_code == 200
    j = r.json()
    assert isinstance(j, list)


def test_bugs_filtered_by_status():
    r = client.get("/api/bugs?status=open")
    assert r.status_code == 200
    j = r.json()
    for b in j:
        assert b["status"] == "open"


def test_post_bug_appends_or_mocks():
    """POST /api/bugs should append (or mock) a new bug."""
    r = client.post("/api/bugs", json={
        "name_en": "Smoke test bug — ignore",
        "severity": "C",
        "env_where_present": "ENV-DMO",
    })
    # Either 200 (appended OK) or 409 (workbook locked) — both acceptable in smoke
    assert r.status_code in (200, 201, 409)
    if r.status_code in (200, 201):
        j = r.json()
        assert "code" in j
        assert j["code"].startswith("BUG-")


def test_post_bug_rejects_missing_required():
    r = client.post("/api/bugs", json={"severity": "B"})
    assert r.status_code == 422


# ──────────────────────────────────────────────────────────────────────────
# §7. Trace bundle export + import + diagnostics (HP Elite air-gap path)
# ──────────────────────────────────────────────────────────────────────────

import io
import zipfile

import pytest


@pytest.fixture
def sample_run_envelope(tmp_path, monkeypatch):
    """Drop a synthetic envelope into runs/ and point server.RUNS_DIR to it."""
    import bouracka_ui.server as srv
    monkeypatch.setattr(srv, "RUNS_DIR", tmp_path)
    rid = "run-2026-05-10T15-00-00Z-abcdef0"
    envelope = {
        "schema_version": "1.0",
        "run_id": rid,
        "env": "demo",
        "env_url": "https://demo.bouracka.cz",
        "started_at": "2026-05-10T15:00:00Z",
        "ended_at":   "2026-05-10T15:02:14Z",
        "duration_ms": 134000,
        "frameworks": ["cypress", "playwright", "selenium"],
        "results": [
            {"tc_code": "TC-CP-A1-MAIN-DEMO",
             "verdicts": {"cypress": "pass", "playwright": "pass", "selenium": "pass"},
             "parity_status": "agree",
             "duration_ms": {"cypress": 1567, "playwright": 1234, "selenium": 1180},
             "evidence": {"cypress": {"trace_ref": None, "screenshot_ref": None, "video_ref": None},
                          "playwright": {"trace_ref": None, "screenshot_ref": None, "video_ref": None},
                          "selenium": {"trace_ref": None, "screenshot_ref": None, "video_ref": None}},
             "covered_tt": [], "error_messages": {"cypress": None, "playwright": None, "selenium": None},
             "framework_specific_notes": {"cypress": "", "playwright": "", "selenium": ""},
             "viewport": "375x667", "bug_ref": None, "soft_pass_reason": None},
        ],
        "summary": {"total_tcs": 1, "passed": 1, "failed": 0, "skipped": 0,
                    "soft_passed": 0, "drift_skip_count": 0,
                    "parity_pass_count": 1, "parity_divergence_count": 0,
                    "pass_rate_strict": 1.0, "pass_rate_drift_aware": 1.0},
        "host": {"os": "test", "host": "smoke", "git_commit": None,
                 "git_branch": None, "tool_versions": None},
        "drift_forensic": None,
        "reporter": {"command": "smoke", "trigger": "manual",
                     "ci_run_id": None, "operator": "test"},
    }
    p = tmp_path / "cross-framework-demo-2026-05-10.json"
    p.write_text(__import__("json").dumps(envelope), encoding="utf-8")
    return rid, envelope, p


def test_export_bundle_returns_zip(sample_run_envelope):
    rid, envelope, _ = sample_run_envelope
    r = client.get(f"/api/runs/{rid}/bundle?full=false&workbook=false")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/zip"
    assert f'trace-bundle-{rid}.zip' in r.headers["content-disposition"]

    # Validate ZIP contents
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    names = set(zf.namelist())
    assert "manifest.json" in names
    assert "envelope.json" in names
    assert "README.md" in names
    assert "server-log.txt" in names
    assert "system/health.json" in names
    assert "repro.sh" in names

    # Manifest sanity
    import json as _json
    manifest = _json.loads(zf.read("manifest.json"))
    assert manifest["bundle_format_version"] == "1.0"
    assert manifest["run_id"] == rid

    # Envelope round-trip
    env2 = _json.loads(zf.read("envelope.json"))
    assert env2["run_id"] == rid
    assert env2["env"] == "demo"


def test_import_bundle_round_trip(sample_run_envelope, tmp_path, monkeypatch):
    """Export a bundle, then import it (after wiping runs/) — verify it appears."""
    rid, envelope, src_path = sample_run_envelope

    # 1. Export
    r = client.get(f"/api/runs/{rid}/bundle?full=false&workbook=false")
    assert r.status_code == 200
    bundle_bytes = r.content

    # 2. Wipe the original envelope from runs/ to simulate import on a fresh machine
    src_path.unlink()
    # /api/runs/{rid} should now 404
    assert client.get(f"/api/runs/{rid}").status_code == 404

    # 3. Import
    r = client.post(
        "/api/bundles/import",
        files={"file": ("trace-bundle.zip", bundle_bytes, "application/zip")},
    )
    assert r.status_code == 200, r.text
    info = r.json()
    assert info["run_id"] == rid
    assert info["env"] == "demo"

    # 4. /api/runs/{rid} should now resolve again
    r = client.get(f"/api/runs/{rid}")
    assert r.status_code == 200
    j = r.json()
    assert j["run_id"] == rid


def test_import_bundle_rejects_non_zip():
    r = client.post(
        "/api/bundles/import",
        files={"file": ("not-a-zip.txt", b"hello world", "text/plain")},
    )
    assert r.status_code == 422


def test_import_bundle_rejects_zip_without_manifest():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("foo.txt", "no manifest here")
    r = client.post(
        "/api/bundles/import",
        files={"file": ("bad.zip", buf.getvalue(), "application/zip")},
    )
    assert r.status_code == 422


def test_diagnostics_snapshot():
    r = client.get("/api/diagnostics/snapshot")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/zip"
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    names = set(zf.namelist())
    assert "manifest.json" in names
    assert "health.json" in names
    assert "system/system.json" in names
    assert "system/tool-versions.txt" in names
    assert "README.md" in names
    import json as _json
    meta = _json.loads(zf.read("manifest.json"))
    assert meta["kind"] == "bouracka-ui-diagnostics-snapshot"
