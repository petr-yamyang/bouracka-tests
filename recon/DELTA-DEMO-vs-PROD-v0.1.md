# DELTA matrix — DEMO Bouračka vs PROD Bouračka — v0.1

> Per CP-SUPIN-04 STEP 5. Tracks every observed or hypothesised
> behavioural divergence between `demo.bouracka.cz` (Tier 2a, public
> since 2026-05-06) and `bouracka.cz` / `tst.bouracka.cz` (Tier 2b,
> integration-fidelity reference).
>
> **Why this matters.** A TC that passes on DEMO but is meaningless
> against PROD (e.g. SMS-gate happy path with mock OTP `1234`) MUST be
> tagged `env: demo-only`. A TC that requires real integration behaviour
> (e.g. AISPOV lookup against the real ROB) MUST be tagged
> `env: prod-only`. Most TCs cover both, with adapters.
>
> **Confidence tags** (last column):
> - `confirmed` — observed on both envs same session
> - `expected` — hypothesised from analytical doc / OQ-CP-* responses
> - `unknown` — needs capture
> - `legacy` — taken from photo-era recon, may be stale

---

## §1. Integration-layer deltas (the big ones)

| # | Integration | DEMO behaviour | PROD/tst behaviour | TC impact | Confidence |
|---|-------------|----------------|--------------------|-----------|------------|
| Δ1 | **N8 SMS Gateway** (INT-002) | **NO SMS dispatched on DEMO**. UI copy: *"Demoverze žádné SMS neodesílá, potvrzovací kód bude v dalším kroku automaticky doplněn."* OTP appears auto-filled on next screen (TBC-confirm) | real SMS dispatch via N8; OTP delivered to the operator's phone | TC-CP-005 / TC-CP-005-PROD; Mockoon profile may need refactor (DEMO behaviour ≠ Mockoon "1234" assumption — DEMO injects on the *next page*, not in the response payload) | **confirmed** (live-walk 2026-05-06; STR-014 evidence) |
| Δ2 | **AISPOV — ROB lookup** (INT-003) | sandbox / empty / synthetic responses | real Registry of Persons | TC-CP-008/009/010 driver-data-load; expected results differ | expected |
| Δ3 | **AISPOV — CRR lookup** (vehicle reg) | sandbox / synthetic | real Central Vehicle Register | TC-CP-014/015 vehicle-data-load | expected |
| Δ4 | **AISPOV — CRV** (insured-vehicle) | sandbox / synthetic | real Central Insured-Vehicle DB | TC-CP-014/015 + insurance partner-routing | expected |
| Δ5 | **ZID / zenID** (OP/ŘP OCR) | likely sandboxed / always-success / always-fail | real document OCR via zenID SDK | TC-CP-007/013 OCR-vs-manual-fallback | expected |
| Δ6 | **reCAPTCHA v3** | site key may differ; threshold may be relaxed | strict threshold; 0.5+ score | smoke + abuse TCs | unknown |
| Δ7 | **Email dispatch** (INT-005) | sinks to tester inbox or `/dev/null` | real SMTP to participant emails | end-of-flow assertion in TC-CP-022 final-confirmation | unknown |
| Δ8 | **OneSignal push** (INT-006) | likely disabled | real push delivery | not in R1 scope; future TC | legacy |

## §2. Configuration-layer deltas (codelists, copy, IDs)

| # | Surface | DEMO | PROD | TC impact | Confidence |
|---|---------|------|------|-----------|------------|
| Δ9 | **Insurance partners list** | may be a frozen snapshot | live partner directory | dropdown content tests; partner-routing branches | unknown |
| Δ10 | **Codelists** (vehicle categories, accident types) | likely identical (same bundle) | identical | no impact | expected |
| Δ11 | **CSS / branding** | `DEMO VERZE` superscript over `BOURAČKA.CZ` logo + persistent orange banner ("Nacházíte se v DEMO VERZI aplikace…") under header | clean PROD branding (no banner, plain BOURAČKA.CZ + ČKP lockup) | screenshot-baseline TCs MUST be env-aware; header+banner region excluded from pixel diff or two baselines per env | **confirmed** (operator screenshot 2026-05-06 10:05 CET) |
| Δ12 | **CSP / cookie domains** | `*.demo.bouracka.cz` | `*.bouracka.cz` | runtime config for Playwright base URL | expected |
| Δ13 | **GA / GTM / analytics** | likely test/staging IDs or off | live IDs | exclusion in test runs (already handled by Playwright network mocking) | unknown |
| Δ14 | **Service worker / PWA** | both should ship same SW | same | no impact | expected |

## §3. Behavioural deltas (validation, state, UI)

| # | Behaviour | DEMO | PROD | TC impact | Confidence |
|---|-----------|------|------|-----------|------------|
| Δ15 | **State machine transitions** (`accidentReportStatus`) | identical (same bundle) | identical | TC suite runs on both | expected |
| Δ16 | **Validation rule firing** (regex, min/max lengths) | identical | identical | identical TCs | expected |
| Δ17 | **Error message copy** (CS strings) | identical | identical | identical TCs | expected |
| Δ18 | **PING gate retry behaviour** (INT-002 PING_NOK) | mock injects fail mode on demand | real outage hard to reproduce | TC-CP-005 alt-path runs only on DEMO with mock | expected |
| Δ19 | **Rate limiting / abuse throttle** | likely off or relaxed | strict | abuse TCs are PROD-only or DEMO with explicit skip-flag | unknown |
| Δ20 | **Form clearing / refresh recovery** | identical | identical | TC-CP-003 (resilience) | expected |

## §4. What we'll learn first when DEMO is reachable

Capture order and what each entry resolves:

| Capture step | Resolves Δ | Effort |
|--------------|------------|--------|
| GET `/formular/` shell + bundle URLs | (foundation; reveals API base, CSP header) | 1 fetch |
| OPTIONS / GET `/api/*` (or whatever the SPA hits) | Δ1, Δ2, Δ3, Δ4, Δ5, Δ7, Δ12 | 5–10 fetches |
| Drive D00–D02 with mock OTP | Δ1, Δ6, Δ15 | live session |
| Drive D03–D06 with synthetic OP/ŘP | Δ2, Δ5, Δ16, Δ17 | live session |
| Drive D08–D11 with synthetic SPZ | Δ3, Δ4, Δ16 | live session |
| Drive D12–D17 to completion | Δ7, Δ15, Δ18, Δ20 | live session |
| Inspect bundle source for env-config values | Δ6, Δ9, Δ12, Δ13 | source read |
| Visual diff DEMO vs analytical doc | Δ11, Δ17 | per-screen |

## §5. How TCs reference this matrix

In `02_TestCases::env_constraints`, allowed values:

| Value | Meaning | Examples |
|-------|---------|----------|
| `both` | Same behaviour, runs identically | TC-CP-001 (smoke), TC-CP-002 (state-machine), TC-CP-018 (validation) |
| `demo-only` | Requires mock OTP / sandbox lookup; PROD would dispatch real SMS or real registry call | TC-CP-005 (SMS-gate-mock), TC-CP-009 (ROB-sandbox-data) |
| `prod-only` | Requires real integration response; cannot run on DEMO without false signal | TC-CP-005-PROD (SMS-gate-real-OTP), TC-CP-022 (email dispatch real) |
| `both-with-adapter` | Same shape, different fixture set per env | TC-CP-008 (driver-data-load with env-keyed fixture) |

## §5b. Cookie banner — first-visit gate (discovered 2026-05-06 via Playwright)

| # | Surface | DEMO | PROD | Confidence | TC vliv |
|---|---------|------|------|------------|---------|
| Δ32 | **Cookie consent modal** ("Používáme cookies") | ANO — centered modal blocks rozcestník H1 on first visit; 3 buttons: POVOLIT VŠE / NASTAVENÍ COOKIES / ODMÍTNOUT VŠE | ANO — předpoklad shodný (stejný JS bundle) | confirmed (DEMO Playwright run 2026-05-06) | TC-CP-001 (smoke) MUSÍ dismissnout před asercemi; TT-CP-R2-COOKIE povýšeno na R1-relevant |

**Důsledek pro test design:**
- Každý TC, který běží proti čerstvé browser session, MUSÍ obsahovat
  cookie-banner dismiss step jako STEP 0
- Helper `dismissCookieBanner()` v `playwright/tests/bring-up-smoke.spec.ts`
  reusable; doporučuje se přesun do `playwright/helpers/page.ts`
- Privacy-preserving default: klik na "ODMÍTNOUT VŠE" (per Claude
  user_privacy guidance — privacy-first volba)

**Důsledek pro analytický dokument:**
- Earlier Chrome-driven walk neviděl banner protože browser měl už
  cookies nastavené z jiných návštěv
- Playwright fresh context = fresh cookies = banner visible
- Live-copy-strings.yaml přidá STR-018..STR-022 pro cookie banner copy

## §6. New deltas surfaced from live-walk 2026-05-06

| # | Surface | DEMO | PROD | TC impact | Confidence |
|---|---------|------|------|-----------|------------|
| Δ21 | **Pre-wizard intro screen** `/formular/informations` | present (5-step "Co vás čeká?" overview gate) | TBC — likely identical (same bundle) | TC-CP-NEW-E asserts intro renders pre-wizard | confirmed on DEMO; expected on PROD |
| Δ22 | **Phase-1 DEMO hint text** ("Demoverze žádné SMS neodesílá…") | rendered above phone input | MUST be absent | TC-CP-NEW-J asserts hint absent on PROD | confirmed on DEMO |
| Δ23 | **Google Maps locale** | `intl/en_gb/` — UI Czech but Maps in EN-GB | TBC; same bundle suggests identical bug | TC-CP-NEW-M asserts `cs` locale; defect-likely candidate | confirmed (Δ + locale mismatch) |
| Δ24 | **Outage feed origin** | Azure Static Web `bourackaodstavky78861.z6.web.core.windows.net` | TBC — likely identical | (none; infrastructure note) | confirmed on DEMO |
| Δ25 | **API base** | `demo.bouracka.cz/api/` | `bouracka.cz/api/` | base-URL config keyed off env | expected |
| Δ26 | **Report-UUID lifecycle** | `POST /api/reports` mints UUID; deep-linkable; data purges if not bilateral-confirmed | identical contract expected; persistence semantics may differ | TC-CP-NEW-F (envelope), TC-CP-NEW-G (deep-link), TC-CP-NEW-K (purge-on-abandon) | confirmed on DEMO; expected on PROD |

## §7. Status

| Item | Value |
|------|-------|
| Matrix | `recon/DELTA-DEMO-vs-PROD-v0.1.md` |
| Δ rows | 26 (8 integration + 6 config + 6 behavioural + 6 live-walk surfaced) |
| Confirmed on DEMO | 7 (Δ1 + Δ11 + Δ21 + Δ22 + Δ23 + Δ24 + Δ26) |
| Expected | 11 |
| Unknown | 7 |
| Legacy | 1 |
| Status | v0.2 — live-walk 2026-05-06 added 6 deltas + confirmed 2 expected; PROD-side capture still pending |
