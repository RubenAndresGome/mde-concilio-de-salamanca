"""
Debate con paralelismo real usando Send API de LangGraph.
Ejecuta todos los agentes de una ronda en paralelo (fan-out),
luego consolida los resultados (fan-in) y pasa al Magister.

Arquitectura:
  START -> fanout_round -> [agente1, agente2, ...] -> consolidate -> [next_round | pnc | magister]
"""

from __future__ import annotations

import operator
from typing import Annotated, Any, Dict, List, TypedDict

from langgraph.graph import END, StateGraph, START
from langgraph.types import Send

from langchain_core.language_models import BaseChatModel

from concilio_salamanca.agents import get_agent_cls, get_agent_label, resolve_agents
from concilio_salamanca.agents.magister_determinans import MagisterDeterminans
from concilio_salamanca.debate.validator_pnc import ValidadorPNC
from concilio_salamanca.schemas import AgentOutput, DebateState


class ParallelDebateState(TypedDict, total=False):
    code: str
    language: str
    static_analysis: str
    agent_keys: List[str]
    round_num: int
    max_rounds: int
    agent_outputs: Dict[str, str]
    arguments_history: List[Dict]
    pnc_validation: Any
    determinatio: Any
    error: str


def build_parallel_graph(
    model: BaseChatModel,
    max_rounds: int = 2,
    enable_pnc: bool = True,
    agents: List[str] = None,
):
    if agents is None:
        agents = ["promotor", "defensor", "doctor", "larouche", "leon_xiii"]

    resolved = resolve_agents(agents)
    magister = MagisterDeterminans(model)
    validator = ValidadorPNC(model) if enable_pnc else None

    g = StateGraph(ParallelDebateState)

    def fanout_round(state: ParallelDebateState):
        round_num = state.get("round_num", 0) + 1
        if round_num > max_rounds:
            return state

        return {
            "round_num": round_num,
            "agent_keys": resolved,
            "max_rounds": max_rounds,
        }

    def send_to_agents(state: ParallelDebateState):
        round_num = state.get("round_num", 0)
        if round_num > max_rounds:
            return []
        sends = []
        for key in resolved:
            sends.append(Send("run_agent", {"agent_key": key}))
        return sends

    def run_agent(state: ParallelDebateState):
        key = state.get("agent_key", "")
        code = state.get("code", "")
        static = state.get("static_analysis", "")
        history = state.get("arguments_history", [])

        label = get_agent_label(key)
        cls = get_agent_cls(key)
        if cls is None:
            return {"agent_outputs": {key: ""}}

        agent = cls(model)

        context = {}
        if history:
            last_round = history[-1].get("arguments", {})
            context = {k: v for k, v in last_round.items() if k != label}

        enhanced_code = code
        if static:
            enhanced_code = f"{code}\n\n--- ANALISIS ESTATICO PREVIO ---\n{static}"

        output = agent.act(enhanced_code, context if context else None)
        return {
            "agent_outputs": {label: output.raw},
            "arguments_history": [{
                "round": state.get("round_num", 0),
                "arguments": {label: output.raw},
            }],
        }

    def consolidate_round(state: ParallelDebateState):
        outputs = state.get("agent_outputs", {})
        history = state.get("arguments_history", [])

        new_entry = {
            "round": state.get("round_num", 0),
            "arguments": outputs,
        }

        return {"arguments_history": [new_entry]}

    def validate_pnc(state: ParallelDebateState):
        if not validator:
            return {}
        history = state.get("arguments_history", [])
        if not history:
            return {}
        last = history[-1].get("arguments", {})
        agent_outputs = {}
        for label, raw_text in last.items():
            agent_outputs[label] = AgentOutput(raw=raw_text)
        pnc = validator.validate(agent_outputs)
        return {"pnc_validation": pnc}

    def magister_judge(state: ParallelDebateState):
        debate_state: DebateState = {
            "code": state.get("code", ""),
            "round_num": state.get("round_num", 0),
            "max_rounds": state.get("max_rounds", 1),
            "arguments_history": state.get("arguments_history", []),
        }
        pnc = state.get("pnc_validation")
        raw = magister.judge(debate_state, pnc)
        determinatio = magister.parse_determinatio(raw)
        determinatio.pnc_validation = pnc
        return {"determinatio": determinatio}

    g.add_node("fanout", fanout_round)
    g.add_node("run_agent", run_agent)
    g.add_node("consolidate", consolidate_round)
    g.add_node("validate_pnc", validate_pnc)
    g.add_node("magister", magister_judge)

    g.add_edge(START, "fanout")
    g.add_conditional_edges("fanout", send_to_agents, ["run_agent"])
    g.add_edge("run_agent", "consolidate")
    g.add_edge("consolidate", "fanout")
    g.add_edge("consolidate", "validate_pnc")
    g.add_edge("validate_pnc", "magister")
    g.add_edge("magister", END)

    return g.compile()


def create_salamanca_graph_parallel(
    model: BaseChatModel, max_rounds: int = 2, enable_pnc: bool = True,
    agents: List[str] = None,
):
    return build_parallel_graph(model, max_rounds, enable_pnc, agents)
