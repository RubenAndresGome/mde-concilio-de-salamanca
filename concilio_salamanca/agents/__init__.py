from __future__ import annotations

import sys
import types

from concilio_salamanca.agents.base import AgenteBase, AgentFromPrompt
from concilio_salamanca.agents.magister_determinans import MagisterDeterminans
from concilio_salamanca.prompts import system_prompts


def _create_agent_class(role_name: str, system_prompt: str) -> type:
    class DynamicAgent(AgentFromPrompt):
        def __init__(self, model):
            super().__init__(role_name, system_prompt, model)

    return DynamicAgent


AGENT_DEFS = {
    "promotor": (
        "Promotor Fidei",
        system_prompts.PROMOTOR_FIDEI,
        "promotor_fidei",
        "PromotorFidei",
    ),
    "defensor": (
        "Defensor Causae Finalis",
        system_prompts.DEFENSOR_CAUSA_FINAL,
        "defensor_causa_final",
        "DefensorCausaFinal",
    ),
    "doctor": (
        "Doctor Materiae",
        system_prompts.DOCTOR_MATERIA,
        "doctor_materia",
        "DoctorMateria",
    ),
    "larouche": (
        "Arquitecto LaRouche",
        system_prompts.ARQUITECTO_LAROUCHE,
        "arquitecto_larouche",
        "ArquitectoLarouche",
    ),
    "leon_xiii": (
        "Defensor Leonis XIII",
        system_prompts.DEFENSOR_LEON_XIII,
        "defensor_leon_xiii",
        "DefensorLeonXIII",
    ),
    "linus": (
        "Linus Torvalds (Pragmaticus Maximus)",
        system_prompts.LINUS_TORVALDS,
        "linus_torvalds",
        "LinusTorvalds",
    ),
    "wozniak": (
        "Steve Wozniak (Artifex Elegantiae)",
        system_prompts.STEVE_WOZNIAK,
        "steve_wozniak",
        "SteveWozniak",
    ),
    "stallman": (
        "Richard Stallman (Custos Libertatis)",
        system_prompts.RICHARD_STALLMAN,
        "richard_stallman",
        "RichardStallman",
    ),
    "stroustrup": (
        "Bjarne Stroustrup (Architectus Typorum)",
        system_prompts.BJARNE_STROUSTRUP,
        "bjarne_stroustrup",
        "BjarneStroustrup",
    ),
    "thompson": (
        "Ken Thompson (Philosophus Unixis)",
        system_prompts.KEN_THOMPSON,
        "ken_thompson",
        "KenThompson",
    ),
    "korotkevich": (
        "Gennady Korotkevich (Certator Optimus)",
        system_prompts.GENNADY_KOROTKEVICH,
        "gennady_korotkevich",
        "GennadyKorotkevich",
    ),
    "auditor_dl": (
        "Auditor Profundi (Deep Learning)",
        system_prompts.AUDITOR_DEEP_LEARNING,
        "auditor_dl",
        "AuditorDeepLearning",
    ),
    "seguridad": (
        "Custos Securitatis (Security)",
        system_prompts.ANALISTA_SEGURIDAD,
        "analista_seguridad",
        "AnalistaSeguridad",
    ),
    "mlops": (
        "Architectus Pipeline (MLOps)",
        system_prompts.INGENIERO_MLOPS,
        "ingeniero_mlops",
        "IngenieroMLOps",
    ),
    "datos": (
        "Purgator Datorum (Data Sanitation)",
        system_prompts.SANITARIO_DATOS,
        "sanitario_datos",
        "SanitarioDatos",
    ),
    "sistemas": (
        "Architectus Systematis (Systems)",
        system_prompts.ARQUITECTO_SISTEMAS,
        "arquitecto_sistemas",
        "ArquitectoSistemas",
    ),
    "iot": (
        "Architectus Siliconis (IoT Embedded)",
        system_prompts.INGENIERO_IOT,
        "ingeniero_iot",
        "IngenieroIoT",
    ),
    "socrates": (
        "Socrates (Philosophus Elenchus)",
        system_prompts.SOCRATES,
        "socrates",
        "Socrates",
    ),
    "scrum": (
        "Magister Processus (Scrum Master)",
        system_prompts.SCRUM_MASTER,
        "scrum_master",
        "ScrumMaster",
    ),
    "sixsigma": (
        "Magister Qualitatis (Six Sigma)",
        system_prompts.SIX_SIGMA,
        "six_sigma",
        "SixSigma",
    ),
    "llull": (
        "Architectus Arboris (Ramon Llull)",
        system_prompts.LLULL,
        "llull",
        "Llull",
    ),
    "bacon": (
        "Magister Experientiae (Roger Bacon)",
        system_prompts.BACON,
        "bacon",
        "Bacon",
    ),
    "vitoria": (
        "Custos Iuris (Francisco de Vitoria)",
        system_prompts.VITORIA,
        "vitoria",
        "Vitoria",
    ),
    "ratio": (
        "Magister Pedagogiae (Ratio Studiorum)",
        system_prompts.RATIO,
        "ratio",
        "Ratio",
    ),
    "ponytail": (
        "Magister Minimalis (Ponytail/YAGNI)",
        system_prompts.PONYTAIL,
        "ponytail",
        "Ponytail",
    ),
    "graphify": (
        "Magister Ontologicus (Graphify)",
        system_prompts.GRAPHIFY,
        "graphify",
        "Graphify",
    ),
    "rtk": ("Magister Signalis (RTK)", system_prompts.RTK, "rtk", "RTK"),
    "telemetry": (
        "Magister Telemetriae (Token Auditor)",
        system_prompts.TELEMETRY,
        "telemetry",
        "Telemetry",
    ),
    "redteam": (
        "Red Team Coordinator",
        system_prompts.REDTEAM,
        "redteam",
        "RedTeamCoordinator",
    ),
    "pentest": (
        "PenTest+ Auditor",
        system_prompts.PENTEST,
        "pentest",
        "PentestAuditor",
    ),
    "abuser": (
        "Abuser Story Generator",
        system_prompts.ABUSER,
        "abuser",
        "AbuserStoryGenerator",
    ),
    "causas": (
        "Analista Causal Aristotelico",
        system_prompts.CAUSAS,
        "causas",
        "AnalistaCausal",
    ),
    "leibniz": (
        "Optimista Leibniziano",
        system_prompts.LEIBNIZ,
        "leibniz",
        "OptimistaLeibniziano",
    ),
    "nietzsche": (
        "Vitalista Nietzscheano",
        system_prompts.NIETZSCHE,
        "nietzsche",
        "VitalistaNietzscheano",
    ),
    "magister_processus": (
        "Magister Processus Integri (PDCA+Scrum)",
        system_prompts.MAGISTER_PROCESSUS_INTEGRI,
        "magister_processus_integri",
        "MagisterProcessusIntegri",
    ),
    "arquimedes": (
        "Arquimedes (Magister Artis/Clean Code)",
        system_prompts.ARQUIMEDES,
        "arquimedes",
        "Arquimedes",
    ),
    "custos_impacti": (
        "Custos Impacti (Analista de Impacto Local)",
        system_prompts.CUSTOS_IMPACTI,
        "custos_impacti",
        "CustosImpacti",
    ),
    "magister_delineationis": (
        "Magister Delineationis (Arquitecto Visual)",
        system_prompts.MAGISTER_DELINEATIONIS,
        "magister_delineationis",
        "MagisterDelineationis",
    ),
    "ockham": (
        "OckhamDev (Navaja de la No-Contradiccion)",
        system_prompts.OCKHAMDEV,
        "ockham_dev",
        "OckhamDev",
    ),
    "lector_externus": (
        "Lector Externus (Website Downloader)",
        system_prompts.LECTOR_EXTERNUS,
        "lector_externus",
        "LectorExternus",
    ),
}

AGENT_REGISTRY = {}

# Populate globals and create dynamic submodules
for key, (label, prompt, mod_name, class_name) in AGENT_DEFS.items():
    cls = _create_agent_class(label, prompt)
    cls.__name__ = class_name
    globals()[class_name] = cls
    AGENT_REGISTRY[key] = (label, cls)

    # Virtual module creation to support backwards-compatible imports
    full_mod_name = f"concilio_salamanca.agents.{mod_name}"
    m = types.ModuleType(full_mod_name)
    setattr(m, class_name, cls)
    sys.modules[full_mod_name] = m

# MagisterDeterminans is imported and exposed but not part of debate AGENT_REGISTRY.

AGENT_GROUPS = {
    "todos": list(AGENT_REGISTRY.keys()),
    "escolasticos": ["promotor", "defensor", "doctor", "larouche", "leon_xiii"],
    "pragmaticos": ["linus", "wozniak", "thompson", "lector_externus"],
    "eticos": ["stallman", "stroustrup"],
    "algoritmicos": ["korotkevich"],
    "tecnicos": ["auditor_dl", "seguridad", "mlops", "datos", "sistemas", "iot"],
    "acusacion": ["promotor", "larouche", "linus", "korotkevich", "seguridad"],
    "defensa": [
        "defensor",
        "doctor",
        "leon_xiii",
        "wozniak",
        "stallman",
        "stroustrup",
        "thompson",
    ],
    "embebidos": ["iot", "wozniak", "thompson", "sistemas"],
    "seguridad_completa": [
        "promotor",
        "defensor",
        "doctor",
        "seguridad",
        "mlops",
        "datos",
    ],
    "ia_produccion": [
        "auditor_dl",
        "mlops",
        "datos",
        "sistemas",
        "seguridad",
        "promotor",
    ],
    "calidad": ["sixsigma", "scrum", "mlops", "datos"],
    "dialecticos": ["socrates", "promotor", "defensor"],
    "metodologia": ["scrum", "sixsigma"],
    "ius_gentium": ["vitoria", "stallman", "leon_xiii"],
    "pedagogicos": ["ratio", "socrates"],
    "empiristas": ["bacon", "linus", "thompson"],
    "token_optimizers": ["ponytail", "rtk", "telemetry", "graphify"],
    "red_team": ["redteam", "pentest", "abuser", "seguridad", "lector_externus"],
    "filosofos_aplicados": ["leibniz", "nietzsche", "socrates", "causas"],
    "clean_code": ["arquimedes", "custos_impacti", "magister_processus"],
    "proceso": ["scrum", "sixsigma", "magister_processus"],
    "delineatio": ["magister_delineationis", "vitoria", "ratio"],
    "logici": ["ockham", "socrates", "bacon", "leibniz"],
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
    "AgentFromPrompt",
    "MagisterDeterminans",
    "AGENT_REGISTRY",
    "AGENT_GROUPS",
    "get_agent_keys",
    "get_agent_label",
    "get_agent_cls",
    "resolve_agents",
    "list_agents",
] + [class_name for _, (_, _, _, class_name) in AGENT_DEFS.items()]
