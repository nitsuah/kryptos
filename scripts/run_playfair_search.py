#!/usr/bin/env python3
"""Run Playfair cipher hypothesis search on K4.

Tests Playfair cipher with Sanborn-related keywords (KRYPTOS, BERLIN, CLOCK, etc.).
Playfair uses 5x5 grid for digraph substitution.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from kryptos.k4.hypotheses import PlayfairHypothesis

# K4 ciphertext (74 chars)
K4_CIPHERTEXT_74 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"


def main():
    print("=" * 80)
    print("PLAYFAIR CIPHER HYPOTHESIS SEARCH")
    print("=" * 80)
    print(f"Ciphertext: {K4_CIPHERTEXT_74}")
    print(f"Length: {len(K4_CIPHERTEXT_74)} chars")
    print()

    # Run hypothesis
    print("Testing Sanborn-related keywords (KRYPTOS, BERLIN, CLOCK, etc.)...")
    hypothesis = PlayfairHypothesis()

    import time

    start = time.time()
    candidates = hypothesis.generate_candidates(K4_CIPHERTEXT_74, limit=10)
    elapsed = time.time() - start

    print(f"Generated {len(candidates)} candidates in {elapsed:.3f}s")
    print()

    # Show all candidates (there should be one per keyword)
    print("All candidates:")
    print("-" * 80)
    for i, c in enumerate(candidates, 1):
        keyword = c.key_info['keyword']
        print(f"{i:2d}. Score: {c.score:8.2f} | Keyword: {keyword:15s}")
        print(f"    {c.plaintext[:74]}")
        # Check for interesting words
        pt_lower = c.plaintext.lower()
        found_words = []
        for word in ['berlin', 'clock', 'kryptos', 'east', 'west', 'north', 'south']:
            if word in pt_lower:
                found_words.append(word)
        if found_words:
            print(f"    ⭐ Found words: {', '.join(found_words)}")
        print()

    # Load random baseline for comparison
    baseline_dir = Path(__file__).parent.parent / "artifacts" / "baselines"
    baseline_files = sorted(baseline_dir.glob("random_scoring_*.json"))
    if baseline_files:
        with open(baseline_files[-1]) as f:
            baseline = json.load(f)
        mean = baseline['statistics']['mean']
        stddev = baseline['statistics']['stddev']
        threshold_2sigma = mean + 2 * stddev
        threshold_3sigma = mean + 3 * stddev

        print("=" * 80)
        print("STATISTICAL ANALYSIS")
        print("=" * 80)
        print(f"Random baseline mean: {mean:.2f}")
        print(f"Random baseline stddev: {stddev:.2f}")
        print(f"2σ threshold (95% confidence): {threshold_2sigma:.2f}")
        print(f"3σ threshold (99.7% confidence): {threshold_3sigma:.2f}")
        print()

        best_score = candidates[0].score
        if best_score > threshold_3sigma:
            print(f"✓ STRONG SIGNAL: Best score ({best_score:.2f}) > 3σ ({threshold_3sigma:.2f})")
            print("  This is statistically significant!")
        elif best_score > threshold_2sigma:
            print(f"⚠ WEAK SIGNAL: Best score ({best_score:.2f}) between 2σ and 3σ")
            print(f"  ({threshold_2sigma:.2f} < {best_score:.2f} < {threshold_3sigma:.2f})")
            print("  Warrants further investigation.")
        else:
            print(f"✗ NO SIGNAL: Best score ({best_score:.2f}) < 2σ ({threshold_2sigma:.2f})")
            print("  Not significantly better than random.")
        print()

    # Save results
    artifacts_dir = Path(__file__).parent.parent / "artifacts" / "playfair_searches"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_file = artifacts_dir / f"search_{timestamp}.json"

    results = {
        'timestamp': timestamp,
        'hypothesis': 'playfair',
        'parameters': {
            'keywords': hypothesis.keywords,
        },
        'ciphertext': K4_CIPHERTEXT_74,
        'num_candidates': len(candidates),
        'elapsed_seconds': elapsed,
        'candidates': [
            {
                'rank': i + 1,
                'id': c.id,
                'plaintext': c.plaintext,
                'key_info': c.key_info,
                'score': c.score,
            }
            for i, c in enumerate(candidates)
        ],
    }

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: {output_file}")
    print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("Hypothesis: Playfair cipher (Sanborn keywords)")
    print(f"Keywords tested: {len(hypothesis.keywords)}")
    print(f"Best score: {candidates[0].score:.2f}")
    print(f"Best keyword: {candidates[0].key_info['keyword']}")
    print(f"Duration: {elapsed:.3f}s")
    print()


if __name__ == '__main__':
    main()
