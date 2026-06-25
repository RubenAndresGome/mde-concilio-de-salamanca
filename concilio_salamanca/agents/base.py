from __future__ import annotations

import hashlib
import json
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.language_models import BaseChatModel

from concilio_salamanca.schemas import AgentOutput, AgentVeredict, Silogismo, Veredicto


class AgenteBase(ABC):
    role_name: str
    system_prompt: str
    json_schema_instruction: str = """
ERES UN DESARROLLADOR DE SOFTWARE QUE RAZONA CON METODO FILOSOFICO.
Tu output es un veredicto tecnico sobre codigo, no un ensayo filosofico.
Las premisas de tus silogismos deben ser afirmaciones tecnicas comprobables sobre el codigo.

FORMATO DE SALIDA OBLIGATORIO (JSON estricto, sin markdown ni texto adicional):
{{{{
  "agente": "{role_name}",
  "rol": "{role}",
  "silogismo": {{{{
    "premisa_mayor": "Afirmacion tecnica universal (ej: Todo codigo que...)",
    "premisa_menor": "Afirmacion tecnica particular sobre este codigo",
    "conclusion": "Veredicto tecnico necesario deducido"
  }}}},
  "principio_no_contradiccion": true,
  "veredicto": "CONDENA|ABSUELVE|RESERVA",
  "fundamento": "Razon tecnica del veredicto",
  "anti_patron_id": "AP-XXX o null"
}}}}
"""

    def __init__(self, model: BaseChatModel):
        self.model = model

    def _build_messages(
        self, code: str, context: Optional[Dict[str, str]] = None
    ) -> List:
        schema = self.json_schema_instruction.format(
            role_name=self.role_name, role=self.role_name
        )
        system = SystemMessage(content=self.system_prompt + "\n\n" + schema)
        user_content = f"Analiza el siguiente codigo segun tu rol de {self.role_name}:\n\n```\n{code}\n```"
        if context:
            user_content += "\n\n--- ARGUMENTOS DE OTROS AGENTES PARA REFUTACION ---\n"
            for agente, argumento in context.items():
                user_content += f"\n### {agente}:\n{argumento}\n"
        return [system, HumanMessage(content=user_content)]

    def _code_fingerprint(self, code: str) -> str:
        return hashlib.sha256(
            f"{self.role_name}|{code}".encode()
        ).hexdigest()[:24]

    def _check_code_cache(self, code: str) -> Optional[AgentOutput]:
        from concilio_salamanca.debate.syllogism_cache import get_syllogism_cache
        cache = get_syllogism_cache()
        fp = self._code_fingerprint(code)
        entry = cache.entries.get(f"code:{fp}")
        if entry and hasattr(entry, 'conclusion_text'):
            structured = self._parse_response(entry.conclusion_text)
            cached = AgentOutput(
                raw=entry.conclusion_text,
                structured=structured,
                timestamp=time.time(),
            )
            return cached
        return None

    def _store_code_cache(self, code: str, output: AgentOutput):
        from concilio_salamanca.debate.syllogism_cache import (
            get_syllogism_cache,
            CacheEntry,
            PropositionType,
            SyllogismPattern,
            SyllogismReducer,
        )

        cache = get_syllogism_cache()
        fp = self._code_fingerprint(code)

        pattern = SyllogismPattern(
            major_type=PropositionType.A,
            minor_type=PropositionType.A,
            conclusion_type=PropositionType.A,
            figure=1,
            subject="",
            predicate="",
            middle="",
        )

        entry = CacheEntry(
            fingerprint=f"code:{fp}",
            pattern=pattern,
            set_relation="",
            conclusion_text=output.raw,
            agent=self.role_name,
            timestamp=time.time(),
        )
        cache.entries[f"code:{fp}"] = entry

        if output.structured:
            sil_pattern = SyllogismReducer.extract_from_json(
                output.structured.model_dump()
            )
            if sil_pattern:
                unified = SyllogismReducer.reduce_all(sil_pattern)
                compressed = SyllogismReducer.format_memory_compressed(unified)
                sil_entry = CacheEntry(
                    fingerprint=sil_pattern.fingerprint(),
                    pattern=sil_pattern,
                    set_relation=compressed,
                    conclusion_text=output.raw[:2000],
                    agent=self.role_name,
                    timestamp=time.time(),
                )
                cache.entries[sil_pattern.fingerprint()] = sil_entry
                cache.unified_store[unified.key] = unified

        cache.save()

    def reason(
        self, code: str, context: Optional[Dict[str, str]] = None,
        max_tokens: int = 0,
    ) -> AgentOutput:
        cached = self._check_code_cache(code)
        if cached:
            return cached

        messages = self._build_messages(code, context)

        if max_tokens > 0:
            budget_instruction = (
                f"RESTRICCION DE TOKENS: Tu respuesta no debe exceder aproximadamente "
                f"{max_tokens} tokens (~{max_tokens // 4} palabras). "
                f"Se conciso. Elimina toda palabra innecesaria. Ve directo a la conclusion."
            )
            messages[0] = SystemMessage(
                content=messages[0].content + "\n\n" + budget_instruction
            )

        ts = time.time()
        response = self.model.invoke(messages)
        raw = response.content
        structured = self._parse_response(raw)
        output = AgentOutput(raw=raw, structured=structured, timestamp=ts)

        try:
            self._store_code_cache(code, output)
        except Exception:
            pass
        return output

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
