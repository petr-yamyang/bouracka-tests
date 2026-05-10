# Cross-Framework Result Schema — v0.1 — 2026-05-10

**Project:** SUPIN/Bouračka delivery + MI-M-T integration roadmap
**Version:** v0.1.0 (binding from this date forward)
**Author:** Sonnet (MacBook Cowork session — Track B Phase 1, post Phase-3 GAL-D01 hand-off)
**Trigger:** Phase 1 prerequisite of `_config/BOURACKA-TES-PRESENTATION-LAYER-DESIGN-v0.1-2026-05-09.md` §6.1; closes OQ-MB-14 (HANDOVER-THINKPAD-OPUS-CP-SUPIN-05-CONVERGED-2026-05-09 §5.3).
**Authority:** **binding** for V0/V1/V2 implementation of `tools/tes_present.py`, `tools/tes_dashboard.py`, and `mimt-cli/append-run-result --api-mode`. Any code emitting cross-framework run results must conform; any code reading them must validate against this spec.
**Audience:** ThinkPad-Sonnet (delivery executor for `tools/consolidate_results.py` v0.5.3+ migration), ThinkPad-Opus (V0 + V1 review + acceptance gate), MacBook-Sonnet (mimt-governance roadmap §5 reporting module), Pete (operator + MI-M-T runner-backend integration).
**Posture:** lifts the schema from `tools/consolidate_results.py` v0.5.2 (the de-facto current shape) into a normative spec. Documents the v0.5.2-actual vs v0.1-target gap and the migration path. After this spec freezes, downstream tools (V0 / V1 / V2) hold the line on this contract.

---

## §0. How to use this doc

```
Step 0 — read THIS file end-to-end (~12 min)
Step 1 — orient on related artefacts:
   1. tools/consolidate_results.py — UPSTREAM emitter (current v0.5.2 shape; the source of truth that will be migrated)
   2. _config/BOURACKA-TES-PRESENTATION-LAYER-DESIGN-v0.1-2026-05-09.md — §3.1 Output 3 + §5.4 schema-coherence rationale
   3. _config/BOURACKA-PROD-ENV-CLONE-DESIGN-v0.1-2026-05-09.md — §3 env-tag enum + applies_to_envs
   4. _specs/from-macbook/HANDOVER-THINKPAD-OPUS-CP-SUPIN-05-CONVERGED-2026-05-09.md — §5.3 (OQ-MB-14) + §5.4 (mimt-governance roadmap)
   5. _specs/from-macbook/SYNCHRO-MACBOOK-FROM-OPUS-CP-SUPIN-05-FOLLOWUP-2026-05-08.md — §4.2 MIMT-IMPORT-CONTRACT-DRAFT (read-side at MI-M-T)
   6. _specs/TEST-EXECUTION-SUMMARY-FORMAT-v0.1-CS.md — sister doc; TES sheet column mapping
Step 2 — implementer: align tools/consolidate_results.py to §2 canonical shape per §4 migration plan
Step 3 — readers (tes_present.py / tes_dashboard.py / mimt-cli): validate inputs against §5 rules; reject anything noncompliant
```

## §1. Purpose + binding scope

The presentation layer (`tools/tes_present.py` V0; `tools/tes_dashboard.py` V1; MI-M-T runner-backend POST V2) consumes consolidated cross-framework run output. Without a single normative shape, each consumer drifts and the architecture devolves into per-tool ad-hoc parsing. This spec is the **one binding contract** that fixes the wire format end-to-end.

| Producer | Consumer(s) | Wire artefact |
|----------|-------------|---------------|
| `tools/consolidate_results.py` (v0.5.3 target) | `tools/tes_present.py` (V0) | `runs/cross-framework-<date>.json` |
| `tools/tes_present.py --json-out` (V0) | `tools/tes_dashboard.py` (V1); `mimt-cli append-run-result` (V2) | `runs/cross-framework-<env>-<date>.json` |
| `tools/tes_present.py --api-mode <mimt-url>` (V2) | MI-M-T `/api/v1/runs/{rid}/results` (per MIMT-IMPORT-CONTRACT-DRAFT §4.2) | HTTP POST body |

All three artefacts carry the **same JSON shape** documented here. Versioning is via top-level `schema_version` (§6).

**In scope:** the run-level + per-TC result envelope. **Not in scope:** per-assertion drill-down (lives in workbook `14_AssertionGateResults`; that's a separate sheet contract — see TEST-EXECUTION-SUMMARY-FORMAT-v0.1-CS.md). The schema here references AGR rows but does not embed them.

## §2. Canonical schema — annotated example

Rendered as a fully-instantiated v0.1 instance with field-level commentary in JSONC format. Every field listed here is **required** unless explicitly marked `(optional)`. Strict additive evolution is per §6.

```jsonc
{
  // §2.1 — top-level run identity
  "schema_version": "1.0",                          // pinned literal "1.0" for this spec; see §6
  "run_id":         "run-2026-05-10T14:30:00Z-a1b2c3d",
                                                     // format: "run-<ISO-8601 UTC w/ Z>-<7-char short hash>"
                                                     // hash = first 7 chars of git HEAD or random uuid4 hex
  "env":            "demo",                          // enum: demo | tst | uat | prod-readonly | prod-writable
                                                     // per BOURACKA-PROD-ENV-CLONE-DESIGN §3
  "env_url":        "https://demo.bouracka.cz",      // (optional) the actual base URL targeted; informational
  "started_at":     "2026-05-10T14:30:00Z",          // ISO-8601 UTC w/ trailing Z; consolidated-run start
  "ended_at":       "2026-05-10T14:32:14Z",          // ISO-8601 UTC w/ trailing Z; consolidated-run end
  "duration_ms":    134000,                           // ended_at - started_at in ms; integer
  "frameworks":     ["playwright", "cypress", "selenium"],
                                                     // ordered list of framework keys present in this run
                                                     // valid keys: playwright | cypress | selenium | playwright-api | postman
                                                     // ordering is canonical-alphabetical by primary 5 (pw,cy,se) then extras

  // §2.2 — per-TC results (the run's main payload)
  "results": [
    {
      "tc_code":       "TC-CP-A1-MAIN-DEMO",         // canonical TC code per TESTCASE-SPEC-FORMAT-v0.2 §2
      "verdicts": {                                   // verdict per framework that ran this TC
        "playwright": "skip-drift",                   // enum: pass | fail | skip-drift | skip-other | soft-pass | error | missing
        "cypress":    "skip-drift",                   // "missing" reserved for "framework didn't run this TC"
        "selenium":   "skip-drift"
      },
      "parity_status": "agree",                       // enum: agree | divergence | not-applicable
                                                     // "agree" = all present-frameworks share normalized verdict
                                                     // "divergence" = frameworks disagree → INVESTIGATE (per HANDOVER §5.3 + OQ-TES-05)
                                                     // "not-applicable" = only one framework ran (no parity check possible)
      "duration_ms": {                                // duration per framework in ms; integer
        "playwright": 1234,
        "cypress":    1567,
        "selenium":   1180
      },
      "evidence": {                                   // evidence paths per framework (relative to repo root)
        "playwright": {
          "trace_ref":      "playwright-report/trace-tc-a1-main-demo.zip",  // (optional)
          "screenshot_ref": "playwright-report/screenshot-tc-a1-main-demo.png", // (optional)
          "video_ref":      null                       // (optional; null if not recorded)
        },
        "cypress": {
          "trace_ref":      null,
          "screenshot_ref": "cypress/screenshots/tc-a1-main-demo.png",
          "video_ref":      "cypress/videos/tc-cp-a1-main-demo.mp4"
        },
        "selenium": {
          "trace_ref":      null,
          "screenshot_ref": "selenium-report/tc-a1-main-demo.png",
          "video_ref":      null
        }
      },
      "covered_tt": [                                 // TT codes covered by this TC (from TT-AS / TT-FUNC etc.)
        "TT-FUNC-MainGalleryReportEntry",
        "TT-AS-001"
      ],
      "error_messages": {                             // first-line of error per framework where present; null otherwise
        "playwright": null,
        "cypress":    null,
        "selenium":   null
      },
      "framework_specific_notes": {                   // (optional) per-fw raw status if non-canonical; informational
        "playwright": "",                              // empty string when status was canonical (passed/failed/skipped)
        "cypress":    "",
        "selenium":   ""
      },
      "viewport":   "375x667",                         // (optional) dominant viewport for this TC; can vary across fw
      "bug_ref":    null,                              // (optional) BUG-CP-... code if this failure is linked to a known bug
      "soft_pass_reason": null                         // (optional) free-text reason if any verdict was "soft-pass"
    }
    // ... one entry per TC in the run
  ],

  // §2.3 — run-level summary (computed; redundant w/ results[] but pre-aggregated for fast UI rendering)
  "summary": {
    "total_tcs":              10,                     // count of distinct tc_code in results[]
    "passed":                 4,                      // count where ALL present-fw verdicts ∈ {pass, soft-pass}
    "failed":                 0,                      // count where ANY present-fw verdict ∈ {fail, error}
    "skipped":                5,                      // count where ALL present-fw verdicts ∈ {skip-drift, skip-other}
    "soft_passed":            1,                      // count where ALL present-fw verdicts == soft-pass
    "drift_skip_count":       5,                      // count where ALL verdicts == skip-drift specifically
    "parity_pass_count":     10,                      // count of results[] entries with parity_status == "agree"
    "parity_divergence_count": 0,                     // count with parity_status == "divergence"
    "pass_rate_strict":       0.40,                   // passed / total_tcs; 2-decimal float
    "pass_rate_drift_aware":  0.90                    // (passed + drift_skip_count) / total_tcs
  },

  // §2.4 — host + provenance (machine + tool versions; needed for cross-host run aggregation in V1+)
  "host": {
    "os":                "Windows-10",                // bare OS string; one of: Windows-10 | Windows-11 | macOS-Tahoe | Ubuntu-22 | (other)
    "host":              "ThinkPad-X1-2026",          // hostname (no FQDN; sanitized if internal); free-string
    "git_commit":        "5fa3977",                   // (optional) short hash of bouracka-tests repo HEAD at run-time
    "git_branch":        "thinkpad",                  // (optional) branch name
    "tool_versions": {                                // (optional) versions of frameworks at run-time
      "playwright": "1.45.0",
      "cypress":    "13.13.0",
      "selenium":   "4.21.0",
      "node":       "20.15.0",
      "python":     "3.11.5"
    }
  },

  // §2.5 — drift forensic (per-env carry; populated when drift skip-guards triggered)
  "drift_forensic": {                                  // (optional; null when drift not active)
    "active":              true,                      // boolean — drift detected on this env at this run
    "drift_type":          "recaptcha-v3",            // enum: recaptcha-v3 | recaptcha-v2 | other-401-403 | rate-limit | (other)
    "trigger_correlation": "54a6e0a3-1234-5678-9abc-def012345678",
                                                     // (optional) correlationId / requestId from rejection response
    "affected_tcs":        ["TC-CP-A1-MAIN-DEMO", "TC-CP-A2-ALT-1", "TC-CP-A2-ALT-4",
                            "TC-CP-A2-ALT-5", "TC-CP-A2-ALT-10"],
    "guard_policy":        "skip-on-drift",           // enum: skip-on-drift | proceed-flag | abort
    "notes":               "reCAPTCHA-v3 active on /api/reports; 5 TCs SKIP via drift guard"
  },

  // §2.6 — reporter command + run-trigger metadata
  "reporter": {
    "command":     "make test ENV=demo",              // free-string; the command that produced this run
    "trigger":     "manual",                          // enum: manual | ci | scheduled | api
    "ci_run_id":   null,                              // (optional) GitHub Actions run_id if trigger == "ci"
    "operator":    "petr-yamyang"                     // (optional) git user.name or system username
  }
}
```

## §3. Field semantics — definitive reference

### §3.1 Top-level identity (§2.1)

| Field | Type | Required | Constraint |
|-------|------|:---:|------------|
| `schema_version` | string | yes | exactly `"1.0"` for this spec; bumps to `"1.1"` etc per §6 |
| `run_id` | string | yes | regex `^run-\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z-[0-9a-f]{7}$`; UUID-uniqueness across all runs |
| `env` | enum string | yes | one of `demo` `tst` `uat` `prod-readonly` `prod-writable` |
| `env_url` | string \| null | no | absolute URL or null; informational only |
| `started_at` / `ended_at` | string | yes | ISO-8601 UTC with trailing `Z`; `started_at` ≤ `ended_at` |
| `duration_ms` | integer | yes | non-negative; should equal `(ended_at - started_at).total_milliseconds()` ± 50ms |
| `frameworks` | array of strings | yes | length ≥ 1; values from `{playwright, cypress, selenium, playwright-api, postman}`; ordered alphabetical |

### §3.2 Per-TC result (§2.2)

| Field | Type | Required | Constraint |
|-------|------|:---:|------------|
| `tc_code` | string | yes | regex `^TC-[A-Z0-9-]+$`; matches a TC entry in `02_TestCases` sheet |
| `verdicts` | object | yes | keys ⊆ `frameworks`; values from `{pass, fail, skip-drift, skip-other, soft-pass, error, missing}` |
| `parity_status` | enum string | yes | `agree` `divergence` `not-applicable` per §3.4 |
| `duration_ms` | object | yes | same keys as `verdicts`; non-negative integers |
| `evidence` | object | yes | keys = `frameworks`; each value is `{trace_ref, screenshot_ref, video_ref}` (each string\|null) |
| `covered_tt` | array of strings | yes | regex `^TT-[A-Z]+-[A-Za-z0-9_]+$`; deduplicated; sorted |
| `error_messages` | object | yes | keys = `frameworks`; values are first-line error or null |
| `framework_specific_notes` | object | no | informational raw-status strings; defaults to empty per fw |
| `viewport` | string | no | format `<width>x<height>`; default `"375x667"` (mobile-first per Bouračka scope) |
| `bug_ref` | string \| null | no | BUG-CP-... code or null |
| `soft_pass_reason` | string \| null | no | required if any verdict is `soft-pass`; null otherwise |

### §3.3 Verdict enum — semantics

| Value | When emitted | Counts toward summary as |
|-------|--------------|--------------------------|
| `pass` | TC executed; all assertions PASS | `passed` |
| `fail` | TC executed; ≥1 assertion FAIL | `failed` |
| `skip-drift` | TC skipped via drift guard (reCAPTCHA-v3, 401/403, rate-limit, etc.); see `drift_forensic` | `skipped` + `drift_skip_count` |
| `skip-other` | TC skipped for non-drift reason (env-tag mismatch, manual `it.skip`, fixture missing) | `skipped` (NOT drift_skip) |
| `soft-pass` | TC executed; passed but flagged as needing review (e.g. ALT-9 known-soft) | `passed` + `soft_passed`; `soft_pass_reason` REQUIRED |
| `error` | TC failed before assertions ran (setup error, tooling crash) | `failed` |
| `missing` | this framework did NOT run this TC at all | (no count; excluded from parity calc) |

Producers MUST emit one of these 7 values per (TC, framework) tuple where the framework was attempted. `missing` is the explicit "wasn't attempted" signal — a missing key in `verdicts` is the SAME as `"missing"` but explicit form is preferred.

### §3.4 `parity_status` computation rule

For each TC entry, `parity_status` is computed by the producer (NOT by the consumer) per:

```
let present_verdicts = [v for fw, v in verdicts.items() if v != "missing"]
let normalized = [normalize(v) for v in present_verdicts]   # see §3.5
if len(present_verdicts) == 0:                  # no framework ran → invalid; producer must emit error
    invalid run — reject
elif len(present_verdicts) == 1:                # only one fw ran → cannot compare
    parity_status = "not-applicable"
elif len(set(normalized)) == 1:                  # all agree (after normalization)
    parity_status = "agree"
else:
    parity_status = "divergence"
```

### §3.5 Verdict normalization for parity check

Soft-pass collapses to pass; skip-other to skip-drift IS NOT done (different semantics):

```
normalize: pass | soft-pass             → pass
normalize: fail | error                 → fail
normalize: skip-drift                   → skip-drift
normalize: skip-other                   → skip-other
                                         (skip-drift and skip-other DO NOT collapse — they remain distinct)
```

Rationale: a TC SKIP'd via drift on cypress + SKIP'd via fixture-missing on selenium has **divergent** root causes; reporting them as `agree` would mask a real bug.

### §3.6 Summary (§2.3) — derivation rules

All summary counts are **computed from `results[]`** at producer time. Consumers MUST recompute and validate (§5). Mismatch is a producer bug.

```
total_tcs                = len(results)
passed                   = count(r for r in results where all_present_verdicts ⊆ {pass, soft-pass})
failed                   = count(r for r in results where any_present_verdict ∈ {fail, error})
skipped                  = count(r for r in results where all_present_verdicts ⊆ {skip-drift, skip-other})
soft_passed              = count(r for r in results where all_present_verdicts == {soft-pass})
drift_skip_count         = count(r for r in results where all_present_verdicts == {skip-drift})
parity_pass_count        = count(r for r in results where parity_status == "agree")
parity_divergence_count  = count(r for r in results where parity_status == "divergence")
pass_rate_strict         = round(passed / total_tcs, 2)
pass_rate_drift_aware    = round((passed + drift_skip_count) / total_tcs, 2)
```

Edge case `total_tcs == 0`: `pass_rate_*` set to `null` (NOT 0.0; division-by-zero is meaningful absence).

### §3.7 `host` + `drift_forensic` + `reporter` (§2.4–§2.6)

These are populated as available and skipped as `null` (or omitted at the field level for nested `host.tool_versions` etc.) when not. They are **informational** — consumers should not block on absence except where a downstream rendering needs them (e.g. V1 trend chart needs `host.os` to color-code per-host runs; if absent, falls back to "unknown").

`drift_forensic` is `null` when `drift_forensic.active == false` could equally apply — consumers MUST treat absence and `{active: false}` as equivalent.

## §4. v0.5.2-actual vs v0.1-target — gap analysis + migration plan

The `tools/consolidate_results.py` v0.5.2 emits a **superset of** the v0.1 spec but with a different shape. Direct migration to v0.1 is required.

### §4.1 Field-by-field gap map

| v0.5.2 actual | v0.1 target | Migration action |
|---------------|-------------|------------------|
| `generated` (date string) | `started_at`, `ended_at` (ISO-8601 UTC) | replace with timestamps; compute `duration_ms` |
| `env` = base URL (e.g. `https://demo.bouracka.cz`) | `env` = enum tag (`demo`); `env_url` = base URL | parse env tag from URL; preserve URL as `env_url` |
| `frameworks` = object (per-fw counts) | `frameworks` = array of fw names; counts move to `summary` | restructure |
| `tcs_with_divergence` | `parity_status: divergence` per result + `summary.parity_divergence_count` | invert: per-TC parity_status drives the divergence list |
| `all_results` array of `{tc_code, framework, status, ...}` (one row PER fw PER TC, flat) | `results[]` array of `{tc_code, verdicts: {fw → status}, ...}` (one row PER TC, nested) | pivot: group by tc_code; build verdicts object |
| `status` enum: `passed/failed/skipped/soft_passed` | `verdicts.<fw>` enum: `pass/fail/skip-drift/skip-other/soft-pass/error/missing` | rename + extend (add `skip-drift` vs `skip-other` distinction; map old `skipped` → `skip-other` UNLESS drift-forensic context overrides) |
| `error_message` (per-result) | `error_messages.<fw>` (per-TC) | move under per-TC envelope |
| `trace_ref` (per-result, single field) | `evidence.<fw>.{trace_ref, screenshot_ref, video_ref}` | expand into nested object |
| `framework_specific_notes` (per-result string) | `framework_specific_notes.<fw>` (per-TC object) | move under per-TC envelope |
| `viewport` (per-result) | `viewport` (per-TC, optional) | hoist to per-TC level |
| `covered_tt` (per-result) | `covered_tt` (per-TC, deduplicated across fw) | merge across fw with set-union |
| (none) | `schema_version`, `run_id`, `summary`, `host`, `drift_forensic`, `reporter` | NEW fields — populate per §3 rules |

### §4.2 Migration action list — `tools/consolidate_results.py` v0.5.2 → v0.5.3

This is the implementation task that `tools/consolidate_results.py` will pick up on next ThinkPad-Sonnet pass. **Scope:** rewrite the consolidator output shape to v0.1; preserve input parsing logic.

```
1. Add CLI flag --env <enum>           (validates against §3.1 env enum)
2. Add CLI flag --run-id <string>      (auto-generates if absent: f"run-{utc_iso}-{git_short_or_uuid7}")
3. Add CLI flag --env-url <url>        (defaults to existing --base-url)
4. Refactor _build_parity_report():
   a. Pivot all_results from flat (per fw × TC) to nested (per TC × {verdicts: {fw → status}})
   b. Compute parity_status per TC per §3.4
   c. Compute summary per §3.6
   d. Map old status enum → new verdict enum (per §4.3 below)
5. Capture started_at = first result timestamp; ended_at = last (or wallclock around invocation)
6. Capture host info via socket.gethostname() + platform.system()
7. Optional: capture git commit + branch via subprocess
8. Output JSON conforming to §2 canonical shape
9. Bump CHANGELOG.md → v0.5.3 entry citing this spec
10. Add test: tests/tools/test_consolidate_results_v05_3_schema.py with 1 golden fixture
```

**Effort:** 1 ThinkPad-Sonnet session (~2 hours).

### §4.3 Status → verdict mapping

The v0.5.2 `status` field carries less information than v0.1 `verdict` (no drift-vs-other distinction). Migration rule:

```
old "passed"      → new "pass"
old "failed"      → new "fail"
old "soft_passed" → new "soft-pass"
old "skipped"     → new "skip-drift"  IF drift_forensic.active == true on this run AND this TC ∈ drift_forensic.affected_tcs
                   → new "skip-other" otherwise
old (anything else) → new "error"
```

Consolidator infers `drift_forensic.active` from the presence of skip-with-correlation-id markers in selenium/cypress logs (existing convention). If consolidator can't tell — emit `skip-other` and let the fixture itself emit `skip-drift` via marker (§4.4).

### §4.4 Producer-side verdict refinement (test fixtures)

For frameworks to emit `skip-drift` precisely (vs falling through to `skip-other`), test fixtures need to mark the skip with a recognizable token. Recommended marker convention:

```python
# Selenium pytest fixture
pytest.skip("DRIFT-RECAPTCHA-V3:correlation_id=54a6e0a3-...")

# Cypress
cy.log('DRIFT-RECAPTCHA-V3:correlation_id=...')
this.skip()

# Playwright
test.skip(true, 'DRIFT-RECAPTCHA-V3:correlation_id=...');
```

The consolidator parses for `^DRIFT-` prefix in skip reasons → upgrades verdict to `skip-drift`. Without prefix → `skip-other`.

This is a fixture-side concern and OUT OF SCOPE for v0.1 schema spec — captured here as a forward dependency for §4.2 step 4d. ThinkPad-Sonnet should ensure fixtures emit the marker consistently when implementing the migration.

## §5. Validation rules

Both producers and consumers MUST validate. Producer validation prevents emitting noncompliant artefacts; consumer validation rejects upstream bugs early.

### §5.1 Producer-side assertions (consolidator emits → must be true)

```
ASSERT schema_version == "1.0"
ASSERT run_id matches regex per §3.1
ASSERT env in {demo, tst, uat, prod-readonly, prod-writable}
ASSERT started_at <= ended_at
ASSERT duration_ms == round((ended_at - started_at).total_seconds() * 1000) ± 50ms
ASSERT frameworks is sorted ascending and deduplicated
ASSERT len(results) == summary.total_tcs
FOR EACH result IN results:
    ASSERT result.tc_code matches regex per §3.2
    ASSERT all keys in result.verdicts ⊆ frameworks
    ASSERT result.parity_status == compute_parity(result.verdicts)  # §3.4
    ASSERT result.duration_ms keys == result.verdicts keys
    ASSERT result.evidence keys == frameworks  (all 3 — present_with_null_subfields if fw didn't run)
    IF any verdict == "soft-pass": ASSERT result.soft_pass_reason is not null
ASSERT summary == compute_summary(results)  # §3.6
IF drift_forensic is not null: ASSERT drift_forensic.affected_tcs ⊆ all tc_code values in results
```

### §5.2 Consumer-side validation (recommended; not strictly required but helps fail-fast)

```
PARSE → if JSON parse fails: reject with diagnostic line+column
CHECK schema_version == "1.0" → if mismatch: reject; suggest version-specific consumer
RE-RUN producer-side assertions §5.1 → if any fails: reject; report which assertion + reproducer JSON pointer
```

A reference Python validator stub belongs at `tools/validate_cross_framework_schema.py` (not part of this v0.1 spec; track as follow-up implementation per §7).

### §5.3 JSON Schema (formal)

A formal JSON Schema (Draft 2020-12) is **deferred to v0.1.1** of this spec. v0.1 is the prose contract; v0.1.1 will ship a `_specs/CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.json` that codifies §3 + §5.1 mechanically. Why not now: the prose is the source of truth; ship the spec first, formalize after one round of consumer feedback.

## §6. Versioning + extensibility

### §6.1 SemVer-like policy

```
v1.0  — frozen by THIS spec; binding from 2026-05-10
v1.1  — additive backward-compatible changes (new optional fields; new enum values for verdict if pre-coordinated)
v2.0  — breaking changes (removing fields; changing required-field shape; renaming top-level keys)
```

Consumers MUST tolerate unknown additional fields (per §6.2). Producers MUST emit `schema_version` matching the highest version they conform to. v1.x consumers MUST refuse v2.x payloads.

### §6.2 Forward compatibility — consumers ignore unknown fields

Consumers built against v1.0 reading a v1.1 payload MUST:
- Accept and ignore any unknown top-level fields
- Accept and ignore any unknown nested-object fields
- Validate the v1.0 fields they care about strictly

This permits incremental rollout: v1.1 emitter ships with new optional fields; old consumers continue working. Old consumers don't get the new value, but don't crash.

### §6.3 Extension points expected for v1.1

Already-foreseen additive fields, deferred to v1.1 to keep v1.0 minimal:

| Field | Where | Purpose |
|-------|-------|---------|
| `applies_to_envs` per-result | inside each `results[]` entry | TC's expected-env CSV (per BOURACKA-PROD-ENV-CLONE-DESIGN §3.3); helps consumer compute "did we run this where we should have" |
| `assertion_summary` per-result | inside each `results[]` entry | per-TC counts of pass/fail assertions (rolled up from `14_AGR`); enables drill-down without joining sheets |
| `mimt_run_id` (top-level) | top-level | when MI-M-T POST consumes this and assigns its own run_id; producer fills if known |
| `parity_divergence_detail` per-divergence | inside each result with parity_status==divergence | structured divergence info: which fws disagree, on which assertion, with which actual values |

Mark these explicitly in v1.0 producer/consumer code as `# v1.1 candidate` for trackability.

### §6.4 Schema-version handshake on POST (V2)

When `tools/tes_present.py --api-mode <mimt-url>` POSTs to MI-M-T:
- POST body MUST include `schema_version`
- MI-M-T MUST 415 (Unsupported Media Type) if it can't handle the version, with body `{"error": "schema_version_mismatch", "supported": ["1.0"]}`
- The `mimt-cli` retries down or surfaces the error; doesn't auto-degrade

This pattern keeps the cross-version negotiation explicit. Per MIMT-IMPORT-CONTRACT-DRAFT §4.2 the MI-M-T side will have its own version header but at v0.2 onward, NOT v0.1 (currently the runner backend is missing 5 CRUD routes per HANDOVER §1.2).

## §7. Open questions

| OQ# | Sev | Urg | Pri | Question | Resolve by |
|---|:---:|:---:|:---:|---|---|
| OQ-SCHEMA-01 | A | A | A | `frameworks` enum — is `playwright-api` (the API-only Playwright runner) a separate framework key OR a subtype of `playwright`? Recommend: separate key for clarity (different reporter shape; different test set). v1.0 enum: `playwright \| cypress \| selenium \| playwright-api \| postman` | v0.1 sign-off |
| OQ-SCHEMA-02 | A | A | A | `viewport` field — keep at per-TC level (current §3.2) OR move to per-(TC, fw) inside `evidence`? Different fws may use different viewports for the same TC. Recommend: per-(TC, fw) in `evidence.<fw>.viewport`; v1.0 keeps the convenience per-TC default for the dominant case. | v0.1 sign-off |
| OQ-SCHEMA-03 | B | A | A | `summary.pass_rate_*` precision — round to 2 decimals (current §3.6) OR keep raw float? Round-to-2 loses info; keep-raw spreads display logic to consumers. Recommend: round-to-2 in v1.0; consumers wanting precision read the counts and recompute. | v0.1 sign-off |
| OQ-SCHEMA-04 | A | A | A | `host.host` sanitization — internal hostnames may leak (e.g. `pete-thinkpad.local`) into committed JSONs. Should producer SHA-256 hash hostnames OR keep raw? Privacy vs traceability tradeoff. Recommend: keep raw for v1.0 (developer-only audit trail); migrate to opt-in hashing at v1.1 if exposure is a concern. | v0.1 sign-off |
| OQ-SCHEMA-05 | B | B | B | When `frameworks: ["playwright-api", "postman"]` (no UI fws), is `viewport` semantically meaningless? Recommend: emit as `null` for those rows; consumers tolerate. Document in v1.1 expansion. | v0.1.1 |
| OQ-SCHEMA-06 | A | A | A | Producer-side validator implementation — Pydantic models in `tools/cross_framework_schema.py` OR plain dict assertions in `consolidate_results.py`? Pydantic adds dep but gives JSON-Schema generation for free. Recommend: plain assertions for v1.0 (zero new deps); revisit at v1.0.1 if validation logic complexity grows. | v0.1.1 |
| OQ-SCHEMA-07 | C | C | C | When divergence happens, should producer emit a `bug_ref: "BUG-CP-{TC}-FRAMEWORK-DIVERGENCE-{auto-slug}"` placeholder OR leave `bug_ref: null` until human triages? Recommend: leave null; auto-slugs become bug-tracker noise. | v0.1.1 |
| OQ-SCHEMA-08 | B | A | A | Tool-version capture — should `host.tool_versions` be required (always emitted) for traceability OR optional (current)? Required gives audit trail but adds startup cost (npm/pip queries). Recommend: optional in v1.0; producers fill best-effort. | v0.1 sign-off |

Total: 8 OQs (OQ-SCHEMA-01..08). 4 to resolve before v0.1 sign-off (OQ-SCHEMA-01/02/03/04/08); 4 deferred to v0.1.1.

## §8. Cross-references

```
~/Documents/VibeCodeProjects/SUPIN/bouracka-tests/
│
├── _specs/
│   ├── CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.md                 [THIS FILE]
│   ├── TEST-EXECUTION-SUMMARY-FORMAT-v0.1-CS.md              [sister — TES sheet column mapping]
│   ├── TESTCASE-SPEC-FORMAT-v0.2.md                          [TC code regex source]
│   ├── TESTTARGET-LIST-FORMAT-v0.2.md                        [TT code regex source]
│   ├── CROSS-FRAMEWORK-PARITY-EXECUTION-v0.1-CS.md           [parity intent — per-fw run protocol]
│   ├── INTEGRATION-CONTRACTS-STRATEGY-v0.2.md                [drift sources — N8/AISPOV/zenID]
│   └── from-macbook/
│       ├── HANDOVER-THINKPAD-OPUS-CP-SUPIN-05-CONVERGED-2026-05-09.md  [§5.3 OQ-MB-14 + §5.4 mimt-governance roadmap]
│       ├── SYNCHRO-MACBOOK-FROM-OPUS-CP-SUPIN-05-FOLLOWUP-2026-05-08.md [§4.2 MIMT-IMPORT-CONTRACT-DRAFT]
│       └── (others)
│
├── tools/
│   ├── consolidate_results.py                                [v0.5.2 → migrating to v0.5.3 per §4.2]
│   ├── append_test_run_result.py                             [legacy UPSERT — wrapped by tes_present.py V0]
│   ├── (proposed) tes_present.py                             [V0 deliverable; consumes this schema]
│   ├── (proposed) tes_dashboard.py                           [V1 deliverable; consumes this schema]
│   └── (proposed) validate_cross_framework_schema.py         [v0.1.1 follow-up; reference validator]
│
└── runs/                                                     [output dir]
    ├── cross-framework-<env>-<date>.json                     [conforms to §2]
    ├── cross-framework-<env>-<date>.md                       [human view; per BOURACKA-TES-PRESENTATION-LAYER-DESIGN §3.1 Output 2]
    └── (V1) dashboard.html                                   [consumes JSONs]


~/Documents/VibeCodeProjects/_config/
├── BOURACKA-TES-PRESENTATION-LAYER-DESIGN-v0.1-2026-05-09.md  [§6.1 — Phase 1 prerequisite (THIS DOC)]
├── BOURACKA-PROD-ENV-CLONE-DESIGN-v0.1-2026-05-09.md          [§3 — env enum source]
└── (others)
```

## §9. Status footer

| Item | Value |
|------|-------|
| Document | `CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.md` |
| Position | `bouracka-tests/_specs/CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.md` |
| Version | v0.1.0 (binding from 2026-05-10) |
| Sections | 10 (use / scope / schema / fields / migration / validation / versioning / OQs / xref / footer) |
| Closes | OQ-MB-14 (per HANDOVER-THINKPAD-OPUS §5.3) |
| Phase 1 of | `_config/BOURACKA-TES-PRESENTATION-LAYER-DESIGN-v0.1-2026-05-09.md` §6.1 |
| Producer migration target | `tools/consolidate_results.py` v0.5.2 → v0.5.3 (per §4.2; ~2h ThinkPad-Sonnet session) |
| Consumer dependencies | `tools/tes_present.py` (V0), `tools/tes_dashboard.py` (V1), `mimt-cli/append-run-result --api-mode` (V2) |
| New OQs | 8 (OQ-SCHEMA-01..08); 4 to resolve before v0.1 sign-off; 4 deferred to v0.1.1 |
| Validator | reference Python validator deferred to v0.1.1 follow-up |
| JSON Schema (formal) | deferred to v0.1.1 (prose is source of truth in v0.1) |
| Status | v0.1 — ready for Opus sign-off; binding once 5 OQs resolved (01/02/03/04/08) |

---

*CROSS-FRAMEWORK-RESULT-SCHEMA-v0.1.md — 2026-05-10 — MacBook Cowork session — Sonnet (Track B Phase 1)*
