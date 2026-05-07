# TestCase Spec Format — v0.1

> **Purpose.** Lock the document format that every TestCase MUST satisfy
> so that a Sonnet (or any agent) automated dev session can pick up one
> spec file and emit framework code (Playwright / Cypress / TestCafe)
> directly — without iterative clarification, without inventing
> selectors, without inferring expected values.
>
> **Audience.** TC authors (Petr; recon-template parsers; future
> ThinkPad task-force sessions) + dev-session readers (Sonnet emitting
> code; reviewers).
>
> **Why this exists.** The CLIENT-PILOT-SUPIN scope §5.1 + §5.2 define
> the *catalogue* shape (Excel `02_TestCases` row); that's enough for
> registry/reporting purposes but **not enough to drive code
> generation**. Per user direction 2026-05-05 (refinement request),
> automated dev sessions need each TC delivered as a self-sufficient
> document.

---

## §1. Where TC specs live

```
bouracka-tests/
├── BOURACKA-TESTPLAN-v0.1.xlsx                (the catalogue;
│   └── sheet 02_TestCases                      one row per TC; the
│       └── column dev_spec_path                row's `dev_spec_path`
│                                               column points here:)
└── specs/
    ├── TC-CP-001-SPEC.md                      (one MD per TC)
    ├── TC-CP-002-SPEC.md
    ├── TC-CP-003-SPEC.md
    ├── TC-CP-004-SPEC.md
    └── _TC-TEMPLATE.md                         (the empty form;
                                                 copy + fill)
```

Excel row = **summary**. MD spec = **dev-session input**. Both versioned
together; row `version_field` matches MD `version` block.

## §2. Required document structure

Every spec MD has these sections in order. Missing any → spec is
**incomplete** and may not be passed to a dev session.

```
1. Header (title + identifiers)
2. Status block
3. Reference index (TT, FLW, INT, SCR, KB, DIV)
4. Pre-conditions (boolean-evaluable + setup steps)
5. Test data (typed fixture refs)
6. Integration touchpoints (mock/stub posture per env)
7. Step list (typed per R-CAST-2; selectors + inputs + expected)
8. Post-conditions (assertions + cleanup)
9. Acceptance criteria (atomic boolean checks)
10. Env divergences (TEST ↔ DEMO behaviour deltas)
11. Viewport applicability (mobile-first per AMENDMENT 2)
12. Failure-mode coupling (R-FAIL-1 link to paired TC or sub-cases)
13. Code-emission hints (deliberate guidance for the dev session)
14. Status footer
```

## §3. Section-by-section contract

### §3.1 Header

```markdown
# TC-CP-NNN — Title (CS) / Title (EN)

> One-line abstract (≤ 25 words).
```

Identifier conventions: `TC-CP-NNN` (Czech-Pilot prefix; zero-padded;
canonical in Excel `item_code`).

### §3.2 Status block

```yaml
spec_version: 0.1.0
spec_status: draft | ready | active | deprecated | blocked
maps_to_test_target: TT-CP-RN-MMM[, TT-CP-RN-MMM]
release: R1 | R2 | R3+
type: happy | failure | regression | smoke
priority: A | B | C | D     # computed from sev × urg matrix
maps_to_flow: FLW-NNN[, FLW-NNN]    # from recon/flows/
maps_to_integrations: INT-NNN[, INT-NNN]    # from recon/integrations/
framework_targets:
  - playwright
  - cypress
  - testcafe   # (drop per Gate 1)
last_updated: YYYY-MM-DD
last_updated_by: <session-or-author>
```

### §3.3 Reference index

Pointer-only block. Referenced documents MUST exist in the workspace.

```markdown
## Reference index

- TestTarget(s):  TT-CP-R1-001 (recon/TEST-TARGET-CANDIDATES.md §1)
- Flow:           FLW-003 (recon/flows/FLW-003.md)
- Integrations:   INT-004 (recon/integrations/INT-004.md)
- Screens:        SCR-002 (recon/screens/SCR-002.md)
- Known issues:   none | KB-CP-NNN
- Divergences:    none | DIV-NNN
- Env config:     env/tst.json, env/tst-demo.json
```

### §3.4 Pre-conditions

Boolean-evaluable conditions + setup steps. The dev session emits the
setup as `beforeAll` / `beforeEach` / fixture loaders.

```markdown
## Pre-conditions

### Boolean conditions

- [PRE-1] env reachable (env.base_url returns 2xx on `/`).
- [PRE-2] `env/<env>.json::recaptcha_bypass_token` is a non-empty string
         (per OQ-CP-14 resolution).
- [PRE-3] `fixtures/shared/test-drivers.json` contains `TD-CP-002` row
         with id_number matching the canonical "Tester Jeden" profile.

### Setup steps

1. Spin a fresh browser context with locale `cs-CZ`, timezone
   `Europe/Prague`, viewport per project.
2. Clear cookies for the SUT origin.
3. Set the reCAPTCHA bypass token cookie if env is `tst` or `tst-demo`.
4. Pre-warm the registry stub by issuing a `GET <env.registry_stub_url>
   /healthz` (assert 200) — fail fast if the stub is down.
```

### §3.5 Test data

Each fixture entry references an Excel `03_TestData` row by
`item_code`; the spec NEVER inlines test data values literally
(prevents drift between Excel and MD).

```markdown
## Test data

| Slot | Fixture ref | Notes |
|------|-------------|-------|
| primary_driver_id | TD-CP-002 (`fixtures/shared/test-drivers.json::tester_jeden`) | OP/ŘP-valid; auto-fill happy |
| primary_vehicle_spz | TD-CP-003 (`fixtures/shared/test-vehicles.json::1ZZ_0001`) | SPZ in registry stub |
| invalid_id | TD-CP-001 (`fixtures/invalid-login.json::wrong_id`) | 404 from registry |
```

### §3.6 Integration touchpoints

For each integration the spec exercises, the **mode** per env must be
declared. The dev session uses this to wire mocks / spies.

```markdown
## Integration touchpoints

| Integration | Env: tst | Env: tst-demo | Test posture |
|-------------|----------|---------------|--------------|
| INT-001 reCAPTCHA | bypass_token | bypass_token_or_disabled | env-config carries the token |
| INT-004 registry | real-stub | real-stub-or-skipped | intercept POST `/api/registry/*` (assert call count = expected); read response for the auto-fill assertion |
```

`Test posture` choices: `passthrough`, `intercept-assert`,
`mock-respond`, `stub-mode`, `skip`.

### §3.7 Step list — the heart of the spec

This is the dev-session-emit-driver. Every step typed per R-CAST-2 with
all data needed to emit framework code.

Step record format (one block per step):

```markdown
### STEP <N>

```yaml
id: TC-CP-NNN-S-<NN>
kind: trigger_point | data_collection_point | control_point | assertion
title_cs: krátký český popis
title_en: short English description
selector: |
  <selector expression OR ref into env/<env>.json::selectors.<key>>
  Example:
  - role-based: getByRole('button', { name: /VYPLNIT ZÁZNAM/i })
  - css: '.grecaptcha-badge'
  - env-ref: env.selectors.primary_cta
input: |
  <literal | fixture-ref | none>
  Example: TD-CP-002.id_number
expected: |
  <literal value | regex | boolean assertion>
  Example: regex /Bouračka/   |   url matches /\\/formular(\\?.*)?$/
viewport_applicability: all | desktop-only | mobile-only | [320, 375, 414]
env_divergence:
  tst: <override or "same as default">
  tst-demo: <override or "same as default">
integration_touchpoint: none | INT-NNN[<mode>]
recovery: none | retry-up-to-N | manual-fallback
notes: |
  free-form notes — gotchas, ambiguity flags
```
```

### §3.8 Post-conditions

```markdown
## Post-conditions

- [POST-1] No record persisted (this is a non-submitting TC).
- [POST-2] No emails dispatched (poll SMTP hook for 0 messages).
- [POST-3] Browser context closed; no localStorage persisted across
          this TC.
```

### §3.9 Acceptance criteria

Atomic, testable, traceable. Each AC maps to ≥ 1 step's assertion.

```markdown
## Acceptance criteria

- [AC-1] Page title at end of STEP 2 matches /Bouračka/.
- [AC-2] Primary CTA at STEP 4 is visible AND its ancestor anchor href
        matches /\\/formular/.
- [AC-3] Mobile-only — at viewports 320 / 375 / 414, the CTA touch-target
        bounding box has both width ≥ 44 px and height ≥ 44 px.
- [AC-4] After CTA click (STEP 6), the URL matches
        /\\/formular(\\?.*)?$/ within 5 seconds.
```

### §3.10 Env divergences

Aggregate view of the per-step env_divergence blocks for at-a-glance
review.

```markdown
## Env divergences

| Step | TST behaviour | DEMO behaviour |
|------|---------------|----------------|
| STEP 9 (reCAPTCHA assert) | badge present | badge may be absent (per OQ-CP-14) |
| STEP 12 (validation msg) | strict CS regex | relaxed (accept any non-empty) |
```

### §3.11 Viewport applicability

```markdown
## Viewport applicability

| Viewport | Run? | Skipped steps |
|----------|------|---------------|
| desktop (1280×720) | YES | none |
| mobile-320 (320×568) | YES | STEP 5 (touch-target N/A on tiny widths if ambient text overflow expected) |
| mobile-375 (375×667) | YES | none |
| mobile-414 (414×896) | YES | none |
```

### §3.12 Failure-mode coupling (R-FAIL-1)

```markdown
## Failure-mode coupling

This spec is a **happy / failure / regression / smoke** TC.

- Pairs with: TC-CP-NNN (the failure pair) — see specs/TC-CP-NNN-SPEC.md.
- Or: this spec IS the failure pair for TC-CP-MMM.
- Or: this spec is `smoke` and pairs with itself per R-FAIL-1 §4.3.
```

### §3.13 Code-emission hints

Deliberate guidance for the Sonnet dev session — what to do, what NOT
to do.

```markdown
## Code-emission hints

- Page-Object Model: extend the existing
  `playwright/pages/WizardGatewayPage.ts` rather than inlining selectors
  in the spec file.
- Cypress: use `cy.viewportPreset()` from `support/e2e.ts` for the
  viewport sweep.
- Do NOT emit `cy.wait(N)`; use `cy.get(...).should('be.visible')` or
  intercept-aware waiting.
- Do NOT emit hard-coded URLs; always go through `baseUrl` (Cypress) or
  the project's `use.baseURL` (Playwright).
- For env divergence: check `env.label` (e.g. `'tst-demo'`) and branch
  with explicit comments tagging which divergence is being honoured.
- Each generated test name MUST start with `TC-CP-NNN — ` so the
  Excel reporter can extract the TC ref.
```

### §3.14 Status footer

```markdown
## Status

| Item | Value |
|------|-------|
| Spec | `specs/TC-CP-NNN-SPEC.md` |
| Spec version | 0.1.0 |
| Last updated | YYYY-MM-DD by <session-id> |
| Related Excel row | `02_TestCases::TC-CP-NNN` |
| Frameworks ready | playwright | cypress | testcafe |
| OQs blocking | OQ-CP-NN[, ...] |
```

## §4. Step-kind decision tree (R-CAST-2)

When unsure which kind to assign, follow this tree:

```
Does the step fire an action OR cause something to start?
    YES → trigger_point
    NO  → continues...
Does the step BRANCH the flow (if/else, switch on response)?
    YES → control_point
    NO  → continues...
Does the step READ state (DOM, network capture, log) WITHOUT asserting on it?
    YES → data_collection_point
    NO  → continues...
Does the step ASSERT expected vs. actual?
    YES → assertion
```

Steps that combine read+assert SHOULD be split into two records (one
data_collection_point + one assertion) so the framework code can fail
the assertion without losing the captured value for diagnostics.

## §5. Selector hierarchy (binding)

Preferred → fallback chain (per W3C ARIA + Playwright/Cypress
recommendations):

```
1. role-based (Playwright getByRole / Cypress findByRole)
2. accessible-name / label (getByLabel, getByText with exact match)
3. test-id (data-testid, data-test, data-qa) — when SUT exposes them
4. id (#login-email)
5. class — only when the class is a stable contract (e.g. .grecaptcha-badge)
6. xpath — last resort; comment WHY no other option works
```

Each step's `selector` field MUST include a comment when descending
below level 4.

## §6. Env-divergence handling (binding)

Three patterns, in order of preference:

1. **Same scenario, different expected per env.** Default. Express via
   `env_divergence` per step.
2. **Different scenario per env.** Split into TC-CP-NNN-A (TST) +
   TC-CP-NNN-B (DEMO). Both reference same TT.
3. **Skip on one env.** Mark per-step
   `env_divergence.<env>: SKIP — <reason>`.

The dev session translates these to:
- (1) → in-test branch on `env.label`
- (2) → two test files
- (3) → `test.skip()` / `it.skip()` with reason

## §7. Validation checklist (apply before passing spec to dev session)

- [ ] All 14 sections present.
- [ ] Status block fields all populated (no `TBD` in `spec_status`).
- [ ] Reference index — every reference resolves to a real file.
- [ ] Pre-conditions — every PRE-N is boolean-evaluable.
- [ ] Test data — every fixture-ref is a real `03_TestData::item_code`.
- [ ] Integrations — `Test posture` for every entry is one of the
      enumerated values.
- [ ] Step list — every step typed per R-CAST-2; selector field
      non-empty; expected non-empty (or "n/a" for trigger_points
      that don't return a value).
- [ ] Post-conditions populated (even if just "no state change").
- [ ] Acceptance criteria — every AC traces to ≥ 1 step.
- [ ] Env divergences — every per-step divergence reflected here.
- [ ] Viewport applicability — explicit per-viewport YES/NO + skipped
      steps.
- [ ] R-FAIL-1 — pair declared.
- [ ] Code-emission hints present.
- [ ] Status footer dated + signed.

## §8. The "lightweight" recon → spec pipeline

Inputs from a colleague filling the lightweight recon template
(`CLIENT-PILOT-SUPIN-RECON-TEMPLATES-LIGHT-V0.1.md`) MUST go through a
**parser + enrichment** step before they can be promoted to a TC spec
in this format:

```
[colleague light template] → parse-light-template.py → [draft TC spec]
                          → human review (Petr) → [enrich missing fields]
                          → spec lint (§7 checklist) → [READY for dev session]
```

The light-template parser lives in `tools/recon-parser/` (per
`CLIENT-PILOT-SUPIN-FUTURE-REPO-STRUCTURE-V0.1.md` §3 plan) — to be
authored in CP-SUPIN-03+.

## §9. Status

| Item | Value |
|------|-------|
| Document | `_specs/TESTCASE-SPEC-FORMAT-v0.1.md` |
| Version | v0.1.0 |
| Trigger | User direction 2026-05-05 (refinement request) |
| Required by | every TC in `bouracka-tests/specs/` |
| First adopters | TC-CP-001..004 (this iteration) |
| Status | v0.1 — binding for all TC specs from now |
