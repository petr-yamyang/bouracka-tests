# TestTargetList Format — v0.2

> **What changed since v0.1.** Per CP-SUPIN-03 (synchro §10 STEP 3.1 +
> Opus review G2+G7+§7) — TT now carries:
>
> - **`furps_dimensions`** (R-FURPS-1) — comma-list F,U,R,P,S,+D,+I,+N,+L,+P_phys
> - **CO/KDO/KDY/KDE/JAK** decomposition (CAST 5W) — five Czech
>   question-words mapping to what / who / when / where / how
> - **`source_artefact_*`** quartet (R-DERIVE-1):
>   `source_artefact_kind`, `source_artefact_ref`, `derivation_rule`,
>   `source_artefact_author_role`
> - **`requirement_ref`** — every TT links to ≥ 1 REQ-CP-NNN in
>   `00b_Requirements`

---

## §1. Updated required fields (v0.2 superset of v0.1 §3)

```yaml
# v0.1 ItemBase block (unchanged)
id, item_code, item_name_cs, item_name_en, item_descr_cs,
item_descr_en, item_type=test_target, item_status, severity,
urgency, priority, submitter, submit_date

# v0.1 R-CAST-1 fields (unchanged)
decomposition_kind, component_ref, behaviour_ref, coverage_basis

# v0.1 release + linkage (unchanged)
release, env_coverage, state_machine_terminal_state,
related_screen_refs, related_flow_refs, related_integration_refs

# NEW v0.2 fields (R-FURPS-1, R-DERIVE-1, CAST 5W)
furps_dimensions               # list e.g. [F, R]
co_what                        # CAST 5W: WHAT is being tested
kdo_who                        # WHO triggers / observes
kdy_when                       # WHEN in the flow
kde_where                      # WHERE in the SUT (screen / area)
jak_how                        # HOW (manual / auto / mixed)
source_artefact_kind           # analytical_doc | activity_diagram |
                               # state_machine | user_direction |
                               # field_definitions | regulation
source_artefact_ref            # specific identifier (page, diagram id)
derivation_rule                # how this TT derives from the source
source_artefact_author_role    # SUPIN | ČKP | Petr | colleague | vendor
requirement_ref                # REQ-CP-NNN — points into 00b_Requirements
```

### §1.1 CO/KDO/KDY/KDE/JAK — what each Czech question-word means

The 5W decomposition — borrowed from CAST analytical practice — gives
each TT a five-axis description that surfaces dimensional gaps before
TC authoring begins.

| Czech | English | Example for TT-CP-R1-A1 (PING gate) |
|-------|---------|--------------------------------------|
| CO | what | "PING request to N8 SMS Gateway endpoint" |
| KDO | who | "SUT (back-end) on user-action 'pokračovat' from screen 01" |
| KDY | when | "before first transition out of NEW state" |
| KDE | where | "wizard gateway D00→D02 boundary" |
| JAK | how | "auto (intercept-assert in tests; Mockoon stub by default)" |

If you can't fill all five, the TT scope is probably under-defined.

---

## §2. R-DERIVE-1 — provenance is mandatory

Every TT MUST cite its source artefact. Choose `source_artefact_kind`
from the enum:

| Kind | When to use | Example ref |
|------|-------------|-------------|
| `analytical_doc` | TT comes from the ČKP/SUPIN analytical doc | `p27/133 §3.1` |
| `activity_diagram` | from D00..D17 swimlane | `D08 swap branch` |
| `state_machine` | from `accidentReportStatus` transitions | `IN_PROGRESS_DRIVERS → IN_PROGRESS_VEHICLES` |
| `user_direction` | from operator decision | `OQ-CP-12 closure 2026-05-05` |
| `field_definitions` | from `fixtures/field-definitions.yaml` | `F-104, F-108` |
| `regulation` | from law / standard / industry rule | `WCAG 2.2 AA target-size` |
| `vendor_doc` | from third-party vendor (zenID, N8) | `(when contracts arrive)` |

`derivation_rule` describes the *reasoning chain* — e.g.
*"D08 SPZ confirm popup is irreversible per analytical doc; therefore
TT covers re-upload-blocked behaviour as part of TT-CP-R1-C scope"*.

---

## §3. R-FURPS-1 + CARTESIAN

Every TT carries `furps_dimensions` — the *dimensions of quality*
this TT exercises. The Cartesian sheet `01b_Req_FURPS_Cartesian`
ensures coverage across all 10 dimensions per requirement:
- TT inherits its FURPS+ from the linked REQ
- when expanding from a Cartesian cell to a TT-set, the cell's
  `cell_status='active'` requires at least one TT exists
- `cell_status='na'` requires `na_justification` (validator-enforced)

---

## §4. Validation checklist (v0.2 — supersedes v0.1 §6)

In addition to the v0.1 checks:

- [ ] `furps_dimensions` populated with at least one valid value
- [ ] `co_what`, `kdo_who`, `kdy_when`, `kde_where`, `jak_how` all
      populated (not blank)
- [ ] `source_artefact_kind` from the enum
- [ ] `source_artefact_ref` non-blank
- [ ] `derivation_rule` is 1-3 sentences (not "TBD")
- [ ] `requirement_ref` resolves to existing `00b_Requirements::item_code`

The `tools/validate-workbook.py` script (CP-SUPIN-03 STEP 5) enforces
these.

---

## §5. Status

| Item | Value |
|------|-------|
| Document | `_specs/TESTTARGET-LIST-FORMAT-v0.2.md` |
| Supersedes | `_specs/TESTTARGET-LIST-FORMAT-v0.1.md` |
| Trigger | CP-SUPIN-03 (synchro 2026-05-06 + Opus review G2+G7) |
| New required columns | 11 (added to `01_TestTargets` by `rev7_xlsx_v02_migration.py`) |
| Status | v0.2 — binding for all TT entries from CP-SUPIN-03 onward |
