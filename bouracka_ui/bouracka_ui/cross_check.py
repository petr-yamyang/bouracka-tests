"""Cross-framework agreement projection over a v0.1 envelope.

PROTOTYPE for FR-K-007 (Brief #007).

Given an envelope, produces a 'cross_check' dict summarising how the
frameworks agreed/disagreed per TC. Pure function; does NOT modify envelope.

The envelope already carries `parity_status` per TC (set by the dispatcher
when building the envelope). This module aggregates those + computes
majority verdict, identifies the divergent framework(s), and resolves
step anchors when a workbook step lookup is provided.

Author: Pete Y. + Opus 4.7 prototype 2026-05-15 (Brief #007 will harden).
"""
from __future__ import annotations

from collections import Counter
from typing import Iterable

# Match dispatcher's canonical labels exactly
VERDICT_ORDER = ["pass", "fail", "skip-drift", "skip-other",
                 "soft-pass", "error", "missing"]

# How verdicts collapse into "decision groups" for majority calculation.
# soft-pass groups with pass; skip-drift / skip-other group separately;
# missing is its own group (excluded from majority math).
DECISION_GROUP = {
    "pass":       "pass-group",
    "soft-pass":  "pass-group",
    "fail":       "fail-group",
    "error":      "fail-group",      # errors counted as fail for agreement
    "skip-drift": "skip-group",
    "skip-other": "skip-group",
    "missing":    "missing",          # never groups
}


# ───────────────────────────────────────────────────────────────────────
# Pure aggregation
# ───────────────────────────────────────────────────────────────────────

def _majority_verdict(verdicts: dict) -> str | None:
    """Return the most-common decision-group verdict, or None if all-missing.

    Soft-pass collapses to pass; error collapses to fail; skips count
    as their own group. Ties broken by VERDICT_ORDER preference.
    """
    groups = [DECISION_GROUP[v] for v in verdicts.values() if v != "missing"]
    if not groups:
        return None
    counter = Counter(groups)
    # Most common
    top_count = max(counter.values())
    top_groups = [g for g, c in counter.items() if c == top_count]
    if len(top_groups) == 1:
        top_group = top_groups[0]
    else:
        # Tie — pick the group containing the verdict closest to top of
        # VERDICT_ORDER (i.e., pass beats fail beats skip)
        canonical_verdicts_in_top = []
        for v, g in zip(verdicts.values(), groups):
            if g in top_groups:
                canonical_verdicts_in_top.append(v)
        canonical_verdicts_in_top.sort(
            key=lambda v: VERDICT_ORDER.index(v) if v in VERDICT_ORDER else 99
        )
        top_group = DECISION_GROUP[canonical_verdicts_in_top[0]]
    # Resolve back to a representative verdict for that group
    representatives = {
        "pass-group": "pass",
        "fail-group": "fail",
        "skip-group": "skip-drift",
    }
    return representatives.get(top_group)


def _differing_frameworks(verdicts: dict, majority: str | None) -> list[str]:
    """List frameworks whose verdict's decision-group differs from majority's."""
    if majority is None:
        return []
    target_group = DECISION_GROUP[majority]
    return sorted([
        fw for fw, v in verdicts.items()
        if v != "missing" and DECISION_GROUP[v] != target_group
    ])


def _resolve_step_anchor(error_messages: dict, tc_steps: list[dict]) -> dict | None:
    """Heuristic: find the step whose action_cs/action_en substring appears in any framework's error message.

    Returns {step_code, step_label} or None if no match.
    Best-effort; if the workbook has no step rows for this TC, returns None.
    """
    if not tc_steps:
        return None
    for fw, msg in error_messages.items():
        if not msg:
            continue
        msg_l = str(msg).lower()
        for step in tc_steps:
            # Try action_cs first, then action_en
            for col in ("action_cs", "action_en"):
                action = step.get(col)
                if action and len(action) >= 6 and action.lower() in msg_l:
                    return {
                        "step_code": step.get("step_code", "?"),
                        "step_label": action,
                    }
    return None


def build_cross_check(envelope: dict,
                      steps_lookup: dict | None = None) -> dict:
    """Build cross-check projection of a v0.1 envelope.

    Args:
      envelope: parsed v0.1 envelope (dict)
      steps_lookup: optional {tc_code: [step_dict, ...]} from workbook_io.list_steps;
                    used for step_anchor resolution

    Returns:
      {
        "run_id", "env", "frameworks", "total_tcs",
        "agreement_summary": {all_agreed, divergence, not_applicable, missing_coverage},
        "divergent_tcs": [{tc_code, verdicts, differing_frameworks, majority_verdict,
                           step_anchor, error_messages}],
        "tc_full_matrix": [{tc_code, verdicts, parity_status, soft_pass_reason}]
      }
    """
    if steps_lookup is None:
        steps_lookup = {}

    results = envelope.get("results", [])
    frameworks = envelope.get("frameworks", [])
    summary_counter = {
        "all_agreed": 0,
        "divergence": 0,
        "not_applicable": 0,
        "missing_coverage": 0,
    }

    divergent_tcs: list[dict] = []
    full_matrix: list[dict] = []

    for r in results:
        tc_code = r["tc_code"]
        verdicts = dict(r.get("verdicts", {}))
        parity = r.get("parity_status", "not-applicable")
        error_messages = dict(r.get("error_messages", {}))

        # missing coverage flag (any framework reported "missing")
        if "missing" in verdicts.values():
            summary_counter["missing_coverage"] += 1

        if parity == "agree":
            summary_counter["all_agreed"] += 1
        elif parity == "divergence":
            summary_counter["divergence"] += 1
            majority = _majority_verdict(verdicts)
            differing = _differing_frameworks(verdicts, majority)
            tc_steps = steps_lookup.get(tc_code, [])
            step_anchor = _resolve_step_anchor(error_messages, tc_steps)
            divergent_tcs.append({
                "tc_code": tc_code,
                "verdicts": verdicts,
                "differing_frameworks": differing,
                "majority_verdict": majority,
                "step_anchor": step_anchor,
                "error_messages": {fw: m for fw, m in error_messages.items() if m},
            })
        else:  # not-applicable (single framework reporting, etc.)
            summary_counter["not_applicable"] += 1

        full_matrix.append({
            "tc_code": tc_code,
            "verdicts": verdicts,
            "parity_status": parity,
            "soft_pass_reason": r.get("soft_pass_reason"),
        })

    return {
        "run_id": envelope.get("run_id"),
        "env": envelope.get("env"),
        "env_url": envelope.get("env_url"),
        "started_at": envelope.get("started_at"),
        "ended_at": envelope.get("ended_at"),
        "frameworks": sorted(frameworks),
        "total_tcs": len(results),
        "agreement_summary": summary_counter,
        "divergent_tcs": divergent_tcs,
        "tc_full_matrix": full_matrix,
    }


# ───────────────────────────────────────────────────────────────────────
# HTML rendering — vanilla, no JS, no external CSS/CDN
# ───────────────────────────────────────────────────────────────────────

VERDICT_COLORS = {
    "pass":       "#1f7a1f",   # dark green
    "soft-pass":  "#5fad5f",   # light green
    "fail":       "#b22222",   # firebrick
    "error":      "#7a1f1f",   # dark red
    "skip-drift": "#d28e00",   # orange
    "skip-other": "#b7a300",   # mustard
    "missing":    "#888888",   # gray
}


def _verdict_cell(verdict: str) -> str:
    color = VERDICT_COLORS.get(verdict, "#000")
    return (
        f'<td style="background:{color};color:white;'
        f'text-align:center;padding:4px 8px;font-family:monospace;'
        f'font-size:12px;">{_html_escape(verdict)}</td>'
    )


def _html_escape(s) -> str:
    if s is None:
        return ""
    return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def render_cross_check_html(cc: dict) -> str:
    """Produce a standalone HTML page with cross-check view.

    No external dependencies — inline CSS, no JS frameworks. ~250 lines max.
    """
    frameworks = cc["frameworks"]
    s = cc["agreement_summary"]
    divergent = cc["divergent_tcs"]
    full = cc["tc_full_matrix"]

    # ── Build HTML ─────────────────────────────────────────────────────
    parts: list[str] = []
    parts.append("<!DOCTYPE html><html><head><meta charset='UTF-8'>")
    parts.append("<title>Cross-framework check — " + _html_escape(cc.get("run_id", "")) + "</title>")
    parts.append("<style>")
    parts.append("""
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
               margin: 24px; color: #222; max-width: 1100px; }
        h1 { font-size: 20px; margin-bottom: 4px; }
        .meta { color: #555; font-size: 12px; margin-bottom: 24px; }
        .summary { display: flex; gap: 16px; margin: 16px 0 24px 0; }
        .summary .card { flex: 1; padding: 12px 16px; border: 1px solid #ddd;
                         border-radius: 4px; background: #fafafa; }
        .summary .card .label { font-size: 11px; color: #777; text-transform: uppercase; }
        .summary .card .value { font-size: 28px; font-weight: 600; }
        .card.agreed .value { color: #1f7a1f; }
        .card.divergent .value { color: #b22222; }
        .card.missing .value { color: #888888; }
        .card.not_applicable .value { color: #555; }
        h2 { font-size: 16px; margin: 32px 0 8px 0; }
        table { border-collapse: collapse; width: 100%; font-size: 13px; }
        th, td { padding: 6px 8px; border-bottom: 1px solid #eee; vertical-align: top; }
        th { background: #f5f5f5; text-align: left; font-weight: 600; }
        .tc-code { font-family: monospace; font-weight: 600; }
        .differing { font-size: 11px; color: #b22222; }
        .step-anchor { font-size: 11px; color: #555; }
        details summary { cursor: pointer; padding: 8px 0; user-select: none; }
        details[open] summary { font-weight: 600; }
        .errmsg { color: #b22222; font-size: 11px; font-family: monospace;
                  background: #fff5f5; padding: 4px 6px; margin: 2px 0; }
    """)
    parts.append("</style></head><body>")

    # Header
    parts.append("<h1>Cross-framework check</h1>")
    parts.append("<div class='meta'>")
    parts.append(f"Run: <code>{_html_escape(cc.get('run_id'))}</code>"
                 f" &middot; Env: {_html_escape(cc.get('env'))}"
                 f" (<a href='{_html_escape(cc.get('env_url'))}'>{_html_escape(cc.get('env_url'))}</a>)"
                 f" &middot; {_html_escape(cc.get('started_at'))} → {_html_escape(cc.get('ended_at'))}")
    parts.append(f" &middot; Frameworks: {', '.join(frameworks)}")
    parts.append("</div>")

    # Summary cards
    parts.append("<div class='summary'>")
    for label, key, css in [
        ("All agreed", "all_agreed", "agreed"),
        ("Divergence", "divergence", "divergent"),
        ("Missing coverage", "missing_coverage", "missing"),
        ("Not applicable", "not_applicable", "not_applicable"),
        ("Total TCs", None, ""),
    ]:
        if key is None:
            parts.append(f"<div class='card'><div class='label'>{label}</div>"
                         f"<div class='value'>{cc['total_tcs']}</div></div>")
        else:
            parts.append(f"<div class='card {css}'><div class='label'>{label}</div>"
                         f"<div class='value'>{s[key]}</div></div>")
    parts.append("</div>")

    # Divergent TCs section
    parts.append(f"<h2>Divergent TCs ({len(divergent)})</h2>")
    if not divergent:
        parts.append("<p style='color:#1f7a1f'>No cross-framework divergence detected.</p>")
    else:
        parts.append("<table>")
        parts.append("<tr><th>TC</th>")
        for fw in frameworks:
            parts.append(f"<th style='text-align:center'>{_html_escape(fw)}</th>")
        parts.append("<th>Differing</th><th>Step anchor</th></tr>")
        for d in divergent:
            parts.append("<tr>")
            parts.append(f"<td class='tc-code'>{_html_escape(d['tc_code'])}</td>")
            for fw in frameworks:
                v = d["verdicts"].get(fw, "missing")
                parts.append(_verdict_cell(v))
            differing_html = ", ".join(d["differing_frameworks"]) or "—"
            parts.append(f"<td class='differing'>{_html_escape(differing_html)}</td>")
            sa = d["step_anchor"]
            if sa:
                sa_html = f"<code>{_html_escape(sa['step_code'])}</code>: {_html_escape(sa['step_label'])}"
            else:
                sa_html = "—"
            parts.append(f"<td class='step-anchor'>{sa_html}</td>")
            parts.append("</tr>")
            # Error messages, if any
            if d.get("error_messages"):
                parts.append(f"<tr><td colspan='{len(frameworks) + 3}'>")
                for fw, msg in d["error_messages"].items():
                    parts.append(f"<div class='errmsg'><strong>{_html_escape(fw)}:</strong> "
                                 f"{_html_escape(msg)}</div>")
                parts.append("</td></tr>")
        parts.append("</table>")

    # Full matrix (collapsible)
    parts.append("<h2>Full TC matrix (collapsible)</h2>")
    parts.append(f"<details><summary>Show all {len(full)} TCs ({len(frameworks)} frameworks each)</summary>")
    parts.append("<table>")
    parts.append("<tr><th>TC</th>")
    for fw in frameworks:
        parts.append(f"<th style='text-align:center'>{_html_escape(fw)}</th>")
    parts.append("<th>Parity</th><th>Soft-pass reason</th></tr>")
    for row in full:
        parts.append("<tr>")
        parts.append(f"<td class='tc-code'>{_html_escape(row['tc_code'])}</td>")
        for fw in frameworks:
            v = row["verdicts"].get(fw, "missing")
            parts.append(_verdict_cell(v))
        parts.append(f"<td style='font-size:11px'>{_html_escape(row['parity_status'])}</td>")
        parts.append(f"<td style='font-size:11px'>{_html_escape(row.get('soft_pass_reason') or '')}</td>")
        parts.append("</tr>")
    parts.append("</table></details>")

    parts.append("</body></html>")
    return "".join(parts)
