from __future__ import annotations

import json
import time
from typing import Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel

from concilio_salamanca.prompts.system_prompts import MAGISTER_DETERMINANS
from concilio_salamanca.schemas import (
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
        self.last_usage = {}
        self.last_latency_ms = 0.0
        self.last_model = "unknown"

    def judge(
        self,
        state: DebateState,
        pnc_validation: Optional[PnCValidation] = None,
        max_tokens: int = 0,
    ) -> str:
        from concilio_salamanca.debate.cave_protocol import encode
        from concilio_salamanca.debate.token_accountant import extract_usage

        # Sólo el último voto estructurado: nunca reenviar código ni rondas completas.
        arguments_text = "\n".join(
            f"{agent_name}:{output.compact or encode(output.structured)}"
            for agent_name, output in state.get("agent_outputs", {}).items()
        )

        pnc_text = ""
        if pnc_validation:
            pnc_text = f"""
VALIDACIÓN DEL PRINCIPIO DE NO CONTRADICCIÓN:
- Hay contradicciones: {pnc_validation.hay_contradicciones}
- Contradicciones detectadas: {json.dumps([c.model_dump() for c in pnc_validation.contradicciones], indent=2, ensure_ascii=False)}
- Resumen: {pnc_validation.resumen}
"""

        messages = [
            SystemMessage(
                content="Eres Magister técnico. Resuelve el ledger, el voto y el PnC. "
                "No inventes evidencia. Devuelve el JSON de determinatio requerido."
            ),
            HumanMessage(
                content=f"""LEDGER COMPRIMIDO:
{arguments_text}

VOTACION: {json.dumps(state.get('voting_summary', {}), ensure_ascii=False)}

{pnc_text}

FORMATO: {{"quaestio":"...","videtur":"...","sed_contra":"...","respondeo":"...","determinatio_codici":"...","veredicto_final":"CONDENA|ABSUELVE|RESERVA"}}"""
            ),
        ]
        llm = self.model.bind(max_tokens=max_tokens) if max_tokens > 0 and isinstance(self.model, BaseChatModel) else self.model
        started = time.time()
        response = llm.invoke(messages)
        self.last_latency_ms = (time.time() - started) * 1000
        self.last_usage = extract_usage(response)
        for attr in ("model_name", "model"):
            value = getattr(self.model, attr, None)
            if isinstance(value, str):
                self.last_model = value
                break
        content = getattr(response, "content", response)
        return content if isinstance(content, str) else str(content)

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
