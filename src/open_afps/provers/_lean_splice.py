"""Provider-agnostic Lean splice helpers shared by whole-proof generation provers.

A whole-proof generation prover (Kimina, and the deferred BFS path) follows the same
mechanical shape: locate each ``sorry``'d ``theorem``/``lemma``, hand the model its
formal statement, and splice the returned proof back over the ``sorry``. These two
pure helpers isolate that text surgery so it can be unit-tested in isolation and
reused across providers:

* :func:`extract_theorems` -- find each ``sorry``'d declaration and report its name,
  its formal statement (the header ending in ``by``/``:=``), and the character span
  of the **proof body** to be replaced.
* :func:`splice_proof` -- substitute a generated proof body over that span.

The parser is deliberately small and offset-preserving (it works on the raw source,
not a cleaned copy) so :func:`splice_proof` lands exactly. It assumes top-level
declarations begin at column 0 -- the normal layout for miniF2F-style statement
files -- and is bracket-aware when locating the proof delimiter so a ``:=`` inside
the signature (default args, structure literals) is not mistaken for it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

#: A top-level ``theorem``/``lemma`` opener at the start of a line. We only target
#: column-0 declarations: indented ``have ... := by`` blocks are proof-internal and
#: must not be treated as separate targets.
_DECL_RE = re.compile(r"(?m)^(theorem|lemma)\s+([A-Za-z_][\w'.]*)")

_SORRY_RE = re.compile(r"\bsorry\b")

#: Opening/closing bracket pairs tracked when scanning for the top-level ``:=``.
_OPENERS = {"(": ")", "[": "]", "{": "}"}
_CLOSERS = {")", "]", "}"}


@dataclass(frozen=True)
class Theorem:
    """One ``sorry``'d declaration located in a Lean source string.

    ``statement`` is the header up to and including the proof delimiter (``... := by``
    for tactic proofs, ``... :=`` for term proofs) -- this is what a whole-proof model
    is prompted with. ``body_span`` is the ``(start, end)`` half-open character range
    of the proof body that :func:`splice_proof` replaces; it covers everything after
    the delimiter (the leading whitespace/newline included), so a generated body that
    carries its own indentation drops in cleanly.
    """

    name: str
    statement: str
    body_span: tuple[int, int]


def _find_top_level_assign(text: str) -> int | None:
    """Index of the ``:`` in the first top-level ``:=`` in ``text``, or ``None``.

    "Top level" means outside any ``()``/``[]``/``{}`` group, so a ``:=`` appearing in
    a default argument or structure literal within the signature is skipped.
    """
    depth = 0
    for i, ch in enumerate(text):
        if ch in _OPENERS:
            depth += 1
        elif ch in _CLOSERS:
            depth -= 1
        elif ch == ":" and depth == 0 and i + 1 < len(text) and text[i + 1] == "=":
            return i
    return None


def extract_theorems(lean_text: str) -> list[Theorem]:
    """Locate every top-level ``sorry``'d ``theorem``/``lemma`` in ``lean_text``.

    Returns one :class:`Theorem` per declaration whose proof body still contains a
    ``sorry``; declarations already proved are skipped (nothing to fill).
    """
    decls = list(_DECL_RE.finditer(lean_text))
    out: list[Theorem] = []
    for i, m in enumerate(decls):
        start = m.start()
        end = decls[i + 1].start() if i + 1 < len(decls) else len(lean_text)
        block = lean_text[start:end]

        assign = _find_top_level_assign(block)
        if assign is None:
            continue
        after_assign = assign + 2  # past the ``:=``

        proof_region = block[after_assign:]
        if not _SORRY_RE.search(proof_region):
            continue  # already proved -- not a target

        # Keep ``by`` in the statement (the model is prompted with a header ending in
        # ``by``); the body to replace is everything after it.
        by = re.match(r"\s*by\b", proof_region)
        body_start_rel = after_assign + (by.end() if by else 0)

        # Trim trailing blank lines that belong to the gap before the next decl.
        body_end_rel = len(block.rstrip())

        out.append(
            Theorem(
                name=m.group(2),
                statement=block[:body_start_rel].strip(),
                body_span=(start + body_start_rel, start + body_end_rel),
            )
        )
    return out


def splice_proof(lean_text: str, body_span: tuple[int, int], proof: str) -> str:
    """Replace the proof-body span in ``lean_text`` with ``proof``.

    ``proof`` is substituted verbatim, so it should carry its own leading
    whitespace/newline to sit after the ``by`` in the surviving header.
    """
    start, end = body_span
    return lean_text[:start] + proof + lean_text[end:]
