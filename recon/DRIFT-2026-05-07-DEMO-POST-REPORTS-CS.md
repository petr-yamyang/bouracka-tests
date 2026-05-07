# Drift report — DEMO Bouračka POST /api/reports — 2026-05-07

> **Detekováno.** 2026-05-07 dopoledne, HP Elite (<test-runner-host>) v interní síti SUPIN
> proti `https://demo.bouracka.cz`.
> **Závažnost.** ★ vysoká — blokuje hlavní E2E happy-day i 3 z 8 alternates.
> **Status.** drift potvrzen empiricky (HP Elite spec runs); obejito v testovací
> sadě v0.4.8 přes „skip-with-rationale".

---

## §1. Symptomy

### §1.1 Direct API call (ALT-9)

```
POST https://demo.bouracka.cz/api/reports
Content-Type: application/json
{}

→ HTTP/1.1 403 Forbidden    (dříve 200 + UUID v4)
```

Naposledy ověřeno **GREEN** v `recon/DEMO-PUBLIC-LIVE-2026-05-06.md` §6.4.

### §1.2 SPA-driven flow (a1-main-happy-day, ALT-1, ALT-4, ALT-5)

```
GET  /formular/                       → 200
GET  /formular/informations           → 200  (intro screen renders)
click [Rozumím]
POST /api/reports                     → 403  (suspect; not visible to user)
GET  /formular/error/timeout          → 200  (SPA's error route)
```

Test asserce na `URL ~ /verification/` selhává s reálným URL
`https://demo.bouracka.cz/formular/error/timeout`.

## §2. Hypotéza root cause

| # | Hypotéza | Pravděpodobnost | Test |
|---|----------|-----------------|------|
| H1 | DEMO server nově vyžaduje **reCAPTCHA token** v body / headeru `POST /api/reports` (zarovnání s PROD security baseline). | ★★★ vysoká | spuštění ALT-10 SPA-probe v0.4.8 → response body / header analysis |
| H2 | DEMO server nově vyžaduje **Origin / Referer / CSRF cookie** (anti-abuse zpřísnění). | ★★ střední | curl s plnou sadou hlaviček vs. bez |
| H3 | DEMO byl **redeployed** a ztratil mock-allow-empty konfiguraci. | ★ nízká | dotaz na DEMO ops — kontrola release notes |
| H4 | Rate-limit kicked in — IP HP Elite (<test-runner-host>) byla zablokována. | ★ nízká | běh z jiného CIDRu (ThinkPad přes mobilní hotspot) |

## §3. Forensic — actual SPA request (z HP Elite trace 2026-05-07 14:54 UTC)

> **Source.** Playwright auto-trace (`a1-main-happy-day-demo` run, project
> `tst-demo-mobile-375`, BASE `https://demo.bouracka.cz`).
> **Trace path** (uvnitř ZIPu Pete poslal): `playwright-report/data/<sha>.zip → 0-trace.network`.
> **Response body** (`resources/10f0fb4577795cb0ca18f293c8444b229b142f6c.json`):
> `{"timestamp":"2026-05-07T12:54:29.359968705Z","correlationId":"<uuid-redacted>","status":403,"error":"Forbidden","message":"Forbidden","path":"/reports"}`

### §3.1 Request shape — to co SPA POSILA

```http
POST https://demo.bouracka.cz/api/reports HTTP/2.0
:authority:        demo.bouracka.cz
content-length:    0
content-type:      (no body sent)
accept:            application/json, text/plain, */*
accept-language:   cs-CZ
cookie:            TECHNICAL_COOKIES=false
origin:            https://demo.bouracka.cz
referer:           https://demo.bouracka.cz/formular/informations
sec-ch-ua:         "HeadlessChrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"
sec-fetch-dest:    empty
sec-fetch-mode:    cors
sec-fetch-site:    same-origin
user-agent:        Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.7727.15 Safari/537.36
x-captcha-token:   <real Google reCAPTCHA-v3 token, 2400+ characters>
x-correlation-id:  <uuid-redacted>
```

### §3.2 Response shape — to co server vrací

```http
HTTP/2.0 403 Forbidden
access-control-allow-credentials:  true
access-control-allow-methods:      GET, POST, PUT, HEAD
access-control-allow-origin:       https://demo.bouracka.cz
content-type:                      application/json
content-length:                    174
date:                              Thu, 07 May 2026 12:54:29 GMT
x-azure-ref:                       <azure-front-door-ref-redacted>
x-correlation-id:                  <uuid-redacted>

{"timestamp":"2026-05-07T12:54:29.359968705Z","correlationId":"<uuid-redacted>","status":403,"error":"Forbidden","message":"Forbidden","path":"/reports"}
```

### §3.3 Re-vyhodnocení hypotéz z §2

| Hyp | Status po forensic | Evidence |
|----|---------------------|----------|
| H1 reCAPTCHA token nyní povinný | **VYVRÁCENO** | SPA token POSÍLÁ (header `x-captcha-token`, ~2400 znaků = legit Google v3 token) |
| H2 Origin/Referer/CSRF | **VYVRÁCENO** | Origin + Referer + CORS všechny správné, server akceptuje preflight |
| H3 DEMO redeploy ztratil mock-allow | **PRAVDĚPODOBNÉ** | Generic `"Forbidden"` error neprozrazuje reason; odpovídá change v captcha verification config |
| H4 Rate-limit IP HP Elite | **NEPRAVDĚPODOBNÉ** | Stejný 403 i z ThinkPad recon 2026-05-06 |

### §3.4 Nová hypotéza H5 — **reCAPTCHA-v3 score-based bot detection**

**Best-fit hypotéza po forensic.** reCAPTCHA v3 nepoužívá CAPTCHA-puzzle UI — místo
toho vrací score 0.0..1.0 ("human likelihood"). Server porovnává score vs. threshold
a 403-uje pod thresholdem. Tři evidence body:

1. **User-Agent:** `HeadlessChrome v147` — Google's bot detection modely flagují
   `HeadlessChrome` agresivně. Score typicky < 0.3.
2. **Cookie:** `TECHNICAL_COOKIES=false` — GDPR essential-only mode → žádné
   analytics cookies → reCAPTCHA nemůže korelovat s historickou důvěrou.
3. **Stack:** Azure Front Door (`x-azure-ref` header) → Spring Boot backend
   (`/reports` path style + JSON `{timestamp, correlationId, status, error, message, path}`)
   → typický reCAPTCHA-gated pipeline patter