from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from concilio_salamanca.agents import (
    AGENT_GROUPS,
    AGENT_REGISTRY,
    get_agent_cls,
    get_agent_label,
    list_agents,
    resolve_agents,
)
from concilio_salamanca.agents.arquitecto_larouche import ArquitectoLarouche
from concilio_salamanca.agents.bjarne_stroustrup import BjarneStroustrup
from concilio_salamanca.agents.defensor_causa_final import DefensorCausaFinal
from concilio_salamanca.agents.defensor_leon_xiii import DefensorLeonXIII
from concilio_salamanca.agents.doctor_materia import DoctorMateria
from concilio_salamanca.agents.gennady_korotkevich import GennadyKorotkevich
from concilio_salamanca.agents.auditor_dl import AuditorDeepLearning
from concilio_salamanca.agents.analista_seguridad import AnalistaSeguridad
from concilio_salamanca.agents.ingeniero_mlops import IngenieroMLOps
from concilio_salamanca.agents.sanitario_datos import SanitarioDatos
from concilio_salamanca.agents.arquitecto_sistemas import ArquitectoSistemas
from concilio_salamanca.agents.ingeniero_iot import IngenieroIoT
from concilio_salamanca.agents.socrates import Socrates
from concilio_salamanca.agents.scrum_master import ScrumMaster
from concilio_salamanca.agents.six_sigma import SixSigma
from concilio_salamanca.agents.llull import Llull
from concilio_salamanca.agents.bacon import Bacon
from concilio_salamanca.agents.vitoria import Vitoria
from concilio_salamanca.agents.ratio import Ratio
from concilio_salamanca.agents.ponytail import Ponytail
from concilio_salamanca.agents.graphify import Graphify
from concilio_salamanca.agents.rtk import RTK
from concilio_salamanca.agents.telemetry import Telemetry
from concilio_salamanca.agents.ken_thompson import KenThompson
from concilio_salamanca.agents.linus_torvalds import LinusTorvalds
from concilio_salamanca.agents.magister_determinans import MagisterDeterminans
from concilio_salamanca.agents.promotor_fidei import PromotorFidei
from concilio_salamanca.agents.richard_stallman import RichardStallman
from concilio_salamanca.agents.steve_wozniak import SteveWozniak
from concilio_salamanca.agents.redteam import RedTeamCoordinator
from concilio_salamanca.agents.pentest import PentestAuditor
from concilio_salamanca.agents.abuser import AbuserStoryGenerator
from concilio_salamanca.agents.causas import AnalistaCausal
from concilio_salamanca.agents.leibniz import OptimistaLeibniziano
from concilio_salamanca.agents.nietzsche import VitalistaNietzscheano
from concilio_salamanca.debate.orchestrator import DebateConfig, DebateOrchestrator
from concilio_salamanca.debate.validator_pnc import ValidadorPNC
from concilio_salamanca.license_generator import LicenseGenerator
from concilio_salamanca.schemas import (
    AgentOutput,
    AgentVeredict,
    Contradiccion,
    Determinatio,
    PnCValidation,
    Silogismo,
    Veredicto,
)


def _mock_model():
    model = MagicMock()
    model.invoke.return_value = MagicMock()
    model.invoke.return_value.content = json.dumps(
        {
            "agente": "TestAgent",
            "rol": "Test",
            "silogismo": {
                "premisa_mayor": "Todo A es B",
                "premisa_menor": "X es A",
                "conclusion": "X es B",
            },
            "principio_no_contradiccion": True,
            "veredicto": "RESERVA",
            "fundamento": "Test",
        }
    )
    return model


# --- Schema tests ---
def test_silogismo_model():
    s = Silogismo(
        premisa_mayor="Todo A es B",
        premisa_menor="X es A",
        conclusion="X es B",
    )
    assert s.premisa_mayor == "Todo A es B"


def test_veredicto_enum():
    assert Veredicto.CONDENA.value == "CONDENA"
    assert Veredicto.ABSUELVE.value == "ABSUELVE"
    assert Veredicto.RESERVA.value == "RESERVA"


def test_agent_veredict():
    av = AgentVeredict(
        agente="Promotor Fidei",
        rol="Acusador",
        silogismo=Silogismo(
            premisa_mayor="Todo A es B",
            premisa_menor="X es A",
            conclusion="X es B",
        ),
        principio_no_contradiccion=True,
        veredicto=Veredicto.CONDENA,
        fundamento="Codigo inseguro",
    )
    assert av.veredicto == Veredicto.CONDENA


def test_pnc_validation():
    pnc = PnCValidation(
        hay_contradicciones=True,
        contradicciones=[
            Contradiccion(
                agente_a="A",
                agente_b="B",
                proposicion_a="P",
                proposicion_b="no-P",
                descripcion="Conflicto",
            )
        ],
        resumen="Hay una contradiccion",
    )
    assert pnc.hay_contradicciones


def test_determinatio():
    d = Determinatio(
        quaestio="Es seguro el codigo?",
        videtur="Parece seguro",
        sed_contra="Tiene vulnerabilidades",
        respondeo="Debe corregirse",
        determinatio_codici="Codigo corregido: ...",
        veredicto_final=Veredicto.CONDENA,
    )
    assert d.veredicto_final == Veredicto.CONDENA


# --- Agent tests (original 6 + new 6) ---
def _test_agent(cls):
    model = _mock_model()
    agent = cls(model)
    output = agent.act("print('hello')")
    assert isinstance(output, AgentOutput)
    assert output.structured is not None
    return output


def test_promotor_fidei():
    _test_agent(PromotorFidei)


def test_defensor_causa_final():
    _test_agent(DefensorCausaFinal)


def test_doctor_materia():
    _test_agent(DoctorMateria)


def test_arquitecto_larouche():
    _test_agent(ArquitectoLarouche)


def test_defensor_leon_xiii():
    _test_agent(DefensorLeonXIII)


def test_linus_torvalds():
    _test_agent(LinusTorvalds)


def test_steve_wozniak():
    _test_agent(SteveWozniak)


def test_richard_stallman():
    _test_agent(RichardStallman)


def test_bjarne_stroustrup():
    _test_agent(BjarneStroustrup)


def test_ken_thompson():
    _test_agent(KenThompson)


def test_gennady_korotkevich():
    _test_agent(GennadyKorotkevich)


def test_auditor_deep_learning():
    _test_agent(AuditorDeepLearning)


def test_analista_seguridad():
    _test_agent(AnalistaSeguridad)


def test_ingeniero_mlops():
    _test_agent(IngenieroMLOps)


def test_sanitario_datos():
    _test_agent(SanitarioDatos)


def test_arquitecto_sistemas():
    _test_agent(ArquitectoSistemas)


def test_ingeniero_iot():
    _test_agent(IngenieroIoT)


def test_socrates():
    _test_agent(Socrates)


def test_scrum_master():
    _test_agent(ScrumMaster)


def test_six_sigma():
    _test_agent(SixSigma)


def test_llull():
    _test_agent(Llull)


def test_bacon():
    _test_agent(Bacon)


def test_vitoria():
    _test_agent(Vitoria)


def test_ratio():
    _test_agent(Ratio)


def test_ponytail():
    _test_agent(Ponytail)


def test_graphify():
    _test_agent(Graphify)


def test_rtk():
    _test_agent(RTK)


def test_telemetry():
    _test_agent(Telemetry)


def test_red_team_coordinator():
    _test_agent(RedTeamCoordinator)


def test_pentest_auditor():
    _test_agent(PentestAuditor)


def test_abuser_story_generator():
    _test_agent(AbuserStoryGenerator)


def test_analista_causal():
    _test_agent(AnalistaCausal)


def test_optimista_leibniziano():
    _test_agent(OptimistaLeibniziano)


def test_vitalista_nietzscheano():
    _test_agent(VitalistaNietzscheano)


def test_magister_parse():
    model = _mock_model()
    magister = MagisterDeterminans(model)
    raw = json.dumps(
        {
            "quaestio": "Es seguro?",
            "videtur": "Parece seguro",
            "sed_contra": "No lo es",
            "respondeo": "Condenado",
            "determinatio_codici": "Corregir X",
            "veredicto_final": "CONDENA",
        }
    )
    d = magister.parse_determinatio(raw)
    assert d.veredicto_final == Veredicto.CONDENA


def test_pnc_validator_parse():
    model = _mock_model()
    validator = ValidadorPNC(model)
    raw = json.dumps(
        {
            "hay_contradicciones": True,
            "contradicciones": [
                {
                    "agente_a": "Promotor Fidei",
                    "agente_b": "Defensor Causae Finalis",
                    "proposicion_a": "El codigo es inseguro",
                    "proposicion_b": "El codigo es seguro",
                    "descripcion": "Contradiccion directa",
                }
            ],
            "resumen": "Existe una contradiccion fundamental",
        }
    )
    result = validator._parse(raw)
    assert result.hay_contradicciones
    assert len(result.contradicciones) == 1


# --- Agent registry tests ---
def test_agent_registry_has_all_agents():
    assert len(AGENT_REGISTRY) == 38
    expected_keys = [
        "promotor",
        "defensor",
        "doctor",
        "larouche",
        "leon_xiii",
        "linus",
        "wozniak",
        "stallman",
        "stroustrup",
        "thompson",
        "korotkevich",
        "redteam",
        "pentest",
        "abuser",
        "causas",
        "leibniz",
        "nietzsche",
    ]
    for k in expected_keys:
        assert k in AGENT_REGISTRY


def test_resolve_agents_individual():
    result = resolve_agents(["linus", "stallman"])
    assert "linus" in result
    assert "stallman" in result


def test_resolve_agents_group():
    result = resolve_agents(["escolasticos"])
    assert "promotor" in result
    assert "defensor" in result
    assert "doctor" in result
    assert "larouche" in result
    assert "leon_xiii" in result


def test_resolve_agents_mixed():
    result = resolve_agents(["escolasticos", "linus", "stallman"])
    assert "promotor" in result
    assert "linus" in result
    assert "stallman" in result


def test_resolve_agents_todos():
    result = resolve_agents(["todos"])
    assert len(result) == 38


def test_resolve_agents_no_duplicates():
    result = resolve_agents(["promotor", "promotor", "escolasticos"])
    assert result.count("promotor") == 1


def test_get_agent_label():
    assert "Promotor Fidei" in get_agent_label("promotor")
    assert "Linus Torvalds" in get_agent_label("linus")
    assert "Richard Stallman" in get_agent_label("stallman")


def test_get_agent_cls():
    assert get_agent_cls("linus") is LinusTorvalds
    assert get_agent_cls("stallman") is RichardStallman
    assert get_agent_cls("nonexistent") is None


def test_agent_groups_exist():
    assert "todos" in AGENT_GROUPS
    assert "escolasticos" in AGENT_GROUPS
    assert "pragmaticos" in AGENT_GROUPS
    assert "eticos" in AGENT_GROUPS
    assert "algoritmicos" in AGENT_GROUPS
    assert "tecnicos" in AGENT_GROUPS
    assert "acusacion" in AGENT_GROUPS
    assert "defensa" in AGENT_GROUPS
    assert "seguridad_completa" in AGENT_GROUPS
    assert "ia_produccion" in AGENT_GROUPS
    assert "embebidos" in AGENT_GROUPS
    assert "clean_code" in AGENT_GROUPS
    assert "proceso" in AGENT_GROUPS
    assert "delineatio" in AGENT_GROUPS


# --- Orchestrator with custom agents ---
def test_orchestrator_with_custom_agents():
    model = _mock_model()
    config = DebateConfig(
        max_rounds=1,
        include_pnc_validation=False,
        agents=["linus", "stallman"],
    )
    orchestrator = DebateOrchestrator(model, config)
    assert len(orchestrator.agent_keys) == 2
    result = orchestrator.run_debate("print('hello')")
    assert result["determinatio"] is not None


def test_orchestrator_parallel():
    model = _mock_model()
    config = DebateConfig(
        max_rounds=1,
        include_pnc_validation=True,
        agents=["linus", "stallman"],
        parallel=True,
    )
    orchestrator = DebateOrchestrator(model, config)
    assert len(orchestrator.agent_keys) == 2
    result = orchestrator.run_debate("print('hello')")
    assert result["determinatio"] is not None
    assert result["pnc_validation"] is not None


def test_parallel_graph():
    from concilio_salamanca.debate.send_graph import create_salamanca_graph_parallel

    model = _mock_model()
    graph = create_salamanca_graph_parallel(
        model=model,
        max_rounds=1,
        enable_pnc=True,
        agents=["linus", "stallman"],
    )
    state = {
        "code": "print('hello')",
        "language": "python",
        "static_analysis": "No static issues",
    }
    result = graph.invoke(state)
    assert result is not None
    assert "determinatio" in result
    assert result["determinatio"] is not None


# --- License tests ---
def test_license_generator():
    gen = LicenseGenerator(
        developer_name="Test Dev",
        project_name="Test Project",
        github_repo="github.com/test/repo",
    )
    license_text = gen.generate_license("MX")
    assert "Test Dev" in license_text
    assert "Test Project" in license_text
    assert "RERUM NOVARUM STATUTO" in license_text
    assert "Salario" in license_text
    assert "Bula" in license_text
    assert "github.com/test/repo" in license_text
    assert "Disney" in license_text
    assert "Big Mac" in license_text
    assert "Sostenibilidad" in license_text
    assert "BME" in license_text
    assert "Oligarca" in license_text


def test_license_free_for_poor_devs():
    gen = LicenseGenerator("Dev", "Proj")
    text = gen.generate_license("US")
    assert "Big Mac" in text
    assert "gratis" in text.lower()
    assert "open source" in text.lower()
    assert "Auto-Favorito" in text


def test_license_ppa_thresholds():
    gen = LicenseGenerator()
    thresholds_us = gen.get_localized_thresholds("US")
    thresholds_in = gen.get_localized_thresholds("IN")
    assert "big_mac_price_usd" in thresholds_us
    assert thresholds_us["big_mac_price_usd"] > 0
    assert thresholds_in["big_mac_price_usd"] > 0


def test_big_mac_calculator():
    from concilio_salamanca.license_generator import LicenseGenerator

    result = LicenseGenerator.calculate_bme(1000, "US")
    assert result["bme"] > 0
    assert "%" in result["tasa"]


def test_geo_arbitrage():
    from concilio_salamanca.license_generator import LicenseGenerator

    bme_mx_income_mx_residence = LicenseGenerator.calculate_bme(3000, "MX")
    bme_us_income_mx_residence = LicenseGenerator.calculate_bme(8000, "MX", "US")
    bme_us_income_us_residence = LicenseGenerator.calculate_bme(8000, "US")

    assert bme_us_income_mx_residence["bme"] > bme_mx_income_mx_residence["bme"]
    assert bme_us_income_mx_residence["tasa"] != "0%"


def test_license_list_countries():
    countries = LicenseGenerator.list_countries()
    assert "US" in countries
    assert "MX" in countries


def test_list_agents_function():
    text = list_agents()
    assert "Linus Torvalds" in text
    assert "Richard Stallman" in text
    assert "Grupos predefinidos" in text


def test_syllogism_cache():
    from concilio_salamanca.debate.syllogism_cache import (
        SyllogismCache,
        SyllogismReducer,
        SyllogismPattern,
        PropositionType,
        CacheEntry,
    )

    pattern = SyllogismPattern(
        major_type=PropositionType.A,
        minor_type=PropositionType.A,
        conclusion_type=PropositionType.A,
        figure=1,
        subject="codigo_inseguro",
        predicate="condenable",
        middle="sin_validacion",
    )

    rel, result = pattern.to_set_relation()
    assert rel is not None
    assert "SUBSET" in result or "subset" in result.lower()

    compressed = SyllogismReducer.compress_to_set(pattern)
    assert "Barbara" in compressed

    fp = pattern.fingerprint()
    assert len(fp) == 16

    import tempfile
    import os

    tmp = os.path.join(tempfile.gettempdir(), "test_syl_cache.json")
    cache = SyllogismCache(cache_path=tmp)
    cached = cache.lookup(pattern)
    assert cached is None

    entry = CacheEntry(
        fingerprint=fp,
        pattern=pattern,
        set_relation=result,
        conclusion_text="El codigo es condenable",
        agent="Promotor Fidei",
        timestamp=0,
    )
    cache.entries[fp] = entry
    cache.save()

    cache2 = SyllogismCache(cache_path=tmp)
    found = cache2.lookup(pattern)
    assert found is not None

    if os.path.exists(tmp):
        os.remove(tmp)


def test_syllogism_trinivel():
    from concilio_salamanca.debate.syllogism_cache import (
        SyllogismReducer,
        SyllogismPattern,
        PropositionType,
    )

    pattern = SyllogismPattern(
        major_type=PropositionType.A,
        minor_type=PropositionType.A,
        conclusion_type=PropositionType.A,
        figure=1,
        subject="funcion",
        predicate="defectuosa",
        middle="sin_validar",
    )

    unified = SyllogismReducer.reduce_all(pattern)
    assert unified.mode_name == "Barbara"
    assert unified.vocal_pattern == "AAA"
    assert unified.figure == 1

    assert "Todo" in unified.scholastic.premise_major_scheme
    assert "SUBSET" in unified.set_theory.conclusion_equation
    assert (
        "forall" in unified.predicate_logic.major_formula
        or "todo" in unified.predicate_logic.major_formula.lower()
    )

    assert len(unified.predicate_logic.derivation_steps) == 6

    compressed = SyllogismReducer.format_memory_compressed(unified)
    assert "Barbara" in compressed
    assert "funcion" in compressed
    assert "subset" in compressed.lower()

    full = SyllogismReducer.format_full_report(unified)
    assert "Nivel 1" in full
    assert "Nivel 2" in full
    assert "Nivel 3" in full
    assert "Aristoteles" in full
    assert "Boole" in full
    assert "Frege" in full


def test_syllogism_celarent():
    from concilio_salamanca.debate.syllogism_cache import (
        SyllogismReducer,
        SyllogismPattern,
        PropositionType,
    )

    pattern = SyllogismPattern(
        major_type=PropositionType.E,
        minor_type=PropositionType.A,
        conclusion_type=PropositionType.E,
        figure=1,
        subject="codigo",
        predicate="seguro",
        middle="validado",
    )

    unified = SyllogismReducer.reduce_all(pattern)
    assert unified.mode_name == "Celarent"
    assert unified.vocal_pattern == "EAE"

    st = unified.set_theory
    assert "empty" in st.conclusion_equation.lower()

    pt = unified.predicate_logic
    assert "not" in pt.major_formula.lower()


def test_cross_paradigm_equivalence():
    from concilio_salamanca.debate.syllogism_cache import (
        SyllogismReducer,
        SyllogismPattern,
        PropositionType,
    )

    p1 = SyllogismPattern(
        PropositionType.A, PropositionType.A, PropositionType.A, 1, "X", "Y", "Z"
    )

    uf1 = SyllogismReducer.unified_fingerprint(p1)
    assert len(uf1) == 16

    assert (
        SyllogismReducer._deduce_figure(
            PropositionType.A, PropositionType.A, PropositionType.A
        )
        == 1
    )

    eq = SyllogismReducer.find_equivalents(p1)
    assert "Barbara (AAA-1)" in eq

    p_i = SyllogismPattern(
        PropositionType.A, PropositionType.I, PropositionType.I, 1, "A", "B", "C"
    )
    eq_i = SyllogismReducer.find_equivalents(p_i)
    assert len(eq_i) >= 4


def test_anti_patrones():
    from concilio_salamanca.reference.anti_patrones import (
        ANTI_PATRONES,
        buscar_anti_patrones,
        listar_anti_patrones,
        resumen_anti_patrones,
    )

    assert len(ANTI_PATRONES) >= 15
    assert all(ap.id.startswith("AP-") for ap in ANTI_PATRONES)

    results = buscar_anti_patrones("XSS")
    assert len(results) >= 1
    assert any("XSS" in ap.nombre for ap in results)

    criticos = listar_anti_patrones(severidad="critica")
    assert len(criticos) >= 3

    resumen = resumen_anti_patrones()
    assert "ANTI-PATRONES" in resumen
    assert "FRONTEND" in resumen


def test_componentes():
    from concilio_salamanca.reference.componentes import (
        COMPONENTES,
        buscar_componente,
        checklist_to_markdown,
        resumen_componentes,
    )

    assert len(COMPONENTES) >= 4

    btn = buscar_componente("Button")
    assert len(btn) >= 1
    assert "loading" in btn[0].checklist[0].lower()

    md = checklist_to_markdown(COMPONENTES[0])
    assert "Checklist" in md
    assert "```tsx" in md

    resumen = resumen_componentes()
    assert "COMPONENTES" in resumen


def test_determinatio_template():
    from concilio_salamanca.reference.determinatio_template import (
        format_determinatio,
    )

    ejecutivo = format_determinatio(
        modo="ejecutivo",
        quaestio="Test",
        videtur="Parece bien",
        sed_contra="Tiene fallos",
        respondeo="Corregir",
        determinatio_codici="Codigo corregido",
        veredicto_final="CONDENA",
        rondas=2,
        num_agentes=3,
    )
    assert "Auditoria de Codigo" in ejecutivo
    assert "| Veredicto |" not in ejecutivo or "Veredicto" in ejecutivo
    assert "Test" in ejecutivo

    escolastico = format_determinatio(
        modo="escolastico",
        quaestio="Test",
        videtur="Bien",
        sed_contra="Mal",
        respondeo="Corregir",
        determinatio_codici="Ok",
        veredicto_final="ABSUELVE",
        participantes="- Agente 1",
        pnc_resumen="Sin contradicciones",
    )
    assert "DETERMINATIO MAGISTRAL" in escolastico
    assert "Sic determinat Magister" in escolastico


def test_providers():
    from concilio_salamanca.debate.providers import (
        PROVIDERS,
        get_provider_info,
        list_providers,
    )

    assert "openai" in PROVIDERS
    assert "deepseek" in PROVIDERS
    assert "anthropic" in PROVIDERS
    assert "groq" in PROVIDERS
    assert "ollama" in PROVIDERS
    assert "opencode" in PROVIDERS

    assert PROVIDERS["deepseek"]["base_url"] == "https://api.deepseek.com"
    assert PROVIDERS["openai"]["env_key"] == "OPENAI_API_KEY"
    assert PROVIDERS["deepseek"]["env_key"] == "DEEPSEEK_API_KEY"

    info = get_provider_info("deepseek")
    assert info["default_model"] == "deepseek-chat"

    with pytest.raises(ValueError):
        get_provider_info("nonexistent")

    output = list_providers()
    assert "openai" in output
    assert "deepseek" in output


def test_static_analysis():
    from concilio_salamanca.debate.static_analysis import (
        analyze_code,
        format_analysis,
        auto_select_agents,
    )

    py_code = """def foo(x: int) -> int:
    if x > 0:
        return x * 2
    return 0"""

    metrics = analyze_code(py_code, "test.py")
    assert metrics["extension"] == ".py"
    assert metrics.get("ast_funciones", metrics.get("funciones_regex", 0)) >= 1
    assert metrics["complejidad_ciclomatica_aprox"] >= 1

    formatted = format_analysis(metrics)
    assert "lineas" in formatted.lower()

    agents = auto_select_agents("test.py", py_code)
    assert "promotor" in agents
    assert "defensor" in agents


def test_precedents():
    from concilio_salamanca.debate.precedents import PrecedentEngine
    from concilio_salamanca.debate.syllogism_cache import (
        SyllogismReducer,
        SyllogismPattern,
        PropositionType,
    )
    import tempfile
    import os

    tmp = os.path.join(tempfile.gettempdir(), "test_precedents.json")
    engine = PrecedentEngine(path=tmp)

    pattern = SyllogismPattern(
        PropositionType.A, PropositionType.A, PropositionType.A, 1, "X", "Y", "Z"
    )
    unified = SyllogismReducer.reduce_all(pattern)
    engine.add(unified, "CONDENA", "Test", "def foo(): pass")

    results = engine.search(["X", "Y"])
    assert len(results) >= 1

    context = engine.format_context(["X", "Y"])
    assert "PRECEDENTES" in context

    stats = engine.stats()
    assert "Precedentes" in stats

    if os.path.exists(tmp):
        os.remove(tmp)
