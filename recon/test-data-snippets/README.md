# test-data-snippets/ — observed test data captured from photos

> Per CP-SUPIN-04 L-WORK-4 + L-WORK-3 (Bouračka and DEMO go in
> parallel). This folder is the staging area where snippets live before
> they're promoted into:
> - `02b_TC_Parameters` (Excel row)
> - `mockoon/n8-sms-gateway.json` (mock scenario tweak)
> - `fixtures/shared/*.json` (test fixture)
> - `fixtures/codelists.yaml` (reference list value)
> - `fixtures/field-definitions.yaml::F-NNN.rules` (validation tightening)

## Folder convention

Snippets live INSIDE flow folders, not here:

```
recon/screenflows-live/flow-A1-main-tst/snippets/
├── snippet-01-phone-input-format.md
├── snippet-02-otp-mock-response.md
└── snippet-03-aispov-rob-happy-payload.md
```

This folder (`recon/test-data-snippets/`) holds:
- `_snippet-template.md` (the template to copy)
- `README.md` (this file)
- consolidated index (when the count grows past ~30 snippets)

## Confidentiality

Per scope §7 + `_install/EMAIL-DELIVERY-GUIDE-CS.md`:

- Snippet `.md` files with `sanitised: yes` → OK to commit
- Snippet `.md` files with `sanitised: no` → keep under
  `fixtures/secrets/` (gitignored); the snippet file in `snippets/`
  is just a pattern + REDACTED placeholder

## Promotion workflow

When a snippet is verified + cross-env-captured:

1. Open the snippet `.md`.
2. Identify its target (TC fixture / mock scenario / codelist / field rule).
3. Edit the target artefact (Excel / Mockoon / YAML).
4. Add `linked_artefact:` to the snippet's `## Status` block.
5. Update snippet `Status: committed-to-test-data`.

## Status

| Item | Value |
|------|-------|
| Folder | `recon/test-data-snippets/` |
| Template | `_snippet-template.md` |
| Convention | snippets live in flow-folder/snippets/; this folder = template + index |
| Status | v0.1 |
