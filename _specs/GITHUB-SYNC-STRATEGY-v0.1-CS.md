# GitHub sync + SUPIN-isolation strategy — v0.1 CS

> **Trigger.** CP-SUPIN-04 STEP 32 (2026-05-06): Pete direction —
> "GitHub use would be synchronised with our project relevant artifacts
> as well as creation of internal SUPIN storage branch if it already make
> sense — SUPIN team has it s own which is now not accessible and our
> development should be independent on use of any SUPIN infrastructure
> as a basic rule for now."
>
> **Audience.** Pete + governance + future CI integrators.
> **Cíl.** Definovat strategii pro GitHub jako náš primary repo home,
> s budoucí sync cestou do SUPIN internal storage AŽ se k němu dostaneme.

---

## §1. Hlavní pravidlo: nezávislost od SUPIN infrastruktury

**Žádný náš artefakt nesmí předpokládat dostupnost SUPIN/ČKP infrastruktury
jako blocker.**

To znamená:
- ❌ Žádné SUPIN-only Git remote endpoints v configu
- ❌ Žádný SUPIN VPN-required CI/CD trigger
- ❌ Žádný build artifact, který se publikuje JEN do SUPIN private storage
- ❌ Žádný hardcoded URL do SUPIN internal services (jen environment variables)

Vše musí běžet **z public veřejně-dostupných zdrojů** (GitHub.com, npm,
PyPI, Microsoft winget) + naše vlastní GitHub repo.

Pokud SUPIN team obnoví přístup ke svému internal storage, **přidáme**
mirror branch (jednosměrný push), ne migration.

## §2. Repo struktura na GitHubu

### §2.1 Návrh repository organization

```
github.com/{owner}/...
├── bouracka-tests/                      ← primary public repo (this dev)
│   └── (current bouracka-tests/ contents)
│
├── SUPIN-ecosystem-map/                 ← second public repo
│   └── (current SUPIN-ecosystem-map/ contents)
│
└── (future)
    ├── x1-tests/                        ← per-system repo when X1 fragments arrive
    ├── ... další SUPIN systémy
```

**Owner:** Pete's personal GitHub (preferred for now — fastest path)
nebo vytvořená org `supin-bouracka-test` / `cko-pojistitelu-test`.

### §2.2 Repo posture per visibility

| Repo | Visibility | Rationale |
|------|------------|-----------|
| `bouracka-tests` | private (Pete + invited testers) | testovací data sice synthetic, ale TestCases popisují SUPIN business logic |
| `SUPIN-ecosystem-map` | private | architektonický recon SUPIN ekosystému |
| (volitelně public) | mirror s sanitized fragmenty | pro MI-M-T methodology contributions, NE pro SUPIN-specific data |

## §3. Sync strategy

### §3.1 Primary remote: GitHub (this dev)

Aktuální stav: žádný Git remote nakonfigurovaný (lokální file system only).

První iterace:
```pwsh
cd C:\Users\vitez\Documents\VibeCodeProjects\SUPIN\bouracka-tests
git init
git remote add origin git@github.com:{user}/bouracka-tests.git
git add .
git commit -m "Initial CP-SUPIN-04 v0.4.x deliverable snapshot"
git push -u origin main
```

A separately pro SUPIN-ecosystem-map:
```pwsh
cd C:\Users\vitez\Documents\VibeCodeProjects\SUPIN\SUPIN-ecosystem-map
git init
git remote add origin git@github.com:{user}/SUPIN-ecosystem-map.git
git add .
git commit -m "Initial CP-SUPIN-04 STEP 30 ecosystem map scaffold"
git push -u origin main
```

### §3.2 Future SUPIN internal mirror (TBD, NOT now)

Až SUPIN obnoví access:

```pwsh
# Add second remote (push-only mirror)
git remote add supin-internal https://supin-internal-git.ckp.cz/{path}/bouracka-tests.git

# One-way sync: github.com → supin-internal
git push supin-internal main

# (NEVER pull from supin-internal — keep github.com as source of truth)
```

**Kritické:** SUPIN internal je **zrcadlo, ne primary**. Náš dev cycle
běží proti GitHubu. SUPIN internal dostane snapshots po milestoneech.

## §4. Co commit-uje, co ne

### §4.1 Co BĚŽÍ na GitHubu

- ✅ Source code (Playwright/Cypress/TestCafe/ReadyAPI/Postman/Selenium tests)
- ✅ Documentation (markdown, UML, Excel template structure — SCHEMA only)
- ✅ Tools (Python migration scripts, helpers)
- ✅ Test fixtures (synthetic data only)
- ✅ Recon docs (analytical artifacts; ČKP review-grade)
- ✅ Strategy + governance docs

### §4.2 Co NEjde na GitHub

- ❌ `node_modules/` (~200 MB, generated)
- ❌ `test-results/` + `playwright-report/` (run outputs)
- ❌ `fixtures/intel-YYYY-MM-DD/` (intel-probe captures — może obsahovat citlivá data)
- ❌ Real ČKP test-credentials, real PROD URLs s tokeny
- ❌ Real občanské/řidičské/SPZ numbers (jen synthetic)
- ❌ N08-test sandbox URLs (post-receive — TBD)

### §4.3 `.gitignore` template

```gitignore
# Dependencies
node_modules/
__pycache__/
.venv/
.env
.env.local

# Test outputs
test-results/
playwright-report/
allure-results/
allure-report/
fixtures/intel-*/

# Real-data fixtures (PII-adjacent)
fixtures/tester-contacts.yaml         # operator-filled, never committed

# OS / IDE
.DS_Store
Thumbs.db
*.swp
.vscode/
.idea/

# Build outputs
delivery/*.zip
delivery/*/*.zip

# Secrets
*.pem
*.key
config.local.*
.env.production
```

## §5. Branching model (GitHub)

| Branch | Účel | Push policy |
|--------|------|-------------|
| `main` | stable; current Opus release (e.g. v0.4.6) | direct push from Opus session |
| `dev/cp-supin-04` | active iteration | active development; merge to main per release |
| `feature/...` | per-Sonnet-session branch | when handing off to dedicated session |
| `archive/v0.X.Y` | tagged historical releases | snapshot only |

### §5.1 Per-target branches (longer-term)

```
feature/cil-1-demo-public        ← Cíl 1 work
feature/cil-2-demo-tst           ← Cíl 2
feature/cil-3-tst-bouracka       ← Cíl 3 (gated on N08 sandbox)
feature/cil-4-prelive            ← Cíl 4 (future)
```

Sonnet sessions work on `feature/...` branches; merge to `dev/...` then
`main` after Opus governance review.

## §6. CI/CD strategy (deferred to CP-SUPIN-05)

### §6.1 GitHub Actions (when ready)

Můžeme spustit testy na:
- **Public DEMO** (`demo.bouracka.cz`) — bez VPN; běží z GitHub-hosted runner
- **Self-hosted runner** (Pete's ThinkPad) — pro DEMO_tst / PROD_tst (vyžaduje VPN)

Trigger:
- Push to `dev/...` → run smoke + alternates
- Pull request to `main` → run full suite
- Nightly cron → full regression cross-env

### §6.2 Independence z SUPIN CI

SUPIN má vlastní Jenkins / Azure DevOps interně. **Naše Actions
neimplikují** SUPIN CI access. Po obnově access můžeme:
- Replicate Actions logic do SUPIN Jenkins
- NEBO publikovat status webhook z Actions do SUPIN dashboard

## §7. Permissions + collaborators

| Role | Permissions | Examples |
|------|-------------|----------|
| Owner | full | Pete |
| Admin | merge, settings | (future Sonnet sessions) |
| Write | branch, PR | testers |
| Read | clone, view | SUPIN architects (read-only review) |

Plus eventual GitHub teams when SUPIN team get access.

## §8. Migration path (SUPIN → us → us+SUPIN)

Per Pete: "creation of internal SUPIN storage branch if it already make
sense — SUPIN team has it s own which is now not accessible".

Mental model:
```
   Today:   GitHub (Pete) ─── primary, only home
   Phase 2: GitHub (Pete) ─→ SUPIN-internal mirror (push only)
   Phase 3: GitHub (Pete) ←→ SUPIN-internal (full bidirectional, governed)
```

Phase 2 entry condition: SUPIN team obnoví internal storage access for Pete.
Phase 3 entry condition: SUPIN team agrees on dual-source-of-truth governance.

## §9. Aktuální action items (CP-SUPIN-04 STEP 32+)

- [ ] Pete: vytvořit GitHub repos (`bouracka-tests` + `SUPIN-ecosystem-map`)
- [ ] Pete: `git init` + initial commit + push
- [ ] Pete: nastavit `.gitignore` per §4.3
- [ ] Opus: emit per-iteration commit message (when this Opus session writes
      something, commit it semantically — "feat: ...", "fix: ...", "docs: ...")
- [ ] CP-SUPIN-05: GitHub Actions workflow scaffold

## §10. Kritická dependency — žádná na SUPIN

| Náš artifact | Závisí na SUPIN? | Náhradní zdroj |
|--------------|-------------------|------------------|
| Playwright code | NE | npm (public) |
| Bouračka SUT URL | bouracka.cz / demo.bouracka.cz (public DNS) | n/a |
| ČÚZK RUIAN | NE — public state service | n/a |
| Google Maps key | hardcoded v Bouračka SUT bundle | n/a |
| reCAPTCHA key | hardcoded v Bouračka SUT bundle | n/a |
| Excel master | náš generated artifact | n/a |
| GitHub | NE — public service | n/a |
| Pete's machine | NE | můžete přesunout na jakoukoliv stanici |

→ **Žádný blocking dependency na SUPIN access.** Náš dev cycle funguje
samostatně. Až SUPIN access obnoven, jen přidáme sync.

## §11. Status

| Item | Hodnota |
|------|---------|
| Strategy | `_specs/GITHUB-SYNC-STRATEGY-v0.1-CS.md` |
| Verze | v0.1 |
| Datum | 2026-05-06 |
| Audience | Pete + governance + future CI integrators |
| Status | strategy locked; first GitHub push pending Pete's action |
