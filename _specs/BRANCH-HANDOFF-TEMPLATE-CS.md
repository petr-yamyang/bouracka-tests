# Bouračka — Branch handoff template — v0.1 CS

> **Trigger.** CP-SUPIN-04 STEP 29 (2026-05-06).
> **Audience.** Pete + Sonnet sessions taking individual branches.
> **Cíl.** Standardizovaný "starting brief" pro každou Sonnet session,
> aby měla úplný kontext pro intensive work bez nutnosti znovu-derivace.

Použití: kopírujte `BRANCH-HANDOFF-TEMPLATE-CS.md` jako
`BRANCH-HANDOFF-{BRANCH_NAME}-{DATE}.md` při zahájení nové Sonnet
session, vyplňte sekce, předejte do Sonnet session jako úvodní brief.

---

## §1. Identita branche

| Pole | Hodnota |
|------|---------|
| Branch name | (např. `demo-public`, `demo-tst`, `prod-tst`, `prelive`) |
| Cílové URL | (např. `https://demo.bouracka.cz`) |
| Síťový gate | (žádný / VPN ČKP / firewall ip-allowlist / atd.) |
| Sonnet session ID | (vyplnit po spuštění) |
| Spuštěna kdy | (datum + čas) |
| Spuštěna kým | Pete |
| Předchozí Opus session | (link / ID) |

## §2. Inherited governance (z Opus session)

Tyto artefakty MUSÍ Sonnet session respektovat:

| Artefakt | Lokace | Verze | Komentář |
|----------|--------|-------|----------|
| Excel master | `BOURACKA-TESTPLAN-v0.4.x.xlsx` | v0.4.x | branch tagging via `applies_to_demo` / `applies_to_prod` |
| Naming conventions | `_specs/BUG-NAMING-CONVENTION-v0.1.md` | v0.1 | `BUG-CP-{TC_CODE}-{ASSERT_CODE}` |
| Doc pattern | `_specs/BRANCHED-MASTER-DOC-PATTERN-v0.1.md` | v0.1 | `<!-- B:DEMO -->...<!-- /B -->` markers |
| Install guide | `_install/INSTALL-FROM-ZERO-v0.4-CS.md` | v0.4 | 6 empirický gotchas, recovery patterns |
| Tester lessons | `_specs/TESTER-LESSONS-LEARNED-v0.1-CS.md` | v0.1 | OTP React-controlled, cookie banner, etc. |
| Δ matice | `recon/DELTA-DEMO-vs-PROD-v0.1.md` | v0.1 | 26 row, 8 confirmed |
| Roadmap | `_specs/ROADMAP-4-TARGET-CS.md` | v0.1 | strategic context |

**NESMÍ** Sonnet session:
- Měnit Excel master schéma (jen Opus může)
- Měnit naming convention (jen Opus)
- Vytvářet nové TC bez updatu master Excel (volat tools/migrate_*.py)

## §3. Branch-specific objectives

(Vyplňte per branch při handoff.)

### Předchozí state (co je hotové)

- (...)
- (...)

### Tato session má dodat

- (...)
- (...)

### Out-of-scope pro tuto session

- (...)
- (...)

## §4. Inherited TC suite + nové TC k dodání

| TC kód | Název | Status | Akce v této session |
|--------|-------|--------|---------------------|
| TC-CP-001 | Bring-up smoke | passed | žádná — smoke validuje pipeline |
| TC-CP-NEW-A | Rozcestník copy | passed | žádná |
| TC-CP-A1-MAIN-DEMO | Full happy day | passed | žádná |
| (nový) | (...) | TBD | implementovat |

## §5. Inherited test artifacts

```
playwright/
  tests/
    bring-up-smoke.spec.ts          ← funkční na DEMO
    a1-main-happy-day-demo.spec.ts  ← funkční na DEMO
    a2-alternates-demo.spec.ts      ← funkční na DEMO
    intel-probes/                   ← read-only API recon
  helpers/
    page-helpers.ts                 ← dismissCookieBanner, waitForSpaHydration
  reporters/
    excel-row-writer.ts             ← UPSERT do 07_TestRunResults
  playwright.config.ts              ← projects: tst / tst-demo / public / public-mobile-375

cypress/
  e2e/
    bring-up-smoke.cy.ts            ← parity s Playwright

testcafe/
  tests/
    bring-up-smoke.test.ts          ← parity s Playwright

tools/
  check_priority_matrix.py          ← validátor priority matrix
  bump_workbook_version.py          ← version + computed values
  migrate_to_v04_branch_tagging.py  ← branch columns
  fix_priority_matrix.py            ← priority bugfix
  render_branch_doc.py              ← branched MD render
  append_test_run_result.py         ← Excel UPSERT z reporter
  validate_workbook.py              ← 10 zdravotních kontrol
```

## §6. Open blockers (musí být vyřešeny PŘED Sonnet handoffu)

| # | Blocker | Typ | Resolution |
|---|---------|-----|------------|
| 1 | (...) | (technical / governance / network) | (...) |

## §7. Sync-back protocol

Po dokončení Sonnet session:

1. **Vytvořit `SYNCHRO-{BRANCH}-{DATE}.md`** v repu — ideally před koncem session
2. **Sync s Pete** — co bylo dodáno, co je open, co potřebuje Opus governance
3. **Pull-back delta-mat** (changes / methodology adjustments) → Pete předá Opus session pro merge do master Excel

Sync-back NESMÍ obsahovat:
- Změny Excel master (jen Opus)
- Změny naming convention (jen Opus)
- Závěry o cross-branch věcech (jen Opus má cross-branch view)

## §8. Sonnet session efficiency tips

- **Read first, write later** — read all referenced artifacts pred change
- **Tag every TC** with `@demo` / `@prod` / `@cross-branch`
- **Reuse helpers** z `playwright/helpers/page-helpers.ts`
- **Run `scripts/sanity-check.ps1`** pred + po každé větší změně
- **Sync intermediate** — pokud session > 4h, midpoint sync přes
  `SYNCHRO-INTERIM-...md`

## §9. Status

| Item | Hodnota |
|------|---------|
| Template | `_specs/BRANCH-HANDOFF-TEMPLATE-CS.md` |
| Verze | v0.1 |
| Datum | 2026-05-06 |
| Status | template — vyplnit per branch při handoff |
