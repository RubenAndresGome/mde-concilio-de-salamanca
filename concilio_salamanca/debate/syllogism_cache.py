"""
Compresor de Silogismos trinivel: reduce silogismos a tres paradigmas formales
para optimizar memoria de pensamiento de los agentes del Concilio.

Nivel 1 - Escolastico (Mnemotecnico): Letras A,E,I,O + consonantes (s,p,m,d)
  Fuente: Aristoteles, Primeros Analiticos / Pedro Hispano, Summulae Logicales
  Compresion maxima: "AAA-1" = Barbara, "EAE-1" = Celarent

Nivel 2 - Teoria de Conjuntos (Algebraico): Variables S,P,M + operadores
  Fuente: Boole, Laws of Thought / Venn, Symbolic Logic
  Compresion: "S subset P", "S intersect P = EMPTY"

Nivel 3 - Logica de Predicados (Formal): Cuantificadores, variables, predicados
  Fuente: Frege, Begriffsschrift / Russell-Whitehead, Principia Mathematica
  Compresion: "forall x. S(x) -> P(x)", "exists x. S(x) and P(x)"
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class PropositionType(Enum):
    A = "A"
    E = "E"
    I = "I"
    O = "O"


class SetRelation(Enum):
    SUBSET = "subset"
    INTERSECT_EMPTY = "intersect_empty"
    INTERSECT_NONEMPTY = "intersect_nonempty"
    NOT_SUBSET = "not_subset"


@dataclass
class SyllogismPattern:
    major_type: PropositionType
    minor_type: PropositionType
    conclusion_type: PropositionType
    figure: int
    subject: str
    predicate: str
    middle: str

    def to_set_relation(self) -> Tuple[SetRelation, str]:
        rel = None
        if self.conclusion_type == PropositionType.A:
            rel = SetRelation.SUBSET
            result = f"{self.subject} SUBSET {self.predicate}"
        elif self.conclusion_type == PropositionType.E:
            rel = SetRelation.INTERSECT_EMPTY
            result = f"{self.subject} INTERSECT {self.predicate} = EMPTY"
        elif self.conclusion_type == PropositionType.I:
            rel = SetRelation.INTERSECT_NONEMPTY
            result = f"{self.subject} INTERSECT {self.predicate} != EMPTY"
        elif self.conclusion_type == PropositionType.O:
            rel = SetRelation.NOT_SUBSET
            result = f"{self.subject} NOT SUBSET {self.predicate}"
        else:
            result = "UNKNOWN"
        return rel, result

    def fingerprint(self) -> str:
        raw = f"{self.major_type.value}|{self.minor_type.value}|{self.conclusion_type.value}|{self.figure}|{self.subject}|{self.predicate}|{self.middle}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def normalized_key(self) -> str:
        raw = f"{self.major_type.value}{self.minor_type.value}{self.conclusion_type.value}-{self.figure}"
        terms = sorted(
            [
                self.subject.lower().strip(),
                self.predicate.lower().strip(),
                self.middle.lower().strip(),
            ]
        )
        terms_str = "|".join(terms)
        return f"{raw}|{hashlib.md5(terms_str.encode()).hexdigest()[:10]}"


@dataclass
class CacheEntry:
    fingerprint: str
    pattern: SyllogismPattern
    set_relation: str
    conclusion_text: str
    agent: str
    timestamp: float
    hit_count: int = 1


@dataclass
class ScholasticReduction:
    mode_name: str
    mnemotechnic: str
    figure: int
    reduction_rules: List[str]
    premise_major_scheme: str
    premise_minor_scheme: str
    conclusion_scheme: str
    vocal_pattern: str
    source: str = "Aristoteles, Primeros Analiticos / Pedro Hispano, Summulae Logicales"


@dataclass
class SetTheoryReduction:
    mode_name: str
    major_equation: str
    minor_equation: str
    conclusion_equation: str
    transitive_chain: str
    boolean_form: str
    venn_region: str
    source: str = "George Boole, The Laws of Thought (1854)"


@dataclass
class PredicateLogicReduction:
    mode_name: str
    major_formula: str
    minor_formula: str
    conclusion_formula: str
    derivation_steps: List[str]
    quantifier_structure: str
    source: str = "Gottlob Frege, Begriffsschrift (1879) / Russell-Whitehead, Principia Mathematica"


@dataclass
class UnifiedSyllogism:
    key: str
    mode_name: str
    vocal_pattern: str
    figure: int
    scholastic: ScholasticReduction
    set_theory: SetTheoryReduction
    predicate_logic: PredicateLogicReduction
    terms: Dict[str, str]


class SyllogismReducer:
    MODE_MAP = {
        ("A", "A", "A", 1): "Barbara",
        ("E", "A", "E", 1): "Celarent",
        ("A", "I", "I", 1): "Darii",
        ("E", "I", "O", 1): "Ferio",
        ("A", "E", "E", 2): "Camestres",
        ("A", "O", "O", 2): "Baroco",
        ("E", "A", "O", 2): "Cesare",
        ("E", "I", "O", 2): "Festino",
        ("A", "A", "I", 3): "Darapti",
        ("E", "A", "O", 3): "Felapton",
        ("I", "A", "I", 3): "Disamis",
        ("A", "I", "I", 3): "Datisi",
        ("O", "A", "O", 3): "Bocardo",
        ("E", "I", "O", 3): "Ferison",
        ("A", "A", "I", 4): "Bamalip",
        ("A", "E", "E", 4): "Camenes",
        ("I", "A", "I", 4): "Dimatis",
        ("E", "A", "O", 4): "Fesapo",
        ("E", "I", "O", 4): "Fresison",
    }

    REDUCTION_RULES = {
        1: {},
        2: {
            "Cesare": ["s (EAE->EAE-1 Celarent)"],
            "Camestres": ["s (AEE->EAE-1)", "m (swap premises)"],
            "Festino": ["s (EIO->EIO-1 Ferio)"],
            "Baroco": ["d (AOO, reductio ad absurdum)"],
        },
        3: {
            "Darapti": ["p (AAI, per accidens from Barbara)"],
            "Felapton": ["p (EAO, per accidens from Celarent)"],
            "Disamis": ["s,m,s (IAI->AII-1 Darii)"],
            "Datisi": ["s (AII->AII-1 Darii)"],
            "Bocardo": ["d (OAO, reductio ad absurdum)"],
            "Ferison": ["s (EIO->EIO-1 Ferio)"],
        },
        4: {
            "Bamalip": ["p,m,s (AAI, per accidens from Barbara)"],
            "Camenes": ["s,m,s (AEE->EAE-1 Celarent)"],
            "Dimatis": ["s,m,s (IAI->AII-1 Darii)"],
            "Fesapo": ["s,p (EAO, per accidens from Celarent)"],
            "Fresison": ["s (EIO->EIO-1 Ferio)"],
        },
    }

    CONSONANT_MEANING = {
        "s": "conversio simplex: intercambiar S y P (valido solo en E e I)",
        "p": "conversio per accidens: de universal a particular (A->I, E->O)",
        "m": "mutatio praemissarum: intercambiar orden de las premisas",
        "d": "deductio ad impossibile: reduccion al absurdo (Baroco, Bocardo)",
        "c": "contradictio: usar la contradiccion de la conclusion como premisa",
    }

    SET_THEORY_TEMPLATES = {
        ("A", "A", "A", 1): {  # Barbara
            "major_eq": "M INTERSECT P_complement = EMPTY",
            "minor_eq": "S INTERSECT M_complement = EMPTY",
            "conc_eq": "S INTERSECT P_complement = EMPTY (S SUBSET P)",
            "chain": "S SUBSET M SUBSET P => S SUBSET P",
            "boolean": "s(1-m) = 0, m(1-p) = 0 => s(1-p) = 0",
            "venn": "Region S outside P = shaded (empty)",
        },
        ("E", "A", "E", 1): {  # Celarent
            "major_eq": "M INTERSECT P = EMPTY",
            "minor_eq": "S SUBSET M",
            "conc_eq": "S INTERSECT P = EMPTY",
            "chain": "S SUBSET M, M INTERSECT P = EMPTY => S INTERSECT P = EMPTY",
            "boolean": "mp = 0, s(1-m) = 0 => sp = 0",
            "venn": "Region S intersect P = shaded (empty)",
        },
        ("A", "I", "I", 1): {  # Darii
            "major_eq": "M SUBSET P",
            "minor_eq": "S INTERSECT M != EMPTY",
            "conc_eq": "S INTERSECT P != EMPTY",
            "chain": "S INTERSECT M != EMPTY, M SUBSET P => S INTERSECT P != EMPTY",
            "boolean": "m(1-p) = 0, sm != 0 => sp != 0",
            "venn": "Region S intersect P = exists (non-empty)",
        },
        ("E", "I", "O", 1): {  # Ferio
            "major_eq": "M INTERSECT P = EMPTY",
            "minor_eq": "S INTERSECT M != EMPTY",
            "conc_eq": "S INTERSECT P_complement != EMPTY (Some S not P)",
            "chain": "S INTERSECT M != EMPTY, M INTERSECT P = EMPTY => S MINUS P != EMPTY",
            "boolean": "mp = 0, sm != 0 => s(1-p) != 0",
            "venn": "Region S outside P = exists (non-empty)",
        },
    }

    PREDICATE_TEMPLATES = {
        ("A", "A", "A", 1): {
            "major": "forall x. M(x) -> P(x)",
            "minor": "forall x. S(x) -> M(x)",
            "conclusion": "forall x. S(x) -> P(x)",
            "steps": [
                "1. forall x. S(x) -> M(x)  [Premisa Menor]",
                "2. forall x. M(x) -> P(x)  [Premisa Mayor]",
                "3. S(a) -> M(a)  [Instanciacion Universal, 1]",
                "4. M(a) -> P(a)  [Instanciacion Universal, 2]",
                "5. S(a) -> P(a)  [Silogismo Hipotetico, 3,4]",
                "6. forall x. S(x) -> P(x)  [Generalizacion Universal, 5]",
            ],
            "quantifier": "universal-universal",
        },
        ("E", "A", "E", 1): {
            "major": "forall x. M(x) -> not P(x)",
            "minor": "forall x. S(x) -> M(x)",
            "conclusion": "forall x. S(x) -> not P(x)",
            "steps": [
                "1. forall x. S(x) -> M(x)  [Premisa Menor]",
                "2. forall x. M(x) -> not P(x)  [Premisa Mayor]",
                "3. S(a) -> M(a)  [IU, 1]",
                "4. M(a) -> not P(a)  [IU, 2]",
                "5. S(a) -> not P(a)  [SH, 3,4]",
                "6. forall x. S(x) -> not P(x)  [GU, 5]",
            ],
            "quantifier": "universal-negative",
        },
        ("A", "I", "I", 1): {
            "major": "forall x. M(x) -> P(x)",
            "minor": "exists x. S(x) and M(x)",
            "conclusion": "exists x. S(x) and P(x)",
            "steps": [
                "1. exists x. S(x) and M(x)  [Premisa Menor]",
                "2. forall x. M(x) -> P(x)  [Premisa Mayor]",
                "3. S(a) and M(a)  [Instanciacion Existencial, 1]",
                "4. M(a) -> P(a)  [IU, 2]",
                "5. S(a)  [Simplificacion, 3]",
                "6. M(a)  [Simplificacion, 3]",
                "7. P(a)  [Modus Ponens, 4,6]",
                "8. S(a) and P(a)  [Conjuncion, 5,7]",
                "9. exists x. S(x) and P(x)  [Generalizacion Existencial, 8]",
            ],
            "quantifier": "universal-existential",
        },
        ("E", "I", "O", 1): {
            "major": "forall x. M(x) -> not P(x)",
            "minor": "exists x. S(x) and M(x)",
            "conclusion": "exists x. S(x) and not P(x)",
            "steps": [
                "1. exists x. S(x) and M(x)  [Premisa Menor]",
                "2. forall x. M(x) -> not P(x)  [Premisa Mayor]",
                "3. S(a) and M(a)  [IE, 1]",
                "4. M(a) -> not P(a)  [IU, 2]",
                "5. S(a)  [Simp, 3]",
                "6. M(a)  [Simp, 3]",
                "7. not P(a)  [MP, 4,6]",
                "8. S(a) and not P(a)  [Conj, 5,7]",
                "9. exists x. S(x) and not P(x)  [GE, 8]",
            ],
            "quantifier": "universal-negative-existential",
        },
    }

    @classmethod
    def get_templates_for(
        cls,
        major: PropositionType,
        minor: PropositionType,
        conc: PropositionType,
        figure: int,
    ):
        key = (major.value, minor.value, conc.value, figure)
        mode = cls.MODE_MAP.get(key, "Desconocido")
        st = cls.SET_THEORY_TEMPLATES.get(
            key,
            {
                "major_eq": f"{major.value}: generico",
                "minor_eq": f"{minor.value}: generico",
                "conc_eq": f"{conc.value}: generico",
                "chain": "",
                "boolean": "",
                "venn": "",
            },
        )
        plt = cls.PREDICATE_TEMPLATES.get(
            key,
            {
                "major": f"Generico mayor ({major.value})",
                "minor": f"Generico menor ({minor.value})",
                "conclusion": f"Generico conclusion ({conc.value})",
                "steps": [],
                "quantifier": "generico",
            },
        )
        return mode, st, plt

    @classmethod
    def reduce_scholastic(cls, pattern: SyllogismPattern) -> ScholasticReduction:
        key = (
            pattern.major_type.value,
            pattern.minor_type.value,
            pattern.conclusion_type.value,
            pattern.figure,
        )
        mode = cls.MODE_MAP.get(key, f"Desconocido-{pattern.figure}")
        rules = cls.REDUCTION_RULES.get(pattern.figure, {}).get(mode, [])

        def prop_scheme(ptype: PropositionType, subj: str, pred: str) -> str:
            schemes = {
                PropositionType.A: f"Todo {subj} es {pred}",
                PropositionType.E: f"Ningun {subj} es {pred}",
                PropositionType.I: f"Algun {subj} es {pred}",
                PropositionType.O: f"Algun {subj} no es {pred}",
            }
            return schemes.get(ptype, f"{subj} ? {pred}")

        return ScholasticReduction(
            mode_name=mode,
            mnemotechnic=f"{pattern.major_type.value}{pattern.minor_type.value}{pattern.conclusion_type.value}-{pattern.figure}",
            figure=pattern.figure,
            reduction_rules=rules,
            premise_major_scheme=prop_scheme(
                pattern.major_type, pattern.middle, pattern.predicate
            ),
            premise_minor_scheme=prop_scheme(
                pattern.minor_type, pattern.subject, pattern.middle
            ),
            conclusion_scheme=prop_scheme(
                pattern.conclusion_type, pattern.subject, pattern.predicate
            ),
            vocal_pattern=f"{pattern.major_type.value}{pattern.minor_type.value}{pattern.conclusion_type.value}",
        )

    @classmethod
    def reduce_set_theory(cls, pattern: SyllogismPattern) -> SetTheoryReduction:
        key = (
            pattern.major_type.value,
            pattern.minor_type.value,
            pattern.conclusion_type.value,
            pattern.figure,
        )
        mode = cls.MODE_MAP.get(key, "Desconocido")
        st = cls.SET_THEORY_TEMPLATES.get(
            key,
            {
                "major_eq": f"{pattern.middle} ? {pattern.predicate}",
                "minor_eq": f"{pattern.subject} ? {pattern.middle}",
                "conc_eq": f"{pattern.subject} ? {pattern.predicate}",
                "chain": f"{pattern.subject} -> {pattern.middle} -> {pattern.predicate}",
                "boolean": "gen",
                "venn": "gen",
            },
        )

        return SetTheoryReduction(
            mode_name=mode,
            major_equation=st["major_eq"],
            minor_equation=st["minor_eq"],
            conclusion_equation=st["conc_eq"],
            transitive_chain=st["chain"],
            boolean_form=st["boolean"],
            venn_region=st["venn"],
        )

    @classmethod
    def reduce_predicate_logic(
        cls, pattern: SyllogismPattern
    ) -> PredicateLogicReduction:
        key = (
            pattern.major_type.value,
            pattern.minor_type.value,
            pattern.conclusion_type.value,
            pattern.figure,
        )
        mode = cls.MODE_MAP.get(key, "Desconocido")
        pt = cls.PREDICATE_TEMPLATES.get(
            key,
            {
                "major": f"{pattern.major_type.value}({pattern.middle},{pattern.predicate})",
                "minor": f"{pattern.minor_type.value}({pattern.subject},{pattern.middle})",
                "conclusion": f"{pattern.conclusion_type.value}({pattern.subject},{pattern.predicate})",
                "steps": [],
                "quantifier": "gen",
            },
        )

        return PredicateLogicReduction(
            mode_name=mode,
            major_formula=pt["major"],
            minor_formula=pt["minor"],
            conclusion_formula=pt["conclusion"],
            derivation_steps=pt["steps"],
            quantifier_structure=pt["quantifier"],
        )

    @classmethod
    def reduce_all(cls, pattern: SyllogismPattern) -> UnifiedSyllogism:
        scholastic = cls.reduce_scholastic(pattern)
        set_theory = cls.reduce_set_theory(pattern)
        predicate = cls.reduce_predicate_logic(pattern)

        return UnifiedSyllogism(
            key=pattern.fingerprint(),
            mode_name=scholastic.mode_name,
            vocal_pattern=scholastic.vocal_pattern,
            figure=pattern.figure,
            scholastic=scholastic,
            set_theory=set_theory,
            predicate_logic=predicate,
            terms={
                "S": pattern.subject,
                "P": pattern.predicate,
                "M": pattern.middle,
            },
        )

    @classmethod
    def find_equivalents(cls, unified_or_pattern) -> List[str]:
        if hasattr(unified_or_pattern, "conclusion_type"):
            pattern = unified_or_pattern
            target = (pattern.conclusion_type.value, pattern.subject, pattern.predicate)
        else:
            unified = unified_or_pattern
            target = (
                unified.vocal_pattern[-1],
                unified.terms.get("S", ""),
                unified.terms.get("P", ""),
            )
        equivalents = []
        for (maj, min_, con_, fig), mode in cls.MODE_MAP.items():
            if con_ == target[0]:
                equivalents.append(f"{mode} ({maj}{min_}{con_}-{fig})")
        return equivalents

    @classmethod
    def format_memory_compressed(cls, unified: UnifiedSyllogism) -> str:
        """Formato ultra-comprimido para la memoria de los agentes."""
        s = unified.scholastic
        st = unified.set_theory
        pt = unified.predicate_logic

        return (
            f"[{s.mnemotechnic}] {s.mode_name} | "
            f"S:{unified.terms['S']} P:{unified.terms['P']} M:{unified.terms['M']} | "
            f"SET:{st.conclusion_equation} | "
            f"FOL:{pt.conclusion_formula}"
        )

    @classmethod
    def format_full_report(cls, unified: UnifiedSyllogism) -> str:
        s = unified.scholastic
        st = unified.set_theory
        pt = unified.predicate_logic
        t = unified.terms

        lines = [
            "=" * 60,
            f"SILOGISMO: {unified.mode_name} ({unified.vocal_pattern}-{unified.figure})",
            f"Terminos: S={t['S']}, P={t['P']}, M={t['M']}",
            "=" * 60,
            "",
            "--- Nivel 1: Reduccion Escolastica ---",
            f"  Mnemotecnia:    {s.mnemotechnic}",
            f"  Premisa Mayor:  {s.premise_major_scheme}",
            f"  Premisa Menor:  {s.premise_minor_scheme}",
            f"  Conclusion:     {s.conclusion_scheme}",
        ]

        if s.reduction_rules:
            lines.append(f"  Reglas:         {', '.join(s.reduction_rules)}")
            for r in s.reduction_rules:
                cons = r[0] if r else ""
                if cons in cls.CONSONANT_MEANING:
                    lines.append(f"    {cons}: {cls.CONSONANT_MEANING[cons]}")

        lines.append(f"  Fuente:         {s.source}")
        lines.append("")

        lines.append("--- Nivel 2: Teoria de Conjuntos ---")
        lines.append(f"  Mayor:  {st.major_equation}")
        lines.append(f"  Menor:  {st.minor_equation}")
        lines.append(f"  Conc:   {st.conclusion_equation}")
        lines.append(f"  Cadena transitiva: {st.transitive_chain}")
        lines.append(f"  Boole:  {st.boolean_form}")
        lines.append(f"  Venn:   {st.venn_region}")
        lines.append(f"  Fuente: {st.source}")
        lines.append("")

        lines.append("--- Nivel 3: Logica de Predicados ---")
        lines.append(f"  Mayor:  {pt.major_formula}")
        lines.append(f"  Menor:  {pt.minor_formula}")
        lines.append(f"  Conc:   {pt.conclusion_formula}")
        if pt.derivation_steps:
            lines.append(f"  Derivacion ({len(pt.derivation_steps)} pasos):")
            for step in pt.derivation_steps:
                lines.append(f"    {step}")
        lines.append(f"  Estructura: {pt.quantifier_structure}")
        lines.append(f"  Fuente:   {pt.source}")
        lines.append("")

        equiv = cls.find_equivalents(unified)
        if len(equiv) > 1:
            lines.append("--- Equivalentes ---")
            lines.append(f"  Modos con misma conclusion: {', '.join(equiv)}")
            lines.append("")

        lines.append(cls.format_memory_compressed(unified))

        return "\n".join(lines)

    @classmethod
    def extract_from_json(cls, agent_output: dict) -> Optional[SyllogismPattern]:
        try:
            sil = agent_output.get("silogismo", {})
            if not sil:
                return None
            pm = sil.get("premisa_mayor", "")
            pn = sil.get("premisa_menor", "")
            conc = sil.get("conclusion", "")

            pm_type_raw = sil.get("premisa_mayor_tipo")
            pn_type_raw = sil.get("premisa_menor_tipo")
            conc_type_raw = sil.get("conclusion_tipo")

            from concilio_salamanca.debate.syllogism_cache import PropositionType

            major_type = None
            if pm_type_raw:
                try:
                    major_type = PropositionType(pm_type_raw.strip().upper())
                except ValueError:
                    pass

            minor_type = None
            if pn_type_raw:
                try:
                    minor_type = PropositionType(pn_type_raw.strip().upper())
                except ValueError:
                    pass

            c_type = None
            if conc_type_raw:
                try:
                    c_type = PropositionType(conc_type_raw.strip().upper())
                except ValueError:
                    pass

            classified_major_type, major_terms = cls._classify_proposition(pm)
            classified_minor_type, minor_terms = cls._classify_proposition(pn)
            classified_conc_type, conc_terms = cls._classify_proposition(conc)

            if not major_type:
                major_type = classified_major_type
            if not minor_type:
                minor_type = classified_minor_type
            if not c_type:
                c_type = classified_conc_type

            if not major_type or not minor_type or not c_type:
                return None

            terms = set()
            if major_terms:
                terms.update(major_terms)
            if minor_terms:
                terms.update(minor_terms)
            if conc_terms:
                terms.update(conc_terms)

            terms_list = list(terms)
            if len(terms_list) < 3:
                terms_list = ["S", "P", "M"]

            figure = cls._deduce_figure(major_type, minor_type, c_type)

            return SyllogismPattern(
                major_type=major_type,
                minor_type=minor_type,
                conclusion_type=c_type,
                figure=figure,
                subject=terms_list[0] if len(terms_list) > 0 else "S",
                predicate=terms_list[1] if len(terms_list) > 1 else "P",
                middle=terms_list[2] if len(terms_list) > 2 else "M",
            )
        except Exception:
            return None

    @classmethod
    def _classify_proposition(
        cls, text: str
    ) -> Tuple[Optional[PropositionType], List[str]]:
        text_lower = text.lower()
        words = re.findall(r"\b[a-zA-Z\u00C0-\u024F]{3,}\b", text_lower)
        if not words:
            return None, []
        terms = []
        for w in words:
            if w not in (
                "todo",
                "toda",
                "todos",
                "ningun",
                "ninguna",
                "algun",
                "alguna",
                "es",
                "son",
                "no",
                "the",
                "all",
                "some",
                "any",
                "every",
                "that",
                "which",
                "para",
                "con",
                "del",
                "una",
                "los",
                "las",
                "por",
                "que",
                "como",
                "sus",
                "entre",
                "cada",
            ):
                if len(w) > 2 and w not in terms:
                    terms.append(w)

        text_norm = re.sub(r"\s+", " ", text_lower)

        has_no = bool(
            re.search(
                r"\b(no|ningun|ninguna|nunca|jamas|none|without|nada|carece|ausencia|falta)\b",
                text_norm,
            )
        )
        has_some = bool(
            re.search(
                r"\b(algun|alguna|algunos|algunas|existe|existen|some|particular|cierto|cierta)\b",
                text_norm,
            )
        )
        has_all = bool(
            re.search(
                r"\b(todo|toda|todos|todas|cada|all|every|cualquier|cualquiera)\b",
                text_norm,
            )
        )
        has_not = bool(
            re.search(
                r"\b(no es|no son|no esta|no estan|not|is not|are not)\b", text_norm
            )
        )

        if has_no and (has_all or not has_some):
            return PropositionType.E, terms[:3]
        if has_some and has_not:
            return PropositionType.O, terms[:3]
        if has_some:
            return PropositionType.I, terms[:3]
        if has_all and has_not:
            return PropositionType.E, terms[:3]
        if has_not:
            return PropositionType.O, terms[:3]
        return PropositionType.A, terms[:3]

    @classmethod
    def _deduce_figure(
        cls, major: PropositionType, minor: PropositionType, conc: PropositionType
    ) -> int:
        key = (major.value, minor.value, conc.value)
        for (maj, min_, con_, fig), _ in cls.MODE_MAP.items():
            if (maj, min_, con_) == key:
                return fig
        return 1

    @classmethod
    def get_mode_name(cls, pattern: SyllogismPattern) -> str:
        key = (
            pattern.major_type.value,
            pattern.minor_type.value,
            pattern.conclusion_type.value,
            pattern.figure,
        )
        return cls.MODE_MAP.get(key, f"Desconocido-{pattern.figure}")

    @classmethod
    def compress_to_set(cls, pattern: SyllogismPattern) -> str:
        rel, result = pattern.to_set_relation()
        mode = cls.get_mode_name(pattern)
        lines = [
            f"Modo: {mode} (Figura {pattern.figure})",
            f"Terminos: S={pattern.subject}, P={pattern.predicate}, M={pattern.middle}",
            f"Reduccion conjuntista: {result}",
        ]
        return "\n".join(lines)

    @classmethod
    def unified_fingerprint(cls, pattern: SyllogismPattern) -> str:
        unified = cls.reduce_all(pattern)
        raw = (
            f"{unified.vocal_pattern}|{unified.figure}|"
            f"{unified.set_theory.conclusion_equation}|"
            f"{unified.predicate_logic.conclusion_formula}"
        )
        return hashlib.sha256(raw.encode()).hexdigest()[:16]


class SyllogismCache:
    def __init__(self, cache_path: Optional[str] = None):
        if cache_path is None:
            cache_path = str(Path(__file__).parent / "syllogism_cache.json")
        self.cache_path = Path(cache_path)
        self.entries: Dict[str, CacheEntry] = {}
        self.unified_store: Dict[str, UnifiedSyllogism] = {}
        self.stats = {
            "hits": 0,
            "misses": 0,
            "tokens_saved_est": 0,
            "scholastic_hits": 0,
            "set_theory_hits": 0,
            "predicate_hits": 0,
        }
        self._load()

    def _load(self):
        if self.cache_path.exists():
            try:
                data = json.loads(self.cache_path.read_text(encoding="utf-8"))
                for fp, entry_data in data.get("entries", {}).items():
                    pat = entry_data["pattern"]
                    pattern = SyllogismPattern(
                        major_type=PropositionType(pat["major_type"]),
                        minor_type=PropositionType(pat["minor_type"]),
                        conclusion_type=PropositionType(pat["conclusion_type"]),
                        figure=pat["figure"],
                        subject=pat["subject"],
                        predicate=pat["predicate"],
                        middle=pat["middle"],
                    )
                    self.entries[fp] = CacheEntry(
                        fingerprint=fp,
                        pattern=pattern,
                        set_relation=entry_data["set_relation"],
                        conclusion_text=entry_data["conclusion_text"],
                        agent=entry_data["agent"],
                        timestamp=entry_data["timestamp"],
                        hit_count=entry_data.get("hit_count", 1),
                    )
                self.stats = data.get("stats", self.stats)
            except (json.JSONDecodeError, KeyError):
                pass

    def save(self):
        data = {"entries": {}, "stats": self.stats}
        for fp, entry in self.entries.items():
            data["entries"][fp] = {
                "pattern": {
                    "major_type": entry.pattern.major_type.value,
                    "minor_type": entry.pattern.minor_type.value,
                    "conclusion_type": entry.pattern.conclusion_type.value,
                    "figure": entry.pattern.figure,
                    "subject": entry.pattern.subject,
                    "predicate": entry.pattern.predicate,
                    "middle": entry.pattern.middle,
                },
                "set_relation": entry.set_relation,
                "conclusion_text": entry.conclusion_text,
                "agent": entry.agent,
                "timestamp": entry.timestamp,
                "hit_count": entry.hit_count,
            }
        self.cache_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def lookup(self, pattern: SyllogismPattern) -> Optional[CacheEntry]:
        fp = pattern.fingerprint()
        key = pattern.normalized_key()

        if fp in self.entries:
            entry = self.entries[fp]
            entry.hit_count += 1
            self.stats["hits"] += 1
            self.stats["tokens_saved_est"] += 800
            return entry

        for existing in self.entries.values():
            if existing.pattern.normalized_key() == key:
                existing.hit_count += 1
                self.stats["hits"] += 1
                self.stats["tokens_saved_est"] += 800
                return existing

        self.stats["misses"] += 1
        return None

    def lookup_unified(self, pattern: SyllogismPattern) -> Optional[UnifiedSyllogism]:
        unified = SyllogismReducer.reduce_all(pattern)
        if unified.key in self.unified_store:
            self.stats["hits"] += 1
            self.stats["tokens_saved_est"] += 300
            return self.unified_store[unified.key]

        for existing in self.unified_store.values():
            if (
                existing.vocal_pattern == unified.vocal_pattern
                and existing.figure == unified.figure
                and existing.terms == unified.terms
            ):
                self.stats["hits"] += 1
                self.stats["tokens_saved_est"] += 300
                return existing

        self.stats["misses"] += 1
        self.unified_store[unified.key] = unified
        return unified

    def store(self, entry: CacheEntry):
        self.entries[entry.fingerprint] = entry
        self.save()

    def summary(self) -> str:
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0
        return (
            f"Cache trinivel: {len(self.entries)} patrones + {len(self.unified_store)} unificados | "
            f"{self.stats['hits']} hits / {self.stats['misses']} misses "
            f"({hit_rate:.0f}%) | "
            f"~{self.stats['tokens_saved_est']:,} tokens ahorrados"
        )


_global_cache: Optional[SyllogismCache] = None


def get_syllogism_cache() -> SyllogismCache:
    global _global_cache
    if _global_cache is None:
        _global_cache = SyllogismCache()
    return _global_cache
