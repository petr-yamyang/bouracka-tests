"""
selenium/conftest.py — shared pytest fixtures for all Selenium tests

CP-SUPIN-05 cross-framework parity.

Run all Selenium tests:
    py -m pytest selenium/ -v

Run specific TC:
    py -m pytest selenium/tests/a2_alternates/test_alt_7_enumerations.py -v

Requirements:
    pip install selenium webdriver-manager pytest pyyaml requests
    pip install selenium-wire   # optional, for ALT-10 network capture fallback

Environment variables:
    BOURACKA_BASE  defaults to https://demo.bouracka.cz
"""
from __future__ import annotations

import os

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService

try:
    from webdriver_manager.chrome import ChromeDriverManager
    _HAS_WDM = True
except ImportError:
    _HAS_WDM = False


BASE = os.environ.get("BOURACKA_BASE", "https://demo.bouracka.cz")


def _build_mobile_options() -> ChromeOptions:
    """Mobile-emulated Chrome (375x667, cs-CZ) — AMENDMENT 2 mobile-first."""
    opts = ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--lang=cs-CZ")
    opts.add_experimental_option(
        "mobileEmulation",
        {
            "deviceMetrics": {"width": 375, "height": 667, "pixelRatio": 2.0},
            "userAgent": (
                "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                "Version/15.0 Mobile/15E148 Safari/604.1"
            ),
        },
    )
    return opts


@pytest.fixture(scope="function")
def driver():
    """Mobile-emulated headless Chrome — 375×667, cs-CZ.

    Scope: function — each test gets a fresh browser session.
    """
    opts = _build_mobile_options()
    if _HAS_WDM:
        svc = ChromeService(ChromeDriverManager().install())
        drv = webdriver.Chrome(service=svc, options=opts)
    else:
        drv = webdriver.Chrome(options=opts)
    drv.set_window_size(375, 667)
    yield drv
    drv.quit()


@pytest.fixture(scope="function")
def base_url() -> str:
    """Base URL for the test target (BOURACKA_BASE env var)."""
    return BASE
