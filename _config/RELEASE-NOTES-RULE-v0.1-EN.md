# Rule — Comprehensive release notes for every shipped artefact

**Established:** 2026-05-15 during v0.1.5 integration session.
**Scope:** Every CHANGELOG entry, every per-brief release notes block, every consolidated integration release notes document.

---

## §1 — The rule (one sentence)

Every release/integration deliverable must include the five sections below. Skipping any section is a defect; partial-coverage entries get rewritten before merge.

---

## §2 — The five mandatory sections

### §2.1 Scope IN
What's included, with detailed bug-fix list.
- For each **bug**: BUG ID + observed symptom + root cause + the fix that was applied.
- For each **feature**: file paths, lines added/changed, endpoint or function signatures introduced.
- For each **test**: function name + what behaviour it locks down.

### §2.2 Scope OUT / Deferred
What was **planned but explicitly not included**, with reason and forward-pointer.
- Distinguish "planned for a later brief" (forward-pointer) from "out of scope entirely" (no forward-pointer).
- "Not planned yet" items get a candidate brief slot (e.g., "Brief #001c candidate").

### §2.3 Regression candidates
Files or features with **heavy churn this cycle** that warrant additional test coverage.
- **Threshold:** any file with >50 lines changed across the deliverable; any file touching `workbook_io`, `dispatcher`, `server.py`, `cross_check.py`, or any test fixture.
- Format: 4-column table (Surface | Churn | Coverage gap | Suggested test).
- Each row must propose a **specific concrete test**, not just "test more".

### §2.4 Cross-brief / cross-deliverable dependencies
**Version coupling** between this work and other parallel work.
- Document every assumption: "Brief X test depends on Brief Y's workbook_io.FEATURE_X".
- Document merge-order constraints if any: "Brief X must merge AFTER Brief Y or test Z will fail".
- Document content-driven coupling: "Brief X's test asserts content that only exists in workbook Y produced by Brief Z".

### §2.5 Known issues at ship
Everything failing or flaky at the integration tag time, with severity + workaround.
- Distinguish **pre-existing** (not introduced by this deliverable) from **new**.
- Note **environment-specific** vs **platform-agnostic**.
- Include **cosmetic** items (warnings, deprecations) — they aggregate into tech-debt and need surfacing.
- For each known issue, propose either a fix forward-pointer or accept-and-move-on.

---

## §3 — Format conventions

- Markdown, English (EN suffix in filename). CS translation is optional and additive.
- Filename pattern for full integration release notes:
  `RELEASE-NOTES-<project>-<version>-INTEGRATION-<YYYY-MM-DD>-EN.md` at repo root.
- Filename pattern for CHANGELOG per-brief entries:
  `## [<project> <version>] — <YYYY-MM-DD> — <Brief #NNN>: <one-line scope>`
  followed by the five sections.
- Use heading levels `## §2.1 Scope IN` (etc.) for sub-headings; bullet points within.
- Tables for §2.3 and §2.5 when the data is comparable across rows.
- Code paths in `backticks`. Brief numbers as `#NNN`. Bug IDs as `BUG-XX-NNN`.

---

## §4 — Authoring workflow

1. **Brief author** drafts §2.1 Scope IN. Always.
2. **Integration owner** writes §2.2–§2.5 during merge:
   - Scope OUT comes from the brief design doc + observed deferral during merge.
   - Regression candidates come from `git diff --stat` (>50-line threshold) + judgement on critical surfaces.
   - Cross-brief deps come from the merge's actual conflicts and from re-reading the brief design docs.
   - Known issues come from the post-merge test run + the merge-tree state.
3. **Reviewer (Pete)** checks all five sections present before accepting the merge as done.

---

## §5 — Example template (copy this for new entries)

```markdown
## [<project> v<X.Y.Z>-devN] — YYYY-MM-DD — Brief #NNN: <one-line scope>

**<one-paragraph framing — is this internal/external, does the customer get it, what milestone slot>.**

### Scope IN — <area, e.g. `bouracka_ui/` cross-check endpoints>

- **<feature 1>** — what it does, where it lives, signature if API. Cite the brief ID.
- **<feature 2>** — ...
- **<test addition>** — what behaviour gets locked down.

### Scope OUT — explicitly deferred

- **<deferred item>** — reason; forward-pointer (e.g., "Brief #NNNc candidate, v0.X.Y").
- **<another>** — ...

### Regression candidates

| Surface | Churn | Coverage gap | Suggested test |
|---|---|---|---|
| `file/path.py::function()` | N lines | what's not covered | concrete test description |
| ... | ... | ... | ... |

### Cross-brief dependencies

- **<Dep A>:** this work assumes Brief #NNN's <feature>. If Brief #NNN is missing, <test Z> will fail.
- **<Dep B>:** ...

### Known issues at merge time

- **<issue 1>** — severity + workaround.
- **<issue 2>** — ...

---
```

---

## §6 — Why this rule exists

- **Avoids tribal knowledge:** the integration owner shouldn't need to re-derive Scope OUT or Known issues from memory. Future-Pete (and future sessions) can read the entry and reconstruct context.
- **Catches incomplete briefs early:** a brief without §2.1 detail can't be merged. Forces upstream rigor.
- **Surfaces tech debt:** §2.5 Known issues + §2.3 Regression candidates aggregate into a backlog rather than vanishing.
- **Enables audit-grade traceability:** every bug-fix lists root cause AND fix; every feature lists where it lives. Auditors can grep one document, not chase commits.

---

**Provenance:** Rule introduced by Pete Y. during v0.1.5-integration session (2026-05-15) in response to brief authors shipping work without comprehensive release notes. Applied retroactively to enhance Briefs #001/#001b/#005/#006/#007 CHANGELOG entries during the same session.
