# Branched master documentation pattern — v0.1

> **Trigger.** CP-SUPIN-04 STEP 19 (2026-05-06): user direction
> "splitting documentation for branch of Bouračka and DEMO Bouračka.
> Maybe even using one master document with parametrisation of what is
> relevant for what branch and hide lines and rows in excel depending
> on the value of parameter Bouračka/DEMO would work."
>
> **Cíl.** Jeden master dokument (Excel + MD) → switchable view podle
> branch (PROD-Bouračka / DEMO-Bouračka). Připraveno pro pre-live
> production tests v dalších iteracích.

---

## §1. Přehled architektury

```
                    ┌──────────────────────────────────────┐
                    │  MASTER DOCUMENTATION                │
                    │  (single source of truth)            │
                    │                                       │
                    │  ┌─────────────────┐  ┌────────────┐ │
                    │  │ Excel master    │  │ MD master  │ │
                    │  │ s branch-cols   │  │ s [B:..]   │ │
                    │  │ + AutoFilter    │  │ markery     │ │
                    │  └─────────────────┘  └────────────┘ │
                    └──────────────────────────────────────┘
                              │            │
              ┌───────────────┘            └─────────────┐
              ▼                                          ▼
   ┌──────────────────────┐                 ┌──────────────────────┐
   │  DEMO branch view    │                 │  PROD branch view    │
   │  • demo.bouracka.cz  │                 │  • bouracka.cz       │
   │  • tst.demo...       │                 │  • tst.bouracka.cz   │
   │  • mocked integrace  │                 │  • reálné integrace  │
   │  • 47 TC v scope     │                 │  • 48 TC v scope     │
   └──────────────────────┘                 └──────────────────────┘
              │                                          │
              ▼                                          ▼
   suite-DEMO-v0.X.Y.zip                        suite-PROD-v0.X.Y.zip
   (parametrický Playwright;                    (parametrický Playwright;
    běží proti oběma DEMO targetům)             běží proti oběma PROD targetům)
```

## §2. Excel — branch-tagging + AutoFilter

### §2.1 Schema (od v0.4.0)

Každý ItemBase list (`00b_Requirements`, `01_TestTargets`, `02_TestCases`,
`08_Bugs`) má 2 nové sloupce:

| Sloupec | Typ | Hodnoty | Význam |
|---------|-----|---------|--------|
| `applies_to_demo` | TEXT | `TRUE` / `FALSE` | řádek je v scope DEMO branche |
| `applies_to_prod` | TEXT | `TRUE` / `FALSE` | řádek je v scope PROD branche |

**Derivace** (pro 02_TestCases):

| `env_constraints` | → `applies_to_demo` | `applies_to_prod` |
|-------------------|---------------------|--------------------|
| `both` | TRUE | TRUE |
| `both-with-adapter` | TRUE | TRUE |
| `demo-only` | TRUE | FALSE |
| `prod-only` | FALSE | TRUE |

### §2.2 Switchování pohledu (operátor)

Postup:

1. Otevřete master sešit `BOURACKA-TESTPLAN-v0.4.0.xlsx`
2. Přejděte na list, který vás zajímá (např. `02_TestCases`)
3. Klikněte na šipku AutoFilter v záhlaví sloupce `applies_to_demo`
4. Pro **DEMO-only pohled**: zaškrtněte JEN `TRUE`, odškrtněte `FALSE`
5. Pro **PROD-only pohled**: stejné na sloupci `applies_to_prod`
6. Pro **reset**: klikněte na šipku → "Vymazat filtr z..."

Filtr je list-lokální — můžete mít různé pohledy na různých listech
současně.

### §2.3 Bezpečné rozšíření přes VBA macro (volitelné)

Pro one-click branch switching napříč všemi listy lze napsat krátký
macro:

```vba
Sub ShowBranch_DEMO()
    Dim ws As Worksheet
    For Each ws In ThisWorkbook.Worksheets
        If InStr(ws.Name, "_TestCases") > 0 _
           Or InStr(ws.Name, "_TestTargets") > 0 _
           Or InStr(ws.Name, "_Requirements") > 0 _
           Or InStr(ws.Name, "_Bugs") > 0 Then
            With ws.AutoFilter
                ' Filter applies_to_demo column to TRUE only
                ws.Range("A1").AutoFilter Field:=ColIdx(ws, "applies_to_demo"), Criteria1:="TRUE"
                ' Show all on applies_to_prod
                ws.Range("A1").AutoFilter Field:=ColIdx(ws, "applies_to_prod")
            End With
        End If
    Next ws
End Sub

Function ColIdx(ws As Worksheet, name As String) As Integer
    Dim c As Range
    For Each c In ws.Range("1:1")
        If c.Value = name Then ColIdx = c.Column : Exit Function
    Next c
End Function
```

(Plný VBA modul: `_install/EXCEL-MACRO-BRANCH-FILTER.bas` — TBD v0.4.1.)

## §3. Markdown master — branch markers

### §3.1 Markup

V master MD dokumentech používat XML-style komentáře pro značení
sekcí specifických pro branch:

```markdown
## Phase 1 — Verification

Společný popis pro obě branche.

<!-- B:DEMO -->
DEMO chování: žádné SMS, libovolný 4-digit OTP přijat.
Zobrazený DEMO hint banner ("Demoverze žádné SMS neodesílá…").
<!-- /B -->

<!-- B:PROD -->
PROD chování: SMS přes N8 SMS Gateway, OTP doručen na telefon
operátora. DEMO hint banner MUSÍ být absent.
<!-- /B -->

Společné po-průběh: oba účastníci vidí "✓ Ověřeno" pill.
```

### §3.2 Render skript

`tools/render_branch_doc.py`:

```pwsh
# Vyrenderovat DEMO-only pohled
python tools/render_branch_doc.py recon/ANALYTICAL-DOC-INTELLIGENCE-v0.4.md --branch demo

# Vyrenderovat PROD-only pohled
python tools/render_branch_doc.py recon/ANALYTICAL-DOC-INTELLIGENCE-v0.4.md --branch prod

# Bez parametru → master se všemi sekcemi
python tools/render_branch_doc.py recon/ANALYTICAL-DOC-INTELLIGENCE-v0.4.md
```

Render strip-uje sekce neaplikovatelné pro daný branch a uloží
`*-DEMO.md` nebo `*-PROD.md` výstup. Skript dodán v balíčku
v0.4.0+ jako součást automation distribuce.

## §4. Test suite — sjednocení dvou ZIPů (cíl pro v0.5)

Aktuální v0.3.0 distribuce má 2 separate suite-ZIPy:

- `bouracka-suite-DEMO-v0.3.0.zip` — env_constraints ∈ {both, demo-only}
- `bouracka-suite-PROD-v0.3.0.zip` — env_constraints ∈ {prod-only, both-with-adapter}

**Cíl pro v0.5:** ONE master suite ZIP s tagy.

```typescript
// playwright.config.ts (master)
projects: [
  { name: 'demo-public',  use: { baseURL: 'https://demo.bouracka.cz'    } },
  { name: 'demo-tst',     use: { baseURL: 'https://tst.demo.bouracka.cz' } },
  { name: 'prod',         use: { baseURL: 'https://bouracka.cz'         } },
  { name: 'prod-tst',     use: { baseURL: 'https://tst.bouracka.cz'     } },
],
```

Test soubory označit Playwright tagy:

```typescript
test('TC-CP-001 — smoke', { tag: ['@both'] }, async ({ page }) => { ... });
test('TC-CP-NEW-O — DEMO accepts any OTP', { tag: ['@demo'] }, async ({ page }) => { ... });
test('TC-CP-NEW-P — PROD rejects wrong OTP', { tag: ['@prod'] }, async ({ page }) => { ... });
```

Spuštění:

```pwsh
# Jen DEMO TCs proti DEMO branch
npx playwright test --project=demo-public --grep '@both|@demo'

# Jen PROD TCs proti PROD branch
npx playwright test --project=prod --grep '@both|@prod'

# Cross-branch consistency check (TC-CP-NEW-J — DEMO baner musí být absent na PROD)
npx playwright test --project=prod --grep '@cross-branch'
```

## §5. Pre-live production tests (cíl pro v0.6)

Architektura předpokládá další iteraci:

- **Pre-live** = nový branch mezi DEMO a PROD (např. `pre-live.bouracka.cz`)
- Reálné integrace, ale s testovacími dummy daty
- Ideální pro CI gate před každým deploy do PROD

V té době přidat:

| Sloupec | Hodnoty |
|---------|---------|
| `applies_to_pre_live` | TRUE/FALSE |

A nový Playwright project `pre-live` v master config. Pattern stejný.

## §6. Status

| Item | Hodnota |
|------|---------|
| Pattern docs | `_specs/BRANCHED-MASTER-DOC-PATTERN-v0.1.md` |
| Excel migration | `tools/migrate_to_v04_branch_tagging.py` |
| Master Excel | `BOURACKA-TESTPLAN-v0.4.0.xlsx` |
| Branch-tagged rows | 97 (20 Reqs + 28 TT + 49 TC + 0 Bugs) |
| AutoFilter pre-set | ANO, na všech ItemBase listech |
| Branch view sheet | `00e_BranchView` (counts + CS návod) |
| Markdown render skript | TBD v v0.4.1 (`tools/render_branch_doc.py`) |
| Excel macro | TBD v v0.4.1 (`_install/EXCEL-MACRO-BRANCH-FILTER.bas`) |
| Cíl v0.5 | sjednocený master suite ZIP s Playwright tagy |
| Cíl v0.6 | pre-live branch column |
| Status | scaffolding hotový; render skript + macro v další iteraci |
