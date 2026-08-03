"""Contabilidad de tokens/caché/costo con parada presupuestaria."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


DEEPSEEK_PRICES = {
    "deepseek-v4-flash": {"cache_hit": 0.0028, "cache_miss": 0.14, "output": 0.28},
    "deepseek-v4-pro": {"cache_hit": 0.003625, "cache_miss": 0.435, "output": 0.87},
}


def extract_usage(response: Any) -> Dict[str, int]:
    metadata = getattr(response, "response_metadata", {}) or {}
    usage = getattr(response, "usage_metadata", {}) or metadata.get("token_usage", {}) or {}
    details = usage.get("input_token_details", {}) or usage.get("prompt_tokens_details", {}) or {}
    output_details = usage.get("output_token_details", {}) or usage.get("completion_tokens_details", {}) or {}
    prompt = int(usage.get("input_tokens", usage.get("prompt_tokens", 0)) or 0)
    output = int(usage.get("output_tokens", usage.get("completion_tokens", 0)) or 0)
    hit = int(
        usage.get("prompt_cache_hit_tokens", details.get("cache_read", details.get("cached_tokens", 0))) or 0
    )
    miss = int(usage.get("prompt_cache_miss_tokens", max(0, prompt - hit)) or 0)
    reasoning = int(
        usage.get("reasoning_tokens", output_details.get("reasoning", output_details.get("reasoning_tokens", 0))) or 0
    )
    return {
        "input_tokens": prompt,
        "output_tokens": output,
        "reasoning_tokens": reasoning,
        "prompt_cache_hit_tokens": hit,
        "prompt_cache_miss_tokens": miss,
    }


@dataclass
class TokenAccountant:
    token_budget: int = 0
    usage: Dict[str, int] = field(default_factory=lambda: {
        "input_tokens": 0,
        "output_tokens": 0,
        "reasoning_tokens": 0,
        "prompt_cache_hit_tokens": 0,
        "prompt_cache_miss_tokens": 0,
    })
    calls_by_model: Dict[str, int] = field(default_factory=dict)
    calls: list[dict] = field(default_factory=list)
    cost_usd: float = 0.0

    def can_call(self, output_limit: int = 0, input_estimate: int = 0) -> bool:
        if self.token_budget <= 0:
            return True
        consumed = self.usage["input_tokens"] + self.usage["output_tokens"]
        return consumed + max(0, input_estimate) + max(0, output_limit) <= self.token_budget

    def record(self, *, usage: Dict[str, int], model: str, agent: str, latency_ms: float = 0) -> None:
        clean = {key: int(usage.get(key, 0) or 0) for key in self.usage}
        for key, value in clean.items():
            self.usage[key] += value
        model = model or "unknown"
        self.calls_by_model[model] = self.calls_by_model.get(model, 0) + 1
        price = DEEPSEEK_PRICES.get(model, {})
        call_cost = (
            clean["prompt_cache_hit_tokens"] * price.get("cache_hit", 0)
            + clean["prompt_cache_miss_tokens"] * price.get("cache_miss", 0)
            + clean["output_tokens"] * price.get("output", 0)
        ) / 1_000_000
        self.cost_usd += call_cost
        self.calls.append({
            "agent": agent,
            "model": model,
            "latency_ms": round(latency_ms, 2),
            "cost_usd": round(call_cost, 8),
            **clean,
        })

    def snapshot(self) -> dict:
        input_total = self.usage["prompt_cache_hit_tokens"] + self.usage["prompt_cache_miss_tokens"]
        return {
            "usage": dict(self.usage),
            "budget": {"token_budget": self.token_budget, "remaining_tokens": (
                max(0, self.token_budget - self.usage["input_tokens"] - self.usage["output_tokens"])
                if self.token_budget > 0 else None
            )},
            "cache_hit_ratio": self.usage["prompt_cache_hit_tokens"] / input_total if input_total else 0.0,
            "calls_by_model": dict(self.calls_by_model),
            "cost_usd": round(self.cost_usd, 8),
            "calls": list(self.calls),
        }
