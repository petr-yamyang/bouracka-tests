"""Run dispatcher for bouracka-ui.

Real implementation — subprocess invocation of cypress / playwright /
pytest+selenium followed by tools/consolidate_results.py to produce the
canonical v0.1 envelope.

Falls back to MOCK mode if BOURACKA_UI_DISPATCH_MODE=mock or if the
cypress/playwright/python tooling is not present on PATH (so the package
still demos cleanly on a non-tester developer machine).

Reference:
  _config/BOURACKA-UI-DESIGN-v0.1-2026-05-10.md §5
"""
from __future__ import annotations

import asyncio
import datetime as _dt
import json
import os
import re
import subprocess
import sys
import uuid
from pathlib import Path

RUN_ID_RE = re.compile(r"^run-\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z-[0-9a-f]{7}$")
# Note: timestamp uses '-' instead of ':' separators so run_ids are valid
# filename components on Windows (NTFS rejects ':' in filenames). POSIX is
# fine with either; we pick filename-safe format for cross-platform parity.

# Per the workbook ENV-* codes per §4.1 of the UI design doc.
ENV_TO_BASE_URL = {
    "demo":          "https://demo.bouracka.cz",
    "tst":           "https://tst.bouracka.cz",
    "uat":           "https://uat.bouracka.cz",
    "prod-readonly": "https://www.bouracka.cz",
}


def generate_run_id() -> str:
    # Use '-' instead of ':' in time portion for Windows filename safety
    # (NTFS rejects ':' in filename components; POSIX accepts either).
    ts = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    short = uuid.uuid4().hex[:7]
    rid = f"run-{ts}-{short}"
    assert RUN_ID_RE.match(rid)
    return rid


def _is_mock_mode() -> bool:
    if os.environ.get("BOURACKA_UI_DISPATCH_MODE", "").lower() == "mock":
        return True
    return False


# ──────────────────────────────────────────────────────────────────────────
# Public entry — async subprocess orchestrator
# ──────────────────────────────────────────────────────────────────────────

async def run_async(run_id: str, env: str, tcs: list[str],
                    frameworks: list[str], repo_root: Path,
                    registry: dict[str, dict]) -> None:
    """Run the selected TCs across selected frameworks.

    Behaviour:
      1. For each framework, build the command per §5.1 of design doc
      2. Subprocess each in turn; stream stdout to registry[run_id]['log_lines']
      3. After all frameworks complete, invoke tools/consolidate_results.py
         with --run-id passthrough so the envelope's run_id matches
      4. Set registry[run_id] status='done' with envelope_path + summary
    """
    reg = registry.get(run_id)
    if reg is None:
        return
    reg["status"] = "running"
    log = reg.setdefault("log_lines", [])

    expanded_fws = ["cypress", "playwright", "selenium"] if "all" in frameworks else frameworks
    base_url = ENV_TO_BASE_URL.get(env, "https://demo.bouracka.cz")

    log.append(f"[bouracka-ui] starting run_id={run_id}")
    log.append(f"[bouracka-ui] env={env} ({base_url})")
    log.append(f"[bouracka-ui] frameworks={expanded_fws}  tcs={tcs}")
    log.append(f"[bouracka-ui] mode={'MOCK' if _is_mock_mode() else 'REAL'}")
    log.append("")

    if _is_mock_mode():
        await _run_mock(run_id, env, tcs, expanded_fws, repo_root, registry)
        return

    # Real subprocess loop — one framework at a time
    exit_codes: dict[str, int] = {}
    for fw in expanded_fws:
        log.append(f"=== {fw} ===")
        cmd = _build_cmd(fw, tcs, base_url, env)
        if cmd is None:
            log.append(f"[{fw}] (no command — skipping; tooling missing on PATH)")
            log.append("")
            continue
        log.append(f"[{fw}] $ {' '.join(cmd)}")
        rc = await _run_subprocess(cmd, cwd=repo_root, log=log, prefix=f"[{fw}]")
        exit_codes[fw] = rc
        log.append(f"[{fw}] exit_code={rc}")
        log.append("")

    # Consolidate results — invoke tools/consolidate_results.py
    log.append("=== consolidate_results.py ===")
    cons_cmd = [
        sys.executable, str(repo_root / "tools" / "consolidate_results.py"),
        "--env", env,
        "--env-url", base_url,
        "--run-id", run_id,
        "--reporter-command", f"bouracka-ui run env={env} fws={','.join(expanded_fws)} tcs={','.join(tcs)}",
        "--trigger", "manual",
    ]
    log.append(f"$ {' '.join(cons_cmd)}")
    cons_rc = await _run_subprocess(cons_cmd, cwd=repo_root, log=log, prefix="[consolidate]")
    log.append(f"[consolidate] exit_code={cons_rc}")

    # Locate the produced envelope
    today = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")
    envelope_path = repo_root / "runs" / f"cross-framework-{env}-{today}.json"
    summary = {}
    if envelope_path.exists():
        try:
            envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
            # Verify the run_id matches what we passed (consolidator should have used --run-id)
            if envelope.get("run_id") == run_id:
                summary = envelope.get("summary", {})
            else:
                log.append(f"[consolidate] WARNING: envelope run_id={envelope.get('run_id')} != "
                           f"requested {run_id}; consolidator may not be using --run-id flag")
        except Exception as e:
            log.append(f"[consolidate] WARNING: could not parse envelope: {e}")
    else:
        log.append(f"[consolidate] WARNING: envelope not found at {envelope_path}")

    log.append("")
    log.append(f"[bouracka-ui] DONE run_id={run_id}  fw_exits={exit_codes}  cons_exit={cons_rc}")

    reg["status"] = "done"
    reg["exit_code"] = max(list(exit_codes.values()) + [cons_rc]) if exit_codes else cons_rc
    reg["envelope_path"] = str(envelope_path) if envelope_path.exists() else None
    reg["summary"] = summary


# ──────────────────────────────────────────────────────────────────────────
# Per-framework command construction
# ──────────────────────────────────────────────────────────────────────────

def _build_cmd(fw: str, tcs: list[str], base_url: str, env: str) -> list[str] | None:
    """Build the framework-specific subprocess command per design §5.1."""
    if fw == "cypress":
        # Cypress spec pattern — convert TC code (TC-CP-A2-ALT-7) to file glob
        # Existing convention per repo: cypress/e2e/<lowercase-dashed>.cy.ts
        # We match on the trailing TC token.
        spec_globs = [_tc_to_cypress_glob(tc) for tc in tcs]
        return [
            "npx", "cypress", "run",
            "--spec", ",".join(spec_globs),
            "--env", f"baseUrl={base_url}",
        ]
    if fw == "playwright":
        # Playwright --grep accepts regex; OR the TC codes
        grep = "|".join(re.escape(tc) for tc in tcs)
        env_inj = {"PLAYWRIGHT_BASE_URL": base_url}
        return [
            "npx", "playwright", "test",
            "--grep", grep,
            f"--reporter=json",  # pipes to playwright-report/results.json via project config
        ]
    if fw == "selenium":
        # pytest -k expression — TC code tokens (underscored; matches test_TC_CP_A2_ALT_7_*)
        k_expr = " or ".join(tc.replace("-", "_") for tc in tcs)
        return [
            sys.executable, "-m", "pytest", "selenium/tests/",
            "-k", k_expr,
            "--json-report",
            "--json-report-file=selenium-report/results.json",
        ]
    return None  # unknown framework — skip


def _tc_to_cypress_glob(tc: str) -> str:
    """TC-CP-A1-MAIN-DEMO → cypress/e2e/**/main-happy-day.cy.ts (best-effort)."""
    # Per existing convention: each TC has one .cy.ts spec; the spec name often
    # encodes the TC token. Glob with the lowercase token is the safest match.
    token = tc.lower().replace("tc-cp-", "")
    return f"cypress/e2e/**/*{token}*.cy.ts"


# ──────────────────────────────────────────────────────────────────────────
# Async subprocess runner with line-buffered stdout to log
# ──────────────────────────────────────────────────────────────────────────

async def _run_subprocess(cmd: list[str], cwd: Path, log: list[str],
                          prefix: str) -> int:
    """Run cmd via asyncio subprocess; stream stdout/stderr line-by-line into log.
    Returns exit code."""
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(cwd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
    except FileNotFoundError as e:
        log.append(f"{prefix} tooling not found: {e}")
        return 127
    except Exception as e:
        log.append(f"{prefix} failed to spawn: {e}")
        return 1

    assert proc.stdout is not None
    while True:
        line = await proc.stdout.readline()
        if not line:
            break
        text = line.decode("utf-8", errors="replace").rstrip()
        log.append(f"{prefix} {text}")
    rc = await proc.wait()
    return rc


# ──────────────────────────────────────────────────────────────────────────
# Mock mode — falls back when tooling unavailable; produces a synthetic
# v0.1 envelope. Useful for demos + CI on a developer machine.
# ──────────────────────────────────────────────────────────────────────────

async def _run_mock(run_id: str, env: str, tcs: list[str],
                    frameworks: list[str], repo_root: Path,
                    registry: dict[str, dict]) -> None:
    reg = registry[run_id]
    log = reg["log_lines"]

    for fw in frameworks:
        log.append(f"=== {fw} (mock) ===")
        for tc in tcs:
            await asyncio.sleep(0.12)
            v = _mock_verdict(tc, fw)
            log.append(f"[{fw}] {v.upper():9s} {tc}")
        log.append(f"[{fw}] complete")
        log.append("")

    log.append("=== consolidate_results.py (mock) ===")
    await asyncio.sleep(0.2)
    envelope = _build_mock_envelope(run_id, env, tcs, frameworks)
    runs_dir = repo_root / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    today = envelope["started_at"].split("T")[0]
    out_path = runs_dir / f"cross-framework-{env}-{today}.json"
    out_path.write_text(json.dumps(envelope, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    log.append(f"[consolidate] written: {out_path}")
    log.append(f"[bouracka-ui] DONE run_id={run_id}")

    reg["status"] = "done"
    reg["exit_code"] = 0
    reg["envelope_path"] = str(out_path)
    reg["summary"] = envelope["summary"]


def _mock_verdict(tc: str, fw: str) -> str:
    if "ALT-1" in tc:
        return "skip-drift"
    if "ALT-9" in tc:
        return "soft-pass"
    if "ALT-4" in tc and fw == "cypress":
        return "fail"
    return "pass"


def _build_mock_envelope(run_id: str, env: str, tcs: list[str],
                         frameworks: list[str]) -> dict:
    started = _dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(seconds=12)
    ended = _dt.datetime.now(_dt.timezone.utc)
    started_iso = started.strftime("%Y-%m-%dT%H:%M:%SZ")
    ended_iso = ended.strftime("%Y-%m-%dT%H:%M:%SZ")
    duration_ms = int((ended - started).total_seconds() * 1000)

    results = []
    for tc in tcs:
        verdicts = {fw: _to_canonical(_mock_verdict(tc, fw)) for fw in frameworks}
        present = [v for v in verdicts.values() if v != "missing"]
        normalized = {_normalize_for_parity(v) for v in present}
        if len(present) == 1:
            parity = "not-applicable"
        elif len(normalized) == 1:
            parity = "agree"
        else:
            parity = "divergence"
        results.append({
            "tc_code": tc,
            "verdicts": verdicts,
            "parity_status": parity,
            "duration_ms": {fw: 1200 + i * 50 for i, fw in enumerate(frameworks)},
            "evidence": {fw: {"trace_ref": None, "screenshot_ref": None,
                              "video_ref": None} for fw in frameworks},
            "covered_tt": [],
            "error_messages": {fw: ("ALT-4 cypress mock failure"
                                     if "ALT-4" in tc and fw == "cypress" else None)
                                for fw in frameworks},
            "framework_specific_notes": {fw: "" for fw in frameworks},
            "viewport": "375x667",
            "bug_ref": None,
            "soft_pass_reason": (f"TC marked soft-pass (mock for {tc})"
                                 if any(v == "soft-pass" for v in verdicts.values())
                                 else None),
        })
    summary = _summarize(results)
    return {
        "schema_version": "1.0", "run_id": run_id, "env": env,
        "env_url": ENV_TO_BASE_URL.get(env, ""),
        "started_at": started_iso, "ended_at": ended_iso, "duration_ms": duration_ms,
        "frameworks": sorted(frameworks),
        "results": results, "summary": summary,
        "host": {"os": "mock", "host": "bouracka-ui-mock",
                 "git_commit": None, "git_branch": None, "tool_versions": None},
        "drift_forensic": ({"active": True, "drift_type": "recaptcha-v3",
                            "trigger_correlation": "mock-correlation",
                            "affected_tcs": [t for t in tcs if "ALT-1" in t],
                            "guard_policy": "skip-on-drift",
                            "notes": "(mock mode)"}
                           if any("ALT-1" in t for t in tcs) else None),
        "reporter": {"command": "bouracka-ui (mock dispatcher)",
                     "trigger": "manual", "ci_run_id": None,
                     "operator": "bouracka-ui-mock"},
    }


def _to_canonical(v: str) -> str:
    return {"pass": "pass", "fail": "fail", "skip-drift": "skip-drift",
            "skip-other": "skip-other", "soft-pass": "soft-pass",
            "error": "error", "missing": "missing"}.get(v, v)


def _normalize_for_parity(v: str) -> str:
    if v in ("pass", "soft-pass"):
        return "pass"
    if v in ("fail", "error"):
        return "fail"
    return v


def _summarize(results: list[dict]) -> dict:
    total = len(results)
    if total == 0:
        return {"total_tcs": 0, "passed": 0, "failed": 0, "skipped": 0,
                "soft_passed": 0, "drift_skip_count": 0,
                "parity_pass_count": 0, "parity_divergence_count": 0,
                "pass_rate_strict": None, "pass_rate_drift_aware": None}

    def present(r):
        return {v for v in r["verdicts"].values() if v != "missing"}

    passed = sum(1 for r in results if present(r) <= {"pass", "soft-pass"} and present(r))
    failed = sum(1 for r in results if present(r) & {"fail", "error"})
    skipped = sum(1 for r in results if present(r) <= {"skip-drift", "skip-other"} and present(r))
    soft = sum(1 for r in results if present(r) == {"soft-pass"})
    drift = sum(1 for r in results if present(r) == {"skip-drift"})
    pp = sum(1 for r in results if r["parity_status"] == "agree")
    pd = sum(1 for r in results if r["parity_status"] == "divergence")
    return {"total_tcs": total, "passed": passed, "failed": failed,
            "skipped": skipped, "soft_passed": soft, "drift_skip_count": drift,
            "parity_pass_count": pp, "parity_divergence_count": pd,
            "pass_rate_strict": round(passed / total, 2),
            "pass_rate_drift_aware": round((passed + drift) / total, 2)}
