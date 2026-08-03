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

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from concilio_salamanca.cli import (  # noqa: E402
    prompt_agents_interactive,
    prompt_audit_level,
    prompt_compute_policy,
    setup_parser,
)
from concilio_salamanca.debate.formatters import (  # noqa: E402
    format_output_json,
    format_output_mermaid,
    format_output_sarif,
    format_output_executive,
    format_output_text,
    format_output_markdown,
)
from concilio_salamanca.debate.voting import build_voting_table  # noqa: E402
from concilio_salamanca.debate.orchestrator import DebateConfig, DebateOrchestrator  # noqa: E402


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
        ".py": "python",
        ".js": "javascript",
        ".mjs": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".jsx": "javascript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".ino": "c",
        ".rb": "ruby",
        ".php": "php",
        ".sql": "sql",
        ".sh": "bash",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".json": "json",
        ".xml": "xml",
        ".html": "html",
        ".css": "css",
        ".scss": "scss",
    }
    if ext in ext_map:
        return ext_map[ext]
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


def main():
    parser = setup_parser()
    args = parser.parse_args()

    if args.list_agents:
        from concilio_salamanca.agents import list_agents

        print(list_agents())
        return

    if args.list_providers:
        from concilio_salamanca.debate.providers import list_providers

        print(list_providers())
        return

    if args.check_tools:
        from concilio_salamanca.debate.tool_detection import check_prerequisites
        from concilio_salamanca.debate.mde_history_writer import HistoryWriter

        print("=== Verificacion de herramientas externas ===")
        status = check_prerequisites(verbose=True)
        print()
        for tool, ok in status.items():
            icon = "✓" if ok else "✗"
            print(f"  {icon} {tool}: {'disponible' if ok else 'no disponible'}")

        print()
        print("=== .mde_history ===")
        writer = HistoryWriter()
        checks = writer.verify_integrity()
        for check, ok in checks.items():
            icon = "✓" if ok else "✗"
            print(f"  {icon} {check}: {'OK' if ok else 'FALLO'}")
        return

    if args.history_stats:
        from concilio_salamanca.debate.mde_history_writer import HistoryWriter

        writer = HistoryWriter()
        print(writer.stats())
        return

    if args.list_model_prices:
        from concilio_salamanca.debate.model_pricing import ModelRanker

        print(ModelRanker.format_price_table())
        print()
        print(ModelRanker.list_models())
        return

    if args.list_anti_patrones:
        from concilio_salamanca.reference.anti_patrones import resumen_anti_patrones

        print(resumen_anti_patrones())
        return

    if args.list_componentes:
        from concilio_salamanca.reference.componentes import resumen_componentes

        print(resumen_componentes())
        return

    if args.command == "dashboard":
        import subprocess

        app_path = Path(__file__).parent / "dashboard" / "app.py"
        print(f"Lanzando Dashboard Streamlit: {app_path}")
        subprocess.run([sys.executable, "-m", "streamlit", "run", str(app_path)])
        return

    if args.command == "install":
        from concilio_salamanca.installer import (
            configure_mcp,
            inject_agents_md,
            copy_skill_md,
            self_test,
            uninstall,
            format_install_report,
        )
        agent = args.agent or "opencode"

        if args.uninstall:
            print(f"Desinstalando configuracion para {agent}...")
            uninstall(agent)
            print("Configuracion removida.")
            return

        print(f"Configurando Concilio para {agent}...")
        configure_mcp(agent, args.binary)
        inject_agents_md(agent)
        copy_skill_md(agent)

        if not args.skip_tests:
            print("\nEjecutando self-test...")
            results = self_test()
            print(format_install_report(results))
        return

    if args.command == "mcp-serve":
        from concilio_salamanca.mcp_server import mcp_serve
        mcp_serve()
        return

    if args.command == "license":
        from concilio_salamanca.license_generator import LicenseGenerator
        from concilio_salamanca.debate.rns_registry import RenerumRegistry

        # --- Registry subcommands ---
        if args.register:
            registry = RenerumRegistry()
            repo = args.repo or "https://github.com/user/project"
            prj = registry.register_project(args.project or "mi-proyecto", repo)
            print(f"Proyecto registrado: {prj.project_name}")
            print(f"  ID: {prj.project_id}")
            print(f"  Badge: {registry.format_badge(prj.project_id)[:80]}...")
            registry._save()
            return

        if args.bula:
            registry = RenerumRegistry()
            if not args.project:
                print("Error: necesita --project <id> para emitir una Bula")
                return
            bula = registry.issue_bula(
                args.dev or "Usuario",
                args.project,
                args.revenue or 0,
            )
            if bula:
                print(f"Bula emitida: {bula.bula_id}")
                print(f"  Titular: {bula.holder_name}")
                print(f"  Proyecto: {bula.project_id}")
                print(f"  Vigencia: {bula.issued_at} -> {bula.expires_at}")
                print(f"  Precio: ${bula.price_usd:,.2f}")
            else:
                print("No se pudo emitir la Bula. Verifica que el proyecto este registrado.")
            return

        if args.pay:
            registry = RenerumRegistry()
            payment = registry.record_payment(
                args.dev or "Usuario",
                args.project or "mi-proyecto",
                args.amount or 0,
            )
            print(f"Pago registrado: ${payment.amount_usd:,.2f}")
            print(f"  Contribucion al Fondo de Sostenibilidad: ${payment.orphan_contribution:,.2f}")
            print(f"  Proyecto: {payment.project_id}")
            return

        if args.list_registry:
            registry = RenerumRegistry()
            print(registry.summary())
            return

        # --- Generacion de licencia estandar ---
        if args.list_countries:
            countries = LicenseGenerator.list_countries()
            bm = LicenseGenerator.big_mac_price
            print("Paises con soporte PPA (precio Big Mac en $USD):")
            for c in countries:
                price = bm(c) if callable(bm) else 0
                print(f"  {c}: ${price:.2f}")
            return

        gen = LicenseGenerator(
            developer_name=args.dev,
            project_name=args.project,
            github_repo=args.repo,
            jubilee_year=args.jubilee,
            std_version=args.std,
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
            print("  (Geo-arbitraje activado: pagas segun tu capacidad real)")
        print(f"Big Mac local:     ${result['big_mac_precio']:.2f} USD")
        print(f"BME disponible:    {result['bme']} Big Macs/mes")
        print(f"Tasa aplicable:    {result['tasa']}")
        print(f"Categoria:         {result['categoria']}")
        return

    if args.command == "audit":
        from concilio_salamanca.reference.anti_patrones import (
            ANTI_PATRONES,
            listar_anti_patrones,
        )

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
                significant = [
                    w
                    for w in keywords
                    if len(w) > 3
                    and w
                    not in (
                        "como",
                        "para",
                        "del",
                        "los",
                        "las",
                        "que",
                        "con",
                        "por",
                        "una",
                        "sus",
                        "the",
                        "and",
                        "for",
                        "with",
                    )
                ]
                if any(kw in code_lower for kw in significant):
                    matches.append(ap)
                    break

        if not matches:
            print(f"No se detectaron anti-patrones en {args.file}")
            return

        print(f"Auditoria rapida de anti-patrones: {args.file}")
        print(f"Se detectaron {len(matches)} posibles anti-patrones:\n")

        for ap in matches:
            severity_icon = {
                "critica": "[CRIT]",
                "alta": "[ALTA]",
                "media": "[MED]",
                "baja": "[BAJA]",
            }.get(ap.severidad.value, "")
            print(f"  {severity_icon} {ap.id}: {ap.nombre}")
            print(f"     Dominio: {ap.dominio.value}")
            print(f"     Conclusion: {ap.conclusion[:120]}...")
            print(f"     Correccion: {ap.correccion}")
            print()
        return

    cfg = load_config(args.config)
    concilio_cfg = cfg.get("concilio", {})
    debate_cfg = cfg.get("debate", {})
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

    interactive_terminal = bool(sys.stdin.isatty() and not args.non_interactive)
    compute_cfg = cfg.get("compute", {})
    compute_policy = args.compute_policy
    priority = args.priority
    if interactive_terminal and compute_policy is None:
        compute_policy, prompted_priority = prompt_compute_policy()
        priority = priority or prompted_priority
    compute_policy = compute_policy or compute_cfg.get("non_interactive_policy", "auto")
    priority = priority or compute_cfg.get("default_priority", "cost")
    audit_level = 1 if args.fast else args.audit_level
    if audit_level is None:
        audit_level = prompt_audit_level() if interactive_terminal else 1

    from concilio_salamanca.debate.audit_profiles import get_audit_profile, select_profile_agents
    from concilio_salamanca.debate.compute_policy import ComputePolicyResolver, ComputeResolution
    from concilio_salamanca.debate.providers import create_model, resolve_api_key

    profile = get_audit_profile(audit_level)
    provider_override = args.provider_obreros or args.provider
    model_override = args.model_obreros or args.model
    if audit_level == 0:
        resolution = ComputeResolution(None, None, compute_policy, priority, "audit-level-0", True)
    else:
        resolution = ComputePolicyResolver().resolve(
            policy=compute_policy,
            priority=priority,
            provider_override=provider_override,
            model_override=model_override,
            api_key=args.api_key,
            non_interactive=not interactive_terminal,
        )
    if audit_level > 0 and resolution.static_only:
        audit_level = 0
        profile = get_audit_profile(0)
        print(f"  RESERVA: {resolution.reserve_reason}. Se ejecutará auditoría estática.")

    if args.interactive and audit_level > 0:
        requested_agents = prompt_agents_interactive()
    elif args.agents and args.agents != "auto":
        requested_agents = [value.strip() for value in args.agents.split(",") if value.strip()]
    else:
        requested_agents = None
    agent_selection = select_profile_agents(audit_level, code, language, requested_agents)

    from concilio_salamanca.agents import resolve_agents, get_agent_label

    resolved = resolve_agents(agent_selection)
    if audit_level > 0 and not resolved:
        print(
            "Error: Ningun agente valido seleccionado. Usa --list-agents para ver opciones."
        )
        sys.exit(1)

    agent_labels = [get_agent_label(key) for key in resolved]

    # Pre-debate static analysis
    static_analysis_text = ""
    if args.file and not args.code:
        from concilio_salamanca.debate.static_analysis import (
            analyze_file,
            format_analysis,
        )

        try:
            static_metrics = analyze_file(args.file)
            static_analysis_text = format_analysis(static_metrics)
            print(
                f"  Analisis estatico: {static_metrics.get('lineas', 0)} lineas, lenguaje: {language}"
            )
        except Exception as e:
            print(f"  Advertencia: No se pudo realizar el analisis estatico: {e}")

    model = None
    magister_model = None
    if not resolution.static_only:
        api_key = resolve_api_key(resolution.provider, args.api_key)
        if resolution.provider != "ollama" and not api_key:
            resolution = resolution.__class__(
                None, None, compute_policy, priority, "static-fallback", True,
                f"Falta la clave del proveedor {resolution.provider}",
            )
            audit_level = 0
            profile = get_audit_profile(0)
            agent_selection = []
            agent_labels = []
        else:
            deepseek_options = (
                {"extra_body": {"thinking": {"type": "disabled"}}}
                if resolution.provider == "deepseek" and priority == "cost" else {}
            )
            model = create_model(
                provider=resolution.provider,
                model=resolution.model,
                temperature=concilio_cfg.get("temperature", 0),
                base_url=args.base_url or concilio_cfg.get("base_url") or None,
                api_key=api_key,
                **deepseek_options,
            )
            magister_model = model
            if args.provider_magister or args.model_magister:
                magister_resolution = ComputePolicyResolver().resolve(
                    policy=compute_policy, priority=priority,
                    provider_override=args.provider_magister or resolution.provider,
                    model_override=args.model_magister,
                    api_key=args.api_key, non_interactive=not interactive_terminal,
                )
                magister_key = resolve_api_key(magister_resolution.provider, args.api_key)
                magister_model = create_model(
                    provider=magister_resolution.provider, model=magister_resolution.model,
                    temperature=0, base_url=args.base_url, api_key=magister_key,
                )

    if args.cache_stats:
        from concilio_salamanca.debate.syllogism_cache import get_syllogism_cache

        cache = get_syllogism_cache()
        print(cache.summary())
        print()

    # Recuperar sólo contexto local acotado para niveles que usan LLM.
    from concilio_salamanca.debate.precedents import get_precedent_engine

    precedent_engine = get_precedent_engine()
    precedent_context = ""
    try:
        if audit_level == 0:
            raise RuntimeError("nivel estatico")
        query_terms = [language]
        if args.file:
            query_terms.append(os.path.basename(args.file))
        precedent_context = precedent_engine.format_context(query_terms, max_results=3)
        if precedent_context:
            print(
                f"  Precedentes: {len(precedent_engine.precedents)} disponibles, contexto inyectado."
            )
    except Exception:
        pass

    # Gather git/mde history context for process-oriented agents
    git_context = ""
    try:
        if audit_level == 0:
            git_context = ""
        else:
            from concilio_salamanca.debate.git_history import format_git_context

            project_path = os.path.dirname(args.file) if args.file else "."
            git_context = format_git_context(project_path, n=15)
            if git_context:
                print("  Contexto Git/MDE History cargado.")
    except Exception as e:
        print(f"  Advertencia: No se pudo cargar contexto git: {e}")

    debate_mode = args.mode or debate_cfg.get("mode", "auto")

    config = DebateConfig(
        max_rounds=profile.max_rounds,
        include_pnc_validation=not args.no_pnc and debate_cfg.get("enable_pnc", True),
        agents=agent_selection,
        parallel=False,
        mode=debate_mode,
        refine_design=args.refine_design,
        enable_ockham=args.ockham,
        save_history=args.save_history,
        auto_save_history=args.auto_save_history,
        audit_level=audit_level,
        token_budget=max(0, args.token_budget if args.token_budget is not None else int(cfg.get("budget", {}).get("default_token_budget", 0))),
        model_name=resolution.model or "static",
        escalation_candidates=cfg.get("frontier", {}).get("candidates", ["gpt-5.6-terra", "gpt-5.6-sol"]),
        reserve_reason=resolution.reserve_reason or "",
    )
    orchestrator = DebateOrchestrator(model=model, magister_model=magister_model, config=config)
    result = orchestrator.run_debate(
        code,
        language,
        static_analysis_text=static_analysis_text,
        precedent_context=precedent_context,
        git_context=git_context,
    )

    escalation = result.get("escalation")
    if interactive_terminal and escalation and escalation.get("requires_user_decision"):
        print("\nEscalamiento opcional (no ejecutado):")
        print(f"  Motivos: {', '.join(escalation.get('reasons', []))}")
        print(f"  Agentes: {', '.join(escalation.get('agents_to_repeat', [])) or 'hasta dos especialistas'}")
        print(f"  Modelos/costo estimado USD: {escalation.get('estimated_cost_usd', {})}")
        print(f"  Máximo de salida por llamada: {escalation.get('max_tokens', 0)} tokens")
        try:
            approve = input("¿Autorizar un modelo frontera para esta decisión? [s/N] > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            approve = ""
        if approve in {"s", "si", "sí", "y", "yes"}:
            candidates = escalation.get("candidates", [])
            candidate = candidates[0] if candidates else "gpt-5.6-terra"
            try:
                chosen = input(f"Modelo [{candidate}] > ").strip()
            except (EOFError, KeyboardInterrupt):
                chosen = ""
            if chosen in candidates:
                candidate = chosen
            frontier_key = resolve_api_key("openai")
            if frontier_key:
                frontier_model = create_model("openai", candidate, api_key=frontier_key, temperature=0)
                result = orchestrator.resume_with_frontier(
                    result, frontier_model,
                    decision_id=escalation["decision_id"], candidate=candidate,
                )
            else:
                print("  No se ejecutó frontera: falta OPENAI_API_KEY.")

    voting = result["voting"] if "voting" in result else build_voting_table(result)
    result["voting"] = voting

    # Store precedents from this debate for future use
    if result.get("determinatio"):
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
        output = format_output_executive(result, agent_labels, profile.max_rounds, voting)
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
        from concilio_salamanca.debate.syllogism_cache import (
            SyllogismReducer,
            get_syllogism_cache,
        )

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
        ext = {"json": ".json", "text": ".txt", "markdown": ".md", "mermaid": ".md", "sarif": ".sarif"}[args.output]
        filename = f"veredicto_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        filepath = Path(save_dir) / filename
        filepath.write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()
