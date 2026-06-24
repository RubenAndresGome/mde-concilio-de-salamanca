from __future__ import annotations

from typing import Dict, Optional

from langchain_core.language_models import BaseChatModel

from concilio_salamanca.agents.base import AgenteBase
from concilio_salamanca.prompts.system_prompts import DEFENSOR_CAUSA_FINAL
from concilio_salamanca.schemas import AgentOutput


class DefensorCausaFinal(AgenteBase):
    role_name = "Defensor Causae Finalis"
    system_prompt = DEFENSOR_CAUSA_FINAL

    def __init__(self, model: BaseChatModel):
        super().__init__(model)

    def act(self, code: str, context: Optional[Dict[str, str]] = None) -> AgentOutput:
        return self.reason(code, context)

    def defend(self, code: str) -> str:
        output = self.reason(code)
        return output.raw
