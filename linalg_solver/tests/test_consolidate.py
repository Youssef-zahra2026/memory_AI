"""Tests for the consolidation pass.

Run with any of:
    python -m linalg_solver.tests.test_consolidate
    pytest linalg_solver/tests/test_consolidate.py

No Ollama is needed: embeddings and the chat call are replaced by fakes.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import numpy as np

import linalg_solver.memory as memory_module
from linalg_solver.consolidate import (
    build_generalization,
    description_length,
    find_clusters,
)
from linalg_solver.memory import Memory


def fake_embed(text: str) -> np.ndarray:
    """Deterministic embeddings: three near-duplicates, and orthogonal noise."""
    t = text.lower()
    if t.startswith("case one"):
        return np.array([1.0, 0.0, 0.0], dtype=np.float32)
    if t.startswith("case two"):
        return np.array([0.99, 0.05, 0.0], dtype=np.float32)
    if t.startswith("case three"):
        return np.array([0.98, 0.10, 0.0], dtype=np.float32)
    if t.startswith("existing general"):
        return np.array([0.995, 0.02, 0.0], dtype=np.float32)
    if t.startswith("general rank rule"):
        return np.array([0.5, 0.0, 0.866], dtype=np.float32)
    if t.startswith("uses case one"):
        return np.array([0.0, 0.7071, 0.7071], dtype=np.float32)
    if t.startswith("external"):
        return np.array([0.0, 1.0, 0.0], dtype=np.float32)
    return np.array([0.0, 0.0, 1.0], dtype=np.float32)


def fake_chat(messages) -> str:
    return (
        "TITLE: general rank rule\n"
        "STATEMENT: If the columns of a matrix are proportional then its rank is 1.\n"
        "PROOF: The columns span a one-dimensional space."
    )


def long_chat(messages) -> str:
    return (
        "TITLE: " + "long " * 80 + "\n"
        "STATEMENT: " + "word " * 200 + "\n"
        "PROOF: " + "proof " * 80
    )


def _build_memory(tmp: Path) -> Memory:
    mem = Memory(tmp / "memory.db")
    mem.add(
        {"id": "external", "kind": "definition", "title": "external fact",
         "statement": "a fact the cases depend on"},
    )
    mem.add(
        {"id": "case-1", "kind": "example", "title": "case one",
         "statement": "the rank of matrix A is 1",
         "proof": "the second column is twice the first"},
        depends_on=["external"],
    )
    mem.add(
        {"id": "case-2", "kind": "example", "title": "case two",
         "statement": "the rank of matrix B is 1",
         "proof": "the rows are proportional"},
        depends_on=["external"],
    )
    mem.add(
        {"id": "case-3", "kind": "example", "title": "case three",
         "statement": "the rank of matrix C is 1",
         "proof": "one column is a multiple of the other"},
        depends_on=["external"],
    )
    mem.add(
        {"id": "unrelated", "kind": "theorem", "title": "unrelated result",
         "statement": "a result that has nothing to do with rank"},
    )
    mem.add(
        {"id": "user", "kind": "theorem", "title": "uses case one",
         "statement": "a result that cites the first case"},
        depends_on=["case-1"],
    )
    return mem


def _with_fake_embed(fn):
    """Run a test with the Ollama embedding call replaced by a fake."""

    def wrapper(*args, **kwargs):
        old = memory_module.embed
        memory_module.embed = fake_embed
        try:
            return fn(*args, **kwargs)
        finally:
            memory_module.embed = old

    wrapper.__name__ = fn.__name__
    return wrapper


@_with_fake_embed
def test_find_clusters() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        mem = _build_memory(Path(tmp))
        clusters = find_clusters(mem, threshold=0.9)
        assert len(clusters) == 1, clusters
        assert clusters[0].size == 3, clusters[0].ids
        assert set(clusters[0].ids) == {"case-1", "case-2", "case-3"}
        assert clusters[0].similarity > 0.99
        mem.close()


@_with_fake_embed
def test_no_cluster_above_threshold() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        mem = _build_memory(Path(tmp))
        clusters = find_clusters(mem, threshold=0.99999)
        assert clusters == [], clusters
        mem.close()


@_with_fake_embed
def test_generalization_is_accepted_by_mdl() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        mem = _build_memory(Path(tmp))
        cluster = find_clusters(mem, threshold=0.9)[0]
        gen = build_generalization(mem, cluster, chat=fake_chat, check_duplicate=False)
        assert gen.accepted, (gen.j_before, gen.j_after)
        assert set(gen.cluster_ids) == {"case-1", "case-2", "case-3"}
        assert "external" in gen.used_ids
        assert gen.existing_id is None
        # A very long general statement must be rejected: no compression.
        long = build_generalization(mem, cluster, chat=long_chat, check_duplicate=False)
        assert not long.accepted, (long.j_before, long.j_after)
        mem.close()


@_with_fake_embed
def test_consolidation_archives_and_redirects() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        mem = _build_memory(Path(tmp))
        cluster = find_clusters(mem, threshold=0.9)[0]
        gen = build_generalization(mem, cluster, chat=fake_chat, check_duplicate=False)

        mem.add(
            {"id": "general-rank", "kind": "theorem", "title": "general rank rule",
             "statement": gen.statement, "proof": gen.proof, "status": "verified"},
            depends_on=gen.used_ids,
        )
        report = mem.consolidate(gen.cluster_ids, "general-rank")

        assert sorted(report["archived"]) == ["case-1", "case-2", "case-3"]
        for cid in ("case-1", "case-2", "case-3"):
            assert mem.get(cid).status == "archived"

        # The general node inherited the cluster's external dependency.
        assert "external" in [n.id for n in mem.dependencies("general-rank")]

        # A node that cited a specific case now cites the general rule.
        assert "general-rank" in [n.id for n in mem.dependencies("user")]

        # Archived nodes never surface in retrieval.
        retrieved = {n.id for n in mem.retrieve("case one", k=10)}
        assert not ({"case-1", "case-2", "case-3"} & retrieved), retrieved

        # The active node count dropped; archived nodes are still on disk.
        stats = mem.counts()
        assert stats["by_status"]["archived"] == 3
        mem.close()


@_with_fake_embed
def test_description_length() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        mem = _build_memory(Path(tmp))
        node = mem.get("case-1")
        assert description_length(node) > 0
        mem.close()


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in tests:
        fn()
        print(f"  ok  {fn.__name__}")
    print(f"{len(tests)} tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
