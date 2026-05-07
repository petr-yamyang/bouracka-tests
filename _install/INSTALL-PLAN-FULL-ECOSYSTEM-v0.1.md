# Install Plan — Full Robust Test Ecosystem — v0.1

> **Companion to** `INSTALL-PLAN-SUPNB-v0.1.md` (the lean R1 baseline).
> This doc upgrades the lab into a multi-layered test ecosystem covering
> functional E2E (Playwright + Cypress + TestCafe), **independent
> REST/SOAP service-contract tests**, **performance / load / latency**
> tests, and a **data-validation pipeline** that gates which fixtures
> are allowed into longer-running E2E scenarios.
>
> **Audience.** ČKP/SUPIN SecOps + the operator + the two QA-engineer
> colleagues. SecOps should be able to read this doc once and approve
> a single deployment ticket per profile (A / B / C) — no per-laptop
> review.
>
> **The user's binding question.** *"How to tackle independent tests
> of REST/SOAP interfaces for each service before E2E suite runs on
> the same, validated data in longer scenarios?"* — answered in §3.

---

## §1. The three install profiles

Profiles are stacked: B = A + extras; C = B + extras. Pick per role.

| Profile | Footprint | Audience | What it adds |
|---------|----------:|----------|--------------|
| **A — Lean E2E** | ~880 MB | Colleagues who run R1 functional tests only | Per `INSTALL-PLAN-SUPNB-v0.1.md` — Node + Playwright (Chromium) |
| **B — Standard QA** | ~1.7 GB | QA engineers running functional + light contract + perf | A + Cypress + TestCafe + Newman + k6 + Mockoon + Mailpit |
| **C — Full Lab** | ~2.6 GB | Operator's notebook; full toolkit + GUI options | B + SoapUI Open Source + MockServer + Eclipse Temurin JRE 21 + Postman desktop |

Default for `<test-runner-host>` (operator) = **C**. Default for `SUPNB002` +
`SUPNB003` (colleagues) = **B** (covers everything except SOAP-GUI
and standalone MockServer; both are useful but not daily-driver tools).

Anyone can downgrade to **A** for a single-purpose run; the suite
detects what's installed and skips layers it can't run.

## §2. The test pyramid (binding architecture)

Five layers, executed in this order on a clean run, each layer gating
the next:

```
    ┌──────────────────────────────────────────────┐
  5 │ PERFORMANCE / LOAD / LATENCY                 │  k6
    │ – per-scenario p95/p99 latency trend         │
    │ – ramped load (smoke / load / stress / soak) │
    └──────────────────────────────────────────────┘
                    ▲   uses validated fixtures
    ┌──────────────────────────────────────────────┐
  4 │ E2E FUNCTIONAL                               │  Playwright (primary)
    │ – TC-CP-001..020 driving the full SUT        │  Cypress (peer)
    │ – mobile-only viewports 320/375/414          │  TestCafe (fallback)
    └──────────────────────────────────────────────┘
                    ▲   uses validated fixtures
    ┌──────────────────────────────────────────────┐
  3 │ INTEGRATION (per integration, SUT-side mocks)│  Mockoon, MockServer
    │ – tests SUT pages with INT-NNN mocked        │
    │ – isolates UI from real-service flakiness    │
    └──────────────────────────────────────────────┘
                    ▲   gates fixtures into E2E
    ┌──────────────────────────────────────────────┐
  2 │ DATA-VALIDATION                              │  seed-validate.ps1
    │ – each fixture is run against the contract   │
    │ – passing fixtures tagged validated_for_env  │
    │ – failing fixtures blocked from E2E          │
    └──────────────────────────────────────────────┘
                    ▲   feeds validated fixtures
    ┌──────────────────────────────────────────────┐
  1 │ SERVICE CONTRACT (REST / SOAP per integration│  Newman (REST)
    │ – AISPOV ROB / CRR / vehicle / insurance     │  node-soap + vitest
    │ – zenID API                                  │  (optionally SoapUI)
    │ – SMS Gateway                                │  k6 in script mode
    │ – RUIAN, Maps, Azure Blob, reCaptcha, SMTP   │
    │ – schema-asserted req/res shape              │
    └──────────────────────────────────────────────┘
```

### §2.1 What lives at each layer

#### Layer 1 — Service Contract tests (THE answer to the REST/SOAP question)

For every INT-NNN in `recon/integrations/`, the suite ships:

```
contracts/
├── INT-001-recaptcha/
│   ├── newman-collection.json     (Postman collection — REST verify endpoint)
│   ├── schemas/
│   │   ├── request.schema.json    (JSON Schema — what we send)
│   │   └── response.schema.json   (what we expect back)
│   ├── fixtures/
│   │   ├── happy.json
│   │   └── failure.json
│   └── README.md
├── INT-002-sms-gateway/
│   ├── newman-collection.json     (REST: PING + issue-OTP + validate-OTP)
│   ├── schemas/
│   │   ├── ping-response.schema.json
│   │   ├── issue-otp-request.schema.json
│   │   ├── validate-otp-request.schema.json
│   │   └── error-422.schema.json  (the EX_CHYBA shape)
│   ├── fixtures/
│   │   ├── valid-cz-phones.json   (regex-tested 9-digit list per analytical doc p28)
│   │   ├── valid-sk-phones.json
│   │   └── invalid-phones.json
│   └── README.md
├── INT-004-aispov/                 (SOAP)
│   ├── wsdl/
│   │   └── AISPOV.wsdl            (the official WSDL — to be supplied OOB)
│   ├── soap-tests/
│   │   ├── rob-driver-lookup.test.ts   (vitest + node-soap)
│   │   ├── crr-license-lookup.test.ts
│   │   ├── vehicle-lookup.test.ts
│   │   └── insurance-contract-lookup.test.ts
│   ├── schemas/
│   │   └── statusvysledek.xsd     (StatusVysledek / SubStatus / Komponenta)
│   ├── fixtures/
│   │   ├── tester-jeden.xml       (canonical OP for happy)
│   │   ├── unknown-driver.xml     (NENALEZENO ROB scenario)
│   │   └── timeout-driver.xml
│   └── README.md
├── INT-006-zenid-websdk/           (REST + JS callback)
├── INT-007-zenid-api/              (REST file upload)
├── INT-008-ruian/                  (REST address autocomplete)
├── INT-009-azure-blob-outage/      (HTTPS GET; static JSON)
├── INT-010-google-analytics/       (browser-side; covered indirectly)
├── INT-003-smtp/                   (no contract test; covered by Mailpit hook)
└── INT-005-maps-geocoder/          (REST geocode)
```

For each contract:
- **REST integrations** → Newman runs the Postman collection against
  `tst.*` (or against the Mockoon stub if the live service is down).
  Each request asserts `expect(response.status).oneOf([200, 4xx])` and
  `tv4.validate(response.body, schema)` (Postman's built-in JSON Schema
  validator).
- **SOAP integrations** → `node-soap` builds a typed client from the
  WSDL; `vitest` runs assertion suites against canonical SOAP envelopes.
  Falls back to **SoapUI Open Source** for visual debug (Profile C).
- **Static-JSON integrations** (Azure Blob outage) → simple `curl` +
  `jq` validate `outages[]` shape and ISO-8601 datetimes.

#### Layer 2 — Data-Validation gate

After Layer 1 passes, the seeder runs every E2E fixture **as if** it
were a real test step against the contract (e.g. for fixture
`TD-CP-002 tester_jeden`, post the OP number to AISPOV ROB lookup;
assert the expected `first_name + last_name + dob` come back). On
success, the fixture is tagged:

```yaml
# fixtures/validated/tst/tester_jeden.json
fixture_id: TD-CP-002
validated_for_env: tst
validated_at: 2026-05-08T13:42:11Z
validated_against:
  - INT-004-aispov-rob: { result: ok, statusvysledek: OK }
  - INT-004-aispov-crr: { result: ok, statusvysledek: OK }
  - INT-006-zenid-websdk: { skipped: ocr-not-applicable-for-fixture-data }
data:
  op_number: <REDACTED — present in fixtures/secrets/, not committed>
  first_name: Tester
  last_name: Jeden
  dob: 1985-04-12
  ...
```

Failed validations get tagged `validated_at: null,
validation_error: "<reason>"` and **the E2E layer refuses to load
them**. This means: when E2E TC-CP-008 fails, we know the failure is
in the SUT's UI/orchestration layer, **not** in stale fixture data
that no longer matches the registry.

#### Layer 3 — Integration tests (SUT-side mocks)

Run E2E TCs with one or more integrations **mocked** instead of live.
Catches the "the SUT works fine when the integration is happy; what
about when AISPOV returns NENALEZENO?" class of bug — without
requiring the real registry to enter that state.

Pattern: Mockoon (or MockServer in Profile C) hosts a local mock at
`http://localhost:NNNN/api/registry/...`. Test runs Playwright with
`env.aispov.url = http://localhost:NNNN`. The same TC-CP-NNN runs;
only the integration target differs.

#### Layer 4 — E2E functional

The 20 R1 TCs from `02_TestCases`. Drives the full SUT against
`tst.*` envs. Consumes only `validated_for_env: <env>` fixtures.

#### Layer 5 — Performance / load / latency

k6 scripts under `perf/`. Each scenario file mirrors an E2E TC but
uses k6's HTTP API directly (no browser overhead — measures
backend latency, not front-end render).

```
perf/
├── smoke/
│   ├── sms-gateway-ping.js          # 1 VU × 1 min — smoke
│   └── aispov-driver-lookup.js
├── load/
│   ├── full-wizard-submit.js        # 10–20 VUs × 10 min
│   └── concurrent-otp-issue.js
├── stress/
│   └── recaptcha-burst.js           # 100 VUs × 5 min
└── soak/
    └── nominal-rate-4h.js           # 5 VUs × 4 h
```

Each script outputs:
- HTML summary (k6 → `--out json` → `xk6-dashboard` or grafana-cloud).
- JSON for time-series trend (per-day p50 / p95 / p99 latency).

Bound: keep load tests at low concurrency (`max_vus ≤ 20`) so we don't
hammer `tst.*` (the real ČKP test env, not load-isolated).

## §3. Pipeline — how the layers wire together (the user's question, in code)

```
# scripts/run-pipeline.ps1
.\scripts\run-contracts.ps1  -Env tst        # Layer 1
.\scripts\seed-validate.ps1  -Env tst        # Layer 2 (gates fixtures)
.\scripts\run-mocked.ps1     -Env tst        # Layer 3 (mocked SUT)
.\scripts\run-e2e.ps1        -Env tst        # Layer 4 (real SUT)
.\scripts\run-perf-smoke.ps1 -Env tst        # Layer 5 (smoke; default)

# Each script halts the pipeline on failure unless -ContinueOnFail.
# Each script writes a JSON gate file to runs/<date>/gate-<layer>.json.
# scripts/run-e2e.ps1 reads runs/<date>/gate-2.json and refuses to start
# if any of its required fixtures are NOT in 'validated' state for env.
```

The gate-file pattern means the suite is naturally CI-able (just chain
the scripts in any CI tool — GitHub Actions, Azure DevOps, Jenkins),
but also runnable interactively on the operator's notebook.

For a long E2E scenario set (e.g. nightly soak), the pipeline runs
once at the start; the validated-fixture set is what feeds the rest of
the night's E2E runs. This is the "validated data, longer scenarios"
guarantee.

---

## §4. Bill of materials per profile

### §4.1 Profile A — Lean E2E (~880 MB)

Identical to `INSTALL-PLAN-SUPNB-v0.1.md` §2.1 — Node 20 LTS +
bouracka-tests + Playwright Chromium. **Sufficient for R1 TC runs.**

### §4.2 Profile B — Standard QA (~1.7 GB) — Profile A plus

| # | Component | Version | Purpose | Per-user? | Source |
|---|-----------|---------|---------|-----------|--------|
| 4 | **Cypress** | `cypress ^13.17.0` | Second E2E framework (peer to Playwright per Gate 1) | YES | npm |
| 5 | **TestCafe** | `testcafe ^3.7.0` | Third E2E framework (fallback per Gate 1) | YES | npm |
| 6 | **Newman** | `newman ^6.2.0` | Postman CLI — REST contract runner | YES | npm |
| 7 | **k6** (Grafana k6) | 0.55.x | Performance / load / latency runner — single Go binary, no runtime needed | YES (portable) | https://github.com/grafana/k6/releases |
| 8 | **Mockoon CLI** | 9.x | Lightweight HTTP mock server (REST integration mocks) | YES | npm `@mockoon/cli` |
| 9 | **Mailpit** | 1.x | Local SMTP capture (single Go binary) | YES (portable) | https://github.com/axllent/mailpit/releases |

Per-laptop add: ~820 MB.

### §4.3 Profile C — Full Lab (~2.6 GB) — Profile B plus

| # | Component | Version | Purpose | Per-user? | Source |
|---|-----------|---------|---------|-----------|--------|
| 10 | **Eclipse Temurin JRE** (or Microsoft Build of OpenJDK) | 21 LTS | JVM runtime — needed by SoapUI + MockServer | YES (portable ZIP recommended) | https://adoptium.net/temurin/releases/?version=21 |
| 11 | **SoapUI Open Source** | 5.7.x | SOAP testing GUI + ProjectRunner CLI for AISPOV WSDL debugging | YES (ZIP) | https://www.soapui.org/downloads/soapui/ |
| 12 | **MockServer** | 5.15.x | Heavy-weight mock for complex integration scenarios (alternative to Mockoon) | YES (jar) | Maven Central |
| 13 | **Postman desktop** *(optional)* | 11.x | Postman GUI for collection editing (operator-only) | YES (per-user MSI) | https://www.postman.com/downloads/ |

Per-laptop add: ~900 MB.

## §5. Disk footprint summary

```
Profile A — Lean E2E      ~  880 MB
Profile B — Standard QA   ~ 1.70 GB    (+ 820 MB)
Profile C — Full Lab      ~ 2.60 GB    (+ 900 MB)
```

On a 367 GB free SSD: 0.7 % footprint even at Profile C. SecOps yes
across the board.

## §6. Network egress allowlist — additions over the lean plan

For Profile B + C, add to the lean-plan §4.1 install-time set:

| Host | Profile | Purpose | Port |
|------|---------|---------|------|
| `github.com` (already permitted) | B + C | k6, Mailpit, MockServer, JRE downloads from GH releases | 443 |
| `objects.githubusercontent.com` (already permitted) | B + C | same | 443 |
| `dl.k6.io` *(only if not using GH releases)* | B | k6 download mirror | 443 |
| `adoptium.net` | C | Temurin JRE downloads | 443 |
| `repo1.maven.org` | C | MockServer jar from Maven Central | 443 |
| `dl.bintray.com` *(legacy; some old tools)* | C only if needed | older SoapUI versions | 443 |
| `download.cypress.io` | B + C | Cypress binary | 443 |
| `nodes.testcafe.io` *(if any TC binary needed)* | B + C | TestCafe assets (usually all via npm) | 443 |

For Profile B + C, add to the run-time set (§4.2 of the lean plan):

| Host | Purpose | Port |
|------|---------|------|
| `localhost` (loopback only) | Mockoon / MockServer / Mailpit listening on 127.0.0.1 | 1025–8025 |
| (no other run-time additions if perf tests target `tst.*` only) | | |

**Loopback is the key**: Mockoon and Mailpit listen on `localhost`
only. They never expose to the LAN. SecOps should NOT need to allow
inbound traffic.

## §7. Privilege footprint

Same as lean plan: **no admin rights needed for any profile**, all
installs are per-user.

The only addition for Profile C: the JRE, SoapUI, MockServer can all
run from `%USERPROFILE%\tools\...` portable folders (no installer).
The operator unzips, runs `set PATH=%USERPROFILE%\tools\jre21\bin;%PATH%`
in the bouracka-tests session, and they're in.

If GPO enforces deny-by-default AppLocker, three additional rules:
- `%USERPROFILE%\tools\jre21\bin\java.exe` — Eclipse Temurin signature.
- `%USERPROFILE%\tools\soapui\*` — SmartBear signature.
- `%USERPROFILE%\tools\k6\k6.exe` — Grafana Labs signature.

All three publishers have valid Code Signing certs.

## §8. Per-profile install workflow

### §8.1 Profile A (already documented in lean plan)

`INSTALL-PLAN-SUPNB-v0.1.md` §8 — verbatim.

### §8.2 Profile B — operator runs after Profile A install

```powershell
cd "%USERPROFILE%\bouracka-tests"

# 1. Add Cypress + TestCafe (as optional dev-deps)
npm run install:cypress
npm install --no-save testcafe@^3.7.0

# 2. Add Newman (REST contract runner)
npm install --no-save newman@^6.2.0

# 3. Add Mockoon CLI (REST mock)
npm install --no-save @mockoon/cli@^9

# 4. Download single-binary tools (k6 + Mailpit) — portable, no install
mkdir "%USERPROFILE%\tools" 2>$null
# k6
Invoke-WebRequest 'https://github.com/grafana/k6/releases/download/v0.55.0/k6-v0.55.0-windows-amd64.zip' -OutFile "$env:USERPROFILE\tools\k6.zip"
Expand-Archive "$env:USERPROFILE\tools\k6.zip" -DestinationPath "$env:USERPROFILE\tools\"
# Mailpit
Invoke-WebRequest 'https://github.com/axllent/mailpit/releases/download/v1.21.0/mailpit-windows-amd64.zip' -OutFile "$env:USERPROFILE\tools\mailpit.zip"
Expand-Archive "$env:USERPROFILE\tools\mailpit.zip" -DestinationPath "$env:USERPROFILE\tools\mailpit\"

# 5. Verify
.\scripts\validate-install.ps1 -Profile B
```

### §8.3 Profile C — operator runs after Profile B install

```powershell
# 6. Eclipse Temurin JRE 21 (portable)
Invoke-WebRequest 'https://api.adoptium.net/v3/binary/latest/21/ga/windows/x64/jre/hotspot/normal/eclipse?project=jdk' -OutFile "$env:USERPROFILE\tools\jre21.zip"
Expand-Archive "$env:USERPROFILE\tools\jre21.zip" -DestinationPath "$env:USERPROFILE\tools\jre21-staging\"
# (Move single contained folder up to %USERPROFILE%\tools\jre21\)

# 7. SoapUI Open Source (ZIP, no installer)
Invoke-WebRequest 'https://dl.eviware.com/soapuios/5.7.2/SoapUI-5.7.2-windows-bin.zip' -OutFile "$env:USERPROFILE\tools\soapui.zip"
Expand-Archive "$env:USERPROFILE\tools\soapui.zip" -DestinationPath "$env:USERPROFILE\tools\"

# 8. MockServer (jar)
mkdir "$env:USERPROFILE\tools\mockserver" 2>$null
Invoke-WebRequest 'https://repo1.maven.org/maven2/org/mock-server/mockserver-netty/5.15.0/mockserver-netty-5.15.0-shaded.jar' -OutFile "$env:USERPROFILE\tools\mockserver\mockserver.jar"

# 9. (optional) Postman desktop — operator only
# Manual download from postman.com; install per-user MSI

# 10. Verify
.\scripts\validate-install.ps1 -Profile C
```

After Profile C install, both colleague notebooks (B) + operator (C)
share the same scripts and folder layout — the suite auto-detects
which tools are present and skips layers it can't run.

## §9. Performance test specifics — k6 scenarios per integration

Each integration gets a smoke + load script. Examples:

**`perf/smoke/aispov-driver-lookup.js`:**
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 1,
  duration: '1m',
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

const FIXTURES = JSON.parse(open('../../fixtures/validated/tst/drivers.json'));

export default function () {
  const driver = FIXTURES[Math.floor(Math.random() * FIXTURES.length)];
  const res = http.post(
    `${__ENV.AISPOV_URL}/driver-lookup`,
    JSON.stringify({ id_number: driver.op_number, document_type: 'OP' }),
    { headers: { 'Content-Type': 'application/json' } },
  );
  check(res, {
    'status is 200': (r) => r.status === 200,
    'returns expected first_name': (r) =>
      r.json('first_name') === driver.first_name,
  });
  sleep(0.5);
}
```

Notice: the script consumes the **same validated fixtures** that E2E
uses — so a perf-test failure of "first_name mismatch" is a real
service regression, not fixture drift.

**`perf/load/full-wizard-submit.js`:**
- Models the 12-step process diagram as a single VU iteration.
- Ramped concurrency: 0 → 10 VUs over 2 min, hold 10 VUs for 6 min,
  ramp down over 2 min.
- Asserts overall transaction time per VU < 60 s p95
  (analytical doc says 10–20 min per real user; for synthetic test
  with seeded fixtures we expect dramatically faster).
- Reports per-step latency breakdown so we can see which integration
  dominates response time.

**Latency-only smoke (CI-friendly):**
```powershell
.\scripts\run-perf-smoke.ps1 -Env tst   # ~3 min total
```

## §10. Validation script — Profile-aware

Updated `scripts/validate-install.ps1` accepts a `-Profile` parameter
and validates accordingly:

```powershell
# Examples
.\scripts\validate-install.ps1                # Profile A (default)
.\scripts\validate-install.ps1 -Profile B
.\scripts\validate-install.ps1 -Profile C
```

Per-profile checks (in addition to the lean baseline):

| Profile | Additional checks |
|---------|-------------------|
| B | `cypress --version` returns; `testcafe --version`; `newman --version`; `mockoon-cli --version`; `k6 version`; `mailpit version`; loopback ports 1025/1080/8025 free |
| C | All of B; plus `java -version` returns (JRE 21); `soapui --version` (or `soapui.bat` exists); `mockserver.jar` SHA256 matches expected; Postman desktop optional check |

Output: same JSON-then-coloured-line pattern. SecOps collects a JSON
per laptop and diffs them — should match the chosen profile exactly.

## §11. Checklist — for SecOps approval (single-pass per profile)

### Profile A — covered by `INSTALL-PLAN-SUPNB-v0.1.md` §11.

### Profile B — additional ticks:

- [ ] BoM reviewed: A + Cypress + TestCafe + Newman + k6 + Mockoon + Mailpit.
- [ ] Network allowlist updated for §6 install-time additions.
- [ ] AppLocker rules for `%USERPROFILE%\tools\k6\*` and
      `%USERPROFILE%\tools\mailpit\*` (if deny-by-default).
- [ ] Defender exclusion: `%USERPROFILE%\bouracka-tests\node_modules`
      AND `%USERPROFILE%\bouracka-tests\runs\*` (perf runs generate
      large JSON files).
- [ ] Loopback ports 1025 (Mailpit SMTP), 1080 (Mailpit web UI),
      8025 (Mockoon default), 8080 (MockServer default) confirmed
      reachable on `127.0.0.1` only.
- [ ] Validation script returns `[OK] Profile B` on all target laptops.

### Profile C — additional ticks:

- [ ] BoM reviewed: B + Temurin JRE 21 + SoapUI OS + MockServer.
- [ ] Network allowlist additions for §6 (Profile C row).
- [ ] AppLocker rules for `%USERPROFILE%\tools\jre21\bin\*`,
      `%USERPROFILE%\tools\soapui\*`,
      `%USERPROFILE%\tools\mockserver\*`.
- [ ] JRE 21 signature verified (Eclipse Foundation).
- [ ] If Postman desktop included: per-user MSI install; reviewed
      separately if SecOps requires.
- [ ] Validation script returns `[OK] Profile C` on the operator laptop.

## §12. How-to runbook — first end-to-end pipeline run

Once <test-runner-host> is at Profile C and SUPNB002/003 at Profile B:

```powershell
cd "%USERPROFILE%\bouracka-tests"

# 1. Pull latest fixtures + wsdl + schemas from the secret bundle
#    (delivered OOB by user; lives in fixtures/secrets/, gitignored)
Expand-Archive -Force "$env:USERPROFILE\Downloads\bouracka-fixtures-v0.1.zip" `
                 -DestinationPath fixtures\secrets\

# 2. Run the pipeline against tst (full)
.\scripts\run-pipeline.ps1 -Env tst -Profile C

# 3. After pass, run the same pipeline against tst-demo
.\scripts\run-pipeline.ps1 -Env tst-demo -Profile C

# 4. Bundle results for return e-mail
.\scripts\package-results.ps1 -Tester "petr"
```

Expected duration end-to-end on a healthy network:
- Layer 1 (contracts): 1–2 min
- Layer 2 (data-validate): 30–60 s
- Layer 3 (mocked E2E subset): 3–5 min
- Layer 4 (real E2E full R1): 10–15 min
- Layer 5 (perf smoke): 3 min
- **Total: ~18–25 min for a complete pipeline run** on the operator's
  laptop.

## §13. What this enables (vs the lean plan alone)

| Capability | Lean (A) | Standard (B) | Full Lab (C) |
|------------|:--------:|:------------:|:------------:|
| Run R1 E2E TCs against tst.* | ✓ | ✓ | ✓ |
| Run all 3 E2E frameworks (Gate 1 comparison) | ✗ | ✓ | ✓ |
| REST contract validation per integration | ✗ | ✓ | ✓ |
| SOAP contract validation (AISPOV WSDL) | ✗ | ✓ (CLI) | ✓ (CLI + GUI) |
| Pre-E2E fixture validation gate | ✗ | ✓ | ✓ |
| Mock SUT integrations for isolation | ✗ | ✓ (Mockoon) | ✓ (Mockoon + MockServer) |
| Capture outbound SMTP for assertion | ✗ | ✓ (Mailpit) | ✓ |
| Performance smoke / load / latency | ✗ | ✓ (k6) | ✓ |
| GUI debugging of SOAP envelopes | ✗ | ✗ | ✓ (SoapUI) |
| Postman collection editing GUI | ✗ | ✗ | ✓ (operator only) |

## §14. Decision points still open

| Open question | Resolved how |
|---------------|--------------|
| Do colleagues need Profile C, or B suffices? | Default = B; operator can elevate one colleague to C if they regularly debug SOAP envelopes |
| Is JRE 21 acceptable to ČKP SecOps? | Yes for Eclipse Temurin — signed by Eclipse Foundation; no telemetry; LTS |
| Postman desktop yes/no? | Defer; use Postman web app (no install) when collection editing is needed |
| Does the perf test layer hammer tst.*? | No — bound at `max_vus = 20` for load; smoke at 1 VU; soak at 5 VUs |
| Where do the WSDL + schemas come from? | OOB delivery from user (lives in `fixtures/secrets/`, gitignored). Filed as **OQ-CP-22 / OQ-CP-23** — pending. |

## §15. Status

| Item | Value |
|------|-------|
| Document | `_install/INSTALL-PLAN-FULL-ECOSYSTEM-v0.1.md` |
| Companion | `_install/INSTALL-PLAN-SUPNB-v0.1.md` (lean baseline) |
| Profiles | 3 (A lean ~880 MB / B standard ~1.7 GB / C full ~2.6 GB) |
| Layers in pyramid | 5 (contract → data-validate → mocked-int → E2E → perf) |
| Default per laptop | <test-runner-host> = C; SUPNB002 + SUPNB003 = B |
| Admin rights required | NO (all per-user) |
| Network allowlist additions | 5 install-time hosts; 0 run-time hosts (loopback only) |
| Validation | `scripts/validate-install.ps1 -Profile {A|B|C}` |
| Status | v0.1 — ready to hand to SecOps |
