# Žádost o testovací přístup k integraci zenID — bouracka.cz testovací sada

> **Šablona pro odeslání kontaktní osobě v SUPIN s.r.o. (ideálně
> integračnímu architektovi pro projekt Bouračka).** Po vyplnění
> editovat dle skutečnosti a odeslat. Anglická verze v §B níže pro
> případ, že komunikace s vendorem zenID probíhá v EN.
>
> **Účel.** Získat testovací přístup k integraci zenID pro
> automatizovanou testovací sadu `bouracka-tests` — tak, abychom mohli
> spolehlivě testovat průchody průvodcem hlášení dopravní nehody bez
> potřeby nahrávat reálné osobní doklady do testovacího prostředí.
>
> **Příjemce.** SUPIN s.r.o. (provider integrace) — případně přeposlat
> přímo zenID, je-li relevantnější.

---

## §A. Česká verze

```
Předmět: bouracka-tests — žádost o testovací přístup k integraci zenID

Vážení kolegové,

v rámci přípravy automatizované testovací sady pro aplikaci Bouračka
(prostředí tst.bouracka.cz a tst.demo.bouracka.cz) potřebujeme nastavit
opakovatelné a deterministické testování průchodu obrazovkami 03 a 08
(Nafocení OP / SPZ s OCR vytěžením přes zenID WebSDK / zenID API).

Vzhledem k tomu, že:
  • testovací sada poběží na třech notebookách v rámci ČKP/SUPIN intranetu
    (operátorský SUPNB001 + dva kolegovské SUPNB002, SUPNB003),
  • do testovacího prostředí nesmíme nahrávat reálné osobní doklady
    (GDPR + zákon č. 110/2019 Sb.),
  • automatizované testy potřebují deterministické odpovědi pro spolehlivé
    běhy (k tomu reálná OCR služba není vhodná — vrací stochastické skóre),

žádáme o jednu z následujících variant podpory (preferujeme variantu 1):

  ┌─ VARIANTA 1 — sandbox / test-mode přístup k zenID ───────────────────┐
  │                                                                       │
  │ • testovací API klíč k zenID API + WebSDK pro tst.bouracka.cz        │
  │ • dokumentace request/response kontraktu — konkrétně:                 │
  │     - JSON shape WebSDK callback výstupu (OK / WARNING / NOK)         │
  │     - REST kontrakt zenID API endpointu pro upload-from-gallery       │
  │     - struktura odpovědi pro každý outcome class (OK/WARNING/NOK)     │
  │     - prahové hodnoty confidence skóre pro WARNING vs NOK             │
  │ • 3–5 vzorových syntetických OP/ŘP/SPZ vstupů (foto nebo ID stringů), │
  │   které v testovacím režimu vrátí předem známý výsledek               │
  │                                                                       │
  └───────────────────────────────────────────────────────────────────────┘

  ┌─ VARIANTA 2 — konfigurační skip-flag v aplikaci ─────────────────────┐
  │                                                                       │
  │ Dle analytické dokumentace (str. 25/133) aplikace Bouračka podporuje  │
  │ konfigurační přeskočení integrací v tst.* prostředích. Žádáme o:      │
  │                                                                       │
  │ • název konfiguračního atributu / environment variable / DB záznamu,  │
  │   který umožní v tst.bouracka.cz a tst.demo.bouracka.cz vypnout       │
  │   integraci zenID (pro náš testovací běh, bez ovlivnění ostatních     │
  │   testerů),                                                           │
  │ • potvrzení, že se aplikace v takovém případě otevře v editačním      │
  │   režimu (ručně vyplnit OP / ŘP / SPZ),                               │
  │ • případně možnost zapnout flag "per-session" tak, aby ostatní         │
  │   testeři ve sdíleném tst.* prostředí nebyli ovlivněni.               │
  │                                                                       │
  └───────────────────────────────────────────────────────────────────────┘

Pokud žádná z variant není dostupná, zvažujeme jako fallback:

  ┌─ VARIANTA 3 — golden-master se syntetickými fotografiemi ────────────┐
  │                                                                       │
  │ Vytvoříme 3–5 syntetických (uměle vyrobených, viditelně označených    │
  │ "VZOREK" / "SPECIMEN") OP/ŘP/SPZ obrázků; jednorázově je propustíme   │
  │ skrz reálnou zenID v tst.*, výsledek uložíme jako "golden master" a   │
  │ následně proti němu testujeme.                                        │
  │                                                                       │
  │ V tomto případě bychom potřebovali:                                   │
  │ • potvrzení, že použití syntetických (nikoliv reálných) dokladů       │
  │   je v souladu s podmínkami užívání zenID v tst.*,                    │
  │ • případně doporučení od ČKP právního, zda postup vyžaduje formální   │
  │   souhlas (rozumíme, že se nejedná o pravé doklady).                  │
  │                                                                       │
  └───────────────────────────────────────────────────────────────────────┘

Co poskytujeme z naší strany:
  • plnou architekturu testovací sady: viz dokumenty v repozitáři
    bouracka-tests (přístup zařídíme),
  • specifikaci "konzumací" zenID v testech: jakými scénáři, s jakými
    typy očekávaných odpovědí,
  • podpis NDA, je-li požadováno,
  • oddělené testovací účty (e-mail) pro každý ze tří notebookov, aby
    bylo zřejmé, že se nejedná o produkční využití,
  • dohledatelnost veškerých testovacích volání (logy, request-id mapování).

Časový rámec: ideálně bychom potřebovali rozhodnutí o jedné z variant
do konce týdne, aby další iterace prací (CP-SUPIN-03..08) mohly
pokračovat bez blokace.

Děkuji za pomoc a rád obratem upřesním cokoliv potřebujete vědět.

S pozdravem,
Petr Žemla
```

---

## §B. English version (forward to vendor if needed)

```
Subject: bouracka-tests — request for zenID test-mode access

Dear Colleagues,

We are setting up an automated test suite for the Bouračka application
(environments tst.bouracka.cz and tst.demo.bouracka.cz). To exercise
screens 03 and 08 (OP / SPZ photo capture with OCR via zenID WebSDK /
zenID API) reliably and deterministically, we need a test-mode posture
that does not require real personal documents in the test environment.

Specifically, because:
  • the test suite runs on three notebooks inside the ČKP/SUPIN
    intranet (operator's SUPNB001 + two peers SUPNB002, SUPNB003),
  • uploading real personal documents to the test environment is
    prohibited by GDPR + Czech act 110/2019,
  • automated tests require deterministic responses (real OCR returns
    stochastic confidence scores),

we ask for one of the following (Option 1 is preferred):

  Option 1 — zenID sandbox / test-mode access:
    - test API key for zenID API + WebSDK on tst.bouracka.cz
    - documentation of the request/response contract:
        * WebSDK JS callback JSON shape (OK / WARNING / NOK)
        * zenID API REST contract for gallery-upload path
        * response envelope for each outcome class
        * confidence-score thresholds defining OK vs WARNING vs NOK
    - 3–5 sample synthetic OP/ŘP/SPZ inputs (photos or ID strings)
      that, in test mode, return predictable results

  Option 2 — SUT-side skip-flag for the integration:
    Per the analytical doc (p. 25/133) the Bouračka application
    supports configuration-driven integration skipping in tst.*. We ask
    for:
    - the name of the config attribute / env var / DB row
    - confirmation the app falls back to manual edit-mode in this case
    - ideally per-session granularity so other testers in the shared
      tst.* environment are not affected by our test runs

  Option 3 (fallback) — golden-master with synthetic photos:
    We create 3–5 synthetic (visibly "VZOREK"-marked) OP/ŘP/SPZ
    images, run them once through real zenID in tst.* to capture a
    golden master, then assert against the golden master in subsequent
    runs. We'd need confirmation that synthetic-doc use is consistent
    with zenID's terms of use in tst.*.

We provide on our side:
  - full architecture of the test suite (repo access can be arranged),
  - specification of how zenID is consumed in tests (scenarios + the
    expected response types),
  - NDA signature if required,
  - separate test accounts (email) per notebook so test usage is
    clearly distinguishable from production,
  - traceability of every test call (logs + request-id mapping).

Timeline: ideally a decision on one of the options by end-of-week so
that downstream test iterations (CP-SUPIN-03..08) are not blocked.

Thank you for the help — happy to expand on any point.

Best regards,
Petr Žemla
```

---

## §C. Same template, other integrations (use as base — adapt the body)

When you need the same conversation for **AISPOV / ROB / CRR / CRV /
Evidence pojištěných vozidel**, **SMS Gateway**, **RUIAN**, **Google
Maps**, copy this file to:

```
_install/contracts/aispov-test-data-request.md
_install/contracts/sms-gateway-test-data-request.md
_install/contracts/ruian-test-data-request.md
_install/contracts/maps-test-data-request.md
```

For each, swap the integration name + tweak the three options:
- AISPOV — almost certainly Option 2 (SUPIN-side skip flag); SUPIN
  owns AISPOV directly.
- SMS Gateway — Option 1 (test API key) or Option 2 (PING-only mode);
  also a "read-back hook" URL where tests can poll for the latest OTP
  sent to a test phone number.
- RUIAN — public API; Option 1 with rate-limit confirmation should
  suffice.
- Google Maps — Option 1 with a billing-protected test API key, or
  Option 2 (manual-address fallback that bypasses Maps entirely).

## §D. Where the answers land

When the SUPIN/zenID reply arrives, the operator updates:

1. `_install/contracts/responses-log.md` (NEW; create on first reply)
   — one entry per ask, with date / who / what / next step.
2. `recon/integrations/INT-006-zenid-websdk.md` and
   `INT-007-zenid-api.md` — the ENV-specific posture rows.
3. `env/tst.json` and `env/tst-demo.json` — the
   `recaptcha_bypass_token`-style fields for `zenid_test_mode_token`
   etc.
4. `fixtures/secrets/photos/` (gitignored) — the synthetic OP/ŘP/SPZ
   photos + golden-master JSON.
5. `OQ-CP-23` status in SESSION-NOTES — promote from "open" to
   "closed" with the resolution noted.

## §E. Status

| Item | Value |
|------|-------|
| Document | `_install/contracts/zenid-test-data-request.md` |
| Companion strategy | `_specs/INTEGRATION-CONTRACTS-STRATEGY-v0.1.md` |
| Languages | CS (primary) + EN (forward to vendor) |
| Options offered | 3 (sandbox / SUT-skip-flag / golden-master fallback) |
| Status | draft v0.1 — review + send |
