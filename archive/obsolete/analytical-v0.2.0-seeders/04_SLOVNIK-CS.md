# 04 — Slovník — Bouračka domain + CAST/MI-M-T pojmy

> *Slovník není jen překladová tabulka — je to dohoda. Když řekneme
> „účastník", víme, že nemyslíme „uživatele". Když řekneme „nehoda",
> víme, že nemyslíme „incident". To rozhoduje o tom, jestli budeme
> mluvit stejnou řečí nebo si jen budeme připadat, že mluvíme.*

(Plný slovník 60 termínů v listu Excelu `10_Glossary`. Tento dokument je
průvodce + zvýrazňuje klíčové domain-specific pojmy pro recenzi SUPIN.)

## §1. Bouračka doménové pojmy

| EN | CS preferovaný | Poznámka |
|---|---|---|
| Participant | **Účastník** | regulatorně závazný; **nikoli "uživatel"** |
| Driver | Řidič | f. Řidička |
| Vehicle | Vozidlo | |
| License plate | SPZ / Registrační značka | SPZ historické; obě v doméně používané |
| ID card | Občanský průkaz (OP) | regex `^[A-Z0-9]{9}$` |
| Driver's licence | Řidičský průkaz (ŘP) | |
| Insurance company | Pojišťovna | filtr `STATUS = 'AKT'` v číselníku |
| Mobile prefix | Mobilní předvolba | 47 platných CZ předvoleb (601..608, 702..706, 719..739, 770..779, 790..799) |
| Emergency services | Integrovaný záchranný systém (IZS) | QR předání ID hlášení DN |
| Accident report | Záznam o dopravní nehodě | terminální PDF |
| Witness | Svědek | (max 3) |
| Sign | Podpis | přes SMS-OTP |
| Submit | Odeslat | terminální akce |

## §2. Stavy přechody (state-machine-derived terms)

| EN | CS | Stav typ |
|---|---|---|
| NEW | Nový | počáteční |
| IN_PROGRESS_DRIVERS | Rozpracováno — řidiči | průběžný |
| IN_PROGRESS_VEHICLES | Rozpracováno — vozidla | průběžný |
| IN_PROGRESS_CIRCUMSTANCES | Rozpracováno — okolnosti | průběžný |
| TO_SIGN | K podpisu | průběžný |
| FINISHED | Dokončeno | terminální happy |
| CANCEL | Zrušeno (user-abort) | terminální user |
| ERROR | Chyba | terminální system |
| ERROR.smsGatewayUnavailable | Chyba — nedostupná SMS brána | sub-reason |
| ERROR.SMS_CODE_ATTEMPTS | Chyba — vyčerpání pokusů OTP | sub-reason |
| ERROR.TELEPHONE_NUMBER_COUNT | Chyba — telefon nadužíván v DB | sub-reason |
| ERROR.AISPOV_ROB_NENALEZENO | Chyba — doklad nenalezen v ROB | sub-reason |
| ERROR.OUTAGE_ACTIVE | Chyba — aktivní odstávka | sub-reason |
| ERROR.ELIGIBILITY_INTERLOCK | Chyba — eligibility interlock | sub-reason |

## §3. Zkratky organizací + integrací

| Zkratka | Plné jméno | Role |
|---|---|---|
| ČKP | Česká kancelář pojistitelů | provozovatel Bouračka |
| ČAP | Česká asociace pojišťoven | mateřská org. SUPIN |
| SUPIN | Servisní IT organizace ČAP | platforma + AISPOV provider |
| AISPOV | Aplikační informační systém pro pojistitele vozidel | SUPIN-hosted gateway pro registry |
| ROB | Registr obyvatel | identifikační lookup (OP) |
| CRR | Centrální registr řidičů | ŘP + skupiny oprávnění |
| CRV | Centrální registr vozidel | vozidlové údaje (značka, model, VIN) |
| RUIAN | Registr územní identifikace, adres a nemovitostí | našeptávač adres |
| IZS | Integrovaný záchranný systém | QR předání ID hlášení DN |
| zenID | (vendor) | OCR + identitní SDK (kamerový + API variant) |
| N8 | (SMS Gateway vendor) | doručování SMS-OTP |

## §4. FURPS+ rozšíření

| Zkratka | Dimenze | Příklad assertion patternu |
|---|---|---|
| F | Funkcionalita | `LIB-AS-FUNC-002` URL matches regex |
| U | Použitelnost | `LIB-AS-USAB-001` WCAG target-size ≥ 44×44 |
| R | Spolehlivost | `LIB-AS-RELI-001` exactly N network calls |
| P | Výkonnost | `LIB-AS-PERF-001` p95 response time |
| S | Udržovatelnost | `LIB-AS-SUPP-001` CS-localised error message |
| +D | Design constraints | (architectural; pokrytí v REQ) |
| +I | Implementation | např. browser version, viewport |
| +N | Interface | např. API contract |
| +L | Legal/regulatory | GDPR, WCAG zákon, ČKP regulations |
| +P_phys | Physical | n/a pro web SUT |

## §5. Verze a stav

(viz 00_README)
