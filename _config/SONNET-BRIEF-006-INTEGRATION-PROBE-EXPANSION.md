# Sonnet brief — BRIEF-006: integration probe expansion (FR-K-006)

**Target Claude.** Sonnet 4.6 in Claude Code (terminal, stateless).
**Issued by.** Opus 4.7 session, 2026-05-15.
**Branch.** `cp-supin-14-int-probe-expansion`.
**Estimated effort.** ~3 hours.
**Reviewer.** Pete in Opus 4.7 session.
**Blocked by.** Nothing — independent extension of existing `recon-harness/int_recon.py`.

---

## 1. Goal in one paragraph

Today `int_recon.py` probes 4 endpoints: D8WS-STD/TST and D5WS-STD/TST. SUPIN integration surface is wider — recon docs INT-001..INT-009 catalog 9 additional integrations (reCAPTCHA, SMS gateway, SMTP, vehicle/driver registry, maps/geocoder, Azure outage feed, Google Maps JS, internal `/api/reports`, ČÚZK RÚIAN). This brief extends `int_recon.py`'s `targets.json` schema to cover all of them with probe types appropriate to each integration, plus introduces a new `expectation` field that records what a healthy probe should produce. Output: from one int_recon run on Pete's SUPIN-VPN-connected ThinkPad, a single JSON report covers every integration touch-point, ready to ingest back into Claude session for INT-001..INT-011 status updates.

---

## 2. Spec — read this BEFORE coding

1. `recon/integrations/INT-001.md` through `INT-011-D5WS-SEDN-lookup.md` — eleven recon docs with endpoint URLs, expected behaviors, evidence
2. `delivery/SUPIN-SERVER-DROP-2026-05-13/recon-harness/int_recon.py` — current probe harness (stdlib only, ~500 lines)
3. `delivery/SUPIN-SERVER-DROP-2026-05-13/recon-harness/targets.json` — current 4-target config
4. `delivery/SUPIN-SERVER-DROP-2026-05-13/recon-harness/README-CS.md` — current operator doc

---

## 3. Inputs / outputs

### Inputs

- Working `int_recon.py` (4 SOAP targets, 4 probe types: tcp_connect, http_head, wsdl_get, soap_fault_elicit)
- 11 recon docs as authoritative endpoint catalog

### Outputs

- Extended `targets.json` with 13 targets total (current 4 SOAP + 9 new from INT-001..009)
- Extended `int_recon.py` supporting 3 new probe types: `http_get_json`, `http_head_with_referrer`, `https_tls_verify`
- Extended README-CS.md documenting which probe runs against which integration
- Output JSON schema bumped to v0.2 (additive — old fields preserved, new fields added)

---

## 4. File boundaries

### Modify

- `delivery/SUPIN-SERVER-DROP-2026-05-13/recon-harness/int_recon.py` — add 3 probe functions + dispatch in `probe_target()`
- `delivery/SUPIN-SERVER-DROP-2026-05-13/recon-harness/targets.json` — add 9 new entries per §F-2
- `delivery/SUPIN-SERVER-DROP-2026-05-13/recon-harness/README-CS.md` — add probe-type matrix + per-INT notes
- `delivery/PETE-HP-ELITE-DROP-2026-05-13/recon-harness/*` — mirror changes (or symlink note)

### DO NOT touch

- `bouracka_ui/` — out of scope, separate rail
- Recon docs themselves — they're authoritative spec; if you find drift, note in §10
- Real SUPIN endpoints — read-only probes only, no auth, no payload

---

## 5. Functional requirements

### F-1. Three new probe types

```python
def probe_http_get_json(url: str) -> dict:
    """GET → parse response as JSON, validate top-level shape if 'expect_json_keys' given."""

def probe_http_head_with_referrer(url: str, referrer: str) -> dict:
    """HEAD with custom Referrer header (some integrations require non-empty referrer)."""

def probe_https_tls_verify(url: str) -> dict:
    """Like http_head but with strict TLS verification (refuse self-signed)."""
```

Each returns dict matching the existing probe schema (verdict, details, http_status, response_excerpt_head, duration_ms).

### F-2. New target entries in `targets.json`

```json
{
  "targets": [
    /* existing 4 SOAP D8WS+D5WS entries */
    {
      "target_id": "INT-001-reCAPTCHA-api-js",
      "url": "https://www.google.com/recaptcha/api.js",
      "expected_role": "STD (production)",
      "expected_service": "Google reCAPTCHA script load",
      "probe_types": ["tcp_connect", "https_tls_verify", "http_head"],
      "notes": "Per INT-001 — Bouracka registers reCAPTCHA via api.js; expect 200 + JS content."
    },
    {
      "target_id": "INT-001-reCAPTCHA-siteverify",
      "url": "https://www.google.com/recaptcha/api/siteverify",
      "expected_role": "STD (production)",
      "expected_service": "reCAPTCHA server-side verification",
      "probe_types": ["tcp_connect", "https_tls_verify"],
      "notes": "POST-only endpoint; HEAD likely 405. TLS handshake is the meaningful probe."
    },
    {
      "target_id": "INT-006-Azure-outage-feed",
      "url": "https://bourackaodstavky78861.z6.web.core.windows.net/odstavky.json",
      "expected_role": "STD (production)",
      "expected_service": "Azure SWA outage announcements JSON feed",
      "probe_types": ["tcp_connect", "https_tls_verify", "http_get_json"],
      "expect_json_keys": ["outages"],
      "notes": "Per INT-006 — must return JSON; bouracka polls this for outage banner."
    },
    {
      "target_id": "INT-007-gmaps-js",
      "url": "https://maps.googleapis.com/maps-api-v3/api/js/64/11d/intl/en_gb/common.js",
      "expected_role": "STD (production)",
      "expected_service": "Google Maps JavaScript API bundle",
      "probe_types": ["tcp_connect", "https_tls_verify", "http_head"],
      "notes": "Per INT-007 — versioned bundle URL; 200 expected. Maps API key is observed in production."
    },
    {
      "target_id": "INT-008-internal-api-reports",
      "url": "https://demo.bouracka.cz/api/health",
      "expected_role": "STD (DEMO tier)",
      "expected_service": "Internal /api REST surface — public DEMO",
      "probe_types": ["tcp_connect", "https_tls_verify", "http_head"],
      "notes": "Per INT-008 — bouracka's own /api/. health endpoint guess; if 404, try /api/reports."
    },
    {
      "target_id": "INT-009-RUIAN-suggest",
      "url": "https://ags.cuzk.cz/arcgis/rest/services/RUIAN/MapServer/exts/GeocodeSOE/tables/1/suggest?text=Praha&f=json",
      "expected_role": "STD (production)",
      "expected_service": "ČÚZK RÚIAN address autocomplete",
      "probe_types": ["tcp_connect", "https_tls_verify", "http_get_json"],
      "expect_json_keys": ["suggestions"],
      "notes": "Per INT-009 — autocomplete with sample query 'Praha'; should return suggestions array."
    },
    {
      "target_id": "INT-009-RUIAN-vyhledavaci",
      "url": "https://ags.cuzk.cz/arcgis/rest/services/RUIAN/Vyhledavaci_sluzba_nad_daty_RUIAN/MapServer/1/query?where=1%3D1&outFields=*&f=json&resultRecordCount=1",
      "expected_role": "STD (production)",
      "expected_service": "ČÚZK RÚIAN address full-resolution query",
      "probe_types": ["tcp_connect", "https_tls_verify", "http_get_json"],
      "expect_json_keys": ["features"],
      "notes": "Per INT-009 — record-count limited to 1 to avoid heavy query."
    }
  ],
  "future_targets_pending_endpoints": [
    "INT-002 SMS gateway — endpoint URL not yet documented; Michal Ciberej follow-up",
    "INT-003 SMTP — gateway URL not yet documented",
    "INT-004 Vehicle/driver registry (AISPOV) — endpoint URL not yet documented; same SUPIN-internal network as D8WS",
    "INT-005 Maps/geocoder for accident location — endpoint URL not yet documented (may overlap INT-007/INT-009)"
  ]
}
```

INT-002, INT-003, INT-004, INT-005 are NOT yet added because the recon docs don't have concrete endpoint URLs. Document them in `future_targets_pending_endpoints` so Pete can extend after SUPIN follow-up.

### F-3. Probe-type dispatch

In `probe_target()`, replace the hardcoded 4-probe sequence with one driven by the target's `probe_types` list:

```python
PROBE_FUNCTIONS = {
    "tcp_connect":           lambda t: probe_tcp(parse_host(t["url"]), parse_port(t["url"])),
    "http_head":             lambda t: probe_http_head(t["url"]),
    "http_head_with_referrer": lambda t: probe_http_head_with_referrer(t["url"], t.get("referrer", "")),
    "http_get_json":         lambda t: probe_http_get_json(t["url"], t.get("expect_json_keys", [])),
    "https_tls_verify":      lambda t: probe_https_tls_verify(t["url"]),
    "wsdl_get":              lambda t: probe_wsdl(t["url"]),
    "soap_fault_elicit":     lambda t: probe_soap_fault_elicit(t["url"]),
}

def probe_target(target):
    results = []
    for ptype in target.get("probe_types", ["tcp_connect", "http_head"]):
        if ptype not in PROBE_FUNCTIONS:
            results.append({"probe_id": ptype, "verdict": "SKIP", "details": "unknown probe type"})
            continue
        results.append(PROBE_FUNCTIONS[ptype](target))
    return {"target_id": target["target_id"], "url": target["url"],
            "expected_role": target.get("expected_role"),
            "expected_service": target.get("expected_service"),
            "probes": results}
```

### F-4. Report schema v0.2 — additive

Add to output JSON top-level:

```json
{
  "schema_version": "0.2",
  "recon_id": "...",
  "host_env": {...},
  "targets": [...],
  "questions_answered": {...},
  "integration_coverage": {
    "documented_in_INT_docs": 11,
    "probed_in_this_run": 7,
    "missing_endpoints": ["INT-002", "INT-003", "INT-004", "INT-005"],
    "fully_reachable": [...],
    "tls_warning": [...]
  }
}
```

### F-5. README-CS.md additions

Add a §4 "Probe-type matrix":

```markdown
| Target | tcp | http_head | https_tls | http_get_json | wsdl_get | soap_fault |
|--------|:---:|:---------:|:---------:|:-------------:|:--------:|:----------:|
| D8WS-STD/TST + D5WS-STD/TST | ✓ | ✓ |   |   | ✓ | ✓ |
| INT-001 reCAPTCHA api.js | ✓ | ✓ | ✓ |   |   |   |
| INT-001 siteverify | ✓ |   | ✓ |   |   |   |
| INT-006 Azure outage feed | ✓ | ✓ | ✓ | ✓ |   |   |
| INT-007 gmaps JS | ✓ | ✓ | ✓ |   |   |   |
| INT-008 internal /api | ✓ | ✓ | ✓ |   |   |   |
| INT-009 RUIAN suggest | ✓ |   | ✓ | ✓ |   |   |
| INT-009 RUIAN vyhledavaci | ✓ |   | ✓ | ✓ |   |   |
```

Plus §5 "Pending endpoints" section listing INT-002, 003, 004, 005 with the followup-with-Michal note.

---

## 6. Tests

Run `python int_recon.py probe-all` from the recon-harness dir on a machine without SUPIN reach. Expected:

- 4 SOAP targets: TCP FAIL (172.16.* unreachable from non-VPN)
- 5 internet-reachable targets (reCAPTCHA, Azure outage, gmaps, demo /api, RÚIAN x2): TCP PASS, TLS PASS, http_head/json results
- Pete runs on VPN: all 4 SOAP healthy + all 5 internet healthy

No automated tests inside the suite — int_recon is a runtime tool; verification is operator-side.

---

## 7. Risk gates — STOP and report

1. **INT-006 / INT-009 endpoints have rate limits** that get hit by probe — be conservative, single-call only, no retry.
2. **gmaps versioned URL stale** — INT-007's exact bundle URL may rotate. If 404, just record + don't halt.
3. **RÚIAN ChÚZK serves SOAP NOT REST** for some queries — verify URL is REST + JSON (the `?f=json` query string forces it).
4. **reCAPTCHA TLS pinning** — probe should NOT use `--insecure`; Google strict-TLS is the whole point.

---

## 8. Return checklist

1. Branch + SHAs
2. Files changed (3-4 modify, 0 create)
3. Output of `python int_recon.py probe-all` from sandbox (FAIL for SOAP, PASS for internet targets)
4. Updated targets.json count: 4 → 11
5. README-CS.md §4 probe-type matrix verified present
6. Out-of-scope findings (e.g., if INT docs need follow-up edits)
7. Deviations
8. Pending: INT-002/003/004/005 endpoints — flag for Pete to chase Michal Ciberej

---

## 9. Don't-go-beyond

- Don't add INT-002/003/004/005 with guessed URLs — wait for SUPIN follow-up
- Don't add auth/credentials — probes stay read-only, no headers
- Don't integrate probes into bouracka-ui server route — recon stays standalone
- Don't add retries — fail-once-report-clearly discipline
- Don't add async — sequential probes are fine (whole run < 30s expected)

---

## 10. Acceptance

- 11 targets in targets.json (was 4)
- 7 probe types supported (was 4)
- Output JSON has schema_version: "0.2" + integration_coverage block
- README-CS.md has probe matrix + pending endpoints section
- Sandbox run produces expected pattern (SOAP fail, internet pass)
- Branch ready for merge

---

**End of BRIEF-006.**
