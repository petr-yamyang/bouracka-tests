#!/usr/bin/env python3
"""int_recon.py — active SOAP-endpoint recon harness for D8WS / D5WS.

Purpose
-------
When placed on a SUPIN-internal host with reach to 172.16.1.13 and run
against the test/prod D8WS+D5WS endpoints, this script probes:

  1. TCP reachability  (low-level socket connect)
  2. HTTP HEAD / GET   (does anything answer at this URL?)
  3. WSDL retrieval    (GET ?wsdl, parse targetNamespace + operations)
  4. SOAP minimal envelope (empty body) -> elicits structured fault
                          to confirm endpoint is alive + flavour-check it

Output
------
Two files under ./outputs/, named with hostname + ISO timestamp:
  RECON-<hostname>-<ts>.json   machine-parseable (Claude ingestion)
  RECON-<hostname>-<ts>.md     human-readable (Pete review)

Stdlib-only (Python 3.8+). NO third-party deps. NO destructive operations.
All probes are read-only / GET-shaped, with one fault-eliciting POST.

Usage
-----
  # Probe everything, write reports, exit (one-shot)
  python int_recon.py probe-all

  # Interactive menu (recommended on first run)
  python int_recon.py menu

  # Probe one target only (TCP + WSDL + SOAP-fault elicit)
  python int_recon.py probe --target D8WS-TST
  python int_recon.py probe --target D5WS-STD

  # List available targets
  python int_recon.py list

  # Show last generated report path
  python int_recon.py last-report

Targets are configured in targets.json (sibling file).

Author: Pete Y. / Claude (2026-05-13).
License: SUPIN internal use.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import socket
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
TARGETS_FILE = SCRIPT_DIR / "targets.json"
OUTPUTS_DIR = SCRIPT_DIR / "outputs"
LAST_REPORT_MARKER = OUTPUTS_DIR / ".last-report"

# How many bytes of response body to embed verbatim in the report.
EXCERPT_HEAD_BYTES = 2048
EXCERPT_TAIL_BYTES = 1024

# Per-probe timeouts (seconds). Keep generous for SUPIN-internal latency.
TCP_TIMEOUT_S = 5.0
HTTP_TIMEOUT_S = 10.0

# SOAP minimal envelope — empty body — designed to elicit a structured fault
# from any well-formed SOAP service while not posting any payload.
SOAP_MINIMAL_ENVELOPE = b"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Header/>
  <soapenv:Body/>
</soapenv:Envelope>"""

# WSDL targetNamespace extraction (lightweight, no XSD validation)
WSDL_NS = "{http://schemas.xmlsoap.org/wsdl/}"
SOAPENV_NS = "{http://schemas.xmlsoap.org/soap/envelope/}"


# ---------------------------------------------------------------------------
# Utility — output helpers
# ---------------------------------------------------------------------------

def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def now_compact_local() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def banner(msg: str, char: str = "=") -> None:
    print()
    print(char * 72)
    print(f"  {msg}")
    print(char * 72)


def step(msg: str) -> None:
    print(f"[..] {msg}")


def ok(msg: str) -> None:
    print(f"[OK] {msg}")


def warn(msg: str) -> None:
    print(f"[!!] {msg}")


def fail(msg: str) -> None:
    print(f"[XX] {msg}")


def section(msg: str) -> None:
    print(f"\n--- {msg} ---")


# ---------------------------------------------------------------------------
# Targets loader
# ---------------------------------------------------------------------------

def load_targets() -> list[dict[str, Any]]:
    if not TARGETS_FILE.exists():
        fail(f"targets file missing: {TARGETS_FILE}")
        sys.exit(2)
    with TARGETS_FILE.open(encoding="utf-8") as f:
        data = json.load(f)
    return data["targets"]


# ---------------------------------------------------------------------------
# Host environment introspection
# ---------------------------------------------------------------------------

def host_env() -> dict[str, Any]:
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = None
    return {
        "hostname": hostname,
        "local_ip_best_guess": local_ip,
        "os": platform.system(),
        "os_release": platform.release(),
        "python_version": platform.python_version(),
        "run_at_iso": now_iso(),
        "supin_internal_indicator": (
            "172.16." in (local_ip or "") or "10." in (local_ip or "")
        ),
    }


# ---------------------------------------------------------------------------
# Probe implementations
# ---------------------------------------------------------------------------

def probe_tcp(host: str, port: int) -> dict[str, Any]:
    """Low-level TCP handshake. PASS = connect, FAIL = refused/timeout/dns."""
    started = time.time()
    rec: dict[str, Any] = {
        "probe_id": "tcp_connect",
        "host": host,
        "port": port,
        "started_at": now_iso(),
    }
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TCP_TIMEOUT_S)
        sock.connect((host, port))
        sock.close()
        rec["verdict"] = "PASS"
        rec["details"] = f"TCP handshake completed in {round((time.time()-started)*1000)}ms"
    except socket.timeout:
        rec["verdict"] = "FAIL"
        rec["details"] = f"timeout after {TCP_TIMEOUT_S}s (firewall? unreachable subnet?)"
    except socket.gaierror as e:
        rec["verdict"] = "FAIL"
        rec["details"] = f"DNS resolution failed: {e}"
    except ConnectionRefusedError:
        rec["verdict"] = "FAIL"
        rec["details"] = "connection refused (port closed; service down?)"
    except OSError as e:
        rec["verdict"] = "FAIL"
        rec["details"] = f"OS error: {e}"
    rec["duration_ms"] = int((time.time() - started) * 1000)
    return rec


def _http_request(
    method: str,
    url: str,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Internal HTTP helper. Returns dict with status / headers / body bytes."""
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    ctx = ssl.create_default_context()
    # SUPIN-internal certs may be self-signed; tolerate for recon but flag.
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    started = time.time()
    rec: dict[str, Any] = {
        "method": method,
        "url": url,
        "started_at": now_iso(),
    }
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_S, context=ctx) as resp:
            body = resp.read()
            rec["http_status"] = resp.status
            rec["response_headers"] = {k.lower(): v for k, v in resp.headers.items()}
            rec["response_bytes"] = len(body)
            rec["response_sha256"] = hashlib.sha256(body).hexdigest()
            rec["response_excerpt_head"] = body[:EXCERPT_HEAD_BYTES].decode(
                "utf-8", errors="replace"
            )
            if len(body) > EXCERPT_HEAD_BYTES + EXCERPT_TAIL_BYTES:
                rec["response_excerpt_tail"] = body[-EXCERPT_TAIL_BYTES:].decode(
                    "utf-8", errors="replace"
                )
                rec["body_truncated"] = True
            else:
                rec["response_excerpt_tail"] = None
                rec["body_truncated"] = False
            rec["raw_body_for_parse"] = body  # consumed by caller, stripped before JSON dump
    except urllib.error.HTTPError as e:
        # 4xx / 5xx — still useful! Capture body.
        body = e.read() if hasattr(e, "read") else b""
        rec["http_status"] = e.code
        rec["response_headers"] = {k.lower(): v for k, v in (e.headers or {}).items()}
        rec["response_bytes"] = len(body)
        rec["response_sha256"] = hashlib.sha256(body).hexdigest() if body else None
        rec["response_excerpt_head"] = body[:EXCERPT_HEAD_BYTES].decode("utf-8", errors="replace")
        rec["response_excerpt_tail"] = None
        rec["body_truncated"] = False
        rec["raw_body_for_parse"] = body
        rec["http_error_reason"] = e.reason
    except urllib.error.URLError as e:
        rec["http_status"] = None
        rec["transport_error"] = str(e.reason)
        rec["raw_body_for_parse"] = b""
    except Exception as e:
        rec["http_status"] = None
        rec["transport_error"] = f"{type(e).__name__}: {e}"
        rec["raw_body_for_parse"] = b""
    rec["duration_ms"] = int((time.time() - started) * 1000)
    return rec


def probe_http_head(url: str) -> dict[str, Any]:
    rec = _http_request("HEAD", url)
    rec["probe_id"] = "http_head"
    if rec.get("http_status") is not None:
        rec["verdict"] = "PASS" if rec["http_status"] < 500 else "INCONCLUSIVE"
        rec["details"] = f"HTTP {rec['http_status']} in {rec['duration_ms']}ms"
    else:
        rec["verdict"] = "FAIL"
        rec["details"] = rec.get("transport_error", "no response")
    rec.pop("raw_body_for_parse", None)
    return rec


def probe_wsdl(url_base: str) -> dict[str, Any]:
    """GET <url_base>?wsdl, parse targetNamespace + operation names."""
    sep = "&" if "?" in url_base else "?"
    wsdl_url = f"{url_base.rstrip('/')}{sep}wsdl"
    rec = _http_request("GET", wsdl_url)
    rec["probe_id"] = "wsdl_get"
    body = rec.pop("raw_body_for_parse", b"")

    if rec.get("http_status") != 200:
        rec["verdict"] = "FAIL"
        rec["details"] = (
            f"WSDL fetch returned HTTP {rec.get('http_status')}"
            if rec.get("http_status")
            else f"WSDL fetch failed: {rec.get('transport_error')}"
        )
        return rec

    # Try parse as WSDL
    try:
        root = ET.fromstring(body)
        rec["wsdl_target_namespace"] = root.get("targetNamespace")
        ops: list[str] = []
        for op in root.iter(f"{WSDL_NS}operation"):
            name = op.get("name")
            if name and name not in ops:
                ops.append(name)
        rec["wsdl_operations"] = ops
        rec["wsdl_root_tag"] = root.tag
        rec["verdict"] = "PASS"
        rec["details"] = (
            f"WSDL parsed: targetNamespace={rec['wsdl_target_namespace']}, "
            f"operations={ops}"
        )
    except ET.ParseError as e:
        rec["verdict"] = "INCONCLUSIVE"
        rec["details"] = (
            f"HTTP 200 but body is not parseable WSDL XML: {e}. "
            f"Possibly an HTML landing page or non-WSDL ?wsdl handler."
        )
    return rec


def probe_soap_fault_elicit(url: str) -> dict[str, Any]:
    """POST a minimal empty-body SOAP envelope to elicit a structured fault.

    A healthy SOAP endpoint will return HTTP 500 + SOAP fault XML.
    A dead endpoint will return HTTP 404 / connection refused.
    An HTTP service that doesn't speak SOAP will return HTTP 400 or 415.
    """
    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": '""',
    }
    rec = _http_request("POST", url, data=SOAP_MINIMAL_ENVELOPE, headers=headers)
    rec["probe_id"] = "soap_fault_elicit"
    body = rec.pop("raw_body_for_parse", b"")

    if rec.get("http_status") is None:
        rec["verdict"] = "FAIL"
        rec["details"] = f"transport error: {rec.get('transport_error')}"
        return rec

    # HTTP 500 + SOAP fault = healthy SOAP service
    fault_signals = (b"Fault", b"faultcode", b"faultstring", b"Envelope")
    has_soap_markers = any(sig in body for sig in fault_signals)

    if rec["http_status"] == 500 and has_soap_markers:
        rec["verdict"] = "PASS"
        rec["details"] = (
            "HTTP 500 with SOAP fault markers — endpoint is a live SOAP service "
            "responding to envelope-shaped requests (expected behavior for empty body)."
        )
        try:
            root = ET.fromstring(body)
            fault = root.find(f".//{SOAPENV_NS}Fault")
            if fault is not None:
                fcode = fault.find("faultcode")
                fstr = fault.find("faultstring")
                rec["soap_fault_code"] = fcode.text if fcode is not None else None
                rec["soap_fault_string"] = fstr.text if fstr is not None else None
        except ET.ParseError:
            pass
    elif rec["http_status"] in (400, 415):
        rec["verdict"] = "INCONCLUSIVE"
        rec["details"] = (
            f"HTTP {rec['http_status']} — service rejected envelope but is alive. "
            "May expect specific SOAPAction or stricter envelope structure."
        )
    elif rec["http_status"] == 404:
        rec["verdict"] = "FAIL"
        rec["details"] = "HTTP 404 — URL path wrong or service moved."
    elif has_soap_markers:
        rec["verdict"] = "PASS"
        rec["details"] = (
            f"HTTP {rec['http_status']} with SOAP markers — endpoint is SOAP-speaking."
        )
    else:
        rec["verdict"] = "INCONCLUSIVE"
        rec["details"] = (
            f"HTTP {rec['http_status']} — no SOAP markers in response. "
            "May not be SOAP, or may be HTML error page."
        )
    return rec


# ---------------------------------------------------------------------------
# URL parse helpers
# ---------------------------------------------------------------------------

def parse_host(url: str) -> str:
    return urllib.parse.urlparse(url).hostname or ""


def parse_port(url: str) -> int:
    p = urllib.parse.urlparse(url)
    return p.port or (443 if p.scheme == "https" else 80)


# ---------------------------------------------------------------------------
# Extended probe implementations (v0.2)
# ---------------------------------------------------------------------------

def probe_http_get_json(url: str, expect_json_keys: list[str] | None = None) -> dict[str, Any]:
    """GET → parse response body as JSON; validate top-level keys if expect_json_keys given."""
    rec = _http_request("GET", url)
    rec["probe_id"] = "http_get_json"
    body = rec.pop("raw_body_for_parse", b"")

    if rec.get("http_status") is None:
        rec["verdict"] = "FAIL"
        rec["details"] = rec.get("transport_error", "no response")
        return rec

    if rec["http_status"] >= 400:
        rec["verdict"] = "FAIL"
        rec["details"] = f"HTTP {rec['http_status']}"
        return rec

    try:
        parsed = json.loads(body)
        rec["json_parsed"] = True
        rec["json_type"] = type(parsed).__name__
        missing = [k for k in (expect_json_keys or []) if k not in (parsed if isinstance(parsed, dict) else {})]
        if missing:
            rec["verdict"] = "INCONCLUSIVE"
            rec["details"] = f"HTTP {rec['http_status']} JSON OK but missing expected keys: {missing}"
        else:
            rec["verdict"] = "PASS"
            rec["details"] = (
                f"HTTP {rec['http_status']} JSON parsed OK in {rec['duration_ms']}ms"
                + (f"; keys present: {expect_json_keys}" if expect_json_keys else "")
            )
    except (json.JSONDecodeError, ValueError) as e:
        rec["json_parsed"] = False
        rec["verdict"] = "INCONCLUSIVE"
        rec["details"] = f"HTTP {rec['http_status']} but body is not valid JSON: {e}"

    return rec


def probe_http_head_with_referrer(url: str, referrer: str = "") -> dict[str, Any]:
    """HEAD with custom Referrer header (some integrations require non-empty referrer)."""
    headers: dict[str, str] = {}
    if referrer:
        headers["Referer"] = referrer
    rec = _http_request("HEAD", url, headers=headers)
    rec["probe_id"] = "http_head_with_referrer"
    rec["referrer_sent"] = referrer
    if rec.get("http_status") is not None:
        rec["verdict"] = "PASS" if rec["http_status"] < 500 else "INCONCLUSIVE"
        rec["details"] = f"HTTP {rec['http_status']} in {rec['duration_ms']}ms (referrer={referrer!r})"
    else:
        rec["verdict"] = "FAIL"
        rec["details"] = rec.get("transport_error", "no response")
    rec.pop("raw_body_for_parse", None)
    return rec


def probe_https_tls_verify(url: str) -> dict[str, Any]:
    """HEAD with strict TLS verification — refuses self-signed certs. Google/Azure probes."""
    started = time.time()
    rec: dict[str, Any] = {
        "probe_id": "https_tls_verify",
        "url": url,
        "started_at": now_iso(),
    }
    req = urllib.request.Request(url, method="HEAD")
    ctx = ssl.create_default_context()  # strict — cert verification enabled
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_S, context=ctx) as resp:
            rec["http_status"] = resp.status
            rec["tls_verified"] = True
            rec["verdict"] = "PASS"
            rec["details"] = f"TLS verified, HTTP {resp.status} in {int((time.time()-started)*1000)}ms"
    except ssl.SSLError as e:
        rec["http_status"] = None
        rec["tls_verified"] = False
        rec["verdict"] = "FAIL"
        rec["details"] = f"TLS verification failed: {e}"
    except urllib.error.HTTPError as e:
        rec["http_status"] = e.code
        rec["tls_verified"] = True
        rec["verdict"] = "PASS" if e.code < 500 else "INCONCLUSIVE"
        rec["details"] = f"TLS verified, HTTP {e.code} in {int((time.time()-started)*1000)}ms"
    except urllib.error.URLError as e:
        rec["http_status"] = None
        rec["tls_verified"] = False
        rec["verdict"] = "FAIL"
        rec["details"] = f"transport error: {e.reason}"
    except Exception as e:
        rec["http_status"] = None
        rec["tls_verified"] = False
        rec["verdict"] = "FAIL"
        rec["details"] = f"{type(e).__name__}: {e}"
    rec["duration_ms"] = int((time.time() - started) * 1000)
    return rec


# ---------------------------------------------------------------------------
# Target-level orchestration — dispatch-table driven (v0.2)
# ---------------------------------------------------------------------------

PROBE_FUNCTIONS: dict[str, Any] = {
    "tcp_connect":             lambda t: probe_tcp(parse_host(t["url"]), parse_port(t["url"])),
    "http_head":               lambda t: probe_http_head(t["url"]),
    "http_head_with_referrer": lambda t: probe_http_head_with_referrer(t["url"], t.get("referrer", "")),
    "http_get_json":           lambda t: probe_http_get_json(t["url"], t.get("expect_json_keys", [])),
    "https_tls_verify":        lambda t: probe_https_tls_verify(t["url"]),
    "wsdl_get":                lambda t: probe_wsdl(t["url"]),
    "soap_fault_elicit":       lambda t: probe_soap_fault_elicit(t["url"]),
}

# Default probe sequence for legacy SOAP targets that have no probe_types field.
_SOAP_DEFAULT_PROBES = ["tcp_connect", "http_head", "wsdl_get", "soap_fault_elicit"]


def probe_target(target: dict[str, Any]) -> dict[str, Any]:
    """Run configured probes against one target using the PROBE_FUNCTIONS dispatch table."""
    banner(f"Probing target: {target['target_id']}  ({target['url']})", "-")
    rec: dict[str, Any] = {
        "target_id": target["target_id"],
        "url": target["url"],
        "expected_role": target.get("expected_role"),
        "expected_service": target.get("expected_service"),
        "started_at": now_iso(),
        "probes": [],
    }

    probe_types = target.get("probe_types", _SOAP_DEFAULT_PROBES)
    total = len(probe_types)
    for i, ptype in enumerate(probe_types, 1):
        step(f"[{i}/{total}] {ptype}  {target['url']}")
        if ptype not in PROBE_FUNCTIONS:
            p: dict[str, Any] = {
                "probe_id": ptype, "verdict": "SKIP",
                "details": f"unknown probe type: {ptype!r}", "duration_ms": 0,
            }
        else:
            p = PROBE_FUNCTIONS[ptype](target)
        rec["probes"].append(p)
        verdict = p.get("verdict", "?")
        msg = p.get("details", "")
        if verdict == "PASS":
            ok(msg)
        elif verdict == "SKIP":
            warn(msg)
        elif verdict == "INCONCLUSIVE":
            warn(msg)
        else:
            fail(msg)

    rec["completed_at"] = now_iso()
    return rec


# ---------------------------------------------------------------------------
# Cross-target reasoning — Q-INT-010-1 port-inversion check
# ---------------------------------------------------------------------------

def reason_questions(target_records: list[dict[str, Any]]) -> dict[str, Any]:
    """Answer the open questions from INT-010 / INT-011 recon docs."""
    by_id = {t["target_id"]: t for t in target_records}

    answers: dict[str, Any] = {}

    # Q-INT-010-1 — port inversion D8WS vs D5WS
    def _wsdl_target_ns(target_id: str) -> str | None:
        t = by_id.get(target_id)
        if not t:
            return None
        for p in t["probes"]:
            if p.get("probe_id") == "wsdl_get" and p.get("wsdl_target_namespace"):
                return p["wsdl_target_namespace"]
        return None

    d8_tst_ns = _wsdl_target_ns("D8WS-TST")
    d8_std_ns = _wsdl_target_ns("D8WS-STD")
    d5_tst_ns = _wsdl_target_ns("D5WS-TST")
    d5_std_ns = _wsdl_target_ns("D5WS-STD")

    evidence_lines = [
        f"D8WS-TST (port 3030) WSDL targetNamespace: {d8_tst_ns}",
        f"D8WS-STD (port 3031) WSDL targetNamespace: {d8_std_ns}",
        f"D5WS-TST (port 3031) WSDL targetNamespace: {d5_tst_ns}",
        f"D5WS-STD (port 3030) WSDL targetNamespace: {d5_std_ns}",
    ]

    def _contains_d8(ns: str | None) -> bool:
        return ns is not None and "D8WS" in ns

    def _contains_d5(ns: str | None) -> bool:
        return ns is not None and "D5WS" in ns

    if d8_tst_ns and d8_std_ns and d5_tst_ns and d5_std_ns:
        d8_self_consistent = _contains_d8(d8_tst_ns) and _contains_d8(d8_std_ns)
        d5_self_consistent = _contains_d5(d5_tst_ns) and _contains_d5(d5_std_ns)
        if d8_self_consistent and d5_self_consistent:
            verdict = "CONFIRMED"
            detail = (
                "Both ports 3030 and 3031 serve D8WS and D5WS namespaces respectively "
                "as documented — port-inversion is intentional, not a typo."
            )
        else:
            verdict = "ANOMALY"
            detail = (
                "WSDL namespaces do NOT match expected service per port — "
                "verify with Michal Ciberej; the recon documentation may have STD/TST swapped."
            )
    else:
        verdict = "INCONCLUSIVE"
        detail = (
            "At least one WSDL was not retrievable; cannot fully confirm. "
            "See per-target probe results."
        )

    answers["Q-INT-010-1"] = {
        "question": "Are D8WS and D5WS port assignments truly inverted between STD and TST (3030/3031)?",
        "verdict": verdict,
        "evidence": evidence_lines,
        "detail": detail,
    }

    # Q-INT-010-2 — SUPIN-internal reachability
    tcp_results = []
    for t in target_records:
        for p in t["probes"]:
            if p.get("probe_id") == "tcp_connect":
                tcp_results.append(
                    f"{t['target_id']} ({p['host']}:{p['port']}): {p['verdict']}"
                )
    all_pass = all(r.endswith("PASS") for r in tcp_results) if tcp_results else False
    answers["Q-INT-010-2"] = {
        "question": "Are D8WS+D5WS reachable from this host (SUPIN-internal)?",
        "verdict": "REACHABLE" if all_pass else "PARTIAL_OR_BLOCKED",
        "evidence": tcp_results,
    }

    return answers


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------

def render_md_report(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# Integration recon report — D8WS / D5WS")
    lines.append("")
    lines.append(f"**Recon ID.** `{payload['recon_id']}`  ")
    lines.append(f"**Run at.** {payload['recon_started_at']}  ")
    lines.append(f"**Host.** {payload['host_env']['hostname']} "
                 f"({payload['host_env']['local_ip_best_guess']}) "
                 f"— {payload['host_env']['os']} {payload['host_env']['os_release']}, "
                 f"Python {payload['host_env']['python_version']}  ")
    lines.append(f"**SUPIN-internal indicator.** "
                 f"{'YES' if payload['host_env']['supin_internal_indicator'] else 'unclear (check IP)'}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Question answers first (highest signal density)
    lines.append("## §1. Open-question verdicts")
    lines.append("")
    for qid, qdata in payload["questions_answered"].items():
        lines.append(f"### {qid} — {qdata['question']}")
        lines.append("")
        lines.append(f"**Verdict.** `{qdata['verdict']}`")
        lines.append("")
        if qdata.get("detail"):
            lines.append(qdata["detail"])
            lines.append("")
        lines.append("Evidence:")
        lines.append("")
        for ev in qdata["evidence"]:
            lines.append(f"- {ev}")
        lines.append("")

    # Per-target detail
    lines.append("---")
    lines.append("")
    lines.append("## §2. Per-target probe results")
    lines.append("")
    for t in payload["targets"]:
        lines.append(f"### {t['target_id']} — `{t['url']}`")
        lines.append("")
        lines.append(f"Expected role: **{t.get('expected_role')}**, "
                     f"expected service: **{t.get('expected_service')}**")
        lines.append("")
        lines.append("| Probe | Verdict | Duration | Details |")
        lines.append("|-------|---------|---------:|---------|")
        for p in t["probes"]:
            details = (p.get("details") or "").replace("|", "\\|")
            if len(details) > 160:
                details = details[:157] + "..."
            lines.append(
                f"| {p['probe_id']} "
                f"| `{p.get('verdict','?')}` "
                f"| {p.get('duration_ms','?')}ms "
                f"| {details} |"
            )
        lines.append("")

        # WSDL detail if available
        for p in t["probes"]:
            if p.get("probe_id") == "wsdl_get" and p.get("verdict") == "PASS":
                lines.append("WSDL details:")
                lines.append("")
                lines.append(f"- **targetNamespace:** `{p['wsdl_target_namespace']}`")
                lines.append(f"- **operations:** {p.get('wsdl_operations', [])}")
                lines.append(f"- **response bytes:** {p.get('response_bytes')}")
                lines.append(f"- **response sha256:** `{p.get('response_sha256')}`")
                lines.append("")
                head = p.get("response_excerpt_head", "")
                if head:
                    lines.append("First 2KB of WSDL:")
                    lines.append("")
                    lines.append("```xml")
                    lines.append(head[:2000])
                    lines.append("```")
                    lines.append("")
            if p.get("probe_id") == "soap_fault_elicit" and p.get("soap_fault_code"):
                lines.append("SOAP fault detail:")
                lines.append("")
                lines.append(f"- **faultcode:** `{p['soap_fault_code']}`")
                lines.append(f"- **faultstring:** `{p.get('soap_fault_string')}`")
                lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## §3. How to return this to Pete / Claude session")
    lines.append("")
    lines.append("Send back the JSON sidecar (machine-parseable) or paste the §1 "
                 "verdicts block + the §2 per-target tables. Both files live in "
                 "`recon-harness/outputs/`.")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def run_probes(target_filter: str | None = None) -> Path:
    targets = load_targets()
    if target_filter:
        targets = [t for t in targets if t["target_id"] == target_filter]
        if not targets:
            fail(f"no target matched: {target_filter}")
            sys.exit(2)

    banner("Integration recon harness — D8WS / D5WS", "=")
    print(f"Targets to probe: {[t['target_id'] for t in targets]}")
    print(f"Host: {socket.gethostname()}")
    print(f"Time: {now_iso()}")

    payload: dict[str, Any] = {
        "schema_version": "0.2",
        "recon_id": str(uuid.uuid4()),
        "recon_started_at": now_iso(),
        "host_env": host_env(),
        "targets": [],
    }

    for t in targets:
        rec = probe_target(t)
        payload["targets"].append(rec)

    payload["recon_completed_at"] = now_iso()
    payload["questions_answered"] = reason_questions(payload["targets"])

    # integration_coverage block (schema v0.2)
    fully_reachable: list[str] = []
    tls_warning: list[str] = []
    for trec in payload["targets"]:
        verdicts = [p.get("verdict") for p in trec.get("probes", [])]
        if verdicts and all(v == "PASS" for v in verdicts):
            fully_reachable.append(trec["target_id"])
        for p in trec.get("probes", []):
            if p.get("probe_id") == "https_tls_verify" and p.get("verdict") != "PASS":
                tls_warning.append(trec["target_id"])
    payload["integration_coverage"] = {
        "documented_in_INT_docs": 11,
        "probed_in_this_run": len(payload["targets"]),
        "missing_endpoints": ["INT-002", "INT-003", "INT-004", "INT-005"],
        "fully_reachable": fully_reachable,
        "tls_warning": tls_warning,
    }

    OUTPUTS_DIR.mkdir(exist_ok=True)
    hostname = socket.gethostname()
    ts = now_compact_local()
    base = f"RECON-{hostname}-{ts}"
    json_path = OUTPUTS_DIR / f"{base}.json"
    md_path = OUTPUTS_DIR / f"{base}.md"

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False, default=str)
    with md_path.open("w", encoding="utf-8") as f:
        f.write(render_md_report(payload))

    LAST_REPORT_MARKER.write_text(str(md_path), encoding="utf-8")

    banner("Done.", "=")
    ok(f"JSON report (Claude ingestion): {json_path}")
    ok(f"MD report  (human review):      {md_path}")
    print()
    print("Send EITHER file back to Pete / paste contents into the Claude session.")
    print("Claude will parse the JSON for direct ingestion.")
    return md_path


# ---------------------------------------------------------------------------
# Interactive menu
# ---------------------------------------------------------------------------

def menu_loop() -> None:
    targets = load_targets()
    while True:
        print()
        print("=" * 56)
        print("  Integration recon — menu")
        print("=" * 56)
        print("  [1] Probe ALL targets + generate report")
        print("  [2] Probe one target (choose)")
        print("  [3] List targets")
        print("  [4] Show last report path")
        print("  [q] Quit")
        choice = input("Select: ").strip().lower()
        if choice == "1":
            run_probes()
        elif choice == "2":
            for i, t in enumerate(targets, 1):
                print(f"  {i}) {t['target_id']:12s} {t['url']}")
            pick = input("Number: ").strip()
            try:
                idx = int(pick) - 1
                tid = targets[idx]["target_id"]
                run_probes(target_filter=tid)
            except (ValueError, IndexError):
                fail("invalid selection")
        elif choice == "3":
            print()
            for t in targets:
                print(f"  - {t['target_id']:12s} {t['url']}   "
                      f"[{t.get('expected_role','?')}/{t.get('expected_service','?')}]")
        elif choice == "4":
            if LAST_REPORT_MARKER.exists():
                print(f"  Last report: {LAST_REPORT_MARKER.read_text(encoding='utf-8').strip()}")
            else:
                print("  No report yet.")
        elif choice in ("q", "quit", "exit"):
            return
        else:
            warn(f"unknown choice: {choice}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="int_recon",
        description="Active SOAP recon harness for D8WS / D5WS endpoints.",
    )
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("menu", help="Interactive menu (recommended)")

    sub.add_parser("probe-all", help="Probe all targets, write report, exit")

    p_one = sub.add_parser("probe", help="Probe a single target")
    p_one.add_argument("--target", required=True, help="target_id (see `list`)")

    sub.add_parser("list", help="List configured targets")

    sub.add_parser("last-report", help="Show path to last generated MD report")

    args = parser.parse_args(argv)

    if args.cmd == "menu" or args.cmd is None:
        menu_loop()
    elif args.cmd == "probe-all":
        run_probes()
    elif args.cmd == "probe":
        run_probes(target_filter=args.target)
    elif args.cmd == "list":
        for t in load_targets():
            print(f"  {t['target_id']:12s} {t['url']}   "
                  f"[{t.get('expected_role','?')}/{t.get('expected_service','?')}]")
    elif args.cmd == "last-report":
        if LAST_REPORT_MARKER.exists():
            print(LAST_REPORT_MARKER.read_text(encoding="utf-8").strip())
        else:
            print("(none yet)")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
