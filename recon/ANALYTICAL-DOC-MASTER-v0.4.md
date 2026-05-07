# Bouračka — Master analytický dokument — v0.4

> **Branched master.** Tento dokument je jeden zdroj pravdy pro **obě** branche
> Bouračky (PROD-Bouračka i DEMO-Bouračka). Sekce specifické pro jednu branch
> jsou označené `<!-- B:DEMO -->...<!-- /B -->` nebo `<!-- B:PROD -->...<!-- /B -->`.
>
> **Render skript** `tools/render_branch_doc.py` produkuje per-branch slim
> verzi — viz `_specs/BRANCHED-MASTER-DOC-PATTERN-v0.1.md` §3.
>
> **Per-branch view:**
> - Pro DEMO branch: `python tools/render_branch_doc.py recon/ANALYTICAL-DOC-MASTER-v0.4.md --branch demo`
> - Pro PROD branch: `python tools/render_branch_doc.py recon/ANALYTICAL-DOC-MASTER-v0.4.md --branch prod`

---

## §1. Identita

Bouračka je webová aplikace ČKP (Česká kancelář pojistitelů) pro
self-record drobných dopravních nehod (R1: ≤ 200 000 Kč škody, 2 účastníci
s českými OP, bez zranění). Existuje ve dvou branchech:

<!-- B:DEMO -->
**DEMO branch:**
- `https://demo.bouracka.cz/formular/` — veřejně dostupné od 2026-05-05/06 (overnight)
- `https://tst.demo.bouracka.cz/formular/` — firewall-gated twin (preprod validace)
- Stejný JS bundle jako PROD; integrace mockované / sandbox
- Hlavní rozdíl: žádné reálné SMS, žádné reálné registrové dotazy, žádné e-maily
<!-- /B -->

<!-- B:PROD -->
**PROD branch:**
- `https://bouracka.cz/formular/` — produkce
- `https://tst.bouracka.cz/formular/` — firewall-gated test (PROD-test)
- Reálné integrace (N8 SMS Gateway, AISPOV ROB/CRR/CRV, zenID OCR)
- Vyžaduje N8 sandbox / skip-flag pro testování bez doručení reálných SMS
<!-- /B -->

## §2. Společný kontrakt (oba branche)

### §2.1 Architektura

- **Frontend:** Vite + React 18+ + Zod + TanStack Query
- **Backend:** REST + JSON, UUID-keyed report resources
- **Codelisty:** `/api/enumerations/*` (selektivní veřejnost — viz §5)
- **3rd-party:** RUIAN ČÚZK (adresy), Google Maps (geokódování), reCAPTCHA v3
- **Outage feed:** Azure Static Web `bourackaodstavky78861.z6.web.core.windows.net`

### §2.2 Wizard taxonomie

4 fáze + Phase A intro + Phase 2.5 svědci (volitelně):

```
Phase 0 — Rozcestník                    /formular/
Phase A — Pre-wizard intro              /formular/informations
Phase 1 — Verifikace                    /formular/report/{r}/verification
Phase 2 — Documents (per účastník)      /documents/{p}/[manual|recap]
Phase 2.5 — Witnesses                   /witness
Phase 3 — Photos / damage / circumstances / location / culprit
Phase 4 — Sign + submit                 /summary /sign-report /success
```

### §2.3 REST API surface (společné)

23 endpointů na `/api/reports/{uuid}/*`. Detail viz
`recon/integrations/INT-008.md` a `fixtures/api-endpoints-live-2026-05-06.yaml`.

## §3. Phase 1 — Verifikace telefonu (OTP)

Společné: vyplnit telefon + GDPR konsent (jen účastník A) → server pošle OTP → uživatel zadá kód → pokračuje na Phase 2.

<!-- B:DEMO -->
### §3.1 DEMO behavior (Δ1, Δ22)

**Žádné SMS se neodesílají.** Server akceptuje libovolný 4-číslicový OTP.

V UI je viditelný žlutý info-box:

> "Demoverze žádné SMS neodesílá, potvrzovací kód bude v dalším kroku
> automaticky doplněn."

Test impact:
- TC-CP-NEW-O: zadáme `1234` → 200 OK (DEMO-only)
- Mockoon profil pro DEMO není potřeba (DEMO je sám-svůj-mock)
<!-- /B -->

<!-- B:PROD -->
### §3.1 PROD behavior

Server volá **N8 SMS Gateway** pro odeslání reálné SMS. Účastník MUSÍ
zadat kód obdržený na své telefon.

Pre-conditions pro testování:
- N8 sandbox URL + API key (env var `N8_SANDBOX_URL`)
- Tester phone E.164 (env var `TESTER_PHONE_E164`)
- Po `sendCodeToVerify` poll N8 sandbox endpoint pro doručený OTP

Test impact:
- TC-CP-005-PROD: poll N8 sandbox pro reálný kód → submit → 200 OK
- TC-CP-NEW-P (negativní): submit `1111` (libovolný špatný kód) → 4xx
- DEMO hint banner MUSÍ být absent (TC-CP-NEW-J jako sanity check)
<!-- /B -->

## §4. Phase 2 — Documents (OP + ŘP + adresa)

Společné: per-účastník formulář pro osobní + ID údaje + ŘP + adresu + e-mail.
Adresa tažená přes RUIAN ČÚZK autocomplete (INT-009 — společná pro oba branche).

<!-- B:DEMO -->
### §4.1 DEMO behavior (Δ5, Δ27)

**zenID OCR neexistuje** — místo OCR z OP je instruktážní video.
**Driver registry (AISPOV CRR) je no-op** — tlačítko "Načíst z registru řidičů"
nemá efekt; uživatel musí vyplnit ručně.

Yellow hint box:

> "V Demo verzi je nahrazeno instruktážním videem."

> "V Demo verzi načtení údajů z registru řidičů neprobíhá, údaje zadejte manuálně."

Test impact:
- TC-CP-NEW-S: deep-link `?validate=false` přijatelný (DEMO automation hook)
- TC-CP-NEW-T-DEMO: AISPOV button no-op (assertion: žádný API call)
- ŘP regex `^[A-Z]{2} \d{6}$` enforced (TC-CP-NEW-V)
<!-- /B -->

<!-- B:PROD -->
### §4.1 PROD behavior

**zenID OCR plně aktivní** — uživatel fotí OP přední + zadní stranu;
zenID extrahuje jméno, příjmení, číslo OP, datum narození, adresu.
**AISPOV CRR funkční** — tlačítko "Načíst z registru řidičů" volá real
state registry (Centrální registr řidičů).

Pre-conditions pro testování:
- zenID test-keys (env var `ZENID_TEST_KEY`)
- AISPOV read-only token (env var `AISPOV_TOKEN`)
- Synthetic OP/ŘP identity z ČKP test-data setu (NE reálná občanská data)

Test impact:
- TC-CP-NEW-T-PROD: AISPOV CRR volání s response 200 → fields auto-fill
- TC-CP-NEW-V (regex) — stejné jako DEMO
- TC-CP-007: zenID OCR happy path (PROD-only)
<!-- /B -->

## §5. Codelisty

Společný endpoint pattern: `GET /api/enumerations/{name}`. **Selektivní
veřejnost:**

| Codelist | Status | Veřejné? |
|----------|--------|----------|
| `insuranceCompanies` | 200 | ANO (13 entries) |
| `vehicleBrands` | 200 | ANO (275 brands) |
| `licenseCategories` | 403 | NE (jen v JS bundle, 17 hodnot) |
| `damageZones` | 403 | NE (DOM-readable, 8 zón + NONE) |
| `movementTypes` | 403 | NE (DOM-readable, 18 typů) |
| `accidentCauses` | 403 | NE |
| `accidentCategories` | 403 | NE |
| `vehicleCategories` | 403 | NE |
| `documentTypes` | 403 | NE |
| `witnessTypes` | 403 | NE |

Detail v `fixtures/codelists-live-2026-05-06.yaml`. Codelisty jsou identické
mezi branche — žádný Δ.

<!-- B:DEMO -->
**DEMO branch:** všechny veřejné endpointy testovatelné přímo přes Playwright
`request.get(...)`. Viz `tests/07-codelist-public.spec.ts` v suite-DEMO.
<!-- /B -->

<!-- B:PROD -->
**PROD branch:** stejný kontrakt; pre-live test může poslat `OPTIONS` request
pro CORS validation (viz TC-CP-NEW-N rate-limit test).
<!-- /B -->

## §6. Phase 4 — Sign + submit

Společné: summary review → checkbox potvrzení → SMS-podpis pro každého
účastníka sekvenčně → success page s PDF + assistance kontakty.

<!-- B:DEMO -->
**DEMO behavior (Δ31):** po podepsání obou účastníků **e-maily se neodesílají**.
UI explicitně říká:

> "V Demo verzi nejsou e-maily účastníkům odesílány."

Test impact: TC-CP-022 přeskočen (`env_constraints: prod-only`).
<!-- /B -->

<!-- B:PROD -->
**PROD behavior:** po podpisu se rozešlou e-maily oběma účastníkům s odkazem
na PDF záznam. Mailing služba TBC (pravděpodobně SendGrid nebo SMTP-přímý).

Test impact:
- TC-CP-022: assert real e-mail dispatch (musí být `tester-contacts.yaml`
  vyplněný s ČKP-přiděleným tester aliasem, ne osobním e-mailem)
- Po každém PROD běhu manuálně zkontrolovat, že tester inbox
  obdržel zprávu
<!-- /B -->

## §7. Δ matice — krátký výtah

Plná Δ matice s 26 řádky v `recon/DELTA-DEMO-vs-PROD-v0.1.md`. 8 potvrzeno
z živé analýzy 2026-05-06:

| # | Surface | DEMO | PROD |
|---|---------|------|------|
| Δ1 | N8 SMS gateway | žádné SMS, libovolný OTP | reálné SMS |
| Δ5 | zenID OCR | instruktážní video | reálné OCR |
| Δ11 | Branding | "DEMO VERZE" baner | čistý PROD |
| Δ21 | Pre-wizard intro | přítomna | shodná |
| Δ22 | Phase-1 hint | žlutý info-box | absent |
| Δ23 | Maps locale | `intl/en_gb/` (vada) | shodná vada |
| Δ24 | Outage feed | Azure Static Web | shodný |
| Δ31 | E-mail dispatch | žádný | reálný |

## §8. Status

| Item | Hodnota |
|------|---------|
| Master dokument | `recon/ANALYTICAL-DOC-MASTER-v0.4.md` |
| Branch markery | 6 sekcí (`<!-- B:DEMO -->`, `<!-- B:PROD -->`) |
| Render skript | `tools/render_branch_doc.py` |
| Per-branch render | `python tools/render_branch_doc.py <master> --branch {demo\|prod}` |
| Master view | bez `--branch` parametru |
| Status | v0.4 — proof-of-concept; další iterace doplní více detailu |
