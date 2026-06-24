from __future__ import annotations

from typing import Dict, Optional

from langchain_core.language_models import BaseChatModel

from concilio_salamanca.agents.base import AgenteBase
from concilio_salamanca.prompts.system_prompts import STEVE_WOZNIAK
from concilio_salamanca.schemas import AgentOutput


class SteveWozniak(AgenteBase):
    role_name = "Steve Wozniak (Artifex Elegantiae)"
    system_prompt = STEVE_WOZNIAK

    def __init__(self, model: BaseChatModel):
        super().__init__(model)

    def act(self, code: str, context: Optional[Dict[str, str]] = None) -> AgentOutput:
        return self.reason(code, context)
