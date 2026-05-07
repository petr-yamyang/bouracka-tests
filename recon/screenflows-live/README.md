# recon/screenflows-live/ — Tier 2 ground truth

> **Tier 2 in the source-of-truth hierarchy** per
> `_specs/DOCUMENTATION-POLICY-v0.1.md` §2. Live screenflow photos
> from `tst.bouracka.cz` and `tst.demo.bouracka.cz` — what the SUT
> *actually* shows today, not what the (now ~10-month-old) analytical
> doc described.
>
> **Trumps Tier 1** (the analytical doc, the draw.io activity
> diagrams). When this folder and a Tier 1 derivative disagree, this
> folder wins; the Tier 1 derivative is updated with a drift footnote.

## Two ingestion patterns (pick by purpose)

This folder hosts **two complementary structures**. CP-SUPIN-04+ uses
both — they answer different questions:

### Pattern A — per-screen `D00..D17/` (state drift)

Use when ingesting **one screen at a time** to record drift vs Tier 1
analytical doc / draw.io. State-by-state edge captures (popup, error
banner, auto-fill render) live here.

```
recon/screenflows-live/
├── _ingest-template.md         ← per-screen template (CP-SUPIN-03 era)
├── DRIFT-LOG.md                ← consolidated drift log
├── D00_homepage-rozcestnik/
│   ├── IMG_NNNN_main.jpg
│   ├── IMG_NNNN_<state>.jpg
│   └── COMPARE.md              ← drift vs Tier 1
├── D01_..D17_*/                ← same structure
```

### Pattern B — per-flow `flow-<ID>-<main|alt>-<env>/` (end-to-end)

Use when ingesting a **full main or alternate flow** for VUP/UML
bottom-up reconstruction (CP-SUPIN-04 L-WORK-1..7). One folder per
flow per environment; holds the photo *sequence*, snippets, and the
3 UML diagrams (Use Case → Activity → Sequence).

```
recon/screenflows-live/
├── _flow-template.md           ← per-flow template (CP-SUPIN-04 era)
├── flow-A1-main-tst/
│   ├── flow.md                 ← copy of _flow-template.md, filled in
│   ├── photos/                 ← IMG_NNNN.jpg, ordered 01..NN
│   ├── snippets/               ← snippet-01-*.md (per L-WORK-4)
│   └── uml/
│       ├── use-case.puml + .png + .svg
│       ├── activity.puml  + .png + .svg
│       └── sequence.puml  + .png + .svg
├── flow-A1-main-tst-demo/      ← parallel DEMO capture (L-WORK-3)
├── flow-A2-alt-tst/
└── flow-A2-alt-tst-demo/
```

Render UML with `tools/render-uml.ps1 -FlowFolder <path>`.

## How to ingest

### Pattern A (per-screen drift) — operator side

1. Photograph each screen with a steady, parallel-axis hold; one
   photo per state. iPhone HEIC is fine.
2. Drop the photos into a folder (e.g. `analyticke vstupy/screenflows-2026-MM-DD/`).
3. Run `tools/heic-to-jpg.ps1` to produce JPGs.
4. Move JPGs into the appropriate per-screen subfolder
   (e.g. `D00_homepage-rozcestnik/`).
5. Open `_ingest-template.md`, copy into a new `COMPARE.md` in the
   per-screen folder, fill in the drift table.
6. Append a row to `DRIFT-LOG.md`.

### Pattern A — Sonnet/Opus session side

1. Use `Read` on each JPG.
2. Compare against the matching `recon/screens/SCR-NNN.md` and the
   matching activity diagram in
   `recon/diagrams/extracted/ACTIVITY-DIAGRAMS-v0.1.md`.
3. Author the per-screen `COMPARE.md` automatically.
4. If drift surfaces, edit:
   - The relevant `recon/screens/SCR-NNN.md` (add a "drift 2026-MM-DD"
     section).
   - The relevant activity diagram block (footnote the change in
     Mermaid with a note: `<!-- drift YYYY-MM-DD: was X, now Y -->`).
   - If it affects an R1 TC, edit `02_TestCases::notes` and rev-bump
     the TC SPEC.

### Pattern B (per-flow VUP/UML) — operator side

1. Photograph the **whole flow** end-to-end in one sitting; tap-by-tap.
   One photo per state transition (per L-WORK-2). Don't skip popups
   or validation states — every branch matters.
2. HEIC → JPG via `tools/heic-to-jpg.ps1`.
3. Create `flow-<ID>-<main|alt>-<env>/` (e.g. `flow-A1-main-tst/`).
4. Drop ordered JPGs into `photos/` (rename `IMG_NNNN.jpg` →
   `01-NN-<short-subject>.jpg` so the alphabetical order = flow order).
5. Copy `_flow-template.md` → `flow-<ID>-…/flow.md`; fill in identity
   + photo sequence + actors + step list.
6. Capture each notable test-data observation with a snippet from
   `recon/test-data-snippets/_snippet-template.md` into
   `flow-<ID>-…/snippets/snippet-NN-<subject>.md` (per L-WORK-4).
7. Author 3 UML files in `flow-<ID>-…/uml/` from the templates in
   `recon/uml-templates/` (Use Case → Activity → Sequence per L-WORK-5).
8. Render: `tools\render-uml.ps1 -FlowFolder recon\screenflows-live\flow-<ID>-…`.
9. Repeat steps 1-8 in parallel for the DEMO sibling
   (`flow-<ID>-…-tst-demo/`) — L-WORK-3.

### Pattern B — Sonnet/Opus session side

1. `Read` each photo in `photos/` in alphabetical order.
2. Fill `flow.md` step list one row per state transition.
3. Cite the source photo on every UML element (per L-WORK-6) — comment
   in `.puml` or note in activity-step description.
4. Cross-env divergence → snippet's `## Cross-env divergence` block.
5. Promote stable snippets into `02b_TC_Parameters` / Mockoon /
   `fixtures/codelists.yaml` per the snippets README.

## Confidentiality posture

Per scope §7 — **screenflow material from tst.* IS confidential**:
- These folders are gitignored (entries already in `bouracka-tests/.gitignore`
  under `recon/screenflows-live/*` patterns).
- The CONSOLIDATED drift log + per-screen COMPARE.md is OK to commit
  if it contains no secret content (no real test phone numbers,
  no real OP numbers, no real personal names).
- Photos themselves stay local — never committed.

## What's expected on first ingestion

### Pattern A baseline (CP-SUPIN-03 carry-over)

State-drift coverage at minimum:
- D00, D01, D02 (gateway + auth — R1-A1 + R1-A2)
- D03, D04, D05, D06 (driver data load — R1-B)
- D08, D09 (vehicle data load — R1-C, vehicle A only is sufficient)
- D12, D13, D14, D15 (circumstances + summary — R1-D)
- D16, D17 (sign + complete — R1-D end)

That's 14 screens × ~3 states each ≈ 40 photos.

### Pattern B baseline (CP-SUPIN-04 main+alt × tst+demo)

The minimum useful matrix for VUP/UML reconstruction is **4 flow
folders**, in priority order:

1. `flow-A1-main-tst/` — main happy path on tst (most-trafficked TT).
2. `flow-A1-main-tst-demo/` — same flow on DEMO; cross-env diff.
3. `flow-A2-alt-tst/` — at least one alternate (e.g. PING-NOK retry,
   or AISPOV degraded → manual entry, or single-driver-cancel).
4. `flow-A2-alt-tst-demo/` — DEMO sibling.

Per L-WORK-3: don't ingest the DEMO folder a week later. Same-day
parallel capture only.

## Status

| Item | Value |
|------|-------|
| Folder | `recon/screenflows-live/` |
| Tier | 2 (live screenflow ground truth) |
| Pattern A subfolders | 18 (D00..D17), 0 photos populated |
| Pattern B subfolders | 0 (awaiting first flow ingestion) |
| Templates | `_ingest-template.md` (A), `_flow-template.md` (B) |
| Status | v0.2 scaffold — Pattern B added for CP-SUPIN-04 |
