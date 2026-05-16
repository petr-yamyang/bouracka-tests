# Sonnet return — Brief #006 integration probe expansion

**Branch.** `cp-supin-14-int-probe-expansion`
**Commit.** `6dc4b08`
**Smoke.** 11 targets probed; 4 SOAP FAIL (expected — no SUPIN VPN), 7 internet ALL PASS

---

## §10 Return checklist

### 1. Branch + SHAs
- Branch: `cp-supin-14-int-probe-expansion` from `main`
- Commit: `6dc4b08`

### 2. Files changed

| File | Change |
|------|--------|
| `delivery/SUPIN-SERVER-DROP-2026-05-13/recon-harness/int_recon.py` | +120 lines: `parse_host()`, `parse_port()`, `probe_http_get_json()`, `probe_http_head_with_referrer()`, `probe_https_tls_verify()`, `PROBE_FUNCTIONS` dict, rewritten `probe_target()`, `integration_coverage` block in `run_probes()` |
| `delivery/SUPIN-SERVER-DROP-2026-05-13/recon-harness/targets.json` | 4 → 11 entries; `probe_types` on all SOAP entries; 7 new internet targets |
| `delivery/SUPIN-SERVER-DROP-2026-05-13/recon-harness/README-CS.md` | v0.1.0 → v0.2.0; added §4 probe-type matrix, §5 pending endpoints; renumbered §6-§11 |
| `delivery/PETE-HP-ELITE-DROP-2026-05-13/recon-harness/int_recon.py` | Mirror |
| `delivery/PETE-HP-ELITE-DROP-2026-05-13/recon-harness/targets.json` | Mirror |
| `delivery/PETE-HP-ELITE-DROP-2026-05-13/recon-harness/README-CS.md` | Mirror |

### 3. Sandbox smoke output (abbreviated)

```
Targets: ['D8WS-STD', 'D8WS-TST', 'D5WS-STD', 'D5WS-TST',
          'INT-001-reCAPTCHA-api-js', 'INT-001-reCAPTCHA-siteverify',
          'INT-006-Azure-outage-feed', 'INT-007-gmaps-js',
          'INT-008-internal-api-reports',
          'INT-009-RUIAN-suggest', 'INT-009-RUIAN-vyhledavaci']

D8WS-STD:  tcp FAIL (timeout), http_head FAIL, wsdl_get FAIL, soap_fault FAIL  ← expected (no VPN)
D8WS-TST:  same
D5WS-STD:  same
D5WS-TST:  same

INT-001 reCAPTCHA api.js:    tcp PASS, https_tls PASS (HTTP 200), http_head PASS (HTTP 200)
INT-001 reCAPTCHA siteverify: tcp PASS, https_tls PASS (HTTP 200)
INT-006 Azure outage feed:   tcp PASS, https_tls PASS (HTTP 200), http_get_json PASS (outages key present)
INT-007 gmaps JS:            tcp PASS, https_tls PASS (HTTP 200), http_head PASS (HTTP 200)
INT-008 internal /api DEMO:  tcp PASS, https_tls PASS (HTTP 403), http_head PASS (HTTP 403)
INT-009 RUIAN suggest:       tcp PASS, https_tls PASS (HTTP 200), http_get_json PASS (suggestions present)
INT-009 RUIAN vyhledavaci:   tcp PASS, https_tls PASS (HTTP 200), http_get_json PASS (features present)
```

Exit code 0. Output JSON written to `outputs/RECON-LAPTOP-7697MAU5-<ts>.json`.

### 4. Target count
4 → 11 (7 new internet targets from INT-001/006/007/008/009)

### 5. README-CS.md probe-type matrix
Present at §4. Verified in committed file.

### 6. Out-of-scope findings

- `INT-008-internal-api-reports`: `demo.bouracka.cz/api/health` returns HTTP 403 (not 404). The `/api/health` path exists but requires auth or is IP-restricted. The `http_head` probe verdict is PASS (< 500), which is correct behavior. Pete may want to note this for INT-008 doc update.
- `INT-007 gmaps-js` versioned URL (`/64/11d/`) is live as of this run. URL may rotate with Google Maps releases — 404 is non-fatal per brief risk gate §7.2.

### 7. Deviations

- None. All 3 F-items implemented as specified.
- Old `probe_target()` had a `# If TCP failed, skip HTTP probes` guard; new dispatch-table approach does NOT skip on TCP fail. This matches the brief's §F-3 spec (iterate all probe_types without conditional skip). Internet targets can have TCP pass but TLS fail, so skipping would be wrong for them.

### 8. Pending: INT-002/003/004/005
No endpoint URLs available in recon docs. Documented in `targets.json → future_targets_pending_endpoints` and README-CS.md §5. Pete should chase Michal Ciberej for:
- INT-002: SMS gateway URL
- INT-003: SMTP relay hostname
- INT-004: AISPOV vehicle/driver registry URL (likely SUPIN-internal)
- INT-005: Geocoder URL (may overlap INT-007/INT-009)
