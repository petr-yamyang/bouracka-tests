# Bugfix advisory — Priority = Severity × Urgency — 2026-05-06

> **Adresát.** Příjemci analytického balíčku v0.3 (v0.3.0) by měli upgradovat
> na **v0.3.1**. Týká se jak `BOURACKA-TESTPLAN-v0.3.xlsx`, tak všech tří
> sešitů z předchozích verzí (v0.1, v0.2 — již archivovány).
>
> **Závažnost.** Vysoká pro analytickou interpretaci priorit; **bez vlivu**
> na běžící testy (priorita je výpočtové pole, ne řídicí logika).

---

## §1. Co bylo špatně

Vzorec v sešitech v0.2 / v0.3 ve sloupci `priority` ItemBase listů
(`00b_Requirements`, `01_TestTargets`, `02_TestCases`, `08_Bugs`):

```excel
=IF(OR(K="",L=""),"D",
  IF(OR(K="D",L="D"),"D",
    IF((CODE(K)+CODE(L)-130)<=3,"A",
      IF((CODE(K)+CODE(L)-130)=4,"B","C"))))
```

Vzorec **nekonzistentně přiřazoval prioritu A** kombinacím severity ×
urgency, které měly podle standardní matice vyšlo nižší prioritu.

**Uživatelem zachycený případ:** severity=B + urgency=B → priority=A
(matice říká **B**).

Audit ukázal, že **8 z 16** kombinací (sev, urg) bylo nesprávně:

| (sev, urg) | Buggy formula | Canonical matrix | Δ |
|------------|---------------|------------------|---|
| (A, C) | A | B | ⚠ |
| (A, D) | D | C | ⚠ |
| (B, B) | A | **B** ← user-flagged | ⚠ |
| (B, C) | A | C | ⚠ |
| (C, A) | A | B | ⚠ |
| (C, B) | A | C | ⚠ |
| (C, C) | B | D | ⚠ |
| (D, A) | D | C | ⚠ |

Ostatní 8 kombinací byly náhodou OK (převážně severity=A/D extrémy).

## §2. Kanonická matice (correct)

```
        urg=A   urg=B   urg=C   urg=D
sev=A:   A       A       B       C
sev=B:   A       B       C       D       ← (B, B) = B
sev=C:   B       C       D       D
sev=D:   C       D       D       D
```

V sum-formě: nechť `s = CODE(severity) + CODE(urgency) − 130`. Pak:

| s | priority |
|---|----------|
| 0 | A |
| 1 | A |
| 2 | B |
| 3 | C |
| ≥4 | D |

## §3. Opravený vzorec

```excel
=IF(OR(K="",L=""),"D",
  IF((CODE(K)+CODE(L)-130)<=1,"A",
    IF((CODE(K)+CODE(L)-130)=2,"B",
      IF((CODE(K)+CODE(L)-130)=3,"C","D"))))
```

Klíčové změny:
1. **`<=3` → `<=1`** (toto byl primární zdroj zlomu — lumpovalo třídy 2 + 3 do A)
2. **Odstraněn shortcut `OR(K="D", L="D") → "D"`** — porušoval matrix
   na hraně `(A, D)=C` a `(D, A)=C`
3. Přidán explicitní case pro priority **C** (s=3); předtím se priorita
   C přidělovala jen "default else" které spotřebovalo i (D, ?) páry

## §4. Co dělat

### §4.1 Pokud máte `BOURACKA-TESTPLAN-v0.3.xlsx`

Použijte přiložený sešit `BOURACKA-TESTPLAN-v0.3.1.xlsx`. Otevřete ho
v Excelu, **dělejte Save once** — Excel přepočítá všechny vzorce a
materializuje cached values.

### §4.2 Pokud máte starší v0.1 / v0.2

Tyto verze jsou v `archive/obsolete/`. Pokud z nich někdo dosud
interpretuje priority, **doporučujeme přejít na v0.3.1**.

### §4.3 Validace

Spusťte:

```pwsh
python tools/check_priority_matrix.py BOURACKA-TESTPLAN-v0.3.1.xlsx
```

Očekávaný výstup: `[summary] N rows checked, 0 violations`. Při exit
code 0 je sešit v souladu s maticí.

## §5. Co se změnilo v v0.3.1 oproti v0.3

| Položka | Změna |
|---------|-------|
| `priority` formula | opraven ve 4 ItemBase listech (00b, 01, 02, 08) |
| `01d_PrioritySevUrgMatrix` | NOVÝ list s kanonickou maticí + bug-history dokumentace |
| 25 TC-CP-NEW-* řádků | doplněno `severity` + `urgency` (předtím chyběly; měli pouze P-tag) |
| `tools/check_priority_matrix.py` | NOVÁ utility pro CI gate (post každý edit) |
| `tools/fix_priority_matrix.py` | NOVÁ utility (one-shot oprava workbooku) |
| `11_Changelog` | rev9.1 entry |

## §6. Lessons learned

- **Excel CODE-arithmetic vzorce** jsou křehké pro vícetřídové matice.
  Doporučení: pro budoucí projekty použít `CHOOSE` nebo `LOOKUP` proti
  explicitní 4×4 matici v hidden listu, ne aritmetiku přes `CODE`.
- **Validační check #11** přidán do `check_priority_matrix.py` — bude
  spouštěn jako CI gate před každým email-deliverable.
- **TC migrace v0.2 → v0.3** přidala 25 řádků s `priority='P1/P2/P3'`
  ale prázdnými `severity` + `urgency`. Tato pre-condition byla nezachycena
  (nebyla v původním validátoru); nyní opraveno zpětně.

## §7. Kontakt + odkazy

- Hlavní detail: `tools/fix_priority_matrix.py` (zdroj opravy + dokumentace)
- Matrix dokumentace: list `01d_PrioritySevUrgMatrix` v sešitu
- Changelog: list `11_Changelog`, rev9.1

## §8. Stav

| Item | Hodnota |
|------|---------|
| Verze sešitu | v0.3.1 (nahrazuje v0.3.0) |
| Datum | 2026-05-06 |
| Validátor | `tools/check_priority_matrix.py` returns 0 violations |
| Zlomené řádky pre-fix | 62 (62/62) |
| Zlomené řádky post-fix | 0 |
| Nahrazuje | v0.1, v0.2, v0.3 sešity (vše v archive/obsolete/) |
