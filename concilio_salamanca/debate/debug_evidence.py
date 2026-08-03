"""Reduce una reproducción a evidencia mínima verificable."""

from __future__ import annotations


def compact_debug_evidence(error: str, traceback: str = "", hypotheses: list[str] | None = None) -> dict:
    lines = [line.rstrip() for line in str(traceback).splitlines() if line.strip()]
    frames = [line for line in lines if "File " in line or line.lstrip().startswith("at ")][-5:]
    tail = lines[-2:] if lines else []
    return {
        "error": " ".join(str(error).split())[:500],
        "trace": frames + [line for line in tail if line not in frames],
        "hypotheses": [" ".join(value.split())[:240] for value in (hypotheses or [])[:3]],
        "contract": "reproducir -> aislar -> verificar; no enviar logs completos",
    }

