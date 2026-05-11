# Bouračka UI v0.1.0 — Diagnostics Playbook (EN)

**Audience:** testers on HP Elite SUPNB001 (or any tester laptop) who need to diagnose problems that aren't obviously the UI's fault — drift, integration mismatches, network egress, certificate trust, mock-vs-live ambiguity.
**Companion docs:** `OPERATOR-GUIDE.md` (how to use the UI) and `TROUBLESHOOTING.md` (what to do when the UI itself misbehaves). This playbook is the third leg: **what to do when the system around the UI misbehaves.**
**Optimised for:** the ThinkPad ↔ HP Elite transfer being labour-intensive (email only, ≤5 MB volumes per IOC packaging rules). Every section below tells you how to capture a structured finding that ships back in one or two emails.

**Confidence tags used in §3 and §4** (read first):

- ⌖ — **known**, captured in CP-SUPIN-03..04 analysis docs
- ◯ — **inferred**, best guess from recon; verify on first contact
- ✗ — **gap**, not captured yet; tester needs to fill in via DELTA-REPORT (§7)

---

## §1. System fingerprint — what to capture on first contact

`bouracka-ui` exposes `/api/diagnostics/snapshot` (top of `/runs` page → ⬇ Diagnostics button). It produces a ZIP containing:

| Entry | What it shows | Why you care |
|-------|---------------|--------------|
| `manifest.json` | Bundle version + timestamp + run_id (if any) | Identifies this snapshot uniquely; cite this hash when emailing back |
| `health.json` | Server + schema versions + workbook path + runs-dir path | Confirms the install resolved REPO_ROOT correctly (look for `bouracka-tests/` in paths, NOT `.venv/`) — see BUG-BUI-004 |
| `system/system.json` | OS version, hostname, Python version, free disk | Baseline for compatibility checks |
| `system/tool-versions.txt` | `npx`, `node`, `python`, `pytest`, `consolidate_results.py` discovery status | If anything red here, see §3 for what fails |
| `system/health.json` | Tool-availability snapshot (npx / playwright / cypress / consolidator detection) | Same data as `/about` page, captured into the bundle |
| `server-log.txt` (last 5000 lines) | Recent server stderr | Contains startup messages + any tracebacks |
| `README.md` | Self-describing bundle layout | Pete can re-import this without context |

**When to grab it:** before the first TST run on a new machine, after any "this is weird" moment, when emailing Pete a question about behaviour. The bundle is `~50 KB`, well under the 5 MB IOC-aware email limit.

---

## §2. Network reachability matrix — per environment

Each environment requires a specific set of egress paths. Failure to reach any required target produces a characteristic symptom in the bouracka-ui log. Use the table to map symptom → likely root cause.

> **Two-tier confidentiality split:** SUPIN-internal hostnames / IPs / cert details / mock URLs are deliberately NOT in this doc. They live in the **SUPIN-internal companion** (`DIAGNOSTICS-PLAYBOOK-SUPIN-INTERNAL.md`, maintained by Pete from the template at `_specs/SUPIN-INTERNAL-companion/`) which is distributed via SUPIN-controlled secure channels — direct handoff, encrypted USB, or SUPIN-internal email only. **NEVER request the SUPIN-internal companion through an external email relay.** The `<FILL-IN-LOCAL>` placeholders below are the seams where the two tiers connect: read this public doc + cross-reference the same-numbered row in the internal companion. If you don't have the companion on your HP Elite, ask Pete via SUPIN-internal channel.

| Env | Target (role) | Why | How to verify (PowerShell) | Symptom if blocked |
|-----|---------------|-----|----------------------------|---------------------|
| DEMO | `demo.bouracka.cz` (public, HTTPS 443) | Primary DEMO traffic | `Test-NetConnection demo.bouracka.cz -Port 443` | Cypress / Playwright connect-timeout |
| DEMO | `www.google.com/recaptcha/api2` (HTTPS) | reCAPTCHA challenge load | `Test-NetConnection www.google.com -Port 443` | reCAPTCHA never resolves; form submit hangs |
| DEMO | `fonts.googleapis.com` (HTTPS, optional) | Web fonts; site loads fine without | — | Cosmetic only |
| TST | `tst.bouracka.cz` (intranet, HTTPS 443) | Primary TST traffic; requires SUPIN LAN / VPN | `Test-NetConnection tst.bouracka.cz -Port 443` | Connection refused / timeout = NOT on right network |
| TST | `<FILL-IN-LOCAL>` — IS ČKP API host | Real ČKP backend integration | populate `_local-config.txt` | 5xx on POST /api/reports |
| TST | `<FILL-IN-LOCAL>` — AISPOV API host | Driver license lookup | populate `_local-config.txt` | TC step "verify driver" hangs |
| TST | `<FILL-IN-LOCAL>` — zenID host | ID document scanning service | populate `_local-config.txt` | "Cannot upload ID" error at photo step |
| TST | `<FILL-IN-LOCAL>` — N8 SMS gateway | Phone verification SMS | populate `_local-config.txt` | SMS code field stays empty; timeout |
| UAT | (same shape as TST, different hosts) | — | populate `_local-config.txt` | — |
| PROD | `www.bouracka.cz` (public, HTTPS 443, READ-ONLY tests only) | Production read-only smoke | `Test-NetConnection www.bouracka.cz -Port 443` | Same as DEMO |

**`_local-config.txt` convention** — create this file at the bouracka-tests root (NOT committed to git) and populate the `<FILL-IN-LOCAL>` placeholders for your specific tester install. Format:

```
# _local-config.txt — local-only env-specific hostnames
# Do NOT commit. Each tester laptop has its own values.
TST_CKP_API_HOST=...
TST_AISPOV_HOST=...
TST_ZENID_HOST=...
TST_N8_SMS_HOST=...
UAT_...=...
```

This file is read by the test scripts via the standard env-var loading pattern. Add it to `.gitignore` if it isn't already (it is in v0.1.0+).

---

## §3. Integration contracts — live vs mock per env

The DEMO environment is **substantially mocked**. TST is "real-ish" — some backends are live (staging), some are still mocked. PROD is fully live but read-only for testing. This table is the empirical record from CP-SUPIN-03..04 recon. **Tag legend in §0.**

| Integration | DEMO | TST | UAT | PROD | Notes |
|-------------|------|-----|-----|------|-------|
| **IS ČKP report API** (POST /api/reports) | ⌖ mocked via Mockoon — accepts any payload, returns success | ⌖ live (staging ČKP API) — schema-validates, returns real bug-IDs | ◯ live (UAT staging) | ⌖ live (PROD), read-only access via tests | DEMO mock accepts garbage; TST rejects malformed payloads → real schema testing happens here |
| **AISPOV driver lookup** | ⌖ mocked — returns fixture driver based on input ID pattern | ◯ live staging — real DB lookup; may reject unknown IDs | ✗ gap — verify on first TST→UAT pass | ⌖ live | TC-CP-A1 + ALT-2/3 path needs real-ish driver IDs in TST |
| **zenID ID-document scan** | ⌖ stubbed — file upload accepted, no actual OCR | ◯ live staging zenID — does real OCR; may fail on poor photos | ✗ gap | ⌖ live | DEMO photo-skip TCs pass trivially; TST photo TCs require legible photos |
| **N8 SMS gateway** | ⌖ no-op — SMS-code field auto-fills with `123456` | ◯ live N8 staging — real SMS sent to test phones | ✗ gap | ⌖ live | TST: requires real test SIM cards; configure `TST_N8_TEST_PHONES=...` |
| **reCAPTCHA v3** | ◯ enabled some days, disabled others (DEMO drift) | ⌖ enabled (KB-CY-001 known drift source) | ◯ likely enabled | ⌖ enabled | Major drift source — see §4 |
| **Cookie banner** | ⌖ present on first load; dismissible | ⌖ present | ◯ present | ⌖ present | Auto-dismissed by Cypress/Playwright in v0.4.7+ |
| **Mockoon mock server** | ⌖ runs locally during tests; ports `:3000`/`:3001` | ✗ N/A — TST uses real backends | ✗ N/A | ✗ N/A | If Mockoon is not running in DEMO, tests fail with `ECONNREFUSED` on mock endpoints |

**Where the gaps are (✗ rows):** UAT environment is least-explored; TST has lots of `◯` because we haven't run live yet. **The TST integration session Pete mentioned is what closes those gaps.** Capture each `◯ → ⌖ (verified live)` or `◯ → ✗ (broken, file BUG-*)` finding using §7's DELTA-REPORT.

---

## §4. Known drift patterns — symptom catalogue

When tests fail in a way that's NOT a real regression, it's usually drift. The bouracka-ui has a built-in drift forensic that flags some of these automatically (verdict = `skip-drift`). Others need manual recognition.

| Drift pattern | Symptom in test log | Root cause | Expected response | Reference |
|---------------|---------------------|------------|-------------------|-----------|
| **reCAPTCHA v3 invisible-challenge** | Form submit hangs at step "submit"; `submit` button stays disabled; no DOM change for >5s | Google challenge triggered; Cypress can't solve | `verdict = skip-drift`; do NOT file BUG; check drift forensic card on results page | KB-040 / BUG-CY-001 IPC-114 evidence |
| **AISPOV mock returns unexpected fixture** | Driver-lookup step succeeds but returned data doesn't match input ID | Mockoon fixture out-of-date with TC expectations | Update Mockoon fixture or update TC expectations | CP-SUPIN-03 STEP 4 + analyticke vstupy/ snippets |
| **zenID stub bypassed** | Photo upload succeeds with any file (even non-image) | DEMO mode skips real OCR | Expected on DEMO. On TST, if same passes, escalate. | CP-SUPIN-04 STEP 5 delta matrix |
| **N8 SMS auto-code `123456`** | SMS-code field already populated when reached | DEMO no-op gateway | Expected on DEMO. On TST/UAT, must come from real SMS. | CP-SUPIN-04 STEP 5 |
| **DEMO POST /api/reports 403** | ALT-9 fails with 403 Forbidden | DEMO API endpoint disabled some days | `verdict = skip-drift`; document day-of-occurrence | ALT-9 diagnosis 2026-05-XX |
| **Page error timeout chain** | a1-main / ALT-1/4/5 fail at "navigate to /error/timeout" | DEMO routing quirk | Apply v0.4.7 timeout-handler fix; if persists, escalate | `/error/timeout chain` diagnosis |
| **Cookie banner blocks click** | First click on any form field misses; banner intercepts | Banner not yet dismissed | Pre-test cookie-banner-dismiss runs automatically in v0.4.7+ | CP-SUPIN-04 STEP 23 |
| **TC selector strict-mode violation** | "ALT-6 200 000 Kč selector matches 2+ elements" | DEMO rendered multiple price labels | Use `.first()` or stricter selector | KB-CY-002 (existing) |

**Adding a new drift pattern:** if you spot a recurring failure that isn't in this table, capture via §7 DELTA-REPORT. Pete will fold it back into this catalogue in the next package iteration.

---

## §5. Diagnostic tools — in priority order

When something fails, walk this ladder top-to-bottom. Stop at the first level that gives you a clear answer.

1. **`/about` page in bouracka-ui** — instant tool-availability snapshot. `npx` red? Cypress isn't going to dispatch. `consolidate_results` red? REPO_ROOT mis-detected → see TROUBLESHOOTING §4 (c).
2. **Results page log tail (dispatch-failed view)** — the four candidate-causes bullet list points you at the right root cause for most failures (see TROUBLESHOOTING §4).
3. **`/api/diagnostics/snapshot` ZIP** — grab on any "this is weird" moment. ~50 KB. Attach to email when escalating.
4. **Browser DevTools — Network tab** — for any HTTP-level mystery: which requests fired, status codes, response times, CORS preflights. Press F12 → Network → reproduce the issue → screenshot or "Save all as HAR".
5. **Browser DevTools — Console tab** — for JS errors. The bouracka-ui SPA logs API errors to console.
6. **Trace bundle export (lightweight)** — Results page → ⬇ Export bundle. Gives envelope + log + manifest in one ZIP. Email back to Pete; he `/api/bundles/import`s on ThinkPad and has the full context in 30 seconds.
7. **Trace bundle export (full)** — same but adds videos + Cypress trace.zip. Several MB; may bump the IOC packaging limit; split into volumes if needed (see EMAIL-DELIVERABILITY-RULES if shipped separately).
8. **IPC-114 Chromium diagnostic methodology** — last resort for stubborn Cypress hangs. Launch Cypress headed, open Chrome DevTools, inspect IPC channel 114 for same-origin persistent connection state. Documented in BUG-CY-001 Round-4 evidence parked at `_specs/`.

---

## §6. Pre-flight checklist — before the first TST run on a new laptop

Walk this list once per laptop (or per major SUPIN network change). Cross off each item as you confirm.

- [ ] Laptop on SUPIN LAN or VPN (`ipconfig` shows expected internal subnet)
- [ ] `Test-NetConnection tst.bouracka.cz -Port 443` succeeds
- [ ] Each `<FILL-IN-LOCAL>` target in §2 row reachable (run the test for each row)
- [ ] Certificate trust: open `https://tst.bouracka.cz` in browser, no cert-error interstitial
- [ ] `_local-config.txt` populated with all required env-specific hostnames
- [ ] `bouracka-ui` started, `/about` page all tools green (or yellow with documented `BOURACKA_UI_DISPATCH_MODE=mock` override if real dispatch not needed)
- [ ] Diagnostics snapshot taken + saved as baseline (file as `baseline-snapshot-YYYY-MM-DD.zip` somewhere — proves "this is what 'working' looked like" if you need to A/B-compare later)
- [ ] One DEMO smoke test run successful (TC-CP-A1-MAIN-DEMO) to confirm UI plumbing works before pointing at TST
- [ ] One TST smoke test run — record exit codes per framework + any drift forensic flags
- [ ] If anything in the run differs from the §3 contract for TST, **DELTA-REPORT it** (next section) — don't assume it's "fine, probably a flaky test"

---

## §7. Delta-capture — how to ship a finding back to ThinkPad efficiently

### §7.1 For TC failures — trace bundle (in-band, preferred)

The trace bundle export is your default channel. It captures the envelope + log + manifest + (optionally) videos in a self-describing ZIP that Pete can `/api/bundles/import` to reproduce on ThinkPad.

Steps:
1. Reproduce the failure (or use the existing failed run from `/runs`)
2. On results page, click **⬇ Export bundle** (lightweight; ~50 KB) or **⬇ Export bundle (full)** if videos/traces help
3. Email the ZIP to Pete. **Subject line:** `bouracka-ui delta — <env> — <TC-code> — <YYYY-MM-DD>`
4. **Body:** one paragraph — what you expected vs. what you observed. No need to repeat the envelope contents; the bundle has them.

**Latency:** Pete imports the bundle, sees the full run state, no clarifying round-trip needed for the common case.

### §7.2 For non-TC findings — DELTA-REPORT plain-text template

Trace bundles don't capture: missing flows in the testplan, undocumented integration behaviour, certificate / network / proxy gaps, UAT/PROD env gaps from §3. For those, use this plain-text template. **Save as `DELTA-REPORT-YYYY-MM-DD-NN.txt`** (NN = serial number) and email back to Pete.

```
========================================================================
DELTA-REPORT v0.1
========================================================================
date_local:    YYYY-MM-DD HH:MM (CEST/CET)
tester:        <your name>
machine:       HP Elite SUPNB001 | other: <hostname>
network:       SUPIN LAN | VPN | external
env:           DEMO | TST | UAT | PROD-READONLY
TC code:       TC-CP-...   (or N/A if not a TC failure)
playbook ref:  §X of DIAGNOSTICS-PLAYBOOK that this contradicts (if any)

------------------------------------------------------------------------
WHAT I OBSERVED:
------------------------------------------------------------------------
<plain text, 2-10 sentences. Be specific. Cite exact error messages,
 timestamps, HTTP status codes, integration names.>

------------------------------------------------------------------------
WHAT I EXPECTED (per §X of playbook or TC-XXX expected behaviour):
------------------------------------------------------------------------
<plain text, 2-5 sentences. Cite the source of the expectation.>

------------------------------------------------------------------------
REPRODUCTION STEPS:
------------------------------------------------------------------------
1. <action>
2. <action>
3. <action>

------------------------------------------------------------------------
EVIDENCE ATTACHED (X what applies):
------------------------------------------------------------------------
[ ] bouracka-ui diagnostics snapshot ZIP (filename: ...)
[ ] trace bundle (lightweight) (filename: ...)
[ ] trace bundle (full) (filename: ...)
[ ] screenshot(s) (filenames: ...)
[ ] browser DevTools Network HAR export (filename: ...)
[ ] cypress video file (filename: ...)
[ ] cypress trace.zip (filename: ...)
[ ] none — live observation only

------------------------------------------------------------------------
HYPOTHESIS (optional, your best guess about root cause):
------------------------------------------------------------------------
<plain text, 1-3 sentences. OK to be tentative — Pete will refine on
 ThinkPad side. Examples: "smells like cert trust issue", "AISPOV
 fixture out-of-date", "TST has reCAPTCHA enabled where DEMO didn't".>

------------------------------------------------------------------------
URGENCY (X one):
------------------------------------------------------------------------
[ ] blocking — can't continue any testing until this is resolved
[ ] high   — blocks this TC but other TCs proceed
[ ] medium — produces wrong answer but not blocking
[ ] low    — cosmetic / nice to fix when convenient

========================================================================
```

**Latency:** one email round-trip; Pete folds the finding back into §3 / §4 in the next package iteration.

### §7.3 Sizing the email — IOC-aware packaging

Per existing SUPIN email scanner rules (EMAIL-DELIVERABILITY-RULES, separate doc):
- One email ≤ 5 MB
- ZIP attachments preferred over loose files
- Avoid filenames triggering AV heuristics (`patch`, `exploit`, `inject`, etc.)
- Multiple findings in one session → batch into one email + one parent ZIP if total < 5 MB

Trace-bundle lightweight (~50 KB) + diagnostics snapshot (~30 KB) + DELTA-REPORT.txt (~5 KB) easily fits one email.

---

## §8. Escalation matrix

Single-line edit per row when contacts get assigned. Default to "Pete" for all.

| Failure class | Symptom hint | Primary contact | Backup | Notes |
|---------------|--------------|-----------------|--------|-------|
| Bouračka-UI bug | UI itself misbehaves; not test data | Pete (`petr.yamyang@gmail.com`) | — | File BUG-BUI-NNN via UI Bugs page if accessible |
| Test data drift (reCAPTCHA, AISPOV mock, etc.) | Verdict `skip-drift` or unexpected mock response | Pete | — | DELTA-REPORT §7 |
| Network / cert / proxy | `Test-NetConnection` fails or cert-error interstitial | `<FILL-IN: SUPIN SecOps>` | Pete | Likely needs SUPIN-internal access change |
| ČKP backend down (TST/UAT/PROD) | 5xx on POST /api/reports across multiple TCs | `<FILL-IN: ČKP API ops>` | Pete | Capture timestamp + diagnostic snapshot |
| AISPOV backend down | Driver lookup hangs across multiple TCs | `<FILL-IN: AISPOV ops>` | Pete | DELTA-REPORT + timestamp |
| zenID backend down | ID upload step fails across multiple TCs | `<FILL-IN: zenID ops>` | Pete | DELTA-REPORT + sample file |
| N8 SMS gateway down | SMS code never arrives across multiple TCs | `<FILL-IN: N8 ops or telco>` | Pete | DELTA-REPORT + test phone number |
| HP Elite hardware / OS | Won't boot / pip install fails / WSL issues | `<FILL-IN: SUPIN IT>` | Pete | Include `system/system.json` from diagnostics |
| Anything ambiguous | Don't know what category | Pete | — | Default route; Pete triages |

---

## §9. Glossary

| Term | Meaning |
|------|---------|
| **AISPOV** | Driver / vehicle insurance database (SUPIN internal) |
| **bundle** | Trace-bundle ZIP exported via `/api/runs/{rid}/bundle` |
| **DELTA-REPORT** | Plain-text finding template per §7.2 |
| **DEMO** | `demo.bouracka.cz` — public, mostly-mocked environment |
| **drift** | A test failure that isn't a real regression; usually env-state or mock-fixture mismatch |
| **envelope** | The v0.1 cross-framework results JSON written by `tools/consolidate_results.py` |
| **IS ČKP** | Internal report system (Centrum Kybernetické Pohotovosti / similar; SUPIN-internal acronym) |
| **mockoon** | Local mock-server framework used in DEMO mode |
| **N8** | SMS verification gateway |
| **PROD** | `www.bouracka.cz` — production, read-only for tests |
| **REPO_ROOT** | bouracka-ui's auto-detected location of bouracka-tests/ (see BUG-BUI-004) |
| **skip-drift** | Verdict assigned when drift forensic detected a known-drift pattern |
| **TST** | `tst.bouracka.cz` — intranet test environment with real-ish backends |
| **UAT** | User-acceptance test environment (between TST and PROD) |
| **zenID** | ID document scanning + OCR service |

End of DIAGNOSTICS-PLAYBOOK.md
