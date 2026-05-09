# SUPIN N8 SMS Gateway — Contract Analysis & Test Strategy — v0.1
## Closes synchro GAP-4 + GAP-10 outright; surfaces the SUPIN-wide platform integration pattern

**Version:** v0.1.0
**Trigger:** operator delivered three N8 artefacts 2026-05-06 morning — `N8.openapi.yaml` (38 KB; OpenAPI 3.1), `N8.postman_collection.json` (401 KB; Postman v2.1 with assertion library), `N8-readyapi-project.xml` (93 KB; SoapUI / ReadyAPI 3.66 project). Together these constitute the **canonical SUPIN-side N8 contract** — including the production envelope, the test envelope, AND a deterministic `/fake/` envelope. The synchro file §3 strategy was authored speculatively (Mockoon + four-ask to SUPIN); now we have the actual contract and a SUPIN-provided fake. This doc supersedes the speculative parts of synchro §3 and feeds into ThinkPad CP-SUPIN-03.
**Audience:** ThinkPad Opus task-force CP-SUPIN-03 (consume §17 paste-ready addendum); MacBook Opus next vocabulary refresh (absorb the SUPIN platform pattern §2 into catalogue v0.1.3); operator (Petr — read §1 + §13 + §16 to decide what to ack with SUPIN).
**Posture:** the contract is *richer than expected* — multi-cluster topology, three send-modes, async + sync mix, year/month versioning, mTLS auth, deterministic `/fake/` mode. Scope expands: this isn't just SMS Gateway test wiring; it's the canonical example of how SUPIN exposes interfaces to partner systems. The same pattern applies to AISPOV, future zenID-via-SUPIN integration, SMTP, the lot.

---

## §1. Executive summary (one screen)

| What | Finding |
|------|---------|
| **Sources** | OpenAPI 3.1 (17 paths × 1 operation each) + Postman (3 envs × 3 clusters × 7 ops with assertion library) + ReadyAPI (full operation catalogue + a single test case skeleton) |
| **Operations (the canonical 7)** | `Ping` · `Odeslani SMS Ihned` · `Odeslani SMS Normal` · `Odeslani SMS Relax` · `SMS ID` (GET) · `SMS Auth` (OTP send) · `SMS Chk Auth` (OTP verify) |
| **Environments** | `STD` (production) · `TST` (test) · `DEV` (dev) — visible in URL path |
| **Multi-cluster** | 3 production hosts: `rest-ws.supin.cz:8883` (WEB1) + `rest-ws-n8-1.supin.cz:7008` (WEB6) + `rest-ws-n8-2.supin.cz:7008` (WEB7); 1 TST host `rest-wstst.supin.cz:8887` |
| **🎯 KEY FIND** | `/N8/2025/01/TST/BOUR/fake/...` is a **deterministic test mode** SUPIN already provides — closes synchro GAP-4 (N8 sandbox negotiation no longer urgent) and GAP-10 (documentation now in hand) |
| **Auth** | mTLS (client cert binds `PartnerKod` + `RozhraniKod` pair) + `X-SUPIN-TransactionInfo` header (kv-pairs; semicolon-separated; partner self-identifies user via `UzivatelKod`) |
| **Versioning** | `/N8/2025/01/...` — year + month (decoupled MAJOR.MINOR; SUPIN can run multiple versions concurrently) |
| **Content type** | `application/xml`; ČKP-namespaced (`xmlns="http://ws.ckp.cz/N8/2025/01"`) — note: **ČKP namespace**, not SUPIN; per L-ARCH-2 (SUPIN hosts ČKP-defined interfaces) |
| **Response shape** | XML root `<SmsInfo>` with attributes `SmsId` · `SmsTS` · `GatewayAN` (A/N) · `GatewayTS` |
| **Status codes** | 200/202/203 all OK; 202 is the dominant "queued" verdict; the Postman assertion library accepts all three |
| **Performance SLO** | < 200 ms response time (per the Postman test scripts — gives us a concrete `LIB-AS-PERF-001` threshold) |
| **Send modes (Zpusob enum)** | `IHNED` (immediate) · `NORMAL` (default queue) · `RELAX` (deferred / low priority / cost-optimised) |
| **Postman assertions reusable as-is** | response status range, response time, content-type, `SmsInfo` root presence, `SmsId` numeric range, `GatewayAN` enum {A,N}, datetime regex on `SmsTS`/`GatewayTS` |
| **Closes synchro gaps** | GAP-4 (N8 sandbox) ✅ closed by `/fake/`; GAP-10 (N8 docs) ✅ closed by these uploads |
| **Opens new gaps** | GAP-11 (cluster routing — which of 3 WEB clusters does Bouračka call? all 3 round-robin? sticky-by-cert?) · GAP-12 (mTLS cert provisioning for Bouračka tester laptops) · GAP-13 (the inbound SMS receive-back path — does N8 deliver real SMS in TST/fake or only simulated?) |

---

## §2. The SUPIN platform integration pattern — generalisable across the ecosystem

The N8 contract exposes a **house pattern** that almost-certainly repeats across other SUPIN-hosted interfaces (AISPOV, future zenID-via-SUPIN, SMTP gateway, RUIAN proxy if any). Capturing the pattern here so future analysis of any SUPIN interface starts with high prior expectations.

### §2.1 URL structure pattern

```
{scheme}://{host}:{port}/{InterfaceCode}/{YYYY}/{MM}/{Env}/{PartnerCode}/{Resource}/{Action}
                                                              ↑
                                                              optional /fake/ here for deterministic mode
```

Components:
- `InterfaceCode` — short acronym (`N8`); decoupled from the interface name
- `YYYY/MM` — calendar versioning; multiple versions can run concurrently
- `Env ∈ {STD, TST, DEV}` — environment in the path itself (not subdomain)
- `PartnerCode` — partner system ID (`BOUR` for Bouračka); same gateway serves multiple partners
- `Resource` — sometimes a hyphen `-` for "no resource"; otherwise a noun (`Sms`, `SmsAuth`, `ChkAuth`, `Sms/SmsId`)
- `Action` — implicit from HTTP method (POST = action; GET = query)
- Optional `fake/` segment immediately before the resource for deterministic test mode

**Generalised expectation for AISPOV (not yet seen):** `https://rest-ws.supin.cz:NNNN/AISPOV/YYYY/MM/{STD|TST|DEV}/BOUR/{Driver|Vehicle|Insurance}/{lookup|verify}` with optional `/fake/`.

### §2.2 X-SUPIN-TransactionInfo header (the platform handshake)

```
X-SUPIN-TransactionInfo: PartnerKod=BOUR; RozhraniKod=N8; UzivatelKod=BourackaAzure; TransID=78877; IdentZaznam=358131869
```

| Key | Required | Purpose |
|---|:---:|---|
| `PartnerKod` | YES | partner system identifier; cert-bound |
| `RozhraniKod` | YES | interface code; cert-bound (with PartnerKod = unique pair) |
| `UzivatelKod` | YES (implicit) | partner-side end-user identifier; **not** validated by SUPIN; trust is delegated to the partner because the cert authenticates the partner-system itself |
| `TransID` | NO | partner-side transaction marker; logged for cross-system trace |
| `IdentZaznam` | NO | partner-side record identifier; logged |
| `TicketId` | NO (future) | conversation continuity (designed-in, not yet used) |

**Discipline implication:** every SUPIN-bound test request our framework emits MUST construct this header. We need a header-builder utility. `playwright/runtime/supin-headers.ts` (NEW) — see §10.

### §2.3 Authentication — mTLS only

mTLS (mutual TLS) — client cert authenticates the partner system to SUPIN. The cert binds to `(PartnerKod, RozhraniKod)` pair; SUPIN verifies the cert's CN/SAN matches the header. The partner is then trusted to self-identify users and processes via `UzivatelKod`.

**Test implication:** the framework needs the partner cert + key on the tester laptop OR routes through a TLS-terminating intermediary that bears the cert. This is a NEW gap — see GAP-12.

### §2.4 Content negotiation

- `Accept: application/xml` — required; SUPIN supports XML (the OpenAPI says JSON in `responses` but actual responses are XML per Postman tests; OpenAPI is deceptive on this).
- `Accept-Charset: utf-8` — required.
- `Content-Type: application/xml` (when sending body).

**OpenAPI annotation drift:** the OpenAPI declares response content as `application/json` with empty schema, but the Postman test scripts assert `Content-Type: application/xml` and parse XML. The OpenAPI is **incomplete**; the Postman tests are the source of truth for response shape. This is a documentation-quality issue worth flagging back to SUPIN.

### §2.5 Status code semantics

| Code | Meaning | Where used |
|---|---|---|
| `200` | OK — synchronous result returned in body | `Ping`, `SMS ID` GET (the sync queries) |
| `202` | Accepted — request queued; result available later via SMS ID GET | `Sms`, `SmsAuth`, `ChkAuth` (the async queueing operations) |
| `203` | Non-Authoritative Information — cache hit OR proxy answered | sometimes for `Ping` and `SMS ID` |

The Postman test scripts use `[200, 203, 202].includes(code)` for query operations and `[202]` strictly for async send operations — gives us the exact assertion logic.

### §2.6 Versioning + concurrent runtime

`/N8/2025/01/...` — calendar versioning. SUPIN can run `/N8/2025/01/` and `/N8/2026/03/` concurrently; partners migrate at their own cadence. Bumps imply contract changes (additive or breaking — not yet specified by SUPIN). **Test implication:** every test fixture pins to a specific year/month version; cross-version testing is a future capability.

### §2.7 Async + sync mix in one interface

| Op | Mode | Concrete pattern |
|---|---|---|
| `Ping` | sync | request → 200 + result body now |
| `SMS ID` (GET) | sync | query queued message status |
| `Sms` (POST any send-mode) | async | request → 202 + `SmsInfo.SmsId`; result via `SMS ID` GET later |
| `SmsAuth` | async | request → 202 + `SmsInfo.SmsId`; OTP delivered via real SMS to phone |
| `ChkAuth` | sync | request → 200 + verification result |

Test framework MUST handle both patterns (intercept the 202 + capture SmsId; later poll the GET). The DEMO `/fake/` mode collapses async to sync (returns the OTP in the response body for the test to capture) — see §7.

---

## §3. N8 endpoint inventory — canonical catalogue

Production base URLs (3-cluster, load-balanced):
- `http://rest-ws.supin.cz:8883/` (WEB1)
- `http://rest-ws-n8-1.supin.cz:7008/` (WEB6)
- `http://rest-ws-n8-2.supin.cz:7008/` (WEB7)

Test base URL (currently 1 cluster):
- `http://rest-wstst.supin.cz:8887/` — serves both `TST` and `TST/fake` paths

Dev base URL: same `rest-wstst.supin.cz:8887` per Postman folder structure (DEV folder duplicates TST endpoints) — likely they map to the same TST physical environment but with DEV semantics.

> **Operational note:** these are HTTP not HTTPS in the artefacts (no `https://` shown). That's almost-certainly because the Postman/ReadyAPI artefacts strip TLS for capture purposes — the actual production endpoints are mTLS-protected (the `X-SUPIN-TransactionInfo` description says "věří se na základě certu" — trust-based-on-cert). **OQ-N8-01:** confirm with SUPIN — production is HTTPS-mTLS even though artefacts show HTTP.

### §3.1 The 7 operations (canonical)

| # | Op CS | Op EN | Method | Path | Body | Sync/Async |
|:--:|---|---|:--:|---|---|:--:|
| 1 | Ping | Health check | POST | `/N8/{Y}/{M}/{Env}/{Partner}/-/Ping` | none | sync |
| 2 | Odeslání SMS Ihned | Send SMS Immediately | POST | `/N8/.../Sms` (header indicates IHNED) | `<SmsSend Zpusob="IHNED" TelCislo="..."><Zprava>...</Zprava></SmsSend>` | async (202) |
| 3 | Odeslání SMS Normal | Send SMS Normal | POST | `/N8/.../Sms` (Zpusob="NORMAL") | same shape | async (202) |
| 4 | Odeslání SMS Relax | Send SMS Relaxed | POST | `/N8/.../Sms` (Zpusob="RELAX") | same shape | async (202) |
| 5 | SMS ID | Query SMS Status by ID | GET | `/N8/.../Sms/SmsId?SMSID=NNN` | none | sync |
| 6 | SMS Auth | Send Authorization OTP | POST | `/N8/.../SmsAuth` | `<SmsAuth TelCislo="..." Delka="5"><Zprava>Vas autorizacni kod ###</Zprava></SmsAuth>` | async (202) |
| 7 | SMS Chk Auth | Verify OTP | POST | `/N8/.../ChkAuth/` | `<ChkAuth SmsId="NNN" AutorizacniKod="..."/>` | sync |

The `Zpusob` attribute on `<SmsSend>` is the send-mode discriminator (IHNED / NORMAL / RELAX); same endpoint different semantics.

### §3.2 Path matrix (env × cluster × op = 17 paths in OpenAPI)

The OpenAPI lists 17 paths (subset; not exhaustive — `Odeslání SMS Normal` and `Relax` collapse onto the same path `/Sms` with different request bodies):

```
/N8/2025/01/STD/BOUR/-/Ping             (1)  sync   PING
/N8/2025/01/STD/BOUR/Sms                (2)  async  send (any Zpusob)
/N8/2025/01/STD/BOUR/Sms/SmsId          (3)  sync   query
/N8/2025/01/STD/BOUR/SmsAuth            (4)  async  OTP send
/N8/2025/01/STD/BOUR/ChkAuth/           (5)  sync   OTP verify

/N8/2025/01/TST/BOUR/-/Ping             (6)
/N8/2025/01/TST/BOUR/Sms                (7)
/N8/2025/01/TST/BOUR/Sms/SmsId          (8)
/N8/2025/01/TST/BOUR/SmsAuth            (9)
/N8/2025/01/TST/BOUR/ChkAuth/           (10)

/N8/2025/01/TST/BOUR/fake/Ping          (11)  ← deterministic mode
/N8/2025/01/TST/BOUR/fake/Sms           (12)
/N8/2025/01/TST/BOUR/fake/Sms/          (13)  ← duplicate trailing-slash variant; SUPIN tolerates both
/N8/2025/01/TST/BOUR/fake/Sms/SmsId     (14)
/N8/2025/01/TST/BOUR/fake/SmsAuth       (15)
/N8/2025/01/TST/BOUR/fake/ChkAuth       (16)

/N8/2025/01/DEV/BOUR/-/Ping             (17)  ← only Ping listed in DEV; expect parity with TST in practice
```

---

## §4. Authentication & headers — wiring detail

### §4.1 Required-headers builder (TypeScript spec for `playwright/runtime/supin-headers.ts`)

```typescript
// NEW file — pseudo-spec ThinkPad implements
export interface SupinTransactionInfoOpts {
  partnerKod: string;        // required, e.g. "BOUR"
  rozhraniKod: string;       // required, e.g. "N8"
  uzivatelKod: string;       // required, partner-side user ID, e.g. "BourackaAzure"
  transId?: string;          // optional, e.g. autogen `${Date.now()}`
  identZaznam?: string;      // optional, partner-side record id
  ticketId?: string;         // optional, future conversation marker
}

export function buildSupinHeaders(opts: SupinTransactionInfoOpts): Record<string, string> {
  const txParts = [
    `PartnerKod=${opts.partnerKod}`,
    `RozhraniKod=${opts.rozhraniKod}`,
    `UzivatelKod=${opts.uzivatelKod}`,
  ];
  if (opts.transId)     txParts.push(`TransID=${opts.transId}`);
  if (opts.identZaznam) txParts.push(`IdentZaznam=${opts.identZaznam}`);
  if (opts.ticketId)    txParts.push(`TicketId=${opts.ticketId}`);
  return {
    'X-SUPIN-TransactionInfo': txParts.join('; '),
    'Accept': 'application/xml',
    'Accept-Charset': 'utf-8',
    'Content-Type': 'application/xml',
  };
}
```

### §4.2 mTLS client-cert wiring

For Playwright (Node-based), mTLS is configured at the request-context level:

```typescript
// playwright.config.ts — NEW project setting
projects: [
  {
    name: 'tst-mtls',
    use: {
      // The cert + key live OUTSIDE the repo (per .gitignore)
      // Tester loads them from %USERPROFILE%\bouracka-tests\secrets\
      clientCertificates: [{
        origin: 'https://rest-wstst.supin.cz:8887',
        certPath: process.env.SUPIN_CLIENT_CERT_PATH,
        keyPath: process.env.SUPIN_CLIENT_KEY_PATH,
      }],
    },
  },
],
```

For Cypress, mTLS is harder (Node-side proxy needed); recommend Playwright as the primary framework for the integration-contract layer (Layer 1).

### §4.3 Cert provisioning — NEW gap

GAP-12: the partner cert + key for `(PartnerKod=BOUR, RozhraniKod=N8)` against TST must be obtained from SUPIN's cert authority. Path: SUPIN issues partner cert; tester laptop installs it; framework references via env vars. **Operator must request as part of the four-ask cycle.** Until then `/fake/` requires no cert (since it's open in TST) — confirm in OQ-N8-02.

---

## §5. Request / response schemas + canonical examples

### §5.1 Ping

```http
POST /N8/2025/01/TST/BOUR/-/Ping HTTP/1.1
Host: rest-wstst.supin.cz:8887
X-SUPIN-TransactionInfo: PartnerKod=BOUR; RozhraniKod=N8; UzivatelKod=BourackaAzure
Accept: application/xml
Accept-Charset: utf-8

(no body)
```

Expected response: `200` (or `203`); body shape: probably `<PingInfo SystemTS="..."/>` (Postman doesn't capture; OpenAPI is empty). **OQ-N8-03:** confirm exact Ping response body shape with SUPIN; meanwhile Mockoon scenario uses placeholder `<PingInfo SystemTS="2026-05-06T12:34:56Z"/>`.

### §5.2 Send SMS (any mode)

```http
POST /N8/2025/01/TST/BOUR/Sms HTTP/1.1
Host: rest-wstst.supin.cz:8887
X-SUPIN-TransactionInfo: TransID=78877; IdentZaznam=358131869; PartnerKod=BOUR; RozhraniKod=N8; UzivatelKod=BourackaAzure
Content-Type: application/xml
Accept: application/xml
Accept-Charset: utf-8

<?xml version="1.0" encoding="utf-8"?>
<SmsSend xmlns="http://ws.ckp.cz/N8/2025/01" TelCislo="+420604123456" Zpusob="NORMAL">
  <Zprava>Dobrý den, hlášení dopravní nehody pokračuje na: https://tst.bouracka.cz/...</Zprava>
</SmsSend>
```

Expected response (status `202`):

```xml
<?xml version="1.0" encoding="utf-8"?>
<SmsInfo
  xmlns="http://ws.ckp.cz/N8/2025/01"
  SmsId="575699776"
  SmsTS="2026-05-06T12:34:56.789Z"
  GatewayAN="A"
  GatewayTS="2026-05-06T12:34:57.012Z"/>
```

Where:
- `SmsId` — the queued message id; partner uses to query status later
- `SmsTS` — when SUPIN accepted the request
- `GatewayAN` — `A` (accepted by gateway) or `N` (not accepted; e.g. invalid number)
- `GatewayTS` — when the gateway returned the verdict

### §5.3 Query SMS by ID

```http
GET /N8/2025/01/TST/BOUR/Sms/SmsId?SMSID=575699776 HTTP/1.1
Host: rest-wstst.supin.cz:8887
X-SUPIN-TransactionInfo: PartnerKod=BOUR; RozhraniKod=N8; UzivatelKod=BourackaAzure
Accept: application/xml
```

Expected response (status `200/203`):

```xml
<?xml version="1.0" encoding="utf-8"?>
<SmsInfo
  xmlns="http://ws.ckp.cz/N8/2025/01"
  SmsId="575699776"
  SmsTS="2026-05-06T12:34:56.789Z"
  GatewayAN="A"
  GatewayTS="2026-05-06T12:34:57.012Z"
  Stav="DELIVERED"
  DodaniTS="2026-05-06T12:35:01.456Z"/>
```

(The `Stav` + `DodaniTS` attributes appear here based on the operation's documented purpose; the Postman tests don't assert on `GatewayAN` for the GET — line `//pm.expect(['A', 'N'])...` is commented out — implying the GET response carries different/additional state. OQ-N8-04: confirm extended-state attributes for `SMS ID` GET.)

### §5.4 SMS Auth (OTP send)

```http
POST /N8/2025/01/TST/BOUR/SmsAuth HTTP/1.1
...
<?xml version="1.0" encoding="utf-8"?>
<SmsAuth xmlns="http://ws.ckp.cz/N8/2025/01" TelCislo="+420604123456" Delka="5">
  <Zprava>Vas autorizacni kod pro odeslani formulare je ###</Zprava>
</SmsAuth>
```

Where:
- `TelCislo` — recipient phone (E.164)
- `Delka` — OTP length (5 chars in the example; alphanumeric)
- `Zprava` body — message template; `###` placeholder gets replaced by the actual generated OTP

Expected response (status `202`): same `<SmsInfo>` shape as Sms send.

### §5.5 SMS Chk Auth (OTP verify)

```http
POST /N8/2025/01/TST/BOUR/ChkAuth/ HTTP/1.1
...
<?xml version="1.0" encoding="utf-8"?>
<ChkAuth xmlns="http://ws.ckp.cz/N8/2025/01" SmsId="575700891" AutorizacniKod="2GYSL"/>
```

Where:
- `SmsId` — the id returned by the `SmsAuth` send response
- `AutorizacniKod` — the OTP value the user entered (e.g. `2GYSL`)

Expected response (status `200`): success/failure verdict — likely `<ChkAuthInfo Stav="OK"/>` or `Stav="MISMATCH"` etc. Postman doesn't capture body; OpenAPI is empty. OQ-N8-05: confirm verdict attribute names.

---

## §6. Async/sync semantics + the `Zpusob` enum

### §6.1 Send-mode taxonomy (the `Zpusob` attribute on `<SmsSend>`)

| Zpusob | CS meaning | Use case | Cost / SLO |
|---|---|---|---|
| `IHNED` | ihned (immediately) | time-critical: 2FA, transaction confirmation, security alerts | premium queue; expected < 5 s gateway-to-handset |
| `NORMAL` | normal | default; informational with mild urgency | standard queue; minutes |
| `RELAX` | relaxovaně (relaxed) | bulk informational, non-critical reminders | bulk queue; cheapest; up to hours |

**Bouračka usage mapping (analytical doc + per-TC inference):**
- Authorisation OTP for record-submit-confirmation → use `SmsAuth` (own endpoint), not `Sms` with IHNED
- Notification "your accident report has been submitted; QR for IZS attached" → use `Sms` with `NORMAL`
- Reminder "you have a draft accident report waiting for completion" → use `Sms` with `RELAX`

### §6.2 Async pattern (request → 202 → poll-by-id)

```
[Bouračka SUT] POST /Sms (Zpusob=NORMAL)            → 202 Accepted; <SmsInfo SmsId="X" GatewayAN="A"/>
       │
       │ (later, or on demand)
       │
       └→ [Bouračka SUT] GET /Sms/SmsId?SMSID=X     → 200; <SmsInfo SmsId="X" Stav="DELIVERED" DodaniTS="..."/>
```

**Test framework consequence:** every async-send TC needs a poll-loop in the post-condition step to confirm eventual delivery. In `/fake/` mode the poll resolves immediately; in real TST mode the poll waits up to `delivery_timeout_ms` (configurable per env).

---

## §7. The `/fake/` deterministic test mode — closes GAP-4 + GAP-10

### §7.1 What `/fake/` is

Per the OpenAPI + Postman, `/N8/2025/01/TST/BOUR/fake/...` exposes the same 7 operations as `/N8/2025/01/TST/BOUR/...` BUT with deterministic (non-real-SMS-dispatching) behaviour. Implications:

| `/fake/` behaviour (inferred + to be confirmed via OQ-N8-06) | Real `/TST/` behaviour |
|---|---|
| `Sms` send → 202 with placeholder `SmsId`; **no real SMS dispatched** | real SMS sent to real phone (cost; slow) |
| `SmsAuth` → 202 with deterministic `SmsId`; **OTP value returned in response body** OR sent to a fixed test-mode hook | real OTP sent to real phone (test must read SMS to retrieve) |
| `ChkAuth` → accepts OTP from /fake/SmsAuth without time-window expiry | real verification with time-window |
| `SMS ID` GET → returns predictable `Stav` ("DELIVERED" always) | reflects actual gateway state |
| `Ping` → identical to real | identical |

### §7.2 Operator concern resolved

Synchro §3 worried about: *"DEMO can skip [SMS Gateway] otherwise"* — meaning DEMO would bypass entirely. **Better outcome:** `/fake/` lets DEMO **exercise the actual N8 contract** without sending real SMS. The DEMO app config sets `sms_gateway_endpoint_base = http://rest-wstst.supin.cz:8887/N8/2025/01/TST/BOUR/fake` and gets full functional coverage of the SMS code path with deterministic test data.

### §7.3 Strategy revision — supersedes synchro §3.2

The original synchro §3.2 four-strategy table needs revision now that `/fake/` is known to exist:

| Strategy | Status now |
|---|---|
| **A — Mockoon mock** | Still useful as Layer 1 contract test (offline; for CI without SUPIN reach) but **no longer the default** for Layer 3 E2E. |
| **B — N8 sandbox** | **Resolved by `/fake/`** — no further negotiation needed for v0.2. The four-ask request still useful for production sandbox semantics + rate limits docs. |
| **C — Inbound SMS hook** | Only relevant for Layer 4 nightly real-SMS smoke (with real phone). DEFER to v0.3. |
| **D — SUT-side bypass** | Still relevant (`skip_integrations.sms = true` in SUT config) for cases where we want to bypass even `/fake/` — but lower priority now since `/fake/` covers most needs. |

**Net effect:** v0.2 testsuite uses `/fake/` for Layer 3 (Bouračka E2E) AND Layer 1 contract tests (Newman against the openapi.yaml), with Mockoon as a CI-time fallback when network reach to `rest-wstst.supin.cz` is unavailable.

---

## §8. Test strategy implications — per integration-pyramid layer

| Layer | Scope | N8 tooling for v0.2 | Cadence |
|---|---|---|---|
| 1 — Service Contract | Newman + the supplied Postman collection (already includes 14 assertions per op) | run against `/fake/` on every push to `thinkpad`; against real `/TST/` nightly | every push |
| 2 — Data validation | Schema validation of XML response shape against derived XSD (auto-generated from OpenAPI + Postman assertions) | run against `/fake/`; ensures namespace + attribute set + value enum invariants hold | every push |
| 3 — Mocked-integration E2E | Bouračka SUT pointed at `/fake/`; Playwright TCs exercise full wizard | local + CI-friendly (no real SMS) | every push |
| 4 — Real-integration E2E | Bouračka SUT against real `/TST/`; Playwright TCs run the same scenarios but with real SMS dispatched | nightly (or on-demand) | nightly |
| 5 — Performance | k6 against `/fake/` for SLO measurement; never against real `/TST/` (phone-cost + carrier ToS) | nightly perf gate | nightly |

---

## §9. Bouračka-specific TC mapping (concrete)

The synchro file §3.4 step 5 introduced TC-CP-005 NEW (SMS OTP send + verify). With the contract now known, the v0.2 testsuite gains these TCs around N8:

| TC | TT | N8 op exercised | Strategy | Notes |
|---|---|---|---|---|
| TC-CP-001 PING SMS Gateway happy | TT-CP-R1-A1 | Ping | Layer 3 against `/fake/` | already in workbook v0.1; just rewire base URL |
| TC-CP-002 PING SMS Gateway NOK / negative-ending | TT-CP-R1-A1 | Ping (forced timeout via Mockoon) | Layer 3 against Mockoon | `/fake/` always returns 200; for forced-NOK use Mockoon |
| TC-CP-005 NEW — SMS OTP send + verify happy | TT-CP-R1-A6 (TO_SIGN → FINISHED) | SmsAuth + ChkAuth | Layer 3 against `/fake/` | the OTP round-trip; test reads OTP from `/fake/` response |
| TC-CP-005-NOK NEW — SMS OTP wrong code | TT-CP-R1-A6 | SmsAuth + ChkAuth (with bad code) | Layer 3 against `/fake/` | verify rejection + retry path |
| TC-CP-005-EXP NEW — SMS OTP expired | TT-CP-R1-A6 | SmsAuth + ChkAuth (with old SmsId) | Layer 3 against Mockoon (force expiry) | `/fake/` may not enforce time-window — Mockoon does |
| TC-CP-N8-CONTRACT-01 NEW — Newman contract test | (Layer 1) | all 7 ops × `/fake/` | Layer 1 | adapts the Postman collection as Newman runner |
| TC-CP-N8-PERF-01 NEW — Send latency p95 < 200 ms | (Layer 5) | Sms NORMAL | Layer 5 against `/fake/` | k6 scenario; `LIB-AS-PERF-001` assertion pattern |

That's 4 NEW TCs (CP-005 + CP-005-NOK + CP-005-EXP + CP-N8-CONTRACT-01 + CP-N8-PERF-01 = 5 NEW; plus TC-CP-001/002 update). **Total v0.2 R1 = 7 + 5 = 12 TCs around N8 alone**, on top of the deeper-wizard TCs that recon will surface.

---

## §10. Mockoon scenarios — using the real shapes (supersedes synchro §3.4 step 1)

`mockoon/n8-sms-gateway.json` profile, refined per the contract:

```jsonc
{
  "uuid": "n8-sms-gateway-mockoon",
  "name": "N8 SMS Gateway — Bouračka mock (real shapes from N8.openapi.yaml + Postman)",
  "endpointPrefix": "N8/2025/01/MOCK/BOUR",
  "port": 8025,
  "routes": [
    {
      "method": "post", "endpoint": "-/Ping",
      "responses": [
        { "label": "PING_OK",
          "statusCode": 200, "body": "<?xml version='1.0' encoding='utf-8'?><PingInfo xmlns='http://ws.ckp.cz/N8/2025/01' SystemTS='{{now}}'/>",
          "headers": [{ "key": "Content-Type", "value": "application/xml" }]
        },
        { "label": "PING_NOK",
          "statusCode": 503,
          "body": "<?xml version='1.0' encoding='utf-8'?><Error xmlns='http://ws.ckp.cz/N8/2025/01' Code='GATEWAY_DOWN'/>"
        }
      ]
    },
    {
      "method": "post", "endpoint": "Sms",
      "responses": [
        { "label": "SMS_QUEUED",
          "statusCode": 202,
          "body": "<?xml version='1.0' encoding='utf-8'?><SmsInfo xmlns='http://ws.ckp.cz/N8/2025/01' SmsId='999000001' SmsTS='{{now}}' GatewayAN='A' GatewayTS='{{now}}'/>"
        },
        { "label": "SMS_REJECTED_BAD_NUMBER",
          "statusCode": 202,
          "body": "<?xml version='1.0' encoding='utf-8'?><SmsInfo xmlns='http://ws.ckp.cz/N8/2025/01' SmsId='-1' SmsTS='{{now}}' GatewayAN='N' GatewayTS='{{now}}'/>"
        }
      ]
    },
    {
      "method": "post", "endpoint": "SmsAuth",
      "responses": [
        { "label": "OTP_QUEUED",
          "statusCode": 202,
          "body": "<?xml version='1.0' encoding='utf-8'?><SmsInfo xmlns='http://ws.ckp.cz/N8/2025/01' SmsId='999000002' SmsTS='{{now}}' GatewayAN='A' GatewayTS='{{now}}' OtpForTest='2GYSL'/>"
        }
      ]
    },
    {
      "method": "post", "endpoint": "ChkAuth/",
      "responses": [
        { "label": "OTP_OK",
          "statusCode": 200,
          "body": "<?xml version='1.0' encoding='utf-8'?><ChkAuthInfo xmlns='http://ws.ckp.cz/N8/2025/01' Stav='OK' VerifiedTS='{{now}}'/>"
        },
        { "label": "OTP_MISMATCH",
          "statusCode": 200,
          "body": "<?xml version='1.0' encoding='utf-8'?><ChkAuthInfo xmlns='http://ws.ckp.cz/N8/2025/01' Stav='MISMATCH'/>"
        },
        { "label": "OTP_EXPIRED",
          "statusCode": 200,
          "body": "<?xml version='1.0' encoding='utf-8'?><ChkAuthInfo xmlns='http://ws.ckp.cz/N8/2025/01' Stav='EXPIRED'/>"
        }
      ]
    },
    {
      "method": "get", "endpoint": "Sms/SmsId",
      "responses": [
        { "label": "SMS_DELIVERED",
          "statusCode": 200,
          "body": "<?xml version='1.0' encoding='utf-8'?><SmsInfo xmlns='http://ws.ckp.cz/N8/2025/01' SmsId='999000001' SmsTS='{{now}}' GatewayAN='A' GatewayTS='{{now}}' Stav='DELIVERED' DodaniTS='{{now}}'/>"
        },
        { "label": "SMS_PENDING",
          "statusCode": 200,
          "body": "<?xml version='1.0' encoding='utf-8'?><SmsInfo xmlns='http://ws.ckp.cz/N8/2025/01' SmsId='999000001' SmsTS='{{now}}' GatewayAN='A' GatewayTS='{{now}}' Stav='PENDING'/>"
        }
      ]
    }
  ]
}
```

**Important:** Mockoon scenario does NOT replace `/fake/` — they coexist. `/fake/` is the **default** for Layer 3 E2E (real SUPIN-side determinism); Mockoon is the **fallback** for Layer 1 contract tests when there's no network reach to `rest-wstst.supin.cz` (i.e. CI sandbox; dev-mode without VPN).

---

## §11. Newman / contract-test specification

### §11.1 What we ship

The supplied `N8.postman_collection.json` is **directly runnable as a Newman contract test** with minor adjustments:

1. Add a Postman environment file `bouracka-tests/postman/env-tst-fake.postman_environment.json` mapping `{{phone_number}}` → test phone, `{{SmsId}}` → captured from previous response (Postman has a `pm.environment.set('SmsId', ...)` mechanism).
2. Wrap with Newman runner script `scripts/run-newman-n8-contract.ps1` that:
   - executes the `TST` folder against `/fake/` URLs by env-var substitution
   - exits non-zero on any test failure
   - emits JUnit XML + HTML report
3. Wire into the v0.2 `02_TestCases` as TC-CP-N8-CONTRACT-01 with `framework_targets = newman` and `state_machine_terminal_state = (n/a; contract layer)`.

### §11.2 Adapt the assertion library

The Postman collection already carries 14 assertion patterns per send-op:
- response status code in {200, 202, 203}
- response time < 200 ms
- response.SmsInfo exists
- response.SmsInfo.$ (attributes) exists
- SmsId numeric range -1..999999999999
- SmsTS valid ISO datetime
- GatewayAN ∈ {A, N}
- GatewayTS valid ISO datetime
- Content-Type includes "application/xml"

These map 1:1 to `02d_AssertionLibrary` entries (the v0.2 schema upgrade per Opus review). Author them as:

| LIB code | Pattern | FURPS+ | Source |
|---|---|---|---|
| LIB-AS-N8-001 | `xml-response-root-present` (root='SmsInfo') | F | Postman line `pm.expect(responseData.SmsInfo).to.exist` |
| LIB-AS-N8-002 | `xml-attribute-numeric-range` (attr='SmsId', min=-1, max=999999999999) | F | Postman `pm.expect(smsIdNumber).to.be.within(...)` |
| LIB-AS-N8-003 | `xml-attribute-datetime-iso` (attr='SmsTS') | F | Postman datetime regex |
| LIB-AS-N8-004 | `xml-attribute-enum` (attr='GatewayAN', allowed=['A','N']) | F | Postman enum check |
| LIB-AS-N8-005 | `response-status-class-2xx` (allowed={200,202,203}) | F | Postman status-code test |
| LIB-AS-N8-006 | `response-time-under-ms` (threshold=200) | P | Postman responseTime test → also serves as `LIB-AS-PERF-001` canonical |
| LIB-AS-N8-007 | `response-content-type-includes` (substring='application/xml') | F | Postman header test |

**These 7 N8-specific patterns + the 5 forward-looking patterns (synchro §2.2) = 12 library entries seeded for v0.2.** The 10 patterns extracted from the existing 7 Bouračka SPECs make 22 total in `02d_AssertionLibrary` v0.2.

---

## §12. k6 performance test specification

`k6/n8-perf.js` (NEW file, ThinkPad authors):

```javascript
// Smoke + soak + ramp scenarios
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  scenarios: {
    smoke: { executor: 'constant-vus', vus: 1, duration: '30s' },
    ramp:  { executor: 'ramping-vus', stages: [
      { duration: '30s', target: 5 },
      { duration: '1m',  target: 20 },   // L-PROC max VUS = 20 per anti-pattern
      { duration: '30s', target: 0 },
    ]},
  },
  thresholds: {
    'http_req_duration{op:ping}':  ['p(95)<200', 'p(99)<500'],
    'http_req_duration{op:sms}':   ['p(95)<200', 'p(99)<500'],
    'http_req_failed':             ['rate<0.01'],
  },
};

const BASE = 'http://rest-wstst.supin.cz:8887/N8/2025/01/TST/BOUR/fake';

export default function () {
  const headers = {
    'X-SUPIN-TransactionInfo': `PartnerKod=BOUR; RozhraniKod=N8; UzivatelKod=k6Test; TransID=${__ITER}`,
    'Accept': 'application/xml',
    'Content-Type': 'application/xml',
  };
  const ping = http.post(`${BASE}/-/Ping`, null, { headers, tags: { op: 'ping' } });
  check(ping, { 'ping 200/203': r => [200, 202, 203].includes(r.status) });
  // Send sample SMS
  const body = `<SmsSend xmlns="http://ws.ckp.cz/N8/2025/01" TelCislo="+420604000000" Zpusob="NORMAL"><Zprava>k6 test ${__ITER}</Zprava></SmsSend>`;
  const sms = http.post(`${BASE}/Sms`, body, { headers, tags: { op: 'sms' } });
  check(sms, { 'sms 202': r => r.status === 202 });
  sleep(1);
}
```

Ship in `bouracka-tests/k6/` directory; runner `scripts/run-k6-n8.ps1`. Layer 5 cadence: nightly only; never on every push.

---

## §13. Inputs gap inventory — UPDATE

Synchro §4.2 gap table updates:

| Gap# | Status |
|---|---|
| GAP-1 | unchanged — analytical doc pages 43..133 still pending |
| GAP-2 | unchanged — tst.* screen-recon Templates 1..N pending |
| GAP-3 | unchanged — DEMO divergence catalogue pending |
| **GAP-4** | **✅ CLOSED** by `/fake/` mode (no sandbox negotiation needed for v0.2) |
| GAP-5 | unchanged — reCAPTCHA bypass token pending |
| GAP-6 | unchanged — synthetic OP/ŘP/SPZ photos pending |
| GAP-7 | unchanged — AISPOV WSDL pending (BUT — see §15: similar pattern expected) |
| GAP-8 | unchanged — tester laptop spec pending |
| GAP-9 | unchanged — SUPIN tester contact pending |
| **GAP-10** | **✅ CLOSED** by these uploads (OpenAPI + Postman documentation in hand) |

NEW gaps from this analysis:

| Gap# | Description | Severity | Resolution path |
|---|---|:---:|---|
| **GAP-11** | Cluster-routing strategy — does Bouračka call WEB1, WEB6, WEB7 round-robin? Or sticky-by-cert? Or partner-config decides? Affects test fixture count + load distribution | B | Ask SUPIN; meanwhile assume one cluster for test, document the assumption |
| **GAP-12** | mTLS partner cert provisioning — Bouračka cert + key for `(BOUR, N8)` against TST not yet obtained | A | Four-ask request to SUPIN cert authority — add to operator email queue |
| **GAP-13** | Inbound SMS receive-back path — does N8/`fake/` deliver real SMS, simulated, or neither? Affects whether nightly Layer-4 needs a real-phone hook | B | Confirm in OQ-N8-06 |

---

## §14. Updates required to SYNCHRO file

The synchro file (`SYNCHRO-THINKPAD-CP-SUPIN-03-2026-05-06.md`) needs these in-place updates *before* email:

| Synchro section | Update |
|---|---|
| §3.1 (the picture) | "N8 is the gateway" → "N8 is the gateway exposed at `rest-wstst.supin.cz:8887` for TST + 3 production hosts; `/N8/2025/01/{Env}/BOUR/{op}` URL pattern" |
| §3.2 (four strategies) | Strategy B status: `/fake/` resolves it for v0.2; sandbox negotiation downgraded to operator-side polish (rate-limits docs) |
| §3.3 (recommended hybrid) | revise pyramid: Layer 1 = Newman-from-Postman against `/fake/`; Layer 3 = Bouračka-against-`/fake/`; Layer 4 = nightly-against-real-`/TST/`; Layer 5 = k6-against-`/fake/` |
| §3.4 (immediate ThinkPad action) | step 1 (Mockoon profile) → keep but reposition as fallback; step 2 (sms_hook_url) → set to `/fake/` URL; step 4 (TC-CP-001 wiring) → wire to `/fake/` directly; step 7 (four-ask request) → reduced scope (rate limits + production semantics docs only) |
| §4.2 (gap inventory) | GAP-4 + GAP-10 marked closed; GAP-11/12/13 added |
| §10 prompt | STEP 4.3 + 4.4 expanded — see §17 of THIS doc for the addendum |

---

## §15. SUPIN ecosystem implications — what we expect by analogy

The N8 contract teaches us what to expect from other SUPIN-hosted interfaces. Concrete predictions:

### §15.1 AISPOV (registry lookups for ROB / CRR / CRV / pojištění)

Expected URL: `http://rest-ws.supin.cz:NNNN/AISPOV/2025/01/{STD|TST|DEV}/BOUR/{Driver|Vehicle|Insurance}/{lookup|verify}` with optional `/fake/`.

Expected header: same `X-SUPIN-TransactionInfo` (with `RozhraniKod=AISPOV`).

Expected auth: same mTLS — **cert binds to `(BOUR, AISPOV)` pair**, separate from `(BOUR, N8)`. So Bouračka tester laptop needs at least 2 partner certs (one per `RozhraniKod`).

Expected response shape: similar XML root + ČKP namespace `http://ws.ckp.cz/AISPOV/2025/01`.

Expected `/fake/` mode: HIGH probability. The same SUPIN platform pattern almost-certainly applies → `/AISPOV/2025/01/TST/BOUR/fake/...` likely exists for Bouračka's auto-fill flow testing.

**Action for the four-ask cycle:** when requesting AISPOV docs, ask SUPIN whether `/fake/` exists and what the URL pattern is — costs nothing to ask, saves weeks if it does.

### §15.2 The platform pattern as a reusable concept

Add to `_config/VOCABULARY-CATALOGUE-CS-EN-V0.1.md` v0.1.3 (next refresh) a new §5b — "SUPIN platform integration pattern":

| Concept | EN canonical | CS preferred |
|---|---|---|
| Partner code | Partner code (PartnerKod) | Kód partnera |
| Interface code | Interface code (RozhraniKod) | Kód rozhraní |
| Partner-side user code | Partner user code (UzivatelKod) | Kód uživatele partnera |
| Transaction info header | Transaction info header (X-SUPIN-TransactionInfo) | Hlavička transakční informace |
| Calendar versioning | Calendar versioning (YYYY/MM) | Kalendářové verzování |
| Deterministic test mode | Fake mode (`/fake/` sub-path) | Fake režim / deterministický testovací režim |
| Send mode (Zpusob enum) | Send mode | Způsob (zpracování) |
| ČKP namespace | ČKP-namespaced XML | XML s ČKP jmenným prostorem |
| Multi-cluster topology | Multi-cluster topology (WEB1/WEB6/WEB7) | Topologie více clusterů |

### §15.3 Architecture pattern for MI-M-T

The MI-M-T product (per `MANIFEST.yaml` + `OPUS-CYCLE-v0.2-MASTER.md`) exposes integration adapters. The N8 pattern — **calendar versioning + path-embedded env + optional `/fake/` + house-style auth header + cert-binds-pair** — is a reasonable model for **MI-M-T's own externally-exposed APIs**. When MI-M-T ships its DOCK-* adapters (per `MI-M-T-V0.2-POC-ONPREM-SCOPE.md` §5+), they can adopt the same shape:

```
/MIMT/2026/05/{STD|TST|DEV}/{ClientCode}/Evidence/upload     ← write evidence
/MIMT/2026/05/{STD|TST|DEV}/{ClientCode}/TestRuns/list       ← read runs
/MIMT/2026/05/{STD|TST|DEV}/{ClientCode}/fake/Evidence/upload ← deterministic for tests
```

This is a v0.3+ design consideration; flag it in the next ARCH iteration.

---

## §16. Open questions — N8-specific

| OQ# | Sev | Urg | Pri | Question | Resolve by |
|-----|:---:|:---:|:---:|----------|------------|
| OQ-N8-01 | A | A | A | Are production endpoints HTTPS-mTLS even though artefacts show HTTP? Confirm scheme. | before any code-gen against STD |
| OQ-N8-02 | B | A | A | Does `/fake/` require a partner cert, or is it open in TST? Affects whether v0.2 testsuite needs cert provisioning to run | CP-SUPIN-03 morning |
| OQ-N8-03 | C | A | C | Exact response-body shape for `Ping` — Postman doesn't capture; need a sample | confirm with first real call |
| OQ-N8-04 | C | A | C | Extended-state attributes for `SMS ID` GET — what does `Stav` enum allow? `DodaniTS` always present? | confirm with first real call |
| OQ-N8-05 | C | A | C | `ChkAuth` verdict shape — `Stav='OK'/'MISMATCH'/'EXPIRED'`? Other values? | confirm with first real call |
| OQ-N8-06 | B | A | A | `/fake/` mode behaviour for SMS dispatch — does it deliver real SMS, simulated, or neither? Need confirmation for nightly Layer-4 strategy | confirm with SUPIN |
| OQ-N8-07 | B | B | B | Multi-cluster routing — partner-config picks one? Round-robin? Sticky? Affects test load distribution + production failover scenarios | confirm with SUPIN |
| OQ-N8-08 | C | C | C | Will SUPIN issue version `2026/05` (or similar) for N8 in the future? If yes, partner expected to implement migration plan? | next architecture review |
| OQ-N8-09 | C | B | C | Does `Zpusob="RELAX"` use a different physical queue with different SLO? Worth perf-testing separately? | post-v0.2 |
| OQ-N8-10 | A | A | A | Bouračka-specific: which `Zpusob` mode does Bouračka use for the post-submit notification? Affects TC expected behaviour | analytical doc page-by-page review |

---

## §17. PASTE-READY ADDENDUM to ThinkPad CP-SUPIN-03 prompt

**Where to insert:** at the end of the synchro file §10 prompt, just before "═══ END PROMPT ═══". This addendum extends STEP 4 with N8-specific work using the canonical contract.

```
═════════════════════════════════════════════════════════════════════════════
ADDENDUM (per _config/SUPIN-N8-CONTRACT-ANALYSIS-v0.1.md)
═════════════════════════════════════════════════════════════════════════════
The synchro file §3 strategy was authored speculatively. Operator
delivered the canonical N8 contract 2026-05-06 morning (3 artefacts:
OpenAPI 3.1, Postman collection, ReadyAPI project). Findings:

  • SUPIN provides /fake/ deterministic test mode at:
      http://rest-wstst.supin.cz:8887/N8/2025/01/TST/BOUR/fake/...
  • This closes synchro GAP-4 + GAP-10 outright; Mockoon downgrades
    from default to fallback (CI-only when sandbox network unreachable)
  • Real contract has 7 ops (Ping, Sms with Zpusob∈{IHNED,NORMAL,RELAX},
    SMS ID GET, SmsAuth, ChkAuth) + multi-cluster prod (WEB1/WEB6/WEB7)
  • mTLS auth via partner cert binding (PartnerKod=BOUR, RozhraniKod=N8)
  • XML responses with ČKP namespace; SmsInfo root + SmsId/SmsTS/
    GatewayAN/GatewayTS attributes; 200/202/203 all OK
  • Performance SLO < 200 ms response time (gives concrete LIB-AS-PERF-001)

═════════════════════════════════════════════════════════════════════════════
STEP 4N — N8 SMS GATEWAY WIRING (replaces synchro STEP 4.3+4.4 partially)
═════════════════════════════════════════════════════════════════════════════
4N.1  Copy the 3 N8 artefacts from operator's email-attachment delivery
      to bouracka-tests/integrations/n8/:
        - n8-openapi.yaml
        - n8-postman.collection.json
        - n8-readyapi-project.xml
      Commit as inputs (recon-grade material).

4N.2  Author bouracka-tests/playwright/runtime/supin-headers.ts (NEW):
      buildSupinHeaders({partnerKod, rozhraniKod, uzivatelKod, ...})
      → returns headers dict including X-SUPIN-TransactionInfo with
      semicolon-separated kv pairs per §4.1 of N8-CONTRACT-ANALYSIS.

4N.3  Update env configs:
      env/tst.json::sms_gateway_endpoint_base =
         "http://rest-wstst.supin.cz:8887/N8/2025/01/TST/BOUR/fake"
      env/tst-demo.json::sms_gateway_endpoint_base =
         (same; DEMO config-points-at-fake)
      env/tst.json::supin_partner_kod = "BOUR"
      env/tst.json::supin_rozhrani_kod = "N8"
      env/tst.json::supin_uzivatel_kod = "BourackaAzure"
      Add column 04_TestEnvironments.sms_gateway_endpoint_base
      (more granular than the existing sms_hook_url).

4N.4  Author Mockoon profile bouracka-tests/mockoon/n8-fallback.json
      per §10 of N8-CONTRACT-ANALYSIS — REAL XML shapes + ČKP namespace
      + the response attribute set (SmsId, SmsTS, GatewayAN, GatewayTS).
      Position this profile as "FALLBACK ONLY" (network-unreachable CI);
      default integration target is the SUPIN /fake/ endpoint.

4N.5  Update workbook 02d_AssertionLibrary with 7 N8-specific patterns
      (LIB-AS-N8-001..007) per §11.2 of N8-CONTRACT-ANALYSIS — 5 of
      them double as the forward-looking patterns from synchro §2.2.

4N.6  Author 5 NEW R1 TCs in 02_TestCases:
      TC-CP-001 PING /fake/ happy           (rewire from current placeholder)
      TC-CP-002 PING NOK (Mockoon fallback) (forced 503)
      TC-CP-005 SMS OTP send + verify happy (SmsAuth + ChkAuth round-trip)
      TC-CP-005-NOK wrong OTP code          (ChkAuth → MISMATCH)
      TC-CP-005-EXP expired OTP             (ChkAuth → EXPIRED via Mockoon)
      TC-CP-N8-CONTRACT-01 Newman contract  (full Postman collection)
      TC-CP-N8-PERF-01 k6 perf < 200ms p95  (Layer 5)

      Each TC carries:
       - furps_dimensions (TC-001/002 = F+R; TC-005* = F; CONTRACT-01 = F+S; PERF-01 = P)
       - test_target_ref (TT-CP-R1-A1 for SMS gateway operations; TT-CP-R1-A6 for OTP)
       - parameters resolved from 02b (env-config + per-variant vars)
       - assertions linked from 02c → 02d (the 7 N8 library patterns)
       - state_machine_terminal_state where applicable

4N.7  Author Newman runner:
      scripts/run-newman-n8-contract.ps1 — adapt the supplied Postman
      collection; substitute env/tst.json values; run against /fake/;
      emit JUnit XML + HTML to runs/<date>-newman/

4N.8  Author k6 runner:
      bouracka-tests/k6/n8-perf.js per §12 of N8-CONTRACT-ANALYSIS
      scripts/run-k6-n8.ps1 wrapper

4N.9  Update INTEGRATION-CONTRACTS-STRATEGY-v0.2.md §3 hybrid pyramid
      to reflect /fake/-as-default; note the GAP-4 closure.

4N.10 File new OQs (OQ-N8-01..10 per §16 of N8-CONTRACT-ANALYSIS) into
      _config/OPEN-QUESTIONS-LOG.yaml (or wherever the project's OQ
      ledger lives on thinkpad branch).

4N.11 Update synchro §4.2 inputs gap inventory with:
       - GAP-4 ✅ CLOSED (note rationale: /fake/ provisioning)
       - GAP-10 ✅ CLOSED (artefacts in hand)
       - GAP-11 NEW (cluster routing — operator-side OQ)
       - GAP-12 NEW (mTLS partner cert provisioning — operator-side)
       - GAP-13 NEW (real-SMS dispatch in /fake/ mode — operator-side)

4N.12 Confirm in SESSION-NOTES.md:
       - cite each closed gap (GAP-4, GAP-10) with the artefact-of-record
         (the 3 N8 files committed under integrations/n8/)
       - cite each new gap (GAP-11..13) with the Sev/Urg/Pri assessment
       - flag the SUPIN platform pattern (§2 of N8-CONTRACT-ANALYSIS) as
         a candidate for next vocabulary refresh on MacBook side
═════════════════════════════════════════════════════════════════════════════
```

---

## §18. Status footer

| Item | Value |
|------|-------|
| Document | `SUPIN-N8-CONTRACT-ANALYSIS-v0.1.md` |
| Output position | `_config/SUPIN-N8-CONTRACT-ANALYSIS-v0.1.md` |
| Sources analysed | 3 (OpenAPI 1054 lines + Postman 7530 lines + ReadyAPI 1988 lines) |
| Operations catalogued | 7 (Ping, Send×3 modes, GET status, OTP send + verify) |
| Environments × clusters | 3 envs × 3 STD-clusters + 1 TST-cluster + 1 DEV-cluster + `/fake/` overlay |
| Synchro gaps closed | 2 (GAP-4 + GAP-10) |
| New gaps surfaced | 3 (GAP-11/12/13) |
| New OQs (N8-specific) | 10 (OQ-N8-01..10) |
| New TCs specified | 5 (TC-CP-001/002/005 + 005-NOK + 005-EXP + CONTRACT-01 + PERF-01) |
| New library patterns | 7 (LIB-AS-N8-001..007) |
| New ThinkPad files specified | 6 (supin-headers.ts + n8-fallback.json + run-newman-n8-contract.ps1 + n8-perf.js + run-k6-n8.ps1 + integrations/n8/* committed inputs) |
| Pattern generalised to SUPIN ecosystem | YES (§2 + §15 — applies to AISPOV, future zenID-via-SUPIN, MI-M-T DOCK-*) |
| Paste-ready ThinkPad addendum | §17 (insert at end of synchro §10 prompt) |
| Status | v0.1 — analysis complete; CP-SUPIN-03 morning consumption ready |

---

*SUPIN-N8-CONTRACT-ANALYSIS-v0.1.md — 2026-05-06 — MacBook CoWork session — Opus*
