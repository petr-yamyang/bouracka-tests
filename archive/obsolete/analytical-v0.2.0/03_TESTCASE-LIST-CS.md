# 03 — Katalog testovacích případů — Bouračka v0.2

> *Dvacet čtyři testů. Žádný není zbytečný; žádný není nepostradatelný.
> Ten, který odhalí závadu jako první, je hrdina dne; ten, který
> ji odhalí jako tisící, je hrdina kvality.*

## §1. Přehled (R1 — 24 TC)

| TC | Název CS | Typ | TT | Pri | FURPS+ | Stav |
|---|---|---|---|:---:|---|---|
| TC-CP-001 | PING SMS Gateway — happy | happy | TT-CP-R1-A1 | A | F, R | active |
| TC-CP-002 | PING SMS Gateway — NOK / negative-ending | failure | TT-CP-R1-A1 | A | F, R | active |
| TC-CP-003 | Phone-OTP — happy oba účastníci | happy | TT-CP-R1-A2 | A | F, R | active |
| TC-CP-004 | Phone-OTP — vyčerpání pokusů (SMS_CODE_ATTEMPTS) | failure | TT-CP-R1-A2 | A | F, R | active |
| **TC-CP-005** | **SMS-OTP odeslání + ověření (NEW v0.2)** | **happy** | **TT-CP-R1-A2** | **A** | **F, R** | **active** |
| TC-CP-006 | TELEPHONE_NUMBER_COUNT — security check | failure | TT-CP-R1-A2 | A | F, R | active |
| TC-CP-007 | OTP retry happy (recoverable) | regression | TT-CP-R1-A2 | A | F, R | active |
| TC-CP-008 | zenID + AISPOV ROB — happy auto-fill | happy | TT-CP-R1-B | A | F, P, S | active |
| TC-CP-009 | zenID NOK → manual + AISPOV button | regression | TT-CP-R1-B | A | F | active |
| TC-CP-010 | AISPOV NENALEZENO ROB — bez auto-fill | failure | TT-CP-R1-B | A | F, S | active |
| TC-CP-011 | Camera permission denied → gallery upload | regression | TT-CP-R1-B | A | F, U, +I | active |
| TC-CP-012 | SPZ scan + AISPOV vehicle — happy | happy | TT-CP-R1-C | A | F, P | active |
| TC-CP-013 | SPZ NOK → gallery upload | regression | TT-CP-R1-C | A | F | active |
| TC-CP-014 | AISPOV vehicle missing — bez insurance fields | failure | TT-CP-R1-C | B | F, S | active |
| TC-CP-015 | Souhrn → SMS-OTP oba řidiči — happy | happy | TT-CP-R1-D | A | F, R, S, +L | active |
| TC-CP-016 | Sign-OTP exhaustion | failure | TT-CP-R1-D | A | F, R | active |
| TC-CP-017 | Submit timeout retry | regression | TT-CP-R1-D | A | F, R | active |
| TC-CP-018 | E2E happy NEW → FINISHED | happy | TT-CP-R1-E | A | F, R | active |
| TC-CP-019 | Outage active — CTA disabled | failure | TT-CP-R1-F | A | F, U, +L | active |
| TC-CP-020 | Mid-wizard interlock self-disclosure | failure | TT-CP-R1-F | A | F, +L | active |
| TC-CP-021 | Změna pořadí vozidel na obrázku (D12) | regression | TT-CP-R1-D | B | F | active |
| TC-CP-022 | Místo nehody — GPS vs manuální adresa (D13) | regression | TT-CP-R1-D | B | F | active |
| TC-CP-023 | Určení viníka — všechny radio varianty (D14) | regression | TT-CP-R1-D | B | F, +L | active |

(Plný katalog je v listu Excelu `02_TestCases`; tento dokument je
průvodce + lidsky čitelný report. Parametry per TC v `02b_TC_Parameters`;
assertion vazby v `02c_TC_Assertions × 02d_AssertionLibrary`.)

## §2. Pravidlo R-FAIL-1 — pairing happy ↔ failure

Každý happy TC má ≥ 1 failure pair (per `02_TestCases.notes`):

| Happy | Failure pair |
|---|---|
| TC-CP-001 (PING happy) | TC-CP-002 (PING NOK) |
| TC-CP-003 (Phone-OTP happy) | TC-CP-004 (attempts exhausted) + TC-CP-006 (NUMBER_COUNT) |
| TC-CP-005 (SMS-OTP happy) | (LATER — když ASK-002 surfaces EX_CHYBA z reálného N8) |
| TC-CP-008 (AISPOV ROB happy) | TC-CP-010 (NENALEZENO) |
| TC-CP-012 (SPZ + AISPOV happy) | TC-CP-014 (vehicle missing) |
| TC-CP-015 (sign happy) | TC-CP-016 (sign exhaustion) |
| TC-CP-018 (E2E happy) | TC-CP-019/020 (outage; interlock) |

## §3. Mobile-only

Per analytický dokument str. 14/133 §3.2: aplikace **POUZE mobilní zobrazení**.

Každý TC se spouští v 3 viewportech: 320×568 + 375×667 + 414×896
(per `02_TestCases.viewport_spec`). Mobilní-pouze assertce
(např. WCAG target-size ≥ 44 × 44 px per `LIB-AS-USAB-001`)
značeny v step listu.

## §4. CS-locale primarně

Všechny očekávané texty v CS první (regex i18n-aware); EN
zrcadlí. Glosář v listu Excelu `10_Glossary` (60 termínů).

## §5. Nové v0.2

- **TC-CP-005** — SMS-OTP odeslání + ověření. Pokrývá round-trip
  s Mockoon profile (deterministický `otp_for_test=1234`).
- **5 forward-looking assertion patternů** v `02d_AssertionLibrary`:
  `LIB-AS-FUNC-001` (network 2xx), `LIB-AS-USAB-001` (WCAG target-size,
  již v použití), `LIB-AS-RELI-001` (network call count), `LIB-AS-PERF-001`
  (p95 latency), `LIB-AS-SUPP-001` (CS error message).
- **Runtime spec-loader** — workbook resolves parameters + assertions
  za běhu; SPEC.md zůstává jako lidský companion.

## §6. Verze a stav

(viz 00_README)
