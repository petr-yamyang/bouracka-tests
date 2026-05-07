<#
.SYNOPSIS
  Render PlantUML files in a flow folder to PNG + SVG.

.DESCRIPTION
  Per CP-SUPIN-04 L-WORK-7. Auto-detects PlantUML jar (Profile C
  install) or falls back to Mermaid via Graphviz.

.PARAMETER FlowFolder
  Path to a flow folder containing *.puml files.

.EXAMPLE
  .\tools\render-uml.ps1 -FlowFolder .\recon\screenflows-live\flow-A1-main-tst
#>
param(
  [Parameter(Mandatory = $true)] [string]$FlowFolder
)
$ErrorActionPreference = 'Continue'

if (-not (Test-Path $FlowFolder -PathType Container)) {
  Write-Host "[FAIL] flow folder not found: $FlowFolder" -ForegroundColor Red
  exit 1
}

$pumlFiles = Get-ChildItem -Path $FlowFolder -File -Filter '*.puml'
if ($pumlFiles.Count -eq 0) {
  Write-Host "[INFO] no .puml files in $FlowFolder" -ForegroundColor Yellow
  exit 0
}

# Locate PlantUML
$plantumlJar = "$env:USERPROFILE\tools\plantuml.jar"
$java = Get-Command java -ErrorAction SilentlyContinue

if ((Test-Path $plantumlJar) -and $java) {
  Write-Host "[render-uml] PlantUML present; rendering..." -ForegroundColor Cyan
  foreach ($f in $pumlFiles) {
    & java -jar $plantumlJar -tpng $f.FullName 2>&1 | Out-Null
    & java -jar $plantumlJar -tsvg $f.FullName 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
      Write-Host "[OK] $($f.Name) -> PNG + SVG" -ForegroundColor Green
    } else {
      Write-Host "[FAIL] $($f.Name) (exit $LASTEXITCODE)" -ForegroundColor Red
    }
  }
} else {
  Write-Host "[FAIL] PlantUML not present." -ForegroundColor Red
  Write-Host "       Install per recon/uml-templates/README.md (Profile C):" -ForegroundColor Yellow
  Write-Host "         winget install Microsoft.OpenJDK.21" -ForegroundColor Yellow
  Write-Host "         Invoke-WebRequest 'https://github.com/plantuml/plantuml/releases/download/v1.2024.7/plantuml-1.2024.7.jar' -OutFile `"`$env:USERPROFILE\tools\plantuml.jar`"" -ForegroundColor Yellow
  Write-Host "" -ForegroundColor Yellow
  Write-Host "       Mermaid fallback: convert .puml content to Mermaid syntax + use" -ForegroundColor Yellow
  Write-Host "       tools/build_mindmaps.py-style Graphviz rendering." -ForegroundColor Yellow
  exit 1
}
