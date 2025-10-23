"""Compare scoring with and without Sanborn-derived cribs.

Reads `docs/sources/sanborn_crib_candidates.txt`, extracts candidate tokens,
and computes baseline vs crib-augmented scores for a small set of samples.

Writes `crib_integration.csv` into a timestamped folder under
`artifacts/tuning_runs/` so you can inspect before/after effects.
"""

import csv
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"


def load_cribs_from_docs(path: Path) -> list[str]:
    cribs: list[str] = []
    if not path.exists():
        return cribs
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            if parts:
                token = parts[0].strip().upper()
                if token.isalpha() and len(token) >= 3:
                    cribs.append(token)
    return cribs


SAMPLES = [
    "BETWEEN SUBTLE SHADING AND THE ABSENCE OF LIGHT LIES THE NUANCE OF ILLUSION",
    "IT WAS TOTALLY INVISIBLE HOWS THAT POSSIBLE THEY USED THE EARTHS MAGNETIC FIELD",
    "SLOWLY DESPARATLY SLOWLY THE REMAINS OF PASSAGE DEBRIS THAT ENCUMBERED THE LOWER",
]


def run():
    try:
        from kryptos.k4 import scoring  # type: ignore
    except ImportError:
        if str(SRC) not in sys.path:
            sys.path.insert(0, str(SRC))
        from kryptos.k4 import scoring  # type: ignore

    docs_path = ROOT / "docs" / "sources" / "sanborn_crib_candidates.txt"
    cribs = load_cribs_from_docs(docs_path)

    ts = time.strftime("%Y%m%dT%H%M%S")
    run_dir = ROOT / "artifacts" / "tuning_runs" / f"run_{ts}"
    run_dir.mkdir(parents=True, exist_ok=True)

    out_path = run_dir / "crib_integration.csv"
    with out_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["sample", "baseline_combined", "with_cribs_combined", "crib_count"])

        for s in SAMPLES:
            base_stats = scoring.baseline_stats(s)
            baseline = base_stats.get("combined_score")

            # compute with cribs applied: temporarily compute crib bonus for the
            # docs-derived cribs without mutating the scoring module global.
            # Reuse scoring.positional_crib_bonus with empty positions; i.e., simple
            # presence bonus using scoring.crib_bonus but providing our own list.
            # We'll emulate scoring.crib_bonus behavior here.
            upper = ''.join(c for c in s.upper() if c.isalpha())
            crib_bonus = 0.0
            for crib in cribs:
                if crib in upper:
                    crib_bonus += 5.0 * len(crib)

            with_crib = baseline + crib_bonus
            writer.writerow([s[:80], f"{baseline:.6f}", f"{with_crib:.6f}", len(cribs)])

    print(f"Wrote crib integration comparison to: {out_path}")


if __name__ == "__main__":
    run()
