# MI-M-T data-store evolution — lessons brick

**Status.** Running notes — not a polished doc. Pete + Cowork append entries
as decisions land or operational experience surfaces patterns worth keeping.

**Purpose.** Capture data-store-evolution lessons learned during Bouračka's
pilot run, for re-use in MI-M-T core methodology and future MI-M-T project
spinoffs.

**Parent doc.** `bouracka-tests/_config/BOURACKA-DATA-STORE-EVOLUTION-PLAN-v0.1-EN.md` §M8.

**Format.** One entry per lesson. Lessons are dated, tagged by sub-domain,
and tied to the originating Bouračka decision when possible. Lessons graduate
to MI-M-T core methodology when Bouračka v1.0.0 ships.

---

## L-DSE-001 — Excel works at single-writer scale; breaks at N=2

**Date.** 2026-05-11 (initial observation), 2026-05-12 (codified).
**Tags.** scale-thresholds, single-writer, calibration.
**Triggered by.** KP review session — KP and Pete both touching v0.4.3.xlsx; coordination by hand-off, not by lock.
**Lesson.** Excel + openpyxl is sufficient when N=1 active writer and read-mostly testers. The moment N=2 simultaneous writers appears (e.g., Pete + Kate both filing bugs), the `WorkbookLockedError 409` becomes a real friction point, not just a defensive guard. Plan migration to multi-writer store BEFORE N=2 lands operationally.
**Pattern for MI-M-T.** Excel / JSON catalogue acceptable for pilot scope ≤ 1 writer. Document the writer-cardinality limit in the data-store choice doc up front so the trigger is unambiguous.

---

## L-DSE-002 — Document-shaped data wants document storage

**Date.** 2026-05-10 (v0.5.4 schema migration).
**Tags.** storage-shape, envelope-design.
**Triggered by.** `tools/consolidate_results.py` v0.5.4 — output pivoted from flat per-(fw × TC) rows to nested per-TC envelopes with `verdicts{}`, `evidence{}`, `error_messages{}` maps.
**Lesson.** Cross-framework result envelope was already document-shaped before we knew it'd land in Mongo (MI-M-T B/E dev store) or Oracle JSON (SUPIN production). Designing storage-agnostic from day one paid off: the same envelope shape ingests into all three (Excel cell-as-JSON-string, Mongo doc, Oracle JSON column) without reshape.
**Pattern for MI-M-T.** Run/result envelopes are document-natural; declare them so in the spec. Don't force them into flat relational tables.

---

## L-DSE-003 — Schema freeze before ERD work, not after

**Date.** 2026-05-12 (BOURACKA-DATA-STORE-EVOLUTION-PLAN v0.1 §M1).
**Tags.** schema-stability, ERD-prerequisites, migration-prep.
**Triggered by.** Phase-2 patcher schema mismatch — the patcher hardcoded column names from a mental model of v0.4.3 that didn't match the actual KP-reviewed schema. Caught at runtime, not at design time.
**Lesson.** ERD work depends on a stable workbook schema. If the workbook keeps gaining columns mid-ERD-design, the ERD invalidates. Freeze the workbook structure (column-level, not row-level) before drafting Oracle DDL.
**Pattern for MI-M-T.** When migrating from any "draft" data store to production RDBMS, freeze the draft schema first. Capture "no new sheets / no new columns" as an explicit moratorium tied to the migration milestone.

---

## L-DSE-004 — Abstraction-hooks beat premature IRepository

**Date.** 2026-05-12 (Pete's M2 revision).
**Tags.** abstraction-discipline, premature-design, MI-M-T-coordination.
**Triggered by.** Cowork's initial M2 proposal was a full IRepository refactor on Bouračka-side. Pete countered: MI-M-T B/E is the lead designer for the repository abstraction; Bouračka shouldn't invent its own and risk shaping wrong.
**Lesson.** When a pilot project is *one of many* under a methodology umbrella, the pilot should leave abstraction hooks visible but defer the full abstraction to the methodology layer. Otherwise the pilot's abstraction shape (e.g., openpyxl-flavored) leaks into the methodology and distorts later pilots.
**Pattern for MI-M-T.** Pilot projects ≠ methodology projects. Pilots use hooks; methodology defines the abstraction. The discipline boundary: pilot's `workbook_io.py` is a module-with-functions, not a class-with-interface, until the methodology says otherwise.

---

## L-DSE-005 — Oracle as production shadow of Postgres+Mongo dev stack

**Date.** 2026-05-12 (Pete's strategic statement).
**Tags.** dev-prod-divergence, SUPIN-institutional, multi-store.
**Triggered by.** Pete: *"structures would be deployed also on Oracle db shadowing PostgreSQL and Mongo used for developing MI-M-T B/E"*.
**Lesson.** When development happens on commodity stack (Postgres+Mongo) but production runs on institutional stack (Oracle), the abstraction layer in B/E code is what makes the dev/prod divergence tolerable. Code talks to "the data store"; the data store implementation is per-environment. Stored procedures, vendor-specific SQL, and other Oracle-flavored idioms STAY OUT of B/E code — they go in DDL files or migration scripts, not in repository implementations.
**Pattern for MI-M-T.** Multi-store-target pattern is normal. Repository abstractions plan for at least 2 target stores from day one (commodity dev + institutional prod). Same applies to document side (Mongo dev / Oracle JSON prod).

---

## L-DSE-006 — Reporting DBs in archive mode still cost redo per DML

**Date.** 2026-05-13.
**Tags.** production-discipline, redo-cost, dev-prod-asymmetry, RDS, archive-mode.
**Triggered by.** SUPIN DBA confirmation (in Czech) of TESTER schema grants — "from db-privilege perspective yes, can create and drop in own schema. Just please — RDS is primarily reporting, but still a production database running in archive mode. So all DML naturally generates redo logs."
**Lesson.** A "reporting" database in institutional context can still be production-grade in operational treatment. If it runs ARCHIVELOG (Oracle) or its equivalent (WAL archival in Postgres, replication oplog in Mongo), every DML the dev/test cycle generates ages into long-term retention, contributes to backup volume, and creates DBA-side pressure. Schema-owner grants do NOT translate into "free DML" — the developer's discipline matters.
**Pattern for MI-M-T.** Distinguish between **dev stores** (where DML is cheap; lots of DROP+CREATE+seed cycles are normal) and **prod-shadow stores** (where DML is metered). MI-M-T B/E patterns should encode this asymmetry:
- Dev (Postgres+Mongo on Pete's laptop): DROP+CREATE freely, no commit-boundary tuning, full data reset every test run is fine
- Prod-shadow (Oracle in SUPIN ARCHIVELOG): no DROP of populated tables, TRUNCATE/MERGE preferred over DELETE+INSERT, batch commit boundaries are deliberate (~1000 rows), DIRECT-PATH `/*+ APPEND */` for one-shot loads on NOLOGGING tables, no chatty audit triggers

Documentation pattern: every B/E module that does DML in prod-shadow context should carry a `# REDO-COST:` annotation indicating expected redo profile (low/medium/high) so reviewers can spot patterns that need attention.

---

## L-DSE-007 — TBD

(Append entries as Bouračka operational experience generates them.)

---

## Graduation criteria

Lessons graduate from this file to MI-M-T core methodology docs when:
- The lesson has been validated by at least one other MI-M-T pilot (Fourier-Foundations is the natural second).
- The pattern has been written up in `mimt-governance/` sibling repo (or wherever MI-M-T methodology docs live).
- Bouračka has shipped v1.0.0 — confirming the lesson survived the full pilot cycle.

Pre-graduation, lessons are advisory for MI-M-T contributors but not yet binding.

---

End of v0.1.
