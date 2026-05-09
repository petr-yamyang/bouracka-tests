"""
TC-CP-A2-ALT-1 — Selenium pytest port

Source-of-truth: playwright/tests/a2-alternates-demo.spec.ts (ALT-1 block, line ~75).

Test: Phase 2 ŘP (Řidičský průkaz) regex rejects malformed input.
  - Full SPA navigation through verification (participant A + B OTP)
  - Reaches /manual?validate=false
  - Fills ŘP field with "INVALID_FORMAT_123"
  - Clicks Potvrdit; waits 2s
  - Asserts URL does NOT end with /recap (form rejected malformed ŘP)

Drift guard: nav_to_verification_or_skip() → pytest.skip() if SPA routes to
/error/timeout. Expected outcome on Cíl 1: SKIPPED.

Run:
    py -m pytest selenium/tests/a2_alternates/test_alt_1_rp_regex.py -v
"""
from __future__ import annotations

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from helpers.data_loader import covers
from helpers.nav_helpers import nav_to_verification_or_skip, set_otp_digits


def _click_button(driver, pattern_text: str, timeout: int = 10):
    """Click first button whose text matches pattern_text (case-insensitive)."""
    xpath = (
        f"//button[contains(translate(text(),"
        f"'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚŮÝŽŠŘČĎŤŇ',"
        f"'abcdefghijklmnopqrstuvwxyzáéíóúůýžšřčďťň'),"
        f"'{pattern_text.lower()}')]"
    )
    btn = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    btn.click()


def test_TC_CP_A2_ALT_1_rp_regex(driver, base_url):
    """TC-CP-A2-ALT-1 — malformed ŘP rejected; URL stays off /recap.

    Covers: TT-FUNC-rpRegex
    """
    covers("TT-FUNC-rpRegex")

    # Navigate to /verification — pytest.skip() fires here on drift
    nav_to_verification_or_skip(driver, base_url)

    # ── Participant A — phone + GDPR + OTP ──────────────────────────────────
    phone_a = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="tel"]'))
    )
    phone_a.clear()
    phone_a.send_keys("608100001")

    # Check first GDPR checkbox
    checkbox = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="checkbox"]'))
    )
    if not checkbox.is_selected():
        checkbox.click()

    _click_button(driver, "odeslat kód")

    # OTP digits 1,2,3,4 via React native setter
    set_otp_digits(driver, "1234")
    _click_button(driver, "ověřit")

    # ── Participant B — phone + OTP ──────────────────────────────────────────
    phone_b = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="tel"]'))
    )
    phone_b.clear()
    phone_b.send_keys("608100002")

    _click_button(driver, "odeslat kód")
    set_otp_digits(driver, "5678")
    _click_button(driver, "ověřit")

    # ── Navigate to manual entry ─────────────────────────────────────────────
    _click_button(driver, "přejít na informace")
    _click_button(driver, "vyplnit údaje ručně")

    WebDriverWait(driver, 15).until(EC.url_contains("manual?validate=false"))

    # ── Bad ŘP — fill and submit ─────────────────────────────────────────────
    # Try id, name, or aria-label patterns matching the ŘP field
    rp_field = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//input[@id[contains(.,'rp')] or @name[contains(.,'rp')] "
            "or contains(@aria-label,'idičského')]",
        ))
    )
    rp_field.clear()
    rp_field.send_keys("INVALID_FORMAT_123")

    _click_button(driver, "potvrdit")

    # Wait 2s — mirrors Playwright waitForTimeout (SPA validation reaction time)
    time.sleep(2)

    # ŘP regex rejected → URL must NOT end with /recap
    current_url = driver.current_url
    assert not current_url.endswith("recap"), (
        f"ŘP validation failed to reject malformed input — "
        f"SPA navigated to recap: {current_url}"
    )
