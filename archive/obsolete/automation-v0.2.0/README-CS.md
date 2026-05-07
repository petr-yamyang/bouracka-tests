# bouracka-tests — Příručka pro testera (CS)

Automatizovaná testovací sada pro `tst.bouracka.cz` a `tst.demo.bouracka.cz`.
Ship verze: `v0.1.0` (CP-SUPIN-02 seed; první funkční scénáře přijdou v `v0.1.1`).

## 1. Předpoklady na notebooku testera

| Položka | Verze | Poznámka |
|---------|-------|----------|
| Windows | 10 / 11 | x64 |
| Node.js | ≥ 18.x (doporučeno 20 LTS) | bez admin-instalace, pokud Node již existuje |
| npm | ≥ 9 | součástí Node |
| Chrome / Chromium | ≥ 132 | Playwright si stáhne vlastní binárku |
| PowerShell | 5.1 / 7+ | Windows native |
| Síťový přístup | `tst.bouracka.cz`, `tst.demo.bouracka.cz` zevnitř SUPIN sítě |

## 2. První spuštění

```powershell
# 1. Rozbal zip do libovolné složky (např. C:\Tests\bouracka-tests)
cd C:\Tests\bouracka-tests

# 2. Instalace závislostí (jednorázová)
npm install
npx playwright install chromium

# 3. Spusť všechny tři frameworky proti TST
.\scripts\run-all.ps1 -Env tst

# 4. Zabal výsledky pro odeslání zpět
.\scripts\package-results.ps1 -Tester "tve-prijmeni"
```

Vznikne `bouracka-results-YYYY-MM-DD-tve-prijmeni.zip` — odešli zpět autorovi
(SHA256 najdeš v souboru `SHA256SUMS-*.txt` vedle zipu).

## 3. Spuštění jednoho frameworku

```powershell
.\scripts\run-playwright.ps1 -Env tst
.\scripts\run-cypress.ps1    -Env tst-demo
.\scripts\run-testcafe.ps1   -Env tst
```

Volby `-Env`: `tst` | `tst-demo` | `public` (`public` je jen pro vývoj — proti
veřejné produkci `bouracka.cz` se ostré scénáře neprovádí).

## 4. Co je v deliverable v0.1

- Adresářová struktura per scope §8 — tři frameworky + sdílené env config + fixtures.
- Excel TestPlan `BOURACKA-TESTPLAN-v0.1.xlsx` — 11 listů, ItemBase sloupce, Sev × Urg → Pri.
- Playwright + Cypress + TestCafe scénáře pro **TC-CP-001** (vstup do formuláře — happy)
  a **TC-CP-002** (větvení Policie ČR — failure pair).
- Skeleton specs pro **TC-CP-003** + **TC-CP-004** (průvodce end-to-end) — implementace
  čeká na user-supplied recon templates pro `tst.*` (OQ-CP-15) a rozhodnutí o
  reCAPTCHA postoji (OQ-CP-14).

## 5. Mobile-first — viewport sweep

Každý běh Playwright projíždí 4 viewporty per env:
- desktop (1280×720)
- mobile-320 (320×568)
- mobile-375 (375×667)
- mobile-414 (414×896)

Cypress viewporty se nastavují pomocí `cy.viewportPreset()` (viz
`cypress/support/e2e.ts`).

## 6. Top 5 pravděpodobných chyb a jak je řešit

| Chyba | Příčina | Řešení |
|-------|---------|--------|
| `npm install` timeout | proxy / firewall blokuje registry.npmjs.org | nastavit npm proxy: `npm config set proxy http://...` |
| `npx playwright install` selže | omezení adminu | spustit jako uživatel s právy zápisu do `%LOCALAPPDATA%\ms-playwright`; firewall pro `cdn.playwright.dev` |
| `Cypress not found` | ne-stažená binárka | `npx cypress install` |
| Test selhává: `tst.bouracka.cz` not reachable | mimo SUPIN síť nebo VPN ne-připojená | ověřit `Test-NetConnection tst.bouracka.cz -Port 443` |
| reCAPTCHA challenge se zobrazí v `tst.*` | bypass token nenakonfigurován | viz `env/tst.json::recaptcha_bypass_token` — nastavit z OOB e-mailu od autora |

## 7. Důvěrnost

- Tato sada **neobsahuje** žádné citlivé údaje. Reálné testovací přihlášení,
  čísla, OP/ŘP atd. dostáváš odděleně (e-mail) a ukládáš do `fixtures/secrets/`
  (gitignored). Po skončení iterace `secrets/` smaž.
- Výsledky (`runs/`, `bouracka-results-*.zip`) **mohou** obsahovat
  personalizovaná data (screenshoty, network logs). Než zip pošleš zpět,
  zkontroluj.

## 8. Kontakt

`info@bouracka.cz` (provozovatel produktu — ČKP).
Autor sady: Petr Žemla (kontakt OOB).
