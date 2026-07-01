# PDCA_014 — Integracion Headroom (compresion de contexto) y Website-downloader (clonador offline) + LectorExternus

| Campo | Valor |
|---:|---|
| **ID Sesion** | `ses-headroom-website-downloader-integration` |
| **Fecha** | 2026-07-01T07:50:00 |
| **Accion** | refactor |
| **Estado** | completed |
| **Agentes activos** | 40 |
| **Tests** | 80 |
| **Tokens usados** | ~28,000 |

---

## Plan (Objetivo)

Integrar la biblioteca Headroom para la compresión de contexto en el flujo de envío de prompts del Concilio de Salamanca, clonar la herramienta Website-downloader e integrar un agente LectorExternus capaz de descargar y estructurar documentación web localmente.

---

## Do (Implementacion)

1. Clonado del repositorio `https://github.com/AhmadIbrahiim/Website-downloader.git` en `concilio_salamanca/tools/Website-downloader`.
2. Implementación de `concilio_salamanca/tools/website_downloader_wrapper.py` con fallback robusto en Python puro utilizando `html.parser` estándar para evitar dependencias externas no instaladas.
3. Integración de compresión de contexto Headroom (`headroom-ai`) en `concilio_salamanca/agents/base.py` de forma opcional (activada vía `HEADROOM_ENABLED=true` o de forma automática cuando el prompt supere 10,000 caracteres), transformando los mensajes LangChain al formato compatible con Headroom.
4. Definición y registro del agente `LECTOR_EXTERNUS` en `prompts/system_prompts.py`, `prompts/__init__.py` y `agents/__init__.py` (dentro de los grupos `pragmaticos` y `red_team`).
5. Creación de casos de prueba unitarios en `concilio_salamanca/tests/test_website_downloader.py` e integración de aserciones en `concilio_salamanca/tests/test_agents.py` para asegurar que el registro de agentes cuente ahora con 40 elementos y que la clase de LectorExternus sea funcional.

### Archivos Afectados

| Archivo | Accion |
|---|---|
| `concilio_salamanca/prompts/system_prompts.py` | modificado |
| `concilio_salamanca/prompts/__init__.py` | modificado |
| `concilio_salamanca/agents/__init__.py` | modificado |
| `concilio_salamanca/agents/base.py` | modificado |
| `concilio_salamanca/requirements.txt` | modificado |
| `concilio_salamanca/tools/website_downloader_wrapper.py` | creado |
| `concilio_salamanca/tests/test_website_downloader.py` | creado |
| `concilio_salamanca/tests/test_agents.py` | modificado |

---

## Check (Validacion)

80 tests pasan satisfactoriamente (`pytest concilio_salamanca/tests/`). La aserción del registro y la coherencia de grupos y dependencias pasaron correctamente.

---

*Archivo generado el 2026-07-01.*
*PDCA counter: 014*
