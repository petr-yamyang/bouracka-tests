# E-mail šablony pro odeslání v0.3 balíčků

> **Použití.** Zkopírujte do nového e-mailu, doplňte adresáty a přiložte.

---

## §1. E-mail #1 — analytický balíček (pro SUPIN/ČKP review)

**Předmět:** `Bouračka R1 — analytický balíček v0.3 — 2026-05-06`

**Adresáti:** SUPIN architekti, ČKP review board, vedoucí QA

**Příloha:** `bouracka-analytical-v0.3.0.zip` (~230 KB) — viz §3 níže

**Tělo:**

```
Vážená paní / vážený pane,

zasílám analytický balíček Bouračka R1 ve verzi v0.3 (datum 2026-05-06).

Tato verze je významný update proti v0.2 z 2026-05-05. Důvod: v noci
2026-05-05/06 se DEMO Bouračka (demo.bouracka.cz/formular) stala
veřejně dostupnou bez IP-restrikce, což umožnilo živou reverzní analýzu
end-to-end. Balíček je kompletně přepracován z této živé evidence
(bottom-up), s vědomím že předchozí analytický dokument (~mid-2025)
byl 10 měsíců starý a v některých aspektech nepřesný.

Klíčové výstupy v0.3:

1. Test-plán BOURACKA-TESTPLAN-v0.3.xlsx s 28 TestTargets a 48 TestCases
   (25 nových TC odvozených z živé analýzy). Nový sloupec env_constraints
   klasifikuje každý TC: both / demo-only / prod-only / both-with-adapter.

2. Δ matice DEMO vs PROD s 26 řádky (8 potvrzeno z živé analýzy):
   N8 SMS Gateway, AISPOV registry, zenID OCR, branding, Maps locale,
   email rozeslání atd.

3. UML diagramy (use-case + activity + sequence) podle VUP/UML 2.5.

4. Bottom-up analytický dokument s 11 explicitními opravami toho, co
   původní dokument popisoval nepřesně.

5. 9 integrací (INT-001..INT-009) — 4 nové: Azure outage feed,
   Google Maps API, interní /api/reports REST surface, ČÚZK RUIAN.

6. Plné číselníky z živého API: 13 pojišťoven, 275 značek vozidel,
   17 ŘP kategorií, 18 typů pohybu, 8 zón poškození, 5 typů nehody.

7. Návrh 4 vad k validaci (Google Maps locale, identifikační kód
   prefix, ?validate=false param, /api/enumerations/licenseCategories
   403) — viz §2.5 v 00_README-CS.md.

8. Návrh 6 položek k rozhodnutí ze strany SUPIN/ČKP (N8 sandbox,
   AISPOV přístup, zenID test-keys atd.) — viz §4 v 00_README-CS.md.

Dokumenty v archivu (8 souborů + Excel + 3 PUML zdroje), celkem
~230 KB. Verifikujte SHA256 podle MANIFEST-CS.md.

S pozdravem,
[jméno]
```

---

## §2. E-mail #2 — automation balíček (pro testovací tým)

**Předmět:** `Bouračka — automation suite v0.3 + instalační příručka`

**Adresáti:** testovací tým, SecOps (pro allowlist review)

**Příloha:** `bouracka-automation-v0.3.0.zip` (~2.3 MB) — viz §3 níže

**Tělo:**

```
Ahoj,

posílám automation suite ve verzi v0.3 (datum 2026-05-06) — kompletní
runnable balíček pro testování DEMO Bouračky a (po doplnění N8 sandbox /
AISPOV přístupu) PROD Bouračky.

Co je v balíčku (~2.3 MB):

- bouracka-tests-v0.3.0.zip — celý source code (Playwright + Cypress
  scaffolding + TestCafe scaffolding + Mockoon profil + tools)
- INSTALL-FROM-ZERO-v0.3-CS.md — krok-za-krokem instalační příručka
  z čisté instalace Windows
- MANIFEST-CS.md — SHA256 + obsah balíčku

Jak začít (cca 30 minut):

1. Rozbalte ZIP do C:\bouracka-tests\
2. Otevřete INSTALL-FROM-ZERO-v0.3-CS.md a postupujte §2 (instalace
   Pythonu, Node.js, JRE — POŽADUJE ADMIN OPRÁVNĚNÍ)
3. Po §5 spusťte první test:
     .\scripts\run-bring-up-smoke.ps1
   Očekávaný výsledek: 1 test passed proti DEMO.

Důležité podmínky:

- Instalace v §2 vyžaduje dočasná admin práva (winget pro Python +
  Node + JRE).
- Síťový allowlist musí povolit npmjs.com, pypi.org, github.com,
  playwright.download.prss.microsoft.com, cdn.playwright.dev.
- DEMO testy nevyžadují žádný login ani VPN.
- Pro PROD testy potřebujeme N8 sandbox sandbox / skip-flag — zatím
  blokuje 5 prod-only TC.

Intel-probes (volitelné, ale doporučené po prvním běhu):

  npx playwright test playwright/tests/intel-probes/

Tyto probe-testy obohatí naše artefakty reálnými daty z DEMO API:
plné číselníky, Zod schémata z bundle, network traces. Detail v
playwright/tests/intel-probes/README-OPERATOR.md.

Pokud něco selže, viz §13 ("Co dělat, když něco selže") v instalační
příručce.

Díky,
[jméno]
```

---

## §3. Příprava ZIPů na odeslání

Z `delivery/analytical-v0.3.0/` a `delivery/automation-v0.3.0/`
vytvořte 2 archivy (PowerShell):

```pwsh
cd C:\Users\vitez\Documents\VibeCodeProjects\SUPIN\bouracka-tests

# Analytický balíček (1 ZIP, ~230 KB)
Compress-Archive -Path delivery\analytical-v0.3.0\* `
                 -DestinationPath delivery\bouracka-analytical-v0.3.0.zip `
                 -CompressionLevel Optimal -Force

# Automation balíček (1 ZIP, ~2.3 MB — obsahuje vnitřní bouracka-tests-v0.3.0.zip)
Compress-Archive -Path delivery\automation-v0.3.0\* `
                 -DestinationPath delivery\bouracka-automation-v0.3.0.zip `
                 -CompressionLevel Optimal -Force

# Verifikace
Get-FileHash delivery\bouracka-analytical-v0.3.0.zip -Algorithm SHA256
Get-FileHash delivery\bouracka-automation-v0.3.0.zip -Algorithm SHA256

# Velikost
Get-Item delivery\bouracka-*.zip | Format-Table Name, Length
```

## §4. Konfidenciální poznámky před odesláním

- **Žádné citlivé údaje** v balíčku nejsou (test data jsou syntetická).
- **API klíč Google Maps** (`AIzaSyACdtrV1A1LCbZTCpEI0j9Xbz0I_x0vCHs`)
  v `recon/integrations/INT-007.md` je veřejně viditelný v URL na
  DEMO bundle — není to únik, jen pozorování.
- **reCAPTCHA site-key** (`6Lfbao4sAAAAANfSk_-NcqLZPYB8wdMvrBS4qM5p`)
  podobně veřejný.
- DEMO endpointy jsou všechny veřejně přístupné — ničemu neškodí
  jejich katalog v archivu.
- PROD endpointy nejsou v balíčku popsány (jen předpokládány).

## §5. Status

| Item | Hodnota |
|------|---------|
| Email šablony | 2 (analytický + automation) |
| Velikost analytického ZIPu | ~230 KB |
| Velikost automation ZIPu | ~2.3 MB |
| Volume split | NE — vejdou se do 1 e-mailu |
| Status | připraveno k odeslání |
