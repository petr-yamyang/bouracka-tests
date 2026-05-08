"""
TC-CP-A1-MAIN-DEMO — Selenium pytest port

Source-of-truth: playwright/tests/a1-main-happy-day-demo.spec.ts
Note: Playwright source had typo `abel(/Model vozidla/i)` — corrected.

Full E2E happy-day flow on DEMO Bouracka:
  Phase 0  (rozcestnik)      → click VYPLNIT ZÁZNAM
  Phase A  (intro)           → click Rozumím
  Phase 1  (verification)    → A: phone+OTP, B: phone+OTP, success
  Phase 2A (documents A)     → manual fallback, 8 fields, recap+email
  Phase 2B (documents B)     → same shape
  Phase 2.5 (witnesses)      → skip
  Phase 3A (vehicle A)       → photos skip, damage NONE, movement, vehicle data
  Phase 3B (vehicle B)       → same
  Phase 3  (circumstances)   → REAR_END_COLLISION + desc
  Phase 3  (situation)       → on-site=yes
  Phase 3  (location)        → free-text fallback
  Phase 3  (culprit)         → A
  Phase 4  (summary)         → checkbox + Podepsat
  Phase 4  (sign A + B)      → OTP sign
  Phase 4  (success)         → assert "Záznam byl odeslán"

Drift guard: pytest.skip() on /error/timeout (Cíl 1 drift — expected SKIPPED).
Timeout budget: 180 s (browser wall-clock). Mobile Chrome 375×667.

Run:
    py -m pytest selenium/tests/a1_main/test_main_happy_day.py -v --timeout=180
"""
from __future__ import annotations

import time

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from selenium.helpers.data_loader import covers
from selenium.helpers.nav_helpers import (
    dismiss_cookie_banner,
    nav_to_verification_or_skip,
    set_otp_digits,
    set_react_input,
)

# ─── helpers ──────────────────────────────────────────────────────────────────

def _wait_url(driver, pattern: str, timeout: int = 15) -> None:
    """Wait until current URL contains pattern."""
    WebDriverWait(driver, timeout).until(EC.url_contains(pattern))


def _click_btn(driver, text_pattern: str, timeout: int = 10) -> None:
    """Click first button whose text matches text_pattern (case-insensitive, Czech)."""
    xpath = (
        f"//button[contains(translate(text(),"
        f"'ABCDEFGHIJKLMNOPQRSTUVWXYZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ',"
        f"'abcdefghijklmnopqrstuvwxyzáčďéěíňóřšťúůýž'),"
        f"'{text_pattern.lower()}')]"
    )
    btn = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    btn.click()


def _fill_input(driver, label_pattern: str, value: str, timeout: int = 10) -> None:
    """Fill first input associated with a label matching label_pattern."""
    xpath = (
        f"//label[contains(translate(text(),"
        f"'ABCDEFGHIJKLMNOPQRSTUVWXYZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ',"
        f"'abcdefghijklmnopqrstuvwxyzáčďéěíňóřšťúůýž'),"
        f"'{label_pattern.lower()}')]//following-sibling::input[1] | "
        f"//input[@aria-label[contains(translate(.,"
        f"'ABCDEFGHIJKLMNOPQRSTUVWXYZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ',"
        f"'abcdefghijklmnopqrstuvwxyzáčďéěíňóřšťúůýž'),'{label_pattern.lower()}')]]"
    )
    el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    el.clear()
    set_react_input(driver, el, value)


def _set_textarea(driver, value: str) -> None:
    """Set textarea value via React native setter."""
    driver.execute_script("""
        const ta = document.querySelector('textarea');
        if (!ta) return;
        const setter = Object.getOwnPropertyDescriptor(
            window.HTMLTextAreaElement.prototype, 'value').set;
        setter.call(ta, arguments[0]);
        ta.dispatchEvent(new Event('input', {bubbles: true}));
        ta.dispatchEvent(new Event('blur', {bubbles: true}));
    """, value)


def _autocomplete(driver, input_xpath: str, query: str, timeout: int = 10) -> None:
    """Type into autocomplete input and click first listbox option."""
    el = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, input_xpath)))
    el.click()
    set_react_input(driver, el, query)
    option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@role="listbox"]//*[@role="option"]'))
    )
    option.click()


def _fill_vehicle_section(driver, spz: str, brand: str, model: str,
                           insurer: str, desc: str) -> None:
    """Per-vehicle Phase 3 sub-flow (called twice for A and B)."""
    # Photos — skip
    _wait_url(driver, "/accident/")
    _click_btn(driver, "pokračovat bez fotografií")

    # Damage — NONE + desc
    _wait_url(driver, "/damage")
    _set_textarea(driver, desc)
    # Check "Vozidlo nebylo poškozeno" checkbox
    try:
        no_damage_label = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//label[contains(text(),'nebylo poškozeno')]//input[@type='checkbox']",
            ))
        )
        if not no_damage_label.is_selected():
            no_damage_label.click()
    except TimeoutException:
        pass  # UI variant without explicit checkbox — desc alone may suffice
    _click_btn(driver, "pokračovat")

    # Movement — "bylo v pohybu"
    _wait_url(driver, "/movement")
    try:
        motion_cb = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//label[contains(text(),'bylo v pohybu')]//input[@type='checkbox']",
            ))
        )
        if not motion_cb.is_selected():
            motion_cb.click()
    except TimeoutException:
        driver.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')[0].click()
    _click_btn(driver, "pokračovat")

    # Vehicle data — SPZ + brand + model + insurer
    _wait_url(driver, "/data")

    spz_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//input[@aria-label[contains(.,'SPZ')] or @name[contains(.,'spz')] or @id[contains(.,'spz')]]",
        ))
    )
    spz_input.clear()
    set_react_input(driver, spz_input, spz)

    # Brand autocomplete
    _autocomplete(
        driver,
        "//input[@aria-label[contains(.,'Značka')] or @name[contains(.,'brand')]]",
        brand,
    )

    # Model autocomplete (Playwright source typo corrected)
    _autocomplete(
        driver,
        "//input[@aria-label[contains(.,'Model')] or @name[contains(.,'model')]]",
        model,
    )

    _click_btn(driver, "potvrdit")

    # Insurer autocomplete
    insurer_key = insurer.split(",")[0]
    _autocomplete(
        driver,
        "//input[@aria-label[contains(.,'Pojišťovna')] or @name[contains(.,'insurer')]]",
        insurer_key,
    )

    _click_btn(driver, "potvrdit")

    # Outer Potvrdit — advances to next vehicle or circumstances
    try:
        _click_btn(driver, "potvrdit", timeout=5)
    except TimeoutException:
        pass  # May auto-advance without extra Potvrdit


# ─── test ─────────────────────────────────────────────────────────────────────

def test_TC_CP_A1_MAIN_DEMO_full_happy_day(driver, base_url):
    """TC-CP-A1-MAIN-DEMO — Phase 0→A→1→2→2.5→3→4→/success.

    Covers: TT-E2E-fullHappyDay
    Expected outcome on Cíl 1 (demo.bouracka.cz): SKIPPED (drift guard).
    """
    covers("TT-E2E-fullHappyDay")

    # ── Phase 0: rozcestnik ──────────────────────────────────────────────────
    driver.get(f"{base_url}/formular/")
    WebDriverWait(driver, 20).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    dismiss_cookie_banner(driver)

    heading = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((
            By.XPATH,
            "//*[contains(text(),'Stala se vám dopravní nehoda')]",
        ))
    )
    assert heading.is_displayed()

    _click_btn(driver, "vyplnit záznam")

    # ── Phase A: intro ───────────────────────────────────────────────────────
    _wait_url(driver, "/informations")
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'Co vás čeká')]"))
    )
    _click_btn(driver, "rozumím")

    # ── Drift guard — SKIP on /error/timeout ─────────────────────────────────
    # nav_to_verification_or_skip navigates + clicks + polls; we already clicked
    # Rozumím above, so we only need to poll here. Replicate the poll inline:
    deadline = time.time() + 30
    resolved = "deadline"
    while time.time() < deadline:
        url = driver.current_url
        if "/verification" in url:
            resolved = "verification"
            break
        if "/error/timeout" in url:
            resolved = "error-timeout"
            break
        time.sleep(0.5)

    if resolved == "error-timeout":
        reason = (
            f"DEMO drift 2026-05-07 v2: SPA routed to /error/timeout after Rozumím. "
            f"Forensic root cause: POST /api/reports → 403 Forbidden despite valid x-captcha-token. "
            f"Hypothesis: reCAPTCHA v3 score < threshold for HeadlessChrome UA. "
            f"URL: {driver.current_url}"
        )
        pytest.skip(reason)

    assert resolved == "verification", (
        f"Unexpected resolution after 30s: {resolved}, URL={driver.current_url}"
    )

    # ── Phase 1: verification A ──────────────────────────────────────────────
    _wait_url(driver, "/verification")
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'Ověřte účastníky')]"))
    )

    phone_a = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="tel"]'))
    )
    phone_a.clear()
    set_react_input(driver, phone_a, "608000001")

    cb = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="checkbox"]'))
    )
    if not cb.is_selected():
        cb.click()

    _click_btn(driver, "odeslat kód")

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((
            By.XPATH, "//*[contains(text(),'Zadejte ověřovací kód')]"
        ))
    )
    set_otp_digits(driver, "1234")
    _click_btn(driver, "ověřit")

    # ── Phase 1: verification B ──────────────────────────────────────────────
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'Účastník B')]"))
    )
    phone_b = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="tel"]'))
    )
    phone_b.clear()
    set_react_input(driver, phone_b, "608000002")
    _click_btn(driver, "odeslat kód")

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((
            By.XPATH, "//*[contains(text(),'Zadejte ověřovací kód')]"
        ))
    )
    set_otp_digits(driver, "5678")
    _click_btn(driver, "ověřit")

    # ── Phase 1: success ─────────────────────────────────────────────────────
    _wait_url(driver, "/verification/success")
    _click_btn(driver, "přejít na informace o nehodě")

    # ── Phase 2-A: documents A (manual fallback) ──────────────────────────
    _wait_url(driver, "/documents/")
    _click_btn(driver, "vyplnit údaje ručně")
    _wait_url(driver, "manual?validate=false")

    _fill_input(driver, "jméno", "Adam Test")
    _fill_input(driver, "příjmení", "Demoversen")
    _fill_input(driver, "číslo op", "123456789")
    # Birth date — try date input or text fallback
    try:
        dob = driver.find_element(By.CSS_SELECTOR, 'input[type="date"]')
        set_react_input(driver, dob, "1990-01-01")
    except NoSuchElementException:
        _fill_input(driver, "datum", "01.01.1990")

    _fill_input(driver, "e-mail", "demo-test-A@example.com")

    _autocomplete(
        driver,
        "//input[@aria-label[contains(.,'adresa')] or @placeholder[contains(.,'adresa')]]",
        "Václavské",
    )

    _fill_input(driver, "řidičského průkazu", "AB 123456")
    _autocomplete(
        driver,
        "//input[@aria-label[contains(.,'oprávnění')] or @name[contains(.,'licenseCategory')]]",
        "B",
    )
    _click_btn(driver, "potvrdit")

    _wait_url(driver, "recap")
    email_recap = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="email"]'))
    )
    email_recap.clear()
    set_react_input(driver, email_recap, "demo-test-A@example.com")
    _click_btn(driver, "uložit")

    # ── Phase 2-B: documents B ────────────────────────────────────────────
    _wait_url(driver, "/documents/")
    _click_btn(driver, "vyplnit údaje ručně")
    _wait_url(driver, "manual?validate=false")

    _fill_input(driver, "jméno", "Beata")
    _fill_input(driver, "příjmení", "Druhá")
    _fill_input(driver, "číslo op", "987654321")
    try:
        dob = driver.find_element(By.CSS_SELECTOR, 'input[type="date"]')
        set_react_input(driver, dob, "1985-06-15")
    except NoSuchElementException:
        _fill_input(driver, "datum", "15.06.1985")

    _fill_input(driver, "e-mail", "demo-test-B@example.com")

    _autocomplete(
        driver,
        "//input[@aria-label[contains(.,'adresa')] or @placeholder[contains(.,'adresa')]]",
        "Karlovo",
    )

    _fill_input(driver, "řidičského průkazu", "CD 654321")
    _autocomplete(
        driver,
        "//input[@aria-label[contains(.,'oprávnění')] or @name[contains(.,'licenseCategory')]]",
        "B",
    )
    _click_btn(driver, "potvrdit")

    _wait_url(driver, "recap")
    email_recap_b = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="email"]'))
    )
    email_recap_b.clear()
    set_react_input(driver, email_recap_b, "demo-test-B@example.com")
    _click_btn(driver, "uložit")

    # ── Phase 2.5: witnesses (skip) ───────────────────────────────────────
    _wait_url(driver, "/witness")
    _click_btn(driver, "pokračovat bez svědků")

    # ── Phase 3-A: vehicle A ──────────────────────────────────────────────
    _fill_vehicle_section(
        driver,
        spz="1AB1234",
        brand="ŠKODA",
        model="OCTAVIA",
        insurer="Allianz pojišťovna, a. s.",
        desc="Demoverze popis: vozidlo A bez poskozeni - testovaci scenar",
    )

    # ── Phase 3-B: vehicle B ──────────────────────────────────────────────
    _fill_vehicle_section(
        driver,
        spz="2BC5678",
        brand="BMW",
        model="3 SERIES",
        insurer="Kooperativa pojišťovna, a. s., Vienna Insurance Group",
        desc="Demoverze popis: vozidlo B bez poskozeni - testovaci scenar",
    )

    # ── Phase 3: circumstances ────────────────────────────────────────────
    _wait_url(driver, "/circumstances")
    rear_end = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((
            By.CSS_SELECTOR, 'input[type="radio"][value="REAR_END_COLLISION"]'
        ))
    )
    rear_end.click()
    _set_textarea(driver, "Demoverze: testovaci scenar A1 - naraz zezadu pri jizde stejnym smerem")
    _click_btn(driver, "pokračovat")

    # ── Phase 3: situation ────────────────────────────────────────────────
    _wait_url(driver, "/situation")
    radios = driver.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')
    if radios:
        radios[0].click()
    _click_btn(driver, "pokračovat")

    # ── Phase 3: location ─────────────────────────────────────────────────
    _wait_url(driver, "/location/manual")
    # Dismiss any alert overlay
    try:
        WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@role="alert"]//button'))
        ).click()
    except TimeoutException:
        pass

    textareas = driver.find_elements(By.TAG_NAME, "textarea")
    if textareas:
        _set_textarea(driver, "Demoverze: krizovatka Vaclavske namesti / Stepanska, Praha 1")
    _click_btn(driver, "pokračovat")

    # ── Phase 3: culprit ──────────────────────────────────────────────────
    _wait_url(driver, "/culprit")
    culprit_radios = driver.find_elements(By.CSS_SELECTOR, 'input[type="radio"]')
    if culprit_radios:
        culprit_radios[0].click()
    _click_btn(driver, "pokračovat")

    # ── Phase 4: summary ──────────────────────────────────────────────────
    _wait_url(driver, "/summary")
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((
            By.XPATH, "//*[contains(text(),'Shrnutí záznamu')]"
        ))
    )
    checkboxes = driver.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')
    if checkboxes:
        if not checkboxes[-1].is_selected():
            checkboxes[-1].click()
    _click_btn(driver, "podepsat záznam o nehodě")

    # ── Phase 4: sign A ───────────────────────────────────────────────────
    _wait_url(driver, "/sign-report")
    _click_btn(driver, "odeslat kód do sms")
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((
            By.XPATH, "//*[contains(text(),'Zadejte ověřovací kód')]"
        ))
    )
    set_otp_digits(driver, "9876")
    _click_btn(driver, "podepsat")

    # ── Phase 4: sign B ───────────────────────────────────────────────────
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'Účastník B')]"))
    )
    _click_btn(driver, "odeslat kód do sms")
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((
            By.XPATH, "//*[contains(text(),'Zadejte ověřovací kód')]"
        ))
    )
    set_otp_digits(driver, "1234")
    _click_btn(driver, "podepsat")

    # ── Phase 4: success ──────────────────────────────────────────────────
    _wait_url(driver, "/success", timeout=30)
    success_heading = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((
            By.XPATH, "//*[contains(text(),'Záznam byl odeslán')]"
        ))
    )
    assert success_heading.is_displayed(), "'Záznam byl odeslán' not visible on success page"

    pdf_btn = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((
            By.XPATH,
            "//button[contains(text(),'Stáhnout PDF záznam')]",
        ))
    )
    assert pdf_btn.is_displayed(), "PDF download button not visible on success page"
