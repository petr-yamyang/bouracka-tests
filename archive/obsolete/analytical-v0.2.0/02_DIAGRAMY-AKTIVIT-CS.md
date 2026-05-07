# 02 — Diagramy aktivit — Bouračka v0.2

> *Stav neexistuje sám o sobě; existuje proto, že předtím
> proběhl přechod, a kvůli tomu, že po něm proběhne další.
> Diagram aktivit je vyprávění, kde stavový stroj je věta,
> přechody jsou slovesa a uživatel je podmět.*

## §1. Stavový stroj `accidentReportStatus`

**8 stavů** (per analytický dokument + extrahováno do listu `01c_StateMachine`):

```
        ┌──────┐
   ──→  │ NEW  │    (po PING_OK na screen 01)
        └──┬───┘
           │  oba účastníci ověřili tel. číslo přes SMS-OTP
           ▼
   ┌─────────────────────────┐
   │ IN_PROGRESS_DRIVERS     │   identifikace přes OP/ŘP + AISPOV ROB+CRR
   └────────┬────────────────┘
            │  všichni řidiči identifikováni
            ▼
   ┌─────────────────────────┐
   │ IN_PROGRESS_VEHICLES    │   identifikace vozidel přes SPZ + AISPOV CRV
   └────────┬────────────────┘
            │  všechna vozidla identifikována
            ▼
   ┌─────────────────────────┐
   │ IN_PROGRESS_CIRCUMSTANCES │ okolnosti, místo, datum, viník, svědek
   └────────┬────────────────┘
            │  uživatel potvrdil souhrn
            ▼
   ┌──────────┐
   │  TO_SIGN │   čeká na SMS-OTP podpis obou účastníků
   └────┬─────┘
        │  oba podepsali
        ▼
   ┌──────────┐
   │ FINISHED │   PDF vygenerován + odeslán + QR pro IZS
   └──────────┘

   (terminální větve)
   ┌────────┐    user-abort přes „Začít znovu"
   │ CANCEL │
   └────────┘
   ┌────────┐    system-failure
   │  ERROR │    sub-reasons: smsGatewayUnavailable, SMS_CODE_ATTEMPTS,
   └────────┘                  TELEPHONE_NUMBER_COUNT, AISPOV_ROB_NENALEZENO,
                               OUTAGE_ACTIVE, ELIGIBILITY_INTERLOCK, ...
```

(Plný diagram + 12 přechodů v listu Excelu `01c_StateMachine`.)

## §2. Diagramy aktivit D00..D17

| Diagram | Téma | Stavový kontext | Související TC |
|---|---|---|---|
| D00 | Vstupní brána (gateway entry) | NEW | TC-CP-001..002, TC-CP-019 |
| D01 | Volba „Volat Policii" — interlock | NEW | TC-CP-003..004 |
| D02 | SMS Gateway PING + SEND_OTP | NEW → IN_PROGRESS_DRIVERS | TC-CP-001..007, **TC-CP-005** |
| D03 | Identifikace OP — upload + OCR | IN_PROGRESS_DRIVERS | TC-CP-008..011 |
| D04 | AISPOV ROB lookup → auto-fill | IN_PROGRESS_DRIVERS | TC-CP-008, TC-CP-010 |
| D05 | Identifikace SPZ — upload + OCR | IN_PROGRESS_VEHICLES | TC-CP-012..013 |
| D06 | AISPOV CRV → vehicle data | IN_PROGRESS_VEHICLES | TC-CP-012, TC-CP-014 |
| D07 | Doplnění svědka | IN_PROGRESS_CIRCUMSTANCES | (R2) |
| D08 | Doplnění okolností nehody | IN_PROGRESS_CIRCUMSTANCES | TC-CP-015 |
| D09 | Vehicle-data finalize | IN_PROGRESS_VEHICLES → IN_PROGRESS_CIRCUMSTANCES | TC-CP-012 |
| D10 | Vozidlo N | IN_PROGRESS_VEHICLES | (R2) |
| D11 | Vozidlo N — pokr. | IN_PROGRESS_CIRCUMSTANCES | (R2) |
| D12 | Změna pořadí vozidel na obrázku | IN_PROGRESS_CIRCUMSTANCES | TC-CP-021 |
| D13 | Místo: GPS vs manuální adresa (Maps + RUIAN) | IN_PROGRESS_CIRCUMSTANCES | TC-CP-022 |
| D14 | Určení viníka — radio (4 varianty) | IN_PROGRESS_CIRCUMSTANCES | TC-CP-023 |
| D15 | Náhled před podpisem | → TO_SIGN | TC-CP-015 |
| D16 | Podpis — happy + retry + exhaustion | TO_SIGN → FINISHED nebo ERROR | TC-CP-015..017 |
| D17 | E-mail / oznámení po podpisu | FINISHED | TC-CP-015 |

**Visualizace každého diagramu**: viz `diagrams/tt-mindmap.{png,svg,pdf}`
+ `diagrams/tc-mindmap.{png,svg,pdf}` přiložené v balíčku.

## §3. Mapování diagramů na TestTargets

```
TT-CP-R1-A1 (PING gate)        ← D00 + D02
TT-CP-R1-A2 (Phone-OTP)        ← D02
TT-CP-R1-B  (driver-data)      ← D03 + D04 + D05 + D06
TT-CP-R1-C  (vehicle-data)     ← D05 + D06 + D09 + D10 + D11
TT-CP-R1-D  (circumstances+sign)← D07 + D08 + D12 + D13 + D14 + D15 + D16 + D17
TT-CP-R1-E  (E2E)              ← všechny D00..D17
TT-CP-R1-F  (failure envelope) ← D00 (outage), D02 (PING_NOK), D04 (AISPOV NENALEZENO),
                                  D16 (sign exhaustion)
```

## §4. Verze a stav

(viz 00_README)
