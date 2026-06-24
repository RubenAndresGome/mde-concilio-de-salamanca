from __future__ import annotations

import json
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from concilio_salamanca.schemas import AgentOutput, AgentVeredict, Silogismo, Veredicto


class AgenteBase(ABC):
    role_name: str
    system_prompt: str
    json_schema_instruction: str = """
FORMATO DE SALIDA OBLIGATORIO (JSON estricto, sin markdown ni texto adicional):
{{{{
  "agente": "{role_name}",
  "rol": "{role}",
  "silogismo": {{{{
    "premisa_mayor": "Premisa universal...",
    "premisa_menor": "Premisa particular...",
    "conclusion": "Conclusión necesaria deducida..."
  }}}},
  "principio_no_contradiccion": true,
  "veredicto": "CONDENA|ABSUELVE|RESERVA",
  "fundamento": "Razón del veredicto..."
}}}}
"""

    def __init__(self, model: ChatOpenAI):
        self.model = model

    def _build_messages(
        self, code: str, context: Optional[Dict[str, str]] = None
    ) -> List:
        schema = self.json_schema_instruction.format(
            role_name=self.role_name, role=self.role_name
        )
        system = SystemMessage(content=self.system_prompt + "\n\n" + schema)
        user_content = f"Analiza el siguiente código según tu rol de {self.role_name}:\n\n```\n{code}\n```"
        if context:
            user_content += "\n\n--- ARGUMENTOS DE OTROS AGENTES PARA REFUTACIÓN ---\n"
            for agente, argumento in context.items():
                user_content += f"\n### {agente}:\n{argumento}\n"
        return [system, HumanMessage(content=user_content)]

    def reason(
        self, code: str, context: Optional[Dict[str, str]] = None
    ) -> AgentOutput:
        messages = self._build_messages(code, context)
        ts = time.time()
        response = self.model.invoke(messages)
        raw = response.content
        structured = self._parse_response(raw)
        return AgentOutput(raw=raw, structured=structured, timestamp=ts)

    def _parse_response(self, raw: str) -> Optional[AgentVeredict]:
        try:
            json_str = raw.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
            data = json.loads(json_str)
            return AgentVeredict(
                agente=data.get("agente", self.role_name),
                rol=data.get("rol", self.role_name),
                silogismo=Silogismo(**data["silogismo"]),
                principio_no_contradiccion=data.get(
                    "principio_no_contradiccion", True
                ),
                veredicto=Veredicto(data.get("veredicto", "RESERVA")),
                fundamento=data.get("fundamento", ""),
            )
        except (json.JSONDecodeError, KeyError, TypeError):
            return AgentVeredict(
                agente=self.role_name,
                rol=self.role_name,
                silogismo=Silogismo(
                    premisa_mayor="[Error de parseo]",
                    premisa_menor="[Error de parseo]",
                    conclusion="[Error de parseo]",
                ),
                principio_no_contradiccion=True,
                veredicto=Veredicto.RESERVA,
                fundamento=f"Error al parsear la respuesta del modelo. Respuesta raw: {raw[:500]}",
            )

    @abstractmethod
    def act(self, code: str, context: Optional[Dict[str, str]] = None) -> AgentOutput:
        ...
