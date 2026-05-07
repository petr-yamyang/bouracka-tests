# Coverage rule introduction strategy — v0.1 CS

> **Trigger.** CP-SUPIN-05 STEP 1 — Pete: "strict coverage rule is not yet
> applied but we need to apply it in proper moment". Cíl: definovat *kdy* a
> *jak* zavedeme strict coverage gate, abychom nezablokovali iterace dříve než
> máme adequate TC base.

---

## §1. Princip coverage gate

**Coverage rule.** Každý relevantní TestTarget (TT) MUSÍ být pokryt alespoň
jedním passing TestCase (TC) — jinak je release blokován.

**Relevant TT** = TT, které jsou v scope dané iteration (např. CP-SUPIN-05 R1
scope = R1 use case "minor accident self-record"). Out-of-scope TT mají
`tt_in_scope=false` a coverage gate je nezohledňuje.

**Coverage strength.**

| Hodnota | Význam | Příklad |
|---------|--------|---------|
| `full` | TC pokrývá entire TT functionality + edge cases | TC-CP-A2-ALT-7 covers TT-LOV-vehicleBrands (passes 200+ items) |
| `partial` | TC pokrývá happy path nebo jen některé case | TC-CP-001 covers TT-FUNC-001 indirectly (smoke only) |
| `indirect` | TC traverses TT ale neasertuje na něj | TC-CP-A1-MAIN-DEMO touches TT-LOV-prefix-cs without explicit assertion |
| `none` | nepokryto | (gap) |

Coverage rule počítá `full` + `partial` jako covered; `indirect` + `none` jako
gap.

## §2. Phased introduction

Premature gate by zablokoval delivery dříve než máme broad-enough TC base.
Test base se ladí společně s coverage rule, ne před.

### §2.1 Phase 0 — informational (now → CP-SUPIN-05 STEP 5)

| Aspekt | Hodnota |
|--------|---------|
| **Stav** | informational only |
| **Audit script** | `tools/coverage_audit.py` (v0.1, scaffold) |
| **Output** | `runs/coverage-audit-{date}.json` + console report |
| **Gate** | žádný — exit 0 vždy |
| **Účel** | sbírat baseline, identifikovat gaps, neblokovat iterace |

Konkrétně v této fázi:
- TT × TC binding annotations povinně (Excel `16_CoverageMatrix` po schema bumpu v0.5.1)
- Audit script tiskne stats: covered/total, per-layer breakdown, top-10 gaps
- Žádný impact na CI build / release

### §2.2 Phase 1 — soft warnings (CP-SUPIN-06)

| Aspekt | Hodnota |
|--------|---------|
| **Stav** | warnings, ne ještě gate |
| **Audit script** | `tools/coverage_audit.py` v0.2 — exit 0 + warnings v reportu |
| **Trigger pro upgrade** | TT-FUNC-* coverage > 80% globally |
| **Gate** | RED warnings v report ale NEzablokuje |
| **Účel** | sociálně tlačit dev/test team na coverage closure |

Concrete rule v Phase 1: každý TT-FUNC-* (5 items) MUSÍ mít alespoň 1 covering
TC. Pokud má coverage_strength = `none`, audit emit warning (žlutá v console),
ale nevrací non-zero exit code.

### §2.3 Phase 2 — gating per-TT-class (CP-SUPIN-07)

| Aspekt | Hodnota |
|--------|---------|
| **Stav** | gated for FUNC, soft for ostatní |
| **Audit script** | v0.3 — exit non-zero pokud TT-FUNC-* coverage < 100% |
| **Trigger** | TT-FUNC-* coverage = 100%, TT-SCRN-* coverage > 90%, TT-LOV-* coverage > 80% |
| **Gate** | release scripts zavolají audit script; non-zero exit blokuje package build |
| **Účel** | zabránit regresi na critical paths |

V této fázi audit script má `--enforce` flag:
```bash
py tools/coverage_audit.py --enforce BOURACKA-TESTPLAN-v0.7.0.xlsx
# exit 0  → all TT-FUNC-* covered, soft warnings on jiné layers
# exit 2  → at least 1 TT-FUNC-* uncovered → BLOCK release
```

### §2.4 Phase 3 — full gating (CP-SUPIN-08+)

| Aspekt | Hodnota |
|--------|---------|
| **Stav** | full strict gating |
| **Audit script** | v0.4 — exit non-zero on ANY uncovered in-scope TT |
| **Trigger** | broad TC base (>200 TC), all 6 frameworks port-complete |
| **Gate** | unbreakable invariant; release blocked dokud žádný gap |
| **Účel** | stabilizovaná coverage governance |

V tomto bodě CI/CD pipeline zahrnuje:
```yaml
# (per CP-SUPIN-09 CI plan)
- name: Coverage gate
  run: |
    py tools/coverage_audit.py --enforce \
       --layer FUNC=100,SCRN=100,LOV=95,ACTV=90 \
       BOURACKA-TESTPLAN-vX.Y.Z.xlsx
```

## §3. Audit script — `tools/coverage_audit.py`

### §3.1 v0.1 (Phase 0)

```python
#!/usr/bin/env python3
"""
coverage_audit.py — audit TestTarget × TestCase coverage matrix.

CP-SUPIN-05 v0.1 — Phase 0 (informational only).
"""
import argparse, json, sys
from datetime import date
from pathlib import Path
from openpyxl import load_workbook
from collections import defaultdict

def audit(xlsx_path: Path, out_dir: Path = Path("runs")) -> int:
    wb = load_workbook(xlsx_path, read_only=True, data_only=True)

    # Read assembly TT (sheet 15_VModelAssemblyMap; v Phase 0 skip pokud chybí)
    if "15_VModelAssemblyMap" not in wb.sheetnames:
        print("[coverage] sheet 15_VModelAssemblyMap missing — Phase 0 OK to skip")
        return 0
    if "16_CoverageMatrix" not in wb.sheetnames:
        print("[coverage] sheet 16_CoverageMatrix missing — Phase 0 OK to skip")
        return 0

    tt_sheet = wb["15_VModelAssemblyMap"]
    cov_sheet = wb["16_CoverageMatrix"]

    # tt_code -> tt_layer
    tt_layer = {}
    headers = [c.value for c in next(tt_sheet.iter_rows(max_row=1))]
    code_idx = headers.index("tt_code")
    layer_idx = headers.index("tt_layer")
    for row in tt_sheet.iter_rows(min_row=2, values_only=True):
        if row[code_idx]:
            tt_layer[row[code_idx]] = row[layer_idx]

    # tc_code × tt_code -> coverage_strength
    matrix = defaultdict(list)
    headers = [c.value for c in next(cov_sheet.iter_rows(max_row=1))]
    tc_idx = headers.index("tc_code")
    tt_idx = headers.index("tt_code")
    str_idx = headers.index("coverage_strength")
    for row in cov_sheet.iter_rows(min_row=2, values_only=True):
        if row[tc_idx] and row[tt_idx]:
            matrix[row[tt_idx]].append((row[tc_idx], row[str_idx]))

    # Compute coverage per layer
    layer_stats = defaultdict(lambda: {"total": 0, "covered": 0, "uncovered": []})
    for tt_code, layer in tt_layer.items():
        stats = layer_stats[layer]
        stats["total"] += 1
        bindings = matrix.get(tt_code, [])
        full_or_partial = [b for b in bindings if b[1] in ("full", "partial")]
        if full_or_partial:
            stats["covered"] += 1
        else:
            stats["uncovered"].append(tt_code)

    # Report
    print(f"[coverage-audit] {xlsx_path.name} — {date.today().isoformat()}")
    for layer in sorted(layer_stats.keys()):
        s = layer_stats[layer]
        pct = (s["covered"] / s["total"] * 100) if s["total"] else 0
        print(f"  TT-{layer}-*  covered: {s['covered']}/{s['total']} ({pct:.0f}%)")
        if s["uncovered"]:
            preview = ", ".join(s["uncovered"][:5])
            more = f" +{len(s['uncovered'])-5} more" if len(s["uncovered"]) > 5 else ""
            print(f"    gaps: {preview}{more}")

    # Save JSON
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"coverage-audit-{date.today().isoformat()}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({k: dict(v) for k, v in layer_stats.items()}, f, indent=2, ensure_ascii=False)
    print(f"[coverage-audit] report: {out_path}")
    return 0  # Phase 0 — never fail


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("xlsx", type=Path)
    ap.add_argument("--out-dir", type=Path, default=Path("runs"))
    ap.add_argument("--enforce", action="store_true",
                    help="Phase 2+: exit non-zero on uncovered FUNC TTs")
    args = ap.parse_args()
    sys.exit(audit(args.xlsx, args.out_dir))
```

### §3.2 Versioning

| Audit version | Phase | Key changes |
|---------------|-------|-------------|
| v0.1 | Phase 0 | informational, exit 0 always |
| v0.2 | Phase 1 | warnings on uncovered TT-FUNC-* |
| v0.3 | Phase 2 | `--enforce` flag, exit 2 on TT-FUNC gap |
| v0.4 | Phase 3 | full strict, per-layer thresholds |

## §4. Excel sheet — `16_CoverageMatrix` schema

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| `tc_code` | str | yes | TC-CP-XXX |
| `tt_code` | str | yes | TT-{LAYER}-{slug} |
| `coverage_strength` | enum | yes | full \| partial \| indirect \| none |
| `assertion_evidence` | str | no | např. "expect(text).toMatch(...)" snippet |
| `framework` | enum | no | playwright \| cypress \| testcafe \| selenium |
| `last_verified_run_id` | str | no | RUN-YYYYMMDDTHHMMSSZ |
| `notes` | str | no | free text |
| `auto_generated` | bool | no | true pokud z reporteru, false pokud manual |

## §5. Integration s reporter

Per CP-SUPIN-04 STEP 32 jsme přidali `13_TestExecutionSummary` + `14_AssertionGateResults`.
V CP-SUPIN-05 v0.5.1 reporter (`excel-row-writer.ts`) se rozšíří o:

```typescript
// Pseudo-code; full impl v CP-SUPIN-06
const coverageBindings = extractCoverageFromTitle(test.title);
// např. titulu "TC-CP-A2-ALT-7 covers TT-LOV-vehicleBrands"
// → bindings = [{tc_code: "TC-CP-A2-ALT-7", tt_code: "TT-LOV-vehicleBrands", strength: "full"}]
appendToCoverageMatrix(coverageBindings, runId);
```

Alternativně explicit annotation v test source (preferred):

```typescript
test.describe("TC-CP-A2-ALT-7 — public enumerations", () => {
  // @covers TT-LOV-insuranceCompanies (full)
  // @covers TT-LOV-vehicleBrands (full)
  // @covers TT-LOV-licenseCategories (partial — only 403 check, no content)
  test("...", async ({ request }) => { ... });
});
```

Reporter parsuje `// @covers ...` komentáře a auto-populates `16_CoverageMatrix`.

## §6. Migration plan

### §6.1 v0.5.0 (immediate)

- Tento doc + scaffold script (Phase 0)
- Žádný Excel schema bump

### §6.2 v0.5.1

- Excel schema bump → `16_CoverageMatrix` sheet (8 cols)
- Initial fill manuálně (Pete + Sonnet branch session)
- First `tools/coverage_audit.py` run → baseline report

### §6.3 v0.6.0

- Reporter integrace — auto-extrakce z `// @covers` annotations
- Coverage_audit upgrade na v0.2 (warnings)

### §6.4 v0.7.0+

- Phase 2/3 gating — viz §2

## §7. Open questions

| # | Otázka | Owner |
|---|--------|-------|
| Q1 | TT-FUNC vs TT-SCRN granularity boundary — kdy mám použít kterou? | Pete + governance |
| Q2 | Coverage_strength `indirect` — počítá se jako covered nebo gap? | Opus next |
| Q3 | Out-of-scope TT — kdo rozhoduje? Pete? Tech-owner? | Pete |
| Q4 | Phase upgrade trigger — automaticky podle metric, nebo manual? | Pete |

## §8. Status

| Item | Hodnota |
|------|---------|
| Spec | `_specs/COVERAGE-RULE-STRATEGY-v0.1-CS.md` |
| Verze | v0.1 |
| Datum | 2026-05-07 EOD |
| Phase | 0 (informational) |
| Audit script | `tools/coverage_audit.py` v0.1 (scaffold) |
| Excel schema bump | plánováno v0.5.1 (sheet `16_CoverageMatrix`) |
| Companion | `_specs/VMODEL-ASSEMBLY-TT-MAPPING-v0.1-CS.md` |
| Status | seed; gate fáze 1 nejdříve v CP-SUPIN-06 |
