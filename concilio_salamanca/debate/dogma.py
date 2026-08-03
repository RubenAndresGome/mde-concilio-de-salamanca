"""Constitucion objetiva de ordenes antes de convocar agentes costosos."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass
from typing import Iterable, Optional

from concilio_salamanca.debate.council_store import CouncilStore


NEGATIONS = {"no", "nunca", "jamas", "evita", "prohibe", "sin"}
FILLERS = {
    "debe", "deben", "debera", "usar", "usa", "use", "uses", "utiliza", "utilizar",
    "quiero", "que", "el", "la", "los", "las", "un", "una", "por", "favor",
}


def _plain(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def normalize_order(text: str) -> tuple[str, int]:
    words = re.findall(r"[a-z0-9_+#.-]+", _plain(text))
    polarity = -1 if any(word in NEGATIONS for word in words) else 1
    proposition = [word for word in words if word not in NEGATIONS | FILLERS]
    return " ".join(proposition), polarity


@dataclass(frozen=True)
class Contradiction:
    order_a: int
    order_b: int
    text_a: str
    text_b: str
    proposition: str


class DogmaEngine:
    def __init__(self, store: Optional[CouncilStore] = None):
        self.store = store or CouncilStore()

    def propose(self, orders: Iterable[str], objective: str = "") -> dict:
        clean_orders = [str(order).strip() for order in orders if str(order).strip()]
        if not clean_orders:
            raise ValueError("Se requiere al menos una orden concreta.")

        parsed = [(text, *normalize_order(text)) for text in clean_orders]
        with self.store.connect() as db:
            cursor = db.execute(
                "INSERT INTO dogmas(objective, status) VALUES (?, ?)",
                (objective.strip(), "PROPUESTO"),
            )
            dogma_id = int(cursor.lastrowid)
            order_ids = []
            for text, proposition, polarity in parsed:
                cursor = db.execute(
                    "INSERT INTO orders(dogma_id, text, proposition, polarity) "
                    "VALUES (?, ?, ?, ?)",
                    (dogma_id, text, proposition, polarity),
                )
                order_ids.append(int(cursor.lastrowid))

            contradictions: list[Contradiction] = []
            for left in range(len(parsed)):
                for right in range(left + 1, len(parsed)):
                    text_a, proposition_a, polarity_a = parsed[left]
                    text_b, proposition_b, polarity_b = parsed[right]
                    if proposition_a and proposition_a == proposition_b and polarity_a != polarity_b:
                        contradiction = Contradiction(
                            order_ids[left], order_ids[right], text_a, text_b, proposition_a
                        )
                        contradictions.append(contradiction)
                        db.execute(
                            "INSERT INTO contradictions(dogma_id, order_a, order_b, reason) "
                            "VALUES (?, ?, ?, ?)",
                            (
                                dogma_id,
                                contradiction.order_a,
                                contradiction.order_b,
                                f"Polaridad opuesta sobre '{proposition_a}'",
                            ),
                        )

            status = "CONTRADICTORIO" if contradictions else "OBJETIVO"
            db.execute("UPDATE dogmas SET status = ? WHERE id = ?", (status, dogma_id))

        dogma_node = f"dogma:{dogma_id}"
        self.store.upsert_node(
            dogma_node, "dogma", objective.strip() or f"Dogma {dogma_id}", {"status": status}
        )
        for order_id, (text, proposition, polarity) in zip(order_ids, parsed):
            node_id = f"order:{order_id}"
            self.store.upsert_node(
                node_id,
                "orden",
                text,
                {"proposicion": proposition, "polaridad": polarity},
            )
            self.store.add_edge(dogma_node, node_id, "CONTIENE")

        conflict_rows = [c.__dict__ for c in contradictions]
        return {
            "dogma_id": dogma_id,
            "estado": status,
            "objetivo": objective.strip(),
            "ordenes": [
                {"id": order_id, "texto": parsed[index][0]}
                for index, order_id in enumerate(order_ids)
            ],
            "contradicciones": conflict_rows,
            "requiere_usuario": bool(contradictions),
            "mensaje_usuario": self._contradiction_message(conflict_rows),
        }

    def resolve(self, dogma_id: int, keep_order_ids: Iterable[int], objective: str) -> dict:
        keep = {int(order_id) for order_id in keep_order_ids}
        if not objective.strip():
            raise ValueError("El Dogma objetivo necesita un objetivo explicito.")
        with self.store.connect() as db:
            rows = db.execute(
                "SELECT id FROM orders WHERE dogma_id = ?", (int(dogma_id),)
            ).fetchall()
            available = {int(row[0]) for row in rows}
            if not keep or not keep.issubset(available):
                raise ValueError("Las ordenes conservadas no pertenecen al Dogma.")
            db.execute(
                "UPDATE orders SET active = CASE WHEN id IN ({}) THEN 1 ELSE 0 END "
                "WHERE dogma_id = ?".format(",".join("?" for _ in keep)),
                (*sorted(keep), int(dogma_id)),
            )
            unresolved = db.execute(
                """SELECT COUNT(*) FROM contradictions c
                   JOIN orders a ON a.id=c.order_a JOIN orders b ON b.id=c.order_b
                   WHERE c.dogma_id=? AND a.active=1 AND b.active=1""",
                (int(dogma_id),),
            ).fetchone()[0]
            if unresolved:
                raise ValueError("Aun conservas ambos lados de una contradiccion.")
            db.execute(
                "UPDATE contradictions SET resolved=1 WHERE dogma_id=?",
                (int(dogma_id),),
            )
            db.execute(
                "UPDATE dogmas SET objective=?, status='OBJETIVO', resolved_at=CURRENT_TIMESTAMP "
                "WHERE id=?",
                (objective.strip(), int(dogma_id)),
            )
        self.store.upsert_node(
            f"dogma:{dogma_id}", "dogma", objective.strip(), {"status": "OBJETIVO"}
        )
        return self.get(int(dogma_id))

    def get(self, dogma_id: int) -> dict:
        with self.store.connect() as db:
            dogma = db.execute(
                "SELECT id, objective, status FROM dogmas WHERE id=?", (dogma_id,)
            ).fetchone()
            if not dogma:
                raise KeyError(f"Dogma {dogma_id} no existe.")
            orders = db.execute(
                "SELECT id, text FROM orders WHERE dogma_id=? AND active=1 ORDER BY id",
                (dogma_id,),
            ).fetchall()
        return {
            "dogma_id": dogma["id"],
            "objetivo": dogma["objective"],
            "estado": dogma["status"],
            "ordenes": [{"id": row["id"], "texto": row["text"]} for row in orders],
        }

    @staticmethod
    def compact(dogma: dict) -> str:
        orders = "; ".join(order["texto"] for order in dogma.get("ordenes", []))
        return f"DOGMA#{dogma['dogma_id']} objetivo={dogma.get('objetivo', '')}; ordenes={orders}"

    @staticmethod
    def _contradiction_message(contradictions: list[dict]) -> str:
        if not contradictions:
            return "Dogma objetivo creado; no se detectaron ordenes incompatibles."
        pairs = [f"«{item['text_a']}» vs «{item['text_b']}»" for item in contradictions]
        return (
            "No puedo convertir las ordenes en Dogma objetivo hasta que el usuario "
            "resuelva: " + "; ".join(pairs)
        )


def stable_node_id(kind: str, text: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    return f"{kind}:{digest}"
