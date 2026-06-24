from __future__ import annotations

from typing import Dict, Optional

from langchain_openai import ChatOpenAI

from concilio_salamanca.agents.base import AgenteBase
from concilio_salamanca.prompts.system_prompts import AUDITOR_DEEP_LEARNING
from concilio_salamanca.schemas import AgentOutput


class AuditorDeepLearning(AgenteBase):
    role_name = "Auditor Profundi (Deep Learning)"
    system_prompt = AUDITOR_DEEP_LEARNING

    def __init__(self, model: ChatOpenAI):
        super().__init__(model)

    def act(self, code: str, context: Optional[Dict[str, str]] = None) -> AgentOutput:
        return self.reason(code, context)
