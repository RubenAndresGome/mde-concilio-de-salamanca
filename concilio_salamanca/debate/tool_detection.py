"""
Detección e instalación de herramientas externas:
- Spec-Kit CLI (`specify`) — Spec-Driven Development
- Open-Design CLI (`od`) — Generative UI/UX design
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from typing import Dict, Optional


def detect_cli(name: str) -> bool:
    """Check if a CLI tool is available on PATH."""
    return shutil.which(name) is not None


def detect_specify() -> Dict[str, bool]:
    """Detect Spec-Kit CLI availability."""
    return {"available": detect_cli("specify")}


def detect_opendesign() -> Dict[str, bool]:
    """Detect Open-Design CLI availability."""
    return {"available": detect_cli("od")}


def install_specify(version: str = "v0.4.2") -> bool:
    """Install Spec-Kit CLI via uv tool install.

    Returns True if installation succeeded.
    """
    if detect_cli("specify"):
        return True
    uv = shutil.which("uv")
    if not uv:
        print("  [WARN] Se requiere `uv` para instalar Spec-Kit. Instalalo desde https://docs.astral.sh/uv/")
        return False
    try:
        print(f"  Instalando Spec-Kit CLI ({version})...")
        result = subprocess.run(
            [
                uv, "tool", "install", "specify-cli",
                "--from", f"git+https://github.com/github/spec-kit.git@{version}",
            ],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0:
            print("  Spec-Kit CLI instalado correctamente.")
            return True
        print(f"  Error instalando Spec-Kit: {result.stderr[-200:]}")
    except Exception as e:
        print(f"  Error instalando Spec-Kit: {e}")
    return False


def install_opendesign_mcp() -> bool:
    """Install Open-Design MCP server for opencode.

    Returns True if MCP was installed or already available.
    """
    if not detect_cli("od"):
        print("  [WARN] Open-Design CLI no encontrado. Descargalo desde https://open-design.ai")
        return False
    try:
        print("  Instalando MCP de Open-Design para OpenCode...")
        result = subprocess.run(
            ["od", "mcp", "install", "opencode"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            print("  MCP de Open-Design instalado correctamente.")
            return True
        print(f"  Error instalando MCP: {result.stderr[-200:]}")
    except Exception as e:
        print(f"  Error instalando MCP: {e}")
    return False


def check_prerequisites(verbose: bool = True) -> Dict[str, bool]:
    """Check all prerequisites and offer installation where possible.

    Returns dict with availability status for each tool.
    """
    status: Dict[str, bool] = {}

    # Spec-Kit
    spec = detect_specify()
    status["specify"] = spec["available"]
    if verbose:
        print(f"  Spec-Kit CLI:    {'✓ disponible' if status['specify'] else '✗ no encontrado'}")

    # Open-Design
    od = detect_opendesign()
    status["opendesign"] = od["available"]
    if verbose:
        print(f"  Open-Design CLI: {'✓ disponible' if status['opendesign'] else '✗ no encontrado'}")

    # MCP
    if status["opendesign"]:
        status["od_mcp"] = install_opendesign_mcp()
    else:
        status["od_mcp"] = False

    # Attempt install if missing
    if not status["specify"]:
        if verbose:
            print("  Intentando instalar Spec-Kit CLI...")
        status["specify"] = install_specify()

    if not status["od_mcp"] and status["opendesign"]:
        if verbose:
            print("  Intentando instalar MCP de Open-Design...")
        status["od_mcp"] = install_opendesign_mcp()

    return status
