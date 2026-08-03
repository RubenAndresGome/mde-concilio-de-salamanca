# install.ps1 — MDE Politeia Conciliar de Salamanca (Windows)
# Instalacion completa: Concilio + CBMM + OpenCode MCP
#
# Uso: .\install.ps1
#   o: Invoke-Expression (Invoke-WebRequest -Uri https://.../install.ps1).Content

param(
    [switch]$SkipCBMM,
    [switch]$SkipTests,
    [switch]$Help
)

if ($Help) {
    Write-Host "MDE Politeia Conciliar de Salamanca — Instalador Windows"
    Write-Host "  .\install.ps1               Instalacion completa"
    Write-Host "  .\install.ps1 -SkipCBMM     Sin Codebase Memory MCP"
    exit 0
}

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  MDE Politeia Conciliar de Salamanca" -ForegroundColor Cyan
Write-Host "  40 agentes IA - Silogismos - Logica de Conjuntos" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. Python check ──────────────────────────────────
Write-Host "[1/4] Verificando Python..." -ForegroundColor Green
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command python3 -ErrorAction SilentlyContinue }
if (-not $python) { $python = Get-Command py -ErrorAction SilentlyContinue }
if (-not $python) {
    Write-Host "ERROR: Python 3.11+ requerido. Instalalo desde https://python.org" -ForegroundColor Red
    exit 1
}
Write-Host "  Python: $($python.Source)"

# ── 2. Install Concilio ───────────────────────────────
Write-Host "[2/4] Instalando concilio-salamanca..." -ForegroundColor Green
& $python -m pip install concilio-salamanca[all] --quiet
Write-Host "  concilio-salamanca instalado."

# ── 3. Install CBMM (dependency) ──────────────────────
if (-not $SkipCBMM) {
    Write-Host "[3/4] Instalando codebase-memory-mcp..." -ForegroundColor Green
    $cbmm = Get-Command codebase-memory-mcp -ErrorAction SilentlyContinue
    if (-not $cbmm) {
        Write-Host "  Descargando CBMM..."
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri "https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.ps1" -OutFile "$env:TEMP\install_cbmm.ps1"
        & "$env:TEMP\install_cbmm.ps1"
        Remove-Item "$env:TEMP\install_cbmm.ps1" -Force -ErrorAction SilentlyContinue
    } else {
        Write-Host "  CBMM ya instalado."
    }
}

# ── 4. Configure Concilio for OpenCode ────────────────
Write-Host "[4/4] Configurando OpenCode..." -ForegroundColor Green
& $python -m concilio_salamanca.main install --agent opencode
Write-Host "  MCP server configurado en opencode.json"

# ── 5. Done ───────────────────────────────────────────
Write-Host ""
Write-Host "Instalacion completada." -ForegroundColor Green
Write-Host ""
Write-Host "  Comandos rapidos:"
Write-Host "    concilio --list-agents         # 40 agentes"
Write-Host "    concilio --list-providers      # 6 proveedores LLM"
Write-Host "    concilio --check-tools         # Verificar herramientas"
Write-Host "    concilio --file app.js --agents escolasticos"
