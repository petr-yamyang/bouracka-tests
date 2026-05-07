# 00 — README — Bouračka testovací plán v0.2

> *Když řidič po nehodě sáhne po telefonu, neměl by se setkat
> s další nehodou — tentokrát digitální. Tento testovací plán
> je naším slibem, že to tak nebude.*

## O čem to je

Bouračka je webová aplikace ČKP, která vede účastníka
dopravní nehody krok za krokem celým procesem hlášení —
od první obrazovky („zavolejte 158, pokud…") přes zachycení
identifikace (OP / ŘP / SPZ) až po podpis a odeslání záznamu
do registru pro IZS. Každý krok je v tichém měřítku zkouškou
toho, jak dobře umíme jako tým držet pozornost účastníka,
který právě prožil to, co nikdo prožít nechtěl.

Tento dokument je analytická + plánovací + reportingová
základna pro **automatizované testy** Bouračky (TST + DEMO
prostředí). Není to pouze popis toho, co testujeme — je to
*živý kontrakt*, který spouští samotnou exekuci testů přes
spec-loader popsaný v `_specs/`.

## Pro koho je tento dokument

| Role | Co najde |
|---|---|
| Recenzent SUPIN | celkové pokrytí, návaznost na požadavky, FURPS+ matici |
| Tester | TC-CP-001..024 katalogu + jak každý běží |
| Vývojář (Sonnet/Claude) | cestu od Excelu k vykonatelnému Playwright/Cypress kódu |
| Petr | jednu pravdu o tom, co je hotovo, co rozpracováno, co odloženo |

## Klíčové změny v0.2 vs v0.1

- **9 nových listů v Excelu**:
  - `00b_Requirements` — registr 20 funkčních + nefunkčních požadavků
  - `01b_Req_FURPS_Cartesian` — kartézské pokrytí 20 reqs × 10 dimenzí FURPS+
  - `01c_StateMachine` — formální stavový stroj `accidentReportStatus`
  - `02b_TC_Parameters` — typované parametry TC (resolved at runtime)
  - `02c_TC_Assertions` — vazba steps → assertion library
  - `02d_AssertionLibrary` — knihovna 14 vzorových assertion patternů (Playwright + Cypress snippety)
  - `05a_TestPlan` / `05b_TestSchedule` / `05c_TestEstimate` — Vaněkovo rozdělení Plan ≠ Schedule ≠ Estimate
- **R-CONTRACT-1** — workbook IS the live execution contract; runtime spec-loader resolves at test time
- **R-FURPS-1** — každý Req + TT + TC carries `furps_dimensions`
- **R-DERIVE-1** — každý TT cite source artefact (analytický doc, state machine, user direction…)
- **N8 SMS Gateway integrace** — Mockoon profile + dedikovaný TC-CP-005

## Verze a stav

| Položka | Hodnota |
|---|---|
| Verze | v0.2.0 |
| Datum | 2026-05-06 |
| Iterace | CP-SUPIN-03 |
| Pokrytí R1 | 7 testovacích cílů × 24 testovacích případů |
| Frameworky | Playwright (primární), Cypress, TestCafe (záloha) |
| Workbook validator | 10/10 zelený |
| Stav | připraveno k recenzi |

## Doporučený postup recenze

1. Otevřít `BOURACKA-TESTPLAN-v0.2.xlsx`, list `00_README` — orientace.
2. List `00b_Requirements` — 20 požadavků s FURPS+ tagging + provenance.
3. List `01b_Req_FURPS_Cartesian` — pokrytí napříč dimenzemi (200 buněk).
4. Listy `02_TestCases` + `02b_TC_Parameters` + `02c/d` — vlastní testovací případy.
5. `02_DIAGRAMY-AKTIVIT-CS.md` — diagramy aktivit D00..D17.
6. `05_POKRYTI-CS.md` — analýza mezer + doporučení dalšího postupu.

Zpětnou vazbu prosím na `petr.yamyang@gmail.com`,
subjekt `[BOURACKA-TESTS RECENZE v0.2.0] <téma>`.
