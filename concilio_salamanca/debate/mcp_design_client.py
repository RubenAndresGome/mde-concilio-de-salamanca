"""
Cliente MCP para Open-Design.

Permite al Magister Delineationis invocar Open-Design via su servidor MCP
para generar prototipos visuales, decks, e imagenes.

Requisito: Open-Design CLI instalada y MCP configurado.
  od mcp install opencode
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


OD_DESIGN_SYSTEMS_DIR = "design-systems"
OD_SKILLS_DIR = "skills"
OD_PREVIEW_URL = "http://localhost:7456"


def detect_od() -> bool:
    """Check if Open-Design CLI is available."""
    import shutil
    return shutil.which("od") is not None


def generate_prototype(
    brief: str,
    skill: str = "landing-page",
    design_system: str = "default",
    output_dir: Optional[str] = None,
    model: str = "deepseek/deepseek-v4-flash",
) -> Dict[str, Any]:
    """Generate a visual prototype via Open-Design CLI.

    Args:
        brief: Description of what to build
        skill: Open-Design skill name (e.g. 'landing-page', 'dashboard', 'mobile-app')
        design_system: Design system name (e.g. 'linear', 'vercel', 'default')
        output_dir: Where to save the output (default: ./od-output/)
        model: Model to use for generation

    Returns:
        Dict with 'success', 'artifact_id', 'preview_url', 'output_path', 'error'
    """
    if not detect_od():
        return {
            "success": False,
            "error": "Open-Design CLI no encontrado. Descargalo desde https://open-design.ai",
        }

    out = output_dir or os.path.join(os.getcwd(), "od-output")
    os.makedirs(out, exist_ok=True)

    try:
        cmd = [
            "od", "generate",
            "--skill", skill,
            "--design-system", design_system,
            "--model", model,
            "--output", out,
            "--brief", brief,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"Open-Design fallo: {result.stderr[-300:]}",
            }
        # Parse output for artifact ID
        output_text = result.stdout
        artifact_id = _parse_artifact_id(output_text)
        return {
            "success": True,
            "artifact_id": artifact_id or "unknown",
            "preview_url": f"{OD_PREVIEW_URL}/preview/{artifact_id}" if artifact_id else OD_PREVIEW_URL,
            "output_path": out,
            "raw_output": output_text,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Open-Design timeout (120s)"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def export_artifact(
    artifact_id: str,
    fmt: str = "html",
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Export an Open-Design artifact to a file.

    Args:
        artifact_id: ID from generate_prototype()
        fmt: 'html', 'pdf', or 'pptx'
        output_path: Destination file path

    Returns:
        Dict with 'success' and 'path'
    """
    if not detect_od():
        return {"success": False, "error": "Open-Design CLI no encontrado"}

    dest = output_path or f"{artifact_id}.{fmt}"
    try:
        cmd = ["od", "export", artifact_id, "--format", fmt, "--output", dest]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            return {"success": False, "error": f"Export fallo: {result.stderr[-200:]}"}
        return {"success": True, "path": dest}
    except Exception as e:
        return {"success": False, "error": str(e)}


def load_design_system(path: str = ".") -> Optional[Dict]:
    """Load DESIGN.md from project directory and parse as structured dict.

    Returns None if no DESIGN.md found.
    """
    design_path = Path(path) / "DESIGN.md"
    if not design_path.exists():
        # Check for design-systems in OD dir
        od_ds = Path.home() / ".open-design" / "design-systems" / "default" / "DESIGN.md"
        if od_ds.exists():
            design_path = od_ds
        else:
            return None

    try:
        content = design_path.read_text(encoding="utf-8")
        return {"path": str(design_path), "content": content, "source": "project"}
    except Exception:
        return None


def check_od_server() -> bool:
    """Check if Open-Design daemon is running."""
    try:
        import urllib.request
        req = urllib.request.Request(f"{OD_PREVIEW_URL}/health", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        return False


def _parse_artifact_id(output: str) -> Optional[str]:
    """Extract artifact ID from Open-Design CLI output."""
    import re
    match = re.search(r"artifact[:\s]+([a-zA-Z0-9_-]+)", output, re.IGNORECASE)
    if match:
        return match.group(1)
    match = re.search(r"id[:\s]+([a-zA-Z0-9_-]+)", output)
    if match:
        return match.group(1)
    return None


def list_skills() -> List[str]:
    """List available Open-Design skills."""
    if not detect_od():
        return []
    try:
        result = subprocess.run(
            ["od", "skills", "list"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        pass
    return []


def list_design_systems() -> List[str]:
    """List available Open-Design design systems."""
    if not detect_od():
        return []
    try:
        result = subprocess.run(
            ["od", "design-system", "list"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        pass
    return []
