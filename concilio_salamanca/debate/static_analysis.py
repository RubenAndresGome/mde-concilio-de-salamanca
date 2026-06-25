"""
Analisis estatico ligero pre-debate.
Extrae metricas objetivas del codigo para inyectarlas como contexto a los agentes.
"""

from __future__ import annotations

import os
import re
from collections import Counter
from pathlib import Path
from typing import Dict, Optional


def analyze_file(filepath: str) -> Dict:
    path = Path(filepath)
    if not path.exists():
        return {"error": f"Archivo no encontrado: {filepath}"}

    code = path.read_text(encoding="utf-8", errors="replace")
    return analyze_code(code, filepath)


def analyze_code(code: str, filepath: str = "") -> Dict:
    ext = os.path.splitext(filepath)[1].lower() if filepath else ""
    lines = code.split("\n")
    total_lines = len(lines)
    non_empty = sum(1 for l in lines if l.strip())
    comment_lines = sum(1 for l in lines if l.strip().startswith(("//", "#", "--", "/*", "*", "<!--")))
    blank_lines = total_lines - non_empty

    metrics = {
        "archivo": filepath or "(string)",
        "extension": ext,
        "lineas_totales": total_lines,
        "lineas_no_vacias": non_empty,
        "lineas_comentarios": comment_lines,
        "lineas_vacias": blank_lines,
        "ratio_comentarios": f"{comment_lines / max(total_lines, 1) * 100:.1f}%",
    }

    if ext in (".py",):
        metrics.update(_analyze_python(code))
    elif ext in (".js", ".ts", ".jsx", ".tsx", ".mjs"):
        metrics.update(_analyze_javascript(code))
    elif ext in (".c", ".cpp", ".h", ".hpp", ".ino"):
        metrics.update(_analyze_c(code))
    elif ext in (".rs",):
        metrics.update(_analyze_rust(code))

    metrics.update(_analyze_common(code))

    return metrics


def _analyze_common(code: str) -> Dict:
    patterns = {
        "funciones": len(re.findall(r'\b(def |function |fn |func |public static |void |int |bool |String )', code)),
        "clases": len(re.findall(r'\b(class |struct |interface |trait |enum )', code)),
        "imports": len(re.findall(r'^\s*(import |from |require\(|#include|use )', code, re.MULTILINE)),
        "complejidad_ciclomatica_aprox": len(re.findall(r'\b(if |else if|for |while |case |catch |\band\b|\bor\b)', code)),
        "try_catch": len(re.findall(r'\btry\b', code)),
        "hardcoded_secrets": len(re.findall(r'(api_key|password|secret|token)\s*=\s*["\'][^"\']+["\']', code, re.IGNORECASE)),
        "console_logs": len(re.findall(r'\b(console\.log|print\(|println!|fmt\.Print|cout)', code)),
    }
    return patterns


def _analyze_python(code: str) -> Dict:
    return {
        "decoradores": len(re.findall(r'^\s*@\w+', code, re.MULTILINE)),
        "type_hints_presentes": bool(re.search(r'def \w+\([^)]*:\s*\w+', code)),
        "async_functions": len(re.findall(r'\basync def\b', code)),
        "comprehensions": len(re.findall(r'\[.* for .* in .*\]', code)),
    }


def _analyze_javascript(code: str) -> Dict:
    return {
        "hooks_react": len(re.findall(r'\buse[A-Z]\w+\(', code)),
        "async_await": len(re.findall(r'\basync\b', code)),
        "jsx_components": len(re.findall(r'<[A-Z]\w+', code)),
        "template_literals": len(re.findall(r'`.*\$\{', code)),
    }


def _analyze_c(code: str) -> Dict:
    return {
        "malloc_free": len(re.findall(r'\b(malloc|calloc|realloc|free)\b', code)),
        "pointers": len(re.findall(r'\*\w+', code)),
        "volatile_vars": len(re.findall(r'\bvolatile\b', code)),
        "isr_functions": len(re.findall(r'\bISR\b|__attribute__\s*\(\s*\(\s*interrupt\s*\)', code)),
    }


def _analyze_rust(code: str) -> Dict:
    return {
        "unsafe_blocks": len(re.findall(r'\bunsafe\b', code)),
        "lifetimes": len(re.findall(r"'[a-z]+", code)),
        "match_expressions": len(re.findall(r'\bmatch\b', code)),
        "unwrap_calls": len(re.findall(r'\.unwrap\(\)', code)),
    }


def format_analysis(metrics: Dict) -> str:
    lines = ["=== ANALISIS ESTATICO PRE-DEBATE ===", ""]
    for key, value in metrics.items():
        if key.startswith("_"):
            continue
        lines.append(f"  {key}: {value}")
    return "\n".join(lines)


def auto_select_agents(filepath: str, code: str) -> list:
    ext = os.path.splitext(filepath)[1].lower()
    code_lower = code.lower()
    agents = []

    if any(kw in code_lower for kw in ("torch", "tensorflow", "tf.", "nn.module", "keras", "jax", "model.fit")):
        agents.append("auditor_dl")
    if ext in (".tsx", ".jsx", ".html", ".css", ".vue", ".svelte"):
        agents.extend(["ratio", "vitoria"])
    if ext in (".ino", ".c", ".h") or any(kw in code_lower for kw in ("esp32", "arduino", "freertos", "gpio", "isr")):
        agents.append("iot")
    if ext in (".sql", ".sqlx"):
        agents.extend(["datos", "sixsigma"])
    if any(kw in code_lower for kw in ("dockerfile", "docker-compose", "k8s", "kubernetes", "helm")):
        agents.extend(["sistemas", "mlops"])
    if any(kw in code_lower for kw in ("password", "auth", "login", "jwt", "oauth", "api_key")):
        agents.append("seguridad")

    agents.append("promotor")
    agents.append("defensor")

    if len(agents) < 4:
        agents.extend(["doctor", "larouche"])

    return list(dict.fromkeys(agents))
