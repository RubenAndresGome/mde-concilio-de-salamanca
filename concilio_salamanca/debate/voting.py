from __future__ import annotations


def build_voting_table(result: dict) -> dict:
    state = result.get("state", {})
    history = state.get("arguments_history", [])

    votes = {"CONDENA": 0, "ABSUELVE": 0, "RESERVA": 0}
    agent_votes = []

    for round_data in history:
        for name, raw in round_data.get("arguments", {}).items():
            raw_upper = raw.upper() if hasattr(raw, "upper") else ""
            for v in ["CONDENA", "ABSUELVE", "RESERVA"]:
                if v in raw_upper:
                    votes[v] += 1
                    agent_votes.append({"agente": name, "veredicto": v})
                    break
            else:
                votes["RESERVA"] += 1
                agent_votes.append({"agente": name, "veredicto": "RESERVA"})

    total = sum(votes.values()) or 1
    majority = max(votes, key=votes.get)
    consensus = votes[majority] / total >= 0.67

    return {
        "votos": votes,
        "agentes": agent_votes,
        "consenso": consensus,
        "mayoria": majority,
        "total": total,
    }
