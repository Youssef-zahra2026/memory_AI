"""Embeddings via the Ollama embedding endpoint."""

from __future__ import annotations

import numpy as np
import requests

from . import config

_BATCH = 16


def embed_batch(texts: list[str]) -> np.ndarray:
    """Embed several texts. Returns float32 array of shape (len(texts), dim)."""
    if not texts:
        return np.zeros((0, 0), dtype=np.float32)
    out: list[list[float]] = []
    url = config.base_url() + "/api/embed"
    for i in range(0, len(texts), _BATCH):
        chunk = [t if t and t.strip() else "(empty)" for t in texts[i : i + _BATCH]]
        try:
            resp = requests.post(
                url,
                json={"model": config.EMBED_MODEL, "input": chunk},
                timeout=(10, config.REQUEST_TIMEOUT),
            )
        except requests.RequestException as exc:
            raise RuntimeError(f"Cannot reach Ollama at {config.base_url()}: {exc}") from exc
        if resp.status_code != 200:
            hint = ""
            if resp.status_code == 404:
                hint = f" (is the embedding model pulled? try: ollama pull {config.EMBED_MODEL})"
            raise RuntimeError(f"Embedding failed HTTP {resp.status_code}{hint}: {resp.text[:300]}")
        data = resp.json()
        embs = data.get("embeddings")
        if embs is None and "embedding" in data:  # older API shape
            embs = [data["embedding"]]
        if embs is None:
            raise RuntimeError(f"Unexpected embedding response: {str(data)[:300]}")
        out.extend(embs)
    return np.asarray(out, dtype=np.float32)


def embed(text: str) -> np.ndarray:
    """embed(text) -> np.ndarray (float32, 1-D)."""
    return embed_batch([text])[0]
