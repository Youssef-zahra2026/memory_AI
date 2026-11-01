"""Agent flows: solve(), prove_and_stage(), teach_and_stage(), save/discard.

Nothing the model writes is ever stored without an explicit /save by the user.
That is the one rule this file must never break.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable

from . import config, llm
from .consolidate import build_generalization, find_clusters
from .embed import embed  # noqa: F401  (re-exported convenience)
from .memory import Memory, Node, slugify
from .render import to_plain_math

SYSTEM_SOLVE = r"""You are a linear algebra assistant. Use ONLY the numbered context below as your
known results; if you need something not in it, say so explicitly.
Write in plain readable mathematical English. Use Unicode symbols (ℝ, ℕ, ∈, ⊂,
≤, ≥, ≠, →, ⇒, ∀, ∃, ∑, √, ‖v‖, f⁻¹, Aᵀ, v₁, v₂) and never LaTeX: no $ signs, no
backslash commands like \frac, \mathbb, \in, \sum. Structure a proof as: Claim,
then numbered steps, then "Therefore ...". Cite memory items as [n].
Solve step by step, keep the answer short (at most ~10 short lines, no preamble).
End with: USED: <comma-separated ids>

CONTEXT:
{context}"""

SYSTEM_PROVE = r"""You are a linear algebra assistant. Write a short, rigorous proof (a few
sentences) of the statement the user gives you. You may use ONLY the numbered
context below; if the proof needs a result that is not there, say so explicitly.
Write in plain readable mathematical English. Use Unicode symbols (ℝ, ℕ, ∈, ⊂,
≤, ≥, ≠, →, ⇒, ∀, ∃, ∑, √, ‖v‖, f⁻¹, Aᵀ, v₁, v₂) and never LaTeX: no $ signs, no
backslash commands like \frac, \mathbb, \in, \sum. Structure a proof as: Claim,
then numbered steps, then "Therefore ...". Cite memory items as [n] where you
use them.
Start your reply with a line "TITLE: <short title>" and end with a final line
"USED: <comma-separated ids of the context items you relied on>".

CONTEXT:
{context}"""

SYSTEM_TEACH = """\
You are a linear algebra assistant. The user gives you a statement and a proof.
Say which of the numbered context items below the proof relies on.
Reply with exactly one line: USED: <comma-separated ids or NONE>

CONTEXT:
{context}"""


@dataclass
class Answer:
    text: str
    context_nodes: list[Node]
    used_ids: list[str]
    prompt_tokens: int = 0
    completion_tokens: int = 0
    seconds: float = 0.0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@dataclass
class Pending:
    """A candidate result held in RAM, waiting for /save."""

    title: str
    statement: str
    proof: str
    used_ids: list[str] = field(default_factory=list)
    kind: str = "theorem"
    # Set when this pending item is a consolidation replacement: the ids of the
    # specific nodes that will be archived on /save.
    consolidation_ids: list[str] = field(default_factory=list)
    existing_id: str | None = None


def context_block(nodes: list[Node]) -> str:
    if not nodes:
        return "(empty — no relevant results in memory)"
    lines = [f"[{i}] [id: {n.id}] {n.title}: {n.statement}" for i, n in enumerate(nodes, 1)]
    return "\n".join(lines)


_USED_RE = re.compile(r"^\s*USED\s*:\s*(.*)$", re.IGNORECASE | re.MULTILINE)
_TITLE_RE = re.compile(r"^\s*TITLE\s*:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
_CITE_RE = re.compile(r"\[(\d+)\]")


def parse_used(text: str, context_nodes: list[Node]) -> list[str]:
    """Extract the ids the model claims to have used, filtered to the context."""
    valid = [n.id for n in context_nodes]
    by_number = {str(i): n.id for i, n in enumerate(context_nodes, 1)}
    candidates: list[str] = []

    matches = _USED_RE.findall(text)
    if matches:
        raw = matches[-1]
        for tok in re.split(r"[,\s;]+", raw):
            tok = tok.strip().strip("[]()")
            if not tok or tok.upper() == "NONE":
                continue
            if tok in by_number:  # cited "[3]" or "3"
                candidates.append(by_number[tok])
            else:
                candidates.append(tok)
    if not candidates:  # fall back to inline citations like [3]
        candidates = [by_number[m] for m in _CITE_RE.findall(text) if m in by_number]

    used: list[str] = []
    for c in candidates:
        c = c.strip()
        if c in valid and c not in used:
            used.append(c)
    return used


def strip_meta_lines(text: str) -> str:
    """Remove TITLE:/USED: lines, keep the rest (the proof/answer body)."""
    lines = [
        ln
        for ln in text.splitlines()
        if not _USED_RE.match(ln) and not _TITLE_RE.match(ln)
    ]
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines).strip()


def derive_title(statement: str, max_len: int = 60) -> str:
    """Derive a readable title (and thus id) from a statement, mechanically."""
    first = statement.strip().rstrip(".;:")
    sentence = re.split(r"(?<=[.;])\s", first, maxsplit=1)[0].strip()
    if len(sentence) >= 12:
        first = sentence
    # prefer keeping the hypothesis of an implication, else drop the math payload
    for sep in (", then ", " = ", " -> ", " :: ", ", where ", " such that "):
        if sep not in first:
            continue
        head = first.split(sep)[0].strip()
        if len(head) >= 12:
            first = head
            break
    # no dangling single letters / particles at the end
    words = first.split()
    while words and (len(words[-1]) == 1 or words[-1] in {"and", "with", "for", "of", "the"}):
        words.pop()
    first = " ".join(words) or statement.strip()
    if len(first) > max_len:
        first = first[:max_len].rsplit(" ", 1)[0] + "…"
    return first


class Agent:
    def __init__(self, memory: Memory):
        self.memory = memory
        self.pending: Pending | None = None
        self.last_report: dict | None = None

    # ------------------------------------------------------------- context
    def build_context(self, query: str, k: int | None = None) -> list[Node]:
        retrieved = self.memory.retrieve(query, k=k if k is not None else config.RETRIEVE_K)
        return self.memory.expand(retrieved)

    # --------------------------------------------------------------- solve
    def solve(
        self,
        problem: str,
        *,
        use_memory: bool = True,
        on_token: Callable[[str], None] | None = None,
    ) -> Answer:
        nodes = self.build_context(problem) if use_memory else []
        system = SYSTEM_SOLVE.format(context=context_block(nodes))
        result = llm.chat_detailed(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": problem},
            ],
            stream=on_token is not None,
            on_token=on_token,
        )
        text = to_plain_math(result.text)  # never print or store LaTeX
        used = parse_used(text, nodes)
        return Answer(
            text=text,
            context_nodes=nodes,
            used_ids=used,
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
            seconds=result.seconds,
        )

    # ------------------------------------------------------- prove / teach
    def prove_and_stage(
        self, statement: str, *, on_token: Callable[[str], None] | None = None
    ) -> tuple[Pending, Answer]:
        """/prove: the LLM writes a proof. Held in RAM until /save."""
        nodes = self.build_context(statement)
        system = SYSTEM_PROVE.format(context=context_block(nodes))
        result = llm.chat_detailed(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": f"Prove the following statement:\n{statement}"},
            ],
            stream=on_token is not None,
            on_token=on_token,
        )
        text = to_plain_math(result.text)  # never print or store LaTeX
        title_match = _TITLE_RE.search(text)
        title = (
            to_plain_math(title_match.group(1).strip())
            if title_match
            else derive_title(statement)
        )
        proof = strip_meta_lines(text)
        used = parse_used(text, nodes)
        pending = Pending(title=title, statement=statement, proof=proof, used_ids=used)
        self.pending = pending
        return pending, Answer(
            text=text,
            context_nodes=nodes,
            used_ids=used,
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
            seconds=result.seconds,
        )

    def teach_and_stage(self, statement: str, proof: str) -> tuple[Pending, list[str]]:
        """/teach: the user's proof is taken as is; the LLM only lists which
        context nodes it relies on. Held in RAM until /save."""
        statement = to_plain_math(statement)  # keep all memory content plain
        proof = to_plain_math(proof)
        nodes = self.build_context(statement + " " + proof)
        system = SYSTEM_TEACH.format(context=context_block(nodes))
        user = f"STATEMENT:\n{statement}\n\nPROOF:\n{proof}\n\nReply with one line: USED: <ids>"
        result = llm.chat_detailed(
            [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ]
        )
        used = parse_used(result.text, nodes)
        pending = Pending(
            title=derive_title(statement),
            statement=statement,
            proof=proof,
            used_ids=used,
        )
        self.pending = pending
        return pending, used

    # ---------------------------------------------------------- consolidate
    def propose_consolidation(self, threshold: float | None = None):
        """Find the best near-duplicate cluster and stage a general replacement.

        Returns (generalization, clusters). Nothing is written: the proposal is
        held in RAM until /save, exactly like /prove and /teach.
        """
        clusters = find_clusters(self.memory, threshold=threshold)
        if not clusters:
            return None, []
        cluster = clusters[0]
        gen = build_generalization(self.memory, cluster)
        if not gen.accepted:
            self.pending = None
            return gen, clusters
        self.pending = Pending(
            title=gen.title,
            statement=gen.statement,
            proof=gen.proof,
            used_ids=gen.used_ids,
            kind="theorem",
            consolidation_ids=gen.cluster_ids,
            existing_id=gen.existing_id,
        )
        return gen, clusters

    # ------------------------------------------------------------ the gate
    def check_duplicate(self, pending: Pending | None = None) -> Node | None:
        p = pending or self.pending
        if p is None:
            return None
        return self.memory.find_duplicate(
            p.statement, threshold=config.DUPLICATE_THRESHOLD, title=p.title
        )

    def commit(self, pending: Pending | None = None, replace_id: str | None = None) -> str:
        """Write the pending item to memory as verified. Only /save calls this."""
        p = pending or self.pending
        if p is None:
            raise ValueError("nothing pending")
        self.last_report = None

        # Consolidation: add (or reuse) the general node, then archive the
        # cluster and redirect its edges. The human /save is the verifier.
        if p.consolidation_ids:
            if p.existing_id is not None:
                node_id = p.existing_id
            else:
                node = {
                    "kind": p.kind,
                    "title": to_plain_math(p.title),
                    "statement": to_plain_math(p.statement),
                    "proof": to_plain_math(p.proof),
                    "status": "verified",
                    "confidence": config.CONFIDENCE_USER,
                    "source": "user",
                }
                node_id = self.memory.unique_id(slugify(p.title))
                node["id"] = node_id
                self.memory.add(node, depends_on=p.used_ids)
            self.last_report = self.memory.consolidate(p.consolidation_ids, node_id)
            self.pending = None
            return node_id

        node = {
            "kind": p.kind,
            "title": to_plain_math(p.title),
            "statement": to_plain_math(p.statement),
            "proof": to_plain_math(p.proof),
            "status": "verified",
            "confidence": config.CONFIDENCE_USER,
            "source": "user",
        }
        if replace_id is not None:
            node_id = self.memory.replace(replace_id, node, depends_on=p.used_ids)
        else:
            node_id = self.memory.unique_id(slugify(p.title))
            node["id"] = node_id
            self.memory.add(node, depends_on=p.used_ids)
        self.pending = None
        return node_id

    def discard(self) -> Pending | None:
        dropped = self.pending
        self.pending = None
        return dropped
