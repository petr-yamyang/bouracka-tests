# Bouračka UI v0.1.0 — Troubleshooting (CS)

Pokud něco nefunguje, najděte níže symptom a postupujte podle receptu. Pokud nic neodpovídá, připojte diagnostický snapshot (stránka `/runs` → ⬇ Diagnostics) a pošlete e-mail Petovi.

---

## §1. Port 8424 už používán / „Errno 10048" při startu

**Symptom:**

```
ERROR: [Errno 10048] error while attempting to bind on address ('127.0.0.1', 8424)
(česky: normálně je povoleno pouze jedno použití každé adresy ... soketu)
```

**Proč:** dřívější proces `bouracka-ui` stále běží. Nejčastější příčina: zavření okna PowerShellu bez Ctrl+C první — uvicorn worker subproces přežije a drží port.

**Oprava:** spusťte přibalený `kill-stragglers.ps1`:

```powershell
.\kill-stragglers.ps1
```

Nebo ručně:

```powershell
# Najdi, co drží 8424
Get-NetTCPConnection -LocalPort 8424 -State Listen -ErrorAction SilentlyContinue |
  ForEach-Object {
    $p = Get-Process -Id $_.OwningProcess
    Write-Host "Killing $($p.ProcessName) (PID $($p.Id))"
    Stop-Process -Id $p.Id -Force
  }

# Sanity check — teď by mělo vrátit nic
Get-NetTCPConnection -LocalPort 8424 -State Listen -ErrorAction SilentlyContinue
```

Pak znovu spusťte `bouracka-ui`.

---

## §2. `pip install` selže s „Access Denied" (Přístup byl odepřen) na .pyd souboru

**Symptom:**

```
ERROR: Could not install packages due to an OSError: [WinError 5]
Přístup byl odepřen: '...\.venv\Lib\site-packages\~-bsockets\speedups.cp310-win_amd64.pyd'
```

Prefix `~-bsockets` nebo `~ttptools` na názvu adresáře znamená, že předchozí pip pokus o instalaci nechal napůl uklizený orphan. Soubor .pyd drží proces, který ho nepustí.

**Oprava:** zabijte držitele + smažte orphany.

```powershell
# 1. Zabij držící proces (typicky starý bouracka-ui server)
.\kill-stragglers.ps1

# 2. Smaž orphany (adresáře začínající tildou)
$venvSite = ".\.venv\Lib\site-packages"
Get-ChildItem $venvSite -Directory | Where-Object Name -like "~*" | Remove-Item -Recurse -Force

# 3. Zkus instalaci znovu
pip install --force-reinstall bouracka_ui-0.1.0-py3-none-any.whl
```

Pokud `Remove-Item` stále hlásí Access Denied i po zabití procesu, restartujte Windows (poslední možnost, ale spolehlivá).

---

## §3. Stránka výsledků dlouho ukazuje „Run not found: run-..."

**Chování:** UI vás přesunulo na `/results/<run_id>` dřív, než běh stihl zapsat envelope na disk.

**Stav v v0.1.0:** **opraveno.** Stránka výsledků se teď pollne každé 2 s a ukazuje pilulku statusu „running", dokud envelope nedorazí. Pokud vidíte „Run not found" trvale déle než 90 s, je něco jiného špatně — viz §4.

Pokud máte buildy starší než v0.1.0 a nemůžete upgradovat, workaround je: počkat 30–60 s, pak kliknout na odkaz Reload na stránce.

---

## §4. Běh se spustí, ale dispatch tiše selže (žádný envelope nikdy nevznikne)

**Symptom:** stránka výsledků ukazuje `dispatch failed — no envelope produced`. Nebo to vidíte s „Run not found", pokud jste na buildu v0.0.x.

V v0.1.0+ stránka „dispatch failed" zobrazuje seznam čtyř nejčastějších kandidátních příčin přímo na stránce; vyberte tu, která odpovídá vašemu logu:

**(a) Binární soubor frameworku chybí na PATH.** `npx` / `cypress` / `playwright` není nainstalovaný. Log ukazuje `tooling not found: [WinError 2]`.
- Nainstalujte Node.js 18+ z nodejs.org → restartujte PowerShell → restartujte bouracka-ui.
- Pro Cypress: z kořene repa: `npm install cypress --save-dev`
- Pro Playwright: `npm install @playwright/test --save-dev; npx playwright install`

**(b) pytest plugin chybí.** `pytest-json-report` není v venv. Log ukazuje `unrecognized arguments: --json-report`.
- v0.1.0+ wheel auto-instaluje `pytest-json-report` jako runtime dependency. Pokud na to přesto narazíte, spusťte `pip install pytest-json-report` ve venv.

**(c) Kořen repa špatně detekován.** bouracka-ui nemůže najít `tools/consolidate_results.py`. Log ukazuje cestu konsolidátoru uvnitř `.venv/` nebo jiného špatného adresáře.
- v0.1.0+ wheel auto-detekuje kořen repa procházením nahoru z CWD a hledáním markeru `tools/consolidate_results.py`. Pokud detekce přesto selže, override přes env proměnnou:

   ```powershell
   $env:BOURACKA_UI_REPO_ROOT = "C:\Users\you\path\to\bouracka-tests"
   bouracka-ui
   ```

**(d) Žádné test specy nevyhovují.** Vaše TC selekce produkuje glob, který se nerozpouští na žádné spec soubory na disku.
- Ověřte, že `cypress/e2e/**/*<tc-token>*.cy.ts` (nebo ekvivalent pro playwright/selenium) skutečně existuje pro TC, který jste vybrali.

**Univerzální fallback — mock mode** (pro demo / iteraci UI bez reálných prohlížečů):

```powershell
$env:BOURACKA_UI_DISPATCH_MODE = "mock"
bouracka-ui
```

Otevřete `/about` v UI pro zobrazení dostupnosti nástrojů (npx / python / consolidate_results — všechny s green/red statusem).

---

## §5. „Workbook locked" (HTTP 409) při zakládání bugu

**Symptom:** kliknutí „File bug" dá `409 Workbook locked (Excel open?)`.

**Proč:** Excel má `BOURACKA-TESTPLAN-*.xlsx` otevřený. `openpyxl` nemůže zapisovat, dokud je výlučně zamčený.

**Oprava:** zavřete workbook v Excelu a zkuste znovu. Žádná data se neztratí.

---

## §6. Testy selhávají s „selector not found" nebo podobně — ale včera prošly

**Pravděpodobná příčina:** drift. Stránky bouracka.cz mohly být přenasazeny s novými selektory, verzemi reCAPTCHA atd.

**Co s tím:**

1. Zkontrolujte kartu **drift forensic** na stránce výsledků (pokud je viditelná).
2. Pokud je detekován drift pattern (`recaptcha-v3` je nejčastější), dotčené TC budou automaticky označeny `skip-drift` — to není regrese ve vašem kódu, je to známé omezení.
3. Pokud TC označené `fail` nesouvisí s driftem, založte bug podle §5 OPERATOR-GUIDE-CS.md.

---

## §7. Prohlížeč otevře prázdnou stránku / 502 / nemůže se připojit

**Symptom:** spustili jste `bouracka-ui`, ale auto-otevřený prohlížeč ukazuje „Tento web nelze dosáhnout" nebo podobně.

**Kontroly:**

1. Okno PowerShellu — server skutečně běží? Hledejte `INFO: Application startup complete.` a `Uvicorn running on http://127.0.0.1:8424`.
2. Pokud server hlásí Errno 10048, viz §1.
3. Pokud server normálně nastartoval, ale prohlížeč se nemůže připojit, zkontrolujte firewall: firemní firewally někdy blokují loopback porty >1024. Zkuste jiný port:

   ```powershell
   bouracka-ui --port 18424
   ```

   ...a otevřete http://127.0.0.1:18424/ ručně.

---

## §8. „Loading…" navždy na stránce Run

**Symptom:** stránka `/run` ukazuje „Loading TCs…" a nikdy nepokročí.

**Proč:** workbook nelze otevřít (špatná cesta, poškozený nebo Excel ho má v exkluzivním zámku).

**Oprava:**

1. Otevřete `/about` a podívejte se na řádek **workbook**. Pokud červený → špatná cesta nebo soubor chybí.
2. Zkontrolujte, že `BOURACKA-TESTPLAN-*.xlsx` je ve stejné složce jako wheel (nebo předejte `--workbook PATH` pro override).
3. Zavřete jakoukoli otevřenou instanci Excelu, která drží soubor.
4. Otevřete DevTools prohlížeče (F12) → záložka Console → hledejte skutečnou chybu z neúspěšného API volání.

---

## §9. Po `git pull` se testy chovají jinak

Tento průvodce je dodán se zmrazeným wheelem — `git pull` nového kódu v repu bouracka-tests NEOVLIVNÍ nainstalovaný binární soubor bouracka-ui. Pro zachycení nových změn bouracka-ui potřebujete nový wheel.

Pokud jste vývojář kolokovaný s touto instalací (tj. máte naklonované repo), udělejte:

```powershell
cd <bouracka-tests>\bouracka_ui
python -m build
pip install --force-reinstall dist\bouracka_ui-*.whl
```

---

## §10. Cokoli jiného

Připojte **diagnostický snapshot** k vašemu bug reportu:

1. Otevřete `/runs` v UI.
2. Klikněte na **⬇ Diagnostics** (vpravo nahoře).
3. Uložte výsledný ZIP.
4. Připojte k bug reportu (nebo pošlete Petovi e-mailem).

Obsahuje: server health, cestu workbooku + dostupnost nástrojů, info o OS, nedávné serverové log řádky, žádné PII.

---

## Příloha A — Známá omezení

- **v0.1.0** dodává MOCK fallback, když nástroje chybí — to je úmyslné, ale znamená, že můžete mít zelenou výsledkovou stránku bez toho, aby skutečně běžel jakýkoli prohlížeč. Zkontrolujte `/about` pro potvrzení real-mode dispatche.
- **Per-framework retry** není zatím podporovaný. Pokud Cypress flakne, musíte re-runnout celou TC sadu.
- **Souběžné běhy** nejsou podporovány. Pouze jeden dispatch najednou; další POST /api/runs během běhu uspěje, ale logy se prolnou.
- **Žádná autentizace** — UI poslouchá pouze na `127.0.0.1` (loopback). Neexponujte na veřejné rozhraní.

Konec TROUBLESHOOTING-CS.md
