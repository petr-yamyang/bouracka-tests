# Drift Comparison — D<NN>_<screen-name> — Tier 1 vs Tier 2

> Template — copy into `D<NN>_<screen-name>/COMPARE.md` and fill in.
> See `recon/screenflows-live/README.md` for the workflow.

## Metadata

```yaml
screen_id: D<NN>
screen_name_cs: <Czech name verbatim from photo header>
photographed_at: YYYY-MM-DD
photographed_on_env: tst | tst-demo | both
photographer: <colleague-name>
photo_count: <N>
ingested_at: YYYY-MM-DD
ingested_by: <session-id>
```

## Photos in this folder

| File | State captured | Notes |
|------|----------------|-------|
| `IMG_NNNN_main.jpg` | default-state | initial render |
| `IMG_NNNN_<state>.jpg` | <e.g. popup-open / error-shown / auto-fill> | <free text> |

## Drift table — Tier 1 (analytical doc) vs Tier 2 (live)

| Element | Tier 1 says | Tier 2 says | Drift? | Action |
|---------|-------------|-------------|:------:|--------|
| Page H1 text | (from analytical doc / SCR-NNN) | (from photo) | ✓/✗ | none / edit SCR-NNN |
| Primary CTA label | … | … | ✓/✗ | … |
| Decision branches present (count) | … | … | ✓/✗ | … |
| Decision branch CS labels | … | … | ✓/✗ | … |
| Validation messages CS regex | … | … | ✓/✗ | … |
| Field labels | … | … | ✓/✗ | … |
| New field NOT in Tier 1 | n/a | (new field) | ✓ | add F-NNN to field-definitions.yaml |
| Field present in Tier 1 but NOT live | (field) | n/a | ✓ | mark deprecated in field-definitions |
| Outage banner state | … | … | ✓/✗ | … |
| Mobile viewport rendering | inferred | observed | ✓/✗ | … |
| Integration touchpoint observable (network panel if available) | (per analytical doc) | (per devtools) | ✓/✗ | … |

## Open questions raised by this comparison

```yaml
- oq_id: OQ-DRIFT-NN
  question: …
  raised_at: YYYY-MM-DD
  blocking: <which TC SPEC, if any>
```

## Free-form observations

- (anything that doesn't fit the table)

## Status

| Item | Value |
|------|-------|
| Drift entries | <N> |
| Drift-affected TC SPECs | <list> |
| Drift-affected SCR recons | <list> |
| Status | v0.1 |
