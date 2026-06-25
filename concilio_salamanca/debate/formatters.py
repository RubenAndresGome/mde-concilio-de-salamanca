from __future__ import annotations

import json
from datetime import datetime
from concilio_salamanca.reference.determinatio_template import format_determinatio


def format_output_json(result: dict) -> str:
    determinatio = result.get("determinatio")
    pnc = result.get("pnc_validation")
    voting = result.get("voting", {})

    output = {
        "timestamp": datetime.now().isoformat(),
        "veredicto_final": determinatio.veredicto_final.value
        if determinatio
        else "ERROR",
        "determinatio": determinatio.model_dump() if determinatio else None,
        "voting": voting,
    }

    if pnc:
        output["pnc_validation"] = pnc.model_dump()

    return json.dumps(output, indent=2, ensure_ascii=False, default=str)


def format_output_mermaid(result: dict) -> str:
    determinatio = result.get("determinatio")
    pnc = result.get("pnc_validation")
    state = result.get("state", {})
    history = state.get("arguments_history", [])

    lines = ["```mermaid", "graph TD"]
    lines.append("  START[/Codigo Fuente/] --> R1[Ronda 1]")

    seen_agents = set()
    for round_data in history:
        r = round_data.get("round", 1)
        for agent_name_raw in round_data.get("arguments", {}):
            label = agent_name_raw
            safe = (
                label.replace(" ", "_")
                .replace("(", "")
                .replace(")", "")
                .replace(".", "")
            )
            if safe not in seen_agents:
                color = "#f0c040"
                lines.append(f'  R{r} --> {safe}["{label[:30]}"]')
                lines.append(f"  style {safe} fill:{color}")
                seen_agents.add(safe)

    if pnc and pnc.hay_contradicciones:
        for c in pnc.contradicciones:
            a = c.agente_a.replace(" ", "_").replace("(", "").replace(")", "")
            b = c.agente_b.replace(" ", "_").replace("(", "").replace(")", "")
            lines.append(f"  {a} -.->|contradice| {b}")
            lines.append(f"  linkStyle {len(lines) - 3} stroke:red")

    verdict_color = {"CONDENA": "#c00000", "ABSUELVE": "#00a000", "RESERVA": "#f0c040"}
    v = determinatio.veredicto_final.value if determinatio else "RESERVA"
    lines.append(f"  R{len(history)} --> MAG[/Magister: {v}/]")
    lines.append(f"  style MAG fill:{verdict_color.get(v, '#f0c040')},color:white")
    lines.append("```")

    return "\n".join(lines)


def format_output_sarif(result: dict, filepath: str = "") -> str:
    determinatio = result.get("determinatio")

    run = {
        "tool": {
            "driver": {
                "name": "Concilio de Salamanca MDE",
                "informationUri": "https://github.com/concilio-salamanca",
            }
        },
        "results": [],
    }

    if determinatio:
        level = (
            "error" if determinatio.veredicto_final.value == "CONDENA" else "warning"
        )
        run["results"].append(
            {
                "ruleId": f"MDE-{determinatio.veredicto_final.value}",
                "level": level,
                "message": {"text": determinatio.determinatio_codici[:500]},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": filepath or "codigo"}
                        }
                    }
                ],
            }
        )

    report = {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [run],
    }

    return json.dumps(report, indent=2, ensure_ascii=False)


def format_output_executive(
    result: dict, agent_labels: list, rounds: int, voting: dict = None
) -> str:
    determinatio = result.get("determinatio")
    pnc = result.get("pnc_validation")

    if not determinatio:
        return "Error: No se pudo generar la determinatio."

    pnc_resumen = "Sin contradicciones detectadas."
    num_contradicciones = 0
    if pnc and pnc.hay_contradicciones:
        num_contradicciones = len(pnc.contradicciones)
        pnc_resumen = (
            f"{num_contradicciones} contradiccion(es) detectada(s): "
            + "; ".join(f"{c.agente_a} vs {c.agente_b}" for c in pnc.contradicciones)
        )

    participantes_text = "\n".join(f"- {label}" for label in agent_labels)

    return format_determinatio(
        modo="ejecutivo",
        quaestio=determinatio.quaestio,
        videtur=determinatio.videtur,
        sed_contra=determinatio.sed_contra,
        respondeo=determinatio.respondeo,
        determinatio_codici=determinatio.determinatio_codici,
        veredicto_final=determinatio.veredicto_final.value,
        participantes=participantes_text,
        pnc_resumen=pnc_resumen,
        rondas=rounds,
        num_agentes=len(agent_labels),
        num_contradicciones=num_contradicciones,
    )


def format_output_text(result: dict) -> str:
    determinatio = result.get("determinatio")
    pnc = result.get("pnc_validation")

    if not determinatio:
        return "Error: No se pudo generar la determinatio."

    lines = [
        "=" * 70,
        "  CONCILIO DE SALAMANCA - DETERMINATIO MAGISTRAL",
        "=" * 70,
        "",
        "QUAESTIO:",
        f"  {determinatio.quaestio}",
        "",
        "VIDETUR (lo que parece):",
        f"  {determinatio.videtur}",
        "",
        "SED CONTRA (argumentos en contra):",
        f"  {determinatio.sed_contra}",
        "",
        "RESPONDEO (resolucion razonada):",
        f"  {determinatio.respondeo}",
        "",
        "DETERMINATIO CODICI (veredicto final):",
        f"  {determinatio.determinatio_codici}",
        "",
        f"VEREDICTO: {determinatio.veredicto_final.value}",
    ]

    if pnc and pnc.hay_contradicciones:
        lines.append("")
        lines.append("ADVERTENCIA DEL PnC:")
        for c in pnc.contradicciones:
            lines.append(
                f"  Contradiccion: {c.agente_a} vs {c.agente_b}: {c.descripcion}"
            )

    lines.append("")
    lines.append("=" * 70)
    lines.append("  *Sic determinat Magister. Causa finita est.*")
    lines.append("=" * 70)

    return "\n".join(lines)


def format_output_markdown(result: dict) -> str:
    determinatio = result.get("determinatio")
    pnc = result.get("pnc_validation")

    if not determinatio:
        return "**Error:** No se pudo generar la determinatio."

    md = [
        "# Determinatio del Concilio de Salamanca",
        "",
        f"**Veredicto:** `{determinatio.veredicto_final.value}`",
        "",
        "## Quaestio",
        determinatio.quaestio,
        "",
        "## Videtur",
        determinatio.videtur,
        "",
        "## Sed Contra",
        determinatio.sed_contra,
        "",
        "## Respondeo",
        determinatio.respondeo,
        "",
        "## Determinatio Codici",
        determinatio.determinatio_codici,
    ]

    if pnc and pnc.hay_contradicciones:
        md.append("")
        md.append("## Validacion del Principio de No Contradiccion")
        md.append(f"Se detectaron {len(pnc.contradicciones)} contradiccion(es):")
        for c in pnc.contradicciones:
            md.append(f"- **{c.agente_a}** vs **{c.agente_b}**: {c.descripcion}")

    md.append("")
    md.append("---")
    md.append("*Sic determinat Magister. Causa finita est.*")

    return "\n".join(md)
