"""
MDE Politeia Conciliar de Salamanca — Auditoria de Codigo por Meta Dialectica Escolastica.

Sistema de 39 agentes IA especializados que debaten usando logica
aristotelico-tomista y emiten veredictos estructurados bajo el
Principio de No Contradiccion.
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
