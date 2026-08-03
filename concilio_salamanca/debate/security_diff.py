"""Activa seguridad sólo cuando el diff toca una superficie de ataque."""

from __future__ import annotations

import re


SURFACES = {
    "auth": r"\b(auth|oauth|jwt|session|cookie|password|credential)\b",
    "injection": r"\b(eval|exec|subprocess|shell|query|sql|deserialize|pickle)\b",
    "network": r"\b(http|socket|cors|tls|webhook|endpoint|route)\b",
    "filesystem": r"\b(open\(|write|unlink|remove|chmod|pathlib|upload)\b",
    "secrets": r"\b(secret|api[_-]?key|private[_-]?key|token)\b",
}


def detect_security_surfaces(diff: str) -> dict:
    added = "\n".join(line[1:] for line in str(diff).splitlines() if line.startswith("+") and not line.startswith("+++"))
    matches = {
        name: sorted(set(match.group(0).lower() for match in re.finditer(pattern, added, re.IGNORECASE)))
        for name, pattern in SURFACES.items()
    }
    matches = {key: values for key, values in matches.items() if values}
    return {"activate_security": bool(matches), "surfaces": matches, "selected_chars": len(added)}

