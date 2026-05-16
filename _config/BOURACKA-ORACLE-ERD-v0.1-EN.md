# Bouračka Oracle ERD — v0.1 first portion (EN)

**Status.** First-portion draft per `_config/BOURACKA-DATA-STORE-EVOLUTION-PLAN-v0.1-EN.md` M4. Covers the 5 most-used workbook sheets translated to Oracle DDL with explicit column types, primary keys, foreign keys, indexes, and naming convention. Awaits SUPIN DBA review per M6.
**SUPIN reality update 2026-05-13:** schema provisioned as `TESTER` (not the notional `BCKA_OWNER` in §2 below); tablespace `TESTER_DATA`; profile `PRFL_TESTER`; 9 grants confirmed; **CREATE TRIGGER NOT granted** — flagged for follow-up per BOURACKA-DWH-DEV-PLAN §2.2. Connect string `RDS.INT-CKP.CZ` (172.16.1.104:1521). See `_config/BOURACKA-DWH-DEV-PLAN-v0.1-EN.md` §2 for full provisioning detail.
**Predecessor.** None.
**Sibling docs.**
- `_config/BOURACKA-DATA-STORE-EVOLUTION-PLAN-v0.1-EN.md` — overall migration plan
- `_specs/CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.md` — binding wire format that informs the run-result tables
- `BOURACKA-TESTPLAN-v0.4.3.xlsx` — source of truth being modelled
**Owner.** Pete Y.
**Authored.** 2026-05-13 (Block 3 of TES stabilisation push).
**Audience.** Pete; SUPIN DBA when contact is established; MI-M-T B/E architect for cross-pilot pattern import.

---

## §1. Scope of this first portion

**In scope (this v0.1 draft):**
- 5 highest-traffic workbook sheets translated to Oracle tables:
  - `01_TestTargets` → `BCKA_TEST_TARGETS`
  - `02_TestCases` → `BCKA_TEST_CASES`
  - `04_TestEnvironments` → `BCKA_TEST_ENVIRONMENTS`
  - `06_TestRuns` → `BCKA_TEST_RUNS` (+ JSON column for envelope tail)
  - `08_Bugs` → `BCKA_BUGS`
- Naming convention (`BCKA_*` prefix)
- Oracle type choices per column with rationale
- Primary keys, foreign keys, indexes, NOT NULL constraints
- Row-version column for optimistic concurrency (M7 of data-store plan)
- Audit columns (created_at, updated_at, created_by, updated_by)

**Deferred to v0.2+:**
- Remaining sheets (00b_Requirements, 01b_Req_FURPS_Cartesian, 01c_StateMachine, 02b-d sub-tables, 03_TestData, 05a-c plan/schedule/estimate, 07_TestRunResults, 09_Reports, 10_Glossary, 11_Changelog, 13_TestExecutionSummary, 14_AssertionGateResults, 01d_PrioritySevUrgMatrix)
- Computed views (00e_BranchView, 09_Reports aggregations)
- DDL change-management (Liquibase / Flyway-style migrations)
- Performance tuning (partitioning, materialised views)
- Auth + row-level security policies

---

## §2. Naming convention

| Convention | Pattern | Rationale |
|------------|---------|-----------|
| Tables | `BCKA_<DOMAIN>` (e.g. `BCKA_TEST_TARGETS`) | `BCKA_` prefix tags Bouračka domain; mandatory to avoid collision with other SUPIN schemas in the shared Oracle instance |
| Primary keys | `<TABLE>_ID` synthetic sequence-driven `NUMBER(19)` | Synthetic PK enables refactoring of business identifiers without breaking foreign keys; Oracle sequences via `BCKA_<TABLE>_SEQ.NEXTVAL` |
| Business identifiers | original Bouračka codes (e.g. `TT-CP-R1-A1`, `TC-CP-A1-MAIN-DEMO`, `BUG-NNN`) preserved as separate `<DOMAIN>_CODE VARCHAR2(64)` columns with UNIQUE constraints | Keeps the codes Pete + operators know in the natural-key column; surrogate PK is internal |
| Foreign keys | `FK_<TABLE>_<REFERENCED_TABLE>` (e.g. `FK_TEST_CASES_TEST_TARGETS`) | Standard Oracle naming; max 30 chars on legacy Oracle, 128 on 12c+; both fit |
| Sequences | `BCKA_<TABLE>_SEQ` | Per-table sequences avoid global lock contention |
| Indexes | `IX_<TABLE>_<COLUMN(S)>` (e.g. `IX_BUGS_STATUS`) | Standard convention; secondary lookup paths |
| Audit columns | `CREATED_AT`, `UPDATED_AT` (TIMESTAMP WITH TIME ZONE), `CREATED_BY`, `UPDATED_BY` (VARCHAR2(128)) | Consistent across all tables; trigger-populated to be defensive against application bugs |
| Row version | `ROW_VERSION NUMBER(10) NOT NULL DEFAULT 0` | Optimistic concurrency per M7 of data-store plan; bumped on every UPDATE via trigger |

---

## §3. `BCKA_TEST_TARGETS` (from `01_TestTargets`)

Workbook v0.4.3 has 28 rows in three buckets (R1 functional, R2 peripheral, Phase/cross-cutting) per `_specs/V-MODEL-TESTTARGET-DECOMPOSITION-v0.1.md` §2.2.

```sql
CREATE TABLE BCKA_TEST_TARGETS (
    -- Identity
    TEST_TARGET_ID          NUMBER(19)        NOT NULL,
    TT_CODE                 VARCHAR2(64)      NOT NULL,
    NAME_CS                 VARCHAR2(256),
    NAME_EN                 VARCHAR2(256),
    DESCR_CS                CLOB,
    DESCR_EN                CLOB,

    -- Classification (per TT attribute model — see TEST-ANALYSIS-AND-DESIGN-DEEP-SESSIONS-PLAN §3.3)
    V_MODEL_LEVEL           VARCHAR2(16),          -- L0-Business | L1-System | L2-Subsystem | L3-Component | L4-Unit
    DECOMPOSITION_KIND      VARCHAR2(32),          -- page | behavior | component | integration | regression | smoke | flow-segment | codelist | identifier
    ITEM_TYPE               VARCHAR2(32),          -- test_target | flow_segment | codelist | etc.

    -- Derivation
    REQUIREMENT_REF         VARCHAR2(256),         -- comma-separated REQ-* codes (denormalized; M:N via BCKA_TT_REQ junction in v0.2)
    SOURCE_ARTEFACTS        CLOB,                  -- free-text refs to recon screens, doc pages, ČKP analytical doc
    FURPS_DIMENSIONS        VARCHAR2(64),          -- comma-separated F,U,R,P,S,+D,+I,+N,+L,+P_phys
    DERIVATION_METHOD       VARCHAR2(32),          -- transposition | recon-derived | contract-derived | model-derived | regression-derived
    CONFIDENCE              VARCHAR2(8),           -- HIGH | MEDIUM | LOW
    LAST_VALIDATED_AT       DATE,

    -- Lifecycle
    ITEM_STATUS             VARCHAR2(16)      NOT NULL,  -- proposed | active | deprecated | retired
    SEVERITY                VARCHAR2(8),
    URGENCY                 VARCHAR2(8),
    PRIORITY                VARCHAR2(16),

    -- Governance
    OWNER_NAME              VARCHAR2(128),
    REVIEW_CADENCE          VARCHAR2(16),          -- weekly | sprint | release | ad-hoc
    CROSS_PILOT_EXPORT      NUMBER(1)         DEFAULT 0,  -- 0 = no, 1 = yes (MI-M-T export)

    -- Audit + concurrency
    CREATED_AT              TIMESTAMP WITH TIME ZONE NOT NULL,
    UPDATED_AT              TIMESTAMP WITH TIME ZONE NOT NULL,
    CREATED_BY              VARCHAR2(128),
    UPDATED_BY              VARCHAR2(128),
    ROW_VERSION             NUMBER(10)        NOT NULL DEFAULT 0,

    CONSTRAINT PK_TEST_TARGETS  PRIMARY KEY (TEST_TARGET_ID),
    CONSTRAINT UQ_TEST_TARGETS_CODE UNIQUE (TT_CODE),
    CONSTRAINT CHK_TT_STATUS    CHECK (ITEM_STATUS IN ('proposed','active','deprecated','retired')),
    CONSTRAINT CHK_TT_V_LEVEL   CHECK (V_MODEL_LEVEL IS NULL OR V_MODEL_LEVEL IN
        ('L0-Business','L1-System','L2-Subsystem','L3-Component','L4-Unit'))
);

CREATE SEQUENCE BCKA_TEST_TARGETS_SEQ START WITH 1000 INCREMENT BY 1 NOCACHE;

CREATE INDEX IX_TT_STATUS         ON BCKA_TEST_TARGETS (ITEM_STATUS);
CREATE INDEX IX_TT_V_MODEL        ON BCKA_TEST_TARGETS (V_MODEL_LEVEL);
CREATE INDEX IX_TT_DECOMPOSITION  ON BCKA_TEST_TARGETS (DECOMPOSITION_KIND);
CREATE INDEX IX_TT_PRIORITY       ON BCKA_TEST_TARGETS (PRIORITY);
```

**Notes for review:**
- `REQUIREMENT_REF` is denormalized (comma-separated) in v0.1 to match workbook shape. v0.2 introduces `BCKA_TT_REQ` M:N junction table — proper relational form.
- `FURPS_DIMENSIONS` likewise denormalized; v0.2 normalises into `BCKA_TT_FURPS` junction.
- `SOURCE_ARTEFACTS` as CLOB rather than separate `BCKA_TT_SOURCES` for v0.1 simplicity; v0.2 may normalise if querying source-artefact provenance becomes a use case.

---

## §4. `BCKA_TEST_CASES` (from `02_TestCases`)

Workbook v0.4.3 has 49 rows + KP review enrichment (`comments_KP_en`, `env`, `ext_ws` columns).

```sql
CREATE TABLE BCKA_TEST_CASES (
    -- Identity
    TEST_CASE_ID            NUMBER(19)        NOT NULL,
    TC_CODE                 VARCHAR2(64)      NOT NULL,
    NAME_CS                 VARCHAR2(256),
    NAME_EN                 VARCHAR2(256),
    DESCR_CS                CLOB,
    DESCR_EN                CLOB,

    -- Linkage to TestTarget (the primary one — M:N via BCKA_TC_TT in v0.2)
    PRIMARY_TT_ID           NUMBER(19),
    TEST_TARGET_REF         VARCHAR2(64),          -- TT-* code denormalized for fast filters

    -- Classification
    TYPE                    VARCHAR2(32),          -- E2E | FUNC | INTEGRATION | SMOKE | REGRESSION | CONTRACT
    ITEM_STATUS             VARCHAR2(16)      NOT NULL,  -- proposed | live | deprecated | retired
    SEVERITY                VARCHAR2(8),
    URGENCY                 VARCHAR2(8),
    PRIORITY                VARCHAR2(16),

    -- Execution shape
    ENV_COVERAGE            VARCHAR2(64),          -- comma-sep env codes (denorm; M:N junction in v0.2)
    VIEWPORT                VARCHAR2(16)      DEFAULT '375x667',
    FRAMEWORK_TARGETS       VARCHAR2(128),         -- comma-sep playwright,cypress,selenium

    -- Coverage hint flags (workbook-level)
    APPLIES_TO_DEMO         NUMBER(1)         DEFAULT 1,
    APPLIES_TO_PROD         NUMBER(1)         DEFAULT 0,

    -- KP review enrichment (v0.4.3) — preserved as columns to honour KP's text
    COMMENTS_KP_EN          CLOB,
    ENV_SHORTHAND           VARCHAR2(64),          -- 'STANDARD' | 'DEMO, STANDARD' | etc.
    EXT_WS                  VARCHAR2(128),         -- 'N8' | 'zenID' | 'AISPOV' | 'AISPOV-AB' | 'RÚIAN'

    -- Audit + concurrency
    CREATED_AT              TIMESTAMP WITH TIME ZONE NOT NULL,
    UPDATED_AT              TIMESTAMP WITH TIME ZONE NOT NULL,
    CREATED_BY              VARCHAR2(128),
    UPDATED_BY              VARCHAR2(128),
    ROW_VERSION             NUMBER(10)        NOT NULL DEFAULT 0,

    CONSTRAINT PK_TEST_CASES                    PRIMARY KEY (TEST_CASE_ID),
    CONSTRAINT UQ_TEST_CASES_CODE               UNIQUE (TC_CODE),
    CONSTRAINT FK_TEST_CASES_TEST_TARGETS       FOREIGN KEY (PRIMARY_TT_ID)
        REFERENCES BCKA_TEST_TARGETS (TEST_TARGET_ID),
    CONSTRAINT CHK_TC_STATUS                    CHECK (ITEM_STATUS IN ('proposed','live','deprecated','retired')),
    CONSTRAINT CHK_TC_BOOL_DEMO                 CHECK (APPLIES_TO_DEMO IN (0,1)),
    CONSTRAINT CHK_TC_BOOL_PROD                 CHECK (APPLIES_TO_PROD IN (0,1))
);

CREATE SEQUENCE BCKA_TEST_CASES_SEQ START WITH 1000 INCREMENT BY 1 NOCACHE;

CREATE INDEX IX_TC_STATUS         ON BCKA_TEST_CASES (ITEM_STATUS);
CREATE INDEX IX_TC_TT_REF         ON BCKA_TEST_CASES (TEST_TARGET_REF);
CREATE INDEX IX_TC_TYPE           ON BCKA_TEST_CASES (TYPE);
CREATE INDEX IX_TC_PRIORITY       ON BCKA_TEST_CASES (PRIORITY);
CREATE INDEX IX_TC_EXT_WS         ON BCKA_TEST_CASES (EXT_WS);
```

**Notes for review:**
- `PRIMARY_TT_ID` is the *primary* TT this TC covers. M:N junction (`BCKA_TC_TT_COVERAGE`) is v0.2 — necessary because per V-MODEL v0.1 §2.3 a TC can cover multiple TTs.
- `COMMENTS_KP_EN` as CLOB preserves KP's natural-language acceptance criteria (e.g. `SMS_CODE_ATTEMPTS`, `ERR_TOO_MANY_PHONE_NUMBER_OCCURRENCE`).
- `EXT_WS` indexed because TES dashboard filters by integration dependency.

---

## §5. `BCKA_TEST_ENVIRONMENTS` (from `04_TestEnvironments`)

Workbook v0.4.3 has 3 active envs (ENV-PUB, ENV-TST, ENV-DMO) plus supplemental ENV-DMO-PUB injected by bouracka-ui (v0.1.2 onward).

```sql
CREATE TABLE BCKA_TEST_ENVIRONMENTS (
    -- Identity
    TEST_ENV_ID             NUMBER(19)        NOT NULL,
    ENV_CODE                VARCHAR2(32)      NOT NULL,        -- ENV-PUB | ENV-TST | ENV-DMO | ENV-DMO-PUB | etc.
    NAME_CS                 VARCHAR2(128),
    NAME_EN                 VARCHAR2(128),
    DESCR_CS                CLOB,
    DESCR_EN                CLOB,

    -- Dispatch routing
    SCHEMA_ENV              VARCHAR2(32)      NOT NULL,        -- demo | tst-demo | tst | uat | prod-readonly | prod-writable
    BASE_URL                VARCHAR2(512)     NOT NULL,
    NETWORK_REACH           VARCHAR2(32),                       -- public | supin-internal
    LOCALE                  VARCHAR2(16)      DEFAULT 'cs_CZ',
    BROWSER_DEFAULT         VARCHAR2(32)      DEFAULT 'chromium',

    -- Anti-bot posture
    RECAPTCHA_POSTURE       VARCHAR2(64),                       -- FULL | BYPASS_TOKEN | BYPASS_TOKEN_OR_DISABLED | live | test-keys
    RECAPTCHA_BYPASS_TOKEN  VARCHAR2(512),                      -- secret; v0.2 moves to vault reference

    -- Integration sub-routing (per-env URLs for N8 / AISPOV / zenID / RÚIAN)
    -- v0.1: denormalized JSON. v0.2: separate BCKA_ENV_INTEGRATIONS table.
    INTEGRATION_ENDPOINTS   CLOB,                               -- JSON: {"n8":"https://...","aispov":"https://..."}

    -- Lifecycle
    ITEM_STATUS             VARCHAR2(16)      NOT NULL,
    NOTES                   CLOB,

    -- Audit + concurrency
    CREATED_AT              TIMESTAMP WITH TIME ZONE NOT NULL,
    UPDATED_AT              TIMESTAMP WITH TIME ZONE NOT NULL,
    CREATED_BY              VARCHAR2(128),
    UPDATED_BY              VARCHAR2(128),
    ROW_VERSION             NUMBER(10)        NOT NULL DEFAULT 0,

    CONSTRAINT PK_TEST_ENVS          PRIMARY KEY (TEST_ENV_ID),
    CONSTRAINT UQ_TEST_ENVS_CODE     UNIQUE (ENV_CODE),
    CONSTRAINT CHK_TENV_SCHEMA_ENV   CHECK (SCHEMA_ENV IN
        ('demo','tst-demo','tst','uat','prod-readonly','prod-writable')),
    CONSTRAINT CHK_TENV_STATUS       CHECK (ITEM_STATUS IN ('proposed','live','deprecated','retired'))
);

CREATE SEQUENCE BCKA_TEST_ENVS_SEQ START WITH 1000 INCREMENT BY 1 NOCACHE;

CREATE INDEX IX_TENV_STATUS         ON BCKA_TEST_ENVIRONMENTS (ITEM_STATUS);
CREATE INDEX IX_TENV_SCHEMA_ENV     ON BCKA_TEST_ENVIRONMENTS (SCHEMA_ENV);
```

**Notes for review:**
- `RECAPTCHA_BYPASS_TOKEN` carries a secret in v0.1; **before production deploy** this must move to Oracle Wallet / vault and the column becomes a vault reference. Flagged for SUPIN SecOps review.
- `INTEGRATION_ENDPOINTS` JSON column requires Oracle 12c+ for native JSON; 19c+ for `JSON_VALUE` / `JSON_TABLE` SQL access. Confirm SUPIN Oracle version.
- ENV_CODE prefix `ENV-` retained to match the workbook + bouracka-ui codes Pete and Kate already use.

---

## §6. `BCKA_TEST_RUNS` (from `06_TestRuns` + cross-framework envelope)

This is the heaviest table — relational columns for queryable fields + JSON column for the full v0.1 envelope tail (per data-store plan §M3).

```sql
CREATE TABLE BCKA_TEST_RUNS (
    -- Identity
    TEST_RUN_ID             NUMBER(19)        NOT NULL,
    RUN_ID                  VARCHAR2(64)      NOT NULL,        -- run-YYYY-MM-DDTHH-MM-SSZ-xxxxxxx
    SCHEMA_VERSION          VARCHAR2(16)      NOT NULL,        -- '1.0' per cross-framework-result-schema v0.1

    -- Time boundaries
    STARTED_AT              TIMESTAMP WITH TIME ZONE NOT NULL,
    ENDED_AT                TIMESTAMP WITH TIME ZONE NOT NULL,
    DURATION_MS             NUMBER(10),

    -- Env + frameworks
    TEST_ENV_ID             NUMBER(19),                          -- FK
    SCHEMA_ENV              VARCHAR2(32)      NOT NULL,          -- denormalized for fast filter
    ENV_URL                 VARCHAR2(512),
    FRAMEWORKS              VARCHAR2(128)     NOT NULL,          -- comma-sep alphabetical

    -- Summary (computed; denormalized for fast list-view rendering)
    TOTAL_TCS               NUMBER(10)        DEFAULT 0,
    PASSED                  NUMBER(10)        DEFAULT 0,
    FAILED                  NUMBER(10)        DEFAULT 0,
    SKIPPED                 NUMBER(10)        DEFAULT 0,
    SOFT_PASSED             NUMBER(10)        DEFAULT 0,
    DRIFT_SKIP_COUNT        NUMBER(10)        DEFAULT 0,
    PARITY_PASS_COUNT       NUMBER(10)        DEFAULT 0,
    PARITY_DIVERGENCE_COUNT NUMBER(10)        DEFAULT 0,
    PASS_RATE_STRICT        NUMBER(5, 2),                        -- 0.00 to 1.00; null when total_tcs=0
    PASS_RATE_DRIFT_AWARE   NUMBER(5, 2),

    -- Host + reporter (denormalized; full host details in envelope JSON)
    HOST_OS                 VARCHAR2(64),
    HOST_NAME               VARCHAR2(128),
    GIT_COMMIT              VARCHAR2(40),
    GIT_BRANCH              VARCHAR2(128),
    REPORTER_COMMAND        CLOB,
    REPORTER_TRIGGER        VARCHAR2(16),                        -- manual | ci | scheduled | api
    CI_RUN_ID               VARCHAR2(64),
    OPERATOR                VARCHAR2(128),

    -- Drift forensic (queryable bits; full detail in envelope JSON)
    DRIFT_ACTIVE            NUMBER(1)         DEFAULT 0,
    DRIFT_TYPE              VARCHAR2(64),                        -- recaptcha-v3 | ipc-114-renderer-kill | etc.
    DRIFT_AFFECTED_COUNT    NUMBER(10),

    -- Full envelope tail (v0.1 schema) — per data-store-plan §M3
    -- Includes results[], evidence, error_messages, framework_specific_notes,
    -- tool_versions, parse_warnings.
    ENVELOPE_JSON           CLOB                CHECK (ENVELOPE_JSON IS JSON),

    -- Retest provenance — links this run to a bug if it was launched as retest
    RETEST_OF_BUG_ID        NUMBER(19),                          -- nullable FK to BCKA_BUGS

    -- Audit + concurrency
    CREATED_AT              TIMESTAMP WITH TIME ZONE NOT NULL,
    UPDATED_AT              TIMESTAMP WITH TIME ZONE NOT NULL,
    ROW_VERSION             NUMBER(10)        NOT NULL DEFAULT 0,

    CONSTRAINT PK_TEST_RUNS            PRIMARY KEY (TEST_RUN_ID),
    CONSTRAINT UQ_TEST_RUNS_RUN_ID     UNIQUE (RUN_ID),
    CONSTRAINT FK_RUNS_ENV             FOREIGN KEY (TEST_ENV_ID)
        REFERENCES BCKA_TEST_ENVIRONMENTS (TEST_ENV_ID),
    CONSTRAINT CHK_RUNS_SCHEMA_ENV     CHECK (SCHEMA_ENV IN
        ('demo','tst-demo','tst','uat','prod-readonly','prod-writable')),
    CONSTRAINT CHK_RUNS_TRIGGER        CHECK (REPORTER_TRIGGER IS NULL OR REPORTER_TRIGGER IN
        ('manual','ci','scheduled','api')),
    CONSTRAINT CHK_RUNS_DRIFT_ACTIVE   CHECK (DRIFT_ACTIVE IN (0,1)),
    CONSTRAINT CHK_RUNS_TIME_ORDER     CHECK (STARTED_AT <= ENDED_AT)
);

CREATE SEQUENCE BCKA_TEST_RUNS_SEQ START WITH 100000 INCREMENT BY 1 NOCACHE;

CREATE INDEX IX_RUNS_STARTED          ON BCKA_TEST_RUNS (STARTED_AT DESC);
CREATE INDEX IX_RUNS_SCHEMA_ENV       ON BCKA_TEST_RUNS (SCHEMA_ENV);
CREATE INDEX IX_RUNS_TRIGGER          ON BCKA_TEST_RUNS (REPORTER_TRIGGER);
CREATE INDEX IX_RUNS_DRIFT_TYPE       ON BCKA_TEST_RUNS (DRIFT_TYPE)
    WHERE DRIFT_ACTIVE = 1;          -- partial index (Oracle 12c+)
CREATE INDEX IX_RUNS_RETEST_BUG       ON BCKA_TEST_RUNS (RETEST_OF_BUG_ID)
    WHERE RETEST_OF_BUG_ID IS NOT NULL;
```

**Notes for review:**
- `ENVELOPE_JSON` `IS JSON` check requires Oracle 12c+. With 21c+ the column can be `JSON` native type; for 19c use CLOB+IS JSON.
- Summary metrics duplicated as flat columns — denormalized vs the envelope's `summary{}` block. Trade-off: writes are slightly more expensive (one extract per metric); reads are fast (no JSON parsing for list views).
- `RETEST_OF_BUG_ID` enables querying "all retests of bug BUG-NNN" efficiently. v0.1.3 bouracka-ui adds the corresponding `last_retest_run_id` column on the bugs side (Block 2).

---

## §7. `BCKA_BUGS` (from `08_Bugs`)

Per Block 2 work in this same session, the bugs schema gains a `LAST_RETEST_RUN_ID` column linking back to `BCKA_TEST_RUNS`.

```sql
CREATE TABLE BCKA_BUGS (
    -- Identity
    BUG_ID                  NUMBER(19)        NOT NULL,
    BUG_CODE                VARCHAR2(32)      NOT NULL,        -- BUG-NNN
    NAME_CS                 VARCHAR2(256),
    NAME_EN                 VARCHAR2(256),
    DESCR_CS                CLOB,
    DESCR_EN                CLOB,
    ITEM_TYPE               VARCHAR2(16)      DEFAULT 'bug',    -- bug | suggestion | issue

    -- Workflow status
    BUG_STATUS              VARCHAR2(32)      NOT NULL,        -- open | investigating | fixed | verified-fixed | reopened | closed | wontfix
    SEVERITY                VARCHAR2(8),                        -- A | B | C | X
    URGENCY                 VARCHAR2(8),
    PRIORITY                VARCHAR2(16),

    -- Submission
    SUBMITTER               VARCHAR2(128),
    SUBMITTED_AT            TIMESTAMP WITH TIME ZONE,

    -- Context
    ENV_WHERE_PRESENT       VARCHAR2(32),                        -- workbook ENV-* code
    LINKED_TC_ID            NUMBER(19),                          -- FK to test cases (resolved at write time)
    LINKED_TC_REF           VARCHAR2(64),                        -- denormalized TC code for fast filter
    LINKED_RUN_RESULT_REF   VARCHAR2(256),                       -- free-form ref to run+TC tuple
    REPRO_STEPS             CLOB,
    EXPECTED                CLOB,
    ACTUAL                  CLOB,

    -- Retest provenance (Block 2 of v0.1.3)
    LAST_RETEST_RUN_ID      NUMBER(19),                          -- FK to BCKA_TEST_RUNS

    -- Evidence
    SCREENSHOT_REF          VARCHAR2(512),
    TRACE_REF               VARCHAR2(512),
    ERROR_MESSAGE           CLOB,

    -- Audit + concurrency
    CREATED_AT              TIMESTAMP WITH TIME ZONE NOT NULL,
    UPDATED_AT              TIMESTAMP WITH TIME ZONE NOT NULL,
    CREATED_BY              VARCHAR2(128),
    UPDATED_BY              VARCHAR2(128),
    ROW_VERSION             NUMBER(10)        NOT NULL DEFAULT 0,

    CONSTRAINT PK_BUGS                  PRIMARY KEY (BUG_ID),
    CONSTRAINT UQ_BUGS_CODE             UNIQUE (BUG_CODE),
    CONSTRAINT FK_BUGS_TC               FOREIGN KEY (LINKED_TC_ID)
        REFERENCES BCKA_TEST_CASES (TEST_CASE_ID),
    CONSTRAINT FK_BUGS_RETEST_RUN       FOREIGN KEY (LAST_RETEST_RUN_ID)
        REFERENCES BCKA_TEST_RUNS (TEST_RUN_ID),
    CONSTRAINT CHK_BUGS_STATUS          CHECK (BUG_STATUS IN
        ('open','investigating','fixed','verified-fixed','reopened','closed','wontfix')),
    CONSTRAINT CHK_BUGS_SEVERITY        CHECK (SEVERITY IS NULL OR SEVERITY IN ('A','B','C','X'))
);

CREATE SEQUENCE BCKA_BUGS_SEQ START WITH 1000 INCREMENT BY 1 NOCACHE;

CREATE INDEX IX_BUGS_STATUS         ON BCKA_BUGS (BUG_STATUS);
CREATE INDEX IX_BUGS_SEVERITY       ON BCKA_BUGS (SEVERITY);
CREATE INDEX IX_BUGS_ENV            ON BCKA_BUGS (ENV_WHERE_PRESENT);
CREATE INDEX IX_BUGS_TC_REF         ON BCKA_BUGS (LINKED_TC_REF);
CREATE INDEX IX_BUGS_TC_ID          ON BCKA_BUGS (LINKED_TC_ID);
CREATE INDEX IX_BUGS_RETEST_RUN     ON BCKA_BUGS (LAST_RETEST_RUN_ID)
    WHERE LAST_RETEST_RUN_ID IS NOT NULL;
```

**Notes for review:**
- `BUG_STATUS` enum lifted from bouracka-ui's edit form (v0.1.3 Block 2): adds `verified-fixed`, `reopened`, `wontfix` beyond the original open/investigating/fixed/closed. Schema check constraint enforces.
- `LINKED_TC_ID` (surrogate FK) + `LINKED_TC_REF` (natural-key denormalized) coexist — typical pattern when migrating from natural-key-only sources.

---

## §8. Cross-cutting concerns

### §8.1 Optimistic concurrency

Every table carries `ROW_VERSION NUMBER(10) NOT NULL DEFAULT 0`. Update statements must include:

```sql
UPDATE BCKA_BUGS
SET BUG_STATUS = :new_status,
    UPDATED_AT = SYSTIMESTAMP,
    UPDATED_BY = :user,
    ROW_VERSION = ROW_VERSION + 1
WHERE BUG_ID = :id
  AND ROW_VERSION = :expected_version;

-- If 0 rows affected: another writer beat us; return 409 Conflict.
```

Application layer (bouracka-ui in `update_bug()`) must:
- Read current `ROW_VERSION` at edit-form load
- Pass it as `expected_version` on PUT
- Translate `0 rows affected` to HTTP 409 with current state for operator to merge

This matches the existing `WorkbookLockedError` 409 behavior — same UX, different mechanism.

### §8.2 Audit triggers

```sql
CREATE OR REPLACE TRIGGER TR_BUGS_AUDIT
BEFORE INSERT OR UPDATE ON BCKA_BUGS
FOR EACH ROW
BEGIN
    IF INSERTING THEN
        :NEW.CREATED_AT := SYSTIMESTAMP;
        :NEW.UPDATED_AT := SYSTIMESTAMP;
        :NEW.ROW_VERSION := 0;
        IF :NEW.BUG_ID IS NULL THEN
            :NEW.BUG_ID := BCKA_BUGS_SEQ.NEXTVAL;
        END IF;
    ELSIF UPDATING THEN
        :NEW.UPDATED_AT := SYSTIMESTAMP;
        :NEW.CREATED_AT := :OLD.CREATED_AT;  -- defensive
        -- ROW_VERSION is bumped by the application's optimistic-concurrency UPDATE
        -- so we don't auto-increment here.
    END IF;
END;
/
```

Equivalent triggers per table. Application code never sets CREATED_AT / UPDATED_AT directly — the trigger is the source of truth.

### §8.3 Performance characteristics

| Table | Expected size at Cíl-4 | Growth rate | Hot indexes |
|-------|------------------------|-------------|-------------|
| BCKA_TEST_TARGETS | ~50-200 rows | static (slow growth) | UQ_TT_CODE |
| BCKA_TEST_CASES | ~100-500 rows | static (slow growth) | UQ_TC_CODE, IX_TC_TT_REF |
| BCKA_TEST_ENVIRONMENTS | ~5-10 rows | static | UQ_ENV_CODE |
| BCKA_TEST_RUNS | 10-100 rows/day = 3,600-36,000/yr | linear with test activity | IX_RUNS_STARTED |
| BCKA_BUGS | 100-2,000 rows total lifetime | bursty | IX_BUGS_STATUS, UQ_BUG_CODE |

`BCKA_TEST_RUNS` is the only table needing partitioning consideration before Cíl-4. Recommend RANGE partitioning by `STARTED_AT` (monthly partitions) once it exceeds ~50,000 rows.

### §8.4 JSON column considerations

`ENVELOPE_JSON` on `BCKA_TEST_RUNS` and `INTEGRATION_ENDPOINTS` on `BCKA_TEST_ENVIRONMENTS` are the two JSON columns in this first portion.

Oracle JSON access patterns expected:
```sql
-- "show me runs where playwright found a divergence on TC-CP-A1-MAIN-DEMO"
SELECT RUN_ID
FROM BCKA_TEST_RUNS,
     JSON_TABLE(ENVELOPE_JSON, '$.results[*]'
         COLUMNS (
             TC_CODE   VARCHAR2(64)   PATH '$.tc_code',
             PARITY    VARCHAR2(32)   PATH '$.parity_status',
             PW_VERD   VARCHAR2(16)   PATH '$.verdicts.playwright'
         )
     ) r
WHERE r.TC_CODE = 'TC-CP-A1-MAIN-DEMO'
  AND r.PARITY = 'divergence'
  AND r.PW_VERD = 'fail';
```

This requires Oracle 12c+. Confirm SUPIN Oracle version per data-store plan §M6.

---

## §9. Open questions for SUPIN DBA (M6 conversations)

| OQ | Question | Default if no answer |
|----|----------|----------------------|
| OQ-ERD-1 | Oracle version + JSON support level (19c IS JSON CLOB vs 21c native JSON) | Assume 19c; codify JSON columns as CLOB+IS JSON check |
| OQ-ERD-2 | Schema-naming preference — `BCKA_*` proposal vs SUPIN convention | Use `BCKA_*` pending DBA pushback |
| OQ-ERD-3 | DDL change-management — Liquibase / Flyway / hand-written DDL files? | Hand-written DDL files in `_db/migrations/` per release tag; reconsider at v1.0 |
| OQ-ERD-4 | Sequence cache size — NOCACHE proposed; OK or override? | NOCACHE for v0.1 (deterministic IDs, no gap on rollback); revisit if bulk-insert perf demands |
| OQ-ERD-5 | Audit trigger pattern — is BEFORE INSERT/UPDATE row-level acceptable, or does SUPIN prefer a separate audit-log table? | Row-level triggers as drafted; separate `BCKA_AUDIT_LOG` is v0.2 candidate |
| OQ-ERD-6 | Tablespace / segment policy — should `BCKA_*` tables live in a dedicated tablespace? | Yes, dedicated `BCKA_DATA` tablespace + `BCKA_IDX` for indexes (DBA names per SUPIN convention) |
| OQ-ERD-7 | RECAPTCHA_BYPASS_TOKEN as plaintext column vs Oracle Wallet reference | v0.1 plaintext (dev/test only); production cutover MUST move to wallet/vault — block v1.0 ship without DBA SecOps sign-off |
| OQ-ERD-8 | Schema owner account naming + grant model — who runs the DDL? | **RESOLVED 2026-05-13:** schema owner is `TESTER` (SUPIN-provisioned). Pete runs DDL directly via the 9 explicit grants. App account separation deferred until multi-user phase (Phase 4 of DWH dev plan) |
| OQ-ERD-9 | CREATE TRIGGER grant — needed for §8.2 audit-trigger pattern | **PENDING DBA:** not in initial grant list (2026-05-13). Pete to request via DBA follow-up after Phase 1 discovery confirms. Fallback per DWH-DEV-PLAN §2.2: application-layer audit (Option A) |
| OQ-ERD-10 | Schema-name impact on `BCKA_*` table prefix policy | Keep `BCKA_*` prefix even within TESTER schema — tags Bouračka domain; future-proofs if TESTER schema later hosts TES presentation tables or MI-M-T objects |

---

## §10. v0.2 roadmap (deferred to next ERD pass)

Tables to add:
- `BCKA_REQUIREMENTS` (00b_Requirements)
- `BCKA_REQ_FURPS` (junction for 01b_Req_FURPS_Cartesian)
- `BCKA_STATE_MACHINE` (01c_StateMachine)
- `BCKA_TC_PARAMETERS` (02b)
- `BCKA_TC_ASSERTIONS` (02c) + `BCKA_ASSERTION_LIBRARY` (02d)
- `BCKA_TEST_DATA` (03)
- `BCKA_TEST_PLAN` + `BCKA_TEST_SCHEDULE` + `BCKA_TEST_ESTIMATE` (05a/b/c)
- `BCKA_TEST_RUN_RESULTS` (07) — per-TC normalized result rows (companion to the envelope JSON on BCKA_TEST_RUNS)
- `BCKA_GLOSSARY` (10)
- `BCKA_TEST_EXECUTION_SUMMARY` (13)
- `BCKA_ASSERTION_GATE_RESULTS` (14)
- `BCKA_PRIORITY_MATRIX` (01d)

Junction tables for M:N relationships:
- `BCKA_TT_REQ` — TestTargets ↔ Requirements
- `BCKA_TT_FURPS` — TestTargets ↔ FURPS+ dimensions
- `BCKA_TC_TT_COVERAGE` — TestCases ↔ TestTargets (M:N per V-MODEL v0.1 §2.3)
- `BCKA_TC_FRAMEWORK` — TestCases ↔ frameworks
- `BCKA_TC_ENV` — TestCases ↔ Environments (env_coverage)

Computed views:
- `V_BCKA_BRANCH_VIEW` (00e_BranchView)
- `V_BCKA_REPORTS_*` (09_Reports aggregations)
- `V_BCKA_COVERAGE_MATRIX` (live coverage_rule_phase status per TT × FURPS+ cell)

---

## §11. Living-doc protocol

v0.2 bumps when:
- SUPIN DBA review returns with required changes
- Block-3 review reveals corrections in v0.1
- Remaining sheets (per §10) are translated
- Concurrency model is updated (e.g., switch from optimistic to hybrid)

---

End of v0.1 first portion. Awaits SUPIN DBA review + Block 4 (deep session) feedback on TT attribute model alignment.
