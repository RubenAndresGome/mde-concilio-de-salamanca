from __future__ import annotations

from typing import Dict, Optional

from langchain_openai import ChatOpenAI

from concilio_salamanca.agents.base import AgenteBase
from concilio_salamanca.prompts.system_prompts import KEN_THOMPSON
from concilio_salamanca.schemas import AgentOutput


class KenThompson(AgenteBase):
    role_name = "Ken Thompson (Philosophus Unixis)"
    system_prompt = KEN_THOMPSON

    def __init__(self, model: ChatOpenAI):
        super().__init__(model)

    def act(self, code: str, context: Optional[Dict[str, str]] = None) -> AgentOutput:
        return self.reason(code, context)
