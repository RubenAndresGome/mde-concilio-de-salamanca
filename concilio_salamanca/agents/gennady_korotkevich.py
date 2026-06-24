from __future__ import annotations

from typing import Dict, Optional

from langchain_core.language_models import BaseChatModel

from concilio_salamanca.agents.base import AgenteBase
from concilio_salamanca.prompts.system_prompts import GENNADY_KOROTKEVICH
from concilio_salamanca.schemas import AgentOutput


class GennadyKorotkevich(AgenteBase):
    role_name = "Gennady Korotkevich (Certator Optimus)"
    system_prompt = GENNADY_KOROTKEVICH

    def __init__(self, model: BaseChatModel):
        super().__init__(model)

    def act(self, code: str, context: Optional[Dict[str, str]] = None) -> AgentOutput:
        return self.reason(code, context)
