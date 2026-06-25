# Changelog — Concilio de Salamanca

## v1.0.0 (2026-06-25) — Lanzamiento Open Source

### Nuevo
- 38 agentes IA con silogismos ontológicos
- 6 proveedores LLM: OpenAI, DeepSeek, Anthropic, Groq, Ollama, OpenRouter
- ModelRanker: selección automática calidad-precio-disponibilidad
- Spec-Kit SDD integrado (modo `--mode sdd|pdca|auto`)
- Open-Design MCP para prototipos visuales (`Magister Delineationis`)
- 3 agentes Clean Code: Arquímedes, Custos Impacti, Magister Processus Integri
- Validaciones Socráticas y Ley de Murphy en el ciclo de debate
- Contexto Git + .mde_history para agentes de proceso
- PyPI package (`pip install concilio-salamanca`)
- CLI entry point (`concilio --file app.js`)
- GitHub Actions CI (lint + test 3.11/3.12/3.13 + build)

### Changed
- Refactorización Clean Code del orquestador (SRP, funciones <20 líneas)
- DebateState extendido con pending_questions, socratic_checks, murphy_checks
- Config YAML con model_weights, roles, budget
