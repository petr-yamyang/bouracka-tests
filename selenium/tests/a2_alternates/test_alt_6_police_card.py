"""
TC-CP-A2-ALT-6 — Selenium pytest port

Source-of-truth: playwright/tests/a2-alternates-demo.spec.ts (ALT-6 block, line ~140).

Test: Police-criteria accordion card expands to reveal key bullets + tel:158.
  - "Někdo je zraněný nebo došlo k úmrtí" visible
  - "Škoda přesahuje 200 000 Kč" visible (fallback: any "200 000 Kč" occurrence)
  - "Došlo ke srážce se zvěří" visible
  - Anchor href containing "158" visible

Pure UI test — no navToVerification; stays on /formular/ rozcestnik.

Run:
    py -m pytest selenium/tests/a2_alternates/test_alt_6_police_card.py -v
"""
from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from selenium.helpers.data_loader import covers
from selenium.helpers.nav_helpers import dismiss_cookie_banner


def test_TC_CP_A2_ALT_6_police_card(driver, base_url):
    """TC-CP-A2-ALT-6 — Police card expands: 3 bullets + tel:158 visible.

    Covers: TT-SCRN-policeCard
    """
    covers("TT-SCRN-policeCard")

    driver.get(f"{base_url}/formular/")
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    dismiss_cookie_banner(driver)

    # Expand the police accordion by clicking its heading
    heading = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//*[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),"
            "'kdy volat policii')]",
        ))
    )
    heading.click()

    # Bullet 1 — injury / fatality
    bullet_injury = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((
            By.XPATH,
            "//*[contains(text(),'Někdo je zraněný nebo došlo k úmrtí')]",
        ))
    )
    assert bullet_injury.is_displayed(), "Injury/fatality bullet not visible"

    # Bullet 2 — damage threshold; try precise match first, fallback to any 200 000 Kč
    elements_precise = driver.find_elements(
        By.XPATH,
        "//*[contains(text(),'přesahuje') and contains(text(),'200')]",
    )
    if elements_precise:
        assert elements_precise[0].is_displayed(), (
            "Damage-threshold bullet (přesahuje) not visible"
        )
    else:
        # Drift fallback: any visible element with "200 000 Kč"
        elems_200k = driver.find_elements(
            By.XPATH,
            "//*[contains(text(),'200 000 Kč')]",
        )
        visible_200k = [e for e in elems_200k if e.is_displayed()]
        assert visible_200k, "No visible '200 000 Kč' element found (fallback)"

    # Bullet 3 — wildlife collision
    bullet_wildlife = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((
            By.XPATH,
            "//*[contains(text(),'Došlo ke srážce se zvěří')]",
        ))
    )
    assert bullet_wildlife.is_displayed(), "Wildlife-collision bullet not visible"

    # Emergency number link — href="tel:158"
    tel_link = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((
            By.XPATH,
            "//a[contains(@href,'158')]",
        ))
    )
    assert tel_link.is_displayed(), "tel:158 link not visible"
