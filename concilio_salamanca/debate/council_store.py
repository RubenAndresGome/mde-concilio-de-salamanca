"""Persistencia SQLite para dogmas, memoria y grafo del Concilio.

La libreria estandar basta: WAL permite lectores concurrentes y FTS5 aporta
recuperacion local sin cargar todo el historial en el prompt.
"""

from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional


def default_db_path() -> Path:
    configured = os.environ.get("CONCILIO_DB_PATH")
    if configured:
        return Path(configured).expanduser()
    root = Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local" / "share"))
    return root / "concilio-salamanca" / "concilio.db"


class CouncilStore:
    """Repositorio transaccional pequeno, portable y auditable."""

    def __init__(self, path: Optional[str | Path] = None):
        self.path = Path(path) if path else default_db_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 10000")
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self.connect() as db:
            db.execute("PRAGMA journal_mode = WAL")
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS dogmas (
                    id INTEGER PRIMARY KEY,
                    objective TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TEXT
                );
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY,
                    dogma_id INTEGER NOT NULL REFERENCES dogmas(id) ON DELETE CASCADE,
                    text TEXT NOT NULL,
                    proposition TEXT NOT NULL,
                    polarity INTEGER NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1
                );
                CREATE TABLE IF NOT EXISTS contradictions (
                    id INTEGER PRIMARY KEY,
                    dogma_id INTEGER NOT NULL REFERENCES dogmas(id) ON DELETE CASCADE,
                    order_a INTEGER NOT NULL REFERENCES orders(id),
                    order_b INTEGER NOT NULL REFERENCES orders(id),
                    reason TEXT NOT NULL,
                    resolved INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS graph_nodes (
                    id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL,
                    label TEXT NOT NULL,
                    payload TEXT NOT NULL DEFAULT '{}',
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS graph_edges (
                    source TEXT NOT NULL REFERENCES graph_nodes(id) ON DELETE CASCADE,
                    target TEXT NOT NULL REFERENCES graph_nodes(id) ON DELETE CASCADE,
                    relation TEXT NOT NULL,
                    weight REAL NOT NULL DEFAULT 1.0,
                    payload TEXT NOT NULL DEFAULT '{}',
                    PRIMARY KEY (source, target, relation)
                );
                CREATE INDEX IF NOT EXISTS idx_edges_source ON graph_edges(source);
                CREATE INDEX IF NOT EXISTS idx_edges_target ON graph_edges(target);
                """
            )
            try:
                db.execute(
                    "CREATE VIRTUAL TABLE IF NOT EXISTS graph_fts "
                    "USING fts5(node_id UNINDEXED, label, content)"
                )
            except sqlite3.OperationalError:
                pass

    def upsert_node(
        self, node_id: str, kind: str, label: str, payload: Optional[dict] = None
    ) -> None:
        serialized = json.dumps(payload or {}, ensure_ascii=False, sort_keys=True)
        with self.connect() as db:
            db.execute(
                """INSERT INTO graph_nodes(id, kind, label, payload)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(id) DO UPDATE SET kind=excluded.kind,
                   label=excluded.label, payload=excluded.payload,
                   updated_at=CURRENT_TIMESTAMP""",
                (node_id, kind, label, serialized),
            )
            try:
                db.execute("DELETE FROM graph_fts WHERE node_id = ?", (node_id,))
                db.execute(
                    "INSERT INTO graph_fts(node_id, label, content) VALUES (?, ?, ?)",
                    (node_id, label, serialized),
                )
            except sqlite3.OperationalError:
                pass

    def add_edge(
        self,
        source: str,
        target: str,
        relation: str,
        weight: float = 1.0,
        payload: Optional[dict] = None,
    ) -> None:
        with self.connect() as db:
            db.execute(
                """INSERT INTO graph_edges(source, target, relation, weight, payload)
                   VALUES (?, ?, ?, ?, ?)
                   ON CONFLICT(source, target, relation) DO UPDATE SET
                   weight=excluded.weight, payload=excluded.payload""",
                (
                    source,
                    target,
                    relation,
                    max(0.0, float(weight)),
                    json.dumps(payload or {}, ensure_ascii=False, sort_keys=True),
                ),
            )

    def local_context(self, query: str, limit: int = 8, hops: int = 1) -> list[dict]:
        """Recuperar nodos lexicales y su vecindario, con limite duro."""
        limit = max(1, min(int(limit), 50))
        hops = max(0, min(int(hops), 3))
        with self.connect() as db:
            seed_ids: list[str] = []
            terms = " ".join(part for part in query.replace('"', " ").split() if part)
            if terms:
                try:
                    rows = db.execute(
                        "SELECT node_id FROM graph_fts WHERE graph_fts MATCH ? "
                        "ORDER BY bm25(graph_fts) LIMIT ?",
                        (terms, limit),
                    ).fetchall()
                    seed_ids = [row[0] for row in rows]
                except sqlite3.OperationalError:
                    pattern = f"%{query[:200]}%"
                    rows = db.execute(
                        "SELECT id FROM graph_nodes WHERE label LIKE ? OR payload LIKE ? LIMIT ?",
                        (pattern, pattern, limit),
                    ).fetchall()
                    seed_ids = [row[0] for row in rows]

            discovered = list(dict.fromkeys(seed_ids))
            frontier = list(discovered)
            for _ in range(hops):
                if not frontier or len(discovered) >= limit:
                    break
                placeholders = ",".join("?" for _ in frontier)
                rows = db.execute(
                    f"SELECT source, target FROM graph_edges "
                    f"WHERE source IN ({placeholders}) OR target IN ({placeholders}) "
                    "ORDER BY weight DESC LIMIT ?",
                    (*frontier, *frontier, limit * 2),
                ).fetchall()
                next_frontier = []
                for row in rows:
                    for node_id in (row[0], row[1]):
                        if node_id not in discovered:
                            discovered.append(node_id)
                            next_frontier.append(node_id)
                            if len(discovered) >= limit:
                                break
                frontier = next_frontier

            if not discovered:
                return []
            placeholders = ",".join("?" for _ in discovered)
            nodes = db.execute(
                f"SELECT id, kind, label, payload FROM graph_nodes "
                f"WHERE id IN ({placeholders})",
                discovered,
            ).fetchall()
            by_id = {
                row["id"]: {
                    "id": row["id"],
                    "kind": row["kind"],
                    "label": row["label"],
                    "payload": json.loads(row["payload"]),
                }
                for row in nodes
            }
            return [by_id[node_id] for node_id in discovered if node_id in by_id][:limit]

    def stats(self) -> dict:
        with self.connect() as db:
            return {
                "dogmas": db.execute("SELECT COUNT(*) FROM dogmas").fetchone()[0],
                "contradicciones_abiertas": db.execute(
                    "SELECT COUNT(*) FROM contradictions WHERE resolved = 0"
                ).fetchone()[0],
                "nodos": db.execute("SELECT COUNT(*) FROM graph_nodes").fetchone()[0],
                "aristas": db.execute("SELECT COUNT(*) FROM graph_edges").fetchone()[0],
                "db_path": str(self.path),
            }
