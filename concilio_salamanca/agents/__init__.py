from concilio_salamanca.agents.base import AgenteBase
from concilio_salamanca.agents.promotor_fidei import PromotorFidei
from concilio_salamanca.agents.defensor_causa_final import DefensorCausaFinal
from concilio_salamanca.agents.doctor_materia import DoctorMateria
from concilio_salamanca.agents.arquitecto_larouche import ArquitectoLarouche
from concilio_salamanca.agents.defensor_leon_xiii import DefensorLeonXIII
from concilio_salamanca.agents.magister_determinans import MagisterDeterminans
from concilio_salamanca.agents.linus_torvalds import LinusTorvalds
from concilio_salamanca.agents.steve_wozniak import SteveWozniak
from concilio_salamanca.agents.richard_stallman import RichardStallman
from concilio_salamanca.agents.bjarne_stroustrup import BjarneStroustrup
from concilio_salamanca.agents.ken_thompson import KenThompson
from concilio_salamanca.agents.gennady_korotkevich import GennadyKorotkevich
from concilio_salamanca.agents.auditor_dl import AuditorDeepLearning
from concilio_salamanca.agents.analista_seguridad import AnalistaSeguridad
from concilio_salamanca.agents.ingeniero_mlops import IngenieroMLOps
from concilio_salamanca.agents.sanitario_datos import SanitarioDatos
from concilio_salamanca.agents.arquitecto_sistemas import ArquitectoSistemas
from concilio_salamanca.agents.ingeniero_iot import IngenieroIoT
from concilio_salamanca.agents.socrates import Socrates
from concilio_salamanca.agents.scrum_master import ScrumMaster
from concilio_salamanca.agents.six_sigma import SixSigma
from concilio_salamanca.agents.llull import Llull
from concilio_salamanca.agents.bacon import Bacon
from concilio_salamanca.agents.vitoria import Vitoria
from concilio_salamanca.agents.ratio import Ratio

AGENT_REGISTRY = {
    "promotor": ("Promotor Fidei", PromotorFidei),
    "defensor": ("Defensor Causae Finalis", DefensorCausaFinal),
    "doctor": ("Doctor Materiae", DoctorMateria),
    "larouche": ("Arquitecto LaRouche", ArquitectoLarouche),
    "leon_xiii": ("Defensor Leonis XIII", DefensorLeonXIII),
    "linus": ("Linus Torvalds (Pragmaticus Maximus)", LinusTorvalds),
    "wozniak": ("Steve Wozniak (Artifex Elegantiae)", SteveWozniak),
    "stallman": ("Richard Stallman (Custos Libertatis)", RichardStallman),
    "stroustrup": ("Bjarne Stroustrup (Architectus Typorum)", BjarneStroustrup),
    "thompson": ("Ken Thompson (Philosophus Unixis)", KenThompson),
    "korotkevich": ("Gennady Korotkevich (Certator Optimus)", GennadyKorotkevich),
    "auditor_dl": ("Auditor Profundi (Deep Learning)", AuditorDeepLearning),
    "seguridad": ("Custos Securitatis (Security)", AnalistaSeguridad),
    "mlops": ("Architectus Pipeline (MLOps)", IngenieroMLOps),
    "datos": ("Purgator Datorum (Data Sanitation)", SanitarioDatos),
    "sistemas": ("Architectus Systematis (Systems)", ArquitectoSistemas),
    "iot": ("Architectus Siliconis (IoT Embedded)", IngenieroIoT),
    "socrates": ("Socrates (Philosophus Elenchus)", Socrates),
    "scrum": ("Magister Processus (Scrum Master)", ScrumMaster),
    "sixsigma": ("Magister Qualitatis (Six Sigma)", SixSigma),
    "llull": ("Architectus Arboris (Ramon Llull)", Llull),
    "bacon": ("Magister Experientiae (Roger Bacon)", Bacon),
    "vitoria": ("Custos Iuris (Francisco de Vitoria)", Vitoria),
    "ratio": ("Magister Pedagogiae (Ratio Studiorum)", Ratio),
}

AGENT_GROUPS = {
    "todos": list(AGENT_REGISTRY.keys()),
    "escolasticos": ["promotor", "defensor", "doctor", "larouche", "leon_xiii"],
    "pragmaticos": ["linus", "wozniak", "thompson"],
    "eticos": ["stallman", "stroustrup"],
    "algoritmicos": ["korotkevich"],
    "tecnicos": ["auditor_dl", "seguridad", "mlops", "datos", "sistemas", "iot"],
    "acusacion": ["promotor", "larouche", "linus", "korotkevich", "seguridad"],
    "defensa": ["defensor", "doctor", "leon_xiii", "wozniak", "stallman", "stroustrup", "thompson"],
    "embebidos": ["iot", "wozniak", "thompson", "sistemas"],
    "seguridad_completa": ["promotor", "defensor", "doctor", "seguridad", "mlops", "datos"],
    "ia_produccion": ["auditor_dl", "mlops", "datos", "sistemas", "seguridad", "promotor"],
    "calidad": ["sixsigma", "scrum", "mlops", "datos"],
    "dialecticos": ["socrates", "promotor", "defensor"],
    "metodologia": ["scrum", "sixsigma"],
    "ius_gentium": ["vitoria", "stallman", "leon_xiii"],
    "pedagogicos": ["ratio", "socrates"],
    "empiristas": ["bacon", "linus", "thompson"],
}

def get_agent_keys() -> list:
    return sorted(AGENT_REGISTRY.keys())

def get_agent_label(key: str) -> str:
    return AGENT_REGISTRY[key][0] if key in AGENT_REGISTRY else key

def get_agent_cls(key: str):
    return AGENT_REGISTRY[key][1] if key in AGENT_REGISTRY else None

def resolve_agents(selection: list) -> list:
    resolved = []
    for item in selection:
        item = item.strip().lower()
        if item in AGENT_GROUPS:
            resolved.extend(AGENT_GROUPS[item])
        elif item in AGENT_REGISTRY:
            resolved.append(item)
    return list(dict.fromkeys(resolved))

def list_agents():
    lines = []
    for key, (label, _) in AGENT_REGISTRY.items():
        lines.append(f"  {key:15s} {label}")
    lines.append("")
    lines.append("Grupos predefinidos:")
    for group, members in AGENT_GROUPS.items():
        lines.append(f"  {group:20s} {', '.join(members)}")
    return "\n".join(lines)


__all__ = [
    "AgenteBase",
    "PromotorFidei",
    "DefensorCausaFinal",
    "DoctorMateria",
    "ArquitectoLarouche",
    "DefensorLeonXIII",
    "MagisterDeterminans",
    "LinusTorvalds",
    "SteveWozniak",
    "RichardStallman",
    "BjarneStroustrup",
    "KenThompson",
    "GennadyKorotkevich",
    "AuditorDeepLearning",
    "AnalistaSeguridad",
    "IngenieroMLOps",
    "SanitarioDatos",
    "ArquitectoSistemas",
    "IngenieroIoT",
    "Socrates",
    "ScrumMaster",
    "SixSigma",
    "Llull",
    "Bacon",
    "Vitoria",
    "Ratio",
    "AGENT_REGISTRY",
    "AGENT_GROUPS",
    "get_agent_keys",
    "get_agent_label",
    "get_agent_cls",
    "resolve_agents",
    "list_agents",
]
