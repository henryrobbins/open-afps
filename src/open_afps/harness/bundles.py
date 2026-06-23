"""Selectable asset bundles mounted into the agent workdir.

A bundle names the skills (and optional default prompt / extra prompt trees) that
get copied into the sandbox; the active bundle is chosen by
``AgentProverConfig.assets``.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from open_afps.harness._paths import _SKILLS, _vendor_numina_dir


@dataclass(frozen=True)
class AssetBundle:
    """A selectable set of agent assets mounted into the workdir.

    Attributes
    ----------
    name:
        Bundle identifier matching ``AgentProverConfig.assets``.
    skills_dir:
        Directory whose contents become the agent's skills (copied into the
        harness's skills location, e.g. ``.claude/skills``).
    prompt_file:
        Optional default system prompt for the bundle, used when the task carries
        no explicit ``instructions``.
    extra_dirs:
        Additional ``(src_dir, dest_relative_to_workdir)`` trees to copy in (e.g.
        Numina's coordinator/subagent prompts under ``.claude/prompts``).
    """

    name: str
    skills_dir: Path
    prompt_file: Path | None = None
    extra_dirs: tuple[tuple[Path, str], ...] = ()

    def default_prompt(self) -> str | None:
        if self.prompt_file is not None and self.prompt_file.is_file():
            return self.prompt_file.read_text()
        return None


#: The built-in bundle: the generic ``filling-sorrys`` skill, no default prompt.
DEFAULT_BUNDLE = AssetBundle(name="default", skills_dir=_SKILLS)


def _numina_bundle() -> AssetBundle:
    root = _vendor_numina_dir()
    return AssetBundle(
        name="numina",
        skills_dir=root / "skills",
        prompt_file=root / "prompts" / "main_entry.md",
        # The coordinator prompt tells the agent to read its subagent prompts from
        # .claude/prompts/subagent_prompts/, so stage the whole prompt tree there.
        extra_dirs=((root / "prompts", ".claude/prompts"),),
    )


#: Asset-bundle registry selected by ``AgentProverConfig.assets``.
BUNDLES: dict[str, Callable[[], AssetBundle]] = {
    "default": lambda: DEFAULT_BUNDLE,
    "numina": _numina_bundle,
}


def resolve_bundle(name: str) -> AssetBundle:
    """Resolve an ``assets`` name to its :class:`AssetBundle`."""
    try:
        return BUNDLES[name]()
    except KeyError:
        raise ValueError(
            f"unknown asset bundle {name!r}; known: {sorted(BUNDLES)}"
        ) from None
