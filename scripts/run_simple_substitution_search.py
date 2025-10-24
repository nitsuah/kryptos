"""Run simple substitution search on K4 (Caesar, Atbash, Reverse)."""

from __future__ import annotations

import json
import time
from datetime import datetime

from kryptos.k4.hypotheses import SimpleSubstitutionHypothesis
from kryptos.paths import get_artifacts_root

K4_CIPHER = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"


def main():
    print("=" * 80)
    print("Simple Substitution Search on K4")
    print("=" * 80)
    print(f"Ciphertext: {K4_CIPHER}")
    print("Testing: Caesar/ROT-N (26 shifts), Atbash, Reverse")
    print()

    hyp = SimpleSubstitutionHypothesis()

    start = time.time()
    candidates = hyp.generate_candidates(K4_CIPHER, limit=28)  # All of them
    elapsed = time.time() - start

    print(f"Search completed in {elapsed:.3f} seconds")
    print()

    # Display top 10
    print("=" * 80)
    print("TOP 10 CANDIDATES")
    print("=" * 80)
    for i, cand in enumerate(candidates[:10], 1):
        print(f"\n#{i} | Score: {cand.score:.2f} | Type: {cand.key_info['type']}")
        if 'shift' in cand.key_info:
            print(f"Shift: {cand.key_info['shift']}")
        print(f"Plaintext: {cand.plaintext[:60]}...")

    # Statistical analysis
    print()
    print("=" * 80)
    print("STATISTICAL ANALYSIS")
    print("=" * 80)
    best = max(c.score for c in candidates)
    random_mean = -355.92
    random_2sigma = -326.68
    random_3sigma = -312.06

    print(f"Best score: {best:.2f}")
    print(f"Random mean: {random_mean:.2f}")
    print(f"Random 2σ: {random_2sigma:.2f}")
    print(f"Random 3σ: {random_3sigma:.2f}")
    print()

    if best > random_3sigma:
        print(f"✓✓✓ BEST SCORE ({best:.2f}) ABOVE 3σ - STRONG SIGNAL!")
    elif best > random_2sigma:
        print(f"✓✓ BEST SCORE ({best:.2f}) ABOVE 2σ - WEAK SIGNAL!")
    elif best > random_mean:
        print(f"✓ BEST SCORE ({best:.2f}) ABOVE RANDOM MEAN")
    else:
        print(f"✗ BEST SCORE ({best:.2f}) BELOW RANDOM MEAN - RULED OUT")

    # Save results
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    output_dir = get_artifacts_root() / "simple_substitution_searches"
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
                "key_info": c.key_info,
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
