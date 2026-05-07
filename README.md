# bouracka-tests

End-to-end test suite + governance methodology for [Bouračka.cz](https://www.bouracka.cz),
the Czech Insurance Bureau (ČKP) self-record web application for minor traffic accidents.

This repository serves a dual purpose:

1. **Working test suite** for the Bouračka SUT — Playwright primary, Cypress + TestCafe + Selenium scaffolds, plus ReadyAPI/Postman API checks
2. **Reference implementation of MI-M-T testing methodology** — V-model assembly-level TestTarget mapping, phased coverage rule introduction, cross-framework data sharing, drift detection, email-deliverability rules, pre-ship audit gates

If you're looking for the **lower-barrier, OSS-friendly version** of the methodology, see the upcoming [`mimt-simple`](https://github.com/petr-yamyang/mimt-simple) (planned CP-SUPIN-06).

## Quick start

Requires Node.js LTS + Python 3.12+ on the test runner.

```bash
git clone https://github.com/petr-yamyang/bouracka-tests.git
cd bouracka-tests
py bouracka.py setup    # one-time, ~5 minutes (npm install + Playwright Chromium)
py bouracka.py test     # per run, ~5 minutes; produces bouracka-results-YYYY-MM-DD-<user>.zip
```

Optional environment override:

```bash
# Test against the DEMO test environment instead of the public DEMO
set BOURACKA_BASE=https://tst.demo.bouracka.cz
py bouracka.py test
```

## Repo layout

| Directory | Purpose |
|-----------|---------|
| `bouracka.py` | Pure-Python orchestrator (setup / test / verify / help) |
| `playwright/` | Primary F/E test suite (8 ALT- variants + full E2E happy-day) |
| `cypress/`, `testcafe/`, `selenium/`, `readyapi/`, `postman/` | Cross-framework parity at smoke level |
| `mockoon/` | N8 SMS gateway mock for DEMO test scenarios |
| `fixtures/` | Test data (single source of truth, YAML) + live-captured codelists |
| `tools/` | Python helpers: coverage audit, pre-ship audit, Excel migrations, reporters |
| `_specs/` | Strategic governance documentation (CS) |
| `_install/` | Install guides + setup procedures |
| `recon/` | Bottom-up analytical recon: site map, integrations, drift forensic, architecture |
| `BOURACKA-TESTPLAN-v0.4.2.xlsx` | Excel master TestPlan with 14 sheets |
| `CHANGELOG.md` | Per-version delta inventory |

## Documentation entry points

- **`READ-ME-FIRST-CS.md`** — three-step tester workflow (CS)
- **`CHANGELOG.md`** — version history
- **`_specs/CP-SUPIN-05-PLAN-CS.md`** — current iteration strategic plan
- **`_specs/EMAIL-DELIVERABILITY-RULES-v0.1-CS.md`** — packaging governance (forbidden file extensions, IOC patterns, fallback channels)
- **`_specs/PLATFORM-ASSESSMENT-v0.1-CS.md`** — evidence-based F/E framework comparison (Playwright > Selenium+Appium > Cypress > TestCafe for this SUT)
- **`_specs/MIMT-NATIVE-AUTOMATION-ASSESSMENT-v0.1-CS.md`** — build-vs-buy decision for MI-M-T native automation harness
- **`_specs/SIMPLIFIED-TESTING-MODEL-v0.1-CS.md`** — `mimt-simple` OSS spec (developer-accessible, no testing-discipline depth required)

Most documentation is in Czech (CS) reflecting the project's local context. English summaries live in this README and `README-EN.md`.

## License

[MIT](LICENSE) — feel free to use, modify, and learn from this project.

## Acknowledgments

- **ČKP** (Česká kancelář pojistitelů) — operator of Bouračka.cz
- **MI-M-T** project context — methodology home
- All test data is **SPECIMEN** material; no real PII
