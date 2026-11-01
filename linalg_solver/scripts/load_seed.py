"""Load the seed knowledge base into memory.db (embeddings + nodes + edges).

Usage:
    python -m linalg_solver.scripts.load_seed            # add missing seed nodes
    python -m linalg_solver.scripts.load_seed --reset    # wipe seed nodes, reload
    python -m linalg_solver.scripts.load_seed --db other.db
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

if __package__ in (None, ""):  # allow: python linalg_solver/scripts/load_seed.py
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from linalg_solver import config  # noqa: E402
from linalg_solver.embed import embed_batch  # noqa: E402
from linalg_solver.memory import Memory  # noqa: E402
from linalg_solver.render import to_plain_math  # noqa: E402


def load_seed(seed_path: Path, memory: Memory, reset: bool = False) -> dict:
    lines = [ln for ln in seed_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    entries = [json.loads(ln) for ln in lines]
    for e in entries:  # seed content is stored as plain readable math, never LaTeX
        e["title"] = to_plain_math(e["title"])
        e["statement"] = to_plain_math(e["statement"])
        if e.get("proof"):
            e["proof"] = to_plain_math(e["proof"])

    ids = [e["id"] for e in entries]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate ids in seed file")
    known = {n.id for n in memory.all_nodes()} | set(ids)
    unknown_deps = [
        (e["id"], d) for e in entries for d in e.get("depends_on", []) if d not in known
    ]
    if unknown_deps:
        raise ValueError(f"seed depends_on unknown ids: {unknown_deps}")

    if reset and ids:
        # Remove the seed's own results and outgoing edges, but keep edges that
        # user-taught nodes point at seed ids: seed ids are stable, so those
        # edges become valid again as soon as the seed nodes are re-inserted.
        qmarks = ",".join("?" * len(ids))
        with memory.conn:
            memory.conn.execute(f"DELETE FROM edges WHERE from_id IN ({qmarks})", ids)
            memory.conn.execute(f"DELETE FROM nodes WHERE id IN ({qmarks})", ids)

    existing = {n.id for n in memory.all_nodes()}
    todo = [e for e in entries if e["id"] not in existing]
    skipped = len(entries) - len(todo)
    if todo:
        texts = [f"{e['title']}. {e['statement']}" for e in todo]
        t0 = time.perf_counter()
        vectors = embed_batch(texts)
        embed_seconds = time.perf_counter() - t0
        for e, vec in zip(todo, vectors):
            memory.add(
                {
                    "id": e["id"],
                    "kind": e["kind"],
                    "title": e["title"],
                    "statement": e["statement"],
                    "proof": e.get("proof"),
                    "status": "seed",
                    "confidence": config.CONFIDENCE_SEED,
                    "embedding": vec,
                    "source": "seed",
                },
                depends_on=e.get("depends_on", []),
            )
    else:
        embed_seconds = 0.0
    # never leave edges pointing at nodes that no longer exist
    with memory.conn:
        memory.conn.execute(
            "DELETE FROM edges WHERE to_id NOT IN (SELECT id FROM nodes)"
        )
    return {
        "total": len(entries),
        "loaded": len(todo),
        "skipped": skipped,
        "embed_seconds": embed_seconds,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default=None, help="path to the SQLite memory file")
    parser.add_argument("--seed", default=None, help="path to the seed jsonl")
    parser.add_argument("--reset", action="store_true", help="delete seed nodes first")
    args = parser.parse_args(argv)

    seed_path = Path(args.seed) if args.seed else config.SEED_PATH
    memory = Memory(args.db)
    t0 = time.perf_counter()
    info = load_seed(seed_path, memory, reset=args.reset)
    elapsed = time.perf_counter() - t0
    stats = memory.counts()
    memory.close()

    print(
        f"seed: {info['loaded']} loaded, {info['skipped']} already present "
        f"({info['total']} in file), {info['embed_seconds']:.1f}s embedding"
    )
    print(
        f"memory now holds {stats['total']} nodes "
        f"({', '.join(f'{k}={v}' for k, v in sorted(stats['by_status'].items()))}) "
        f"and {stats['edges']} edges — total {elapsed:.1f}s"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
