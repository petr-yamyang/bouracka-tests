# Lessons Learned — CP-SUPIN-02 — v0.1

> One iteration's worth of stumbles, course-corrections, and durable
> insights — captured so CP-SUPIN-03..08 (and the next campaign at a
> different client) don't trip on the same things twice.
>
> Session: brand-new ThinkPad task-force opened 2026-05-05 from
> `bouracka-thinkpad-archive-2026-05-03`. Worked through six revisions
> (rev 1 seed → rev 6 with full ecosystem). 26 deliverable files;
> 5 OQs raised, 5 OQs closed; 7 R1 TestTargets + 11 R2; 20 R1 TestCases;
> 121 fields catalogued; 6 mindmap renders; full-ecosystem install plan
> + ~5 supporting docs.

---

## §1. Process lessons

### L-PROC-1 — The "implicit auth" model surfaced via direct user direction, not docs

The CLIENT-PILOT-SUPIN-V0.1.md scope §4.1 placeholders called for "login
happy / login failure" TCs. Real SUT has **no login surface at all** —
authentication is implicit ID-registration (OP/ŘP/SPZ → Czech registers
via AISPOV). We discovered this only after one user message
(2026-05-05). **Action for next campaign:** at scope-doc time, ask
the user explicitly *"is there a credentialed login surface, or is
identity established differently?"* — don't assume the EU-standard
web-app shape.

### L-PROC-2 — Public recon is shallow; the analytical doc is gold

We spent ~30 min driving public bouracka.cz via Chrome MCP and got
~5 % of the architectural picture (landing + gateway + FAQ + cookies).
Pages 11–42 of the analytical doc gave us 60 % of what we needed in
~20 min of photo-reading. **Action:** ask for the analytical doc
**first**, not last. Public driving is a sanity-check for what's
already in the doc.

### L-PROC-3 — The "what's in scope for R1?" question is decisive

User direction "release 1 covers just these scenarios; other should be
identified but developed when information available" cleanly bisected
our 7 candidate TTs into 4 R1 + others R2. Without that, we'd have
authored 7 SPECs and discarded 3. **Action:** at scope-doc time, ask
explicitly for the R1 cut.

### L-PROC-4 — Photos > screenshots > textual transfer for analytical docs

The ČKP analytical doc (133 pages) was unobtainable as a file. iPhone
HEIC photos at ~1800 px were sharp enough to read every body text,
every screen mockup margin label, every state-machine string literal.
Photo quality grade B+ across both batches. **Action:** when textual
transfer is impossible, request HEIC photos (one page = one photo;
parallel-axis hold; diffuse light). Skip screenshots — they're often
worse quality due to monitor capture.

### L-PROC-5 — Iterative re-shape is faster than getting it right first time

Rev 1 → rev 6 of the Excel involved restructuring `01_TestTargets`
twice + `02_TestCases` twice. Each time the workbook re-rendered
cleanly (zero formula errors) because the rebuild scripts were
script-driven, not hand-typed. **Action:** keep all Excel building in
Python scripts (`outputs/rev*_xlsx.py`); never edit by hand once
populated.

### L-PROC-6 — The OQ ledger is the project memory

By rev 6 we had 26 OQs (CP-01..26); 5 were closed, 21 still tracked.
Without that ledger we'd have lost track of what blocked what.
**Action:** every session begins by reviewing the OQ ledger; closes
with status updates; new OQs always carry Sev/Urg/Pri.

## §2. Architectural lessons

### L-ARCH-1 — `accidentReportStatus` is the canonical decomposition axis

Once we found the state-machine values
(`NEW / IN_PROGRESS_DRIVERS / IN_PROGRESS_VEHICLES / IN_PROGRESS_CIRCUMSTANCES / TO_SIGN / FINISHED / CANCEL / ERROR`),
TT decomposition wrote itself: one TT per state-transition cluster.
Pre-state-machine, our split was R-CAST-style "page / behaviour /
component" — useful but coarser. **Action:** for every SUT, find the
canonical state machine first; let it drive the decomposition.

### L-ARCH-2 — SUPIN is the platform, not just the CDN

Initial assumption: SUPIN = CDN provider for ČKP. Reality: SUPIN s.r.o.
is the **Servisní IT organizace ČAP** (Czech Insurance Association) —
broader than ČKP alone. AISPOV (the SUPIN-hosted service) proxies
ROB / CRR / CRV / Evidence pojištěných vozidel. **Action:** trace the
ownership chain explicitly in the glossary; don't infer from URL
patterns.

### L-ARCH-3 — Vendor integrations + register integrations need different test strategies

zenID = commercial vendor (no public sandbox; needs four asks to
SUPIN). AISPOV = SUPIN-internal (skip-flag confirmation suffices).
SMS Gateway = telecom integration (test-mode + read-back hook).
**Action:** classify each integration by ownership at recon time
(`vendor | platform-internal | first-party`); the strategy follows.

### L-ARCH-4 — Mobile-only changes the viewport spec

AMENDMENT 2 said "mobile-first"; analytical doc page 14/133 said
"mobile-only". The latter is stricter — desktop renders are R2
sentinel only. **Action:** distinguish the two from the start;
"mobile-first" allows desktop as primary, "mobile-only" doesn't.

### L-ARCH-5 — Config-driven integration skipping is the killer feature

Analytical doc p25/133: SUT can skip integrations via config. This
is the test-mode mechanism that resolves 60 % of integration mocking
work. **Action:** every SUT recon should look for a config-driven
test-mode flag early; build the test posture around it if present.

## §3. Tooling lessons

### L-TOOL-1 — Cowork sandbox egress allowlist is a hard wall

The sandbox blocks `bouracka.cz`, `ckp.cz`, `supin.cz`. Workaround
via Chrome MCP browser (which uses the user's real network egress).
**Action:** at session start, confirm egress reach to the SUT
domain; if blocked, route via Chrome MCP from start.

### L-TOOL-2 — HEIC needs ImageMagick + libheif (sandbox has both)

Native `convert IMG.HEIC IMG.jpg` works in the bash sandbox. The Read
tool can ingest the resulting JPGs. **Action:** wrap into
`tools/heic-to-jpg.ps1` (Windows) + bash equivalent so any contributor
can run it without re-deriving the command.

### L-TOOL-3 — Graphviz `twopi` makes excellent one-page mindmaps

For TT/TC visual review, radial twopi layout is far more legible than
hierarchical `dot`. Color-code by priority, shape-code by type, hub
nodes by area. **Action:** keep `tools/build_mindmaps.py` as the
canonical visualiser; re-render after every Excel edit.

### L-TOOL-4 — Per-user Windows installs are friction-free

Node + Playwright + Cypress + Newman + k6 + Mailpit + Mockoon all
land under `%LOCALAPPDATA%` or `%USERPROFILE%\tools\` without admin
rights. Even Graphviz via winget installs system-wide but doesn't
require admin token. **Action:** every install step in the SUPNB plan
is per-user; SecOps just approves the BoM, no per-laptop admin
escalation.

### L-TOOL-5 — PowerShell + native commands + `ErrorActionPreference=Stop` is a trap

`$ErrorActionPreference = 'Stop'` PLUS a native command (python, dot)
writing anything to stderr → terminating error, even when exit code
is 0. Discovered when `python -c "import openpyxl"` (exit 1, stderr
traceback) crashed the wrapper. **Action:** use
`$ErrorActionPreference = 'Continue'` + explicit `$LASTEXITCODE`
checks; capture stderr to `2>&1` then assign to a variable.

### L-TOOL-6 — Markdown linkification corrupts copy-pasted commands

Some chat/desktop renderers auto-linkify `_filename.py` patterns into
`build_[mindmaps.py](http://mindmaps.py)`. Pasted into PowerShell, the
first interpreter run treats the brackets as literal path components.
**Action:** in instructional text, prefer forward slashes
(`tools/build_mindmaps.py`), avoid the underscore-then-extension
pattern, or escape with backticks consistently. Verify by reading
back what the user pastes.

### L-TOOL-7 — `winget` Graphviz install adds to system PATH but not the existing shell

A new PowerShell window after install picks up `dot` automatically.
The existing shell needs a manual PATH refresh:
```
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```
**Action:** after every winget install, open a new shell rather than
trying to refresh in place.

### L-TOOL-8 — Microsoft Store Python lacks the `py` launcher

Store Python (`python_qbz5n2kfra8p0` package) is the default on
HP EliteBook G11. Only `python.exe` and `pip.exe`; no `py.exe`.
**Action:** in cross-platform docs, prefer `python` (works
everywhere) over `py` (Windows-launcher-only).

### L-TOOL-9 — YAML beats JSON for hand-editable reference catalogues

The 121-field catalogue ships as YAML (one block per field, multi-line
`rules:`, easy diff). JSON would have made every line escape-heavy.
Excel was chosen for the high-level catalogue (auto-pivot reports);
YAML for the field-grain reference. Mindmap PNG/SVG/PDF for visual.
**Action:** three formats of the same data is appropriate when the
audiences differ; keep one source of truth, derive the others.

## §4. Communication lessons

### L-COMM-1 — Send the four-ask to vendors once, in writing

For zenID (and any commercial vendor): test-mode credentials +
contract docs + sample fixtures + skip-flag confirmation. One email,
one structured ask. **Action:** the
`_install/contracts/<int>-test-data-request.md` template is the
artefact; per integration, copy-and-fill once, send once, log
in `responses-log.md`.

### L-COMM-2 — SecOps reads docs once if the doc is one-page

`_install/CHECKLIST-FULL-ECOSYSTEM.md` is one printable page. SecOps
ticks it once per profile (A/B/C), once per laptop. Multi-page rambles
get bounced. **Action:** for any SecOps deliverable, if it's > one
page, extract a one-page checklist version.

### L-COMM-3 — Czech-first content for tester-facing material

README-CS as primary, README-EN as mirror. Glossary CS column first.
Test-data fixtures with Czech-locale validations. **Action:** for
any Czech client engagement, default to CS-first; EN-second is
collegial (helps incoming non-CS contributors).

### L-COMM-4 — Three install profiles map to three audiences

A (lean) for colleagues running R1; B (standard QA) for the testers
adding contract + perf; C (full lab) for the operator. Each profile
gets exactly one SecOps approval cycle. **Action:** for every test
campaign, map fleet → profile early; don't overspec the colleague
laptop.

## §5. Domain-specific lessons (Czech / SUPIN / ČKP)

### L-DOM-1 — `Účastník` is the legal term, not `uživatel`

The analytical doc never uses "user" — it uses "účastník" (participant
in the accident). This is regulatory-grade vocabulary. **Action:**
all CS-facing UI strings + glossary entries respect the legal term;
EN translations use "participant" not "user".

### L-DOM-2 — Czech mobile-prefix list is a published validation rule

The 47-prefix list (`601-608, 702-706, 719-739, 770-779, 790-792, 794, 795,
797, 799`) is canonical and on page 28/133. **Action:** capture as
regex once in the env config; reference from every TC; never re-type.

### L-DOM-3 — Czech ID format `^[A-Z0-9]{9}$` is the OP regex

Page 30/133 confirmed. **Action:** capture once, reference everywhere.

### L-DOM-4 — Insurance code list filters by `STATUS = 'AKT'`

Pojišťovny dropdown shows only active companies. The codelist has
inactive entries that must be filtered out. **Action:** any combobox
sourced from a codelist with status field needs the active filter
asserted in the corresponding TC.

### L-DOM-5 — `IZS` (emergency services) reachable via QR code

Once the report is signed, the QR contains `ID hlášení DN` for IZS to
read. This is a regulatory-grade hand-off. **Action:** the QR-presence
assertion is mandatory in any happy-path TC that reaches `TO_SIGN`.

## §6. Anti-patterns we avoided (and what worked instead)

| Tempting wrong path | What we did instead |
|---------------------|---------------------|
| Drive tst.* directly from the sandbox | Recon via analytical doc + Chrome MCP for public; tst.* recon via user-supplied templates |
| Author 20 SPEC.md files in one session | Lock spec format first; author 2 full + 2 skeleton; defer rest to per-session 4–5 SPECs |
| Load-test against tst.* with high VU counts | Cap perf at max_vus=20; smoke at 1; soak at 5; never hammer ČKP infra |
| Ship Cypress + Playwright + TestCafe to every laptop | Profile-driven install: Lean A for colleagues, Full C for operator |
| Hand-author 121 YAML fields | Build via repeatable Python script; verify via diff vs Excel |
| Re-shoot photos when one batch was suboptimal | Quality grade once; live with B+ for batch 2; recommend better setup for batch 3 |
| Trust Excel ↔ MD ↔ YAML to stay in sync | One source of truth (Excel for catalogues; YAML for field-grain); regenerate views on edit |
| Single huge install plan for SecOps | Two plans: lean baseline + full ecosystem; SecOps picks profile |

## §7. What's still open (to pick up next session)

1. **Pages 43–133 of the analytical doc** — six photo batches more.
   Likely sub-reasons of `ERROR`, full screen flow for sign + complete,
   integration mock fixtures.
2. **Číselníky tab values** — codelist contents (8 codelists; only
   license categories pre-populated).
3. **Obrazovky stavy tab** — possibly the formal `accidentReportStatus`
   transition table.
4. **AISPOV WSDL + zenID API contracts** — contingent on SUPIN reply
   to `_install/contracts/zenid-test-data-request.md`.
5. **Per-TC SPEC.md authoring** — TC-CP-001..020. ~5 per session →
   4 sessions of work.
6. **Activity diagrams from `SUPIN_DEMO_Bouracka` source** — being
   processed in this session (CP-SUPIN-02 rev 7).
7. **TC-coverage gap analysis** — every activity-diagram path mapped
   to ≥ 1 TC; surface uncovered branches.
8. **Mockoon stubs for INT-001..INT-010** — Layer 1 contracts work.

## §8. Status

| Item | Value |
|------|-------|
| Document | `_specs/LESSONS-LEARNED-CP-SUPIN-02-v0.1.md` |
| Iteration | CP-SUPIN-02 (rev 1..7) |
| Lessons captured | 22 across process / arch / tooling / communication / domain |
| Anti-patterns avoided | 8 |
| Next-session items | 8 |
| Status | v0.1 — read at start of CP-SUPIN-03; refine as new lessons land |
