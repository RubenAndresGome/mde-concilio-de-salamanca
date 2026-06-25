# Mejoras Concilio de Salamanca — Task Tracker

## Fase 0 — Bugs Bloqueantes
- [x] **F0-1**: Fix Magister — leer de `arguments_history` dinámicamente
- [x] **F0-2**: Eliminar código muerto en `format_output_executive` (L210-L222)
- [x] **F0-3**: Fix caché — incluir hash del contexto en fingerprint
- [x] **F0-4**: Hacer `DebateState` dinámico

## Fase 1 — Robustez
- [x] **F1-1**: Mejorar parseo JSON (regex + fallback robusto)
- [x] **F1-2**: Inyectar análisis estático como contexto a los agentes
- [x] **F1-3**: Conectar PrecedentEngine al flujo de debate
- [x] **F1-4**: Unificar implementaciones de grafo (eliminado `graph.py` obsoleto, corregido paralelismo en `send_graph.py`)
- [x] **F1-5**: Fix `detect_language()` — usar extensión primero
- [x] **F1-6**: Fix `providers.py` L87 — precedencia confusa
- [x] **F1-7**: Alertar al usuario cuando un agente falla parseo JSON (agregado warning a stderr)

## Fase 2 — Simplificación Arquitectónica
- [x] **F2-1**: Reemplazar 28 stubs por una sola clase parametrizada `AgentFromPrompt`
- [x] **F2-2**: Añadir ejecución paralela opcional con `asyncio.gather` para agentes en la misma ronda
- [x] **F2-3**: Crear modo `--fast` con 2-3 agentes y 1 ronda para CI/CD (latencia <30s)
- [x] **F2-4**: Separar `main.py` en módulos: `cli.py`, `formatters.py`, `voting.py`
- [x] **F2-5**: Mejorar `_classify_proposition()` usando LLM para clasificar A/E/I/O directamente
- [x] **F2-6**: Añadir tests de integración con mock LLM

## Fase 3 — Hacia la Visión Completa
- [x] **F3-1**: Integrar tree-sitter para AST parsing real (Python y JavaScript)
- [x] **F3-2**: Implementar Z3 para validación formal del PnC
- [x] **F3-3**: Implementar MCP (Model Context Protocol) para consultas externas
- [x] **F3-4**: Setup y test script para A/B Testing
- [x] **F3-5**: Implementar "Guess-and-Check" para invariantes de bucle con Z3
- [x] **F3-6**: Dashboard Web (Streamlit)
- [x] **F3-7**: Publicar system prompts (`PROMPTS_OPEN_SOURCE.md`)

## Fase 4 — Mantenimiento y Expansión Open Source
- [x] **F4-0**: Agregar 6 agentes de seguridad ofensiva y filosofía aplicada (redteam, pentest, abuser, causas, leibniz, nietzsche)
- `[ ]` **F4-1**: Publicar el paquete en PyPI (`pip install concilio-salamanca`)
- `[ ]` **F4-2**: Integrar nativamente con GitHub Actions / GitLab CI
- `[ ]` **F4-3**: Crear servidor de Discord / comunidad para discutir aportes de agentes
- `[ ]` **F4-4**: Permitir creación de "Agentes Custom" mediante un DSL simple

> **ESTADO GLOBAL:** Las fases 0, 1, 2 y 3 (Arquitectura Base, Verificación Formal y Herramientas UI/A-B) han sido **100% COMPLETADAS**. La Fase 4 ha iniciado exitosamente expandiendo el sistema a 34 agentes (Seguridad Ofensiva y Filosofía Aplicada).
