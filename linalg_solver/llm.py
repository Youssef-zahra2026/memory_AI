"""Thin Ollama HTTP client. No framework, just requests."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Callable

import requests

from . import config


class LLMError(RuntimeError):
    """Raised when the Ollama server is unreachable or answers with an error."""


@dataclass
class ChatResult:
    text: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    seconds: float = 0.0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


def chat_detailed(
    messages: list[dict],
    *,
    stream: bool = False,
    on_token: Callable[[str], None] | None = None,
    temperature: float | None = None,
    num_ctx: int | None = None,
    model: str | None = None,
) -> ChatResult:
    """Send a chat request to Ollama and return text + token stats + latency."""
    payload = {
        "model": model or config.CHAT_MODEL,
        "messages": messages,
        "stream": bool(stream),
        "options": {
            "temperature": config.TEMPERATURE if temperature is None else temperature,
            "num_ctx": config.NUM_CTX if num_ctx is None else num_ctx,
            "num_predict": config.MAX_TOKENS,
        },
        "keep_alive": config.KEEP_ALIVE,
    }
    url = config.base_url() + "/api/chat"
    t0 = time.perf_counter()
    try:
        resp = requests.post(
            url, json=payload, stream=bool(stream), timeout=(10, config.REQUEST_TIMEOUT)
        )
    except requests.RequestException as exc:
        raise LLMError(f"Cannot reach Ollama at {config.base_url()}: {exc}") from exc

    if resp.status_code != 200:
        snippet = resp.text[:300]
        hint = ""
        if resp.status_code == 404:
            hint = f" (is the model pulled? try: ollama pull {payload['model']})"
        raise LLMError(f"Ollama HTTP {resp.status_code}{hint}: {snippet}")

    if not stream:
        data = resp.json()
        result = ChatResult(
            text=(data.get("message") or {}).get("content", ""),
            prompt_tokens=data.get("prompt_eval_count", 0) or 0,
            completion_tokens=data.get("eval_count", 0) or 0,
        )
    else:
        parts: list[str] = []
        final: dict = {}
        for raw_line in resp.iter_lines():
            if not raw_line:
                continue
            obj = json.loads(raw_line)  # bytes are decoded as UTF-8 by json
            if obj.get("error"):
                raise LLMError(f"Ollama stream error: {obj['error']}")
            chunk = (obj.get("message") or {}).get("content", "")
            if chunk:
                parts.append(chunk)
                if on_token is not None:
                    on_token(chunk)
            if obj.get("done"):
                final = obj
        result = ChatResult(
            text="".join(parts),
            prompt_tokens=final.get("prompt_eval_count", 0) or 0,
            completion_tokens=final.get("eval_count", 0) or 0,
        )
    result.seconds = time.perf_counter() - t0
    return result


def chat(messages: list[dict], **kwargs) -> str:
    """chat(messages) -> str, as promised by the spec."""
    return chat_detailed(messages, **kwargs).text
