"""Central configuration for linalg_solver.

Everything tunable lives here: model names, retrieval knobs, thresholds, paths.
The model name must never be hardcoded anywhere else.
"""

from __future__ import annotations

import os
import socket
from pathlib import Path
from urllib.parse import urlsplit

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent

# --- Models (override with env vars if needed) -------------------------------
CHAT_MODEL = os.environ.get("LINALG_MODEL", "qwen2.5:7b")
EMBED_MODEL = os.environ.get("LINALG_EMBED_MODEL", "nomic-embed-text")

# --- LLM server --------------------------------------------------------------
# Empty string -> auto-detect (env OLLAMA_BASE_URL, then localhost, then the
# WSL gateway IP which routes to an Ollama running on the Windows host).
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "").rstrip("/")
OLLAMA_PORT = int(os.environ.get("OLLAMA_PORT", "11434"))

TEMPERATURE = 0.2
NUM_CTX = 2048  # small on purpose: few context nodes, faster prefill on CPU
MAX_TOKENS = 768  # safety cap on the answer length (num_predict)
KEEP_ALIVE = "30m"  # keep the model loaded between calls
REQUEST_TIMEOUT = 600  # seconds; a 7B model on CPU can be slow

# --- Retrieval ---------------------------------------------------------------
RETRIEVE_K = 5
EXPAND_CAP = 8
# Tuned for nomic-embed-text: an identical statement with a different title
# scores ~0.86-1.0, while merely related results score up to ~0.88, so the
# embedding check sits at 0.88 and memory.find_duplicate additionally treats
# an exact (normalized) statement match as a duplicate regardless of score.
DUPLICATE_THRESHOLD = 0.88

# --- Consolidation -----------------------------------------------------------
# A cluster must be at least this similar under *complete* linkage (every pair)
# before the pass will propose replacing it with one general node.
CONSOLIDATION_THRESHOLD = 0.90
CONSOLIDATION_MIN_CLUSTER = 2
CONSOLIDATION_MAX_CLUSTER = 5
# Cost of one active node in the simplified MDL score J(M); see consolidate.py.
CONSOLIDATION_NODE_COST = 20
# If the general statement already exists above this similarity, archive the
# cluster into the existing node instead of adding a near-duplicate.
CONSOLIDATION_DUPLICATE_THRESHOLD = 0.90

# --- Confidence defaults -----------------------------------------------------
CONFIDENCE_SEED = 1.0
CONFIDENCE_USER = 0.9

# --- Paths -------------------------------------------------------------------
DB_PATH = Path(os.environ.get("LINALG_DB", PROJECT_ROOT / "memory.db"))
SEED_PATH = PACKAGE_DIR / "seed" / "linear_algebra.jsonl"
PROBLEMS_PATH = PACKAGE_DIR / "eval" / "problems.jsonl"
RESULTS_DIR = PACKAGE_DIR / "eval" / "results"


def _wsl_gateway_ip() -> str | None:
    """Default gateway of this machine (on WSL2: the Windows host) or None."""
    try:
        with open("/proc/net/route", encoding="ascii") as f:
            next(f)  # header
            for line in f:
                fields = line.split()
                # fields: Iface Destination Gateway Flags ...
                if len(fields) > 2 and fields[1] == "00000000":
                    raw = fields[2]  # little-endian hex, e.g. "0130A8C0"
                    octets = [int(raw[i : i + 2], 16) for i in range(0, 8, 2)]
                    return ".".join(str(o) for o in reversed(octets))
    except OSError:
        return None
    return None


def _port_open(host: str, port: int, timeout: float = 1.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


_resolved_base_url: str | None = None


def _candidates() -> list[str]:
    cands: list[str] = []
    if OLLAMA_BASE_URL:
        cands.append(OLLAMA_BASE_URL)
    cands.append(f"http://localhost:{OLLAMA_PORT}")
    gw = _wsl_gateway_ip()
    if gw:
        cands.append(f"http://{gw}:{OLLAMA_PORT}")
    # de-duplicate, keep order
    seen: set[str] = set()
    return [c for c in cands if not (c in seen or seen.add(c))]


def base_url(refresh: bool = False) -> str:
    """Resolve the Ollama base URL once and cache it."""
    global _resolved_base_url
    if _resolved_base_url and not refresh:
        return _resolved_base_url
    for url in _candidates():
        parts = urlsplit(url)
        if _port_open(parts.hostname or "localhost", parts.port or OLLAMA_PORT):
            _resolved_base_url = url
            return url
    tried = ", ".join(_candidates())
    raise RuntimeError(
        f"Cannot reach Ollama (tried: {tried}).\n"
        "Start it with `ollama serve`, or if it runs on the Windows host set "
        "OLLAMA_HOST=0.0.0.0 there and restart it, or point OLLAMA_BASE_URL at it."
    )


def db_path() -> Path:
    return Path(DB_PATH)
