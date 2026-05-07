# TC-CP-001 — Implicitní ID-autentizace — happy / Implicit ID-auth — happy

> Naskenuj OP + ŘP + SPZ → registr roundtrip → auto-fill se zobrazí
> k potvrzení; uživatel pokračuje do dalšího kroku průvodce.

## Status

```yaml
spec_version: 0.1.0
spec_status: draft
maps_to_test_target: TT-CP-R1-001
release: R1
type: happy
priority: A
maps_to_flow: FLW-003
maps_to_integrations: INT-001, INT-004
framework_targets:
  - playwright
  - cypress
last_updated: 2026-05-05
last_updated_by: cowork-opus-cp-supin-02
```

## Reference index

- TestTarget(s):  TT-CP-R1-001 (recon/TEST-TARGET-CANDIDATES.md §1)
- Flow:           FLW-003 (recon/flows/FLW-003.md) — STEPs 1..6
- Integrations:   INT-004 (recon/integrations/INT-004.md) — primary;
                  INT-001 reCAPTCHA (gateway badge presence only)
- Screens:        SCR-002 (gateway), SCR-006 (id-scan step — recon
                  pending tst.* template)
- Known issues:   none
- Divergences:    DIV-CP-001 (DEMO may skip OCR and fall back to manual
                  entry — recon pending)
- Env config:     env/tst.json, env/tst-demo.json

## Pre-conditions

### Boolean conditions

- [PRE-1] env reachable: `GET <env.base_url>/` returns HTTP 2xx.
- [PRE-2] `env.recaptcha_bypass_token` is a non-empty string when
        `env.label ∈ {tst, tst-demo}` (per OQ-CP-14 — assumed
        configured before this TC runs).
- [PRE-3] `env.registry_stub_url` resolves and `GET
        <env.registry_stub_url>/healthz` returns 200.
- [PRE-4] `fixtures/shared/test-drivers.json::tester_jeden` row exists
        with shape `{op_number, rp_number, first_name, last_name, dob}`
        (TD-CP-002).
- [PRE-5] `fixtures/shared/test-vehicles.json::1ZZ_0001` row exists
        with shape `{spz, make, model, year, owner_op_number}`
        (TD-CP-003).
- [PRE-6] Document-photo fixtures exist:
        `fixtures/shared/photos/op-tester-jeden.jpg`,
        `fixtures/shared/photos/rp-tester-jeden.jpg`,
        `fixtures/shared/photos/spz-1zz0001.jpg` (placeholders OK on
        public-dev; real fixtures supplied OOB for tst.*).

### Setup steps

1. Spin a fresh browser context with locale `cs-CZ`, timezone
   `Europe/Prague`, and viewport per project.
2. Clear cookies for the SUT origin.
3. Set the reCAPTCHA bypass cookie if env is `tst` or `tst-demo`
   (cookie name + value carried by env config).
4. Pre-warm: `GET <env.registry_stub_url>/healthz` → assert 200.
   If non-200, this TC verdict = `blocked` (NOT `fail`) — distinguishes
   infrastructure issue from SUT regression.

## Test data

| Slot | Fixture ref | Notes |
|------|-------------|-------|
| primary_driver | TD-CP-002 (`fixtures/shared/test-drivers.json::tester_jeden`) | OP+ŘP valid; auto-fill happy |
| primary_vehicle | TD-CP-003 (`fixtures/shared/test-vehicles.json::1ZZ_0001`) | SPZ in registry stub |
| op_photo | `fixtures/shared/photos/op-tester-jeden.jpg` | clear quality (OCR happy) |
| rp_photo | `fixtures/shared/photos/rp-tester-jeden.jpg` | clear |
| spz_photo | `fixtures/shared/photos/spz-1zz0001.jpg` | clear |

## Integration touchpoints

| Integration | Env: tst | Env: tst-demo | Test posture |
|-------------|----------|---------------|--------------|
| INT-001 reCAPTCHA | bypass_token | bypass_or_disabled | env-config carries token; assert badge attached on `/formular` (one-time) |
| INT-004 registry — driver lookup | real-stub via `env.registry_stub_url` | real-stub-or-skipped | intercept-assert: exactly 1 POST to `/api/registry/driver-lookup` per OP-photo upload; capture response body for AC-3 assertion |
| INT-004 registry — vehicle lookup | real-stub | real-stub-or-skipped | intercept-assert: exactly 1 POST to `/api/registry/vehicle-lookup` per SPZ-photo upload; capture response for AC-4 |

## Steps

### STEP 1
```yaml
id: TC-CP-001-S-01
kind: trigger_point
title_cs: Otevři vstupní bránu /formular
title_en: Navigate to wizard gateway /formular
selector: n/a
input: env.base_url + "/formular"
expected: page navigation initiated; HTTP 2xx
viewport_applicability: all
env_divergence:
  tst: same as default
  tst-demo: same as default
integration_touchpoint: none
recovery: none
notes: |
  Direct nav (skips landing CTA path; that's TC-CP-R2-001's concern).
```

### STEP 2
```yaml
id: TC-CP-001-S-02
kind: assertion
title_cs: Ověř titulek stránky
title_en: Assert page title
selector: page title (browser API)
input: none
expected: regex /Bouračka|dopravní nehoda/i
viewport_applicability: all
env_divergence:
  tst: same
  tst-demo: same
integration_touchpoint: none
recovery: none
notes: |
  AC-1 trace.
```

### STEP 3
```yaml
id: TC-CP-001-S-03
kind: data_collection_point
title_cs: Zachyť přítomnost reCAPTCHA badge
title_en: Capture reCAPTCHA badge presence
selector: env.selectors.recaptcha_badge   # ".grecaptcha-badge, [data-recaptcha]"
input: none
expected: locator attached within 15 s
viewport_applicability: all
env_divergence:
  tst: badge expected attached (bypass token still loads the script)
  tst-demo: badge MAY be absent if reCAPTCHA disabled at env level
integration_touchpoint: INT-001 [intercept-assert]
recovery: none
notes: |
  Per OQ-CP-14 — DEMO may have reCAPTCHA disabled. Spec uses
  env.recaptcha_posture to branch: if 'BYPASS_TOKEN_OR_DISABLED' AND
  badge not attached after 15 s, log warning but continue (NOT fail).
```

### STEP 4
```yaml
id: TC-CP-001-S-04
kind: trigger_point
title_cs: Klikni na hlavní CTA "VYPLNIT ZÁZNAM"
title_en: Click primary CTA "VYPLNIT ZÁZNAM"
selector: |
  role-based:
    page.getByRole('button', { name: /Vyplnit záznam/i }).first()
input: none
expected: navigation to wizard step 1 (URL change)
viewport_applicability: all
env_divergence:
  tst: same
  tst-demo: same
integration_touchpoint: none
recovery: none
notes: |
  AC-2 trace (touch-target size on mobile).
```

### STEP 5
```yaml
id: TC-CP-001-S-05
kind: assertion
title_cs: Mobile-only — touch-target velikosti CTA ≥ 44×44 px
title_en: Mobile-only — CTA touch-target ≥ 44×44 px
selector: same locator as STEP 4
input: none
expected: boundingBox().width >= 44 AND boundingBox().height >= 44
viewport_applicability: [320, 375, 414]
env_divergence:
  tst: same
  tst-demo: same
integration_touchpoint: none
recovery: none
notes: |
  WCAG 2.2 AA target-size. AC-2.
```

### STEP 6
```yaml
id: TC-CP-001-S-06
kind: control_point
title_cs: Větvení dle URL po kliku
title_en: Branch on URL after click
selector: page URL
input: none
expected: URL matches /\/formular\/(zacatek|krok-1|step1)\/?$/
         OR matches /\/wizard\/.+/
viewport_applicability: all
env_divergence:
  tst: URL pattern per env.expected.wizard_step1_path_regex
  tst-demo: same key, possibly different regex
integration_touchpoint: none
recovery: retry-up-to-1
notes: |
  Wizard URL convention not yet recon'd; the regex above is a placeholder
  using likely candidate paths. User template fills the real value.
```

### STEP 7
```yaml
id: TC-CP-001-S-07
kind: trigger_point
title_cs: Nahraj fotku OP
title_en: Upload OP photo
selector: |
  role-based:
    page.getByLabel(/Nahrát|Vyfotit/i, { exact: false })
        .or(page.locator('input[type="file"][name*="op"]'))
        .first()
input: fixtures/shared/photos/op-tester-jeden.jpg
expected: file accepted; OCR pipeline starts
viewport_applicability: all
env_divergence:
  tst: same
  tst-demo: input may be skipped if DEMO disables OCR (manual-entry
           fallback) — env.validation_relaxations.ocr_auto_fill_required
           controls this branch
integration_touchpoint: INT-004 [intercept-assert]
recovery: retry-up-to-1
notes: |
  When mobile + camera permission granted, this would normally trigger
  the camera; in tests we always upload from disk via setInputFiles().
```

### STEP 8
```yaml
id: TC-CP-001-S-08
kind: data_collection_point
title_cs: Zachyť POST /api/registry/driver-lookup
title_en: Capture POST /api/registry/driver-lookup
selector: |
  network-route:
    page.route('**/api/registry/driver-lookup', ...)
    OR page.waitForResponse(r => r.url().includes('/registry/driver-lookup'))
input: none
expected: exactly 1 POST observed within 10 s
viewport_applicability: all
env_divergence:
  tst: same
  tst-demo: 0 POSTs if env.validation_relaxations.ocr_auto_fill_required==false
integration_touchpoint: INT-004 [intercept-assert]
recovery: none
notes: |
  AC-3 trace. Capture response.json() for STEP 9.
```

### STEP 9
```yaml
id: TC-CP-001-S-09
kind: assertion
title_cs: Ověř shape odpovědi z driver-lookup
title_en: Assert driver-lookup response shape
selector: response captured in STEP 8
input: none
expected: |
  status === 200 AND
  body.first_name === fixtures.tester_jeden.first_name AND
  body.last_name === fixtures.tester_jeden.last_name AND
  body.dob === fixtures.tester_jeden.dob
viewport_applicability: all
env_divergence:
  tst: assertion as stated
  tst-demo: skip on DEMO if INT-004 skipped (per STEP 8 branch)
integration_touchpoint: INT-004 [intercept-assert]
recovery: none
notes: |
  AC-3.
```

### STEP 10
```yaml
id: TC-CP-001-S-10
kind: data_collection_point
title_cs: Zachyť rendered auto-fill (jméno + DOB)
title_en: Capture rendered auto-fill (name + DOB)
selector: |
  page.getByRole('region', { name: /údaje řidiče|driver/i })
      .or(page.locator('[data-section="driver"]'))
input: none
expected: locator visible AND innerText contains body.first_name
viewport_applicability: all
env_divergence:
  tst: same
  tst-demo: locator may be a manual-entry form instead of auto-fill —
           env.validation_relaxations.ocr_auto_fill_required==false
           branches to STEP 10b (manual entry; defined in TC-CP-001-DEMO)
integration_touchpoint: none
recovery: none
notes: |
  AC-5.
```

### STEPs 11–14 — repeat 7..10 for ŘP photo
```yaml
# Same shape as STEPs 7..10, with input = rp_photo and selector
# adjusted to the RP-upload widget. driver-lookup may be a single
# call covering OP+ŘP combined or separate per-doc calls — this is
# determined by user template.
```

### STEPs 15–18 — repeat 7..10 for SPZ photo (vehicle-lookup)
```yaml
# Same shape, but the integration is INT-004 vehicle-lookup endpoint
# (POST /api/registry/vehicle-lookup) and assertion is on
# fixtures.test_vehicles.1ZZ_0001 shape.
```

### STEP 19
```yaml
id: TC-CP-001-S-19
kind: trigger_point
title_cs: Klikni "Pokračovat"
title_en: Click "Pokračovat"
selector: page.getByRole('button', { name: /Pokračovat|Continue/i }).first()
input: none
expected: navigation to next wizard step
viewport_applicability: all
env_divergence:
  tst: same
  tst-demo: same
integration_touchpoint: none
recovery: none
notes: |
  This TC ends here; deeper steps belong to TC-CP-003.
```

### STEP 20
```yaml
id: TC-CP-001-S-20
kind: assertion
title_cs: Ověř, že průvodce postoupil
title_en: Assert wizard advanced
selector: page URL or step-indicator
input: none
expected: URL matches /\/(krok-2|step2|telefony)\/?$/
         OR a step-indicator element shows step 2 of N selected
viewport_applicability: all
env_divergence:
  tst: same
  tst-demo: same
integration_touchpoint: none
recovery: none
notes: |
  AC-6 — terminal assertion of TC-CP-001.
```

## Post-conditions

- [POST-1] No record persisted yet (POST `/api/submit` was NOT called
  during this TC). Assertable: capture network trace and confirm zero
  POSTs to `/api/submit` or `/api/records`.
- [POST-2] No emails dispatched. Poll SMTP hook for 0 messages addressed
  to fixtures.tester_jeden.email within 5 s.
- [POST-3] Browser context closed; no localStorage entries persist
  across tests.

## Acceptance criteria

- [AC-1] At STEP 2, page title matches `/Bouračka|dopravní nehoda/i`.
- [AC-2] At STEPs 4 + 5, primary CTA visible; on viewports 320/375/414
  bounding box dims ≥ 44×44 px.
- [AC-3] At STEP 9, exactly 1 POST to `/api/registry/driver-lookup`
  observed; response.body.first_name + last_name + dob match fixture
  exactly. (Skipped on DEMO with OCR-relaxed env.)
- [AC-4] At STEPs 11–18 equivalents, exactly 1 POST per
  document/vehicle lookup; response shapes match fixtures.
- [AC-5] At STEP 10, auto-fill region renders the looked-up identity
  visibly. (Or, on DEMO, manual-entry form renders.)
- [AC-6] At STEP 20, wizard advanced past the ID-auth step.

Each AC traces to ≥ 1 step's assertion. Failure of any AC = test
verdict `fail`.

## Env divergences

| Step | TST behaviour | DEMO behaviour |
|------|---------------|----------------|
| STEP 3 (reCAPTCHA badge) | badge attached | may be absent (warning, not fail) |
| STEP 7..18 (registry calls) | exactly 1 POST per doc | 0 POSTs if OCR disabled; manual entry instead |
| STEP 10 (auto-fill region) | auto-fill region visible | manual-entry form visible |

## Viewport applicability

| Viewport | Run? | Skipped steps |
|----------|------|---------------|
| desktop (1280×720) | YES | STEP 5 (mobile-only) |
| mobile-320 (320×568) | YES | none |
| mobile-375 (375×667) | YES | none |
| mobile-414 (414×896) | YES | none |

## Failure-mode coupling (R-FAIL-1)

This is a **happy** TC. Pairs with **TC-CP-002** (Implicit ID-auth —
negative-ending) per `specs/TC-CP-002-SPEC.md`.

## Code-emission hints

- Page-Object Model: extend
  `playwright/pages/WizardGatewayPage.ts` and create
  `playwright/pages/WizardIdAuthPage.ts` (NEW) for STEPs 7–20.
- Cypress: use `cy.viewportPreset()` from `support/e2e.ts`.
- File-upload via `setInputFiles()` (Playwright) /
  `cy.get('input[type=file]').selectFile(...)` (Cypress).
- Register-route intercept: Playwright `page.route(...)` ; Cypress
  `cy.intercept(...)`.
- Do NOT emit `cy.wait(N)` or `page.waitForTimeout(N)`; always wait on
  network / locator visibility.
- Each generated test name MUST start with `TC-CP-001 — ` so the
  Excel reporter extracts the TC ref.
- Skip STEP 5 on the desktop project (`testInfo.project.name` doesn't
  include "mobile-").

## Status

| Item | Value |
|------|-------|
| Spec | `specs/TC-CP-001-SPEC.md` |
| Spec version | 0.1.0 |
| Last updated | 2026-05-05 |
| Related Excel row | `02_TestCases::TC-CP-001` |
| Frameworks ready | playwright + cypress (TestCafe gated) |
| OQs blocking | OQ-CP-14 (reCAPTCHA bypass), OQ-CP-15 (tst.* recon for STEPs 6–18 selector exactness, wizard URL pattern) |
