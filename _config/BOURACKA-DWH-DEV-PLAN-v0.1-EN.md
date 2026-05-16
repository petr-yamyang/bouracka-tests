# Bouračka DWH B/E development plan — v0.1 (EN)

**Status.** Strategic plan for back-end implementation of the Bouračka TestPlan + TES (Test Execution Summary) data warehouse on the SUPIN-provisioned Oracle RDS instance, while keeping the current Excel + bouracka-ui solution running in parallel.
**Trigger.** 2026-05-13 — SUPIN DBA provisioned schema `TESTER` on `RDS.INT-CKP.CZ` with tablespace `TESTER_DATA`, profile `PRFL_TESTER`, and 9 DDL grants. M6 of `BOURACKA-DATA-STORE-EVOLUTION-PLAN-v0.1-EN.md` unblocked.
**Sibling docs.**
- `_config/BOURACKA-DATA-STORE-EVOLUTION-PLAN-v0.1-EN.md` — overall migration plan (8 chessmate moves M1-M8)
- `_config/BOURACKA-ORACLE-ERD-v0.1-EN.md` — first-portion ERD covering 5 highest-traffic tables
- `_specs/CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.md` — binding wire format the DWH ingests
- `_specs/TEST-TARGET-ATTRIBUTE-MODEL-v0.1.md` — TT attribute discipline informing schema design
- `_config/MI-M-T-DATA-STORE-EVOLUTION-LESSONS-v0.1.md` — running lessons brick
**Owner.** Pete Y.
**Authored.** 2026-05-13.
**Audience.** Pete (executor); SUPIN DBA (review + grants follow-up); MI-M-T B/E architect (pattern import); bouracka-ui future maintainer (hooks consumer).

---

## §1. Strategic frame — discovery before commitment

Pete 2026-05-13: *"start with creating documentation and hooks ... in way that produce first scripts i will run manually on the test instance and collect necessary informations for serious development."*

This frames the next phase as **discovery, not commitment**. The Oracle ERD v0.1 was authored without empirical knowledge of:
- The exact Oracle version SUPIN runs (12c / 19c / 21c / 23c each have different JSON support, partitioning, indexing)
- The character set + NLS settings (affects Czech-language data + sort behaviour)
- Tablespace quota and growth policy
- What's already in the TESTER schema (if anything — would cause naming collisions)
- Whether the granted privileges actually include everything ERD §8.2 needs (notably CREATE TRIGGER which is NOT in the explicit grant list)
- Performance characteristics for typical operations (INSERT/UPDATE/SELECT on small reference tables vs large run-archive tables)
- Session settings (commit_write, cursor_sharing, optimizer_features_enable)

Running discovery scripts on the live test instance answers these questions empirically and feeds the v0.2 ERD with concrete information rather than assumptions.

```
┌──────────────────── PHASE 1 — DISCOVERY (this doc's scope) ──────────────────────┐
│                                                                                    │
│  Pete runs _db/discovery/*.sql manually on RDS.INT-CKP.CZ                          │
│  Each script outputs structured findings (commented + machine-readable)            │
│  Pete pastes findings into discovery-results-YYYY-MM-DD.md                         │
│  Cowork consumes findings → produces v0.2 ERD with reality-grounded decisions     │
│                                                                                    │
└────────────────────────────────────┬───────────────────────────────────────────────┘
                                     ↓
┌──────────────────── PHASE 2 — DDL DRAFT (informed by Phase 1) ──────────────────────┐
│                                                                                      │
│  v0.2 ERD authored with discovered facts                                             │
│  v0.1 DDL files produced split per table                                             │
│  Smoke-test SQL written for each table (CRUD + concurrency)                          │
│  Send to SUPIN DBA for review                                                        │
│                                                                                      │
└────────────────────────────────────┬─────────────────────────────────────────────────┘
                                     ↓
┌──────────────────── PHASE 3 — DDL APPLY (informed by DBA review) ───────────────────┐
│                                                                                      │
│  Apply DDL on RDS test instance per DBA approval                                     │
│  Phase-2 smoke-test SQL runs against each created table                              │
│  Reconcile any deltas from DBA review                                                │
│                                                                                      │
└────────────────────────────────────┬─────────────────────────────────────────────────┘
                                     ↓
┌──────────────────── PHASE 4 — B/E IMPL (parallel to keeping Excel running) ─────────┐
│                                                                                      │
│  bouracka_ui/dwh/ subpackage authored with OracleRepository                          │
│  workbook_io.py REPO-HOOK boundaries swap-in points exercised                        │
│  Dual-write phase: bouracka-ui writes both workbook AND Oracle                       │
│  Read-side cutover phase: bouracka-ui reads from Oracle, workbook becomes audit copy │
│  Eventually: Excel retired as primary; remains as DBA-snapshot CSV import           │
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

Phases 1-2 are immediate (this week / next week). Phase 3 is post-DBA review. Phase 4 is parallel work over weeks.

---

## §2. What's provisioned (SUPIN DBA confirmation 2026-05-13)

| Item | Value | Notes |
|------|-------|-------|
| Database instance | `RDS.INT-CKP.CZ` | RDS = Oracle's database product line (Real Application Cluster Database Service?), hosted at SUPIN. *Discovery script confirms exact version*. |
| Connect string TNS | `(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=172.16.1.104)(PORT=1521)))(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=rds.int-ckp.cz)))` | Save into `tnsnames.ora` or use EZCONNECT inline |
| EZCONNECT string | `TESTER@172.16.1.104:1521/rds.int-ckp.cz` | Useful for tools that bypass TNS |
| Schema owner | `TESTER` | Replaces the `BCKA_OWNER` placeholder in ERD v0.1 §2; tables created in TESTER schema with `BCKA_*` prefix for domain identification |
| Tablespace | `TESTER_DATA` | Dedicated; quota assumed UNLIMITED — discovery script confirms |
| Profile | `PRFL_TESTER` | Dedicated profile; password expiry / session limits per SUPIN policy — discovery script reads `DBA_PROFILES` to surface |
| Password | (separate channel) | Pete coordinates with SUPIN delivery via secure channel |
| Network reach | SUPIN-internal `172.16.1.0/24` | Pete's ThinkPad needs SUPIN VPN active to connect |

### §2.1 Granted privileges

| Grant | Need it for | ERD §reference |
|-------|-------------|----------------|
| `GRANT CONNECT TO TESTER` | session creation | basic |
| `GRANT CREATE TABLE TO TESTER` | `BCKA_*` tables + implicit `CREATE INDEX` on owned tables | §3-7 |
| `GRANT CREATE PROCEDURE TO TESTER` | PL/SQL procs / functions / packages | §10 v0.2 candidate |
| `GRANT CREATE VIEW TO TESTER` | computed `V_BCKA_*` views | §10 v0.2 candidate |
| `GRANT CREATE SEQUENCE TO TESTER` | per-table `BCKA_*_SEQ` for PK generation | §3-7 each table |
| `GRANT CREATE SYNONYM TO TESTER` | friendly aliases (optional) | future |
| `GRANT CREATE DATABASE LINK TO TESTER` | future MI-M-T B/E federation from Postgres | not in v0.1 |
| `GRANT CREATE JOB TO TESTER` | DBMS_SCHEDULER for batch coverage recompute, archive maintenance | future |
| `GRANT CREATE MATERIALIZED VIEW TO TESTER` | coverage-matrix performance + Cíl-4 partitioning prep | future |

### §2.2 Missing privileges (request via DBA follow-up)

| Missing grant | Need it for | Workaround if denied |
|---------------|-------------|----------------------|
| `CREATE TRIGGER` | ERD §8.2 audit-trigger pattern (CREATED_AT / UPDATED_AT / ROW_VERSION auto-bump) | **Option A**: application-layer audit (bouracka-ui sets timestamps explicitly on every INSERT/UPDATE). **Option B**: DBA enables Oracle Unified Audit (12c+) per-table — DBA-side, not user-side |
| `CREATE TYPE` (optional) | user-defined types (collections, objects) | Not used in v0.1 ERD; future-proofing only |

**Action:** Pete asks SUPIN DBA to add `CREATE TRIGGER` after discovery Phase 1 confirms tablespace quota + Oracle version. The reason to wait: bundling the two requests reduces DBA round-trips.

---

## §3. Discovery script catalogue (Phase 1 — Pete-runs-manually)

10 numbered scripts in `_db/discovery/`. Pete runs them sequentially using SQL Developer / sqlcl / DBeaver / DataGrip (any Oracle-aware client). Each script outputs human-readable + machine-parseable findings.

| # | Script | Duration | What it reveals |
|---|--------|----------|-----------------|
| 01 | `01_environment_smoke.sql` | ~1 s | Username, default tablespace, profile, db_name, server host, Oracle version banner |
| 02 | `02_privilege_inventory.sql` | ~1 s | All `USER_SYS_PRIVS` + `USER_ROLE_PRIVS` + `USER_TS_QUOTAS` — empirical confirmation of grants + tablespace quota |
| 03 | `03_features_inventory.sql` | ~2 s | `V$VERSION` + `V$OPTION` (where readable) — confirms JSON support, partitioning, advanced compression, etc. |
| 04 | `04_session_settings.sql` | ~1 s | NLS settings (`NLS_DATE_FORMAT`, `NLS_TIMESTAMP_TZ_FORMAT`, charset), session timezone, optimizer_features_enable |
| 05 | `05_quota_and_space.sql` | ~2 s | `DBA_TABLESPACES` (where readable) + `USER_TS_QUOTAS` + `USER_SEGMENTS` — current space usage, autoextend policy if visible |
| 06 | `06_proto_table_test.sql` | ~5 s | Creates `BCKA_PROBE_T` proto table + sequence + index; tests INSERT, SELECT, UPDATE with `ROW_VERSION` increment, DELETE, DROP. Surfaces any DDL / DML quirks |
| 07 | `07_json_feature_test.sql` | ~3 s | Creates a probe table with `CLOB CHECK (... IS JSON)` (12c+) and tests `JSON_VALUE` + `JSON_TABLE` queries. If Oracle 21c+ also tests native `JSON` type |
| 08 | `08_trigger_feature_test.sql` | ~2 s | Tests whether `CREATE TRIGGER` privilege is granted — attempts to create + drop a minimal trigger on the probe table. Surfaces clear pass/fail |
| 09 | `09_existing_objects.sql` | ~1 s | Inventories what already exists in the TESTER schema — `USER_OBJECTS` summary by type. Catches contamination from prior provisioning |
| 10 | `10_collect_findings.sql` | ~1 s | Aggregates findings from all prior scripts into a single SELECT that Pete pastes into `discovery-results-YYYY-MM-DD.md` |

**Master runbook**: `_db/discovery/00_master_runbook.md` walks Pete through the sequence + provides paste-back templates.

---

## §4. Mapping current Excel TestPlan + TES to DWH

The DWH B/E doesn't replace the workbook on day one. It mirrors then absorbs. Mapping per data-store-evolution plan §4:

```
                CURRENT (bouracka-ui v0.1.3)                            FUTURE (DWH B/E)
                ──────────────────────────                              ─────────────────

  Operator     →  workbook_io.list_envs(WORKBOOK_PATH)   ◄──REPO-HOOK──►  OracleRepository.list_envs()
  reads        →  workbook_io.list_tcs(...)              ◄──REPO-HOOK──►  OracleRepository.list_tcs()
                 workbook_io.list_bugs(...)              ◄──REPO-HOOK──►  OracleRepository.list_bugs()
                 workbook_io.get_bug(code)               ◄──REPO-HOOK──►  OracleRepository.get_bug(code)

  Operator     →  workbook_io.append_bug(...)            ◄──REPO-HOOK──►  OracleRepository.append_bug()
  writes       →  workbook_io.update_bug(code, fields)   ◄──REPO-HOOK──►  OracleRepository.update_bug()
                 workbook_io.set_bug_retest_run_id(...)  ◄──REPO-HOOK──►  OracleRepository.set_bug_retest_run_id()

  Test runs    →  consolidate_results.py writes envelope JSON           OracleRepository.ingest_envelope(envelope)
                  to runs/cross-framework-*.json                          → inserts into BCKA_TEST_RUNS
                                                                            with ENVELOPE_JSON column + denormalized
                                                                            summary fields per ERD §6

  Bug-retest   →  POST /api/bugs/{code}/retest                          (same — dispatcher unchanged;
  workflow        triggers dispatcher.run_async                           OracleRepository.set_bug_retest_run_id
                  sets last_retest_run_id on workbook                     just writes to BCKA_BUGS instead)

  Coverage     →  tools/coverage_audit.py reads workbook                OracleRepository.compute_coverage()
  view            generates info report                                   uses SQL over the TT lattice + TC×TT junction
                                                                          materialized view
```

The REPO-HOOK boundaries are the swap-in points. Per `BOURACKA-DATA-STORE-EVOLUTION-PLAN-v0.1-EN.md` §M2, current Bouračka discipline is to keep these boundaries CLEAN (no openpyxl imports leaking into server.py) so the future swap is mechanical.

---

## §5. Sequencing — what each phase produces

### Phase 1 — Discovery (this week, gated on password arrival)

| Day | Activity | Output |
|-----|----------|--------|
| D1 (T+0 from password) | Pete loads connect string in SQL client, runs scripts 01-05 (~10 min total) | `discovery-results-YYYY-MM-DD.md` Part A: environment + privileges + space + NLS |
| D1 | Pete runs scripts 06-09 (~15 min total) | Part B: feature flags (JSON, trigger, existing-objects) |
| D1 | Pete runs script 10 | Part C: consolidated findings |
| D1-D2 | Cowork consumes findings → drafts v0.2 ERD reality-grounded | `BOURACKA-ORACLE-ERD-v0.2-EN.md` |
| D2 | Pete asks DBA: CREATE TRIGGER grant (+ any other gaps surfaced by scripts) | DBA round-trip |

### Phase 2 — DDL draft (week of DBA review)

| Day | Activity | Output |
|-----|----------|--------|
| D3 | Cowork authors split SQL files per table | `_db/migrations/v0.1.0_initial_schema/`: 01_envs.sql, 02_targets.sql, 03_cases.sql, 04_runs.sql, 05_bugs.sql, 06_triggers.sql (or 06_app_audit_helpers.sql if trigger denied), 99_master.sql |
| D3 | Cowork authors per-table smoke SQL | `_db/test/v0.1.0_smoke/` parallel structure |
| D3-D4 | Pete reviews DDL, edits as needed | Pete-approved DDL |
| D4 | Pete sends to DBA for review | DBA round-trip |

### Phase 3 — DDL apply (post DBA approval)

| Day | Activity | Output |
|-----|----------|--------|
| D5+ | Pete applies DDL in dependency order on RDS test | TESTER schema populated with 5 tables + sequences + indexes |
| D5+ | Pete runs smoke SQL per table | Phase 3 confirmation log |
| D5+ | Cowork reconciles any DBA-revision deltas | ERD v0.2 → v0.2.1 if changes |

### Phase 4 — B/E impl (parallel; weeks-long)

| Phase | Activity | Output |
|-------|----------|--------|
| 4A | `bouracka_ui/dwh/` subpackage scaffold | `__init__.py`, `oracle_repository.py` stub, `oracle_connection.py` stub |
| 4B | First read path implemented: `list_envs()` from Oracle | OracleRepository reads BCKA_TEST_ENVIRONMENTS |
| 4C | Dual-write enabled: writes go to both workbook + Oracle | Bouračka-ui flag `BOURACKA_UI_DUAL_WRITE=true` |
| 4D | Read cutover: bouracka-ui reads from Oracle (workbook is fallback) | Flag `BOURACKA_UI_READ_FROM=oracle` |
| 4E | Excel retired as primary | Workbook snapshot is now read-only audit artefact |

Phases 4A-4E are weeks-long. Each is independently shippable; rollback is one flag flip.

---

## §6. Code hooks established now (parallel to discovery)

Per Pete's "hooks for development of B/E implementation" framing, the following minimal scaffold lands in `bouracka_ui/` without disturbing v0.1.3 behaviour:

1. `bouracka_ui/dwh/__init__.py` — empty subpackage; marks the boundary.
2. `bouracka_ui/dwh/oracle_repository.py` — stub module with the `IRepository` shape (interface comments only; no implementation).
3. `bouracka_ui/dwh/oracle_connection.py` — connection-management stub; reads `BOURACKA_UI_ORACLE_DSN` env var when set.
4. `bouracka_ui/workbook_io.py` — `# REPO-HOOK:` comments at every public function boundary.

The dwh subpackage carries **no executable code** for v0.1.3. It's marker territory: when Phase 4A starts, the implementer fills in these stubs. The advantage of having the markers now is that the bouracka-ui smoke tests + IDE auto-import already see the namespace; no big refactor when Oracle impl lands.

---

## §6a. Operational constraint — RDS in archive mode (redo-log awareness)

**Confirmed by SUPIN DBA 2026-05-13** (paraphrased from Czech original):

> "From the DB-privileges perspective for user TESTER — yes, can create and subsequently drop objects in own schema. Just please — RDS is primarily a reporting database, but still production, running in **archive mode**. So all DML operations naturally generate **redo logs**."

### §6a.1 What this means

- The RDS instance is **production-grade** in operational treatment despite its primary use being reporting. It runs `ARCHIVELOG` mode — every committed DML (`INSERT`/`UPDATE`/`DELETE`) produces redo entries that ship to archive logs.
- DBA-side this means our test activity ages off into long-term retention, contributes to backup volume, and is recoverable via PITR.
- For Bouračka DWH development this creates a **cost gradient** we should respect:

| Operation pattern | Redo impact | Mitigation |
|-------------------|-------------|------------|
| Discovery scripts 01-05 (read-only `SELECT`) | None | No constraint |
| Discovery scripts 06/07/08 (small CRUD + DROP) | Low | OK as-is; cleanup at end keeps footprint small |
| First ERD apply DDL (~5 tables) | Low (one-shot) | No special handling |
| Initial seed-load (small reference data — ENV / Targets / TCs) | Low | Per-table single INSERT batches; commit after each table |
| Run-envelope ingest (high-frequency writes once Phase 4 lands) | **MEDIUM-HIGH** | Pace ingest; consider batch sizes ≤ 1000 rows per commit; avoid intra-batch ROLLBACK |
| Dual-write Phase 4B-4C | **Doubles redo** during transition | Time-bound the dual-write window; cut over fast to read-from-Oracle only |
| Bulk reload / replay (archive backfill) | **HIGH** | Coordinate with DBA on maintenance window; consider DIRECT-PATH INSERT (`/*+ APPEND */`) for nologging-capable loads |
| Audit triggers (if/when CREATE TRIGGER granted) | Multiplier on every DML | Trigger PL/SQL stays minimal; no logging inside trigger body |

### §6a.2 Patterns to adopt

1. **Commit boundaries are deliberate.** Don't batch-commit larger than ~1000 rows; don't commit smaller than ~100 rows (excessive log-buffer pressure either way).
2. **No "DROP and recreate" for data tables in production-like flows.** TRUNCATE (if needed) is cheaper than DELETE + INSERT for bulk replace. Both still produce redo.
3. **DIRECT-PATH INSERT for one-shot loads.** `INSERT /*+ APPEND */ INTO BCKA_* SELECT ...` writes above the high-water mark and minimizes redo when the table is in NOLOGGING mode. NOLOGGING is a per-table attribute (`ALTER TABLE ... NOLOGGING`) — defer to DBA approval per table.
4. **Avoid trigger-side logging.** Audit triggers (when granted) populate columns only — no `DBMS_OUTPUT`, no log-table inserts, no remote calls. Each adds redo per fire.
5. **Dual-write phase has a clock.** Phases 4B (dual-write) → 4C (read cutover) → 4D (write cutover) compress to days, not weeks. The longer dual-write runs, the more redo.

### §6a.3 What we will NOT do

- Heavy load-testing on the RDS test instance without DBA coordination. Performance characterisation goes on a separate sandbox or against a snapshot.
- Bulk DELETE of entire tables for "reset" — TRUNCATE PARTITION or controlled per-row delete via PL/SQL with explicit commit boundaries.
- Long-running uncommitted transactions (e.g., interactive sessions left open with pending writes) — undo segment pressure + risk of ORA-01555.

### §6a.4 Operational acknowledgement

By treating RDS as a production database **in operational discipline** (even though we have schema-owner grants), we keep the relationship with the DBA team productive. DBA goodwill matters for the M6 / Phase 3 follow-up grants we still need (notably `CREATE TRIGGER`).

---

## §7. Risk catalogue

| ID | Risk | Severity | Mitigation |
|----|------|:---:|------------|
| R-DWH-1 | DBA denies `CREATE TRIGGER` grant | MEDIUM | Application-layer audit fallback (Option A in §2.2) — works for v0.1; loses defensive-against-app-bug property |
| R-DWH-2 | Oracle version is older than 12c — no JSON column support | MEDIUM-HIGH | Store envelope JSON as CLOB without `IS JSON` constraint; lose `JSON_TABLE` query path; query envelope tail in application layer instead |
| R-DWH-3 | Character set is not UTF-8 (e.g. WE8MSWIN1250 or AL16UTF16-AL32UTF8 misconfig) | MEDIUM | Czech NAME_CS fields may corrupt; verify in script 04 + apply NLS_LANG client-side workaround if needed |
| R-DWH-4 | Existing objects in TESTER schema cause naming collisions | LOW | Script 09 surfaces; Cowork renames `BCKA_*` prefixes or schema-qualifies if collision found |
| R-DWH-5 | Tablespace quota smaller than expected | LOW | Script 02 + 05 surface; DBA round-trip if quota inadequate |
| R-DWH-6 | Pete's ThinkPad SUPIN VPN access lapses | LOW-MEDIUM | Documentation maintained; discovery scripts re-runnable; VPN re-enable is SUPIN IT routine |
| R-DWH-7 | RDS instance has session-limit policy (PRFL_TESTER) that breaks SQL client | LOW | Script 01 reads profile; if `SESSIONS_PER_USER < 2` matters for SQL Developer multi-tab usage |
| R-DWH-8 | RDS upgrade window during apply phase | LOW | Pete schedules DDL outside DBA maintenance windows; coordinates with DBA on calendar |
| R-DWH-9 | bouracka-ui smoke-test 28/28 breaks when `dwh/` subpackage added | LOW | Subpackage carries no executable code in v0.1.3; just marker files. Smoke tests unaffected |
| R-DWH-10 | DBA review of v0.2 ERD finds structural issues requiring v0.3 redraw | LOW-MEDIUM | Phase 2 is explicitly draft + review; expect 1 revision cycle |

---

## §8. Open questions (v0.1 — Pete + SUPIN DBA)

| OQ | Question | Default |
|----|----------|---------|
| OQ-DWH-1 | Oracle version (12c / 19c / 21c / 23c)? | Discovery script 03 reveals |
| OQ-DWH-2 | Character set (UTF-8 expected)? | Script 04 reveals |
| OQ-DWH-3 | Tablespace quota policy (UNLIMITED vs specific size)? | Script 02 + 05 reveal |
| OQ-DWH-4 | Will DBA grant `CREATE TRIGGER`? | Pete asks after Phase 1 |
| OQ-DWH-5 | DDL apply ownership — Pete via direct DDL grants (current) or DBA-mediated? | Direct (Pete has grants); fallback to DBA-mediated if SUPIN policy demands |
| OQ-DWH-6 | Change-management — Liquibase / Flyway / hand-written DDL with versioned files? | Hand-written DDL in `_db/migrations/` per release; revisit when v0.2 stabilises |
| OQ-DWH-7 | Backup / PITR policy on RDS instance? | DBA-managed; Pete asks for recovery-point-objective spec |
| OQ-DWH-8 | Connection pooling — should bouracka-ui use cx_Oracle Pool or SQLAlchemy create_pool? | Decided at Phase 4A; default cx_Oracle session pool |
| OQ-DWH-9 | Multi-tester concurrent-read load expected? | LOW (~5 concurrent at peak) — informs profile sessions_per_user |
| OQ-DWH-10 | First DDL-apply window — coordinated with DBA on-call calendar | Pete coordinates after Phase 2 review |

---

## §9. v0.2 living-doc protocol

This plan bumps to v0.2 when:
- Phase 1 discovery results land (Pete pastes back script outputs)
- DBA returns review on Phase 2 DDL
- Any OQ-DWH-* resolves

Each bump folds discovery findings into a sharper plan. v0.2 is expected within ~7 days of password arrival.

---

End of v0.1.
