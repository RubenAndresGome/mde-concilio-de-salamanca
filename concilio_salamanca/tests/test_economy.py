from __future__ import annotations

import json
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field

from concilio_salamanca.agents import get_agent_cls
from concilio_salamanca.agents.base import AgenteBase
from concilio_salamanca.debate.audit_profiles import get_audit_profile, select_profile_agents
from concilio_salamanca.debate.compute_policy import ComputePolicyResolver
from concilio_salamanca.debate.orchestrator import DebateConfig, DebateOrchestrator
from concilio_salamanca.debate.security_diff import detect_security_surfaces
from concilio_salamanca.debate.test_impact import select_impacted_tests
from concilio_salamanca.debate.token_accountant import TokenAccountant, extract_usage
from concilio_salamanca.schemas import Veredicto


def _agent_response(verdict: str = "ABSUELVE", questions: list[str] | None = None) -> str:
    return json.dumps({
        "A": "elector", "D": "test", "S": {"PM": "Todo fallo tiene evidencia", "Pm": "No hay fallo", "C": "No condenar"},
        "N": True, "V": verdict, "E": "evidencia", "Q": questions or [],
    })


def _magister_response(verdict: str = "ABSUELVE") -> str:
    return json.dumps({
        "quaestio": "Q", "videtur": "V", "sed_contra": "S", "respondeo": "R",
        "determinatio_codici": "D", "veredicto_final": verdict,
    })


class RecordingChatModel(BaseChatModel):
    responses: list[str] = Field(default_factory=list)
    calls: list[dict[str, Any]] = Field(default_factory=list)
    model_name: str = "deepseek-v4-flash"

    @property
    def _llm_type(self) -> str:
        return "recording"

    def _generate(self, messages, stop=None, run_manager=None, **kwargs) -> ChatResult:
        self.calls.append({"messages": messages, "kwargs": kwargs})
        content = self.responses.pop(0) if self.responses else _agent_response()
        message = AIMessage(
            content=content,
            response_metadata={
                "token_usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 20,
                    "prompt_cache_hit_tokens": 60,
                    "prompt_cache_miss_tokens": 40,
                }
            },
        )
        return ChatResult(generations=[ChatGeneration(message=message)])


def _disable_cache(monkeypatch) -> None:
    monkeypatch.setattr(AgenteBase, "_check_code_cache", lambda *args, **kwargs: None)
    monkeypatch.setattr(AgenteBase, "_store_code_cache", lambda *args, **kwargs: None)


def test_audit_profiles_are_exact():
    assert [(get_audit_profile(i).max_agents, get_audit_profile(i).max_calls) for i in range(4)] == [
        (0, 0), (2, 2), (3, 6), (5, 11)
    ]
    assert get_audit_profile(1).agent_max_tokens == 384
    assert get_audit_profile(2).magister_max_tokens == 768


def test_cli_and_mcp_expose_economic_contract():
    from concilio_salamanca.cli import setup_parser
    from concilio_salamanca.mcp_server import MCP_TOOLS

    args = setup_parser().parse_args([
        "--audit-level", "2", "--compute-policy", "cloud", "--priority", "quality",
        "--token-budget", "5000", "--non-interactive", "--code", "x=1",
    ])
    assert (args.audit_level, args.compute_policy, args.priority, args.token_budget) == (2, "cloud", "quality", 5000)
    schema = next(tool for tool in MCP_TOOLS if tool["name"] == "run_audit")["inputSchema"]["properties"]
    assert {"audit_level", "compute_policy", "priority", "token_budget", "frontier_decision"} <= set(schema)


def test_contextual_agent_selection():
    assert select_profile_agents(1, "password = request.body", "python") == ["arquimedes", "seguridad"]
    assert select_profile_agents(2, "SELECT * FROM users", "sql")[-1] == "datos"
    assert select_profile_agents(0, "x=1") == []


def test_compute_policy_deepseek_and_fallback(monkeypatch):
    resolver = ComputePolicyResolver(ollama_probe=lambda: ["qwen2.5-coder:7b"])
    monkeypatch.setenv("DEEPSEEK_API_KEY", "secret")
    cloud = resolver.resolve(policy="cloud", priority="cost")
    assert (cloud.provider, cloud.model) == ("deepseek", "deepseek-v4-flash")
    monkeypatch.delenv("DEEPSEEK_API_KEY")
    local = resolver.resolve(policy="auto")
    assert (local.provider, local.model) == ("ollama", "qwen2.5-coder:7b")
    static = ComputePolicyResolver(ollama_probe=lambda: []).resolve(policy="auto")
    assert static.static_only and static.reserve_reason
    assert "secret" not in repr(cloud)


def test_common_prompt_prefix_and_role_after_code():
    model = RecordingChatModel()
    a = get_agent_cls("promotor")(model)
    b = get_agent_cls("defensor")(model)
    am = a._build_messages("x = 1")
    bm = b._build_messages("x = 1")
    assert am[0].content == bm[0].content
    assert am[1].content.split("ROLE:", 1)[0] == bm[1].content.split("ROLE:", 1)[0]
    assert am[1].content.index("x = 1") < am[1].content.index("ROLE:")


def test_deepseek_cache_usage_extraction():
    response = AIMessage(content="ok", response_metadata={"token_usage": {
        "prompt_tokens": 100, "completion_tokens": 9,
        "prompt_cache_hit_tokens": 75, "prompt_cache_miss_tokens": 25,
    }})
    usage = extract_usage(response)
    assert usage["prompt_cache_hit_tokens"] == 75
    accountant = TokenAccountant(1000)
    accountant.record(usage=usage, model="deepseek-v4-flash", agent="A")
    assert accountant.snapshot()["cache_hit_ratio"] == 0.75


def test_level_zero_never_calls_llm():
    model = RecordingChatModel()
    result = DebateOrchestrator(model, DebateConfig(audit_level=0)).run_debate("eval(user)")
    assert model.calls == []
    assert result["determinatio"].veredicto_final == Veredicto.CONDENA
    assert result["stop_reason"] == "static_complete"


def test_level_one_two_calls_no_magister_and_hard_limits(monkeypatch):
    _disable_cache(monkeypatch)
    model = RecordingChatModel(responses=[_agent_response(), _agent_response()])
    config = DebateConfig(audit_level=1, agents=["arquimedes", "linus"], model_name=model.model_name)
    result = DebateOrchestrator(model, config).run_debate("unique_level_one = 1")
    assert len(model.calls) == 2
    assert all(call["kwargs"]["max_tokens"] == 384 for call in model.calls)
    assert result["calls_by_model"] == {"deepseek-v4-flash": 2}
    assert result["cache_hit_ratio"] == 0.6
    assert result["stop_reason"] == "consensus_reached"


def test_level_two_early_stop_calls_three_agents_and_magister(monkeypatch):
    _disable_cache(monkeypatch)
    model = RecordingChatModel(responses=[
        _agent_response(), _agent_response(), _agent_response(), _magister_response(),
    ])
    config = DebateConfig(audit_level=2, agents=["promotor", "defensor", "linus"])
    result = DebateOrchestrator(model, config).run_debate("unique_level_two = 2")
    assert len(model.calls) == 4
    assert [call["kwargs"]["max_tokens"] for call in model.calls] == [512, 512, 512, 768]
    assert result["determinatio"].veredicto_final == Veredicto.ABSUELVE


def test_level_two_contested_caps_at_six_calls(monkeypatch):
    _disable_cache(monkeypatch)
    model = RecordingChatModel(responses=[
        _agent_response("CONDENA"), _agent_response("ABSUELVE"), _agent_response("RESERVA"),
        _agent_response("CONDENA"), _agent_response("ABSUELVE"), _magister_response("RESERVA"),
    ])
    config = DebateConfig(audit_level=2, agents=["promotor", "defensor", "linus"])
    result = DebateOrchestrator(model, config).run_debate("unique_contested = 3")
    assert len(model.calls) == 6
    assert result["pnc_validation"].hay_contradicciones
    assert result["escalation"]["requires_user_decision"]
    assert all(value is not None for value in result["escalation"]["estimated_cost_usd"].values())


def test_level_three_contested_caps_at_eleven_calls(monkeypatch):
    _disable_cache(monkeypatch)
    responses = [
        _agent_response("CONDENA"), _agent_response("ABSUELVE"), _agent_response("RESERVA"),
        _agent_response("CONDENA"), _agent_response("ABSUELVE"),
        _agent_response("CONDENA"), _agent_response("ABSUELVE"), _agent_response("RESERVA"),
        _agent_response("CONDENA"), _agent_response("ABSUELVE"), _magister_response("RESERVA"),
    ]
    model = RecordingChatModel(responses=responses)
    config = DebateConfig(
        audit_level=3, agents=["promotor", "defensor", "doctor", "larouche", "linus"]
    )
    DebateOrchestrator(model, config).run_debate("unique_full = 4")
    assert len(model.calls) == 11


def test_token_budget_stops_before_call(monkeypatch):
    _disable_cache(monkeypatch)
    model = RecordingChatModel(responses=[_agent_response(), _agent_response()])
    result = DebateOrchestrator(
        model,
        DebateConfig(audit_level=1, agents=["arquimedes", "linus"], token_budget=100),
    ).run_debate("unique_budget = 5")
    assert len(model.calls) == 0
    assert result["stop_reason"] == "token_budget_exhausted"


def test_question_categories_are_capped(monkeypatch):
    _disable_cache(monkeypatch)
    questions = ["Limite: vacio?", "Fallo: red?", "Autoridad: quien?", "Tiempo: cuando?"]
    model = RecordingChatModel(responses=[_agent_response(questions=questions), _agent_response(questions=questions)])
    result = DebateOrchestrator(model, DebateConfig(audit_level=1, agents=["arquimedes", "linus"])).run_debate("unique_questions")
    assert len(result["state"]["pending_questions"]) == 2


def test_security_diff_only_uses_added_lines():
    result = detect_security_surfaces("- password = old\n+ value = 1")
    assert not result["activate_security"]
    assert detect_security_surfaces("+ token = request.cookie")["activate_security"]


def test_test_impact_selects_named_and_graph_tests():
    selected = select_impacted_tests(
        ["src/auth.py"], ["tests/test_auth.py", "tests/test_api.py"],
        {"tests/test_api.py": ["src/auth.py"]},
    )
    assert selected == ["tests/test_api.py", "tests/test_auth.py"]


def test_economic_profiles_reduce_declared_output_budget():
    legacy = 11 * 1200
    level_one = 2 * get_audit_profile(1).agent_max_tokens
    level_two_worst = 5 * get_audit_profile(2).agent_max_tokens + get_audit_profile(2).magister_max_tokens
    assert 1 - level_one / legacy >= 0.70
    assert 1 - level_two_worst / legacy >= 0.50


def test_static_veto_preserves_critical_findings(monkeypatch):
    _disable_cache(monkeypatch)
    model = RecordingChatModel(responses=[_agent_response(), _agent_response()])
    result = DebateOrchestrator(
        model, DebateConfig(audit_level=1, agents=["arquimedes", "linus"])
    ).run_debate("value = eval(user_input)")
    assert result["determinatio"].veredicto_final == Veredicto.CONDENA
    assert result["state"]["critical_static_findings"] == ["eval("]


def test_recorded_benchmark_acceptance():
    from concilio_salamanca.scripts.benchmark_economy import projected_live_cost, recorded_benchmark

    report = recorded_benchmark()
    assert report["levels"]["1"]["reduction"] >= 0.70
    assert report["levels"]["2"]["reduction"] >= 0.50
    assert report["critical_findings_lost"] == 0
    assert report["noncritical_verdict_discrepancy"] <= 0.10
    assert projected_live_cost() < 0.05


def test_frontier_resume_rejects_unapproved_decision(monkeypatch):
    _disable_cache(monkeypatch)
    cheap = RecordingChatModel(responses=[_agent_response("CONDENA"), _agent_response("ABSUELVE")])
    orchestrator = DebateOrchestrator(
        cheap, DebateConfig(audit_level=1, agents=["arquimedes", "linus"])
    )
    result = orchestrator.run_debate("unique_frontier = 6")
    frontier = RecordingChatModel(responses=[_agent_response(), _magister_response()])
    try:
        orchestrator.resume_with_frontier(
            result, frontier, decision_id="incorrecta", candidate="gpt-5.6-terra"
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Se aceptó una decisión frontera no autorizada")
    assert frontier.calls == []
