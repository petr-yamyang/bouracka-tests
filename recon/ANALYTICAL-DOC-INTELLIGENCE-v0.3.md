# Analytical Document Intelligence — v0.3 (bottom-up from live evidence)

> **Trigger.** Per CP-SUPIN-04 STEP 11 (2026-05-06): the original analytical
> document (mid-2025, dated for July-2025 MVP) is now ~10 months stale.
> DEMO went public overnight 2026-05-05; live walk on 2026-05-06 produced
> high-fidelity Tier-2a evidence. This document is **rebuilt bottom-up**
> from that evidence, deprecating the v0.1/v0.2 top-down analyses.
>
> **Scope.** R1 main happy path (single accident, 2 Czech-ID participants,
> ≤200 000 Kč damage, no injuries) — fully observable end-to-end on DEMO.
> Out of scope here: alternate paths, PROD-only behaviour (covered in Δ matrix).

---

## §1. Top-line corrections to the analytical doc (what the doc got wrong)

| Item | Doc said | Reality (live evidence) | Source |
|------|----------|--------------------------|--------|
| Wizard granularity | 18 screens (D00..D17) | **4 visible phases** (Telefonní čísla / Základní údaje / Fotografie+popis / Potvrzení) progress bar; ~22 internal sub-screens | Phase A intro screen + observed routes |
| State-machine surface | `accidentReportStatus: NEW → IN_PROGRESS_DRIVERS → IN_PROGRESS_VEHICLES → IN_PROGRESS_CIRCUMSTANCES → TO_SIGN → FINISHED` | Resource lifecycle visible via 30+ REST endpoints; section-by-section completeness via `GET /completenessStatus` | `GET /completenessStatus` + per-section PUTs |
| Auth | "user logs in implicitly via existing IDs" | No login at all on DEMO. Anonymous user → `POST /reports` mints a UUID; subsequent state bound to that UUID + cookie session; phone-OTP is the only identity proof | `POST /api/reports` returns UUID without any creds |
| Address source | unspecified | **RUIAN ČÚZK ArcGIS REST** — direct from browser (INT-009) | network panel observation |
| Map | unspecified | **Google Maps JS + Static-Maps API** with embedded API key + locale=`en_gb` (defect candidate) | INT-007 |
| Outages signalling | unspecified | **Azure Static Web Apps** feed `bourackaodstavky78861.z6.web.core.windows.net/odstavky.json` | INT-006 |
| Insurance partners | "list" | **13 entries** with code/name/IČO/email/phone/claims-link, served from `/api/enumerations/insuranceCompanies` | live capture; full list in `fixtures/codelists-live-2026-05-06.yaml` |
| Vehicle catalogue | "list" | **275 brands × N models** served from `/api/enumerations/vehicleBrands` | live capture |
| Witness step | not mentioned | **Optional Phase 2.5** with `/witness` route + max 3 witnesses | live capture |
| "Identifikační kód" | not mentioned | Format `XXXXXX-YY-NNNNNNN` (e.g. `111111-26-0000001`) — Police/IZS lookup; persistent header modal post-verification | live capture |

## §2. Four phases — actual flow vs documented

### §2.1 The phases as the SPA itself describes them (intro screen)

From `/formular/informations` → "Jak probíhá online záznam o nehodě?":

1. **Telefonní čísla** — "Ověříme telefonní čísla obou účastníků."
2. **Základní údaje** — "Vyplníte osobní a technické údaje potřebné k záznamu."
3. **Fotografie a popis nehody** — "Vyfotíte poškození obou vozidel a krátce popíšete situaci."
4. **Potvrzení** — "Každý z účastníků obdrží SMS s ověřovacím kódem pro podpis záznamu."
5. **Hotovo** (terminal, not a wizard step) — "Záznam dostanou oba účastníci e-mailem a bude i ke stažení jako PDF."

### §2.2 Sub-screens per phase (from end-to-end walk)

```
Phase 0 — Rozcestník                               /formular/
Phase A — Pre-wizard intro                         /formular/informations
Phase 1 — Verification                             /formular/report/{r}/verification
  ├── OTP for participant A (sequential)
  ├── OTP for participant B
  └── Success → /verification/success
Phase 2 — Documents (per participant)              /formular/report/{r}/documents/{p}
  ├── Photo cards (skip-able)
  ├── Manual fallback                              /documents/{p}/manual?validate=false
  └── Recap                                        /documents/{p}/recap
Phase 2.5 — Witnesses                              /formular/report/{r}/witness
Phase 3 — Photos + circumstances + place
  ├── Per-participant photos                       /accident/{p}
  ├── Per-participant damage                       /accident/{p}/damage
  ├── Per-participant movement                     /accident/{p}/damage/movement
  ├── Per-participant vehicle+insurer              /accident/{p}/damage/data
  ├── Shared circumstances                         /accident/circumstances
  ├── Date+time+on-site                            /situation
  ├── Location                                     /situation/location/manual
  └── Culprit                                      /culprit
Phase 4 — Sign + done
  ├── Summary                                      /summary
  ├── Sign (sequential A then B)                   /sign-report
  └── Success → PDF + assistance contacts          /success
```

## §3. REST API surface (INT-008 contract)

Base: `https://demo.bouracka.cz/api/` (DEMO); `https://bouracka.cz/api/` expected on PROD.

### §3.1 Reports lifecycle

| Verb | Path | Side effect |
|------|------|-------------|
| `POST` | `/reports` | mint UUID + initial state |
| `GET`  | `/reports/{r}` | hydrate (called on every route mount) |
| `GET`  | `/reports/{r}/completenessStatus` | per-section progress |
| `GET`  | `/reports/{r}/summaryId` | human-friendly identifier |

### §3.2 Participants

| Verb | Path | Side effect |
|------|------|-------------|
| `PUT`  | `/reports/{r}/reporter` | save A's phone — ONLY way to "create" A |
| `POST` | `/reports/{r}/participants` | create B (and any future witness?) |
| `GET`  | `/reports/{r}/participants` | list all |
| `GET`  | `/reports/{r}/participants/{p}` | single participant |
| `PUT`  | `/reports/{r}/participants/{p}/participantData` | personal data block |
| `PUT`  | `/reports/{r}/participants/{p}/email` | email (separate atomic write) |
| `PUT`  | `/reports/{r}/participants/{p}/drivingLicense/update` | ŘP block |
| `GET`  | `/reports/{r}/participants/canRetrieveVehicleAndInsurerData` | AISPOV-CRR-probe |

### §3.3 Verification (Phase 1) + Signing (Phase 4) — same shape, different verb-suffix

| Verb | Path | Phase |
|------|------|-------|
| `POST` | `/reports/{r}/participants/{p}/sendCodeToVerify` | Phase 1 |
| `POST` | `/reports/{r}/participants/{p}/verify` | Phase 1 |
| `POST` | `/reports/{r}/participants/{p}/sendCodeToSign` | Phase 4 |
| `POST` | `/reports/{r}/participants/{p}/sign` | Phase 4 |
| `GET`  | `/reports/{r}/participantsInVerification` | Phase 1 state probe |
| `GET`  | `/reports/{r}/participantsInSigning` | Phase 4 state probe |
| `POST` | `/session/refresh` | rotate token at phase boundaries |

### §3.4 Damage / accident description

| Verb | Path |
|------|------|
| `PUT` | `/reports/{r}/participants/{p}/damage` (description + zones) |
| `PUT` | `/reports/{r}/participants/{p}/movementDefinition` (movement codelist single-select) |
| `PUT` | `/reports/{r}/participants/{p}/vehicle` (SPZ + brand + model) |
| `PUT` | `/reports/{r}/participants/{p}/insurer` (insurer code + comprehensive flag) |
| `PUT` | `/reports/{r}/circumstances` (accident-type + free-text — shared) |
| `PUT` | `/reports/{r}/datetime` (date + time + on-site flag) |
| `PUT` | `/reports/{r}/location` (address + free-text + coords) |
| `PUT` | `/reports/{r}/responsibleParticipant` (culprit) |

### §3.5 Final / Witnesses / Codelists

| Verb | Path | Notes |
|------|------|-------|
| `GET`  | `/reports/{r}/witnesses` | optional Phase 2.5 |
| `POST` | `/reports/{r}/confirmation` | lock-for-sign (Phase 4 trigger) |
| `GET`  | `/enumerations/insuranceCompanies` | **PUBLIC** (200) — 13 entries |
| `GET`  | `/enumerations/vehicleBrands` | **PUBLIC** (200) — 275 brands |
| `GET`  | `/enumerations/{licenseCategories,damageZones,movementTypes,accidentCauses,accidentCategories,vehicleCategories,documentTypes,witnessTypes}` | **PROTECTED** (403) — bundled into JS |

## §4. Frontend stack inferred

- **Build**: Vite (hashed asset names; per-route lazy chunks)
- **Framework**: React 18+ (`useId` auto-IDs `«rh»`/`«ri»`)
- **State / data**: TanStack Query (`useIsFetching` hook)
- **Validation**: Zod (schemas mirrored client + server)
- **UI primitives**: Material UI suspected (FormCheckbox, FormRadioGroup, MenuItem, Autocomplete combobox patterns)
- **PDF**: `FileSaver.js` (client-side blob save)
- **Date**: MUI X Date Pickers (`DesktopDatePicker`)
- **Map**: Google Maps JS API + Static Maps; site-key `AIzaSyACdtrV1A1LCbZTCpEI0j9Xbz0I_x0vCHs`; locale forced to `en_gb` (defect)
- **Geocoding**: ČÚZK ArcGIS REST direct from browser (INT-009)
- **Captcha**: reCAPTCHA v3 invisible; site-key `6Lfbao4sAAAAANfSk_-NcqLZPYB8wdMvrBS4qM5p`

## §5. State-machine — refined from live observation

The doc-postulated `accidentReportStatus` enum is **partially wrong**. The
actual state machine is more granular and per-section:

```
report.status                                           — top-level
  NEW                          (post POST /reports)
  IN_PROGRESS                  (after first PUT /reporter)
  AWAITING_VERIFICATION_A      (sendCodeToVerify A)
  VERIFIED_A                   (verify A success)
  AWAITING_VERIFICATION_B      (after POST /participants for B)
  VERIFIED                     (both verified)
  IN_PROGRESS_DOCUMENTS        (Phase 2)
  IN_PROGRESS_DAMAGE           (Phase 3)
  IN_PROGRESS_CIRCUMSTANCES    (Phase 3 shared)
  AWAITING_SIGN                (POST /confirmation)
  AWAITING_SIGN_A              (sendCodeToSign A)
  SIGNED_A                     (sign A success)
  AWAITING_SIGN_B
  COMPLETED                    (both signed → /success)
  CANCEL / ERROR

participant.status                                       — per participant
  CREATED
  PHONE_PROVIDED
  CODE_SENT
  VERIFIED
  PARTICIPANT_DATA_SET
  EMAIL_SET
  DRIVING_LICENSE_SET
  DAMAGE_SET
  MOVEMENT_SET
  VEHICLE_SET
  INSURER_SET
  COMPLETE_FOR_SIGN
  SIGN_CODE_SENT
  SIGNED
```

Validate this enum-shape against the actual `GET /completenessStatus`
response payload in next walk pass.

## §6. Codelists — actual values (vs analytical doc placeholders)

See `fixtures/codelists-live-2026-05-06.yaml` for full payloads. Summary:

| Codelist | Doc state | Live state |
|----------|-----------|-----------|
| Insurance | placeholder | 13 actual entries with claims-handling contacts |
| Vehicle brands | not catalogued | 275 brands (incl. obscure historical ones like AERO, AVIA, BABETTA, etc.) |
| ŘP categories | placeholder | 17 entries (full EU + B96 + T) |
| Damage zones | placeholder | 8 zones + NONE toggle |
| Movement | placeholder (17 expected, EU directive) | 18 (17 + Czech-specific NO_YIELD) |
| Accident type | not catalogued | 5 (REAR_END_COLLISION / LANE_CHANGE / TURNING / PARKING / ANOTHER) |
| Culprit | not catalogued (radiobutton) | 3 (participantA-uuid / participantB-uuid / "none") |

## §7. Validation rules — derived from live observation

| Field | Rule observed | TC reference |
|-------|---------------|--------------|
| Phone (Phase 1, sign) | format `XXX XXX XXX` digits, auto-spaced | TC-CP-018 |
| Předvolba | CZ (`+420`) or SK (`+421`) | TC-CP-NEW-H |
| Číslo OP | text — no enforced format observed (DEMO accepts `123456789`) | TC TBD |
| Datum narození | `DD.MM.YYYY` enforced | TC-CP-NEW-W |
| Číslo ŘP | format `XY 000000` (regex `^[A-Z]{2} \d{6}$`) | TC-CP-NEW-V |
| E-mail | enforced (`example.invalid` rejected; `example.com` accepted) | TC TBD |
| GDPR consent | required only for participant A | TC-CP-NEW-I |
| Skupiny ŘP | required (1-of-17, multi-select) | TC-CP-NEW-V |
| Damage description | required even with `?validate=false` | TC-CP-NEW-S |
| Movement | required (1-of-18 single select) | new TC |
| SPZ | text, no enforced format observed (DEMO accepts `1AB1234`, `2BC5678`) | new TC |

## §8. Status

| Item | Value |
|------|-------|
| Document | `recon/ANALYTICAL-DOC-INTELLIGENCE-v0.3.md` |
| Approach | bottom-up from live walk evidence (Tier 2a) |
| Coverage | R1 main happy path (A1) end-to-end on DEMO |
| Status | v0.3 — supersedes v0.1/v0.2 top-down analyses for fact-finding; v0.1/v0.2 retained for historical/business-context content |
| Pending | alternate paths (A2..A4); PROD twin (Tier 2b) when access opens; activity-diagram CS-only re-render |
