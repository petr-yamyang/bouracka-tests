"""
TC-CP-A2-ALT-5 — Selenium pytest port

Source-of-truth: playwright/tests/a2-alternates-demo.spec.ts (ALT-5 block, line ~134).

Test: Slovak +421 phone-prefix selectable from Předvolba dropdown.
  - Navigate to /verification via full click chain (drift-skip guard active)
  - Click first element labelled "Předvolba"
  - Assert "+421" option visible in opened dropdown

Drift guard: nav_to_verification_or_skip() calls pytest.skip() if SPA routes
to /error/timeout (POST /api/reports 403 reCAPTCHA drift — 2026-05-07).

Run:
    py -m pytest selenium/tests/a2_alternates/test_alt_5_slovak_prefix.py -v
"""
from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.helpers.data_loader import covers
from selenium.helpers.nav_helpers import nav_to_verification_or_skip


def test_TC_CP_A2_ALT_5_slovak_prefix(driver, base_url):
    """TC-CP-A2-ALT-5 — +421 option visible in phone prefix dropdown.

    Covers: TT-SCRN-predvolba421
    """
    covers("TT-SCRN-predvolba421")

    # Navigate to /verification — pytest.skip() fires here on drift
    nav_to_verification_or_skip(driver, base_url)

    # Click the first "Předvolba" labelled element (dropdown trigger)
    predvolba = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((
            By.XPATH,
            # Match label text; covers both <label> and aria-label patterns
            "//*[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
            "'předvolba') or contains(@aria-label,'Předvolba')]",
        ))
    )
    predvolba.click()

    # Assert "+421" visible in the expanded dropdown
    option_421 = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((
            By.XPATH,
            "//*[contains(text(),'+421')]",
        ))
    )
    assert option_421.is_displayed(), "+421 option not visible in Předvolba dropdown"
