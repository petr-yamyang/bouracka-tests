# Three-device development + testing plan — v0.2 CS

> **Trigger.** CP-SUPIN-04 STEP 33 (2026-05-06 EOD); revize 2026-05-07 ráno
> po Peteově re-klarifikaci device topologie.
>
> **Audience.** Pete (operating all 3 devices), governance, future testers.
> **Cíl.** Definovat role každé ze 3 vývojových+testovacích stanic + sync
> protocol mezi nimi.
>
> **Klíčová klarifikace 2026-05-07** (Pete přímý citát):
> *"ThinkPad is the computer we are working now, HP Elite is SUPIN owned*
> *notebook we are running tests because it sits inside of the internal*
> *network but could not use tools such as Claude and other specific tools*
> *because security rules applies. Ecosystem now consists: 1. ThinkPad and*
> *MacBook are personal and working systems, 2. HP Elite is first-running-*
> *computer for all delivered."*
>
> **Implikace pro tento plán.**
> - HP Elite (`<test-runner-host>`) je **vlastnictví SUPIN/ČKP**, nikoli Peteovo personal.
> - HP Elite je **první runtime cíl** pro všechny deliverables — testy musí
>   GREEN-it tam, ne na ThinkPadu.
> - HP Elite **nemůže používat Claude / Cowork / Anthropic services** —
>   security policy ČKP. Pete řídí ručně + přes spakované nástroje.
> - HP Elite je **uvnitř ČKP korporátní sítě** → má reach na `tst.demo.bouracka.cz`,
>   `tst.bouracka.cz`, interní `n08-test`, AISPOV ROB/CRR/CRV, atd.
> - Personal devices: ThinkPad (Opus governance) + MacBook (Sonnet/MI-M-T
>   analytical) — ty Claude používat smějí.

---

## §1. Tři stanice — role + posture

```
   ┌─────────────────────────────────────────────────────────────────┐
   │                                                                 │
   │   ThinkPad ◄────────────► MacBook         ────────► HP Elite    │
   │   (Opus session,           (Sonnet/MI-M-T              (no Claude,│
   │    governance,              analytical                  internal  │
   │    primary dev)             session)                    SUPIN net)│
   │                                                                 │
   │      │                          │                          │    │
   │      └──── via GitHub ───────── └── via SUPIN VPN ─────────┘    │
   │           (public sync)             (when accessible)           │
   │                                                                 │
   └─────────────────────────────────────────────────────────────────┘
```

### §1.1 ThinkPad — primary development + Opus session

| Aspekt | Hodnota |
|--------|---------|
| **OS** | Windows 11 |
| **Owner** | Pete |
| **Role** | (1) Opus session governance, (2) primary dev, (3) Bouračka tests against DEMO public |
| **Has installed** | Python 3.12, Node 20, JDK 21, Playwright + Chromium, openpyxl, mockoon-cli |
| **Has access to** | demo.bouracka.cz (public), GitHub, npm, PyPI, github.com |
| **Does NOT have access to** | tst.demo.bouracka.cz (firewall), tst.bouracka.cz (firewall), bouracka.cz prelive (TBD), SUPIN internal |
| **Source of truth** | Workspace folder `C:\Users\vitez\Documents\VibeCodeProjects\SUPIN\` |
| **Git remote** | (TBD — Pete creates GitHub repos) |
| **Sync** | GitHub push/pull, e-mail (for SUPIN delivery) |

**Daily workflow:**
1. Open Cowork → Opus session (this) for governance work
2. Run `scripts\sanity-check.ps1` to verify environment
3. Develop tests against `demo.bouracka.cz` (public)
4. Commit to GitHub when milestone hit
5. Send e-mail deliverable per branch (e.g. `DEMO bouracka/`)

### §1.2 MacBook — analytical MI-M-T session

| Aspekt | Hodnota |
|--------|---------|
| **OS** | macOS |
| **Owner** | Pete |
| **Role** | analytical session for MI-M-T methodology consideration; bigger-picture integration thinking |
| **Has installed** | (Sonnet sessions; minimal local toolchain — mostly read/write of governance docs) |
| **Has access to** | GitHub, public web; (potentially SUPIN VPN if Pete loaded credentials) |
| **Does NOT have access to** | (likely) demo.bouracka.cz testing machinery — MacBook is not a test runner |
| **Source of truth** | Same GitHub repos as ThinkPad |
| **Sync** | GitHub clone/pull; SYNCHRO-MACBOOK-*.md drops |

**Per-iteration workflow:**
1. Pull latest from GitHub
2. Read `SYNCHRO-MACBOOK-CP-SUPIN-XX-YYYY-MM-DD.md` (= delta since last MacBook session)
3. Read new artefacts in `bouracka-tests/_specs/`, `SUPIN-ecosystem-map/`
4. Generate MI-M-T methodology proposals → `_specs/MIMT-*.md`
5. Optionally: extract reusable patterns into separate MI-M-T-bound repo
6. Sync-back via `SYNCHRO-MACBOOK-TO-OPUS-{DATE}.md`

### §1.3 HP Elite (<test-runner-host>) — SUPIN-owned, internal-network primary runtime

| Aspekt | Hodnota |
|--------|---------|
| **Hostname** | `<test-runner-host>` (potvrzeno z `validate-install.ps1` výstupu 2026-05-07) |
| **OS** | Windows 11 Enterprise (potvrzeno) |
| **User** | `<test-runner-user>` (SUPIN účet, ne `vitez` / personal) |
| **Owner** | **SUPIN / ČKP** (NE Pete osobně) |
| **Role** | **První běhové prostředí pro všechny deliverables** — kit musí GREEN-it primárně tady; ThinkPad je vývojářský preview |
| **Lokace** | uvnitř ČKP korporátní sítě — má reach na `tst.demo.bouracka.cz`, `tst.bouracka.cz`, interní AISPOV/N08/zenID |
| **Claude / Cowork** | **NO — security policy ČKP.** Pete drive-uje **ručně** přes pakované nástroje (ZIP / signed PowerShell scripts) |
| **Has installed** | Confirmed 2026-05-07: Node 24.15.0, npm 11.12.1, Playwright 1.59.1; reachability `demo` ✅ + `tst.demo` ✅ |
| **Has access to** | ČKP intranet (= bez VPN), všechny 4 Bouračka environments (DEMO public + DEMO test + PROD test + PROD prelive) |
| **Does NOT have access to** | Cowork / Anthropic services (žádný Claude přímo na stroji) |
| **Source of truth** | (a) e-mail attached ZIP z ThinkPadu (current); (b) SUPIN internal Git mirror (Phase 2 budoucí per GitHub strategy §8) |
| **Sync** | E-mail attachments (current); USB jako záložní kanál; nikdy přímý push proti GitHubu (out-of-bound z ČKP) |
| **Test results sync-back** | Pete vyexportuje `test-results/`, `playwright-report/`, screenshots → e-mail nebo USB → Pete na ThinkPadu absorbuje do `recon/` + Excel TES sheets |

**Per-week workflow (when active):**
1. Pete carries USB / e-mail with latest `bouracka-automation-vX.Y.Z.zip`
2. Extracts on HP Elite, runs tests against firewalled environments
3. **Captures findings** (screenshots, logs, network traces) — ne přímo commit-uje na GitHub
4. **Pete carries findings back to ThinkPad** for Opus session intake
5. Findings → fragments in `SUPIN-ecosystem-map/fragments/` + drift log

## §2. Cross-device sync protocol

### §2.1 ThinkPad ↔ MacBook (via GitHub — public)

```
ThinkPad (Pete + Opus)
   │
   │ git push origin main
   ▼
GitHub (cloud)
   │
   │ git pull origin main
   ▼
MacBook (Pete + Sonnet/analytical)
```

**Frekvence:** po každé Opus iteraci (typicky milestone-shaped).
**Volume:** small commits (~50-200 KB per iteration).
**Drift risk:** low — both Petes' machines, single owner.

### §2.2 ThinkPad → HP Elite (via e-mail / USB)

```
ThinkPad (Opus session emit)
   │
   │ build deliverable ZIP (~1.5 MB)
   ▼
E-mail (Pete → Pete) OR USB drive
   │
   │ Pete walks to HP Elite, extracts
   ▼
HP Elite
   │
   │ Pete runs tests in SUPIN intranet
   ▼
Findings (screenshots, logs)
   │
   │ Pete walks back to ThinkPad
   ▼
ThinkPad (Opus ingestion)
   │
   │ fragments/ entry + Δ matrix update
   ▼
GitHub commit
```

**Frekvence:** ad-hoc per testing window.
**Volume:** ZIP ~1.5 MB out, findings ~2-5 MB back.
**Drift risk:** medium — manual relay; dates important for Δ tracking.

### §2.3 ThinkPad → SUPIN internal (future, per GitHub strategy §8)

When SUPIN internal Git opens:
```
ThinkPad commits → GitHub (primary)
                  → SUPIN-internal-git (push-only mirror)
```

NEVER pull from SUPIN-internal — keep GitHub as single source of truth.

## §3. Per-device deliverable bundles

### §3.1 ThinkPad (workspace folder)

`C:\Users\vitez\Documents\VibeCodeProjects\SUPIN\` — full mono-repo:
- `bouracka-tests/` (full repo with node_modules + test results)
- `SUPIN-ecosystem-map/` (full architectural repo)
- `bouracka - automated test suites inouts and seeders/` (versioned archives)
- `analyticke vstupy/` (raw analytical inputs from Pete)

### §3.2 MacBook handoff bundle

Subset for analytical work — text-only, no node_modules / binaries:
```
SUPIN-MacBook-handoff-CP-SUPIN-04-2026-05-07/
├── README-CS.md                                ← orientation for MacBook
├── SYNCHRO-MACBOOK-CP-SUPIN-04-2026-05-07-EOD.md  ← latest delta
├── _specs/                                     ← all governance + strategy docs
├── recon/                                      ← analytical artefacts
└── (git URL: github.com/{user}/bouracka-tests + SUPIN-ecosystem-map)
```

Size: ~2 MB.

### §3.3 HP Elite handoff bundle

Runnable subset for SUPIN intranet testing:
```
HP-Elite-deploy-CP-SUPIN-04-2026-05-07/
├── INSTALL-FROM-ZERO-v0.4-CS.md                ← install procedure
├── SECOPS-COMPONENTS-CS.md                     ← what gets installed
├── bouracka-automation-v0.4.7.zip              ← runnable suite
├── bouracka-suite-DEMO-v0.3.0.zip              ← parametrized DEMO suite
└── README-HP-ELITE-CS.md                       ← HP-Elite-specific run guide (NEW)
```

Size: ~1.5 MB.

## §4. Per-device task allocation (for next morning + week)

### §4.1 Morning 2026-05-07 — by-device action items

| Device | Task | Outcome |
|--------|------|---------|
| ThinkPad | Read morning e-mail with v0.4.7 ZIPs | confirmation |
| ThinkPad | Re-extract / sanity-check after refresh | 7/7 pass |
| ThinkPad | Run automation suite tests (per Pete: "Next steps will be automation suit tests in SUPIN in the morning") | new test results landed in `13_TestExecutionSummary` |
| MacBook | Open SYNCHRO-MACBOOK doc | absorb v0.4.6 + v0.4.7 deltas |
| MacBook | Optional: draft MI-M-T import contract | draft `_specs/MIMT-IMPORT-CONTRACT-DRAFT.md` |
| HP Elite | (idle until SUPIN VPN access window) | n/a today |

### §4.2 Week-of 2026-05-07 — by-device

| Device | Tasks for the week |
|--------|---------------------|
| ThinkPad | (1) Run multi-framework parallel — Playwright + ReadyAPI + Postman against DEMO. (2) Capture results in `13_TestExecutionSummary`. (3) First evidence-based framework comparison. |
| MacBook | MI-M-T methodology export draft based on multi-platform learnings |
| HP Elite | Once VPN access: bring up Bouračka kit, run smoke against `tst.demo.bouracka.cz` (Cíl 2 first activation) |

## §5. Shared resources (per device)

### §5.1 GitHub repos

| Repo | ThinkPad | MacBook | HP Elite |
|------|----------|---------|----------|
| `bouracka-tests` | clone + push (primary) | clone + read | clone + (run only; commits via ThinkPad relay) |
| `SUPIN-ecosystem-map` | clone + push | clone + read | clone (occasional read) |

### §5.2 Excel master location

| Stage | Where |
|-------|-------|
| Authoring | ThinkPad workspace (`C:\Users\vitez\Documents\VibeCodeProjects\SUPIN\bouracka-tests\BOURACKA-TESTPLAN-vX.Y.Z.xlsx`) |
| Review | MacBook (clone of GitHub) |
| Test execution writes | ThinkPad + HP Elite (separate runs; runs sync back via Pete's ThinkPad relay) |

## §6. Risk per device

| Device | Risk | Mitigation |
|--------|------|-----------|
| ThinkPad | Single point of dev, hardware failure | regular GitHub push; backup workspace once a week |
| MacBook | Out-of-sync vs ThinkPad | always pull before reading; sync-back doc |
| HP Elite | (a) email scanner stripping ZIPs, (b) findings lost in transit ThinkPad | (a) USB backup channel; (b) ALWAYS commit findings to GitHub from ThinkPad after relay |

## §7. Status

| Item | Hodnota |
|------|---------|
| Plan | `_specs/THREE-DEVICE-PLAN-CS.md` |
| Verze | **v0.2** (revize 2026-05-07 ráno po HP Elite first-run) |
| Datum | 2026-05-06 EOD initial; 2026-05-07 ráno revize |
| Audience | Pete + governance + SecOps (ČKP) |
| Klíčové změny v v0.2 | (1) HP Elite re-klasifikace SUPIN-owned (NE Peteovo personal); (2) hostname `<test-runner-host>` zaznamenán; (3) HP Elite je první běhové prostředí, ThinkPad je preview; (4) personal vs SUPIN-owned rozdělení explicitní pro SecOps audit |
| Status | aktivní; HP Elite první run úspěšný; čeká na DEMO drift resolution (`recon/DRIFT-2026-05-07-...md`) |
