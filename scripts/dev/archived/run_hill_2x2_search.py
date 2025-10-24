"""Run exhaustive Hill 2x2 cipher search on K4 and report top candidates."""

from __future__ import annotations

import json
import time
from datetime import datetime

from kryptos.k4.hypotheses import HillCipher2x2Hypothesis
from kryptos.paths import get_artifacts_root

# K4 ciphertext
K4_CIPHER = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"


def main():
    print("=" * 80)
    print("Hill 2x2 Exhaustive Search on K4")
    print("=" * 80)
    print(f"Ciphertext: {K4_CIPHER}")
    print(f"Length: {len(K4_CIPHER)} characters")
    print()

    # Create hypothesis
    hyp = HillCipher2x2Hypothesis()

    # Run search
    print("Searching all ~158,000 invertible 2x2 matrices mod 26...")
    start = time.time()
    candidates = hyp.generate_candidates(K4_CIPHER, limit=50)
    elapsed = time.time() - start

    print(f"Search completed in {elapsed:.2f} seconds")
    print(f"Found {len(candidates)} candidates")
    print()

    # Display top 10
    print("=" * 80)
    print("TOP 10 CANDIDATES")
    print("=" * 80)
    for i, cand in enumerate(candidates[:10], 1):
        key_matrix = cand.key_info['matrix']
        print(f"\n#{i} | Score: {cand.score:.2f}")
        print(f"Key: [[{key_matrix[0][0]}, {key_matrix[0][1]}], [{key_matrix[1][0]}, {key_matrix[1][1]}]]")
        print(f"Plaintext: {cand.plaintext}")

    # Save results to artifacts
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    output_dir = get_artifacts_root() / "hill_2x2_searches"
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
                "key_matrix": c.key_info['matrix'],
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
