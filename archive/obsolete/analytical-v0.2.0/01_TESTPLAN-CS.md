# 01 — Testovací plán — Bouračka v0.2

> *Plán není rozvrh ani odhad — plán je rozhodnutí, jaké
> testy spustíme, v jakém pořadí a proč. Rozvrh přijde po
> plánu. Odhad přijde po rozvrhu. Když si tyhle tři pojmy
> spleteme, projektová doba zmizí beze stopy.* — Vaněk, 2009

## §1. Účel testování

Ověřit, že Bouračka v testovacím prostředí (TST) i v DEMO
prostředí provede účastníka procesem hlášení dopravní nehody:
- bezporuchově (FURPS+ R) — pod normálním zatížením i při
  výpadku integrací,
- přívětivě (FURPS+ U) — na mobilu, podle zákonných
  standardů přístupnosti (WCAG 2.2 AA),
- správně (FURPS+ F) — auto-vyplnění z registrů AISPOV
  (ROB / CRR / CRV) odpovídá očekávanému výsledku, hraniční
  hodnoty jsou validovány,
- výkonně (FURPS+ P) — odezva pod definovanými prahovými
  hodnotami,
- udržovatelně (FURPS+ S) — všechny chybové hlášky mají CS
  rendering odpovídající glosáři, žádný hard-coded řetězec
  bez i18n.

## §2. Rozsah R1 (první vlna; tato verze)

7 testovacích cílů (`01_TestTargets`) odvozených od stavového
diagramu `accidentReportStatus`:

| TT | Stav / přechod | FURPS+ | Pokrytí (počet TC) |
|---|---|---|---:|
| TT-CP-R1-A1 | Vstupní brána + SMS-PING | F, R | 2 |
| TT-CP-R1-A2 | Phone-OTP (NEW → IN_PROGRESS_DRIVERS) | F, R, S | 5 |
| TT-CP-R1-B  | Identifikace řidičů (zenID + AISPOV ROB+CRR) | F, P, S, +L | 4 |
| TT-CP-R1-C  | Identifikace vozidel (zenID + AISPOV CRV) | F, P | 3 |
| TT-CP-R1-D  | Okolnosti + podpis + dokončení | F, U, R, S, +L | 6 |
| TT-CP-R1-E  | E2E orchestrace (cross-area) | F, R | 1 |
| TT-CP-R1-F  | Obálka chyb a ukončení | F, R, S, +L | 3 |

**24 R1 TC celkem** (TC-CP-001..024); mapování viz `02_TestCases.test_target_ref`.

## §3. Rozsah R2 (sentinel; připraveno k aktivaci)

11 R2 testovacích cílů evidováno; jejich SPEC.md soubory jsou
skeletony. Aktivace po ukončení R1 + recenze.

## §4. Plán × Rozvrh × Odhad — pozor na rozdíl

- **Plán** (rozhodnutí): tento dokument + `05a_TestPlan`
- **Rozvrh** (časová osa): `05b_TestSchedule`
- **Odhad** (pracnost): `05c_TestEstimate`

(Vaněkovo rozlišení per analytickou tradici testovací správy.)

## §5. Strategie integrací

Per `_specs/INTEGRATION-CONTRACTS-STRATEGY-v0.2.md`:
- **Layer 1..3 — defaultně Mockoon (Strategy A)** — testy spustitelné
  bez závislosti na vendor sandbox.
- **Layer 4 daily — SUT-skip (Strategy D)** — když SUPIN potvrdí
  `skip_integrations.*` flag.
- **Layer 4 nightly — real-vendor (Strategy B)** — když landují
  sandbox credentials.
- **Layer 5 — Mockoon** — žádné load proti reálným službám.

### N8 SMS Gateway (NEW v0.2)
- Mockoon profile `mockoon/n8-sms-gateway.json` se 3 scénáři:
  PING_OK / PING_NOK / SEND_OTP (vrací deterministický `otp_for_test=1234`).
- Vendor request šablona `_install/contracts/n8-sms-gateway-test-data-request.md`.

## §6. FURPS+ pokrytí

| Dimenze | Aktivní cells | Pending cells | N/A cells | % aktivace |
|---|:---:|:---:|:---:|:---:|
| F (Funkcionalita) | 17 | 3 | 0 | 85 % |
| U (Použitelnost) | 4 | 16 | 0 | 20 % |
| R (Spolehlivost) | 6 | 14 | 0 | 30 % |
| P (Výkonnost) | 3 | 17 | 0 | 15 % — **MEZERA** |
| S (Udržovatelnost) | 6 | 14 | 0 | 30 % |
| +D | 0 | 20 | 0 | 0 % |
| +I | 3 | 17 | 0 | 15 % |
| +N | 0 | 20 | 0 | 0 % |
| +L | 5 | 15 | 0 | 25 % |
| +P_phys | 0 | 0 | 20 | n/a (web SUT) |

(Plná Cartesian matice v `01b_Req_FURPS_Cartesian`.)

## §7. Rizika + mitigace

Per `_specs/SYNCHRO-THINKPAD-CP-SUPIN-03-2026-05-06.md` §4:

| Riziko | Mitigace |
|---|---|
| N8 SMS Gateway integrace bez sandbox credentials | Mockoon profile (default v0.2); GAP-4 vendor request odeslán |
| Wizard URL pattern best-guess pro tst.* | Recon Template 1 fill — colleague dodá tst.* screenshoty |
| Pages 43–133 analytického dokumentu nezpracovány | GAP-1 — operator dodá fotky před CP-SUPIN-04 |
| reCAPTCHA bypass token pro tst.* (OQ-CP-14) | GAP-5 — SUPIN env-config team |
| Synthetic OP/ŘP/SPZ photos | GAP-6 — Petr + ČKP-legal sign-off |

## §8. Akceptační kritéria pro v0.2

- [x] všech 24 R1 TC enumerováno v `02_TestCases`
- [x] validator script `tools/validate-workbook.py` zelený (10/10)
- [x] Mockoon profile pro N8 SMS Gateway přiložen
- [x] runtime spec-loader autorován (R-CONTRACT-1)
- [x] code-gen vytvořen (`tools/generate_tests.py`)
- [ ] proti tst.* end-to-end zelené (gated GAP-4 + GAP-5 + GAP-7)
- [ ] SPEC.md plný step list pro TC-CP-006..023 (gated GAP-1 + GAP-2)

## §9. Verze a stav

(viz 00_README)
