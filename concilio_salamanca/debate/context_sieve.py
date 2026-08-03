"""Tamiz de contexto reproducible previo a cualquier llamada LLM."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SiftedContext:
    code: str
    diagnostics: str
    omitted_chars: int


def sift_context(code: str, diagnostics: str = "", max_chars: int = 12_000) -> SiftedContext:
    if len(code) <= max_chars:
        return SiftedContext(code, diagnostics[:3000], 0)
    lines = code.splitlines()
    risk = re.compile(
        r"(TODO|FIXME|except|catch|eval\(|exec\(|subprocess|password|secret|SELECT|INSERT|DELETE|unsafe|panic|throw)",
        re.IGNORECASE,
    )
    selected = []
    seen = set()
    for index, line in enumerate(lines):
        if risk.search(line):
            for neighbor in range(max(0, index - 2), min(len(lines), index + 3)):
                if neighbor not in seen:
                    selected.append(f"L{neighbor + 1}:{lines[neighbor]}")
                    seen.add(neighbor)
    if not selected:
        selected = [f"L{i + 1}:{line}" for i, line in enumerate(lines[:200])]
    compact = "\n".join(selected)[:max_chars]
    return SiftedContext(compact, diagnostics[:3000], max(0, len(code) - len(compact)))
