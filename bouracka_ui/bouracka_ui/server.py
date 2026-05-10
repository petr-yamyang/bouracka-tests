"""FastAPI server for bouracka-ui.

All endpoints stubbed with synthetic data at v0.1 (Phase 1 — Runnable Mock).
Phase 2 swaps in real workbook reads via workbook_io.py;
Phase 3 swaps in real subprocess dispatch via dispatcher.py.

Reference: _config/BOURACKA-UI-DESIGN-v0.1-2026-05-10.md §3.1
"""
from __future__ import annotations

import asyncio
import datetime as _dt
import json
import os
import shutil
import sys
import time
import uuid
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse

from . import __schema_version__, __version__
from . import workbook_io, dispatcher, trace_bundle

# ──────────────────────────────────────────────────────────────────────────
# Configuration — overridable via environment variables for CLI flag passthrough
# ──────────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(os.environ.get(
    "BOURACKA_UI_REPO_ROOT",
    str(Path(__file__).resolve().parents[3])  # .../bouracka-tests/
))
WORKBOOK_PATH = Path(os.environ.get(
    "BOURACKA_UI_WORKBOOK",
    str(REPO_ROOT / "BOURACKA-TESTPLAN-v0.4.2.xlsx")
))
RUNS_DIR = Path(os.environ.get(
    "BOURACKA_UI_RUNS_DIR",
    str(REPO_ROOT / "runs")
))
STATIC_DIR = Path(__file__).resolve().parent / "static"

# In-memory run-state registry (run_id → dict). Replaced by sqlite/file cache at v0.2.
_RUN_REGISTRY: dict[str, dict] = {}

# Rolling server log capture (for diagnostics snapshots). Bounded ring buffer.
_SERVER_LOG: list[str] = []
_SERVER_LOG_MAX = 5000


def _server_log(msg: str) -> None:
    """Append to bounded server log ring + stderr."""
    ts = _dt.datetime.now(_dt.timezone.utc).strftime("%H:%M:%S")
    line = f"{ts} {msg}"
    _SERVER_LOG.append(line)
    if len(_SERVER_LOG) > _SERVER_LOG_MAX:
        del _SERVER_LOG[: len(_SERVER_LOG) - _SERVER_LOG_MAX]
    print(f"[server] {line}", file=sys.stderr, flush=True)

# ──────────────────────────────────────────────────────────────────────────
# App
# ──────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="bouracka-ui",
    version=__version__,
    description="Local presentation-layer UI for Bouračka test suite",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:*", "http://127.0.0.1:*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────────────────────────────────
# Static + index
# ──────────────────────────────────────────────────────────────────────────

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def index():
    """Serve the SPA shell."""
    idx = STATIC_DIR / "index.html"
    if not idx.exists():
        raise HTTPException(500, "index.html not found in package static/")
    return FileResponse(str(idx))


# ──────────────────────────────────────────────────────────────────────────
# §3.1 endpoint 1 — health
# ──────────────────────────────────────────────────────────────────────────

def _health_dict() -> dict:
    """Build the health snapshot dict (shared by /api/health + diagnostics)."""
    return {
        "schema_version": __schema_version__,
        "server_version": __version__,
        "workbook_path": str(WORKBOOK_PATH),
        "workbook_exists": WORKBOOK_PATH.exists(),
        "runs_dir": str(RUNS_DIR),
        "runs_dir_exists": RUNS_DIR.exists(),
        "tools": {
            "npx": shutil.which("npx") is not None,
            "node": shutil.which("node") is not None,
            "python": shutil.which("python3") is not None or shutil.which("python") is not None,
            "pytest": (REPO_ROOT / "selenium" / "tests").exists(),
            "consolidate_results": (REPO_ROOT / "tools" / "consolidate_results.py").exists(),
        },
        "dispatch_mode": os.environ.get("BOURACKA_UI_DISPATCH_MODE", "real"),
    }


@app.get("/api/health")
async def health():
    """Return server status + tool availability check."""
    return _health_dict()


# ──────────────────────────────────────────────────────────────────────────
# §3.1 endpoint 2 — envs
# ──────────────────────────────────────────────────────────────────────────

@app.get("/api/envs")
async def list_envs():
    """List available test environments. Reads 04_TestEnvironments via workbook_io."""
    return workbook_io.list_envs(WORKBOOK_PATH)


# ──────────────────────────────────────────────────────────────────────────
# §3.1 endpoint 3 — tcs
# ──────────────────────────────────────────────────────────────────────────

@app.get("/api/tcs")
async def list_tcs(
    env: str | None = Query(None, description="schema env tag (demo/tst/uat/...)"),
    framework: str | None = Query(None, description="cypress / playwright / selenium"),
):
    """List test cases. Reads 02_TestCases via workbook_io."""
    return workbook_io.list_tcs(WORKBOOK_PATH, env=env, framework=framework)


# ──────────────────────────────────────────────────────────────────────────
# §3.1 endpoint 4 — POST runs
# ──────────────────────────────────────────────────────────────────────────

@app.post("/api/runs")
async def trigger_run(payload: dict):
    """Trigger a test run subprocess.

    Body: { env: "demo", tcs: ["TC-..."], frameworks: ["all"|"cypress"|...] }
    Returns: { run_id: "run-...-abc1234" } 202 Accepted.
    """
    env = payload.get("env")
    tcs = payload.get("tcs", [])
    frameworks = payload.get("frameworks", ["all"])
    if not env:
        raise HTTPException(422, "env required")
    if not tcs:
        raise HTTPException(422, "tcs required (non-empty list)")

    # Generate run_id; spawn subprocess; record in registry
    run_id = dispatcher.generate_run_id()
    _RUN_REGISTRY[run_id] = {
        "run_id": run_id,
        "env": env,
        "tcs": tcs,
        "frameworks": frameworks,
        "status": "pending",
        "started_at": _dt.datetime.now(_dt.timezone.utc).isoformat() + "Z",
        "log_lines": [],
        "exit_code": None,
        "envelope_path": None,
    }
    # Fire-and-forget background task
    asyncio.create_task(dispatcher.run_async(
        run_id=run_id,
        env=env,
        tcs=tcs,
        frameworks=frameworks,
        repo_root=REPO_ROOT,
        registry=_RUN_REGISTRY,
    ))
    return {"run_id": run_id, "status": "pending"}


# ──────────────────────────────────────────────────────────────────────────
# §3.1 endpoint 5 — GET runs (list)
# ──────────────────────────────────────────────────────────────────────────

@app.get("/api/runs")
async def list_runs(
    env: str | None = Query(None),
    since: str | None = Query(None, description="ISO date YYYY-MM-DD lower bound"),
    limit: int = Query(50, ge=1, le=500),
):
    """List past runs by scanning runs/cross-framework-*.json files."""
    if not RUNS_DIR.exists():
        return []
    rows = []
    for p in sorted(RUNS_DIR.glob("cross-framework-*.json"), reverse=True):
        try:
            envelope = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if env and envelope.get("env") != env:
            continue
        if since and envelope.get("started_at", "") < since:
            continue
        s = envelope.get("summary", {})
        rows.append({
            "run_id": envelope.get("run_id"),
            "env": envelope.get("env"),
            "started_at": envelope.get("started_at"),
            "ended_at": envelope.get("ended_at"),
            "duration_ms": envelope.get("duration_ms"),
            "frameworks": envelope.get("frameworks", []),
            "total_tcs": s.get("total_tcs", 0),
            "passed": s.get("passed", 0),
            "failed": s.get("failed", 0),
            "skipped": s.get("skipped", 0),
            "drift_skip_count": s.get("drift_skip_count", 0),
            "parity_pass_count": s.get("parity_pass_count", 0),
            "parity_divergence_count": s.get("parity_divergence_count", 0),
            "envelope_file": p.name,
        })
        if len(rows) >= limit:
            break
    return rows


# ──────────────────────────────────────────────────────────────────────────
# §3.1 endpoint 6 — GET runs/{rid}
# ──────────────────────────────────────────────────────────────────────────

@app.get("/api/runs/{run_id}")
async def get_run(run_id: str):
    """Return the full v0.1 envelope for a run."""
    # First check active runs registry (in-progress)
    reg = _RUN_REGISTRY.get(run_id)
    if reg and reg.get("envelope_path"):
        try:
            return json.loads(Path(reg["envelope_path"]).read_text(encoding="utf-8"))
        except Exception:
            pass
    # Otherwise scan disk
    if RUNS_DIR.exists():
        for p in RUNS_DIR.glob("cross-framework-*.json"):
            try:
                env = json.loads(p.read_text(encoding="utf-8"))
                if env.get("run_id") == run_id:
                    return env
            except Exception:
                continue
    raise HTTPException(404, f"run_id {run_id!r} not found")


# ──────────────────────────────────────────────────────────────────────────
# §3.1 endpoint 7 — SSE log stream
# ──────────────────────────────────────────────────────────────────────────

@app.get("/api/runs/{run_id}/log")
async def stream_log(run_id: str):
    """SSE stream of stdout from active subprocess."""
    if run_id not in _RUN_REGISTRY:
        raise HTTPException(404, f"run_id {run_id!r} not found in active registry")

    async def gen() -> AsyncGenerator[dict, None]:
        last_idx = 0
        while True:
            reg = _RUN_REGISTRY.get(run_id, {})
            lines = reg.get("log_lines", [])
            while last_idx < len(lines):
                yield {"event": "stdout", "data": lines[last_idx]}
                last_idx += 1
            if reg.get("status") == "done":
                summary = reg.get("summary", {})
                yield {
                    "event": "done",
                    "data": json.dumps({
                        "run_id": run_id,
                        "exit_code": reg.get("exit_code"),
                        "envelope_path": reg.get("envelope_path"),
                        "summary": summary,
                    }),
                }
                return
            if reg.get("status") == "failed":
                yield {
                    "event": "error",
                    "data": json.dumps({"run_id": run_id, "error": reg.get("error", "unknown")}),
                }
                return
            await asyncio.sleep(0.25)

    return EventSourceResponse(gen())


# ──────────────────────────────────────────────────────────────────────────
# §3.1 endpoint 8 — GET bugs (list)
# ──────────────────────────────────────────────────────────────────────────

@app.get("/api/bugs")
async def list_bugs(
    status: str | None = Query(None),
    severity: str | None = Query(None),
):
    """List bugs from 08_Bugs sheet."""
    return workbook_io.list_bugs(WORKBOOK_PATH, status=status, severity=severity)


# ──────────────────────────────────────────────────────────────────────────
# §3.1 endpoint 9 — POST bugs (append new)
# ──────────────────────────────────────────────────────────────────────────

@app.post("/api/bugs")
async def file_bug(payload: dict):
    """Append a new bug to 08_Bugs.

    Body: { name_en, severity, urgency, env_where_present, linked_tc_ref,
            repro_steps, expected, actual }
    Returns: 201 { id, code: "BUG-NNN" }
    """
    required = {"name_en", "severity"}
    missing = required - set(payload.keys())
    if missing:
        raise HTTPException(422, f"missing fields: {missing}")
    try:
        new_code = workbook_io.append_bug(WORKBOOK_PATH, payload)
        _server_log(f"bug filed: {new_code}")
    except workbook_io.WorkbookLockedError as e:
        raise HTTPException(409, f"Workbook locked (Excel open?): {e}")
    return {"code": new_code, "status": "filed"}


# ──────────────────────────────────────────────────────────────────────────
# §3.1 endpoint 10 — Trace bundle export (HP Elite air-gap workflow)
# ──────────────────────────────────────────────────────────────────────────

@app.get("/api/runs/{run_id}/bundle")
async def export_bundle(
    run_id: str,
    full: bool = Query(False, description="include videos + traces (large)"),
    workbook: bool = Query(True, description="include workbook snapshot CSVs"),
):
    """Build a self-describing trace bundle ZIP for transfer to a remote
    inspection workstation. See trace_bundle.build_bundle for layout.

    Default: include screenshots + reporter JSONs + system info + workbook
    snapshot. `?full=true` adds videos + Playwright traces (substantially larger).
    """
    # Locate the envelope
    envelope = await get_run(run_id)  # raises 404 if missing
    envelope_path: Path | None = None
    if RUNS_DIR.exists():
        for p in RUNS_DIR.glob("cross-framework-*.json"):
            try:
                e = json.loads(p.read_text(encoding="utf-8"))
                if e.get("run_id") == run_id:
                    envelope_path = p
                    break
            except Exception:
                continue
    if envelope_path is None:
        # Bundle from in-memory envelope only (no on-disk path; degraded)
        envelope_path = RUNS_DIR / f"cross-framework-{envelope.get('env','demo')}-bundle-tmp.json"

    # Pull server-log lines that mention this run_id (best-effort)
    run_log_lines = [ln for ln in _SERVER_LOG if run_id in ln]
    reg = _RUN_REGISTRY.get(run_id, {})
    if reg.get("log_lines"):
        run_log_lines = reg["log_lines"] + run_log_lines

    zip_bytes = trace_bundle.build_bundle(
        run_id=run_id,
        envelope=envelope,
        envelope_path=envelope_path,
        repo_root=REPO_ROOT,
        server_log_lines=run_log_lines,
        include_evidence=full,
        include_workbook=workbook,
        workbook_path=WORKBOOK_PATH if workbook else None,
    )
    _server_log(f"bundle exported: run_id={run_id} size={len(zip_bytes)} full={full}")
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="trace-bundle-{run_id}.zip"'},
    )


# ──────────────────────────────────────────────────────────────────────────
# §3.1 endpoint 11 — Trace bundle import (Pete-side ingestion)
# ──────────────────────────────────────────────────────────────────────────

@app.post("/api/bundles/import")
async def import_bundle(file: UploadFile = File(...)):
    """Accept an uploaded trace bundle and register the run for local
    inspection. The envelope inside the bundle is persisted into runs/ so
    it shows up in /runs listing immediately.
    """
    raw = await file.read()
    try:
        info = trace_bundle.import_bundle(raw, runs_dir=RUNS_DIR)
    except trace_bundle.BundleImportError as e:
        raise HTTPException(422, f"Bundle import failed: {e}")
    _server_log(f"bundle imported: run_id={info['run_id']} ({len(raw)} bytes)")
    return info


# ──────────────────────────────────────────────────────────────────────────
# §3.1 endpoint 12 — Diagnostics snapshot (no-run system dump)
# ──────────────────────────────────────────────────────────────────────────

@app.get("/api/diagnostics/snapshot")
async def diagnostics_snapshot():
    """Build a no-run diagnostics ZIP for "UI itself misbehaving" debugging.

    Includes system info, tool versions, workbook sanity check, runs/ index,
    and recent server log lines. Useful for HP Elite remote debugging when
    no specific test run is involved.
    """
    zip_bytes = trace_bundle.build_diagnostics_snapshot(
        repo_root=REPO_ROOT,
        workbook_path=WORKBOOK_PATH,
        health=_health_dict(),
        recent_log_lines=list(_SERVER_LOG[-200:]),
    )
    ts = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    _server_log(f"diagnostics snapshot exported ({len(zip_bytes)} bytes)")
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="bouracka-ui-diag-{ts}.zip"'},
    )
