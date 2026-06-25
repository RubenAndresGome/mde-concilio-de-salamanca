from __future__ import annotations

from typing import Dict, Optional

from langchain_core.language_models import BaseChatModel

from concilio_salamanca.agents.base import AgenteBase
from concilio_salamanca.prompts.system_prompts import BACON
from concilio_salamanca.schemas import AgentOutput


class Bacon(AgenteBase):
    role_name = "Magister Experientiae (Roger Bacon)"
    system_prompt = BACON

    def __init__(self, model: BaseChatModel):
        super().__init__(model)

    def act(self, code: str, context: Optional[Dict[str, str]] = None) -> AgentOutput:
        return self.reason(code, context)
