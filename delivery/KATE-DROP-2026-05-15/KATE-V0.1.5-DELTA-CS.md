# Bouračka UI v0.1.5.dev5 — co je nové od v0.1.4 (operátorský pohled)

**Verze tohoto dokumentu:** v1.0 (2026-05-15)
**Cílová role:** Kate (operátor testovacího prostředí)
**Cílový stroj:** SUPIN HP EliteBook s instalovanou v0.1.4 nebo čistou instalací z přibaleného `bouracka-ui-hp-elite-v0.1.5.dev5-CS-multi-abi.zip`
**Délka čtení:** ~5 minut
**Status:** **Interní dev build.** Verzový suffix `.dev5` je úmyslný — jedná se o integrační milestone, ne o produkční release. Funkční je plně. Release-engineering pass (Brief #008) ještě neproběhl, takže runbook `KATE-FROM-ZERO-INSTALL-CS.md` v tomto dropu stále píše "v0.1.4". **Instalační postup je identický** — držte se ho podle písmene; tento delta-dokument doplňuje pouze co nového uvidíte po instalaci.

---

## §1. Shrnutí změn v jedné větě

UI dostalo **6 nových REST endpointů**, **1 nové prostředí (ENV-DMO-PUB)**, **cross-framework check report** (nová stránka pro porovnání shody mezi runnery), a **workbook se posunul na v0.4.4** se třemi novými datovými strukturami (`02e_TestSteps`, `steps_count`, typované `evidence_*` sloupce na bugs).

---

## §2. Nový workbook — `BOURACKA-TESTPLAN-v0.4.4.xlsx`

| | v0.4.3 (předchozí) | v0.4.4 (tento drop) |
|---|---|---|
| List `02_TestCases` | bez `steps_count` | **přibyl sloupec `steps_count`** (počet kroků odvozený z `steps_summary` nebo přímo z nového listu `02e_TestSteps`) |
| List `02e_TestSteps` | **neexistuje** | **nový list** — jeden řádek na krok, s `step_code` ve formátu `STP-{TC}-{NN}` |
| List `08_Bugs` evidence | textové sloupce `screenshot_ref` + `trace_ref` | **přibyly typované sloupce** `evidence_path`, `evidence_kind`, `evidence_url`, `evidence_on_disk_flag`. Původní `screenshot_ref` + `trace_ref` zůstávají kvůli zpětné kompatibilitě. |

**Co to znamená v praxi:**
- V UI se na stránce `/run` objeví **počet kroků** u každého testcase (sloupec `Kroky`).
- Pokud zatím existuje TC s prázdným `framework_targets`, UI ho **správně započítá pro všechny frameworky** (cypress / playwright / selenium). To je dlouhodobé chování (BUG-K-001 fix v v0.1.4) — teď ho ale uvidíte poprvé na reálných datech, protože ve v0.4.4 přibyl `TC-CP-NEW-A` s prázdnou hodnotou.
- Žádný akce z Vaší strany — UI workbook auto-discovery najde nový soubor v kořeni instalace.

---

## §3. Nové REST endpointy (přehled — všechny GET, žádný breaking change)

| Endpoint | Co dělá | Kdy ho uvidíte v UI |
|---|---|---|
| `GET /api/tcs/{tc_code}/steps` | Vrátí seznam kroků pro daný TC | Po kliku na kód TC na stránce `/run` (FR-K-002 zatím v plánu na v0.1.5+) |
| `GET /api/steps/{step_code}` | Detail jednoho kroku podle kódu | Použije se v drill-down zobrazení (zatím napojení pouze API-side) |
| `GET /api/bugs/{bug_code}/evidence` | Vrátí strukturovanou evidenci k bugu (cesta + URL + flag „na disku") | Otevře se na stránce `/bugs` při proklikávání bug detailu (postupné UI napojení) |
| `GET /api/runs/{run_id}/cross-check` | **Nový hlavní výstup.** Cross-framework agreement projection (JSON) | Z výsledkové stránky `/results/{rid}` po kliku na "Cross-check report" |
| `GET /api/runs/{run_id}/cross-check.html` | Stejná data jako výše, ale jako samostatná HTML stránka (inline CSS, žádné externí závislosti) | Po stisku tlačítka „Stáhnout HTML report" — dostanete soubor, který můžete poslat e-mailem |
| `/api/runs/...` (statické soubory) | Servíruje artefakty (screenshoty, video, trace) z `runs/` adresáře | Nepřímo — UI dál odkazuje na artefakty přes tyto cesty |

**Verifikace endpointů po instalaci:** otevřete v prohlížeči `http://127.0.0.1:8424/api/health` — měli byste vidět:

```json
{ "schema_version": "1.0", "server_version": "0.1.5-dev5", "tools": { ... } }
```

Pokud `server_version` ukazuje `0.1.4` nebo cokoli jiného než `0.1.5-dev5`, instalace je **nedokončená** — opakujte krok §3 z `KATE-FROM-ZERO-INSTALL-CS.md`.

---

## §4. Nové prostředí — `ENV-DMO-PUB`

Drop-down `Prostředí` na stránce `/run` nyní obsahuje **4 položky** místo 3:

| Kód | URL | Účel |
|---|---|---|
| `ENV-PUB` | `https://www.bouracka.cz` | Public produkce (read-only, smoke pouze pro dev recon) |
| `ENV-TST` | `https://tst.bouracka.cz` | SUPIN-internal TEST (hlavní cíl pro Vaše smoke runy) |
| `ENV-DMO` | `https://tst.demo.bouracka.cz` | SUPIN-internal DEMO pro autoškolu — workbook ENV-DMO řádek |
| **`ENV-DMO-PUB`** | `https://demo.bouracka.cz` | **NOVÉ** — public DEMO, doplňkové, supplemental-merged přes `workbook_io.SUPPLEMENTAL_ENVS` |

`ENV-DMO-PUB` se v workbooku přímo neobjevuje — je injektovaná v UI při čtení seznamu prostředí. Pokud na něm spustíte smoke, dispatcher použije `https://demo.bouracka.cz` jako base URL.

---

## §5. Cross-check report — nová samostatná funkce

Na stránce `/results/{run_id}` (po doběhnutí runu) je nové tlačítko **„Cross-framework check"**. Otevře cross-check matici, která ukáže:

- **`agreement_summary`** — kolik TC se shoduje napříč všemi runnery (cypress + playwright + selenium), kolik diverguje
- **`divergent_tcs`** — konkrétní list TC, které runnery vrátily jinak (s detailem který runner co řekl)
- **`tc_full_matrix`** — celá matice TC × runner × verdikt, rozbalitelná

**Tlačítko „Stáhnout HTML"** vedle reportu uloží samostatný HTML soubor (asi 50–100 KB), který si můžete poslat e-mailem nebo přiložit k bug ticketu. HTML je zcela soběstačný (inline CSS, žádné externí závislosti, žádný JavaScript) — funguje i offline.

**Užitečné kdy:** když runnery hlásí různá verdikta pro stejný TC, často je to skutečný divergence (potenciální BUG), ne flaky test. Cross-check report toto pomáhá rychle identifikovat bez nutnosti procházet tři log soubory.

---

## §6. Co zůstává naprosto stejné

- **Instalační postup.** Krok-po-kroku podle `KATE-FROM-ZERO-INSTALL-CS.md` v tomto dropu — žádná změna v sekvenci `pip install`, žádná změna v cílovém adresáři `C:\TestAutomationSite\`, žádná změna v aktivačním port `8424`.
- **`bouracka-ui` startovací příkaz.** Pořád `python -m bouracka_ui` (nebo přes ikonu na desktopu, pokud jste si ji vytvořila).
- **UI navigace.** Stejné čtyři stránky: `/run` · `/runs` · `/results/{rid}` · `/bugs` · `/about`.
- **Bug filing workflow.** Stejné — vytvořit / editovat / re-test. Příprava bugu skrz `/results/{rid}` → klik na TC → „Filovat bug".
- **Workbook governance.** Pravidlo „jeden workbook v kořeni instalace" platí dál (BUG-K-003 fix z v0.1.4). Pokud ve své instalaci vidíte více `BOURACKA-TESTPLAN-*.xlsx` souborů, ten nejmladší (= v0.4.4) je aktivní — bouracka-ui to kontroluje a vyhlásí varování při startu, pokud najde víc kandidátů.

---

## §7. Co dělat při problémech

| Symptom | Pravděpodobná příčina | První pokus o opravu |
|---|---|---|
| Po instalaci `/api/health` ukazuje stále `server_version: "0.1.4"` | Pip cache nainstalovala starou verzi z lokálního cache | `pip install --no-cache-dir --upgrade bouracka_ui` ze složky s wheelhouse |
| Stránka `/run` nevypadá změněně (chybí sloupec „Kroky") | Workbook v kořeni instalace je stále v0.4.3 | Zkontrolujte `dir C:\TestAutomationSite\BOURACKA-TESTPLAN-*.xlsx`, smažte v0.4.3 |
| Drop-down prostředí neukazuje `ENV-DMO-PUB` | Stará verze backendu běží | Restartujte `bouracka-ui` (Ctrl+C v terminálu, znovu `python -m bouracka_ui`) |
| Tlačítko „Cross-framework check" chybí na `/results/{rid}` | UI cache | Hard refresh prohlížeče: `Ctrl+Shift+R` |
| `Cross-check` endpoint vrací 404 i pro existující `run_id` | Run dosud nedoběhl nebo envelope soubor chybí v `runs/` | Podívejte se do `runs/` na soubor `cross-framework-{run_id}.json` — pokud neexistuje, run nedoběhl |
| Nějaký jiný problém | — | Mail Petrovi s výpisem z `bouracka-ui` konzole + screenshot |

---

## §8. Pro úplnost — co se v tomto dropu **neposílá**

- **Patcher `workbook-v0.4.3-to-v0.4.4.py`** — nástroj pro Pete, ne pro Vás. Pokud byste měla v ruce starší workbook a chtěla ho upgradovat, kontaktujte Petra; nespouštějte patcher přímo (vyžaduje synthetic test fixturu a `--source-data` flag pro řádkovou migraci uživatelských dat).
- **Recon harness** — diagnostický nástroj pro SUPIN-server, ne pro HP Elite. Nepouštějte se do něj.
- **DWH / Oracle ERD design dokumenty** — interní specifikace v0.2 plánovaných funkcí. Není potřeba teď.

---

## §9. Otázky?

Pokud něco z této verze nedává smysl nebo se chová odlišně od popisu, mailujte Petrovi se subjectem `[bouracka-ui v0.1.5.dev5] <stručný popis>`. Pomůže log z `bouracka-ui` konzole (zkopírovat všechno od startu příkazu) + screenshot stránky, kde se anomálie projevila.

**Pete Y. · 2026-05-15**
