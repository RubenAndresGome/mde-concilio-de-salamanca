from __future__ import annotations

from typing import Dict, Optional

from langchain_core.language_models import BaseChatModel

from concilio_salamanca.agents.base import AgenteBase
from concilio_salamanca.prompts.system_prompts import ARQUITECTO_SISTEMAS
from concilio_salamanca.schemas import AgentOutput


class ArquitectoSistemas(AgenteBase):
    role_name = "Architectus Systematis (Systems Architect)"
    system_prompt = ARQUITECTO_SISTEMAS

    def __init__(self, model: BaseChatModel):
        super().__init__(model)

    def act(self, code: str, context: Optional[Dict[str, str]] = None) -> AgentOutput:
        return self.reason(code, context)
