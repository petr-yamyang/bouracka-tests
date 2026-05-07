# Flow Reconstruction — flow-<ID>-<env>

> Template — copy into `recon/screenflows-live/flow-<ID>-<env>/FLOW.md`
> and fill from the photo sequence in `./photos/`.
>
> **Difference from `_ingest-template.md`:** this template captures a
> SEQUENCE of screens (a flow), not one screen at a time.
> Per CP-SUPIN-04 L-WORK-1.

## §1. Identity

```yaml
flow_id: flow-<A1|B|C|D|…>-<main|alt-<reason>>-<tst|tst-demo>
flow_name_cs: <e.g. "Vstup + SMS-PING happy">
flow_name_en: <e.g. "Entry + SMS-PING happy path">
classification: main | alternate-failure | alternate-edge | regression
parent_main_flow_id: <when classification != main; ref to its main flow>
captured_at: YYYY-MM-DD HH:MM
captured_on_env: tst | tst-demo
captured_by: <Petr | colleague-name>
photo_count: <N>
ingested_at: YYYY-MM-DD
ingested_by: <session-id>
```

## §2. Photo sequence (the evidence)

| # | Photo | What's on screen | State transition? |
|---|-------|------------------|-------------------|
| 01 | `photos/IMG_NNNN.jpg` | (1-line description) | NEW → IN_PROGRESS_DRIVERS, etc. |
| 02 | `photos/IMG_NNNN.jpg` | … | … |
| 03 | … | … | … |

Sequence the photos in chronological order of the user's interaction.
Mark transition pairs (before-click + after-navigation).

## §3. Actors + integrations involved

```yaml
actors:
  - id: U1
    name: Účastník (driver A)
    role: primary-driver
  - id: U2
    name: Účastník (driver N)
    role: secondary-driver
  - id: SYS
    name: SUT — Bouračka
    role: system

integrations_invoked:
  - INT-002 N8 SMS Gateway      # PING + SEND_OTP
  - INT-001 reCAPTCHA           # bot-defence on phone-input
```

## §4. Step list (with photo refs as evidence)

For each step:

```yaml
- step: 01
  kind: trigger | data_collection | control | assertion
  actor: U1 | SYS | INT-NNN
  action_cs: <co se stalo>
  evidence_photo: photos/IMG_NNNN.jpg
  evidence_zoom: <e.g. "top-half">
  expected_result_cs: <co očekáváme>
  observed_result_cs: <co skutečně viděno>
  drift_vs_analytical_doc: <yes/no — if yes, log in DRIFT-LOG.md>
```

(One bullet per step; numbered 01..NN.)

## §5. Branches (alternate paths within this flow)

If this is a MAIN flow with internal branches (decisions), list them:

```yaml
branches:
  - branch_id: B1
    decision_step: <step NN>
    guard_cs: "Číslo OK?"
    happy_target: step NN+1 (this flow)
    alternate_target: alternate flow flow-<ID>-alt-<reason>-<env>
```

If this IS an alternate flow, link back to the main:

```yaml
parent: flow-<ID>-main-<env>
diverged_at_main_step: NN
return_to_main: <step | terminal>
```

## §6. Cross-env reference (Bouračka ↔ DEMO Bouračka)

```yaml
sibling_env_flow: flow-<ID>-<main|alt>-<other-env>
drift_summary:
  - DEMO: <difference>
  - DEMO: <difference>
```

(Filled after both env flows are captured.)

## §7. UML reconstruction targets

Three diagrams to author from this flow (see
`recon/uml-templates/`):

- `use-case.puml` — actor + use case relationships
- `activity.puml` — swim-lane activity diagram
- `sequence.puml` — sequence with messages

Render via `tools/render-uml.ps1`.

## §8. Mapping to TT/TC

```yaml
maps_to_test_target: TT-CP-R1-<X>
covered_by_tc:
  - TC-CP-NNN  # primary
  - TC-CP-NNN  # alternate (if applicable)
```

If no TC exists yet for this flow → propose one in §9.

## §9. New TC candidate (if surfaced by this flow)

(Only fill if the flow exposes a branch / behaviour not yet covered.)

```yaml
proposed_tc:
  code: TC-CP-<NNN>
  title_cs: …
  type: happy | failure | regression | smoke
  priority_proposal: A | B | C | D
  state_machine_terminal_state: <NEW|IN_PROGRESS_*|TO_SIGN|FINISHED|ERROR>
  rationale_cs: <why this needs its own TC>
```

## §10. Status

| Item | Value |
|------|-------|
| FLOW.md | `recon/screenflows-live/flow-<ID>-<env>/FLOW.md` |
| Photo count | <N> |
| UML diagrams | <none|partial|complete> |
| Cross-env sibling | <captured | pending | n/a> |
| Drift entries | <count in DRIFT-LOG.md> |
| Status | <draft | reviewed | approved-for-TC-refinement> |
