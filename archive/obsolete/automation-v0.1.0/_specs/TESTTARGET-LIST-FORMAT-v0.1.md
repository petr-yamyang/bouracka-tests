# TestTargetList Format — v0.1

> **Purpose.** Lock the format for TestTarget catalogue entries — both
> the narrative (`recon/TEST-TARGET-CANDIDATES.md`) and the tabular
> (`BOURACKA-TESTPLAN-v0.1.xlsx::01_TestTargets`) — so the same row
> can be consumed by humans, by an automated TC-spec generator, and by
> the future MI-M-T DOCK-EXCEL adapter.

---

## §1. Where TT entries live

```
bouracka-tests/
├── recon/
│   └── TEST-TARGET-CANDIDATES.md         ← narrative + R1/R2 partition
└── BOURACKA-TESTPLAN-v0.1.xlsx
    └── 01_TestTargets                     ← tabular row per TT
```

The Excel row is the **canonical record**; the MD narrative is its
human-readable companion. Both must agree on every field listed in §3.

## §2. ID conventions

```
TT-CP-RN-MMM
   │  │   │
   │  │   └─ zero-padded sequence within the release
   │  └────── release number (R1 / R2 / R3+)
   └────────── campaign code (CP = Client-Pilot SUPIN)
```

Examples:
- `TT-CP-R1-001` — first R1 TestTarget.
- `TT-CP-R2-007` — seventh R2-deferred TestTarget.

Once an R2 TT is promoted to R1 in a later iteration, it gets a NEW
R1 ID; the R2 entry is marked `deprecated` per R-STRUCT-1 (no silent
re-numbering).

## §3. Required fields (Excel + MD must both carry)

### §3.1 ItemBase block (per scope §5.2 — first 13 columns)

`id, item_code, item_name_cs, item_name_en, item_descr_cs,
item_descr_en, item_type (= 'test_target'), item_status, severity,
urgency, priority (computed), submitter, submit_date`

### §3.2 R-CAST-1 binding fields

`decomposition_kind`  — one of `page | behaviour | component |
integration | regression | smoke`
`component_ref`       — present iff `decomposition_kind ∈ {component,
page, integration}`; structural unit name (e.g.
`formular-gateway-page`)
`behaviour_ref`       — present iff `decomposition_kind = behaviour`;
verb-phrase identifier (e.g.
`authenticate-user-via-id-registers`)
`coverage_basis`      — 1–3 sentence rationale; the "why this is a
useful TestTarget" — rendered as the `test_targets.item_descr` in MI-M-T

### §3.3 Release + scope fields

`release`             — `R1 | R2 | R3+`
`env_coverage`        — comma-list of env codes from
`04_TestEnvironments::item_code` (e.g. `TST + DMO`)

### §3.4 Linkage fields

`related_screen_refs`        — comma-list of `SCR-NNN`
`related_flow_refs`          — comma-list of `FLW-NNN`
`related_integration_refs`   — comma-list of `INT-NNN`

### §3.5 ItemBase tail

`created_at, updated_at, notes`

## §4. Narrative (MD) section template per TT

```markdown
### TT-CP-RN-MMM — Title (CS) / Title (EN)

```
DECOMPOSITION_KIND: page | behaviour | component | integration | regression | smoke
COMPONENT_REF:      <if applicable>
BEHAVIOUR_REF:      <if applicable>
COVERAGE_BASIS:     1-3 sentence rationale
ENV_COVERAGE:       <env codes>
PRIORITY:           Sev=X / Urg=Y / Pri=Z
RELEASE:            R1 | R2 | R3+
RELATED INTEGRATIONS: INT-NNN[, INT-NNN]
RELATED FLOWS:      FLW-NNN[, FLW-NNN]
RELATED SCREENS:    SCR-NNN[, SCR-NNN]
NOTES:              optional free-form
```
```

## §5. Promotion rules (R2 → R1)

When a TT moves from R2 to R1 in a later iteration:

1. Mark the existing R2 row `item_status: deprecated`; add a notes
   pointer "promoted to TT-CP-R1-MMM in iteration CP-SUPIN-NN".
2. Author a NEW row with R1 prefix (per §2) and `item_status: active`.
3. Author the corresponding TC spec under `specs/`.
4. Update `recon/TEST-TARGET-CANDIDATES.md` §3 with the
   NEW / REPLACED / UNCHANGED block (R-STRUCT-1).
5. Note the promotion in `11_Changelog`.

NEVER: silently re-number; reuse an R2 ID for an R1 row; delete an R2
row before depreciation.

## §6. Validation checklist

- [ ] ID matches `TT-CP-RN-MMM` regex.
- [ ] All ItemBase columns populated.
- [ ] `item_type = 'test_target'`.
- [ ] `decomposition_kind` is from the enumerated set.
- [ ] Exactly one of `component_ref` / `behaviour_ref` populated for
      a `behaviour` kind; either OK for `page` / `integration`; just
      `component_ref` for `component`.
- [ ] `coverage_basis` is 1–3 sentences; not "TBD".
- [ ] Every linked SCR-NNN / FLW-NNN / INT-NNN points to an existing
      file under `recon/`.
- [ ] `env_coverage` references existing rows in
      `04_TestEnvironments`.
- [ ] `release` is one of `R1 / R2 / R3+`.

## §7. Status

| Item | Value |
|------|-------|
| Document | `_specs/TESTTARGET-LIST-FORMAT-v0.1.md` |
| Version | v0.1.0 |
| Trigger | User direction 2026-05-05 (refinement request) |
| Status | v0.1 — binding for all TT entries from now |
