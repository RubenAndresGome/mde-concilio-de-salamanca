"""
MCP Server — Exponer herramientas del Concilio via JSON-RPC stdio.

El servidor MCP expone las siguientes herramientas:
  - list_agents: Lista los 40 agentes del Concilio
  - run_audit: Ejecuta una auditoria completa (silogismos + veredicto)
  - audit_antipatterns: Escanea anti-patrones sin LLM
  - generate_license: Genera licencia RNS v5.0
  - check_tools: Verifica herramientas externas
  - history_stats: Estadisticas de .mde_history/
  - propose_dogma / resolve_dogma: Ordenes coherentes y contradicciones
  - exhaust_cases: Preguntas casuisticas acotadas
  - graph_remember / graph_context: Memoria SQLite local

Uso:
  concilio mcp-serve          # Inicia servidor MCP via stdio
  echo '{"method":"tools/list"}' | concilio mcp-serve  # Listar herramientas
"""

from __future__ import annotations

import json
from typing import Any, Dict


MCP_TOOLS = [
    {
        "name": "list_agents",
        "description": "Lista los 40 agentes del Concilio de Salamanca con sus grupos",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "run_audit",
        "description": "Ejecuta una auditoria de codigo con los agentes seleccionados",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Codigo fuente a auditar"},
                "language": {"type": "string", "description": "Lenguaje (python, javascript, etc.)", "default": "auto"},
                "agents": {"type": "string", "description": "Agentes o grupo (ej: escolasticos, logici)", "default": "escolasticos"},
                "mode": {"type": "string", "enum": ["escolastico", "ejecutivo", "sdd", "pdca", "auto"], "default": "auto"},
                "audit_level": {"type": "integer", "minimum": 0, "maximum": 3, "default": 1},
                "compute_policy": {"type": "string", "enum": ["local", "cloud", "auto"], "default": "auto"},
                "priority": {"type": "string", "enum": ["cost", "quality"], "default": "cost"},
                "token_budget": {"type": "integer", "minimum": 0, "default": 0},
                "provider": {"type": "string", "description": "Override explícito"},
                "model": {"type": "string", "description": "Override explícito"},
                "frontier_decision": {
                    "type": "object",
                    "properties": {
                        "decision_id": {"type": "string"},
                        "approved": {"type": "boolean"},
                        "candidate": {"type": "string"}
                    }
                },
                "objective": {"type": "string", "description": "Objetivo del Dogma"},
                "orders": {"type": "array", "items": {"type": "string"}, "description": "Ordenes del usuario que deben ser coherentes"},
            },
            "required": ["code"],
        },
    },
    {
        "name": "propose_dogma",
        "description": "Detecta contradicciones entre ordenes antes de gastar tokens y crea un Dogma si son coherentes",
        "inputSchema": {
            "type": "object",
            "properties": {
                "orders": {"type": "array", "items": {"type": "string"}},
                "objective": {"type": "string", "default": ""},
                "db_path": {"type": "string"},
            },
            "required": ["orders"],
        },
    },
    {
        "name": "resolve_dogma",
        "description": "Resuelve un Dogma contradictorio conservando las ordenes elegidas por el usuario",
        "inputSchema": {
            "type": "object",
            "properties": {
                "dogma_id": {"type": "integer"},
                "keep_order_ids": {"type": "array", "items": {"type": "integer"}},
                "objective": {"type": "string"},
                "db_path": {"type": "string"},
            },
            "required": ["dogma_id", "keep_order_ids", "objective"],
        },
    },
    {
        "name": "exhaust_cases",
        "description": "Formula preguntas casuisticas por clases de riesgo con un limite estricto",
        "inputSchema": {
            "type": "object",
            "properties": {
                "context": {"type": "string", "default": ""},
                "answered": {"type": "array", "items": {"type": "string"}},
                "limit": {"type": "integer", "minimum": 1, "maximum": 10, "default": 8},
            },
        },
    },
    {
        "name": "graph_remember",
        "description": "Guarda un nodo o relacion en el grafo SQLite local sin invocar un LLM",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string"}, "kind": {"type": "string"},
                "label": {"type": "string"}, "payload": {"type": "object"},
                "source": {"type": "string"}, "target": {"type": "string"},
                "relation": {"type": "string"}, "weight": {"type": "number", "default": 1.0},
                "db_path": {"type": "string"},
            },
            "required": ["id", "kind", "label"],
        },
    },
    {
        "name": "graph_context",
        "description": "Recupera contexto local FTS5 y multi-salto del grafo con presupuesto limitado",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}, "limit": {"type": "integer", "default": 8},
                "hops": {"type": "integer", "minimum": 0, "maximum": 3, "default": 1},
                "db_path": {"type": "string"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "context_sieve",
        "description": "Recorta código y diagnósticos al contexto de riesgo antes de invocar un LLM",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string"}, "diagnostics": {"type": "string"},
                "max_chars": {"type": "integer", "minimum": 512, "maximum": 50000, "default": 12000}
            },
            "required": ["code"]
        },
    },
    {
        "name": "security_diff",
        "description": "Decide sin LLM si un diff requiere especialistas de seguridad",
        "inputSchema": {
            "type": "object", "properties": {"diff": {"type": "string"}}, "required": ["diff"]
        },
    },
    {
        "name": "test_impact",
        "description": "Selecciona sólo pruebas afectadas mediante rutas y aristas de dependencia",
        "inputSchema": {
            "type": "object",
            "properties": {
                "changed_files": {"type": "array", "items": {"type": "string"}},
                "test_files": {"type": "array", "items": {"type": "string"}},
                "dependency_edges": {"type": "object"}
            },
            "required": ["changed_files", "test_files"]
        },
    },
    {
        "name": "debug_evidence",
        "description": "Comprime error, traza mínima e hipótesis verificables",
        "inputSchema": {
            "type": "object",
            "properties": {
                "error": {"type": "string"}, "traceback": {"type": "string"},
                "hypotheses": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["error"]
        },
    },
    {
        "name": "audit_antipatterns",
        "description": "Escanea codigo en busca de anti-patrones conocidos (sin LLM, gratuito)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Codigo fuente a escanear"},
                "domain": {"type": "string", "enum": ["frontend", "backend", "seguridad", "rendimiento", "datos", "fullstack"]},
            },
            "required": ["code"],
        },
    },
    {
        "name": "generate_license",
        "description": "Genera una licencia Rerum Novarum Statuto v5.0",
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "default": "US", "description": "Codigo de pais (MX, US, AR, etc.)"},
                "developer": {"type": "string", "default": "", "description": "Nombre del desarrollador"},
                "project": {"type": "string", "default": "", "description": "Nombre del proyecto"},
                "repo": {"type": "string", "default": "", "description": "URL del repositorio GitHub"},
                "jubilee_year": {"type": "integer", "description": "Ano de ultima version major"},
                "std": {"type": "boolean", "default": False, "description": "Marcar como version STD"},
            },
        },
    },
    {
        "name": "check_tools",
        "description": "Verifica herramientas externas (CBMM, Spec-Kit, Open-Design) e integridad de .mde_history/",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "history_stats",
        "description": "Muestra estadisticas de .mde_history/ (sesiones, PDCA files, metricas)",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def handle_list_tools(_params: Dict[str, Any]) -> Dict[str, Any]:
    return {"tools": MCP_TOOLS}


def handle_call_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    if tool_name == "list_agents":
        from concilio_salamanca.agents import list_agents as la
        return {"content": [{"type": "text", "text": la()}]}

    elif tool_name == "run_audit":
        code = args.get("code", "")
        if not str(code).strip():
            return {"content": [{"type": "text", "text": "El codigo no puede estar vacio."}], "isError": True}
        language = args.get("language", "auto")
        agents_str = args.get("agents")
        mode = args.get("mode", "auto")
        audit_level = max(0, min(int(args.get("audit_level", 1)), 3))

        from concilio_salamanca.debate.audit_profiles import get_audit_profile, select_profile_agents
        from concilio_salamanca.debate.compute_policy import ComputePolicyResolver, ComputeResolution
        from concilio_salamanca.debate.providers import create_model, resolve_api_key
        from concilio_salamanca.debate.orchestrator import DebateConfig, DebateOrchestrator

        orders = args.get("orders") or []
        if orders:
            from concilio_salamanca.debate.dogma import DogmaEngine

            dogma_engine = DogmaEngine()
            dogma = dogma_engine.propose(orders, args.get("objective", ""))
            if dogma["requiere_usuario"]:
                return {
                    "content": [{"type": "text", "text": json.dumps(dogma, ensure_ascii=False, indent=2)}],
                    "requires_user_decision": True,
                }
            code = DogmaEngine.compact(dogma) + "\n\n" + code

        if audit_level == 0:
            resolution = ComputeResolution(None, None, "auto", "cost", "audit-level-0", True)
        else:
            resolution = ComputePolicyResolver().resolve(
                policy=args.get("compute_policy", "auto"),
                priority=args.get("priority", "cost"),
                provider_override=args.get("provider"),
                model_override=args.get("model"),
                non_interactive=True,
            )
        if audit_level > 0 and resolution.static_only:
            audit_level = 0
        model = None
        if not resolution.static_only:
            provider_key = resolve_api_key(resolution.provider)
            if resolution.provider != "ollama" and not provider_key:
                resolution = resolution.__class__(
                    None, None, args.get("compute_policy", "auto"), args.get("priority", "cost"),
                    "static-fallback", True, f"Falta la clave del proveedor {resolution.provider}",
                )
                audit_level = 0
            else:
                deepseek_options = (
                    {"extra_body": {"thinking": {"type": "disabled"}}}
                    if resolution.provider == "deepseek" and args.get("priority", "cost") == "cost" else {}
                )
                model = create_model(
                    resolution.provider, resolution.model,
                    api_key=provider_key, temperature=0,
                    **deepseek_options,
                )
        profile = get_audit_profile(audit_level)
        requested = [a.strip() for a in agents_str.split(",")] if agents_str else None
        agent_selection = select_profile_agents(audit_level, code, language, requested)
        config = DebateConfig(
            max_rounds=profile.max_rounds,
            agents=agent_selection,
            mode=mode,
            audit_level=audit_level,
            token_budget=max(0, int(args.get("token_budget", 0))),
            model_name=resolution.model or "static",
            reserve_reason=resolution.reserve_reason or "",
        )
        orchestrator = DebateOrchestrator(model=model, config=config)
        result = orchestrator.run_debate(code, language)
        escalation = result.get("escalation")
        decision = args.get("frontier_decision") or {}
        approved = bool(
            escalation and decision.get("approved")
            and decision.get("decision_id") == escalation.get("decision_id")
            and decision.get("candidate") in escalation.get("candidates", [])
        )
        if approved:
            frontier_key = resolve_api_key("openai")
            if not frontier_key:
                return {
                    "content": [{"type": "text", "text": "Aprobación válida, pero falta OPENAI_API_KEY; no se hizo ninguna llamada frontera."}],
                    "isError": True,
                }
            candidate = decision["candidate"]
            frontier_model = create_model("openai", candidate, api_key=frontier_key, temperature=0)
            result = orchestrator.resume_with_frontier(
                result, frontier_model,
                decision_id=decision["decision_id"], candidate=candidate,
            )
            escalation = result.get("escalation")
        determinatio = result.get("determinatio")
        payload = {
            "veredicto": determinatio.veredicto_final.value if determinatio else "RESERVA",
            "determinatio": determinatio.model_dump(mode="json") if determinatio else None,
            "voting": result.get("voting", {}),
            "usage": result.get("usage", {}),
            "budget": result.get("budget", {}),
            "cache_hit_ratio": result.get("cache_hit_ratio", 0.0),
            "calls_by_model": result.get("calls_by_model", {}),
            "stop_reason": result.get("stop_reason"),
            "escalation": escalation,
        }
        if escalation and not approved:
            payload["status"] = "requires_user_decision"
            return {
                "content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False, indent=2)}],
                "requires_user_decision": True,
                "decision_id": escalation["decision_id"],
                "candidates": escalation["candidates"],
            }
        if approved:
            payload["status"] = "frontier_approved_completed"
        else:
            payload["status"] = "completed"
        return {"content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False, indent=2)}]}

    elif tool_name == "propose_dogma":
        from concilio_salamanca.debate.council_store import CouncilStore
        from concilio_salamanca.debate.dogma import DogmaEngine

        engine = DogmaEngine(CouncilStore(args.get("db_path")))
        value = engine.propose(args.get("orders") or [], args.get("objective", ""))
        return {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False, indent=2)}]}

    elif tool_name == "resolve_dogma":
        from concilio_salamanca.debate.council_store import CouncilStore
        from concilio_salamanca.debate.dogma import DogmaEngine

        engine = DogmaEngine(CouncilStore(args.get("db_path")))
        value = engine.resolve(
            int(args["dogma_id"]), args.get("keep_order_ids") or [], args.get("objective", "")
        )
        return {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False, indent=2)}]}

    elif tool_name == "exhaust_cases":
        from concilio_salamanca.debate.casuistry import exhaust_cases

        questions = exhaust_cases(
            args.get("context", ""), args.get("answered") or [], args.get("limit", 8)
        )
        return {"content": [{"type": "text", "text": "\n".join(f"- {q}" for q in questions)}]}

    elif tool_name == "graph_remember":
        from concilio_salamanca.debate.council_store import CouncilStore

        store = CouncilStore(args.get("db_path"))
        store.upsert_node(args["id"], args["kind"], args["label"], args.get("payload"))
        if args.get("source") and args.get("target") and args.get("relation"):
            store.add_edge(
                args["source"], args["target"], args["relation"], args.get("weight", 1.0)
            )
        return {"content": [{"type": "text", "text": json.dumps(store.stats(), ensure_ascii=False)}]}

    elif tool_name == "graph_context":
        from concilio_salamanca.debate.council_store import CouncilStore

        store = CouncilStore(args.get("db_path"))
        value = store.local_context(args["query"], args.get("limit", 8), args.get("hops", 1))
        return {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False, indent=2)}]}

    elif tool_name == "context_sieve":
        from concilio_salamanca.debate.context_sieve import sift_context

        value = sift_context(args.get("code", ""), args.get("diagnostics", ""), int(args.get("max_chars", 12000)))
        return {"content": [{"type": "text", "text": json.dumps(value.__dict__, ensure_ascii=False, indent=2)}]}

    elif tool_name == "security_diff":
        from concilio_salamanca.debate.security_diff import detect_security_surfaces

        value = detect_security_surfaces(args.get("diff", ""))
        return {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False, indent=2)}]}

    elif tool_name == "test_impact":
        from concilio_salamanca.debate.test_impact import select_impacted_tests

        value = select_impacted_tests(
            args.get("changed_files", []), args.get("test_files", []), args.get("dependency_edges") or {}
        )
        return {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False, indent=2)}]}

    elif tool_name == "debug_evidence":
        from concilio_salamanca.debate.debug_evidence import compact_debug_evidence

        value = compact_debug_evidence(args.get("error", ""), args.get("traceback", ""), args.get("hypotheses"))
        return {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False, indent=2)}]}

    elif tool_name == "audit_antipatterns":
        code = args.get("code", "")
        from concilio_salamanca.reference.anti_patrones import ANTI_PATRONES
        code_lower = code.lower()
        matches = []
        for ap in ANTI_PATRONES:
            for sintoma in ap.sintomas:
                if any(kw in code_lower for kw in sintoma.lower().split() if len(kw) > 3):
                    matches.append(f"{ap.id}: {ap.nombre} — {ap.conclusion[:100]}")
                    break
        text = "\n".join(matches) if matches else "No se detectaron anti-patrones."
        return {"content": [{"type": "text", "text": text}]}

    elif tool_name == "generate_license":
        from concilio_salamanca.license_generator import LicenseGenerator
        gen = LicenseGenerator(
            developer_name=args.get("developer", ""),
            project_name=args.get("project", ""),
            github_repo=args.get("repo", ""),
            jubilee_year=args.get("jubilee_year"),
            std_version=args.get("std", False),
        )
        license_text = gen.generate_license(args.get("country", "US"))
        return {"content": [{"type": "text", "text": license_text[:4000]}]}

    elif tool_name == "check_tools":
        from concilio_salamanca.debate.tool_detection import check_prerequisites
        from concilio_salamanca.debate.mde_history_writer import HistoryWriter
        status = check_prerequisites(verbose=False)
        writer = HistoryWriter()
        checks = writer.verify_integrity()
        lines = ["=== Herramientas ==="]
        for k, v in status.items():
            lines.append(f"  {k}: {'OK' if v else 'NO'}")
        lines.append("=== .mde_history ===")
        for k, v in checks.items():
            lines.append(f"  {k}: {'OK' if v else 'NO'}")
        return {"content": [{"type": "text", "text": "\n".join(lines)}]}

    elif tool_name == "history_stats":
        from concilio_salamanca.debate.mde_history_writer import HistoryWriter
        writer = HistoryWriter()
        return {"content": [{"type": "text", "text": writer.stats()}]}

    return {"content": [{"type": "text", "text": f"Tool '{tool_name}' no encontrada."}], "isError": True}


def mcp_serve():
    """Bucle principal del servidor MCP via stdio."""
    import sys
    from concilio_salamanca import __version__

    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
        except json.JSONDecodeError:
            continue

        method = request.get("method", "")
        req_id = request.get("id")

        if method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "concilio-salamanca",
                        "version": __version__,
                    },
                },
            }
        elif method == "tools/list":
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": handle_list_tools(request.get("params", {})),
            }
        elif method == "tools/call":
            params = request.get("params", {})
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})
            try:
                result = handle_call_tool(tool_name, tool_args)
            except Exception as error:
                result = {
                    "content": [
                        {"type": "text", "text": f"{type(error).__name__}: {error}"}
                    ],
                    "isError": True,
                }
            response = {"jsonrpc": "2.0", "id": req_id, "result": result}
        elif method == "notifications/initialized":
            continue
        else:
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method '{method}' not found"},
            }

        sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
        sys.stdout.flush()
