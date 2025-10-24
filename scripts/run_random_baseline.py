"""Generate random baseline scoring distribution for statistical thresholds.

This establishes what "random gibberish" scores look like, allowing us to
distinguish meaningful candidates from noise using statistical significance.
"""

from __future__ import annotations

import json
import random
import string
import time
from datetime import datetime

from kryptos.k4.scoring import combined_plaintext_score
from kryptos.paths import get_artifacts_root


def generate_random_text(length: int = 74) -> str:
    """Generate random A-Z text of specified length."""
    return ''.join(random.choices(string.ascii_uppercase, k=length))


def compute_statistics(scores: list[float]) -> dict:
    """Compute statistical measures from score distribution."""
    scores_sorted = sorted(scores)
    n = len(scores)

    mean = sum(scores) / n
    variance = sum((x - mean) ** 2 for x in scores) / n
    stddev = variance**0.5

    percentiles = {
        '1': scores_sorted[int(n * 0.01)],
        '5': scores_sorted[int(n * 0.05)],
        '10': scores_sorted[int(n * 0.10)],
        '25': scores_sorted[int(n * 0.25)],
        '50': scores_sorted[int(n * 0.50)],
        '75': scores_sorted[int(n * 0.75)],
        '90': scores_sorted[int(n * 0.90)],
        '95': scores_sorted[int(n * 0.95)],
        '99': scores_sorted[int(n * 0.99)],
    }

    return {
        'mean': mean,
        'stddev': stddev,
        'min': scores_sorted[0],
        'max': scores_sorted[-1],
        'percentiles': percentiles,
        'threshold_1sigma': mean + stddev,
        'threshold_2sigma': mean + 2 * stddev,
        'threshold_3sigma': mean + 3 * stddev,
    }


def main():
    print("=" * 80)
    print("Random Baseline Scoring Distribution")
    print("=" * 80)
    print("Generating 10,000 random 74-character A-Z strings...")
    print("This establishes statistical baseline for distinguishing signal from noise.")
    print()

    # Generate random texts and score them
    n_samples = 10_000
    scores = []

    start = time.time()
    for i in range(n_samples):
        if i > 0 and i % 1000 == 0:
            print(f"Progress: {i}/{n_samples} ({i/n_samples*100:.0f}%)")

        text = generate_random_text(74)
        score = combined_plaintext_score(text)
        scores.append(score)

    elapsed = time.time() - start

    print(f"\nCompleted in {elapsed:.2f} seconds")
    print()

    # Compute statistics
    stats = compute_statistics(scores)

    # Display results
    print("=" * 80)
    print("STATISTICAL SUMMARY")
    print("=" * 80)
    print(f"Samples: {n_samples:,}")
    print(f"Mean score: {stats['mean']:.2f}")
    print(f"Std deviation: {stats['stddev']:.2f}")
    print(f"Range: [{stats['min']:.2f}, {stats['max']:.2f}]")
    print()

    print("Percentiles:")
    for pct, val in stats['percentiles'].items():
        print(f"  {pct:>3}th: {val:>8.2f}")
    print()

    print("Statistical Thresholds:")
    print(f"  Mean + 1σ: {stats['threshold_1sigma']:>8.2f} (68% of random below this)")
    print(f"  Mean + 2σ: {stats['threshold_2sigma']:>8.2f} (95% of random below this)")
    print(f"  Mean + 3σ: {stats['threshold_3sigma']:>8.2f} (99.7% of random below this)")
    print()

    # Interpretation
    print("=" * 80)
    print("INTERPRETATION")
    print("=" * 80)
    print(f"Any candidate scoring above {stats['threshold_3sigma']:.2f} is statistically")
    print("significant (>99.7% confidence it's not random noise).")
    print()
    print("Use this to evaluate hypothesis results:")
    print(f"  - Score < {stats['mean']:.2f}: worse than random (BAD)")
    print(f"  - Score {stats['mean']:.2f} to {stats['threshold_1sigma']:.2f}: random noise")
    print(f"  - Score {stats['threshold_1sigma']:.2f} to {stats['threshold_2sigma']:.2f}: weak signal (investigate)")
    print(f"  - Score > {stats['threshold_3sigma']:.2f}: strong signal (PROMISING!)")
    print()

    # Compare to our hypothesis results
    print("=" * 80)
    print("COMPARISON TO HYPOTHESIS RESULTS")
    print("=" * 80)
    print("Hill 2x2 best score:        -329.45")
    print("Transposition best score:   -350.80")
    print(f"Random baseline mean:       {stats['mean']:.2f}")
    print()

    if -329.45 < stats['mean']:
        print("✓ Hill 2x2 scores BELOW random mean - definitively ruled out")
    else:
        print("⚠ Hill 2x2 scores ABOVE random mean - may need re-evaluation")

    if -350.80 < stats['mean']:
        print("✓ Transposition scores BELOW random mean - definitively ruled out")
    else:
        print("⚠ Transposition scores ABOVE random mean - may need re-evaluation")
    print()

    # Save results
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    output_dir = get_artifacts_root() / "baselines"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"random_scoring_{ts}.json"

    results = {
        "timestamp": ts,
        "n_samples": n_samples,
        "text_length": 74,
        "elapsed_seconds": elapsed,
        "statistics": stats,
        "samples": scores[:100],  # Store first 100 as examples
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print("=" * 80)
    print(f"Results saved to: {output_file}")
    print("=" * 80)


if __name__ == '__main__':
    main()
