# Coverage Gap Analysis — Activity Diagrams ↔ TestCases — v0.1

> Walks every decision diamond in every D00..D17 swimlane in
> `recon/diagrams/extracted/ACTIVITY-DIAGRAMS-v0.1.md` and cross-checks
> that the corresponding test scenario exists in `02_TestCases`.
> Surfaces gaps as new TC candidates that should land in CP-SUPIN-03.

## §1. Executive summary

| Metric | Value |
|--------|-------|
| Diagrams walked | 18 (D00..D17) |
| Decision branches catalogued | 32 |
| Branches with R1 TC coverage | 23 (72 %) |
| Branches deferred to R2 (acknowledged) | 6 (19 %) |
| **Branches with NO coverage today (gaps)** | **3 (9 %)** |
| New TC candidates surfaced | 3 (TC-CP-021..023) |

Gaps are NOT severe — all three are inside R1 scope but were not
itemised in the rev-4 TC enumeration because the analytical doc text
treated them as "obvious sub-steps". The activity diagrams make them
explicit and test-ownable.

## §2. Gap detail

### §2.1 GAP-1 — D12 Vehicle-order swap

**Where:** D12_Okolnosti nehody, decision diamond *"Změnit pořadí
vozidel na obrázku?"*

**Why it matters:** The user can manually reorder which vehicle is
labelled "A" vs "N" on the situational sketch. This is a regulatory-
adjacent operation (the situační nákres ends up on the signed PDF;
mis-labelling could attribute fault wrongly). The decision branches
are: *no swap* (default; flow continues) or *swap, then confirm,
then proceed*.

**Coverage today:** Only implicitly inside TC-CP-018 (E2E
orchestration) — but the swap branch is unlikely to be exercised
unless the test fixture deliberately triggers it.

**Proposed:**

```yaml
- code: TC-CP-021
  title_cs: "Okolnosti nehody — změna pořadí vozidel"
  title_en: "Circumstances — vehicle order swap"
  type: regression
  priority: B
  test_target_ref: TT-CP-R1-D
  state_machine_terminal_state: IN_PROGRESS_CIRCUMSTANCES
  acceptance:
    - At D12 click "ZMĚNIT POŘADÍ" → assert obrázky re-rendered with
      swapped order
    - Click "POKRAČOVAT" → assert state advances + the swapped order
      is persisted to the situační nákres in the final PDF
```

### §2.2 GAP-2 — D13 GPS vs manual-address branch

**Where:** D13_Datum, čas a místo nehody, decision diamond
*"GPS nebo manuálně?"*

**Why it matters:** Two distinct integration paths — INT-005 Google
Maps geolocation vs INT-008 RUIAN autocomplete. Each exercises
different network calls + different data shapes in the saved fields.

**Coverage today:** Only implicitly inside TC-CP-018 (E2E
orchestration) — and our default fixture path picks one branch
(typically manual-address per FLW-005 hypothesis). The other branch
is dark.

**Proposed:**

```yaml
- code: TC-CP-022
  title_cs: "Místo nehody — větvení GPS vs manuální adresa"
  title_en: "Accident location — GPS vs manual-address branch"
  type: regression
  priority: B
  test_target_ref: TT-CP-R1-D
  state_machine_terminal_state: IN_PROGRESS_CIRCUMSTANCES
  acceptance:
    - GPS branch: assert exactly 1 call to INT-005 with valid lat/lon;
      RUIAN call NOT made
    - Manual-address branch: assert RUIAN autocomplete called as user
      types; INT-005 NOT called
    - Both branches persist canonical accident-location fields per
      F-061..F-069 in the field-definitions catalogue
```

### §2.3 GAP-3 — D14 Fault-attribution radio

**Where:** D14_Určení viníka nehody, the radiobutton choice
*"účastník A | účastník N | žádný | neurčeno"*

**Why it matters:** This is a regulatory-grade datapoint. The fault
attribution affects the final PDF + the insurer-side processing.
Each radio value must be testable independently.

**Coverage today:** Only implicitly inside TC-CP-018 — and our
fixture sets fault to a default value (likely "účastník N" as it's
the typical at-fault-by-other scenario). The other three values are
dark.

**Proposed:**

```yaml
- code: TC-CP-023
  title_cs: "Určení viníka nehody — všechny radio varianty"
  title_en: "Fault attribution — all radio variants"
  type: regression
  priority: B
  test_target_ref: TT-CP-R1-D
  state_machine_terminal_state: IN_PROGRESS_CIRCUMSTANCES
  acceptance:
    - For each of {účastník A, účastník N, žádný, neurčeno}:
      drive D14, click POKRAČOVAT, assert state advances
    - Final PDF contains the chosen value verbatim under
      "Kdo zavinil nehodu?" field per F-112
```

## §3. R2-deferred branches (acknowledged; not gaps)

| Branch | Diagram | Why R2 |
|--------|---------|--------|
| Witness add (multiple, passenger marking) | D07 | TT-CP-R2-WITNESS — explicit R2 per user direction |
| Sdílený záznam load + re-load when changed | D15 | TT-CP-R2-SHARED — secondary cross-device flow |
| Cookie banner first-visit | D00 | TT-CP-R2-COOKIE |
| Outage warning (yellow box) | D00 | TT-CP-R2-OUTAGE-WARN — separate from active outage which IS R1 |
| In-app menu — Začít znovu confirmation | every D-screen | TT-CP-R2-MENU |
| Post-FINISHED actions (PDF download, QR scan, asistenční volání) | D17 | TT-CP-R2-SHARED + post-flow concerns |

These are explicitly out of R1 scope per user direction
"release 1 covers just these scenarios; other should be identified
but developed when information available". Logged here for
completeness — not gaps.

## §4. Cross-cutting completeness checks

The activity diagrams also surface **assertion candidates** that
strengthen existing TCs:

| Existing TC | Strengthening from diagrams |
|-------------|------------------------------|
| TC-CP-008 (driver ID happy) | Add assertion: "no further AISPOV calls for participant N if first ROB lookup empty" — explicit in D04 / D06 |
| TC-CP-012 (vehicle SPZ happy) | Add assertion: "SPZ photo cannot be re-uploaded after confirm" — explicit in D08 |
| TC-CP-015 (sign happy) | Add assertion: "PDF contains QR + Identifikační kód" — explicit in D17 |
| TC-CP-019 (outage active) | Add assertion: "VYPLNIT ZÁZNAM CTA disabled (not just hidden)" — explicit in D00 |

These are tightening, not gap-filling — same TC scope, more precise
acceptance criteria. CP-SUPIN-03 SPEC.md authoring picks these up.

## §5. Action items for CP-SUPIN-03

1. **Add TC-CP-021..023 to `02_TestCases`** — three rows, all priority
   B, all mapped to TT-CP-R1-D.
2. **Re-render mindmaps** after the addition
   (`tools/build-mindmaps.ps1`).
3. **Strengthen existing TC SPEC.md files** with the §4 assertions.
4. **Update `recon/TEST-TARGET-CANDIDATES.md`** v0.4 noting the 3 new
   TCs.
5. **Re-run coverage analysis** (this doc) to confirm 100 %
   diagram-branch coverage in R1.

## §6. Status

| Item | Value |
|------|-------|
| Document | `recon/COVERAGE-GAP-ANALYSIS.md` |
| Companion | `recon/diagrams/extracted/ACTIVITY-DIAGRAMS-v0.1.md` |
| Branches catalogued | 32 |
| Gaps in R1 | 3 (TC-CP-021..023) — actionable in CP-SUPIN-03 |
| Strengthening additions | 4 existing TCs |
| Status | v0.1 — review + apply in CP-SUPIN-03 prep |
