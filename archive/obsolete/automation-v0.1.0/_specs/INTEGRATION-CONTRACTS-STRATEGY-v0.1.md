# Integration Contracts Strategy — v0.1

> **The problem.** Bouračka leans on third-party + register-backed
> services (zenID, AISPOV → ROB / CRR / CRV / pojištění, SMS Gateway,
> RUIAN, Google Maps, reCAPTCHA, SMTP). Each has a different
> "how-do-we-test-against-it?" answer. **zenID is the hardest** —
> camera-driven SDK, OCR on personal documents, no public sandbox.
> This doc lays out the option menu, recommends a hybrid, and
> provides drafts the operator can send to SUPIN to settle the
> contract.
>
> **Audience.** Operator (Petr) negotiating with SUPIN; CP-SUPIN-03+
> dev sessions consuming the resulting fixtures.
>
> **Status.** v0.1 — strategic; specific quantities (number of
> sample photos, exact endpoints) firm up after the SUPIN reply.

---

## §1. Why zenID is the hardest one

| Constraint | Impact on tests |
|------------|-----------------|
| **Personal-data law** (GDPR + Czech act 110/2019) | Cannot upload real OP/ŘP photos to a test environment without explicit consent of the document holder; "test data" must be anonymised or synthetic |
| **Anti-forgery law** (zákon č. 269/1994 Sb. + §348 trestního zákoníku) | Synthetic OP/ŘP photos must carry visible "VZOREK / SPECIMEN" markings so they cannot be confused with valid documents |
| **Camera-driven SDK** | The zenID WebSDK takes over the browser camera and guides the user through the capture; automated tests cannot drive the camera UI in the same way they drive a regular `<input type=file>` |
| **Stochastic OCR results** | Real OCR returns different confidence scores per attempt; tests need a deterministic OK / WARNING / NOK outcome to assert against |
| **Vendor opacity** | zenID is a commercial product; no public docs of the request/response contract; no published sandbox |

The same constraints (with milder versions) apply to AISPOV
(government registers), SMS Gateway (real SMS to real phones), and
to a lesser extent RUIAN (no privacy issue, just rate limits).

## §2. The four strategies

### §2.1 Strategy A — Mock at the network layer

Test framework intercepts the SUT's calls to zenID and returns canned
responses (Playwright `page.route()`, Mockoon, MockServer).

```
SUT  ─→ [intercepted by Mockoon at localhost:8025] ─→ canned response
```

| Pro | Con |
|-----|-----|
| Fully deterministic | Bypasses the real zenID WebSDK entirely — doesn't test the camera + upload UI surface |
| Fast (no upload, no OCR) | We only know how the SUT *handles* zenID's response, not whether the integration *contract* still matches |
| No personal-data exposure | Brittle to zenID API changes — our mock can drift from reality silently |
| Immediate; no vendor dependency | Mock fixtures must be authored by reverse-engineering the contract from the analytical doc |

**Best for:** Layer 1 contract tests + Layer 3 mocked-integration E2E.
Default fall-back when no vendor data is available.

### §2.2 Strategy B — Vendor sandbox (the "right" answer)

Ask SUPIN/zenID for **test-mode credentials** that produce
predictable results from a small set of test-only inputs. Most
enterprise OCR vendors (DocuVix, Veriff, Onfido, Jumio) have this
pattern; zenID likely does too.

```
SUT (configured with TEST_API_KEY) ─→ zenID sandbox endpoint ─→ canned response per input id
```

| Pro | Con |
|-----|-----|
| Tests the **real** WebSDK + the real network path | Depends on vendor responsiveness |
| Vendor-maintained → never drifts from production | Needs a written request + likely an NDA |
| No legal risk from real personal data | May cost money (some vendors charge for sandbox seats) |
| Same test fixtures work for tst + tst-demo | Setup time: weeks-to-months from request to access |

**Best for:** Layer 4 E2E real-integration runs + Layer 5 perf
smoke. The strategic target.

### §2.3 Strategy C — Synthetic photos + golden-master responses

Curate a small set of **synthetic** OP/ŘP/SPZ photos that:
- carry a visible "VZOREK / SPECIMEN" overlay (legal safety),
- are not real persons,
- have known expected OCR results stored alongside.

Each synthetic photo is run through real zenID once; the response
is captured as a "golden master" and stored. Subsequent tests
re-run the same photo and assert against the golden master.

```
synthetic-op-tester-jeden.jpg      golden-master-tester-jeden.json
       ▼                                      ▲
       └──→ zenID real ──────────────────────→┘
                          (assert match)
```

| Pro | Con |
|-----|-----|
| Tests the **real** OCR pipeline end-to-end | OCR is stochastic — golden master may need re-baselining periodically |
| No vendor dependency | Need to author + maintain synthetic photos (skill: graphic design + Czech-doc layout knowledge) |
| Privacy + anti-forgery clean if "VZOREK" overlay visible | Depends on availability of zenID documentation to interpret responses |
| Deterministic-ish (use same photos every run) | Slow — every test invocation runs real OCR |

**Best for:** A nightly "real-zenID smoke" that validates the
contract hasn't drifted, plus the curated photos become the
**fixture set** the dev sessions use for E2E.

### §2.4 Strategy D — SUT-side bypass via config flag

Per analytical doc page 25/133: *"V případě, že aplikace zjistí
z konfigurace, že má některé integrace přeskakovat, bude příslušné
obrazovky hlášení provedeny ihned v editačním režimu k provolání
dané služby nedojde."*

The SUT itself supports a config flag that **skips** integrations
in `tst.*`. Tests opt into the bypass and enter data manually.

```
SUT configured with skip_zenid=true ─→ zenID never invoked
                                       editing-mode form rendered
                                       test fills manually
```

| Pro | Con |
|-----|-----|
| Zero new infrastructure; uses an existing SUT mechanism | Doesn't test the zenID code path at all |
| Fully deterministic | Misses regressions in the SUT's zenID handling |
| Fast | Cannot test the WARNING / NOK branches without invoking zenID |
| Privacy-clean | Manual-entry path may differ slightly from auto-fill — can't validate auto-fill behaviour |

**Best for:** The bulk of E2E TCs that are about non-zenID
behaviour (wizard navigation, witness add, signing). When the test
isn't *about* zenID, skip it.

## §3. Recommended hybrid

**Use all four strategies in different layers of the test pyramid.**
Each layer of `_install/INSTALL-PLAN-FULL-ECOSYSTEM-v0.1.md` §2 picks
the strategy that fits its purpose:

```
Layer 1 — Service Contract (Newman/SOAP/k6 against zenID)
   ↳ Strategy B if vendor sandbox available; else Strategy A (Mockoon
     with hand-authored fixtures derived from analytical doc).
   ↳ Cadence: every pipeline run, ≤ 30 s.

Layer 2 — Data-validation gate
   ↳ Strategy A or B — same as Layer 1; validates that fixtures
     produce the expected service responses.

Layer 3 — Mocked-integration E2E
   ↳ Strategy A — Mockoon supplies the canned responses; SUT exercises
     real WebSDK (camera permission flow, upload, popup-confirm) but
     the OCR endpoint is intercepted.

Layer 4 — Real-integration E2E
   ↳ Strategy D for default — fast, deterministic, exercises every
     non-zenID code path for daily runs.
   ↳ Strategy C nightly subset — runs ~5 synthetic-photo TCs against
     real zenID to detect contract drift.

Layer 5 — Performance/load
   ↳ Strategy A only — never hammer the real zenID with k6 (cost +
     vendor terms-of-service). Mock at network layer.
```

**Coverage matrix:**

| TC class | Layer 4 strategy | Layer 5 strategy |
|----------|------------------|------------------|
| TC-CP-001..007 (Phone OTP — does not touch zenID) | D bypass | A mock |
| TC-CP-008 happy zenID + AISPOV ROB | D bypass for E2E + C nightly real | A mock |
| TC-CP-009 zenID NOK → manual fallback | A intercept (force NOK response) | A mock |
| TC-CP-010 AISPOV NENALEZENO | D for zenID + A mock for AISPOV | A mock |
| TC-CP-011 camera-permission denied | D for zenID + Playwright permission API | A mock |
| TC-CP-012 SPZ scan + AISPOV vehicle | D bypass for E2E + C nightly real | A mock |
| TC-CP-013 SPZ NOK → gallery | A intercept (force NOK on first call) | A mock |
| TC-CP-014..020 | D bypass | A mock |

This keeps:
- **daily E2E pipeline runs fast** (Strategy D dominates),
- **regression sentinel real** (Strategy C nightly catches contract drift),
- **failure modes coverable** (Strategy A injects WARNING/NOK on demand),
- **vendor cost zero** (no real zenID calls in load tests).

## §4. What we need to make this work — the SUPIN/zenID contract

To enable Strategies B + C, the operator needs four things from
SUPIN/zenID. The draft email template is in
`_install/contracts/zenid-test-data-request.md`. The four asks:

1. **Test-mode credentials** for zenID WebSDK + zenID API in `tst.*`.
   Either (a) sandbox endpoint URLs + API key, or (b) a documented
   `test_mode: true` flag the existing SUT instance can set in tst.*.
2. **Documentation of the request/response contract** — the WebSDK
   JS SDK callback shape + the API REST contract (OpenAPI or
   plain-doc). Specifically: what the OK / WARNING / NOK envelopes
   look like, what fields they carry (first_name, last_name, dob,
   document_number, …), and what the confidence-score thresholds
   for OK ↔ WARNING ↔ NOK are.
3. **Sample fixtures**: 3–5 example synthetic OP / ŘP / SPZ photos
   (or ID strings) that produce known OCR results in test mode.
   These become our golden-master inputs for Strategy C.
4. **Confirmation of the SUT-side `skip_zenid` flag** — name of the
   config attribute, the env var or DB row that controls it,
   and confirmation it's safe to flip in `tst.*` without affecting
   other tester sessions.

Plus, for completeness, the same four-ask pattern applied to AISPOV,
SMS Gateway, RUIAN, Maps. See §6 below.

## §5. Fallback if SUPIN/zenID is non-responsive

If asks 1+2+3 do not land within the CP-SUPIN-03..08 window
(week-end deliverable target), the suite ships with **Strategy A
only** for zenID:

- Mockoon hosts the zenID stub at `localhost:8025`.
- Mock fixtures hand-authored from the analytical-doc field-shapes
  + community-knowledge of similar OCR vendors' response shapes.
- Tests that depend on real zenID behaviour are **skipped with a
  documented reason** (`OQ-CP-23 not yet resolved`).
- A `tools/zenid-mock-fixtures-stub.js` module exposes:
  - `mockHappy(driver_id)` → returns OK shape with given driver
    data
  - `mockWarning(driver_id, fields_low_confidence)` → WARNING shape
  - `mockNok(reason)` → NOK shape
  - `mockCameraPermissionDenied()` → simulates the SDK's own error
- This buys us R1 functional coverage without a vendor dependency,
  at the cost of "we don't yet know the integration is real".

We document this trade-off in the SecOps/SUPIN delivery note so it
is not silent.

## §6. Same pattern, other integrations

| Integration | Strategy A (mock) feasible? | Strategy B (sandbox) likely? | Strategy C (golden-master) needed? | Strategy D (SUT-bypass) supported? |
|-------------|:---------------------------:|:----------------------------:|:----------------------------------:|:----------------------------------:|
| zenID | YES (Mockoon) | yes — to be requested | YES (5 photos) | YES per analytical doc p25 |
| AISPOV (ROB / CRR / CRV / pojištění) | YES (Mockoon) | likely — SUPIN owns it | NO (data, not images) | YES per analytical doc p25 |
| SMS Gateway | YES (REST mock) | likely — SUPIN owns it | n/a | YES (PING + read-back hook) |
| RUIAN | YES (REST mock) | RUIAN has a public API | n/a | not needed (data is public) |
| Google Maps | YES (REST mock) | Google billing-protected | n/a | YES (manual-address fallback) |
| reCAPTCHA | YES (script intercept) | Google has test keys | n/a | YES (per analytical doc p25) |
| SMTP | YES (Mailpit) | n/a | n/a | YES (test SMTP relay) |
| Azure Blob outage | YES (static JSON) | n/a (config we own) | n/a | YES (config-driven) |

For each, the same four-ask request goes to whoever owns the
integration on SUPIN's side. The zenID request is the most urgent
because zenID is the only **commercial-vendor** integration —
SUPIN can answer the others themselves.

## §7. Action items (for the operator)

1. **Send the request** in `_install/contracts/zenid-test-data-request.md`
   to your SUPIN contact this week. Cc the SUPIN / ČKP integration
   architect if known.
2. **Track responses** in a new file
   `_install/contracts/responses-log.md` — one entry per ask, with
   date sent / date received / accepted-rejected / next step.
3. **Curate 3 synthetic OP photos** as a parallel track (Strategy C
   prep). Skill needed: graphic design or AI image generation; visible
   "VZOREK" / "SPECIMEN" overlay; not a real person. If unsure where
   to start, search Czech web for existing "vzorové" OP layouts (the
   Ministry of Interior publishes a layout reference) and adapt.
4. **Confirm with ČKP legal** that the synthetic-photos approach is
   acceptable — usually it is, but a formal sign-off saves time
   later.
5. **Schedule a 30-min sync** with the SUPIN integration team to
   walk them through this doc + the request. Faster than e-mail
   round-trips.

## §8. Budget — time + token estimates

| Activity | Effort | Pre-condition |
|----------|--------|---------------|
| Mock fixtures for Strategy A (zenID) | 1 ThinkPad Sonnet session | analytical-doc response shapes (we have enough) |
| Synthetic-photo authoring (Strategy C) | 0.5 day operator + designer | legal sign-off on §7 ask 4 |
| First real-zenID golden-master capture | 1 ThinkPad session × 5 photos | sandbox credentials (§4 ask 1) |
| Vendor sandbox negotiation (Strategy B) | weeks of operator+SUPIN | vendor-side responsiveness |
| Pipeline integration of all four strategies | 1 ThinkPad session per layer | mock fixtures + skip-flag confirmed |

**Total** to a working hybrid: ~5 ThinkPad sessions + parallel ops
work. Aligns with CP-SUPIN-03..08 plan.

## §9. Status

| Item | Value |
|------|-------|
| Document | `_specs/INTEGRATION-CONTRACTS-STRATEGY-v0.1.md` |
| Companion | `_install/contracts/zenid-test-data-request.md` (the draft request) |
| Strategies covered | 4 (Mock / Vendor sandbox / Synthetic golden-master / SUT-bypass) |
| Recommended | Hybrid — different strategy per pyramid layer + per TC class |
| Resolves OQ | partially OQ-CP-23 (zenID contracts); pattern applies to OQ-CP-22 (AISPOV WSDL) too |
| Status | v0.1 — strategy locked; the asks need to land before depth ships |
