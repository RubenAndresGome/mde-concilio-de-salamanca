"""
Factory multi-proveedor de modelos LLM para el Concilio de Salamanca.

Soporta: OpenAI, DeepSeek, Anthropic, Groq, Ollama, opencode.
Cada proveedor se configura via nombre, key de entorno, y base_url opcional.
"""

from __future__ import annotations

import os
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
        "default_model": "deepseek-chat",
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
    "opencode": {
        "cls": "ChatOpenAI",
        "pkg": "langchain_openai",
        "env_key": "OPENAI_API_KEY",
        "default_model": "gpt-4o",
    },
}


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
    return cli_key or os.environ.get(env_key) or os.environ.get("OPENAI_API_KEY") or None


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
