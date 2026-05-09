"""
selenium/helpers/nav_helpers.py — CP-SUPIN-05 navigation helpers

Per _specs/CROSS-FRAMEWORK-PARITY-EXECUTION-v0.1-CS.md §5.2.

Drift guard pattern ported from Playwright a2-alternates-demo.spec.ts:43.
2026-05-07 drift: POST /api/reports returns 403 (reCAPTCHA-v3 score <
threshold for HeadlessChrome UA) → SPA routes to /formular/error/timeout.
"""
from __future__ import annotations

import time

import pytest
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

DRIFT_REASON = (
    "DEMO drift 2026-05-07 v2: SPA routed to /formular/error/timeout after Rozumím. "
    "Forensic root cause: POST /api/reports → 403 Forbidden despite valid x-captcha-token. "
    "Hypothesis: reCAPTCHA v3 score < threshold for HeadlessChrome UA. "
    "Per recon/DRIFT-2026-05-07-DEMO-POST-REPORTS-CS.md."
)


def dismiss_cookie_banner(driver: WebDriver) -> bool:
    """Best-effort dismiss of cookie modal (privacy default: ODMÍTNOUT VŠE).

    Returns True if banner was dismissed, False if not present.
    """
    try:
        wait = WebDriverWait(driver, 5)
        reject = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            "//button[contains(translate(text(),'ODMÍTNOUTVŠEÍÉÁČĚ','odmítnoutvšeieace'),"
            "'odmítnout vše') or contains(text(),'ODMÍTNOUT VŠE')]",
        )))
        reject.click()
        time.sleep(0.4)
        return True
    except TimeoutException:
        return False


def nav_to_verification_or_skip(driver: WebDriver, base_url: str) -> None:
    """Navigate to /formular/, dismiss banner, click VYPLNIT ZÁZNAM + Rozumím,
    then poll URL for 30s:
      - /verification  → happy path, return normally
      - /error/timeout → pytest.skip() with drift rationale

    Per _specs/CROSS-FRAMEWORK-PARITY-EXECUTION-v0.1-CS.md §5.2.
    """
    driver.get(f"{base_url}/formular/")
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    dismiss_cookie_banner(driver)

    # Click VYPLNIT ZÁZNAM
    cta = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((
        By.XPATH,
        "//button[contains(translate(text(),'VYPLNITZÁZNAM','vyplnitzáznam'),"
        "'vyplnit záznam')]",
    )))
    cta.click()

    # Wait for /informations before Rozumím
    try:
        WebDriverWait(driver, 15).until(EC.url_contains("/informations"))
    except TimeoutException:
        pass  # SPA may route differently; continue to Rozumím attempt

    # Click Rozumím
    try:
        rozumim = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
            By.XPATH, "//button[contains(text(),'Rozumím')]",
        )))
        rozumim.click()
    except TimeoutException:
        pass  # Button may already be gone due to fast SPA transition

    # Poll URL — 30s budget
    deadline = time.time() + 30
    while time.time() < deadline:
        url = driver.current_url
        if "/verification" in url:
            return  # happy path
        if "/error/timeout" in url:
            pytest.skip(
                f"{DRIFT_REASON} URL: {url}"
            )
        time.sleep(0.5)

    # Deadline reached without resolving — assert to fail clearly
    assert "/verification" in driver.current_url, (
        f"navToVerification deadline exceeded. URL: {driver.current_url}"
    )


def set_otp_digits(driver: WebDriver, digits: str) -> None:
    """Set OTP digits via React-aware native setter pattern.

    Equivalent of Playwright page.evaluate() native setter, ported to
    Selenium execute_script(). Works with controlled React <input type="tel">
    components that do not react to standard send_keys().

    Args:
        driver: active WebDriver instance
        digits: 4-char string, e.g. "1234"
    """
    script = """
        var inputs = document.querySelectorAll('input[type="tel"]');
        var setter = Object.getOwnPropertyDescriptor(
            window.HTMLInputElement.prototype, 'value'
        ).set;
        var digits = arguments[0];
        for (var i = 0; i < Math.min(inputs.length, digits.length); i++) {
            setter.call(inputs[i], digits[i]);
            inputs[i].dispatchEvent(new Event('input', {bubbles: true}));
        }
    """
    driver.execute_script(script, digits)


def set_react_input(driver: WebDriver, element, value: str) -> None:
    """Set a React-controlled input element value via native setter.

    Per _specs/CROSS-FRAMEWORK-PARITY-EXECUTION-v0.1-CS.md §6.2.

    Args:
        driver:  active WebDriver instance
        element: WebElement reference to the input
        value:   value to set
    """
    driver.execute_script(
        "arguments[0].value = arguments[1]; "
        "arguments[0].dispatchEvent(new Event('input', {bubbles: true}));",
        element,
        value,
    )
