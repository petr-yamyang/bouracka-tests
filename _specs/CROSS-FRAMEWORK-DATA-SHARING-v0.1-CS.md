# Cross-framework test-data sharing convention — v0.1 CS

> **Trigger.** CP-SUPIN-05 STEP 2 — Pete: "expand test sets per technological
> base — Playwright, Cypress, TestCafe, Selenium — sharing same testbase and
> testdata".
>
> **Princip.** Single source of truth pro test data + per-framework adapters,
> aby přidání 1 nové test-data fixture neznamenalo 4× ručně sync.

---

## §1. Současný stav (CP-SUPIN-04 closure)

| Framework | Current data location | Sharing? |
|-----------|----------------------|----------|
| Playwright | `playwright/tests/*.spec.ts` (inline strings) | ❌ duplicated per spec |
| Cypress | `cypress/e2e/*.cy.ts` (inline strings) | ❌ duplicated |
| TestCafe | `testcafe/tests/*.ts` (inline strings) | ❌ duplicated |
| Selenium | `selenium/tests/*.py` (inline strings) | ❌ duplicated |
| ReadyAPI | `readyapi/projects/*.xml` (XML test data) | ❌ separate format |
| Postman | `postman/collections/*.json` (collection vars) | ❌ separate format |

**Důsledek.** Když změníme např. `phoneA = "608000001"` na `"608000099"`, musíme
to upravit v 6 frameworks. Drift mezi frameworks je nevyhnutelný.

## §2. Cílový stav

```
fixtures/test-data/
├── test-participants.yaml       ← single source of truth
├── test-vehicles.yaml
├── test-addresses.yaml
├── test-otp-codes.yaml
├── codelists-live-2026-05-06.yaml  (existing, captured z live recon)
├── api-endpoints-live-2026-05-06.yaml (existing)
└── live-copy-strings.yaml       (existing, 17 STR rows)
```

Per framework existuje **loader adapter**:

```
playwright/helpers/data-loader.ts        ← reads YAML, returns typed JS object
cypress/support/data-loader.ts            ← same
testcafe/helpers/data-loader.ts           ← same
selenium/helpers/data_loader.py           ← Python equivalent

# B/E frameworks have their own quirks but follow similar pattern:
readyapi/data-loaders/data-loader.groovy  ← (TBD when ČKP IT engages)
postman/scripts/preReq-load-data.js       ← Postman pre-request script
```

## §3. YAML data shape

```yaml
# fixtures/test-data/test-participants.yaml — example
participants:
  A:
    name: "Adam Test"
    surname: "Demoversen"
    op_number: "123456789"
    birth_date: "01.01.1990"
    email: "demo-test-A@example.com"
    phone: "608000001"
    phone_prefix: "+420"
    address_query: "Václavské"  # for RUIAN autocomplete
    gdpr_consent: true
    otp_code: "1234"
  B:
    name: "Beáta Demova"
    surname: "Druhá"
    op_number: "987654321"
    birth_date: "02.02.1985"
    email: "demo-test-B@example.com"
    phone: "608000002"
    phone_prefix: "+420"
    address_query: "Národní"
    gdpr_consent: true
    otp_code: "5678"

vehicles:
  A:
    spz: "1AB 2345"
    brand: "ŠKODA"
    model: "Octavia"
    insurer: "Allianz"
    color: "černá"
    desc: "Levá strana lehce poškozena. Kapota neporušená. Bez zranění."
  B:
    spz: "5XY 6789"
    brand: "VOLKSWAGEN"
    model: "Golf"
    insurer: "Kooperativa"
    color: "stříbrná"
    desc: "Pravý zadní nárazník odřený. Bez zranění."

negative_data:
  bad_op_number: "INVALID_FORMAT_123"   # for ALT-1 ŘP regex test
  invalid_otp: "0000"                   # for OTP failure paths
  too_short_phone: "608"                # for phone length validation
  empty_consent: false                  # for GDPR negative
```

## §4. Per-framework loader pattern

### §4.1 TypeScript (Playwright / Cypress / TestCafe)

```typescript
// playwright/helpers/data-loader.ts
import * as YAML from "yaml";
import * as fs from "fs";
import * as path from "path";

const fixturesRoot = path.resolve(__dirname, "../../fixtures/test-data");

export function loadFixture<T = any>(name: string): T {
  const p = path.join(fixturesRoot, `${name}.yaml`);
  return YAML.parse(fs.readFileSync(p, "utf-8")) as T;
}

// Usage in spec:
import { loadFixture } from "../helpers/data-loader";
const participants = loadFixture<{participants: Record<string, any>}>("test-participants").participants;
const vehicleA = loadFixture<{vehicles: Record<string, any>}>("test-vehicles").vehicles.A;
```

Stejný adapter pattern pro Cypress (`cypress/support/data-loader.ts`) a
TestCafe (`testcafe/helpers/data-loader.ts`); jen relative path se liší.

### §4.2 Python (Selenium pytest)

```python
# selenium/helpers/data_loader.py
from pathlib import Path
import yaml

FIXTURES_ROOT = Path(__file__).resolve().parents[2] / "fixtures" / "test-data"

def load_fixture(name: str) -> dict:
    p = FIXTURES_ROOT / f"{name}.yaml"
    with open(p, encoding="utf-8") as h:
        return yaml.safe_load(h)

# Usage in test:
from helpers.data_loader import load_fixture
participants = load_fixture("test-participants")["participants"]
vehicle_a = load_fixture("test-vehicles")["vehicles"]["A"]
```

### §4.3 ReadyAPI / SoapUI (Groovy)

```groovy
// readyapi/data-loaders/data-loader.groovy
import org.yaml.snakeyaml.Yaml
def fixturesRoot = new File(testCase.testSuite.project.path).parent + "/../../fixtures/test-data"
def yaml = new Yaml()
def participants = yaml.load(new File("${fixturesRoot}/test-participants.yaml").text)
testRunner.testCase.setPropertyValue("phone_A", participants.participants.A.phone)
testRunner.testCase.setPropertyValue("otp_A", participants.participants.A.otp_code)
```

### §4.4 Postman (pre-request script)

Postman nemá filesystem access. Workaround: convert YAML → environment.json
pre-build:

```bash
# tools/build-postman-env.py
python3 tools/build-postman-env.py \
  --in fixtures/test-data/test-participants.yaml \
  --out postman/environments/test-data.environment.json
```

Postman pak loaduje `test-data.environment.json` jako environment variables,
přístupné v request body via `{{phone_A}}` syntax.

## §5. TC code alignment napříč frameworks

**Pravidlo.** Stejný TC code musí mít stejný název a stejný outcome napříč
všemi 4 frameworks.

| TC code | Playwright | Cypress | TestCafe | Selenium |
|---------|------------|---------|----------|----------|
| TC-CP-001 (bring-up) | `playwright/tests/bring-up-smoke.spec.ts` ✅ | `cypress/e2e/bring-up-smoke.cy.ts` ✅ | `testcafe/tests/bring-up-smoke.test.ts` ✅ | `selenium/tests/test_bring_up_smoke.py` ✅ |
| TC-CP-A1-MAIN-DEMO | `a1-main-happy-day-demo.spec.ts` ✅ | (port v fáze 2) | (port v fáze 2) | (port v fáze 2) |
| TC-CP-A2-ALT-1 | `a2-alternates-demo.spec.ts:64` ✅ | (port v fáze 2) | (port v fáze 2) | (port v fáze 2) |
| ... | ... | ... | ... | ... |

**Test title convention:**
- TS: `test("TC-CP-A2-ALT-1 — Phase 2 ŘP regex rejects malformed input", ...)`
- Python: `def test_tc_cp_a2_alt_1_rp_regex_rejects(...)`
- Group display name: `TC-CP-A2-* — alternate flows on DEMO`

Reporter consoliation (viz §6) extrahuje TC code přes regex `/\bTC-CP-[A-Z0-9-]+\b/`.

## §6. Reporter consolidation (CP-SUPIN-05 fáze 3)

```
                                                  ┌─────────────────────┐
   Playwright run  ── results.json ──→            │                     │
   Cypress run    ── mochawesome.json ──→         │  tools/             │
                                                  │  consolidate_       │
   TestCafe run   ── reporter-json output ──→     │   results.py        │
                                                  │                     │
   Selenium run   ── pytest --junit-xml ──→       │                     │
                                                  └──────────┬──────────┘
                                                             ▼
                                              common-results-{date}.json
                                                             │
                                                             ▼
                                          tools/append_test_run_result.py
                                                             │
                                                             ▼
                                           BOURACKA-TESTPLAN-v0.X.Y.xlsx
                                              → 13_TestExecutionSummary
                                              → 14_AssertionGateResults
                                              → 16_CoverageMatrix (CP-SUPIN-06+)
```

**Common JSON schema** (per-test entry):

```json
{
  "tc_code": "TC-CP-A2-ALT-1",
  "framework": "playwright|cypress|testcafe|selenium",
  "status": "passed|failed|skipped|interrupted",
  "duration_ms": 12345,
  "started_at": "2026-05-07T14:50:00Z",
  "ended_at":   "2026-05-07T14:50:12Z",
  "env": "https://demo.bouracka.cz",
  "viewport": "375x*",
  "retry": 0,
  "error_message": "...",
  "screenshot_ref": "test-results/.../test-failed-1.png",
  "trace_ref": "test-results/.../trace.zip",
  "covered_tt": ["TT-FUNC-002", "TT-SCRN-overeni", "TT-ACTV-OTP-input"]
}
```

`covered_tt` field je nový — naplní se ze static map v `_specs/VMODEL-ASSEMBLY-TT-MAPPING.md`
nebo z explicit annotation v test source.

## §7. Migration plan

### §7.1 v0.5.0 (immediate)

- Tento doc + adresář skeleton `fixtures/test-data/`
- Initial fixtures: `test-participants.yaml`, `test-vehicles.yaml` z existing inline data
- Žádné refaktoring testů yet — jen scaffold pro připravení

### §7.2 v0.5.1 (next iteration)

- Implementovat `playwright/helpers/data-loader.ts` + refaktorovat `a1-main-happy-day-demo.spec.ts` na něj
- Initial port `a2-alternates-demo.spec.ts` na Cypress (s data-loader)
- Initial port `bring-up-smoke` adopting unified data-loader
- Excel `13_TestExecutionSummary` schema rozšířen o `covered_tt` JSON column

### §7.3 v0.6.0 (mid CP-SUPIN-05)

- Cypress + TestCafe + Selenium ports of full a2-alternates suite
- `tools/consolidate_results.py` first impl
- First evidence-based cross-framework comparison report

### §7.4 v0.7.0 (CP-SUPIN-05 close)

- Reporter consolidation v plnou produkci
- Coverage matrix integration (TC × TT bindings exported per run)
- Decision: which frameworks proceed full-suite vs which stay smoke-only

## §8. Open questions

| # | Otázka | Owner |
|---|--------|-------|
| Q1 | Cypress uses CommonJS modules; how do we share TS data-loader cleanly? | Opus next |
| Q2 | Selenium pytest fixture vs `load_fixture()` — který pattern dominantní? | Opus next |
| Q3 | Postman: stačí pre-build env file, nebo skutečně live YAML reload? | Pete (low priority) |
| Q4 | ReadyAPI: ČKP IT bude doplňovat — kdy aktivovat sharing? | ČKP IT |

## §9. Status

| Item | Hodnota |
|------|---------|
| Spec | `_specs/CROSS-FRAMEWORK-DATA-SHARING-v0.1-CS.md` |
| Verze | v0.1 |
| Datum | 2026-05-07 EOD |
| Audience | Pete + governance + Sonnet branch sessions (test-author scope) |
| Implementation start | v0.5.1 (po review tohoto docu) |
| Status | scaffold; čeká na review + first refactoring v v0.5.1 |
