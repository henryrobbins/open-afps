"""Benchmark sweep tests (no Docker, no creds).

Drives :func:`~open_atp.benchmark.run_benchmark` with scripted, no-backend provers
(reusing the ``FakeProver`` seam): it lays out ``output_dir/<task>/<prover>/`` with a
``results.json`` per cell, records a raising prover as a failed result without aborting
the sweep, and renders a table with one row per ``(task, prover)`` pair.
"""

from __future__ import annotations

import json
from pathlib import Path

from open_atp.benchmark import run_benchmark
from open_atp.lean import LeanProject, ProofTask

from .test_api import FIXTURE, FakeProver


def _tasks() -> dict[str, ProofTask]:
    task = ProofTask(LeanProject(FIXTURE))
    return {"alpha": task, "beta": task}


def test_layout_and_results_json(tmp_path: Path) -> None:
    provers = {"good": FakeProver("agent"), "bad": FakeProver("numina", verified=False)}

    result = run_benchmark(_tasks(), provers, tmp_path)

    # Every (task, prover) cell has its own <task>/<prover>/ dir with wd/logs/results.
    for task in ("alpha", "beta"):
        for prover in ("good", "bad"):
            run_dir = tmp_path / task / prover
            assert (run_dir / "wd").is_dir()
            assert (run_dir / "logs").is_dir()
            payload = json.loads((run_dir / "results.json").read_text())
            assert payload["success"] is (prover == "good")

    assert len(result.runs) == 4
    assert {(r.task, r.prover) for r in result.runs} == {
        ("alpha", "good"),
        ("alpha", "bad"),
        ("beta", "good"),
        ("beta", "bad"),
    }


def test_raising_prover_recorded_not_aborted(tmp_path: Path) -> None:
    provers = {
        "boom": FakeProver("agent", raises=RuntimeError("docker down")),
        "ok": FakeProver("numina"),
    }

    result = run_benchmark({"alpha": _tasks()["alpha"]}, provers, tmp_path)

    by_prover = {r.prover: r.result for r in result.runs}
    assert by_prover["boom"].error == "docker down"
    assert by_prover["boom"].verification is None
    assert by_prover["boom"].success is False
    assert by_prover["ok"].success is True
    # The failed cell still wrote its results.json.
    payload = json.loads((tmp_path / "alpha" / "boom" / "results.json").read_text())
    assert payload["error"] == "docker down"


def test_table_has_a_row_per_pair(tmp_path: Path) -> None:
    provers = {"good": FakeProver("agent"), "bad": FakeProver("numina", verified=False)}

    table = run_benchmark(_tasks(), provers, tmp_path).table()

    lines = table.splitlines()
    assert lines[0].split()[:5] == ["task", "prover", "status", "cost", "time"]
    # header + separator + 4 data rows
    assert len(lines) == 6
    assert "✓" in table and "✗" in table
