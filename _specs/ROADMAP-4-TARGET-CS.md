# Bouračka — 4-target gradual deployment roadmap — v0.1 CS

> **Trigger.** CP-SUPIN-04 STEP 29 (2026-05-06) — strategic alignment session.
> **Audience.** SUPIN/ČKP architekti, governance, MI-M-T projekt.
> **Cíl.** Definovat fázovaný plán dodání testovací suite pro 4 cílová
> prostředí Bouračky, jejich integrační požadavky a sekvenci přechodu
> z fast-Excel-frameworku do live MI-M-T.

---

## §1. Strategický kontext

Bouračka je **kalibrační případ** pro MI-M-T (Methodology + Implementation +
Modeling + Testing). Je to první a nejjednodušší cíl SUPIN ekosystému;
slouží jako:

1. **Zdroj nástrojů** — každá utility/skript/komponenta vyvinutá pro
   Bouračka testing → kandidát na modularizaci do MI-M-T
2. **Validace metodologie** — Excel-based framework je fast-prototyping
   prostředí; co se ukáže jako stabilní → migruje se do MI-M-T
3. **Reverse analytical input** — recon-driven test analysis (bottom-up
   z živých SUT) ukazuje paterny použitelné napříč SUPIN

Současný stav (CP-SUPIN-04, 2026-05-06):
- Excel framework v0.4.1 stabilní
- DEMO Bouračka (PROD site, public) plně mapovaná + happy-path Playwright suite
- Bug naming convention + branch tagging zavedeno
- 6 empirických gotchas zachycených pro followery

## §2. Čtyři cílová prostředí

| # | Cíl | URL | Síťový gate | Integrace | Stage |
|---|-----|-----|-------------|-----------|-------|
| 1 | **DEMO veřejný** | `demo.bouracka.cz` | žádný (public) | mockované (DEMO-internal) | ✅ shipped |
| 2 | **DEMO test** | `tst.demo.bouracka.cz` | VPN ČKP / firewall | mockované (stejné jako #1) | 🔄 cloning v této iteraci |
| 3 | **PROD test** | `tst.bouracka.cz` | VPN ČKP / firewall | reálné test sandboxy: N08-test, RUIAN, AISPOV-test, zenID-test | ⏳ blokováno (čeká N08 sandbox) |
| 4 | **PROD prelive** | `bouracka.cz` | žádný (public) | reálné PROD integrace | ⏳ jen healthcheck/smoke |

### §2.1 Per-target charakteristika

#### Cíl 1 — DEMO veřejný (PROD-deployed DEMO instance)
- **Účel pro testy:** kalibrace, UX validace, copy regression, codelist drift detection
- **Test-data:** syntetické (libovolné OP, ŘP, SPZ, telefony — DEMO bypassy)
- **Risk profile:** žádný — public DEMO nevolá reálné integrace
- **Frekvence:** každý PR check + nightly regression
- **Suite:** `bouracka-suite-DEMO-v0.3.0.zip` (existuje)

#### Cíl 2 — DEMO test (firewall-gated mirror)
- **Účel pro testy:** preprod validace před deployem do public DEMO
- **Test-data:** stejná jako Cíl 1 (stejný SUT bundle)
- **Risk profile:** žádný (mockované integrace)
- **Frekvence:** před každým DEMO release; smoke + delta vs Cíl 1
- **Suite:** klon Cíl-1 suite s `BOURACKA_BASE=https://tst.demo.bouracka.cz`

#### Cíl 3 — PROD test (firewall-gated, reálné sandboxy)
- **Účel pro testy:** integrační regression, end-to-end real-stack
- **Test-data:** ČKP-přidělené testovací identity (NE reálné občanské)
- **Integrace vyžadují:**
  - **N08-test SMS gateway** — čeká na ČKP IT (OQ-CP-27)
  - **RUIAN-test** — pravděpodobně shodné s `ags.cuzk.cz` (volné public service)
  - **AISPOV-test** — sandbox CRR/CRV/ROB, čeká na ČKP IT
  - **zenID-test** — test-keys, čeká na ČKP IT
- **Risk profile:** nízký — testovací sandboxy
- **Frekvence:** denně + před každým PROD release
- **Suite:** `bouracka-suite-PROD-v0.3.0.zip` (scaffolding existuje, gated tests waiting na sandboxy)

#### Cíl 4 — PROD prelive / healthcheck
- **Účel pro testy:** post-deploy verifikace + ongoing monitoring
- **Test-data:** žádné write operace (read-only smoke)
- **Risk profile:** **VYSOKÝ** — running proti živé production
- **Frekvence:** každých 5 minut (uptime probe), full smoke per release
- **Limity:**
  - **Jen healthcheck operace** — rozcestník visible, /api/reports POST 200, codelist API alive
  - **Nikdy** plný E2E flow (žádné pokladní SMS, žádný registr lookup)
  - **Dedikované monitoring infra** (separátní od test infra)
- **Suite:** TBD — `bouracka-suite-prelive-v0.X.0.zip` ve fázi 4

### §2.2 Δ matice DEMO vs PROD platí pro celý stack

Detail viz `recon/DELTA-DEMO-vs-PROD-v0.1.md` (26 row Δ matice).

Kritické rozdíly Cíl 1+2 (DEMO) vs Cíl 3+4 (PROD):
- N08 SMS Gateway (mockovaný vs reálný)
- zenID OCR (instruktážní video vs reálný OCR)
- AISPOV registry (sandbox vs reálné CRR/CRV/ROB)
- Email dispatch (žádný vs reálný)
- DEMO branding banner (přítomen vs absent)

## §3. Sekvence dodávek

### §3.1 Aktuální iterace (CP-SUPIN-04, květen 2026)

```
   ╔════════════════════════════════════════════════════════════════════╗
   ║  ITERACE CP-SUPIN-04 — calibration + DEMO twins                    ║
   ╠════════════════════════════════════════════════════════════════════╣
   ║  Cíl 1 (demo.bouracka.cz)                                          ║
   ║    ✅ Test analysis (bottom-up reverse)                            ║
   ║    ✅ Test design (TT 28 + TC 49 + Δ matice 26)                    ║
   ║    ✅ Test suite (Playwright bring-up + alternates + full E2E)     ║
   ║    ✅ Excel master v0.4.1 + branch tagging                         ║
   ║    🔄 Cypress + TestCafe parity (smoke first, full suite later)    ║
   ║                                                                     ║
   ║  Cíl 2 (tst.demo.bouracka.cz)                                      ║
   ║    🔄 Clone Cíl-1 suite s BOURACKA_BASE override                   ║
   ║    ⏳ Cross-env delta detection (auto-flag rendering rozdíly)      ║
   ║                                                                     ║
   ║  Cíle 3+4: scaffolding only — čeká N08/AISPOV/zenID sandboxy       ║
   ╚════════════════════════════════════════════════════════════════════╝
```

### §3.2 Další iterace (CP-SUPIN-05, červen 2026)

```
   ╔════════════════════════════════════════════════════════════════════╗
   ║  ITERACE CP-SUPIN-05 — Multi-framework + tst.bouracka.cz unblock   ║
   ╠════════════════════════════════════════════════════════════════════╣
   ║  Cíl 3 (tst.bouracka.cz)                                           ║
   ║    Po dodání: N08-test + RUIAN-test + AISPOV-test + zenID-test     ║
   ║    Adaptér Mockoon → reálné sandboxy                               ║
   ║    Suite "bouracka-suite-PROD" → run-able                          ║
   ║                                                                     ║
   ║  Multi-framework decision                                          ║
   ║    Run all 3 frameworks proti Cíl 1 + Cíl 2 + Cíl 3                ║
   ║    Aggregate + compare via tools/test_console.py                   ║
   ║    Vybrat 1 vítězný framework pro long-term                        ║
   ║                                                                     ║
   ║  Excel framework → MI-M-T migration prep                           ║
   ║    Stabilizovat Excel schema (žádné další breaking changes)        ║
   ║    Document MI-M-T import contract                                 ║
   ╚════════════════════════════════════════════════════════════════════╝
```

### §3.3 Bolder strokes (CP-SUPIN-06+, Q3 2026)

```
   ╔════════════════════════════════════════════════════════════════════╗
   ║  ITERACE CP-SUPIN-06+ — Production prelive + MI-M-T integration    ║
   ╠════════════════════════════════════════════════════════════════════╣
   ║  Cíl 4 (bouracka.cz prelive)                                       ║
   ║    Healthcheck-only suite (smoke / probe / canary)                 ║
   ║    Dedikované monitoring infrastructure (Datadog / Grafana)        ║
   ║    Page-level uptime probes každých 5 min                          ║
   ║                                                                     ║
   ║  Bouracka → MI-M-T module migration                                ║
   ║    Recon tools (heic-to-jpg, render-uml, build_mindmaps) →         ║
   ║      MI-M-T modules                                                ║
   ║    Excel framework → MI-M-T live workbook bridge                   ║
   ║    Test_console.py → MI-M-T runner backend                         ║
   ║                                                                     ║
   ║  Další SUPIN systémy                                               ║
   ║    Aplikovat naučenou metodologii na další ČKP aplikace            ║
   ║    (jiné než Bouračka — TBD per SUPIN backlog)                     ║
   ╚════════════════════════════════════════════════════════════════════╝
```

## §4. Branch development model

### §4.1 Opus governance session (this one)

- **Role:** maintainer of methodology + Excel master + cross-branch consistency
- **Outputs:** schema migrations, naming conventions, lessons learned, master analytical doc
- **Frekvence:** po každé větší architektonické změně
- **Sustains:** governance + řešení neobvyklých blockerů

### §4.2 Per-branch Sonnet sessions (future)

Každý ze 4 cílů dostane své vlastní Sonnet sessions pro intensive
development. Handoff template viz `_specs/BRANCH-HANDOFF-TEMPLATE-CS.md`.

| Branch | Sonnet session ID | Hlavní úkol |
|--------|-------------------|--------------|
| `demo-public` | (TBA) | Doplnit alternate flows, validation negatives, perf tests |
| `demo-tst` | (TBA) | Clone + parametrizace + cross-env delta detection |
| `prod-tst` | (TBA, blokováno) | Real-integrace adaptéry; po dodání sandboxů od ČKP |
| `prelive` | (TBA, future) | Healthcheck design; dedikovaná monitoring stack |

Sonnet sessions vrací **pull-back deltas** do Opus session pro
schema/methodology updates.

## §5. MI-M-T migration plan (long-term)

### §5.1 Co migruje

| Komponenta | Z (Bouračka) | Do (MI-M-T) |
|------------|--------------|-------------|
| Test plan | Excel `BOURACKA-TESTPLAN-v0.4.x.xlsx` | MI-M-T live workbook |
| Bug tracking | Excel `08_Bugs` sheet | MI-M-T issue module |
| Test runs | Excel `07_TestRunResults` + JSON dumps | MI-M-T run database |
| Codelists | YAML `fixtures/codelists*.yaml` | MI-M-T reference data |
| Tools | Python `tools/*.py` | MI-M-T module wrappers |
| Recon | Markdown + UML | MI-M-T documentation module |

### §5.2 Co NE migruje

- Empirické install-time gotchas (Windows-specific, MI-M-T agnostic)
- Per-tester runbook (každý projekt si dělá vlastní)
- DEMO-vs-PROD Δ matrix (Bouračka-specific)

### §5.3 Časový horizont

- **Q3 2026:** Excel framework freeze; document MI-M-T import contract
- **Q4 2026:** First MI-M-T module ports (codelists, tools)
- **Q1 2027:** Live workbook bridge; Bouračka v0.5.x runs against MI-M-T
- **Q2 2027:** Full migration; Excel framework becomes legacy reference

## §6. Open governance questions

| # | Otázka | Odpovědný | Stav |
|---|--------|-----------|------|
| Q1 | Kdy switchne governance z Excel na live MI-M-T? | SUPIN architekti | open |
| Q2 | Kdo je MI-M-T tech-owner pro Bouračka import? | SUPIN | TBA |
| Q3 | N08-test sandbox kdy? | ČKP IT (OQ-CP-27) | pending |
| Q4 | Tester laptop pool — single ThinkPad nebo více? | SUPIN OPS | TBD |
| Q5 | MacBook (analytical MI-M-T session) syncs how often? | Pete | po každé Opus iteraci |
| Q6 | Dedicated Sonnet sessions — kdy spustit 1st? | this Opus session | po Cíl-1 stabilizaci ✅ |

## §7. Status

| Item | Hodnota |
|------|---------|
| Roadmap | `_specs/ROADMAP-4-TARGET-CS.md` |
| Verze | v0.1 |
| Datum | 2026-05-06 |
| Audience | SUPIN governance + MI-M-T project + Pete |
| Status | strategic locked — execution v dalších iteracích |
| Companion | `_specs/BRANCH-HANDOFF-TEMPLATE-CS.md` |
