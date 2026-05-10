"""Workbook reader for bouracka-ui.

v0.1 Phase 1 — Runnable Mock: returns synthetic data based on the schema
of BOURACKA-TESTPLAN-v0.4.2.xlsx but doesn't actually read the file. Phase 2
implements real reads via openpyxl.

Reference:
  _config/BOURACKA-UI-DESIGN-v0.1-2026-05-10.md §4
"""
from __future__ import annotations

import datetime as _dt
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────
# ENV code → schema env enum mapping (per design doc §4.1)
# ──────────────────────────────────────────────────────────────────────────
ENV_CODE_TO_SCHEMA = {
    "ENV-PUB": "prod-readonly",
    "ENV-TST": "tst",
    "ENV-DMO": "demo",
    # Future: ENV-UAT → uat (when env-tagging migration v0.5.2 lands)
    # Future: ENV-PRD-W → prod-writable
}


class WorkbookLockedError(RuntimeError):
    """Raised when the workbook is open in Excel and we can't write."""


# ──────────────────────────────────────────────────────────────────────────
# §4.1 read paths
# ──────────────────────────────────────────────────────────────────────────

def list_envs(wb_path: Path) -> list[dict]:
    """Read 04_TestEnvironments → list of dicts.

    Phase 1 mock: returns synthetic data matching the workbook's actual shape.
    Phase 2 implements real openpyxl read.
    """
    if not wb_path.exists():
        return _mock_envs()
    try:
        from openpyxl import load_workbook
        wb = load_workbook(str(wb_path), read_only=True, data_only=True)
        if "04_TestEnvironments" not in wb.sheetnames:
            return _mock_envs()
        ws = wb["04_TestEnvironments"]
        rows = list(ws.iter_rows(min_row=2, values_only=True))
        # Map by header position (per investigation 2026-05-10):
        # 0:id 1:item_code 2:name_cs 3:name_en 4:descr_cs 5:descr_en
        # 6:item_type 7:item_status 8:severity 9:urgency 10:priority
        # 13:base_url 14:network_reach 15:locale 16:browser_default 17:recaptcha_posture
        out = []
        for r in rows:
            if not r or not r[1]:
                continue
            code = r[1]
            out.append({
                "code": code,
                "name_cs": r[2],
                "name_en": r[3],
                "descr_en": r[5],
                "base_url": r[13],
                "recaptcha_posture": r[17],
                "schema_env": ENV_CODE_TO_SCHEMA.get(code, "demo"),
                "status": r[7],
            })
        return out
    except Exception as e:
        # Workbook unreadable — fall back to mock so UI still loads
        return _mock_envs()


def list_tcs(wb_path: Path, env: str | None = None,
             framework: str | None = None) -> list[dict]:
    """Read 02_TestCases. Filter by env (applies_to_demo / applies_to_prod)
    and framework (substring in framework_targets) if provided.

    Phase 1 mock unless workbook readable.
    """
    if not wb_path.exists():
        return _mock_tcs(env, framework)
    try:
        from openpyxl import load_workbook
        wb = load_workbook(str(wb_path), read_only=True, data_only=True)
        if "02_TestCases" not in wb.sheetnames:
            return _mock_tcs(env, framework)
        ws = wb["02_TestCases"]
        rows = list(ws.iter_rows(min_row=2, values_only=True))
        # Header positions (per investigation 2026-05-10):
        # 0:id 1:item_code 2:name_cs 3:name_en 8:severity 9:urgency 10:priority
        # 7:item_status 14:type 19:env_coverage 20:viewport 21:framework_targets
        # 34:applies_to_demo 35:applies_to_prod
        out = []
        for r in rows:
            if not r or not r[1]:
                continue
            code = r[1]
            framework_targets = (r[21] or "") if len(r) > 21 else ""
            applies_to_demo = bool(r[34]) if len(r) > 34 else None
            applies_to_prod = bool(r[35]) if len(r) > 35 else None
            # Env filter
            if env == "demo" and applies_to_demo is False:
                continue
            if env == "prod-readonly" and applies_to_prod is False:
                continue
            # Framework filter (substring match)
            if framework and framework not in str(framework_targets).lower():
                continue
            out.append({
                "code": code,
                "name_cs": r[2],
                "name_en": r[3],
                "severity": r[8],
                "urgency": r[9],
                "priority": r[10],
                "status": r[7],
                "type": r[14] if len(r) > 14 else None,
                "framework_targets": framework_targets,
                "applies_to_demo": applies_to_demo,
                "applies_to_prod": applies_to_prod,
            })
        return out
    except Exception:
        return _mock_tcs(env, framework)


def list_bugs(wb_path: Path, status: str | None = None,
              severity: str | None = None) -> list[dict]:
    """Read 08_Bugs → JIRA-style list of dicts."""
    if not wb_path.exists():
        return _mock_bugs(status, severity)
    try:
        from openpyxl import load_workbook
        wb = load_workbook(str(wb_path), read_only=True, data_only=True)
        if "08_Bugs" not in wb.sheetnames:
            return _mock_bugs(status, severity)
        ws = wb["08_Bugs"]
        rows = list(ws.iter_rows(min_row=2, values_only=True))
        # Header positions (per investigation 2026-05-10):
        # 0:id 1:code 2:name_cs 3:name_en 7:status 8:severity 9:urgency 10:priority
        # 13:env_where_present 14:linked_tc_ref 15:linked_run_result_ref
        # 36:screenshot_ref 37:trace_ref 38:error_message
        out = []
        for r in rows:
            if not r or not r[1]:
                continue
            row_status = r[7]
            row_severity = r[8]
            if status and row_status != status:
                continue
            if severity and row_severity != severity:
                continue
            out.append({
                "code": r[1],
                "name_cs": r[2],
                "name_en": r[3],
                "status": row_status,
                "severity": row_severity,
                "urgency": r[9],
                "priority": r[10],
                "env_where_present": r[13] if len(r) > 13 else None,
                "linked_tc_ref": r[14] if len(r) > 14 else None,
                "linked_run_result_ref": r[15] if len(r) > 15 else None,
                "screenshot_ref": r[36] if len(r) > 36 else None,
                "error_message": r[38] if len(r) > 38 else None,
            })
        return out
    except Exception:
        return _mock_bugs(status, severity)


def append_bug(wb_path: Path, bug: dict) -> str:
    """Append one row to 08_Bugs. Returns assigned bug code (BUG-NNN).

    Phase 1 mock: returns a fake code without touching the workbook.
    Phase 2 implements real append via openpyxl.
    """
    if not wb_path.exists():
        # Mock — returns fake code
        return "BUG-MOCK-001"
    try:
        from openpyxl import load_workbook
        wb = load_workbook(str(wb_path))  # NOT read_only — we need to write
        if "08_Bugs" not in wb.sheetnames:
            raise RuntimeError("08_Bugs sheet missing")
        ws = wb["08_Bugs"]
        # Compute next bug code
        codes = [c.value for c in ws["B"][1:] if c.value and str(c.value).startswith("BUG-")]
        nums = []
        for c in codes:
            try:
                nums.append(int(str(c).split("-")[-1]))
            except (ValueError, IndexError):
                continue
        next_n = (max(nums) if nums else 0) + 1
        new_code = f"BUG-{next_n:03d}"
        next_id = (max([c.value for c in ws["A"][1:] if isinstance(c.value, int)] or [0]) + 1)
        now = _dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        new_row = [None] * 39  # match header count
        new_row[0] = next_id
        new_row[1] = new_code
        new_row[3] = bug.get("name_en", "")
        new_row[5] = bug.get("descr_en", "")
        new_row[6] = "bug"
        new_row[7] = "open"
        new_row[8] = bug.get("severity", "C")
        new_row[9] = bug.get("urgency", "C")
        new_row[10] = bug.get("priority", "P3-medium")
        new_row[11] = bug.get("submitter", "bouracka-ui")
        new_row[12] = now
        new_row[13] = bug.get("env_where_present")
        new_row[14] = bug.get("linked_tc_ref")
        new_row[15] = bug.get("linked_run_result_ref")
        new_row[16] = bug.get("repro_steps")
        new_row[17] = bug.get("expected")
        new_row[18] = bug.get("actual")
        new_row[21] = now  # created_at
        new_row[22] = now  # updated_at
        ws.append(new_row)
        wb.save(str(wb_path))
        return new_code
    except PermissionError as e:
        raise WorkbookLockedError(str(e)) from e


# ──────────────────────────────────────────────────────────────────────────
# Mocks (used in Phase 1 + when workbook missing/unreadable)
# ──────────────────────────────────────────────────────────────────────────

def _mock_envs() -> list[dict]:
    return [
        {"code": "ENV-PUB", "name_cs": "Public produkce",
         "name_en": "Public production",
         "descr_en": "Public production; dev-time recon only, never test execution.",
         "base_url": "https://www.bouracka.cz",
         "recaptcha_posture": "live",
         "schema_env": "prod-readonly", "status": "live"},
        {"code": "ENV-TST", "name_cs": "Testovací prostředí",
         "name_en": "TEST environment",
         "descr_en": "Primary test env; full validation; both drivers sign via SMS-OTP.",
         "base_url": "https://tst.bouracka.cz",
         "recaptcha_posture": "test-keys",
         "schema_env": "tst", "status": "live"},
        {"code": "ENV-DMO", "name_cs": "DEMO prostředí (autoškola)",
         "name_en": "DEMO env (driving school)",
         "descr_en": "Driving-school variant; reduced validation; watermarked PDF output.",
         "base_url": "https://demo.bouracka.cz",
         "recaptcha_posture": "live",
         "schema_env": "demo", "status": "live"},
    ]


def _mock_tcs(env: str | None, framework: str | None) -> list[dict]:
    base = [
        {"code": "TC-CP-A1-MAIN-DEMO",
         "name_en": "A1 — Main happy day end-to-end (DEMO)",
         "severity": "A", "urgency": "A", "priority": "P1-critical",
         "status": "live", "type": "E2E",
         "framework_targets": "playwright,cypress,selenium",
         "applies_to_demo": True, "applies_to_prod": False},
        {"code": "TC-CP-A2-ALT-1",
         "name_en": "A2 ALT-1 — RP regex validation",
         "severity": "B", "urgency": "B", "priority": "P2-high",
         "status": "live", "type": "FUNC",
         "framework_targets": "playwright,cypress,selenium",
         "applies_to_demo": True, "applies_to_prod": True},
        {"code": "TC-CP-A2-ALT-4",
         "name_en": "A2 ALT-4 — GDPR consent capture",
         "severity": "B", "urgency": "A", "priority": "P2-high",
         "status": "live", "type": "FUNC",
         "framework_targets": "playwright,cypress,selenium",
         "applies_to_demo": True, "applies_to_prod": True},
        {"code": "TC-CP-A2-ALT-5",
         "name_en": "A2 ALT-5 — Slovak prefix RP recognition",
         "severity": "C", "urgency": "B", "priority": "P3-medium",
         "status": "live", "type": "FUNC",
         "framework_targets": "playwright,cypress,selenium",
         "applies_to_demo": True, "applies_to_prod": True},
        {"code": "TC-CP-A2-ALT-6",
         "name_en": "A2 ALT-6 — Police card optional path",
         "severity": "B", "urgency": "B", "priority": "P2-high",
         "status": "live", "type": "FUNC",
         "framework_targets": "playwright,cypress,selenium",
         "applies_to_demo": True, "applies_to_prod": True},
        {"code": "TC-CP-A2-ALT-7",
         "name_en": "A2 ALT-7 — Enumerations completeness",
         "severity": "B", "urgency": "A", "priority": "P2-high",
         "status": "live", "type": "FUNC",
         "framework_targets": "playwright,cypress,selenium",
         "applies_to_demo": True, "applies_to_prod": True},
        {"code": "TC-CP-A2-ALT-8",
         "name_en": "A2 ALT-8 — DEMO banner presence",
         "severity": "B", "urgency": "B", "priority": "P2-high",
         "status": "live", "type": "FUNC",
         "framework_targets": "playwright,cypress,selenium",
         "applies_to_demo": True, "applies_to_prod": False},
        {"code": "TC-CP-A2-ALT-9",
         "name_en": "A2 ALT-9 — Post-reports drift detection (soft-pass)",
         "severity": "A", "urgency": "A", "priority": "P1-critical",
         "status": "live", "type": "FUNC",
         "framework_targets": "playwright,cypress,selenium",
         "applies_to_demo": True, "applies_to_prod": True},
        {"code": "TC-CP-A2-ALT-10",
         "name_en": "A2 ALT-10 — SPA post-probe",
         "severity": "B", "urgency": "A", "priority": "P2-high",
         "status": "live", "type": "FUNC",
         "framework_targets": "playwright,cypress,selenium",
         "applies_to_demo": True, "applies_to_prod": True},
    ]
    if env == "demo":
        base = [t for t in base if t["applies_to_demo"]]
    if env == "prod-readonly":
        base = [t for t in base if t["applies_to_prod"]]
    if framework:
        base = [t for t in base if framework in t["framework_targets"].lower()]
    return base


def _mock_bugs(status: str | None, severity: str | None) -> list[dict]:
    base = [
        {"code": "BUG-027",
         "name_en": "mim-alliance-card partner badge stretches full-width",
         "status": "open", "severity": "B", "urgency": "B", "priority": "P3-medium",
         "env_where_present": "ENV-DMO", "linked_tc_ref": None,
         "linked_run_result_ref": None, "screenshot_ref": None,
         "error_message": None},
        {"code": "BUG-028",
         "name_en": "mim-alliance-card__title wraps to 2 lines on RCMT",
         "status": "open", "severity": "B", "urgency": "B", "priority": "P3-medium",
         "env_where_present": "ENV-DMO", "linked_tc_ref": None,
         "linked_run_result_ref": None, "screenshot_ref": None,
         "error_message": None},
        {"code": "BUG-MOCK-001",
         "name_en": "Mock bug — replace via Phase 2 real workbook read",
         "status": "open", "severity": "C", "urgency": "C", "priority": "P3-medium",
         "env_where_present": "ENV-TST", "linked_tc_ref": "TC-CP-A2-ALT-1",
         "linked_run_result_ref": None, "screenshot_ref": None,
         "error_message": "(synthetic — Phase 1 mock)"},
    ]
    if status:
        base = [b for b in base if b["status"] == status]
    if severity:
        base = [b for b in base if b["severity"] == severity]
    return base
