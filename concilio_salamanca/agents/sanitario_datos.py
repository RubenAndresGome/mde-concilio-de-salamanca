from __future__ import annotations

from typing import Dict, Optional

from langchain_core.language_models import BaseChatModel

from concilio_salamanca.agents.base import AgenteBase
from concilio_salamanca.prompts.system_prompts import SANITARIO_DATOS
from concilio_salamanca.schemas import AgentOutput


class SanitarioDatos(AgenteBase):
    role_name = "Purgator Datorum (Data Sanitation)"
    system_prompt = SANITARIO_DATOS

    def __init__(self, model: BaseChatModel):
        super().__init__(model)

    def act(self, code: str, context: Optional[Dict[str, str]] = None) -> AgentOutput:
        return self.reason(code, context)
