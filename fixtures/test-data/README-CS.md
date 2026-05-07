# test-data — single source of truth pro cross-framework testy

> **Per CP-SUPIN-05 v0.5.0.** Všechny 4 frameworks (Playwright / Cypress /
> TestCafe / Selenium) loadují fixtures z této složky přes per-framework
> data-loader helpery.
>
> Spec: `_specs/CROSS-FRAMEWORK-DATA-SHARING-v0.1-CS.md`

## Soubory

| Soubor | Obsah |
|--------|-------|
| `test-participants.yaml` | Adam + Beáta + A_specimen (SPECIMEN OP card data) |
| `test-vehicles.yaml` | ŠKODA Octavia + VW Golf + edge-case AVIA |
| `test-photos.yaml` | Refs do `analyticke vstupy/test-data-snippets/` (SPECIMEN OP photos, SPZ, Účastník A/B fotky) |
| (TBD v0.5.1) `test-addresses.yaml` | RUIAN autocomplete fixtures |
| (TBD v0.5.1) `test-otp-codes.yaml` | Mock OTP scenarios (any-4-digit, lockout, expired) |

## Photo binary layout — kde sídlí 164 MB obrázky

`test-photos.yaml` referencuje cesty **mimo test kit ZIP** — fotky jsou velké
(164 MB) a do mailového release scanner-friendly ZIPu se nehodí.

```
SUPIN/                                          ← Pete's workspace root
├── bouracka-tests/                             ← test kit (shipped via email)
│   └── fixtures/test-data/
│       ├── test-participants.yaml              ← refs SPECIMEN MRZ
│       ├── test-photos.yaml                    ← refs paths below
│       └── ...
└── analyticke vstupy/                          ← Pete's local raw inputs
    └── test-data-snippets/                     ← 164 MB photos staged here
        ├── OP - test ID s/OP1/                 ← 3 SPECIMEN OP photos
        ├── SPZ/                                ← 3 license plate photos
        └── fotky/
            ├── Účastník_A/                     ← 9 photos (UUID-named SPA output)
            ├── Účastník_B/                     ← 9 photos (UUID-named SPA output)
            └── *.jpg                           ← 7 generic accident scenes
```

**Per-host distribution.**
- Pete's **ThinkPad** + **MacBook**: photos at `…/analyticke vstupy/test-data-snippets/` (existing)
- **HP Elite SUPNB001**: separate channel needed:
  - SUPIN intranet share, OR
  - USB drop one-time, OR
  - Cloud share with SHA256 manifest
- After landing on HP Elite: copy/link to a parallel `analyticke vstupy/test-data-snippets/` next to `C:\TestAutomationSite\` so `bouracka.py` finds the relative paths.

## Loadery (nezbytné)

| Framework | Path |
|-----------|------|
| Playwright | `playwright/helpers/data-loader.ts` (TBD v0.5.1) |
| Cypress    | `cypress/support/data-loader.ts`    (TBD v0.5.1) |
| TestCafe   | `testcafe/helpers/data-loader.ts`   (TBD v0.5.1) |
| Selenium   | `selenium/helpers/data_loader.py`   (TBD v0.5.1) |

V v0.5.0 jsou jen YAML fixtures + spec; první loader implementation v v0.5.1.

## Editing rules

1. **Stejný yaml klíč napříč fixtures** = stejná konceptuální entita; nikdy
   neduplikovat ručně mezi soubory
2. **`_meta` block** v každém YAML — version + provenance + change tracking
3. **Žádný PII / real data** — všechny emails fictional, všechna jména
   demonstrative; SPZ nesmí kolidovat s reálnými registrovanými vozidly
4. **Schema změna** = bump `_meta.version` + záznam v `_specs/CROSS-FRAMEWORK-DATA-SHARING-v0.1-CS.md`
   §X.Y "Schema history"

## Provenance

Initial fixtures z DEMO Bouračka live walk 2026-05-06 (Pete recon session).
Populated jako součást CP-SUPIN-05 v0.5.0 strategic seed.
