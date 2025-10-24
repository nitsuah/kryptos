#!/usr/bin/env python3
"""Test composite hypotheses against K4 ciphertext.

Quick test runner for newly implemented composite cipher methods.
"""

from __future__ import annotations

import time
from pathlib import Path

from kryptos.k4.hypotheses import (
    SubstitutionThenTranspositionHypothesis,
    TranspositionThenHillHypothesis,
    VigenereThenTranspositionHypothesis,
)

# K4 ciphertext (97 chars)
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Statistical thresholds (from random baseline)
THRESHOLD_2SIGMA = -326.68  # 95% confidence
THRESHOLD_3SIGMA = -312.06  # 99.7% confidence


def test_hypothesis(name: str, hypothesis, limit: int = 10) -> dict:
    """Test a hypothesis and return results."""
    print(f"\n{'='*80}")
    print(f"Testing: {name}")
    print(f"{'='*80}")

    start_time = time.time()

    try:
        candidates = hypothesis.generate_candidates(K4_CIPHERTEXT, limit=limit)
        duration = time.time() - start_time

        print(f"\nCompleted in {duration:.1f} seconds")
        print(f"Generated {len(candidates)} candidates")

        if candidates:
            best = candidates[0]
            print("\nBest candidate:")
            print(f"  ID: {best.id[:80]}...")
            print(f"  Score: {best.score:.2f}")
            print(f"  Plaintext: {best.plaintext}")

            # Check significance
            if best.score > THRESHOLD_3SIGMA:
                print(f"  🎯 STRONG SIGNAL! (>{THRESHOLD_3SIGMA:.2f}, 3σ)")
            elif best.score > THRESHOLD_2SIGMA:
                print(f"  ⚠️  WEAK SIGNAL (>{THRESHOLD_2SIGMA:.2f}, 2σ)")
            else:
                print(f"  ❌ No significant signal (<{THRESHOLD_2SIGMA:.2f})")

            # Show top 5
            if len(candidates) >= 5:
                print("\nTop 5 scores:")
                for i, c in enumerate(candidates[:5], 1):
                    print(f"  {i}. {c.score:.2f}")

        return {
            "name": name,
            "success": True,
            "duration": duration,
            "count": len(candidates),
            "best_score": candidates[0].score if candidates else None,
            "best_plaintext": candidates[0].plaintext if candidates else None,
        }

    except Exception as e:
        duration = time.time() - start_time
        print(f"\n❌ ERROR: {e}")
        return {
            "name": name,
            "success": False,
            "duration": duration,
            "error": str(e),
        }


def main():
    """Run all composite hypothesis tests."""
    print("=" * 80)
    print("COMPOSITE HYPOTHESIS TESTING - K4 CRYPTANALYSIS")
    print("=" * 80)
    print(f"Ciphertext: {K4_CIPHERTEXT}")
    print(f"Length: {len(K4_CIPHERTEXT)} characters")
    print("\nStatistical Thresholds:")
    print(f"  2σ (95%): {THRESHOLD_2SIGMA:.2f}")
    print(f"  3σ (99.7%): {THRESHOLD_3SIGMA:.2f}")

    results = []

    # Test 1: Transposition → Hill 2x2 (most promising)
    # Reduced parameters for quick test
    results.append(
        test_hypothesis(
            "Transposition → Hill 2x2 (Quick Test)",
            TranspositionThenHillHypothesis(
                transposition_candidates=10,  # Reduced from 20
                hill_limit=500,  # Reduced from 1000
                transposition_widths=[5, 6, 7, 8, 10],  # Subset of widths
            ),
            limit=5,
        ),
    )

    # Test 2: Vigenère → Transposition
    results.append(
        test_hypothesis(
            "Vigenère → Transposition (Quick Test)",
            VigenereThenTranspositionHypothesis(
                vigenere_candidates=20,  # Reduced from 50
                transposition_limit=50,  # Reduced from 100
                vigenere_max_key_length=8,  # Reduced from 12
                transposition_widths=[5, 6, 7, 8],  # Subset
            ),
            limit=5,
        ),
    )

    # Test 3: Substitution → Transposition (fastest)
    results.append(
        test_hypothesis(
            "Simple Substitution → Transposition",
            SubstitutionThenTranspositionHypothesis(
                transposition_limit=50,  # Reduced from 100
                transposition_widths=[5, 6, 7, 8],  # Subset
            ),
            limit=5,
        ),
    )

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    print(f"\nTests run: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")

    if successful:
        total_time = sum(r["duration"] for r in successful)
        print(f"Total runtime: {total_time:.1f} seconds")

        # Best overall score
        best_result = max(successful, key=lambda r: r.get("best_score", float("-inf")))
        if best_result.get("best_score"):
            print(f"\nBest overall score: {best_result['best_score']:.2f}")
            print(f"From: {best_result['name']}")

            if best_result["best_score"] > THRESHOLD_3SIGMA:
                print("\n🎯 SUCCESS: Found strong signal above 3σ threshold!")
            elif best_result["best_score"] > THRESHOLD_2SIGMA:
                print("\n⚠️  INTERESTING: Found weak signal above 2σ threshold")
            else:
                print("\n❌ No statistically significant signals found")

    # Save results
    artifact_dir = Path("artifacts/composite_tests")
    artifact_dir.mkdir(parents=True, exist_ok=True)

    import json
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    output_file = artifact_dir / f"quick_test_{timestamp}.json"

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
