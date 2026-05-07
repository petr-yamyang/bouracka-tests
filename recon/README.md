# recon/ — bouracka-tests reconnaissance materials

> Per `_config/CLIENT-PILOT-SUPIN-RECON-TEMPLATES-V0.1.md`.

## Folder map

| Folder | Source | Confidentiality |
|--------|--------|-----------------|
| `screens/` | Template 1 fillings — one MD per screen | PUBLIC recon: OK to commit. tst.* recon: confidential — gitignored attachment subfolder. |
| `flows/` | Template 2 fillings — one MD per flow + §5b.2 step typing | Same as `screens/` |
| `integrations/` | Template 3 fillings — one MD per integration + §5b.3 data-collection points | Same as `screens/` |
| `bugs/` | Template 4 fillings — known-issue catalogue | Confidential — gitignored |
| `divergences/` | Template 5 fillings — TEST↔DEMO deltas | Confidential — gitignored |
| `raw/` | curl/curl-on-thinkpad raw captures (HTML, headers, robots.txt) | Confidential — gitignored |
| `SITEMAP.md` | Public-side page graph | PUBLIC recon: OK to commit |
| `TEST-TARGET-CANDIDATES.md` | Synthesised TT catalogue with R-CAST-1 tagging | PUBLIC recon: OK to commit |

## E-mail subject-line routing

The user emails recon material with one of the prefixes documented in the
recon-templates spec §6:

```
[SUPIN-RECON] [SCREEN] <name>   → screens/SCR-NNN.md
[SUPIN-RECON] [FLOW]   <name>   → flows/FLW-NNN.md
[SUPIN-RECON] [INTEG]  <name>   → integrations/INT-NNN.md
[SUPIN-RECON] [BUG]    <name>   → bugs/BUG-CP-NNN.md
[SUPIN-RECON] [DIV]    <name>   → divergences/DIV-NNN.md
[SUPIN-RECON] [META]   <name>   → ./meta-NNN.md
```

ThinkPad Sonnet on the next iteration parses incoming e-mails and writes
into the right subfolder. Until the parser ships (`tools/recon-parser/`
in the future test-repo per FUTURE-REPO-STRUCTURE §3), Sonnet does this
manually.

## Status

CP-SUPIN-02 deliverable: SITEMAP, TEST-TARGET-CANDIDATES, screens/SCR-001..004,
flows/FLW-001..005, integrations/INT-001..005 — all PUBLIC recon.
tst.* delta layer arrives with the first user-supplied recon e-mails.
