# graph.py was removed to unify the implementation on orchestrator.py / send_graph.py
from concilio_salamanca.debate.orchestrator import DebateConfig, DebateOrchestrator
from concilio_salamanca.debate.validator_pnc import ValidadorPNC
from concilio_salamanca.debate.syllogism_cache import (
    CacheEntry,
    PredicateLogicReduction,
    ScholasticReduction,
    SetTheoryReduction,
    SyllogismCache,
    SyllogismPattern,
    SyllogismReducer,
    UnifiedSyllogism,
    get_syllogism_cache,
)
from concilio_salamanca.debate.providers import (
    PROVIDERS,
    create_model,
    get_provider_info,
    list_providers,
    resolve_api_key,
    get_sorted_providers_by_weight,
    resolve_provider_from_weights,
)
from concilio_salamanca.debate.static_analysis import (
    analyze_code,
    analyze_file,
    auto_select_agents,
    format_analysis,
)
from concilio_salamanca.debate.precedents import (
    PrecedentEngine,
    get_precedent_engine,
)
from concilio_salamanca.debate.send_graph import (
    create_salamanca_graph_parallel,
    build_parallel_graph,
)
from concilio_salamanca.debate.checks import (
    run_socratic_check,
    run_murphy_check,
)
from concilio_salamanca.debate.git_history import (
    format_git_context,
    get_git_log,
    get_mde_history,
)
from concilio_salamanca.debate.ockham_engine import OckhamEngine
from concilio_salamanca.debate.mde_history_writer import HistoryWriter
from concilio_salamanca.debate.rns_registry import RenerumRegistry
from concilio_salamanca.debate.model_pricing import ModelRanker, ModelSpec
from concilio_salamanca.debate.tool_detection import (
    check_prerequisites,
    detect_specify,
    install_specify,
    install_cbmm,
)
from concilio_salamanca.debate.mcp_design_client import (
    generate_prototype,
    load_design_system,
)
from concilio_salamanca.debate.formatters import (
    format_output_text,
    format_output_json,
    format_output_markdown,
    format_output_mermaid,
    format_output_sarif,
    format_output_executive,
)
from concilio_salamanca.debate.voting import build_voting_table
from concilio_salamanca.debate.formal_verification import FormalVerifier
from concilio_salamanca.debate.loop_invariants import LoopInvariantEngine
from concilio_salamanca.debate.mcp_client import MCPClientManager
from concilio_salamanca.debate.audit_profiles import AuditProfile, get_audit_profile
from concilio_salamanca.debate.compute_policy import ComputePolicyResolver, ComputeResolution
from concilio_salamanca.debate.token_accountant import TokenAccountant

__all__ = [
    "DebateConfig",
    "DebateOrchestrator",
    "ValidadorPNC",
    "SyllogismCache",
    "SyllogismPattern",
    "SyllogismReducer",
    "ScholasticReduction",
    "SetTheoryReduction",
    "PredicateLogicReduction",
    "UnifiedSyllogism",
    "CacheEntry",
    "get_syllogism_cache",
    "PROVIDERS",
    "create_model",
    "get_provider_info",
    "list_providers",
    "resolve_api_key",
    "get_sorted_providers_by_weight",
    "resolve_provider_from_weights",
    "analyze_code",
    "analyze_file",
    "auto_select_agents",
    "format_analysis",
    "PrecedentEngine",
    "get_precedent_engine",
    "create_salamanca_graph_parallel",
    "build_parallel_graph",
    "run_socratic_check",
    "run_murphy_check",
    "format_git_context",
    "get_git_log",
    "get_mde_history",
    "OckhamEngine",
    "HistoryWriter",
    "RenerumRegistry",
    "ModelRanker",
    "ModelSpec",
    "check_prerequisites",
    "detect_specify",
    "install_specify",
    "install_cbmm",
    "generate_prototype",
    "load_design_system",
    "format_output_text",
    "format_output_json",
    "format_output_markdown",
    "format_output_mermaid",
    "format_output_sarif",
    "format_output_executive",
    "build_voting_table",
    "FormalVerifier",
    "LoopInvariantEngine",
    "MCPClientManager",
    "AuditProfile",
    "get_audit_profile",
    "ComputePolicyResolver",
    "ComputeResolution",
    "TokenAccountant",
]
