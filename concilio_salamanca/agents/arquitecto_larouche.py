from __future__ import annotations

from typing import Dict, Optional

from langchain_openai import ChatOpenAI

from concilio_salamanca.agents.base import AgenteBase
from concilio_salamanca.prompts.system_prompts import ARQUITECTO_LAROUCHE
from concilio_salamanca.schemas import AgentOutput


class ArquitectoLarouche(AgenteBase):
    role_name = "Arquitecto LaRouche"
    system_prompt = ARQUITECTO_LAROUCHE

    def __init__(self, model: ChatOpenAI):
        super().__init__(model)

    def act(self, code: str, context: Optional[Dict[str, str]] = None) -> AgentOutput:
        return self.reason(code, context)

    def analyze(self, code: str) -> str:
        output = self.reason(code)
        return output.raw
