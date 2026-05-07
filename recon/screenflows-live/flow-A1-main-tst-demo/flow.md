# Flow A1 — Main happy path — DEMO Bouračka — live capture

> **Source.** Live navigation through `demo.bouracka.cz/formular/`
> driven via Claude in Chrome on 2026-05-06 ~10:08–10:15 CET (Tier 2a).
> **Operator:** Petr Žemla. **Captor:** Cowork Opus.
> **Status:** in-progress; phases 0–1 captured, phases 2–4 pending.

---

## §0. Identity

| Item | Value |
|------|-------|
| Flow ID | `flow-A1-main-tst-demo` |
| Description | Single-driver fills accident record on DEMO; both participants Czech IDs; ≤200 000 Kč damage; no injuries |
| Env | `demo.bouracka.cz` (DEMO public; Tier 2a) |
| Sibling flow | `flow-A1-main-tst` (PROD; Tier 2b; photo-driven; pending) |
| Capture session | 2026-05-06 morning |
| Operator viewport | desktop 1568×688 (Chrome on Windows ThinkPad) |
| Capture method | Claude in Chrome (DOM read_page + network read + screenshot) |

## §1. Architecture observed

### §1.1 Frontend stack (inferred from bundle names)

- **Build tool**: Vite (hashed asset names: `informations-D1Jrhrhq.js`, `index-CZZXqFaQ.js`, `VerifyCode-nIV1di_B.js`, etc.)
- **Component framework**: React (probable)
- **State / data fetching**: TanStack Query (inferred from `useIsFetching-DxOtLLvl.js`)
- **Schema validation**: **Zod** (`zod-DVe_3Twt.js`)
- **UI primitives**: likely Material UI / similar (`MenuItem-CdZsV3Vk.js`, `FormCheckbox-CR7ygL4S.js`)
- **Per-route lazy chunks**: confirmed (each route loads its own bundle)

### §1.2 Backend API surface (discovered so far)

Base: `https://demo.bouracka.cz/api/`

| Verb | Path | Purpose | Status |
|------|------|---------|--------|
| `POST` | `/api/reports` | create new report; returns UUID | 200 |
| `GET` | `/api/reports/{uuid}` | fetch report state | 200 |
| `GET` | `/api/reports/{uuid}/completenessStatus` | per-section completeness | 200 |
| `GET` | `/api/reports/{uuid}/participantsInVerification` | verification phase state | 200 |

**Implication.** Each fresh visit to the rozcestník + click-through
mints a new report UUID (server-generated). Test automation MUST
either ride along with whatever UUID the API returns, OR pre-create
a report via direct API and hand the UUID to the SPA via deep-link
(`/formular/report/{uuid}/verification` is the format).

### §1.3 Routes observed

| Route | Screen | Dependency |
|-------|--------|-----------|
| `/formular` (rozcestník) | gateway: emergency / police / fill-record | ANY user |
| `/formular/personal-data` | GDPR / personal-data processing notice | static |
| `/formular/informations` | pre-wizard "Co vás čeká?" intro | post-CTA-click; NOT a wizard step |
| `/formular/report/{uuid}/verification` | wizard phase 1 — phone verification | post-`POST /api/reports` |
| `/formular/report/{uuid}/<phase 2..>` | TBC | TBC |

### §1.4 Third-party integrations observed

| INT-ID candidate | Integration | Where | Notes |
|------------------|-------------|-------|-------|
| **INT-NEW-Azure-Outages** | Azure Static Web Apps — outage feed | `https://bourackaodstavky78861.z6.web.core.windows.net/odstavky.json` | called twice on rozcestník + once after CTA click; outage banner driven from this feed |
| **INT-NEW-GoogleMaps** | Google Maps JavaScript API | `https://maps.googleapis.com/maps-api-v3/api/js/64/11d/intl/en_gb/{common,map,util}.js` | locale forced to `en_gb`; **CS locale violation candidate** |
| INT-001 reCAPTCHA v3 | site key `6Lfbao4sAAAAANfSk_-NcqLZPYB8wdMvrBS4qM5p` | Google reCAPTCHA | observed `clr` POST returned 503 (non-blocking) |
| INT-002 N8 SMS Gateway | **DEMO MOCKED** — does not dispatch SMS | per page hint | confirmed Δ1 |

## §2. Phase-by-phase capture

### Phase 0 — Rozcestník (`/formular/`)

- **URL:** `https://demo.bouracka.cz/formular/`
- **Title:** "ČKP - Bouračka"
- **Identity heading:** "Stala se vám dopravní nehoda? To zvládnete."
- **DEMO banner** (orange, persistent, header-stuck):
  > "Nacházíte se v DEMO VERZI aplikace. Všechny údaje v této verzi
  > jsou pouze ukázkové. Formulář si můžete bezpečně vyzkoušet bez
  > zadávání reálných údajů."
- **Three rozcestník cards:**
  1. "Potřebujete okamžitou pomoc?" → `tel:112`
  2. "Kdy volat Policii ČR?" → expandable; reveals 7 criteria + `tel:158`
  3. "Záznam o dopravní nehodě" → R1 entry → CTA "VYPLNIT ZÁZNAM"
- **R1-scope copy** (verbatim, on card 3):
  > "Vhodné pro malé nehody bez zranění a škody do 200 000 Kč vzniklé
  > mezi 2 účastníky s českými občanskými průkazy."
- **Safety bullets** ("CO DĚLAT PŘI NEHODĚ?"):
  1. "Zapněte výstražná světla a oblékněte si reflexní vestu"
  2. "Zabezpečte místo nehody výstražným trojúhelníkem (50 m za vozidlo, na dálnici 100 m)"
  3. "Pokud je někdo zraněn, volejte 112"
- **Police-criteria** (revealed on expand):
  1. "Někdo je zraněný nebo došlo k úmrtí"
  2. "Škoda na některém vozidle včetně přepravovaných věcí přesahuje 200 000 Kč"
  3. "Došlo ke škodě na majetku 3. osoby (u služebních či leasingových vozidel policii volat nemusíte)"
  4. "Je poškozené nebo zničené obecně prospěšné zařízení (semafor, značka, svodidla apod.)"
  5. "Účastníci nehody nejsou schopni zajistit plynulost provozu"
  6. "Viník od nehody ujel nebo nespolupracuje"
  7. "Došlo ke srážce se zvěří"
- **reCAPTCHA badge**: bottom-right, present
- **Hamburger menu**: top-right (button "menu")
- **Privacy link**: `/formular/personal-data`
- **Network on first load**:
  - 2× `bourackaodstavky78861.z6.web.core.windows.net/odstavky.json`
  - 3× Google Maps JS bundles (`common.js` + `map.js` + a CSP test ping)

### Phase A — "Co vás čeká?" intro (`/formular/informations`)

This screen was **not** in the photo-driven recon. It's a pre-wizard
intro that the operator must dismiss before the wizard mounts.

- **URL:** `/formular/informations` (route bundle: `informations-D1Jrhrhq.js`)
- **Heading:** "Co vás čeká?"
- **Info box (blue):** "Formulář vyplňuje vždy jen jeden účastník.
  Potvrzení obdrží oba účastníci e-mailem."
- **Section "Jak probíhá online záznam o nehodě?"** lists 5 steps
  (4 phases + "Hotovo" terminal):
  1. **Telefonní čísla** — "Ověříme telefonní čísla obou účastníků."
  2. **Základní údaje** — "Vyplníte osobní a technické údaje potřebné k záznamu."
  3. **Fotografie a popis nehody** — "Vyfotíte poškození obou vozidel a krátce popíšete situaci."
  4. **Potvrzení** — "Každý z účastníků obdrží SMS s ověřovacím kódem pro podpis záznamu."
  5. **Hotovo** — "Záznam dostanou oba účastníci e-mailem a bude i ke stažení jako PDF."
- **Progress bar**: 4 segments visible, all empty (wizard hasn't started)
- **CTA**: "Rozumím" (acknowledgement; advances to phase 1)
- **Wizard taxonomy correction**: the photo-driven D00..D17 numbering
  encoded too-fine granularity. The SPA presents **4 phases** with
  internal sub-screens. Excel `01_TestTargets` should be migrated
  toward 4 phases × N sub-screens.

### Phase 1 — Verification (`/formular/report/{uuid}/verification`)

- **Trigger.** Click "Rozumím" on Phase A. Side effects:
  - `POST /api/reports` → returns new UUID, e.g. `ad84a45e-ae72-442d-babf-eed9badd898f`
  - SPA navigates to `/formular/report/{uuid}/verification`
  - SPA fetches `/api/reports/{uuid}` and `/api/reports/{uuid}/completenessStatus` and `/api/reports/{uuid}/participantsInVerification` to hydrate state
- **URL:** `/formular/report/ad84a45e-ae72-442d-babf-eed9badd898f/verification`
- **Heading:** "Ověřte účastníky nehody"
- **Body copy** (verbatim, three paragraphs):
  > "Ověřte telefonní čísla obou účastníků nehody pomocí kódu, který
  > vám postupně zašleme v SMS."
  >
  > "Čísla budou následně sloužit i pro zaslání kódu pro podpis záznamu."
  >
  > "Pokud nedojde k závěrečnému oboustrannému potvrzení, všechna
  > zadaná data včetně kontaktů budou smazána bez uložení."
- **Section heading:** "Účastník A (ten, který vyplňuje hlášení)"
- **DEMO HINT BOX (yellow/orange)** — KEY:
  > "Zadejte libovolné české nebo slovenské mobilní telefonní číslo.
  > Demoverze žádné SMS neodesílá, potvrzovací kód bude v dalším
  > kroku automaticky doplněn."
- **Form fields:**
  - `Předvolba` (combobox) — default `+420` with CZ flag SVG; CZ + SK selectable per hint
  - `Napište číslo účastníka A` (textbox, type=tel)
  - Format hint: `Formát čísla: 608 323 999`
  - GDPR checkbox: "Seznámil/a jsem se s poučením o zpracování osobních údajů" with link to `/formular/personal-data`
  - Submit button: "Odeslat kód"
- **Progress bar**: phase 1 segment now active (1/4 highlighted)

#### Phase 1 — known unknowns (TBC by continuing the walk)

- What does `Odeslat kód` do? (probable: `POST /api/reports/{uuid}/verification/sendCode` or similar)
- Does the OTP screen auto-fill (per DEMO hint)?
- Does the participant-B verification screen come immediately, or only after participant-A is done?
- Slovak number support — does `+421` actually work or is it just claimed?

## §3. Δ matrix updates from this capture

| Δ row | Status update |
|-------|--------------|
| Δ1 (N8 SMS gateway) | **CONFIRMED on DEMO**: zero SMS dispatched; OTP auto-injected on next screen (per DEMO hint) |
| Δ11 (DEMO branding) | already confirmed; banner copy verbatim recorded above |

## §4. Live-copy-strings additions queued (write to `fixtures/live-copy-strings.yaml`)

- STR-006 — Phase A intro heading "Co vás čeká?"
- STR-007 — Phase A info-box "Formulář vyplňuje vždy jen jeden účastník…"
- STR-008 — Phase A 5-step list (each entry as own STR)
- STR-009 — Phase A CTA "Rozumím"
- STR-010 — Phase 1 heading "Ověřte účastníky nehody"
- STR-011 — Phase 1 body para 1 ("Ověřte telefonní čísla…")
- STR-012 — Phase 1 body para 2 ("Čísla budou následně…")
- STR-013 — Phase 1 body para 3 (data-deletion warning)
- STR-014 — Phase 1 DEMO hint ("Zadejte libovolné české nebo slovenské…") — DEMO-only string
- STR-015 — Phase 1 phone format hint "Formát čísla: 608 323 999"
- STR-016 — Phase 1 GDPR consent label
- STR-017 — Phase 1 submit button "Odeslat kód"

## §5. New TC candidates from phases 0+A+1

| Candidate | What it asserts |
|-----------|-----------------|
| TC-CP-NEW-A | rozcestník copy integrity (heading + 3 card titles + safety bullets) |
| TC-CP-NEW-B | R1 scope-sentence verbatim |
| TC-CP-NEW-C | DEMO banner present on DEMO; absent on PROD |
| TC-CP-NEW-D | Police-criteria expand interaction (7 bullets visible after expand) |
| TC-CP-NEW-E | `/formular/informations` intro renders before wizard mount |
| TC-CP-NEW-F | `POST /api/reports` returns UUID-v4 in expected envelope |
| TC-CP-NEW-G | `/formular/report/{uuid}/verification` deep-link works (skip the intro) |
| TC-CP-NEW-H | Phase 1 form: Slovak `+421` predvolba selectable + valid number accepted |
| TC-CP-NEW-I | Phase 1 form: GDPR checkbox is required (submit blocked if unchecked) |
| TC-CP-NEW-J | Phase 1 DEMO hint absent on PROD (PROD MUST send real SMS) |

### Phase 1 (post-submit) — OTP entry for Participant A

- **Trigger.** Submit Phase-1 form. Side effects:
  - `PUT /api/reports/{uuid}/reporter` (200) — saves reporter (participant A) phone
  - `POST /api/reports/{uuid}/participants/{participantA-uuid}/sendCodeToVerify` (200)
  - `GET /api/reports/{uuid}/participantsInVerification` (200)
  - reCAPTCHA `clr` POST returned 503 (non-blocking)
- **Participant A UUID assigned**: `d9422397-15bb-4c9c-9b05-0249a435ede8`
- **URL stays at** `/formular/report/{uuid}/verification` (sub-state via SPA, not URL change)
- **Heading body now reads**: "Zadejte ověřovací kód, který jsme odeslali na číslo **+420 608 123 456.**"
- **DEMO hint refines**:
  > "Do tohoto pole se vkládá kód, který je v provozní verzi zasílán
  > do SMS. Pokračujte stisknutím Ověřit"
- **OTP input**: 4 separate `input[type=tel]` boxes (React-controlled; auto-IDs `«rh»..«rk»`); placeholder labels "1, 2, 3, 4" persist visually even when filled — no separate placeholder attribute, just low-contrast styling
- **Submit**: "Ověřit" button (no GDPR checkbox second time)
- **Footer link**: "NEMŮŽETE ZADAT KÓD?" (escape-hatch — TBC what it does)
- **DEMO accepts ANY 4-digit code.** Tested with `1234` — server returned 200 on `POST /api/reports/{uuid}/participants/{participantA-uuid}/verify`.
- **Massive media pre-fetch.** After clicking `Rozumím` on intro, the SPA pre-fetched **20 video assets** (3 quality tiers × 6 tutorials):
  - `bouracka-screen-spz1.{low,med,full}.mp4`
  - `bouracka-screen-spz2.{low,med,full}.mp4`
  - `bouracka-screen-op-predni1.{low,med,full}.mp4`
  - `bouracka-screen-op-predni2.{low,med,full}.mp4`
  - `bouracka-screen-op-zadni1.{low,med,full}.mp4`
  - `bouracka-screen-op-zadni2.{low,med,full}.mp4`
  - These are the DEMO's instructional-video substitutes for ZID/OCR (per Δ5).

### Phase 1 — Participant B verification

- **Submit-A → next form is Participant B**. Identical shape; **GDPR checkbox absent the second time** (one consent covers both).
- **Endpoint**: `POST /api/reports/{uuid}/participants` (200) — creates B as a regular participant (vs A which used `PUT /reporter`).
- **Participant B UUID assigned**: `7d9500c1-1232-48be-8416-d35dc2b42d37`.
- **OTP for B**: tested with `5678` — accepted. `POST .../participants/{B-uuid}/verify` returned 200.
- After B verifies, `POST /api/session/refresh` fires (security/auth-token rotation on phase boundary).

### Phase 1 — Verification success (`/formular/report/{uuid}/verification/success`)

- **URL**: `/formular/report/{uuid}/verification/success`
- **Both pills**: "+420 608 123 456 ✓ Ověřeno" and "+420 608 987 654 ✓ Ověřeno"
- **CTA**: "Přejít na informace o nehodě" → links to `/formular/report/{uuid}/documents/{participantA-uuid}` (note: per-participant-keyed URL)
- **Police/IZS modal** (DOM-present, hidden behind a button):
  - Heading: "Záznam pro Policii ČR nebo IZS"
  - Copy: "Na vyžádání ukažte identifikační kód a QR kód příslušníkům Policie ČR nebo záchranných složek."
  - **Identifikační kód**: `111111-26-0000001` — format `XXXXXX-YY-NNNNNNN` (6-digit prefix; 2-digit year; 7-digit sequence). The `111111` prefix appears DEMO-specific. New TT candidate.
- New header icon (4-dot grid) appears post-verification — likely opens this police/IZS modal.

### Phase 2 — Documents / OP (`/formular/report/{uuid}/documents/{participantA-uuid}`)

- **URL pattern**: `/formular/report/{report-uuid}/documents/{participant-uuid}` (per-participant-keyed)
- **Heading**: "Údaje o účastníkovi A s číslem +420 608 123 456"
- **Subtitle**: "Pro ověření totožnosti načtěte údaje z obou stran občanského průkazu"
- **DEMO hint**: "V Demo verzi je nahrazeno instruktážním videem." (Δ5 zenID/OCR confirmed mocked)
- **Two camera-icon cards**: PŘEDNÍ STRANA (front) + ZADNÍ STRANA (back) — each is a `button[type=file]` for camera/upload binding
- **Privacy note**: "Údaje se neuloží do Vašeho telefonu, pouze se načtou do záznamu o nehodě. Pokud nebude možné údaje načíst, můžete je vyplnit ručně."
- **CTAs**:
  - "POKRAČOVAT" (greyed/disabled until both sides scanned)
  - "VYPLNIT ÚDAJE RUČNĚ" (manual entry escape-hatch — chosen for this session)

### Phase 2 — Manual fallback form (`/formular/report/{uuid}/documents/{participantA-uuid}/manual?validate=false`)

- **Critical automation hook**: `?validate=false` query param. Bypasses strict OCR-data validation. The corresponding OCR-success URL likely uses `?validate=true`. **TCs can deep-link to either path with synthetic data.**
- **Heading**: "Údaje o účastníkovi A s číslem +420 608 123 456"
- **Subtitle**: "Zkontrolujte osobní údaje účastníka"
- **DEMO hint**: "Zobrazené údaje jsou pouze ukázkové. Není potřeba zadávat vaše skutečné osobní údaje."
- **Section: Osobní údaje** (5 fields)
  - `Jméno` (text)
  - `Příjmení` (text)
  - `Číslo OP` (text — Czech ID-card number)
  - `Datum narození` (text + date-picker; `DD.MM.YYYY` placeholder)
  - `E-mail` (email)
- **Section: Adresa** (1 field + manual fallback)
  - `Vaše adresa` — **combobox** (suggests an address-autocomplete integration; likely RUIAN — Czech address registry — TO CONFIRM in Phase 3 capture)
  - Button: "Zadat adresu manuálně" (manual fallback)
- **Section: Řidičský průkaz** (driving license)
  - **DEMO hint**: "V Demo verzi načtení údajů z registru řidičů neprobíhá, údaje zadejte manuálně." (Δ-NEW: driver-registry mocked)
  - Button: "Načíst z registru řidičů" (loads from drivers' registry — AISPOV/CRR call)
  - `Číslo řidičského průkazu` (text — format hint: `Číslo ŘP najdete na přední straně dokladu a má tvar XY 000000.` → regex `^[A-Z]{2} \d{6}$`)
  - `Skupiny řidičských oprávnění` (combobox — codelist)
- **Submit**: "Potvrdit"
- **Endpoints fetched**: `GET /api/reports/{uuid}/participants/{participantA-uuid}` (load full participant)
- **New bundles**: `manual-BA4ODE-G`, `UserDataPage-CFn6m5y1`, `Row-CfmzZE_1`, `addressFormatter-BUKVLbbz`, `EditRounded-Be9Irwty`, `FormDatePicker-BTisidzY`, `DesktopDatePicker-VnsEbIlP`, `transformEmptyStrings-BGcTUKvZ`

## §3. Δ matrix updates from this capture

| Δ row | Status update |
|-------|--------------|
| Δ1 (N8 SMS gateway) | **CONFIRMED** — DEMO accepts any 4-digit OTP; no SMS dispatched at any point |
| Δ5 (ZID / zenID OCR) | **CONFIRMED** — DEMO replaces with instructional video; manual-entry fallback always available |
| Δ11 (DEMO branding) | already confirmed |
| Δ-NEW27 | **Driver-registry** (AISPOV CRR) mocked on DEMO — only manual entry; "Načíst z registru řidičů" button presumably no-ops or stubs |
| Δ-NEW28 | **Address registry** (RUIAN suspected) — TBC; combobox suggests live autocomplete |
| Δ-NEW29 | **Identifikační kód** prefix `111111-` may be DEMO-marker; PROD likely uses different prefix |
| Δ-NEW30 | **Police/IZS QR-code modal** — universally accessible from header post-verification — TC candidate |

## §4. Live-copy-strings additions queued (write to YAML)

- Phase 1 post-submit: STR-018..STR-025 (OTP-screen body + hint variants + "Ověřit" + "NEMŮŽETE ZADAT KÓD?")
- Phase 1 success: STR-026..STR-028 (success-pill "Ověřeno" + CTA "Přejít na informace o nehodě")
- Phase 2: STR-029..STR-040+ (OP screen heading + camera buttons + manual-fallback + 12 form labels + driver-registry hint)

## §5. Mockoon profile — IMPACT

The current Mockoon profile (`mockoon/n8-sms-gateway.json`) was authored
to mock N8 with a fixed OTP `1234`. **DEMO behaviour is different**:
DEMO's backend accepts ANY 4-digit OTP via its own `POST .../verify`
endpoint. So:

- Mockoon stays useful for **PROD-mode testing** where N8 is the
  real gateway and we want to swap in a mock.
- Mockoon is NOT NEEDED for DEMO-mode testing — DEMO is its own mock.
- TC-CP-005 should split:
  - `TC-CP-005-DEMO`: just submit any 4-digit code; assert 200
  - `TC-CP-005-PROD-with-mock`: route to Mockoon, fixed code `1234`
  - `TC-CP-005-PROD-real-N8`: blocked until N8 sandbox lands (OQ-CP-27)

## §6. New TC candidates from phases 0–2

| Candidate | What it asserts |
|-----------|-----------------|
| TC-CP-NEW-A | rozcestník copy integrity |
| TC-CP-NEW-B | R1 scope-sentence verbatim |
| TC-CP-NEW-C | DEMO banner present on DEMO; absent on PROD |
| TC-CP-NEW-D | Police-criteria expand interaction |
| TC-CP-NEW-E | `/formular/informations` intro renders pre-wizard |
| TC-CP-NEW-F | `POST /api/reports` returns UUID-v4 in expected envelope |
| TC-CP-NEW-G | `/formular/report/{uuid}/verification` deep-link works |
| TC-CP-NEW-H | Phase 1 form: Slovak `+421` predvolba selectable + valid number accepted |
| TC-CP-NEW-I | Phase 1 form: GDPR checkbox is required for participant A; absent for B |
| TC-CP-NEW-J | Phase 1 DEMO hint absent on PROD (PROD MUST send real SMS) |
| TC-CP-NEW-K | Data-purge-on-abandon (per Phase 1 disclaimer copy) |
| TC-CP-NEW-L | Outage-feed reachable; outage banner state matches feed |
| TC-CP-NEW-M | Map locale `cs` not `en_gb` (defect candidate) |
| TC-CP-NEW-N | `POST /api/reports` is rate-limited (anti-abuse) |
| TC-CP-NEW-O | DEMO accepts ANY 4-digit OTP (smoke for the bypass behaviour) |
| TC-CP-NEW-P | PROD rejects an arbitrary 4-digit OTP (negation of NEW-O) |
| TC-CP-NEW-Q | Identifikační kód `XXXXXX-YY-NNNNNNN` format integrity |
| TC-CP-NEW-R | Police/IZS QR modal accessible from header post-verification |
| TC-CP-NEW-S | Phase 2 manual-entry deep-link: `?validate=false` parameter respected |
| TC-CP-NEW-T | Phase 2 driver-registry button: DEMO no-ops; PROD calls AISPOV CRR |
| TC-CP-NEW-U | Phase 2 address autocomplete (RUIAN): minimum 3 chars triggers; results returned |
| TC-CP-NEW-V | Phase 2 ŘP-number validation: regex `^[A-Z]{2} \d{6}$` enforced |
| TC-CP-NEW-W | Phase 2 birth-date format `DD.MM.YYYY` enforced |
| TC-CP-NEW-X | Pre-wizard 20-video pre-fetch is non-blocking (no Phase-1 form lockup) |

## §7. Status

| Item | Value |
|------|-------|
| Flow folder | `recon/screenflows-live/flow-A1-main-tst-demo/` |
| Phases captured | 0 (rozcestník), A (intro), 1 (full — A+B verified + success), 2 (Documents intro + manual-fallback form schema) |
| Phases pending | 2 (post-submit), 3 (Fotografie a popis), 4 (Potvrzení) + Phase 2 for participant B |
| Network endpoints discovered | 4 internal `/api/reports*` + 4 added (sendCodeToVerify, verify, participants POST, session/refresh) + `GET .../participants/{id}` + 2 third-party (Azure outages, Google Maps) |
| Routes mapped | 7 confirmed |
| Bundles observed | 17 distinct |
| Status | v0.2 — phase 0–2 captured; flow extends in next live-walk session |

### Phase 2.5 — Witnesses (`/witness`)

- **NEW PHASE not in 4-step intro list**. URL: `/formular/report/{uuid}/witness`.
- Heading: "Máte svědky nehody?"
- Body: "Můžete přidat celkem 3 svědky. Mohou to být kolemjdoucí nebo spolujezdci."
- CTAs: "Přidat svědka nehody" (add) + "Pokračovat bez svědků" (skip — chosen)
- Endpoint: `GET /api/reports/{uuid}/witnesses` (called twice on mount)

### Phase 3 — Photos `/accident/{participantUuid}` (per participant)

- URL pattern: `/formular/report/{reportUuid}/accident/{participantUuid}`
- Heading: "Focení vozidla A" (or B)
- DEMO hint: "V Demo verzi je nahrazeno instruktážním videem. Prostřednictvím údajů získaných z SPZ jsou v provozn..." (PROD uses SPZ to look up registry; DEMO substitutes with instructional video — Δ confirmed)
- Two photo categories:
  - **Fotografie SPZ (0/1)** — 1 photo of license plate
  - **Fotodokumentace (0/8)** — 8 photo slots (damage close-up + situational positioning)
- 3 file-input buttons (front-camera, rear-camera, file-upload)
- Pre-loaded SVGs: car_front, car_rear, car-damage, cars-accident
- CTAs: "Pokračovat" + "POKRAČOVAT BEZ FOTOGRAFIÍ" (skip — chosen for both A and B)

### Phase 3 — Damage description `/accident/{participantUuid}/damage`

- Heading: "Popište poškození" + "Vlastními slovy popište poškození vozidla {A|B}"
- Textarea with placeholder: "Prasklý přední nárazník, rozbité levé přední světlo, promáčknutá kapota, k poškození nedošlo."
- Heading: "Označte poškozené části vozidla {A|B}"
- **Damage-zones codelist** (8 zones + 1 "no damage" toggle): FRONT_LEFT, FRONT, FRONT_RIGHT, LEFT, RIGHT, REAR_LEFT, REAR, REAR_RIGHT, NONE (mutually exclusive)
- "Vozidlo nebylo poškozeno" toggle deselects all zones
- Endpoint: `PUT .../participants/{participantUuid}/damage`
- **Critical**: even with `?validate=false` URL param, the SPA enforces required-field validation client-side ("Toto pole je povinné" surfaced when description empty)

### Phase 3 — Movement `/accident/{participantUuid}/damage/movement`

- Heading: "Pohyb vozidla {A|B} v době nehody"
- 18-option **Movement codelist** (single-select):
  STOPPED_PARKED, STARTING, IN_MOTION, STOPPING, EXITING_PRIVATE, TURNING_TO_PRIVATE, ENTERING_ROUNDABT, IN_ROUNDABOUT, REAR_END_SAME_LANE, PARALLEL_OTHER_LANE, CHANGING_LANE, OVERTAKING, TURNING_RIGHT, TURNING_LEFT, REVERSING, WRONG_WAY, APPROACHING_RIGHT, NO_YIELD
- Endpoint: `PUT .../participants/{participantUuid}/movementDefinition`

### Phase 3 — Vehicle data + Insurer `/accident/{participantUuid}/damage/data`

- Heading: "Potvrďte údaje o vozidle {A|B}"
- Form 1 — Vehicle:
  - SPZ vozidla (text — Czech registration plate; format `7-char alphanumeric`)
  - Značka vozidla (combobox; **API: GET /api/enumerations/vehicleBrands** — 275 brands; e.g. ŠKODA, BMW)
  - Model vozidla (combobox; populated per-brand from the same response's `models[]` array)
  - Submit: "Potvrdit"
- Form 2 — Insurer (vehicle-bound):
  - Pojišťovna (combobox; **API: GET /api/enumerations/insuranceCompanies** — 13 entries with code/name/IČO/email/phone/link)
  - Checkbox: "Vozidlo má havarijní pojištění" (comprehensive/CASCO insurance flag)
  - Submit: "Potvrdit"
- Outer "Potvrdit" button advances when both forms valid
- Endpoints:
  - `PUT .../participants/{participantUuid}/vehicle` (SPZ + brand + model)
  - `PUT .../participants/{participantUuid}/insurer` (insurer code + comprehensive flag)
  - `GET .../participants/canRetrieveVehicleAndInsurerData` (probe — checks if AISPOV CRR can resolve; on DEMO presumably always falsy, hence manual entry)

### Phase 3 — Circumstances `/accident/circumstances` (shared between participants)

- URL: `/formular/report/{reportUuid}/accident/circumstances` (NO participant UUID — this is shared)
- Heading: "Okolnosti nehody" + "Jak se nehoda stala?"
- Both participants listed as labels: "Adam Test Demoversen, SPZ: 1AB1234" + "Beata Druhá, SPZ: 2BC5678"
- Button: "Změnit pořadí vozidel na obrázku" (swap A/B in the situational diagram)
- **5-option Accident-type codelist** (radio with SVG icons):
  - REAR_END_COLLISION — Náraz zezadu — `from_behind_variant_a.svg`
  - LANE_CHANGE — Změna pruhu — `changing_lane_variant_a.svg`
  - TURNING — Při odbočování — `while_turning_variant_a.svg`
  - PARKING — Při parkování — `while_parking_variant_a.svg`
  - ANOTHER — Jiný typ nehody (no SVG)
- "Váš popis nehody" textarea (free-text accident description)
- Endpoint: `PUT /api/reports/{uuid}/circumstances`

### Phase 3 — Date/time `/situation`

- Heading: "Datum, čas a místo nehody"
- Date input (default = today; format DD.MM.YYYY)
- Time input (default = current; format hh:mm)
- "Jste pořád na místě nehody?" (Yes / No radio)
- Endpoint: `PUT /api/reports/{uuid}/datetime`

### Phase 3 — Location `/situation/location/manual`

- URL: `/formular/report/{uuid}/situation/location/manual`
- Geolocation API auto-attempted; **alert observed**: "Určení polohy trvá příliš dlouho. Vyberte prosím polohu z mapy." (browser geolocation timeout — DEMO/automation context)
- **Google Static Maps API** observed: `https://maps.googleapis.com/maps/api/staticmap?key=AIzaSyACdtrV1A1LCbZTCpEI0j9Xbz0I_x0vCHs&size=820x150&center=50.0755,14.4378&zoom=7` — **API key exposed in URL** (Prague Old Town center default)
- "Adresa místa nehody" combobox — same RUIAN autocomplete as Phase 2 (INT-009)
- "Zadat adresu manuálně" button (free-text fallback)
- "Slovní popis místa nehody" textarea (free-text)
- Help drawer: "Jak se zorientovat na místě nehody?" with 3 tips (lampposts, highway markers, locals)
- Endpoint: `PUT /api/reports/{uuid}/location`

### Phase 3 — Culprit `/culprit`

- URL: `/formular/report/{reportUuid}/culprit`
- Heading: "Kdo zavinil nehodu?" + "Označte viníka nehody"
- 3-option radiogroup:
  - `{participantA-uuid}` → "Účastník A, Adam Test Demoversen, SPZ 1AB1234"
  - `{participantB-uuid}` → "Účastník B, Beata Druhá, SPZ 2BC5678"
  - `none` → "Není zřejmé"
- Endpoint: `PUT /api/reports/{uuid}/responsibleParticipant`

### Phase 4 — Summary `/summary`

- URL: `/formular/report/{uuid}/summary`
- Heading: "Shrnutí záznamu o dopravní nehodě"
- Body: "Před odesláním hlášení zkontrolujte správnost všech údajů. Účastník B si může údaje zkontrolovat pom..."
- Per-participant blocks: phone / email / address / OP / ŘP / ŘP-categories + "Informace o vozidle {SPZ}" expandable button
- Circumstances block: "Datum a čas: 06.05.2026, 10:12" / "Viník nehody: Adam Test Demoversen SPZ 1AB1234" / "Co se stalo: Náraz zezadu" / "Popis nehody: ..."
- Confirmation checkbox: "Uvedené informace jsou pravdivé a potvrzuji odeslání záznamu na uvedené kontakty"
- Disclaimer: "Editace předchozích částí je možná před kliknutím na tlačítko Podepsat záznam o nehodě. Následně již..."
- CTA: **"Podepsat záznam o nehodě"**
- Endpoint: `POST /api/reports/{uuid}/confirmation` (locks the report for signing)
- Endpoint: `GET /api/reports/{uuid}/summaryId` (returns the human-friendly identifier)
- Bundle: `SummaryPage-DH6qA0bf.js`, `FileSaver.min-CuljzYJW.js` (PDF download capability staged)

### Phase 4 — Sign-report `/sign-report`

- Heading: "Podepište záznam nehody"
- Body: "Pro pokračování je nutné podepsat záznam o nehodě pomocí nového kódu, který každému účastníkovi nyní..."
- Sequential per-participant signing (A first, then B)
- Each participant: phone-readonly + "Odeslat kód do sms" button
- Note: "Číslo není možné změnit, bylo již ověřeno v předchozích krocích" (number locked from Phase 1)
- After OTP send: same 4-box code entry as Phase 1 with "Podepsat" submit (instead of "Ověřit")
- DEMO hint: same text — accepts any 4-digit code
- Endpoints:
  - `POST .../participants/{participantUuid}/sendCodeToSign`
  - `POST .../participants/{participantUuid}/sign`
  - `GET .../participantsInSigning` (state probe between rounds)

### Phase 4 — Success `/success`

- URL: `/formular/report/{reportUuid}/success`
- Heading: "Záznam byl odeslán"
- Body: "Záznam byl odeslán na vaše e-mailové adresy, kde naleznete informace a rady k dalšímu postupu."
- **DEMO hint**: "V Demo verzi nejsou e-maily účastníkům odesílány." (Δ-NEW31 — DEMO no-email confirmation)
- "Druhý účastník nehody může pro stažení záznamu naskenovat QR kód."
- CTA: **"Stáhnout PDF záznam"** (FileSaver.js — client-side PDF download)
- Heading: "Pro pomoc s odtahem vozidla volejte asistenční službu pojišťovny"
- Per-participant towing-assistance contacts (auto-routed from chosen insurer):
  - "SPZ {plate} — {insurer-name} — {tel-number}" + "Volat ({tel})" button (links to `tel:` URI)
  - The phone is sourced from `insuranceCompanies[insurer-code].contact`
- **Per-insurer logos** observed in `/formular/assets/images/logos/{INSURER_CODE}.png` (e.g. `ALLIANZ.png`, `KOOPERATIVA.png` — confirms 13 logo assets exist)
- Return: "Přejít na hlavní obrazovku" → `/formular/`

## §9. End-to-end flow — final summary

| Phase | Route(s) | Surface | Endpoint(s) PUT/POST |
|-------|----------|---------|----------------------|
| 0 | `/formular/` | rozcestník | (none — static) |
| A | `/formular/informations` | "Co vás čeká?" intro | `POST /api/reports` (on Rozumím) |
| 1 | `/formular/report/{r}/verification` | OTP for A then B | `PUT /reporter`, `POST /participants`, `POST /participants/{p}/sendCodeToVerify`, `POST /participants/{p}/verify` |
| 1.5 | `/formular/report/{r}/verification/success` | "Ověřeno ✓" pills | (read-only) |
| 2-A | `/.../documents/{p-A}` + `/manual?validate=false` | OP + ŘP form | `PUT participantData`, `PUT email`, `PUT drivingLicense/update` |
| 2-A.recap | `/.../documents/{p-A}/recap` | review + email entry | `PUT email` |
| 2-B | `/.../documents/{p-B}` + `/manual?validate=false` + `/recap` | same shape for B | identical PUTs |
| 2.5 | `/.../witness` | optional witnesses | `GET /witnesses`, future POST/PUT |
| 3-A | `/.../accident/{p-A}` | photos prompt | (skip-button branch) |
| 3-A.dmg | `/.../accident/{p-A}/damage` | damage zones + description | `PUT .../damage` |
| 3-A.mov | `/.../accident/{p-A}/damage/movement` | movement codelist | `PUT .../movementDefinition` |
| 3-A.veh | `/.../accident/{p-A}/damage/data` | SPZ + brand + insurer | `PUT .../vehicle`, `PUT .../insurer` |
| 3-B | identical for B | (rinse) | (same PUTs against B's UUID) |
| 3.shared | `/.../accident/circumstances` | accident-type radio + free-text | `PUT /circumstances` |
| 3.dt | `/.../situation` | date + time + on-site | `PUT /datetime` |
| 3.loc | `/.../situation/location/manual` | address autocomplete + geo | `PUT /location` |
| 3.culprit | `/.../culprit` | viník radiogroup | `PUT /responsibleParticipant` |
| 4 | `/.../summary` | review-everything + lock-for-sign | `POST /confirmation`, `GET /summaryId` |
| 4.sign | `/.../sign-report` | OTP-sign per participant | `POST .../sendCodeToSign`, `POST .../sign` |
| 4.done | `/.../success` | PDF + assistance + return | `GET /summaryId` (final) |

**Total endpoints discovered (PUT/POST/GET): ~30 internal + 6 third-party.**

## §10. Open questions resolved during walk

- **NEMŮŽETE ZADAT KÓD?** — button present but not exercised; presumably triggers resend or admin-contact path
- **DEMO accepts any 4-digit OTP** — ✓ confirmed for both verify and sign rounds
- **Address combobox** — RUIAN ČÚZK (INT-009) confirmed
- **`?validate=false`** — disables OCR/registry validation but NOT required-field validation
- **20 pre-fetched videos** — they're instructional substitutes for OCR steps (Δ5 zenID mock)
- **reCAPTCHA `clr` 503** — non-blocking; persistent across the walk

## §11. Status

| Item | Value |
|------|-------|
| Flow folder | `recon/screenflows-live/flow-A1-main-tst-demo/` |
| Phases captured | 0, A, 1, 1.5, 2-A, 2-A.recap, 2-B, 2-B.recap, 2.5, 3-A.{photos,damage,movement,vehicle}, 3-B.{same}, 3.shared.{circumstances,datetime,location,culprit}, 4.{summary,sign,success} |
| Coverage | end-to-end main happy path **complete** for A1 DEMO |
| Internal endpoints | 30+ (catalogued in `fixtures/api-endpoints-live-2026-05-06.yaml`) |
| Third-party integrations | 6 (INT-001 reCAPTCHA, INT-006 Azure outages, INT-007 Google Maps, INT-009 RUIAN, plus FileSaver.js client-side, plus tel: URIs) |
| Codelists captured | 7 (insurance-13, brands-275, license-17, damage-9, movement-18, accident-type-5, culprit-3) |
| Δ rows confirmed live | 8 (Δ1, Δ5, Δ11, Δ21-26, Δ31 = no-email-on-DEMO success-screen) |
| TC candidates surfaced | 25+ |
| Status | **v0.3 — main path E2E complete; alternate paths + PROD twin pending** |


## §7. Status

| Item | Value |
|------|-------|
| Flow folder | `recon/screenflows-live/flow-A1-main-tst-demo/` |
| Phases captured | 0 (rozcestník), A (intro), 1 (verification — pre-submit) |
| Phases pending | 1 (post-submit), 2, 3, 4 |
| Network endpoints discovered | 4 internal `/api/reports*` + 2 third-party (Azure outages, Google Maps) |
| Routes mapped | 5 (`/formular`, `/formular/personal-data`, `/formular/informations`, `/formular/report/{uuid}/verification`, + parametrised) |
| Status | v0.1 — live capture in progress |
