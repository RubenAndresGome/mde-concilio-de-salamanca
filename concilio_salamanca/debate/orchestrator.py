from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from langchain_core.language_models import BaseChatModel

from concilio_salamanca.agents import (
    AGENT_REGISTRY,
    get_agent_cls,
    get_agent_label,
    resolve_agents,
)
from concilio_salamanca.agents.magister_determinans import MagisterDeterminans
from concilio_salamanca.debate.validator_pnc import ValidadorPNC
from concilio_salamanca.schemas import (
    AgentOutput,
    DebateState,
    Determinatio,
    PnCValidation,
)


@dataclass
class DebateConfig:
    max_rounds: int = 2
    include_pnc_validation: bool = True
    agents: List[str] = field(default_factory=lambda: ["promotor", "defensor", "doctor", "larouche", "leon_xiii"])


class DebateOrchestrator:
    def __init__(
        self,
        model: BaseChatModel,
        config: Optional[DebateConfig] = None,
    ):
        self.model = model
        self.config = config or DebateConfig()
        self.magister = MagisterDeterminans(model)
        self.validator = ValidadorPNC(model) if self.config.include_pnc_validation else None

        self._selected_keys = resolve_agents(self.config.agents)
        self._agent_instances: Dict[str, Any] = {}

        for key in self._selected_keys:
            cls = get_agent_cls(key)
            if cls:
                self._agent_instances[key] = cls(model)

    @property
    def agent_keys(self) -> List[str]:
        return self._selected_keys

    def run_debate(self, code: str, language: str = "auto") -> Dict[str, Any]:
        state: DebateState = {
            "code": code,
            "language": language,
            "round_num": 0,
            "max_rounds": self.config.max_rounds,
            "arguments_history": [],
        }

        previous_arguments: Dict[str, str] = {}

        for round_num in range(1, self.config.max_rounds + 1):
            state["round_num"] = round_num
            round_outputs: Dict[str, AgentOutput] = {}

            for key in self._selected_keys:
                agent = self._agent_instances.get(key)
                if not agent:
                    continue
                label = get_agent_label(key)

                context = None
                if round_num > 1 and previous_arguments:
                    context = {
                        k: v
                        for k, v in previous_arguments.items()
                        if k != label
                    }

                output = agent.act(code, context)
                round_outputs[key] = output
                previous_arguments[label] = output.raw

            state["arguments_history"].append({
                "round": round_num,
                "arguments": {
                    get_agent_label(key): output.raw
                    for key, output in round_outputs.items()
                },
            })

        pnc = None
        if self.validator:
            agent_outputs_for_pnc = {
                get_agent_label(key): output
                for key, output in round_outputs.items()
            }
            pnc = self.validator.validate(agent_outputs_for_pnc)
            state["pnc_validation"] = pnc

        determinatio_raw = self.magister.judge(state, pnc)
        determinatio = self.magister.parse_determinatio(determinatio_raw)
        determinatio.pnc_validation = pnc
        state["determinatio"] = determinatio

        return {
            "state": state,
            "determinatio": determinatio,
            "pnc_validation": pnc,
        }
