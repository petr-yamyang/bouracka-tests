# Bouračka data-store evolution plan — v0.1 (EN)

**Status.** Strategic planning draft. Not a commitment to specific code changes today.
**Predecessor.** None — first version of this plan.
**Sibling docs.**
- `bouracka-tests/_specs/CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.md` (binding wire format)
- `bouracka-tests/_specs/from-macbook/SUPIN-ARCH-HARVEST-DISCIPLINE-v0.1.md` (Track 2 ERD harvest discipline)
- `FOURIER-FOUNDATIONS-WORKING-SPEC-v0.2-EN.md` §3.2 (Fourier's JSON-catalogue choice)
- `bouracka-tests/_config/BOURACKA-UI-DESIGN-v0.1-2026-05-10.md` (current UI design)
**Owner.** Pete Y.
**Authored.** 2026-05-12, after Kate v0.1.2 drop dispatched.
**Audience.** Pete (project lead), future MI-M-T contributors who'll inherit Bouračka patterns, SUPIN architecture board if/when consulted.

---

## §1. Strategic frame

Bouračka is a **pilot under MI-M-T**, not an independent product. Its data-store
evolution must therefore harmonise with MI-M-T B/E patterns rather than invent
local-Bouračka idioms. The shape:

```
┌──────────────────────────── DEVELOPMENT (Pete's laptops) ────────────────────────────┐
│                                                                                       │
│   MI-M-T B/E (in development)                Bouračka B/E (pilot)                     │
│   ────────────────────────                   ──────────────────                       │
│   PostgreSQL    — relational data            BOURACKA-TESTPLAN-v0.4.x.xlsx            │
│   MongoDB       — document data              Excel (single-writer)                    │
│                                                                                       │
│   Repository abstractions emerge here.       Workbook_io.py / openpyxl reads/writes.  │
│   When stable, exported as patterns.         Awaits MI-M-T patterns to crystallise.   │
│                                                                                       │
└──────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼  patterns + DDL  +  ops runbooks
┌──────────────────────────── PRODUCTION (SUPIN-managed) ──────────────────────────────┐
│                                                                                       │
│   SUPIN existing shared Oracle instance                                               │
│   ──────────────────────────────────────                                              │
│   • Bouračka schema (BCKA_* tables) — relational tables that mirror Postgres shape   │
│   • Bouračka JSON columns (or sibling tables) — Oracle JSON column type or BLOB       │
│     storage that mirrors Mongo document shape                                         │
│   • DBA-mediated DDL changes (SUPIN review gate)                                      │
│   • Backup/PITR per SUPIN DBA policy                                                  │
│                                                                                       │
│   Bouračka-UI server-side: SUPIN-hosted; auth via SUPIN identity provider             │
│                                                                                       │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

This frame answers Pete's M2-question:

> *"prepare hooks and arch patterns during existing versions of Bouračka B/E
> rework and use patterns developing for MI-M-T. MI-M-T will be more complex
> and richer, but structures would be deployed also on Oracle db shadowing
> PostgreSQL and Mongo used for developing MI-M-T B/E."*

Bouračka **does not refactor `workbook_io.py` into a full IRepository
abstraction today**. Bouračka **leaves the hooks visible** so that when
MI-M-T's `IRepository` (or whatever the canonical name turns out to be)
crystallises, the swap is mechanical not architectural.

---

## §2. Trigger conditions

Per Pete 2026-05-12: **migration trigger = Bouračka-tests v1.0.0 release (Cíl-4 complete)**.

Translates to: full coverage rule reaches strict gating across all four Cíl
levels per `_specs/COVERAGE-RULE-STRATEGY-v0.1-CS.md`. Conservative timeline
— estimate Q3-Q4 2026, possibly into 2027.

**This is the right trigger because:**
- Cíl-1/2/3 are demo + tst-demo + tst + uat environments respectively. At Cíl-4 the test suite is gating production. Production-gating means the data store is on the critical path; migration to RDBMS is no longer optional.
- Until then, Excel + bouracka-ui is sufficient for Pete + Kate + handful of testers. Single-writer is acceptable. No multi-team audit yet.
- MI-M-T B/E patterns have time to crystallise in parallel.

**Soft-trigger overrides** (any one accelerates migration regardless of Cíl):
- Two or more concurrent testers regularly hit `WorkbookLockedError 409`
- A regulator / auditor requests row-level history that Excel can't cheaply produce
- A new client pilot adopts Bouračka and brings its own multi-tester team
- MI-M-T B/E pattern formalisation lands earlier than expected and Pete chooses to early-port Bouračka as the demonstration

---

## §3. The 8 chessmate moves (revised after Pete's 2026-05-12 input)

### M1 — Workbook schema freeze after Phase-2 patches

**State.** v0.4.3 is KP-reviewed primary. v0.4.4 (RÚIAN target + state machine
codes) is the planned final structural bump per `CHANGELOG.md` 2026-05-12.

**Action.** After Phase-2 patcher is fixed (against the real workbook headers
this time) and v0.4.4 lands:
- No new sheets.
- No new columns.
- Only **data** changes thereafter.
- Each sheet documented as a **proto-table spec** in §4 of this doc — column types, FK relationships, intended Oracle-column-name mapping, indexes.

**Effort.** Phase-2 patches: ~2 hours (rerun against real schema). Proto-table specs: ~4 hours one-time + incremental as sheets evolve.

**Risk if skipped.** Migration target keeps moving. ERD work is destabilised by structural Excel churn.

### M2 (REVISED) — Leave the abstraction hooks visible, don't refactor yet

**Old M2.** "Refactor `workbook_io.py` into `IRepository` interface with `ExcelRepository` impl."

**New M2 per Pete.** Don't refactor. Instead:
- Keep `workbook_io.py` as it is — one module, openpyxl-backed.
- **Annotate** the module + each public function with `# REPO-HOOK:` comments marking the boundaries where a future `IRepository` impl would substitute.
- **Avoid leaking openpyxl idioms into `server.py`.** Server.py calls `workbook_io.list_envs()`, `list_tcs()`, `list_bugs()`, `append_bug()` — never imports `openpyxl` directly.
- **Existing B/E rework** (when Pete cycles back to bouracka-ui code) follows the principle: no openpyxl in callers; all data access through `workbook_io.py` module-level functions.
- When MI-M-T B/E publishes its repository pattern, swap `workbook_io.py` for a `IRepository`-conforming module in one commit.

**Effort.** Zero new code. Discipline + light annotation as Pete touches the existing modules.

**Why this is the right discipline.** MI-M-T B/E is being designed against Postgres+Mongo, which have different idioms than openpyxl. A premature `IRepository` shaped around openpyxl idioms could **distort** MI-M-T's natural abstraction. Better to wait for MI-M-T patterns to land and shape Bouračka around them.

### M3 — Cross-framework result envelope locked as Oracle ingest contract

**State.** `_specs/CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.md` is already storage-agnostic. The envelope has all the columns Oracle needs: `schema_version, run_id, env, env_url, started_at, ended_at, duration_ms, host, drift_forensic, reporter, results[], summary{}`.

**Action.** Mark this spec as **binding for Oracle ingest**:
- The eventual `OracleRepository.insert_run(envelope)` accepts the envelope verbatim.
- Oracle JSON column type (Oracle 12c+) stores the document parts (`drift_forensic`, `results[]` per TC, `evidence`, `error_messages`); flat relational columns store the queryable parts (`schema_version`, `run_id`, `env`, timestamps, summary metrics).
- No envelope-schema changes between now and Cíl-4 without bumping `schema_version` and writing a migrator.

**Effort.** Paperwork: ~30 min — add a note to the schema doc that v0.1 is the binding Oracle ingest contract.

### M4 — Oracle ERD design doc (Track 2 harvest, no code)

**Action.** Author `_config/BOURACKA-ORACLE-ERD-v0.1-EN.md` in parallel to current Bouračka work. One section per sheet in v0.4.4 workbook, mapping to:
- Oracle table name (`BCKA_TEST_CASES`, `BCKA_TEST_TARGETS`, `BCKA_BUGS`, etc.) following SUPIN naming convention.
- Column list with Oracle types (`VARCHAR2(255)`, `NUMBER(10,2)`, `CLOB`, `TIMESTAMP WITH TIME ZONE`, `JSON` for Oracle 21c+).
- Primary keys (synthetic `id` column auto-incremented via sequence).
- Foreign keys with explicit `ON DELETE` policy.
- Indexes for the query patterns the UI uses.
- Row-version column for optimistic concurrency (see M7).

**Sheets that become document storage** (Oracle JSON column, not relational table):
- `06_TestRuns` — run envelopes are inherently document-shaped per M3.
- `07_TestRunResults` — same.
- `14_AssertionGateResults` — assertion-by-assertion blobs; document-shaped.
- `13_TestExecutionSummary` — summary computed at consolidation time; could be either, lean document.

**Effort.** ~6-10 hours over multiple sessions. Independent of code work. Feeds DBA conversations in M6.

### M5 — Auth boundary scaffolding (hooks, not implementation)

**Action.** Add `Depends(get_current_user)` shim to `bouracka_ui/server.py` route handlers:
- Today: `get_current_user()` returns hardcoded `{"username": "local-pete", "roles": ["operator", "admin"]}`.
- Tomorrow (server-side): returns real user from SUPIN identity provider (OIDC / SAML / SUPIN-internal SSO — TBD per M6 DBA chat).
- Route handlers shift signature from `def list_envs():` to `def list_envs(user = Depends(get_current_user)):`.
- Today no behaviour change. Tomorrow no code change.

**Effort.** ~2 hours when Pete next touches server.py. Defer until then.

### M6 — Existing SUPIN Oracle instance: DBA contact + policy

**Action items (Pete-side, not code):**
- Identify SUPIN DBA owner of the Oracle instance.
- Confirm Oracle version (12c / 19c / 21c / 23c — naming convention + JSON support varies).
- Confirm DDL policy: dev-issued DDL vs DBA-issued. (Existing SUPIN shared instance almost certainly = DBA-mediated.)
- Confirm schema naming convention (`BCKA_*` proposed; SUPIN may have an established pattern).
- Confirm backup/PITR policy.
- Confirm change-window cadence (some SUPIN Oracle instances have e.g. weekly DBA windows).

**Effort.** SUPIN-side conversations. Could start anytime. Result captured back in §6 of this doc as decisions land.

### M7 — Concurrency model: optimistic with `row_version` column

**Decision.** Optimistic concurrency with `row_version` (or `last_modified_at`) column on every mutable table.

**Rationale.**
- Test-execution workload is read-heavy; few concurrent writers.
- Bug filing is the main write path; conflicts are rare in practice (testers filing different bugs).
- Optimistic concurrency avoids lock-holding that pessimistic would cause across HTTP request boundaries.
- Standard Oracle pattern; matches MI-M-T's likely Postgres pattern (Postgres also defaults to MVCC-friendly optimistic patterns).

**Action.** Document the decision here. Implementation lands at migration time, not before.

**Conflict resolution policy** (to be confirmed):
- Bouračka-UI on write detects `row_version` mismatch → returns HTTP 409 with conflict body → operator reviews and re-submits.
- For bug filing: auto-merge attempts not advisable (free-text fields don't merge cleanly); operator-mediated only.

### M8 — Lessons brick into MI-M-T

**Action.** Maintain `_config/MI-M-T-DATA-STORE-EVOLUTION-LESSONS-v0.1.md` as a running notes file capturing decisions made during Bouračka's evolution:
- "Excel sufficed for N=1-3 testers, single-writer, single-team" — calibration point for when JSON suffices vs RDBMS necessary.
- "Cross-framework result envelope was already document-shaped before we knew it would land in Mongo / Oracle JSON" — pattern: design envelopes storage-agnostic.
- "Schema freeze at v0.4.x before migration prevented thrash" — pattern: lock schema before ERD.
- "Repository hooks left in source for ~6 months before MI-M-T patterns landed" — pattern: discipline > premature abstraction.

This file becomes a chapter in MI-M-T core methodology docs when Bouračka v1.0.0 ships.

**Effort.** Running notes, ~30 min per significant decision. ~10 hours over the lifetime.

---

## §4. Sheet → proto-table mapping (seed for M4 ERD doc)

This section seeds the ERD design doc. Each row is a hypothesis to validate
against the actual v0.4.4 workbook structure during M1 schema-freeze.

| Workbook sheet | Proposed Oracle table | Storage shape | Notes |
|---|---|---|---|
| `00_README` | (none — repo doc) | — | Lives in source control, not DB |
| `00b_Requirements` | `BCKA_REQUIREMENTS` | Relational | One row per REQ-* |
| `00c_VersionSanityRules` | `BCKA_VERSION_RULES` | Relational | Small static config table |
| `00e_BranchView` | (computed view) | View | Not a base table; computed from `BCKA_*` joins |
| `01_TestTargets` | `BCKA_TEST_TARGETS` | Relational | FK to `BCKA_REQUIREMENTS` |
| `01b_Req_FURPS_Cartesian` | `BCKA_FURPS_MATRIX` | Relational | M:N between REQ and FURPS classifier |
| `01c_StateMachine` | `BCKA_STATE_MACHINE` | Relational | Static transition table; small |
| `01d_PrioritySevUrgMatrix` | `BCKA_PRIORITY_MATRIX` | Relational | Tiny static reference table |
| `02_TestCases` | `BCKA_TEST_CASES` | Relational | The big table; ~150-300 rows |
| `02b_TC_Parameters` | `BCKA_TC_PARAMETERS` | Relational | FK to `BCKA_TEST_CASES` |
| `02c_TC_Assertions` | `BCKA_TC_ASSERTIONS` | Relational | FK to `BCKA_TEST_CASES`, FK to `BCKA_ASSERTION_LIBRARY` |
| `02d_AssertionLibrary` | `BCKA_ASSERTION_LIBRARY` | Relational | Catalog of assertion templates |
| `03_TestData` | `BCKA_TEST_DATA` | Relational + JSON | Bulk YAML fixtures; consider JSON column for the YAML blob |
| `04_TestEnvironments` | `BCKA_TEST_ENVIRONMENTS` | Relational | One row per ENV-* code |
| `05_TestSets_DEPRECATED` | (drop, do not migrate) | — | Already deprecated per sheet name |
| `05a_TestPlan` | `BCKA_TEST_PLAN` | Relational | One row per planned campaign |
| `05b_TestSchedule` | `BCKA_TEST_SCHEDULE` | Relational | FK to `BCKA_TEST_PLAN` |
| `05c_TestEstimate` | `BCKA_TEST_ESTIMATE` | Relational | FK to `BCKA_TEST_PLAN` |
| `06_TestRuns` | `BCKA_TEST_RUNS` | Relational + JSON | Flat columns for queryable bits; JSON column for envelope tail |
| `07_TestRunResults` | `BCKA_TEST_RUN_RESULTS` | Relational + JSON | Per-TC results; FK to `BCKA_TEST_RUNS`; JSON for verdict + evidence blobs |
| `08_Bugs` | `BCKA_BUGS` | Relational | Append-heavy table; FK to `BCKA_TEST_RUN_RESULTS` |
| `09_Reports` | (computed views) | Views | Reports are aggregations; not base tables |
| `10_Glossary` | `BCKA_GLOSSARY` | Relational | Reference data |
| `11_Changelog` | (none — repo CHANGELOG.md is canonical) | — | Don't migrate; CHANGELOG.md stays in source control |
| `13_TestExecutionSummary` | `BCKA_TEST_EXECUTION_SUMMARY` | Relational + JSON | Per-run summary; lean toward JSON document |
| `14_AssertionGateResults` | `BCKA_ASSERTION_GATE_RESULTS` | Relational + JSON | Per-assertion outcome; JSON for the assertion params |

**Total:** ~20 base tables + ~3 computed views. Within scope of a single SUPIN
DBA review cycle.

---

## §5. Bouračka-UI server-side deployment (post-migration)

Out-of-scope for v0.1 of this doc; placeholder for v0.2 once MI-M-T B/E
deployment patterns are clearer. Open questions:

- SUPIN VM vs container vs hybrid?
- Reverse proxy (nginx? Apache? SUPIN-managed ingress)?
- TLS termination location?
- Multi-tester session model (sticky vs stateless)?
- Static asset hosting (CDN vs server-local)?
- Backup of UI-side state (run logs, trace bundles) vs Oracle-side state?

---

## §6. Open questions for Pete + SUPIN

| OQ | Question | Default if no decision |
|---|---|---|
| OQ-DSE-1 | SUPIN Oracle version + JSON-column support level | Assume Oracle 19c + JSON BLOB; revise if 21c+ confirms native JSON type |
| OQ-DSE-2 | DBA contact + change-window cadence | Assume weekly DDL window; revise per DBA |
| OQ-DSE-3 | Schema naming convention — `BCKA_*` vs SUPIN-established | Use `BCKA_*` as proposal; defer to DBA review |
| OQ-DSE-4 | Auth provider — SUPIN SSO? OIDC? SAML? Local LDAP? | Defer to M6 DBA chat |
| OQ-DSE-5 | Single Oracle schema or multi-schema (e.g. dev / uat / prod separation within the same instance)? | Single schema initially; partitioning emerges with multi-Cíl scaling |
| OQ-DSE-6 | When MI-M-T B/E publishes its repository pattern, who owns the Bouračka adoption — Pete or someone else? | Pete |
| OQ-DSE-7 | Do we publish this plan to MI-M-T core docs (sibling `mimt-governance/` repo) once v0.2 stabilises? | Yes, once Cíl-2 baseline confirms patterns hold |

---

## §7. Timing checkpoints

| Checkpoint | What it triggers | Estimated date |
|---|---|---|
| Kate v0.1.2 install PASS | Confirms current state works under SUPIN HP Elite constraints. **Unblocks Phase-2 workbook patches**. | Within 1-2 days of 2026-05-12 |
| Phase-2 workbook patches land (v0.4.4) | **M1 schema freeze.** | Within 1 week |
| First Cíl-2 baseline green on tst.demo.bouracka.cz | Pattern validation continues; no migration trigger | Estimated Q3 2026 |
| MI-M-T B/E publishes IRepository pattern | **M2 unblocks.** Bouračka adopts. | Unknown — track quarterly |
| Bouračka v1.0.0 / Cíl-4 strict gating | **Migration trigger.** Begin Oracle DDL work. | Q4 2026 / Q1 2027 estimate |
| Oracle migration cutover | Bouračka-UI moves server-side, Excel retired as primary | TBD, post v1.0.0 |

---

## §8. What we don't do in v0.1 of this doc

- **No code changes.** This is a planning artefact only.
- **No Oracle DDL drafted.** That comes after M4 ERD doc + M6 DBA conversations.
- **No commitment to specific MI-M-T pattern shape.** Bouračka follows when MI-M-T B/E publishes; doesn't predict.
- **No retirement of Excel workbook.** Excel + bouracka-ui remains the operative architecture until v1.0.0 trigger.
- **No UI server-side hosting plan.** Deferred to v0.2 of this doc.

---

## §9. Living-doc protocol

This doc bumps version (v0.1 → v0.2 → ...) when:
- An OQ-DSE-* gets resolved (capture decision + rationale, advance the section).
- A timing checkpoint moves significantly (>1 quarter).
- MI-M-T B/E publishes a relevant pattern (capture how Bouračka adopts).
- A new chessmate move emerges from operational experience (add as M9, M10, ...).

Pete authors; Cowork/Opus assists. Versions tagged in git. Older versions
archived under `_config/archive/`.

---

End of v0.1.
