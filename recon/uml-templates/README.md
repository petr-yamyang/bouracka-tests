# UML Templates — VUP-compliant reconstruction

> Per CP-SUPIN-04 L-WORK-5..7 — bottom-up UML reconstruction from flow
> photo sequences for VUP (Unified Process) compliance.

## Templates

| File | Diagram kind | When to author |
|------|--------------|----------------|
| `use-case-template.puml` | UML 2.5 Use Case | First — actor + use cases + extends/includes |
| `activity-template.puml` | UML 2.5 Activity (swim-lane) | Second — flow with decision diamonds + fork/join |
| `sequence-template.puml` | UML 2.5 Sequence | Third — message-passing detail with alt/opt/loop fragments |

## How to use per flow

1. Create a flow folder per `_flow-template.md`:
   ```
   recon/screenflows-live/flow-A1-main-tst/
   ├── photos/
   ├── snippets/
   ├── FLOW.md
   ├── use-case.puml      ← copy from this folder; rename + fill
   ├── activity.puml
   └── sequence.puml
   ```

2. Author bottom-up: every UML element must comment its source photo:
   ```plantuml
   ' source: photos/IMG_NNNN.jpg (top-half region)
   :Klik VYPLNIT ZÁZNAM;
   ```

3. Render to PNG/SVG:
   ```powershell
   .\tools\render-uml.ps1 -FlowFolder .\recon\screenflows-live\flow-A1-main-tst
   ```

   Renders all .puml files in the folder to .png + .svg siblings.

## PlantUML prerequisite

PlantUML is a Java tool. Two install options:

**Option A — JRE + plantuml.jar (Profile C of install plan):**
```powershell
# JRE 21 per _install/INSTALL-PLAN-FULL-ECOSYSTEM-v0.1.md §4.3
Invoke-WebRequest 'https://github.com/plantuml/plantuml/releases/download/v1.2024.7/plantuml-1.2024.7.jar' `
  -OutFile "$env:USERPROFILE\tools\plantuml.jar"
```

**Option B — Mermaid fallback (no JRE):**
The same diagrams can be authored in Mermaid `flowchart TB` /
`sequenceDiagram` syntax and rendered via the existing
`tools/build_mindmaps.py` Graphviz toolchain. Less UML-strict but
zero new runtime.

`tools/render-uml.ps1` auto-detects which is available.

## Why VUP cares about all three

VUP (Unified Process) calls for orthogonal views of the same behaviour:
- Use Case = WHO interacts with WHAT
- Activity = HOW the flow proceeds (with branches)
- Sequence = WHAT messages cross WHICH lifelines (timing-aware)

Authoring all three from the same photo evidence catches inconsistencies
the single-diagram view would miss.

## Status

| Item | Value |
|------|-------|
| Folder | `recon/uml-templates/` |
| Templates | 3 (use case, activity, sequence) |
| Rendering | PlantUML (Profile C) or Mermaid fallback |
| Status | v0.1 — copy + fill per flow folder |
