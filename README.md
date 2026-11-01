# linalg_solver — a linear algebra agent with a structured memory

A small CLI agent. A local 7B model (Ollama) reasons. A SQLite memory supplies
the context. When the user gives or approves a proof, it is saved for later.

No frameworks, no vector DB, no web UI: one Python package, one SQLite file,
one local LLM.

## Layout

```
linalg_solver/
  config.py                  model names, k, thresholds, paths (nothing hardcoded elsewhere)
  llm.py                     chat(messages) -> str  (Ollama HTTP)
  embed.py                   embed(text) -> np.ndarray  (Ollama embeddings)
  memory.py                  Memory: nodes + edges schema, add/retrieve/expand/find_duplicate
  consolidate.py             cluster near-duplicates, propose a general rule, MDL check, archive
  agent.py                   solve(), prove_and_stage(), teach_and_stage(), the save gate
  render.py                  to_plain_math(): any leftover LaTeX -> readable Unicode
  cli.py                     REPL: solve / /prove / /teach / /consolidate / /save / /discard / /memory / /stats
  seed/linear_algebra.jsonl  52 seed results (definitions, theorems, lemmas, examples)
  scripts/load_seed.py       embeds + inserts the seed
  eval/problems.jsonl        10 test problems
  eval/run_eval.py           with-memory vs no-memory comparison
  tests/test_render.py       plain-math tests (no backslash, no dollar sign)
  tests/test_consolidate.py  consolidation tests (fake embeddings, no Ollama needed)
memory.db                    the memory (created on first use, kept out of the package)
```

## Setup

Requirements: a running Ollama with a chat model and an embedding model.

```bash
ollama pull qwen2.5:7b          # chat model   (config.CHAT_MODEL)
ollama pull nomic-embed-text    # embed model  (config.EMBED_MODEL)

# python environment (uv makes this painless; plain venv works too)
uv venv --python 3.12 .venv
uv pip install --python .venv numpy requests pylatexenc
```

On this machine the venv lives in `~/.venvs/memory_ai` and `.venv` is a
symlink to it (keeps Python off the slow `/mnt/c` filesystem).

### Ollama on Windows + WSL note

This project runs inside WSL but Ollama runs on the Windows host. Ollama was
configured to listen on all interfaces:

```
setx OLLAMA_HOST 0.0.0.0     # once, then restart the Ollama app
```

`config.py` auto-detects the server: it tries `OLLAMA_BASE_URL`, then
`http://localhost:11434`, then the WSL default gateway (the Windows host,
e.g. `http://192.168.48.1:11434`). If the IP ever changes, nothing breaks —
detection is dynamic. You can always force one with
`export OLLAMA_BASE_URL=http://192.168.48.1:11434`.

## Use

```bash
.venv/bin/python -m linalg_solver.scripts.load_seed   # one-time: embed + insert the seed
.venv/bin/python -m linalg_solver.cli                 # start the REPL
```

```
> What is the rank of [[1, 2], [2, 4]]?
> /prove Eigenvectors of distinct eigenvalues are linearly independent
> /teach For A = [[a, b], [c, d]] with ad - bc != 0, A^(-1) = 1/(ad - bc) [[d, -b], [-c, a]]
        :: Let D = ad - bc. Multiplying A by [[d, -b], [-c, a]] gives D I, so dividing by D
           gives the identity; hence the displayed matrix is the inverse.
> /consolidate  # find near-duplicates and propose one general rule (waits for /save)
> /save      # commits the pending item as verified (runs the duplicate check first)
> /discard   # or throw it away
> /memory eigenvalue
> /stats
```

**The human gate:** nothing the model writes is stored until you type `/save`.
Pending items live in RAM only. On `/save`, a near-duplicate (cosine similarity
>= `DUPLICATE_THRESHOLD`, or an exactly matching statement) is shown and you
choose `replace / keep both / cancel`.

**Consolidation:** teach two or three specific cases of the same idea, then
`/consolidate`. The pass clusters them by embedding (complete linkage, threshold
`CONSOLIDATION_THRESHOLD` = 0.90), asks the model for one general statement, and
scores the replacement with a simplified MDL criterion: it is accepted only if
the general rule is shorter than the cases it replaces. Nothing is written until
`/save`; on save the originals are archived (kept for provenance, never
retrieved) and edges that pointed at them are redirected to the general node.
`/stats` shows the archived count.

**Plain math only:** every answer and proof is plain readable text — Unicode
symbols (ℝ, ∈, ≤, →, ∑, √, ‖v‖, Aᵀ, λ₁, f⁻¹, ...), never LaTeX. The prompts ask
for it, and `render.py` converts anything that still slips through (its own
scanner for bare LaTeX, `pylatexenc` for `$...$` math) before the text is printed
and before it can be saved — memory content can never contain a backslash or a
`$`. The seed ships in plain math too. Check it any time:

```bash
.venv/bin/python -m linalg_solver.tests.test_render
```

There is no `/delete` command in v1, but removing a bad node is one line:

```bash
.venv/bin/python -c "from linalg_solver.memory import Memory; Memory().delete('node-id')"
```

## Evaluation

```bash
.venv/bin/python -m linalg_solver.eval.run_eval --tag baseline
# ... teach the agent a few results with /teach ... then re-run and compare:
.venv/bin/python -m linalg_solver.eval.run_eval --tag taught --compare baseline.json
```

Each problem runs twice (with memory context / with an empty context): the
table reports correctness, tokens and latency for both. Results are written to
`linalg_solver/eval/results/<tag>.json` including the full answers for manual
re-grading.

## Performance on this machine

CPU-only inference on an i7-1260P gives about **5.5 tok/s generation** and
~20 tok/s prompt prefill with `qwen2.5:7b` (Q4_K_M); thread/batch tuning barely
moved it. The defaults are chosen accordingly:

- `NUM_CTX = 2048` — the context is 5–8 short results, so nothing bigger is needed;
- `MAX_TOKENS = 768` — a hard cap so a run-away answer cannot cost 10 minutes;
- `KEEP_ALIVE = "30m"` — the model stays loaded between calls (~10 s saved per call);
- the prompts ask for short answers (a few sentences).

Expect roughly 30–120 s per answer, and ~30 min for one full eval run
(10 problems x 2 modes).

## Design notes (v1)

- Node kinds: `definition`, `theorem`, `lemma`, `example`; statuses: `seed`,
  `staged`, `verified`, `archived`. Retrieval never returns `staged` or
  `archived` nodes.
- Edges mean "`from_id` is proved using / depends on `to_id`" — one relation type.
- Retrieval: cosine similarity, top-5, then one hop of dependencies, capped at 8
  nodes (`expand`).
- Duplicate detection (`find_duplicate`) has two triggers: an exact normalized
  statement match, or cosine similarity >= `DUPLICATE_THRESHOLD`. The threshold
  is 0.88, tuned for `nomic-embed-text` on this seed: identical statements with
  different titles score ~0.86–1.0 while merely related results top out at
  ~0.88. Over-prompting is fine (the user decides); silently duplicating is not.
- Consolidation (`consolidate.py`) is human-gated: cluster verified nodes by
  complete-linkage cosine similarity, ask the model for one general statement,
  accept it only if a simplified MDL score decreases, then archive the
  originals and redirect their edges on `/save`. The accepted node is verified;
  the archive is kept for provenance and is never retrieved.
- Explicitly out of scope for v1: multi-hop traversal, typed edges,
  feedback-based confidence, symbolic verification, multi-agent, web UI.
