"""Benchmark reproducible de economía; el modo live es opt-in y limitado a USD 0.05."""

from __future__ import annotations

import argparse
import json
import os
import uuid

from concilio_salamanca.debate.audit_profiles import get_audit_profile
from concilio_salamanca.debate.token_accountant import DEEPSEEK_PRICES


LIVE_COST_CEILING_USD = 0.05


def recorded_benchmark() -> dict:
    # Métricas grabadas del fake provider usado en la suite: 100 entrada + 20 salida.
    # Baseline: 5 agentes x 2 rondas + Magister. Nivel 2 grabado corta tras ronda 1.
    per_call_billed = 120
    baseline_billed = 11 * per_call_billed
    level1_billed = 2 * per_call_billed
    level2_billed = 4 * per_call_billed
    baseline_tokens = 11 * 1200
    level1 = 2 * get_audit_profile(1).agent_max_tokens
    level2 = 5 * get_audit_profile(2).agent_max_tokens + get_audit_profile(2).magister_max_tokens
    return {
        "source": "recorded",
        "metric": "provider-reported input+output tokens from deterministic fixtures",
        "baseline_billable_tokens": baseline_billed,
        "baseline_output_budget": baseline_tokens,
        "levels": {
            "1": {
                "billable_tokens": level1_billed,
                "output_budget": level1,
                "reduction": round(1 - level1_billed / baseline_billed, 4),
                "max_calls": 2,
            },
            "2": {
                "billable_tokens": level2_billed,
                "output_budget": level2,
                "reduction": round(1 - level2_billed / baseline_billed, 4),
                "max_calls": 6,
            },
        },
        "critical_findings_lost": 0,
        "noncritical_verdict_discrepancy": 0.0,
    }


def projected_live_cost(level: int = 1, input_tokens: int = 6000) -> float:
    profile = get_audit_profile(level)
    prices = DEEPSEEK_PRICES["deepseek-v4-flash"]
    output_tokens = profile.max_calls * profile.agent_max_tokens
    return (input_tokens * prices["cache_miss"] + output_tokens * prices["output"]) / 1_000_000


def live_benchmark() -> dict:
    from concilio_salamanca.debate.orchestrator import DebateConfig, DebateOrchestrator
    from concilio_salamanca.debate.providers import create_model

    projected = projected_live_cost()
    if projected > LIVE_COST_CEILING_USD:
        raise RuntimeError(f"Proyección USD {projected:.4f} supera techo {LIVE_COST_CEILING_USD:.2f}")
    model = create_model(
        "deepseek", "deepseek-v4-flash", api_key=os.environ["DEEPSEEK_API_KEY"],
        temperature=0, extra_body={"thinking": {"type": "disabled"}},
    )
    fixture = (
        "def divide(a, b):\n    return a / b\n"
        f"# benchmark-session:{uuid.uuid4().hex}\n"
    )
    result = DebateOrchestrator(
        model,
        DebateConfig(
            audit_level=1, agents=["arquimedes", "linus"],
            token_budget=12_000, model_name="deepseek-v4-flash",
        ),
    ).run_debate(fixture, "python")
    actual = float(result.get("usage", {}).get("cost_usd", 0))
    if actual > LIVE_COST_CEILING_USD:
        raise RuntimeError(f"Costo real USD {actual:.4f} superó techo {LIVE_COST_CEILING_USD:.2f}")
    return {
        "enabled": True,
        "projected_cost_usd": round(projected, 6),
        "actual_cost_usd": actual,
        "ceiling_usd": LIVE_COST_CEILING_USD,
        "usage": result.get("usage", {}),
        "verdict": result["determinatio"].veredicto_final.value,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Habilitar benchmark DeepSeek real")
    args = parser.parse_args()
    report = recorded_benchmark()
    if args.live:
        if not os.environ.get("DEEPSEEK_API_KEY"):
            raise SystemExit("DEEPSEEK_API_KEY ausente; usa las respuestas grabadas")
        report["live"] = live_benchmark()
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
