# Implementación de la Fase 3 Completa

Este plan detalla la implementación de todas las tareas pertenecientes a la **Fase 3** del Concilio de Salamanca (Hacia la Visión Completa), tal y como se define en `analysis_concilio_salamanca.md`. 

Dada la magnitud de estas implementaciones (AST parsing profundo, verificación formal con Z3, protocolo MCP, etc.), se propone avanzar en las siguientes sub-etapas.

## User Review Required

> [!WARNING]
> La Fase 3 requiere añadir dependencias significativas como `tree-sitter`, `z3-solver` y frameworks para la interfaz web. Esto aumentará la complejidad de instalación y el tamaño del proyecto.
> Además, F3-4 requiere un A/B test con 100 archivos, lo que incurrirá en costos de API LLM (estimado ~20-50 USD según el modelo y longitud del código).

## Open Questions

> [!IMPORTANT]
> Necesito clarificación sobre los siguientes puntos antes de comenzar la ejecución:
> 1. **Tree-sitter (F3-1):** ¿Para qué lenguajes iniciales debemos dar soporte de AST parsing? (Por defecto asumiré Python y JavaScript/TypeScript).
> 2. **Dashboard Web (F3-6):** ¿Qué framework prefieres para el dashboard? Opciones sugeridas: **Streamlit** (rápido de implementar, enfocado en Python) o **Vite+React** (más robusto pero requiere una API backend separada).
> 3. **A/B Testing (F3-4):** ¿Deseas que prepare los scripts para el A/B test con los 100 archivos o preferirías que primero nos enfoquemos en construir la infraestructura técnica (Z3, MCP, AST)?

## Proposed Changes

### 1. Integración Tree-sitter (F3-1)

Se reemplazará el análisis estático basado en expresiones regulares por análisis sintáctico real.

#### [MODIFY] `concilio_salamanca/debate/static_analysis.py`
Se refactorizará para utilizar `tree-sitter`. Extraerá métricas verdaderas: complejidad ciclomática basada en ramas AST, detección de hooks/decoradores exacta, y árbol de dependencias. Se actualizará el analizador para inyectar este árbol simplificado en el contexto de los agentes.

#### [MODIFY] `concilio_salamanca/requirements.txt`
Se añadirá `tree-sitter` y los conectores correspondientes (ej. `tree-sitter-python`, `tree-sitter-javascript`).

---

### 2. Verificación Formal con Z3 (F3-2 y F3-5)

Se integrará el solver SMT Z3 para validación formal y verificación de invariantes.

#### [NEW] `concilio_salamanca/debate/formal_verification.py`
Este módulo tomará las aserciones de los agentes (ej. "el bucle terminará", "la variable X nunca será nula") y las traducirá a predicados Z3. Implementará la validación PnC de contradicciones lógicas usando álgebra booleana asistida por el SMT solver.

#### [NEW] `concilio_salamanca/debate/loop_invariants.py`
Implementará el motor "Guess-and-Check" (F3-5). Pedirá al LLM adivinar invariantes candidatos, los pasará a Z3 como precondiciones, e iterará si Z3 encuentra un contraejemplo.

#### [MODIFY] `concilio_salamanca/debate/validator_pnc.py`
Delegará las contradicciones de pura lógica proposicional a Z3, y reservará el LLM para evaluar si los términos semánticos son equivalentes.

---

### 3. Model Context Protocol - MCP (F3-3)

Dotaremos a los agentes de capacidades de grounding real mediante el estándar MCP.

#### [NEW] `concilio_salamanca/debate/mcp_client.py`
Implementación de un cliente MCP básico para que el orquestador exponga herramientas a los agentes (por ejemplo, buscar en documentación, invocar linters como Semgrep localmente, chequear vulnerabilidades npm).

#### [MODIFY] `concilio_salamanca/agents/base.py`
Se habilitará el uso de herramientas MCP en la invocación del LLM.

---

### 4. Dashboard Web (F3-6)

Visualización interactiva del debate y métricas en tiempo real.

#### [NEW] `concilio_salamanca/dashboard/app.py`
Aplicación web (Streamlit o equivalente) que escuchará los eventos emitidos por el Orchestrator. Mostrará la tabla de votaciones interactiva, el flujo del grafo y los silogismos descubiertos por el Precedent Engine.

#### [MODIFY] `concilio_salamanca/main.py`
Se añadirá un nuevo subcomando `dashboard` para lanzar la UI web.

---

### 5. Empaquetado y A/B Testing (F3-4 y F3-7)

#### [NEW] `concilio_salamanca/tests/ab_tester.py`
Script automatizado que ejecutará el sistema en 100 archivos del dataset (con silogismos vs sin silogismos) y comparará métricas de calidad y tokens gastados.

#### [NEW] `PROMPTS_OPEN_SOURCE.md`
Se extraerán los 18 system prompts a un documento Markdown independiente con licencia abierta, sirviendo como publicación del recurso (F3-7).

## Verification Plan

### Automated Tests
- `pytest tests/test_static_analysis_ast.py`: Para validar el parseo de tree-sitter.
- `pytest tests/test_z3_formal.py`: Para validar que el solver detecta correctamente la satisfacibilidad de aserciones puestas por los agentes.
- `pytest tests/test_mcp.py`: Para validar que las herramientas son accesibles vía LLM.

### Manual Verification
- Ejecutar el dashboard web localmente e inyectar un debate de prueba.
- Verificar la publicación correcta del archivo markdown con los prompts.
