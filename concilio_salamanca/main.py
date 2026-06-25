#!/usr/bin/env python3
"""
Concilio de Salamanca - Sistema de Auditoria de Codigo por Meta Dialectica Escolastica (MDE)

Uso:
    python main.py --code "print('hello')"
    python main.py --file app.js --rounds 3 --model gpt-4o
    python main.py --file app.js --output json
    python main.py --file app.js --agents promotor,linus,stallman
    python main.py --file app.js --agents acusacion
    python main.py --list-agents
    python main.py license --country MX --dev "Mi Nombre" --project "Mi App"
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import yaml

from langchain_core.language_models import BaseChatModel


def load_config(config_path: Optional[str] = None) -> dict:
    if config_path:
        path = Path(config_path)
    else:
        path = Path(__file__).parent / "config.yaml"

    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def detect_language(code: str, filepath: str = "") -> str:
    ext = os.path.splitext(filepath)[1].lower() if filepath else ""
    ext_map = {
        ".py": "python", ".js": "javascript", ".mjs": "javascript",
        ".ts": "typescript", ".tsx": "typescript", ".jsx": "javascript",
        ".java": "java", ".go": "go", ".rs": "rust",
        ".c": "c", ".cpp": "cpp", ".h": "c", ".hpp": "cpp",
        ".ino": "c", ".rb": "ruby", ".php": "php",
        ".sql": "sql", ".sh": "bash", ".yaml": "yaml",
        ".yml": "yaml", ".json": "json", ".xml": "xml",
        ".html": "html", ".css": "css", ".scss": "scss",
    }
    if ext in ext_map:
        return ext_map[ext]
    code_lower = code.strip().lower()
    if "def " in code or "import " in code or "print(" in code:
        return "python"
    if "function " in code or "const " in code or "=>" in code or "require(" in code:
        return "javascript"
    if "public class" in code or "System.out" in code:
        return "java"
    if "package " in code and "func " in code:
        return "go"
    if "fn " in code or "let mut" in code or "impl " in code:
        return "rust"
    if "#include" in code and ("int main" in code or "cout" in code):
        return "cpp"
    return "auto"


def format_output_json(result: dict) -> str:
    determinatio = result.get("determinatio")
    pnc = result.get("pnc_validation")
    voting = result.get("voting", {})

    output = {
        "timestamp": datetime.now().isoformat(),
        "veredicto_final": determinatio.veredicto_final.value if determinatio else "ERROR",
        "determinatio": determinatio.model_dump() if determinatio else None,
        "voting": voting,
    }

    if pnc:
        output["pnc_validation"] = pnc.model_dump()

    return json.dumps(output, indent=2, ensure_ascii=False, default=str)


def format_output_mermaid(result: dict) -> str:
    from concilio_salamanca.agents import get_agent_label

    determinatio = result.get("determinatio")
    pnc = result.get("pnc_validation")
    state = result.get("state", {})
    history = state.get("arguments_history", [])

    lines = ["```mermaid", "graph TD"]
    lines.append("  START[/Codigo Fuente/] --> R1[Ronda 1]")

    seen_agents = set()
    for round_data in history:
        r = round_data.get("round", 1)
        for agent_name_raw in round_data.get("arguments", {}):
            label = agent_name_raw
            safe = label.replace(" ", "_").replace("(", "").replace(")", "").replace(".", "")
            if safe not in seen_agents:
                verdict = "RESERVA"
                color = "#f0c040"
                for agent_output_dict in []:
                    pass
                lines.append(f'  R{r} --> {safe}["{label[:30]}"]')
                lines.append(f'  style {safe} fill:{color}')
                seen_agents.add(safe)

    if pnc and pnc.hay_contradicciones:
        for c in pnc.contradicciones:
            a = c.agente_a.replace(" ", "_").replace("(", "").replace(")", "")
            b = c.agente_b.replace(" ", "_").replace("(", "").replace(")", "")
            lines.append(f'  {a} -.->|contradice| {b}')
            lines.append(f'  linkStyle {len(lines)-3} stroke:red')

    verdict_color = {"CONDENA": "#c00000", "ABSUELVE": "#00a000", "RESERVA": "#f0c040"}
    v = determinatio.veredicto_final.value if determinatio else "RESERVA"
    lines.append(f'  R{len(history)} --> MAG[/Magister: {v}/]')
    lines.append(f'  style MAG fill:{verdict_color.get(v, "#f0c040")},color:white')
    lines.append("```")

    return "\n".join(lines)


def format_output_sarif(result: dict, filepath: str = "") -> str:
    determinatio = result.get("determinatio")

    run = {
        "tool": {"driver": {"name": "Concilio de Salamanca MDE", "informationUri": "https://github.com/concilio-salamanca"}},
        "results": [],
    }

    if determinatio:
        level = "error" if determinatio.veredicto_final.value == "CONDENA" else "warning"
        run["results"].append({
            "ruleId": f"MDE-{determinatio.veredicto_final.value}",
            "level": level,
            "message": {"text": determinatio.determinatio_codici[:500]},
            "locations": [{"physicalLocation": {"artifactLocation": {"uri": filepath or "codigo"}}}],
        })

    report = {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [run],
    }

    return json.dumps(report, indent=2, ensure_ascii=False)


def build_voting_table(result: dict) -> dict:
    state = result.get("state", {})
    history = state.get("arguments_history", [])

    votes = {"CONDENA": 0, "ABSUELVE": 0, "RESERVA": 0}
    agent_votes = []

    for round_data in history:
        for name, raw in round_data.get("arguments", {}).items():
            raw_upper = raw.upper() if hasattr(raw, "upper") else ""
            for v in ["CONDENA", "ABSUELVE", "RESERVA"]:
                if v in raw_upper:
                    votes[v] += 1
                    agent_votes.append({"agente": name, "veredicto": v})
                    break
            else:
                votes["RESERVA"] += 1
                agent_votes.append({"agente": name, "veredicto": "RESERVA"})

    total = sum(votes.values()) or 1
    majority = max(votes, key=votes.get)
    consensus = votes[majority] / total >= 0.67

    return {
        "votos": votes,
        "agentes": agent_votes,
        "consenso": consensus,
        "mayoria": majority,
        "total": total,
    }


def format_output_executive(result: dict, agent_labels: list, rounds: int, voting: dict = None) -> str:
    from concilio_salamanca.reference.determinatio_template import format_determinatio

    determinatio = result.get("determinatio")
    pnc = result.get("pnc_validation")

    if not determinatio:
        return "Error: No se pudo generar la determinatio."

    pnc_resumen = "Sin contradicciones detectadas."
    num_contradicciones = 0
    if pnc and pnc.hay_contradicciones:
        num_contradicciones = len(pnc.contradicciones)
        pnc_resumen = f"{num_contradicciones} contradiccion(es) detectada(s): " + "; ".join(
            f"{c.agente_a} vs {c.agente_b}" for c in pnc.contradicciones
        )

    participantes_text = "\n".join(f"- {label}" for label in agent_labels)

    return format_determinatio(
        modo="ejecutivo",
        quaestio=determinatio.quaestio,
        videtur=determinatio.videtur,
        sed_contra=determinatio.sed_contra,
        respondeo=determinatio.respondeo,
        determinatio_codici=determinatio.determinatio_codici,
        veredicto_final=determinatio.veredicto_final.value,
        participantes=participantes_text,
        pnc_resumen=pnc_resumen,
        rondas=rounds,
        num_agentes=len(agent_labels),
        num_contradicciones=num_contradicciones,
    )


def format_output_text(result: dict) -> str:
    determinatio = result.get("determinatio")
    pnc = result.get("pnc_validation")

    if not determinatio:
        return "Error: No se pudo generar la determinatio."

    lines = [
        "=" * 70,
        "  CONCILIO DE SALAMANCA - DETERMINATIO MAGISTRAL",
        "=" * 70,
        "",
        "QUAESTIO:",
        f"  {determinatio.quaestio}",
        "",
        "VIDETUR (lo que parece):",
        f"  {determinatio.videtur}",
        "",
        "SED CONTRA (argumentos en contra):",
        f"  {determinatio.sed_contra}",
        "",
        "RESPONDEO (resolucion razonada):",
        f"  {determinatio.respondeo}",
        "",
        "DETERMINATIO CODICI (veredicto final):",
        f"  {determinatio.determinatio_codici}",
        "",
        f"VEREDICTO: {determinatio.veredicto_final.value}",
    ]

    if pnc and pnc.hay_contradicciones:
        lines.append("")
        lines.append("ADVERTENCIA DEL PnC:")
        for c in pnc.contradicciones:
            lines.append(
                f"  Contradiccion: {c.agente_a} vs {c.agente_b}: {c.descripcion}"
            )

    lines.append("")
    lines.append("=" * 70)
    lines.append(
        "  *Sic determinat Magister. Causa finita est.*"
    )
    lines.append("=" * 70)

    return "\n".join(lines)


def format_output_markdown(result: dict) -> str:
    determinatio = result.get("determinatio")
    pnc = result.get("pnc_validation")

    if not determinatio:
        return "**Error:** No se pudo generar la determinatio."

    md = [
        "# Determinatio del Concilio de Salamanca",
        "",
        f"**Veredicto:** `{determinatio.veredicto_final.value}`",
        "",
        "## Quaestio",
        determinatio.quaestio,
        "",
        "## Videtur",
        determinatio.videtur,
        "",
        "## Sed Contra",
        determinatio.sed_contra,
        "",
        "## Respondeo",
        determinatio.respondeo,
        "",
        "## Determinatio Codici",
        determinatio.determinatio_codici,
    ]

    if pnc and pnc.hay_contradicciones:
        md.append("")
        md.append("## Validacion del Principio de No Contradiccion")
        md.append(f"Se detectaron {len(pnc.contradicciones)} contradiccion(es):")
        for c in pnc.contradicciones:
            md.append(f"- **{c.agente_a}** vs **{c.agente_b}**: {c.descripcion}")

    md.append("")
    md.append("---")
    md.append("*Sic determinat Magister. Causa finita est.*")

    return "\n".join(md)


def prompt_agents_interactive() -> List[str]:
    from concilio_salamanca.agents import AGENT_REGISTRY, AGENT_GROUPS, get_agent_label

    print("\nSelecciona los agentes que participaran en el Concilio:")
    print("  - Escribe las claves separadas por comas (ej: promotor,linus,stallman)")
    print("  - O usa un grupo predefinido (ej: escolasticos, pragmaticos, todos)")
    print()
    print("Grupos disponibles:")
    for group, members in AGENT_GROUPS.items():
        print(f"  {group:15s} = {', '.join(members)}")
    print()
    print("Agentes disponibles:")
    for key, (label, _) in AGENT_REGISTRY.items():
        print(f"  {key:15s} - {label}")
    print()
    print("Default: promotor,defensor,doctor,larouche,leon_xiii")
    print()

    try:
        raw = input("Agentes > ").strip()
    except (EOFError, KeyboardInterrupt):
        return ["promotor", "defensor", "doctor", "larouche", "leon_xiii"]

    if not raw:
        return ["promotor", "defensor", "doctor", "larouche", "leon_xiii"]

    return [a.strip() for a in raw.split(",") if a.strip()]


def main():
    parser = argparse.ArgumentParser(
        description="Concilio de Salamanca - Auditoria MDE de Codigo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--code", "-c", type=str, help="Codigo a analizar (string directo)"
    )
    parser.add_argument(
        "--file", "-f", type=str, help="Archivo de codigo a analizar"
    )
    parser.add_argument(
        "--model", "-m", type=str, default=None, help="Modelo LLM a usar"
    )
    parser.add_argument(
        "--provider", type=str, default=None,
        choices=["openai", "deepseek", "anthropic", "groq", "ollama", "opencode"],
        help="Proveedor LLM (openai, deepseek, anthropic, groq, ollama, opencode)",
    )
    parser.add_argument(
        "--base-url", type=str, default=None,
        help="URL base del endpoint (para proxies o self-hosted)",
    )
    parser.add_argument(
        "--list-providers", action="store_true",
        help="Listar proveedores LLM soportados y salir",
    )
    parser.add_argument(
        "--rounds", "-r", type=int, default=None, help="Rondas de debate"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="text",
        choices=["text", "json", "markdown", "mermaid", "sarif"],
        help="Formato de salida",
    )
    parser.add_argument(
        "--agents", "-a",
        type=str,
        default=None,
        help="Agentes del debate (claves separadas por comas o nombre de grupo). Usa --list-agents para ver opciones.",
    )
    parser.add_argument(
        "--mode", type=str, default="escolastico",
        choices=["escolastico", "ejecutivo"],
        help="Modo de salida: escolastico (completo) o ejecutivo (informe tecnico reducido)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Mostrar reporte trinivel de silogismos (escolastico, conjuntos, predicados)",
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Seleccion interactiva de agentes",
    )
    parser.add_argument(
        "--list-agents",
        action="store_true",
        help="Listar agentes y grupos disponibles y salir",
    )
    parser.add_argument(
        "--list-anti-patrones",
        action="store_true",
        help="Listar catalogo de anti-patrones y salir",
    )
    parser.add_argument(
        "--list-componentes",
        action="store_true",
        help="Listar ejemplos de componentes de referencia y salir",
    )
    parser.add_argument(
        "--no-pnc",
        action="store_true",
        help="Deshabilitar validacion del Principio de No Contradiccion",
    )
    parser.add_argument(
        "--config", type=str, default=None, help="Archivo de configuracion YAML"
    )
    parser.add_argument(
        "--api-key", type=str, default=None, help="API key de OpenAI"
    )
    parser.add_argument(
        "--save", "-s", type=str, default=None, help="Guardar veredicto en archivo"
    )
    parser.add_argument(
        "--cache-stats",
        action="store_true",
        help="Mostrar estadisticas del cache de silogismos",
    )

    subparsers = parser.add_subparsers(dest="command", help="Comandos adicionales")

    license_parser = subparsers.add_parser(
        "license", help="Generar Licencia Rerum Novarum"
    )
    license_parser.add_argument(
        "--country", type=str, default="US", help="Codigo de pais para umbrales PPA"
    )
    license_parser.add_argument(
        "--dev", type=str, default="", help="Nombre del desarrollador"
    )
    license_parser.add_argument(
        "--project", type=str, default="", help="Nombre del proyecto"
    )
    license_parser.add_argument(
        "--repo", type=str, default="", help="URL del repositorio GitHub (para clausula Auto-Favorito)"
    )
    license_parser.add_argument(
        "--save", "-s", type=str, default=None, help="Guardar licencia en archivo"
    )
    license_parser.add_argument(
        "--list-countries",
        action="store_true",
        help="Listar paises con soporte PPA",
    )

    bme_parser = subparsers.add_parser(
        "bme", help="Calcular Big Mac Equivalents (Precio Justo)"
    )
    bme_parser.add_argument(
        "--income", type=float, required=True, help="Ingreso bruto mensual en USD"
    )
    bme_parser.add_argument(
        "--residence", type=str, required=True, help="Pais de residencia (codigo ISO)"
    )
    bme_parser.add_argument(
        "--income-country", type=str, default=None,
        help="Pais de origen del ingreso (si es distinto al de residencia, activa geo-arbitraje)",
    )

    audit_parser = subparsers.add_parser(
        "audit", help="Escanear codigo en busca de anti-patrones conocidos (sin LLM)"
    )
    audit_parser.add_argument(
        "--file", "-f", type=str, required=True, help="Archivo a escanear"
    )
    audit_parser.add_argument(
        "--domain", type=str, default=None,
        choices=["frontend", "backend", "seguridad", "rendimiento", "datos", "fullstack"],
        help="Filtrar por dominio",
    )

    args = parser.parse_args()

    if args.list_agents:
        from concilio_salamanca.agents import list_agents
        print(list_agents())
        return

    if args.list_providers:
        from concilio_salamanca.debate.providers import list_providers
        print(list_providers())
        return

    if args.list_anti_patrones:
        from concilio_salamanca.reference.anti_patrones import resumen_anti_patrones
        print(resumen_anti_patrones())
        return

    if args.list_componentes:
        from concilio_salamanca.reference.componentes import resumen_componentes
        print(resumen_componentes())
        return

    if args.command == "license":
        from concilio_salamanca.license_generator import LicenseGenerator

        if args.list_countries:
            countries = LicenseGenerator.list_countries()
            print("Paises con soporte PPA:")
            for c in countries:
                from concilio_salamanca.license_generator import PPA_TABLE
                print(f"  {c}: factor {PPA_TABLE[c]:.2f}")
            return

        gen = LicenseGenerator(
            developer_name=args.dev,
            project_name=args.project,
            github_repo=args.repo,
        )
        license_text = gen.generate_license(args.country)

        if args.save:
            gen.save_license(args.save, args.country)
            print(f"Licencia guardada en: {args.save}")
        else:
            print(license_text)
        return

    if args.command == "bme":
        from concilio_salamanca.license_generator import LicenseGenerator

        result = LicenseGenerator.calculate_bme(
            monthly_income_usd=args.income,
            residence_country=args.residence,
            income_country=args.income_country,
        )
        print(f"Ingreso mensual:   ${args.income:,.2f} USD")
        print(f"Residencia:        {args.residence.upper()}")
        if args.income_country:
            print(f"Origen del ingreso: {args.income_country.upper()}")
            print(f"  (Geo-arbitraje activado: pagas segun tu capacidad real)")
        print(f"Big Mac local:     ${result['big_mac_precio']:.2f} USD")
        print(f"BME disponible:    {result['bme']} Big Macs/mes")
        print(f"Tasa aplicable:    {result['tasa']}")
        print(f"Categoria:         {result['categoria']}")
        return

    if args.command == "audit":
        from concilio_salamanca.reference.anti_patrones import ANTI_PATRONES, listar_anti_patrones

        filepath = Path(args.file)
        if not filepath.exists():
            print(f"Error: Archivo no encontrado: {args.file}")
            sys.exit(1)

        code = filepath.read_text(encoding="utf-8")
        code_lower = code.lower()

        if args.domain:
            candidates = listar_anti_patrones(dominio=args.domain)
        else:
            candidates = ANTI_PATRONES

        matches = []
        for ap in candidates:
            for sintoma in ap.sintomas:
                keywords = sintoma.lower().split()
                significant = [w for w in keywords if len(w) > 3 and w not in ("como", "para", "del", "los", "las", "que", "con", "por", "una", "sus", "the", "and", "for", "with")]
                if any(kw in code_lower for kw in significant):
                    matches.append(ap)
                    break

        if not matches:
            print(f"No se detectaron anti-patrones en {args.file}")
            return

        print(f"Auditoria rapida de anti-patrones: {args.file}")
        print(f"Se detectaron {len(matches)} posibles anti-patrones:\n")

        for ap in matches:
            severity_icon = {"critica": "[CRIT]", "alta": "[ALTA]", "media": "[MED]", "baja": "[BAJA]"}.get(ap.severidad.value, "")
            print(f"  {severity_icon} {ap.id}: {ap.nombre}")
            print(f"     Dominio: {ap.dominio.value}")
            print(f"     Conclusion: {ap.conclusion[:120]}...")
            print(f"     Correccion: {ap.correccion}")
            print()
        return

    cfg = load_config(args.config)
    concilio_cfg = cfg.get("concilio", {})
    debate_cfg = cfg.get("debate", {})

    model_name = args.model or concilio_cfg.get("model", "gpt-4o")
    provider = args.provider or concilio_cfg.get("provider", "openai")
    base_url = args.base_url or concilio_cfg.get("base_url") or None
    temperature = concilio_cfg.get("temperature", 0)
    max_rounds = args.rounds or debate_cfg.get("max_rounds", 2)
    enable_pnc = not args.no_pnc and debate_cfg.get("enable_pnc", True)

    if args.interactive:
        agent_selection = prompt_agents_interactive()
    elif args.agents == "auto" or (not args.agents and args.file):
        from concilio_salamanca.debate.static_analysis import auto_select_agents

        code_for_auto = code if args.code else ""
        filepath_auto = args.file if args.file else ""
        agent_selection = auto_select_agents(filepath_auto, code_for_auto)
        print(f"  Auto-seleccion: {agent_selection}")
    elif args.agents:
        agent_selection = [a.strip() for a in args.agents.split(",") if a.strip()]
    elif debate_cfg.get("agents"):
        agent_selection = debate_cfg["agents"]
    else:
        agent_selection = ["promotor", "defensor", "doctor", "larouche", "leon_xiii"]

    from concilio_salamanca.debate.providers import create_model, resolve_api_key

    api_key = resolve_api_key(provider, args.api_key)
    if not api_key and provider not in ("ollama",):
        env_key = {"openai": "OPENAI_API_KEY", "deepseek": "DEEPSEEK_API_KEY",
                    "anthropic": "ANTHROPIC_API_KEY", "groq": "GROQ_API_KEY"}.get(provider, "API_KEY")
        print(f"Error: Se requiere {env_key} (variable de entorno, --api-key o config.yaml)")
        sys.exit(1)

    if args.code:
        code = args.code
    elif args.file:
        filepath = Path(args.file)
        if not filepath.exists():
            print(f"Error: Archivo no encontrado: {args.file}")
            sys.exit(1)
        code = filepath.read_text(encoding="utf-8")
    else:
        print("Error: Debes proporcionar --code o --file")
        sys.exit(1)

    language = detect_language(code, args.file or "")

    from concilio_salamanca.agents import resolve_agents

    resolved = resolve_agents(agent_selection)
    if not resolved:
        print("Error: Ningun agente valido seleccionado. Usa --list-agents para ver opciones.")
        sys.exit(1)

    from concilio_salamanca.agents import get_agent_label

    agent_labels = [get_agent_label(k) for k in resolved]

    print(f"Concilio de Salamanca convocado.")
    print(f"  Proveedor:  {provider}")
    print(f"  Modelo:     {model_name}")
    print(f"  Modo:       {args.mode}")
    print(f"  Rondas:     {max_rounds}")
    print(f"  PnC:        {'Activado' if enable_pnc else 'Desactivado'}")
    print(f"  Lenguaje:   {language}")
    print(f"  Codigo:     {len(code)} caracteres")
    print(f"  Agentes ({len(agent_labels)}):")
    for lbl in agent_labels:
        print(f"    - {lbl}")
    print()

    model = create_model(
        provider=provider,
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
    )

    from concilio_salamanca.debate.orchestrator import DebateConfig, DebateOrchestrator

    static_analysis_text = ""
    if args.file and not args.code:
        from concilio_salamanca.debate.static_analysis import analyze_file, format_analysis
        try:
            static_metrics = analyze_file(args.file)
            static_analysis_text = format_analysis(static_metrics)
            print(f"  Static: {static_metrics.get('lineas_totales', '?')} lineas, "
                  f"complejidad ~{static_metrics.get('complejidad_ciclomatica_aprox', '?')}")
        except Exception:
            pass

    if args.cache_stats:
        from concilio_salamanca.debate.syllogism_cache import get_syllogism_cache
        cache = get_syllogism_cache()
        print(cache.summary())
        print()

    config = DebateConfig(
        max_rounds=max_rounds,
        include_pnc_validation=enable_pnc,
        agents=agent_selection,
    )
    orchestrator = DebateOrchestrator(model, config)
    result = orchestrator.run_debate(code, language)

    voting = build_voting_table(result)
    result["voting"] = voting

    from concilio_salamanca.debate.precedents import get_precedent_engine
    precedent_engine = get_precedent_engine()
    if result.get("determinatio"):
        terms = [language, result["determinatio"].veredicto_final.value]
        precedent_engine.add_precedent_from_result(result)

    if args.output == "mermaid":
        output = format_output_mermaid(result)
        print(output)
        return

    if args.output == "sarif":
        output = format_output_sarif(result, args.file or "stdin")
        print(output)
        return

    if args.mode == "ejecutivo" and args.output == "text":
        output = format_output_executive(result, agent_labels, max_rounds, voting)
    else:
        formatters = {
            "json": format_output_json,
            "text": format_output_text,
            "markdown": format_output_markdown,
        }
        output = formatters[args.output](result)
    print(output)

    if args.verbose:
        print("\n" + "=" * 70)
        print("REPORTE TRINIVEL DE SILOGISMOS")
        print("=" * 70)
        from concilio_salamanca.debate.syllogism_cache import SyllogismReducer, get_syllogism_cache
        cache = get_syllogism_cache()
        for key, unified in cache.unified_store.items():
            report = SyllogismReducer.format_full_report(unified)
            print(report)
            print()

    if args.save:
        Path(args.save).write_text(output, encoding="utf-8")
        print(f"\nVeredicto guardado en: {args.save}")

    save_dir = cfg.get("output", {}).get("save_dir")
    if save_dir:
        Path(save_dir).mkdir(parents=True, exist_ok=True)
        ext = {"json": ".json", "text": ".txt", "markdown": ".md"}[args.output]
        filename = f"veredicto_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        filepath = Path(save_dir) / filename
        filepath.write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()
