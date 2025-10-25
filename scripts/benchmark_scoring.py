"""Quick benchmark script with readable output."""

import time

from kryptos.k4.scoring import combined_plaintext_score, composite_score_with_stage_analysis


def benchmark_scoring():
    """Benchmark scoring functions with clear timing."""
    texts = [
        "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG" * 2,
        "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK" * 5,
    ]

    # Benchmark combined_plaintext_score
    start = time.perf_counter()
    for _ in range(500):
        for text in texts:
            combined_plaintext_score(text)
    elapsed = time.perf_counter() - start
    print(f"combined_plaintext_score (1000 calls): {elapsed:.3f}s ({elapsed/1000*1000:.2f}ms per call)")

    # Benchmark composite scoring
    stage1_text = "QWERTYUIOPASDFGHJKLZXCVBNM" * 20
    stage2_text = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG" * 15

    start = time.perf_counter()
    for _ in range(100):
        s1 = combined_plaintext_score(stage1_text)
        s2 = combined_plaintext_score(stage2_text)
        composite_score_with_stage_analysis(stage1_text, stage2_text, s1, s2)
    elapsed = time.perf_counter() - start
    print(f"composite_score_with_stage_analysis (100 calls): {elapsed:.3f}s ({elapsed/100*1000:.2f}ms per call)")


if __name__ == "__main__":
    print("Benchmarking scoring functions...")
    print("=" * 60)
    benchmark_scoring()
    print("=" * 60)
