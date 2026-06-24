from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from langgraph.graph import END, StateGraph, START

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
)


class SalamancaGraphBuilder:
    def __init__(
        self,
        model: BaseChatModel,
        max_rounds: int = 2,
        enable_pnc: bool = True,
        agents: Optional[List[str]] = None,
    ):
        self.model = model
        self.max_rounds = max_rounds
        self.enable_pnc = enable_pnc
        self.magister = MagisterDeterminans(model)
        self.validator = ValidadorPNC(model) if enable_pnc else None

        if agents is None:
            agents = ["promotor", "defensor", "doctor", "larouche", "leon_xiii"]
        self._selected_keys = resolve_agents(agents)

    def build(self):
        g = StateGraph(DebateState)

        g.add_node("debate_round", self._debate_round)
        g.add_node("validate_pnc", self._validate_pnc)
        g.add_node("magister", self._magister_judge)

        g.add_edge(START, "debate_round")
        g.add_conditional_edges(
            "debate_round",
            self._should_continue_debate,
            {
                "continue": "debate_round",
                "validate": "validate_pnc",
                "judge": "magister",
            },
        )
        g.add_edge("validate_pnc", "magister")
        g.add_edge("magister", END)

        return g.compile()

    def _should_continue_debate(self, state: DebateState) -> str:
        round_num = state.get("round_num", 0)
        if round_num < self.max_rounds:
            return "continue"
        if self.enable_pnc and state.get("pnc_validation") is None:
            return "validate"
        return "judge"

    def _debate_round(self, state: DebateState) -> Dict[str, Any]:
        code = state.get("code", "")
        round_num = state.get("round_num", 0) + 1
        history = state.get("arguments_history", [])

        previous_args: Dict[str, str] = {}
        if history:
            last_round = history[-1].get("arguments", {})
            previous_args = last_round

        results: Dict[str, AgentOutput] = {}

        for key in self._selected_keys:
            label = get_agent_label(key)
            cls = get_agent_cls(key)
            if cls is None:
                continue
            agent = cls(self.model)
            context = None
            if round_num > 1 and previous_args:
                context = {
                    k: v
                    for k, v in previous_args.items()
                    if k != label
                }
            output = agent.act(code, context)
            results[key] = output

        new_entry = {
            "round": round_num,
            "arguments": {
                get_agent_label(key): output.raw
                for key, output in results.items()
            },
        }

        return {
            "code": code,
            "round_num": round_num,
            "arguments_history": history + [new_entry],
        }

    def _validate_pnc(self, state: DebateState) -> Dict[str, Any]:
        if not self.validator:
            return {}

        history = state.get("arguments_history", [])
        if not history:
            return {}

        last_round = history[-1].get("arguments", {})
        agent_outputs = {}
        for label, raw_text in last_round.items():
            agent_outputs[label] = AgentOutput(raw=raw_text)

        pnc = self.validator.validate(agent_outputs)
        return {"pnc_validation": pnc}

    def _magister_judge(self, state: DebateState) -> Dict[str, Any]:
        pnc = state.get("pnc_validation")
        raw = self.magister.judge(state, pnc)
        determinatio = self.magister.parse_determinatio(raw)
        determinatio.pnc_validation = pnc
        return {"determinatio": determinatio}


def create_salamanca_graph(
    model: BaseChatModel,
    max_rounds: int = 2,
    enable_pnc: bool = True,
    agents: Optional[List[str]] = None,
):
    builder = SalamancaGraphBuilder(
        model=model,
        max_rounds=max_rounds,
        enable_pnc=enable_pnc,
        agents=agents,
    )
    return builder.build()


def create_salamanca_graph_legacy(model: BaseChatModel):
    return create_salamanca_graph(model, max_rounds=1, enable_pnc=False)
