# Lessons Learned — CP-SUPIN-04 — WORKING reference (read during session)

> **Different from** `LESSONS-LEARNED-CP-SUPIN-{02,03}-v*.md` — those
> were retrospective. This doc is a **during-session quick-reference**
> for the photo-driven main+alternate flow extraction work the user is
> running today.
>
> **Constraint accepted:** photos remain the only viable input channel;
> no direct tst.* access. Sub-optimal but durable — the artefacts below
> make the suboptimal pipeline reproducible, traceable, and friendly to
> the bottom-up UML reconstruction approach VUP (Unified Process)
> compliance demands.

---

## §0. The session shape

| Phase | Input | Output | Tool |
|-------|-------|--------|------|
| 1. Photo ingest | HEIC → JPG | `recon/screenflows-live/<flow-id>/photos/IMG_NNNN.jpg` | `tools/heic-to-jpg.ps1` |
| 2. Flow reconstruction | photo sequences | `recon/screenflows-live/<flow-id>/FLOW.md` per `_flow-template.md` | hand-fill |
| 3. UML formalisation | flow markdown | UML-compliant activity + sequence + use-case in Mermaid/PlantUML | `recon/uml-templates/*.puml` skeletons |
| 4. Test data capture | photo snippets | `recon/test-data-snippets/<flow>/snippet-NN.md` | `_snippet-template.md` |
| 5. Drift cross-check | flow + Excel rows | drift entries in `recon/screenflows-live/DRIFT-LOG.md` | hand-update |
| 6. SPEC.md refinement | confirmed flows | TC SPEC.md step lists firmed up | Tier-A workbook + Tier-B SPEC |
| 7. Aggregate decisions | run results across frameworks | `tools/test-console.py` → comparative report | (NEW this session) |

The pipeline is a loop: photo → flow → UML → SPEC → run → aggregate →
decide what's next.

---

## §1. Photo-as-evidence working rules

### L-WORK-1 — One flow per ingestion folder, NOT one screen

CP-SUPIN-02 used per-screen folders (`D00_homepage-rozcestnik/`).
That made sense for the analytical-doc photos (one page = one screen).
For LIVE flow capture, photos are sequential — you photograph the
**main flow** path through 10 screens, then go back and capture the
**alternate flow** through 3 of them.

**Rule:** create folders by flow, not by screen:
```
recon/screenflows-live/
├── flow-A1-main/             ← happy main path through PING + Phone-OTP
│   ├── photos/
│   ├── FLOW.md               ← the bottom-up reconstruction
│   └── snippets/             ← test data snippets in scope
├── flow-A1-alt-NOK/          ← alternate (failure) variant
├── flow-B-main/              ← happy main: driver-data load
├── flow-B-alt-OCR-NOK/
├── flow-B-alt-camera-denied/
└── …
```

Per-screen captures (when needed) live INSIDE the flow folder.

### L-WORK-2 — Photograph state-transition boundaries

The most useful single photos are the ones at **state transitions**
(`accidentReportStatus` changes). When you click "Pokračovat" and the
URL changes, capture both:
- the screen BEFORE the click (with cursor on the button)
- the screen AFTER the navigation completes

These pairs are the goldsource for the swim-lane swap in activity
diagrams. Without them you're guessing.

### L-WORK-3 — Bouračka and DEMO go in parallel folders, never mixed

Naming convention:
```
flow-A1-main-tst/             ← tst.bouracka.cz capture
flow-A1-main-tst-demo/        ← tst.demo.bouracka.cz capture
```

Cross-link in each `FLOW.md`:
```markdown
## Cross-env reference
- TST sibling : flow-A1-main-tst
- DEMO sibling: flow-A1-main-tst-demo
- Drift table : (filled after both folders complete)
```

DEMO usually mirrors TST with reduced validation (per scope C-5).
Photographing both lets the drift table populate cleanly.

### L-WORK-4 — Test data snippets are NOT in the photo folders

Test data (phone numbers used; OP numbers entered; expected names from
AISPOV; QR codes scanned) goes in a sibling folder:

```
flow-A1-main-tst/
├── photos/
└── snippets/
    ├── snippet-01-phone-number-input.md
    ├── snippet-02-otp-received.md
    ├── snippet-03-aispov-response.md
    └── …
```

Each snippet follows `_snippet-template.md` (see §3 below). Reason:
snippets often need redaction before commit; photos go in
`.gitignore` per `_install/EMAIL-DELIVERY-GUIDE-CS.md` confidentiality
posture.

---

## §2. UML-compliant reconstruction (VUP / Unified Process)

VUP / Unified Process expects three diagram kinds for testable
analytical artefacts:

### L-WORK-5 — Use Case diagram FIRST, then Activity, then Sequence

Order matters for VUP compliance:
1. **Use Case** (`recon/uml-templates/use-case-template.puml`) —
   actor + use case + extends/includes relationships.
2. **Activity Diagram** (`recon/uml-templates/activity-template.puml`)
   — swim-lanes (Účastník | Systém | Integrace), decision diamonds
   with guard expressions, fork/join bars where parallel.
3. **Sequence Diagram** (`recon/uml-templates/sequence-template.puml`)
   — lifelines per actor + integration, messages with parameters,
   `alt` / `opt` / `loop` fragments for branches.

Mermaid is OK for casual review; **PlantUML is the VUP-compliant
authoring target**. PlantUML renders to PNG/SVG via the same Graphviz
already on PATH.

### L-WORK-6 — Bottom-up reconstruction = evidence-grounded, not invented

Every UML element MUST cite its source photo:

```plantuml
'@startuml
actor "Účastník" as U
participant "SUT (Bouračka)" as S
participant "INT-002 N8 SMS Gateway" as N8

' source: flow-A1-main-tst/photos/IMG_1097.jpg (gateway entry)
U -> S: Click "VYPLNIT ZÁZNAM"
S -> S: Validate eligibility

' source: flow-A1-main-tst/photos/IMG_1098.jpg (transition state)
S -> N8: PING /api/v1/sms/ping
N8 --> S: 200 OK
@enduml
```

Comments with photo refs become inline citations.

### L-WORK-7 — Three diagrams per flow folder; auto-render via tool

For each `flow-<id>/` folder ship:
- `FLOW.md` — narrative (the human reading)
- `use-case.puml` — UML use case
- `activity.puml` — UML activity diagram
- `sequence.puml` — UML sequence diagram

Render via `tools/render-uml.ps1` (SCAFFOLD this session — see §5).

---

## §3. Test data snippets — standard shape

Each snippet captures one piece of test-relevant data observed in a
photo (or derived from one):

```markdown
# Snippet — <short subject>

## Provenance
| Field | Value |
|-------|-------|
| flow | flow-A1-main-tst |
| photo_ref | IMG_1099.jpg (zoom region: top-right corner) |
| captured_at | YYYY-MM-DD HH:MM |
| env | tst | tst-demo |

## Data captured
\```yaml
field_name: value
field_kind: phone | op_number | rp_number | spz | otp | response_json | …
data_source: <user-entered | sut-rendered | network-response | …>
sanitised: <yes | no — REQUIRES REDACTION BEFORE COMMIT>
\```

## What this enables
- (test scenario / TC ref / Mockoon scenario / fixture row)

## Cross-env divergence (if known)
- TST: …
- DEMO: …
```

**Sanitisation rule:** any snippet with `sanitised: no` is
gitignored automatically (`.gitignore` already covers
`recon/screenflows-live/**/snippets/`).

---

## §4. Aggregating runs across frameworks

The Gate 1/2/3 decisions in `CLIENT-PILOT-SUPIN-V0.1.md` §3.3
(Cypress vs Playwright vs TestCafe) need data, not opinions.
The **test console** (§5) writes one row to `07_TestRunResults` per
TC × framework × env, with these new aggregation-relevant columns:

| Column | Purpose |
|--------|---------|
| `framework` | playwright \| cypress \| testcafe |
| `verdict` | pass \| fail \| skip \| blocked \| partial |
| `duration_ms` | for performance comparison |
| `viewport` | which mobile viewport (320 / 375 / 414) |
| `flake_count` | retry-to-green count (reliability proxy) |
| `console_errors_n` | front-end errors observed during run |
| `network_failures_n` | XHR/fetch failures observed |

Reports query:
- per-framework pass-rate
- per-framework p95 duration
- per-framework flake rate
- which TC fails on N frameworks but not M

**Decision rule:** at Gate 2 (after ≥ 5 R1 TCs run on each framework)
the framework with the highest pass-rate × lowest flake-rate × lowest
p95-duration becomes the primary; the others stay as backup.

---

## §5. Test console scaffold (NEW this session)

### L-WORK-8 — One CLI; multi-framework; multi-env; one report

`tools/test-console.py` is the single entry point. CLI:

```
python tools/test-console.py run --env tst --frameworks playwright,cypress
python tools/test-console.py run --env tst --tcs TC-CP-001,TC-CP-005
python tools/test-console.py report --since 2026-05-06 --by framework
python tools/test-console.py compare --tcs TC-CP-001..TC-CP-005
```

Output: writes rows to `07_TestRunResults` of the workbook (already
designed for it — Excel reporter convention from CP-SUPIN-02).

### L-WORK-9 — The console tells the framework decision

After each run cycle the console emits a one-page comparison report
per `recon/RUN-AGGREGATION/<date>.md`:

```
| Framework | TCs run | Pass | Fail | Skip | p50 dur | p95 dur | Flake-rate |
|-----------|--------:|-----:|-----:|-----:|--------:|--------:|-----------:|
| playwright | 24 | 22 | 1 | 1 | 12 s | 38 s | 4 % |
| cypress    | 24 | 21 | 2 | 1 | 14 s | 42 s | 6 % |
| testcafe   | 12 |  9 | 1 | 2 | 18 s | 55 s | 12 % |
```

This is what gets fed into the Gate 1/2/3 decision. Numbers, not
preference.

---

## §6. Friction list — things to fix before next session

(Append-only; CP-SUPIN-05 picks up.)

- [ ] Per-screen template still useful for analytical-doc photos;
      keep + add per-flow template (L-WORK-1)
- [ ] Mockoon profile only covers happy + EX_CHYBA; real N8 may
      reveal more failure modes — extend profile after OQ-CP-27 reply
- [ ] Test console doesn't yet integrate cypress + testcafe (CP-SUPIN-05
      fills these adapters; this session = playwright-only)
- [ ] PlantUML render needs JRE (Profile C of install plan); operator
      check before authoring puml — fall back to Mermaid if no JRE

---

## §6b. Mid-session amendment — DEMO went public 2026-05-06

Posture change discovered mid-session: `demo.bouracka.cz/formular/`
is now publicly reachable (was IP-restricted yesterday). This adds
**L-WORK-10..12** without invalidating L-WORK-1..9.

### L-WORK-10 — Tier 2 splits into 2a (DEMO scrapeable) + 2b (PROD photo-only)

`_specs/DOCUMENTATION-POLICY-v0.1.md` §2 updated. DEMO is now the
**cheapest accurate** ground-truth source for UX/UI/state/validation
shape. PROD/tst stays the **integration-fidelity** reference — real
N8 SMS dispatch, real AISPOV registry behaviour, real ZID OCR. The
two coexist; the delta matrix tracks where they diverge.

### L-WORK-11 — Always carry an `env_constraint` on every TC

Per `recon/DELTA-DEMO-vs-PROD-v0.1.md` §5, `02_TestCases` gets a new
column `env_constraints` with values `both | demo-only | prod-only |
both-with-adapter`. CP-SUPIN-04 STEP 7 schema-migrates the workbook
+ backfills.

### L-WORK-12 — Every observed divergence becomes a Δ row before it becomes a TC change

Don't quietly fork TCs when DEMO ≠ PROD. Append a Δ row to
`DELTA-DEMO-vs-PROD-v0.1.md` first; **then** decide whether the TC
forks (`-DEMO` / `-PROD`) or carries an env-keyed fixture
(`both-with-adapter`). The matrix is the audit trail; the TC fork
is the consequence.

### Companion artefacts authored mid-session

- `recon/DEMO-PUBLIC-LIVE-2026-05-06.md` — posture-change brief +
  capture plan + reachability status.
- `recon/DELTA-DEMO-vs-PROD-v0.1.md` — 20-row Δ matrix scaffold
  (8 integration + 6 config + 6 behavioural).
- `_specs/DOCUMENTATION-POLICY-v0.1.md` §2 + §2.1 — tier model
  expanded to 4 tiers (Tier 1 / Tier 2a / Tier 2b / Tier 3) with
  drift-handling rule for Tier 2a-vs-2b.

### Capture pending

Egress allowlist on this Cowork session blocks `demo.bouracka.cz`.
Three unblock options documented in
`recon/DEMO-PUBLIC-LIVE-2026-05-06.md` §1; recommended path is
connecting the Claude in Chrome extension for live SPA navigation.

---

## §7. Status

| Item | Value |
|------|-------|
| Document | `_specs/LESSONS-LEARNED-CP-SUPIN-04-WORKING.md` |
| Type | working reference (not retrospective) |
| Companion artefacts | flow template (§1), UML templates (§2), snippet template (§3), test console (§5), DEMO posture brief + Δ matrix (§6b) |
| Authored by | Cowork Opus / CP-SUPIN-04 opening + mid-session amendment |
| Lessons | L-WORK-1..12 |
| Status | v0.2 — read DURING the iteration; refine as session progresses |
