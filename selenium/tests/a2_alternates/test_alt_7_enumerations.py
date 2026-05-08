"""
TC-CP-A2-ALT-7 — Selenium pytest port

Per _specs/CROSS-FRAMEWORK-PARITY-EXECUTION-v0.1-CS.md §2 (port order: ALT-7 first).
Source-of-truth: playwright/tests/a2-alternates-demo.spec.ts (ALT-7 block, line ~158).

Test: public enumerations return expected counts; protected return 403.
  - /api/enumerations/insuranceCompanies → 200, ≥10 entries, ALLIANZ present
  - /api/enumerations/vehicleBrands      → 200, ≥200 entries, ŠKODA present
  - 8 protected endpoints                → 403 each

Pure API test — no Selenium WebDriver used; uses requests library directly.
This matches Playwright's `request` fixture pattern (API-only test).

Run:
    py -m pytest selenium/tests/a2_alternates/test_alt_7_enumerations.py -v
"""
from __future__ import annotations

import os

import pytest
import requests as http

from selenium.helpers.data_loader import covers

BASE = os.environ.get("BOURACKA_BASE", "https://demo.bouracka.cz")

PROTECTED_ENDPOINTS = [
    "licenseCategories",
    "damageZones",
    "movementTypes",
    "accidentCauses",
    "accidentCategories",
    "vehicleCategories",
    "documentTypes",
    "witnessTypes",
]


def test_TC_CP_A2_ALT_7_enumerations():
    """TC-CP-A2-ALT-7 — insuranceCompanies ≥10 + ALLIANZ; vehicleBrands ≥200 + ŠKODA;
    8 protected → 403.

    Covers: TT-LOV-insuranceCompanies, TT-LOV-vehicleBrands, TT-ACTV-enumProtection
    """
    covers("TT-LOV-insuranceCompanies", "TT-LOV-vehicleBrands", "TT-ACTV-enumProtection")

    session = http.Session()

    # ── insuranceCompanies ────────────────────────────────────────────────────
    r = session.get(f"{BASE}/api/enumerations/insuranceCompanies", timeout=15)
    assert r.status_code == 200, f"insuranceCompanies: expected 200, got {r.status_code}"
    body = r.json()
    assert len(body) >= 10, f"insuranceCompanies count: expected ≥10, got {len(body)}"
    allianz = next((x for x in body if x.get("code") == "ALLIANZ"), None)
    assert allianz is not None, "ALLIANZ not found in insuranceCompanies"

    # ── vehicleBrands ─────────────────────────────────────────────────────────
    r = session.get(f"{BASE}/api/enumerations/vehicleBrands", timeout=15)
    assert r.status_code == 200, f"vehicleBrands: expected 200, got {r.status_code}"
    body = r.json()
    assert len(body) >= 200, f"vehicleBrands count: expected ≥200, got {len(body)}"
    skoda = next((x for x in body if x.get("name") == "ŠKODA"), None)
    assert skoda is not None, "ŠKODA not found in vehicleBrands"

    # ── Protected endpoints → 403 ─────────────────────────────────────────────
    for name in PROTECTED_ENDPOINTS:
        r = session.get(f"{BASE}/api/enumerations/{name}", timeout=15)
        assert r.status_code == 403, (
            f"{name} should return 403, got {r.status_code}; body={r.text[:200]}"
        )
