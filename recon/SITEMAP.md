# SITEMAP — public bouracka.cz — CP-SUPIN-02 recon — 2026-05-05

> Authoritative public-side page graph as observed during CP-SUPIN-02.
> Per CLIENT-PILOT-SUPIN-V0.1.md AMENDMENT 1: this is the **structural
> basis**; per-env divergences (TEST + DEMO) are a **delta layer** on
> top, supplied via user-filled recon templates.

## §1. Pages reached and structure

| Path | Status | Title (CS) | Purpose | Recon ref |
|------|--------|------------|---------|-----------|
| `/` | 200 | "Bouračka.cz - Vyplňte formulář jednoduše online" | Landing page; hero + 3-step explainer + project-team band + "kdy volat policii" interlock + FAQ accordion (5 items) + media block | SCR-001 |
| `/formular` | 200 | "ČKP - Bouračka" | Wizard gateway: emergency-call card, kdy-volat-policii decision link, primary CTA "VYPLNIT ZÁZNAM", on-scene checklist; reCAPTCHA badge present | SCR-002 |
| `/formular?utm_source=landing` | 200 | (same) | Marketing-attribution variant of `/formular`; same DOM | SCR-002 |
| `/formular/personal-data` | 200 (not entered in recon — link only) | "Zpracování osobních údajů" | GDPR processing notice for the wizard | SCR-005 (deferred) |
| `/faq` | 200 | "Bouračka.cz - Vyplňte formulář jednoduše online" | FAQ taxonomy of 6 categories (Základní info / Technické požadavky / Vyplňování / Bezpečnost / Výstupy / Ostatní) — accordion items | SCR-003 |
| `/tz-ckp-bouracka.pdf` | (asset) | (PDF) | Press release "O kampani — Tisková zpráva" | non-test |
| `/dotazy.pdf` | (asset, search-confirmed) | (PDF) | Older Q&A document | non-test |

## §2. In-page anchor sections (landing only)

| Anchor | Heading (CS) | Purpose |
|--------|--------------|---------|
| `#kdy` | "V jaké situaci se záznam o nehodě vyplňuje" | Eligibility list (3 conditions) + police-call interlock |
| `#jak` | "Jak to probíhá?" | 5-step explainer + manual link + video play button |
| `#bezpecnost` | "Bezpečnost a soukromí" | GDPR/security 2-bullet card + memorandum link |
| `#dotazy` | "Často kladené otázky" | FAQ accordion (5 items) + "Zobrazit všechny dotazy (FAQ)" link to `/faq` |
| `#pro-media` | "Pro média" | Press kit card linking to `/tz-ckp-bouracka.pdf` |

## §3. External references (off-domain)

| Target | Kind | Used by |
|--------|------|---------|
| `tel:112` | tel-uri | `/formular` emergency-call card; `/` "kdy volat policii" |
| `tel:158` | tel-uri | `/formular` police-decision branch button |
| `mailto:info@bouracka.cz` | mailto | Footer contact card |
| `https://www.instagram.com/bourackacz` | social | Footer |
| `https://www.youtube.com/@ceskakancelarpojistitelu` | social | Footer |
| `https://www.ckp.cz/images/clanky/cz/bouracka/bouracka-manual-uzivatele.pdf` | PDF | "Uživatelský manuál" (landing #jak) |
| `https://www.ckp.cz/images/clanky/cz/O_nas/bouracka-informacni-memorandum-GDPR.pdf` | PDF | Footer "Chráníme Vaše osobní údaje" |
| `https://ecdn.supin.cz/cookie/2.0.0/ckp/cookies_ckp_cz.pdf` | PDF | Footer "Cookies" — **SUPIN CDN ownership marker** |

## §4. Owner/operator chain

```
End-user (CS-locale, mobile-primary, anonymous)
        │
        └── bouracka.cz                          (front-of-house)
                │
                └── Česká kancelář pojistitelů   (legal operator;
                                                  per copyright + footer
                                                  + GDPR memorandum)
                        │
                        └── SUPIN.cz             (platform / CDN /
                                                  cookie-doc host;
                                                  internal-network
                                                  test envs reside here)
```

## §5. Surfaces NOT reached during this recon (deliberate)

- The multi-step wizard interior (post-`/formular` "VYPLNIT ZÁZNAM"
  click) was **not exercised** to avoid driving against production +
  triggering Google reCAPTCHA bot heuristics. Per CLIENT-PILOT-SUPIN
  C-2: deep wizard recon is a `tst.*`-side activity supplied via
  user-filled recon-template emails.
- `/formular/personal-data` not opened (link only); will be SCR-005 if
  needed for assertion targets in TC-CP-003/004.
- The video player ("Jak na to") was not played — irrelevant to test
  scope.
- The hamburger menu (`Open menu` in header `<banner>`) was not
  expanded — desktop layout already shows the same nav links;
  expansion is a TC-mobile-specific surface for the AMENDMENT 2
  viewport spec.

## §6. Anti-bot / gating posture (binding for framework choice)

- **Google reCAPTCHA** badge present on `/formular` (SCR-002) — exact
  variant unknown without DOM-deep inspection (likely v3 invisible
  given the badge-only UX).
- No visible rate-limit; no robots.txt was reachable from the sandbox
  — `bouracka.cz/robots.txt` not retrievable through the egress
  proxy; if the user can fetch it from inside SUPIN's network, attach
  via `[SUPIN-RECON] [META] robots.txt`.
- Cookies / GDPR banner was **not observed** during recon (likely
  because the connected Chrome already has the consent set for this
  domain from prior browsing). Cookie-banner behaviour will need a
  fresh-context test pass — flagged for CP-SUPIN-03.

## §7. Status

| Item | Value |
|------|-------|
| Document | `recon/SITEMAP.md` |
| Iteration | CP-SUPIN-02 |
| Public pages reached | 4 (+ 2 anchors-only on landing) |
| Off-domain refs catalogued | 8 |
| Wizard interior recon | NOT performed (deliberate; tst.*-side delta) |
| Confidentiality posture | recon material is gitignored on dev side per scope §7 — this file is PUBLIC recon and is OK to commit |
| Status | v0.1 — seeded; will be amended as user-supplied tst.* materials arrive |
