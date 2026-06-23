"""Filesystem anchors for the harness package's vendored assets.

Centralised here so the asset/vendor locations are computed from the package
*directory* rather than counting ``Path(__file__).parents[N]`` hops in each
module -- the hop counts shift whenever a file moves, the package anchor does not.
"""

from __future__ import annotations

from pathlib import Path

import open_afps

#: Directory of this ``harness`` package; the vendored agent assets live under it.
_HARNESS_DIR = Path(__file__).parent
_ASSETS = _HARNESS_DIR / "assets"
_SCRIPTS = _ASSETS / "scripts"
_SKILLS = _ASSETS / "skills"
_MCP_JSON = _ASSETS / "configs" / "mcp.json"
#: Vibe-specific assets: the vendored stand-in agent profile (lean scaffold on a
#: non-Labs model) copied into the sandbox's per-workdir VIBE_HOME/agents.
_VIBE_ASSETS = _ASSETS / "vibe"

#: Root of the ``open_afps`` package, used to locate the vendored Numina bundle.
_OPEN_AFPS_DIR = Path(open_afps.__file__).parent


def _vendor_numina_dir() -> Path:
    """Locate the vendored Numina bundle in both wheel and source layouts."""
    candidates = [
        # Built wheel: force-included at open_afps/vendor/numina (see pyproject).
        _OPEN_AFPS_DIR / "vendor" / "numina",
        # Source checkout / editable install: vendor/ at the repo root.
        _OPEN_AFPS_DIR.parent.parent / "vendor" / "numina",
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[0]
