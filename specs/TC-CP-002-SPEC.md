# TC-CP-002 — Implicitní ID-autentizace — negativní konec / Implicit ID-auth — negative-ending

> Naskenuj neplatný OP nebo nenalezené SPZ → registr 'not found' →
> průvodce ukončí s CS zprávou + actionable next step (kontakt ČKP).

## Status

```yaml
spec_version: 0.1.0
spec_status: draft
maps_to_test_target: TT-CP-R1-001, TT-CP-R1-004
release: R1
type: failure
priority: A
maps_to_flow: FLW-004 (irrecoverable subset — F1 ID-not-found branch)
maps_to_integrations: INT-004
framework_targets:
  - playwright
  - cypress
last_updated: 2026-05-05
last_updated_by: cowork-opus-cp-supin-02
```

## Reference index

- TestTarget(s):  TT-CP-R1-001, TT-CP-R1-004
- Flow:           FLW-004 (irrecoverable F1 branch)
- Integrations:   INT-004 (registry — primary; expects 404)
- Screens:        SCR-002, SCR-006 (pending)
- Known issues:   none
- Divergences:    DIV-CP-002 (DEMO may relax registry-validation entirely;
                  recon pending)
- Env config:     env/tst.json, env/tst-demo.json

## Pre-conditions

### Boolean conditions

- [PRE-1] env reachable.
- [PRE-2] `env.recaptcha_bypass_token` configured for tst.*.
- [PRE-3] `env.registry_stub_url` resolves and `/healthz` returns 200.
- [PRE-4] `fixtures/invalid-login.json::wrong_id` row exists with shape
        `{op_number: '<intentionally invalid>', expected_status: 404,
        expected_error_code: 'ID_NOT_FOUND'}` (TD-CP-001).
- [PRE-5] Document-photo placeholder fixture exists:
        `fixtures/shared/photos/op-invalid.jpg` (any clear photo of a
        non-registered ID).

### Setup steps

1. Spin a fresh browser context (cs-CZ, Europe/Prague).
2. Clear cookies.
3. Set reCAPTCHA bypass.
4. Pre-warm registry stub `/healthz`.

## Test data

| Slot | Fixture ref | Notes |
|------|-------------|-------|
| invalid_id | TD-CP-001 (`fixtures/invalid-login.json::wrong_id`) | OP number not in registry |
| op_photo | `fixtures/shared/photos/op-invalid.jpg` | clear (so OCR succeeds; only the LOOKUP fails) |

## Integration touchpoints

| Integration | Env: tst | Env: tst-demo | Test posture |
|-------------|----------|---------------|--------------|
| INT-004 registry — driver lookup | mock-respond: status 404, body.error_code = "ID_NOT_FOUND" | DEMO may bypass lookup — see env_divergence | mock-respond: the test sets up an interceptor that overrides the stub's response with a 404 for THIS test only |

## Steps

### STEP 1
```yaml
id: TC-CP-002-S-01
kind: trigger_point
title_cs: Navigace na /formular
title_en: Navigate to /formular
selector: n/a
input: env.base_url + "/formular"
expected: HTTP 2xx
viewport_applicability: all
env_divergence:
  tst: same
  tst-demo: same
integration_touchpoint: none
recovery: none
notes: same as TC-CP-001 STEP 1
```

### STEP 2
```yaml
id: TC-CP-002-S-02
kind: trigger_point
title_cs: Aktivuj mock 404 na /api/registry/driver-lookup
title_en: Install mock 404 for /api/registry/driver-lookup
selector: |
  network-route:
    page.route('**/api/registry/driver-lookup', route =>
      route.fulfill({status: 404, body: '{"error_code":"ID_NOT_FOUND"}'}))
input: none
expected: route registered before the wizard advances
viewport_applicability: all
env_divergence:
  tst: as above
  tst-demo: skip if env.validation_relaxations.ocr_auto_fill_required==false
           AND lookup is bypassed entirely (in which case no terminator
           fires — this TC verdict = 'skip' with reason)
integration_touchpoint: INT-004 [mock-respond]
recovery: none
notes: |
  This test deterministically forces the not-found branch via interception,
  rather than depending on the stub's configured rejection set.
```

### STEP 3
```yaml
id: TC-CP-002-S-03
kind: trigger_point
title_cs: Klikni "VYPLNIT ZÁZNAM"
title_en: Click primary CTA
selector: page.getByRole('button', { name: /Vyplnit záznam/i }).first()
input: none
expected: navigation to wizard step 1
viewport_applicability: all
env_divergence:
  tst: same
  tst-demo: same
integration_touchpoint: none
recovery: none
notes: same as TC-CP-001 STEP 4
```

### STEP 4
```yaml
id: TC-CP-002-S-04
kind: trigger_point
title_cs: Nahraj OP foto (čitelné, ale s neplatným ID)
title_en: Upload OP photo (readable, but with invalid ID)
selector: |
  page.getByLabel(/Nahrát|Vyfotit/i, { exact: false })
      .or(page.locator('input[type="file"][name*="op"]'))
      .first()
input: fixtures/shared/photos/op-invalid.jpg
expected: file accepted; OCR pipeline runs; lookup is invoked
viewport_applicability: all
env_divergence:
  tst: same
  tst-demo: skip if OCR disabled (no lookup → no terminator → skip TC)
integration_touchpoint: INT-004 [mock-respond]
recovery: none
notes: |
  STEP 2 ensures the lookup returns 404.
```

### STEP 5
```yaml
id: TC-CP-002-S-05
kind: data_collection_point
title_cs: Zachyť volání driver-lookup
title_en: Capture driver-lookup call
selector: |
  page.waitForResponse(r => r.url().includes('/registry/driver-lookup'))
input: none
expected: exactly 1 response observed within 10 s with status 404
viewport_applicability: all
env_divergence:
  tst: same
  tst-demo: skip per STEP 4
integration_touchpoint: INT-004
recovery: none
notes: |
  AC-2 trace.
```

### STEP 6
```yaml
id: TC-CP-002-S-06
kind: assertion
title_cs: Ověř, že odpověď má status 404 a error_code 'ID_NOT_FOUND'
title_en: Assert response status 404 + error_code 'ID_NOT_FOUND'
selector: response captured in STEP 5
input: none
expected: |
  response.status() === 404 AND
  response.json().error_code === 'ID_NOT_FOUND'
viewport_applicability: all
env_divergence:
  tst: as stated
  tst-demo: skipped per STEP 4
integration_touchpoint: INT-004
recovery: none
notes: |
  AC-2.
```

### STEP 7
```yaml
id: TC-CP-002-S-07
kind: data_collection_point
title_cs: Zachyť CS chybovou zprávu na obrazovce
title_en: Capture CS error message on screen
selector: |
  page.getByRole('alert')
      .or(page.locator('[role="status"], [data-error="true"], .error-msg'))
input: none
expected: locator visible within 5 s; non-empty innerText
viewport_applicability: all
env_divergence:
  tst: same
  tst-demo: skipped per STEP 4
integration_touchpoint: none
recovery: none
notes: |
  AC-3 trace.
```

### STEP 8
```yaml
id: TC-CP-002-S-08
kind: assertion
title_cs: Ověř, že CS zpráva odpovídá očekávanému regex
title_en: Assert CS message matches expected regex
selector: locator from STEP 7
input: none
expected: |
  innerText matches one of:
    /Doklad nenalezen/i
    /nenalezeno v registru/i
    /údaje nelze ověřit/i
    /kontaktujte ČKP/i
  (any one match satisfies)
viewport_applicability: all
env_divergence:
  tst: as stated
  tst-demo: relaxed — accept any non-empty error text
integration_touchpoint: none
recovery: none
notes: |
  AC-3. Exact regex set will tighten as user-template recon arrives.
```

### STEP 9
```yaml
id: TC-CP-002-S-09
kind: assertion
title_cs: Ověř, že průvodce nepokračoval
title_en: Assert wizard did NOT advance
selector: page URL
input: none
expected: |
  URL matches the same wizard step as STEP 4 (NOT advanced)
  AND no element-tree change indicating "step 2 of N" or further
viewport_applicability: all
env_divergence:
  tst: same
  tst-demo: skipped per STEP 4
integration_touchpoint: none
recovery: none
notes: |
  AC-4. Wizard MUST stay on the ID-auth step.
```

### STEP 10
```yaml
id: TC-CP-002-S-10
kind: assertion
title_cs: Ověř, že žádný záznam nebyl uložen
title_en: Assert no record persisted
selector: |
  network-trace:
    no POST to /api/submit OR /api/records observed during this TC
input: none
expected: zero POSTs to those endpoints
viewport_applicability: all
env_divergence:
  tst: same
  tst-demo: same
integration_touchpoint: none
recovery: none
notes: |
  AC-5 — POST-1.
```

### STEP 11
```yaml
id: TC-CP-002-S-11
kind: assertion
title_cs: Ověř, že žádný e-mail nebyl odeslán
title_en: Assert no e-mail dispatched
selector: |
  http-poll:
    GET <env.smtp_hook_url>/messages?to=<fixture.email>
input: none
expected: response array is empty after 5 s
viewport_applicability: all
env_divergence:
  tst: same
  tst-demo: same
integration_touchpoint: INT-003 [intercept-assert]
recovery: none
notes: |
  AC-6 — POST-2.
```

## Post-conditions

- [POST-1] No record persisted (asserted in STEP 10).
- [POST-2] No e-mail dispatched (asserted in STEP 11).
- [POST-3] Browser context closed.

## Acceptance criteria

- [AC-1] At STEP 5, exactly 1 POST to `/api/registry/driver-lookup`
  observed.
- [AC-2] At STEPs 5+6, response status = 404 and body.error_code =
  `ID_NOT_FOUND`.
- [AC-3] At STEPs 7+8, a CS error message renders matching the
  expected regex set.
- [AC-4] At STEP 9, wizard stays on the ID-auth step.
- [AC-5] At STEP 10, no POST to record-persist endpoints.
- [AC-6] At STEP 11, SMTP hook receives 0 messages.

## Env divergences

| Step | TST behaviour | DEMO behaviour |
|------|---------------|----------------|
| STEP 2 (mock 404) | install interceptor | skip TC if OCR-relaxed (no lookup to mock) |
| STEP 8 (CS msg regex) | strict regex set | relaxed — accept any non-empty error |

## Viewport applicability

| Viewport | Run? | Skipped steps |
|----------|------|---------------|
| desktop (1280×720) | YES | none |
| mobile-320 (320×568) | YES | none |
| mobile-375 (375×667) | YES | none |
| mobile-414 (414×896) | YES | none |

(No mobile-only steps — touch-target check is in TC-CP-001.)

## Failure-mode coupling (R-FAIL-1)

This is a **failure** TC. Pairs with **TC-CP-001** (Implicit ID-auth —
happy) per `specs/TC-CP-001-SPEC.md`.

## Code-emission hints

- Use `page.route()` (Playwright) / `cy.intercept()` (Cypress) to
  install the 404 stub for `/api/registry/driver-lookup` BEFORE the
  user uploads the OP photo.
- For Cypress, the `cy.intercept()` URL pattern should be
  `'**/api/registry/driver-lookup'` to match across env base URLs.
- For Playwright, use `await page.route('**/registry/driver-lookup', ...)`
  in test setup.
- Detection of the CS error message should preferentially use
  `getByRole('alert')` first, falling back to the broader CSS
  selector list.
- Test name MUST start with `TC-CP-002 — `.
- For DEMO env-skip path, use `test.skip(condition, reason)` and
  surface the reason in the Excel reporter as verdict `skip`.

## Status

| Item | Value |
|------|-------|
| Spec | `specs/TC-CP-002-SPEC.md` |
| Spec version | 0.1.0 |
| Last updated | 2026-05-05 |
| Related Excel row | `02_TestCases::TC-CP-002` |
| Frameworks ready | playwright + cypress |
| OQs blocking | OQ-CP-14 (reCAPTCHA bypass), OQ-CP-15 (tst.* recon for upload selector + CS message regex tightening) |
