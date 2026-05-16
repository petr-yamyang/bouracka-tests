# Sonnet brief — BRIEF-008: v0.1.5 release engineering + Kate Round-3 ship

**Target Claude.** Sonnet 4.6 in Claude Code (terminal, stateless).
**Issued by.** Opus 4.7 session, 2026-05-15.
**Branch.** `cp-supin-16-v015-release`.
**Estimated effort.** ~2 hours (mostly mechanical).
**Reviewer.** Pete in Opus 4.7 session.
**Blocked by.** ALL OF: #002, #003, #001b, #004, #005, #006, #007, #009 merged into v0.1.5 integration branch.

---

## 1. Goal in one paragraph

The final brief — turn the v0.1.5 integration branch into a shippable release. Bump version from `0.1.5-devN` to `0.1.5`, rebuild wheel + multi-ABI ZIPs (using the existing scripts that we proved green), re-stage Kate/SUPIN/Pete drops with the new artefacts, run the full VERIFY-AND-SHIP gate, author KATE-V0.1.5-RELEASE-CS.md (replacing v0.1.4 reinstall doc), confirm BUG-K-008 recovery procedure is included, produce final SHAs ready for Drive upload + Kate message. After this brief returns green, Pete uploads + sends Kate the Round-3 package.

---

## 2. Spec — read this BEFORE coding

1. `_config/MAJOR-DEV-SESSION-PLAN-v0.1.5-EN.md` — §3.3 four-gate test ladder, §6 Kate-ship trigger, §7 Definition of Done
2. `delivery/package-hp-elite-v0.1.4-multi-abi.ps1` — multi-ABI packager (already proven; you may need to bump `$wheelVersion` to `0.1.5`)
3. `delivery/RESTAGE-DROPS-MULTI-ABI.ps1` — restage script
4. `delivery/VERIFY-AND-SHIP-V0.1.4-MULTI-ABI.ps1` — verify gate (you'll create `-V0.1.5-` variant)
5. `delivery/KATE-V0.1.4-REINSTALL-CS.md` — Kate's last install doc; you author Round-3 replacement
6. `CHANGELOG.md` — accumulated dev0..dev5 entries; you write the final v0.1.5 entry consolidating them

---

## 3. Inputs / outputs

### Inputs

- Integration branch with all 8 prior briefs merged (#001 already + #002 + #003 + #001b + #004 + #005 + #006 + #007 + #009)
- `__version__` currently `0.1.5-devN` (depends on last brief merged)
- Multi-ABI packager + restage + verify scripts proven for v0.1.4

### Outputs

1. `__version__ = "0.1.5"` (no dev suffix) in 2 files (`__init__.py` + `pyproject.toml`)
2. Fresh wheel `bouracka_ui/dist/bouracka_ui-0.1.5-py3-none-any.whl`
3. Multi-ABI ZIPs: `bouracka-ui-hp-elite-v0.1.5-CS-multi-abi.zip` + `...-EN-...`
4. All 3 drop folders re-staged with v0.1.5 artefacts + v0.4.5 workbook (post-Brief #003)
5. `delivery/VERIFY-AND-SHIP-V0.1.5-MULTI-ABI.ps1` — variant of v0.1.4 gate adapted to v0.1.5 sha + version expectations
6. `delivery/KATE-V0.1.5-RELEASE-CS.md` — Kate Round-3 release notes + install/upgrade procedure
7. Final CHANGELOG.md v0.1.5 consolidated entry
8. KATE-DROP-2026-05-13 (or new dated drop) folder ready for Drive upload

---

## 4. File boundaries

### Create

- `delivery/VERIFY-AND-SHIP-V0.1.5-MULTI-ABI.ps1` — clone-and-adapt of v0.1.4 gate
- `delivery/KATE-V0.1.5-RELEASE-CS.md` — fresh release notes (don't modify v0.1.4 doc)
- (Optional) new dated drop folders like `delivery/KATE-DROP-2026-05-15/` if Pete wants per-release archive

### Modify

- `bouracka_ui/bouracka_ui/__init__.py` → `__version__ = "0.1.5"`
- `bouracka_ui/pyproject.toml` → `version = "0.1.5"`
- `delivery/package-hp-elite-v0.1.4-multi-abi.ps1` → adapt to `$wheelVersion = "0.1.5"` AND `$distVersion = "v0.1.5"`. Either modify in place OR clone as `package-hp-elite-v0.1.5-multi-abi.ps1` and update RESTAGE script accordingly.
- `delivery/RESTAGE-DROPS-MULTI-ABI.ps1` → update source ZIP filenames from `v0.1.4-CS-multi-abi.zip` to `v0.1.5-CS-multi-abi.zip`
- `CHANGELOG.md` — consolidate all dev0..dev5 entries into a single v0.1.5 release section

### DO NOT touch

- `bouracka_ui/bouracka_ui/dispatcher.py` / `server.py` / `workbook_io.py` / `audit_dispatcher.py` / `cross_check.py` — production code, already shipped by prior briefs
- `tools/workbook-v0.4.*.py` patchers — done by prior briefs
- `BOURACKA-TESTPLAN-v0.4.5.xlsx` — workbook is canonical, don't modify (Brief #003 produced it)
- `_config/` — read-only specs
- `recon/integrations/` — read-only

---

## 5. Functional requirements

### F-1. Version bumps (2 files)

```python
# bouracka_ui/bouracka_ui/__init__.py
__version__ = "0.1.5"
```

```toml
# bouracka_ui/pyproject.toml
version = "0.1.5"
```

### F-2. Build wheel

```bash
cd bouracka_ui
python -m build
```

Output: `bouracka_ui/dist/bouracka_ui-0.1.5-py3-none-any.whl` + `.tar.gz`. Verify SHA256 of wheel.

### F-3. Update packager + restage scripts for v0.1.5

In `delivery/package-hp-elite-v0.1.4-multi-abi.ps1` (or new `-v0.1.5-` variant):

```powershell
$distVersion  = "v0.1.5"     # was v0.1.4
$wheelVersion = "0.1.5"      # was 0.1.4
$supportedAbis = @("310", "311", "312")    # unchanged
```

Plus add `psutil` to the critical-deps sanity-check list (Brief #009 added psutil dep):

```powershell
$criticalDeps = @("httptools", "watchfiles", "websockets", "pyyaml",
                  "pydantic_core", "psutil")
```

Same single-file change in restage script — bump source ZIP filename pattern from v0.1.4 → v0.1.5.

### F-4. Run packager + restage + verify

The packager + restage scripts are battle-tested. Run them:

```powershell
.\delivery\package-hp-elite-v0.1.5-multi-abi.ps1   # produces 2 ZIPs
.\delivery\RESTAGE-DROPS-MULTI-ABI.ps1             # propagates to 3 drops
```

Capture the new SHA256s for both ZIPs. Update `KATE-V0.1.5-RELEASE-CS.md` with them.

### F-5. VERIFY-AND-SHIP-V0.1.5-MULTI-ABI.ps1

Clone v0.1.4 gate as v0.1.5 variant. Changes:

- Update file path references throughout from `v0.1.4-*-multi-abi.zip` to `v0.1.5-*-multi-abi.zip`
- Update sha256 expectations to the actual new SHAs from F-4
- Bump expected `server_version` assertion in C.6 health check from `"0.1.4"` to `"0.1.5"`
- Bump expected test count from current 28+5 to whatever the actual current count is (sum of all briefs' test additions)
- Add C.8 (new step) — exercise the audit-mode endpoint: `curl -X POST /api/audit/runs -d '...'` → expect 200 with audit_run_id

Run the verify gate end-to-end. Must reach Phase D SHIP-READY verdict before considering this brief done.

### F-6. KATE-V0.1.5-RELEASE-CS.md authoring

Replace v0.1.4 reinstall doc (do NOT modify in place; create a new file). Structure:

```markdown
# Bouračka UI v0.1.5 — release pro Kate (Round 3)

**Verze.** v0.1.5 multi-ABI (2026-05-15).
**Pro.** Kate — upgrade z předchozí v0.1.4 multi-ABI nebo from-zero install.
**Časová náročnost.** ~15 minut.

## §1. Předpoklady na cílovém stroji
(per Brief #004 §F-3 prereq section)

## §2. Co se mění oproti v0.1.4
- BUG-K-008 oprava: workbook patcher MIGRUJE tvoje bugy (žádná ztráta při version bumpu)
- BUG-K-009: instalační návod má explicit prereq sekci (Node + selenium)
- BUG-K-010: dispatcher posílá správný --env do consolidatoru
- BUG-K-012: TestRuns se příště APPEND-uje, ne přepisuje
- BUG-K-013: TC seznam přichází z workbooku (TC-CP-001..024), ne ze spec filů
- NEW FR-K-001 Bug↔TC↔Step traceability
- NEW FR-K-002 TC step preview
- NEW FR-K-003 human-readable run console
- NEW FR-K-004 bug → screenshot/video evidence
- NEW FR-K-005 mock-mode dispatch shield (interní)
- NEW FR-K-006 integration probe expansion (interní)
- NEW FR-K-007 cross-check report (/api/runs/{id}/cross-check.html)
- NEW FR-K-008 Audit/Inspection mode (/audit page)

## §3. Postup upgradu (~15 min)
(Step-by-step Powershell sequence including BUG-K-008 recovery —
 if Kate has backup of her v0.4.3 workbook with BUG-002, the patcher's
 --source-data flag (Brief #001b) migrates it into the new v0.4.5)

## §4. Verifikace
(Three quick API checks: health = v0.1.5, /api/tcs returns workbook-sourced TCs,
 /audit page accessible)

## §5. Kontakt
```

Bake in the actual SHA256 hashes from F-4 output.

### F-7. CHANGELOG consolidation

Replace the scattered dev0..dev5 entries with a single v0.1.5 release section:

```markdown
## v0.1.5 (2026-05-15)

### New features
- FR-K-001 Bug↔TC↔Step traceability (Brief #002, #003)
- FR-K-002 TC step preview accordion (Brief #002)
- FR-K-003 Human-readable run console (Brief #002)
- FR-K-004 Bug→screenshot/video evidence (Brief #002 + dispatcher changes)
- FR-K-005 Mock-mode dispatch e2e shield (Brief #005)
- FR-K-006 Integration probe expansion (Brief #006)
- FR-K-007 Cross-framework agreement report (Brief #007)
- FR-K-008 Audit/Inspection mode for test runs (Brief #009)

### Bug fixes
- BUG-K-008 Workbook patcher row-level data migration (Brief #001b)
- BUG-K-009 Install runbook prereq section added (Brief #004)
- BUG-K-010 Dispatcher env-mapping for consolidator fixed (Brief #004)
- BUG-K-012 TestRuns APPEND vs OVERWRITE (Brief #004)
- BUG-K-013 TC discovery from workbook (Brief #003)

### Schema
- Workbook v0.4.5 — adds `cypress_spec_glob`, `playwright_grep`, `selenium_pytest_k` columns
- Workbook v0.4.4 → v0.4.5 patcher with optional `--source-data` migration mode

### Dependencies added
- psutil >= 5.9 (for audit-mode pause/resume — Brief #009)

### Tests
- 28 baseline → 50+ tests across smoke + mock-dispatch-e2e + audit-mode-e2e + cross-check + patcher
```

(Final test count depends on what Sonnet actually shipped from each brief; consolidate.)

### F-8. Kate ship checklist

Final pre-Drive-upload check:

```powershell
# 1. SHA verification
Get-FileHash delivery\bouracka-ui-hp-elite-v0.1.5-CS-multi-abi.zip
Get-FileHash delivery\bouracka-ui-hp-elite-v0.1.5-EN-multi-abi.zip

# 2. KATE-DROP folder contents
Get-ChildItem delivery\KATE-DROP-2026-05-13\
# Expected: 5 files (CS ZIP, source ZIP, v0.4.5 workbook, KATE-V0.1.5-RELEASE-CS.md, SHA256SUMS.txt)

# 3. SHA256SUMS verification
cat delivery\KATE-DROP-2026-05-13\SHA256SUMS.txt
```

Output of these commands becomes return checklist item 4.

---

## 6. Risk gates — STOP and report

1. **VERIFY-AND-SHIP-V0.1.5 gate fails.** This is the ultimate "DO NOT SHIP" trigger. Halt; show the failed gate, do NOT proceed to F-6/F-7/F-8.
2. **Multi-ABI packager critical-deps gate fails** for psutil cp310/cp311/cp312 wheels. Likely psutil wasn't added to bouracka_ui/pyproject.toml dependencies in Brief #009. Halt; coordinate with Brief #009 author to fix.
3. **Workbook v0.4.5 not in repo root.** Brief #003 was supposed to produce it. Halt; verify Brief #003 properly merged.
4. **Test count regressed** (current run < previous baseline). Some merge clobbered tests. Halt + diff.
5. **CHANGELOG.md has merge conflicts** from multiple briefs editing it. Resolve cleanly with the consolidated section per F-7.

---

## 7. Don't-go-beyond

- Don't introduce new features at the release stage — purely engineering
- Don't bump to v0.1.6 or skip directly to v0.2 — strict v0.1.5
- Don't ship dev suffix; v0.1.5 has no `-dev*` form
- Don't upload to Drive — Pete does that manually after review
- Don't send Kate any message — Pete does that

---

## 8. Return checklist

1. Branch + SHAs
2. Files changed
3. VERIFY-AND-SHIP-V0.1.5 output — paste the Phase D SHIP-READY block verbatim
4. F-8 SHA outputs (both ZIPs + KATE-DROP folder listing + SHA256SUMS)
5. KATE-V0.1.5-RELEASE-CS.md — confirm the actual SHAs are baked in
6. CHANGELOG.md v0.1.5 section snapshot
7. Out-of-scope findings — anything weird discovered during integration testing
8. Deviations
9. Open questions for Pete pre-upload (e.g., should we tag git tag v0.1.5? rename KATE-DROP-2026-05-13 → KATE-DROP-2026-05-15?)

---

## 9. Acceptance — done when

- `__version__` reads `0.1.5` exactly
- New multi-ABI ZIPs exist + verified clean (BUG-K-006 post-flight gate passes)
- All 3 drop folders have v0.1.5 ZIPs + v0.4.5 workbook + KATE-V0.1.5-RELEASE-CS.md
- VERIFY-AND-SHIP-V0.1.5 Phase D = SHIP-READY (or equivalent verdict)
- CHANGELOG.md has consolidated v0.1.5 entry (no scattered dev entries left)
- Branch ready for tag + push
- Return checklist §10 pasted

After Pete reviews + tags + uploads, Kate Round-3 is complete. Pete sends her the message based on KATE-V0.1.5-RELEASE-CS.md content.

---

**End of BRIEF-008.**
