"""Selección barata de pruebas afectadas por nombre/ruta/dependencias explícitas."""

from __future__ import annotations

from pathlib import PurePath
from typing import Iterable, Mapping


def select_impacted_tests(
    changed_files: Iterable[str],
    test_files: Iterable[str],
    dependency_edges: Mapping[str, Iterable[str]] | None = None,
) -> list[str]:
    changed = {str(PurePath(path)).replace("\\", "/") for path in changed_files}
    stems = {PurePath(path).stem.lower() for path in changed}
    dependencies = dependency_edges or {}
    impacted = set()
    for test in test_files:
        normalized = str(PurePath(test)).replace("\\", "/")
        low = normalized.lower()
        if any(stem and stem in low for stem in stems):
            impacted.add(normalized)
            continue
        covered = {str(PurePath(path)).replace("\\", "/") for path in dependencies.get(normalized, [])}
        if covered & changed:
            impacted.add(normalized)
    return sorted(impacted)

