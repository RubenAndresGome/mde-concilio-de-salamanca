"""
Esquemas Pydantic y TypedDict para los tipos de datos del Concilio de Salamanca.

Define: DebateState, AgentOutput, AgentVeredict, Silogismo, Veredicto,
PnCValidation, Determinatio, VotingTable, StaticAnalysis.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional, TypedDict

from pydantic import BaseModel, Field


class Veredicto(str, Enum):
    CONDENA = "CONDENA"
    ABSUELVE = "ABSUELVE"
    RESERVA = "RESERVA"


class Silogismo(BaseModel):
    premisa_mayor: str = Field(..., description="Premisa mayor universal")
    premisa_mayor_tipo: Optional[str] = Field(
        default=None, description="Tipo A/E/I/O de la premisa mayor"
    )
    premisa_menor: str = Field(..., description="Premisa menor particular")
    premisa_menor_tipo: Optional[str] = Field(
        default=None, description="Tipo A/E/I/O de la premisa menor"
    )
    conclusion: str = Field(..., description="Conclusión necesaria deducida")
    conclusion_tipo: Optional[str] = Field(
        default=None, description="Tipo A/E/I/O de la conclusión"
    )


class AgentVeredict(BaseModel):
    agente: str = Field(..., description="Nombre del agente emisor")
    rol: str = Field(..., description="Rol del agente en el Concilio")
    silogismo: Silogismo = Field(..., description="Silogismo formal estructurado")
    principio_no_contradiccion: bool = Field(
        default=True,
        description="Indica si el razonamiento respeta el Principio de No Contradicción",
    )
    veredicto: Veredicto = Field(..., description="CONDENA, ABSUELVE o RESERVA")
    fundamento: str = Field(
        default="", description="Fundamentación adicional del veredicto"
    )
    preguntas_casuisticas: List[str] = Field(
        default_factory=list,
        description="Dos o tres casos limite no redundantes que faltan por determinar",
    )


class AgentOutput(BaseModel):
    raw: str = Field(..., description="Respuesta textual completa del agente")
    structured: Optional[AgentVeredict] = Field(
        default=None, description="Respuesta parseada estructurada"
    )
    timestamp: float = Field(default=0, description="Timestamp del razonamiento")
    compact: str = Field(default="", description="Ledger interno en cave-protocol")
    usage: Dict[str, int] = Field(default_factory=dict, description="Uso reportado por el proveedor")
    model: str = Field(default="", description="Modelo que produjo la salida")
    latency_ms: float = Field(default=0, description="Latencia de la llamada")
    parse_error: bool = Field(default=False, description="Indica salida no estructurable")
    cached: bool = Field(default=False, description="Resultado recuperado de caché local")


class Contradiccion(BaseModel):
    agente_a: str
    agente_b: str
    proposicion_a: str
    proposicion_b: str
    descripcion: str


class PnCValidation(BaseModel):
    hay_contradicciones: bool = False
    contradicciones: List[Contradiccion] = Field(default_factory=list)
    resumen: str = ""
    principio_violado: bool = False


class Determinatio(BaseModel):
    quaestio: str = Field(..., description="La cuestión planteada")
    videtur: str = Field(..., description="Argumentos a favor (lo que parece)")
    sed_contra: str = Field(..., description="Argumentos en contra")
    respondeo: str = Field(..., description="Resolución razonada del Magister")
    determinatio_codici: str = Field(
        ..., description="Veredicto final y código corregido si aplica"
    )
    veredicto_final: Veredicto = Field(..., description="CONDENA, ABSUELVE o RESERVA")
    pnc_validation: Optional[PnCValidation] = Field(
        default=None, description="Validación del Principio de No Contradicción"
    )


class DebateState(TypedDict, total=False):
    code: str
    language: str
    round_num: int
    max_rounds: int
    static_analysis: Optional[str]
    agent_outputs: Dict[str, AgentOutput]
    arguments_history: List[Dict]
    pnc_validation: Optional[PnCValidation]
    determinatio: Optional[Determinatio]
    error: Optional[str]
    voting_summary: Optional[Dict]
    pending_questions: List[str]
    socratic_checks: Optional[List[str]]
    murphy_checks: Optional[List[str]]
    ockham_analysis: Optional[Dict]
    token_metrics: Optional[Dict[str, int]]
    usage: Optional[Dict]
    budget: Optional[Dict]
    cache_hit_ratio: Optional[float]
    calls_by_model: Optional[Dict[str, int]]
    stop_reason: Optional[str]
    escalation: Optional[Dict]


class AgentVote(BaseModel):
    agente: str
    veredicto: Veredicto
    silogismo_resumen: str = ""


class VotingTable(BaseModel):
    votos: List[AgentVote] = Field(default_factory=list)
    condenas: int = 0
    absoluciones: int = 0
    reservas: int = 0
    consenso: bool = False
    veredicto_mayoritario: Optional[Veredicto] = None


class SARIFReport(BaseModel):
    version: str = "2.1.0"
    runs: List[Dict] = Field(default_factory=list)


class StaticAnalysis(BaseModel):
    metrics: Dict[str, object] = Field(default_factory=dict)
    summary: str = ""
