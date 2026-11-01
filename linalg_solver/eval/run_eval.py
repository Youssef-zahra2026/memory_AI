"""Evaluation harness: run every problem with memory and with empty context.

Usage:
    python -m linalg_solver.eval.run_eval --tag baseline
    python -m linalg_solver.eval.run_eval --tag taught --compare results/baseline.json

Correctness is a reference match: every regex in the problem's "match" list
must be found in the model answer (case-insensitive). Full answers are saved
to eval/results/<tag>.json so a human can re-grade manually.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

if __package__ in (None, ""):  # allow: python linalg_solver/eval/run_eval.py
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from linalg_solver import config  # noqa: E402
from linalg_solver.agent import Agent  # noqa: E402
from linalg_solver.memory import Memory  # noqa: E402


def grade(problem: dict, answer: str) -> tuple[int, list[str]]:
    """1 if every match regex is found in the answer, else 0 (+ missing ones)."""
    missing = [
        pat
        for pat in problem.get("match", [])
        if not re.search(pat, answer, re.IGNORECASE | re.DOTALL)
    ]
    return (0 if missing else 1), missing


def run_mode(agent: Agent, problem: dict, use_memory: bool) -> dict:
    answer = agent.solve(problem["problem"], use_memory=use_memory)
    ok, missing = grade(problem, answer.text)
    return {
        "correct": ok,
        "missing": missing,
        "answer": answer.text,
        "context_ids": [n.id for n in answer.context_nodes],
        "used_ids": answer.used_ids,
        "prompt_tokens": answer.prompt_tokens,
        "completion_tokens": answer.completion_tokens,
        "seconds": round(answer.seconds, 2),
    }


def load_problems(path: Path) -> list[dict]:
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def summary(rows: dict) -> dict:
    def col(name: str) -> list[float]:
        return [r[name]["correct"] for r in rows.values()]

    def mean(vals: list[float]) -> float:
        return sum(vals) / len(vals) if vals else 0.0

    return {
        "n": len(rows),
        "correct_memory": int(sum(col("memory"))),
        "correct_nomem": int(sum(col("nomem"))),
        "tokens_memory": round(mean([r["memory"]["prompt_tokens"] + r["memory"]["completion_tokens"] for r in rows.values()]), 1),
        "tokens_nomem": round(mean([r["nomem"]["prompt_tokens"] + r["nomem"]["completion_tokens"] for r in rows.values()]), 1),
        "seconds_memory": round(mean([r["memory"]["seconds"] for r in rows.values()]), 1),
        "seconds_nomem": round(mean([r["nomem"]["seconds"] for r in rows.values()]), 1),
    }


def print_tables(rows: dict, summ: dict) -> None:
    head = f"{'problem':<26} {'mem':>4} {'nomem':>6} {'mem_tok':>8} {'nomem_tok':>10} {'mem_s':>7} {'nomem_s':>8}"
    print(head)
    print("-" * len(head))
    for pid, r in rows.items():
        mem, no = r["memory"], r["nomem"]
        print(
            f"{pid:<26} {mem['correct']:>4} {no['correct']:>6} "
            f"{mem['prompt_tokens'] + mem['completion_tokens']:>8} "
            f"{no['prompt_tokens'] + no['completion_tokens']:>10} "
            f"{mem['seconds']:>7.1f} {no['seconds']:>8.1f}"
        )
    print("-" * len(head))
    print(
        f"correct: memory {summ['correct_memory']}/{summ['n']} vs "
        f"no-memory {summ['correct_nomem']}/{summ['n']}   "
        f"avg tokens: {summ['tokens_memory']} vs {summ['tokens_nomem']}   "
        f"avg s: {summ['seconds_memory']} vs {summ['seconds_nomem']}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", default="run", help="name for this run (file eval/results/<tag>.json)")
    parser.add_argument("--db", default=None, help="memory db path (default: config.DB_PATH)")
    parser.add_argument("--problems", default=None, help="problems jsonl path")
    parser.add_argument("--compare", default=None, help="previous results json to compare with")
    args = parser.parse_args(argv)

    problems_path = Path(args.problems) if args.problems else config.PROBLEMS_PATH
    problems = load_problems(problems_path)
    memory = Memory(args.db)
    agent = Agent(memory)
    stats = memory.counts()

    print(f"eval tag={args.tag}  model={config.CHAT_MODEL}  problems={len(problems)}")
    print(f"memory: {memory.path} — {stats['total']} nodes, {stats['edges']} edges")

    t0 = time.perf_counter()
    rows: dict[str, dict] = {}
    for p in problems:
        rows[p["id"]] = {
            "memory": run_mode(agent, p, use_memory=True),
            "nomem": run_mode(agent, p, use_memory=False),
        }
        r = rows[p["id"]]
        print(
            f"  {p['id']:<26} mem={'OK' if r['memory']['correct'] else '--'} "
            f"nomem={'OK' if r['nomem']['correct'] else '--'} "
            f"({r['memory']['seconds']:.0f}s + {r['nomem']['seconds']:.0f}s)",
            flush=True,
        )
    summ = summary(rows)
    total_seconds = time.perf_counter() - t0

    print()
    print_tables(rows, summ)

    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = config.RESULTS_DIR / f"{args.tag}.json"
    out_path.write_text(
        json.dumps(
            {
                "tag": args.tag,
                "model": config.CHAT_MODEL,
                "embed_model": config.EMBED_MODEL,
                "db": str(memory.path),
                "memory_stats": stats,
                "summary": summ,
                "total_seconds": round(total_seconds, 1),
                "rows": rows,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    memory.close()
    print(f"\nwrote {out_path}  ({total_seconds:.0f}s total)")

    if args.compare:
        requested = Path(args.compare)
        prev_path = next(
            (p for p in (requested, config.RESULTS_DIR / requested.name) if p.exists()), None
        )
        if prev_path is None:
            print(f"\ncompare file not found: {args.compare}")
            return 1
        prev = json.loads(prev_path.read_text(encoding="utf-8"))
        ps = prev["summary"]
        print()
        print(f"compare with {prev_path} (tag={prev.get('tag')}):")
        print(
            f"  correct: memory {ps['correct_memory']} -> {summ['correct_memory']}, "
            f"no-memory {ps['correct_nomem']} -> {summ['correct_nomem']}"
        )
        print(
            f"  avg tokens: memory {ps['tokens_memory']} -> {summ['tokens_memory']}, "
            f"no-memory {ps['tokens_nomem']} -> {summ['tokens_nomem']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
