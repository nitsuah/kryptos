"""Attack-sweep benchmark harness.

Runs the fast K4 attack sweeps under a timer and records throughput and
search-space statistics so changes to scoring/pruning can be compared run
over run (locally via ``kryptos benchmark``, and in CI which uploads the
results as a build artifact).

Each result row:

    {"cipher": "K4", "method": "quagmire_sweep", "time_sec": 1.23,
     "tested": 6240, "tested_per_sec": 5073.2, "space_reduction": null,
     "status": "null_result", "timestamp": "..."}

``space_reduction`` is the fraction of the enumerated space pruned *before*
the expensive scoring step, for attacks that report a pre-filter (e.g. the
clock→Hill invertibility filter); ``null`` for attacks with no pre-filter.

Attack null artifacts are written to a temporary directory and discarded —
provenance artifacts belong to real research runs, not benchmarks.
"""

from __future__ import annotations

import csv
import json
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from kryptos.k4.eureka import EurekaSignal

DEFAULT_OUT_DIR = "benchmarks"

CSV_FIELDS = ["cipher", "method", "time_sec", "tested", "tested_per_sec", "space_reduction", "status", "timestamp"]


@dataclass
class BenchmarkCase:
    cipher: str
    method: str
    run: Callable[[Path], dict[str, Any]]  # artifact_dir -> sweep summary


def _beaufort(artifact_dir: Path) -> dict[str, Any]:
    from kryptos.k4.beaufort_sweep import run_beaufort_sweep

    return run_beaufort_sweep(null_artifact_path=artifact_dir / "beaufort.json")


def _quagmire(artifact_dir: Path) -> dict[str, Any]:
    from kryptos.k4.quagmire_sweep import run_quagmire_sweep

    return run_quagmire_sweep(null_artifact_path=artifact_dir / "quagmire.json")


def _clock_hill(artifact_dir: Path) -> dict[str, Any]:
    from kryptos.k4.clock_hill_attack import run_clock_hill_attack

    return run_clock_hill_attack(null_artifact_path=artifact_dir / "clock_hill.json")


def _clock_vigenere(artifact_dir: Path) -> dict[str, Any]:
    from kryptos.k4.clock_hill_attack import run_clock_vigenere_attack

    return run_clock_vigenere_attack(null_artifact_path=artifact_dir / "clock_vigenere.json")


def _clock_subrow(artifact_dir: Path) -> dict[str, Any]:
    from kryptos.k4.clock_subrow_attack import run_clock_subrow_attack

    return run_clock_subrow_attack(null_artifact_path=artifact_dir / "clock_subrow.json")


def _clock_transposition(artifact_dir: Path) -> dict[str, Any]:
    from kryptos.k4.clock_subrow_attack import run_clock_transposition_attack

    return run_clock_transposition_attack(null_artifact_path=artifact_dir / "clock_transposition.json")


BENCHMARK_CASES: dict[str, BenchmarkCase] = {
    "beaufort_sweep": BenchmarkCase("K4", "beaufort_sweep", _beaufort),
    "quagmire_sweep": BenchmarkCase("K4", "quagmire_sweep", _quagmire),
    "clock_hill": BenchmarkCase("K4", "clock_hill_attack", _clock_hill),
    "clock_vigenere": BenchmarkCase("K4", "clock_vigenere_attack", _clock_vigenere),
    "clock_subrow": BenchmarkCase("K4", "clock_subrow_attack", _clock_subrow),
    "clock_transposition": BenchmarkCase("K4", "clock_transposition_attack", _clock_transposition),
}


def _extract_tested(summary: dict[str, Any]) -> int | None:
    params = summary.get("run_params", {})
    for key in ("total_tested", "total_clock_states"):
        if key in params:
            return int(params[key])
    return None


def _extract_space_reduction(summary: dict[str, Any]) -> float | None:
    """Fraction of enumerated space pruned by a pre-filter, if reported."""
    params = summary.get("run_params", {})
    total = params.get("total_clock_states")
    kept = params.get("invertible_states")
    if total and kept is not None:
        return round(1.0 - kept / total, 4)
    return None


def run_benchmarks(
    names: list[str] | None = None,
    out_dir: str | Path = DEFAULT_OUT_DIR,
) -> list[dict[str, Any]]:
    """Run benchmark cases and write ``results.json`` + ``results.csv``.

    Args:
        names: Subset of BENCHMARK_CASES keys (default: all).
        out_dir: Directory for results files (created if missing).

    Returns:
        List of result rows (also persisted to out_dir).
    """
    if names is None:
        names = list(BENCHMARK_CASES)
    unknown = [n for n in names if n not in BENCHMARK_CASES]
    if unknown:
        raise ValueError(f"Unknown benchmark case(s): {', '.join(unknown)}")

    rows: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory() as tmp:
        artifact_dir = Path(tmp)
        for name in names:
            case = BENCHMARK_CASES[name]
            start = time.perf_counter()
            try:
                summary = case.run(artifact_dir)
                status = str(summary.get("status", "unknown"))
            except EurekaSignal as signal:  # a benchmark would be a funny way to solve K4
                summary = {"run_params": {}, "status": "eureka", "result": signal.result}
                status = "eureka"
            elapsed = time.perf_counter() - start

            tested = _extract_tested(summary)
            rows.append(
                {
                    "cipher": case.cipher,
                    "method": case.method,
                    "time_sec": round(elapsed, 4),
                    "tested": tested,
                    "tested_per_sec": round(tested / elapsed, 2) if tested and elapsed > 0 else None,
                    "space_reduction": _extract_space_reduction(summary),
                    "status": status,
                    "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                }
            )

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    with open(out / "results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return rows


def format_results_table(rows: list[dict[str, Any]]) -> str:
    """Render rows as a GitHub-flavoured markdown table (for CI step summaries)."""
    lines = [
        "| cipher | method | time (s) | tested | tested/s | space reduction | status |",
        "|--------|--------|----------|--------|----------|-----------------|--------|",
    ]
    for r in rows:
        reduction = f"{r['space_reduction']:.2%}" if r["space_reduction"] is not None else "—"
        lines.append(
            f"| {r['cipher']} | {r['method']} | {r['time_sec']} | {r['tested']} |"
            f" {r['tested_per_sec']} | {reduction} | {r['status']} |"
        )
    return "\n".join(lines)


__all__ = ["BENCHMARK_CASES", "BenchmarkCase", "run_benchmarks", "format_results_table", "CSV_FIELDS"]
