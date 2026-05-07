# V-model assembly-level TestTarget mapping — v0.1 CS

> **Trigger.** CP-SUPIN-05 STEP 1 — Pete: "mapping of TestTargets v terms of
> V-model TestTargets in assembly level (functionality, screens and elements,
> lists of values, active elements)".
>
> **Princip.** Existing `02_TestTargets` sheet má flow-driven TT (TT-001..TT-028
> = scénáře). To je acceptance-level. Pro V-model decomposition potřebujeme
> assembly-level TT — komponenty SUT mapping, ne user-flow mapping.
>
> **Cíl.** Vytvořit assembly-level TT taxonomy se 4 vrstvami (FUNC / SCRN /
> LOV / ACTV), naplnit initial katalog z DEMO recon, cross-linkovat na
> existing flow-TT.

---

## §1. V-model context

```
                                                       ┌──────────────────┐
        Acceptance level    ←──────────TC bind────────→│ TT-FLOW-* (now)  │  /02_TestTargets/
        (user scenario)                                │ TT-001..TT-028   │
                                                       └──────────────────┘
                                                                ▲
                                                                │  decomposition
                                                                │
        Assembly level      ←──────────TC bind────────→ ┌──────────────────┐
        (component / fn)                               │ TT-FUNC-*        │
                                                       │ TT-SCRN-*        │  /15_VModelAssemblyMap/
                                                       │ TT-LOV-*         │  (schema bump v0.5.0)
                                                       │ TT-ACTV-*        │
                                                       └──────────────────┘
                                                                ▲
                                                                │  refinement
                                                                │
        Component level     ←──────────TC bind────────→ ┌──────────────────┐
        (UI atomic widget,                             │ (future TT-WIDG-*│
         API endpoint atomic)                          │  TT-API-* per    │
                                                       │  endpoint)       │
                                                       └──────────────────┘
```

**Důsledek.** Jeden flow-TT (např. TT-005 "fillVehicleSection") obvykle pokrývá
N assembly-TT (např. SCRN-data + LOV-vehicleBrands + LOV-insuranceCompanies +
ACTV-autocomplete-brand + ACTV-autocomplete-model). Coverage matrix v
`16_CoverageMatrix` musí tuto traceability evidovat.

## §2. Naming convention

```
TT-{LAYER}-{slug}

LAYER ∈ {FUNC, SCRN, LOV, ACTV}
slug  = lowercase-kebab-case  (cs nebo en, dle čitelnosti)
```

| Prefix | Vrstva | Co reprezentuje |
|--------|--------|----------------|
| `TT-FUNC-*` | Funkcionalita | Use-case capability (mid-grain). Např. "fill účastníci A+B". |
| `TT-SCRN-*` | Screen | Konkrétní URL/route + jeho UI elementy jako celek. |
| `TT-LOV-*` | List of values | Codelist / enumeration / dropdown source. |
| `TT-ACTV-*` | Active element | Behavior trigger — button, input, autocomplete, signature pad. |

Slug nesmí obsahovat mezeru, lomítko ani diakritiku (kvůli stabilitě v Excelu +
`tt_code` field).

## §3. Initial catalog (z DEMO recon)

### §3.1 TT-FUNC-* (5 items, mid-grain functionality)

| TT code | Popis | Mapuje se na flow-TT |
|---------|-------|----------------------|
| TT-FUNC-001 | Vyplnění záznamu o nehodě (top-level use case) | TT-001 |
| TT-FUNC-002 | Ověření účastníků (OTP via N8 mock) | TT-005, TT-006 |
| TT-FUNC-003 | Sběr dokumentů (manual + zenID OCR) | TT-007, TT-008 |
| TT-FUNC-004 | Foto-evidence škod (Phase 3) | TT-014 |
| TT-FUNC-005 | Podpis a finalizace záznamu (Phase 4) | TT-019, TT-020 |

### §3.2 TT-SCRN-* (12 items — DEMO 4-phase wizard route map)

| TT code | URL | Phase |
|---------|-----|-------|
| TT-SCRN-rozcestnik | `/formular/` | 0 — gateway |
| TT-SCRN-informace | `/formular/informations` | A — intro |
| TT-SCRN-error-timeout | `/formular/error/timeout` | drift route (UX bug) |
| TT-SCRN-overeni | `/verification` | 1 — verification A+B |
| TT-SCRN-overeni-uspech | `/verification/success` | 1 — verified |
| TT-SCRN-dokumenty | `/documents/<rid>/` | 2 — manual fallback gate |
| TT-SCRN-dokumenty-manual | `/documents/<rid>/manual` | 2 — manual form |
| TT-SCRN-dokumenty-recap | `/documents/<rid>/recap` | 2 — recap |
| TT-SCRN-svedci | `/witnesses` | 2.5 — witness path |
| TT-SCRN-fotky | `/accident/<aid>/` | 3 — photo capture |
| TT-SCRN-poskozeni | `/damage` | 3 — damage screen |
| TT-SCRN-pohyb | `/movement` | 3 — movement screen |
| TT-SCRN-data | `/data` | 3 — vehicle data |
| TT-SCRN-circumstances | `/circumstances` | 3 — circumstances |
| TT-SCRN-datetime | `/datetime` | 3 — datetime + on-site |
| TT-SCRN-location | `/location` | 3 — location (RUIAN) |
| TT-SCRN-culprit | `/culprit` | 3 — culprit pick |
| TT-SCRN-summary | `/summary` | 4 — final review |
| TT-SCRN-sign | `/sign` | 4 — signature step |
| TT-SCRN-success | `/success` | 4 — záznam odeslán |

### §3.3 TT-LOV-* (10 items — codelists captured z live recon)

| TT code | Source | Public/Protected | Items |
|---------|--------|------------------|-------|
| TT-LOV-insuranceCompanies | `GET /api/enumerations/insuranceCompanies` | public 200 | ~215 |
| TT-LOV-vehicleBrands | `GET /api/enumerations/vehicleBrands` | public 200 | ~200 |
| TT-LOV-licenseCategories | `GET /api/enumerations/licenseCategories` | protected 403 | n/a |
| TT-LOV-damageZones | `GET /api/enumerations/damageZones` | protected 403 | n/a |
| TT-LOV-movementTypes | `GET /api/enumerations/movementTypes` | protected 403 | n/a |
| TT-LOV-accidentCauses | `GET /api/enumerations/accidentCauses` | protected 403 | n/a |
| TT-LOV-accidentCategories | `GET /api/enumerations/accidentCategories` | protected 403 | n/a |
| TT-LOV-vehicleCategories | `GET /api/enumerations/vehicleCategories` | protected 403 | n/a |
| TT-LOV-documentTypes | `GET /api/enumerations/documentTypes` | protected 403 | n/a |
| TT-LOV-witnessTypes | `GET /api/enumerations/witnessTypes` | protected 403 | n/a |
| TT-LOV-prefix-cs | UI dropdown component | static | 1 (+420) |
| TT-LOV-prefix-sk | UI dropdown component | static | 1 (+421) |

### §3.4 TT-ACTV-* (15 items — active elements identified from live walk)

| TT code | UI element | Phase | Notes |
|---------|-----------|-------|-------|
| TT-ACTV-CTA-vyplnit | button "VYPLNIT ZÁZNAM" | rozcestnik | WCAG 2.2 AA touch ≥ 44×44 |
| TT-ACTV-cookie-banner | "ODMÍTNOUT VŠE" / "PŘIJMOUT" | rozcestnik | Privacy default reject |
| TT-ACTV-rozumim | button "Rozumím" | informace | drift trigger; SPA POST /api/reports |
| TT-ACTV-checkbox-GDPR | GDPR consent checkbox | verification | gates PUT /reporter |
| TT-ACTV-OTP-input | 4 × `input[type=tel]` (React-controlled) | verification | needs native setter helper |
| TT-ACTV-button-odeslat-kod | "Odeslat kód" | verification | triggers N8 SMS mock |
| TT-ACTV-button-overit | "Ověřit" | verification | OTP submission |
| TT-ACTV-button-vyplnit-rucne | "Vyplnit údaje ručně" | dokumenty gate | bypasses zenID |
| TT-ACTV-autocomplete-RUIAN | address autocomplete | manual form | ČÚZK ArcGIS direct from browser |
| TT-ACTV-autocomplete-brand | vehicle brand combobox | data | LOV-vehicleBrands |
| TT-ACTV-autocomplete-model | vehicle model combobox | data | dynamic, brand-dependent |
| TT-ACTV-autocomplete-insurer | insurer combobox | data | LOV-insuranceCompanies |
| TT-ACTV-photo-capture | camera/upload widget | accident/photos | mobile camera API |
| TT-ACTV-checkbox-no-damage | "Vozidlo nebylo poškozeno" | damage | shortcut path |
| TT-ACTV-checkbox-in-motion | "bylo v pohybu" | movement | enumeration choice |
| TT-ACTV-textarea-desc | damage description textarea | damage | needs native setter helper |
| TT-ACTV-button-pokracovat | "Pokračovat" (Phase 3 step button) | many | recurrence; per-screen |
| TT-ACTV-button-potvrdit | "Potvrdit" (autocomplete confirm) | data | dual-button (inner+outer) |
| TT-ACTV-button-podepsat | "Podepsat" | summary | triggers /sign route |
| TT-ACTV-sign-canvas | touch signature canvas | sign | Phase 4; mouse-fallback for desktop test |
| TT-ACTV-button-odeslat | "Odeslat záznam" | sign | final commit |
| TT-ACTV-link-error-back | "Přejít na hlavní obrazovku" | error/timeout | drift escape |
| TT-ACTV-link-error-restart | "Vyplnit záznam o nehodě" | error/timeout | drift retry |

## §4. Cross-link na flow-TT

Mapping table (sample — full version v Excel `15_VModelAssemblyMap`):

| Assembly TT | Flow TT | Existing TC |
|-------------|---------|-------------|
| TT-FUNC-001 | TT-001 | TC-CP-A1-MAIN-DEMO |
| TT-SCRN-rozcestnik | TT-001, TT-002 | TC-CP-001 (bring-up smoke) + TC-CP-A1-MAIN-DEMO |
| TT-ACTV-CTA-vyplnit | TT-002 | TC-CP-001 |
| TT-LOV-insuranceCompanies | TT-013 | TC-CP-A2-ALT-7 (enumerations) |
| TT-LOV-prefix-sk | TT-014 | TC-CP-A2-ALT-5 (Slovak +421) |
| TT-ACTV-OTP-input | TT-005, TT-006 | TC-CP-A1-MAIN-DEMO + TC-CP-A2-ALT-1 (regex negative) |
| TT-ACTV-checkbox-GDPR | TT-005 | TC-CP-A2-ALT-4 |
| TT-SCRN-error-timeout | (drift) | TC-CP-A1-MAIN-DEMO (skip-rationale) + TC-CP-A2-ALT-* (skip-rationale) |
| TT-LOV-vehicleBrands | TT-016 | TC-CP-A2-ALT-7 |
| ... | ... | ... |

## §5. Excel sheet schema — `15_VModelAssemblyMap`

| Column | Type | Description |
|--------|------|-------------|
| `tt_code` | str | TT-{FUNC|SCRN|LOV|ACTV}-{slug} |
| `tt_layer` | enum | FUNC \| SCRN \| LOV \| ACTV |
| `tt_label_cs` | str | Czech display name |
| `tt_label_en` | str | English display name |
| `tt_url_pattern` | str | URL regex (jen pro SCRN; jinak prázdné) |
| `tt_api_endpoint` | str | API path (jen pro LOV; jinak prázdné) |
| `tt_widget_role` | str | ARIA role (jen pro ACTV; jinak prázdné) |
| `tt_phase` | int | wizard phase 0..4 (kde aplikovatelné) |
| `tt_env_constraints` | str | both / demo-only / prod-only / both-with-adapter |
| `tt_priority` | enum | A B C D |
| `tt_owner` | str | Pete / SUPIN / ČKP / extern |
| `tt_notes` | str | free text |

## §6. Coverage matrix — předpoklad pro `16_CoverageMatrix`

```
tc_code  ×  tt_code  →  coverage_strength ∈ {full, partial, indirect, none}

TC-CP-A1-MAIN-DEMO × TT-FUNC-001       = full        (covers entire flow)
TC-CP-A1-MAIN-DEMO × TT-SCRN-rozcestnik = full
TC-CP-A1-MAIN-DEMO × TT-ACTV-OTP-input  = full        (uses helper)
TC-CP-001          × TT-SCRN-rozcestnik = full
TC-CP-001          × TT-FUNC-001        = indirect    (smoke only)
TC-CP-A2-ALT-1     × TT-ACTV-OTP-input  = partial     (negative path)
TC-CP-A2-ALT-7     × TT-LOV-vehicle*    = full        (200+ items asserted)
```

**Coverage rule** (CP-SUPIN-05 phased introduction, viz `COVERAGE-RULE-STRATEGY-v0.1-CS.md`):
- Phase 0: informational
- Phase 1: warnings on uncovered TT-FUNC-*
- Phase 2: gating per-TT-class
- Phase 3: full gating

## §7. Migration plan

### §7.1 v0.5.0 — preview

- Tento doc + initial katalog (~70 assembly-level TT, viz §3)
- Coverage strategy doc
- Excel schema — **NO bump zatím**, v0.4.2 zůstává

### §7.2 v0.5.1 — Excel schema bump

- `tools/migrate_to_v0_5_0_assembly_coverage.py`:
  - Přidá `15_VModelAssemblyMap` sheet (12 cols) prefilled z tohoto docu
  - Přidá `16_CoverageMatrix` sheet (8 cols) initial empty
  - Bumps `00_README` to v0.5.0
  - Adds entry do `00b_ChangeLog`
  - Updates `00c_VersionSanityRules` s novým invariantem (každý TT-FUNC-* musí
    mít alespoň 1 covering TC v `16_CoverageMatrix`)

### §7.3 v0.5.x — coverage_audit.py first run

- `tools/coverage_audit.py BOURACKA-TESTPLAN-v0.5.0.xlsx`
- Output: report `runs/coverage-audit-{date}.json`
- Fields per TT: covering TC count, coverage_strength avg, gap detected?
- Phase 0: jen tisk reportu (informational); Phase 1+: exit non-zero on gap

## §8. Status

| Item | Hodnota |
|------|---------|
| Spec | `_specs/VMODEL-ASSEMBLY-TT-MAPPING-v0.1-CS.md` |
| Verze | v0.1 |
| Datum | 2026-05-07 EOD |
| Initial catalog | ~70 assembly-level TT (5 FUNC + 19 SCRN + 12 LOV + 23 ACTV + cross-links) |
| Excel schema bump | plánováno v0.5.1 (po review tohoto docu) |
| Coverage rule | viz companion `COVERAGE-RULE-STRATEGY-v0.1-CS.md` |
| Status | seed; čeká review + Excel bump v0.5.1 |
