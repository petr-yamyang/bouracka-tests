# Analytical-Document Intelligence — v0.2 (additive over v0.1)

> Adds intelligence from photo batch IMG_1048..IMG_1060 (13 photos;
> pages **31–42** of 133). Combined coverage now: pages 11–42 (32 of
> 133 ≈ 24 %). v0.1 transcript still authoritative for pages 11–30.

## §1. Photo quality assessment (per user request)

**Quality grade: B+ overall — fit for purpose, with minor batch-2 caveats.**

| Aspect | Batch 1 (1028–1047) | Batch 2 (1048–1060) |
|--------|---------------------|---------------------|
| Text legibility | A — sharp, all body text readable | A− — readable with minor strain on a few thumbnails |
| Screenshot clarity (mobile-app cuts in margin) | A — UI is crisp | A — UI cuts excellent (good for selector/label inference) |
| Glare / reflection | minimal | **moderate on IMG_1058 / IMG_1060** (laptop screen reflection bleeds into upper third of frame; partial bleed-through of header text from a different document) |
| Focus | sharp | A− — IMG_1060 is slightly soft from off-axis hold |
| Cropping / framing | full pages | **page break visible on IMG_1058 / IMG_1059** (page 41/133 begins mid-frame; page 42/133 ends mid-frame on the next photo). Pages 41 + 42 readable but require cross-photo stitching by reader |
| HEIC quality | high (~6 MB original; ~400 kB after my downscale-to-1600 pass) | identical |
| Live-Photo `.MOV` companion | present (unused; we only need stills) | present |

**Recommendations for the next batch (operator side):**
1. Hold the device parallel to the screen (orthogonal axis) — reduces
   trapezoidal distortion + reflection on glossy panels.
2. Step half a metre back, fill the frame with one full page only —
   avoids the page-break-mid-frame artefact seen on IMG_1058–1060.
3. Diffuse overhead lighting if possible — the bright source visible at
   top-left of IMG_1059 is the principal glare contributor.
4. Sequence numerically (you already do); next batch starts at
   `IMG_1061` — one photo per page, page numbers in body match your
   sequence.
5. HEIC is fine; if you ever need to send fewer files, JPEG export at
   ~85 % from Photos.app reduces ~6 MB → ~700 kB without legibility
   loss.

**Bottom line:** quality is sufficient to drive the spec refinement
without re-shoots. If a specific page fails to transcribe later, I'll
flag the IMG_NNNN id and we can retake just that one.

---

## §2. New intelligence — pages 31–42

### §2.1 Screen 03 — Nafocení OP a Osobní údaje – účastník A (continuation)

- Two upload paths per OP side: **(a) zenID WebSDK with camera**
  (interactive, SDK guides framing) or **(b) gallery upload**
  (front + back as separate single-photo uploads).
- Camera permission denied → CS error
  *"Přístup k fotoaparátu byl zamítnut. Zkontrolujte prosím nastavení
  prohlížeče a povolení daných služeb."* User returned to upload screen.
- Per-file validation: size + format per configurational rules
  (config-driven; thresholds TBC from definiční excel).
- "Nemůže pořídit fotografie" tlačítko = manual-fallback escape hatch
  (go straight to 04 in editing mode without OCR).
- After both sides uploaded → continue triggers zenID OCR. **Three OCR
  outcomes**:
  - **OK** — proceeds to 04 with auto-fill rendered.
  - **WARNING** — same as OK (proceeds + auto-fill); confidence below
    threshold but app trusts and lets user edit.
  - **NOK** (`ERROR`) — proceeds to 04 in editing mode + popup error.
- Once OP photos uploaded, **back-navigation cannot re-trigger
  extraction** — user can only edit data manually on 04.

### §2.2 Screen 04 — Osobní údaje – účastník A

The decisive auth surface. App calls **AISPOV (SUPIN-hosted service
that proxies ROB + CRR)**:

| OCR outcome | App behaviour at screen 04 entry |
|-------------|-----------------------------------|
| OK or WARNING | Calls AISPOV. ROB+CRR result branches: |
|   ↳ AISPOV `StatusVysledek = OK` | Form pre-filled (full match in ROB+CRR). User can edit. |
|   ↳ AISPOV `StatusVysledek = NENALEZENO`, `SubStatus = OK`, `Komponenta = "ROB"` | Form partially pre-filled (Zenid data only); editing mode. |
|   ↳ AISPOV ERROR / not-found / Komponenta ≠ "ROB" | Empty editing mode. **NO further AISPOV calls for any participant in this report.** |
| NOK (ERROR) | Empty editing mode. User fills manually. May press "načíst údaje z registru" after entering Jméno+Příjmení+DOB+OPnumber+Adresa → triggers AISPOV with same branch logic. |

- **Email is always manual** — never registry-derived.
- If RP data not loaded → "Řidičský průkaz vydal" field is hidden.
- AISPOV call-count is **config-limited** per report (cost + abuse
  control). Editing then save evaluates whether to re-call.
- Save semantics on continue:
  - Pure auto-fill (no edits) → save Zenid+AISPOV data unchanged.
  - Edited → save current (auto-fill + edits combined).
  - Pure manual → save manual only.
- Address auto-completion uses **RUIAN** (Registr územní identifikace,
  adres a nemovitostí).

### §2.3 Screens 05+06 — Účastník N replicas

**Identical flow** to 03 + 04, but for participant N. R1 must run both
to assert the iteration logic + the "no further AISPOV calls" cap if
the first AISPOV failed.

### §2.4 Screen 07 — Svědci nehody

- Optional witness add (multiple).
- Witness can be flagged as "spolujezdec" → app offers participant
  selection.
- Witness CRUD (edit/delete) within screen.
- If no witnesses → PDF gets text "Svědci nebyli vyplněni".
- On continue → **`accidentReportStatus = IN_PROGRESS_VEHICLES`**;
  navigate to 08.

### §2.5 Screens 08–11 — Nafocení nehody + SPZ + 09_Údaje o vozidle (per participant)

**Two-section layout per vehicle:**
- **Fotografie SPZ** — exactly 1 photo, irreversible once OCR'd.
- **Fotodokumentace** with two subsections sharing a max-N config:
  - **Poškození vozidla** — damage photos.
  - **Postavení vozidel při střetu** — collision-position photos.
  - Total photos in both subsections = N (config) − 1 (the SPZ one).

**SPZ flow** (screen 08 part 1):
- zenID WebSDK or gallery upload → zenID API server-side OCR.
- Successful extraction → popup *"Souhlasí načtená SPZ vozidla?"*
  (NE / ANO).
- Confirmed SPZ → saved + photo locked (cannot re-upload for this
  participant; can edit value manually).
- Failed extraction → retry / skip + manual / upload from phone.

**Damage marking** (screen 08 part 2):
- User marks damaged areas on a vehicle outline (8-direction arrows in
  the screenshot; appears to be an SVG-based component).
- Or selects "Vozidlo nebylo poškozeno" — clears any prior markings.
- If neither → continue blocked + CS error.
- Multiple markings allowed simultaneously.
- "Jak se vozidlo A pohybovalo" — predefined movement options to mark.

**Screen 09 — Údaje o vozidle A:**
- App checks: confirmed SPZ exists AND AISPOV still callable per
  config → calls AISPOV with vehicle+insurance lookup.
- Branches:
  - AISPOV success → form pre-filled; user can Upravit (edit; if
    user changes Pojišťovna, Číslo smlouvy + Číslo zelené karty fields
    are hidden) or Potvrdit (confirm).
  - AISPOV partial / error → editing mode without contract+green-card
    fields; user can fill manually.
- Footnote 2 of doc: if AISPOV returns a value not in the app's known
  číselník (codebook), field is left empty and user must fill manually.
- **Back-navigation cannot re-upload SPZ.**
- On continue:
  - More participants? → 10_Nafocení nehody + SPZ – informace o
    vozidle N (replicates 08+09 for participant N).
  - No more participants? → 12_Okolnosti nehody;
    **`accidentReportStatus = IN_PROGRESS_CIRCUMSTANCES`**.
- Save semantics: same 3-case as screen 04 (auto-fill / edited /
  manual).

### §2.6 Refined integration catalogue

| INT-NNN | Name | Where invoked | Fail modes |
|---------|------|---------------|------------|
| INT-001 | reCaptcha | rozcestník init + screen 02 inputs | challenge fails |
| INT-002 | SMS Gateway | screen 01 PING + screen 02 issue/validate + screen 17 sign-OTP | PING NOK; HTTP 422 EX_CHYBA; OTP exhaustion; OTP expiry |
| INT-003 | SMTP | screen 18 e-mail dispatch | non-delivery |
| INT-004 | **AISPOV (SUPIN proxy)** | screen 04 (driver) + screen 09 (vehicle) | StatusVysledek ≠ OK; NENALEZENO ROB; NENALEZENO CRR; per-report call limit reached |
| INT-005 | Maps geocoder | screen 13_Datum, čas a místo nehody | TBC next batch |
| INT-006 | **zenID WebSDK** | screen 03 OP camera + screen 08 SPZ camera + screen 10 vehicle-N | Camera permission denied; OCR NOK |
| INT-007 | **zenID API (server-side)** | screen 03 OP gallery + screen 08 SPZ gallery + screen 10 vehicle-N | OCR NOK |
| INT-008 | **RUIAN** | screen 04 + 06 address fields | autocomplete unavailable |
| INT-009 | **Azure Blob — outage config** | every page load | malformed JSON ignored gracefully |
| INT-010 | **Google Analytics** | rozcestník init + LandingPage init | analytics-cookie-rejected branch |

Note: ČNR (mentioned in batch 1 process diagram as "Doložení údajů o
řidičích dle čísla OP a ČNR") and AISPOV are **the same integration
viewed at different abstraction levels** — ČNR is the legal/regulatory
endpoint name; AISPOV is the SUPIN-hosted service interface that
proxies it. The CRR (Centrální Registr Řidičů) is also part of AISPOV.
Likewise RZWS (vehicle registry) + PSWS (insurance contract registry)
are AISPOV sub-components.

### §2.7 Confirmed accidentReportStatus state machine

```
NEW                          ← screen 01 transition (after SMS PING OK)
  ↓
IN_PROGRESS_DRIVERS          ← screen 02 transition (both phones verified)
  ↓                              [screens 03, 04, 05, 06 do not advance state;
  ↓                               they're internal to the IN_PROGRESS_DRIVERS phase]
IN_PROGRESS_VEHICLES         ← screen 07 transition (witnesses confirmed)
  ↓                              [screens 08, 09, 10, 11 internal]
IN_PROGRESS_CIRCUMSTANCES    ← screen 11 transition (all vehicles done)
  ↓                              [screens 12, 13, 14, 15 internal]
TO_SIGN                      ← screen 15 transition (summary confirmed)
  ↓
FINISHED                     ← screen 18 (after both drivers signed + e-mail dispatched)

  ↘
   CANCEL (user-initiated abort via Začít znovu)
   ↘
    ERROR (terminal failure)
       sub-reasons:
         SMS_CODE_ATTEMPTS    (page 29)
         TELEPHONE_NUMBER_COUNT (page 29)
         + more TBC from pages 43..133
```

---

## §3. R1 split + decomposition (per user direction "split and decomposition")

The new intelligence justifies splitting R1 from 4 → 7 TestTargets,
each narrowly scoped to one **state-machine transition cluster**. This
is a precise decomposition along the SUT's own state machine; the unit
of test isolation matches the unit of business behaviour.

### §3.1 R1 TestTarget list (NEW — supersedes prior R1 set)

| ID | Title (CS / EN) | State transition | Decomposition |
|----|-----------------|------------------|---------------|
| **TT-CP-R1-A1** | Vstupní brána a SMS-PING (screen 01) | → NEW | behaviour: gate-on-sms-gateway-availability |
| **TT-CP-R1-A2** | Ověření telefonních čísel (screen 02) | NEW → IN_PROGRESS_DRIVERS | behaviour: verify-participants-via-otp |
| **TT-CP-R1-B**  | ID-based driver-data load (screens 03..06) — **= "implicit ID-based auth"** per user direction 2026-05-05 | (internal to IN_PROGRESS_DRIVERS) | behaviour: load-driver-data-from-zenid-aispov |
| **TT-CP-R1-C**  | SPZ + vehicle-data load (screens 08..11) | IN_PROGRESS_VEHICLES → IN_PROGRESS_CIRCUMSTANCES | behaviour: load-vehicle-data-from-zenid-aispov |
| **TT-CP-R1-D**  | Okolnosti, datum, místo, viník, souhrn, podpis (screens 12..18) | IN_PROGRESS_CIRCUMSTANCES → TO_SIGN → FINISHED | behaviour: complete-circumstances-and-sign |
| **TT-CP-R1-E**  | Cross-area happy E2E (orchestration) | NEW → FINISHED | behaviour: submit-traffic-accident-record-end-to-end |
| **TT-CP-R1-F**  | Recoverable + irrecoverable failure envelope (cross-area) | any → ERROR (sub-reasons) | behaviour: handle-wizard-exceptions-and-terminations |

This decomposition has the engineering-friendly property: **each TT has
a single responsibility for a small contiguous state-transition window
of the SUT's state machine.**

### §3.2 R1 TestCase enumeration (NEW — 20 TCs)

For each TT, enumerated TCs covering happy + recoverable + negatively-
ending sub-cases. Each TC pairs with at least one failure peer per
R-FAIL-1.

```
TT-CP-R1-A1 (SMS PING):
  TC-CP-001  Happy        — PING OK → state = NEW
  TC-CP-002  Negative     — PING NOK → ERROR endpage; no state change

TT-CP-R1-A2 (Phone OTP):
  TC-CP-003  Happy        — both phones verified → IN_PROGRESS_DRIVERS
  TC-CP-004  Negative     — SMS_CODE_ATTEMPTS exhausted → ERROR/SMS_CODE_ATTEMPTS
  TC-CP-005  Negative     — TELEPHONE_NUMBER_COUNT exceeded → ERROR/TELEPHONE_NUMBER_COUNT
  TC-CP-006  Negative     — SMS Gateway HTTP 422 EX_CHYBA → inline error, no advance
  TC-CP-007  Recoverable  — invalid OTP → 1 retry → success → IN_PROGRESS_DRIVERS

TT-CP-R1-B (Driver ID load):
  TC-CP-008  Happy        — zenID OK + AISPOV ROB OK → form pre-filled
  TC-CP-009  Recoverable  — zenID NOK → manual fill → AISPOV button → ROB OK → pre-fill
  TC-CP-010  Negative     — AISPOV NENALEZENO ROB → editing mode + no further AISPOV
  TC-CP-011  Recoverable  — camera-permission-denied → gallery-upload path → success

TT-CP-R1-C (Vehicle SPZ load):
  TC-CP-012  Happy        — zenID SPZ OK + AISPOV vehicle+insurance OK
  TC-CP-013  Recoverable  — zenID NOK → upload from gallery → success
  TC-CP-014  Negative     — AISPOV vehicle missing → editing mode without contract/green-card

TT-CP-R1-D (Circumstances + sign):
  TC-CP-015  Happy        — full sign flow → FINISHED + 2 e-mails dispatched
  TC-CP-016  Negative     — sign-OTP exhaustion → ERROR
  TC-CP-017  Recoverable  — submit timeout → retry → FINISHED

TT-CP-R1-E (E2E orchestration):
  TC-CP-018  Happy        — full happy E2E (NEW → FINISHED across all areas)

TT-CP-R1-F (Failure envelope):
  TC-CP-019  Negative     — outage active → CTA disabled on landing
  TC-CP-020  Negative     — Eligibility self-disclosure mid-wizard → terminate
```

R-FAIL-1 satisfied across all TTs (every happy paired with ≥ 1
failure).

### §3.3 R2+ identified-but-deferred (refined)

Confirmed R2+ surfaces:
- **TT-CP-R2-COOKIE** Cookie banner first-visit + reject-all path
- **TT-CP-R2-OUTAGE** Yellow-warning-box pre-outage rendering (within
  `from − warning_before_hours` window) — separate from R1-F outage
  active
- **TT-CP-R2-SHARED** Sdílený záznam screen for participant N (the
  link/QR generated on screen 15 with 60 min default lifetime)
- **TT-CP-R2-MENU** In-app sidebar/hamburger menu state-aware
  navigation
- **TT-CP-R2-FAQ** /faq taxonomy + accordion smoke
- **TT-CP-R2-LANDING** Landing-page marketing surface smoke
- **TT-CP-R2-HEADER** Header / hamburger cross-page component
- **TT-CP-R2-GDPR** /formular/personal-data static page
- **TT-CP-R2-WITNESS** Svědci nehody screen with passenger marking
  (the witness UI is mid-wizard — could arguably be R1 inside TT-CP-R1-D,
  but per user "release 1 covers just these scenarios" we keep it R2
  unless info forces otherwise)
- **TT-CP-R2-SHARE-LINK** Sdílený záznam link expiry handling
- **TT-CP-R2-DEMO-RELAX** DEMO env's "reduced validation" surface
  (per scope C-5; needs comparison against tst.bouracka.cz baseline)

### §3.4 Acceptance criteria refinement (binding)

Every R1 TC must now also assert at terminal step:
- `accidentReportStatus` value matches expected.
- Sub-reason populated when state = ERROR.
- `data_source` annotation per saved field — one of `zenid` /
  `aispov` / `manual` / `mixed` (per page-35/133 save semantics).

Filed as TestCase-spec-format addendum in §6 below.

---

## §4. New OQs raised in this batch

| OQ | Sev | Urg | Pri | Question |
|----|:---:|:---:|:---:|----------|
| OQ-CP-21 | A | A | A | The "definiční excel" mentioned on page 14/133 — when can the user provide it? Drives field-level validation rules + max-N photo configs + AISPOV call cap + SMS retry counts. Same theme as OQ-CP-16; restated to remind. |
| OQ-CP-22 | A | B | A | AISPOV endpoint shape — concrete WSDL/OpenAPI for ROB + CRR + vehicle + insurance lookups. Required for mock-respond posture in tests. |
| OQ-CP-23 | A | B | A | zenID WebSDK + zenID API integration contracts — what are the OK/WARNING/NOK response shapes the app expects? |
| OQ-CP-24 | B | B | B | "Předem domluvená response pro neúspěšné vytěžení/chybu" (page 37) — what is the agreed-upon error shape from zenID? |
| OQ-CP-25 | B | C | C | Damage-marking widget on screen 08 — is it an SVG-based vehicle outline component? Needs a stable test-id contract. |
| OQ-CP-26 | C | B | C | The "vyhodnocení nevhodného účastníka" (page 25/133) — restating OQ-CP-19; criteria to be confirmed. |

---

## §5. Direct artefact-update directives (binding for v0.2 of TestPlan)

| Artefact | Change |
|----------|--------|
| `01_TestTargets` (Excel) | Replace 11 rows with 7 R1 + ≥ 11 R2 (TT-CP-R1-A1..F + TT-CP-R2-…); add `state_machine_terminal_state` column. |
| `02_TestCases` (Excel) | Replace 4 rows with 20 R1 TCs (TC-CP-001..020); add `state_machine_terminal_state` + `state_error_subreason` columns. |
| `recon/TEST-TARGET-CANDIDATES.md` | Update to rev 3 reflecting R1 split. |
| `_specs/TESTCASE-SPEC-FORMAT-v0.1.md` | Add §3.5b — `accidentReportStatus` + `data_source` annotations as required terminal-step assertions. |
| `recon/integrations/INT-006..010` | Author NEW. |
| `recon/screens/SCR-005..020` | Author NEW (or stub) per the screen catalogue. |

Per-TC SPEC.md authoring (TC-CP-001..020 × full format) is **deferred
to CP-SUPIN-03 prep** — the 20-TC enumeration with the state-machine
mapping is the spec-shape input that lets a Sonnet dev session emit
the framework code over the next sessions, with each session producing
4–5 SPEC.md files.

---

## §6. Status

| Item | Value |
|------|-------|
| Document | `recon/ANALYTICAL-DOC-INTELLIGENCE-v0.2.md` |
| Source | IMG_1048..IMG_1060 (13 photos; pages 31–42 of 133) |
| Total coverage now | pages 11–42 (24 % of doc) |
| New screens identified | 03, 04, 05, 06, 07, 08, 09, 10 (8 wizard screens, 7 of which are R1-relevant) |
| New integrations | INT-006 zenID WebSDK, INT-007 zenID API, INT-008 RUIAN, INT-009 Azure Blob outage, INT-010 GA — refined; AISPOV (INT-004) re-anchored as the canonical proxy for ROB + CRR + vehicle + insurance |
| accidentReportStatus | confirmed states + transitions per §2.7 |
| R1 TestTargets | 7 (A1, A2, B, C, D, E, F) — 3 more than v0.1 |
| R1 TestCases | 20 (TC-CP-001..020) — 16 more than v0.1 |
| New OQs | 6 (OQ-CP-21..26) |
| Status | v0.2 — additive over v0.1; ready for Excel rev 4 |
