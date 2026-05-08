#!/usr/bin/env python3
"""
consolidate_results.py -- merge per-framework test outputs into cross-framework comparison.

CP-SUPIN-05 v0.5.2 -- cross-framework parity consolidation tool.

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
# Fallback for Selenium nodeids: test_TC_CP_A2_ALT_7_enumerations -> TC-CP-A2-ALT-7
_NODEID_TC_RE = re.compile(r"::test_(TC(?:_[A-Z0-9]+)+)")

SOFT_PASS_MARKERS = {"TC-CP-A2-ALT-9"}


def _extract_tc_code(title: str):
    m = TC_CODE_RE.search(title)
    return m.group(0) if m else None


def _extract_tt_codes(title: str, notes: str = ""):
    found = TT_CODE_RE.findall(title + " " + notes)
    return sorted(set(found))


def _parse_playwright(path: Path, env: str):
    if not path.exists():
        warnings.warn(f"[consolidate] Playwright results not found: {path}")
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    results = []

    def _walk(suite):
        for spec in suite.get("specs", []):
            for test in spec.get("tests", []):
                title = " ".join([suite.get("title",""), spec.get("title",""), test.get("title","")])
                tc = _extract_tc_code(title)
                if not tc:
                    continue
                results_raw = test.get("results", [{}])
                last = results_raw[-1] if results_raw else {}
                pw_status = last.get("status", "unknown")
                duration_ms = last.get("duration", 0)
                status = {"passed":"passed","failed":"failed","skipped":"skipped","timedOut":"failed","interrupted":"failed"}.get(pw_status, "failed")
                if status == "passed" and tc in SOFT_PASS_MARKERS:
                    status = "soft_passed"
                error_msg = None
                for er in results_raw:
                    if er.get("error"):
                        error_msg = er["error"].get("message","")
                        break
                results.append({"tc_code":tc,"framework":"playwright","status":status,"duration_ms":int(duration_ms),"env":env,"viewport":"375x667","covered_tt":_extract_tt_codes(title),"error_message":error_msg,"trace_ref":last.get("attachments",[{}])[0].get("path") if last.get("attachments") else None,"framework_specific_notes":pw_status if pw_status not in ("passed","failed") else ""})
        for child in suite.get("suites", []):
            _walk(child)

    for suite in raw.get("suites", []):
        _walk(suite)
    return results


def _parse_cypress(paths, env: str):
    results = []
    for path in paths:
        if not path.exists():
            warnings.warn(f"[consolidate] Cypress results not found: {path}")
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        for suite in raw.get("results", [raw]):
            suite_title = suite.get("fullTitle", suite.get("title",""))
            for test in suite.get("tests", []):
                title = f"{suite_title} {test.get('fullTitle', test.get('title',''))}"
                tc = _extract_tc_code(title)
                if not tc:
                    continue
                cy_state = test.get("state","unknown")
                duration_ms = int(test.get("duration", 0))
                status = {"passed":"passed","failed":"failed","pending":"skipped","skipped":"skipped"}.get(cy_state, "failed")
                if status == "passed" and tc in SOFT_PASS_MARKERS:
                    status = "soft_passed"
                err = test.get("err", {})
                error_msg = err.get("message") if err else None
                results.append({"tc_code":tc,"framework":"cypress","status":status,"duration_ms":duration_ms,"env":env,"viewport":"375x667","covered_tt":_extract_tt_codes(title),"error_message":error_msg,"trace_ref":None,"framework_specific_notes":cy_state if cy_state not in ("passed","failed") else ""})
    return results


def _parse_selenium(path: Path, env: str):
    if not path.exists():
        warnings.warn(f"[consolidate] Selenium results not found: {path}")
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    results = []
    for test in raw.get("tests", []):
        nodeid = test.get("nodeid","")
        title = nodeid + " " + test.get("metadata",{}).get("description","")
        tc = _extract_tc_code(title)
        if not tc:
            m = _NODEID_TC_RE.search(nodeid)
            if m:
                tc = m.group(1).replace("_", "-")
        if not tc:
            continue
        py_outcome = test.get("outcome","unknown")
        duration_ms = int(test.get("duration", 0) * 1000)
        status = {"passed":"passed","failed":"failed","skipped":"skipped","error":"failed"}.get(py_outcome, "failed")
        if status == "passed" and tc in SOFT_PASS_MARKERS:
            status = "soft_passed"
        call_data = test.get("call", {})
        error_msg = call_data.get("longrepr") if call_data else None
        results.append({"tc_code":tc,"framework":"selenium","status":status,"duration_ms":duration_ms,"env":env,"viewport":"375x667","covered_tt":_extract_tt_codes(title),"error_message":str(error_msg)[:300] if error_msg else None,"trace_ref":None,"framework_specific_notes":py_outcome if py_outcome not in ("passed","failed") else ""})
    return results


def _normalize_status(s: str) -> str:
    return "passed" if s == "soft_passed" else s


def _build_parity_report(all_results, env: str):
    frameworks = ["playwright", "cypress", "selenium"]
    by_tc = defaultdict(dict)
    for r in all_results:
        by_tc[r["tc_code"]][r["framework"]] = r["status"]
    fw_summary = {fw: {"passed":0,"failed":0,"skipped":0,"soft_passed":0,"missing":0} for fw in frameworks}
    for tc, fw_map in by_tc.items():
        for fw in frameworks:
            s = fw_map.get(fw, "missing")
            fw_summary[fw][s] = fw_summary[fw].get(s, 0) + 1
    divergences = []
    for tc in sorted(by_tc.keys()):
        fw_map = by_tc[tc]
        present = {fw: _normalize_status(fw_map[fw]) for fw in frameworks if fw in fw_map}
        if len(set(present.values())) > 1:
            divergences.append({"tc_code":tc,"per_framework":fw_map,"normalized":present})
    return {"generated":str(date.today()),"env":env,"frameworks":fw_summary,"tcs_with_divergence":divergences,"all_results":all_results}


def _write_md(report, out_path: Path):
    lines = [
        f"# Cross-Framework Parity Report -- {report['generated']}",
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
        lines.append(f"| {fw} | {counts.get('passed',0)} | {counts.get('soft_passed',0)} | {counts.get('skipped',0)} | {counts.get('failed',0)} | {counts.get('missing',0)} |")
    div = report["tcs_with_divergence"]
    parity_claim = "PARITY CONFIRMED -- no divergences" if not div else f"{len(div)} DIVERGENCE(S) FOUND"
    lines += ["", f"## Parity verdict: {parity_claim}", ""]
    if div:
        lines += ["| TC code | Playwright | Cypress | Selenium |", "|---------|-----------|---------|----------|"]
        for d in div:
            pf = d["per_framework"]
            lines.append(f"| {d['tc_code']} | {pf.get('playwright','--')} | {pf.get('cypress','--')} | {pf.get('selenium','--')} |")
        lines += ["", "> Each divergence must be investigated and documented as BUG-CP-{TC}-FRAMEWORK-DIVERGENCE-{slug}"]
    lines += ["", "## All TC results", "", "| TC code | Framework | Status | Duration (ms) | Error |", "|---------|-----------|--------|----------------|-------|"]
    for r in sorted(report["all_results"], key=lambda x: (x["tc_code"], x["framework"])):
        err_snip = (r["error_message"] or "")[:60].replace("|","\\|") if r["error_message"] else "--"
        lines.append(f"| {r['tc_code']} | {r['framework']} | {r['status']} | {r['duration_ms']} | {err_snip} |")
    lines += ["", "---", "_Generated by tools/consolidate_results.py -- CP-SUPIN-05_"]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="https://demo.bouracka.cz")
    parser.add_argument("--pw", default=str(REPO_ROOT / "playwright-report" / "results.json"))
    parser.add_argument("--cy", default=str(REPO_ROOT / "cypress" / "cypress-results" / "*.json"))
    parser.add_argument("--se", default=str(REPO_ROOT / "selenium-report" / "results.json"))
    parser.add_argument("--out-dir", default=str(REPO_ROOT / "runs"))
    args = parser.parse_args(argv)

    env = args.base_url
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    today = str(date.today())
    all_results = []
    all_results.extend(_parse_playwright(Path(args.pw), env))
    cy_paths = [Path(p) for p in glob.glob(args.cy)] or [Path(args.cy)]
    all_results.extend(_parse_cypress(cy_paths, env))
    all_results.extend(_parse_selenium(Path(args.se), env))

    if not all_results:
        print("[consolidate] WARNING: no test results found in any framework.")
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
    print(f"[consolidate] Results: {len(all_results)} entries across {len(set(r['framework'] for r in all_results))} framework(s)")
    print(f"[consolidate] Divergences: {div_count} {'-- PARITY OK' if div_count == 0 else '-- INVESTIGATE'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
