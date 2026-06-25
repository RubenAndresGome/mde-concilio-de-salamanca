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
    premisa_menor: str = Field(..., description="Premisa menor particular")
    conclusion: str = Field(..., description="Conclusión necesaria deducida")


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


class AgentOutput(BaseModel):
    raw: str = Field(..., description="Respuesta textual completa del agente")
    structured: Optional[AgentVeredict] = Field(
        default=None, description="Respuesta parseada estructurada"
    )
    timestamp: float = Field(default=0, description="Timestamp del razonamiento")


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
    promotor: Optional[AgentOutput]
    defensor: Optional[AgentOutput]
    doctor: Optional[AgentOutput]
    larouche: Optional[AgentOutput]
    leon_xiii: Optional[AgentOutput]
    arguments_history: List[Dict]
    pnc_validation: Optional[PnCValidation]
    determinatio: Optional[Determinatio]
    error: Optional[str]
    voting_summary: Optional[Dict[str, int]] = None


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
