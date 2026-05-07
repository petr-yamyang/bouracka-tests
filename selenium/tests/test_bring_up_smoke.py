"""
test_bring_up_smoke.py — Selenium WebDriver port of Bouracka bring-up smoke

Per CP-SUPIN-04 STEP 32. Selenium parity for Playwright/Cypress/TestCafe smoke.
Demonstrates "robust automation" use case per Pete direction.

Run via pytest:
  py -m pytest selenium/tests/test_bring_up_smoke.py -v

Or with allure for VUP-grade step recording:
  py -m pytest selenium/tests/ -v --alluredir=test-results/allure-selenium

Requirements (one-time):
  py -m pip install --break-system-packages selenium pytest webdriver-manager allure-pytest
"""
from __future__ import annotations
import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


BASE = os.environ.get("BOURACKA_BASE", "https://demo.bouracka.cz")


@pytest.fixture(scope="function")
def driver():
    """Mobile-emulated Chrome (375x667 viewport) per AMENDMENT 2."""
    opts = ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--lang=cs-CZ")
    opts.add_experimental_option(
        "mobileEmulation",
        {"deviceMetrics": {"width": 375, "height": 667, "pixelRatio": 2.0},
         "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"},
    )
    drv = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=opts)
    drv.set_window_size(375, 667)
    yield drv
    drv.quit()


def dismiss_cookie_banner(driver):
    """Best-effort dismiss of cookie modal (privacy default: ODMITNOUT VSE).
    Returns True if banner was dismissed, False otherwise."""
    try:
        wait = WebDriverWait(driver, 5)
        reject = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(translate(text(), 'odmítnoutvšeOOÍÉ', 'odmítnoutvšeoiie'), 'odmítnout vše') or contains(text(), 'ODMÍTNOUT VŠE')]")
        ))
        reject.click()
        time.sleep(0.5)
        return True
    except TimeoutException:
        return False


def test_TC_CP_001_bring_up_smoke(driver):
    """TC-CP-001 — Selenium parity for bring-up smoke.

    Steps:
      S1 — navigate to /formular/
      S2 — dismiss cookie banner
      S3 — assert page title contains 'Bouračka'
      S4 — assert primary CTA visible
      S5 — assert WCAG 2.2 AA touch target ≥ 44×44 px
      S6 — click CTA → /formular/informations
    """
    # STEP 1 — navigate
    driver.get(f"{BASE}/formular/")
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

    # STEP 2 — dismiss cookies (privacy)
    dismissed = dismiss_cookie_banner(driver)
    print(f"[selenium-smoke] cookie dismissed: {dismissed}")

    # STEP 3 — title sanity
    assert "Bouračka" in driver.title, f"Title missing 'Bouračka': {driver.title!r}"

    # STEP 4 — CTA visible
    cta = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(translate(text(), 'VYPLNITZÁNAM', 'vyplnitzánam'), 'vyplnit záznam')]")
        )
    )
    assert cta.is_displayed(), "CTA not visible"

    # STEP 5 — WCAG touch target
    box = cta.size
    assert box["width"] >= 44, f"CTA width {box['width']}px < 44 (WCAG fail)"
    assert box["height"] >= 44, f"CTA height {box['height']}px < 44"

    # STEP 6 — click + URL change
    cta.click()
    WebDriverWait(driver, 15).until(
        EC.url_matches(r".*/formular/informations/?$")
    )
    assert "/formular/informations" in driver.current_url, f"URL did not change to /informations: {driver.current_url!r}"
