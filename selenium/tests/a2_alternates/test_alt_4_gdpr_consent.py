"""
TC-CP-A2-ALT-4 — Selenium pytest port

Source-of-truth: playwright/tests/a2-alternates-demo.spec.ts (ALT-4 block, line ~118).

Test: Phase 1 GDPR consent required for participant A.
  - Navigate to /verification (drift-skip guard active)
  - Fill phone "608400004" for participant A
  - Intentionally do NOT check the GDPR checkbox
  - Inject JS fetch/XHR interceptor to monitor PUT /reporter calls
  - Click "Odeslat kód"
  - Wait 2s
  - Assert no PUT /reporter call was fired (form blocked without GDPR)

Drift guard: nav_to_verification_or_skip() → pytest.skip() if SPA routes to
/error/timeout. Expected outcome on Cíl 1: SKIPPED.

Run:
    py -m pytest selenium/tests/a2_alternates/test_alt_4_gdpr_consent.py -v
"""
from __future__ import annotations

import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.helpers.data_loader import covers
from selenium.helpers.nav_helpers import nav_to_verification_or_skip


# JS snippet: inject fetch + XHR interceptor to count PUT /reporter requests.
# Must be injected BEFORE the user interaction that might fire the PUT.
_INJECT_REPORTER_SPY = """
window.__alt4_reporterPutCount = 0;

// ── fetch interceptor ───────────────────────────────────────────────────────
const _origFetch = window.fetch;
window.fetch = async function(input, init) {
    const url  = typeof input === 'string' ? input : (input.url || String(input));
    const meth = (init && init.method) ? init.method.toUpperCase() : 'GET';
    if (meth === 'PUT' && /\\/reporter/.test(url)) {
        window.__alt4_reporterPutCount++;
    }
    return _origFetch.apply(this, arguments);
};

// ── XHR interceptor ─────────────────────────────────────────────────────────
const _origOpen = XMLHttpRequest.prototype.open;
XMLHttpRequest.prototype.open = function(method, url) {
    if (method && method.toUpperCase() === 'PUT' && /\\/reporter/.test(String(url))) {
        this.__isReporterPut = true;
    }
    return _origOpen.apply(this, arguments);
};
const _origSend = XMLHttpRequest.prototype.send;
XMLHttpRequest.prototype.send = function() {
    if (this.__isReporterPut) {
        window.__alt4_reporterPutCount++;
    }
    return _origSend.apply(this, arguments);
};
"""


def test_TC_CP_A2_ALT_4_gdpr_consent(driver, base_url):
    """TC-CP-A2-ALT-4 — no PUT /reporter fires without GDPR consent.

    Covers: TT-FUNC-gdprConsent
    """
    covers("TT-FUNC-gdprConsent")

    # Navigate to /verification — pytest.skip() fires here on drift
    nav_to_verification_or_skip(driver, base_url)

    # Inject PUT /reporter spy BEFORE user interaction
    driver.execute_script(_INJECT_REPORTER_SPY)

    # Fill phone for participant A — intentionally skip GDPR checkbox
    phone_a = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="tel"]'))
    )
    phone_a.clear()
    phone_a.send_keys("608400004")

    # Intentionally do NOT check the GDPR checkbox — this is the negative test

    # Click Odeslat kód
    odeslat = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//button[contains(translate(text(),"
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
            "'odeslat kód')]",
        ))
    )
    odeslat.click()

    # Wait 2s — mirrors Playwright waitForTimeout (SPA reaction time)
    time.sleep(2)

    # Assert PUT /reporter was NOT fired
    reporter_count = driver.execute_script(
        "return window.__alt4_reporterPutCount || 0;"
    )
    assert reporter_count == 0, (
        f"PUT /reporter fired {reporter_count} time(s) despite missing GDPR consent — "
        f"form must block submission without consent"
    )
