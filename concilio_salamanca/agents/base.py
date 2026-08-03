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
    common_system_prompt: str = (
        "Audita codigo con evidencia verificable. Respeta el Dogma y el PnC. "
        "No inventes archivos ni ejecuciones. RESERVA si falta evidencia. "
        "Devuelve JSON estricto, sin markdown. Esquema compacto: "
        '{"A":"agente","D":"rol","S":{"PM":"premisa mayor","Pm":"premisa menor",'
        '"C":"conclusion"},"N":true,"V":"CONDENA|ABSUELVE|RESERVA",'
        '"E":"fundamento","Q":["preguntas breves"]}.'
    )

    def __init__(self, model: BaseChatModel):
        self.model = model

    def _build_messages(
        self, code: str, context: Optional[Dict[str, str]] = None
    ) -> List:
        system = SystemMessage(content=self.common_system_prompt)
        # El prefijo hasta el cierre del código es idéntico entre electores.
        user_content = f"DOGMA: auditar el objeto dado con el mínimo contexto suficiente.\nCODIGO:\n```\n{code}\n```"
        if context:
            user_content += "\nLEDGER PREVIO:\n" + "\n".join(
                f"{agente}:{argumento}" for agente, argumento in sorted(context.items())
            )
        user_content += (
            f"\nROLE:{self.role_name}\nCONTRATO DEL ROL:\n{self.system_prompt}\n"
            "Responde con el esquema compacto. Máximo tres preguntas, sólo si cambian la decisión."
        )
        return [system, HumanMessage(content=user_content)]

    def _model_name(self) -> str:
        for attr in ("model_name", "model"):
            value = getattr(self.model, attr, None)
            if isinstance(value, str):
                return value
        return "unknown"

    def _bounded_model(self, max_tokens: int):
        if max_tokens > 0 and isinstance(self.model, BaseChatModel):
            return self.model.bind(max_tokens=max_tokens)
        return self.model

    @staticmethod
    def _response_text(response) -> str:
        content = getattr(response, "content", response)
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "".join(
                str(item.get("text", "")) if isinstance(item, dict) else str(item)
                for item in content
            )
        return str(content)

    def _code_fingerprint(
        self, code: str, context: Optional[Dict[str, str]] = None
    ) -> str:
        ctx_hash = ""
        if context:
            ctx_sorted = "|".join(f"{k}:{v[:200]}" for k, v in sorted(context.items()))
            ctx_hash = hashlib.sha256(ctx_sorted.encode()).hexdigest()[:12]
        return hashlib.sha256(
            f"{self._model_name()}|{self.role_name}|{code}|{ctx_hash}".encode()
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
                compact="",
                cached=True,
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

        # Headroom context compression integration
        import os
        if os.environ.get("HEADROOM_ENABLED", "false").lower() == "true":
            try:
                from headroom import compress
                from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
                headroom_msgs = [{"role": "system" if m.type == "system" else ("user" if m.type == "human" else "assistant"), "content": m.content} for m in messages]
                compressed_msgs = compress(headroom_msgs)
                messages = [
                    SystemMessage(content=m["content"]) if m["role"] == "system" else
                    (HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"]))
                    for m in compressed_msgs
                ]
            except Exception as e:
                import sys
                sys.stderr.write(f"\n[ADVERTENCIA] Fallo compresion de Headroom: {e}\n")

        ts = time.time()

        # Inject MCP Tools via bind_tools if supported
        from concilio_salamanca.debate.mcp_client import HAS_MCP

        llm = self._bounded_model(max_tokens)
        if HAS_MCP:
            # Here we would bind actual LangChain wrappers of MCP tools
            pass

        response = await llm.ainvoke(messages)
        latency_ms = (time.time() - ts) * 1000
        raw = self._response_text(response)
        structured = self._parse_response(raw)
        from concilio_salamanca.debate.cave_protocol import encode
        from concilio_salamanca.debate.token_accountant import extract_usage

        parse_error = structured is None or structured.fundamento.startswith("Error al parsear")
        output = AgentOutput(
            raw=raw, structured=structured, timestamp=ts, compact=encode(structured),
            usage=extract_usage(response), model=self._model_name(), latency_ms=latency_ms,
            parse_error=parse_error,
        )

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

        # Headroom context compression integration
        import os
        if os.environ.get("HEADROOM_ENABLED", "false").lower() == "true":
            try:
                from headroom import compress
                from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
                headroom_msgs = [{"role": "system" if m.type == "system" else ("user" if m.type == "human" else "assistant"), "content": m.content} for m in messages]
                compressed_msgs = compress(headroom_msgs)
                messages = [
                    SystemMessage(content=m["content"]) if m["role"] == "system" else
                    (HumanMessage(content=m["content"]) if m["role"] == "user" else AIMessage(content=m["content"]))
                    for m in compressed_msgs
                ]
            except Exception as e:
                import sys
                sys.stderr.write(f"\n[ADVERTENCIA] Fallo compresion de Headroom: {e}\n")

        ts = time.time()
        response = self._bounded_model(max_tokens).invoke(messages)
        latency_ms = (time.time() - ts) * 1000
        raw = self._response_text(response)
        structured = self._parse_response(raw)
        from concilio_salamanca.debate.cave_protocol import encode
        from concilio_salamanca.debate.token_accountant import extract_usage

        parse_error = structured is None or structured.fundamento.startswith("Error al parsear")
        output = AgentOutput(
            raw=raw, structured=structured, timestamp=ts, compact=encode(structured),
            usage=extract_usage(response), model=self._model_name(), latency_ms=latency_ms,
            parse_error=parse_error,
        )

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
            raw_questions = data.get("preguntas_casuisticas", data.get("Q", []))
            if not isinstance(raw_questions, list):
                raw_questions = []
            return AgentVeredict(
                agente=data.get("agente", data.get("A", self.role_name)),
                rol=data.get("rol", data.get("D", self.role_name)),
                silogismo=self._parse_syllogism(data),
                principio_no_contradiccion=data.get("principio_no_contradiccion", data.get("N", True)),
                veredicto=Veredicto(data.get("veredicto", data.get("V", "RESERVA"))),
                fundamento=data.get("fundamento", data.get("E", "")),
                preguntas_casuisticas=[
                    str(question)[:300]
                    for question in raw_questions[:3]
                    if str(question).strip()
                ],
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

    @staticmethod
    def _parse_syllogism(data: dict) -> Silogismo:
        if "silogismo" in data:
            return Silogismo(**data["silogismo"])
        compact = data["S"]
        return Silogismo(
            premisa_mayor=compact["PM"],
            premisa_menor=compact["Pm"],
            conclusion=compact["C"],
        )

    @abstractmethod
    def act(
        self, code: str, context: Optional[Dict[str, str]] = None, max_tokens: int = 0
    ) -> AgentOutput: ...


class AgentFromPrompt(AgenteBase):
    def __init__(self, role_name: str, system_prompt: str, model: BaseChatModel):
        self.role_name = role_name
        self.system_prompt = system_prompt
        super().__init__(model)

    def act(
        self, code: str, context: Optional[Dict[str, str]] = None, max_tokens: int = 0
    ) -> AgentOutput:
        return self.reason(code, context, max_tokens=max_tokens)

    async def act_async(
        self, code: str, context: Optional[Dict[str, str]] = None, max_tokens: int = 0
    ) -> AgentOutput:
        return await self.reason_async(code, context, max_tokens=max_tokens)

    def attack(self, code: str) -> str:
        output = self.reason(code)
        return output.raw
