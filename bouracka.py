#!/usr/bin/env python3
"""
bouracka.py — pure-Python orchestrator for the bouracka-tests kit.

Per CP-SUPIN-04 v0.4.9.1-SAFE. Replaces the .cmd/.ps1 wrappers from v0.4.9
because email scanners (Gmail, Active24) flag PowerShell scripts as malware-
delivery vectors. This file uses only Python's standard library + subprocess
calls to npm/npx — no PowerShell, no shell magic, no IOC strings.

Usage on HP Elite (<test-runner-host>):
    py bouracka.py setup    # one-time: npm install + playwright chromium
    py bouracka.py test     # run the suite + package results
    py bouracka.py all      # both, sequentially
    py bouracka.py verify   # integrity check only (no run)
    py bouracka.py help

Email back: bouracka-results-YYYY-MM-DD-<USERNAME>.zip from this directory.
"""

import argparse
import getpass
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile
from datetime import date
from pathlib import Path


HERE = Path(__file__).resolve().parent
RUN_LOG = HERE / "bouracka-run.log"


# ── tiny logging helpers ────────────────────────────────────────────────────

def log(msg: str, file=None) -> None:
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    with open(RUN_LOG, "a", encoding="utf-8") as h:
        h.write(line + "\n")


def section(title: str) -> None:
    bar = "-" * 70
    log(bar)
    log(f" {title}")
    log(bar)


# ── subprocess wrapper that streams output ──────────────────────────────────

def run(cmd: list[str], cwd: Path = None, check: bool = True) -> int:
    cwd = cwd or HERE
    log(f"$ {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=str(cwd), shell=False)
    if check and proc.returncode != 0:
        log(f"  -> exit {proc.returncode} (FAIL)")
        sys.exit(proc.returncode)
    log(f"  -> exit {proc.returncode}")
    return proc.returncode


def run_soft(cmd: list[str], cwd: Path = None) -> int:
    """Run a command but don't abort on non-zero exit (test runs fail = ok)."""
    return run(cmd, cwd=cwd, check=False)


# ── command resolution: works around Windows MS-Store python.exe stub ───────

def npm_cmd() -> list[str]:
    """Return the right invocation for npm on this platform."""
    if os.name == "nt":
        return ["npm.cmd"]  # cmd shim from Node.js installer
    return ["npm"]


def npx_cmd() -> list[str]:
    if os.name == "nt":
        return ["npx.cmd"]
    return ["npx"]


# ── 1. integrity check ──────────────────────────────────────────────────────

CRITICAL_FILES = [
    "playwright/tests/bring-up-smoke.spec.ts",
    "playwright/tests/a2-alternates-demo.spec.ts",
    "playwright/tests/a1-main-happy-day-demo.spec.ts",
    "playwright/reporters/excel-row-writer.ts",
    "playwright/playwright.config.ts",
    "package.json",
]


def cmd_verify() -> int:
    section("Integrity check on critical source files")
    bad = 0
    for rel in CRITICAL_FILES:
        p = HERE / rel
        if not p.exists():
            log(f"  MISSING  {rel}")
            bad += 1
            continue
        data = p.read_bytes()
        nulls = data.count(b"\x00")
        ok = nulls == 0 and len(data) > 0
        status = "OK " if ok else "BAD"
        log(f"  {status}  {rel:<55} {len(data):>7} B  nulls={nulls}")
        if not ok:
            bad += 1
    if bad > 0:
        log(f"FAIL: {bad} file(s) corrupt or missing.")
        return 2
    log("All critical files clean.")
    return 0


# ── 2. setup (one-time per machine) ─────────────────────────────────────────

def cmd_setup() -> int:
    rc = cmd_verify()
    if rc != 0:
        return rc

    section("Preflight: Node + npm + Python")
    for binary in ["node", "npm.cmd" if os.name == "nt" else "npm"]:
        if shutil.which(binary) is None:
            log(f"  MISSING tool: {binary}")
            log("  Install Node.js LTS from https://nodejs.org/ then retry.")
            return 3
    log(f"  python:  {sys.executable}")
    log(f"  python:  {sys.version.split()[0]}")

    section("npm install (~5 min, ~1 GB)")
    run(npm_cmd() + ["install"])

    section("Playwright browsers — install chromium")
    run(npx_cmd() + ["playwright", "install", "chromium"])

    section("Setup complete")
    log("Next: py bouracka.py test")
    return 0


# ── 3. test (per run) ───────────────────────────────────────────────────────

PLAYWRIGHT_SPECS = [
    "playwright/tests/bring-up-smoke.spec.ts",
    "playwright/tests/a2-alternates-demo.spec.ts",
    "playwright/tests/a1-main-happy-day-demo.spec.ts",
]


def cmd_test() -> int:
    rc = cmd_verify()
    if rc != 0:
        return rc

    base = os.environ.get("BOURACKA_BASE", "https://demo.bouracka.cz")
    section(f"Running Playwright suite against: {base}")

    worst = 0
    for spec in PLAYWRIGHT_SPECS:
        section(f"  -> {spec}")
        ec = run_soft(npx_cmd() + ["playwright", "test",
                                   "--config=playwright/playwright.config.ts",
                                   spec])
        worst = max(worst, ec)

    section("Packaging results")
    today = date.today().isoformat()
    user = (os.environ.get("USERNAME") or os.environ.get("USER") or "unknown")
    user_safe = "".join(c for c in user if c.isalnum())
    zip_name = HERE / f"bouracka-results-{today}-{user_safe}.zip"
    if zip_name.exists():
        zip_name.unlink()

    bundle_dirs = []
    for d in ("test-results", "playwright-report"):
        p = HERE / d
        if p.exists():
            bundle_dirs.append(p)

    if not bundle_dirs:
        log("  no test-results / playwright-report dirs to bundle")
    else:
        with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zf:
            for d in bundle_dirs:
                for fp in d.rglob("*"):
                    if fp.is_file():
                        arcname = fp.relative_to(HERE)
                        zf.write(fp, arcname)
            # also include the run log
            if RUN_LOG.exists():
                zf.write(RUN_LOG, RUN_LOG.name)
        sz = zip_name.stat().st_size
        sha = hashlib.sha256(zip_name.read_bytes()).hexdigest()
        log(f"  wrote: {zip_name.name}  ({sz/1024:.1f} KB)")
        log(f"  sha256: {sha}")

    section(f"Suite complete. worst-exit={worst}")
    log(f"Mail back: {zip_name.name}")
    log("Most useful single artefact: test-results/<run>/alt10-spa-post.json")
    return worst


# ── 4. all (setup + test) ──────────────────────────────────────────────────

def cmd_all() -> int:
    rc = cmd_setup()
    if rc != 0:
        return rc
    return cmd_test()


# ── help ────────────────────────────────────────────────────────────────────

def cmd_help() -> int:
    print(__doc__)
    return 0


# ── argparse entrypoint ─────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(
        prog="bouracka.py",
        description="Pure-Python orchestrator for the bouracka-tests kit",
    )
    ap.add_argument("command", nargs="?", default="help",
                    choices=["setup", "test", "all", "verify", "help"])
    args = ap.parse_args()

    log(f"=== bouracka.py {args.command} (v0.5.0-CP-SUPIN-05) ===")
    log(f"cwd: {HERE}")
    log(f"user: {getpass.getuser()}")

    table = {
        "setup":  cmd_setup,
        "test":   cmd_test,
        "all":    cmd_all,
        "verify": cmd_verify,
        "help":   cmd_help,
    }
    return table[args.command]()


if __name__ == "__main__":
    sys.exit(mai