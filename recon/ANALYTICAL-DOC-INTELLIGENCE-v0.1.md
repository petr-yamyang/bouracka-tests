# Analytical-Document Intelligence — bouracka.cz Funkční + technická analýza — v0.1

> **Source.** Photos `IMG_1028.HEIC` … `IMG_1047.HEIC` taken by Petr from
> the ČKP/SUPIN-internal **"Funkční a technická analýza realizace webové
> aplikace Bouračka — digitalizace EU formuláře pro hlášení dopravních
> nehod"** document. 133 pages total; pages **11–30** captured in this
> first batch (20 photos).
>
> **Confidentiality posture.** This is recon material derived from a
> document marked as formal vývoj+test specification for the project.
> Per scope §7 and AMENDMENT 2 point 5 — confidentiality reservation
> enforced; this file lives in `recon/` (gitignore patterns apply to
> attachment subfolders, but the consolidated intelligence in *this*
> file is OK to commit because it carries no secrets — it just records
> the system's published-to-tester architecture).
>
> **Status.** v0.1 — first batch of 20 photos transcribed; further
> photos expected for pages 31..133 (screen specs 03..15+, integration
> mappings, field-validation Excel pointer, error states, config
> parameters).

---

## §1. Document framing (per §2.1 Cíl dokumentu — page 11/133)

> "Tento dokument popisuje funkční a technickou analýzu realizace
> webové aplikace Bouračka — digitalizace EU formuláře pro hlášení
> dopravních nehod. Dále tento dokument slouží jako formální zadání
> pro vývojový a testing tým v rámci fáze implementace a testování
> projektu."

The document IS the formal dev-and-test specification. Treat as
authoritative for terminology, architecture, state machine, and field
contracts.

## §2. Glossary additions (per §2.2 — pages 11–12/133)

**Substantive additions to `10_Glossary` Excel sheet** — these terms
were inferred or wrong before; canonical CKP/SUPIN definitions below.

| CS | EN / canonical | Definition (per ČKP doc) |
|----|----------------|--------------------------|
| **SUPIN s.r.o.** | SUPIN | **Servisní IT organizace ČAP** (NOT just CDN as previously inferred). ČAP = Česká asociace pojišťoven; SUPIN is the IT-service org of the Czech insurance industry — broader than ČKP alone. |
| **ČKP** | Czech Insurance Bureau | Česká kancelář pojistitelů; bouracka.cz operator. |
| **ČAP** | Czech Insurance Association | Česká asociace pojišťoven; SUPIN's parent. |
| **PS** | insurance contract | Pojistná smlouva. |
| **DN** | traffic accident | Dopravní nehoda. |
| **Účastník** | participant | Osoba, která vyplňuje hlášení o dopravní nehodě. (NB: this is the legal/business term used throughout — NOT "uživatel"/"user".) |
| **Ověřený účastník** | verified participant | Účastník nehody, který v hlášení nehody již ověřil své tel. číslo. |
| **Účastník A** | participant A (driver A) | První účastník dopravní nehody — osoba která formulář o nehodě vyplňuje na zařízení. |
| **Účastník N** | participant N (driver B/C/…) | Další účastník — Účastník B, C atd. (R1 = N=B only; R2+ = ≥3 drivers per §9 Rozvojové body). |
| **Zařízení** | device | Zařízení, na kterém jeden z účastníků vyplňuje hlášení. |
| **DB** | database | Databáze. |
| **WS** | web service | Web service. |
| **SOAP** | SOAP | Protokol pro výměnu zpráv založených na XML přes síť, hlavně pomocí HTTP. |
| **REST** | REST | Protokol pro výměnu zpráv založený primárně na JSON přes síť, hlavně pomocí HTTP. |
| **WAF** | Web Application Firewall | Web application firewall — chrání webové aplikace před různými aplikačními vrstvami. |
| **BE / FE** | back-end / front-end | Vrstva aplikace operující s daty / Prezentační vrstva aplikace. |
| **RPO / RTO** | Recovery Point/Time Objective | Recovery posture metrics. |
| **MTPD** | Maximum Tolerable Period of Disruption | Maximální akceptovatelná doba výpadku. |
| **MTDL** | Maximum Tolerable Data Loss | Maximální akceptovatelná ztráta dat. |
| **WCAG** | WCAG | Web Content Accessibility Guidelines (the application meets the basic requirements: vnímatelnost, ovladatelnost, srozumitelnost, robustnost). |
| **MVP** | MVP | Minimum Viable Product. |
| **IZS** | IRS | Integrovaný záchranný systém — Hasičský záchranný sbor, Policie, Zdravotnická záchranná služba. |
| **zenID** | zenID | Third-party identity-verification SDK (zenID WebSDK) used for OP/ŘP scanning + OCR; **does not store OP on user device**. |
| **ČNR** | Central national register | Mentioned in step 4 of process diagram for driver-data lookup by OP number. (Scope/source TBD next batch.) |
| **RZWS / PSWS** | vehicle-registry / contract-registry web services | Mentioned in step 7 — vehicle data + insurance lookup by SPZ. (Endpoints/contracts TBD next batch.) |
| **SMS Gateway** | SMS Gateway | The service that issues + validates OTP codes for participant phone verification. Specific HTTP error codes documented (e.g. 422 with `N8/2025/01: EX_CHYBA_TELCISLA_NEBO_SMSTEXTU`). |
| **ID hlášení** | report ID | Internal report ID; also exposed as QR for IZS. Created at NEW state. Embedded in completion PDF. |
| **accidentReportStatus** | report state | The wizard's state-machine field. Enumerated values: NEW, IN_PROGRESS_DRIVERS, IN_PROGRESS_VEHICLES, IN_PROGRESS_CIRCUMSTANCES, TO_SIGN, FINISHED, CANCEL, ERROR. |

## §3. Architectural facts (binding for tests)

### §3.1 Mobile-only realisation (page 14/133, §3.2)

> "Aplikace je realizována formou jednotlivých obrazovek pouze pro
> mobilní zobrazení."

**This supersedes the AMENDMENT 2 mobile-first framing — bouracka is
mobile-ONLY**. Desktop access is not a first-class concern of the SUT.
Implication for test viewports:
- **R1 viewport set tightens to** `[320, 375, 414]` px (drop the
  desktop project from R1 spec runs).
- Desktop-rendering tests become R2 sentinel-only ("does the desktop
  render not crash?" smoke).

### §3.2 Browser support (page 14/133)

- Chromium-based ≥ v121
- Safari ≥ v16

Implication: tests should pin Chromium 121+ (Playwright + Cypress) and
include WebKit for Safari coverage at v16+ — Playwright supports
WebKit natively, Cypress does not. **Gate-1 reasoning may flip toward
Playwright** because of WebKit coverage.

### §3.3 Validation timing (page 14/133)

> "Validace se provádí vždy při ztrátě focus na daném poli, případně
> při kliku na tlačítko pro pokračování."

Two-pronged trigger: blur + continue-click. Tests must exercise both.

### §3.4 Manual-fallback always available (page 14/133)

> "Všechna pole aplikace je možné vyplnit manuálně pro dokončení
> procesu — není tedy nutné fotit nehodu, doklad ani SPZ pro dokončení
> hlášení nehody."

Implication for TC-CP-001 (implicit-ID-auth happy):
- Two parallel happy paths: (a) photo+OCR+register-lookup; (b) manual
  entry. R1 should cover **both** as separate sub-cases — likely
  TC-CP-001-A (photo path) + TC-CP-001-B (manual path).
- Source-of-data tracking: "Aplikace uchovává informaci o zdroji údaje
  (automatické dotažení / manuální vyplnění)" — this is an assertable
  contract on submit.

### §3.5 Data persistence model (page 20/133)

> "Data se do DB ukládají průběžně, vždy po potvrzení celé obrazovky
> (moment stisku tlačítka a přechodu na další obrazovku)."

Per-screen-on-continue persistence. **Photos are NOT persisted** — if
session interrupted, photos lost; form data preserved. Recovery via
ID hlášení possible (per state machine + QR).

### §3.6 Field-definition Excel (page 14/133)

> "Logika, vlastnosti a povinnosti jednotlivých polí formulářů jsou
> popsány v definičním excelu zde."

A separate definitive Excel exists (linked from the analytical doc).
**This is gold for TC fixtures + per-field validation rules.** Land
into `_specs/RECON-INPUT-EXTENSIONS-v0.2.md` Template 6 once obtained.
Filed as **OQ-CP-16** below.

### §3.7 Configuration-driven integration skipping (page 25/133)

> "V případě, že aplikace zjistí z konfigurace, že má některé integrace
> přeskakovat, bude příslušné obrazovky hlášení provedeny ihned v
> editačním režimu k provolání dané služby nedojde — Účastník nebude
> o této variantě nijak informován."

**This is the canonical test-mode mechanism.** `tst.*` envs likely
have integrations selectively skipped via this flag. Resolves OQ-CP-14
in principle (reCAPTCHA bypass is one such skip). Test code can
exploit this via env-config attribute `integrations_skip_list: [...]`.

### §3.8 Outage configuration via Azure Blob (page 24/133)

```json
{
  "outages": [{
    "from": "2025-09-13T22:00:00+02:00",
    "to":   "2025-09-21T04:00:00+02:00",
    "warning_before_hours": 2
  }]
}
```

- ISO-8601 datetimes.
- Configurable URL of the outage JSON (Azure Blob).
- Malformed JSON → ignored gracefully (no error surfaced).
- Outage attributes drive: yellow "Plánovaná odstávka" box (in window
  defined by `from − warning_before_hours .. from`), red "Aktuální
  odstávka" box (in `from .. to`), and disable of the
  "VYPLNIT ZÁZNAM" CTA on landing.
- **Outage-active scenario** must be a R1 negatively-ending sub-case
  (TC-CP-002 or TC-CP-004).

### §3.9 Session expiry (page 14/133)

- Configurable session lifetime.
- Session expired during wizard → koncová obrazovka shown; user can
  restart (new ID hlášení).
- Implication for tests: clock-mock or long-wait pattern needed for
  session-expiry sub-case. Defer to R2 unless feasible in tst.*.

### §3.10 Privacy + tracking (page 14/133, page 25/133)

- Google Analytics — initiated on landing + on rozcestník.
- reCaptcha — initiated on rozcestník + used to validate phone-input
  fields on screen 02 (Ověření telefonních čísel).
- "Veškeré chování účastníků je zaznamenáváno pomocí nástroje Google
  analytics" + application logging.

### §3.11 Czech ID-format validation (page 28/133)

- **CZ +420** — phone numbers must start with one of the prefixes from
  the published list `601 .. 608, 702..708, 720..729, 730..739, 770..779,
  790..799` + 6 more digits = 9-digit body. (Full list captured in
  IMG_1045 — see notes section §6 below.)
- **SK +421** — only the 9-digit length condition is enforced.

This converts the CS-locale recon row in scope §4.2 from "TBD" to
**concrete rule**: regex per env config.

## §4. Process flow — the 12-step diagram (page 13/133, §3.1)

```
1.  Bouracka.cz, GDPR, rozcestník
2.  Ověření kontaktů obou řidičů pomocí SMS              (SMS Gateway)
3.  Postupné nafocení OP obou řidičů, OCR data z dokladů (zenID)
4.  Doložení údajů o řidičích dle čísla OP a ČNR
5.  Zaevidování svědků nehody
6.  Postupné nafocení vozidel a definice jejich poškození
7.  Postupné dotahování údajů o vozidlech a pojišťovně
    dle SPZ + RZWS + PSWS                                 (zenID + RZWS + PSWS)
8.  Určení a popis okolností nehody
9.  Dotažení polohy místa nehody, data a času
10. Určení viníka nehody
11. Podpis obou účastníků pomocí autorizační SMS         (SMS Gateway)
12. Generování PDF, odeslání na emaily účastníků
    a pojišťoven; možnost stažení výsledného PDF
    (pro nevyplňující účastník přes QR kód)
```

Grouped into 4 areas:
- **A — Informovanost a ověření telefonních čísel** (steps 1, 2)
- **B — Informace o účastnících a svědcích nehody** (steps 3, 4, 5)
- **C — Nafocení vozidel a popis okolností nehody** (steps 6, 7, 8, 9, 10)
- **D — Souhrn a podpis** (steps 11, 12)

This is the canonical R1 happy-path skeleton for TC-CP-003. The
existing FLW-003 24-step skeleton was directionally correct; areas
A→D align.

## §5. Screen catalogue (pages 14–30/133)

The screen IDs are zero-padded numerical, not free-form names. Updated
SCR-NNN mapping below.

### §5.1 Two-part split (page 15/133, §3.3.2)

- **LandingPage** at `https://www.bouracka.cz` — public marketing.
- **Aplikace** at `https://www.bouracka.cz/formular` — the wizard;
  reachable directly without LandingPage.
- Both share cookies + GA.

### §5.2 Screens identified in this batch

| Internal ID | Title | Our SCR-NNN | Page in doc |
|-------------|-------|-------------|-------------|
| LandingPage / Bouracka.cz | Landing | SCR-001 (existing) | 16–18 |
| FAQ | FAQ | SCR-003 (existing) | 19 |
| Menu | In-app sidebar/hamburger nav | SCR-013 (NEW) | 20 |
| Sdílený záznam | Shared-record view (driver N) | SCR-014 (NEW) | 23 |
| Odstávková obrazovka | Outage screen | SCR-015 (NEW) | 23–24 |
| Cookies lišta | Cookies banner | SCR-016 (NEW) | 21–22 |
| Zpracování osobních údajů | GDPR processing | SCR-005 (existing/deferred — now scoped) | 22 |
| 00_Homepage – Rozcestník | Wizard rozcestník | SCR-002 (existing — re-aligned) | 25 |
| 01_Potvrzení účastníků nehody | Participant count confirmation | SCR-017 (NEW) | 27 |
| 02_Ověření telefonních čísel | Phone OTP verification | SCR-018 (NEW) | 27–29 |
| 03_Nafocení OP a Osobní údaje – účastník A | OP scan + driver A data | SCR-019 (NEW; partial) | 30 |
| QR Kód | QR display (in-wizard) | SCR-020 (NEW component) | 21 |

### §5.3 Significant nuances per screen (paraphrased; for full detail see linked doc pages)

- **00_Rozcestník**: outage banners (yellow=planned, red=active) with
  `From / To / Warning_before_hours` JSON config; 5 sections (immediate
  help, when to call police, the report itself, what to do at small
  accidents, GDPR link); CTA to 01.
- **01_Potvrzení účastníků**: PRE-flight gate — clicks "pokračovat"
  triggers `SMS Gateway PING`; on NOK → ERROR Endpage (no advance);
  on OK → app creates internal ID hlášení (`accidentReportStatus =
  NEW`) + records timestamp + participant count (defaulted to 2).
- **02_Ověření telefonních čísel**: phone-prefix dropdown (CZ +420 / SK
  +421); validated against prefix-list regex; GDPR-consent checkbox
  gates "send code" button activation; SMS sent via Gateway with
  configurable `Platnost SMS v minutách`, `Pokusy na ověření`,
  `Pokusy na znovu odeslání`, `Pokusy na změnu tel. čísla`; loop for
  driver N (different consent path: SMS link); reCaptcha on input
  fields; on success
  `accidentReportStatus = IN_PROGRESS_DRIVERS` + QR code generated
  with Identifikační kód for IZS.
- **03_Nafocení OP a Osobní údaje – účastník A**: zenID WebSDK photo
  scan; OCR; ČNR lookup; data does NOT persist on device (per ČKP
  privacy posture).
- **Cookies lišta**: 2 categories — Technické (povinné, nelze editovat),
  Analytické (lze povolit/zamítnout); buttons Detaily / Povolit vše /
  Nastavení cookies / Odmítnout.
- **Sdílený záznam**: review-only screen for driver N, generated as
  link/QR by driver A on screen 15; default lifetime 60 min
  (configurable); shows form data + PDF download; on reload checks
  `accidentReportStatus` (Nepodepsáno = TO_SIGN, Zneplatněno =
  CANCEL/ERROR, Podepsáno = FINISHED).
- **Menu (in-app)**: section progression — sections become clickable as
  user fills them; "Začít znovu" with native confirmation if
  ID hlášení already created; navigation to filled-screens disabled
  on certain states.

## §6. Czech mobile-prefix list (page 28/133, captured in IMG_1045)

For the CZ +420 validation regex:

```
^(601|602|603|604|605|606|607|608|702|703|704|705|706|719|720|721|722|723|724|725|726|727|728|729|730|731|732|733|734|735|736|737|738|739|770|771|772|773|774|775|776|777|778|779|790|791|792|794|795|797|799)\d{6}$
```

For SK +421: `^\d{9}$`.

This converts TC-CP-001 STEP "phone-input validation" from a soft
"valid CZ phone" to a literal regex assertion.

## §7. Updated R1 / R2 split — no change to release scope, only refinement

The 4 R1 TestTargets remain valid; their `coverage_basis` and step
references tighten:

- **TT-CP-R1-001 — Implicit ID-based authentication via Czech
  governmental registers.** Now precisely scoped to the **screen-03
  zenID OCR + ČNR lookup + auto-fill** mechanism, NOT the phone
  verification (which is a SEPARATE behaviour — a precondition gate).
- **TT-CP-R1-001b (NEW; promote to R1) — Phone-OTP-based participant
  identity gate.** The 02_Ověření telefonních čísel screen has its own
  state machine, its own integration (SMS Gateway), its own
  failure-mode envelope (`SMS_CODE_ATTEMPTS`, `TELEPHONE_NUMBER_COUNT`,
  HTTP 422 EX_CHYBA, PING fail). Per R-CAST-1, this deserves its own
  TT.
- **TT-CP-R1-002 — Wizard happy E2E.** Aligns with 12-step process
  diagram; the four areas A→D map cleanly.
- **TT-CP-R1-003 — Recoverable exceptions.** Now itemisable: SMS
  resend, OTP retry, OCR retry, server timeout retry, location adjust,
  phone-number change.
- **TT-CP-R1-004 — Negatively-ending.** Now itemisable: SMS exhaustion,
  TELEPHONE_NUMBER_COUNT, OP-not-in-ČNR, vehicle-not-in-RZWS, outage
  active, session expiry, eligibility ≥200k Kč, PING fail.

Filed as **OQ-CP-17**: should TT-CP-R1-001 be split into two
(phone-OTP gate + zenID ID-load)? Recommendation: YES, R1 expands
to **5 TTs**.

## §8. New integrations identified

| INT-NNN | Name | Where invoked | Notes |
|---------|------|---------------|-------|
| INT-006 (NEW) | **zenID WebSDK** | screen 03 OP scan, screen 06 vehicle damage photo, screen 07 SPZ scan | OCR + identity confirmation; does not persist OP on device |
| INT-007 (NEW) | **Azure Blob — outage config** | every load of LandingPage, FAQ, /formular | JSON file with `outages[]`; configurable URL; fails-open on bad data |
| INT-002 (existing — refined) | **SMS Gateway** | screen 01 PING + screen 02 issue/validate + screen 11 sign-OTP | Now we know HTTP 422 codes, retry/expiry params, per-field config |
| INT-008 (NEW) | **ČNR — driver lookup** | screen 04 (post screen 03 OP photo) | Czech central national register; lookup by OP number |
| INT-009 (NEW) | **RZWS — vehicle registry** | screen 07 | Vehicle data lookup by SPZ |
| INT-010 (NEW) | **PSWS — insurance contract registry** | screen 07 | Contract/insurer lookup by SPZ |
| INT-001 (existing) | reCaptcha | rozcestník init + screen 02 input fields | Used as bot-defence on phone fields, not just submit |

## §9. New OQs raised by this intelligence

| OQ | Sev | Urg | Pri | Question |
|----|:---:|:---:|:---:|----------|
| OQ-CP-16 | A | A | A | The "definiční excel" referenced on page 14/133 — when can the user provide it? It carries the per-field logic, validation, mandatoriness — which directly drives TC fixtures. Resolve before CP-SUPIN-03 starts. |
| OQ-CP-17 | B | A | A | Should TT-CP-R1-001 split into TT-CP-R1-001a (phone-OTP gate) + TT-CP-R1-001b (zenID/ČNR ID-load)? **Recommendation: YES.** Resolve at next session boundary. |
| OQ-CP-18 | A | A | A | Endpoints + auth posture for ČNR / RZWS / PSWS in `tst.*` — is there a public-facing "stub" the test code can hit, or is the ChainNew a real production-like service? OQ for both happy + negative-mock reference. |
| OQ-CP-19 | B | B | B | The "vyhodnocení nevhodného účastníka" (page 25/133) — what criteria? Geo, browser, userAgent? Drives a possible R2+ negatively-ending sub-case. |
| OQ-CP-20 | C | C | C | Pages 31..133 of the analytical doc — when are subsequent photo batches expected? Drives planning of CP-SUPIN-03..08 spec depth. |

## §10. Direct impact on already-authored artefacts

| Artefact | Change required | Priority |
|----------|-----------------|:--------:|
| `_specs/TESTCASE-SPEC-FORMAT-v0.1.md` | Add §3.5b — `accidentReportStatus` assertion as a first-class step kind hint (every TC tracks the SUT state-machine value at terminal step). | A |
| `recon/TEST-TARGET-CANDIDATES.md` | Apply OQ-CP-17 split (R1 = 5 TTs); add new R2 entries for SCR-013..020. | A |
| `01_TestTargets` (Excel) | Add `state_machine_terminal_state` column referencing `accidentReportStatus`. | A |
| `02_TestCases` (Excel) | Add `state_machine_terminal_state` column; populate with NEW / IN_PROGRESS_DRIVERS / FINISHED / ERROR + sub-reason. | A |
| `specs/TC-CP-001-SPEC.md` | Tighten — happy path is now FROM 00 THROUGH IN_PROGRESS_DRIVERS milestone, with explicit assertions on state-machine value. Add manual-entry sub-case (TC-CP-001-B). | A |
| `specs/TC-CP-002-SPEC.md` | Replace soft mock-404 with the documented errors: SMS_CODE_ATTEMPTS, TELEPHONE_NUMBER_COUNT, HTTP-422 EX_CHYBA. | A |
| `recon/integrations/INT-001..005` | Refine; add INT-006..010 NEW. | A |
| `_specs/RECON-INPUT-EXTENSIONS-v0.2.md` | Add Template 7 — "Per-config-parameter recon" capturing the configurable thresholds (SMS validity, retry counts, frequency limit). | B |
| `env/{tst,tst-demo}.json` | Add `integrations_skip_list[]` config knob; add `outage_config_url` knob; add `phone_validation_prefix_list_cz` block. | B |

## §11. Status

| Item | Value |
|------|-------|
| Document | `recon/ANALYTICAL-DOC-INTELLIGENCE-v0.1.md` |
| Source | IMG_1028..IMG_1047 (20 photos; pages 11–30 of 133) |
| Captured screens | 12 (4 already in scope; 8 NEW) |
| Captured integrations | 4 already in scope (refined) + 5 NEW |
| New OQs | 5 (OQ-CP-16..20) |
| New artefact-update directives | 9 |
| Confidentiality | OK to commit (no secrets; document framing references published-to-tester architecture) |
| Status | v0.1 — first batch transcribed; awaits next batch (pages 31..133) |
