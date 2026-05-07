# TestCase Spec Format — v0.2

> **What changed since v0.1.** Per CP-SUPIN-03 (synchro
> 2026-05-06 §10 STEP 3.2 + Opus review §6.1+§6.2+§7) — five-rule
> upgrade:
>
> - **R-FURPS-1** — every TC carries `furps_dimensions`.
> - **R-CONTRACT-1** — workbook IS the live execution contract;
>   parameters resolved from `02b_TC_Parameters`; assertions resolved
>   from `02c_TC_Assertions × 02d_AssertionLibrary`. SPEC.md is the
>   human companion, NOT the source of truth for execution.
> - **R-DERIVE-1** — TC inherits `requirement_ref` from its TT.
> - **R-EXPAND-1** — TC origin from FURPS+ Cartesian cell carries
>   sev+urg tags via `01b`.
> - **R-PLAN-2** — TC `scheduling_unit_kind` matches project
>   methodology.
>
> v0.1 specs remain valid as human companions; their step lists are
> bootstrap material for the runtime spec-loader.

---

## §1. Two-tier authoring model (NEW v0.2)

```
       ┌────────────────────────────────────────────────────────┐
       │ TIER A — workbook (live execution contract per R-CONTRACT-1)│
       │   02_TestCases    : the TC roster                          │
       │   02b_TC_Parameters: typed parameters per TC               │
       │   02c_TC_Assertions: per-step assertion-library refs       │
       │   02d_AssertionLibrary: reusable patterns w/ snippets     │
       └──────────────────────────┬─────────────────────────────┘
                                  │ resolved at runtime by
                                  │ playwright/runtime/spec-loader.ts
                                  ▼
       ┌────────────────────────────────────────────────────────┐
       │ TIER B — SPEC.md (human companion + provenance)            │
       │   specs/TC-CP-NNN-SPEC.md per v0.1 14-section format       │
       │   - human-readable narrative                               │
       │   - acceptance criteria in prose                           │
       │   - code-emission hints                                    │
       │   - now ALSO: explicit pointers into 02b/02c/02d rows      │
       └────────────────────────────────────────────────────────┘
```

**Authoring workflow:**
1. Write the SPEC.md (Tier B) — narrative-first, human-reviewable.
2. Extract typed params into `02b_TC_Parameters` (Tier A).
3. Map each step's assertion to a `02d_AssertionLibrary` row via
   `02c_TC_Assertions` (Tier A).
4. The runtime spec-loader builds the executable from Tier A;
   Tier B remains as documentation.

---

## §2. NEW required fields in v0.2

### §2.1 Status block

```yaml
spec_version: 0.2.0                             # bumped
spec_status: draft | ready | active | deprecated | blocked
maps_to_test_target: TT-CP-RN-MMM
release: R1 | R2 | R3+
type: happy | failure | regression | smoke
priority: A | B | C | D
furps_dimensions: [F, U, R, P, S]               # NEW v0.2 (R-FURPS-1)
requirement_ref: REQ-CP-NNN                     # NEW v0.2 (R-DERIVE-1; via TT)
impulse_ref: <activity-step-id> | <bug-id>      # NEW v0.2 (R-IMPULSE-1)
diligence: smoke | happy | exception | negative | regression | exhaustive  # NEW v0.2
maps_to_flow: FLW-NNN | D<NN>
maps_to_integrations: INT-NNN[, INT-NNN]
framework_targets: [playwright, cypress, testcafe]
parameter_refs: [TC-CP-NNN-P-01, ...]           # NEW v0.2 — points into 02b
assertion_refs: [TC-CP-NNN-S-01, ...]           # NEW v0.2 — points into 02c
last_updated: YYYY-MM-DD
last_updated_by: <session-id>
```

### §2.2 NEW §3.15 — Parameters reference

For every parameter the test uses (URL, viewport, OTP value, fixture),
add a row to `02b_TC_Parameters` and reference it here:

```markdown
## Parameters reference (Tier A)

Resolved at runtime by playwright/runtime/spec-loader.ts from
BOURACKA-TESTPLAN-v0.2.xlsx::02b_TC_Parameters. This SPEC must
not hard-code these values.

| Param ID | Name | Source | Default |
|----------|------|--------|---------|
| TC-CP-001-P-01 | env_url | env-config | https://tst.bouracka.cz |
| TC-CP-001-P-02 | viewport | literal | 375x667 |
| ... | ... | ... | ... |
```

**Source kinds (enum):**
- `literal` — hard-coded string/integer
- `fixture-ref` — path into `fixtures/shared/*.json::key`
- `env-config` — path into `env/{env}.json::key`
- `derived` — computed at runtime from another value
- `from-mock-response` — read from a mock's response (e.g. Mockoon
  returns OTP value the test then uses)

### §2.3 NEW §3.16 — Assertion library references

Each assertion step in the SPEC (R-CAST-2 step with `kind: assertion`)
must be linked to one or more rows in `02c_TC_Assertions`, which in
turn point to a `02d_AssertionLibrary` pattern:

```markdown
## Assertion library refs (Tier A)

Resolved at runtime. Patterns live in 02d_AssertionLibrary; per-step
mappings in 02c_TC_Assertions.

| Step ID | Library code | FURPS+ | Expected (one-line summary) |
|---------|--------------|:------:|------------------------------|
| TC-CP-001-S-04 | LIB-AS-FUNC-002 | F | URL matches /\\/formular(\\?.*)?$/ |
| TC-CP-001-S-09 | LIB-AS-FUNC-002 | F | title matches /Bouračka/i |
| TC-CP-001-S-10 | LIB-AS-USAB-001 | U | touch-target ≥ 44×44 px |
```

The full snippet (Playwright + Cypress) lives in 02d; the SPEC just
records WHICH pattern is invoked at WHICH step.

---

## §3. FURPS+ tagging — guidance

`furps_dimensions` is a list, not a singleton. A TC may exercise:
- **F** functional behaviour (the default for happy/failure TCs)
- **U** usability (touch-target, error-message clarity, navigation)
- **R** reliability (retry, timeout, no-silent-failure)
- **P** performance (response-time threshold)
- **S** supportability (logging, error-codes, i18n)
- **+D** design constraints (architectural — usually covered by REQ
  not TC)
- **+I** implementation constraints (browser version, viewport)
- **+N** interface constraints (API contract)
- **+L** legal/regulatory (GDPR, accessibility law, ČKP regulations)
- **+P_phys** physical (almost always N/A for web SUT)

Most R1 TCs tag at least F. TCs with mobile-specific assertions add U.
TCs that exercise integration retry add R. Etc.

---

## §4. Validation checklist (v0.2 — supersedes v0.1 §7)

In addition to the 14 v0.1 checks:

- [ ] `furps_dimensions` populated with at least one valid value
- [ ] `requirement_ref` resolves to existing row in `00b_Requirements`
- [ ] `impulse_ref` populated (activity step, bug, or
      `cartesian:01b_…cell-id`)
- [ ] `diligence` is one of the enum values
- [ ] Every parameter in the SPEC has a matching `02b_TC_Parameters`
      row
- [ ] Every assertion step has a matching `02c_TC_Assertions` row
      pointing to a real `02d_AssertionLibrary` pattern
- [ ] Spec version is exactly `0.2.0`

The `tools/validate-workbook.py` script (CP-SUPIN-03 STEP 5) runs
these checks across the workbook + all SPECs and exits non-zero on
any failure.

---

## §5. Backward compatibility with v0.1

v0.1 SPECs (TC-CP-001..023) automatically migrate to v0.2 by:
1. Bumping `spec_version: 0.2.0`
2. Adding the new fields per §2.1
3. Authoring the §3.15 + §3.16 sections (extracting params + linking
   assertions to library patterns).

Where the SPEC's existing step assertions don't have a library pattern
yet, the v0.2 migration ADDS the pattern to `02d_AssertionLibrary`
(see how rev7_xlsx_v02_migration.py extracted 10 patterns from the
existing 7 R1 SPECs).

---

## §6. Status

| Item | Value |
|------|-------|
| Document | `_specs/TESTCASE-SPEC-FORMAT-v0.2.md` |
| Supersedes | `_specs/TESTCASE-SPEC-FORMAT-v0.1.md` (kept for reference) |
| Trigger | CP-SUPIN-03 (synchro 2026-05-06 + Opus review §6.1+§6.2+§7) |
| Tier-A spreadsheet | `BOURACKA-TESTPLAN-v0.2.xlsx` (21 sheets) |
| New required fields | `furps_dimensions`, `requirement_ref`, `impulse_ref`, `diligence`, `parameter_refs`, `assertion_refs` |
| New required sections | §3.15 (Parameters), §3.16 (Assertion library refs) |
| Status | v0.2 — binding for all TC specs from CP-SUPIN-03 onward |
