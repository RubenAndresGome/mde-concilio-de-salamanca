"""Compresion simbolica determinista para el contexto entre agentes."""

from __future__ import annotations

import json
import math
import re
from typing import Mapping


def estimate_tokens(text: str) -> int:
    """Estimacion conservadora y sin dependencia de un tokenizer concreto."""
    return math.ceil(len(text) / 4)


def _json_object(raw: str) -> dict:
    candidate = raw.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", candidate, re.DOTALL)
    if fenced:
        candidate = fenced.group(1)
    try:
        value = json.loads(candidate)
        return value if isinstance(value, dict) else {}
    except (json.JSONDecodeError, TypeError):
        return {}


def compress_argument(raw: str, max_chars: int = 420) -> str:
    data = _json_object(raw) if isinstance(raw, str) else {}
    if data:
        syllogism = data.get("silogismo") or data.get("S") or {}
        pieces = [f"V={data.get('veredicto', data.get('V', 'RESERVA'))}"]
        for key, prefix in (
            ("premisa_mayor", "PM"),
            ("premisa_menor", "Pm"),
            ("conclusion", "C"),
        ):
            alias = {"premisa_mayor": "PM", "premisa_menor": "Pm", "conclusion": "C"}[key]
            value = str(syllogism.get(key, syllogism.get(alias, ""))).strip()
            if value:
                pieces.append(f"{prefix}={value}")
        foundation = str(data.get("fundamento", data.get("E", ""))).strip()
        if foundation:
            pieces.append(f"F={foundation}")
        questions = data.get("preguntas_casuisticas") or data.get("Q") or []
        if questions:
            pieces.append(f"Q={str(questions[0]).strip()}")
        compact = " | ".join(pieces)
    else:
        compact = " ".join(str(raw).split())
    if len(compact) <= max_chars:
        return compact
    head = max_chars * 3 // 4
    tail = max_chars - head - 5
    return compact[:head].rstrip() + " … " + compact[-tail:].lstrip()


def compress_context(
    arguments: Mapping[str, str], exclude: str = "", budget_chars: int = 2400
) -> dict[str, str]:
    """Un argumento final por agente, deduplicado y dentro de presupuesto."""
    result: dict[str, str] = {}
    seen: set[str] = set()
    remaining = max(256, int(budget_chars))
    for agent, raw in reversed(list(arguments.items())):
        if agent == exclude:
            continue
        compact = compress_argument(raw)
        signature = re.sub(r"\s+", " ", compact.lower())
        if signature in seen:
            continue
        seen.add(signature)
        allowance = remaining - len(agent) - 8
        if allowance < 80:
            break
        compact = compact[:allowance]
        result[agent] = compact
        remaining -= len(agent) + len(compact) + 8
    return dict(reversed(list(result.items())))


def compact_section(text: str, max_chars: int) -> str:
    normalized = "\n".join(line.rstrip() for line in str(text).splitlines() if line.strip())
    if len(normalized) <= max_chars:
        return normalized
    marker = "\n…[contexto acotado]…\n"
    head = (max_chars - len(marker)) * 2 // 3
    tail = max_chars - len(marker) - head
    return normalized[:head] + marker + normalized[-tail:]
