# Public-visibility audit pre first push — v0.1 CS

> **Trigger.** 2026-05-07 mid-session: Pete created
> `github.com/petr-yamyang/bouracka-tests` as **PUBLIC repo**. Need to verify
> no sensitive content goes public on first push.
>
> **Cíl.** Per-item recommendation: KEEP / SCRUB / EXCLUDE. Pete final word
> on judgement calls.

---

## §1. Audit summary — what's safe vs sensitive

| Category | Items | Recommendation |
|----------|-------|----------------|
| **Internal hostnames** | `SUPNB001`, user `petr.zemla` | SCRUB nebo EXCLUDE — see §2.1 |
| **ČKP internal infrastructure** | `AISPOV` / `B3WS` / `P3WS` / `D8WS` / `SEDN` / `AIS ČKP` / `ROB` / `CRŘ via ISSS` | KEEP **but** consider abstraction — see §2.2 |
| **DEMO drift forensic data** | `correlationId`, `x-azure-ref`, full request/response shapes | KEEP **with redaction** — see §2.3 |
| **Real Czech insurance company emails** | `regresy@allianz.cz`, `bouracka@slavia-pojistovna.cz`, etc. | KEEP — already public on bouracka.cz |
| **Pete's gmail** | `petr.yamyang@gmail.com` | KEEP — already public via GitHub account |
| **Test photos (164 MB)** | `analyticke vstupy/test-data-snippets/` | EXCLUDE — already gitignored, lives outside repo root |
| **SPECIMEN OP card MRZ data** | RČ 816008/0610, address Trmice | KEEP — confirmed SPECIMEN/VZOR card, no real PII |
| **Older Excel revisions** | v0.1..v0.4.1 | EXCLUDE via .gitignore — superseded |
| **`archive/obsolete/` folder** | 100+ files of superseded docs | EXCLUDE via .gitignore — pollution |
| **`delivery/` folder** | build outputs, ZIPs | EXCLUDE via .gitignore — regenerable |
| **`runs/` folder** | local test run logs | EXCLUDE via .gitignore — regenerable |
| **License** | NONE present | ADD `LICENSE` (MIT) — see §2.4 |
| **README.md (top-level English)** | NOT present (only README-CS + README-EN; both Czech-context) | ADD top-level `README.md` for OSS audience — see §2.5 |

## §2. Per-item recommendations

### §2.1 Internal hostnames — `SUPNB001` + `petr.zemla`

**Where:**
- `_specs/THREE-DEVICE-PLAN-CS.md` (CURRENT in repo) — explicit references
- `_install/INSTALL-PLAN-SUPNB-v0.1.md` — has it in the title
- `_install/SECOPS-COMPONENTS-CS.md` — references throughout
- `archive/obsolete/...` — superseded copies (will be excluded via .gitignore)

**Recommendation:**

| File | Action |
|------|--------|
| `_specs/THREE-DEVICE-PLAN-CS.md` | **SCRUB** — replace `SUPNB001` → `<test-runner-host>`; `petr.zemla` → `<test-runner-user>`. Keep doc itself (useful for governance). |
| `_install/INSTALL-PLAN-SUPNB-v0.1.md` | **EXCLUDE via .gitignore** (already added) — too SUPIN-specific for OSS public; keep in private repo if needed |
| `_install/SECOPS-COMPONENTS-CS.md` | **EXCLUDE via .gitignore** (already added) — ČKP-specific compliance doc; not relevant to OSS users |
| `archive/obsolete/` | **EXCLUDE via .gitignore** (already added) |

**Why:** these identifiers correlate to actual SUPIN/ČKP corporate setup.
Public exposure offers no upside; minor risk (info gathering / social
engineering basis).

### §2.2 ČKP internal infrastructure references (`AISPOV`, `B3WS`, etc.)

**Where:** `recon/ARCHITECTURE-OVERVIEW-v0.1-CS.md` (8 numbered flows + IS ČKP map)

**Recommendation:** **KEEP, but Pete confirms.** Three perspectives:

1. **Open-source argument for KEEP:** The architecture is reverse-engineered
   from publicly available Bouračka.cz behavior + public Pete-shared diagram.
   No customer-confidential breach. Educational value high (illustrates real
   insurance/automotive ČKP ecosystem for OSS testing methodology).

2. **Conservative argument for ABSTRACT:** Replace concrete names with
   role-based abstractions:
   - `AISPOV (Bouračka)` → `Backend façade #1`
   - `AIS ČKP` → `Master registry`
   - `B3WS / P3WS` → `Vehicle WS aspect 1/2`
   - `D8WS` → `Insurer forwarding WS`
   - `SEDN` → `Secure document network`
   - `ROB` → `Population registry`
   - `CRŘ via ISSS` → `Driver registry via state interop bus`

3. **Hybrid:** Keep one concrete reference doc (this one), publish abstracted
   version as `_specs/ARCHITECTURE-PATTERN-OSS-v0.1.md` for community.

**Default recommendation: KEEP CONCRETE.** Pete already shared the original
diagram inline; reverse-engineered version no more sensitive than the source.
ČKP staff would recognize this as accurately describing publicly observable
behavior. **Override if Pete prefers abstract.**

### §2.3 DEMO drift forensic — correlation IDs + Azure refs

**Where:** `recon/DRIFT-2026-05-07-DEMO-POST-REPORTS-CS.md` §3.1 + §3.2

**Specific items:**
- `x-correlation-id: 2a43fe78-a8ac-4d91-b261-33133d3ef577`
- `x-azure-ref: 20260507T125429Z-1764578ff7drfrmthC1CPHf84g0000001wmg0000000092d6`
- Full reCAPTCHA token (~2400 chars)

**Recommendation:** **REDACT specific values; keep schema/shape.** The point
of the doc is the shape of the request/response and the diagnosis logic, not
the specific IDs.

Replace with:
- `x-correlation-id: <uuid-redacted>`
- `x-azure-ref: <azure-ref-redacted>`
- `x-captcha-token: <2400-char-google-recaptcha-v3-token-redacted>`

Server response body keep as-is — it's a generic Spring Boot 403 shape.

**Effort:** 5-minute search-and-replace.

### §2.4 LICENSE — add MIT

**Where:** `LICENSE` (NEW file at repo root)

**Recommendation:** MIT — most permissive, OSS-standard, enterprise-friendly.
Already added by this session. Pete can swap to Apache 2.0 if preferred (more
explicit patent grant).

### §2.5 README.md top-level — add OSS-friendly intro

**Where:** `README.md` (NEW file at repo root) — currently only Czech
README-CS + README-EN exist (both with internal context).

**Recommendation:** Author one English `README.md` with:
- One-paragraph project intro for OSS audience
- "What this is": real-world testing project against a Czech traffic-accident
  self-record web app, used as MI-M-T methodology reference impl
- "What this is not": NOT a test framework; it's a SUT-specific test suite +
  governance methodology
- Quick start: `py bouracka.py setup; py bouracka.py test`
- Link to `_specs/CP-SUPIN-05-PLAN-CS.md` for the strategic context
- Link to `LICENSE` (MIT)
- Link to `mimt-simple` repo (TBD when created)

## §3. Suggested .gitignore additions (already applied)

```gitignore
# Workspace artifacts NOT to push to public repo
archive/                                    # superseded analytical/automation snapshots
delivery/                                   # build outputs (already covered partially above)
runs/                                       # local test run logs
bouracka-results-*.zip                      # local test result bundles

# Older Excel TestPlan revisions — keep only latest
BOURACKA-TESTPLAN-v0.1.xlsx
BOURACKA-TESTPLAN-v0.2.xlsx
BOURACKA-TESTPLAN-v0.3.xlsx
BOURACKA-TESTPLAN-v0.3.1.xlsx
BOURACKA-TESTPLAN-v0.3.2.xlsx
BOURACKA-TESTPLAN-v0.4.0.xlsx
BOURACKA-TESTPLAN-v0.4.1.xlsx
.~lock.*

# Sensitive — exclude from PUBLIC repo
_install/INSTALL-PLAN-SUPNB-v0.1.md         # contains SUPNB001 hostname + petr.zemla user
_install/SECOPS-COMPONENTS-CS.md             # ČKP SecOps audit doc — internal
recon/raw/                                  # raw transcripts may contain unredacted operator data
```

## §4. Pre-push action checklist

Before `git push -u origin main`:

- [x] `LICENSE` (MIT) added to repo root
- [x] `.gitignore` updated with sensitive-content exclusions
- [x] **`_specs/THREE-DEVICE-PLAN-CS.md`** scrubbed (placeholders applied)
- [x] **`_specs/CIL-2-ENABLEMENT-v0.1-CS.md`** scrubbed
- [x] **`_specs/CP-SUPIN-05-PLAN-CS.md`** scrubbed
- [x] **`_specs/DOCUMENTATION-POLICY-v0.1.md`** scrubbed
- [x] **`recon/DRIFT-2026-05-07-DEMO-POST-REPORTS-CS.md`** correlation-id + azure-ref redacted
- [x] **`README.md`** (top-level English) added — OSS-friendly intro
- [ ] **Pete decision** on §2.2 (keep ČKP names concrete OR abstract) — DEFAULT KEEP
- [ ] **Pete-side execution**: `git init` + 10-commit sequence per `_specs/GIT-SYNC-CHECKLIST-v0.1-CS.md` §2 + push + tag v0.5.0
- [ ] **Pete-side post-push**: enable Dependabot + Secret scanning + Push protection in repo Settings

## §5. After-push monitoring

GitHub public repo enables:
- **GitHub Secret Scanning** — auto-scans for known credential patterns; will alert if any leaked
- **Dependabot** — auto-PRs for vulnerable npm dependencies
- **Code scanning (CodeQL)** — optional, free for public repos

**Recommendation:** Enable all three in repo Settings > Security tab after first push.

## §6. Status

| Item | Hodnota |
|------|---------|
| Doc | `_specs/PUBLIC-VISIBILITY-AUDIT-v0.1-CS.md` |
| Verze | v0.1 |
| Datum | 2026-05-07 mid-session |
| Repo | `github.com/petr-yamyang/bouracka-tests` (public) |
| Audit findings | 4 categories needing action; 2 of 6 pre-push items DONE |
| Pete decisions pending | (1) §2.2 abstract or concrete; (2) §2.5 README content review |
| Status | audit complete; ready for Pete-side push after final scrub |
