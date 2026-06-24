"""
Compresor de Silogismos: reduce silogismos aristotelicos a operaciones de conjuntos,
permitiendo cachear conclusiones y ahorrar llamadas al LLM (memoria de pensamiento).

Mapeo silogismo -> teoria de conjuntos:
  Barbara (AAA-1):  M subset P, S subset M  =>  S subset P
  Celarent (EAE-1): M intersect P = empty, S subset M  =>  S intersect P = empty
  Darii (AII-1):    M subset P, S intersect M != empty  =>  S intersect P != empty
  Ferio (EIO-1):    M intersect P = empty, S intersect M != empty  =>  (S-M-P) != empty

Cada silogismo se normaliza extrayendo sus terminos (S=subject, P=predicate, M=middle),
se hashea, y se almacena en cache. Antes de invocar al LLM, se verifica si un silogismo
equivalente ya fue razonado.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class PropositionType(Enum):
    A = "A"  # Universal Affirmative: All S are P
    E = "E"  # Universal Negative: No S is P
    I = "I"  # Particular Affirmative: Some S are P
    O = "O"  # Particular Negative: Some S are not P


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
    figure: int  # 1-4
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
        terms = sorted([self.subject.lower().strip(), self.predicate.lower().strip(), self.middle.lower().strip()])
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


class SyllogismCache:
    def __init__(self, cache_path: Optional[str] = None):
        if cache_path is None:
            cache_path = str(Path(__file__).parent / "syllogism_cache.json")
        self.cache_path = Path(cache_path)
        self.entries: Dict[str, CacheEntry] = {}
        self.stats = {"hits": 0, "misses": 0, "tokens_saved_est": 0}
        self._load()

    def _load(self):
        if self.cache_path.exists():
            try:
                data = json.loads(self.cache_path.read_text(encoding="utf-8"))
                for fp, entry_data in data.get("entries", {}).items():
                    pattern_data = entry_data["pattern"]
                    pattern = SyllogismPattern(
                        major_type=PropositionType(pattern_data["major_type"]),
                        minor_type=PropositionType(pattern_data["minor_type"]),
                        conclusion_type=PropositionType(pattern_data["conclusion_type"]),
                        figure=pattern_data["figure"],
                        subject=pattern_data["subject"],
                        predicate=pattern_data["predicate"],
                        middle=pattern_data["middle"],
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
                self.stats = data.get("stats", {"hits": 0, "misses": 0, "tokens_saved_est": 0})
            except (json.JSONDecodeError, KeyError):
                pass

    def save(self):
        data = {
            "entries": {},
            "stats": self.stats,
        }
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
        self.cache_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

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

    def store(self, entry: CacheEntry):
        self.entries[entry.fingerprint] = entry
        self.save()

    def summary(self) -> str:
        total = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0
        return (
            f"Cache de Silogismos: {len(self.entries)} entradas | "
            f"{self.stats['hits']} hits / {self.stats['misses']} misses "
            f"({hit_rate:.0f}%) | "
            f"~{self.stats['tokens_saved_est']:,} tokens ahorrados"
        )


class SyllogismCompressor:
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

    @classmethod
    def extract_from_json(cls, agent_output: dict) -> Optional[SyllogismPattern]:
        try:
            sil = agent_output.get("silogismo", {})
            if not sil:
                return None

            pm = sil.get("premisa_mayor", "")
            pn = sil.get("premisa_menor", "")
            conc = sil.get("conclusion", "")

            major_type, major_terms = cls._classify_proposition(pm)
            minor_type, minor_terms = cls._classify_proposition(pn)
            conc_type, conc_terms = cls._classify_proposition(conc)

            if not major_type or not minor_type or not conc_type:
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

            figure = cls._deduce_figure(major_type, minor_type, conc_type)

            return SyllogismPattern(
                major_type=major_type,
                minor_type=minor_type,
                conclusion_type=conc_type,
                figure=figure,
                subject=terms_list[0] if len(terms_list) > 0 else "S",
                predicate=terms_list[1] if len(terms_list) > 1 else "P",
                middle=terms_list[2] if len(terms_list) > 2 else "M",
            )
        except Exception:
            return None

    @classmethod
    def _classify_proposition(cls, text: str) -> Tuple[Optional[PropositionType], List[str]]:
        text_lower = text.lower()
        words = re.findall(r'\b[a-zA-Z\u00C0-\u024F]{3,}\b', text_lower)

        if not words:
            return None, []

        terms = []
        for w in words:
            if w not in ("todo", "toda", "todos", "ningun", "ninguna", "algun", "alguna", "es", "son", "no", "the", "all", "some", "any", "every", "that", "which"):
                if len(w) > 2 and w not in terms:
                    terms.append(w)

        if re.search(r'\b(todo|toda|todos|todas|all|every|cada)\b', text_lower):
            if re.search(r'\b(no|ningun|ninguna|except)\b', text_lower) and not re.search(r'\b(es buena|es util|es verdad|perfecciona)\b', text_lower):
                return PropositionType.E, terms[:3]
            return PropositionType.A, terms[:3]

        if re.search(r'\b(ningun|ninguna|no hay|no existe|none|no)\b', text_lower):
            return PropositionType.E, terms[:3]

        if re.search(r'\b(algun|alguna|algunos|algunas|some|existe|particular)\b', text_lower):
            if re.search(r'\b(no es|no son|not|is not)\b', text_lower):
                return PropositionType.O, terms[:3]
            return PropositionType.I, terms[:3]

        return PropositionType.A, terms[:3]

    @classmethod
    def _deduce_figure(cls, major: PropositionType, minor: PropositionType, conc: PropositionType) -> int:
        key = (major.value, minor.value, conc.value)
        for (maj, min_, con_, fig), _ in cls.MODE_MAP.items():
            if (maj, min_, con_) == key:
                return fig
        return 1

    @classmethod
    def get_mode_name(cls, pattern: SyllogismPattern) -> str:
        key = (pattern.major_type.value, pattern.minor_type.value,
               pattern.conclusion_type.value, pattern.figure)
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


_global_cache: Optional[SyllogismCache] = None


def get_syllogism_cache() -> SyllogismCache:
    global _global_cache
    if _global_cache is None:
        _global_cache = SyllogismCache()
    return _global_cache
