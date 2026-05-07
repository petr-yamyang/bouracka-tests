# Synchro MacBook — CP-SUPIN-05 v0.5.0 EOD — 2026-05-07

> **Adresát.** MacBook session (analytical MI-M-T context).
> **Z.** ThinkPad Opus session, 2026-05-07 (full day).
> **Cíl.** Aktualizovat MacBook s velkým posunem do CP-SUPIN-05 fáze;
> nahrazuje předchozí `SYNCHRO-MACBOOK-CP-SUPIN-04-2026-05-07-EOD.md`.

---

## §1. Velký posun za 24 h

CP-SUPIN-04 closure → CP-SUPIN-05 seed v jednom dni. Dva hlavní pivots:

### §1.1 Email scanner pivot (PowerShell → Python orchestrace)

v0.4.9 byla zablokována Gmail/Active24 scannery (22 .ps1 + IOC strings).
v0.4.9.1-SAFE → v0.5.0 odstranily VŠECHNY .cmd/.ps1 z bundle a nahradily
orchestraci jediným `bouracka.py` (pure Python stdlib + subprocess).

**Důsledek pro MI-M-T:** kterýkoliv test kit emailovaný do enterprise
prostředí MUSÍ projít `tools/preship_audit.py` PASS. Toto je generalizovatelné
pravidlo — viz `_specs/EMAIL-DELIVERABILITY-RULES-v0.1-CS.md`.

### §1.2 DEMO drift forensic + reCAPTCHA hypothesis

HP Elite (<test-runner-host>) run zachytil **plný SPA POST /api/reports trace** —
včetně `x-captcha-token` header (legit Google reCAPTCHA v3 token, ~2400 char).
Server vrací 403 Forbidden DESPITE token. Best-fit hypothesis:
**reCAPTCHA-v3 score-based bot detection** flag-uje HeadlessChrome UA.

**Důsledek:** drift-fix path candidates jsou (a) headed mode, (b) mock bypass
token z DEMO ops, (c) puppeteer-stealth ekvivalent pro Playwright,
(d) admin-side report-ID pre-mint.

## §2. CP-SUPIN-05 strategic plan — 5 streams konsolidovány

**Read order pro MacBook:**
1. `_specs/CP-SUPIN-05-PLAN-CS.md` (master plan)
2. `_specs/VMODEL-ASSEMBLY-TT-MAPPING-v0.1-CS.md`
3. `_specs/CROSS-FRAMEWORK-DATA-SHARING-v0.1-CS.md`
4. `_specs/COVERAGE-RULE-STRATEGY-v0.1-CS.md`
5. `_specs/CIL-2-ENABLEMENT-v0.1-CS.md`
6. `recon/ARCHITECTURE-OVERVIEW-v0.1-CS.md` (8 numbered flows + 6 new components)

## §3. MI-M-T extraction candidates

Z 5 nových docs jsou tyto patterns **generalizovatelné** mimo Bouračka case:

| Pattern | Generalizable? | MI-M-T module? |
|---------|----------------|----------------|
| Email-deliverability rules (forbidden ext + IOC scan + Python-first) | ★★★ universal | yes — packaging governance module |
| V-model 4-layer TT taxonomy (FUNC/SCRN/LOV/ACTV) | ★★★ universal | yes — methodology module |
| Cross-framework data sharing (single-source YAML + per-framework loaders) | ★★★ universal | yes — test-data governance module |
| Coverage rule phased introduction (informational → soft → gating per-class → strict) | ★★★ universal | yes — coverage governance module |
| 4-target gradual delivery (DEMO public → DEMO test → PROD test → PROD prelive) | ★★ context-dependent | partial — adapt per SUT environment topology |
| Drift detection convention (per-env Δ matrix + drift docs naming) | ★★★ universal | yes — environment governance module |
| Pre-ship audit script | ★★★ universal | yes — directly portable |

## §4. Co MacBook může napsat (návrh)

V iteration po MacBook-side:

1. **`_specs/MIMT-METHODOLOGY-PROPOSAL-v0.2.md`** — z 7 patterns výše vyčlenit
   universal module proposals + Bouračka-specific specializations.
2. **`_specs/MIMT-IMPORT-CONTRACT-DRAFT.md`** — Excel + JSON exchange format
   spec (TestPlan + RunResults + CoverageMatrix); kompatibilní s budoucím
   MI-M-T live workbook.
3. **`_specs/MIMT-COMPONENT-MIGRATION-v0.2.md`** — z `tools/*.py` které jsou
   kandidáti pro MI-M-T modules:
   - `preship_audit.py` → universal packaging gate
   - `coverage_audit.py` → universal coverage gate
   - `validate_workbook.py` → universal Excel governance
   - `migrate_to_v04_*` → versioned schema migrations (template pattern)

## §5. Co NEpsát z MacBook (Opus governance scope)

- Změny Excel schema → jen Opus (ThinkPad)
- Změny v Bouračka tests → Sonnet branch sessions
- Změny naming conventions → Opus
- Drift recon updates → Opus (žije u live evidence z HP Elite)

## §6. 3-device sync status (per `THREE-DEVICE-PLAN-CS.md`)

| Device | Status (2026-05-07 EOD) |
|--------|--------------------------|
| ThinkPad | full Opus session ran 2026-05-07 (CP-SUPIN-04 closure + CP-SUPIN-05 seed); session closed |
| MacBook | this synchro doc je entry; pull GitHub when ready |
| HP Elite | first run 2026-05-07 14:09 OK (validate-install + sanity-check + bring-up GREEN); a1-main + a2-alternates failed on drift; await Cíl 2 follow-up run |

## §7. Open governance questions for MI-M-T

| # | Question | Owner |
|---|----------|-------|
| Q-MIMT-1 | Excel framework freeze date — kdy stop schema bumps a začít MI-M-T live workbook integration? | SUPIN architects + MI-M-T tech-owner |
| Q-MIMT-2 | MI-M-T live workbook readiness pro Bouračka migration | MI-M-T project |
| Q-MIMT-3 | Coverage rule Phase 2/3 trigger — same pro Bouračka i pro budoucí SUT v MI-M-T? | governance |
| Q-MIMT-4 | Component module hosting — Bouračka tools/*.py → MI-M-T governance lib? | MI-M-T |
| Q-MIMT-5 | Email-deliverability rules — corporate-wide standard nebo jen per-SUT? | governance |

## §8. Status

| Item | Hodnota |
|------|---------|
| Synchro doc | `SYNCHRO-MACBOOK-CP-SUPIN-05-2026-05-07-EOD.md` |
| Datum | 2026-05-07 EOD |
| Z | ThinkPad Opus session (Pete) |
| Pro | MacBook session (analytical MI-M-T) |
| Replaces | `SYNCHRO-MACBOOK-CP-SUPIN-04-2026-05-07-EOD.md` |
| Velikost změn | 6 nových strategic docs + 2 nových recon docs + 2 nové tools + 1 new fixture set + email-pivot |
| Status | připraveno k MacBook synchronizaci |
