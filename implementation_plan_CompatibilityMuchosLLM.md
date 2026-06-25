# Plan de Implementación: Sistema PDCA, Compresión Inter-Agentes y Arquitectura Clean Code

Este plan detalla la estrategia integral para el Concilio de Salamanca, abarcando el ciclo PDCA, la gestión de modelos LLM mediante configuración pesada, el análisis de impacto arquitectónico bajo los principios de Clean Code y SOLID, y la inclusión de agentes inquisitivos y socráticos.

## 1. Configuración de Modelos (Jerarquía Director/Ejecutor)

Se añadirá un archivo de configuración (ej. `models_config.json` o extensión de `config.yaml`) donde el usuario define explícitamente los pesos de uso. El modelo default será DeepSeek (el más barato y eficiente como Ejecutor), mientras que los modelos "Thinking" operan como Directores.

```json
{
  "model_weights": {
    "DeepSeek": 1,
    "Claude Opus": 0,
    "QWen": 0,
    "GLM 5.2": 0,
    "GPT 5.5": 0
  },
  "roles": {
    "executor": "DeepSeek",
    "director_strategy": "Claude Opus"
  }
}
```
*Justificación:* Esto da control total al usuario sobre el presupuesto y permite una rápida transición si un modelo reduce sus costos.

## 2. Agentes Híbridos y Nuevos Roles (Clean Code)

### 2.1 Magister Processus Integri (PDCA + Scrum)
Este agente inquisitivo no solo lee el código, sino que investiga el entorno de desarrollo:
- **Lectura Activa:** Ejecutará `git log` y leerá el `.mde_history` del proyecto para medir velocidad, incrementos (D) y objetivos (P).
- **Inquisitivo:** Si encuentra vacíos de información o no comprende una métrica, pausará y **preguntará al usuario**. Mide tiempos, tokens y deuda técnica.
- **Mapeo:** Plan = Sprint Planning, Do = Commits/Ejecución, Check = Review/Métricas, Act = Refactorización.

### 2.2 Arquímedes (Magister Artis)
Basado en el tratado de **Clean Code y SOLID**:
- Se encarga de auditar nombres semánticos, tamaño de funciones (<20 líneas), y los principios SRP, OCP, LSP, ISP y DIP.
- Aplica la *Regla del Boy Scout* (dejar el código mejor de lo que se encontró) y exige pruebas unitarias y TDD como documentación viva.

### 2.3 Custos Impacti (Analista de Impacto Local)
Cuando se sugiere modificar o eliminar un componente, este agente realiza un análisis deductivo:
- **Último Término:** ¿Cuál es la consecuencia final de esta modificación?
- **Grafo de Dependencias:** ¿Qué otros módulos lo llaman? ¿Se rompe un contrato (violación LSP)?
- **Localidad:** Diseña planes de refactorización (ej. aplicando Adaptadores o Inversión de Dependencias) para asegurar que el impacto de la modificación sea estrictamente local.

## 3. Método Socrático y Ley de Murphy en el Análisis

### 3.1 Preguntas Socráticas (Evaluación Cognitiva)
Antes de aprobar cualquier cambio estructural, los agentes deberán resolver (o preguntar al usuario) las siguientes cuestiones:
- *¿Por qué este módulo necesita conocer la estructura interna de esta base de datos? (Ley de Demeter)*
- *¿Cómo garantiza este componente que las futuras extensiones no obligarán a reescribir su lógica? (OCP)*
- *¿Por qué llamamos "Processor" a esta clase si no refleja una entidad tangible del negocio?*

### 3.2 Prevención de Murphy (Análisis de Fallos)
Aplicación de la Ley de Murphy en cada *Determinatio*:
- *¿Qué pasa si el servicio externo (ej. Git log) falla o retorna un historial vacío?* (Fallo en la lectura de métricas).
- *¿Qué sucede si un agente sobreescribe un bloque de código al intentar "refactorizar localmente" y rompe un side-effect no documentado?* (Riesgo de modificación).
- *¿Qué ocurre si el usuario asigna peso `1` a dos modelos distintos en el JSON de configuración?*

## 4. Plan de Implementación de Leyes Clean Code

El sistema aplicará un **Protocolo Clean Code** al momento de procesar código fuente:
1. **Revisión Microscópica:** Identificar funciones largas, argumentos excesivos (más de 2), y nombres ambiguos. (Agente *Arquímedes*).
2. **Revisión Mesoscópica:** Validación de cohesión. Si una clase tiene más de una razón para cambiar (SRP), se sugiere división y uso de interfaces segregadas (ISP).
3. **Análisis Macroscópico:** Inversión de Dependencias (DIP) verificando que el dominio no dependa de implementaciones concretas como BD o UI.
4. **Refactorización Segura:** Asegurada mediante el análisis de impacto del *Custos Impacti*, aislando el cambio con Patrones Strategy o Puertos y Adaptadores.

## 5. Tareas a Ejecutar en el Sistema (Reflejado en task.md)
1. Adaptar `config.yaml` / JSON para leer los pesos del modelo (Default DeepSeek = 1).
2. Crear archivo `task.md` local para gestión de tareas de desarrollo.
3. Actualizar `agents/__init__.py` y `prompts/system_prompts.py` con los nuevos agentes (Arquímedes, Custos Impacti, Magister Processus Integri).
4. Implementar capacidad en el agente Scrum para usar la herramienta de línea de comandos (`git log`) y leer `.mde_history`.
5. Integrar validaciones Socráticas y de Murphy en el bucle del orquestador.
