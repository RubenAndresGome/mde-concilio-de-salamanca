from __future__ import annotations

from typing import Dict, Optional

from langchain_core.language_models import BaseChatModel

from concilio_salamanca.agents.base import AgenteBase
from concilio_salamanca.prompts.system_prompts import VITORIA
from concilio_salamanca.schemas import AgentOutput


class Vitoria(AgenteBase):
    role_name = "Custos Iuris (Francisco de Vitoria)"
    system_prompt = VITORIA

    def __init__(self, model: BaseChatModel):
        super().__init__(model)

    def act(self, code: str, context: Optional[Dict[str, str]] = None) -> AgentOutput:
        return self.reason(code, context)
