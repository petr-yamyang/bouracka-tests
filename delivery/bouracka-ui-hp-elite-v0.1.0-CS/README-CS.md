# Bouračka UI v0.1.2 — distribuční balíček pro HP Elite (CS, Kate drop 2026-05-12)

**Začněte tady:** otevřete soubor `INSTALL-HP-ELITE-CS.txt` a postupujte krok za krokem.

## Dokumenty v balíčku

| Soubor | K čemu slouží | Kdy číst |
|--------|---------------|----------|
| `INSTALL-HP-ELITE-CS.txt` | Instalace od čistého notebooku až po funkční `bouracka-ui --help` | **nejdřív**, jednou pro každý notebook |
| `OPERATOR-GUIDE-CS.md` | Každodenní workflow: spuštění testů, zakládání chyb, export trace bundle | po první úspěšné instalaci |
| `TROUBLESHOOTING-CS.md` | Postupy pro známé chybové stavy UI (obsazený port, zamčené DLL, dispatch issues atd.) | když nefunguje UI samotné |
| `DIAGNOSTICS-PLAYBOOK-CS.md` | Co kontrolovat, když nefunguje SYSTÉM kolem UI: network reachability, mock-vs-live delty integrací, drift katalog, pre-flight TST checklist, DELTA-REPORT šablona pro zpětné posílání nálezů | pro jakýkoli moment „tohle není zjevný UI bug" |
| `kill-stragglers.ps1` | Pomocný skript: zabije zaseklé servery + vyčistí pip orphany | když to říká TROUBLESHOOTING |
| `SHA256SUMS.txt` | Kontrolní součty pro ověření integrity | volitelně, před instalací na security-citlivém stroji |
| `bouracka_ui-0.1.2-py3-none-any.whl` | Instalační wheel | odkazuje na něj INSTALL krok 4 |
| `wheelhouse/` | ~28 .whl souborů, předem stažené závislosti (air-gap install) | použito v INSTALL kroku 4 |
| `BOURACKA-TESTPLAN-v0.4.3.xlsx` | Testovací workbook (TC / prostředí / bugy) — KP-reviewed primary | používá ho UI; přímo neupravovat |

## Rychlá kontrola po instalaci

Pokud už máš nainstalováno a chceš jen ověřit, že vše funguje:

```powershell
cd C:\bouracka-ui
.\.venv\Scripts\Activate.ps1
bouracka-ui --help
```

Měl by se zobrazit banner s nápovědou. Pokud ne — typicky pomůže `TROUBLESHOOTING-CS.md` §1 (obsazený port) nebo §2 (pip Přístup byl odepřen).

## Co je nového v v0.1.0

- První vydání bouracka-ui jako prezentační vrstvy nad testovacími runnery.
- Cross-framework spouštění: Cypress + Playwright + Selenium z jedné obrazovky.
- Zakládání bugů zapisuje přímo do Excel workbooku.
- Trace bundle export/import pro air-gap workflow HP Elite (bez GitHubu).
- Endpoint pro diagnostický snapshot pro hlášení typu „UI nefunguje".
- **Oprava BUG-BUI-001:** run_id používá filename-safe formát pro Windows (bez znaku `:`).
- **Oprava BUG-BUI-002:** Stránka výsledků se každé 2 s pollne, dokud běh není dokončen — žádné přechodné stránky „Run not found".

## Autor + údržba

Pete Y. (petr.yamyang@gmail.com).
