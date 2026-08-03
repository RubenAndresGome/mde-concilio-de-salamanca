"""Protocolo compacto interno; nunca se presenta como interfaz al usuario."""

from __future__ import annotations

from typing import Optional

from concilio_salamanca.schemas import AgentVeredict


def encode(veredict: Optional[AgentVeredict]) -> str:
    if veredict is None:
        return "A:?|D:?|V:RESERVA|PM:?|Pm:?|C:?|E:?|Q:"
    s = veredict.silogismo

    def clean(value) -> str:
        return " ".join(str(value).replace("|", "/").split())

    questions = ";".join(clean(q) for q in veredict.preguntas_casuisticas[:3])
    return (
        f"A:{clean(veredict.agente)}|D:{clean(veredict.rol)}|V:{veredict.veredicto.value}"
        f"|PM:{clean(s.premisa_mayor)}|Pm:{clean(s.premisa_menor)}"
        f"|C:{clean(s.conclusion)}|E:{clean(veredict.fundamento)}|Q:{questions}"
    )
