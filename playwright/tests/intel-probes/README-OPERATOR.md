# Intel-probes — operator runbook

> **Audience.** Operator with temporary admin permissions on the ThinkPad.
> **Purpose.** Run the intel-probes Playwright suite to enrich the artefact
> set with data we can only collect from a real SUT (full enum payloads,
> bundle source, network traces, codelist DOM scrapes).

## §1. One-time setup (admin window)

```pwsh
# 1. Install Node.js (Profile-C → Node 20 LTS)
winget install OpenJS.NodeJS.LTS

# 2. Install repo dependencies
cd C:\Users\vitez\Documents\VibeCodeProjects\SUPIN\bouracka-tests
npm install

# 3. Install Playwright browsers
npx playwright install chromium

# 4. (Optional) install Cypress + TestCafe for CP-SUPIN-05 multi-framework
npm install --save-dev cypress testcafe
```

## §2. Run the read-only probes (safe — no SUT writes)

```pwsh
# All read-only probes (no POST /reports)
npx playwright test playwright/tests/intel-probes/01-enumeration-dump.spec.ts

# Inspect outputs
ls fixtures/intel-*
```

Reads:
- `/api/enumerations/insuranceCompanies` (200 — 13 entries)
- `/api/enumerations/vehicleBrands` (200 — 275 brands)
- 8× protected enumerations (assert 403)
- All Vite-hashed JS bundle files (Zod schemas + regexes + Czech strings)
- Rozcestník network trace

Writes:
- `fixtures/intel-YYYY-MM-DD/enums/{insuranceCompanies,vehicleBrands}.json`
- `fixtures/intel-YYYY-MM-DD/bundles/bundle-findings.json`
- `fixtures/intel-YYYY-MM-DD/traces/rozcestnik.json`

## §3. Run the deeper probes (creates a report — opt-in)

```pwsh
# Set the gate flag and run
$env:INTEL_PROBE_CREATE_REPORT = "1"
npx playwright test playwright/tests/intel-probes/02-codelist-scrape.spec.ts
$env:INTEL_PROBE_CREATE_REPORT = ""  # unset
```

This drives the wizard end-to-end (uses synthetic data) and scrapes the
DOM-rendered codelists that the SPA loads from its own bundle (which is
why `/api/enumerations/licenseCategories` returns 403 directly — it's
embedded in the JS).

## §4. After running — what to do with the harvested data

1. Review the JSON dumps in `fixtures/intel-YYYY-MM-DD/`.
2. Manually merge new findings into the canonical fixtures:
   - `fixtures/codelists-live-2026-05-06.yaml` — append any new codelists
   - `fixtures/api-endpoints-live-2026-05-06.yaml` — append any new endpoints
   - `fixtures/live-copy-strings.yaml` — append any new STR-* rows
3. If new validators surfaced from bundle reads → update
   `fixtures/field-definitions.yaml::F-NNN.rules`.
4. If new endpoints surfaced → update `recon/integrations/INT-008.md`.
5. Bump the workbook rev: `python tools/migrate_to_v04.py` (future).

## §5. Caveats

- These probes are **DEMO-only** until PROD-Bouračka access opens.
- The `INTEL_PROBE_CREATE_REPORT=1` gate exists because each run creates a
  report UUID server-side; data is purged by the SPA's bilateral-confirmation
  rule (per Phase 1 disclaimer) but it still consumes a database row.
- The bundle source-read parses Vite minified JS — the heuristic regexes
  are best-effort. False positives expected; review before committing
  any of the auto-extracted strings to canonical fixtures.
- Operator timezone matters: `TODAY` uses ISO-8601 UTC.

## §6. Status

| Item | Value |
|------|-------|
| Tests | 9 (5 in `01-enumeration-dump`, 4 in `02-codelist-scrape`) |
| Read-only count | 4 (TC-INTEL-001..004) |
| Opt-in count | 5 (TC-INTEL-005..009) |
| Status | v0.1 — author-time scaffold; first run pending operator admin window |
