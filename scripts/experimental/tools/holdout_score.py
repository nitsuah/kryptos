#!/usr/bin/env python3
"""Compute holdout scoring for a chosen crib weight and write CSV results.

Usage: python scripts/tools/holdout_score.py --weight 0.65 --out artifacts/reports/holdout.csv
"""

import argparse
import csv
import sys
from pathlib import Path


def load_scoring(repo_root: Path):
    try:
        from kryptos.k4 import scoring as hold_scoring

        return hold_scoring
    except Exception:
        try:
            from src.k4 import scoring as hold_scoring

            return hold_scoring
        except Exception:
            if str(repo_root / 'src') not in sys.path:
                sys.path.insert(0, str(repo_root / 'src'))
            import k4.scoring as hold_scoring

            return hold_scoring


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--weight', type=float, required=True)
    parser.add_argument('--out', type=str, default='artifacts/reports/holdout.csv')
    args = parser.parse_args()

    repo_root = Path.cwd()
    scoring = load_scoring(repo_root)

    HOLDOUT = [
        'IN THE QUIET AFTERNOON THE SHADOWS GREW LONG ON THE FLOOR',
        'THE SECRET MESSAGE WAS HIDDEN IN PLAIN SIGHT AMONG THE TEXT',
    ]

    chosen_w = float(args.weight)
    rows = []
    for s in HOLDOUT:
        base = scoring.combined_plaintext_score(s)
        withc = scoring.combined_plaintext_score_with_external_cribs(s, external_cribs=[], crib_weight=chosen_w)
        rows.append({'sample': s, 'base': base, 'with': withc, 'delta': withc - base})

    outp = repo_root / args.out
    outp.parent.mkdir(parents=True, exist_ok=True)
    with outp.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=['sample', 'base', 'with', 'delta'])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    mean_delta = sum(r['delta'] for r in rows) / len(rows) if rows else None
    print(f'Wrote holdout to {outp} (mean_delta={mean_delta})')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
