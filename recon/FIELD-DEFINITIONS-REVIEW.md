# Field-Definition Catalogue — Review Note — v0.1

> Companion to `fixtures/field-definitions.yaml` (the canonical machine-
> readable catalogue) and `fixtures/codelists.yaml` (the 8 codelist
> shells). This review note is for human eyes — counts, gaps, edits to
> tick off.
>
> **Source.** `SUPIN_Bouracka_summary_ANA_v6.xlsx` tab "Data" — captured
> from photos `IMG_1063..IMG_1066` placed by user in
> `analyticke vstupy/lists of values/`.

## §1. Summary by entity

| Entity | Field count | Notes |
|--------|------------:|-------|
| **Report** | 19 | metadata + accident date/time/location + fault attribution |
| **Participant** | 76 | the bulk; phone OTP × 2, OP/ŘP × 2, vehicle × 2, insurance × 2, sign × 2 |
| **Witness** | 6 | optional; max 3 per report |
| **ParticipantVehicleMovementDefinition** | 2 | vehicle A + N — multichoice from CL-DEFINICE-POHYBU |
| **ParticipantVehicleDamageLocation** | 2 | vehicle A + N — multichoice from CL-POSKOZENI-CASTI |
| **VehiclePolicyholder** | 20 | placeholder data structures, **aktuálně bez využití** (not in MVP) |
| **Total** | **121** | matches your "121 values to be considered" |

## §2. Summary by screen / sekce

| Screen | Field count |
|--------|------------:|
| `V celé aplikaci a po ověření telefonních čísel` | 1 |
| `Od přístupu uživatele na landing page` | 1 |
| `nezobrazeno` (1 row — Status hlášení system field) | 1 |
| `Ověření telefonních čísel` | 14 |
| `Údaje o vozidle - vozidlo 1` (= vozidlo A) | 1 |
| `Údaje o vozidle - vozidlo A` | 8 |
| `Údaje o vozidle - vozidlo N` | 9 |
| `Osobní údaje - účastník 1` (= účastník A) | 1 |
| `Osobní údaje - účastník A` | 14 |
| `Osobní údaje - účastník N` | 15 |
| `Datum, čas a místo nehody` | 11 |
| `Svědci nehody` | 6 |
| `Nafocení nehody + SPZ - informace o vozidle A` | 3 |
| `Nafocení nehody + SPZ - informace o vozidle N` | 3 |
| `Okolnosti nehody` | 2 |
| `Souhrn a potvrzení zadaných údajů` | 2 |
| `Podpis (účastníci) pomocí SMS` | 8 |
| `n/a` (VehiclePolicyholder placeholder block) | 20 |

Maps cleanly to the screen catalogue we have in
`recon/ANALYTICAL-DOC-INTELLIGENCE-v0.2.md` §5.

## §3. Summary by data source (`Vstup atributu z/od`)

| Source | Count | Notes |
|--------|------:|-------|
| `Aplikace` (system-generated) | 16 | session ids, status, retry counters, signature timestamps |
| `Uživatel` | 22 | manual entry — phones, email, descriptive text, witnesses |
| `Uživatel (SMS)` | 4 | OTP codes (verify ×2, sign ×2) |
| `OCR fotky OP (ZenID)` + `AISPOV (ROB, CRR)` | 14 | OP/ŘP scan + register lookup |
| `OCR fotky OP (ZenID)` only | 6 | participant N address fields |
| `OCR fotky SPZ (ZenID), AISPOV (Evidence poj. vozidel)` | 2 | SPZ scan + insurance lookup |
| `AISPOV (CRV)` | 8 | vehicle data — make, model, year, VIN |
| `AISPOV (CRR)` | 6 | license number + categories + issuer |
| `AISPOV (Evidence poj. vozidel)` | 6 | insurance contract + green card |
| `Google Maps` | 2 | GPS lat/lon |
| `RUIAN` | 7 | accident-location address autocomplete |
| `(none — placeholder)` | 20 | VehiclePolicyholder block |
| not captured / blank | 8 | sign-screen counters, etc. |

## §4. Summary by FE type

| Type | Count |
|------|------:|
| `inputbox` | 51 |
| `inputbox(read only)` | 4 |
| `inputbox+kalendář` | 3 |
| `combobox` | 8 |
| `multichoice` | 6 |
| `checkbox` | 3 |
| `radiobutton` | 2 |
| `QR kód` | 1 |
| `nezobrazeno` (system fields) | 23 |
| `n/a` (placeholder block) | 20 |

**85 visible interactive fields** + 36 system/placeholder = 121.

## §5. Summary by Output (`Výstup atributu do`)

| Output | Count | Implication |
|--------|------:|-------------|
| `Vyplněné PDF` | ~85 | These fields end up on the signed accident-record PDF |
| `Aplikace` (internal-only) | ~16 | session ids, retry counters — never on PDF |
| (placeholder/blank) | ~20 | VehiclePolicyholder + a few |

## §6. Reference checklist (for human review of the YAML)

- [x] All 121 rows transcribed
- [x] IDs F-001..F-121 assigned, zero-padded
- [x] Codelist references point to 8 entries in `codelists.yaml`
- [x] Notes added where the doc explicitly says something binding
      ("Defaultní nastaveno na 5", "Email formát", "Předvyplnit +420")
- [x] Czech mobile-prefix regex captured in F-008 / F-015 rules block
- [ ] Číselníky tab (third Excel tab) — values for the 8 codelists
      pending; only license-category list pre-populated based on
      EU standard
- [ ] DEMO overrides (per scope C-5 reduced validation) — pending
      tst.demo recon; `demo_overrides:` block left blank on every
      field
- [ ] AISPOV WSDL contracts (OQ-CP-22) — pending; once landed we can
      cross-validate the field-shape promises in this catalogue
      against the actual SOAP envelope shapes

## §7. Where the YAML feeds into the rest of the suite

| Consumer | How it uses field-definitions.yaml |
|----------|-----------------------------------|
| `_specs/TESTCASE-SPEC-FORMAT-v0.1.md` | Step records can reference field by `id: F-008` instead of by Czech name — stable cross-references |
| TC-CP-001..020 SPEC.md (per-TC dev specs) | Each step's `selector` and `expected` can reference fields by F-NNN id; CS messages and validation rules pulled from `rules:` |
| `contracts/INT-004-aispov/` | The schema-asserts in Newman/SOAP runs validate the response shape against `data_type` declarations here |
| `seed-validate.ps1` | For each fixture row, picks fields by entity+screen and posts their data through the contract; passes only if shape matches the catalogue |
| Excel `02_TestCases::dev_spec_path` SPEC.md files | F-NNN refs in Pre-conditions / Steps / Acceptance criteria |
| `perf/load/full-wizard-submit.js` (k6) | Uses `rules` to generate valid synthetic phone numbers, OP IDs etc. for VU iterations |

## §8. Open editing actions

When you next sit with the Excel master, please confirm:

1. The 21 `string(2,12)` SPZ entries — is the lower bound really 2
   characters? (Czech SPZ pattern is normally 7-8.)
2. F-007/F-014 phone prefix dropdown — is the `string(5)` length
   chosen to fit "+420" (4) and "+421" (4) plus a leading character?
3. F-068 `Místo nehody - slovní popis - ruian id` — is RUIAN id
   really `integer(10)` (it can grow to 10 digits in practice).
4. The 20 VehiclePolicyholder rows — confirm "aktuálně bez využití"
   means R3+ (post v0.1 of the SUT, not just a future test scope).

These four points are where the YAML's note column carries my best
inference; please overwrite where the master Excel says different.

## §9. Status

| Item | Value |
|------|-------|
| Document | `recon/FIELD-DEFINITIONS-REVIEW.md` |
| Companion data | `fixtures/field-definitions.yaml` (121 entries) + `fixtures/codelists.yaml` (8 codelists, 1 pre-populated) |
| Source | IMG_1063..IMG_1066 = `SUPIN_Bouracka_summary_ANA_v6.xlsx` Data tab |
| Resolves | OQ-CP-21 (the "definiční excel") |
| Pending | Číselníky tab values, Obrazovky stavy tab, DEMO overrides |
| Status | v0.1 — ready for review + iterative additions |
