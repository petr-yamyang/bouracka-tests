#!/usr/bin/env python3
"""
consolidate_results.py — merge per-framework test outputs into cross-framework run record.

CP-SUPIN-05 v0.5.4 — schema migration: emits canonical v0.1 cross-framework
result envelope per `_specs/CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.md`.

Reads (any subset present; missing sources are skipped with a warning):
  playwright-report/results.json          (Playwright JSON reporter output)
  cypress/cypress-results/*.json          (Cypress --reporter json output)
  selenium-report/results.json            (pytest-json-report plugin output)

Writes:
  runs/cross-framework-<env>-<date>.json  (machine-readable, schema v1.0)
  runs/cross-framework-<env>-<date>.md    (human-readable digest)

Usage examples:
  python3 tools/consolidate_results.py --env demo
  python3 tools/consolidate_results.py --env tst --env-url https://tst.bouracka.cz
  python3 tools/consolidate_results.py --base-url https://demo.bouracka.cz
                                            # back-compat: env auto-inferred from URL

Schema reference:
  _specs/CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.md (binding from 2026-05-10)
"""
from __future__ import annotations

import argparse
import datetime as _dt
import glob
import json
import os
import platform
import re
import socket
import subprocess
import sys
import uuid
import warnings
from collections import defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_VERSION = "1.0"
SCRIPT_VERSION = "0.5.4"

# ──────────────────────────────────────────────────────────────────────────
# §1. Constants — TC discovery, env enum, soft-pass markers, drift markers
# ──────────────────────────────────────────────────────────────────────────

ENV_ENUM = ("demo", "tst", "uat", "prod-readonly", "prod-writable")
FRAMEWORK_KEYS = ("playwright", "cypress", "selenium", "playwright-api", "postman")

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
TT_CODE_RE = re.compile(r"TT-[A-Z]+-[a-zA-Z0-9_]+")
# Fallback for Selenium nodeids: test_TC_CP_A2_ALT_7_enumerations -> TC-CP-A2-ALT-7
_NODEID_TC_RE = re.compile(r"::test_(TC(?:_[A-Z0-9]+)+)")
# Drift skip marker prefix per schema spec §4.4
_DRIFT_SKIP_RE = re.compile(r"DRIFT-[A-Z0-9-]+")
# Run-id format: run-<ISO timestamp>-<7-hex>
RUN_ID_RE = re.compile(r"^run-\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z-[0-9a-f]{7}$")

SOFT_PASS_MARKERS = {"TC-CP-A2-ALT-9"}

# Verdict enum (v0.1 schema §3.3)
VERDICT_PASS = "pass"
VERDICT_FAIL = "fail"
VERDICT_SKIP_DRIFT = "skip-drift"
VERDICT_SKIP_OTHER = "skip-other"
VERDICT_SOFT_PASS = "soft-pass"
VERDICT_ERROR = "error"
VERDICT_MISSING = "missing"

# ──────────────────────────────────────────────────────────────────────────
# §2. Per-framework parsers — PRESERVED FROM v0.5.2 with verdict mapping
# ──────────────────────────────────────────────────────────────────────────

def _extract_tc_code(title: str):
    m = TC_CODE_RE.search(title)
    return m.group(0) if m else None


def _extract_tt_codes(title: str, notes: str = ""):
    found = TT_CODE_RE.findall(title + " " + notes)
    return sorted(set(found))


def _classify_skip(skip_reason: str | None) -> str:
    """Map a skip reason string to either skip-drift or skip-other.

    Per schema spec §4.4: fixtures emitting `pytest.skip("DRIFT-...")` /
    cy.log('DRIFT-...') / test.skip(true, 'DRIFT-...') signal a drift skip.
    Anything else is skip-other.
    """
    if skip_reason and _DRIFT_SKIP_RE.search(skip_reason):
        return VERDICT_SKIP_DRIFT
    return VERDICT_SKIP_OTHER


def _map_status(raw: str, tc_code: str, skip_reason: str | None = None) -> str:
    """Map a per-framework raw status to canonical v0.1 verdict enum."""
    if raw in ("passed", "pass"):
        if tc_code in SOFT_PASS_MARKERS:
            return VERDICT_SOFT_PASS
        return VERDICT_PASS
    if raw in ("failed", "fail", "timedOut", "interrupted", "error"):
        return VERDICT_FAIL if raw != "error" else VERDICT_ERROR
    if raw in ("skipped", "skip", "pending"):
        return _classify_skip(skip_reason)
    return VERDICT_ERROR


def _parse_playwright(path: Path):
    if not path.exists():
        warnings.warn(f"[consolidate] Playwright results not found: {path}")
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    results = []

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
                pw_status = last.get("status", "unknown")
                duration_ms = int(last.get("duration", 0))
                # Skip reason — Playwright stores in error.message or annotations
                skip_reason = None
                for ann in test.get("annotations", []) or []:
                    if ann.get("type") == "skip":
                        skip_reason = ann.get("description") or ""
                        break
                error_msg = None
                for er in results_raw:
                    if er.get("error"):
                        error_msg = er["error"].get("message", "")
                        break
                # Evidence
                attachments = last.get("attachments", []) or []
                trace_ref = next((a.get("path") for a in attachments
                                  if a.get("name") == "trace"), None)
                screenshot_ref = next((a.get("path") for a in attachments
                                       if a.get("contentType", "").startswith("image/")), None)
                video_ref = next((a.get("path") for a in attachments
                                  if a.get("contentType", "").startswith("video/")), None)
                results.append({
                    "tc_code": tc,
                    "framework": "playwright",
                    "status": _map_status(pw_status, tc, skip_reason),
                    "raw_status": pw_status,
                    "duration_ms": duration_ms,
                    "covered_tt": _extract_tt_codes(title),
                    "error_message": error_msg,
                    "trace_ref": trace_ref,
                    "screenshot_ref": screenshot_ref,
                    "video_ref": video_ref,
                    "viewport": "375x667",
                })
        for child in suite.get("suites", []):
            _walk(child)

    for suite in raw.get("suites", []):
        _walk(suite)
    return results


def _parse_cypress(paths):
    results = []
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
                cy_state = test.get("state", "unknown")
                duration_ms = int(test.get("duration", 0))
                err = test.get("err", {}) or {}
                error_msg = err.get("message")
                # Cypress skip reason — stored in test.body or err.message for skipped tests
                skip_reason = None
                if cy_state == "pending" or cy_state == "skipped":
                    skip_reason = error_msg or test.get("body", "") or ""
                # Cypress trace not natively produced; videos under cypress/videos/
                video_ref = test.get("video") or None
                screenshot_ref = (test.get("screenshots") or [{}])[0].get("path") if test.get("screenshots") else None
                results.append({
                    "tc_code": tc,
                    "framework": "cypress",
                    "status": _map_status(cy_state, tc, skip_reason),
                    "raw_status": cy_state,
                    "duration_ms": duration_ms,
                    "covered_tt": _extract_tt_codes(title),
                    "error_message": error_msg,
                    "trace_ref": None,
                    "screenshot_ref": screenshot_ref,
                    "video_ref": video_ref,
                    "viewport": "375x667",
                })
    return results


def _parse_selenium(path: Path):
    if not path.exists():
        warnings.warn(f"[consolidate] Selenium results not found: {path}")
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    results = []
    for test in raw.get("tests", []):
        nodeid = test.get("nodeid", "")
        title = nodeid + " " + test.get("metadata", {}).get("description", "")
        tc = _extract_tc_code(title)
        if not tc:
            m = _NODEID_TC_RE.search(nodeid)
            if m:
                tc = m.group(1).replace("_", "-")
        if not tc:
            continue
        py_outcome = test.get("outcome", "unknown")
        duration_ms = int(test.get("duration", 0) * 1000)
        call_data = test.get("call", {})
        error_msg = call_data.get("longrepr") if call_data else None
        # Skip reason — pytest stores in setup.longrepr or call.longrepr for skipped tests
        skip_reason = None
        if py_outcome == "skipped":
            setup = test.get("setup", {}) or {}
            skip_reason = (setup.get("longrepr") or call_data.get("longrepr") or "")
            if isinstance(skip_reason, list) and skip_reason:
                skip_reason = str(skip_reason[-1])
            elif not isinstance(skip_reason, str):
                skip_reason = str(skip_reason)
        # Evidence
        screenshot_ref = (test.get("metadata", {}) or {}).get("screenshot_path")
        results.append({
            "tc_code": tc,
            "framework": "selenium",
            "status": _map_status(py_outcome, tc, skip_reason),
            "raw_status": py_outcome,
            "duration_ms": duration_ms,
            "covered_tt": _extract_tt_codes(title),
            "error_message": str(error_msg)[:300] if error_msg else None,
            "trace_ref": None,
            "screenshot_ref": screenshot_ref,
            "video_ref": None,
            "viewport": "375x667",
        })
    return results


# ──────────────────────────────────────────────────────────────────────────
# §3. Schema construction — pivot flat → nested per-TC envelope
# ──────────────────────────────────────────────────────────────────────────

def _normalize_for_parity(verdict: str) -> str:
    """Per schema §3.5 — collapse soft-pass→pass, error→fail, but keep
    skip-drift and skip-other distinct."""
    if verdict in (VERDICT_PASS, VERDICT_SOFT_PASS):
        return VERDICT_PASS
    if verdict in (VERDICT_FAIL, VERDICT_ERROR):
        return VERDICT_FAIL
    return verdict  # skip-drift, skip-other unchanged


def _compute_parity_status(verdicts: dict[str, str]) -> str:
    """Per schema §3.4."""
    present = [v for v in verdicts.values() if v != VERDICT_MISSING]
    if not present:
        raise ValueError("No framework ran this TC — invalid run shape")
    if len(present) == 1:
        return "not-applicable"
    normalized = {_normalize_for_parity(v) for v in present}
    return "agree" if len(normalized) == 1 else "divergence"


def _pivot_to_nested(flat_results: list[dict], frameworks: list[str]) -> list[dict]:
    """Pivot flat per-(fw,tc) rows into nested per-TC verdict envelopes."""
    by_tc: dict[str, dict[str, dict]] = defaultdict(dict)
    for r in flat_results:
        by_tc[r["tc_code"]][r["framework"]] = r

    nested = []
    for tc_code in sorted(by_tc.keys()):
        per_fw = by_tc[tc_code]
        verdicts = {}
        durations = {}
        evidence = {}
        error_messages = {}
        framework_specific_notes = {}
        covered_tt_set: set[str] = set()
        viewports = []
        soft_pass_reason = None
        for fw in frameworks:
            r = per_fw.get(fw)
            if r is None:
                verdicts[fw] = VERDICT_MISSING
                durations[fw] = 0
                evidence[fw] = {"trace_ref": None, "screenshot_ref": None, "video_ref": None}
                error_messages[fw] = None
                framework_specific_notes[fw] = ""
                continue
            verdicts[fw] = r["status"]
            durations[fw] = r["duration_ms"]
            evidence[fw] = {
                "trace_ref": r.get("trace_ref"),
                "screenshot_ref": r.get("screenshot_ref"),
                "video_ref": r.get("video_ref"),
            }
            error_messages[fw] = r.get("error_message")
            raw = r.get("raw_status", "")
            framework_specific_notes[fw] = raw if raw not in ("passed", "failed", "pass", "fail") else ""
            covered_tt_set.update(r.get("covered_tt", []))
            if r.get("viewport"):
                viewports.append(r["viewport"])
            if r["status"] == VERDICT_SOFT_PASS and not soft_pass_reason:
                soft_pass_reason = f"TC marked soft-pass per SOFT_PASS_MARKERS (tc={tc_code})"

        nested.append({
            "tc_code": tc_code,
            "verdicts": verdicts,
            "parity_status": _compute_parity_status(verdicts),
            "duration_ms": durations,
            "evidence": evidence,
            "covered_tt": sorted(covered_tt_set),
            "error_messages": error_messages,
            "framework_specific_notes": framework_specific_notes,
            "viewport": viewports[0] if viewports else None,
            "bug_ref": None,
            "soft_pass_reason": soft_pass_reason,
        })
    return nested


def _compute_summary(nested_results: list[dict]) -> dict:
    """Per schema §3.6."""
    total = len(nested_results)
    if total == 0:
        return {
            "total_tcs": 0,
            "passed": 0, "failed": 0, "skipped": 0, "soft_passed": 0,
            "drift_skip_count": 0,
            "parity_pass_count": 0, "parity_divergence_count": 0,
            "pass_rate_strict": None,
            "pass_rate_drift_aware": None,
        }

    def present_verdicts(r):
        return {v for v in r["verdicts"].values() if v != VERDICT_MISSING}

    passed = sum(1 for r in nested_results
                 if present_verdicts(r) <= {VERDICT_PASS, VERDICT_SOFT_PASS}
                 and present_verdicts(r))
    failed = sum(1 for r in nested_results
                 if present_verdicts(r) & {VERDICT_FAIL, VERDICT_ERROR})
    skipped = sum(1 for r in nested_results
                  if present_verdicts(r) <= {VERDICT_SKIP_DRIFT, VERDICT_SKIP_OTHER}
                  and present_verdicts(r))
    soft_passed = sum(1 for r in nested_results
                      if present_verdicts(r) == {VERDICT_SOFT_PASS})
    drift_skip = sum(1 for r in nested_results
                     if present_verdicts(r) == {VERDICT_SKIP_DRIFT})
    parity_pass = sum(1 for r in nested_results if r["parity_status"] == "agree")
    parity_diverge = sum(1 for r in nested_results if r["parity_status"] == "divergence")

    return {
        "total_tcs": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "soft_passed": soft_passed,
        "drift_skip_count": drift_skip,
        "parity_pass_count": parity_pass,
        "parity_divergence_count": parity_diverge,
        "pass_rate_strict": round(passed / total, 2),
        "pass_rate_drift_aware": round((passed + drift_skip) / total, 2),
    }


# ──────────────────────────────────────────────────────────────────────────
# §4. Run identity + host capture
# ──────────────────────────────────────────────────────────────────────────

def _utc_now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _generate_run_id(started_at_iso: str | None = None) -> str:
    ts = started_at_iso or _utc_now_iso()
    short = uuid.uuid4().hex[:7]
    # Try git short hash for traceability; fall back to uuid
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short=7", "HEAD"],
            cwd=str(REPO_ROOT), stderr=subprocess.DEVNULL,
        ).decode().strip()
        if re.fullmatch(r"[0-9a-f]{7}", out):
            short = out
    except Exception:
        pass
    return f"run-{ts}-{short}"


def _capture_host() -> dict:
    host = {
        "os": f"{platform.system()}-{platform.release()}",
        "host": socket.gethostname() or "unknown",
        "git_commit": None,
        "git_branch": None,
        "tool_versions": None,
    }
    try:
        host["git_commit"] = subprocess.check_output(
            ["git", "rev-parse", "--short=7", "HEAD"],
            cwd=str(REPO_ROOT), stderr=subprocess.DEVNULL,
        ).decode().strip() or None
        host["git_branch"] = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=str(REPO_ROOT), stderr=subprocess.DEVNULL,
        ).decode().strip() or None
    except Exception:
        pass
    return host


def _infer_env_from_url(url: str) -> str | None:
    """Best-effort extraction of env tag from base URL hostname.

    Maps demo.bouracka.cz → demo; tst.bouracka.cz → tst; etc. Returns
    None if no recognizable env-prefix in the hostname."""
    if not url:
        return None
    m = re.match(r"^https?://([a-z0-9-]+)\.bouracka\.cz", url, re.IGNORECASE)
    if not m:
        return None
    sub = m.group(1).lower()
    if sub in ENV_ENUM:
        return sub
    return None


# ──────────────────────────────────────────────────────────────────────────
# §5. Producer-side validation per schema §5.1
# ──────────────────────────────────────────────────────────────────────────

def _validate_envelope(env: dict) -> None:
    """Raise AssertionError with descriptive message if envelope is invalid."""
    assert env["schema_version"] == SCHEMA_VERSION, \
        f"schema_version must be {SCHEMA_VERSION!r}, got {env['schema_version']!r}"
    assert RUN_ID_RE.match(env["run_id"]), \
        f"run_id format invalid: {env['run_id']!r}"
    assert env["env"] in ENV_ENUM, \
        f"env must be one of {ENV_ENUM}, got {env['env']!r}"
    assert env["started_at"] <= env["ended_at"], \
        f"started_at ({env['started_at']}) must be ≤ ended_at ({env['ended_at']})"
    assert env["frameworks"] == sorted(set(env["frameworks"])), \
        "frameworks must be sorted ascending and deduplicated"
    assert len(env["results"]) == env["summary"]["total_tcs"], \
        f"len(results)={len(env['results'])} != summary.total_tcs={env['summary']['total_tcs']}"
    fw_set = set(env["frameworks"])
    for r in env["results"]:
        assert TC_CODE_RE.fullmatch(r["tc_code"]) or r["tc_code"].startswith("TC-"), \
            f"tc_code format: {r['tc_code']!r}"
        assert set(r["verdicts"].keys()) <= fw_set | {"playwright", "cypress", "selenium"}, \
            f"verdicts keys not subset of frameworks for {r['tc_code']}"
        expected_parity = _compute_parity_status(r["verdicts"])
        assert r["parity_status"] == expected_parity, \
            f"parity_status mismatch for {r['tc_code']}: {r['parity_status']!r} != {expected_parity!r}"
        if any(v == VERDICT_SOFT_PASS for v in r["verdicts"].values()):
            assert r.get("soft_pass_reason"), \
                f"soft_pass_reason required for {r['tc_code']} (verdict has soft-pass)"


# ──────────────────────────────────────────────────────────────────────────
# §6. Markdown digest
# ──────────────────────────────────────────────────────────────────────────

def _verdict_glyph(v: str) -> str:
    return {
        VERDICT_PASS: "PASS",
        VERDICT_FAIL: "FAIL",
        VERDICT_SKIP_DRIFT: "SKIP-d",
        VERDICT_SKIP_OTHER: "SKIP-o",
        VERDICT_SOFT_PASS: "PASS-soft",
        VERDICT_ERROR: "ERROR",
        VERDICT_MISSING: "—",
    }.get(v, v)


def _parity_glyph(p: str) -> str:
    return {"agree": "OK", "divergence": "DIVERGE", "not-applicable": "n/a"}.get(p, p)


def _write_md(envelope: dict, out_path: Path) -> None:
    s = envelope["summary"]
    lines = [
        f"# Bouračka {envelope['env']} — Test Run {envelope['started_at']}",
        "",
        f"**Run ID:** `{envelope['run_id']}`",
        f"**Env URL:** {envelope.get('env_url') or '(not set)'}",
        f"**Duration:** {envelope['duration_ms']} ms ({envelope['started_at']} → {envelope['ended_at']})",
        f"**Frameworks:** {', '.join(envelope['frameworks'])}",
        "",
        f"**Pass rate:** {s['passed']}/{s['total_tcs']} strict "
        f"({s['pass_rate_strict']}); "
        f"under drift-guard: {s['pass_rate_drift_aware']}",
        f"**Parity:** {s['parity_pass_count']}/{s['total_tcs']} agree, "
        f"{s['parity_divergence_count']} divergence(s)",
        "",
        "## Result matrix",
        "",
    ]
    fw_cols = envelope["frameworks"]
    header = "| TC | " + " | ".join(fw_cols) + " | parity |"
    sep = "|" + "---|" * (len(fw_cols) + 2)
    lines += [header, sep]
    for r in envelope["results"]:
        row = [r["tc_code"]]
        for fw in fw_cols:
            row.append(_verdict_glyph(r["verdicts"].get(fw, VERDICT_MISSING)))
        row.append(_parity_glyph(r["parity_status"]))
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", "## Failures (this run)", ""]
    failures = [r for r in envelope["results"]
                if any(v in (VERDICT_FAIL, VERDICT_ERROR) for v in r["verdicts"].values())]
    if not failures:
        lines.append("(none)")
    else:
        lines += ["| TC | Framework | Error |", "|---|---|---|"]
        for r in failures:
            for fw, v in r["verdicts"].items():
                if v in (VERDICT_FAIL, VERDICT_ERROR):
                    err = (r["error_messages"].get(fw) or "").replace("\n", " ").replace("|", "\\|")[:120]
                    lines.append(f"| {r['tc_code']} | {fw} | {err or '(no message)'} |")
    df = envelope.get("drift_forensic")
    if df and df.get("active"):
        lines += [
            "",
            "## Drift forensic",
            "",
            f"- Type: {df.get('drift_type')}",
            f"- Affected TCs: {', '.join(df.get('affected_tcs', []))}",
            f"- Notes: {df.get('notes', '')}",
        ]
    lines += [
        "",
        "## Provenance",
        "",
        f"- Host: {envelope['host']['os']} on {envelope['host']['host']}",
        f"- Git: {envelope['host'].get('git_branch') or '(no branch)'} @ {envelope['host'].get('git_commit') or '(no commit)'}",
        f"- Reporter: `{envelope['reporter']['command']}` (trigger: {envelope['reporter']['trigger']})",
        "",
        "---",
        f"_Generated by tools/consolidate_results.py v{SCRIPT_VERSION} — schema v{SCHEMA_VERSION}_",
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ──────────────────────────────────────────────────────────────────────────
# §7. Drift-forensic synthesis (best-effort from selenium skip reasons)
# ──────────────────────────────────────────────────────────────────────────

def _synthesize_drift_forensic(flat_results: list[dict]) -> dict | None:
    """Build drift_forensic block from any DRIFT-* skip markers in flat results."""
    drift_tcs = set()
    drift_types = set()
    correlation_id = None
    for r in flat_results:
        if r["status"] == VERDICT_SKIP_DRIFT:
            drift_tcs.add(r["tc_code"])
            err = r.get("error_message") or ""
            m = _DRIFT_SKIP_RE.search(err)
            if m:
                drift_types.add(m.group(0))
            mc = re.search(r"correlation_id=([0-9a-f-]+)", err, re.IGNORECASE)
            if mc and not correlation_id:
                correlation_id = mc.group(1)
    if not drift_tcs:
        return None
    drift_type = "recaptcha-v3"  # default; refine via marker parse
    for dt in drift_types:
        low = dt.lower()
        if "recaptcha-v2" in low:
            drift_type = "recaptcha-v2"
            break
        if "recaptcha-v3" in low:
            drift_type = "recaptcha-v3"
            break
        if "rate-limit" in low:
            drift_type = "rate-limit"
            break
    return {
        "active": True,
        "drift_type": drift_type,
        "trigger_correlation": correlation_id,
        "affected_tcs": sorted(drift_tcs),
        "guard_policy": "skip-on-drift",
        "notes": f"{len(drift_tcs)} TC(s) skipped via drift guard",
    }


# ──────────────────────────────────────────────────────────────────────────
# §8. Main
# ──────────────────────────────────────────────────────────────────────────

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Consolidate per-framework test outputs into v0.1 schema envelope.",
    )
    parser.add_argument("--env", choices=ENV_ENUM, default=None,
                        help=f"environment tag (one of {ENV_ENUM}); auto-inferred from URL if omitted")
    parser.add_argument("--env-url", default=None,
                        help="canonical env URL (e.g. https://demo.bouracka.cz)")
    parser.add_argument("--base-url", default="https://demo.bouracka.cz",
                        help="back-compat alias for --env-url")
    parser.add_argument("--run-id", default=None,
                        help=f"run id (regex {RUN_ID_RE.pattern}); auto-generated if omitted")
    parser.add_argument("--pw", default=str(REPO_ROOT / "playwright-report" / "results.json"))
    parser.add_argument("--cy", default=str(REPO_ROOT / "cypress" / "cypress-results" / "*.json"))
    parser.add_argument("--se", default=str(REPO_ROOT / "selenium-report" / "results.json"))
    parser.add_argument("--out-dir", default=str(REPO_ROOT / "runs"))
    parser.add_argument("--reporter-command", default=" ".join(sys.argv),
                        help="command that produced this run (free-string; goes into reporter.command)")
    parser.add_argument("--trigger", choices=("manual", "ci", "scheduled", "api"),
                        default="manual")
    parser.add_argument("--ci-run-id", default=None)
    args = parser.parse_args(argv)

    started_at = _utc_now_iso()

    env_url = args.env_url or args.base_url
    env = args.env or _infer_env_from_url(env_url)
    if env is None:
        print(f"[consolidate] ERROR: --env required and could not be inferred from URL {env_url!r}",
              file=sys.stderr)
        return 2

    run_id = args.run_id or _generate_run_id(started_at)
    if not RUN_ID_RE.match(run_id):
        print(f"[consolidate] ERROR: --run-id format invalid: {run_id!r}", file=sys.stderr)
        return 2

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    flat_results: list[dict] = []
    flat_results.extend(_parse_playwright(Path(args.pw)))
    cy_paths = [Path(p) for p in glob.glob(args.cy)] or [Path(args.cy)]
    flat_results.extend(_parse_cypress(cy_paths))
    flat_results.extend(_parse_selenium(Path(args.se)))

    frameworks_present = sorted({r["framework"] for r in flat_results})
    if not frameworks_present:
        print("[consolidate] WARNING: no test results found in any framework.")

    nested = _pivot_to_nested(flat_results, frameworks_present)
    summary = _compute_summary(nested)
    drift = _synthesize_drift_forensic(flat_results)

    ended_at = _utc_now_iso()
    duration_ms = int(
        (_dt.datetime.fromisoformat(ended_at.replace("Z", "+00:00"))
         - _dt.datetime.fromisoformat(started_at.replace("Z", "+00:00"))).total_seconds() * 1000
    )

    envelope = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "env": env,
        "env_url": env_url,
        "started_at": started_at,
        "ended_at": ended_at,
        "duration_ms": duration_ms,
        "frameworks": frameworks_present,
        "results": nested,
        "summary": summary,
        "host": _capture_host(),
        "drift_forensic": drift,
        "reporter": {
            "command": args.reporter_command,
            "trigger": args.trigger,
            "ci_run_id": args.ci_run_id,
            "operator": os.environ.get("USER") or os.environ.get("USERNAME") or "unknown",
        },
    }

    # Producer-side validation per schema §5.1
    try:
        _validate_envelope(envelope)
    except AssertionError as e:
        print(f"[consolidate] SCHEMA VIOLATION: {e}", file=sys.stderr)
        return 3

    today = started_at.split("T")[0]
    json_out = out_dir / f"cross-framework-{env}-{today}.json"
    md_out = out_dir / f"cross-framework-{env}-{today}.md"
    json_out.write_text(json.dumps(envelope, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    _write_md(envelope, md_out)

    print(f"[consolidate] schema_version: {SCHEMA_VERSION}  run_id: {run_id}")
    print(f"[consolidate] env: {env}  frameworks: {frameworks_present}  TCs: {summary['total_tcs']}")
    print(f"[consolidate] verdicts:  passed={summary['passed']}  failed={summary['failed']}  "
          f"skipped={summary['skipped']} (drift={summary['drift_skip_count']})  "
          f"soft={summary['soft_passed']}")
    print(f"[consolidate] parity:    agree={summary['parity_pass_count']}  "
          f"diverge={summary['parity_divergence_count']}")
    print(f"[consolidate] written:   {json_out}")
    print(f"[consolidate] written:   {md_out}")
    return 0 if summary["parity_divergence_count"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
