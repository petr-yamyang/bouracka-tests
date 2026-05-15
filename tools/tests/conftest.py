"""pytest fixtures for workbook patcher tests."""

from __future__ import annotations

import pathlib
import shutil
import tempfile

import pytest

FIXTURES_DIR = pathlib.Path(__file__).parent / "fixtures"
SYNTHETIC_SOURCE = FIXTURES_DIR / "synthetic-v0.4.3-mini.xlsx"
REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
REAL_SOURCE = REPO_ROOT / "BOURACKA-TESTPLAN-v0.4.3.xlsx"


@pytest.fixture()
def synthetic_source(tmp_path: pathlib.Path) -> pathlib.Path:
    """Copy synthetic fixture into tmp_path; return path to the copy."""
    dest = tmp_path / "synthetic-v0.4.3-mini.xlsx"
    shutil.copy2(SYNTHETIC_SOURCE, dest)
    return dest


@pytest.fixture()
def patched_workbook(synthetic_source: pathlib.Path, tmp_path: pathlib.Path):
    """Run the patcher against the synthetic source and return (dest_path, report_path)."""
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
    from importlib import import_module

    patcher_mod = _load_patcher()
    dest = tmp_path / "synthetic-v0.4.4.xlsx"
    rc = patcher_mod.patch(synthetic_source, dest, dry_run=False, verbose=False)
    assert rc in (0, 1), f"Patcher returned unexpected exit code {rc}"
    return dest


def _load_patcher():
    """Import tools/workbook-v0.4.3-to-v0.4.4.py as a module."""
    import importlib.util
    spec_path = pathlib.Path(__file__).resolve().parent.parent / "workbook-v0.4.3-to-v0.4.4.py"
    spec = importlib.util.spec_from_file_location("workbook_patcher", spec_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
