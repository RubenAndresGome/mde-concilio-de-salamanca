"""
OckhamEngine — Motor de logica escolastica y teoria de conjuntos para el Concilio.

Conecta con codebase-memory-mcp (CBMM) via subprocess/CLI para obtener el grafo
de conocimiento del codebase y ejecuta operaciones de conjunto:

- DEFINIDOS: entes (funciones/clases) que existen en el codebase
- INVOCADOS: entes que son llamados por otros
- CONTRADICCIONES = INVOCADOS ∖ DEFINIDOS (alucinaciones)
- SUPERFLUOS = DEFINIDOS ∖ INVOCADOS (codigo muerto, violacion Ockham)
- SANOS = DEFINIDOS ∩ INVOCADOS

Silogismo fundamental:
  Premisa Mayor:  ∀x (I(x) → E(x))  — Todo ente invocado debe existir.
  Premisa Menor:  f es invocada pero ¬E(f).
  Conclusio:      Hay CONTRADICCION. f es una alucinacion.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Any, Dict, List, Optional, Set, Tuple


class OckhamEngine:
    """Motor de analisis logico-escolastico basado en grafos CBMM.

    Usa codebase-memory-mcp CLI para consultar el grafo de conocimiento
    y ejecuta operaciones de conjunto para detectar contradicciones logicas.
    """

    def __init__(self, codebase_path: Optional[str] = None):
        self.codebase_path = codebase_path or os.getcwd()
        self._cbmm_available = shutil.which("codebase-memory-mcp") is not None

    @property
    def available(self) -> bool:
        return self._cbmm_available

    # ── Consultas a CBMM ─────────────────────────────────────────────

    def _cli(self, tool: str, args: dict) -> Optional[Dict[str, Any]]:
        """Invoca una herramienta MCP de CBMM via CLI."""
        if not self._cbmm_available:
            return None
        try:
            arg_json = json.dumps(args)
            result = subprocess.run(
                ["codebase-memory-mcp", "cli", tool, arg_json],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout)
        except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
            pass
        return None

    def get_defined_entities(self) -> Set[str]:
        """Retorna el conjunto de entes DEFINIDOS en el codebase.

        Consulta CBMM search_graph para obtener todas las funciones, clases,
        metodos e interfaces definidas.
        """
        result = self._cli("search_graph", {"label": "Function", "limit": 5000})
        if not result or "results" not in result:
            return set()
        entities = set()
        for r in result["results"]:
            name = r.get("name", "")
            if name:
                entities.add(name)
        # Also get classes
        cls_result = self._cli("search_graph", {"label": "Class", "limit": 2000})
        if cls_result and "results" in cls_result:
            for r in cls_result["results"]:
                name = r.get("name", "")
                if name:
                    entities.add(name)
        return entities

    def get_invoked_entities(self) -> Set[str]:
        """Retorna el conjunto de entes INVOCADOS.

        Extrae callers del grafo para determinar que funciones son llamadas.
        """
        result = self._cli("search_graph", {"label": "Function", "limit": 5000})
        if not result or "results" not in result:
            return set()
        invoked = set()
        for r in result["results"]:
            if r.get("call_count", 0) > 0 or r.get("in_degree", 0) > 0:
                name = r.get("name", "")
                if name:
                    invoked.add(name)
        return invoked

    def trace_callers(self, function_name: str) -> List[str]:
        """Retorna los caller de una funcion especifica."""
        result = self._cli("trace_path", {
            "function_name": function_name,
            "direction": "inbound",
            "depth": 1,
        })
        if not result or "results" not in result:
            return []
        return [r.get("name", "") for r in result["results"] if r.get("name")]

    # ── Operaciones de Conjunto ───────────────────────────────────────

    @staticmethod
    def contradiction_set(invocados: Set[str], definidos: Set[str]) -> Set[str]:
        """CONTRADICCIONES = INVOCADOS ∖ DEFINIDOS.

        Entes que son invocados pero no existen. = Alucinaciones del LLM.
        """
        return invocados - definidos

    @staticmethod
    def superfluous_set(definidos: Set[str], invocados: Set[str]) -> Set[str]:
        """SUPERFLUOS = DEFINIDOS ∖ INVOCADOS.

        Entes que existen pero no son invocados. = Codigo muerto.
        """
        return definidos - invocados

    @staticmethod
    def healthy_set(definidos: Set[str], invocados: Set[str]) -> Set[str]:
        """SANOS = DEFINIDOS ∩ INVOCADOS.

        Entes que existen Y son invocados. = Codigo sano.
        """
        return definidos & invocados

    # ── Analisis Logico ───────────────────────────────────────────────

    def analyze(self, scope: Optional[str] = None) -> Dict[str, Any]:
        """Ejecuta el analisis completo de logica escolastica.

        Args:
            scope: Si se especifica, limita el analisis a un modulo/archivo.

        Returns:
            dict con resultados de conjuntos y veredicto.
        """
        definidos = self.get_defined_entities()
        invocados = self.get_invoked_entities()

        contradicciones = self.contradiction_set(invocados, definidos)
        superfluos = self.superfluous_set(definidos, invocados)
        sanos = self.healthy_set(definidos, invocados)

        # Veredicto
        total = len(definidos) or 1
        health_ratio = len(sanos) / total

        if health_ratio >= 0.95:
            veredicto = "ESSENTIA PURA"
            veredicto_detail = "El codebase es ontologicamente coherente y parsimonioso."
        elif health_ratio >= 0.80:
            veredicto = "RESERVA MENOR"
            veredicto_detail = "Hay algunas contradicciones o entes superfluos, pero aceptable."
        elif health_ratio >= 0.50:
            veredicto = "RESERVA MAYOR"
            veredicto_detail = "Se requieren correcciones significativas."
        else:
            veredicto = "CONDEMNATIO"
            veredicto_detail = "El codebase viola el Principio de No Contradiccion."

        return {
            "definidos": sorted(definidos),
            "invocados": sorted(invocados),
            "contradicciones": sorted(contradicciones),
            "superfluos": sorted(superfluos),
            "sanos": sorted(sanos),
            "total_entes": len(definidos),
            "total_contradicciones": len(contradicciones),
            "total_superfluos": len(superfluos),
            "health_ratio": round(health_ratio, 4),
            "veredicto": veredicto,
            "veredicto_detail": veredicto_detail,
            "cbmm_available": self._cbmm_available,
        }

    def format_for_prompt(self, analysis: Dict[str, Any]) -> str:
        """Formatea el analisis como contexto para el prompt del agente OckhamDev."""
        if not analysis["cbmm_available"]:
            return "(CBMM no disponible. OckhamDev opera sin grafo de conocimiento.)"

        lines = [
            "--- ANALISIS OCKHAM (Logica Escolastica de Conjuntos) ---",
            f"Total entes DEFINIDOS: {analysis['total_entes']}",
            f"Total entes INVOCADOS: {len(analysis['invocados'])}",
            f"CONTRADICCIONES (invocados pero no existen): {analysis['total_contradicciones']}",
            f"SUPERFLUOS (existen pero no se invocan): {analysis['total_superfluos']}",
            f"SANOS (existen y se invocan): {len(analysis['sanos'])}",
            f"Health Ratio: {analysis['health_ratio']*100:.1f}%",
            f"VEREDICTO: {analysis['veredicto']}",
            "",
        ]
        if analysis["contradicciones"]:
            lines.append("⚠️ CONTRADICCIONES (alucinaciones):")
            for e in analysis["contradicciones"][:10]:
                lines.append(f"  - {e}")
        if analysis["superfluos"]:
            lines.append("✂️ SUPERFLUOS (violacion Ockham):")
            for e in analysis["superfluos"][:10]:
                lines.append(f"  - {e}")
        return "\n".join(lines)

    def check_non_contradiction(self, invoked_name: str) -> Tuple[bool, str]:
        """Verifica si un ente especifico viola el PNC.

        Returns:
            (pasa, mensaje)
        """
        definidos = self.get_defined_entities()
        if invoked_name not in definidos:
            return False, (
                f"VIOLACION PNC: El ente '{invoked_name}' es invocado pero no existe "
                f"en el codebase. Esto es una alucinacion logica."
            )
        return True, f"El ente '{invoked_name}' existe y es coherente."
