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
    "premisa_mayor_tipo": "A|E|I|O",
    "premisa_menor": "Afirmacion tecnica particular sobre este codigo",
    "premisa_menor_tipo": "A|E|I|O",
    "conclusion": "Veredicto tecnico necesario deducido",
    "conclusion_tipo": "A|E|I|O"
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

    def _code_fingerprint(
        self, code: str, context: Optional[Dict[str, str]] = None
    ) -> str:
        ctx_hash = ""
        if context:
            ctx_sorted = "|".join(f"{k}:{v[:200]}" for k, v in sorted(context.items()))
            ctx_hash = hashlib.sha256(ctx_sorted.encode()).hexdigest()[:12]
        return hashlib.sha256(
            f"{self.role_name}|{code}|{ctx_hash}".encode()
        ).hexdigest()[:24]

    def _check_code_cache(
        self, code: str, context: Optional[Dict[str, str]] = None
    ) -> Optional[AgentOutput]:
        from concilio_salamanca.debate.syllogism_cache import get_syllogism_cache

        cache = get_syllogism_cache()
        fp = self._code_fingerprint(code, context)
        entry = cache.entries.get(f"code:{fp}")
        if entry and hasattr(entry, "conclusion_text"):
            structured = self._parse_response(entry.conclusion_text)
            cached = AgentOutput(
                raw=entry.conclusion_text,
                structured=structured
                if structured and "[Error" not in structured.fundamento
                else None,
                timestamp=time.time(),
            )
            return cached
        return None

    def _store_code_cache(
        self, code: str, output: AgentOutput, context: Optional[Dict[str, str]] = None
    ):
        from concilio_salamanca.debate.syllogism_cache import (
            get_syllogism_cache,
            CacheEntry,
            PropositionType,
            SyllogismPattern,
            SyllogismReducer,
        )

        cache = get_syllogism_cache()
        fp = self._code_fingerprint(code, context)

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

    async def reason_async(
        self,
        code: str,
        context: Optional[Dict[str, str]] = None,
        max_tokens: int = 0,
    ) -> AgentOutput:
        cached = self._check_code_cache(code, context)
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

        # Inject MCP Tools via bind_tools if supported
        from concilio_salamanca.debate.mcp_client import HAS_MCP

        llm = self.model
        if HAS_MCP:
            # Here we would bind actual LangChain wrappers of MCP tools
            pass

        response = await llm.ainvoke(messages)
        raw = response.content
        structured = self._parse_response(raw)
        output = AgentOutput(raw=raw, structured=structured, timestamp=ts)

        try:
            self._store_code_cache(code, output, context)
        except Exception:
            pass
        return output

    def reason(
        self,
        code: str,
        context: Optional[Dict[str, str]] = None,
        max_tokens: int = 0,
    ) -> AgentOutput:
        cached = self._check_code_cache(code, context)
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
            self._store_code_cache(code, output, context)
        except Exception:
            pass
        return output

    @staticmethod
    def _extract_json(raw: str) -> str:
        import re

        raw_stripped = raw.strip()
        if raw_stripped.startswith("{") and raw_stripped.endswith("}"):
            return raw_stripped
        match = re.search(r'\{\s*"agente".*?\}', raw, re.DOTALL)
        if match:
            return match.group(0)
        for marker in ("```json", "```"):
            if marker in raw:
                parts = raw.split(marker)
                if len(parts) > 1:
                    inner = parts[1].split("```")[0]
                    inner_match = re.search(r"\{.*\}", inner, re.DOTALL)
                    if inner_match:
                        return inner_match.group(0)
        return raw

    def _parse_response(self, raw: str) -> Optional[AgentVeredict]:
        try:
            json_str = self._extract_json(raw)
            data = json.loads(json_str)
            return AgentVeredict(
                agente=data.get("agente", self.role_name),
                rol=data.get("rol", self.role_name),
                silogismo=Silogismo(**data["silogismo"]),
                principio_no_contradiccion=data.get("principio_no_contradiccion", True),
                veredicto=Veredicto(data.get("veredicto", "RESERVA")),
                fundamento=data.get("fundamento", ""),
            )
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            import sys

            sys.stderr.write(
                f"\n[ADVERTENCIA] El agente '{self.role_name}' falló al parsear la respuesta JSON del LLM. Error: {str(e)[:100]}\n"
            )
            return AgentVeredict(
                agente=self.role_name,
                rol=self.role_name,
                silogismo=Silogismo(
                    premisa_mayor=f"[Error de parseo: {str(e)[:100]}]",
                    premisa_menor="[Error de parseo]",
                    conclusion="[Error de parseo]",
                ),
                principio_no_contradiccion=True,
                veredicto=Veredicto.RESERVA,
                fundamento=f"Error al parsear JSON de respuesta. LLM emitio formato invalido. Raw: {raw[:300]}",
            )

    @abstractmethod
    def act(
        self, code: str, context: Optional[Dict[str, str]] = None
    ) -> AgentOutput: ...


class AgentFromPrompt(AgenteBase):
    def __init__(self, role_name: str, system_prompt: str, model: BaseChatModel):
        self.role_name = role_name
        self.system_prompt = system_prompt
        super().__init__(model)

    def act(self, code: str, context: Optional[Dict[str, str]] = None) -> AgentOutput:
        return self.reason(code, context)

    async def act_async(
        self, code: str, context: Optional[Dict[str, str]] = None
    ) -> AgentOutput:
        return await self.reason_async(code, context)

    def attack(self, code: str) -> str:
        output = self.reason(code)
        return output.raw
