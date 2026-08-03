"""Perfiles deterministas de economía cognitiva del Concilio."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

from concilio_salamanca.agents import resolve_agents


@dataclass(frozen=True)
class AuditProfile:
    level: int
    name: str
    max_agents: int
    max_rounds: int
    max_calls: int
    agent_max_tokens: int
    magister_max_tokens: int
    use_magister: bool
    question_limit: int
    consensus_threshold: float = 0.67


AUDIT_PROFILES = {
    0: AuditProfile(0, "estatico", 0, 0, 0, 0, 0, False, 0),
    1: AuditProfile(1, "economico", 2, 1, 2, 384, 0, False, 2),
    2: AuditProfile(2, "normal", 3, 2, 6, 512, 768, True, 3),
    3: AuditProfile(3, "pleno", 5, 2, 11, 768, 1200, True, 3),
}


def get_audit_profile(level: int) -> AuditProfile:
    try:
        return AUDIT_PROFILES[int(level)]
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("audit_level debe ser 0, 1, 2 o 3") from error


def detect_specialist(code: str, language: str = "auto") -> str:
    """Elige un único especialista por superficie observable, sin LLM."""
    sample = f"{language}\n{code}".lower()
    security = (
        "password", "secret", "token", "jwt", "oauth", "crypto", "subprocess",
        "eval(", "exec(", "sql injection", "deserialize", "pickle", "chmod",
    )
    data = ("select ", "insert ", "update ", "sqlite", "postgres", "database", "orm")
    frontend = ("react", "vue", "angular", "css", "html", "dom", "component", "useeffect")
    mlops = ("pytorch", "tensorflow", "sklearn", "model.fit", "dockerfile", "kubernetes")
    embedded = ("arduino", "gpio", "firmware", "interrupt", "microcontroller", "mqtt")
    if any(term in sample for term in security):
        return "seguridad"
    if any(term in sample for term in data):
        return "datos"
    if any(term in sample for term in frontend):
        return "magister_delineationis"
    if any(term in sample for term in mlops):
        return "mlops"
    if any(term in sample for term in embedded):
        return "iot"
    return "linus"


def select_profile_agents(
    level: int,
    code: str,
    language: str = "auto",
    requested: Optional[Iterable[str]] = None,
) -> List[str]:
    profile = get_audit_profile(level)
    if profile.max_agents == 0:
        return []
    if requested:
        explicit = resolve_agents(list(requested))
        if explicit:
            return explicit[: profile.max_agents]
    specialist = detect_specialist(code, language)
    if level == 1:
        candidates = ["arquimedes", specialist]
    elif level == 2:
        candidates = ["promotor", "defensor", specialist]
    else:
        candidates = ["promotor", "defensor", "doctor", "larouche", specialist]
    unique = []
    for key in candidates:
        if key not in unique:
            unique.append(key)
    for fallback in ("arquimedes", "linus", "leon_xiii"):
        if len(unique) >= profile.max_agents:
            break
        if fallback not in unique:
            unique.append(fallback)
    return unique[: profile.max_agents]

