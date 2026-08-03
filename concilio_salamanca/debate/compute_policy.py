"""Resolución única y auditable de proveedor/modelo."""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import asdict, dataclass
from typing import Callable, Optional


@dataclass(frozen=True)
class ComputeResolution:
    provider: Optional[str]
    model: Optional[str]
    policy: str
    priority: str
    source: str
    static_only: bool = False
    reserve_reason: Optional[str] = None

    def as_dict(self) -> dict:
        return asdict(self)


class ComputePolicyResolver:
    COST_MODEL = "deepseek-v4-flash"
    QUALITY_MODEL = "deepseek-v4-pro"
    LOCAL_PREFERENCES = (
        "deepseek-v4", "deepseek-r1", "deepseek-coder", "qwen3-coder",
        "qwen2.5-coder", "qwen",
    )

    def __init__(self, ollama_probe: Optional[Callable[[], list[str]]] = None):
        self._ollama_probe = ollama_probe or self._probe_ollama

    @staticmethod
    def _probe_ollama() -> list[str]:
        try:
            completed = subprocess.run(
                ["ollama", "list", "--json"],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
            )
            if completed.returncode == 0 and completed.stdout.strip():
                parsed = json.loads(completed.stdout)
                rows = parsed.get("models", parsed) if isinstance(parsed, dict) else parsed
                return [str(row.get("name", "")) for row in rows if isinstance(row, dict)]
        except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
            pass
        try:
            completed = subprocess.run(
                ["ollama", "list"], capture_output=True, text=True, timeout=3, check=False
            )
            if completed.returncode == 0:
                return [line.split()[0] for line in completed.stdout.splitlines()[1:] if line.strip()]
        except (OSError, subprocess.SubprocessError):
            pass
        return []

    @classmethod
    def _best_local(cls, available: list[str]) -> Optional[str]:
        lowered = [(name, name.lower()) for name in available]
        for preference in cls.LOCAL_PREFERENCES:
            for original, normalized in lowered:
                if preference in normalized:
                    return original
        return None

    def resolve(
        self,
        *,
        policy: str = "auto",
        priority: str = "cost",
        provider_override: Optional[str] = None,
        model_override: Optional[str] = None,
        api_key: Optional[str] = None,
        non_interactive: bool = False,
    ) -> ComputeResolution:
        policy = (policy or "auto").lower()
        priority = (priority or "cost").lower()
        if policy not in {"local", "cloud", "auto"}:
            raise ValueError("compute_policy debe ser local, cloud o auto")
        if priority not in {"cost", "quality"}:
            raise ValueError("priority debe ser cost o quality")

        if provider_override or model_override:
            provider = (provider_override or "deepseek").lower()
            model = model_override or (
                self.QUALITY_MODEL if provider == "deepseek" and priority == "quality" else self.COST_MODEL
            )
            return ComputeResolution(provider, model, policy, priority, "override")

        key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if policy != "local" and key:
            model = self.QUALITY_MODEL if priority == "quality" else self.COST_MODEL
            return ComputeResolution("deepseek", model, policy, priority, "deepseek")

        local = self._best_local(self._ollama_probe())
        if local:
            return ComputeResolution("ollama", local, policy, priority, "ollama-fallback")

        reason = "Sin DEEPSEEK_API_KEY ni modelo Ollama DeepSeek/Qwen Coder disponible"
        if policy == "cloud" and non_interactive:
            reason = "Cloud solicitado en modo no interactivo, pero falta DEEPSEEK_API_KEY"
        return ComputeResolution(None, None, policy, priority, "static-fallback", True, reason)

