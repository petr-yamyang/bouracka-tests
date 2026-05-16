# Sonnet brief — BRIEF-004: hotfix bundle (BUG-K-009, K-010, K-012)

**Target Claude.** Sonnet 4.6 in Claude Code (terminal, stateless).
**Issued by.** Opus 4.7 session (Pete Y. + Claude), 2026-05-15.
**Branch.** `cp-supin-13-hotfix-bundle` (create from current `main` head).
**Estimated effort.** ~2 hours.
**Reviewer.** Pete in Opus 4.7 session after §10 checklist.
**Blocked by.** Nothing — independent of #002/#003/#001b/#005/#009 work.

---

## 1. Goal in one paragraph

Bundle three independent fixes that each block real dispatch reaching ship quality, all folded into the v0.1.5 release per `_config/MAJOR-DEV-SESSION-PLAN-v0.1.5-EN.md` §2.1. BUG-K-009: doc-only — add Node.js + selenium prereq section to KATE-V0.1.4-REINSTALL-CS.md. BUG-K-010: code — `dispatcher.py` sends `--env tst-demo` (rejected by consolidator) instead of split `--env demo --env-url https://tst.demo.bouracka.cz`. BUG-K-012: code — `/api/runs` POST + `workbook_io` overwrite the single `06_TestRuns` row instead of appending per-dispatch rows. All three are surgical changes; total diff under 200 lines.

---

## 2. Spec — read this BEFORE coding

1. `_config/MAJOR-DEV-SESSION-PLAN-v0.1.5-EN.md` §2.1 — bundle scope
2. **Kate's actual failure log** (in this brief §3 below) — concrete evidence of BUG-K-010
3. `bouracka_ui/bouracka_ui/dispatcher.py` — `_run_consolidator` (around line ~250+) — find where `--env $env` is constructed
4. `bouracka_ui/bouracka_ui/server.py` `/api/runs` POST handler (line ~210) + `workbook_io` — find where TestRuns sheet is touched
5. `delivery/KATE-V0.1.4-REINSTALL-CS.md` §1 (or wherever prereqs live) — for BUG-K-009 doc-only fix

---

## 3. BUG-K-010 evidence (verbatim from Kate's run log 2026-05-14)

```
[bouracka-ui] env=tst-demo (https://tst.demo.bouracka.cz)
...
[consolidate] $ ...consolidate_results.py --env tst-demo --env-url https://tst.demo.bouracka.cz ...
[consolidate] consolidate_results.py: error: argument --env: invalid choice: 'tst-demo'
              (choose from demo, tst, uat, prod-readonly, prod-writable)
[consolidate] exit_code=2
[consolidate] WARNING: envelope not found at ...
```

**Root cause:** UI env label `tst-demo` (a compound label = tier + sub-env) is passed verbatim to `consolidate_results.py --env` which only accepts tier names. The base URL is already in `--env-url`.

**Fix shape:** in dispatcher.py where `--env <env>` argument is built, normalize the UI label to a tier name before passing to consolidator. Lookup table:

```python
UI_ENV_TO_TIER = {
    "demo":           "demo",
    "tst-demo":       "demo",       # tst sub-env of demo tier
    "tst":            "tst",
    "uat":            "uat",
    "prod-readonly":  "prod-readonly",
}
```

`--env-url` continues to carry the full sub-env URL (already correct in current code per the log evidence).

---

## 4. File boundaries

### Create

- (no new files)

### Modify

- `bouracka_ui/bouracka_ui/dispatcher.py` — F-1 below
- `bouracka_ui/bouracka_ui/server.py` — F-2 below (if append logic lives here)
- `bouracka_ui/bouracka_ui/workbook_io.py` — F-2 below (if append logic lives here)
- `delivery/KATE-V0.1.4-REINSTALL-CS.md` — F-3 below (doc only)
- `delivery/SUPIN-SERVER-INSTALL-FROM-ZERO-CS.md` — F-3 below (same prereq section pattern)
- `delivery/PETE-HP-ELITE-DROP-2026-05-13/PETE-V0.1.4-ALIGN-CS.md` — F-3 below (mirror Kate runbook)
- `bouracka_ui/tests/test_smoke.py` — add 4 tests (F-4)
- `bouracka_ui/bouracka_ui/__init__.py` → `__version__ = "0.1.5-dev4"`
- `bouracka_ui/pyproject.toml` → `version = "0.1.5.dev4"`
- `CHANGELOG.md` — append v0.1.5-dev4 entry

### DO NOT touch

- `tools/consolidate_results.py` — that's the consumer; we fix the producer (dispatcher) per design
- `audit_dispatcher.py` (Brief #009 territory) — separate rail
- `workbook-v0.4.3-to-v0.4.4.py` — out of scope
- `_config/` — read-only specs

---

## 5. Functional requirements

### F-1. BUG-K-010 — dispatcher env normalization

**Locate** the function in `dispatcher.py` that constructs the consolidator subprocess invocation. Look for `--env` arg construction near a `subprocess.Popen` or `await asyncio.create_subprocess_exec`.

**Add** at module top (or near ENV_TO_BASE_URL):

```python
UI_ENV_TO_CONSOLIDATOR_TIER = {
    "demo":           "demo",
    "tst-demo":       "demo",       # sub-env of demo tier
    "tst":            "tst",
    "uat":            "uat",
    "prod-readonly":  "prod-readonly",
    "prod-writable":  "prod-writable",  # future extensibility; consolidator already supports
}

def normalize_env_for_consolidator(ui_env: str) -> str:
    """UI env label → consolidator --env tier name. Raises ValueError on unknown."""
    if ui_env not in UI_ENV_TO_CONSOLIDATOR_TIER:
        raise ValueError(f"unknown UI env label: {ui_env}")
    return UI_ENV_TO_CONSOLIDATOR_TIER[ui_env]
```

**Replace** the `--env <env>` arg construction with:

```python
consolidator_args = [
    sys.executable, str(consolidate_path),
    "--env", normalize_env_for_consolidator(env),
    "--env-url", ENV_TO_BASE_URL.get(env, ""),
    ...
]
```

Verify the test passes: real-mode dispatch with `env="tst-demo"` produces `--env demo --env-url https://tst.demo.bouracka.cz` in the consolidator call.

### F-2. BUG-K-012 — TestRuns append vs overwrite

**Investigate first.** Read `server.py` `/api/runs` POST handler (line ~210). The current state probably tracks runs in `_RUN_REGISTRY` (in-memory dict) only, and writes to workbook either via `workbook_io.append_run` (if it exists) OR not at all (runs are filesystem-only via `runs/cross-framework-*.json` envelopes).

**Two outcomes possible:**

**Outcome A — workbook NOT touched by dispatch.** Runs are persisted ONLY as envelope files. Then Kate's complaint ("Runs being overwritten") actually means: SHE manually adds rows to `06_TestRuns` to track them, and the workbook patcher (or a sync) overwrites them. In this case, BUG-K-012 is closer to BUG-K-011 (patcher data preservation). Note in §10 item 6 and STOP — don't change anything unless this is wrong.

**Outcome B — workbook IS touched on dispatch (append_run exists or similar).** Find the function. If it's writing/overwriting a single row at index 1 (or always row 2), change it to truly append using `ws.max_row + 1`. Schema:

```python
def append_test_run(wb_path: Path, run_record: dict) -> None:
    """Append a row to 06_TestRuns. NEVER overwrites existing rows."""
    wb = openpyxl.load_workbook(wb_path)
    ws = wb["06_TestRuns"]
    headers = [c.value for c in ws[1]]
    col_map = {h: i for i, h in enumerate(headers) if h}
    new_row = ws.max_row + 1
    for key, value in run_record.items():
        if key in col_map:
            ws.cell(row=new_row, column=col_map[key] + 1, value=value)
    wb.save(wb_path)
```

Test: dispatch run twice in a row → `06_TestRuns.max_row` increments by 2.

### F-3. BUG-K-009 — runbook prereq section

In each of Kate / SUPIN-server / Pete-HP-Elite install runbooks, add a new top-of-file §1 (or before existing §1) titled "**Předpoklady na cílovém stroji**" (CS) — must be installed BEFORE running the bouracka-ui installer:

```markdown
### §1.0 Předpoklady (MUSÍ být nainstalované)

| Co | Verze | Proč | Jak |
|----|-------|------|-----|
| Python | 3.10 / 3.11 / 3.12 (jedno z) | bouracka-ui běhové prostředí | Stáhni z python.org → installer s defaulty (NE Microsoft Store edice) |
| Node.js | 20+ LTS | npx → cypress + playwright | Stáhni z nodejs.org → "LTS" → installer s defaulty |
| Cypress + Playwright deps | per package.json | framework runtime | `cd tests-source\cypress && npm install` + `cd ..\playwright && npm install && npx playwright install chromium` (vyžaduje internet) |
| Selenium python | `pip install selenium` | selenium webdriver | Po `pip install bouracka_ui-...whl` ve venv |

Bez Node.js → cypress/playwright nepoběží (WinError 2 / [tooling not found]).
Bez selenium pip → selenium suite hodí ImportError při loadu conftest.py.
```

Pattern identical across all 3 runbooks. SUPIN server version adds note about systemd service account needing access to npm cache.

### F-4. Smoke tests (4 new)

```python
def test_normalize_env_for_consolidator():
    """F-1: tst-demo → demo, tst → tst, etc."""
    from bouracka_ui.dispatcher import normalize_env_for_consolidator
    assert normalize_env_for_consolidator("tst-demo") == "demo"
    assert normalize_env_for_consolidator("demo") == "demo"
    assert normalize_env_for_consolidator("tst") == "tst"
    assert normalize_env_for_consolidator("uat") == "uat"
    with pytest.raises(ValueError):
        normalize_env_for_consolidator("bogus-env")

def test_dispatcher_uses_normalized_env_in_consolidator_invocation(monkeypatch):
    """F-1: when env='tst-demo', the consolidator argv contains '--env demo' not '--env tst-demo'."""
    # Capture subprocess.create_subprocess_exec calls
    captured_argvs = []
    async def fake_create_subprocess_exec(*argv, **kwargs):
        captured_argvs.append(argv)
        class FakeProc:
            returncode = 0
            async def communicate(self): return (b"", b"")
        return FakeProc()
    monkeypatch.setattr("asyncio.create_subprocess_exec", fake_create_subprocess_exec)
    # ... trigger dispatch in mock-or-real-fallback path
    # Assert: "--env" in argv AND argv[argv.index("--env") + 1] == "demo"

def test_test_runs_append_not_overwrite(tmp_workbook):
    """F-2 outcome B: append 3 runs → 3 rows total."""
    if not hasattr(workbook_io, "append_test_run"):
        pytest.skip("append_test_run not implemented (Outcome A — workbook untouched)")
    initial = _count_rows(tmp_workbook, "06_TestRuns")
    workbook_io.append_test_run(tmp_workbook, {"run_id": "run-A", ...})
    workbook_io.append_test_run(tmp_workbook, {"run_id": "run-B", ...})
    workbook_io.append_test_run(tmp_workbook, {"run_id": "run-C", ...})
    assert _count_rows(tmp_workbook, "06_TestRuns") == initial + 3

def test_install_runbook_has_prereq_section():
    """F-3: each install runbook has §1.0 prereq table mentioning Node.js + selenium."""
    paths = [
        Path("delivery/KATE-V0.1.4-REINSTALL-CS.md"),
        Path("delivery/SUPIN-SERVER-INSTALL-FROM-ZERO-CS.md"),
    ]
    for p in paths:
        text = p.read_text(encoding="utf-8")
        assert "Node.js" in text and "selenium" in text.lower(), \
            f"{p} missing prereq mention"
```

### F-5. Version bump

```
__version__ = "0.1.5-dev4"
version = "0.1.5.dev4"
```

CHANGELOG v0.1.5-dev4:

- BUG-K-009: install runbook prereq section (Node + selenium)
- BUG-K-010: dispatcher env normalization for consolidator
- BUG-K-012: TestRuns append behavior (Outcome A: documented as patcher concern; Outcome B: real fix)

---

## 6. Idempotency

- Re-running with already-fixed dispatcher: `normalize_env_for_consolidator` is idempotent — gives same output every time.
- Append test runs: only adds, never removes. Multiple dispatches → multiple rows, exactly as expected.

---

## 7. CLI surface

No CLI changes.

---

## 8. Risk gates — STOP and report

1. **F-1: cannot find the consolidator subprocess invocation in dispatcher.py.** Halt; share grep output for `--env` / `consolidate_results` / `Popen`. Pete points you at the right line.
2. **F-2: Outcome A is the actual state (workbook untouched).** Then BUG-K-012 is a misdiagnosis — note in §10 item 6 with explanation, do NOT change workbook_io. The "TestRuns overwritten" Kate observed is actually her own workbook editing behavior + patcher.
3. **F-2: append_test_run already exists and looks correct on inspection.** Run integration test against real workbook to verify; if 3 dispatches → only 1 row appears, halt + investigate WHY (file lock? race? schema mismatch?).
4. **F-3: install runbook structure too different to graft `§1.0` cleanly.** Halt; share the existing §1 + propose alternative insertion point.

---

## 9. Don't-go-beyond

- Don't touch `consolidate_results.py` — fix the producer (dispatcher), not the consumer
- Don't change `--env-url` semantics — already correct
- Don't implement env-mapping in workbook (the table belongs in dispatcher, not data)
- Don't refactor dispatcher beyond the F-1 patch
- Don't change `06_TestRuns` schema — append only

---

## 10. Return checklist

1. Branch + SHAs
2. Files changed
3. Test results
4. Show output of mock dispatch with `env="tst-demo"` — confirm `--env demo --env-url https://tst.demo.bouracka.cz` in consolidator call
5. F-2 outcome (A or B) — be explicit
6. Out-of-scope findings
7. Deviations
8. Open questions

---

## 11. Acceptance

- All 4 new tests pass; existing tests stay green
- Manual: dispatch with env=tst-demo → consolidator runs without "invalid choice" error
- 3 runbooks have §1.0 prereq section
- `__version__` reads `0.1.5-dev4`
- CHANGELOG updated
- Branch ready for merge

---

**End of BRIEF-004.**
