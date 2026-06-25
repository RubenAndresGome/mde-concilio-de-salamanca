"""
Sistema de Precedentes (Stare Decisis del Concilio).
Almacena los silogismos mas solidos de debates pasados y los recupera
como contexto para debates futuros. Los agentes reciben precedentes relevantes
para fundamentar o refutar sus argumentos.

Indice: TF-IDF ligero sobre los terminos S, P, M de cada silogismo.
"""

from __future__ import annotations

import json
import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from concilio_salamanca.debate.syllogism_cache import SyllogismReducer, SyllogismPattern, UnifiedSyllogism


@dataclass
class Precedent:
    fingerprint: str
    terms: Dict[str, str]
    mode: str
    conclusion_text: str
    veredicto: str
    agent: str
    timestamp: float
    code_snippet: str
    weight: float = 1.0


class PrecedentEngine:
    def __init__(self, path: Optional[str] = None):
        if path is None:
            path = str(Path(__file__).parent / "precedents.json")
        self.path = Path(path)
        self.precedents: List[Precedent] = []
        self._term_index: Dict[str, List[int]] = defaultdict(list)
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding="utf-8"))
                for p in data:
                    prec = Precedent(**p)
                    self.precedents.append(prec)
                    for term_key, term_val in prec.terms.items():
                        self._term_index[term_val.lower()].append(len(self.precedents) - 1)
            except (json.JSONDecodeError, TypeError):
                pass

    def save(self):
        data = [p.__dict__ for p in self.precedents]
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def add(self, unified: UnifiedSyllogism, veredicto: str, agent: str, code_snippet: str = ""):
        prec = Precedent(
            fingerprint=unified.key,
            terms=unified.terms,
            mode=unified.mode_name,
            conclusion_text=unified.set_theory.conclusion_equation,
            veredicto=veredicto,
            agent=agent,
            timestamp=time.time(),
            code_snippet=code_snippet[:500],
        )
        idx = len(self.precedents)
        self.precedents.append(prec)
        for term_val in unified.terms.values():
            self._term_index[term_val.lower()].append(idx)
        self.save()

    def search(self, query_terms: List[str], max_results: int = 5) -> List[Precedent]:
        scores = defaultdict(float)

        for term in query_terms:
            term_lower = term.lower()
            for idx in self._term_index.get(term_lower, []):
                scores[idx] += 1.0

            for stored_term, indices in self._term_index.items():
                if term_lower in stored_term or stored_term in term_lower:
                    for idx in indices:
                        scores[idx] += 0.5

        ranked = sorted(scores.items(), key=lambda x: -x[1])[:max_results]
        results = []
        for idx, score in ranked:
            if score > 0.3:
                prec = self.precedents[idx]
                prec.weight = score
                results.append(prec)

        return results

    def format_context(self, query_terms: List[str], max_results: int = 3) -> str:
        results = self.search(query_terms, max_results)
        if not results:
            return ""

        lines = ["--- PRECEDENTES DEL CONCILIO (jurisprudencia) ---"]
        for i, p in enumerate(results, 1):
            lines.append(f"{i}. [{p.mode}] {p.agent} => {p.veredicto}")
            lines.append(f"   Conclusion: {p.conclusion_text}")
            if p.code_snippet:
                snippet = p.code_snippet[:120].replace("\n", " ")
                lines.append(f"   Codigo similar: ...{snippet}...")
        lines.append("")
        return "\n".join(lines)

    def stats(self) -> str:
        if not self.precedents:
            return "Sin precedentes almacenados."
        recent = [p for p in self.precedents if time.time() - p.timestamp < 86400 * 30]
        veredictos = defaultdict(int)
        for p in self.precedents:
            veredictos[p.veredicto] += 1
        total = len(self.precedents)
        return (
            f"Precedentes: {total} total | {len(recent)} ultimos 30 dias | "
            f"Condenas: {veredictos.get('CONDENA', 0)} | "
            f"Absueltos: {veredictos.get('ABSUELVE', 0)} | "
            f"Reservas: {veredictos.get('RESERVA', 0)}"
        )

    def add_precedent_from_result(self, result: dict):
        determinatio = result.get("determinatio")
        state = result.get("state", {})
        history = state.get("arguments_history", [])
        if not determinatio or not history:
            return
        last = history[-1].get("arguments", {})
        code = state.get("code", "")[:500]
        for agent_name, raw in last.items():
            try:
                data = json.loads(raw) if isinstance(raw, str) and raw.strip().startswith("{") else {"silogismo": {}, "veredicto": "RESERVA"}
                if data.get("silogismo"):
                    pattern = SyllogismReducer.extract_from_json(data)
                    if pattern:
                        unified = SyllogismReducer.reduce_all(pattern)
                        self.add(unified, data.get("veredicto", "RESERVA"),
                                 agent_name, code)
            except Exception:
                pass


_engine: Optional[PrecedentEngine] = None


def get_precedent_engine() -> PrecedentEngine:
    global _engine
    if _engine is None:
        _engine = PrecedentEngine()
    return _engine
