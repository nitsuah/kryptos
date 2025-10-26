"""Core hypothesis runner - unified execution logic.

This module contains the reusable logic for running any hypothesis search.
Individual scripts should be thin wrappers that just specify which hypothesis to run.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from kryptos.paths import get_artifacts_root

K4_CIPHERTEXT = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK"


def run_hypothesis_search(
    hypothesis_name: str,
    hypothesis_instance: Any,
    ciphertext: str = K4_CIPHERTEXT,
    limit: int = 50,
    output_dir: str | None = None,
) -> dict[str, Any]:
    """Run a hypothesis search and save results.

    Args:
        hypothesis_name: Name for artifacts (e.g., 'hill_2x2', 'vigenere')
        hypothesis_instance: Instance of hypothesis class with generate_candidates()
        ciphertext: Ciphertext to decrypt
        limit: Max candidates to generate
        output_dir: Override default artifacts directory

    Returns:
        Results dictionary with candidates, timing, etc.
    """
    print("=" * 80)
    print(f"{hypothesis_name.upper().replace('_', ' ')} HYPOTHESIS SEARCH")
    print("=" * 80)
    print(f"Ciphertext: {ciphertext}")
    print(f"Length: {len(ciphertext)} chars")
    print()

    print(f"Running {hypothesis_name} search...")
    start = time.time()
    candidates = hypothesis_instance.generate_candidates(ciphertext, limit=limit)
    elapsed = time.time() - start

    print(f"Generated {len(candidates)} candidates in {elapsed:.3f}s")
    print()

    print("Top 10 candidates:")
    print("-" * 80)
    for i, c in enumerate(candidates[:10], 1):
        print(f"{i:2d}. Score: {c.score:8.2f}")
        print(f"    {c.plaintext[:74]}")
        if c.key_info:
            key_display = str(c.key_info)[:60]
            print(f"    Key: {key_display}")
        print()

    baseline_dir = get_artifacts_root() / "baselines"
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

        best_score = candidates[0].score if candidates else float('-inf')
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

    if output_dir:
        artifacts_dir = Path(output_dir)
    else:
        artifacts_dir = get_artifacts_root() / f"{hypothesis_name}_searches"

    artifacts_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_file = artifacts_dir / f"search_{timestamp}.json"

    results = {
        'timestamp': timestamp,
        'hypothesis': hypothesis_name,
        'ciphertext': ciphertext,
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

    if hasattr(hypothesis_instance, '__dict__'):
        results['parameters'] = {
            k: v
            for k, v in hypothesis_instance.__dict__.items()
            if not k.startswith('_') and isinstance(v, (str, int, float, list, dict, bool))
        }

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: {output_file}")
    print()

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Hypothesis: {hypothesis_name}")
    print(f"Candidates generated: {len(candidates)}")
    if candidates:
        print(f"Best score: {candidates[0].score:.2f}")
    print(f"Duration: {elapsed:.3f}s")
    print()

    return results
