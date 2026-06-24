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

from langchain_openai import ChatOpenAI


def load_config(config_path: Optional[str] = None) -> dict:
    if config_path:
        path = Path(config_path)
    else:
        path = Path(__file__).parent / "config.yaml"

    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def detect_language(code: str) -> str:
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

    output = {
        "timestamp": datetime.now().isoformat(),
        "veredicto_final": determinatio.veredicto_final.value if determinatio else "ERROR",
        "determinatio": determinatio.model_dump() if determinatio else None,
    }

    if pnc:
        output["pnc_validation"] = pnc.model_dump()

    return json.dumps(output, indent=2, ensure_ascii=False, default=str)


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
        "--rounds", "-r", type=int, default=None, help="Rondas de debate"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="text",
        choices=["text", "json", "markdown"],
        help="Formato de salida",
    )
    parser.add_argument(
        "--agents", "-a",
        type=str,
        default=None,
        help="Agentes del debate (claves separadas por comas o nombre de grupo). Usa --list-agents para ver opciones.",
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
        help="Pais de origen del ingreso (si es distinto al de residencia, activa geo-arbitraje)"
    )

    args = parser.parse_args()

    if args.list_agents:
        from concilio_salamanca.agents import list_agents
        print(list_agents())
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

    cfg = load_config(args.config)
    concilio_cfg = cfg.get("concilio", {})
    debate_cfg = cfg.get("debate", {})

    model_name = args.model or concilio_cfg.get("model", "gpt-4o")
    temperature = concilio_cfg.get("temperature", 0)
    max_rounds = args.rounds or debate_cfg.get("max_rounds", 2)
    enable_pnc = not args.no_pnc and debate_cfg.get("enable_pnc", True)

    if args.interactive:
        agent_selection = prompt_agents_interactive()
    elif args.agents:
        agent_selection = [a.strip() for a in args.agents.split(",") if a.strip()]
    elif debate_cfg.get("agents"):
        agent_selection = debate_cfg["agents"]
    else:
        agent_selection = ["promotor", "defensor", "doctor", "larouche", "leon_xiii"]

    api_key = args.api_key or concilio_cfg.get("api_key") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: Se requiere OPENAI_API_KEY (variable de entorno, --api-key o config.yaml)")
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

    language = detect_language(code)

    from concilio_salamanca.agents import resolve_agents

    resolved = resolve_agents(agent_selection)
    if not resolved:
        print("Error: Ningun agente valido seleccionado. Usa --list-agents para ver opciones.")
        sys.exit(1)

    from concilio_salamanca.agents import get_agent_label

    agent_labels = [get_agent_label(k) for k in resolved]

    print(f"Concilio de Salamanca convocado.")
    print(f"  Modelo:     {model_name}")
    print(f"  Rondas:     {max_rounds}")
    print(f"  PnC:        {'Activado' if enable_pnc else 'Desactivado'}")
    print(f"  Lenguaje:   {language}")
    print(f"  Codigo:     {len(code)} caracteres")
    print(f"  Agentes ({len(agent_labels)}):")
    for lbl in agent_labels:
        print(f"    - {lbl}")
    print()

    model = ChatOpenAI(model=model_name, temperature=temperature, api_key=api_key)

    from concilio_salamanca.debate.orchestrator import DebateConfig, DebateOrchestrator

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

    formatters = {
        "json": format_output_json,
        "text": format_output_text,
        "markdown": format_output_markdown,
    }
    output = formatters[args.output](result)
    print(output)

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
