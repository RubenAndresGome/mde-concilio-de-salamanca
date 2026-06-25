from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

from concilio_salamanca.cli import setup_parser
from concilio_salamanca.debate.formatters import (
    format_output_json,
    format_output_markdown,
    format_output_mermaid,
    format_output_sarif,
    format_output_text,
    format_output_executive,
)
from concilio_salamanca.debate.voting import build_voting_table
from concilio_salamanca.schemas import (
    AgentOutput,
    AgentVeredict,
    Determinatio,
    Silogismo,
    Veredicto,
    PnCValidation,
)
from concilio_salamanca.main import main


def _create_mock_result():
    s = Silogismo(
        premisa_mayor="Todo A es B",
        premisa_mayor_tipo="A",
        premisa_menor="X es A",
        premisa_menor_tipo="A",
        conclusion="X es B",
        conclusion_tipo="A",
    )
    av = AgentVeredict(
        agente="Promotor Fidei",
        rol="Acusador",
        silogismo=s,
        principio_no_contradiccion=True,
        veredicto=Veredicto.CONDENA,
        fundamento="Codigo inseguro",
    )
    ao = AgentOutput(
        raw="mock-raw-text",
        structured=av,
        timestamp=12345.67,
    )
    det = Determinatio(
        quaestio="Es seguro el codigo?",
        videtur="Parece seguro",
        sed_contra="Tiene vulnerabilidades",
        respondeo="Debe corregirse",
        determinatio_codici="Codigo corregido: ...",
        veredicto_final=Veredicto.CONDENA,
    )
    pnc = PnCValidation(
        hay_contradicciones=False,
        contradicciones=[],
        resumen="Sin contradicciones",
    )
    state = {
        "code": "print('hello')",
        "language": "python",
        "round_num": 1,
        "max_rounds": 1,
        "agent_outputs": {"promotor": ao},
        "arguments_history": [
            {
                "round": 1,
                "arguments": {
                    "Promotor Fidei": "CONDENA: El codigo es vulnerable porque A es B"
                },
            }
        ],
    }
    return {
        "state": state,
        "determinatio": det,
        "pnc_validation": pnc,
    }


def test_cli_parser_fast():
    parser = setup_parser()
    args = parser.parse_args(["--fast", "-f", "test.py"])
    assert args.fast
    assert args.file == "test.py"


def test_voting_calculation():
    result = _create_mock_result()
    voting = build_voting_table(result)
    assert voting["votos"]["CONDENA"] == 1
    assert voting["votos"]["ABSUELVE"] == 0
    assert voting["mayoria"] == "CONDENA"
    assert voting["consenso"] is True  # 1/1 = 100% >= 67%


def test_formatters():
    result = _create_mock_result()
    result["voting"] = build_voting_table(result)

    # JSON
    js = format_output_json(result)
    data = json.loads(js)
    assert data["veredicto_final"] == "CONDENA"
    assert data["voting"]["mayoria"] == "CONDENA"

    # Text
    txt = format_output_text(result)
    assert "CONCILIO DE SALAMANCA" in txt
    assert "QUAESTIO:" in txt
    assert "CONDENA" in txt

    # Markdown
    md = format_output_markdown(result)
    assert "# Determinatio del Concilio de Salamanca" in md
    assert "**Veredicto:** `CONDENA`" in md

    # Mermaid
    mer = format_output_mermaid(result)
    assert "graph TD" in mer
    assert "Promotor_Fidei" in mer

    # SARIF
    sar = format_output_sarif(result, filepath="app.py")
    sar_data = json.loads(sar)
    assert sar_data["version"] == "2.1.0"
    assert len(sar_data["runs"][0]["results"]) == 1

    # Executive
    exe = format_output_executive(result, ["Promotor Fidei"], 1, result["voting"])
    assert (
        "INFORME DE AUDITORÍA" in exe
        or "AUDITORÍA" in exe
        or "DETERMINATIO" in exe
        or "Veredicto" in exe
    )


@patch("concilio_salamanca.debate.providers.resolve_api_key")
@patch("concilio_salamanca.debate.providers.create_model")
@patch("concilio_salamanca.main.DebateOrchestrator")
@patch("builtins.print")
def test_main_cli_execution(
    mock_print, mock_orch_cls, mock_create_model, mock_resolve_key
):
    mock_resolve_key.return_value = "dummy_key"
    mock_orch = MagicMock()
    mock_orch_cls.return_value = mock_orch

    res = _create_mock_result()
    mock_orch.run_debate.return_value = res

    # Mock arguments to run main with "--fast" and "--code"
    test_args = ["main.py", "--fast", "--code", "print('hello')"]
    with patch.object(sys, "argv", test_args):
        main()

    mock_orch.run_debate.assert_called_once()
    args, kwargs = mock_orch.run_debate.call_args
    assert args[0] == "print('hello')"
    assert args[1] == "python"


def test_script_can_run_from_repo_root():
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "concilio_salamanca" / "main.py"

    completed = subprocess.run(
        [sys.executable, str(script), "--list-agents"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert completed.returncode == 0, completed.stderr
    assert "promotor" in completed.stdout.lower()
