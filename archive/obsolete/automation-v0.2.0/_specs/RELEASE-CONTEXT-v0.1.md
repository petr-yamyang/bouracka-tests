# Release Context — Bouračka MVP — v0.1

> Surfaced from `recon/cs-locale-reference/CALIBRATION-CORPUS-v0.1.md`
> §1c.2 — analytical-doc page 14/133 verbatim text.

## Key release facts (binding for the test campaign)

```yaml
mvp_release_date: 2025-07            # July 2025 (analytical doc verbatim)
mvp_scope: 2-driver-workflow         # default; 1-driver and 3+-drivers are R3+ extensibility
analytical_doc_authored: ~2025-mid    # for the July 2025 launch
analytical_doc_age_at_test_campaign: ~9-10 months
sut_baseline: post-launch tst.* (rolling-deployed since 07/2025)
```

## Implications for the test campaign

1. **Tier 2 (live screenflow) trumps Tier 1 (analytical doc).** The
   doc was authored for the launch state; today's tst.* may include
   post-launch refinements (new error sub-reasons, copy-edits, edge
   flows, validation tightening). See `_specs/DOCUMENTATION-POLICY-v0.1.md`
   §2 for drift-handling.

2. **R1 = the released MVP scope** — exactly the 2-driver workflow
   in the field-definitions catalogue (121 fields). R3+ extensibility
   (1-driver / 3+-drivers) is **post-launch enhancement work**, not
   just deferred test scope. This sharpens the R2/R3 distinction
   that was hand-wavy until this fact landed.

3. **Bug-vintage interpretation.** When a tester reports a defect on
   tst.*, "is it in the original MVP scope or post-launch
   extensibility?" becomes a clearer question. Anything outside the
   2-driver workflow is by definition not an MVP-scope regression.

4. **Field-definitions stability.** The 121-field catalogue
   (`fixtures/field-definitions.yaml`) is canonical for the MVP.
   New fields surfacing in live screenflow recon ⇒ they're R3+
   extensibility additions; older fields disappearing ⇒ deprecation
   to investigate.

## Status footer

| Item | Value |
|------|-------|
| Document | `_specs/RELEASE-CONTEXT-v0.1.md` |
| Source | analytical doc page 14/133 + CALIBRATION-CORPUS §1c |
| Status | v0.1 — locked |
