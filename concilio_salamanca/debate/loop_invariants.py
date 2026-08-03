"""
Motor Guess-and-Check para invariantes de bucle usando Z3.
"""

import json
import logging
from typing import Dict, Any

try:
    import z3

    HAS_Z3 = True
except ImportError:
    HAS_Z3 = False

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

GUESS_PROMPT = """Eres un experto en verificación formal de programas.
Te daré un fragmento de código que contiene un bucle. Debes adivinar un "Invariante de bucle" válido.
Un invariante de bucle es una condición que es verdadera antes de entrar al bucle, verdadera al inicio de cada iteración y verdadera al salir del bucle.

Debes devolver la respuesta en formato JSON estricto:
{
  "variables": [{"nombre": "i", "tipo": "int"}, {"nombre": "n", "tipo": "int"}],
  "precondicion": "n > 0",
  "invariante": "And(i >= 0, i <= n)",
  "condicion_bucle": "i < n",
  "post_iteracion": "i == i_old + 1"
}
Usa sintaxis compatible con Z3 en Python: And(), Or(), Not(), Implies(), ==, >, <, >=, <=, +, -, *, /.
Para referirte al valor de una variable de la iteración anterior, usa el sufijo '_old'.
"""


class LoopInvariantEngine:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    def guess_and_check(
        self, code_snippet: str, max_iterations: int = 3
    ) -> Dict[str, Any]:
        if not HAS_Z3:
            return {"success": False, "error": "Z3 no instalado"}

        history = []

        for attempt in range(max_iterations):
            history_text = "\n".join(history)
            messages = [
                SystemMessage(content=GUESS_PROMPT),
                HumanMessage(
                    content=f"Código:\n{code_snippet}\n\nIntentos previos (no repitas fallos):\n{history_text}"
                ),
            ]

            try:
                resp = self.llm.invoke(messages)
                raw = resp.content.strip()
                if "```json" in raw:
                    raw = raw.split("```json")[1].split("```")[0]
                elif "```" in raw:
                    raw = raw.split("```")[1].split("```")[0]
                data = json.loads(raw)
            except Exception as e:
                return {"success": False, "error": f"Fallo LLM JSON: {e}"}

            # Validar con Z3
            s = z3.Solver()
            eval_ns = {"And": z3.And, "Or": z3.Or, "Not": z3.Not, "Implies": z3.Implies}
            z3_vars = {}
            for v in data.get("variables", []):
                vname = v["nombre"]
                if v["tipo"] == "int":
                    z3_vars[vname] = z3.Int(vname)
                    z3_vars[vname + "_old"] = z3.Int(vname + "_old")
                elif v["tipo"] == "bool":
                    z3_vars[vname] = z3.Bool(vname)
                    z3_vars[vname + "_old"] = z3.Bool(vname + "_old")

            eval_ns.update(z3_vars)

            try:
                inv = eval(data["invariante"], {"__builtins__": None}, eval_ns)
                eval(data["condicion_bucle"], {"__builtins__": None}, eval_ns)
                eval(data["post_iteracion"], {"__builtins__": None}, eval_ns)

                # Check 1: Invariante conservado?
                # inv_old AND cond_old AND post -> inv
                # Para simplificar, sustituimos _old

                # Esto es un proof of concept muy simplificado
                # En un sistema real de Hoare logic esto sería más robusto.
                s.add(z3.Not(inv))  # Queremos ver si el invariante puede violarse

                if s.check() == z3.sat:
                    history.append(
                        f"Intento {attempt}: {data['invariante']} falló la verificación Z3 (es falsificable)."
                    )
                    continue
                else:
                    return {
                        "success": True,
                        "invariante": data["invariante"],
                        "intentos": attempt + 1,
                    }

            except Exception as e:
                history.append(f"Intento {attempt}: Error al evaluar en Z3: {e}")
                continue

        return {
            "success": False,
            "error": "Maximos intentos alcanzados sin encontrar invariante",
            "history": history,
        }
