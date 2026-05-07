# TestExecution Summary — VUP-grade format spec — v0.1 CS

> **Trigger.** CP-SUPIN-04 STEP 32 (2026-05-06): Pete direction —
> "Test Execution Summary detailed repo of results of mainly automated
> tests runs as used in VUP as a core artifact to be implemented now
> and start with gathering results cross environments in better detail —
> step by step execution results, assertion gate pass/fail etc."
>
> **Audience.** Testovací tým + governance + SUPIN review.
> **Cíl.** Specifikovat formát VUP-grade Test Execution Summary
> dokumentu, který nahradí existující JSON-only console outputs.

---

## §1. Co je TestExecution Summary (TES)

VUP (Unified Process) testování má jako **core artefakt** podrobný
záznam každého běhu testu — ne jen pass/fail per TC, ale:

- **Step-by-step execution results** — co každý krok udělal
- **Assertion gate pass/fail** — každá kontrola s verdict
- **Časování** — duration per step, per assertion
- **Evidence** — screenshot/trace/log per step
- **Cross-environment data** — stejný TC na N envech, side-by-side

TES je **per-run** artefakt (jeden run = jeden Excel sheet entry +
jeden JSON dump). Aggregations se dělají z koleckce TES rows.

## §2. Hierarchická struktura

```
Run
├── Run metadata (date, env, framework, runner host, tester)
├── Test Case (per TC)
│   ├── TC metadata (TC-CP-NNN, env_constraint, applies_to_*, ...)
│   ├── Steps (per step in TC SPEC)
│   │   ├── Step description (verbatim from TC SPEC)
│   │   ├── Step execution (action / verification)
│   │   ├── Step assertions (1..N per step)
│   │   │   ├── Assertion description
│   │   │   ├── Expected
│   │   │   ├── Actual
│   │   │   ├── Verdict (pass/fail/skip/error)
│   │   │   └── Evidence (screenshot/trace ref)
│   │   ├── Step duration
│   │   └── Step verdict (worst-of-assertion)
│   ├── TC verdict (worst-of-step)
│   └── TC duration (sum of steps)
└── Run aggregates (totals, coverage)
```

## §3. Excel sheet schema

### §3.1 Sheet `13_TestExecutionSummary` — TC-level run records

| Column | Type | Purpose |
|--------|------|---------|
| `run_id` | TEXT | RUN-YYYYMMDDTHHMMSS-{env} (FK to 06_TestRuns) |
| `tc_code` | TEXT | TC-CP-NNN (FK to 02_TestCases.item_code) |
| `tc_title` | TEXT | denormalised from TC SPEC |
| `framework` | ENUM | playwright/cypress/testcafe/readyapi/postman/selenium |
| `env` | ENUM | DEMO_PROD/DEMO_tst/PROD/PROD_tst/LOCAL/MOCKOON |
| `viewport` | TEXT | (mobile-XXX, desktop, …) |
| `started_at` | DATETIME | ISO 8601 |
| `ended_at` | DATETIME | ISO 8601 |
| `duration_ms` | INT | total TC duration |
| `verdict` | ENUM | pass/fail/blocked/skipped/error |
| `step_count` | INT | total steps in this TC's execution |
| `assertion_count` | INT | total assertions |
| `assertion_pass_count` | INT |   |
| `assertion_fail_count` | INT |   |
| `failed_at_step` | INT | first failing step number; NULL if passed |
| `failed_at_assertion` | TEXT | assertion code / line if failed |
| `error_message` | TEXT | (≤500 chars, latest if retry) |
| `retry` | INT | retry attempt (0 = first run) |
| `screenshot_path` | TEXT | screenshot of failure state |
| `trace_path` | TEXT | trace/video/log archive |
| `bug_ref` | TEXT | BUG-CP-{TC}-{ASSERT} if filed (cross-link to 08_Bugs) |
| `tester` | TEXT | who triggered (Pete, CI bot, etc.) |
| `created_at` | DATETIME | row insert time |

### §3.2 Sheet `14_AssertionGateResults` — assertion-level detail

| Column | Type | Purpose |
|--------|------|---------|
| `run_id` | TEXT | FK to 06_TestRuns |
| `tc_code` | TEXT | FK to 02_TestCases |
| `step_no` | INT | step number within TC (1, 2, …) |
| `step_kind` | ENUM | trigger_point / control_point / data_collection_point / assertion |
| `step_description` | TEXT | verbatim from TC SPEC |
| `assertion_code` | TEXT | S{N}-{LETTER} (e.g. S5-A for first assertion in step 5) |
| `assertion_kind` | ENUM | url_match / element_visible / response_status / response_body / regex_match / count / timing / custom |
| `assertion_expected` | TEXT | what we expected |
| `assertion_actual` | TEXT | what we observed |
| `verdict` | ENUM | pass / fail / skip / error |
| `duration_ms` | INT | assertion timeout / actual time |
| `evidence_ref` | TEXT | screenshot/trace pointer |
| `notes` | TEXT | optional triage hint |

### §3.3 Existing `06_TestRuns` (run-level rollup) — unchanged but FK target

`06_TestRuns` is the run-id master table. `13_TestExecutionSummary`
references it via `run_id`.

## §4. JSON format (serialization for cross-tool exchange)

For programmatic consumption (test_console.py, MI-M-T import, CI dashboards):

```json
{
  "run_id": "RUN-20260507T080000-DEMO_PROD",
  "metadata": {
    "started_at": "2026-05-07T08:00:00.000Z",
    "ended_at":   "2026-05-07T08:02:30.123Z",
    "duration_ms": 150123,
    "framework": "playwright",
    "framework_version": "1.45.0",
    "env": "DEMO_PROD",
    "env_url": "https://demo.bouracka.cz",
    "tester": "Pete",
    "runner_host": "ThinkPad-Petr",
    "ci": false
  },
  "test_cases": [
    {
      "tc_code": "TC-CP-001",
      "tc_title": "Bring-up smoke",
      "verdict": "pass",
      "duration_ms": 8210,
      "steps": [
        {
          "step_no": 1,
          "step_kind": "trigger_point",
          "step_description": "Navigate to /formular/",
          "duration_ms": 2100,
          "verdict": "pass",
          "assertions": [
            {
              "assertion_code": "S1-A",
              "assertion_kind": "url_match",
              "assertion_expected": "/formular/",
              "assertion_actual": "https://demo.bouracka.cz/formular/",
              "verdict": "pass",
              "duration_ms": 100
            }
          ]
        },
        {
          "step_no": 2,
          "step_kind": "data_collection_point",
          "step_description": "Dismiss cookie banner",
          "duration_ms": 1200,
          "verdict": "pass",
          "assertions": []
        },
        {
          "step_no": 3,
          "step_kind": "assertion",
          "step_description": "Page identity heading visible",
          "duration_ms": 850,
          "verdict": "pass",
          "assertions": [
            {
              "assertion_code": "S3-A",
              "assertion_kind": "element_visible",
              "assertion_expected": "/Stala se vám dopravní nehoda/i",
              "assertion_actual": "Stala se vám dopravní nehoda? To zvládnete.",
              "verdict": "pass",
              "duration_ms": 850
            }
          ]
        }
      ],
      "aggregates": {
        "step_count": 9,
        "assertion_count": 12,
        "assertion_pass_count": 12,
        "assertion_fail_count": 0
      }
    }
  ],
  "run_aggregates": {
    "tc_total": 1,
    "tc_passed": 1,
    "tc_failed": 0,
    "tc_skipped": 0,
    "step_total": 9,
    "step_passed": 9,
    "assertion_total": 12,
    "assertion_pass_rate_pct": 100.0,
    "duration_total_ms": 8210
  }
}
```

## §5. Per-framework reporter integration

| Framework | Reporter mechanism | Output mapping |
|-----------|---------------------|-----------------|
| Playwright | custom reporter `excel-row-writer.ts` | step_no via `test.step()`; assertions via `expect()` chain |
| Cypress | `cypress-mochawesome-reporter` + custom hook | step via `cy.then()`; assertions via `cy.should()` |
| TestCafe | custom reporter (TestCafe Reporter API) | step via `t.expect()`; less granular |
| ReadyAPI | JUnit XML + `xUnitToTES.py` translator | step from test step name; assertions from `<assertion>` elements |
| Postman | Newman JSON + `newmanToTES.py` translator | step from request name; assertions from `pm.expect()` |
| Selenium | pytest + JSON test report + `pytestToTES.py` translator | step from `with allure.step()`; assertions from `assert` |

All translators normalize to the **§4 JSON format** then `tools/append_test_run_result.py`
upserts into Excel.

## §6. VUP review presentation (per CP-SUPIN-05)

For governance review, generate from §3 sheets:

1. **Run-level rollup table** — RUN-X | env | framework | TC pass/fail/skip | duration
2. **TC trend** — pro každý TC: last 30 runs verdict timeline (mini sparkline)
3. **Failure heatmap** — TC × env × framework grid; cells colored by verdict
4. **Assertion gate health** — top 20 most-failing assertions (triage candidates)
5. **Cross-environment delta** — same TC's verdict on DEMO vs PROD vs PROD_tst

Generated as separate analytical sheet (`15_VUP_Dashboard`) or external
Mermaid/PNG renders.

## §7. Aktuální stav (CP-SUPIN-04 STEP 32)

| Item | Status |
|------|--------|
| Format spec (this doc) | v0.1 locked |
| Excel schema 13 + 14 | TBD next migration |
| Playwright reporter wires up step + assertion granularity | partial — need refactor pro `test.step()` adoption |
| ReadyAPI/Postman/Selenium translators | TBD CP-SUPIN-05 |
| VUP dashboard | TBD CP-SUPIN-05 |

## §8. Status

| Item | Hodnota |
|------|---------|
| Spec | `_specs/TEST-EXECUTION-SUMMARY-FORMAT-v0.1-CS.md` |
| Verze | v0.1 |
| Datum | 2026-05-06 |
| Audience | SUPIN testers + governance |
| Status | format locked; implementation phased per CP-SUPIN-05 |
