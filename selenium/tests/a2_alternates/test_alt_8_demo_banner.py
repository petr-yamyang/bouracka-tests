"""
TC-CP-A2-ALT-8 — Selenium pytest port

Source-of-truth: playwright/tests/a2-alternates-demo.spec.ts (ALT-8 block, line ~179).

Test: DEMO banner present on /formular/ rozcestnik (Δ11 + Δ22 confirmation).
  - "Nacházíte se v DEMO VERZI aplikace" visible
  - "Vhodné pro malé nehody..." visible

DEMO-only: pytest.skip() if BASE does not contain demo.bouracka.cz.

Run:
    py -m pytest selenium/tests/a2_alternates/test_alt_8_demo_banner.py -v
"""
from __future__ import annotations

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.helpers.data_loader import covers
from selenium.helpers.nav_helpers import dismiss_cookie_banner


def test_TC_CP_A2_ALT_8_demo_banner(driver, base_url):
    """TC-CP-A2-ALT-8 — DEMO banner visible (Δ11 + Δ22 confirmation).

    Covers: TT-SCRN-demoBanner
    """
    if "demo.bouracka.cz" not in base_url:
        pytest.skip("DEMO-only test — skip when BASE is not demo.bouracka.cz")

    covers("TT-SCRN-demoBanner")

    driver.get(f"{base_url}/formular/")
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    dismiss_cookie_banner(driver)

    # DEMO banner — Δ11 confirmation
    banner_demo = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((
            By.XPATH,
            "//*[contains(text(),'Nacházíte se v DEMO VERZI aplikace')]",
        ))
    )
    assert banner_demo.is_displayed(), "DEMO banner text not visible"

    # Scope statement — Δ22 confirmation
    scope_text = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((
            By.XPATH,
            "//*[contains(text(),'Vhodné pro malé nehody bez zranění a škody do 200 000 Kč')]",
        ))
    )
    assert scope_text.is_displayed(), "Scope statement not visible"
