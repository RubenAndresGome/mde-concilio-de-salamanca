"""Preguntas casuisticas acotadas: agotar clases de caso, no tokens."""

from __future__ import annotations

from typing import Iterable


CASE_TEMPLATES = (
    "Caso limite: ¿qué debe ocurrir con entrada vacia, nula o de tamaño maximo?",
    "Fallo externo: ¿qué conducta objetiva rige si red, modelo, disco o base de datos no responde?",
    "Concurrencia: ¿qué resultado debe prevalecer si dos agentes actuan al mismo tiempo?",
    "Autoridad: ¿qué orden prevalece si usuario, Dogma y evidencia verificable discrepan?",
    "Reversibilidad: ¿qué cambios requieren confirmacion porque no pueden deshacerse con seguridad?",
    "Temporalidad: ¿cuándo caduca esta regla y cómo se versiona su sustituta?",
    "Observabilidad: ¿qué evidencia permite demostrar después por qué se tomó la decisión?",
    "Privacidad: ¿qué datos no deben entrar al prompt, registro o memoria persistente?",
    "Presupuesto: ¿qué límite de tokens, costo o latencia obliga a degradar el procedimiento?",
    "Empate: ¿qué reserva o escalamiento se aplica si el colegio electoral no alcanza consenso?",
)


def exhaust_cases(context: str = "", answered: Iterable[str] = (), limit: int = 8) -> list[str]:
    seen = {item.strip().lower() for item in answered}
    limit = max(1, min(int(limit), len(CASE_TEMPLATES)))
    questions = [question for question in CASE_TEMPLATES if question.lower() not in seen]
    lowered = context.lower()
    if not any(word in lowered for word in ("token", "costo", "latencia")):
        questions.remove(CASE_TEMPLATES[8])
        questions.append(CASE_TEMPLATES[8])
    return questions[:limit]
