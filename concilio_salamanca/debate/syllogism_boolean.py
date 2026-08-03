"""Validación determinista mínima de contradicciones entre veredictos."""

from __future__ import annotations

from typing import Dict

from concilio_salamanca.schemas import AgentOutput, Contradiccion, PnCValidation, Veredicto


def validate_boolean_pnc(outputs: Dict[str, AgentOutput]) -> PnCValidation:
    convictions = []
    acquittals = []
    explicit_pnc = []
    for name, output in outputs.items():
        verdict = output.structured
        if verdict is None:
            continue
        if not verdict.principio_no_contradiccion:
            explicit_pnc.append(name)
        if verdict.veredicto == Veredicto.CONDENA:
            convictions.append((name, verdict.silogismo.conclusion))
        elif verdict.veredicto == Veredicto.ABSUELVE:
            acquittals.append((name, verdict.silogismo.conclusion))
    contradictions = []
    if convictions and acquittals:
        a, pa = convictions[0]
        b, pb = acquittals[0]
        contradictions.append(Contradiccion(
            agente_a=a, agente_b=b, proposicion_a=pa, proposicion_b=pb,
            descripcion="Veredictos opuestos sobre el mismo objeto auditado; requiere distinguir contexto o autoridad.",
        ))
    for name in explicit_pnc:
        contradictions.append(Contradiccion(
            agente_a=name, agente_b=name, proposicion_a="PnC=true", proposicion_b="PnC=false",
            descripcion="El propio agente declaró no respetar el Principio de No Contradicción.",
        ))
    return PnCValidation(
        hay_contradicciones=bool(contradictions),
        contradicciones=contradictions,
        resumen=("Contradicción determinista detectada." if contradictions else "Sin contradicción booleana observable."),
        principio_violado=bool(contradictions),
    )

