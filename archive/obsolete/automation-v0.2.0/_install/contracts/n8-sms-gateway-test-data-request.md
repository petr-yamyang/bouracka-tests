# Žádost o testovací přístup k integraci N8 SMS Gateway — bouracka.cz testovací sada

> **Šablona pro odeslání kontaktní osobě v SUPIN/N8** (ideálně
> integračnímu architektovi pro projekt Bouračka + N8 vendor support).
> Po vyplnění editovat dle skutečnosti a odeslat. EN verze v §B.

---

## §A. Česká verze

```
Předmět: bouracka-tests — žádost o testovací přístup k integraci N8 SMS Gateway

Vážení kolegové,

v rámci přípravy automatizované testovací sady pro aplikaci Bouračka
(prostředí tst.bouracka.cz a tst.demo.bouracka.cz) potřebujeme nastavit
opakovatelné a deterministické testování průchodu obrazovkami:

  - 01_Potvrzení účastníků nehody (PING SMS Gateway)
  - 02_Ověření telefonních čísel (SEND OTP + ověření)
  - 17_Podpis účastníků pomocí SMS (sign OTP)

Vzhledem k tomu, že:
  • testovací sada poběží na třech notebookách v rámci ČKP/SUPIN intranetu
    (operátorský SUPNB001 + dva kolegovské SUPNB002, SUPNB003),
  • do testovacího prostředí nesmíme posílat reálné SMS na reálná čísla
    (nákladově + reputačně + GDPR),
  • automatizované testy potřebují deterministické odpovědi pro spolehlivé
    běhy (přijatý OTP musí být zpětně dostupný testu),

žádáme o jednu z následujících variant podpory (preferujeme variantu 2):

  ┌─ VARIANTA 1 — sandbox / test-mode přístup k N8 ─────────────────────┐
  │                                                                       │
  │ • testovací API klíč k N8 SMS Gateway pro tst.bouracka.cz            │
  │ • dokumentace request/response kontraktu — konkrétně:                 │
  │     - PING endpoint shape (URL, HTTP method, query params)            │
  │     - SEND OTP endpoint shape (URL, body schema, response shape)      │
  │     - 422 EX_CHYBA error envelope (struktura)                         │
  │     - rate limity (req/min) v testovacím režimu                       │
  │ • mechanismus pro test-side čtení odeslaného OTP (test-only inbound   │
  │   webhook? deterministic-OTP mode? polling endpoint pro poslední      │
  │   zaslaný kód podle phone+timestamp?)                                 │
  │                                                                       │
  └───────────────────────────────────────────────────────────────────────┘

  ┌─ VARIANTA 2 — konfigurační skip-flag v aplikaci (PREFERENCE) ────────┐
  │                                                                       │
  │ Dle analytické dokumentace (str. 25/133) aplikace Bouračka podporuje  │
  │ konfigurační přeskočení integrací v tst.* prostředích. Žádáme o:      │
  │                                                                       │
  │ • potvrzení, zda existuje flag specificky pro SMS Gateway:            │
  │     skip_integrations.sms = true                                      │
  │ • název konfiguračního atributu / environment variable / DB záznamu,  │
  │   který umožní flag flipnout                                          │
  │ • potvrzení, že v takovém případě aplikace generuje deterministický   │
  │   OTP lokálně (např. "0000" nebo "1234") a neposílá reálné SMS        │
  │ • per-session granularita (volitelná) — aby naše test runs           │
  │   neovlivňovaly ostatní testery ve sdíleném tst.* prostředí          │
  │                                                                       │
  └───────────────────────────────────────────────────────────────────────┘

Pokud žádná z variant není dostupná, fallback je Mockoon stub na
localhost — viz `mockoon/n8-sms-gateway.json` v naší testovací sadě.
V takovém případě bychom potřebovali:
  • potvrzení očekávaných response shapes pro PING / SEND OTP / VALIDATE
    OTP, aby naše Mockoon scénáře odpovídaly realitě N8

Co poskytujeme z naší strany:
  • plnou architekturu testovací sady (přístup zařídíme)
  • specifikaci „konzumací" N8 v testech: jakými scénáři, s jakými
    typy očekávaných odpovědí
  • podpis NDA, je-li požadováno
  • oddělené testovací účty (telefonní čísla) pro každý notebook
  • dohledatelnost veškerých testovacích volání (logy, request-id mapping)

Časový rámec: ideálně bychom potřebovali rozhodnutí o jedné z variant
do konce týdne 2026-05-15, aby další iterace prací (CP-SUPIN-04..08)
mohly pokračovat bez blokace.

Děkuji za pomoc a rád obratem upřesním cokoliv potřebujete vědět.

S pozdravem,
Petr Žemla
```

---

## §B. English version (forward to vendor if needed)

```
Subject: bouracka-tests — request for N8 SMS Gateway test-mode access

Dear Colleagues,

We are setting up an automated test suite for the Bouračka application
(environments tst.bouracka.cz and tst.demo.bouracka.cz). To exercise
the screens involving SMS Gateway integration (screen 01 PING; screen
02 phone-OTP verification; screen 17 sign-OTP) reliably and
deterministically, we need a test-mode posture that does not require
sending real SMS to real numbers.

Specifically, because:
  • the test suite runs on three notebooks inside the ČKP/SUPIN
    intranet (operator's SUPNB001 + two peers SUPNB002, SUPNB003),
  • sending real SMS to real numbers in the test env is prohibited by
    cost, reputation, and GDPR,
  • automated tests require deterministic responses (the received OTP
    must be readable back by the test),

we ask for one of the following (Option 2 is preferred):

  Option 1 — N8 sandbox / test-mode access:
    - test API key for tst.bouracka.cz
    - documentation of the request/response contract:
        * PING endpoint shape (URL, HTTP method, query params)
        * SEND OTP endpoint shape (body schema, response shape)
        * 422 EX_CHYBA error envelope structure
        * rate limits in test mode
    - mechanism for test-side reading of issued OTP (test-only inbound
      webhook? deterministic-OTP mode? polling endpoint?)

  Option 2 — SUT-side skip-flag for the integration (PREFERRED):
    Per the analytical doc (p. 25/133) Bouračka supports
    configuration-driven integration skipping in tst.*. We ask for:
    - confirmation whether a SMS-specific flag exists:
        skip_integrations.sms = true
    - the env var / DB record name that controls it
    - confirmation the SUT generates a deterministic OTP locally
      (e.g. "0000" or "1234") in this mode
    - per-session granularity (optional) so our test runs don't affect
      other testers in shared tst.* environments

If neither Option is available, fallback is the Mockoon stub on
localhost — see `mockoon/n8-sms-gateway.json` in our suite. In that
case we'd need:
  • confirmation of expected response shapes for PING / SEND OTP /
    VALIDATE OTP, so our Mockoon scenarios match real N8 behaviour

We provide on our side:
  • full architecture of the test suite (repo access can be arranged)
  • specification of how N8 is consumed in tests
  • NDA signature if required
  • separate test phone numbers per notebook
  • traceability of every test call

Timeline: ideally a decision on one of the options by end-of-week
2026-05-15 so that downstream iterations (CP-SUPIN-04..08) are not
blocked.

Thank you for the help — happy to expand on any point.

Best regards,
Petr Žemla
```

---

## §C. Where the answers land

When the SUPIN/N8 reply arrives, the operator updates:

1. `_install/contracts/responses-log.md` — add entry ASK-002.
2. `recon/integrations/INT-002-sms-gateway.md` — env-specific posture rows.
3. `env/tst.json` and `env/tst-demo.json` — `sms_gateway_mode` enum value.
4. `mockoon/n8-sms-gateway.json` — refine response shapes if N8 contract
   reveals shape differences from our best-guess.
5. `OQ-CP-27` status in SESSION-NOTES — promote from "open" to "closed".

## §D. Status

| Item | Value |
|------|-------|
| Document | `_install/contracts/n8-sms-gateway-test-data-request.md` |
| Companion strategy | `_specs/INTEGRATION-CONTRACTS-STRATEGY-v0.2.md` §3 |
| Languages | CS (primary) + EN (forward to vendor) |
| Options offered | 3 (sandbox / SUT-skip-flag / Mockoon fallback) |
| Status | draft v0.1 — review + send |
