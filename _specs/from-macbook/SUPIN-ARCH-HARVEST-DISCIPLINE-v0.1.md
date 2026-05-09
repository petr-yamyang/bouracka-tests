# SUPIN Ecosystem — Architectural Harvest Discipline — v0.1
## The second analytical track: harvest, connect, compare, validate; build coherent ArchiMate / BPMN / UML / ERD model layer

**Version:** v0.1.0
**Trigger:** operator clarification 2026-05-06: *"keep all these inputs with pinch of salt — they are not confirmed as up-to-date exact informations because SUPIN ecosystem is well developed but not well documented in consistent and coherent analytical way. This is reason why most important part of SUPIN engagement mission in long term is construction consistent ArchiMate / BPMN / UML model documentation with connections to the lower level of the system and data. Important to harvest informations, connect them, compare, test consistency and validity as a second track of test analytical effort."*  Operator also delivered the Bouračka–IS ČKP architectural diagram (PNG; hand-drawn / Visio-style) — first piece of system-of-systems context for the harvest. This doc establishes the discipline, annotates the diagram, and feeds the ThinkPad CP-SUPIN-03 v0.2 deliverable.
**Audience:** ThinkPad Opus task-force CP-SUPIN-03 (consume §11 paste-ready addendum); MacBook Opus next vocabulary refresh (absorb the model-harvest vocabulary into catalogue v0.1.3); operator (Petr — read §1, §3, §4 to ground the dual-track frame for SUPIN stakeholders).
**Posture:** the testing track produces **executable evidence** about runtime behaviour. The architectural-harvest track produces **modelled understanding** about what the system *is*. Each track surfaces gaps the other can't see. They co-evolve: the model proposes test targets; the tests validate (or contradict) the model. **Neither leads; both are first-class.** This is the discipline VUP §4.3.2c hinted at with "Capture a Common Vocabulary" + "Determine Logical Test Structure" — generalised here to its full form.

---

## §0. Sources processed in this analysis pass

| # | Source | Form | Provenance confidence | Last-validated |
|:--:|---|---|:---:|---|
| S1 | Bouračka–IS ČKP architectural diagram | hand-drawn / Visio-style PNG | LOW (no version, no date, no author signature, no XMI export) | unknown |
| S2 | N8 OpenAPI 3.1 + Postman + ReadyAPI | tool-exported (per `SUPIN-N8-CONTRACT-ANALYSIS-v0.1.md`) | MEDIUM-HIGH (tool-managed; OpenAPI declared `version: 1.0.0`; calendar-versioned URL `/N8/2025/01/`) | 2026-05-06 (operator delivery) |
| S3 | Analytical document pages 1..42 (per LESSONS L-PROC-2 + L-ARCH-1) | iPhone HEIC photos | MEDIUM (133-page document; only first 42 pages photographed; document version unclear) | 2026-05-05 (during ThinkPad CP-SUPIN-02) |
| S4 | LESSONS L-DOM-1..5 (Czech / SUPIN / ČKP-specific terms) | derivable from analytical doc + tester observation | MEDIUM | 2026-05-05 |
| S5 | Catalogue v0.1.2 §2 + §3 + §4 + §6 vocabulary | curated (Vaněk + Vaněk-Kukol + ISTQB CZ + DVA-2016) | HIGH | 2026-05-03 |
| S6 | Public bouracka.cz DOM + structure | live recon (per LESSONS L-PROC-2) | MEDIUM (public; production-shape = no auth surface; ≠ tst.* / DEMO content) | 2026-05-05 |

> **Operator caveat (binding for this entire doc):** every model element constructed from S1–S6 carries an explicit `confidence` tag (`HIGH / MEDIUM / LOW`) and a `last_validated_at` date. **No element is treated as ground truth without re-validation.** When an element's `last_validated_at` is older than its `validity_decay_days` threshold, it goes into the harvest backlog for re-confirmation.

---

## §1. Strategic framing — two tracks of analytical effort

### §1.1 The two tracks

```
┌───────────────────────────── ANALYTICAL EFFORT ─────────────────────────────┐
│                                                                              │
│   TRACK 1 — TESTING                  TRACK 2 — ARCHITECTURAL HARVEST          │
│   (executable evidence)              (modelled understanding)                 │
│                                                                              │
│   Output:                            Output:                                  │
│   • TestPlan workbook (live          • ArchiMate (Business / Application /   │
│     execution contract)                Technology layers)                    │
│   • TC SPECs                         • BPMN process models                   │
│   • Mockoon / Newman / k6            • UML class / sequence / state /        │
│     fixtures                           activity diagrams                     │
│   • Playwright / Cypress code        • ERD / data dictionary                 │
│   • Run-result reports               • Integration topology map              │
│                                      • Glossary / Common vocabulary         │
│                                                                              │
│   Cadence:                           Cadence:                                 │
│   per iteration; runs nightly        per iteration; refreshed per harvest    │
│                                                                              │
│   Validates by:                      Validates by:                            │
│   actual SUT behaviour               cross-source consistency checks +       │
│                                      runtime probes vs declared model       │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
                            │                │
                            ▼                ▼
                    ┌───────── FEEDBACK LOOP ─────────┐
                    │ tests find model drift          │
                    │ models propose new test targets │
                    └─────────────────────────────────┘
```

### §1.2 Why two tracks (not one)

| One-track failure mode | What two tracks prevent |
|---|---|
| Tests pass; no one knows whether the model behind them is current | Model has its own validity SLO; stale model triggers harvest cycle |
| New analyst arrives; no map of the territory; spends 3 weeks reverse-engineering | Model is the map; analyst onboards in 3 days |
| SUPIN architecture changes silently (Service B replaces Service A); tests still green against old name; report wrong | Cross-source consistency check fires; harvest cycle detects |
| Stakeholder asks "what does Bouračka touch?"; tester opens Excel; can't answer cleanly | Architecture diagram answers in 30 seconds |
| Vendor migration (e.g. zenID v2 lands); no model means impact analysis takes weeks | Model traces the dependency; impact analysis takes hours |

### §1.3 Why this is appropriate for SUPIN specifically (per operator note)

- SUPIN ecosystem is **well-developed but inconsistently documented** — the modelling capability already exists in scattered sources (Visio diagrams, Word docs, oral knowledge, 2009-vintage WSDL files, 2025-vintage OpenAPIs).
- The harvest track is a **constructive synthesis**, not a from-scratch design — its value is in connecting + reconciling existing material.
- This positions the engagement long-term: as the model matures, the engagement becomes more strategic (architecture board input; impact-analysis service; vendor-migration support); not just QA.

---

## §2. The Bouračka–IS ČKP diagram (S1) — annotated

### §2.1 What the diagram shows (faithful re-rendering as text)

```
                        ┌─────────────────────────────────────────────┐
[6] PDF ──────────► Email │                                              │
[N8] SMS ──────────► SMS │                  Klient                      │
                          │                                              │
                          └──────────────────┬──┬────────────────────────┘
                                             │  │
                                             ▼  ▼
                                       Web aplikace
                                          │   │
                                          ▼   ▼
                                     [1] Záznam DN
                                          │
                          ┌───────────────┴────────────────┐
                          │                                 │
                          │       Aplikace Bouračka         │◄─[Azure]
                          │                                 │
                          └─────┬──────────────────┬────────┘
                                │                  │
                            [7] XML            [2] Dotaz: ČOP+Jméno+Příjmení+DN
                            Záznam DN          [4] Dotaz: SPZ
                                │                  │
                                ▼                  ▼
                       (D8WS)──────────► WS AISPOV
                                                   │
                          ┌────────────────────────┴───────────────────────────┐
                          │                                                     │
                          │   ┌─SEDN──┬─P3WS──┬─AISPOV(Bouračka)──┬─B3WS──┐    │
                          │   │       │       │   ▲    ▲     ▲    │       │    │
                          │   │       │  [5b]─┘   │    │     │    └──[5a]─┘    │
                          │   │       │   Dotaz:  │    │     │   Dotaz: SPZ    │
                          │   │       │   SPZ     │    │     │                 │
                          │   │       │           │    │     │                 │
                          │   │       │       [3a]│ [3c]│ [3b]│                 │
                          │   │       │       Dotaz: Dotaz: Dotaz:              │
                          │   │       │       ČOP+    KIFO  ČOP+                │
                          │   │       │       …             …                  │
                          │   │       │           │    │     │                 │
                          │   │       │           ▼    ▼     ▼                 │
                          │   │       │            AIS ČKP                     │
                          │   │       │              ▲                         │
                          │   │       │              │ [3d]                    │
                          │   │       │              │ Dotaz: AIFO             │
                          │   │       │              │                         │
                          │   │       │     ┌────────┴────────┐                │
                          │   │       │     │                 │                │
                          │   │       │   CRŘ (ISSS)         ROB              │
                          │   │       │                                        │
                          │   │       │           IS ČKP                       │
                          │   │       │                                        │
                          └───┴───────┴────────────────────────────────────────┘
                              ▲
                              │
                              │ (D8WS)
                              │
                          [8] Záznam DN + Přílohy
                              │
                          Pojistitel PČR
```

### §2.2 Element inventory + confidence + open questions

| Element | Type | Confidence | Source | OQ raised |
|---|---|:---:|---|---|
| Klient | actor | HIGH | S1 + matches "Účastník" per L-DOM-1 | OQ-ARCH-01 — is "Klient" the diagram-author's casual usage, or is it an actual deviation from "Účastník" in the live system? |
| Aplikace Bouračka (Web aplikace + Azure) | application component | MEDIUM | S1 + S6 (public bouracka.cz live) | OQ-ARCH-02 — confirm Azure hosting; the cloud icon may be aspirational vs current |
| N8 (SMS gateway) | external service | HIGH | S1 + S2 (full contract in hand) | — |
| WS AISPOV | integration interface | MEDIUM-HIGH | S1 (label appears) + S2 (SUPIN platform pattern predicts shape) | OQ-ARCH-03 — confirm AISPOV exposes the same `/InterfaceCode/YYYY/MM/Env/PartnerCode/...` pattern as N8 |
| AISPOV (Bouračka) | application component (inside IS ČKP) | MEDIUM | S1 | OQ-ARCH-04 — clarify: is AISPOV a service (singular) used by Bouračka (the partner-app sense), or is "AISPOV (Bouračka)" the Bouračka-instance of AISPOV? Naming ambiguous |
| SEDN | application component | LOW | S1 (only label visible) | OQ-ARCH-05 — what is SEDN? expand acronym; what does it do; what protocol does it expose |
| P3WS, B3WS, D8WS | web service interfaces | LOW | S1 (only labels visible) | OQ-ARCH-06 — naming pattern (P3WS / B3WS / D8WS) — what's the "P/B/D" prefix? what's the "WS" mean? versioning scheme? |
| AIS ČKP | application component (different colour — orange — suggests external/distinct) | MEDIUM | S1 | OQ-ARCH-07 — AIS ČKP is the ČKP master application; confirm scope (claims handling? all ČKP business processes?); ownership (who maintains it) |
| CRŘ (ISSS) | external system | HIGH | S1 + L-ARCH-2 references registers | OQ-ARCH-08 — ISSS expansion = Information System / Information State System? confirm |
| ROB | external system | HIGH | S1 + LESSONS / public knowledge of Czech eGov | — |
| Pojistitel PČR | external actor | MEDIUM | S1 (block at lower-left; flow `Záznam DN + Přílohy via D8WS`) | OQ-ARCH-09 — "Pojistitel PČR" reads as "insurer-Police"; ambiguous — likely two actors merged in the diagram (Pojistitel = the insurer; PČR = Police of the Czech Republic). Need clarification of which is which destination |
| [1] Záznam DN | data flow / artefact | HIGH | S1 + analytical doc | — |
| [2] Dotaz: ČOP + Jméno + Příjmení + DN | data flow | HIGH | S1 | OQ-ARCH-10 — DN here = Datum Narození (date of birth); confirm |
| [3a] Dotaz: ČOP + … (to AIS ČKP) | data flow | MEDIUM | S1 (path traverses AISPOV) | — |
| [3b] Dotaz: ČOP + … (AIS ČKP → ROB) | data flow | MEDIUM | S1 (returns to ROB from AIS ČKP) | OQ-ARCH-11 — what triggers AIS ČKP to query ROB? is this synchronous within AISPOV's scope, or async ČKP-internal? |
| [3c] Dotaz: KIFO | data flow | LOW | S1 (label only) | OQ-ARCH-12 — KIFO expansion? Klient Identifikační Formát Osoby? Klient ID Formát Operace? |
| [3d] Dotaz: AIFO | data flow | MEDIUM | S1 + Czech eGov public knowledge (AIFO = Agendový identifikátor fyzické osoby — agenda-bound personal identifier; **the standard Czech eGov pseudonym**) | OQ-ARCH-13 — confirm AIFO usage; under which agenda code does Bouračka operate? |
| [4] Dotaz: SPZ | data flow | HIGH | S1 + L-DOM-2 | — |
| [5a/5b] Dotaz: SPZ | data flow | LOW | S1 (returns to two services B3WS + P3WS) | OQ-ARCH-14 — why does SPZ query go to BOTH B3WS and P3WS? what's the difference? probably (centralni-registr-vozidel vs centralni-registr-pojisteni) but confirm |
| [6] PDF Záznam DN | output artefact | HIGH | S1 | — |
| [7] XML Záznam DN | output artefact (via D8WS) | MEDIUM | S1 | OQ-ARCH-15 — D8WS expansion + interface contract location |
| [8] Záznam DN + Přílohy | output artefact (to Pojistitel PČR via SEDN) | MEDIUM | S1 | OQ-ARCH-16 — Přílohy = attachments; what kinds (photos? signed PDFs?); what's the size limit |

### §2.3 What the diagram *probably* gets wrong (testable inconsistencies)

These are hypotheses to **test against runtime + against other sources** — not definitive findings.

| Suspicion | Why we suspect | How to test |
|---|---|---|
| The diagram conflates AISPOV (a SUPIN-platform service) with AIS ČKP (a ČKP application) | "AISPOV (Bouračka)" naming is inside IS ČKP block but AISPOV is a SUPIN-hosted service per L-ARCH-2. The label may be the wrong-side-of-the-fence or a Bouračka-instance-namespace within AISPOV | runtime probe: hit an `AISPOV/.../.../.../Ping` endpoint and inspect TLS cert subject; if SUPIN-issued, confirms platform-side hosting |
| The diagram is missing the certificate / mTLS layer | No certificate is shown anywhere. We know from N8 contract (§4 of `SUPIN-N8-CONTRACT-ANALYSIS-v0.1.md`) that mTLS is the auth pattern. Likely the diagram abstracts auth | none — accept as architectural-summary-level abstraction |
| The diagram is missing async patterns | N8 has 202-Accepted async + poll-by-id pattern; analogous patterns probably exist for register lookups but the diagram shows single-arrow synchronous flows | runtime probe per integration; document async/sync per call |
| The diagram is missing failure flows | Only happy-path arrows shown; no ERROR-state branches; no retry loops; no circuit-breaker feedback | derive from state-machine `accidentReportStatus` (per L-ARCH-1) — overlay ERROR sub-flows as a separate diagram |
| The diagram may be out-of-date for newer integrations | zenID + reCAPTCHA + Mailpit-equivalent SMTP + Maps + RUIAN — none appear on the diagram. Either they're missing, or post-diagram additions, or diagrammed elsewhere | catalogue per analytical doc + cross-check |
| Label inconsistency: "Klient" vs "Účastník" | Diagram says Klient; legal/regulatory term is Účastník (per L-DOM-1) | flag as documentation drift; confirm canonical usage with SUPIN |
| Naming pattern P3WS / B3WS / D8WS is ambiguous | letters + number + WS suffix — likely a SUPIN house style (e.g. Pojištění-3-Web-Service / Behavioral-3-Web-Service / Data-8-Web-Service) but completely unconfirmed | confirm with SUPIN; absorb pattern into catalogue if real |

### §2.4 What the diagram does **confirm** (high-confidence findings)

| Finding | Implication |
|---|---|
| AISPOV is the orchestrator for register lookups | Bouračka does NOT directly query ROB / CRŘ — it goes through AISPOV. This affects mock strategy (we mock AISPOV, not the registers); test posture; integration-contract test scope |
| Multiple register lookups per session | At least 4 distinct query types ([2], [4], [3a-d], [5a/b]) — each is a candidate TestTarget under R-DERIVE-1 (source = this diagram + analytical doc) |
| Output paths are diverse | SMS (N8) + Email (SMTP) + PDF (Bouračka-internal generation) + XML (D8WS to insurer/police) + SEDN (attachments to Pojistitel PČR). Each has a distinct test posture |
| Bouračka is the Azure-hosted partner-app facing the citizen | Cloud icon next to "Aplikace Bouračka". This matches the `UzivatelKod=BourackaAzure` value seen in N8 X-SUPIN-TransactionInfo header (per `SUPIN-N8-CONTRACT-ANALYSIS-v0.1.md` §4.1 example) — internal consistency between two sources is HIGH-confidence |
| The IS ČKP boundary contains: SEDN, P3WS, AISPOV, B3WS, AIS ČKP | This is the system-of-systems Bouračka sees on the ČKP side. AIFO query [3d] reaches OUTSIDE this boundary to CRŘ. ROB receives query via AIS ČKP |
| `Záznam DN + Přílohy` flows via SEDN | SEDN is the attachment / large-payload path. Distinct from D8WS (XML-only). Test posture differs (file uploads vs API calls) |

---

## §3. The harvest discipline — process

### §3.1 The four phases (binding cycle)

```
   ┌─────────────────────────────────────────────────────────────────┐
   │                                                                  │
   │                    HARVEST CYCLE (per iteration)                 │
   │                                                                  │
   │   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
   │   │ HARVEST  │───►│  CONNECT │───►│  COMPARE │───►│ VALIDATE │  │
   │   │          │    │          │    │          │    │          │  │
   │   │ collect  │    │ link     │    │ check    │    │ runtime  │  │
   │   │ raw      │    │ elements │    │ against  │    │ probe;   │  │
   │   │ source   │    │ across   │    │ peer     │    │ compare  │  │
   │   │ material │    │ sources  │    │ sources; │    │ vs       │  │
   │   │          │    │          │    │ surface  │    │ declared │  │
   │   │          │    │          │    │ deltas   │    │ model    │  │
   │   └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
   │                                                          │       │
   │                                                          ▼       │
   │                                                    ┌──────────┐  │
   │                                                    │  REFINE  │  │
   │                                                    │  MODEL   │  │
   │                                                    │  + log   │  │
   │                                                    │  drift   │  │
   │                                                    └──────────┘  │
   │                                                          │       │
   └──────────────────────────────────────────────────────────┼───────┘
                                                              │
                                                       (next iteration)
```

### §3.2 Harvest sources catalogue (where material comes from)

| Kind | Examples | Confidence default |
|---|---|:---:|
| Tool-managed exports | OpenAPI 3.x YAML, WSDL, GraphQL schema, BPMN XML, ArchiMate XMI | HIGH |
| Tool-rendered docs | Postman collection, ReadyAPI/SoapUI project, Swagger UI render | MEDIUM-HIGH |
| Hand-drawn diagrams | Visio diagrams, hand-drawn sketches, whiteboard photos | LOW (no version, no XMI) |
| Source code | controller routes, model definitions, ORM entities, integration adapter code | HIGH (when readable; live code is closer to truth than any doc) |
| Database introspection | live `\d+` of tables, foreign keys, indexes; data samples | HIGH |
| Runtime probes | request/response captures, log samples, distributed-trace data | HIGH (snapshot-in-time) |
| Documentation prose | Word docs, Confluence pages, README files, analytical PDFs | MEDIUM |
| Oral knowledge / interviews | architect notes, stakeholder briefs, support tickets | MEDIUM (decay-fast) |
| Public observation | DOM of public-facing app, OSINT, press releases | MEDIUM |
| Test artefacts | TC SPECs, test logs, bug reports — what other people *thought* the system did | MEDIUM (evidence-of-belief, not evidence-of-fact) |

### §3.3 R-rules — binding for the harvest track

> **R-HARVEST-1 (binding from v0.1):** every model element carries `provenance` (≥ 1 source from §3.2 catalogue), `confidence` (HIGH / MEDIUM / LOW), `last_validated_at` (date), and `validity_decay_days` (default 90). Elements without these tags MUST NOT enter the canonical model.

> **R-VALIDITY-1 (binding from v0.1):** when an element's `last_validated_at + validity_decay_days < today`, the element is **stale** and enters the harvest backlog for re-validation. Stale elements remain in the model (greyed out in renders) but flag any tests/derived artefacts that depend on them.

> **R-CONSISTENCY-1 (binding from v0.1):** when two sources disagree about an element, the disagreement is **logged**, not silently resolved. The model carries the higher-confidence interpretation as canonical + the lower as alternative. A consistency-test TC fires runtime probes to break the tie.

> **R-MODEL-IS-CODE (binding from v0.1):** all model artefacts ship in machine-checkable formats — ArchiMate as XMI, BPMN as XML, UML as XMI/PlantUML, ERD as DBML or PlantUML, glossary as YAML/JSON. Free-text-only docs may accompany but never substitute. `tools/validate-models.py` runs in CI and validates: schema-compliance + R-HARVEST-1 tag presence + cross-reference integrity.

### §3.4 The model as a living document — versioned + tagged

```
arch-models/
├── archimate/
│   ├── 01-business-layer.archimate     (XMI; ArchiMate Open Group model exchange format)
│   ├── 02-application-layer.archimate
│   └── 03-technology-layer.archimate
├── bpmn/
│   ├── BP-CP-001-podani-zaznamu-DN.bpmn
│   └── BP-CP-002-OTP-podpis.bpmn
├── uml/
│   ├── class/
│   │   └── CLS-CP-001-zaznam-DN.puml
│   ├── sequence/
│   │   ├── SEQ-CP-001-podani-happy.puml
│   │   ├── SEQ-CP-002-OTP-roundtrip.puml
│   │   └── SEQ-CP-003-AISPOV-orchestration.puml
│   ├── activity/
│   │   └── ACT-CP-001-state-machine.puml
│   └── state/
│       └── ST-CP-001-accidentReportStatus.puml
├── erd/
│   └── ERD-CP-001-bouracka-data.dbml
├── topology/
│   └── TOPO-CP-001-supin-bouracka-ecosystem.archimate
├── glossary/
│   └── GLOSSARY-CP.yaml                 (also referenced by VOCABULARY-CATALOGUE)
└── provenance/
    ├── elements.yaml                    (every model element with provenance/confidence/last_validated)
    ├── consistency-checks.yaml          (R-CONSISTENCY-1 disagreement log)
    └── validity-probes.yaml             (R-VALIDITY-1 runtime probe definitions)
```

Live in the same repo as the testing track; cross-referenced via element IDs.

---

## §4. Validity testing strategy — the second-track equivalent of TC-CP-N8-CONTRACT

The **harvest track has its own test cases** — these don't test the SUT, they test the model's own truth.

### §4.1 Validity probe types

| Probe type | What it tests | Frequency | Tooling |
|---|---|---|---|
| Schema conformance | Is each model file valid against its tool's schema (XMI / BPMN / DBML)? | every commit | `tools/validate-models.py` + `xmllint`, `dbml-cli` |
| Cross-reference integrity | Do all element IDs referenced by other elements / by tests resolve? | every commit | `tools/validate-models.py` graph traversal |
| Provenance coverage | Does every element have ≥ 1 source + confidence + last_validated tag? (R-HARVEST-1) | every commit | `tools/validate-models.py` tag check |
| Validity decay scan | Are any elements past their `last_validated_at + validity_decay_days`? | nightly | `tools/scan-stale-models.py` → emits stale-element report |
| Source consistency | When element X appears in 2 sources, do the attributes match? (R-CONSISTENCY-1) | nightly | `tools/cross-source-diff.py` |
| Runtime probe — element existence | If model says service X has endpoint Y, does an HTTP probe confirm Y responds (not necessarily 200; just *something*)? | nightly | `tools/runtime-probes.py` (Newman-driven; auth-aware) |
| Runtime probe — shape conformance | Given declared schema for endpoint Y's response, does an actual response from a synthetic request conform? | nightly | `tools/runtime-probes.py` + JSON-schema validator |
| Behaviour probe — TC reflection | Given the TC catalogue's `test_target_ref → recon ref`, does the model contain the referenced source-artefact? | every workbook validate | extends `tools/validate-workbook.py` (per Opus review §6.6) |
| Drift detector — release vs model | When SUT releases a new version (per `06_TestRuns.framework_version`), are there any model elements that haven't been re-validated since? | per release | `tools/drift-detect.py` |

### §4.2 Validity probes file format (`provenance/validity-probes.yaml`)

```yaml
- probe_id: VP-N8-001
  element_ref: arch-models/archimate/02-application-layer.archimate#N8-Service
  kind: runtime_existence
  url: http://rest-wstst.supin.cz:8887/N8/2025/01/TST/BOUR/fake/-/Ping
  method: POST
  expected_status_class: [200, 202, 203]
  cadence: nightly
  on_failure: log_drift; flag_element_stale

- probe_id: VP-AISPOV-001
  element_ref: arch-models/archimate/02-application-layer.archimate#AISPOV-Service
  kind: runtime_existence
  url_template: http://<TBD>/AISPOV/{year}/{month}/TST/BOUR/{op}/fake/Ping
  cadence: nightly
  status: BLOCKED
  blocked_by: OQ-ARCH-03
  on_unblock: derive concrete URL from operator-confirmed pattern

- probe_id: VP-CONSISTENCY-001
  kind: source_consistency
  element_ref: arch-models/glossary/GLOSSARY-CP.yaml#klient
  sources:
    - source: S1 (diagram label "Klient")
    - source: L-DOM-1 (legal term "Účastník")
  consistency_rule: declared canonical = "Účastník"; "Klient" is documentation drift
  cadence: every_commit
  resolution: keep both as aliases in glossary; UI labels follow legal term
```

### §4.3 R-VALIDITY-1 in operation

```
Element X (e.g. AIS-ČKP component on diagram)
   provenance:        [S1 (diagram, LOW confidence)]
   confidence:        LOW
   last_validated_at: 2026-05-06
   validity_decay_days: 30   (because LOW-confidence elements decay faster)
   ↓
   2026-06-05: tools/scan-stale-models.py reports X as stale.
   ↓
   Harvest backlog adds: "re-validate AIS-ČKP component scope + ownership; trigger = stale".
   ↓
   Operator-side: ask SUPIN architect (interview) OR find newer doc.
   ↓
   Add new source S7 (interview notes, MEDIUM confidence).
   ↓
   Update element X: provenance += [S7]; confidence = MEDIUM; last_validated_at = 2026-06-08.
   ↓
   Element X re-enters fresh state.
```

---

## §5. Connection to existing work

### §5.1 Catalogue v0.1.2 (vocabulary)

- **§2d source-artefact derivation** — already covers the "TT derives from analytical artefact" rule. The harvest track *produces* analytical artefacts; the testing track *consumes* them. Same vocabulary; different verbs.
- **§4.3.2c VUP Test Discipline activities** — already includes "Capture a Common Vocabulary" and "Determine Logical Test Structure". This doc operationalises "Capture a Common Architecture" as the larger sibling. **Add to catalogue v0.1.3** §4.3.2c-bis: "Capture a Common Architecture / Process / Data Model" as VUP-Test-Discipline-aligned activities.
- **§5 DVA-2016 architecture vocabulary** — `Provider / Consumer`, `DTO/DSO/DDO`, orchestrated/choreographed, Cooperation pattern. The harvest track's primary linguistic toolkit. Already binding.

### §5.2 Methodology mapping AMENDMENT (already shipped)

- **CAST decomposition matrix (CO/KDO/KDY/KDE/JAK)** — applies to model elements too: every component answers WHO uses it / WHEN / WHERE / WHAT it does / HOW. Add to model-element schema.
- **Diligence (CAST 3rd dim)** — applies to model elements: a model element representing legal-compliance machinery has HIGH diligence; a casual UI label has LOW.
- **Plan ≠ Schedule ≠ Estimate** — applies to harvest cycle: the *harvest plan* is "we will document AISPOV next"; *schedule* is "by end of CP-SUPIN-04"; *estimate* is "1 ThinkPad session". All three coexist.

### §5.3 N8 contract analysis (already shipped) — what it teaches the harvest track

- The SUPIN platform integration pattern (per `SUPIN-N8-CONTRACT-ANALYSIS-v0.1.md` §2 + §15) is **the first piece of harvested architectural model**. The N8 contract analysis IS a harvest output — proving the discipline works.
- The platform pattern is now a `pattern` element in the model (`arch-models/patterns/PATTERN-CP-001-supin-platform-interface.archimate`). Future SUPIN interface analyses (AISPOV, future zenID-via-SUPIN, etc.) inherit from this pattern; deviations are flagged.

### §5.4 Opus review of ThinkPad delivery (already shipped) — what it teaches

- The `01b_Req_FURPS_Cartesian` sheet (per Opus review §6.5 G7) — every Requirement × FURPS+ cell carries `source_artefact_kind` + `source_artefact_ref` (per R-DERIVE-1). These same source-refs are model element refs in the harvest track. **Same identifier scheme; one source of truth across both tracks.**

### §5.5 SYNCHRO ThinkPad CP-SUPIN-03 (already shipped)

- The synchro file specifies the v0.2 deliverables (workbook + code + tests). **This doc adds a parallel deliverable**: the `arch-models/` directory and its contents. Same v0.2 release; two tracks ship together.

---

## §6. Specific findings from S1 (the diagram) applied to v0.2

### §6.1 New R1 model deliverables

For v0.2, ThinkPad authors:

| Deliverable | Source | Confidence at first authoring |
|---|---|:---:|
| `arch-models/archimate/02-application-layer.archimate` containing: Bouračka (Azure-hosted partner-app) + AISPOV + AIS ČKP + SEDN + P3WS + B3WS + D8WS + N8 + ROB + CRŘ; relationships per S1 + S2 | S1 (diagram) + S2 (N8 contract) | LOW-MEDIUM (per element; per S1 caveat) |
| `arch-models/uml/sequence/SEQ-CP-003-AISPOV-orchestration.puml` showing register-lookup orchestration: Bouračka → AISPOV → ROB / CRŘ / AIS ČKP → response chain | S1 + L-ARCH-2 | LOW |
| `arch-models/uml/sequence/SEQ-CP-004-N8-OTP-roundtrip.puml` showing OTP send + verify chain (per N8 contract analysis §6.2) | S2 | HIGH |
| `arch-models/uml/sequence/SEQ-CP-005-output-fanout.puml` showing the diverse output paths: SMS/Email/PDF/XML/SEDN | S1 | MEDIUM |
| `arch-models/uml/state/ST-CP-001-accidentReportStatus.puml` formalised from L-ARCH-1 + workbook `01c_StateMachine` sheet | L-ARCH-1 + workbook | HIGH |
| `arch-models/glossary/GLOSSARY-CP.yaml` first version — terms with confidence + provenance | S1 + S4 + L-DOM-1..5 | varies per term |
| `arch-models/provenance/elements.yaml` first version — every element above with R-HARVEST-1 tags | this doc | HIGH (provenance metadata is fresh) |
| `arch-models/provenance/consistency-checks.yaml` first version — pre-seeded with §2.3 suspicions as logged disagreements | this doc | HIGH |
| `arch-models/provenance/validity-probes.yaml` first version — VP-N8-001 + VP-AISPOV-001 + VP-CONSISTENCY-001 (per §4.2) | this doc | HIGH |
| `arch-models/patterns/PATTERN-CP-001-supin-platform-interface.archimate` extracted from N8 contract; reused for AISPOV inference | S2 + S5 | HIGH (pattern definition) / LOW (AISPOV inference instance) |

### §6.2 The architectural diagram itself becomes a tracked artefact

`arch-models/source/S1-bouracka-iskcp-diagram-2026-05-06.png` — committed to repo. The harvest track's first audit-trail entry. Future revisions of this same diagram (when SUPIN ships an updated one) get committed alongside; diff'd; consistency-check fires.

### §6.3 Open questions (OQ-ARCH-01..16) flow into the OQ ledger

The 16 OQs from §2.2 are **first-class deliverables** of the harvest track — they are the *known unknowns* that the next harvest cycle aims to close. Each gets a Sev/Urg/Pri tag per the priority matrix governance.

---

## §7. SUPIN engagement long-term arc — what this enables

Stages of the architectural-harvest track maturity (per `OPUS-CYCLE-v0.2.1-STAGES-ADDENDUM.md` topology — the same stage 0/1/2 frame applies):

| Stage | Scope | Output |
|---|---|---|
| **Stage 0 (now)** | ThinkPad authors v0.2 model from the diagram + N8 contract; LOW-MEDIUM confidence; many OQs | first 3 ArchiMate / UML / glossary files; the discipline operational |
| **Stage 1** | Operator + SUPIN architect interview cycle resolves ~70 % of OQs; AISPOV contract harvested; further integrations (zenID-via-SUPIN, SMTP, Maps) catalogued | full IS ČKP application-layer ArchiMate; major BPMN processes; consistent glossary |
| **Stage 2** | Validity probes wired into nightly CI; runtime drift detection live; SUPIN consumes the model as their own internal architectural reference (positions engagement as architecture-as-a-service alongside QA) | model-driven impact analysis; vendor-migration support; new-engagement-bootstrap accelerator |
| **Stage 3+** | The model becomes a **living standard** SUPIN/ČKP rely on; Bouračka tests are derived from the model not vice-versa; the engagement becomes a long-term architecture board contributor | the engagement transcends the QA-vendor frame; becomes a strategic capability |

This is the long-term value capture. The testing track ships immediate value (working tests against tst.bouracka.cz); the harvest track ships the value that compounds.

---

## §8. Open questions

| OQ# | Sev | Urg | Pri | Question | Resolve by |
|-----|:---:|:---:|:---:|----------|------------|
| OQ-ARCH-01..16 | varies | varies | varies | per §2.2 element-level questions | rolling per harvest iteration |
| OQ-ARCH-17 | A | A | A | Tool choice for ArchiMate authoring on the operator + ThinkPad side — Archi (free; XMI export), Sparx Enterprise Architect (heavyweight; the original VUP authoring tool), or text-based PlantUML-archimate? Recommendation: **Archi** (free; XMI; live model exchange) for new authoring; convert legacy SUPIN diagrams to Archi as harvest-step | CP-SUPIN-03 morning |
| OQ-ARCH-18 | A | B | A | BPMN tool choice — Camunda Modeler (free; XML export; widely-used) recommended | CP-SUPIN-03 |
| OQ-ARCH-19 | B | B | B | UML tool choice — PlantUML (text; diff-friendly; CI-renderable) for sequence/activity/state; class diagrams via PlantUML or DBML for ERD | CP-SUPIN-03 |
| OQ-ARCH-20 | B | A | A | The `arch-models/` directory — does it live in `bouracka-tests/` repo (same repo as testing track), or in a sibling `bouracka-arch/` repo, or in an upstream `supin-arch/` repo (cross-engagement)? Recommendation: same repo for v0.2; promote to `supin-arch/` when stage-1 maturity hits | CP-SUPIN-03 |
| OQ-ARCH-21 | C | B | C | Confidence taxonomy — HIGH / MEDIUM / LOW only, or 5-level (HIGH / MEDIUM-HIGH / MEDIUM / MEDIUM-LOW / LOW)? Currently 3-level for simplicity | post v0.2 |
| OQ-ARCH-22 | B | B | B | Validity decay days default — 90 across the board, or graduated (HIGH=180, MEDIUM=90, LOW=30)? Current proposal in §4.3 = graduated (LOW = 30) | CP-SUPIN-03 |
| OQ-ARCH-23 | A | A | A | Validity probes against real `/TST/` endpoints — do they require partner mTLS cert (VP-AISPOV-001 is BLOCKED on this; same as GAP-12 from synchro) or can they go through `/fake/`? Recommendation: probes against `/fake/` whenever it exists; against real `/TST/` only when cert provisioned | rolling per integration |
| OQ-ARCH-24 | C | C | C | When (which iteration) does the harvest track open its own LESSONS-LEARNED-ARCH-v0.1.md, separate from the testing-track LESSONS? Recommendation: at the second harvest cycle | post v0.2 |
| OQ-ARCH-25 | B | A | B | Do we ship the v0.2 archive bundle to SUPIN with the `arch-models/` directory included (analytical bundle) or separately? Recommendation: included — SUPIN should see this is part of the engagement value, not hidden as internal | CP-SUPIN-03 packaging step |

---

## §9. Status footer

| Item | Value |
|------|-------|
| Document | `SUPIN-ARCH-HARVEST-DISCIPLINE-v0.1.md` |
| Output position | `_config/SUPIN-ARCH-HARVEST-DISCIPLINE-v0.1.md` |
| Sources annotated | 6 (S1–S6), with confidence per source |
| Diagram elements catalogued | ~25, each with confidence + OQ |
| Architectural OQs raised | 25 (OQ-ARCH-01..25) |
| Suspicions logged | 7 testable inconsistencies (per §2.3) |
| New binding rules | 4 (R-HARVEST-1, R-VALIDITY-1, R-CONSISTENCY-1, R-MODEL-IS-CODE) |
| New deliverables for v0.2 | 11 (per §6.1 — ArchiMate + UML + glossary + provenance + patterns + the diagram itself committed) |
| Connection to existing | catalogue §2d + §4.3.2c + §5; methodology AMENDMENT; N8 contract §2 + §15; Opus review §6.5; SYNCHRO §3 |
| Long-term arc | 4 stages (per §7) — stage 0 starts CP-SUPIN-03 morning |
| Paste-ready ThinkPad addendum | §11 below (insert at end of synchro §10 prompt OR after the N8 addendum from `SUPIN-N8-CONTRACT-ANALYSIS-v0.1.md` §17) |
| Status | v0.1 — discipline established; CP-SUPIN-03 morning consumption ready |

---

## §10. SUPIN GitHub branch / Bouračka tree placement

Per operator note: ThinkPad pushes to **GitHub SUPIN branch / Bouračka tree**. This is a more granular path than the existing `thinkpad` branch on the monorepo. Operator-side decision:

- Option A: continue using `thinkpad` branch with `bouracka-tests/` directory; promote to dedicated SUPIN branch later.
- Option B: create new `supin` branch on the monorepo NOW; `bouracka-tests/` lives there; future SUPIN engagements (other apps) extend the same tree.
- Option C: dedicated `supin/bouracka` branch (granular per-app).

Recommendation: **Option B** for v0.2 — gives breathing room for AISPOV, zenID-via-SUPIN, future SUPIN apps without thrashing the branch tree; one rename-rebase from current `thinkpad`. ThinkPad does the rebase as STEP 7 sub-task of CP-SUPIN-03.

The `arch-models/` directory lives at the repo root (not under `bouracka-tests/`) — because it spans multiple apps in the SUPIN ecosystem, not just Bouračka.

```
<repo-root>/                                  (on supin branch)
├── bouracka-tests/                            (current; testing track)
│   ├── BOURACKA-TESTPLAN-v0.2.xlsx
│   ├── playwright/ cypress/ testcafe/
│   ├── _specs/
│   └── ... (per existing structure)
│
├── arch-models/                               (NEW; harvest track)
│   ├── archimate/
│   ├── bpmn/
│   ├── uml/
│   ├── erd/
│   ├── topology/
│   ├── glossary/
│   ├── provenance/
│   ├── patterns/
│   └── source/                                (committed source materials: S1 diagram, scans, etc.)
│
├── tools/
│   ├── validate-models.py                     (NEW)
│   ├── scan-stale-models.py                   (NEW)
│   ├── cross-source-diff.py                   (NEW)
│   ├── runtime-probes.py                      (NEW)
│   ├── drift-detect.py                        (NEW; nightly)
│   ├── validate-workbook.py                   (existing per Opus review §6.6 — extend to check arch-model refs)
│   └── ...
│
├── _config/                                   (workspace meta — already exists on macbook)
│   ├── VOCABULARY-CATALOGUE-CS-EN-V0.1.md
│   ├── SUPIN-N8-CONTRACT-ANALYSIS-v0.1.md
│   ├── SUPIN-ARCH-HARVEST-DISCIPLINE-v0.1.md     ← THIS
│   └── ...
│
└── CHANGELOG.md
```

---

## §11. PASTE-READY ADDENDUM to ThinkPad CP-SUPIN-03 prompt

Append AFTER the N8 contract addendum (§17 of `SUPIN-N8-CONTRACT-ANALYSIS-v0.1.md`), BEFORE `═══ END PROMPT ═══`.

```
═════════════════════════════════════════════════════════════════════════════
ADDENDUM 2 (per _config/SUPIN-ARCH-HARVEST-DISCIPLINE-v0.1.md)
═════════════════════════════════════════════════════════════════════════════
Operator established a SECOND analytical track 2026-05-06 — the
architectural-harvest track. Its purpose: build coherent
ArchiMate / BPMN / UML / ERD model documentation for the SUPIN
ecosystem (NOT just Bouračka), connecting hand-drawn diagrams,
WSDL files, OpenAPIs, code, and runtime probes into a single
living model.

Operator-supplied first source (S1): Bouračka–IS ČKP architectural
diagram (PNG; LOW confidence per S1 metadata). Operator caveat:
"keep all these inputs with pinch of salt; not confirmed up-to-date".
SUPIN ecosystem is well-developed but inconsistently documented —
the harvest track addresses this gap as an explicit long-term
engagement value.

═════════════════════════════════════════════════════════════════════════════
STEP 4A — ARCHITECTURAL HARVEST (NEW track for v0.2 deliverable)
═════════════════════════════════════════════════════════════════════════════
4A.1  Rebase + branch: rebase thinkpad → create new branch `supin`
      from current thinkpad HEAD. Push origin/supin. From now CP-SUPIN-NN
      iterations land on `supin` branch (per OQ-ARCH-20 recommendation).

4A.2  Create directory structure at repo root:
        arch-models/{archimate,bpmn,uml/{class,sequence,activity,state},erd,topology,glossary,provenance,patterns,source}/
        tools/{validate-models,scan-stale-models,cross-source-diff,runtime-probes,drift-detect}.py (stubs)

4A.3  Commit source materials:
        arch-models/source/S1-bouracka-iskcp-diagram-2026-05-06.png
        arch-models/source/S2-n8-openapi.yaml
        arch-models/source/S2-n8-postman.collection.json
        arch-models/source/S2-n8-readyapi-project.xml

4A.4  Author first architecture model files (LOW-MEDIUM confidence; LOG
      every element's source/confidence/last_validated):
        arch-models/archimate/02-application-layer.archimate
          - actors: Klient (alias: Účastník per L-DOM-1)
          - components: Aplikace Bouračka (Azure), AISPOV, AIS ČKP, SEDN,
                        P3WS, B3WS, D8WS, N8, ROB, CRŘ
          - relationships per §2.1 of SUPIN-ARCH-HARVEST-DISCIPLINE
          - boundary: IS ČKP (containing SEDN, P3WS, AISPOV, B3WS, AIS ČKP)
          - external: ROB, CRŘ (ISSS), Pojistitel/PČR
        arch-models/patterns/PATTERN-CP-001-supin-platform-interface.archimate
          - extracted from SUPIN-N8-CONTRACT-ANALYSIS §2 (the SUPIN house style)
          - URL pattern, header pattern, mTLS, /fake/ overlay, calendar versioning
        arch-models/uml/state/ST-CP-001-accidentReportStatus.puml
          - PlantUML state diagram; 8 states + transitions per L-ARCH-1
          - cross-reference to workbook 01c_StateMachine
        arch-models/uml/sequence/SEQ-CP-003-AISPOV-orchestration.puml
          - Bouračka → AISPOV → {ROB, CRŘ, AIS ČKP} → reply chain
          - confidence LOW; based on S1 reading; hypothesis pending OQ-ARCH-03+04+11
        arch-models/uml/sequence/SEQ-CP-004-N8-OTP-roundtrip.puml
          - per N8 contract §6.2; confidence HIGH (full contract in hand)
        arch-models/uml/sequence/SEQ-CP-005-output-fanout.puml
          - SMS / Email / PDF / XML / SEDN paths from S1
        arch-models/glossary/GLOSSARY-CP.yaml
          - terms harvested from S1 + S4 + L-DOM-1..5 + N8 platform pattern
          - cross-reference to VOCABULARY-CATALOGUE §6 + §2 of harvest doc

4A.5  Author provenance + validity files:
        arch-models/provenance/elements.yaml
          - one entry per element with R-HARVEST-1 tags
        arch-models/provenance/consistency-checks.yaml
          - pre-seed with 7 §2.3 suspicions from harvest doc
        arch-models/provenance/validity-probes.yaml
          - VP-N8-001 (Ping against /fake/; nightly; cadence)
          - VP-AISPOV-001 (BLOCKED on OQ-ARCH-03; status=blocked)
          - VP-CONSISTENCY-001 (Klient ↔ Účastník drift; every commit)

4A.6  Author tools:
        tools/validate-models.py — schema + cross-ref + R-HARVEST-1 tag check
        tools/scan-stale-models.py — R-VALIDITY-1 decay scan; emits stale report
        tools/cross-source-diff.py — R-CONSISTENCY-1 cross-source diff
        tools/runtime-probes.py — Newman-driven; consumes validity-probes.yaml
        tools/drift-detect.py — release vs model staleness

      EXTEND tools/validate-workbook.py (per Opus review §6.6) to check that
      every workbook source_artefact_ref resolves to either a recon material
      OR a model element ID under arch-models/.

4A.7  Author scripts wrappers:
        scripts/validate-models.ps1
        scripts/scan-stale-models.ps1
        scripts/cross-source-diff.ps1
        scripts/runtime-probes.ps1
        scripts/drift-detect.ps1

4A.8  File OQs:
        OQ-ARCH-01..16 from §2.2 of harvest doc (element-level)
        OQ-ARCH-17..25 from §8 of harvest doc (track-level)

4A.9  Update analytical bundle packaging script:
        scripts/package-delivery-analytical-v0.2.0.ps1 INCLUDES the
        arch-models/ directory + the new tools/. SUPIN sees the harvest
        track as a first-class engagement deliverable, not a side-project.

4A.10 Update LESSONS-LEARNED-CP-SUPIN-02-v0.1.md → v0.2 add new section:
        §6 Lessons-arch-track (the dual-track frame is operational)

═════════════════════════════════════════════════════════════════════════════
NEW R-RULES (binding from now)
═════════════════════════════════════════════════════════════════════════════
R-HARVEST-1     every model element carries provenance + confidence +
                last_validated_at + validity_decay_days; no silent untagged
                elements
R-VALIDITY-1    elements past their decay window go to harvest backlog;
                stale elements are flagged in renders and propagate flag
                to dependent tests/derived artefacts
R-CONSISTENCY-1 source disagreements logged not silently resolved;
                consistency-test TC fires runtime probe to break tie
R-MODEL-IS-CODE all model artefacts ship in machine-checkable formats;
                free-text-only docs may accompany but never substitute

═════════════════════════════════════════════════════════════════════════════
WHEN TO BOUNCE BACK
═════════════════════════════════════════════════════════════════════════════
File OQ + STOP if:
  • Tooling choice (Archi vs alternatives — OQ-ARCH-17) blocks v0.2
    authoring → escalate to operator immediately; meanwhile use
    PlantUML-archimate as bridging format
  • Branch rebase fails → halt; operator-side resolves; harvest
    work continues on thinkpad branch with an explicit "to-rebase"
    note
  • Validity probes against real /TST/ endpoints uniformly need
    mTLS cert (VP-AISPOV-001 currently blocked; if VP-N8-001 also
    blocks despite /fake/ being open, that's a finding worth
    flagging immediately)
═════════════════════════════════════════════════════════════════════════════
```

---

*SUPIN-ARCH-HARVEST-DISCIPLINE-v0.1.md — 2026-05-06 — MacBook CoWork session — Opus*
