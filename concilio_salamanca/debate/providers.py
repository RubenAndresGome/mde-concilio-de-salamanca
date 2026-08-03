"""
Factory multi-proveedor de modelos LLM para el Concilio de Salamanca.

Soporta: OpenAI, DeepSeek, Anthropic, Groq, Ollama, OpenRouter, opencode.
Incluye ModelRanker para seleccion automatica calidad-precio-disponibilidad
y warning economico para modelos caros.
"""

from __future__ import annotations

import os
import warnings
from importlib import import_module
from typing import Any, Dict, Optional

from langchain_core.language_models import BaseChatModel

PROVIDERS: Dict[str, Dict[str, Any]] = {
    "openai": {
        "cls": "ChatOpenAI",
        "pkg": "langchain_openai",
        "env_key": "OPENAI_API_KEY",
        "default_model": "gpt-4o",
    },
    "deepseek": {
        "cls": "ChatOpenAI",
        "pkg": "langchain_openai",
        "env_key": "DEEPSEEK_API_KEY",
        "base_url": "https://api.deepseek.com",
        "default_model": "deepseek-v4-flash",
    },
    "anthropic": {
        "cls": "ChatAnthropic",
        "pkg": "langchain_anthropic",
        "env_key": "ANTHROPIC_API_KEY",
        "default_model": "claude-sonnet-4-20250514",
    },
    "groq": {
        "cls": "ChatGroq",
        "pkg": "langchain_groq",
        "env_key": "GROQ_API_KEY",
        "default_model": "llama-3.3-70b-versatile",
    },
    "ollama": {
        "cls": "ChatOllama",
        "pkg": "langchain_ollama",
        "env_key": "",
        "default_model": "llama3",
    },
    "openrouter": {
        "cls": "ChatOpenAI",
        "pkg": "langchain_openai",
        "env_key": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "deepseek/deepseek-v4-flash",
    },
    "opencode": {
        "cls": "ChatOpenAI",
        "pkg": "langchain_openai",
        "env_key": "OPENAI_API_KEY",
        "default_model": "gpt-4o",
    },
}

_WARNED_EXPENSIVE: set = set()


def _warn_expensive(provider: str, model: str, cost_est: float = 0):
    key = f"{provider}/{model}"
    if key in _WARNED_EXPENSIVE:
        return
    _WARNED_EXPENSIVE.add(key)
    if cost_est > 10:
        warnings.warn(
            f"ALTO COSTO: modelo {key} (~${cost_est:.2f}/MTok). "
            f"Considera --provider-obreros deepseek --provider-magister openai",
            RuntimeWarning,
        )
    elif cost_est > 1:
        warnings.warn(
            f"COSTO MODERADO: modelo {key} (~${cost_est:.2f}/MTok).",
            RuntimeWarning,
        )


def get_provider_info(provider: str) -> Dict[str, Any]:
    if provider not in PROVIDERS:
        raise ValueError(
            f"Proveedor '{provider}' no soportado. "
            f"Opciones: {list(PROVIDERS.keys())}"
        )
    return PROVIDERS[provider]


def create_model(
    provider: str,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    temperature: float = 0,
    **kwargs,
) -> BaseChatModel:
    info = get_provider_info(provider)
    pkg = import_module(info["pkg"])
    cls = getattr(pkg, info["cls"])

    resolved_key = api_key or os.environ.get(info.get("env_key", ""), "")
    resolved_model = model or info.get("default_model", "gpt-4o")
    resolved_url = base_url or info.get("base_url") or None

    init_kwargs = {
        "model": resolved_model,
        "temperature": temperature,
    }

    if resolved_key:
        init_kwargs["api_key"] = resolved_key

    if resolved_url:
        init_kwargs["base_url"] = resolved_url

    init_kwargs.update(kwargs)
    return cls(**{k: v for k, v in init_kwargs.items() if v is not None})


def resolve_api_key(provider: str, cli_key: Optional[str] = None) -> Optional[str]:
    info = get_provider_info(provider)
    env_key = info.get("env_key", "")
    if not env_key:
        return cli_key or None
    resolved = cli_key or os.environ.get(env_key)
    # Una clave de otro proveedor nunca debe reinterpretarse silenciosamente.
    return resolved or None


def get_sorted_providers_by_weight(weights_config: dict) -> list:
    valid = []
    for prov, weight in weights_config.items():
        prov = prov.lower().strip()
        if prov in PROVIDERS and isinstance(weight, (int, float)) and weight > 0:
            valid.append((prov, float(weight)))
    valid.sort(key=lambda x: x[1], reverse=True)
    return valid


def _model_id_to_provider(model_id: str) -> str:
    prefix = model_id.split("/")[0]
    if prefix in PROVIDERS:
        return prefix
    if prefix in ("meta-llama",):
        return "openrouter"
    if prefix in ("ollama",):
        return "ollama"
    return "openrouter"


def resolve_provider_from_weights(
    weights_config: dict,
    role: str = "ejecutor",
    roles_config: dict = None,
    prefer_local: bool = True,
) -> dict:
    """Resolves the best provider and model for a given role.

    Supports 'auto' resolution via ModelRanker when role value is 'auto'.

    Args:
        weights_config: dict of provider -> weight
        role: 'ejecutor', 'director_strategy', or 'auto' for ModelRanker
        roles_config: dict mapping role -> provider name (optional override)
        prefer_local: if True, prefer Ollama local models

    Returns:
        dict with 'provider' and 'model' keys.
    """
    explicit_role = (roles_config or {}).get(role, "")
    if explicit_role == "auto" or role == "auto":
        from concilio_salamanca.debate.model_pricing import ModelRanker

        task_tags = ["reasoning"] if role == "director_strategy" else ["fast"]
        best = ModelRanker.best_for_role(
            role=role, prefer_local=prefer_local, task_tags=task_tags
        )
        if best:
            model_id = best.id
            prov = _model_id_to_provider(model_id)
            _warn_expensive(prov, model_id, best.price_in_1m)
            return {"provider": prov, "model": model_id}

    sorted_providers = get_sorted_providers_by_weight(weights_config)

    if roles_config and role in roles_config:
        explicit = roles_config[role].lower().strip()
        if explicit in PROVIDERS:
            info = PROVIDERS[explicit]
            return {
                "provider": explicit,
                "model": info.get("default_model", "deepseek-v4-flash"),
            }

    if sorted_providers:
        best = sorted_providers[0][0]
        info = PROVIDERS[best]
        return {
            "provider": best,
            "model": info.get("default_model", "deepseek-v4-flash"),
        }

    return {"provider": "deepseek", "model": "deepseek-v4-flash"}


def list_providers() -> str:
    lines = ["Proveedores LLM soportados por el Concilio de Salamanca:", ""]
    for name, info in PROVIDERS.items():
        pkg_cls = f"{info['pkg']}.{info['cls']}"
        default_model = info.get("default_model", "requiere --model")
        env = info.get("env_key", "sin key (local)")
        lines.append(f"  {name:12s}  {pkg_cls:40s}  default: {default_model}")
        lines.append(f"  {'':12s}  env: {env}")
        if info.get("base_url"):
            lines.append(f"  {'':12s}  base_url: {info['base_url']}")
        lines.append("")
    return "\n".join(lines)
