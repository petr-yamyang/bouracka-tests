# Recon-Input Template Extensions — v0.2

> **Purpose.** Per user direction 2026-05-05: the documents that *gather*
> inputs (recon templates, both `full` and `lightweight`) need refinement
> so the inputs they collect feed the TestTargetList + TestCase List
> precisely enough to drive an automated dev session.
>
> This doc is an **addendum** to:
> - `_config/CLIENT-PILOT-SUPIN-RECON-TEMPLATES-V0.1.md` (full templates)
> - `_config/CLIENT-PILOT-SUPIN-RECON-TEMPLATES-LIGHT-V0.1.md` (light)
>
> v0.2 adds Template 6 (per-ID-validation-case) and tightens four
> field requirements across Templates 1–5 to remove "soft" TBD-friendly
> language.

---

## §1. Template 6 (NEW) — Per-ID-validation-case recon

The implicit-ID-auth model (per user direction 2026-05-05; OQ-CP-12
resolution) makes the **identity-validation surface** the SUT's
authentication mechanism. Tests against this surface need fixture-grade
input cases the user fills via this NEW template.

```
═══════════════════════ TEMPLATE 6 — PER-ID-VALIDATION-CASE ════════════
Subject prefix: [SUPIN-RECON] [ID-CASE] <short-case-name>

──────────────────────────────────────────────────────────────────────────

CASE ID [REQUIRED]: ID-CASE-NNN
CASE NAME (CS) [REQUIRED]:
CASE NAME (EN):

ENV [REQUIRED]: tst | tst-demo | both

EXPECTED OUTCOME CLASS [REQUIRED]: happy | exception-recoverable | negative-ending
                                   (per the R1 envelope user defined
                                    2026-05-05)

──── INPUT MATERIALS (what the user enters into the SUT) ────────────────
OP (občanský průkaz):
  number_format     [REQUIRED]: <e.g. 123456789 — 9 digits>
  number_value      [REQUIRED, may be SANITISED placeholder]:
  document_photo    [optional]: filename if attached; quality (clear / blurred / cropped)

ŘP (řidičský průkaz):
  number_format     [REQUIRED]:
  number_value      [REQUIRED]:
  classes           [REQUIRED]: <A / B / C / etc.>
  expiry            [REQUIRED]: YYYY-MM-DD or "valid"
  document_photo    [optional]:

SPZ (vehicle registration plate):
  format            [REQUIRED]: matches ^\d[A-Z]{2}\s?\d{4}$ ?
  value             [REQUIRED]:
  vehicle_type      [REQUIRED]: passenger | motorcycle | truck | other
  document_photo    [optional]: SPZ photo

──── EXPECTED REGISTRY RESPONSE ──────────────────────────────────────────
DRIVER LOOKUP RESPONSE [REQUIRED]:
  http_status                [REQUIRED]: 200 | 404 | 5xx
  body.first_name            [REQUIRED if 200]:
  body.last_name             [REQUIRED if 200]:
  body.dob                   [REQUIRED if 200]: YYYY-MM-DD
  body.error_code            [REQUIRED if non-200]: e.g. "ID_NOT_FOUND" | "REG_TIMEOUT"

VEHICLE LOOKUP RESPONSE [REQUIRED]:
  http_status                [REQUIRED]:
  body.make                  [REQUIRED if 200]:
  body.model                 [REQUIRED if 200]:
  body.year                  [REQUIRED if 200]:
  body.error_code            [REQUIRED if non-200]:

──── EXPECTED UI BEHAVIOUR ───────────────────────────────────────────────
ON HAPPY (lookup 200):
  auto-fill rendered for confirmation? [REQUIRED]: yes | no
  fields auto-filled                   [REQUIRED]: <list>
  user can advance                     [REQUIRED]: yes | no
  CS confirmation message regex        [REQUIRED]: e.g. "Údaje načteny"

ON EXCEPTION-RECOVERABLE (e.g. timeout):
  CS retry-prompt regex                [REQUIRED]: e.g. "Zkuste to prosím"
  retry-button visible                 [REQUIRED]: yes | no
  state preserved on retry             [REQUIRED]: yes | no

ON NEGATIVE-ENDING (lookup 404 or fatal):
  CS error-message regex               [REQUIRED]: e.g. "Doklad nenalezen"
  user-actionable next-step            [REQUIRED]: contact-CKP | call-insurer | start-over | other
  wizard advances                      [REQUIRED]: NO (must be NO)
  record persisted                     [REQUIRED]: NO (must be NO)

──── §5b.1 TestAnalysis context (CAST-binding) ───────────────────────────
DECOMPOSITION KIND [REQUIRED]: behaviour
BEHAVIOUR_REF [REQUIRED]: authenticate-user-via-id-registers
COVERAGE_BASIS [REQUIRED]: <1-2 sentence rationale>
RELATED MI-M-T TT IDs: <e.g. TT-CP-R1-001>

──── §5b.3 Data collection points ─────────────────────────────────────────
WHICH TC: <e.g. TC-CP-001 | TC-CP-002 | both>
COLLECTION TIMING [REQUIRED]: during_call (intercept registry POST) +
                              after_call (capture response payload)
ASSERTION TARGETS:
  - exactly N driver-lookup calls per ID-photo upload
  - response body shape matches expected
  - UI surfaced exactly the auto-fill OR the error message specified above

──── ATTACHMENTS ────────────────────────────────────────────────────────
- screenshot-tst-id-case-<n>.png         (auto-fill state OR error state)
- screenshot-tst-demo-id-case-<n>.png    (if env=both and divergence)
═══════════════════════════════════════════════════════════════════════════
```

### Lightweight version of Template 6

For a colleague who is NOT yet familiar with testing terminology
(per scope §6.4 / AMENDMENT 2 point 4), the lightweight version drops
field-typing jargon:

```
══════════════ TEMPLATE 6-LIGHT — PER-ID-VALIDATION-CASE ════════════
Subject prefix: [SUPIN-RECON] [ID-CASE-LIGHT] <short-case-name>

──────────────────────────────────────────────────────────────────────────

JE TO PŘÍPAD: happy (vše je OK) | výjimka (jde to opravit) | konec (nelze pokračovat)

OP CISLO: <číslo občanského průkazu, můžeš dát placeholder>
RP CISLO: <číslo řidičského průkazu, placeholder OK>
SPZ: <např. 1ZZ 2345>

CO BY SE MELO STAT NA OBRAZOVCE:
- u happy: aplikace načte jméno a údaje a zeptá se "potvrzuješ?"
- u výjimky: aplikace řekne "zkuste to znovu" a tlačítko Zkusit znovu se zobrazí
- u konce: aplikace řekne "nelze pokračovat" a vysvětlí proč (např. "doklad
  nenalezen v registru")

CO PROSIM POSLI JAKO SCREENSHOT:
- Obrazovku ve chvíli, kdy se zobrazí výsledek (auto-fill nebo chyba)
- Na mobilu i na desktopu, jestli máš obojí

POZNAMKY (volně):
═══════════════════════════════════════════════════════════════════════════
```

The lightweight version goes through `tools/recon-parser/parse-light-template.py`
which translates colleague answers → full Template 6 fields, marking
inferred fields with a `_inferred: true` flag for human review.

## §2. Tightened-field amendments to Templates 1–5

The original recon templates (`...-V0.1.md`) used phrases like
"Bulleted list" and "free-form" in some required fields. v0.2 tightens
these into machine-parseable shapes:

### §2.1 Template 1 (Per-screen recon) — KEY UI ELEMENTS field

OLD: bulleted list with free shape.
NEW: each element is one row of a tab-separated mini-table:

```
TYPE	LABEL_CS	SELECTOR_HINT	NOTES
input	E-mail	id="login-email"	required, email type
button	Přihlásit se	class="btn-primary"	submits the form
link	Zapomenuté heslo?	class="forgot-link"	→ /forgot-password
```

Reason: the mini-table is parseable into the TC step list's `selector`
field directly, with no manual cleanup.

### §2.2 Template 1 — VALIDATION RULES field

OLD: free-form per-input list.
NEW: structured rules:

```
FIELD	RULE_KIND	PARAM	CS_MESSAGE_REGEX
E-mail	required	—	"Pole je povinné"
E-mail	format	email	"Neplatný e-mail"
Heslo	required	—	"Pole je povinné"
Heslo	min_length	8	"Heslo musí mít alespoň 8 znaků"
```

`RULE_KIND` enum: `required | format | min_length | max_length |
pattern | range | confirm | custom`.

### §2.3 Template 2 (Per-flow) — STEP SEQUENCE field

OLD: numbered list with free-form steps.
NEW: each step is one row of a structured sub-block per §5b.2:

```
STEP_N	KIND	ACTION_VERB	OBJECT_REF	EXPECTED_NEXT_STATE
1	trigger_point	navigate_to	/login	SCR-001 visible
2	trigger_point	fill_input	SCR-001#login-email	email-filled
3	trigger_point	click	SCR-001#submit	→ SCR-002 (dashboard)
```

`KIND` enum: per R-CAST-2.

### §2.4 Template 3 (Per-integration) — REQUEST/RESPONSE SHAPE

OLD: free-form JSON example.
NEW: JSON with explicit type annotations + sample line:

```jsonc
{
  "$schema": "request",
  "address": "<string; required; max 200>"   // sample: "Václavské náměstí 1, Praha 1"
}
```

Reason: enables auto-derivation of mock-response shapes for
test-side stubs.

### §2.5 Template 5 (Per-divergence) — TEST-IMPLICATION field

OLD: 4 enumerated options.
NEW: same 4 options PLUS each row carries a `step_id_or_ac_id` ref so
the divergence can be wired to a specific TC step or AC:

```
OPTION	REF	NOTES
SAME-DIFFERENT-EXPECTED	TC-CP-003-S-12::expected	DEMO accepts OTP=0000 always
DIFFERENT-SCENARIO-PER-ENV	—	split into TC-CP-NNN-A and -B
SKIP-ON-ONE-ENV	TC-CP-004-S-04	skip on tst-demo (no OCR)
SHARED-CODE-DIFFERENT-CONFIG	env/tst-demo.json::sms_fixed_otp	per-env value
```

## §3. New REQUIRED field across all templates: `dev_session_consumability`

Added at the bottom of every template instance:

```
DEV-SESSION CONSUMABILITY [REQUIRED]:
- All required fields filled?           yes | no
- Selectors expressed per §5 of TC-spec format? yes | no
- CS message regexes provided where required?   yes | no
- Reviewed by Petr?                              yes | no
```

If any answer is `no` → the recon material goes through the
human-enrichment loop before being promoted into a TT row or TC spec.

## §4. Light-template parser pipeline

```
[colleague light-template email]
        ↓
  tools/recon-parser/parse-light-template.py
        ↓
[draft full template with _inferred:true flags]
        ↓
  human review (Petr enriches missing fields)
        ↓
[full template with all required fields]
        ↓
  promotes to:
    - recon/screens/SCR-NNN.md         (Template 1)
    - recon/flows/FLW-NNN.md           (Template 2)
    - recon/integrations/INT-NNN.md    (Template 3)
    - recon/bugs/KB-CP-NNN.md          (Template 4; gitignored)
    - recon/divergences/DIV-NNN.md     (Template 5; gitignored)
    - recon/id-cases/ID-CASE-NNN.md    (Template 6; gitignored)
```

The parser ships in CP-SUPIN-03+ (per FUTURE-REPO-STRUCTURE §3); until
then, Petr (or a Sonnet session) parses by hand.

## §5. Status

| Item | Value |
|------|-------|
| Document | `_specs/RECON-INPUT-EXTENSIONS-v0.2.md` |
| Version | v0.2.0 (additive over v0.1) |
| Trigger | User direction 2026-05-05 (implicit-ID-auth model + refinement request) |
| New templates | 1 (Template 6 — per-ID-validation-case) + lightweight version |
| Tightened existing | Templates 1, 2, 3, 5 (specific fields per §2) |
| New required field | `dev_session_consumability` |
| Status | v0.2 — additive; v0.1 templates remain in scope, fields now stricter |
