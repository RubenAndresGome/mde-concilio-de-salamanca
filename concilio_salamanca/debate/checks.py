"""
Validaciones Socráticas y Ley de Murphy para el ciclo de debate del Concilio.

- Socratic Checks: preguntas que exponen contradicciones y vacíos de información.
- Murphy Checks: análisis preventivo de fallos ("qué puede salir mal").
"""

from __future__ import annotations

from typing import Dict, List, Optional


SOCRATIC_QUESTIONS = [
    "¿Por qué este módulo necesita conocer la estructura interna de esta base de datos? (Ley de Demeter)",
    "¿Cómo garantiza este componente que las futuras extensiones no obligarán a reescribir su lógica? (OCP)",
    "¿Por qué llamamos '{name}' a esta entidad si no refleja una responsabilidad tangible del negocio?",
    "¿Qué pasa si el input esperado cambia de formato? ¿El código falla o se adapta?",
    "¿Cuál es la razón suficiente (Leibniz) para que exista esta abstracción en lugar de una más simple?",
    "¿Puede esta función ser reemplazada por una solución de la librería estándar? (YAGNI/Navaja de Occam)",
    "¿Este código resuelve el problema o solo oculta sus síntomas? (Causa raíz vs. parche)",
    "Si un nuevo desarrollador lee esto mañana, ¿entenderá el propósito sin documentación externa?",
]

MURPHY_CHECKS = [
    "¿Qué sucede si el servicio externo (API, base de datos, sistema de archivos) falla o retorna un resultado vacío?",
    "¿Qué ocurre si un agente sobreescribe un bloque de código al refactorizar y rompe un side-effect no documentado?",
    "¿Qué pasa si el usuario asigna un peso inválido (ej. 'foo': 999) en la configuración de modelos?",
    "¿Qué sucede si el archivo a auditar no existe o está vacío?",
    "¿Qué ocurre si el contexto acumulado del debate supera el límite de tokens del modelo?",
    "¿Qué pasa si dos modelos tienen exactamente el mismo peso en la config?",
    "¿Qué sucede si la API key del proveedor no está configurada o ha expirado?",
    "¿Qué ocurre si el parser de JSON de un agente falla y devuelve contenido no estructurado?",
    "¿Qué pasa si el repositorio Git tiene más de 10,000 commits? ¿El comando git log escala?",
    "¿Qué sucede si el código analizado contiene caracteres no UTF-8 o binarios?",
]


def run_socratic_check(
    agent_outputs: Dict[str, str],
    previous_checks: Optional[List[str]] = None,
) -> List[str]:
    """Genera preguntas socráticas pertinentes basadas en los outputs de los agentes.

    Analiza los argumentos de los agentes y selecciona preguntas del catalogo
    que sean relevantes al contexto del debate.
    """
    questions: List[str] = []
    seen = set(previous_checks or [])

    all_text = " ".join(agent_outputs.values()).lower()

    # Seleccionar preguntas relevantes basadas en keywords en los argumentos
    if any(w in all_text for w in ["base de datos", "database", "sql", "db", "consulta"]):
        q = SOCRATIC_QUESTIONS[0]
        if q not in seen:
            questions.append(q)
            seen.add(q)

    if any(w in all_text for w in ["extender", "futuro", "version", "cambio", "modificar"]):
        q = SOCRATIC_QUESTIONS[1]
        if q not in seen:
            questions.append(q)
            seen.add(q)

    if any(w in all_text for w in ["funcion", "clase", "metodo", "componente"]):
        q = SOCRATIC_QUESTIONS[2].format(name="[nombre]")
        if q not in seen:
            questions.append(q)
            seen.add(q)

    if any(w in all_text for w in ["input", "entrada", "parametro", "argumento"]):
        q = SOCRATIC_QUESTIONS[3]
        if q not in seen:
            questions.append(q)
            seen.add(q)

    # Siempre incluir al menos 2 preguntas generales si no hay especificas
    if len(questions) < 2:
        for q in SOCRATIC_QUESTIONS:
            if q not in seen:
                questions.append(q)
                seen.add(q)
                if len(questions) >= 3:
                    break

    return questions


def run_murphy_check(
    config_snapshot: dict,
    previous_checks: Optional[List[str]] = None,
) -> List[str]:
    """Genera advertencias de Murphy basadas en el contexto actual del debate.

    Revisa configuraciones, flujo de datos y supuestos para identificar
    puntos de fallo potenciales.
    """
    warnings: List[str] = []
    seen = set(previous_checks or [])

    for check in MURPHY_CHECKS:
        if check not in seen:
            warnings.append(check)
            seen.add(check)

    # Limitar a max 5 advertencias por ronda
    return warnings[:5]
