# Contribuyendo al Concilio de Salamanca

¡Gracias por tu interés en contribuir! Este proyecto es una skill MDE (Meta Dialéctica Escolástica) para auditoría de código.

## Cómo Contribuir

### Reportar Bugs
1. Verifica que el bug no haya sido reportado ya en [Issues](https://github.com/anomalyco/opencode/issues)
2. Incluye: descripción, pasos para reproducir, comportamiento esperado vs actual, logs

### Sugerir Mejoras
1. Describe el problema que resuelves y por qué beneficiaría al Concilio
2. Si es un nuevo agente, incluye el silogismo ontológico y las reglas de hierro

### Pull Requests
1. Haz fork del repositorio
2. Crea una rama: `git checkout -b feature/mi-mejora`
3. Haz commit con mensajes claros (los commits deben ser atómicos)
4. Asegura que los tests pasen: `pytest concilio_salamanca/tests/`
5. Envía el PR describiendo los cambios

### Guía de Estilo
- Sigue Clean Code: funciones <20 líneas, nombres semánticos, SRP
- Los agentes siguen el patrón `AgentFromPrompt` en `agents/base.py`
- Los prompts están en `prompts/system_prompts.py`
- Los precios de modelos en `debate/model_pricing.py`

### Ejecutar Tests
```bash
pip install -e ".[dev]"
pytest concilio_salamanca/tests/ -v
```

## Estructura del Proyecto
```
concilio_salamanca/
├── main.py              # CLI entry point
├── agents/              # Agentes del Concilio
├── debate/              # Orquestación, proveedores, lógica
├── prompts/             # System prompts de todos los agentes
├── reference/           # Anti-patrones, componentes, templates
├── templates/           # Brand contract DESIGN.md
├── tests/               # Tests unitarios y de integración
```
