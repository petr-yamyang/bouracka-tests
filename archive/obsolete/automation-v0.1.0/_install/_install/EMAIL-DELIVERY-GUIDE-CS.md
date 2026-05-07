# Příručka pro příjem e-mailové dodávky — bouracka-tests

> **Pro koho.** Příjemce e-mailových příloh s testovací sadou
> bouracka-tests (nebo přidružených materiálů — fotografií,
> dokumentace, výsledků).
>
> **Účel.** Bezpečně a kompletně sestavit přijaté přílohy zpět do
> jednoho funkčního adresáře na lokálním disku nebo síťovém sdílení.
>
> **Hlavní myšlenka.** Příjem se skládá z N očíslovaných ZIP archivů
> (každý ≤ 5 MB, aby prošel firemními limity e-mailu) + jednoho
> manifestu `*-PART-INDEX.txt`. Každý ZIP je samostatný (lze rozbalit
> nezávisle); společný kořenový adresář zajišťuje, že všechny díly
> "splynou" do jedné struktury.

---

## §1. Co je v e-mailu

Příjmete N + 1 souborů:

```
bouracka-tests-v0.1.0-part-01-of-NN.zip          (~ 4 MB)
bouracka-tests-v0.1.0-part-02-of-NN.zip          (~ 4 MB)
…
bouracka-tests-v0.1.0-part-NN-of-NN.zip          (~ 4 MB)
bouracka-tests-v0.1.0-PART-INDEX.txt             (≤ 1 KB)
```

Manifest `PART-INDEX.txt` je textový soubor — obsahuje seznam dílů +
SHA256 každého dílu pro ověření celistvosti + návod k rozbalení.

## §2. Postup — varianta A (PowerShell, doporučeno)

### Krok 1 — Stáhněte všechny díly do jedné složky

Uložte všechny `*.zip` díly **a** manifest `PART-INDEX.txt` do jedné
nové složky, například:

```
C:\Users\<vy>\Downloads\bouracka-incoming\
```

### Krok 2 — Spusťte sestavení

Otevřete PowerShell a spusťte:

```powershell
# nahraďte cesty podle vašeho prostředí
.\extract-email-volumes.ps1 `
  -SourceDir 'C:\Users\<vy>\Downloads\bouracka-incoming' `
  -DestDir   'C:\Users\<vy>\Documents\bouracka-tests'
```

(Skript `extract-email-volumes.ps1` přibalený jako součást Part-01;
po jeho rozbalení najdete v `bouracka-tests\scripts\`.)

Skript:
1. Najde manifest v zadané složce.
2. Ověří SHA256 každého dílu.
3. Pokud cokoliv chybí nebo má špatný hash → zastaví s jasnou
   chybovou hláškou.
4. Postupně rozbalí všechny díly do cílové složky.
5. Na závěr vypíše počet souborů a potvrdí splnění očekávaných počtů.

### Krok 3 — Ověření

Po dokončení byste měli vidět:

```
[OK] verified bouracka-tests-v0.1.0-part-01-of-NN.zip
[OK] verified bouracka-tests-v0.1.0-part-02-of-NN.zip
…
[OK] extracted into: C:\Users\<vy>\Documents\bouracka-tests
[OK] N file(s) reconstructed
[OK] file count matches (or exceeds) manifest expectation (N).
```

Hotovo — sada je v cílové složce, lze ji použít.

## §3. Postup — varianta B (Průzkumník Windows, bez skriptu)

Pokud nechcete spouštět PowerShell skript:

### Krok 1 — Stáhněte všechny díly

Stejně jako varianta A — uložte všechny `*.zip` díly do jedné složky.

### Krok 2 — Rozbalte každý díl postupně do **téže** cílové složky

Pro každý ZIP díl:

1. Klikněte pravým tlačítkem na soubor.
2. Zvolte "Extrahovat vše..." (Extract All...).
3. **Důležité:** v poli "Cíl" zadejte **stejnou** cílovou složku pro
   všechny díly, například `C:\Users\<vy>\Documents`.
4. Zaškrtněte "Po dokončení zobrazit extrahované soubory" (volitelné).
5. Klikněte na "Extrahovat".

Každý díl obsahuje stejný kořenový adresář (např. `bouracka-tests-v0.1.0`),
takže všechny rozbalené soubory **splynou** do jednoho stromu — Windows
si automaticky poradí s mergem.

### Krok 3 — Ručně ověřte SHA256 (volitelné)

Pokud chcete potvrdit, že žádný díl nebyl při přenosu poškozen:

```powershell
# z PowerShellu, ve složce s ZIPy:
Get-FileHash *.zip | Format-Table Path, Hash -AutoSize
```

Porovnejte výpis s hodnotami v `PART-INDEX.txt`. Mělo by sedět všechno.

## §4. Cílová struktura — co se objeví v cílové složce

```
C:\Users\<vy>\Documents\
└── bouracka-tests\                ← společný kořen pro všechny díly
    ├── BOURACKA-TESTPLAN-v0.1.xlsx
    ├── README-CS.md
    ├── README-EN.md
    ├── _install\
    │   ├── INSTALL-PLAN-SUPNB-v0.1.md
    │   ├── INSTALL-PLAN-FULL-ECOSYSTEM-v0.1.md
    │   └── …
    ├── _specs\
    ├── env\
    ├── fixtures\
    ├── playwright\
    ├── cypress\
    ├── testcafe\
    ├── recon\
    ├── scripts\
    ├── tools\
    └── …
```

## §5. Síťové sdílení — pozor na délku cesty

Pokud rozbalujete na síťový disk (např. `\\server\share\`), zkontrolujte:

- Celková délka cesty < 260 znaků (Windows limit). Jméno
  `bouracka-tests` je krátké, takže typicky problém nenastane —
  ale pokud rozbalíte do `\\server\share\very-long-team-name\subteam\…\`,
  cesta může přerůst limit. V takovém případě:
  - rozbalte nejdříve lokálně → ověřte → přesuňte.
  - nebo povolte podporu dlouhých cest na cílovém serveru
    (Group Policy: "Enable Win32 long paths").

- Sdílení musí povolit zápis (write) — Tester guide vyžaduje, aby
  bylo možné instalovat npm balíčky a stahovat Playwright browser
  binární soubory do `node_modules\` (cca 200 MB po `npm install`).
  Pokud je sdílení read-only, instalujte na lokální disk.

## §6. Co dělat pokud něco selže

| Problém | Co dělat |
|---------|----------|
| `[FAIL] missing part(s)` — chybí jeden nebo více ZIPů | Vraťte se do e-mailové schránky, zkontrolujte zda jste stáhli **všechny** přílohy. Manifest říká `parts : N` — tolik ZIPů musíte mít. Pokud chybí, vyžádejte si od odesílatele znovu konkrétní díl podle čísla. |
| `[FAIL] SHA256 mismatch` | Konkrétní díl byl při přenosu poškozen (e-mailové gateway občas přepisuje atributy). Vyžádejte si znovu **jen ten jeden díl** s konkrétním číslem. |
| `Cesta je příliš dlouhá` | Cílová složka je hluboko ve stromě sdílení. Zkraťte cestu (např. použijte `C:\bt\`) nebo povolte long paths v GPO. |
| Některé soubory chybí ve výsledku | Manifest udává očekávaný počet souborů. Pokud výsledek neodpovídá, některý díl se buď nerozbalil úspěšně, nebo došlo ke konfliktu jmen. Zkontrolujte log skriptu. |
| Nemám PowerShell práva | Použijte variantu B (Průzkumník) — pravé tlačítko → Extrahovat vše. |

## §7. Kontakt

E-mail: `petr.yamyang@gmail.com`
Subjekt: `[BOURACKA-TESTS PŘÍJEM] <konkrétní problém>`

Při hlášení problému uveďte:
- jméno dílu, kde nastal problém,
- výpis z `extract-email-volumes.ps1` nebo screenshot Průzkumníka,
- cílová cesta (lokální vs síťová).

## §8. Status

| Položka | Hodnota |
|---------|---------|
| Dokument | `_install/EMAIL-DELIVERY-GUIDE-CS.md` |
| Verze | v0.1 |
| Související skripty | `scripts/package-email-volumes.ps1` (odesílatel), `scripts/extract-email-volumes.ps1` (příjemce) |
| Limit dílu | 5 MB / kus (default 4.5 MB cíl + rezerva na ZIP hlavičky) |
| Stav | v0.1 — připraveno pro první e-mailovou dodávku CP-SUPIN-03 |
