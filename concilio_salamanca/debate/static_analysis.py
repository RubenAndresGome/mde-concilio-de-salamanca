"""
Analisis estatico pre-debate usando AST (Tree-sitter) y fallback a regex.
Extrae metricas objetivas del codigo y un arbol simplificado.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Dict

try:
    import tree_sitter
    import tree_sitter_python as tspython
    import tree_sitter_javascript as tsjavascript
    from tree_sitter import Language, Parser

    HAS_TREE_SITTER = True
    PY_LANGUAGE = Language(tspython.language())
    JS_LANGUAGE = Language(tsjavascript.language())
except ImportError:
    HAS_TREE_SITTER = False


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
    comment_lines = sum(
        1 for l in lines if l.strip().startswith(("//", "#", "--", "/*", "*", "<!--"))
    )
    blank_lines = total_lines - non_empty

    metrics = {
        "archivo": filepath or "(string)",
        "extension": ext,
        "lineas_totales": total_lines,
        "lineas_no_vacias": non_empty,
        "lineas_comentarios": comment_lines,
        "lineas_vacias": blank_lines,
        "ratio_comentarios": f"{comment_lines / max(total_lines, 1) * 100:.1f}%",
        "ast_parseado": False,
    }

    ast_summary = ""

    if HAS_TREE_SITTER and ext in (".py", ".js", ".ts", ".jsx", ".tsx", ".mjs"):
        metrics["ast_parseado"] = True
        if ext == ".py":
            parser = Parser()
            parser.language = PY_LANGUAGE
            tree = parser.parse(bytes(code, "utf8"))
            metrics.update(_analyze_python_ast(tree.root_node, code))
            ast_summary = _generate_ast_summary(tree.root_node, code, lang="python")
        else:
            parser = Parser()
            parser.language = JS_LANGUAGE
            tree = parser.parse(bytes(code, "utf8"))
            metrics.update(_analyze_javascript_ast(tree.root_node, code))
            ast_summary = _generate_ast_summary(tree.root_node, code, lang="javascript")

        metrics["ast_summary"] = ast_summary
    else:
        # Fallback a regex
        if ext in (".py",):
            metrics.update(_analyze_python_regex(code))
        elif ext in (".js", ".ts", ".jsx", ".tsx", ".mjs"):
            metrics.update(_analyze_javascript_regex(code))
        elif ext in (".c", ".cpp", ".h", ".hpp", ".ino"):
            metrics.update(_analyze_c(code))
        elif ext in (".rs",):
            metrics.update(_analyze_rust(code))

    metrics.update(_analyze_common_regex(code))

    return metrics


def _analyze_python_ast(root, code: str) -> Dict:
    funciones = 0
    clases = 0
    imports = 0
    async_funcs = 0

    def traverse(node):
        nonlocal funciones, clases, imports, async_funcs
        if node.type == "function_definition":
            funciones += 1
            if node.child_by_field_name("return_type"):
                pass  # Has type hints
        elif node.type == "class_definition":
            clases += 1
        elif node.type in ("import_statement", "import_from_statement"):
            imports += 1

        # Check for async
        if node.type == "function_definition":
            for child in node.children:
                if child.type == "async":
                    async_funcs += 1
                    break

        for child in node.children:
            traverse(child)

    traverse(root)
    return {
        "ast_funciones": funciones,
        "ast_clases": clases,
        "ast_imports": imports,
        "async_functions": async_funcs,
    }


def _analyze_javascript_ast(root, code: str) -> Dict:
    funciones = 0
    clases = 0
    imports = 0

    def traverse(node):
        nonlocal funciones, clases, imports
        if node.type in ("function_declaration", "arrow_function", "method_definition"):
            funciones += 1
        elif node.type == "class_declaration":
            clases += 1
        elif node.type == "import_statement":
            imports += 1

        for child in node.children:
            traverse(child)

    traverse(root)
    return {"ast_funciones": funciones, "ast_clases": clases, "ast_imports": imports}


def _generate_ast_summary(root, code: str, lang: str) -> str:
    """Genera un resumen simplificado del AST para inyectar en el prompt"""
    summary = []

    def traverse(node, depth=0):
        if depth > 2:  # No profundizar mucho para no ahogar el token window
            return

        indent = "  " * depth
        if lang == "python":
            if node.type == "class_definition":
                name = node.child_by_field_name("name")
                if name:
                    summary.append(
                        f"{indent}Class: {code[name.start_byte : name.end_byte]}"
                    )
            elif node.type == "function_definition":
                name = node.child_by_field_name("name")
                if name:
                    summary.append(
                        f"{indent}Function: {code[name.start_byte : name.end_byte]}"
                    )
        elif lang == "javascript":
            if node.type == "class_declaration":
                name = node.child_by_field_name("name")
                if name:
                    summary.append(
                        f"{indent}Class: {code[name.start_byte : name.end_byte]}"
                    )
            elif node.type == "function_declaration":
                name = node.child_by_field_name("name")
                if name:
                    summary.append(
                        f"{indent}Function: {code[name.start_byte : name.end_byte]}"
                    )

        for child in node.children:
            traverse(
                child,
                depth
                + (1 if node.type in ("class_definition", "class_declaration") else 0),
            )

    traverse(root)
    return "\n".join(summary[:50])  # Limitar a 50 líneas


def _analyze_common_regex(code: str) -> Dict:
    return {
        "complejidad_ciclomatica_aprox": len(
            re.findall(r"\b(if |else if|for |while |case |catch |\band\b|\bor\b)", code)
        ),
        "try_catch": len(re.findall(r"\btry\b", code)),
        "hardcoded_secrets": len(
            re.findall(
                r'(api_key|password|secret|token)\s*=\s*["\'][^"\']+["\']',
                code,
                re.IGNORECASE,
            )
        ),
        "console_logs": len(
            re.findall(r"\b(console\.log|print\(|println!|fmt\.Print|cout)", code)
        ),
    }


def _analyze_python_regex(code: str) -> Dict:
    return {
        "funciones_regex": len(re.findall(r"\bdef \w+", code)),
        "clases_regex": len(re.findall(r"\bclass \w+", code)),
        "decoradores": len(re.findall(r"^\s*@\w+", code, re.MULTILINE)),
        "type_hints_presentes": bool(re.search(r"def \w+\([^)]*:\s*\w+", code)),
        "async_functions": len(re.findall(r"\basync def\b", code)),
        "comprehensions": len(re.findall(r"\[.* for .* in .*\]", code)),
    }


def _analyze_javascript_regex(code: str) -> Dict:
    return {
        "funciones_regex": len(re.findall(r"\bfunction \w+", code))
        + len(re.findall(r"=>", code)),
        "clases_regex": len(re.findall(r"\bclass \w+", code)),
        "hooks_react": len(re.findall(r"\buse[A-Z]\w+\(", code)),
        "async_await": len(re.findall(r"\basync\b", code)),
        "jsx_components": len(re.findall(r"<[A-Z]\w+", code)),
        "template_literals": len(re.findall(r"`.*\$\{", code)),
    }


def _analyze_c(code: str) -> Dict:
    return {
        "malloc_free": len(re.findall(r"\b(malloc|calloc|realloc|free)\b", code)),
        "pointers": len(re.findall(r"\*\w+", code)),
        "volatile_vars": len(re.findall(r"\bvolatile\b", code)),
        "isr_functions": len(
            re.findall(r"\bISR\b|__attribute__\s*\(\s*\(\s*interrupt\s*\)", code)
        ),
    }


def _analyze_rust(code: str) -> Dict:
    return {
        "unsafe_blocks": len(re.findall(r"\bunsafe\b", code)),
        "lifetimes": len(re.findall(r"'[a-z]+", code)),
        "match_expressions": len(re.findall(r"\bmatch\b", code)),
        "unwrap_calls": len(re.findall(r"\.unwrap\(\)", code)),
    }


def format_analysis(metrics: Dict) -> str:
    lines = ["=== ANALISIS ESTATICO PRE-DEBATE ===", ""]
    for key, value in metrics.items():
        if key.startswith("_") or key == "ast_summary":
            continue
        lines.append(f"  {key}: {value}")

    if "ast_summary" in metrics and metrics["ast_summary"]:
        lines.append("")
        lines.append("--- Estructura AST (Tree-sitter) ---")
        lines.append(metrics["ast_summary"])

    return "\n".join(lines)


def auto_select_agents(filepath: str, code: str) -> list:
    ext = os.path.splitext(filepath)[1].lower()
    code_lower = code.lower()
    agents = []

    if any(
        kw in code_lower
        for kw in (
            "torch",
            "tensorflow",
            "tf.",
            "nn.module",
            "keras",
            "jax",
            "model.fit",
        )
    ):
        agents.append("auditor_dl")
    if ext in (".tsx", ".jsx", ".html", ".css", ".vue", ".svelte"):
        agents.extend(["ratio", "vitoria"])
    if ext in (".ino", ".c", ".h") or any(
        kw in code_lower for kw in ("esp32", "arduino", "freertos", "gpio", "isr")
    ):
        agents.append("iot")
    if ext in (".sql", ".sqlx"):
        agents.extend(["datos", "sixsigma"])
    if any(
        kw in code_lower
        for kw in ("dockerfile", "docker-compose", "k8s", "kubernetes", "helm")
    ):
        agents.extend(["sistemas", "mlops"])
    if any(
        kw in code_lower
        for kw in ("password", "auth", "login", "jwt", "oauth", "api_key")
    ):
        agents.append("seguridad")

    agents.append("promotor")
    agents.append("defensor")

    if len(agents) < 4:
        agents.extend(["doctor", "larouche"])

    return list(dict.fromkeys(agents))
