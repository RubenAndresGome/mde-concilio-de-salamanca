from concilio_salamanca.debate.graph import (
    SalamancaGraphBuilder,
    create_salamanca_graph,
    create_salamanca_graph_legacy,
)
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

__all__ = [
    "DebateConfig",
    "DebateOrchestrator",
    "ValidadorPNC",
    "SalamancaGraphBuilder",
    "create_salamanca_graph",
    "create_salamanca_graph_legacy",
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
    "analyze_code",
    "analyze_file",
    "auto_select_agents",
    "format_analysis",
    "PrecedentEngine",
    "get_precedent_engine",
    "create_salamanca_graph_parallel",
    "build_parallel_graph",
]
