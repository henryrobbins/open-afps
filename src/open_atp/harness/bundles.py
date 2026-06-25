"""Vendored agent assets and the selectable :class:`AssetBundle` preset.

Two kinds of asset are resolvable **by name** (from a vendored catalog) or **by full
path**, via :func:`resolve_skill` / :func:`resolve_plugin`:

* **skills** -- host-agnostic Agent Skills (``<name>/SKILL.md``) listed on
  ``AgentProverConfig.skills`` and copied by the :class:`~...AgentProver` into each
  harness's skill location (``.claude/skills``, ``.agents/skills``,
  ``VIBE_HOME/skills``). The default is ``lean-proof`` from the vendored
  ``leanprover/skills`` catalog.
* **plugins** -- Claude Code plugins (a dir with ``.claude-plugin/plugin.json``)
  listed on ``ClaudeCodeHarnessConfig.plugins`` and loaded **only** by the Claude
  harness via ``--plugin-dir`` (no other harness supports plugins). The default is
  the vendored ``lean4`` plugin.

A named :class:`AssetBundle` packages the *remaining* preset pieces that aren't a
simple list -- ``extra_dirs`` and the legacy ``skills_dir`` whole-directory mount
(both Numina-only today); :func:`resolve_bundle` resolves it from ``config.assets``.
Skills, plugins, and the prompt are **not** bundle concerns: skills/plugins are owned
by the config (resolved here, copied by the prover/Claude harness) and the prompt by
the prover and task (see :func:`~open_atp.provers.base.compose_prompt`).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from open_atp.harness._paths import (
    _vendor_lean4_skills_dir,
    _vendor_leanprover_skills_dir,
    _vendor_numina_dir,
)

#: Directories searched when a skill is named rather than given as a path: the
#: vendored ``leanprover/skills`` catalog (``lean-proof``, ``lean-setup``, ...).
_SKILL_CATALOGS: tuple[Path, ...] = (_vendor_leanprover_skills_dir() / "skills",)

#: Directories searched when a plugin is named rather than given as a path: the
#: vendored ``lean4-skills`` plugins (``lean4``).
_PLUGIN_CATALOGS: tuple[Path, ...] = (_vendor_lean4_skills_dir() / "plugins",)


def _resolve(spec: str, catalogs: tuple[Path, ...], kind: str) -> Path:
    """Resolve a ``spec`` to a directory: an existing path, else a catalog name."""
    p = Path(spec).expanduser()
    if p.is_dir():
        return p.resolve()
    for catalog in catalogs:
        candidate = catalog / spec
        if candidate.is_dir():
            return candidate
    known = sorted(
        d.name for c in catalogs if c.is_dir() for d in c.iterdir() if d.is_dir()
    )
    raise ValueError(
        f"unknown {kind} {spec!r}: not an existing directory and not found in any "
        f"catalog; known {kind}s: {known}"
    )


def resolve_skill(spec: str) -> Path:
    """Resolve a skill name (from a catalog) or a path to its source directory."""
    return _resolve(spec, _SKILL_CATALOGS, "skill")


def resolve_plugin(spec: str) -> Path:
    """Resolve a plugin name (from a catalog) or a path to its source directory."""
    return _resolve(spec, _PLUGIN_CATALOGS, "plugin")


@dataclass(frozen=True)
class AssetBundle:
    """A selectable preset of the non-list assets mounted into the workdir.

    Skills and plugins are *not* here -- they are lists on the configs
    (``AgentProverConfig.skills`` / ``ClaudeCodeHarnessConfig.plugins``). A bundle
    carries only the pieces that aren't a flat list of named assets.

    Attributes
    ----------
    name:
        Bundle identifier matching ``AgentProverConfig.assets``.
    extra_dirs:
        Additional ``(src_dir, dest_relative_to_workdir)`` trees to copy in (e.g.
        Numina's coordinator/subagent prompts under ``.claude/prompts``).
    skills_dir:
        Legacy whole-directory mount: its *contents* are copied to the harness's
        skill location root (so a top-level ``SKILL.md`` lands at ``<dest>/SKILL.md``).
        Used by the Numina bundle, which mounts one root-level skill plus helper
        subdirs (``cli/`` etc.). Ordinary skills go on ``AgentProverConfig.skills``.
    """

    name: str
    extra_dirs: tuple[tuple[Path, str], ...] = ()
    skills_dir: Path | None = None


def _default_bundle() -> AssetBundle:
    """The built-in default: an empty preset.

    The default skill (``lean-proof``) and plugin (``lean4``) are config defaults
    (``AgentProverConfig.skills`` / ``ClaudeCodeHarnessConfig.plugins``), not bundle
    contents, so the default bundle carries no ``extra_dirs`` / ``skills_dir``.
    """
    return AssetBundle(name="default")


def _numina_bundle() -> AssetBundle:
    root = _vendor_numina_dir()
    return AssetBundle(
        name="numina",
        # Numina is one root-mounted skill (top-level SKILL.md + cli/ helpers), so
        # its whole skills/ tree is copied to the skill-location root.
        skills_dir=root / "skills",
        # The coordinator prompt tells the agent to read its subagent prompts from
        # .claude/prompts/subagent_prompts/, so stage the whole prompt tree there.
        extra_dirs=((root / "prompts", ".claude/prompts"),),
    )


#: Asset-bundle registry selected by ``AgentProverConfig.assets``.
BUNDLES: dict[str, Callable[[], AssetBundle]] = {
    "default": _default_bundle,
    "numina": _numina_bundle,
}

#: Eagerly-resolved default (the common case), so callers have a ready bundle.
DEFAULT_BUNDLE = _default_bundle()


def resolve_bundle(name: str) -> AssetBundle:
    """Resolve an ``assets`` name to its :class:`AssetBundle`."""
    try:
        return BUNDLES[name]()
    except KeyError:
        raise ValueError(
            f"unknown asset bundle {name!r}; known: {sorted(BUNDLES)}"
        ) from None
