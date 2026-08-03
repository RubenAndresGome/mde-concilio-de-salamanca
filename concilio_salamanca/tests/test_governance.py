import json

from concilio_salamanca.cli import setup_parser
from concilio_salamanca.debate.context_compression import compress_context
from concilio_salamanca.debate.council_store import CouncilStore
from concilio_salamanca.debate.dogma import DogmaEngine
from concilio_salamanca.debate.voting import build_voting_table
from concilio_salamanca.mcp_server import handle_call_tool, handle_list_tools
from concilio_salamanca.schemas import AgentOutput, AgentVeredict, Silogismo, Veredicto


def _output(verdict: Veredicto, pnc: bool = True) -> AgentOutput:
    structured = AgentVeredict(
        agente="test",
        rol="test",
        silogismo=Silogismo(
            premisa_mayor="Todo secreto expuesto es vulnerable",
            premisa_menor="Esta clave es un secreto expuesto",
            conclusion="Esta clave es vulnerable",
        ),
        principio_no_contradiccion=pnc,
        veredicto=verdict,
    )
    return AgentOutput(raw=structured.model_dump_json(), structured=structured)


def test_college_counts_only_final_vote_and_weights_context():
    security = _output(Veredicto.CONDENA)
    generic = _output(Veredicto.ABSUELVE)
    result = {
        "state": {
            "language": "python",
            "code": "password = 'hardcoded secret'",
            "arguments_history": [
                {"round": 1, "arguments": {"Auditor de Seguridad": "ABSUELVE"}},
                {
                    "round": 2,
                    "arguments": {
                        "Auditor de Seguridad": security.raw,
                        "Agente Generico": generic.raw,
                    },
                },
            ],
            "agent_outputs": {
                "Auditor de Seguridad": security,
                "Agente Generico": generic,
            },
        }
    }
    voting = build_voting_table(result)
    assert voting["total"] == 2
    assert voting["votos"] == {"CONDENA": 1, "ABSUELVE": 1, "RESERVA": 0}
    assert voting["votos_ponderados"]["CONDENA"] > voting["votos_ponderados"]["ABSUELVE"]
    assert voting["mayoria"] == "CONDENA"


def test_pnc_violation_reduces_vote_weight():
    valid = _output(Veredicto.CONDENA, pnc=True)
    invalid = _output(Veredicto.CONDENA, pnc=False)
    result = {
        "state": {
            "code": "def f(): pass",
            "arguments_history": [{"arguments": {"Doctor": valid.raw, "Socrates": invalid.raw}}],
            "agent_outputs": {"Doctor": valid, "Socrates": invalid},
        }
    }
    agents = build_voting_table(result)["agentes"]
    assert agents[0]["peso"] > agents[1]["peso"]


def test_dogma_requires_user_on_contradiction_and_can_resolve(tmp_path):
    engine = DogmaEngine(CouncilStore(tmp_path / "council.db"))
    proposed = engine.propose(
        ["Usa SQLite", "No uses SQLite", "Reduce el consumo de tokens"],
        "Hacer funcional el Concilio",
    )
    assert proposed["estado"] == "CONTRADICTORIO"
    assert proposed["requiere_usuario"] is True
    assert "usuario" in proposed["mensaje_usuario"]

    sqlite_positive = next(
        order["id"] for order in proposed["ordenes"] if order["texto"] == "Usa SQLite"
    )
    token_order = next(
        order["id"] for order in proposed["ordenes"] if "tokens" in order["texto"]
    )
    resolved = engine.resolve(
        proposed["dogma_id"],
        [sqlite_positive, token_order],
        "Usar SQLite y reducir tokens",
    )
    assert resolved["estado"] == "OBJETIVO"
    assert len(resolved["ordenes"]) == 2


def test_sqlite_graph_local_context(tmp_path):
    store = CouncilStore(tmp_path / "graph.db")
    store.upsert_node("dogma:1", "dogma", "Reducir tokens", {"budget": 1000})
    store.upsert_node("rule:1", "regla", "Compresion por silogismos")
    store.add_edge("dogma:1", "rule:1", "SE_REALIZA_CON", 1.5)
    context = store.local_context("Reducir tokens", limit=4, hops=1)
    assert {node["id"] for node in context} == {"dogma:1", "rule:1"}
    assert store.stats()["aristas"] == 1


def test_context_compression_is_bounded_and_deduplicated():
    verbose = json.dumps(
        {
            "veredicto": "CONDENA",
            "silogismo": {
                "premisa_mayor": "A" * 500,
                "premisa_menor": "B" * 500,
                "conclusion": "C" * 500,
            },
        }
    )
    context = compress_context({"A": verbose, "B": verbose, "C": "RESERVA"}, budget_chars=600)
    assert len("".join(context.values())) <= 600
    assert len(context) == 2


def test_mcp_exposes_governance_tools():
    names = {tool["name"] for tool in handle_list_tools({})["tools"]}
    assert {"propose_dogma", "resolve_dogma", "exhaust_cases", "graph_context"} <= names


def test_mcp_casuistry_has_hard_limit():
    result = handle_call_tool("exhaust_cases", {"context": "auditoria", "limit": 3})
    assert result["content"][0]["text"].count("\n") == 2


def test_local_provider_does_not_inherit_openai_key(monkeypatch):
    from concilio_salamanca.debate.providers import resolve_api_key

    monkeypatch.setenv("OPENAI_API_KEY", "must-not-leak-to-local-provider")
    assert resolve_api_key("ollama") is None


def test_mcp_server_is_reachable_from_cli():
    assert setup_parser().parse_args(["mcp-serve"]).command == "mcp-serve"


def test_installer_points_to_packaged_skill():
    from concilio_salamanca.installer import SKILL_MD_SOURCE, SKILL_ROOT

    assert SKILL_MD_SOURCE == SKILL_ROOT / "SKILL.md"
    assert SKILL_MD_SOURCE.exists()
    assert (SKILL_ROOT / "reference" / "gobernanza_cognitiva.md").exists()
