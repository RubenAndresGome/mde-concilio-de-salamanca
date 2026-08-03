"""
Instalador del Concilio — Configuracion automatica de OpenCode MCP.

Detecta agentes, configura opencode.json, inyecta AGENTS.md,
copia SKILL.md y ejecuta self-tests.
"""

from __future__ import annotations

import json
import importlib.util
import shutil
from pathlib import Path
from typing import Dict, Optional


AGENT_CONFIG_PATHS: Dict[str, Dict[str, str]] = {
    "opencode": {
        "config_dir": ".config/opencode",
        "config_file": "opencode.json",
        "agents_file": "AGENTS.md",
        "skills_dir": ".opencode/skills/concilio-salamanca",
    },
    "claude": {
        "config_dir": ".claude",
        "config_file": ".mcp.json",
        "agents_file": "CLAUDE.md",
    },
}

SKILL_ROOT = Path(__file__).parent
SKILL_MD_SOURCE = SKILL_ROOT / "SKILL.md"
AGENTS_MD_SOURCE = SKILL_ROOT.parent / "AGENTS.md"

AGENTS_MD_CONTENT = """<!-- concilio-salamanca:start -->
## Concilio de Salamanca — MDE Politeia

Cuando trabajes con codigo fuente, usa el Concilio de Salamanca para auditoria:

```bash
# Auditoria basica (escolastica)
concilio --file <archivo> --agents escolasticos

# Auditoria rapida (CI/CD)
concilio --file <archivo> --fast

# Auditoria de seguridad
concilio --file <archivo> --agents red_team

# Con logica de conjuntos (OckhamDev + CBMM)
concilio --file <archivo> --agents logici --ockham

# Generar licencia RNS v5.0
concilio license --country MX --dev "Nombre" --project "Proyecto" --std

# Ver herramientas disponibles
concilio --check-tools
```

El Concilio expone 40 agentes IA que debaten usando silogismos aristotelico-tomistas.
Prefiere usar `concilio` sobre grep/file-read para auditoria de codigo.
<!-- concilio-salamanca:end -->
"""


def detect_agent(agent_name: str) -> bool:
    """Detecta si un agente de codigo (OpenCode, Claude, etc.) esta instalado."""
    if agent_name == "opencode":
        return shutil.which("opencode") is not None
    if agent_name == "claude":
        return shutil.which("claude") is not None
    return False


def get_config_path(agent: str) -> Optional[Path]:
    """Retorna la ruta al directorio de configuracion del agente."""
    info = AGENT_CONFIG_PATHS.get(agent)
    if not info:
        return None
    home = Path.home()
    config_dir = home / info["config_dir"]
    return config_dir if config_dir.exists() else None


def configure_mcp(agent: str = "opencode", binary_path: Optional[str] = None) -> bool:
    """Configura el MCP server para concilio-salamanca en el agente.

    Para OpenCode, modifica ~/.config/opencode/opencode.json anadiendo
    la entrada MCP bajo la clave "mcp".
    """
    if agent != "opencode":
        print(f"  [WARN] Agente '{agent}' no soportado aun. Solo OpenCode.")
        return False

    config_dir = get_config_path(agent)
    if not config_dir:
        print(f"  [WARN] No se encontro {agent} config. Instala {agent} primero.")
        return False

    config_file = config_dir / "opencode.json"
    existing = {}
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                existing = json.loads(f.read())
        except json.JSONDecodeError:
            pass

    binary = binary_path or shutil.which("concilio") or "concilio"
    mcp_entry = {
        "enabled": True,
        "type": "local",
        "command": [binary, "mcp-serve"],
    }

    if "mcp" not in existing:
        existing["mcp"] = {}
    existing["mcp"]["concilio-salamanca"] = mcp_entry

    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)
    print(f"  MCP configurado: {config_file}")
    return True


def inject_agents_md(agent: str = "opencode") -> bool:
    """Inyecta instrucciones del Concilio en AGENTS.md del agente."""
    config_dir = get_config_path(agent)
    if not config_dir:
        return False

    agents_file = config_dir / "AGENTS.md"
    content = AGENTS_MD_CONTENT

    if agents_file.exists():
        existing = agents_file.read_text(encoding="utf-8", errors="ignore")
        start = "<!-- concilio-salamanca:start -->"
        end = "<!-- concilio-salamanca:end -->"
        if start in existing and end in existing:
            pre = existing[:existing.index(start)]
            post = existing[existing.index(end) + len(end):]
            content = pre + content + post
        else:
            content = existing + "\n\n" + content

    agents_file.write_text(content, encoding="utf-8")
    print(f"  AGENTS.md actualizado: {agents_file}")
    return True


def copy_skill_md(agent: str = "opencode") -> bool:
    """Copia la skill y las referencias que enlaza, sin archivos superfluos."""
    if not SKILL_MD_SOURCE.exists():
        print("  [WARN] SKILL.md no encontrado en el paquete.")
        return False

    if agent == "opencode":
        # OpenCode skills van en ~/.config/opencode/skills/concilio-salamanca/
        skills_dir = Path.home() / ".config" / "opencode" / "skills" / "concilio-salamanca"
    else:
        skills_dir = Path.home() / AGENT_CONFIG_PATHS[agent]["skills_dir"]

    skills_dir.mkdir(parents=True, exist_ok=True)
    dest = skills_dir / "SKILL.md"
    shutil.copy2(SKILL_MD_SOURCE, dest)
    resources = (
        (SKILL_ROOT / "agents" / "openai.yaml", skills_dir / "agents" / "openai.yaml"),
        (
            SKILL_ROOT / "reference" / "gobernanza_cognitiva.md",
            skills_dir / "reference" / "gobernanza_cognitiva.md",
        ),
    )
    for source, target in resources:
        if source.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    print(f"  Skill copiada a: {skills_dir}")
    return True


def self_test() -> Dict[str, bool]:
    """Ejecuta verificaciones basicas post-instalacion."""
    results = {}
    results["import_ok"] = _try_import()
    results["cli_ok"] = shutil.which("concilio") is not None
    results["cbmm_ok"] = shutil.which("codebase-memory-mcp") is not None
    results["agents_ok"] = _try_count_agents()
    return results


def _try_import() -> bool:
    return importlib.util.find_spec("concilio_salamanca") is not None


def _try_count_agents() -> bool:
    try:
        from concilio_salamanca.agents import AGENT_REGISTRY
        return len(AGENT_REGISTRY) >= 35
    except Exception:
        return False


def uninstall(agent: str = "opencode") -> bool:
    """Desinstala la configuracion MCP del Concilio."""
    config_dir = get_config_path(agent)
    if not config_dir:
        return False

    config_file = config_dir / "opencode.json"
    if config_file.exists():
        try:
            data = json.loads(config_file.read_text(encoding="utf-8"))
            data.get("mcp", {}).pop("concilio-salamanca", None)
            config_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        except (json.JSONDecodeError, KeyError):
            pass

    agents_file = config_dir / "AGENTS.md"
    if agents_file.exists():
        content = agents_file.read_text(encoding="utf-8", errors="ignore")
        start = "<!-- concilio-salamanca:start -->"
        end = "<!-- concilio-salamanca:end -->"
        if start in content and end in content:
            content = content[:content.index(start)] + content[content.index(end) + len(end):]
            agents_file.write_text(content, encoding="utf-8")

    return True


def format_install_report(results: Dict[str, bool]) -> str:
    lines = ["=== Reporte de Instalacion ===", ""]
    for key, ok in results.items():
        lines.append(f"  {'✓' if ok else '✗'} {key}: {'OK' if ok else 'FALLO'}")
    return "\n".join(lines)
