from __future__ import annotations

import json
import time
from typing import Dict, List, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel

from concilio_salamanca.prompts.system_prompts import MAGISTER_DETERMINANS
from concilio_salamanca.schemas import (
    AgentOutput,
    DebateState,
    Determinatio,
    PnCValidation,
    Veredicto,
)


class MagisterDeterminans:
    role_name = "Magister Determinans"
    system_prompt = MAGISTER_DETERMINANS

    def __init__(self, model: BaseChatModel):
        self.model = model

    def judge(
        self,
        state: DebateState,
        pnc_validation: Optional[PnCValidation] = None,
    ) -> str:
        code = state.get("code", "")
        history = state.get("arguments_history", [])

        arguments_text = ""

        if history:
            last_round = history[-1].get("arguments", {})
            for agent_name, raw_content in last_round.items():
                content = raw_content if isinstance(raw_content, str) else str(raw_content)
                arguments_text += f"\n\n===== {agent_name} =====\n{content[:3000]}"
        else:
            for key in ["promotor", "defensor", "doctor", "larouche", "leon_xiii",
                         "linus", "wozniak", "stallman", "stroustrup", "thompson",
                         "korotkevich", "auditor_dl", "seguridad", "mlops", "datos",
                         "sistemas", "iot", "socrates", "scrum", "sixsigma",
                         "llull", "bacon", "vitoria", "ratio",
                         "ponytail", "graphify", "rtk", "telemetry"]:
                output = state.get(key)
                if output:
                    content = output.raw if hasattr(output, "raw") else str(output)
                    arguments_text += f"\n\n===== {key} =====\n{content[:3000]}"

        pnc_text = ""
        if pnc_validation:
            pnc_text = f"""
VALIDACIÓN DEL PRINCIPIO DE NO CONTRADICCIÓN:
- Hay contradicciones: {pnc_validation.hay_contradicciones}
- Contradicciones detectadas: {json.dumps([c.model_dump() for c in pnc_validation.contradicciones], indent=2, ensure_ascii=False)}
- Resumen: {pnc_validation.resumen}
"""

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(
                content=f"""CÓDIGO BAJO JUICIO:
```
{code}
```

ARGUMENTOS DE LOS AGENTES DEL CONCILIO:
{arguments_text}

{pnc_text}

Emite tu DETERMINATIO final en el formato JSON requerido."""
            ),
        ]

        response = self.model.invoke(messages)
        return response.content

    def parse_determinatio(self, raw: str) -> Determinatio:
        try:
            json_str = raw.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            data = json.loads(json_str)
            return Determinatio(
                quaestio=data.get("quaestio", ""),
                videtur=data.get("videtur", ""),
                sed_contra=data.get("sed_contra", ""),
                respondeo=data.get("respondeo", ""),
                determinatio_codici=data.get(
                    "determinatio_codici",
                    data.get("codigo_corregido", "No se requiere corrección."),
                ),
                veredicto_final=Veredicto(data.get("veredicto_final", "RESERVA")),
            )
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            return Determinatio(
                quaestio="[Error de parseo del fallo]",
                videtur="",
                sed_contra="",
                respondeo=f"Error: {str(e)}",
                determinatio_codici=raw[:2000],
                veredicto_final=Veredicto.RESERVA,
            )
