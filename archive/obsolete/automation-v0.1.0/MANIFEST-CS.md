# MANIFEST — bouracka-tests automatizace v0.1.0 — CS

> **Co tento balíček obsahuje:** plnou automatizační framework sadu —
> kód (Playwright/Cypress/TestCafe), testovací plán (Excel), všechny
> instalační dokumenty, validační skripty, smoke test. **Samostatný
> balíček** — instalovatelný SecDev týmem bez odkazů na jiné zdroje.
>
> **Cíl:** SUPNB001 + SUPNB002 + SUPNB003 (HP EliteBook G11 class,
> Win 11 Enterprise 25H2).

## Co dělat — krok za krokem

### 1. Rozbalte balíček

Balíček dorazil v ZIP dílech. Postup v
`_install/EMAIL-DELIVERY-GUIDE-CS.md`.

### 2. Otevřete instalační průvodce

`
INSTALL-CS.md   ← v kořeni balíčku, hlavní dokument pro SecDev
`

Průvodce vás provede:
- Co musí povolit SecOps (firewall allowlist + AppLocker pravidla)
- Co stáhnout (Node.js MSI nebo winget)
- Jeden příkaz pro instalaci (`setup-from-zero.ps1`)
- Diagnostiku selhání

### 3. Spuštění one-command setup

Po přípravě prostředí:

`powershell
cd C:\Users\<vy>\bouracka-tests
.\scripts\setup-from-zero.ps1
`

Cca 8–12 minut. Konec hlásí `[OK] sada je nainstalována a otestována`.

### 4. Předání testerovi

Po zelené kontrole je sada připravená. Tester se řídí `README-CS.md`
v kořeni balíčku.

## Obsah balíčku — strom

`
bouracka-tests/                              ← top-level kontejner
├── INSTALL-CS.md                            ← SecDev hlavní průvodce
├── README-CS.md                             ← README pro testera
├── README-EN.md                             ← README pro testera (EN)
├── package.json                             ← deklarace závislostí
├── package-lock.json                        ← uzamčené verze

├── BOURACKA-TESTPLAN-v0.1.xlsx              ← TestPlán + TC List (12 listů)
├── env/                                     ← konfigurace prostředí
├── fixtures/                                ← testovací data (bez secrets)
├── playwright/                              ← Playwright framework
├── cypress/                                 ← Cypress framework
├── testcafe/                                ← TestCafe framework
├── scripts/                                 ← všechny .ps1 skripty
├── tools/                                   ← pomocné nástroje
├── _install/                                ← všechny instalační dokumenty
├── _specs/                                  ← formální specifikace
└── specs/                                   ← per-TC SPEC.md soubory
`

## Co tento balíček NEOBSAHUJE

- Recon materiály, fotografie, drift logy — interní pracovní materiály
  (jsou v samostatném balíčku `analytical-v0.1.0` pro recenzi).
- `node_modules/` — instaluje se `npm ci` z `package-lock.json`.
- `runs/` — výsledky testů, vznikají během provozu.
- `secrets/` — citlivá testovací data; dodává se odděleně OOB.
- Playwright Chromium binárka (~600 MB) — stahuje
  `npx playwright install chromium` během setup.

## Síťové požadavky pro instalaci

Detail v `INSTALL-CS.md` §1.1. Stručně:
- `registry.npmjs.org` (npm balíčky)
- `cdn.playwright.dev` (Chromium binárka)
- `github.com` (občas)

## Síťové požadavky pro provoz

Detail v `INSTALL-CS.md` §1.1. Stručně:
- `tst.bouracka.cz` + `tst.demo.bouracka.cz` (testovací prostředí)
- `*.supin.cz`, `*.ckp.cz` (CDN + integrace)

## Reportování problémů

E-mail: `petr.yamyang@gmail.com`
Subjekt: `[BOURACKA-TESTS INSTAL] <konkrétní problém>`

## Verze

| Položka | Hodnota |
|---------|---------|
| Verze | v0.1.0 |
| Datum sestavení | 2026-05-05 |
| Sestavil | vitez na LAPTOP-7697MAU5 |
| Offline npm cache | NE (online install vyžadován) |
| Stav | v0.1 — připraveno pro SecDev |
