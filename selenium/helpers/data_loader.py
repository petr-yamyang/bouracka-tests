"""
selenium/helpers/data_loader.py — CP-SUPIN-05 fixture loader

Per _specs/CROSS-FRAMEWORK-DATA-SHARING-v0.1-CS.md §4.2.

Usage:
    from selenium.helpers.data_loader import load_fixture, covers

    data = load_fixture("test-participants")
    phone_a = data["participants"]["A"]["phone"]

    covers("TT-FUNC-001", "TT-LOV-insuranceCompanies")
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

# Project root → fixtures/test-data/
FIXTURES_ROOT = Path(__file__).resolve().parents[3] / "fixtures" / "test-data"


def load_fixture(name: str) -> dict[str, Any]:
    """Load a YAML fixture by base name (without .yaml extension).

    Args:
        name: bare fixture name, e.g. "test-participants" or "test-vehicles"

    Returns:
        Parsed YAML object as a Python dict.

    Raises:
        FileNotFoundError: if the fixture file is not found at FIXTURES_ROOT.
    """
    base = name.removesuffix(".yaml")
    path = FIXTURES_ROOT / f"{base}.yaml"
    if not path.exists():
        raise FileNotFoundError(
            f"Fixture not found: {path}\n"
            f"FIXTURES_ROOT = {FIXTURES_ROOT}\n"
            f"Available: {sorted(p.name for p in FIXTURES_ROOT.glob('*.yaml'))}"
        )
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def covers(*tt_codes: str) -> None:
    """Metadata annotation — records which TestTarget (TT) codes are exercised.

    No effect on test pass/fail. Prints to stdout for capture in pytest -s.

    Per _specs/CROSS-FRAMEWORK-PARITY-EXECUTION-v0.1-CS.md §7.1 acceptance #2.

    Example:
        covers("TT-LOV-vehicleBrands", "TT-SCRN-rozcestnik")
    """
    print(f"[covers] {', '.join(tt_codes)}")
