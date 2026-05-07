# MANIFEST — Bouračka analytická dodávka v0.2.0 — CS

> Tento balíček obsahuje analytické artefakty pro recenzi
> SUPIN/ČKP. Není určen pro instalaci — pro tu slouží
> samostatný balíček `automation-v0.2.0`.

## Co je nového vs v0.1.0

**MAJOR schema upgrade** per CP-SUPIN-03 (synchro 2026-05-06):

- **9 nových listů v Excelu**:
  - `00b_Requirements` — registr 20 funkčních + nefunkčních požadavků
  - `01b_Req_FURPS_Cartesian` — kartézské pokrytí 20 reqs × 10 dimenzí FURPS+
    (200 buněk; každá s `cell_status='active|pending|na'` + N/A justification)
  - `01c_StateMachine` — formální stavový stroj `accidentReportStatus`
    (8 stavů + 12 přechodů)
  - `02b_TC_Parameters` — typované parametry TC (resolved at runtime)
  - `02c_TC_Assertions` — vazba steps → assertion library
  - `02d_AssertionLibrary` — knihovna 14 vzorových assertion patternů
    (10 extracted z existujících SPECs + 5 forward-looking FURPS+ canonicals
    s Playwright + Cypress snippety)
  - `05a_TestPlan` / `05b_TestSchedule` / `05c_TestEstimate` — Vaněkovo
    rozdělení Plan ≠ Schedule ≠ Estimate
- **14 nových sloupců** na 4 existujících listech:
  - `01_TestTargets` +11: furps_dimensions, CO/KDO/KDY/KDE/JAK,
    source_artefact_kind/ref/derivation_rule/author_role, requirement_ref
  - `02_TestCases` +3: furps_dimensions, impulse_ref, diligence
  - `04_TestEnvironments` +1: sms_gateway_mode
  - `07_TestRunResults` +2: assertion_ref, furps_dimension_failed
  - `08_Bugs` +2: diligence, impulse_ref
- **5 nových R-pravidel**:
  - **R-DERIVE-1** — každý TT cite source artefact
  - **R-FURPS-1** — každý Req + TT + TC carries furps_dimensions
  - **R-EXPAND-1** — Cartesian cells become TC-sets s sev+urg tags
  - **R-PLAN-2** — scheduling_unit_kind matches projects.methodology
  - **R-CONTRACT-1** — workbook IS the live execution contract
- **`05_TestSets` deprekováno** → split do `05a/b/c` (per Vaněk)
- **Nový TC-CP-005** — SMS-OTP odeslání + ověření (s Mockoon profile)
- **N8 SMS Gateway** poprvé jako first-class integration (INT-002 enriched)

## Validator

Workbook prošel `tools/validate-workbook.py` se **10/10 zelenými checky**:
- 01_required_sheets_present ✓
- 02_itembase_present ✓
- 03_furps_dimensions_populated ✓
- 04_tt_source_artefact_present ✓
- 05_tt_requirement_ref_valid ✓
- 06_tc_test_target_ref_valid ✓
- 07_assertion_library_ref_valid ✓
- 08_cartesian_na_justified ✓
- 09_scheduling_unit_kind_valid ✓
- 10_state_machine_integrity ✓

## Obsah

| Soubor | Účel |
|--------|------|
| `00_README-CS.md` | Úvod a pokyny pro recenzenty |
| `01_TESTPLAN-CS.md` | Testovací plán Bouračka v0.2 |
| `02_DIAGRAMY-AKTIVIT-CS.md` | Diagramy aktivit D00..D17 + state machine |
| `03_TESTCASE-LIST-CS.md` | Katalog 24 R1 TC |
| `04_SLOVNIK-CS.md` | Slovník (60 termínů; plný v Excelu) |
| `05_POKRYTI-CS.md` | Analýza pokrytí + 10 inputs gaps |
| `BOURACKA-TESTPLAN-v0.2.xlsx` | Hlavní artefakt — 21 listů, 288 vzorců |
| `diagrams/tt-mindmap.{png,svg,pdf}` | Mindmapa TestTargets |
| `diagrams/tc-mindmap.{png,svg,pdf}` | Mindmapa TestCases |

## Doporučený postup recenze

1. Přečíst tento MANIFEST.
2. Otevřít `00_README-CS.md` — orientace.
3. Otevřít `BOURACKA-TESTPLAN-v0.2.xlsx`:
   - List `00_README` — popis
   - List `00b_Requirements` — 20 reqs
   - List `01_TestTargets` — 18 TT (7 R1 + 11 R2)
   - List `02_TestCases` — 24 R1 TC
   - List `01b_Req_FURPS_Cartesian` — Cartesian 200 cells
   - List `01c_StateMachine` — state machine
4. Diagramy (`diagrams/`) pro vizuální orientaci.
5. `05_POKRYTI-CS.md` — kde jsou mezery + co dál.

## Zpětná vazba

E-mail: `petr.yamyang@gmail.com`
Subjekt: `[BOURACKA-TESTS RECENZE v0.2.0] <téma>`

## Verze

| Položka | Hodnota |
|---|---|
| Verze | v0.2.0 |
| Datum sestavení | 2026-05-06 |
| Iterace | CP-SUPIN-03 |
| Schémická migrace z v0.1 | per `tools/rev7_xlsx_v02_migration.py` (committed v repo) |
| Validator status | 10/10 ✓ |
| Stav | k recenzi |
