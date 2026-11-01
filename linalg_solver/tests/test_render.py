"""Tests for linalg_solver.render.to_plain_math.

Run with any of:
    python -m linalg_solver.tests.test_render
    pytest linalg_solver/tests/test_render.py

The core requirement: the output of to_plain_math must contain no backslash
and no dollar sign, for anything the model or a user might produce.
"""

from __future__ import annotations

import json
import pathlib
import sys

from linalg_solver import config
from linalg_solver.render import to_plain_math

CASES = [
    # -- inline and display math --------------------------------------------
    r"Compute $A = \begin{bmatrix} 1 & 2 \\ 2 & 4 \end{bmatrix}$.",
    r"\[ \frac{1}{\sqrt{2}} (1, 1) \]",
    r"The determinant is \(\det A = 2 \cdot 4 - 1 \cdot 7 = 1\).",
    r"\(\lambda \in \mathbb{R}\), \(v \in \mathbb{R}^n\)",
    r"\(\sum_{i=1}^{n} \lambda_i = \operatorname{tr} A\)",
    r"\(\|v\| = \sqrt{\langle v, v \rangle}\), \(v \perp w\)",
    r"\(A^T A = I\) and \(P^{-1} A P\), \(f^{-1}\), \(v_1, v_2, \ldots, v_n\)",
    r"\(x \le y \ge z \neq 0\), \(x \to \infty\), \(X \Rightarrow Y\)",
    r"\(\forall \varepsilon > 0 \; \exists \delta > 0\)",
    # -- bare LaTeX with no delimiters --------------------------------------
    r"Use \frac{a}{b} and \sqrt{2} and \mathbb{N} here.",
    r"\begin{pmatrix} a & b \\ c & d \end{pmatrix} \cdot x",
    r"A_ij, B^{n-1}, x^2 over bare text without math mode",
    # -- mixed prose ---------------------------------------------------------
    "The rank is 1, since 100% of the rows are proportional.",
    "No math at all in this sentence; this must survive unchanged.",
    r"Claim: if \(f\) is injective then \(\ker f = \{0\}\). Therefore dim V ≤ dim W.",
    # -- old-model artifacts (real answers seen in this project) -------------
    r"The unit vector is \(\frac{1}{\sqrt{2}}(1, 1) = \left(\frac{1}{\sqrt{2}}, \frac{1}{\sqrt{2}}\right)\).",
    r"USED: rank-nullity, dimension" + "\n" + r"\( \dim V = \dim \ker f + \dim \operatorname{im} f \)",
]


def _assert_plain(text: str, label: str) -> str:
    out = to_plain_math(text)
    assert "\\" not in out, f"backslash survived in {label}: {out!r}"
    assert "$" not in out, f"dollar sign survived in {label}: {out!r}"
    return out


def test_no_backslash_no_dollar() -> None:
    for i, case in enumerate(CASES):
        _assert_plain(case, f"case {i}")


def test_expected_symbols() -> None:
    out = to_plain_math(r"$x \in \mathbb{R}^n$, $\|v\|$, $\sqrt{2}$, $\lambda_1$, $A^T$, $f^{-1}$, $\le$")
    assert "∈" in out and "ℝ" in out
    assert "‖v‖" in out
    assert "√2" in out
    assert "λ₁" in out
    assert "Aᵀ" in out
    assert "f⁻¹" in out
    assert "≤" in out
    assert "ⁿ" in out


def test_matrix_env() -> None:
    out = to_plain_math(r"$A = \begin{bmatrix} 1 & 2 \\ 2 & 4 \end{bmatrix}$")
    assert out == "A = [[1, 2], [2, 4]]", out


def test_prose_passthrough() -> None:
    prose = "The rank is 1, since 100% of the rows are proportional."
    assert to_plain_math(prose) == prose


def test_scripts() -> None:
    assert to_plain_math("A_ij") == "Aᵢⱼ"
    assert to_plain_math("x^2 + v_1") == "x² + v₁"
    assert to_plain_math("P^{-1}") == "P⁻¹"


def test_seed_file_is_plain() -> None:
    path = pathlib.Path(config.SEED_PATH)
    if not path.exists():  # pragma: no cover
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        entry = json.loads(line)
        for field in ("title", "statement", "proof"):
            value = entry.get(field)
            if value:
                out = _assert_plain(value, f"{entry['id']}.{field}")
                assert out == value, f"seed {entry['id']}.{field} is not already plain: {value!r}"


def test_already_plain_is_stable() -> None:
    for case in CASES:
        once = to_plain_math(case)
        twice = to_plain_math(once)
        assert once == twice, f"to_plain_math is not idempotent on: {case!r}"


def test_plain_stream() -> None:
    from linalg_solver.render import PlainStream

    out: list[str] = []
    stream = PlainStream(write=out.append)
    for token in [r"$A = \begin{bmatrix} 1 & 2 \\ 2 & 4 \end{bmatrix}$", "\n", "x_", "1 = 0", "\n", r"\(\|v\| = \sqrt{2}\)"]:
        stream(token)
    stream.flush()
    text = "\n".join(out)
    assert "\\" not in text and "$" not in text, text
    assert "[[1, 2], [2, 4]]" in text, text
    assert "x₁ = 0" in text, text
    assert "‖v‖ = √2" in text, text


def main() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in tests:
        fn()
        print(f"  ok  {fn.__name__}")
    print(f"{len(tests)} tests passed, {len(CASES)} cases checked for \\ and $")
    return 0


if __name__ == "__main__":
    sys.exit(main())
