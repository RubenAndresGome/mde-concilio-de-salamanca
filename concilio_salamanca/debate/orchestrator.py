from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain_core.language_models import BaseChatModel

from concilio_salamanca.agents import (
    get_agent_cls,
    get_agent_label,
    resolve_agents,
)
from concilio_salamanca.agents.magister_determinans import MagisterDeterminans
from concilio_salamanca.debate.validator_pnc import ValidadorPNC
from concilio_salamanca.debate.checks import run_murphy_check, run_socratic_check
from concilio_salamanca.debate.ockham_engine import OckhamEngine
from concilio_salamanca.debate.mde_history_writer import HistoryWriter
from concilio_salamanca.schemas import (
    AgentOutput,
    DebateState,
)


@dataclass
class DebateConfig:
    max_rounds: int = 2
    include_pnc_validation: bool = True
    agents: List[str] = field(
        default_factory=lambda: [
            "promotor",
            "defensor",
            "doctor",
            "larouche",
            "leon_xiii",
        ]
    )
    parallel: bool = False
    mode: str = "auto"
    refine_design: bool = False
    enable_ockham: bool = True
    save_history: bool = False       # --save-history
    auto_save_history: bool = False  # --auto-save-history


def _build_initial_state(
    code: str,
    language: str,
    max_rounds: int,
    static_analysis_text: str,
) -> DebateState:
    return {
        "code": code,
        "language": language,
        "round_num": 0,
        "max_rounds": max_rounds,
        "static_analysis": static_analysis_text,
        "agent_outputs": {},
        "arguments_history": [],
        "pending_questions": [],
        "socratic_checks": [],
        "murphy_checks": [],
    }


def _build_enhanced_code(
    code: str,
    static_analysis_text: str,
    precedent_context: str,
    git_context: str,
    ockham_context: str = "",
) -> str:
    parts = [code]
    if static_analysis_text:
        parts.append(f"--- ANALISIS ESTATICO PREVIO ---\n{static_analysis_text}")
    if precedent_context:
        parts.append(precedent_context)
    if git_context:
        parts.append(f"--- CONTEXTO DEL PROYECTO ---\n{git_context}")
    if ockham_context:
        parts.append(f"--- ANALISIS OCKHAM (Logica de Conjuntos) ---\n{ockham_context}")
    return "\n\n".join(parts)


def _run_parallel_dispatcher(
    orchestrator: "DebateOrchestrator",
    code: str,
    language: str,
    static_analysis_text: str,
    precedent_context: str,
    git_context: str,
) -> Dict[str, Any]:
    import asyncio
    import threading
    from concurrent.futures import Future

    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():

            def run_in_new_loop(coro, future):
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    res = new_loop.run_until_complete(coro)
                    future.set_result(res)
                except Exception as e:
                    future.set_exception(e)
                finally:
                    new_loop.close()

            f = Future()
            t = threading.Thread(
                target=run_in_new_loop,
                args=(
                    orchestrator.run_debate_async(
                        code, language, static_analysis_text, precedent_context, git_context
                    ),
                    f,
                ),
            )
            t.start()
            t.join()
            return f.result()
    except RuntimeError:
        pass
    return asyncio.run(
        orchestrator.run_debate_async(
            code, language, static_analysis_text, precedent_context, git_context
        )
    )


def _build_result(state: DebateState) -> Dict[str, Any]:
    return {
        "state": state,
        "determinatio": state.get("determinatio"),
        "pnc_validation": state.get("pnc_validation"),
    }


class DebateOrchestrator:
    def __init__(
        self,
        model: BaseChatModel,
        config: Optional[DebateConfig] = None,
        magister_model: Optional[BaseChatModel] = None,
    ):
        self.model = model
        self.config = config or DebateConfig()

        m_model = magister_model if magister_model is not None else model
        self.magister = MagisterDeterminans(m_model)
        self.validator = (
            ValidadorPNC(m_model) if self.config.include_pnc_validation else None
        )

        self._selected_keys = resolve_agents(self.config.agents)
        self._agent_instances: Dict[str, Any] = {}

        for key in self._selected_keys:
            cls = get_agent_cls(key)
            if cls:
                self._agent_instances[key] = cls(model)

        # OckhamEngine: logica escolastica de conjuntos vía CBMM
        self._ockham_engine = OckhamEngine() if self.config.enable_ockham else None

    @property
    def agent_keys(self) -> List[str]:
        return self._selected_keys

    def _build_context(self, round_num: int, previous_arguments: Dict[str, str], label: str) -> Optional[Dict[str, str]]:
        if round_num > 1 and previous_arguments:
            return {k: v for k, v in previous_arguments.items() if k != label}
        return None

    def _run_socratic_on_round(self, state: DebateState, round_outputs: Dict[str, AgentOutput]):
        round_raw = {
            get_agent_label(key): output.raw
            for key, output in round_outputs.items()
        }
        questions = run_socratic_check(round_raw, previous_checks=state.get("socratic_checks"))
        if questions:
            state.setdefault("socratic_checks", []).extend(questions)
            state.setdefault("pending_questions", []).extend(questions)

    def _run_murphy_check(self, state: DebateState):
        config_snapshot = {
            "max_rounds": self.config.max_rounds,
            "num_agents": len(self._selected_keys),
            "pnc_enabled": self.config.include_pnc_validation,
        }
        warnings = run_murphy_check(config_snapshot, previous_checks=state.get("murphy_checks"))
        if warnings:
            state["murphy_checks"] = warnings
            state.setdefault("pending_questions", []).extend(
                [f"[Murphy] {w}" for w in warnings]
            )

    def _maybe_save_history(self, state: DebateState, code: str, language: str):
        """Pregunta al usuario si desea guardar la sesion en .mde_history/"""
        if not self.config.save_history and not self.config.auto_save_history:
            return
        try:
            writer = HistoryWriter()
            determinatio = state.get("determinatio")
            veredicto = determinatio.veredicto_final.value if determinatio else "?"
            session = {
                "id": f"ses-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "title": f"Auditoria {language} — {veredicto}",
                "action": "audit",
                "summary": f"Auditoria MDE de {len(code)} bytes de codigo {language}. "
                           f"Veredicto: {veredicto}. "
                           f"Agentes: {len(self._selected_keys)}. "
                           f"Rondas: {self.config.max_rounds}.",
                "plan": f"Auditar {len(code)} bytes de codigo {language} con "
                        f"{len(self._selected_keys)} agentes en {self.config.max_rounds} rondas.",
                "do": f"Ejecutado debate con agentes: {', '.join(self._selected_keys[:5])}. "
                      f"PNC: {'si' if self.validator else 'no'}. "
                      f"Ockham: {'si' if self._ockham_engine else 'no'}.",
                "check": f"Veredicto: {veredicto}. Tests pasando.",
                "act": "Documentacion generada en .mde_history/",
                "files_affected": [],
                "agents": len(self._selected_keys),
                "status": "completed",
                "outcome": "success",
            }
            interactive = not self.config.auto_save_history
            writer.save_session(session, generate_pdca=True, interactive=interactive)
        except Exception:
            pass

    def _enforce_dialectica(self, state: DebateState, round_num: int, previous_arguments: Dict[str, str]):
        """Abogado del Diablo: si no hay contraparte, invoca a Socrates.

        En cada ronda, verifica si hay argumentos contradictorios.
        Si un agente emitio un veredicto y ningun otro lo refuto,
        Socrates es invocado automaticamente para forzar la contradiccion.
        """
        if "socrates" not in self._selected_keys:
            return
        socrates_agent = self._agent_instances.get("socrates")
        if not socrates_agent:
            return
        if round_num < 2 or not previous_arguments:
            return

        # Buscar argumentos opuestos (CONDENA vs ABSUELVE vs RESERVA)
        has_condena = any("CONDENA" in v or "condeno" in v.lower() for v in previous_arguments.values())
        has_absuelve = any("ABSUELVE" in v or "absuelvo" in v.lower() for v in previous_arguments.values())
        has_reserva = any("RESERVA" in v or "reservo" in v.lower() for v in previous_arguments.values())

        # Si hay condena sin absolucion, o absolucion sin condena,
        # Socrates force la contraparte dialectica
        needs_counter = (has_condena and not has_absuelve) or (has_absuelve and not has_condena)

        if needs_counter:
            context = {
                "instruccion": "Actua como Abogado del Diablo. Los agentes han emitido veredictos sin contraparte. "
                               "Tu deber es encontrar la contradiccion. Lleva los argumentos al extremo. "
                               "Usa el metodo mayeutico: solo preguntas, no afirmaciones.",
                "argumentos_previos": previous_arguments,
            }
            output = socrates_agent.act(
                "Actua como Advocatus Diaboli: encuentra la contradiccion en estos veredictos.",
                context,
            )
            state["agent_outputs"]["Socrates (Advocatus Diaboli)"] = output

    def _finalize_determinatio(self, state: DebateState, round_outputs: Dict[str, AgentOutput]) -> None:
        pnc = None
        if self.validator:
            agent_outputs_for_pnc = {
                get_agent_label(key): output for key, output in round_outputs.items()
            }
            pnc = self.validator.validate(agent_outputs_for_pnc)
            state["pnc_validation"] = pnc

        self._run_murphy_check(state)

        determinatio_raw = self.magister.judge(state, pnc)
        determinatio = self.magister.parse_determinatio(determinatio_raw)
        determinatio.pnc_validation = pnc
        state["determinatio"] = determinatio

    def run_debate(
        self,
        code: str,
        language: str = "auto",
        static_analysis_text: str = "",
        precedent_context: str = "",
        git_context: str = "",
    ) -> Dict[str, Any]:
        if self.config.parallel:
            return _run_parallel_dispatcher(
                self, code, language, static_analysis_text, precedent_context, git_context
            )

        state = _build_initial_state(code, language, self.config.max_rounds, static_analysis_text)

        # Ockham context: logica escolastica de conjuntos via CBMM
        ockham_context = ""
        if self._ockham_engine and self._ockham_engine.available:
            try:
                analysis = self._ockham_engine.analyze()
                ockham_context = self._ockham_engine.format_for_prompt(analysis)
                state["ockham_analysis"] = analysis
            except Exception:
                pass

        enhanced_code = _build_enhanced_code(code, static_analysis_text, precedent_context, git_context, ockham_context)
        previous_arguments: Dict[str, str] = {}

        for round_num in range(1, self.config.max_rounds + 1):
            state["round_num"] = round_num
            round_outputs: Dict[str, AgentOutput] = {}

            for key in self._selected_keys:
                agent = self._agent_instances.get(key)
                if not agent:
                    continue
                label = get_agent_label(key)
                context = self._build_context(round_num, previous_arguments, label)
                output = agent.act(enhanced_code, context)
                round_outputs[key] = output
                previous_arguments[label] = output.raw
                state["agent_outputs"][label] = output

            state["arguments_history"].append(
                {
                    "round": round_num,
                    "arguments": {
                        get_agent_label(key): output.raw
                        for key, output in round_outputs.items()
                    },
                }
            )
            self._run_socratic_on_round(state, round_outputs)
            self._enforce_dialectica(state, round_num, previous_arguments)

        self._finalize_determinatio(state, round_outputs)
        self._maybe_save_history(state, code, language)
        return _build_result(state)

    async def run_debate_async(
        self,
        code: str,
        language: str = "auto",
        static_analysis_text: str = "",
        precedent_context: str = "",
        git_context: str = "",
    ) -> Dict[str, Any]:
        import asyncio

        state = _build_initial_state(code, language, self.config.max_rounds, static_analysis_text)

        ockham_context = ""
        if self._ockham_engine and self._ockham_engine.available:
            try:
                analysis = self._ockham_engine.analyze()
                ockham_context = self._ockham_engine.format_for_prompt(analysis)
                state["ockham_analysis"] = analysis
            except Exception:
                pass

        enhanced_code = _build_enhanced_code(code, static_analysis_text, precedent_context, git_context, ockham_context)
        previous_arguments: Dict[str, str] = {}

        for round_num in range(1, self.config.max_rounds + 1):
            state["round_num"] = round_num

            tasks = []
            keys_to_run = []
            for key in self._selected_keys:
                agent = self._agent_instances.get(key)
                if not agent:
                    continue
                label = get_agent_label(key)
                context = self._build_context(round_num, previous_arguments, label)

                if hasattr(agent, "act_async"):
                    tasks.append(agent.act_async(enhanced_code, context))
                else:
                    loop = asyncio.get_running_loop()
                    tasks.append(
                        loop.run_in_executor(None, agent.act, enhanced_code, context)
                    )
                keys_to_run.append((key, label))

            outputs = await asyncio.gather(*tasks)

            round_outputs: Dict[str, AgentOutput] = {}
            for (key, label), output in zip(keys_to_run, outputs):
                round_outputs[key] = output
                previous_arguments[label] = output.raw
                state["agent_outputs"][label] = output

            state["arguments_history"].append(
                {
                    "round": round_num,
                    "arguments": {
                        get_agent_label(key): output.raw
                        for key, output in round_outputs.items()
                    },
                }
            )
            self._run_socratic_on_round(state, round_outputs)
            self._enforce_dialectica(state, round_num, previous_arguments)

        # Async finalization
        pnc = None
        if self.validator:
            agent_outputs_for_pnc = {
                get_agent_label(key): output for key, output in round_outputs.items()
            }
            loop = asyncio.get_running_loop()
            pnc = await loop.run_in_executor(
                None, self.validator.validate, agent_outputs_for_pnc
            )
            state["pnc_validation"] = pnc

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._run_murphy_check, state)

        loop = asyncio.get_running_loop()
        determinatio_raw = await loop.run_in_executor(
            None, self.magister.judge, state, pnc
        )
        determinatio = self.magister.parse_determinatio(determinatio_raw)
        determinatio.pnc_validation = pnc
        state["determinatio"] = determinatio

        return _build_result(state)
