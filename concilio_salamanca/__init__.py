"""
Concilio de Salamanca — MDE Skill de Auditoria de Codigo.

Sistema de 38 agentes IA especializados que debaten usando logica
aristotelico-tomista y emiten un veredicto estructurado.
"""

from __future__ import annotations

from concilio_salamanca.schemas import (
    AgentOutput,
    AgentVeredict,
    Contradiccion,
    DebateState,
    Determinatio,
    PnCValidation,
    Silogismo,
    Veredicto,
    VotingTable,
)

__version__ = "1.0.0"
__all__ = [
    "AgentOutput",
    "AgentVeredict",
    "Contradiccion",
    "DebateState",
    "Determinatio",
    "PnCValidation",
    "Silogismo",
    "Veredicto",
    "VotingTable",
]
