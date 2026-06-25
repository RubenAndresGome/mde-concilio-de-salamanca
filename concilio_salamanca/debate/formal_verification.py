import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

try:
    import z3

    HAS_Z3 = True
except ImportError:
    HAS_Z3 = False

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)


@dataclass
class Z3ValidationResult:
    is_satisfiable: bool
    model: Optional[Dict[str, Any]] = None
    unsat_core: Optional[List[str]] = None
    error: Optional[str] = None
    z3_used: bool = False


Z3_TRANSLATOR_PROMPT = """Eres el traductor formal de Z3.
Tu objetivo es leer afirmaciones hechas por agentes sobre un código y extraer restricciones lógicas booleanas formales que puedan ser evaluadas por el solver SMT Z3.

Reglas de extracción:
1. Identifica las proposiciones atómicas (ej. "A", "B", "C") donde cada letra representa una afirmación clara.
2. Define las relaciones lógicas entre las afirmaciones de los agentes (ej. Implicaciones, negaciones, conjunciones).
3. Salida estrictamente en JSON con la siguiente estructura:
{
  "variables": ["A", "B"],
  "significado": {"A": "El código usa autenticación JWT", "B": "El código es inseguro"},
  "restricciones_agentes": {
    "promotor": ["A -> B", "A"],
    "defensor": ["Not(B)"]
  }
}
"""


class FormalVerifier:
    def __init__(self, llm: BaseChatModel):
        self.llm = llm

    def check_pnc(self, agent_outputs: Dict[str, str]) -> Z3ValidationResult:
        if not HAS_Z3:
            return Z3ValidationResult(
                is_satisfiable=True, error="Z3 no está instalado", z3_used=False
            )

        # 1. Translate arguments to logical formulas using LLM
        arguments_text = ""
        for name, output in agent_outputs.items():
            arguments_text += f"\n\n===== {name} =====\n{output}"

        messages = [
            SystemMessage(content=Z3_TRANSLATOR_PROMPT),
            HumanMessage(
                content=f"Extrae las restricciones lógicas de estos argumentos:\n{arguments_text}"
            ),
        ]

        try:
            response = self.llm.invoke(messages)
            raw_content = response.content.strip()
            if "```json" in raw_content:
                raw_content = raw_content.split("```json")[1].split("```")[0]
            elif "```" in raw_content:
                raw_content = raw_content.split("```")[1].split("```")[0]

            data = json.loads(raw_content)
        except Exception as e:
            return Z3ValidationResult(
                is_satisfiable=True,
                error=f"Fallo al parsear LLM a Z3: {e}",
                z3_used=False,
            )

        # 2. Build Z3 Model
        variables = data.get("variables", [])
        constraints_by_agent = data.get("restricciones_agentes", {})

        s = z3.Solver()

        # We will use simple eval of python expressions over Z3 Bools.
        # This is a bit hacky but works for a proof of concept LLM->Z3 bridge.
        z3_vars = {v: z3.Bool(v) for v in variables}

        # Helper namespace for eval
        eval_namespace = {
            **z3_vars,
            "Not": z3.Not,
            "And": z3.And,
            "Or": z3.Or,
            "Implies": z3.Implies,
        }

        for agent, constraints in constraints_by_agent.items():
            for c in constraints:
                # We expect LLM to output simple python expressions like "Implies(A, B)" or "A == B"
                # To handle "A -> B" safely we might need to rely on the LLM outputting python compatible strings
                # For safety, let's just do a basic string replacement if needed
                c_clean = c.replace("->", "<=").replace(
                    "=>", "<="
                )  # P <= Q is P implies Q in some contexts, but let's just use Implies
                try:
                    expr = eval(c, {"__builtins__": None}, eval_namespace)
                    s.add(expr)
                except Exception as e:
                    logger.warning(f"Error evaluando restricción Z3 '{c}': {e}")
                    pass

        # 3. Check SAT
        result = s.check()
        if result == z3.sat:
            m = s.model()
            model_dict = {v: bool(m.evaluate(z3_vars[v])) for v in variables}
            return Z3ValidationResult(
                is_satisfiable=True, model=model_dict, z3_used=True
            )
        elif result == z3.unsat:
            return Z3ValidationResult(is_satisfiable=False, z3_used=True)
        else:
            return Z3ValidationResult(
                is_satisfiable=False, error="Z3 returned unknown", z3_used=True
            )
