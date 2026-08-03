#!/bin/bash
# ============================================================================
# install.sh — MDE Politeia Conciliar de Salamanca
# Instalacion completa: Concilio + CBMM + OpenCode MCP
#
# Uso: curl -fsSL https://raw.githubusercontent.com/.../install.sh | bash
# ============================================================================
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'
INSTALL_DIR="${HOME}/.local/bin"

main() {
    echo -e "${CYAN}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║  MDE Politeia Conciliar de Salamanca                    ║"
    echo "║  40 agentes IA · Silogismos · Logica de Conjuntos        ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"

    # ── 1. Python check ──────────────────────────────────
    echo -e "${GREEN}[1/4] Verificando Python...${NC}"
    command -v python3 >/dev/null || { echo -e "${RED}Requiere Python 3.11+. Instalalo primero.${NC}"; exit 1; }
    PYTHON=$(command -v python3)
    echo "  Python: $($PYTHON --version)"

    # ── 2. Install Concilio ───────────────────────────────
    echo -e "${GREEN}[2/4] Instalando concilio-salamanca...${NC}"
    pip install concilio-salamanca[all] --quiet 2>/dev/null || \
        $PYTHON -m pip install concilio-salamanca[all] --quiet
    echo "  concilio-salamanca instalado."

    # ── 3. Install CBMM (dependency) ──────────────────────
    echo -e "${GREEN}[3/4] Instalando codebase-memory-mcp...${NC}"
    if command -v codebase-memory-mcp >/dev/null 2>&1; then
        echo "  CBMM ya instalado: $(codebase-memory-mcp --version 2>/dev/null || echo 'detectado')"
    else
        echo "  Descargando CBMM..."
        curl -fsSL https://raw.githubusercontent.com/DeusData/codebase-memory-mcp/main/install.sh | bash
    fi

    # ── 4. Configure Concilio for OpenCode ────────────────
    echo -e "${GREEN}[4/4] Configurando OpenCode...${NC}"
    concilio install --agent opencode 2>/dev/null || \
        $PYTHON -m concilio_salamanca.main install --agent opencode
    echo "  MCP server configurado en opencode.json"

    # ── 5. Self-test ──────────────────────────────────────
    echo ""
    echo -e "${GREEN}✓ Instalacion completada.${NC}"
    echo ""
    echo "  Comandos rapidos:"
    echo "    concilio --list-agents         # 40 agentes"
    echo "    concilio --list-providers      # 6 proveedores LLM"
    echo "    concilio --check-tools         # Verificar herramientas"
    echo "    concilio --file app.js --agents escolasticos"
    echo ""
    echo "  Licencia:"
    echo "    concilio license --country MX --dev \"Tu Nombre\" --project \"Tu Proyecto\" --std"
    echo ""
}

main "$@"
