# Screenflow Drift Log

> Append-only log of drift between Tier 1 (analytical doc) and Tier 2
> (live screenflow photos). Newest entries on top. One row per drift
> finding.

## How to add an entry

When a per-screen `COMPARE.md` surfaces drift, copy a row here:

```yaml
- entry_id: DR-NNN
  date: YYYY-MM-DD
  screen: D<NN>_<screen>
  element: <e.g. "primary CTA label", "validation msg regex">
  tier_1: "<old>"
  tier_2: "<new from live>"
  source_photos: ["IMG_NNNN_main.jpg", "IMG_NNNN_state2.jpg"]
  affected_artefacts:
    - recon/screens/SCR-NNN.md
    - recon/diagrams/extracted/ACTIVITY-DIAGRAMS-v0.1.md (D<NN>)
    - 02_TestCases::TC-CP-NNN
  resolution: <free text — what we changed in response>
  status: open | resolved | wont-fix
```

## Entries

(no entries yet — populates on first batch of screenflow photos)
