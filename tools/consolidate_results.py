#!/usr/bin/env python3
"""
consolidate_results.py — merge per-framework test outputs into cross-framework comparison.

CP-SUPIN-05 v0.5.1 — cross-framework parity consolidation tool.

Reads (any subset present; missing sources are skipped with a warning):
  playwright-report/results.json          (Playwright JSON reporter output)
  cypress/cypress-results/*.json          (Cypress --reporter json output)
  selenium-report/results.json            (pytest-json-report plugin output)

Writes:
  runs/cross-framework-{date}.json        (machine-readable comparison)
  runs/cross-framework-{date}.md          (human-readable parity summary)

Usage:
  py tools/consolidate_results.py
  py tools/consolidate_results.py --base-url https://demo.bouracka.cz
  py tools/consolidate_results.py --pw playwright-report/results.json \\
                                   --cy cypress/cypress-results/results.json \\
                                   --se selenium-report/results.json

Schema per TC entry (common JSON):
  {
    "tc_code":                  "TC-CP-A2-ALT-7",
    "framework":                "playwright|cypress|selenium",
    "status":                   "passed|failed|skipped|soft_passed",
    "duration_ms":              12345,
    "env":                      "https://demo.bouracka.cz",
    "viewport":                 "375x667",
    "covered_tt":               ["TT-LOV-insuranceCompanies"],
    "error_message":            null,
    "trace_ref":                null,
    "framework_specific_notes": ""
  }

Per _specs/CROSS-FRAMEWORK-PARITY-EXECUTION-v0.1-CS.md §8.
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import sys
import warnings
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

# ─── constants ────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent

KNOWN_TC_CODES = [
    "TC-CP-A1-MAIN-DEMO",
    "TC-CP-A2-ALT-1",
    "TC-CP-A2-ALT-4",
    "TC-CP-A2-ALT-5",
    "TC-CP-A2-ALT-6",
    "TC-CP-A2-ALT-7",
    "TC-CP-A2-ALT-8",
    "TC-CP-A2-ALT-9",
    "TC-CP-A2-ALT-10",
]

TC_CODE_RE = re.compile(r"TC-CP-[A-Z0-9-]+")
TT_CODE_RE = re.compile(r"TT-[A-Z]+-[a-zA-Z0-9]+")

SOFT_PASS_MARKERS = {
    "TC-CP-A2-ALT-9",  # 200 OR 403 both valid
}


# ─── parsers ──────────────────────────────────────────────────────────────────

def _extract_tc_code(title: str) -> str | None:
    """Extract TC code from test title string."""
    m = TC_CODE_RE.search(title)
    return m.group(0) if m else None


def _extract_tt_codes(title: str, notes: str = "") -> list[str]:
    """Extract TT-* codes from test title or attached notes."""
    found = TT_CODE_RE.findall(title + " " + notes)
    return sorted(set(found))


def _parse_playwright(path: Path, env: str) -> list[dict[str, Any]]:
    """Parse Playwright JSON reporter output (--reporter=json)."""
    if not path.exists():
        warnings.warn(f"[consolidate] Playwright results not found: {path}")
        return []

    raw = json.loads(path.read_text(encoding="utf-8"))
    results: list[dict[str, Any]] = []

    def _walk(suite):
        for spec in suite.get("specs", []):
            for test in spec.get("tests", []):
                title = " ".join([
                    suite.get("title", ""),
                    spec.get("title", ""),
                    test.get("title", ""),
                ])
                tc = _extract_tc_code(title)
                if not tc:
                    continue

                results_raw = test.get("results", [{}])
                last = results_raw[-1] if results_raw else {}
                pw_status = last.get("status", "unknown")  # passed/failed/skipped/timedOut
                duration_ms = last.get("duration", 0)

                status = {
                    "passed": "passed",
                    "failed": "failed",
                    "skipped": "skipped",
                    "timedOut": "failed",
                    "interrupted": "failed",
                }.get(pw_status, "failed")

                if status == "passed" and tc in SOFT_PASS_MARKERS:
                    status = "soft_passed"

                error_msg = None
                for err_result in results_raw:
                    if err_result.get("error"):
                        error_msg = err_result["error"].get("message", "")
                        break

                results.append({
                    "tc_code": tc,
                    "framework": "playwright",
                    "status": status,
                    "duration_ms": int(duration_ms),
                    "env": env,
                    "viewport": "375x667",
                    "covered_tt": _extract_tt_codes(title),
                    "error_message": error_msg,
                    "trace_ref": last.get("attachments", [{}])[0].get("path") if last.get("attachments") else None,
                    "framework_specific_notes": pw_status if pw_status not in ("passed", "failed") else "",
                })

        for child in suite.get("suites", []):
            _walk(child)

    for suite in raw.get("suites", []):
        _walk(suite)

    return results


def _parse_cypress(paths: list[Path], env: str) -> list[dict[str, Any]]:
    """Parse Cypress JSON reporter output (cypress run --reporter json)."""
    results: list[dict[str, Any]] = []

    for path in paths:
        if not path.exists():
            warnings.warn(f"[consolidate] Cypress results not found: {path}")
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))

        for suite in raw.get("results", [raw]):
            suite_title = suite.get("fullTitle", suite.get("title", ""))
            for test in suite.get("tests", []):
                title = f"{suite_title} {test.get('fullTitle', test.get('title', ''))}"
                tc = _extract_tc_code(title)
                if not tc:
                    continue

                cy_state = test.get("state", "unknown")  # passed/failed/pending
                duration_ms = int(test.get("duration", 0))

                status = {
                    "passed": "passed",
                    "failed": "failed",
                    "pending": "skipped",  # Mocha pending = skipped
                    "skipped": "skipped",
                }.get(cy_state, "failed")

                if status == "passed" and tc in SOFT_PASS_MARKERS:
                    status = "soft_passed"

                err = test.get("err", {})
                error_msg = err.get("message") if err else None

                results.append({
                    "tc_code": tc,
                    "framework": "cypress",
                    "status": status,
                    "duration_ms": duration_ms,
                    "env": env,
                    "viewport": "375x667",
                    "covered_tt": _extract_tt_codes(title),
                    "error_message": error_msg,
                    "trace_ref": None,
                    "framework_specific_notes": cy_state if cy_state not in ("passed", "failed") else "",
                })

    return results


def _parse_selenium(path: Path, env: str) -> list[dict[str, Any]]:
    """Parse pytest-json-report output (pytest --json-report --json-report-file=...)."""
    if not path.exists():
        warnings.warn(f"[consolidate] Selenium results not found: {path}")
        return []

    raw = json.loads(path.read_text(encoding="utf-8"))
    results: list[dict[str, Any]] = []

    for test in raw.get("tests", []):
        title = test.get("nodeid", "") + " " + test.get("metadata", {}).get("description", "")
        tc = _extract_tc_code(title)
        if not tc:
            continue

        py_outcome = test.get("outcome", "unknown")  # passed/failed/skipped/error
        duration_ms = int(test.get("duration", 0) * 1000)

        status = {
            "passed": "passed",
            "failed": "failed",
            "skipped": "skipped",
            "error": "failed",
        }.get(py_outcome, "failed")

        if status == "passed" and tc in SOFT_PASS_MARKERS:
            status = "soft_passed"

        call_data = test.get("call", {})
        error_msg = call_data.get("longrepr") if call_data else None

        results.append({
            "tc_code": tc,
            "framework": "selenium",
            "status": status,
            "duration_ms": duration_ms,
            "env": env,
            "viewport": "375x667",
            "covered_tt": _extract_tt_codes(title),
            "error_message": str(error_msg)[:300] if error_msg else None,
            "trace_ref": None,
            "framework_specific_notes": py_outcome if py_outcome not in ("passed", "failed") else "",
        })

    return results


# ─── parity analysis ──────────────────────────────────────────────────────────

def _normalize_status(s: str) -> str:
    """Collapse soft_passed → passed for divergence comparison."""
    return "passed" if s == "soft_passed" else s


def _build_parity_report(
    all_results: list[dict[str, Any]],
    env: str,
) -> dict[str, Any]:
    """Build cross-framework parity comparison from merged result list."""
    frameworks = ["playwright", "cypress", "selenium"]

    # Group by TC code × framework → last status wins
    by_tc: dict[str, dict[str, str]] = defaultdict(dict)
    for r in all_results:
        by_tc[r["tc_code"]][r["framework"]] = r["status"]

    # Per-framework summary counts
    fw_summary: dict[str, dict[str, int]] = {
        fw: {"passed": 0, "failed": 0, "skipped": 0, "soft_passed": 0, "missing": 0}
        for fw in frameworks
    }
    for tc, fw_map in by_tc.items():
        for fw in frameworks:
            s = fw_map.get(fw, "missing")
            fw_summary[fw][s] = fw_summary[fw].get(s, 0) + 1

    # Detect divergences: any TC where normalized status differs across frameworks
    divergences: list[dict[str, Any]] = []
    for tc in sorted(by_tc.keys()):
        fw_map = by_tc[tc]
        present = {fw: _normalize_status(fw_map[fw]) for fw in frameworks if fw in fw_map}
        unique_statuses = set(present.values())
        if len(unique_statuses) > 1:
            divergences.append({
                "tc_code": tc,
                "per_framework": fw_map,
                "normalized": present,
            })

    return {
        "generated": str(date.today()),
        "env": env,
        "frameworks": fw_summary,
        "tcs_with_divergence": divergences,
        "all_results": all_results,
    }


# ─── writers ──────────────────────────────────────────────────────────────────

def _write_md(report: dict[str, Any], out_path: Path) -> None:
    """Write human-readable Markdown summary."""
    lines: list[str] = [
        f"# Cross-Framework Parity Report — {report['generated']}",
        "",
        f"**Target:** `{report['env']}`",
        f"**Date:** {report['generated']}",
        "",
        "## Framework summary",
        "",
        "| Framework | passed | soft_passed | skipped | failed | missing |",
        "|-----------|--------|-------------|---------|--------|---------|",
    ]

    for fw, counts in report["frameworks"].items():
        lines.append(
            f"| {fw} | {counts.get('passed',0)} | {counts.get('soft_passed',0)} | "
            f"{counts.get('skipped',0)} | {counts.get('failed',0)} | {counts.get('missing',0)} |"
        )

    div = report["tcs_with_divergence"]
    parity_claim = "✅ **PARITY CONFIRMED** — no divergences" if not div else f"❌ **{len(div)} DIVERGENCE(S) FOUND**"
    lines += [
        "",
        f"## Parity verdict: {parity_claim}",
        "",
    ]

    if div:
        lines += ["| TC code | Playwright | Cypress | Selenium |", "|---------|-----------|---------|----------|"]
        for d in div:
            pf = d["per_framework"]
            lines.append(
                f"| {d['tc_code']} | {pf.get('playwright','—')} | "
                f"{pf.get('cypress','—')} | {pf.get('selenium','—')} |"
            )
        lines.append("")
        lines.append("> Each divergence must be investigated and documented as `BUG-CP-{TC}-FRAMEWORK-DIVERGENCE-{slug}`")

    lines += [
        "",
        "## All TC results",
        "",
        "| TC code | Framework | Status | Duration (ms) | Error |",
        "|---------|-----------|--------|----------------|-------|",
    ]

    for r in sorted(report["all_results"], key=lambda x: (x["tc_code"], x["framework"])):
        err_snip = (r["error_message"] or "")[:60].replace("|", "\\|") if r["error_message"] else "—"
        lines.append(
            f"| {r['tc_code']} | {r['framework']} | {r['status']} | "
            f"{r['duration_ms']} | {err_snip} |"
        )

    lines += [
        "",
        "---",
        "_Generated by `tools/consolidate_results.py` — CP-SUPIN-05_",
    ]

    out_path.write_text("\n".join(lines), encoding="utf-8")


# ─── main ─────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base-url", default="https://demo.bouracka.cz", help="Target env URL")
    parser.add_argument("--pw", default=str(REPO_ROOT / "playwright-report" / "results.json"),
                        help="Playwright results.json path")
    parser.add_argument("--cy", default=str(REPO_ROOT / "cypress" / "cypress-results" / "*.json"),
                        help="Cypress results JSON path (glob OK)")
    parser.add_argument("--se", default=str(REPO_ROOT / "selenium-report" / "results.json"),
                        help="Selenium results.json path (pytest-json-report)")
    parser.add_argument("--out-dir", default=str(REPO_ROOT / "runs"),
                        help="Output directory for reports")
    args = parser.parse_args(argv)

    env = args.base_url
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    today = str(date.today())

    all_results: list[dict[str, Any]] = []

    # Playwright
    all_results.extend(_parse_playwright(Path(args.pw), env))

    # Cypress (supports glob)
    cy_paths = [Path(p) for p in glob.glob(args.cy)] or [Path(args.cy)]
    all_results.extend(_parse_cypress(cy_paths, env))

    # Selenium
    all_results.extend(_parse_selenium(Path(args.se), env))

    if not all_results:
        print("[consolidate] WARNING: no test results found in any framework. "
              "Run tests first, then re-run consolidate.")
        # Write empty-but-valid report so CI doesn't hard-fail
        report = _build_parity_report([], env)
    else:
        report = _build_parity_report(all_results, env)

    json_out = out_dir / f"cross-framework-{today}.json"
    md_out = out_dir / f"cross-framework-{today}.md"

    json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    _write_md(report, md_out)

    div_count = len(report["tcs_with_divergence"])
    print(f"[consolidate] Written: {json_out}")
    print(f"[consolidate] Written: {md_out}")
    print(f"[consolidate] Results: {len(all_results)} entries across "
          f"{len(set(r['framework'] for r in all_results))} framework(s)")
    print(f"[consolidate] Divergences: {div_count} {'— PARITY OK' if div_count == 0 else '— INVESTIGATE'}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
