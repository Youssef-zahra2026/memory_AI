"""Consolidation: replace a cluster of near-duplicate nodes by one general node.

The pass is deliberately small and human-gated, in the spirit of the paper:

  1. cluster verified nodes by embedding similarity (complete linkage);
  2. ask the LLM to induce one general statement from the cluster;
  3. score the replacement with a simplified MDL criterion;
  4. stage it -- nothing is written until the user types /save.

On commit the originals are archived (never deleted), edges that pointed at
them are redirected to the general node, and the general node inherits the
cluster's external dependencies. Retrieval never returns archived nodes, so
the active memory really does get smaller.
"""

from __future__ import annotations

import itertools
import re
from dataclasses import dataclass

import numpy as np

from . import config, llm
from .memory import Memory, Node
from .render import to_plain_math

# --------------------------------------------------------------------------- data


@dataclass
class Cluster:
    """A set of near-duplicate nodes, tight under complete linkage."""

    nodes: list[Node]
    similarity: float  # minimum pairwise cosine similarity in the cluster

    @property
    def ids(self) -> list[str]:
        return [n.id for n in self.nodes]

    @property
    def size(self) -> int:
        return len(self.nodes)


@dataclass
class Generalization:
    """The proposed replacement for a cluster."""

    title: str
    statement: str
    proof: str
    used_ids: list[str]
    cluster_ids: list[str]
    j_before: int
    j_after: int
    existing_id: str | None = None  # set when an existing node already subsumes it
    note: str = ""

    @property
    def accepted(self) -> bool:
        """The MDL test: the replacement must make J(M) smaller."""
        return self.j_after < self.j_before


# ------------------------------------------------------------------------ scoring


def _tokens(text: str | None) -> int:
    if not text:
        return 0
    return len(text.split())


def description_length(node: Node) -> int:
    """Cheap stand-in for the description length l(x | M) in the paper.

    Tokens needed to state the node: title + statement + proof. It is not a
    true MDL code length, but it is measurable, deterministic, and enough to
    reject replacements that are longer than what they replace.
    """
    return _tokens(node.title) + _tokens(node.statement) + _tokens(node.proof)


def _general_description_length(title: str, statement: str, proof: str) -> int:
    return _tokens(title) + _tokens(statement) + _tokens(proof)


# ---------------------------------------------------------------------- clustering


def _normalize(mat: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return mat / norms


def find_clusters(
    memory: Memory,
    threshold: float | None = None,
    min_size: int | None = None,
    max_size: int | None = None,
) -> list[Cluster]:
    """Find tight clusters of near-duplicate verified nodes.

    Greedy complete linkage: a node joins a cluster only if it is at least
    `threshold` similar to *every* member. That avoids the chaining problem
    where A~B and B~C drags A and C into one cluster. Clusters are returned
    largest first, then tightest first.
    """
    threshold = config.CONSOLIDATION_THRESHOLD if threshold is None else threshold
    min_size = config.CONSOLIDATION_MIN_CLUSTER if min_size is None else min_size
    max_size = config.CONSOLIDATION_MAX_CLUSTER if max_size is None else max_size

    embeddings = memory.embedding_map()
    nodes = {n.id: n for n in memory.all_nodes() if n.id in embeddings}
    ids = list(embeddings)
    if len(ids) < min_size:
        return []

    mat = _normalize(np.stack([embeddings[i] for i in ids]).astype(np.float32))
    sim = mat @ mat.T

    pairs = [
        (float(sim[i, j]), i, j)
        for i in range(len(ids))
        for j in range(i + 1, len(ids))
        if float(sim[i, j]) >= threshold
    ]
    pairs.sort(key=lambda t: -t[0])

    assigned: dict[int, int] = {}
    clusters: list[list[int]] = []

    for _score, i, j in pairs:
        ci, cj = assigned.get(i), assigned.get(j)
        if ci is None and cj is None:
            clusters.append([i, j])
            assigned[i] = assigned[j] = len(clusters) - 1
        elif ci is not None and cj is None:
            members = clusters[ci]
            if len(members) < max_size and all(sim[j, k] >= threshold for k in members):
                members.append(j)
                assigned[j] = ci
        elif cj is not None and ci is None:
            members = clusters[cj]
            if len(members) < max_size and all(sim[i, k] >= threshold for k in members):
                members.append(i)
                assigned[i] = cj
        # both already assigned: either same cluster or a chained pair; skip

    out: list[Cluster] = []
    for members in clusters:
        if len(members) < min_size:
            continue
        idx = sorted(members)
        min_sim = min(float(sim[a, b]) for a, b in itertools.combinations(idx, 2))
        out.append(
            Cluster(nodes=[nodes[ids[k]] for k in idx], similarity=min_sim)
        )

    out.sort(key=lambda c: (-c.size, -c.similarity))
    return out


# --------------------------------------------------------------- generalisation

_SYSTEM = """\
You are a linear algebra expert. Below are several stored results that express
the same underlying idea at different levels of specificity. Write ONE general
statement that subsumes all of them, plus a one-sentence justification.

Rules:
- The statement must be true for every listed case.
- Keep the statement under 30 words.
- Keep the proof to one sentence.
- Reply with exactly three lines, no preamble:
TITLE: <short title>
STATEMENT: <general statement>
PROOF: <one-sentence justification>
"""

_LINE_RE = {
    "title": re.compile(r"^\s*TITLE\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE),
    "statement": re.compile(r"^\s*STATEMENT\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE),
    "proof": re.compile(r"^\s*PROOF\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE),
}


def _cluster_prompt(cluster: Cluster) -> str:
    lines = []
    for i, n in enumerate(cluster.nodes, 1):
        proof = f" Proof: {n.proof}" if n.proof else ""
        lines.append(f"[{i}] {n.title}: {n.statement}.{proof}")
    return "\n".join(lines)


def generalize(cluster: Cluster, chat=None) -> tuple[str, str, str]:
    """Ask the model for one general statement covering the cluster."""
    chat = chat or llm.chat
    raw = chat(
        [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": _cluster_prompt(cluster)},
        ]
    )
    text = to_plain_math(raw)  # memory content is always plain math
    found: dict[str, str] = {}
    for key, pattern in _LINE_RE.items():
        match = pattern.search(text)
        if match:
            found[key] = match.group(1).strip()
    missing = [k for k in ("title", "statement", "proof") if not found.get(k)]
    if missing:
        raise ValueError(
            f"could not parse the generalisation (missing {', '.join(missing)}); "
            f"model said: {raw[:300]!r}"
        )
    return found["title"], found["statement"], found["proof"]


# ---------------------------------------------------------------------- proposal


def build_generalization(
    memory: Memory,
    cluster: Cluster,
    *,
    chat=None,
    check_duplicate: bool = True,
) -> Generalization:
    """Stage-ready proposal for replacing `cluster` with one general node."""
    title, statement, proof = generalize(cluster, chat=chat)

    cluster_set = set(cluster.ids)
    used_ids: list[str] = []
    for node in cluster.nodes:
        for dep in memory.dependencies(node.id):
            if dep.id not in cluster_set and dep.id not in used_ids:
                used_ids.append(dep.id)

    j_before = config.CONSOLIDATION_NODE_COST * cluster.size + sum(
        description_length(n) for n in cluster.nodes
    )

    existing = None
    if check_duplicate:
        existing = memory.find_duplicate(
            statement, threshold=config.CONSOLIDATION_DUPLICATE_THRESHOLD
        )
        if existing is not None and existing.id in cluster_set:
            existing = None

    if existing is not None:
        # The general rule already exists: archive the specifics into it
        # instead of adding a duplicate node.
        j_after = 0
        return Generalization(
            title=existing.title,
            statement=existing.statement,
            proof=existing.proof or "",
            used_ids=[d.id for d in memory.dependencies(existing.id)],
            cluster_ids=cluster.ids,
            j_before=j_before,
            j_after=j_after,
            existing_id=existing.id,
            note=f"existing node {existing.id!r} already subsumes the cluster",
        )

    j_after = config.CONSOLIDATION_NODE_COST + _general_description_length(
        title, statement, proof
    )
    return Generalization(
        title=title,
        statement=statement,
        proof=proof,
        used_ids=used_ids,
        cluster_ids=cluster.ids,
        j_before=j_before,
        j_after=j_after,
    )
