# 05 — Pokrytí — analýza mezer — Bouračka v0.2

> *Pokrytí není o tom, co děláme dobře — pokrytí je o tom, co ještě
> neděláme. Jeden zelený dashboard nám neřekne, jestli jsme
> nepřehlédli celou dimenzi kvality, která může den před produkcí
> spadnout na hlavu.*

## §1. Pokrytí podle stavového stroje

| Stav / přechod | TC počet | Diligence | Mezera? |
|---|:---:|:---:|:---:|
| NEW (entry) | 4 | smoke + happy + negative | — |
| NEW → IN_PROGRESS_DRIVERS (Phone-OTP) | 5 | happy + negative + regression | — |
| NEW → ERROR.smsGatewayUnavailable | 1 | negative | — |
| IN_PROGRESS_DRIVERS (entry) | 4 | happy + negative + regression | — |
| IN_PROGRESS_DRIVERS (AISPOV ROB) | 3 | happy + negative | — |
| IN_PROGRESS_DRIVERS → IN_PROGRESS_VEHICLES | 1 | (E2E only) | RECON GAP-1 (deeper SPEC) |
| IN_PROGRESS_VEHICLES (SPZ + AISPOV CRV) | 3 | happy + negative + regression | — |
| IN_PROGRESS_VEHICLES → IN_PROGRESS_CIRCUMSTANCES | 1 | (E2E only) | RECON GAP-2 |
| IN_PROGRESS_CIRCUMSTANCES (location, fault) | 3 | regression × 3 | — (NEW v0.2: TC-CP-021..023) |
| IN_PROGRESS_CIRCUMSTANCES → TO_SIGN | (covered in TC-CP-015) | happy | — |
| TO_SIGN → FINISHED | 1 | happy | — |
| TO_SIGN → ERROR.SIGN_OTP_ATTEMPTS | 1 | negative | — |
| Recoverable retry on submit | 1 | regression | — |
| OUTAGE_ACTIVE entry-block | 1 | negative | — |

**Celkem 24 R1 TC pokrývají všechny 8 stavů + většinu přechodů.**
Aktivace mezer čeká na deeper-wizard recon (GAP-1, GAP-2).

## §2. Pokrytí podle FURPS+ dimenze (per `01b_Req_FURPS_Cartesian`)

| Dimenze | Aktivní cells | Pending cells | N/A cells | % aktivace | Komentář |
|---|:---:|:---:|:---:|:---:|---|
| F (Funkcionalita) | 17 | 3 | 0 | 85 % | dobře pokryto — všechny core wizard happy/failure paths |
| U (Použitelnost) | 4 | 16 | 0 | 20 % | mezera — autorovat 3 TC pro WCAG compliance |
| R (Spolehlivost) | 6 | 14 | 0 | 30 % | mezera — autorovat retry/timeout TC pro AISPOV + SMS |
| **P (Výkonnost)** | **3** | **17** | **0** | **15 %** | **MEZERA — kandidát na první 3 perf TC pro AISPOV registry** |
| S (Udržovatelnost) | 6 | 14 | 0 | 30 % | mezera — i18n + log-correlation TC |
| +D (Design) | 0 | 20 | 0 | 0 % | architectural; pokrytí v REQ — neodvozuje TC |
| +I (Implementation) | 3 | 17 | 0 | 15 % | mezera — browser-version compatibility TC |
| +N (Interface) | 0 | 20 | 0 | 0 % | mezera — API contract test (Layer 1) |
| +L (Legal/regulatory) | 5 | 15 | 0 | 25 % | dobře — GDPR + WCAG + ČKP regs zachyceno |
| +P_phys (Physical) | 0 | 0 | 20 | n/a | správně N/A pro web SUT |

## §3. Pokrytí podle integrace

| Integrace | Strategy A pokryto | Strategy B/D | Mezera? |
|---|:---:|:---:|---|
| INT-001 reCAPTCHA | YES (env-config token) | sandbox keys | OQ-CP-14 |
| **INT-002 N8 SMS Gateway (NEW v0.2)** | **YES (Mockoon profile)** | **OQ-CP-27 (sandbox/skip)** | **GAP-4 + GAP-10** |
| INT-003 SMTP | YES (Mailpit) | live | — |
| INT-004 AISPOV (ROB+CRR+CRV) | YES (Mockoon — schema check) | sandbox | GAP-7 |
| INT-005 Maps geocoder | YES (Mockoon) | sandbox | — |
| INT-006 zenID WebSDK | partial (Strategy A only) | OQ-CP-23 | GAP-6 |
| INT-007 zenID API | partial | OQ-CP-23 | GAP-6 |
| INT-008 RUIAN | YES (Mockoon) | public API | — |
| INT-009 Azure Blob outage | YES (static JSON config) | live | — |
| INT-010 Google Analytics | YES (script intercept) | Google test keys | — |

## §4. Inputs gap inventory (per synchro §4.2)

| GAP# | Co chybí | Kdo dodává | Do kdy | Odemkne |
|---|---|---|---|---|
| GAP-1 | Pages 43..133 analytického dokumentu | Petr (foto batch) | před CP-SUPIN-04 | TC-CP-006..020 specs (deeper wizard) |
| GAP-2 | tst.bouracka.cz screen-recon Template 1 fills | Colleague | rolling | selectors + URL patterns |
| GAP-3 | tst.demo.bouracka.cz divergence catalogue | Colleague | rolling | env_divergence rows |
| GAP-4 | N8 SMS Gateway sandbox / `skip_integrations.sms` | SUPIN/N8 | týden 2026-05-11 | TC-CP-001/002/005 proti reálnému N8 |
| GAP-5 | reCAPTCHA bypass token pro tst.* | SUPIN/ČKP env-config | před tester runs | každý TC |
| GAP-6 | Synthetic OP/ŘP/SPZ photos | Petr + ČKP-legal | týden 2026-05-11 | TC-CP-008..010 reálné zenID |
| GAP-7 | AISPOV WSDL/OpenAPI | SUPIN-internal | rolling | TC-CP-006..015 contract test |
| GAP-8 | Tester laptop spec | SUPNB001/002/003 audit | před CP-SUPIN-08 | install profil A/B/C |
| GAP-9 | Real SUPIN tester contact | Petr → SUPIN | před CP-SUPIN-09 | human-in-loop run |
| GAP-10 | N8 documentation (rate limits, shapes) | SUPIN/N8 | rolling | Mockoon scenario fidelity |

## §5. Doporučení — co testovat dál

V pořadí podle přínos / pracnost:

1. **(P-dimenze mezera)** — autorovat 3 výkonové TC pro AISPOV registry
   (Strategy A; měření p95 přes `LIB-AS-PERF-001`).
2. **(GAP-1)** — Petr dodá fotky stránek 43..133 → odemkne 15 deeper-wizard TC.
3. **(GAP-4)** — N8 sandbox negotiations → TC-CP-001/002/005 proti
   reálnému tst.*.
4. **(GAP-6)** — synthetic OP photos → odemkne nightly real-zenID smoke.
5. **(U-dimenze mezera)** — autorovat 3 WCAG TC (focus management,
   keyboard navigation, screen reader).

## §6. Verze a stav

(viz 00_README)
