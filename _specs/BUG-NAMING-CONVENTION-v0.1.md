# Bug Naming Convention — v0.1

> **Trigger.** CP-SUPIN-04 STEP 23 (2026-05-06): user reported test
> failures produce duplicate bug entities. Root cause: bug ID was a
> sequential counter (BUG-CP-001, -002, ...) without dedup key, so
> the same defect failing across retries / envs / days created N rows.
>
> **Cíl.** Deterministic key formula → 1 unique defect = 1 row;
> subsequent observations bump counters, never create new rows.

---

## §1. Naming convention

### §1.1 Bug ID — deterministic dedup key

Format:

```
BUG-CP-{TC_CODE}-{ASSERT_CODE}
```

Where:
- `TC_CODE` — TestCase that surfaced the defect (e.g. `001`, `NEW-A`, `005-PROD`)
- `ASSERT_CODE` — short stable code identifying which assertion failed within the TC
  - Format: `S{N}` where N is the step number from the TC SPEC (`S3`, `S5`, `S10`)
  - OR a 6-character hash of the failing locator/expression for assertions without a clear step-number anchor

Examples:

| Bug ID | Co znamená |
|--------|------------|
| `BUG-CP-001-S4` | TC-CP-001 step 4 (CTA visible) failed |
| `BUG-CP-NEW-A-S1` | TC-CP-NEW-A step 1 (rozcestník H1) failed |
| `BUG-CP-005-PROD-S7` | TC-CP-005 PROD variant step 7 (verify OTP) failed |
| `BUG-CP-003-A1B2C3` | TC-CP-003 assertion with hash A1B2C3 (no step number) |

**Rules:**
1. ID is deterministic — same TC + same assertion → same ID, every time
2. Capital letters; underscores allowed in TC_CODE; no spaces
3. ID is the **primary key** of the row in `08_Bugs`
4. Re-running the same failing test → finds existing row by ID → updates counters; does NOT create new row

### §1.2 Required columns on `08_Bugs` sheet

In addition to standard ItemBase columns:

| Column | Type | Purpose |
|--------|------|---------|
| `item_code` | TEXT | the BUG-CP-{TC_CODE}-{ASSERT_CODE} ID (PK) |
| `tc_ref` | TEXT | TC that surfaced this bug (e.g. `TC-CP-001`) — denormalised for easy filtering |
| `assertion_code` | TEXT | the assert anchor (e.g. `S4` or `A1B2C3`) |
| `assertion_text` | TEXT | the failing expression / message verbatim |
| `first_seen` | DATE | first time this bug was observed |
| `last_seen` | DATE | most recent observation |
| `occurrences` | INT | total count of failures with this signature |
| `envs_seen` | TEXT | comma-list of env_constraints where it fired (e.g. `demo-public,prod-tst`) |
| `runs_seen` | TEXT | comma-list of last 10 RUN-* IDs that hit this bug |
| `screenshot_ref` | TEXT | path to most-recent test-failed-1.png |
| `trace_ref` | TEXT | path to most-recent trace.zip |
| `error_message` | TEXT | most-recent verbatim error (replaces previous on update) |
| `status` | ENUM | `open` / `triaged` / `in_progress` / `resolved` / `wont_fix` / `flake` |

### §1.3 Severity / Urgency / Priority

Standard ItemBase columns (per `01d_PrioritySevUrgMatrix`):
- `severity` — set by reporter based on user-facing impact
- `urgency` — set by reporter based on business deadline
- `priority` — STATIC computed value from MATRIX[(severity, urgency)]

(Same matrix as TC priorities — see CP-SUPIN-04 STEP 17.)

## §2. Update logic — append vs upsert

### §2.1 Pseudocode

```
on test failure (tc_code, assert_code, run_id, env, error_msg, screenshot, trace):
    bug_id = f"BUG-CP-{tc_code}-{assert_code}"
    if bug_id in 08_Bugs:
        # UPDATE — never duplicate
        row.last_seen = today()
        row.occurrences += 1
        row.runs_seen = (last 10 of: row.runs_seen ∪ {run_id})
        row.envs_seen = sorted(set(row.envs_seen.split(',') + [env]))
        row.screenshot_ref = screenshot   # latest
        row.trace_ref = trace             # latest
        row.error_message = error_msg     # latest verbatim
        row.status = "open" if row.status not in {"resolved","wont_fix","flake"} else row.status
        # Note: do NOT auto-reopen "resolved" — flag for triage instead
    else:
        # INSERT new row
        row = new BugRow(
            item_code = bug_id,
            tc_ref = tc_code,
            assertion_code = assert_code,
            assertion_text = "",   # filled at TC author time
            first_seen = today(),
            last_seen = today(),
            occurrences = 1,
            envs_seen = env,
            runs_seen = run_id,
            screenshot_ref = screenshot,
            trace_ref = trace,
            error_message = error_msg,
            severity = "C",   # default; reporter triages
            urgency = "C",
            status = "open",
        )
        append row to 08_Bugs
```

### §2.2 Implementation hooks

| Tool | Volání | Co dělá |
|------|--------|---------|
| `tools/test_console.py` | po každém běhu Playwright/Cypress/TestCafe | parse JSON results → upsert do 08_Bugs |
| `tools/check_priority_matrix.py` | rozšířeno: validuje BUG-* IDs proti naming pattern | exit non-zero pri ne-conformantní ID |
| `playwright/reporters/excel-row-writer.ts` | reporter Playwright after-each | volá Python upsert helper |

(Detailní implementace v CP-SUPIN-05.)

## §3. Co NESMÍ vytvořit duplikátu

| Scenario | Pre-rev | Post-rev |
|----------|---------|----------|
| Test fails 2x (retry+1) v 1 runu | 2 řádky BUG-CP-NNN, BUG-CP-NNN+1 | 1 řádek; occurrences=2 |
| Test fails 1x na DEMO + 1x na PROD | 2 řádky | 1 řádek; envs_seen="demo-public,prod" |
| Test fails 5 dní za sebou | 5 řádků | 1 řádek; first_seen=Day1, last_seen=Day5, occurrences=5+ |
| Stejný test fail po release (resolved → reopened) | nový řádek | existující řádek; status flagged for triage; manuální posun back to "open" |

## §4. Edge cases

### §4.1 Test má více assertions, fails více než jedna

Naming: každá assertion má svůj `S{N}` kód → samostatný BUG-* row.

Příklad: TC-CP-NEW-A má step 1 (rozcestník copy) + step 5 (CTA visible).
Pokud oba selžou:
- `BUG-CP-NEW-A-S1` (copy)
- `BUG-CP-NEW-A-S5` (CTA)

Dva nezávislé bugy. Triage rozhodne, zda jsou root-cause same nebo different.

### §4.2 Stejný TC selže s různými chybovými hláškami

Naming: stejný `BUG-CP-{TC}-{S}` → updates `error_message` na nejnovější.
Předchozí messages se ztratí, ALE:
- `runs_seen` ukazuje run-IDs → trace-zip preserved per run
- Manuální triage může extrahovat history z `runs_seen` linked traces

### §4.3 Test je flaky (občas pass, občas fail)

Po N+1 fail v daném run + následné pass v retry:
- Bug status zůstává "open" — test failed at least once
- Triage řeší přepnutím na status `flake` → bug nezasahuje SLO metriky
- `occurrences` count rozliší flaky-flap od trvalého fail

### §4.4 Test selže s ENV-specific patternem (DEMO ok, PROD fail)

`envs_seen` ukazuje rozsah:
- `envs_seen="prod"` → bug je PROD-only (= legitimate Δ between branches)
- `envs_seen="demo-public,demo-tst"` → DEMO-only bug
- `envs_seen="demo-public,demo-tst,prod,prod-tst"` → universal bug

Triage filter: status `open` AND `envs_seen` contains "prod" → real PROD defect.

## §5. Migration of existing 08_Bugs data

Currently empty (max_row=1). No migration needed; new convention applies
on first bug filed.

## §6. Validator check (added to CP-SUPIN-05 validator)

```python
def check_bug_naming(wb):
    """Validator check #12 — every BUG-* row in 08_Bugs has:
       1. item_code matching pattern: BUG-CP-{TC_REF}-{ASSERT_CODE}
       2. tc_ref present and ∈ 02_TestCases.item_code
       3. first_seen <= last_seen
       4. occurrences >= 1
       5. envs_seen non-empty
    """
```

## §7. Status

| Item | Value |
|------|-------|
| Convention doc | `_specs/BUG-NAMING-CONVENTION-v0.1.md` |
| Schema migration | TBD — `tools/migrate_08bugs_v04.py` (next step) |
| Implementation | TBD — Playwright reporter + test_console.py upsert hook |
| Naming pattern | `BUG-CP-{TC_CODE}-{ASSERT_CODE}` (deterministic) |
| Dedup mechanism | UPSERT on item_code; first_seen / last_seen / occurrences counters |
| Status | v0.1 — convention locked; migration in next iteration |
