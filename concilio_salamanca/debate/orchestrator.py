"""Orquestador económico del colegio electoral del Concilio."""

from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from langchain_core.language_models import BaseChatModel

from concilio_salamanca.agents import get_agent_cls, get_agent_label, resolve_agents
from concilio_salamanca.agents.magister_determinans import MagisterDeterminans
from concilio_salamanca.debate.audit_profiles import get_audit_profile
from concilio_salamanca.debate.context_compression import compact_section, compress_context, estimate_tokens
from concilio_salamanca.debate.context_sieve import sift_context
from concilio_salamanca.debate.mde_history_writer import HistoryWriter
from concilio_salamanca.debate.ockham_engine import OckhamEngine
from concilio_salamanca.debate.syllogism_boolean import validate_boolean_pnc
from concilio_salamanca.debate.token_accountant import TokenAccountant
from concilio_salamanca.debate.validator_pnc import ValidadorPNC
from concilio_salamanca.schemas import AgentOutput, DebateState, Determinatio, PnCValidation, Veredicto


@dataclass
class DebateConfig:
    max_rounds: int = 2
    include_pnc_validation: bool = True
    agents: List[str] = field(default_factory=lambda: ["promotor", "defensor", "doctor", "larouche", "leon_xiii"])
    parallel: bool = False
    mode: str = "auto"
    refine_design: bool = False
    enable_ockham: bool = True
    save_history: bool = False
    auto_save_history: bool = False
    context_budget_chars: int = 2400
    audit_level: Optional[int] = None
    token_budget: int = 0
    model_name: str = ""
    escalation_candidates: List[str] = field(default_factory=lambda: ["gpt-5.6-terra", "gpt-5.6-sol"])
    reserve_reason: str = ""


def _build_initial_state(code: str, language: str, max_rounds: int, static_analysis_text: str) -> DebateState:
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
        "token_metrics": {"context_tokens_before_est": 0, "context_tokens_after_est": 0, "context_tokens_saved_est": 0},
    }


def _build_result(state: DebateState) -> Dict[str, Any]:
    return {
        "state": state,
        "determinatio": state.get("determinatio"),
        "pnc_validation": state.get("pnc_validation"),
        "voting": state.get("voting_summary", {}),
        "usage": state.get("usage", {}),
        "budget": state.get("budget", {}),
        "cache_hit_ratio": state.get("cache_hit_ratio", 0.0),
        "calls_by_model": state.get("calls_by_model", {}),
        "stop_reason": state.get("stop_reason", ""),
        "escalation": state.get("escalation"),
    }


class DebateOrchestrator:
    def __init__(
        self,
        model: Optional[BaseChatModel],
        config: Optional[DebateConfig] = None,
        magister_model: Optional[BaseChatModel] = None,
    ):
        self.model = model
        self.config = config or DebateConfig()
        self.profile = get_audit_profile(self.config.audit_level) if self.config.audit_level is not None else None
        if self.profile:
            self.config.max_rounds = self.profile.max_rounds
            self.config.agents = resolve_agents(self.config.agents)[: self.profile.max_agents]
        self._selected_keys = resolve_agents(self.config.agents)
        self._agent_instances: Dict[str, Any] = {}
        if model is not None:
            for key in self._selected_keys:
                cls = get_agent_cls(key)
                if cls:
                    self._agent_instances[key] = cls(model)
        final_model = magister_model if magister_model is not None else model
        self.magister = MagisterDeterminans(final_model) if final_model is not None else None
        # El validador semántico heredado sólo se conserva fuera de los perfiles económicos.
        self.validator = (
            ValidadorPNC(final_model)
            if final_model is not None and self.config.include_pnc_validation and self.profile is None
            else None
        )
        self._ockham_engine = OckhamEngine() if self.config.enable_ockham else None
        self.accountant = TokenAccountant(self.config.token_budget)

    @property
    def agent_keys(self) -> List[str]:
        return self._selected_keys

    def _agent_token_limit(self) -> int:
        return self.profile.agent_max_tokens if self.profile else 0

    def _question_limit(self) -> int:
        return self.profile.question_limit if self.profile else 3

    def _build_context(self, round_num: int, previous: Dict[str, str], label: str) -> Optional[Dict[str, str]]:
        if round_num <= 1 or not previous:
            return None
        return compress_context(previous, exclude=label, budget_chars=self.config.context_budget_chars)

    def _record_context_savings(self, state: DebateState, previous: Dict[str, str], context: Optional[Dict[str, str]], label: str) -> None:
        if not context:
            return
        before = estimate_tokens("\n".join(raw for agent, raw in previous.items() if agent != label))
        after = estimate_tokens("\n".join(context.values()))
        metrics = state.setdefault("token_metrics", {})
        metrics["context_tokens_before_est"] = metrics.get("context_tokens_before_est", 0) + before
        metrics["context_tokens_after_est"] = metrics.get("context_tokens_after_est", 0) + after
        metrics["context_tokens_saved_est"] = metrics.get("context_tokens_saved_est", 0) + max(0, before - after)

    def _collect_questions(self, state: DebateState, outputs: Dict[str, AgentOutput]) -> None:
        existing = state.setdefault("pending_questions", [])
        categories = {question.split(":", 1)[0].strip().lower() for question in existing}
        for output in outputs.values():
            if not output.structured:
                continue
            for question in output.structured.preguntas_casuisticas:
                category = question.split(":", 1)[0].strip().lower()
                if category in categories:
                    continue
                existing.append(question)
                categories.add(category)
                if len(existing) >= self._question_limit():
                    return

    @staticmethod
    def _deterministic_determination(state: DebateState, pnc: Optional[PnCValidation] = None) -> Determinatio:
        voting = state.get("voting_summary", {})
        verdict_value = voting.get("mayoria", "RESERVA")
        try:
            verdict = Veredicto(verdict_value)
        except ValueError:
            verdict = Veredicto.RESERVA
        agents = voting.get("agentes", [])
        for_votes = [v["agente"] for v in agents if v.get("veredicto") == verdict.value]
        against = [v["agente"] for v in agents if v.get("veredicto") != verdict.value]
        return Determinatio(
            quaestio="¿El código satisface el Dogma y la evidencia disponible?",
            videtur="Votos favorables: " + (", ".join(for_votes) or "ninguno"),
            sed_contra="Votos discrepantes: " + (", ".join(against) or "ninguno"),
            respondeo=(
                f"Síntesis electoral determinista: {verdict.value}; cuota "
                f"{float(voting.get('cuota_mayoria', 0)):.0%}."
            ),
            determinatio_codici="Revisar las evidencias del ledger compacto; no se generó código por LLM.",
            veredicto_final=verdict,
            pnc_validation=pnc,
        )

    @staticmethod
    def _static_determination(code: str, static_analysis: str, reserve_reason: str = "") -> Determinatio:
        text = f"{code}\n{static_analysis}".lower()
        critical = [term for term in ("eval(", "exec(", "pickle.loads", "shell=true", "password =", "secret =") if term in text]
        verdict = Veredicto.RESERVA if reserve_reason else (Veredicto.CONDENA if critical else Veredicto.ABSUELVE)
        evidence = ", ".join(critical) if critical else "sin patrón crítico determinista"
        return Determinatio(
            quaestio="Auditoría estática sin LLM",
            videtur=compact_section(static_analysis or "Sin diagnóstico externo.", 800),
            sed_contra=evidence,
            respondeo=(reserve_reason or f"Resultado reproducible de reglas locales: {verdict.value}."),
            determinatio_codici="No se modificó el código.",
            veredicto_final=verdict,
        )

    @staticmethod
    def _critical_static_findings(code: str, static_analysis: str = "") -> list[str]:
        text = f"{code}\n{static_analysis}".lower()
        return [
            term for term in ("eval(", "exec(", "pickle.loads", "shell=true", "password =", "secret =")
            if term in text
        ]

    def _apply_static_veto(self, state: DebateState) -> None:
        findings = self._critical_static_findings(state.get("code", ""), state.get("static_analysis", ""))
        state["critical_static_findings"] = findings
        determination = state.get("determinatio")
        if findings and determination and determination.veredicto_final != Veredicto.CONDENA:
            determination.veredicto_final = Veredicto.CONDENA
            determination.respondeo += (
                " Veto estático: un hallazgo crítico determinista no puede ser absuelto por consenso LLM."
            )
            determination.determinatio_codici = "Corregir evidencia crítica: " + ", ".join(findings)

    def _escalation(self, state: DebateState, pnc: Optional[PnCValidation]) -> Optional[dict]:
        voting = state.get("voting_summary", {})
        reasons = []
        if pnc and pnc.hay_contradicciones:
            reasons.append("contradiccion_pnc")
        if voting and float(voting.get("cuota_mayoria", 0)) < 0.67:
            reasons.append("mayoria_inferior_67")
        parse_errors = [name for name, output in state.get("agent_outputs", {}).items() if output.parse_error]
        if len(parse_errors) >= 2:
            reasons.append("parseo_fallido_repetido")
        reserves = [v.get("agente") for v in voting.get("agentes", []) if v.get("veredicto") == "RESERVA"]
        if reserves:
            reasons.append("reserva_especialista")
        if not reasons:
            return None
        specialists = list(dict.fromkeys((parse_errors + reserves)))[:2]
        seed = "|".join(reasons + specialists + [str(state.get("round_num", 0))])
        from concilio_salamanca.debate.model_pricing import ModelRanker

        specialist_calls = max(1, len(specialists))
        input_estimate = estimate_tokens(state.get("code", "")) * (specialist_calls + 1)
        output_estimate = (self.profile.agent_max_tokens * specialist_calls + self.profile.magister_max_tokens) if self.profile else 1792
        estimates = {}
        pricing_status = "current"
        for candidate in self.config.escalation_candidates:
            try:
                estimates[candidate] = round(ModelRanker.estimate_cost(
                    f"openai/{candidate}", input_estimate, output_estimate
                ), 6)
            except RuntimeError:
                estimates[candidate] = None
                pricing_status = "stale_blocked"
        return {
            "requires_user_decision": True,
            "decision_id": hashlib.sha256(seed.encode()).hexdigest()[:16],
            "reasons": reasons,
            "agents_to_repeat": specialists,
            "candidates": list(self.config.escalation_candidates),
            "max_tokens": (self.profile.magister_max_tokens if self.profile else 768),
            "estimated_cost_usd": estimates,
            "pricing_status": pricing_status,
        }

    def _sync_accounting(self, state: DebateState) -> None:
        snapshot = self.accountant.snapshot()
        state.update({key: snapshot[key] for key in ("usage", "budget", "cache_hit_ratio", "calls_by_model")})
        state["usage"]["cost_usd"] = snapshot["cost_usd"]
        state["usage"]["calls"] = snapshot["calls"]

    def _maybe_save_history(self, state: DebateState, code: str, language: str) -> None:
        if not self.config.save_history and not self.config.auto_save_history:
            return
        try:
            verdict = state["determinatio"].veredicto_final.value
            HistoryWriter().save_session({
                "id": f"ses-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "title": f"Auditoria {language} — {verdict}",
                "action": "audit",
                "summary": f"{len(code)} bytes; {len(self._selected_keys)} agentes; {state.get('round_num', 0)} rondas.",
                "plan": "Auditoría con economía cognitiva.", "do": "Colegio electoral contextual.",
                "check": f"Veredicto: {verdict}.", "act": "Ledger registrado.",
                "files_affected": [], "agents": len(self._selected_keys), "status": "completed", "outcome": "success",
            }, generate_pdca=True, interactive=not self.config.auto_save_history)
        except Exception:
            pass

    def run_debate(
        self,
        code: str,
        language: str = "auto",
        static_analysis_text: str = "",
        precedent_context: str = "",
        git_context: str = "",
    ) -> Dict[str, Any]:
        from concilio_salamanca.debate.voting import build_voting_table

        max_rounds = self.config.max_rounds
        state = _build_initial_state(code, language, max_rounds, static_analysis_text)
        if self.profile and self.profile.level == 0:
            state["determinatio"] = self._static_determination(code, static_analysis_text, self.config.reserve_reason)
            state["voting_summary"] = {}
            state["stop_reason"] = "provider_unavailable_static_reserve" if self.config.reserve_reason else "static_complete"
            self._apply_static_veto(state)
            self._sync_accounting(state)
            return _build_result(state)

        sifted = sift_context(code, static_analysis_text)
        parts = [sifted.code]
        if sifted.diagnostics:
            parts.append("DIAGNOSTICOS:\n" + sifted.diagnostics)
        if precedent_context:
            parts.append(compact_section(precedent_context, 1800))
        if git_context:
            parts.append(compact_section(git_context, 1800))
        enhanced_code = "\n\n".join(parts)
        estimated_agent_input = estimate_tokens(enhanced_code) + 350
        state["token_metrics"]["context_sieve_chars_saved"] = sifted.omitted_chars
        previous: Dict[str, str] = {}
        all_latest: Dict[str, AgentOutput] = {}
        stop_reason = "max_rounds"

        for round_num in range(1, max_rounds + 1):
            state["round_num"] = round_num
            keys = self._selected_keys
            if self.profile and self.profile.level == 2 and round_num == 2:
                keys = keys[:2]
            round_outputs: Dict[str, AgentOutput] = {}
            snapshot = dict(previous)
            for key in keys:
                if self.profile and len(self.accountant.calls) >= self.profile.max_calls - int(self.profile.use_magister):
                    stop_reason = "call_budget_exhausted"
                    break
                limit = self._agent_token_limit()
                if not self.accountant.can_call(limit, estimated_agent_input):
                    stop_reason = "token_budget_exhausted"
                    break
                agent = self._agent_instances.get(key)
                if agent is None:
                    continue
                label = get_agent_label(key)
                context = self._build_context(round_num, snapshot, label)
                self._record_context_savings(state, snapshot, context, label)
                output = agent.act(enhanced_code, context, max_tokens=limit)
                round_outputs[key] = output
                all_latest[label] = output
                previous[label] = output.compact or output.raw
                state["agent_outputs"][label] = output
                if not output.cached:
                    self.accountant.record(
                        usage=output.usage, model=output.model or self.config.model_name,
                        agent=label, latency_ms=output.latency_ms,
                    )
            state["arguments_history"].append({
                "round": round_num,
                "arguments": {get_agent_label(key): output.compact or output.raw for key, output in round_outputs.items()},
            })
            self._collect_questions(state, round_outputs)
            state["voting_summary"] = build_voting_table(
                {"state": state}, consensus_threshold=(self.profile.consensus_threshold if self.profile else 0.67)
            )
            pnc = validate_boolean_pnc(all_latest) if self.config.include_pnc_validation else None
            state["pnc_validation"] = pnc
            if stop_reason in {"call_budget_exhausted", "token_budget_exhausted"}:
                break
            if self.profile and state["voting_summary"].get("consenso") and not (pnc and pnc.hay_contradicciones):
                stop_reason = "consensus_reached"
                break

        pnc = state.get("pnc_validation")
        if self.validator:
            pnc = self.validator.validate(all_latest)
            state["pnc_validation"] = pnc

        if self.profile and not self.profile.use_magister:
            state["determinatio"] = self._deterministic_determination(state, pnc)
        elif self.magister is not None:
            limit = self.profile.magister_max_tokens if self.profile else 0
            magister_input_estimate = estimate_tokens("\n".join(previous.values())) + 300
            if self.accountant.can_call(limit, magister_input_estimate):
                raw = self.magister.judge(state, pnc, max_tokens=limit)
                state["determinatio"] = self.magister.parse_determinatio(raw)
                state["determinatio"].pnc_validation = pnc
                self.accountant.record(
                    usage=self.magister.last_usage, model=self.magister.last_model or self.config.model_name,
                    agent="Magister Determinans", latency_ms=self.magister.last_latency_ms,
                )
            else:
                stop_reason = "token_budget_exhausted"
                state["determinatio"] = self._deterministic_determination(state, pnc)
        else:
            state["determinatio"] = self._deterministic_determination(state, pnc)

        state["stop_reason"] = stop_reason
        state["escalation"] = self._escalation(state, pnc)
        self._apply_static_veto(state)
        self._sync_accounting(state)
        self._maybe_save_history(state, code, language)
        return _build_result(state)

    def resume_with_frontier(
        self,
        result: Dict[str, Any],
        frontier_model: BaseChatModel,
        *,
        decision_id: str,
        candidate: str,
    ) -> Dict[str, Any]:
        """Reanuda sólo Magister y hasta dos especialistas tras aprobación explícita."""
        from concilio_salamanca.debate.voting import build_voting_table

        state = result["state"]
        escalation = state.get("escalation") or {}
        if decision_id != escalation.get("decision_id") or candidate not in escalation.get("candidates", []):
            raise ValueError("La decisión frontera no coincide con el escalamiento pendiente")
        labels = set(escalation.get("agents_to_repeat") or [])
        keys = [key for key in self._selected_keys if get_agent_label(key) in labels][:2]
        if not keys:
            keys = self._selected_keys[:2]
        compact_context = {
            name: output.compact or output.raw
            for name, output in state.get("agent_outputs", {}).items()
        }
        rerun = {}
        limit = self.profile.agent_max_tokens if self.profile else 512
        for key in keys:
            if not self.accountant.can_call(limit, estimate_tokens(state.get("code", "")) + 350):
                state["stop_reason"] = "token_budget_exhausted_before_frontier"
                break
            cls = get_agent_cls(key)
            if cls is None:
                continue
            label = get_agent_label(key)
            output = cls(frontier_model).act(
                state.get("code", ""),
                compress_context(compact_context, exclude=label, budget_chars=self.config.context_budget_chars),
                max_tokens=limit,
            )
            rerun[key] = output
            state["agent_outputs"][label] = output
            self.accountant.record(
                usage=output.usage, model=candidate, agent=label, latency_ms=output.latency_ms
            )
        if rerun:
            state["round_num"] = int(state.get("round_num", 0)) + 1
            state["arguments_history"].append({
                "round": "frontier",
                "arguments": {get_agent_label(key): output.compact or output.raw for key, output in rerun.items()},
            })
        state["voting_summary"] = build_voting_table({"state": state})
        pnc = validate_boolean_pnc(state.get("agent_outputs", {}))
        state["pnc_validation"] = pnc
        magister = MagisterDeterminans(frontier_model)
        magister_limit = self.profile.magister_max_tokens if self.profile else 768
        frontier_ledger_estimate = estimate_tokens("\n".join(compact_context.values())) + 300
        if not self.accountant.can_call(magister_limit, frontier_ledger_estimate):
            state["stop_reason"] = "token_budget_exhausted_before_frontier_magister"
            self._sync_accounting(state)
            return _build_result(state)
        raw = magister.judge(state, pnc, max_tokens=magister_limit)
        state["determinatio"] = magister.parse_determinatio(raw)
        state["determinatio"].pnc_validation = pnc
        self.accountant.record(
            usage=magister.last_usage, model=candidate,
            agent="Magister Determinans", latency_ms=magister.last_latency_ms,
        )
        state["stop_reason"] = "frontier_approved_completed"
        state["escalation"] = {
            **escalation, "requires_user_decision": False, "approved": True,
            "selected_candidate": candidate, "executed_calls": len(rerun) + 1,
        }
        self._apply_static_veto(state)
        self._sync_accounting(state)
        return _build_result(state)

    async def run_debate_async(self, *args, **kwargs) -> Dict[str, Any]:
        return await asyncio.to_thread(self.run_debate, *args, **kwargs)
