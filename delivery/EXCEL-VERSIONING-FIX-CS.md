# Bugfix advisory — Excel versioning + computed values — 2026-05-06

> **Adresát.** Příjemci `BOURACKA-TESTPLAN-v0.3.0.xlsx` nebo `v0.3.1.xlsx`.
> Upgrade na **v0.3.2** doporučen.
>
> **Závažnost.** Střední. Hodnoty priorit se nyní zobrazují korektně všem
> čtenářům (předtím jen Excel + ruční Save once); identita souboru je
> konzistentní s názvem souboru i obsahem.

---

## §1. Co bylo špatně (2 problémy)

### §1.1 Verzování úvodního listu

Sešit má list `00_README` s titulem v buňce `A1`. Ten **se nikdy neaktualizoval**
napříč revizemi:

| Verze souboru | Co bylo v `00_README!A1` | Co mělo být |
|---------------|--------------------------|-------------|
| v0.1.0 | "BOURACKA-TESTPLAN — v0.1" | OK |
| v0.2.0 | "BOURACKA-TESTPLAN — v0.1" | (mělo být v0.2) |
| v0.3.0 | "BOURACKA-TESTPLAN — v0.1" | (mělo být v0.3) |
| v0.3.1 | "BOURACKA-TESTPLAN — v0.1" | (mělo být v0.3.1) |
| **v0.3.2** | **"BOURACKA-TESTPLAN — v0.3.2"** ✓ | OK |

Migrační skripty `migrate_to_v02.py` / `migrate_to_v03.py` /
`fix_priority_matrix.py` přidávaly nové řádky a opravovaly vzorce, ale
**nikdy se nedotkly úvodního listu**. Reviewer otevřel sešit, viděl
"v0.1" a oprávněně se ptal, zda dostal aktuální verzi.

### §1.2 Vzorce priority bez cached values

Druhý problém: Excel ukládá pro každou buňku **vzorec + cached value**.
Když `openpyxl` zapíše nový vzorec, **cached value zůstane prázdná**
(žádný embedded interpreter).

Důsledek:
- **Kdo otevře v Excelu**: vzorce se přepočítají při otevření, vidí
  správné hodnoty. ✓
- **Kdo otevře v Pythonu** (`load_workbook(data_only=True)`): vidí
  `None` v každé priority buňce. ✗
- **Kdo otevře v web-based xlsx readeru** (Google Sheets preview, GitHub
  preview, SharePoint thumbnail): vidí blank. ✗

To znamená, že CI gate skripty + automatická generace TC dokumentace
+ web previewy ukazovaly **prázdná pole** místo priorit, dokud někdo
neotevřel sešit v Excelu a neuložil ho ručně. **Ne robust.**

## §2. Oprava ve v0.3.2

| Co | Jak |
|----|-----|
| `00_README!A1` | bumpnuto na `BOURACKA-TESTPLAN — v0.3.2` |
| `00_README!B3` | bumpnuto na `v0.3.2` |
| Priority buňky (87 buněk napříč 4 ItemBase listy) | nahrazeno **statickou hodnotou** (plain `'A'` / `'B'` / `'C'` / `'D'` z matice) — vzorec odstraněn |
| Color-coding | A=červená, B=žlutá, C=světlemodrá, D=šedá (visuálně okamžitý přehled priorit) |
| Comment na první priority buňce každého listu | "Static value computed from severity × urgency per 01d_PrioritySevUrgMatrix" |
| `updated_at` napříč ItemBase | bumpnuto na 2026-05-06 (77 řádků) |
| `00c_VersionSanityRules` | NOVÝ list — 7 pravidel pro budoucí migrace |
| `11_Changelog` | rev10 entry |

## §3. Trade-off — proč static a ne dynamický recomputed?

**Static (zvolený)**:
- ✓ Každý čtenář vidí správnou hodnotu okamžitě
- ✓ CI gate, web preview, openpyxl scripty fungují
- ✓ Verifikovatelné offline
- ✗ Pokud někdo ručně změní severity/urgency v Excelu, priority se
  neaktualizuje automaticky (musí spustit `tools/bump_workbook_version.py`)

**Dynamický vzorec** (předchozí):
- ✓ Auto-recompute při ruční změně
- ✗ Bez Excel + Save vidí čtenáři prázdná pole
- ✗ Vzorec sám historicky obsahoval bug (rev9.1 oprava)

**Volba:** static, protože workbook je zamýšlený jako **verifikovatelný
audit artefakt**, ne živý nástroj. Pokud se severity/urgency mění,
patří to do migračního cyklu (rev bump), ne ad-hoc úprav.

## §4. Validace po upgrade

```pwsh
python tools/check_priority_matrix.py BOURACKA-TESTPLAN-v0.3.2.xlsx
# očekávaný výstup: [summary] N rows checked, 0 violations
```

Plus list `00c_VersionSanityRules` v sešitu dokumentuje 7 pravidel,
která kontrolují versioning konzistenci napříč budoucími revizemi.

## §5. Co dělat — postup upgrade

| Krok | Příkaz / akce |
|------|---------------|
| 1. Stáhnout | `BOURACKA-TESTPLAN-v0.3.2.xlsx` (z přílohy) |
| 2. Verifikovat SHA256 | `Get-FileHash BOURACKA-TESTPLAN-v0.3.2.xlsx -Algorithm SHA256` |
| 3. Otevřít v Excelu | jakákoliv MS Excel verze 2016+ |
| 4. Zkontrolovat A1 | mělo by být `BOURACKA-TESTPLAN — v0.3.2` |
| 5. Zkontrolovat priority | barevně označené sloupce v 00b/01/02 |
| 6. Smazat starou verzi | v0.3.0 / v0.3.1 přesunout do `archive/obsolete/older-workbooks/` |

## §6. Stav

| Item | Hodnota |
|------|---------|
| Verze sešitu | v0.3.2 |
| Datum | 2026-05-06 |
| Front-page bumpnut | ANO (z "v0.1") |
| Priority buňky materializovány | 87 (formula → static) |
| Validátor | 0 violations |
| Nahrazuje | v0.3.0, v0.3.1 |
