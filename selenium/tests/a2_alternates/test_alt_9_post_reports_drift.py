"""
TC-CP-A2-ALT-9 — Selenium pytest port

Source-of-truth: playwright/tests/a2-alternates-demo.spec.ts (ALT-9 block, line ~187).

Test: POST /api/reports characterization (drift-aware).
  - Direct HTTP POST via requests library (pure API — no WebDriver needed)
  - Status 200 → body must contain UUIDv4 (happy path, legacy behaviour)
  - Status 403 → soft-pass with warning (drift: reCAPTCHA-v3 gate active)
  - Any other status → hard AssertionError

Acceptance: GREEN-soft (200 OR 403 are both valid outcomes at Cíl 1).
Writes runs/alt9-selenium-response.txt as diagnostic artefact.

Run:
    py -m pytest selenium/tests/a2_alternates/test_alt_9_post_reports_drift.py -v
"""
from __future__ import annotations

import json
import os
import re
import warnings
from pathlib import Path

import requests as http

from helpers.data_loader import covers

BASE = os.environ.get("BOURACKA_BASE", "https://demo.bouracka.cz")
RUNS_DIR = Path(__file__).resolve().parents[3] / "runs"

UUID_V4_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
    re.IGNORECASE,
)


def test_TC_CP_A2_ALT_9_post_reports_drift():
    """TC-CP-A2-ALT-9 — POST /api/reports: 200+UUID (happy) OR 403 (drift).

    Covers: TT-ACTV-postReports
    """
    covers("TT-ACTV-postReports")

    r = http.post(
        f"{BASE}/api/reports",
        json={},
        headers={"Content-Type": "application/json"},
        timeout=15,
    )
    status = r.status_code
    body = r.text

    # Write diagnostic artefact (mirrors Playwright testInfo.attach)
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    artifact_path = RUNS_DIR / "alt9-selenium-response.txt"
    artifact_path.write_text(
        f"status={status}\n\n"
        "--- headers ---\n"
        f"{json.dumps(dict(r.headers), indent=2)}\n\n"
        "--- body ---\n"
        f"{body}\n",
        encoding="utf-8",
    )

    if status == 200:
        # Happy path — UUIDv4 report ID in body
        assert UUID_V4_RE.search(body), (
            f"POST /api/reports returned 200 but body contains no UUIDv4: {body[:200]}"
        )
    elif status == 403:
        # Drift path — soft-pass
        warnings.warn(
            f"[ALT-9 drift] POST /api/reports returned 403; body={body[:200]}",
            stacklevel=2,
        )
        assert status in (200, 403), f"Unexpected status: {status}"
    else:
        raise AssertionError(
            f"Unexpected POST /api/reports status: {status}; body={body[:200]}"
        )
