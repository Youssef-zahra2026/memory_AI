"""Command-line REPL: solve, prove, teach, save, discard."""

from __future__ import annotations

import argparse
import sys

from . import config
from .agent import Agent
from .llm import LLMError
from .memory import Memory
from .render import PlainStream

HELP = """\
Commands:
  <any text>                 solve it with memory context
  /prove <statement>         the LLM writes a proof using memory (waits for /save)
  /teach <stmt> :: <proof>   you provide the proof (waits for /save)
  /consolidate [t]           find near-duplicates and propose one general rule
                             (optional t = similarity threshold, default 0.90)
  /save                      commit the pending item to memory as verified
  /discard                   drop the pending item
  /memory <query>            show the top-5 retrieved nodes (debug)
  /stats                     node count by status + edge count
  /help                      this help
  /quit                      leave
"""


def _fmt_node(n) -> str:
    score = f"{n.score:.2f} " if n.score is not None else ""
    return f"  {score}{n.status:<8} {n.kind:<10} {n.id:<32} {n.title}"


class CLI:
    def __init__(self, db_path: str | None = None):
        self.memory = Memory(db_path)
        self.agent = Agent(self.memory)

    # ------------------------------------------------------------- printing
    def banner(self) -> None:
        print("Linear Algebra Solver (v1)")
        try:
            url = config.base_url()
            print(f"  model : {config.CHAT_MODEL} @ {url}")
        except RuntimeError as exc:
            print(f"  model : {config.CHAT_MODEL} (WARNING: {exc})")
        print(f"  embed : {config.EMBED_MODEL}")
        stats = self.memory.counts()
        by = ", ".join(f"{k}={v}" for k, v in sorted(stats["by_status"].items()))
        print(f"  memory: {self.memory.path} — {stats['total']} nodes ({by}), {stats['edges']} edges")
        if stats["total"] == 0:
            print("  hint  : memory is empty, load the seed:  python -m linalg_solver.scripts.load_seed")
        print("Type /help for commands.\n")

    def report_answer(self, answer) -> None:
        ids = [n.id for n in answer.context_nodes]
        print()
        print(f"[context: {', '.join(ids) if ids else '(none)'}]")
        print(f"[cited : {', '.join(answer.used_ids) if answer.used_ids else '(none)'}]")
        print(
            f"[{answer.total_tokens} tokens, {answer.seconds:.1f}s]"
        )

    # -------------------------------------------------------------- commands
    def do_solve(self, problem: str) -> None:
        stream = PlainStream()
        answer = self.agent.solve(problem, on_token=stream)
        stream.flush()
        self.report_answer(answer)

    def do_prove(self, statement: str) -> None:
        stream = PlainStream()
        pending, answer = self.agent.prove_and_stage(statement, on_token=stream)
        stream.flush()
        self.report_answer(answer)
        self.show_pending(pending)

    def do_teach(self, arg: str) -> None:
        if " :: " not in arg:
            print("usage: /teach <statement> :: <proof>")
            return
        statement, proof = arg.split(" :: ", 1)
        pending, used = self.agent.teach_and_stage(statement.strip(), proof.strip())
        print("\n--- staged (nothing saved yet) ---")
        print(f"id guess  : {pending.title}")
        print(f"statement : {pending.statement}")
        print(f"proof     : {pending.proof}")
        print(f"relies on : {', '.join(used) if used else '(none)'}")
        print("----------------------------------")

    def show_pending(self, pending) -> None:
        print("\n--- staged (nothing saved yet) ---")
        print(f"title     : {pending.title}")
        print(f"statement : {pending.statement}")
        print(f"relies on : {', '.join(pending.used_ids) if pending.used_ids else '(none)'}")
        print("Type /save to commit it to memory, or /discard to drop it.")
        print("----------------------------------")

    def do_consolidate(self, threshold: float | None = None) -> None:
        gen, clusters = self.agent.propose_consolidation(threshold=threshold)
        if gen is None:
            used = config.CONSOLIDATION_THRESHOLD if threshold is None else threshold
            print(f"no near-duplicate cluster found at threshold {used:.2f}.")
            print(
                f"Teach 2-3 specific cases first (min cluster "
                f"{config.CONSOLIDATION_MIN_CLUSTER}), or run /consolidate 0.85."
            )
            return

        cluster = clusters[0]
        print(
            f"\ncluster: {cluster.size} nodes, min pairwise similarity "
            f"{cluster.similarity:.3f}"
        )
        for n in cluster.nodes:
            print(_fmt_node(n))
        print(
            f"\nMDL: J(before)={gen.j_before}  J(after)={gen.j_after}  -> "
            f"{'accept' if gen.accepted else 'reject'}"
        )
        if not gen.accepted:
            print("the general rule is not shorter than the cases it replaces; nothing staged.")
            return
        if gen.note:
            print(f"note: {gen.note}")

        print("\n--- staged generalisation (nothing saved yet) ---")
        print(f"title     : {gen.title}")
        print(f"statement : {gen.statement}")
        print(f"proof     : {gen.proof}")
        print(f"replaces  : {', '.join(gen.cluster_ids)}")
        print(f"relies on : {', '.join(gen.used_ids) if gen.used_ids else '(none)'}")
        print("Type /save to archive the specifics and keep the general rule, or /discard.")
        print("-------------------------------------------------")

    def do_save(self) -> None:
        if self.agent.pending is None:
            print("nothing pending — use /prove, /teach or /consolidate first")
            return

        if self.agent.pending.consolidation_ids:
            node_id = self.agent.commit()
            report = self.agent.last_report or {}
            print(
                f"consolidated into {node_id!r}: archived "
                f"{len(report.get('archived', []))} nodes, redirected "
                f"{report.get('redirected', 0)} edges, inherited "
                f"{report.get('dependencies', 0)} dependencies, skipped "
                f"{report.get('skipped_cycles', 0)} cycle(s)"
            )
            return

        dup = self.agent.check_duplicate()
        replace_id = None
        if dup is not None:
            print(f"near-duplicate found (similarity {dup.score:.3f}):")
            print(_fmt_node(dup))
            print(f"  statement: {dup.statement}")
            while True:
                choice = input("replace / keep both / cancel ? ").strip().lower()
                if choice in ("replace", "r"):
                    replace_id = dup.id
                    break
                if choice in ("keep both", "keep", "k", "both"):
                    break
                if choice in ("cancel", "c", ""):
                    print("save cancelled, pending item kept")
                    return
                print("please answer replace, keep both or cancel")
        node_id = self.agent.commit(replace_id=replace_id)
        node = self.memory.get(node_id)
        print(
            f"saved {node_id!r} (status={node.status}, confidence={node.confidence}, "
            f"edges -> {', '.join(n.id for n in self.memory.dependencies(node_id)) or 'none'})"
        )

    def do_discard(self) -> None:
        dropped = self.agent.discard()
        print("discarded" if dropped else "nothing pending")

    def do_memory(self, query: str) -> None:
        nodes = self.memory.retrieve(query, k=config.RETRIEVE_K)
        if not nodes:
            print("(no nodes in memory)")
            return
        title = f"top-{len(nodes)} for {query!r}:"
        print(title)
        for n in nodes:
            print(_fmt_node(n))

    def do_stats(self) -> None:
        stats = self.memory.counts()
        print(f"nodes: {stats['total']}")
        for status, n in sorted(stats["by_status"].items()):
            print(f"  {status:<9} {n}")
        print(f"edges: {stats['edges']}")
        print(f"db   : {self.memory.path}")

    # ------------------------------------------------------------------ loop
    def repl(self) -> None:
        self.banner()
        while True:
            try:
                line = input("> ")
            except (EOFError, KeyboardInterrupt):
                print()
                break
            line = line.strip()
            if not line:
                continue
            try:
                if line in ("/quit", "/exit", "/q"):
                    break
                elif line == "/help":
                    print(HELP)
                elif line.startswith("/prove"):
                    stmt = line[len("/prove") :].strip()
                    if stmt:
                        self.do_prove(stmt)
                    else:
                        print("usage: /prove <statement>")
                elif line.startswith("/teach"):
                    self.do_teach(line[len("/teach") :].strip())
                elif line.startswith("/consolidate"):
                    arg = line[len("/consolidate") :].strip()
                    try:
                        threshold = float(arg) if arg else None
                    except ValueError:
                        print("usage: /consolidate [threshold]  e.g. /consolidate 0.85")
                        continue
                    self.do_consolidate(threshold)
                elif line == "/save":
                    self.do_save()
                elif line == "/discard":
                    self.do_discard()
                elif line.startswith("/memory"):
                    q = line[len("/memory") :].strip()
                    if q:
                        self.do_memory(q)
                    else:
                        print("usage: /memory <query>")
                elif line == "/stats":
                    self.do_stats()
                elif line.startswith("/"):
                    print(f"unknown command {line.split()[0]!r} — try /help")
                else:
                    self.do_solve(line)
            except KeyboardInterrupt:
                print("\n[interrupted]")
            except (LLMError, RuntimeError, ValueError) as exc:
                print(f"[error] {exc}")
        self.memory.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m linalg_solver.cli", description=__doc__)
    parser.add_argument("--db", default=None, help="path to the SQLite memory file")
    args = parser.parse_args(argv)
    CLI(args.db).repl()
    return 0


if __name__ == "__main__":
    sys.exit(main())
