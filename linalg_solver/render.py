"""Plain-math rendering: turn any leftover LaTeX in text into readable Unicode.

The model is instructed to never emit LaTeX, but old outputs, user input and
model slips still contain it. to_plain_math() is applied to every LLM output
before it is printed and before anything is written to memory, and the result
is guaranteed to contain no backslash and no dollar sign.

Strategy, in order:
  1. normalize math delimiters (\\( \\[ into $ forms) and a few constructs that
     pylatexenc mishandles (\\|, ^\\perp, \\operatorname, \\det ...);
  2. convert matrix-like environments to bracketed rows;
  3. send only the *math segments* to pylatexenc (never raw prose: it treats
     '%' as a comment and would swallow the rest of a sentence);
  4. run a small scanner over everything else (Greek letters, symbols,
     sub/superscripts, \\frac, \\sqrt, stray commands);
  5. scrub: drop any remaining backslash or dollar sign.
"""

from __future__ import annotations

import re

try:  # optional but installed by default in this project
    from pylatexenc.latex2text import LatexNodes2Text

    _L2T = LatexNodes2Text()
except Exception:  # pragma: no cover - fallback to the replacement table only
    _L2T = None

# ---------------------------------------------------------------- symbol tables

_GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε",
    "varepsilon": "ε", "zeta": "ζ", "eta": "η", "theta": "θ", "vartheta": "ϑ",
    "iota": "ι", "kappa": "κ", "lambda": "λ", "mu": "μ", "nu": "ν", "xi": "ξ",
    "pi": "π", "rho": "ρ", "sigma": "σ", "tau": "τ", "upsilon": "υ", "phi": "φ",
    "varphi": "φ", "chi": "χ", "psi": "ψ", "omega": "ω",
    "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ", "Xi": "Ξ",
    "Pi": "Π", "Sigma": "Σ", "Upsilon": "Υ", "Phi": "Φ", "Psi": "Ψ", "Omega": "Ω",
}

_SYMBOLS = {
    "in": "∈", "notin": "∉", "subset": "⊂", "subseteq": "⊆", "supset": "⊃",
    "supseteq": "⊇", "cup": "∪", "cap": "∩", "le": "≤", "leq": "≤", "ge": "≥",
    "geq": "≥", "neq": "≠", "ne": "≠", "to": "→", "rightarrow": "→",
    "longrightarrow": "→", "Rightarrow": "⇒", "implies": "⇒",
    "Leftrightarrow": "⇔", "leftrightarrow": "↔", "mapsto": "↦", "forall": "∀",
    "exists": "∃", "nexists": "∄", "sum": "∑", "prod": "∏", "int": "∫",
    "iint": "∬", "oint": "∮", "partial": "∂", "nabla": "∇", "cdot": "·",
    "times": "×", "div": "÷", "pm": "±", "mp": "∓", "infty": "∞",
    "emptyset": "∅", "varnothing": "∅", "perp": "⊥", "oplus": "⊕",
    "otimes": "⊗", "approx": "≈", "equiv": "≡", "sim": "∼", "simeq": "≅",
    "cong": "≅", "angle": "∠", "circ": "∘", "bullet": "•", "ldots": "…",
    "cdots": "⋯", "dots": "…", "vdots": "⋮", "ddots": "⋱", "prime": "′",
    "ast": "∗", "star": "⋆", "wedge": "∧", "vee": "∨", "land": "∧", "lor": "∨",
    "neg": "¬", "lnot": "¬", "top": "⊤", "bot": "⊥", "square": "□",
    "mid": "∣", "nmid": "∤", "parallel": "∥", "hbar": "ℏ", "ell": "ℓ",
    "Re": "ℜ", "Im": "ℑ", "aleph": "ℵ", "checkmark": "✓",
}

_WORDS = {
    "det": "det", "dim": "dim", "ker": "ker", "tr": "tr", "trace": "tr",
    "rank": "rank", "nullity": "nullity", "im": "im", "img": "im", "span": "span",
    "gcd": "gcd", "lcm": "lcm", "max": "max", "min": "min", "sup": "sup",
    "inf": "inf", "lim": "lim", "log": "log", "ln": "ln", "lg": "lg", "exp": "exp",
    "sin": "sin", "cos": "cos", "tan": "tan", "cot": "cot", "sec": "sec",
    "csc": "csc", "arcsin": "arcsin", "arccos": "arccos", "arctan": "arctan",
    "arg": "arg", "deg": "deg", "mod": "mod", "bmod": "mod", "diag": "diag",
    "adj": "adj", "Hom": "Hom", "End": "End", "Mat": "Mat", "GL": "GL",
    "SL": "SL", "SO": "SO", "SU": "SU",
}

_BLACKBOARD = {
    "R": "ℝ", "N": "ℕ", "Z": "ℤ", "Q": "ℚ", "C": "ℂ", "K": "𝕂",
    "F": "𝔽", "P": "ℙ", "H": "ℍ", "E": "𝔼",
}

_SUP = {
    "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵", "6": "⁶",
    "7": "⁷", "8": "⁸", "9": "⁹", "+": "⁺", "-": "⁻", "=": "⁼", "(": "⁽",
    ")": "⁾", "n": "ⁿ", "i": "ⁱ", "j": "ʲ", "k": "ᵏ", "m": "ᵐ", "r": "ʳ",
    "s": "ˢ", "t": "ᵗ", "T": "ᵀ", "a": "ᵃ", "e": "ᵉ", "o": "ᵒ", "x": "ˣ",
}

_SUB = {
    "0": "₀", "1": "₁", "2": "₂", "3": "₃", "4": "₄", "5": "₅", "6": "₆",
    "7": "₇", "8": "₈", "9": "₉", "+": "₊", "-": "₋", "=": "₌", "(": "₍",
    ")": "₎", "a": "ₐ", "e": "ₑ", "h": "ₕ", "i": "ᵢ", "j": "ⱼ", "k": "ₖ",
    "l": "ₗ", "m": "ₘ", "n": "ₙ", "o": "ₒ", "p": "ₚ", "r": "ᵣ", "s": "ₛ",
    "t": "ₜ", "u": "ᵤ", "v": "ᵥ", "x": "ₓ",
}

# constructs to fix up before pylatexenc, which loses or mangles them
_PRE_LITERAL = [
    (r"^{\perp}", "⊥"),
    (r"^\perp", "⊥"),
    (r"\|", "‖"),
    (r"\lVert", "‖"),
    (r"\rVert", "‖"),
    (r"\quad", "  "),
    (r"\qquad", "    "),
]

_PRE_REGEX = [
    (r"\\operatorname\s*\{([^{}]*)\}", r"\1"),
    (r"\\det(?![a-zA-Z])", "det"),
    (r"\\dim(?![a-zA-Z])", "dim"),
    (r"\\ker(?![a-zA-Z])", "ker"),
    (r"\\nullity(?![a-zA-Z])", "nullity"),
    (r"\\gcd(?![a-zA-Z])", "gcd"),
    (r"\\rank(?![a-zA-Z])", "rank"),
    (r"\\tr(?![a-zA-Z])", "tr"),
    (r"\\prod(?![a-zA-Z])", "∏"),
]

_MATH_DISPLAY = re.compile(r"\$\$(.+?)\$\$", re.S)
_MATH_INLINE = re.compile(r"\$([^$]+)\$", re.S)
_ENV = re.compile(
    r"\\begin\{(?P<kind>[a-zA-Z]*(?:matrix|array|tabular))\}(?P<body>.*?)\\end\{(?P=kind)\}",
    re.S,
)


def _read_group(text: str, start: int) -> tuple[str, int]:
    """text[start] == '{'; return (inner, index after the closing brace)."""
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : i], i + 1
    return text[start + 1 :], len(text)  # unbalanced: take the rest


def _to_scripts(chars: str, table: dict, wrap: str) -> str:
    if not chars:
        return ""
    converted = "".join(table.get(c, "") for c in chars)
    if len(converted) == len(chars):
        return converted
    return f"{wrap}{chars})"


def _read_parens(text: str, start: int) -> int:
    """text[start] == '('; return the index just after the matching ')'."""
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return i + 1
    return len(text)


def _apply_command(name: str, args: list[str]) -> str:
    scanned = [_scan(a) for a in args]
    if name in _WORDS:
        return _WORDS[name]
    if name in _GREEK:
        return _GREEK[name]
    if name in _SYMBOLS:
        return _SYMBOLS[name]
    if name in ("text", "mathrm", "mathbf", "mathit", "mathsf", "mbox", "mathrmS"):
        return scanned[0] if scanned else ""
    if name == "mathbb":
        inner = scanned[0] if scanned else ""
        return _BLACKBOARD.get(inner, inner)
    if name == "mathcal":
        return scanned[0] if scanned else ""
    if name in ("frac", "dfrac", "tfrac"):
        if len(scanned) >= 2:
            return f"({scanned[0]})/({scanned[1]})"
        return scanned[0] if scanned else ""
    if name == "sqrt":
        if scanned:
            inner = scanned[0]
            return "√(" + inner + ")"
        return "√"
    if name in ("left", "right", "big", "Big", "bigg", "Bigg", "bigl", "bigr"):
        return scanned[0] if scanned else ""
    if name in ("begin", "end"):
        return ""
    if name in ("overline", "bar"):
        return scanned[0] + "\u0305" if scanned else ""
    if name == "hat":
        return scanned[0] + "\u0302" if scanned else ""
    if name in ("vec", "overrightarrow"):
        return scanned[0] + "\u20d7" if scanned else ""
    if name in ("hspace", "vspace", "hskip", "phantom"):
        return " "
    # unknown command: keep its arguments, drop the name
    return " ".join(scanned) if scanned else ""


def _scan(text: str) -> str:
    """Left-to-right pass: commands, ^ and _ scripts, stray dollars."""
    out: list[str] = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == "\\":
            m = re.match(r"\\([a-zA-Z]+)\s?", text[i:])
            if m:
                name = m.group(1)
                i += len(m.group(0))
                args: list[str] = []
                while len(args) < 3 and i < n and text[i] == "{":
                    arg, i = _read_group(text, i)
                    args.append(arg)
                out.append(_apply_command(name, args))
                continue
            if i + 1 < n:
                nxt = text[i + 1]
                if nxt == "\\":
                    out.append("\n")
                    i += 2
                    continue
                if nxt in "%&#_${}":
                    out.append(nxt)
                    i += 2
                    continue
                if nxt in ",;:! ":
                    out.append(" ")
                    i += 2
                    continue
            i += 1  # lone backslash: drop
            continue
        if c in "^_":
            table, wrap = (_SUP, "^(") if c == "^" else (_SUB, "_(")
            if i + 1 < n and text[i + 1] == "{":
                arg, i = _read_group(text, i + 1)
                out.append(_to_scripts(arg, table, wrap))
            elif i + 1 < n and text[i + 1] == "(":
                j = _read_parens(text, i + 1)
                out.append(c + text[i + 1 : j])  # already plain: ^(n-1)
                i = j
            elif i + 1 < n:
                m = re.match(r"[0-9A-Za-z+\-]+", text[i + 1 :])
                if m:
                    out.append(_to_scripts(m.group(0), table, wrap))
                    i += 1 + len(m.group(0))
                else:
                    i += 1
            else:
                i += 1
            continue
        if c == "$":
            i += 1  # stray delimiter
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _convert_envs(text: str) -> str:
    """\\begin{bmatrix} a & b \\\\ c & d \\end{bmatrix} -> [[a, b], [c, d]]"""

    def repl(m: re.Match) -> str:
        kind = m.group("kind") or ""
        body = m.group("body")
        rows = []
        for raw_row in re.split(r"\\\\", body):
            cells = [c.strip() for c in raw_row.split("&")]
            if any(cells):
                rows.append(cells)
        inner = ", ".join("[" + ", ".join(r) + "]" for r in rows)
        if kind.startswith("p") or kind.startswith("v") or kind.startswith("V"):
            return "(" + inner + ")" if kind.startswith("p") else "[" + inner + "]"
        return "[" + inner + "]"

    return _ENV.sub(repl, text)


def _render_math(segment: str) -> str:
    """Convert one math segment; pylatexenc when possible, scanner otherwise."""
    result: str | None = None
    if _L2T is not None:
        try:
            result = _L2T.latex_to_text(segment)
        except Exception:
            result = None
    if result is None:
        result = segment
    return _scan(result)


def _scrub(text: str) -> str:
    t = text
    t = re.sub(r"√\(([0-9A-Za-z])\)", r"√\1", t)  # √(2) -> √2
    # (1)/(2) -> 1/2, but keep parentheses around compound denominators
    t = re.sub(r"\(\s*([0-9A-Za-z√]{1,6})\s*\)/\(\s*([0-9A-Za-z√]{1,6})\s*\)", r"\1/\2", t)
    t = t.replace("$", "")
    t = re.sub(r"\\[a-zA-Z]+\*?", "", t)  # any remaining command name
    t = t.replace("\\", "")  # any remaining lone backslash
    # breathing room after relation symbols
    t = re.sub(
        r"([∈∉⊂⊆⊃⊇≤≥≠≈≡⇒⇔↦→←↔∣∥∪∩⊕⊗])"
        r"(?=[0-9A-Za-z∀∃(√\u0370-\u03FF\u2100-\u214F\u1D400-\u1D7FF])",
        r"\1 ",
        t,
    )
    t = re.sub(r"[ \t]{2,}", " ", t)
    t = re.sub(r" +([,;)])", r"\1", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return "\n".join(ln.rstrip() for ln in t.splitlines()).strip()


def to_plain_math(text: str) -> str:
    """Return `text` as readable plain math: no backslash, no dollar sign."""
    if not text:
        return text
    t = text
    # 1. delimiter normalization and pre-fixes
    t = t.replace(r"\[", "$$").replace(r"\]", "$$").replace(r"\(", "$").replace(r"\)", "$")
    for lit, rep in _PRE_LITERAL:
        t = t.replace(lit, rep)
    for pat, rep in _PRE_REGEX:
        t = re.sub(pat, rep, t)
    t = _convert_envs(t)
    # 2. math segments through pylatexenc (never raw prose: '%' would eat it)
    t = _MATH_DISPLAY.sub(lambda m: _render_math(m.group(1)), t)
    t = _MATH_INLINE.sub(lambda m: _render_math(m.group(1)), t)
    # 3. everything else through the scanner, 4. final scrub
    t = _scan(t)
    return _scrub(t)


class PlainStream:
    """Streaming callback that prints model output as plain math, line by line.

    Wire it as ``on_token`` in the CLI: tokens are buffered until a full line is
    available, converted with :func:`to_plain_math`, and printed. Call
    ``flush()`` once generation finished to emit the trailing partial line.
    """

    def __init__(self, write=None):
        self._write = write if write is not None else (lambda s: print(s, flush=True))
        self._buf = ""

    def __call__(self, token: str) -> None:
        self._buf += token
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            self._write(to_plain_math(line))

    def flush(self) -> None:
        rest, self._buf = self._buf, ""
        if rest:
            self._write(to_plain_math(rest))


if __name__ == "__main__":  # tiny demo: python -m linalg_solver.render
    demo = r"$A = \begin{bmatrix} 1 & 2 \\ 2 & 4 \end{bmatrix}$, $\|v\| = \sqrt{2}$, $\lambda_1 \neq \mu$"
    print(to_plain_math(demo))
