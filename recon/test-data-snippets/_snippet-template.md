# Snippet — <short subject>

> Template — copy into a flow folder's `snippets/` subdirectory and
> fill from a single photo (or zoom region of one).
> Per CP-SUPIN-04 L-WORK-4 + §3 of working lessons.

## Provenance

```yaml
flow: flow-<ID>-<main|alt>-<env>
photo_ref: IMG_NNNN.jpg
photo_zoom: <e.g. "top-right corner" | "full screen" | "popup overlay">
captured_at: YYYY-MM-DD HH:MM
env: tst | tst-demo
captured_by: <Petr | colleague-name>
ingested_at: YYYY-MM-DD
ingested_by: <session-id>
```

## Data captured

```yaml
field_name: <e.g. "tel_cislo_ucastnik_a">
field_kind: phone | op_number | rp_number | spz | otp |
            response_json | validation_message | other
data_source: user-entered | sut-rendered | network-response |
             integration-result
sanitised: yes | no
```

If `sanitised: yes` (data is non-personal / placeholder / public):
```yaml
data_value: <verbatim from photo, OK to commit>
```

If `sanitised: no` (real personal data observed; NEEDS REDACTION):
```yaml
data_redacted: <REDACTED — see `fixtures/secrets/<flow>-<snippet>.json` (gitignored)>
data_pattern: <regex describing the shape, OK to commit, e.g. ^\+420\d{9}$>
```

## What this enables

Pick all that apply:

- [ ] TC fixture row in `02b_TC_Parameters` (specify TC ref)
- [ ] Mockoon scenario response (specify mock route + scenario)
- [ ] AISPOV expected lookup result (specify ROB/CRR/CRV table)
- [ ] N8 SMS Gateway expected behaviour
- [ ] Validation rule confirmation (`fixtures/field-definitions.yaml::F-NNN.rules`)
- [ ] Drift evidence vs analytical doc (specify which page)
- [ ] Other: <free text>

## Cross-env divergence (if observed)

```yaml
tst_value: <as captured>
tst_demo_value: <if known; populate after sibling flow capture>
divergence_kind: identical | format-differs | value-differs | absent-on-one-env
```

## Notes

- (any free-form observation about the data — formatting quirks,
  unexpected fields, error envelopes that surprised the captor)

## Status

| Item | Value |
|------|-------|
| Snippet | `recon/screenflows-live/flow-<ID>-<env>/snippets/snippet-NN-<subject>.md` |
| Sanitised | <yes/no> |
| Cross-env captured | <yes/no/n-a> |
| Linked artefact | <TC code | Mockoon scenario | fixture YAML key | …> |
| Status | <draft | reviewed | committed-to-test-data> |
