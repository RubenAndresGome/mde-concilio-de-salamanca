from __future__ import annotations

import json
from typing import Dict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel

from concilio_salamanca.schemas import (
    AgentOutput,
    Contradiccion,
    PnCValidation,
)
from concilio_salamanca.debate.formal_verification import FormalVerifier

PNC_SYSTEM_PROMPT = """# VALIDADOR DEL PRINCIPIO DE NO CONTRADICCIÓN

Eres el Validador Lógico del Concilio de Salamanca. Tu única función es detectar contradicciones formales entre los argumentos de los agentes, aplicando estrictamente el Principio de No Contradicción aristotélico: "Es imposible que lo mismo se dé y no se dé en lo mismo a la vez y bajo el mismo aspecto."

**Reglas:**
1. Una contradicción existe cuando dos agentes afirman proposiciones lógicamente incompatibles sobre el mismo hecho del código.
2. No señales como contradicción diferencias de énfasis, perspectiva o valoración subjetiva.
3. Debes identificar EXACTAMENTE qué proposición de cada agente entra en conflicto.
4. Si no hay contradicciones reales, decláralo explícitamente.

FORMATO DE SALIDA OBLIGATORIO (JSON):
{
  "hay_contradicciones": true/false,
  "contradicciones": [
    {
      "agente_a": "Nombre del agente A",
      "agente_b": "Nombre del agente B",
      "proposicion_a": "Texto exacto de la proposición del agente A",
      "proposicion_b": "Texto exacto de la proposición del agente B",
      "descripcion": "Por qué son lógicamente incompatibles"
    }
  ],
  "resumen": "Resumen del análisis de consistencia lógica"
}
"""


class ValidadorPNC:
    def __init__(self, model: BaseChatModel):
        self.model = model
        self.formal_verifier = FormalVerifier(model)

    def validate(self, agent_outputs: Dict[str, AgentOutput]) -> PnCValidation:
        agent_texts = {
            nombre: (output.raw if hasattr(output, "raw") else str(output))
            for nombre, output in agent_outputs.items()
        }

        # 1. Fallback / traditional semantic validation
        arguments_text = ""
        for nombre, text in agent_texts.items():
            arguments_text += f"\n\n===== {nombre} =====\n{text}"

        messages = [
            SystemMessage(content=PNC_SYSTEM_PROMPT),
            HumanMessage(
                content=f"Analiza los siguientes argumentos de los agentes del Concilio y detecta cualquier violación del Principio de No Contradicción:\n\n{arguments_text}"
            ),
        ]

        response = self.model.invoke(messages)
        semantic_validation = self._parse(response.content)

        # 2. Formal Z3 Validation (Phase 3 addition)
        z3_result = self.formal_verifier.check_pnc(agent_texts)

        # Merge results
        if semantic_validation.hay_contradicciones:
            semantic_validation.resumen += f"\n\n[Z3 Formal Check]: Satisfiable? {z3_result.is_satisfiable}. Model: {z3_result.model}"

        return semantic_validation

    def _parse(self, raw: str) -> PnCValidation:
        try:
            json_str = raw.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            data = json.loads(json_str)
            return PnCValidation(
                hay_contradicciones=data.get("hay_contradicciones", False),
                contradicciones=[
                    Contradiccion(**c) for c in data.get("contradicciones", [])
                ],
                resumen=data.get("resumen", ""),
                principio_violado=data.get("hay_contradicciones", False),
            )
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            return PnCValidation(
                hay_contradicciones=False,
                contradicciones=[],
                resumen=f"Error al analizar contradicciones: {str(e)}",
                principio_violado=False,
            )
