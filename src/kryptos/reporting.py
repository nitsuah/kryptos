"""Canonical reporting module (replaces legacy `src/report.py` and shim).

Generates frequency analysis bar chart and crib summary text file. Uses Agg backend
to avoid GUI requirements. Callers pass in a mapping of keys to frequencies and cribs.
"""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")


def generate_report(results: Mapping[str, dict], cipher_name: str, out_dir: str | os.PathLike[str] = "reports") -> Path:
    freqs_map: Mapping[str, Mapping[str, float]] = results.get("frequencies", {})  # type: ignore
    cribs_map: Mapping[str, Sequence[str]] = results.get("cribs", {})  # type: ignore
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    png_path = out_path / f"{cipher_name}_report.png"

    if freqs_map:
        all_chars = sorted({c for fm in freqs_map.values() for c in fm.keys()})
        avg_vals: list[float] = []
        for ch in all_chars:
            vals = [fm.get(ch, 0.0) for fm in freqs_map.values()]
            avg_vals.append(sum(vals) / len(vals))
        plt.figure(figsize=(max(6, len(all_chars) * 0.3), 4))
        plt.bar(all_chars, avg_vals)
        plt.title(f"Frequency Analysis (avg) for {cipher_name}")
        plt.xlabel("Characters")
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.savefig(png_path)
        plt.close()

    summary_path = out_path / f"{cipher_name}_summary.txt"
    with summary_path.open("w", encoding="utf-8") as fh:
        for key, cribs in cribs_map.items():
            fh.write(f"Key={key}: {', '.join(cribs) if cribs else '[none]'}\n")
    return png_path


__all__ = ["generate_report"]
