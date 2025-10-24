"""Run Berlin Clock-constrained transposition search on K4 and report top candidates."""

from __future__ import annotations

import json
import time
from datetime import datetime

from kryptos.k4.hypotheses import BerlinClockTranspositionHypothesis
from kryptos.paths import get_artifacts_root

# K4 ciphertext
K4_CIPHER = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"


def main():
    print("=" * 80)
    print("Berlin Clock Transposition Search on K4")
    print("=" * 80)
    print(f"Ciphertext: {K4_CIPHER}")
    print(f"Length: {len(K4_CIPHER)} characters")
    print()

    # Create hypothesis
    hyp = BerlinClockTranspositionHypothesis()

    # Run search
    print("Searching clock-inspired column widths (5, 6, 7, 8, 10, 11, 12, 15, 24)...")
    print("Using adaptive pruning to limit permutation explosion...")
    start = time.time()
    candidates = hyp.generate_candidates(K4_CIPHER, limit=50)
    elapsed = time.time() - start

    print(f"Search completed in {elapsed:.2f} seconds")
    print(f"Found {len(candidates)} unique candidates")
    print()

    # Display top 10
    print("=" * 80)
    print("TOP 10 CANDIDATES")
    print("=" * 80)
    for i, cand in enumerate(candidates[:10], 1):
        cols = cand.key_info['columns']
        perm = cand.key_info['permutation']
        perm_display = str(perm) if len(perm) <= 12 else f"{perm[:6]}...{perm[-3:]}"
        print(f"\n#{i} | Score: {cand.score:.2f} | Columns: {cols}")
        print(f"Permutation: {perm_display}")
        print(f"Plaintext: {cand.plaintext}")

    # Save results to artifacts
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    output_dir = get_artifacts_root() / "transposition_searches"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"search_{ts}.json"

    results = {
        "timestamp": ts,
        "ciphertext": K4_CIPHER,
        "search_time_seconds": elapsed,
        "total_candidates": len(candidates),
        "candidates": [
            {
                "rank": i + 1,
                "id": c.id,
                "plaintext": c.plaintext,
                "columns": c.key_info['columns'],
                "permutation": list(c.key_info['permutation']),
                "score": c.score,
            }
            for i, c in enumerate(candidates)
        ],
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print()
    print("=" * 80)
    print(f"Results saved to: {output_file}")
    print("=" * 80)


if __name__ == '__main__':
    main()
