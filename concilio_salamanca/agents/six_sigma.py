from __future__ import annotations

from typing import Dict, Optional

from langchain_core.language_models import BaseChatModel

from concilio_salamanca.agents.base import AgenteBase
from concilio_salamanca.prompts.system_prompts import SIX_SIGMA
from concilio_salamanca.schemas import AgentOutput


class SixSigma(AgenteBase):
    role_name = "Magister Qualitatis (Six Sigma)"
    system_prompt = SIX_SIGMA

    def __init__(self, model: BaseChatModel):
        super().__init__(model)

    def act(self, code: str, context: Optional[Dict[str, str]] = None) -> AgentOutput:
        return self.reason(code, context)
