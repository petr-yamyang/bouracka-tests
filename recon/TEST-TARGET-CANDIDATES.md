# TEST-TARGET-CANDIDATES — CP-SUPIN-02 — 2026-05-05 (rev 2)

> **Rev 2 supersedes rev 1.** Per user direction 2026-05-05 (responding
> to OQ-CP-12): authentication on bouracka.cz is **implicit, via
> registration of existing IDs** — anybody with valid IDs relevant to
> Czech governmental registers (OP / ŘP / SPZ → register lookup) can use
> the app. The principal user-journey shape is therefore one cohesive
> flow with three scenario flavors:
>   1. **Happy-day** (valid IDs + valid eligibility + accepted OTPs)
>   2. **Exception states** (recoverable mid-flow failures)
>   3. **Negatively-ending** (irrecoverable failures — invalid IDs,
>      eligibility violations, regulatory interlock)
>
> **Release 1 (R1) covers JUST these three scenario flavors** (plus the
> implicit-ID-auth mechanic that gates them). Other test surfaces are
> identified below as R2+ and developed only when info becomes available
> — per user "release 1 covers just these scenarios; other should be
> identified but developed when information available, later".
>
> Per user direction in same message: **public approach to
> `tst.bouracka.cz` and `tst.demo.bouracka.cz` will not be allowed**.
> Recon for the dev side runs through the connected Chrome browser
> + publicly-available documentation (ČKP user manual + secondary
> media). Drives against `tst.*` happen on SUPIN tester laptops only,
> per scope C-1 / C-2.

> R-CAST-1 binding: every TestTarget is tagged with
> `decomposition_kind` + `component_ref` OR `behaviour_ref` +
> `coverage_basis`. R-STRUCT-1 — this rev's NEW / REPLACED / UNCHANGED
> block is in §3.

---

## §1. Release 1 (R1) — develop NOW

These four TTs together cover the user's binding R1 envelope. They
overlay one cohesive wizard journey, decomposed by scenario flavor for
testing isolation.

### TT-CP-R1-001 — Implicit ID-based authentication via Czech governmental registers

```
DECOMPOSITION_KIND: behaviour
BEHAVIOUR_REF:      authenticate-user-via-id-registers
COVERAGE_BASIS:     This IS the SUT's authentication mechanism per user
                    direction 2026-05-05. There is NO traditional login.
                    Identity is established implicitly by photographing
                    (or entering) OP / ŘP / SPZ; the system validates
                    against Czech governmental registers (občanský
                    průkaz registr, řidičský průkaz registr, registr
                    silničních vozidel) via INT-004. R1 must exercise:
                    valid-IDs happy (round-trip → auto-fill rendered),
                    invalid-IDs negative (lookup fails → terminate),
                    register-server-down recoverable (timeout → retry).
ENV_COVERAGE:       TST + DMO (NOT public — registry round-trip not
                    driveable from outside SUPIN)
PRIORITY:           Sev=A / Urg=A / Pri=A
RELEASE:            R1
RELATED INTEGRATIONS: INT-004 (registry lookup primary)
```

### TT-CP-R1-002 — Wizard happy-day end-to-end (post-ID-auth)

```
DECOMPOSITION_KIND: behaviour
BEHAVIOUR_REF:      submit-traffic-accident-record-happy
COVERAGE_BASIS:     The full happy path after ID-auth succeeds: telefonní
                    čísla obou účastníků → OP/ŘP foto + auto-fill
                    confirm → SPZ foto + vehicle-registry confirm →
                    poškození foto → místo nehody (mapa nebo GPS) →
                    review summary → SMS-OTP both drivers → submit →
                    e-mail dispatch with signed PDF. Per ČKP secondary
                    sources: end-to-end runtime ~10–20 min for a real
                    user; tests should complete within env-config'd
                    timeout. All five integrations
                    (reCAPTCHA / SMS / SMTP / registry / maps) exercised.
ENV_COVERAGE:       TST + DMO
PRIORITY:           Sev=A / Urg=A / Pri=A
RELEASE:            R1
RELATED INTEGRATIONS: INT-001..005 (all five)
```

### TT-CP-R1-003 — Wizard exception states (recoverable)

```
DECOMPOSITION_KIND: behaviour
BEHAVIOUR_REF:      recover-from-wizard-exception
COVERAGE_BASIS:     Mid-flow failures that the user can recover from
                    without losing wizard state: OTP retry (wrong code →
                    re-enter), OCR retry (unreadable doc → re-photograph
                    or manual entry), SMS-resend (didn't arrive → resend
                    button), server timeout (transient 5xx → retry),
                    location-adjust (wrong pin → re-pin). On each:
                    state must be preserved, error message in CS,
                    submit eventually succeeds.
ENV_COVERAGE:       TST + DMO
PRIORITY:           Sev=A / Urg=A / Pri=A
RELEASE:            R1
RELATED INTEGRATIONS: INT-002 (SMS retry primary) + INT-004 (OCR retry)
                      + INT-005 (location adjust)
```

### TT-CP-R1-004 — Wizard negatively-ending scenarios (irrecoverable)

```
DECOMPOSITION_KIND: behaviour
BEHAVIOUR_REF:      terminate-wizard-on-irrecoverable-failure
COVERAGE_BASIS:     Failures where the wizard must halt and present a
                    user-actionable next step (call police, call
                    insurer, contact ČKP). Branches: invalid IDs
                    (register lookup returns 'not found' → terminate
                    early); eligibility violation (damage > 200 000 Kč,
                    injuries reported, accident outside ČR → terminate
                    with regulatory message); ID-validation: blocked
                    or expired ŘP, vozidlo není v registru; OTP
                    exhaustion (N retries failed → terminate);
                    eligibility self-disclosure during wizard
                    (user reports the police-call interlock applies
                    → terminate with redirect to tel:158).
                    Each terminator must surface a CS message, NOT
                    silently accept, NOT corrupt server state, and
                    leave the user with a clear next step.
ENV_COVERAGE:       TST + DMO
PRIORITY:           Sev=A / Urg=A / Pri=A
RELEASE:            R1
RELATED INTEGRATIONS: INT-004 (lookup-not-found is the primary
                      negative-ending branch); INT-001 (reCAPTCHA fail
                      where applicable)
```

---

## §2. Release 2+ (R2+) — IDENTIFIED ONLY; develop later when info available

Per user direction: identify but do NOT develop yet. These are public-side
or boundary surfaces that are not part of the wizard scenario envelope
and lack tester-laptop info to scope concretely.

| ID | Surface | Decomposition | Why deferred |
|----|---------|---------------|--------------|
| TT-CP-R2-001 | Wizard entry gateway page (`/formular`) — smoke | page | Pre-ID-auth surface; outside R1 scenario envelope |
| TT-CP-R2-002 | Police-call interlock decision branch (`/formular` panel) | behaviour | Upstream of ID-auth; regulatory-grade but not in R1 envelope. Note: an EQUIVALENT terminator exists IN-WIZARD as part of TT-CP-R1-004 (user self-discloses interlock condition mid-wizard) — that part stays R1 |
| TT-CP-R2-003 | FAQ taxonomy + content (`/faq`) — smoke | page | Cheap "first-scenario" smoke for tester-laptop bring-up; not in R1 envelope; useful as a Gate-1 install-policy validator on tester laptops |
| TT-CP-R2-004 | Header / hamburger / brand-link cross-page component | component | Mobile-first AMENDMENT 2 sweep target; cross-cuts all pages but no specific R1 behaviour-link |
| TT-CP-R2-005 | Landing page (`/`) — marketing surface smoke | page | Pre-ID-auth surface; SCR-001 |
| TT-CP-R2-006 | GDPR / personal-data page (`/formular/personal-data`) | page | Static doc page; SCR-005 (deferred recon) |
| TT-CP-R2-007 | Cookie banner first-visit | component | Cross-cutting first-visit-only behaviour; one-shot smoke |

R2+ TTs each carry an §5b.1 sub-block hint here (decomposition + brief
basis) but are NOT seeded into Excel `01_TestTargets` until they're
promoted into a future iteration.

---

## §3. NEW / REPLACED / UNCHANGED (R-STRUCT-1)

### NEW

- TT-CP-R1-001..004 (4 R1 TestTargets — implicit ID-auth + happy + exception + negative-ending)
- TT-CP-R2-001..007 (7 R2+ TestTargets identified for later)
- Resolution markers for OQ-CP-11/12/14/15 in §4

### REPLACED

- Previous TT-CP-001..006 from rev 1 are **REPLACED** by the R1/R2 split:
  - rev1 TT-CP-001 (gateway page smoke) → R2 (TT-CP-R2-001)
  - rev1 TT-CP-002 (police-call interlock) → split: in-wizard self-disclosure stays R1 (folded into TT-CP-R1-004); upstream `/formular` panel decision stays R2 (TT-CP-R2-002)
  - rev1 TT-CP-003 (wizard happy E2E) → TT-CP-R1-002
  - rev1 TT-CP-004 (wizard failure envelope) → split: recoverable → TT-CP-R1-003; irrecoverable → TT-CP-R1-004
  - rev1 TT-CP-005 (FAQ smoke) → R2 (TT-CP-R2-003)
  - rev1 TT-CP-006 (header/hamburger) → R2 (TT-CP-R2-004)

### UNCHANGED

- The 5 integrations (INT-001..005); all five are exercised by R1 TTs.
- The 4 SCR-NNN screen recons (SCR-001..004); they remain accurate.
- The 5 FLW-NNN flow drafts; FLW-003 + FLW-004 are now mapped to R1
  TTs (003→R1-002, 004→R1-003+R1-004 split).
- The Excel column-block schema (ItemBase + entity-specific tail).
- All binding rules (R-METH, R-STRUCT, R-CAST, R-FAIL, mobile-first,
  Czech-first, priority matrix).

---

## §4. OQ resolutions — closed by user message 2026-05-05

| OQ | Status | Resolution |
|----|:------:|------------|
| OQ-CP-11 | **closed** | Public approach to `tst.bouracka.cz` + `tst.demo.bouracka.cz` is NOT allowed. Recon runs through the connected Chrome browser + publicly-available documentation only. The Cowork sandbox egress allowlist remains as-is — egress is not the bottleneck because there's no permitted destination either way. |
| OQ-CP-12 | **closed** | Authentication is **implicit, via registration of existing IDs** — valid OP / ŘP / SPZ → register lookup → auto-fill. No traditional login surface exists or will exist. R1 covers happy-day + exception states + negatively-ending. TC-CP-001..004 re-mapped per §6 below. |
| OQ-CP-13 | **open** | (`ecdn.supin.cz` other-asset hosting question — defer to integration-tests scope expansion in R2+) |
| OQ-CP-14 | **open** | reCAPTCHA posture in `tst.*` — still needs ČKP/SUPIN confirmation. Until then, R1 framework specs treat reCAPTCHA as bypassed-via-env-config and document the dependency in env files. |
| OQ-CP-15 | **superseded** | "When does user begin filling tst.* recon templates?" — superseded by user direction: tst.* recon will arrive via the user-supplied template emails (Phase A delivery model); no remote driving against tst.* from this side at all. |

---

## §5. Mapping back to TC-CP-001..004 (post-rev2)

| TC ID | Title (CS / EN) | Maps to R1 TT |
|-------|-----------------|---------------|
| TC-CP-001 | Implicitní autentizace přes ID — happy / Implicit ID-auth happy | TT-CP-R1-001 |
| TC-CP-002 | Implicitní autentizace přes ID — selhání / Implicit ID-auth negative-ending | TT-CP-R1-001 + TT-CP-R1-004 |
| TC-CP-003 | Průvodce — happy end-to-end / Wizard happy E2E | TT-CP-R1-002 |
| TC-CP-004 | Průvodce — výjimečné stavy a negativní konce / Wizard exceptions + negative-endings | TT-CP-R1-003 + TT-CP-R1-004 |

R-FAIL-1 still satisfied: TC-CP-001 (happy) pairs with TC-CP-002
(failure); TC-CP-003 (happy) pairs with TC-CP-004 (failure envelope).

All four TCs carry the AMENDMENT 2 viewport spec
`320 / 375 / 414 / 1024 / 1512`.

---

## §6. Status

| Item | Value |
|------|-------|
| Document | `recon/TEST-TARGET-CANDIDATES.md` |
| Iteration | CP-SUPIN-02 (rev 2) |
| Revision trigger | User direction 2026-05-05 (OQ-CP-12 resolution) |
| R1 TestTargets | 4 (TT-CP-R1-001..004) |
| R2+ TestTargets identified | 7 (TT-CP-R2-001..007) |
| All R1 carry §5b.1 sub-block | YES |
| All R1 carry env_coverage | YES |
| All R1 carry priority | YES |
| All R1 carry RELEASE field | YES |
| Status | v0.2 — feeds Excel `01_TestTargets` rev 2 |
