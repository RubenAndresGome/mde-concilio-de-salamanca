# Tareas de Desarrollo: MDE Skill Módulos — Lanzamiento Open Source

## Fase 4 — Publicación y Community

- [x] **F4-0**: Agregar 6 agentes de seguridad ofensiva y filosofía aplicada
- [x] **F4-1**: Publicar paquete en PyPI (`pip install concilio-salamanca`)
  - [x] `pyproject.toml` con metadatos completos
  - [x] `__version__ = "1.0.0"` en `concilio_salamanca/__init__.py`
  - [x] `LICENSE` (MIT)
  - [x] `concilio` CLI entry point (`concilio --file app.js`)
- [x] **F4-2**: Integrar GitHub Actions
  - [x] `.github/workflows/ci.yml` — lint + test (3.11, 3.12, 3.13) + build & publish
- [x] **F4-3**: Documentación comunitaria
  - [x] `CODE_OF_CONDUCT.md`
  - [x] `CONTRIBUTING.md`
  - [x] `CHANGELOG.md`
- [ ] **F4-4**: Permitir creación de "Agentes Custom" mediante un DSL simple (pendiente)

## Fase 5 — Compatibilidad Muchos LLM y Clean Code
- [x] **F5-1 a F5-5**: Sistema multi-modelo, 3 agentes Clean Code, git context, Socratic/Murphy, refactor

## 5S — Housekeeping
- [x] SEIRI: Archivar markdowns obsoletos, eliminar archivos vacíos
- [x] SEITON: `.gitignore` con runtime artifacts
- [x] SEISO: Auditoría de imports — 0 muertos
- [x] SEIKETSU: Docstrings en módulos clave
- [x] SHITSUKE: 74/74 tests pasan

---

**Estado**: Listo para lanzar en GitHub + PyPI.
