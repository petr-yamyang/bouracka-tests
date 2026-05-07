# DEMO Bouračka — went public 2026-05-06

> **Trigger.** User direction CP-SUPIN-04 STEP 4 (2026-05-06):
> `https://demo.bouracka.cz/formular/` is now publicly reachable
> (was IP-restricted before). This is a major posture change for
> reverse-analysis: most recon work that previously depended on
> photos can now run against the live SUT directly.
>
> **Constraint.** Egress allowlist on this Cowork session does **not**
> currently include `demo.bouracka.cz` — see §1 below for unblock
> options. Until unblocked, this file collects *what we know* and
> *what we plan to capture*.

---

## §1. Reachability status (this session)

| Channel | Status | Unblock cost |
|---------|--------|--------------|
| `mcp__workspace__web_fetch` (sandbox HTTP) | **blocked** — `cowork-egress-blocked` | Settings → Capabilities → add `demo.bouracka.cz` (also recommend `bouracka.cz`, `*.bouracka.cz` for assets) |
| Claude in Chrome (real browser) | not connected | install/connect Chrome extension on this laptop |
| Operator-side `Invoke-WebRequest` | available | operator runs locally + pastes |

**Recommended primary**: connect Chrome — handles the SPA bundle, JS
state, network panel, reCAPTCHA — i.e. closes Tier 2a recon end-to-end.
**Recommended fallback**: allowlist; still useful for static asset URLs
+ API endpoints once we know the base.

## §2. What we expect to find at `demo.bouracka.cz/formular/`

Based on Tier 1 (analytical doc) + Tier 2b photo intel:

### §2.1 Probable bundle architecture

- SPA — likely Vue/React (analytical doc mentions Vue scaffolding).
- Mobile-first viewport — the `/formular/` route is the linear wizard
  through D00…D17.
- reCAPTCHA v3 invisible — badge bottom-right.
- Some asset CDN under `bouracka.cz` or third-party (image OCR is
  almost certainly delegated to a microservice).
- API base likely `/api/` on same origin OR a separate origin we'll
  identify from the network panel.

### §2.2 Behaviours to verify against analytical doc

The doc described 12 process steps + 18 screens (D00..D17). The
public DEMO will let us confirm or refute, screen by screen:

1. Whether the URL is `/formular/` (vs `/formular`) and whether the
   trailing slash redirects.
2. The exact entry-point UI: rozcestník (D00) + the "potvrzení účastníků"
   (D01) + "ověření telefonních čísel" (D02).
3. Field IDs / names in the DOM — these become locator strategies for
   Playwright/Cypress/TestCafe.
4. Validation rules in their actual JS-fired form (regex, min/max
   lengths, error messages).
5. Whether `reCAPTCHA` fires on first interaction or on submit.
6. The state-machine transitions
   (`accidentReportStatus: NEW → IN_PROGRESS_DRIVERS → …`) — how
   they're surfaced to the client (URL? localStorage? server round-trip?).
7. Codelist contents (DEMO is likely on a static/sandbox copy of
   AISPOV/CRR/CRV/ROB).
8. SMS gate: DEMO will likely **mock** the SMS or expose a
   `?otp_for_test=1234` style hint (per OQ-CP-27 working hypothesis).

### §2.3 Behaviours that will diverge from PROD

See `DELTA-DEMO-vs-PROD-v0.1.md`. Quick list:

- N8 SMS gateway → mocked on DEMO; real on PROD.
- AISPOV ROB/CRR/CRV → likely sandbox/empty on DEMO; real on PROD.
- ZID / zenID → likely test-key on DEMO; real on PROD.
- Codelists → may be frozen snapshots on DEMO.
- Email dispatch → DEMO may sink to a black hole or to a tester inbox.

## §3. Capture plan once unblocked

Run in this order (each step closes a gap from the working-lessons
doc and produces a concrete artefact):

1. **GET `/formular/`** → harvest:
   - HTML shell (probably a div + `<script src=…>` references).
   - Bundle URLs (JS, CSS).
   - Any SSR-rendered initial state.
   - HTTP headers (CSP, CORS, cookies, X-* custom).
2. **GET each bundle URL** (or rely on Chrome's source panel) → harvest
   route table, store schema, validator regex set, copy strings.
3. **Drive D00..D17 in browser** with synthesis-quality test data:
   - Czech phone numbers (use the documented `+420` regex)
   - OP / ŘP / SPZ — bouračka should accept ANY format-valid synthetic
   - Capture network panel for each step → `recon/network-traces/demo/`
4. **Extract codelist contents** by dropdown enumeration — these
   become `fixtures/codelists.yaml` confirmations.
5. **Capture validation messages** by submitting deliberately-broken
   data → `recon/validation-corpus/demo/`.
6. **Document ALL the URLs the SPA hits** → integrations contract.

## §4. What this enables (downstream)

- **Recon path A → Recon path B compression.** L-WORK-1..7
  (photo-driven) compresses by ~70 % because we no longer need
  photographic coverage of DEMO; live navigation IS the source.
- **TC dev unblock.** TC-CP-006..023 SPEC.md depth was waiting for
  GAP-1 (analytical doc pages 43-133) + GAP-2 (real screen recon).
  Public DEMO collapses GAP-2 entirely.
- **Mockoon profile validation.** N8 SMS gateway mock
  (`mockoon/n8-sms-gateway.json`) was authored against analytical-doc
  intel only. Live DEMO behaviour confirms or refutes the route shapes.
- **First runnable suite.** Playwright smoke against
  `demo.bouracka.cz/formular/` (no auth, no IP gate, no reCAPTCHA
  bypass token needed in headed mode for local-laptop runs) → one or
  two TCs go green this session.
- **Delta matrix.** `recon/DELTA-DEMO-vs-PROD-v0.1.md` lets us assign
  every TC an `env_constraint`: DEMO-only, PROD-only, or both.

## §5. What does NOT change

- **PROD-Bouračka still gates the integration TCs.** Real N8, real
  AISPOV, real ZID can only be exercised against PROD/tst. Photo +
  colleague-capture remains the recon mode for those.
- **CS-only output policy** (DOCUMENTATION-POLICY §1) unchanged.
- **VUP/UML bottom-up reconstruction** (L-WORK-5..7) unchanged —
  Use Case → Activity → Sequence per flow folder, just now driven
  by live navigation instead of photos for the DEMO branch.

## §6. First observations from operator screenshot (2026-05-06 ~10:05 CET)

> Captured via operator's full-window browser screenshot, supplied
> while we wait for Claude in Chrome to handshake. Treat as Tier 2a
> evidence (live SUT) with caveat: only one viewport, only the
> rozcestník screen, no DOM/network capture yet.

### §6.1 Confirmed page identity

- URL: `https://demo.bouracka.cz/formular/` — trailing slash present.
- Page IS the **rozcestník** (D00 equivalent), not the wizard's first
  step. The wizard starts AFTER the user clicks `VYPLNIT ZÁZNAM`
  (presumably mounts at `/formular/zaznam/` or hides behind a JS
  router push — to confirm post-handshake).

### §6.2 Confirmed DEMO branding (Δ11 → confirmed)

- Top-left logo lockup: `DEMO VERZE` superscript above `BOURAČKA.CZ`,
  alongside ČKP (Česká kancelář pojistitelů) wordmark.
- Persistent orange warning banner directly under header:
  > "Nacházíte se v DEMO VERZI aplikace. Všechny údaje v této verzi
  > jsou pouze ukázkové. Formulář si můžete bezpečně vyzkoušet bez
  > zadávání reálných údajů."
- Implication for screenshot-baseline TCs: header + banner regions
  MUST be excluded from DEMO-vs-PROD pixel diffs (or two baseline
  sets, env-keyed).

### §6.3 Confirmed R1 scope (from rozcestník copy)

The card "Záznam o dopravní nehodě" subtitle codifies R1 scope verbatim:

> "Vhodné pro malé nehody bez zranění a škody do 200 000 Kč vzniklé
> mezi 2 účastníky s českými občanskými průkazy."

This pins the legal/business contract:
- ≤ 200 000 Kč damage cap
- exactly 2 účastníci
- both with české občanské průkazy
- no injuries

→ matches what's in `01_TestTargets::scope_in_r1` already; minor
copy refresh on `06_POKRYTI-CS.md` may be warranted to quote
verbatim from production string.

### §6.4 Other on-page elements

| Element | Position | Observation |
|---------|----------|-------------|
| H1 | top of content | `Stala se vám dopravní nehoda? To zvládnete.` |
| Emergency exit card | first card | `Tísňové volání` — phone-icon CTA right side |
| Police-criteria card | second card | `Kdy volat Policii ČR?` — content collapsed by default? |
| **Primary CTA card** | third card | `VYPLNIT ZÁZNAM` blue full-width button |
| Safety-checklist section | below CTA | `CO DĚLAT PŘI NEHODĚ?` with green-check bullets |
| reCAPTCHA badge | bottom-right | present; partially hidden by chatbot bubble |
| Chatbot bubble | bottom-right | orange floating bubble — widget service unknown (suspicion: integrated AI-helper or similar) |

### §6.5 New TT/TC candidates surfaced from the rozcestník alone

- **TC-CP-NEW-A** — assert that the orange DEMO banner copy matches
  the verbatim string above; absence implies a config bug or
  PROD-bundle-leak into DEMO.
- **TC-CP-NEW-B** — assert the R1 scope sentence is rendered exactly;
  if the threshold changes (e.g. 250 000 Kč after future
  legislation), this TC catches it.
- **TT-CP-NEW-X** — chatbot bubble integration: until now uncatalogued
  in `recon/integrations/`. Capture the script src to identify the
  vendor; document as new INT-NNN.
- **Possible R2 TC** — police-criteria card behaviour (collapsed vs
  expanded; might be a click-to-expand, might be a separate route).

### §6.6 What still needs Chrome handshake

- DOM tree (locator strategies; field IDs)
- Network panel (API base, OPTIONS preflights, asset CDN)
- JS bundle URLs + reading them for state schema, validators, copy
- Walking past `VYPLNIT ZÁZNAM` into the wizard itself (D01..D17)
- Clicking the chatbot bubble to identify vendor
- Inspecting reCAPTCHA site key
- Cookie / localStorage state inspection

## §7. Status

| Item | Value |
|------|-------|
| DEMO entry point | `https://demo.bouracka.cz/formular/` |
| Public since | 2026-05-05 (overnight) |
| Reach this session | partial — operator screenshot landed §6; awaiting Chrome handshake for DOM/network |
| Photo dependency for DEMO | dropped (Tier 2a now scrape-capable, screenshot+Chrome path) |
| Photo dependency for PROD/tst | unchanged (Tier 2b still photo-only) |
| Δ matrix rows confirmed | 1 (Δ11 — DEMO branding) |
| Status | scaffold v0.2 — first observations folded; deeper capture pending Chrome connect |
