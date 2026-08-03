# Changelog — MDE Politeia Conciliar de Salamanca

## v1.1.0 (2026-08-02) — Economía cognitiva

### Nuevo
- Niveles de auditoría 0–3, `--fast` como alias económico y presupuestos reales.
- `ComputePolicyResolver`: DeepSeek V4 Flash/Pro, fallback Ollama y `RESERVA` estática.
- Prefijo compartido para caché, cave-protocol y ledger comprimido para Magister.
- PnC booleana, parada al 67%, veto estático de hallazgos críticos y escalamiento aprobado.
- Micro-herramientas `context_sieve`, `security_diff`, `test_impact` y `debug_evidence`.
- Métricas de tokens, caché, latencia, costo, causa de parada y llamadas por modelo.

## v5.0.0 (2026-06-25) — Grafo de Conocimiento + Logica de Conjuntos

### Nuevo
- 40 agentes IA + 1 Magister Determinans (41 clases)
- Agente OckhamDev (Navaja de la No-Contradiccion + logica de conjuntos)
- Codebase Memory MCP integrado (grafo de conocimiento)
- Chequeo hilemorfico (materia/forma) via CBMM
- Agente Lector Externus (Website Downloader)
- Socorro extendido: Abogado del Diablo + 5S + 5 Whys
- Six Sigma extendido: 5S + 5 Whys aristotelicos
- OckhamDev extendido: chequeo hilemorfico + modo degradado
- _enforce_dialectica() en orquestador
- .mde_history/ con arquitectura 5S + PDCA
- RNS v5.0: Diezmo sin Compliance 0-3%, Derivative Work 50% recargo
- FRN_ROADMAP.md: Manifiesto Politeia de Desarrolladores
- MANUAL.md: Guia paso a paso con diagramas
- AGENTS.md: Instrucciones para AI agents
- MANUAL.md: Guia paso a paso con diagramas
- modelo de precios + ModelRanker

### Changed
- Refactorizacion Clean Code del orquestador (SRP, funciones <20 lineas)
- SKILL.md actualizado con 40 agentes, RNS v5.0, CBMM
- RNS v4.0 → v5.0: tabla plana, modelo Deuda, auditoria CI, Bulas
- Reformateo MDE_Skill_core.md (de 1 linea a 459 lineas, 16 secciones)

## v1.0.0 (2026-06-25) — Lanzamiento Open Source

### Nuevo
- 38 agentes IA con silogismos ontologicos
- 6 proveedores LLM: OpenAI, DeepSeek, Anthropic, Groq, Ollama, OpenRouter
- PyPI package (`pip install concilio-salamanca`)
- GitHub Actions CI (lint + test 3.11/3.12/3.13 + build)
- CLI entry point (`concilio --file app.js`)
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
