"""Run thorough transposition search on K4 - all widths 2-20, no pruning."""

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
    print("THOROUGH Transposition Search on K4")
    print("=" * 80)
    print(f"Ciphertext: {K4_CIPHER}")
    print(f"Length: {len(K4_CIPHER)} characters")
    print()
    print("Testing ALL column widths 2-20 (not just Berlin Clock periods)")
    print("WITHOUT adaptive pruning to ensure thorough coverage")
    print("Max permutations: 10,000 per width (or factorial if smaller)")
    print()

    # Create hypothesis with all widths 2-20, no pruning
    widths = list(range(2, 21))  # 2, 3, 4, ..., 20
    hyp = BerlinClockTranspositionHypothesis(
        widths=widths,
        prune=False,  # No pruning - test everything
        max_perms=10_000,  # Higher limit
    )

    # Run search
    print(f"Searching {len(widths)} column widths...")
    start = time.time()
    candidates = hyp.generate_candidates(K4_CIPHER, limit=100)
    elapsed = time.time() - start

    print(f"Search completed in {elapsed:.2f} seconds")
    print(f"Found {len(candidates)} unique candidates")
    print()

    # Display top 20
    print("=" * 80)
    print("TOP 20 CANDIDATES")
    print("=" * 80)
    for i, cand in enumerate(candidates[:20], 1):
        cols = cand.key_info['columns']
        perm = cand.key_info['permutation']
        perm_display = str(perm) if len(perm) <= 8 else f"{perm[:4]}...{perm[-3:]}"
        print(f"\n#{i} | Score: {cand.score:.2f} | Columns: {cols}")
        print(f"Permutation: {perm_display}")
        print(f"Plaintext: {cand.plaintext[:60]}...")

    # Statistical analysis
    print()
    print("=" * 80)
    print("STATISTICAL ANALYSIS")
    print("=" * 80)
    scores = [c.score for c in candidates]
    if scores:
        print(f"Best score: {max(scores):.2f}")
        print(f"Worst score: {min(scores):.2f}")
        print(f"Mean score: {sum(scores)/len(scores):.2f}")
        print()

        # Compare to random baseline
        random_mean = -355.92
        random_threshold_2sigma = -326.68
        random_threshold_3sigma = -312.06

        print("Comparison to Random Baseline:")
        print(f"  Random mean: {random_mean:.2f}")
        print(f"  Random 2σ threshold: {random_threshold_2sigma:.2f}")
        print(f"  Random 3σ threshold: {random_threshold_3sigma:.2f}")
        print()

        best = max(scores)
        if best > random_threshold_3sigma:
            print(f"✓✓✓ BEST SCORE ({best:.2f}) IS ABOVE 3σ - STRONG SIGNAL!")
        elif best > random_threshold_2sigma:
            print(f"✓✓ BEST SCORE ({best:.2f}) IS ABOVE 2σ - WEAK SIGNAL!")
        elif best > random_mean:
            print(f"✓ BEST SCORE ({best:.2f}) IS ABOVE RANDOM MEAN - INVESTIGATE")
        else:
            print(f"✗ BEST SCORE ({best:.2f}) IS BELOW RANDOM MEAN - RULED OUT")

    # Save results to artifacts
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    output_dir = get_artifacts_root() / "transposition_searches"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"thorough_search_{ts}.json"

    results = {
        "timestamp": ts,
        "ciphertext": K4_CIPHER,
        "search_time_seconds": elapsed,
        "widths_tested": widths,
        "pruning_enabled": False,
        "max_perms_per_width": 10_000,
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
