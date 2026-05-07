#!/usr/bin/env python3
"""
test_console.py — multi-framework + multi-env test runner + aggregator.

Per CP-SUPIN-04 L-WORK-8+9. Single CLI for:
  - running test cases across installed frameworks (Playwright/Cypress/TestCafe)
  - aggregating results across runs
  - emitting a comparison report that feeds the Gate 1/2/3 framework
    decision in CLIENT-PILOT-SUPIN §3.3

This v0.1 implements the SCAFFOLD: framework auto-detect, run dispatch
to wrappers, JSON results capture, comparison-report generation.
Excel-row-write to 07_TestRunResults ships in CP-SUPIN-05.

USAGE
  python tools/test_console.py run --env tst --frameworks playwright
  python tools/test_console.py run --env tst --frameworks playwright,cypress \\
                                    --tcs TC-CP-001,TC-CP-005
  python tools/test_console.py report --since 2026-05-06
  python tools/test_console.py compare --tcs TC-CP-001..TC-CP-005
  python tools/test_console.py status     # what's installed; what's runnable
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = ROOT / "runs"
RUNS_DIR.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Framework detection
# ─────────────────────────────────────────────────────────────────────────────

def detect_frameworks() -> dict[str, dict]:
    """Probe what's installed; return per-framework status."""
    out = {}

    # Playwright — check for npx playwright
    pw_present = (ROOT / "node_modules" / "@playwright" / "test").exists()
    out["playwright"] = {
        "installed": pw_present,
        "config_path": str(ROOT / "playwright" / "playwright.config.ts"),
        "spec_dir": str(ROOT / "playwright" / "tests"),
    }

    # Cypress — check for node_modules/cypress
    cy_present = (ROOT / "node_modules" / "cypress").exists()
    out["cypress"] = {
        "installed": cy_present,
        "config_path": str(ROOT / "cypress" / "cypress.config.ts"),
        "spec_dir": str(ROOT / "cypress" / "e2e"),
    }

    # TestCafe — check for node_modules/testcafe
    tc_present = (ROOT / "node_modules" / "testcafe").exists()
    out["testcafe"] = {
        "installed": tc_present,
        "config_path": str(ROOT / "testcafe" / ".testcaferc.json"),
        "spec_dir": str(ROOT / "testcafe" / "tests"),
    }

    # Mockoon — required for many R1 TCs in mock mode
    mockoon_cli = shutil.which("mockoon-cli") is not None
    out["_mockoon"] = {
        "installed": mockoon_cli,
        "profile_path": str(ROOT / "mockoon" / "n8-sms-gateway.json"),
    }

    return out


# ─────────────────────────────────────────────────────────────────────────────
# Run dispatch
# ─────────────────────────────────────────────────────────────────────────────

def run_playwright(env: str, tcs: list[str] | None) -> dict:
    """Dispatch to Playwright via existing scripts/run-playwright.ps1 logic."""
    started = datetime.utcnow().isoformat() + "Z"
    cmd = ["npx", "playwright", "test",
           "--config=playwright/playwright.config.ts",
           "--reporter=json"]
    if tcs:
        # Filter by TC code in the test title (Playwright -g grep)
        cmd.extend(["-g", "|".join(tcs)])

    env_vars = {"BOURACKA_ENV": env}
    print(f"[run_playwright] env={env} cmd={' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT,
                            env={**__import__('os').environ, **env_vars})
    finished = datetime.utcnow().isoformat() + "Z"

    return {
        "framework": "playwright",
        "env": env,
        "tcs_filter": tcs,
        "started_at": started,
        "finished_at": finished,
        "exit_code": result.returncode,
        "stdout_tail": result.stdout[-2000:],
        "stderr_tail": result.stderr[-2000:],
    }


def run_cypress(env: str, tcs: list[str] | None) -> dict:
    started = datetime.utcnow().isoformat() + "Z"
    cmd = ["npx", "cypress", "run",
           "--config-file=cypress/cypress.config.ts",
           "--reporter=json"]
    if tcs:
        # Cypress glob filter — write a temporary spec list
        cmd.extend(["--spec", ",".join(f"cypress/e2e/**/*{t}*.cy.ts" for t in tcs)])

    env_vars = {"BOURACKA_ENV": env}
    print(f"[run_cypress] env={env} cmd={' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT,
                            env={**__import__('os').environ, **env_vars})
    finished = datetime.utcnow().isoformat() + "Z"

    return {
        "framework": "cypress",
        "env": env,
        "tcs_filter": tcs,
        "started_at": started,
        "finished_at": finished,
        "exit_code": result.returncode,
        "stdout_tail": result.stdout[-2000:],
        "stderr_tail": result.stderr[-2000:],
    }


def run_testcafe(env: str, tcs: list[str] | None) -> dict:
    started = datetime.utcnow().isoformat() + "Z"
    cmd = ["npx", "testcafe", "chrome:headless",
           "testcafe/tests/**/*.test.ts",
           "--config-file", "testcafe/.testcaferc.json",
           "--reporter", "json"]
    env_vars = {"BOURACKA_ENV": env}
    print(f"[run_testcafe] env={env} cmd={' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT,
                            env={**__import__('os').environ, **env_vars})
    finished = datetime.utcnow().isoformat() + "Z"

    return {
        "framework": "testcafe",
        "env": env,
        "tcs_filter": tcs,
        "started_at": started,
        "finished_at": finished,
        "exit_code": result.returncode,
        "stdout_tail": result.stdout[-2000:],
        "stderr_tail": result.stderr[-2000:],
    }


RUNNERS = {
    "playwright": run_playwright,
    "cypress": run_cypress,
    "testcafe": run_testcafe,
}


# ─────────────────────────────────────────────────────────────────────────────
# CLI commands
# ─────────────────────────────────────────────────────────────────────────────

def cmd_status(args):
    fw = detect_frameworks()
    print("[test-console] framework status:")
    for name, info in fw.items():
        if name.startswith("_"):
            continue
        sym = "✓" if info["installed"] else "✗"
        print(f"  {sym}  {name:12s} (installed={info['installed']})")
    print()
    print(f"  Mockoon CLI: {'✓ installed' if fw['_mockoon']['installed'] else '✗ NOT installed (npm install -g @mockoon/cli)'}")
    print(f"  Mockoon profile: {fw['_mockoon']['profile_path']}")


def cmd_run(args):
    env = args.env
    frameworks = (args.frameworks or "").split(",") if args.frameworks else None
    tcs = (args.tcs or "").split(",") if args.tcs else None
    fw_status = detect_frameworks()

    available = [f for f in RUNNERS if fw_status[f]["installed"]]
    if not available:
        print("[FAIL] no frameworks installed; run 'npm install' + 'npx playwright install chromium' first")
        sys.exit(1)

    targets = frameworks or available
    targets = [f for f in targets if f in available]
    if not targets:
        print(f"[FAIL] requested frameworks not installed: {frameworks}")
        sys.exit(1)

    print(f"[test-console] env={env}  frameworks={targets}  tcs={tcs or 'all'}")
    print()

    run_id = f"RUN-{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}-{env}"
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for f in targets:
        runner = RUNNERS[f]
        result = runner(env, tcs)
        results.append(result)
        # Write per-framework JSON
        (run_dir / f"{f}.json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        sym = "✓ PASS" if result["exit_code"] == 0 else f"✗ FAIL (exit {result['exit_code']})"
        print(f"  {f:12s} {sym}")

    # Aggregate manifest
    manifest = {
        "run_id": run_id,
        "started_at": results[0]["started_at"] if results else None,
        "env": env,
        "frameworks_run": targets,
        "tcs_filter": tcs,
        "results_summary": [
            {"framework": r["framework"], "exit_code": r["exit_code"]}
            for r in results
        ],
    }
    (run_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print()
    print(f"[OK] run results in: {run_dir}")
    print(f"[next] python tools/test_console.py report --since {datetime.utcnow().date()}")


def cmd_report(args):
    """Aggregate results from all runs since the given date."""
    since = args.since
    print(f"[test-console] report from runs since: {since}")
    runs = sorted(RUNS_DIR.glob("RUN-*"))
    if not runs:
        print("  (no runs found)")
        return
    print()
    print(f"  {'Run ID':40s} {'Env':10s} {'Frameworks':30s} {'Verdict':10s}")
    for r in runs:
        m = r / "manifest.json"
        if not m.exists():
            continue
        if r.stat().st_mtime_ns / 1e9 < datetime.fromisoformat(since).timestamp():
            continue
        manifest = json.loads(m.read_text(encoding="utf-8"))
        all_pass = all(s["exit_code"] == 0 for s in manifest["results_summary"])
        verdict = "PASS" if all_pass else "MIXED"
        print(f"  {manifest['run_id']:40s} {manifest['env']:10s} "
              f"{','.join(manifest['frameworks_run']):30s} {verdict:10s}")


def cmd_compare(args):
    """Comparative table per framework × TC."""
    print(f"[test-console] comparison for: {args.tcs}")
    runs = sorted(RUNS_DIR.glob("RUN-*"))
    if not runs:
        print("  (no runs found)")
        return

    # For now: print last run per framework
    last_per_fw: dict[str, dict] = {}
    for r in runs:
        m = r / "manifest.json"
        if not m.exists():
            continue
        manifest = json.loads(m.read_text(encoding="utf-8"))
        for s in manifest["results_summary"]:
            last_per_fw[s["framework"]] = {"run_id": manifest["run_id"], "exit_code": s["exit_code"]}

    print()
    print(f"  {'Framework':12s} {'Last run':40s} {'Exit code':10s}")
    for fw, data in last_per_fw.items():
        print(f"  {fw:12s} {data['run_id']:40s} {data['exit_code']:10d}")
    print()
    print("[next] CP-SUPIN-05 expands this with per-TC verdict + duration + flake-rate columns")
    print("[next] reads from 07_TestRunResults sheet of the workbook")


# ─────────────────────────────────────────────────────────────────────────────
# Argparse
# ─────────────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(prog="test_console", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("status", help="Show installed-framework status")
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("run", help="Run TCs across frameworks")
    sp.add_argument("--env", required=True, choices=["tst", "tst-demo", "public"])
    sp.add_argument("--frameworks", help="comma-list; default = all installed")
    sp.add_argument("--tcs", help="comma-list of TC codes (e.g. TC-CP-001,TC-CP-005); default = all")
    sp.set_defaults(func=cmd_run)

    sp = sub.add_parser("report", help="Aggregate report since date")
    sp.add_argument("--since", required=True, help="YYYY-MM-DD")
    sp.set_defaults(func=cmd_report)

    sp = sub.add_parser("compare", help="Per-TC framework comparison")
    sp.add_argument("--tcs", required=True, help="comma-list or range (TC-CP-001..TC-CP-005)")
    sp.set_defaults(func=cmd_compare)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
