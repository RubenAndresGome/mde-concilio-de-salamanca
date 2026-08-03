"""Colegio electoral contextual del Concilio.

Cada agente conserva un solo voto (el de su ultima ronda). Su peso depende de
competencia contextual y calidad formal, nunca del numero de mensajes emitidos.
"""

from __future__ import annotations

import json
import re
import unicodedata
from typing import Any


VERDICTS = ("CONDENA", "ABSUELVE", "RESERVA")
EXPERTISE = {
    "seguridad": {"security", "backend"},
    "pentest": {"security"},
    "red team": {"security"},
    "abuser": {"security", "ux"},
    "datos": {"data", "database"},
    "mlops": {"ai", "ops"},
    "dl": {"ai", "data"},
    "iot": {"embedded", "performance"},
    "sistemas": {"ops", "performance"},
    "linus": {"performance", "systems"},
    "thompson": {"systems", "security"},
    "wozniak": {"embedded", "systems"},
    "korotkevich": {"algorithm", "performance"},
    "delineationis": {"frontend", "ux"},
    "arquimedes": {"architecture", "quality"},
    "processus": {"quality", "process"},
    "six sigma": {"quality", "process"},
    "scrum": {"process"},
    "ockham": {"logic", "architecture"},
    "leibniz": {"logic", "architecture"},
    "socrates": {"logic", "requirements"},
    "vitoria": {"ethics", "requirements"},
    "stallman": {"ethics", "security"},
    "promotor": {"security", "quality"},
    "defensor": {"reliability", "requirements"},
    "doctor": {"logic", "architecture"},
}


def _plain(value: str) -> str:
    text = unicodedata.normalize("NFKD", value.lower())
    return "".join(char for char in text if not unicodedata.combining(char))


def infer_domains(state: dict) -> set[str]:
    text = _plain(
        " ".join(
            str(state.get(key, ""))
            for key in ("language", "code", "static_analysis")
        )
    )
    rules = {
        "security": ("auth", "token", "password", "secret", "crypto", "xss", "sql injection"),
        "database": ("sqlite", "postgres", "database", "select ", "insert ", "sql"),
        "data": ("dataframe", "dataset", "pandas", "etl"),
        "ai": ("model", "llm", "torch", "tensorflow", "embedding"),
        "frontend": ("react", "html", "css", "dom", "browser"),
        "ux": ("accessibility", "aria", "responsive", "ui"),
        "ops": ("docker", "kubernetes", "deploy", "pipeline", "ci/cd"),
        "embedded": ("firmware", "sensor", "arduino", "microcontroller"),
        "algorithm": ("complexity", "algorithm", "recursive", "sort"),
        "performance": ("latency", "memory", "performance", "cache", "async"),
        "requirements": ("requirement", "user order", "dogma", "contradiction"),
        "architecture": ("class ", "module", "dependency", "interface"),
        "quality": ("test", "bug", "exception", "error"),
    }
    domains = {domain for domain, terms in rules.items() if any(term in text for term in terms)}
    return domains or {"quality"}


def _verdict(raw: Any, structured: Any = None) -> tuple[str, bool, bool]:
    if structured is not None:
        verdict = getattr(structured, "veredicto", None)
        value = getattr(verdict, "value", verdict)
        if value in VERDICTS:
            pnc = bool(getattr(structured, "principio_no_contradiccion", True))
            return str(value), True, pnc

    text = str(raw or "")
    candidate = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", candidate, re.DOTALL)
    if fenced:
        candidate = fenced.group(1)
    try:
        data = json.loads(candidate)
        value = str(data.get("veredicto", data.get("V", ""))).upper()
        if value in VERDICTS:
            return value, bool(data.get("silogismo") or data.get("S")), bool(
                data.get("principio_no_contradiccion", data.get("N", True))
            )
    except (json.JSONDecodeError, AttributeError, TypeError):
        pass

    matches = re.findall(r"\b(CONDENA|ABSUELVE|RESERVA)\b", text.upper())
    return (matches[-1] if matches else "RESERVA"), False, True


def _agent_expertise(name: str) -> set[str]:
    normalized = _plain(name)
    domains: set[str] = set()
    for marker, values in EXPERTISE.items():
        if marker in normalized:
            domains.update(values)
    return domains


def build_voting_table(result: dict, consensus_threshold: float = 0.67) -> dict:
    state = result.get("state", {})
    history = state.get("arguments_history", [])
    latest: dict[str, Any] = {}
    for round_data in history:
        latest.update(round_data.get("arguments", {}))

    outputs = state.get("agent_outputs", {})
    domains = infer_domains(state)
    counts = {verdict: 0 for verdict in VERDICTS}
    weighted = {verdict: 0.0 for verdict in VERDICTS}
    agent_votes = []

    for name, raw in latest.items():
        output = outputs.get(name)
        structured = getattr(output, "structured", None)
        raw_value = getattr(output, "raw", raw)
        verdict, formal, respects_pnc = _verdict(raw_value, structured)
        expertise = _agent_expertise(name)
        matches = sorted(domains & expertise)
        competence = min(1.5, 0.5 * len(matches))
        formal_factor = 1.15 if formal else 0.85
        pnc_factor = 1.0 if respects_pnc else 0.5
        reserve_factor = 0.8 if verdict == "RESERVA" else 1.0
        weight = round((1.0 + competence) * formal_factor * pnc_factor * reserve_factor, 3)

        counts[verdict] += 1
        weighted[verdict] += weight
        agent_votes.append(
            {
                "agente": name,
                "veredicto": verdict,
                "peso": weight,
                "competencias_contextuales": matches,
                "silogismo_estructurado": formal,
                "respeta_pnc": respects_pnc,
            }
        )

    weighted = {key: round(value, 3) for key, value in weighted.items()}
    total_weight = round(sum(weighted.values()), 3)
    majority = max(VERDICTS, key=lambda key: (weighted[key], counts[key], -VERDICTS.index(key)))
    share = weighted[majority] / total_weight if total_weight else 0.0
    return {
        "votos": counts,
        "votos_ponderados": weighted,
        "agentes": agent_votes,
        "contexto": sorted(domains),
        "formula": "peso=(1+competencia_contextual)*calidad_silogismo*PnC*reserva",
        "consenso": bool(total_weight and share >= consensus_threshold),
        "mayoria": majority,
        "cuota_mayoria": round(share, 4),
        "umbral_consenso": consensus_threshold,
        "total": sum(counts.values()),
        "total_ponderado": total_weight,
    }
