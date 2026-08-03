"""Fachada de vecindarios SQLite para no cargar el repositorio completo."""

from __future__ import annotations

from concilio_salamanca.debate.council_store import CouncilStore


def architecture_neighborhood(query: str, *, db_path: str | None = None, limit: int = 8, hops: int = 1) -> dict:
    return CouncilStore(db_path).local_context(query, limit=max(1, min(limit, 20)), hops=max(0, min(hops, 3)))
