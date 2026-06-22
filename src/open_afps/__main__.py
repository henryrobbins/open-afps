"""``open-afps`` CLI: a thin shell over :class:`~open_afps.api.Platform`.

    open-afps solve <project-dir> --provers aristotle,agent,numina [--json]

Mirrors milp_flare's arg-parsing style. The core stays a plain Python API
(:func:`open_afps.api.Platform.solve`); this is just the terminal front door.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from open_afps.api import (
    Platform,
    available_provers,
    project_from_dir,
    stage_files,
)
from open_afps.core.task import ProofTask
from open_afps.images import DEFAULT_IMAGE, DEFAULT_TOOLCHAIN


def _solve(args: argparse.Namespace) -> int:
    inputs = [Path(p) for p in args.inputs]
    if len(inputs) == 1 and inputs[0].is_dir():
        project = project_from_dir(inputs[0])
    else:
        # Bare .lean files -> stage into the pinned skeleton under the run tree.
        stage_dir = Path(args.runs_dir) / "_staged"
        project = stage_files(inputs, stage_dir)

    targets = tuple(Path(t) for t in args.targets.split(",")) if args.targets else ()
    task = ProofTask(project, targets=targets, instructions=args.instructions)

    platform = Platform(
        image=args.image,
        toolchain=args.toolchain,
        backend=args.backend,
        agent_backend=args.agent_backend,
        runs_dir=args.runs_dir,
    )
    provers = [p.strip() for p in args.provers.split(",") if p.strip()]
    result = platform.solve(task, provers, max_workers=args.max_workers)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
        return 0 if result.verified() else 1

    print(f"run {result.run_id}  ({result.run_dir})")
    for r in result.results:
        status = "✓ verified" if r.success else (r.error or "✗ unverified")
        cost = f"${r.cost_usd:.4f}" if r.cost_usd is not None else "—"
        dur = f"{r.duration_s:.0f}s" if r.duration_s is not None else "—"
        print(f"  {r.prover:<16} {status:<28} cost={cost:<10} time={dur}")
    best = result.best()
    best_name = best.prover if best else "none"
    print(f"best: {best_name}   total cost: ${result.total_cost_usd:.4f}")
    return 0 if result.verified() else 1


def _build_image(args: argparse.Namespace) -> int:
    images_dir = Path(__file__).resolve().parents[2] / "images"
    cmd = ["docker", "build", "-t", args.tag]
    if args.no_cache:
        cmd.append("--no-cache")
    cmd.append(str(images_dir))
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd).returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="open-afps")
    sub = parser.add_subparsers(dest="command", required=True)

    solve = sub.add_parser(
        "solve",
        help="Run provers over a lake project (or bare .lean files) and compare.",
    )
    solve.add_argument(
        "inputs",
        nargs="+",
        help="A lake project directory, or one or more bare .lean files.",
    )
    solve.add_argument(
        "--provers",
        default="agent",
        help=f"Comma-separated prover names. Available: {available_provers()}.",
    )
    solve.add_argument(
        "--instructions", default=None, help="Guidance forwarded to provers."
    )
    solve.add_argument(
        "--targets",
        default=None,
        help="Comma-separated files (relative to the project) to focus on.",
    )
    solve.add_argument("--image", default=DEFAULT_IMAGE)
    solve.add_argument("--toolchain", default=DEFAULT_TOOLCHAIN)
    solve.add_argument("--backend", default="docker", choices=["docker", "modal"])
    solve.add_argument(
        "--agent-backend",
        default=None,
        choices=["docker", "modal"],
        help="Separate generation backend (defaults to --backend).",
    )
    solve.add_argument("--runs-dir", default="runs")
    solve.add_argument("--max-workers", type=int, default=None)
    solve.add_argument(
        "--json", action="store_true", help="Emit the SolveResult as JSON."
    )

    build = sub.add_parser(
        "build-image", help="Build the sandbox Docker image from images/Dockerfile."
    )
    build.add_argument(
        "--tag", default=DEFAULT_IMAGE, help=f"Image tag (default: {DEFAULT_IMAGE})."
    )
    build.add_argument(
        "--no-cache", action="store_true", help="Pass --no-cache to docker build."
    )

    args = parser.parse_args(argv)
    if args.command == "solve":
        return _solve(args)
    if args.command == "build-image":
        return _build_image(args)
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
