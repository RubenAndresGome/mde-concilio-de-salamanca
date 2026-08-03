from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# MODEL CATALOGUE —  Top ~40 models with known pricing and quality tiers
# ---------------------------------------------------------------------------
# Prices in USD per 1M tokens (input / output).
# Quality is a heuristic, never an absolute ranking.
# ---------------------------------------------------------------------------

CATALOGUE_UPDATED_AT = "2026-08-02"
CATALOGUE_STALE_AFTER_DAYS = 30

@dataclass
class ModelSpec:
    id: str                           # OpenRouter / provider id
    provider: str                     # canonical provider name
    name: str                         # human-readable
    price_in_1m: float                # input $/MTok
    price_out_1m: float               # output $/MTok
    quality: int                      # 1-10 (10 = best)
    tags: List[str] = field(default_factory=list)  # "coding","reasoning","fast","vision",...
    price_cache_hit_1m: float = 0.0
    frontier: bool = False


MODEL_CATALOGUE: Dict[str, ModelSpec] = {
    "openai/gpt-5.6-terra": ModelSpec(
        id="openai/gpt-5.6-terra", provider="openai", name="GPT-5.6 Terra",
        price_in_1m=2.50, price_out_1m=15.0, price_cache_hit_1m=0.25,
        quality=10, tags=["coding", "reasoning", "frontier"], frontier=True,
    ),
    "openai/gpt-5.6-sol": ModelSpec(
        id="openai/gpt-5.6-sol", provider="openai", name="GPT-5.6 Sol",
        price_in_1m=5.0, price_out_1m=30.0, price_cache_hit_1m=0.50,
        quality=10, tags=["coding", "reasoning", "frontier"], frontier=True,
    ),
    # ── Ollama local (gratis) ──────────────────────────────────────────
    "ollama/gemma4:e4b": ModelSpec(
        id="ollama/gemma4:e4b", provider="ollama",
        name="Gemma 4 4B (local)", price_in_1m=0.0, price_out_1m=0.0,
        quality=4, tags=["local", "free", "small"],
    ),
    "ollama/deepseek-r1:8b": ModelSpec(
        id="ollama/deepseek-r1:8b", provider="ollama",
        name="DeepSeek R1 8B (local)", price_in_1m=0.0, price_out_1m=0.0,
        quality=6, tags=["local", "free", "reasoning"],
    ),
    "ollama/qwen2.5-coder:7b": ModelSpec(
        id="ollama/qwen2.5-coder:7b", provider="ollama",
        name="Qwen 2.5 Coder 7B (local)", price_in_1m=0.0, price_out_1m=0.0,
        quality=6, tags=["local", "free", "coding"],
    ),

    # ── Meta / Facebook Llama ─────────────────────────────────────────
    "meta-llama/llama-3.1-8b-instruct": ModelSpec(
        id="meta-llama/llama-3.1-8b-instruct", provider="meta-llama",
        name="Llama 3.1 8B Instruct", price_in_1m=0.02, price_out_1m=0.03,
        quality=6, tags=["fast", "cheap", "general"],
    ),
    "meta-llama/llama-3.3-70b-instruct": ModelSpec(
        id="meta-llama/llama-3.3-70b-instruct", provider="meta-llama",
        name="Llama 3.3 70B Instruct", price_in_1m=0.10, price_out_1m=0.32,
        quality=8, tags=["reasoning", "coding"],
    ),
    "meta-llama/llama-4-scout": ModelSpec(
        id="meta-llama/llama-4-scout", provider="meta-llama",
        name="Llama 4 Scout", price_in_1m=0.10, price_out_1m=0.30,
        quality=8, tags=["reasoning", "coding", "fast"],
    ),

    # ── DeepSeek (China) ──────────────────────────────────────────────
    "deepseek/deepseek-v4-flash": ModelSpec(
        id="deepseek/deepseek-v4-flash", provider="deepseek",
        name="DeepSeek V4 Flash", price_in_1m=0.14, price_out_1m=0.28,
        quality=8, tags=["fast", "reasoning", "coding"], price_cache_hit_1m=0.0028,
    ),
    "deepseek/deepseek-v4-pro": ModelSpec(
        id="deepseek/deepseek-v4-pro", provider="deepseek",
        name="DeepSeek V4 Pro", price_in_1m=0.435, price_out_1m=0.87,
        quality=9, tags=["reasoning", "coding", "quality"], price_cache_hit_1m=0.003625,
    ),
    # ── Qwen / Alibaba (China) ────────────────────────────────────────
    "qwen/qwen-2.5-7b-instruct": ModelSpec(
        id="qwen/qwen-2.5-7b-instruct", provider="qwen",
        name="Qwen 2.5 7B", price_in_1m=0.04, price_out_1m=0.10,
        quality=5, tags=["cheap", "small", "general"],
    ),
    "qwen/qwen3-8b": ModelSpec(
        id="qwen/qwen3-8b", provider="qwen",
        name="Qwen3 8B", price_in_1m=0.05, price_out_1m=0.40,
        quality=6, tags=["cheap", "general"],
    ),
    "qwen/qwen3-32b": ModelSpec(
        id="qwen/qwen3-32b", provider="qwen",
        name="Qwen3 32B", price_in_1m=0.08, price_out_1m=0.28,
        quality=7, tags=["reasoning", "coding"],
    ),
    "qwen/qwen-2.5-coder-32b-instruct": ModelSpec(
        id="qwen/qwen-2.5-coder-32b-instruct", provider="qwen",
        name="Qwen 2.5 Coder 32B", price_in_1m=0.66, price_out_1m=1.00,
        quality=8, tags=["coding", "reasoning"],
    ),
    "qwen/qwen3-max": ModelSpec(
        id="qwen/qwen3-max", provider="qwen",
        name="Qwen3 Max", price_in_1m=0.78, price_out_1m=3.90,
        quality=9, tags=["reasoning", "coding", "premium"],
    ),

    # ── MiniMax (China) ───────────────────────────────────────────────
    "minimax/minimax-m2.5": ModelSpec(
        id="minimax/minimax-m2.5", provider="minimax",
        name="MiniMax M2.5", price_in_1m=0.12, price_out_1m=0.48,
        quality=6, tags=["cheap", "general"],
    ),
    "minimax/minimax-m3": ModelSpec(
        id="minimax/minimax-m3", provider="minimax",
        name="MiniMax M3", price_in_1m=0.30, price_out_1m=1.20,
        quality=7, tags=["reasoning"],
    ),

    # ── GLM / Zhipu AI (China) ────────────────────────────────────────
    "z-ai/glm-4.7-flash": ModelSpec(
        id="z-ai/glm-4.7-flash", provider="z-ai",
        name="GLM 4.7 Flash", price_in_1m=0.06, price_out_1m=0.40,
        quality=6, tags=["fast", "cheap", "general"],
    ),

    # ── ByteDance / StepFun / Tencent (China) ─────────────────────────
    "bytedance-seed/seed-1.6-flash": ModelSpec(
        id="bytedance-seed/seed-1.6-flash", provider="bytedance-seed",
        name="Seed 1.6 Flash", price_in_1m=0.075, price_out_1m=0.30,
        quality=6, tags=["fast", "cheap"],
    ),
    "stepfun/step-3.5-flash": ModelSpec(
        id="stepfun/step-3.5-flash", provider="stepfun",
        name="Step 3.5 Flash", price_in_1m=0.09, price_out_1m=0.30,
        quality=6, tags=["fast", "cheap"],
    ),
    "tencent/hy3-preview": ModelSpec(
        id="tencent/hy3-preview", provider="tencent",
        name="Hunyuan Hy3", price_in_1m=0.063, price_out_1m=0.21,
        quality=6, tags=["cheap", "general"],
    ),

    # ── OpenAI ────────────────────────────────────────────────────────
    "openai/gpt-4o-mini": ModelSpec(
        id="openai/gpt-4o-mini", provider="openai",
        name="GPT-4o Mini", price_in_1m=0.15, price_out_1m=0.60,
        quality=8, tags=["fast", "general"],
    ),
    "openai/gpt-4o": ModelSpec(
        id="openai/gpt-4o", provider="openai",
        name="GPT-4o", price_in_1m=2.50, price_out_1m=10.00,
        quality=9, tags=["reasoning", "coding", "premium"],
    ),

    # ── Claude (techo absoluto) ───────────────────────────────────────
    "anthropic/claude-sonnet-4": ModelSpec(
        id="anthropic/claude-sonnet-4", provider="anthropic",
        name="Claude Sonnet 4", price_in_1m=3.00, price_out_1m=15.00,
        quality=10, tags=["reasoning", "coding", "premium", "techo"],
    ),
    "anthropic/claude-opus-4": ModelSpec(
        id="anthropic/claude-opus-4", provider="anthropic",
        name="Claude Opus 4", price_in_1m=15.00, price_out_1m=75.00,
        quality=10, tags=["reasoning", "coding", "premium", "techo", "max"],
    ),
}


# ---------------------------------------------------------------------------
# ModelRanker — cost-quality-availability ranking engine
# ---------------------------------------------------------------------------

def _ollama_aliases(spec: ModelSpec) -> list:
    """Generate possible Ollama aliases for a model spec."""
    parts = spec.id.split("/")
    name = parts[-1] if len(parts) > 1 else parts[0]
    aliases = [f"ollama/{name}"]
    if ":" in name:
        short = name.split(":")[0]
        aliases.append(f"ollama/{short}")
    return aliases


class ModelRanker:
    """Singleton that ranks available models by cost-quality-availability.

    Priority order:
      1. Ollama local (free)
      2. Ultra-cheap (<$0.10/MTok input) with quality >= 6
      3. Cheap ($0.10-$0.50/MTok) with quality >= 7
      4. Mid ($0.50-$2.00/MTok) with quality >= 8
      5. Premium ($2.00-$10.00/MTok)
      6. Claude techo (only if explicitly requested)
    """

    _instance: "ModelRanker" = None
    _ollama_cache: Dict[str, bool] = {}

    def __new__(cls) -> "ModelRanker":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def check_ollama(timeout: int = 5) -> Dict[str, bool]:
        """Probe local Ollama server and return available model ids."""
        if ModelRanker._ollama_cache:
            return ModelRanker._ollama_cache
        try:
            import json
            import urllib.request

            req = urllib.request.Request("http://localhost:11434/api/tags")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read())

            available: Dict[str, bool] = {}
            for m in data.get("models", []):
                name = m["name"]
                available[f"ollama/{name}"] = True
                # Also expose short aliases for convenience
                if ":" in name:
                    short = name.split(":")[0]
                    available[f"ollama/{short}"] = True
            ModelRanker._ollama_cache = available
            return available
        except Exception:
            return {}

    @staticmethod
    def catalogue_is_stale(today: Optional[date] = None) -> bool:
        updated = datetime.strptime(CATALOGUE_UPDATED_AT, "%Y-%m-%d").date()
        return ((today or date.today()) - updated).days > CATALOGUE_STALE_AFTER_DAYS

    @staticmethod
    def estimate_cost(
        model_id: str,
        input_tokens: int,
        output_tokens: int,
        cache_hit_tokens: int = 0,
        *,
        allow_stale_frontier: bool = False,
    ) -> float:
        """Estimate USD cost for a given model and token counts."""
        spec = MODEL_CATALOGUE.get(model_id)
        if not spec:
            return 0.0
        if spec.frontier and ModelRanker.catalogue_is_stale() and not allow_stale_frontier:
            raise RuntimeError("Catálogo de precios frontera obsoleto; actualízalo antes de estimar")
        hit = min(max(0, cache_hit_tokens), max(0, input_tokens))
        miss = max(0, input_tokens - hit)
        cost = (spec.price_in_1m * miss / 1_000_000) + (
            spec.price_cache_hit_1m * hit / 1_000_000
        ) + (
            spec.price_out_1m * output_tokens / 1_000_000
        )
        return cost

    @staticmethod
    def rank_for_role(
        role: str = "ejecutor",
        prefer_local: bool = True,
        max_budget_usd: Optional[float] = None,
        task_tags: Optional[List[str]] = None,
    ) -> List[ModelSpec]:
        """Return models sorted by best cost-quality for a given role.

        Args:
            role: 'ejecutor' (cheap workers) or 'director_strategy' (premium)
            prefer_local: if True, prioritise Ollama free models
            max_budget_usd: optional max cost per 1M tokens input
            task_tags: optional tags to match (e.g. ['coding','fast'])
        """
        ollama_models = ModelRanker.check_ollama() if prefer_local else {}
        candidates: List[ModelSpec] = []

        for mid, spec in MODEL_CATALOGUE.items():
            if "retired" in spec.tags:
                continue
            # Filter by budget
            if max_budget_usd is not None and spec.price_in_1m > max_budget_usd:
                continue

            # Filter by task tags
            if task_tags:
                if not any(t in spec.tags for t in task_tags):
                    continue

            candidates.append(spec)

        def _sort_key(s: ModelSpec) -> Tuple[float, int, float]:
            """Primary: local availability. Secondary: quality/price ratio."""
            is_local = s.provider == "ollama" and (
                s.id in ollama_models
                or any(alias in ollama_models for alias in _ollama_aliases(s))
            )
            if is_local and prefer_local:
                return (0.0, -s.quality, s.price_in_1m)
            # For ejecutor: prefer high quality at low price
            if role == "ejecutor":
                price_penalty = s.price_in_1m * 10
                return (1.0, -s.quality + price_penalty, s.price_in_1m)
            # For director_strategy: prefer quality regardless of price
            return (2.0, -s.quality, s.price_in_1m)

        candidates.sort(key=_sort_key)
        return candidates

    @staticmethod
    def best_for_role(
        role: str = "ejecutor",
        prefer_local: bool = True,
        max_budget_usd: Optional[float] = None,
        task_tags: Optional[List[str]] = None,
    ) -> Optional[ModelSpec]:
        """Returns the single best model for a role."""
        ranked = ModelRanker.rank_for_role(role, prefer_local, max_budget_usd, task_tags)
        return ranked[0] if ranked else None

    @staticmethod
    def format_price_table(max_rows: int = 20) -> str:
        """Pretty-print a Markdown price table."""
        lines = [
            "| Modelo | Provider | Input $/MTok | Output $/MTok | Calidad | Tags |",
            "|--------|----------|-------------|--------------|---------|------|",
        ]
        sorted_models = sorted(
            MODEL_CATALOGUE.values(), key=lambda s: (s.price_in_1m, -s.quality)
        )
        for spec in sorted_models[:max_rows]:
            tags_short = ", ".join(spec.tags[:3])
            lines.append(
                f"| {spec.name:35s} | {spec.provider:12s} | ${spec.price_in_1m:<8.3f} | "
                f"${spec.price_out_1m:<9.3f} | {spec.quality:<6d} | {tags_short} |"
            )
        return "\n".join(lines)

    @staticmethod
    def list_models() -> str:
        """Return a formatted list of all catalogued models."""
        lines = ["Modelos disponibles en el catálogo de precios:", ""]
        for mid, spec in sorted(MODEL_CATALOGUE.items()):
            local = " (local)" if spec.provider == "ollama" else ""
            lines.append(
                f"  {mid:40s}  ${spec.price_in_1m:.3f}/${spec.price_out_1m:.3f}  "
                f"Q={spec.quality}{local}"
            )
        return "\n".join(lines)
