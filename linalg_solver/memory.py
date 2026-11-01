"""SQLite-backed structured memory: nodes (claims) + edges (dependencies).

One file, one table for nodes, one for edges. Embeddings are float32 blobs and
similarity is plain numpy cosine over a few hundred rows — no index needed.
"""

from __future__ import annotations

import re
import sqlite3
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

from . import config
from .embed import embed

_SCHEMA = """
CREATE TABLE IF NOT EXISTS nodes (
    id          TEXT PRIMARY KEY,
    kind        TEXT NOT NULL,             -- definition | theorem | lemma | example
    title       TEXT NOT NULL,
    statement   TEXT NOT NULL,
    proof       TEXT,                      -- nullable
    status      TEXT NOT NULL,             -- seed | staged | verified
    confidence  REAL NOT NULL,
    embedding   BLOB,                      -- float32, of title + statement
    source      TEXT NOT NULL,             -- seed | user
    created_at  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS edges (
    from_id TEXT NOT NULL,                 -- from_id depends on / is proved using to_id
    to_id   TEXT NOT NULL,
    PRIMARY KEY (from_id, to_id)
);
CREATE INDEX IF NOT EXISTS idx_edges_to ON edges(to_id);
"""


@dataclass
class Node:
    id: str
    kind: str
    title: str
    statement: str
    proof: str | None
    status: str
    confidence: float
    source: str
    created_at: str
    score: float | None = None  # transient, set by retrieve()/find_duplicate()

    @property
    def kind_title(self) -> str:
        return f"{self.kind} {self.id}"


def _row_to_node(row: sqlite3.Row, score: float | None = None) -> Node:
    return Node(
        id=row["id"],
        kind=row["kind"],
        title=row["title"],
        statement=row["statement"],
        proof=row["proof"],
        status=row["status"],
        confidence=row["confidence"],
        source=row["source"],
        created_at=row["created_at"],
        score=score,
    )


def slugify(text: str, max_len: int = 48) -> str:
    """'Rank–nullity theorem!' -> 'rank-nullity-theorem'."""
    text = text.replace("–", "-").replace("—", "-").replace("−", "-")
    text = text.replace("×", "x")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:max_len].strip("-") or "node"


def _normalize(mat: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return mat / norms


def _norm_text(text: str) -> str:
    """Lowercase, punctuation- and whitespace-insensitive form for exact dedup."""
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


class Memory:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path is not None else config.db_path()
        # timeout: tolerate a second CLI/eval process writing briefly
        self.conn = sqlite3.connect(self.path, timeout=30)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(_SCHEMA)
        self.conn.commit()

    # ------------------------------------------------------------------ write
    def add(self, node: dict, depends_on: Iterable[str] = ()) -> str:
        """Insert a node plus `depends_on` edges. Computes the embedding if absent."""
        nid = node["id"]
        status = node.get("status", "verified")
        confidence = node.get("confidence")
        if confidence is None:
            confidence = (
                config.CONFIDENCE_SEED if status == "seed" else config.CONFIDENCE_USER
            )
        blob = node.get("embedding")
        if blob is None:
            vec = embed(f"{node['title']}. {node['statement']}")
            blob = np.asarray(vec, dtype=np.float32).tobytes()
        elif isinstance(blob, np.ndarray):
            blob = blob.astype(np.float32).tobytes()

        self.conn.execute(
            """INSERT INTO nodes
               (id, kind, title, statement, proof, status, confidence, embedding, source, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                nid,
                node.get("kind", "theorem"),
                node["title"],
                node["statement"],
                node.get("proof"),
                status,
                float(confidence),
                blob,
                node.get("source", "user"),
                node.get("created_at")
                or datetime.now(timezone.utc).isoformat(timespec="seconds"),
            ),
        )
        missing = []
        for dep in depends_on:
            if self.get(dep) is None:
                missing.append(dep)
                continue
            self.conn.execute(
                "INSERT OR IGNORE INTO edges (from_id, to_id) VALUES (?, ?)", (nid, dep)
            )
        self.conn.commit()
        if missing:
            raise ValueError(f"unknown dependency ids, no edge created: {missing}")
        return nid

    def replace(self, node_id: str, node: dict, depends_on: Iterable[str] = ()) -> str:
        """Overwrite an existing node (statement/proof/status/…) and its out-edges."""
        if self.get(node_id) is None:
            raise ValueError(f"node {node_id!r} does not exist")
        vec = node.get("embedding")
        if vec is None:
            vec = embed(f"{node['title']}. {node['statement']}")
        blob = np.asarray(vec, dtype=np.float32).tobytes()
        self.conn.execute(
            """UPDATE nodes SET kind=?, title=?, statement=?, proof=?, status=?,
               confidence=?, embedding=?, source=? WHERE id=?""",
            (
                node.get("kind", "theorem"),
                node["title"],
                node["statement"],
                node.get("proof"),
                node.get("status", "verified"),
                float(node.get("confidence", config.CONFIDENCE_USER)),
                blob,
                node.get("source", "user"),
                node_id,
            ),
        )
        self.conn.execute("DELETE FROM edges WHERE from_id = ?", (node_id,))
        for dep in depends_on:
            if self.get(dep) is None:
                continue
            self.conn.execute(
                "INSERT OR IGNORE INTO edges (from_id, to_id) VALUES (?, ?)",
                (node_id, dep),
            )
        self.conn.commit()
        return node_id

    def delete(self, node_id: str) -> None:
        self.conn.execute("DELETE FROM nodes WHERE id = ?", (node_id,))
        self.conn.execute("DELETE FROM edges WHERE from_id = ? OR to_id = ?", (node_id, node_id))
        self.conn.commit()

    def consolidate(self, cluster_ids: Sequence[str], replacement_id: str) -> dict:
        """Archive a cluster and redirect its edges to `replacement_id`.

        The replacement must already exist and be verified. Originals are kept
        with status='archived' for provenance; retrieval never returns them.
        Returns a small report (archived ids, redirected edges, skipped cycles).
        """
        cluster_ids = list(dict.fromkeys(cluster_ids))
        if not cluster_ids:
            raise ValueError("cluster_ids must not be empty")
        if replacement_id in cluster_ids:
            raise ValueError("replacement must not be one of the archived nodes")

        cluster: list[Node] = []
        for cid in cluster_ids:
            node = self.get(cid)
            if node is None:
                raise ValueError(f"unknown node {cid!r}")
            if node.status not in ("seed", "verified"):
                raise ValueError(
                    f"node {cid!r} has status {node.status!r}; "
                    "only seed/verified nodes can be consolidated"
                )
            cluster.append(node)

        replacement = self.get(replacement_id)
        if replacement is None:
            raise ValueError(f"unknown replacement node {replacement_id!r}")
        if replacement.status in ("staged", "archived"):
            raise ValueError(
                f"replacement {replacement_id!r} is {replacement.status}; verify it first"
            )

        report = {"archived": [], "redirected": 0, "dependencies": 0, "skipped_cycles": 0}
        cluster_set = set(cluster_ids)

        # 1. The general node inherits the cluster's external dependencies.
        for node in cluster:
            for dep in self.dependencies(node.id):
                if dep.id in cluster_set:
                    continue
                if self._depends_on(dep.id, replacement_id):
                    report["skipped_cycles"] += 1
                    continue
                cur = self.conn.execute(
                    "INSERT OR IGNORE INTO edges (from_id, to_id) VALUES (?, ?)",
                    (replacement_id, dep.id),
                )
                report["dependencies"] += cur.rowcount

        # 2. Edges that pointed at an archived node now point at the general one.
        placeholders = ",".join("?" for _ in cluster_ids)
        inbound = self.conn.execute(
            f"SELECT DISTINCT from_id FROM edges WHERE to_id IN ({placeholders})",
            cluster_ids,
        ).fetchall()
        for row in inbound:
            from_id = row["from_id"]
            if from_id in cluster_set:
                continue
            if self._depends_on(replacement_id, from_id):
                report["skipped_cycles"] += 1
                continue
            cur = self.conn.execute(
                "INSERT OR IGNORE INTO edges (from_id, to_id) VALUES (?, ?)",
                (from_id, replacement_id),
            )
            report["redirected"] += cur.rowcount

        # 3. Archive the originals. Keep their edges for provenance.
        for node in cluster:
            self.conn.execute(
                "UPDATE nodes SET status = 'archived' WHERE id = ?", (node.id,)
            )
            report["archived"].append(node.id)

        self.conn.commit()
        return report

    def _depends_on(self, start: str, target: str) -> bool:
        """True if `start` depends transitively on `target` (following out-edges)."""
        if start == target:
            return True
        seen = {start}
        stack = [start]
        while stack:
            cur = stack.pop()
            rows = self.conn.execute(
                """SELECT e.to_id FROM edges e JOIN nodes n ON n.id = e.to_id
                   WHERE e.from_id = ? AND n.status != 'archived'""",
                (cur,),
            ).fetchall()
            for row in rows:
                nxt = row["to_id"]
                if nxt == target:
                    return True
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        return False

    # ------------------------------------------------------------------- read
    def get(self, node_id: str) -> Node | None:
        row = self.conn.execute("SELECT * FROM nodes WHERE id = ?", (node_id,)).fetchone()
        return _row_to_node(row) if row else None

    def all_nodes(self, status: str | None = None) -> list[Node]:
        if status is None:
            rows = self.conn.execute("SELECT * FROM nodes ORDER BY id").fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM nodes WHERE status = ? ORDER BY id", (status,)
            ).fetchall()
        return [_row_to_node(r) for r in rows]

    def embedding_map(self) -> dict[str, np.ndarray]:
        """id -> embedding for active (not staged/archived) nodes."""
        rows = self.conn.execute(
            "SELECT id, embedding FROM nodes "
            "WHERE status NOT IN ('staged', 'archived') AND embedding IS NOT NULL"
        ).fetchall()
        return {
            r["id"]: np.frombuffer(r["embedding"], dtype=np.float32) for r in rows
        }

    def dependencies(self, node_id: str) -> list[Node]:
        """Direct out-neighbours: what `node_id` is proved using."""
        rows = self.conn.execute(
            """SELECT n.* FROM edges e JOIN nodes n ON n.id = e.to_id
               WHERE e.from_id = ? AND n.status NOT IN ('staged', 'archived')
               ORDER BY e.rowid""",
            (node_id,),
        ).fetchall()
        return [_row_to_node(r) for r in rows]

    def unique_id(self, base: str) -> str:
        """base, base-2, base-3, … first one not already taken."""
        candidate = base
        i = 2
        while self.get(candidate) is not None:
            candidate = f"{base}-{i}"
            i += 1
        return candidate

    # -------------------------------------------------------------- retrieval
    def retrieve(self, query: str, k: int = config.RETRIEVE_K) -> list[Node]:
        """Top-k by cosine similarity. Staged and archived nodes never surface."""
        rows = self.conn.execute(
            "SELECT * FROM nodes WHERE status NOT IN ('staged', 'archived') "
            "AND embedding IS NOT NULL"
        ).fetchall()
        if not rows:
            return []
        blobs = [np.frombuffer(r["embedding"], dtype=np.float32) for r in rows]
        q = embed(query).astype(np.float32)
        dim = max(max(b.shape[0] for b in blobs), q.shape[0])
        mat = np.zeros((len(blobs), dim), dtype=np.float32)
        for i, b in enumerate(blobs):
            mat[i, : b.shape[0]] = b
        if q.shape[0] < dim:
            q = np.pad(q, (0, dim - q.shape[0]))
        sims = _normalize(mat) @ (q / (np.linalg.norm(q) or 1.0))
        order = np.argsort(-sims)[: max(0, k)]
        return [_row_to_node(rows[i], float(sims[i])) for i in order]

    def expand(self, nodes: Sequence[Node], cap: int | None = None) -> list[Node]:
        """Add 1 hop of dependencies, dedupe, keep order, cap the total."""
        cap = config.EXPAND_CAP if cap is None else cap
        out: list[Node] = []
        seen: set[str] = set()
        for node in nodes:
            if node.id not in seen:
                out.append(node)
                seen.add(node.id)
            if len(out) >= cap:
                return out
        for node in list(out):
            for dep in self.dependencies(node.id):
                if dep.id not in seen:
                    out.append(dep)
                    seen.add(dep.id)
                if len(out) >= cap:
                    return out
        return out

    def find_duplicate(
        self, statement: str, threshold: float = config.DUPLICATE_THRESHOLD, title: str | None = None
    ) -> Node | None:
        """Return the most similar existing node if it looks like a duplicate.

        Two independent triggers: an exact (normalized) statement match, or
        cosine similarity >= threshold between embeddings.
        """
        rows = self.conn.execute(
            "SELECT * FROM nodes WHERE status NOT IN ('staged', 'archived') "
            "AND embedding IS NOT NULL"
        ).fetchall()
        if not rows:
            return None
        target = _norm_text(statement)
        for r in rows:
            if _norm_text(r["statement"]) == target:
                return _row_to_node(r, 1.0)
        blobs = [np.frombuffer(r["embedding"], dtype=np.float32) for r in rows]
        q = embed(f"{title}. {statement}" if title else statement).astype(np.float32)
        dim = max(max(b.shape[0] for b in blobs), q.shape[0])
        mat = np.zeros((len(blobs), dim), dtype=np.float32)
        for i, b in enumerate(blobs):
            mat[i, : b.shape[0]] = b
        if q.shape[0] < dim:
            q = np.pad(q, (0, dim - q.shape[0]))
        sims = _normalize(mat) @ (q / (np.linalg.norm(q) or 1.0))
        idx = int(np.argmax(sims))
        if float(sims[idx]) >= threshold:
            return _row_to_node(rows[idx], float(sims[idx]))
        return None

    # ------------------------------------------------------------------ stats
    def counts(self) -> dict:
        by_status = {
            row["status"]: row["n"]
            for row in self.conn.execute(
                "SELECT status, COUNT(*) AS n FROM nodes GROUP BY status"
            )
        }
        n_edges = self.conn.execute("SELECT COUNT(*) AS n FROM edges").fetchone()["n"]
        total = sum(by_status.values())
        return {"total": total, "by_status": by_status, "edges": n_edges}

    def close(self) -> None:
        self.conn.close()
