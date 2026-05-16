# Working model — when to use which Claude

**Status.** Heuristic v0.1 (2026-05-13). Refine as we hit edges.
**Author.** Pete Y. (operating model) + Claude (rationale).

---

## §1. Why a split exists at all

Three Claude variants cover different cost/capability points. Picking the right one for the right task = roughly 3–5× cheaper runs without losing quality on the high-stakes work.

| Variant | Where it lives | What it's optimised for | Where it falls short |
|---------|----------------|--------------------------|----------------------|
| **Opus 4.7** (this Cowork desktop session) | Persistent project context, multi-day memory, can read whole repo + workbook + design docs | Architecture, ambiguity resolution, schema design, multi-step planning, judgment calls, novel-pattern reasoning | Burns tokens on routine mechanical work; overkill for "write 20 unit tests" |
| **Sonnet** (via Claude Code in terminal, or new desktop tab) | Same repo but stateless per session | Code generation against a clear spec, refactor passes, write-the-tests-from-a-design-doc, doc rewrites, mechanical patcher work | Weaker at novel architecture, may default to surface-level fixes for deep bugs |
| **Claude Design** (Anthropic's UI-mockup-oriented variant — when available) | Standalone mockup/wireframe session | UI sketches, layout iteration, design-token decisions, mockup-to-code | Not for code review / not for analytical work |

---

## §2. Decision rules

### §2.1 Stay in **Opus 4.7** (this session) when:

- The task **needs the project context** I've accumulated this session (v0.1.4 fixes history, BUG-K-* hypotheses, the workbook schema archaeology, what KP changed, the Oracle ERD draft).
- The task requires **resolving ambiguity** — "is this a typo or intentional?", "should this be in v0.1.5 or v0.1.6?", "what's the right schema shape here?".
- The task **decides architecture** — new entity in the data model, new API surface, new state in the wizard FSM.
- The task **walks across multiple files/sheets** to find a pattern (e.g., the dangling `step_id` FK finding).
- The task is **a planning/strategy doc** I'll re-use later (P0 ranking, deep-session agenda, design notes).
- The task is a **judgment call about user-facing language** (e.g., what Czech to put in Kate's reinstall message).

### §2.2 Hand off to **Sonnet** (Claude Code) when:

- The spec is **clear in a design doc** I've already written (e.g., the v0.1.5 design notes §3 schema; Sonnet can implement `workbook_io.list_steps()` from the design without me re-deriving it).
- The task is **mechanical refactor** — "rename column `tc_ref` to `linked_tc_ref` in 18 places".
- The task is **writing tests against an existing API surface** — "write 6 new pytest cases for `/api/tcs/{tc}/steps`".
- The task is a **patcher script** with clear input/output — "split `steps_summary` rows into `02e_TestSteps` rows".
- The task is **boilerplate documentation** — release notes, CHANGELOG bumps, copy of an existing doc with the version number changed.
- The task is **build/release engineering** — "run `python -m build`, then sha256 the wheel, then zip with the workbook".

### §2.3 Spin a **Claude Design** session when:

- Iterating on a **mockup** — FR-K-002 step accordion layout, FR-K-003 run console rendering, FR-K-004 evidence modal.
- Picking **design tokens** — typography scale for the run console, severity-color mapping.
- Doing a **UI design review** — does this card hierarchy land for a non-engineer tester?

### §2.4 Always come back to Opus 4.7 after:

- Sonnet finishes a chunk → **review** here before commit.
- Claude Design produces a mockup → **integrate into design notes** here.
- Anything that touches the workbook schema, the FSM, or the integration recon docs.

---

## §3. The current backlog, classified

Apply the rules above to the open task list (as of 2026-05-13):

| # | Task | Where it belongs | Notes |
|---|------|------------------|-------|
| #21 | git park-commit `cp-supin-06-kate-drop` | **Sonnet** | Commit message body already drafted; mechanical. |
| #22 | Upload to Pete's Drive | **Pete-side** | Not a Claude task. |
| #31 | Day 1B int-recon dispatch | **Done in this session** | Harness shipped. |
| #44 | Bundle 2 (v0.1.5) **implementation** | **Sonnet** after KP review | Design notes are the spec. Schema decisions stayed here in Opus. |
| (new) | v0.1.5 workbook patcher `tools/workbook-v0.4.3-to-v0.4.4.py` | **Sonnet** | Clear input/output; design notes spec it. |
| (new) | FR-K-001/002/003/004 endpoint impl | **Sonnet** | Each one has API shape declared in design notes §4–§6. |
| (new) | Evidence modal UI (FR-K-004) | **Claude Design first**, then **Sonnet** to implement | Mockup decision then mechanical wire-up. |
| (new) | Step-accordion UI (FR-K-002) | **Claude Design first**, then **Sonnet** | Same pattern. |
| (new) | P0 ranker as `tools/p0-ranker.py` | **Sonnet** | Algorithm is fully specified in P0-RANKING doc §2 and §11. |
| (new) | Selenium step-emission listener | **Opus 4.7** | Architectural decision: when to fail vs degrade; needs context on what Kate's flows do. |
| (next session) | Deep Session 1 — TestAnalysis + TestDesign refinement | **Opus 4.7** | Deep architectural work; whole purpose is judgment. |
| (next session) | Deep Session 2 — D6c FR-K-* deeper review | **Opus 4.7** | Same. |
| (deferred) | Oracle Phase 1 discovery — when DBA delivers password | **Opus 4.7** to design queries, **Sonnet** to run boilerplate | The first query batch decides what we explore next; that's a judgment call. |

---

## §4. Handoff hygiene

When this session sends work to Sonnet, the handoff brief should include:

1. **The exact spec section** (e.g., "implement per `BOURACKA-UI-V0.1.5-DESIGN-NOTES-EN.md` §4.2 GET /api/tcs/{tc}/steps").
2. **The acceptance test** (e.g., "smoke test must assert `/api/tcs/TC-CP-008/steps` returns at least 1 step record with non-null `action_en`").
3. **The file boundaries** Sonnet may touch (e.g., "modify `bouracka_ui/workbook_io.py`, `bouracka_ui/server.py`, and `tests/test_smoke.py`; do NOT touch `cli.py` or `dispatcher.py`").
4. **The "don't go beyond" markers** — "if you find that 02e_TestSteps doesn't exist in the workbook yet, fall back per design §3.3 and tell Pete; do NOT generate the schema yourself".
5. **The return checklist** — what to report back so Opus can review (diff summary, test results, any deviations from spec).

This is roughly the same brief an internal contractor would get. Reduces the risk of Sonnet "improving" the spec in ways that drift from the architectural intent.

---

## §5. When the rules break

- If Sonnet **stalls on a deep question**, escalate back here. Don't let Sonnet make architectural decisions it doesn't have context for.
- If this session **gets stuck on mechanical noise** (long file rewrites, version bumps across 6 files), recognise the pattern and call it out — that's Sonnet's lane.
- If a "routine" task **reveals a hidden architectural question** (e.g., a refactor turns out to need a schema change), kick it back here.

---

## §6. Costs to watch

- **Cowork session length matters** — long context = quadratic-ish cost. Periodic park-commits + new sessions are cheaper than one mega-session, especially after major milestones.
- **Sonnet hot-path** — Claude Code in terminal is the cheapest way to run mechanical work; doesn't carry desktop session state.
- **Design model uses are short** — quick mockup iterations, not sustained sessions.

---

## §7. Refs

- `_config/BOURACKA-UI-V0.1.5-DESIGN-NOTES-EN.md` — the spec Sonnet will implement against.
- `_config/BOURACKA-P0-SMOKE-TC-RANKING-v0.1-EN.md` — Opus-produced, Sonnet can re-run the algorithm from §11.
- `_config/TEST-ANALYSIS-AND-DESIGN-DEEP-SESSIONS-PLAN-v0.1-EN.md` — where the Opus-only deep sessions live.
