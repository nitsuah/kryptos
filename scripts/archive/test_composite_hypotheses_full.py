#!/usr/bin/env python3
"""Full-scale composite hypothesis testing against K4 ciphertext.

This runs complete parameter exploration (~65 minutes total).
Use test_composite_hypotheses.py for quick smoke tests.
"""

from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path

from kryptos.k4.hypotheses import (
    SubstitutionThenTranspositionHypothesis,
    TranspositionThenHillHypothesis,
    VigenereThenTranspositionHypothesis,
)
from kryptos.paths import get_provenance_info

# K4 ciphertext (97 chars)
K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

# Statistical thresholds (from random baseline)
THRESHOLD_2SIGMA = -326.68  # 95% confidence
THRESHOLD_3SIGMA = -312.06  # 99.7% confidence


def run_hypothesis_test(name: str, hypothesis, limit: int = 10) -> dict:
    """Test a hypothesis and return results.

    Note: Renamed from test_hypothesis to avoid pytest collection.
    """
    print(f"\n{'='*80}")
    print(f"Testing: {name} (FULL SCALE)")
    print(f"{'='*80}")

    start_time = time.time()

    try:
        candidates = hypothesis.generate_candidates(K4_CIPHERTEXT, limit=limit)
        duration = time.time() - start_time

        print(f"\nCompleted in {duration:.1f} seconds ({duration/60:.1f} minutes)")
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
                print(f"  ⚠️  POTENTIAL SIGNAL (>{THRESHOLD_2SIGMA:.2f}, 2σ)")
            else:
                print("  ❌ No signal (below 2σ threshold)")

            return {
                'name': name,
                'duration': duration,
                'candidates': len(candidates),
                'best_score': best.score,
                'best_id': best.id,
                'best_plaintext': best.plaintext,
                'exceeds_2sigma': best.score > THRESHOLD_2SIGMA,
                'exceeds_3sigma': best.score > THRESHOLD_3SIGMA,
            }
        else:
            print("  ⚠️  No candidates generated")
            return {
                'name': name,
                'duration': duration,
                'candidates': 0,
                'best_score': None,
                'exceeds_2sigma': False,
                'exceeds_3sigma': False,
            }

    except Exception as e:
        duration = time.time() - start_time
        print(f"  ❌ ERROR: {e}")
        return {
            'name': name,
            'duration': duration,
            'error': str(e),
        }


def main():
    """Run full-scale composite hypothesis tests."""
    print("=" * 80)
    print("COMPOSITE HYPOTHESIS TESTING - K4 CRYPTANALYSIS (FULL SCALE)")
    print("=" * 80)
    print(f"Ciphertext: {K4_CIPHERTEXT}")
    print(f"Length: {len(K4_CIPHERTEXT)} characters")
    print("\nStatistical thresholds:")
    print(f"  2σ (95% confidence): {THRESHOLD_2SIGMA:.2f}")
    print(f"  3σ (99.7% confidence): {THRESHOLD_3SIGMA:.2f}")
    print("\nWARNING: Full-scale tests will take ~65 minutes total")
    print("=" * 80)

    results = []

    # Test 1: Transposition → Hill 2x2 (FULL PARAMETERS)
    # 20 transposition candidates × 1000 Hill keys = 20,000 combinations
    # Expected runtime: ~30 minutes
    print("\n\n## Test 1: Transposition → Hill 2x2 (Full Scale)")
    print("Parameters: 20 transposition candidates × 1,000 Hill keys")
    print("Expected: ~30 minutes")
    hyp1 = TranspositionThenHillHypothesis(
        transposition_candidates=20,
        hill_limit=1000,
    )
    result1 = run_hypothesis_test("Transposition → Hill 2x2", hyp1, limit=10)
    results.append(result1)

    # Test 2: Vigenère → Transposition (FULL PARAMETERS)
    # 50 Vigenère candidates × 100 transposition permutations = 5,000 combinations
    # Expected runtime: ~20 minutes
    print("\n\n## Test 2: Vigenère → Transposition (Full Scale)")
    print("Parameters: 50 Vigenère candidates × 100 transposition permutations")
    print("Expected: ~20 minutes")
    hyp2 = VigenereThenTranspositionHypothesis(
        vigenere_candidates=50,
        transposition_limit=100,
        vigenere_max_key_length=12,
    )
    result2 = run_hypothesis_test("Vigenère → Transposition", hyp2, limit=10)
    results.append(result2)

    # Test 3: Simple Substitution → Transposition (FULL PARAMETERS)
    # 28 substitution variants × 100 transposition permutations = 2,800 combinations
    # Expected runtime: ~15 minutes
    print("\n\n## Test 3: Simple Substitution → Transposition (Full Scale)")
    print("Parameters: 28 substitution variants × 100 transposition permutations")
    print("Expected: ~15 minutes")
    hyp3 = SubstitutionThenTranspositionHypothesis(
        transposition_limit=100,
    )
    result3 = run_hypothesis_test("Substitution → Transposition", hyp3, limit=10)
    results.append(result3)

    # Summary
    print("\n\n" + "=" * 80)
    print("SUMMARY - FULL SCALE COMPOSITE TESTS")
    print("=" * 80)

    total_time = sum(r.get('duration', 0) for r in results)
    print(f"\nTotal runtime: {total_time:.1f}s ({total_time/60:.1f} minutes)")

    signals_2sigma = [r for r in results if r.get('exceeds_2sigma')]
    signals_3sigma = [r for r in results if r.get('exceeds_3sigma')]

    print("\nResults:")
    for r in results:
        name = r['name']
        score = r.get('best_score')
        if score is not None:
            status = "🎯 3σ" if r.get('exceeds_3sigma') else "⚠️  2σ" if r.get('exceeds_2sigma') else "❌"
            print(f"  {status} {name}: {score:.2f}")
        else:
            print(f"  ❌ {name}: No results")

    if signals_3sigma:
        print(f"\n🎯 BREAKTHROUGH: {len(signals_3sigma)} method(s) exceeded 3σ threshold!")
    elif signals_2sigma:
        print(f"\n⚠️  INTERESTING: {len(signals_2sigma)} method(s) exceeded 2σ threshold")
    else:
        print("\n❌ No statistically significant signals found")
        print("Conclusion: K4 likely does not use simple two-layer classical ciphers")

    # Save results
    artifacts_dir = Path("artifacts/composite_tests")
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    output_file = artifacts_dir / f"full_test_{timestamp}.json"

    # Capture provenance info for reproducibility
    provenance = get_provenance_info(
        include_params={
            'test_type': 'full_scale_composite',
            'ciphertext_length': len(K4_CIPHERTEXT),
            'threshold_2sigma': THRESHOLD_2SIGMA,
            'threshold_3sigma': THRESHOLD_3SIGMA,
        },
    )

    output_data = {
        'test_type': 'full_scale_composite',
        'timestamp': timestamp,
        'provenance': provenance,
        'ciphertext': K4_CIPHERTEXT,
        'ciphertext_length': len(K4_CIPHERTEXT),
        'threshold_2sigma': THRESHOLD_2SIGMA,
        'threshold_3sigma': THRESHOLD_3SIGMA,
        'total_runtime_seconds': total_time,
        'results': results,
    }

    with output_file.open('w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == '__main__':
    main()
