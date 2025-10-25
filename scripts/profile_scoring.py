"""Profile scoring.py to identify performance hotspots.

This script uses cProfile to analyze the performance of key scoring functions
and identify opportunities for optimization.
"""

import cProfile
import pstats
from io import StringIO

from kryptos.k4.scoring import (
    bigram_score,
    chi_square_stat,
    combined_plaintext_score,
    composite_score_with_stage_analysis,
    index_of_coincidence,
    quadgram_score,
    trigram_score,
    wordlist_hit_rate,
)


def profile_combined_plaintext_score():
    """Profile the combined_plaintext_score function."""
    # Test with various text lengths
    texts = [
        "A" * 50,  # Short uniform
        "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG" * 2,  # Medium English-like
        "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPK" * 10,  # Long K4-like
    ]

    for _ in range(100):
        for text in texts:
            combined_plaintext_score(text)


def profile_individual_scores():
    """Profile individual scoring components."""
    text = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG" * 10

    # IOC
    for _ in range(1000):
        index_of_coincidence(text)

    # Chi-square
    for _ in range(1000):
        chi_square_stat(text)

    # Bigram score
    for _ in range(100):
        bigram_score(text)

    # Trigram score
    for _ in range(100):
        trigram_score(text)

    # Quadgram score
    for _ in range(100):
        quadgram_score(text)

    # Wordlist hit rate
    for _ in range(100):
        wordlist_hit_rate(text)


def profile_composite_scoring():
    """Profile composite score analysis."""
    stage1_text = "QWERTYUIOPASDFGHJKLZXCVBNM" * 20
    stage2_text = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG" * 15

    for _ in range(50):
        stage1_score = combined_plaintext_score(stage1_text)
        stage2_score = combined_plaintext_score(stage2_text)
        composite_score_with_stage_analysis(
            stage1_text,
            stage2_text,
            stage1_score,
            stage2_score,
            stage1_weight=0.3,
            stage2_weight=0.7,
        )


def run_profiling():
    """Run all profiling tests and display results."""
    print("=" * 80)
    print("PROFILING SCORING.PY")
    print("=" * 80)

    # Profile combined_plaintext_score
    print("\n1. Profiling combined_plaintext_score...")
    profiler = cProfile.Profile()
    profiler.enable()
    profile_combined_plaintext_score()
    profiler.disable()

    s = StringIO()
    stats = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    stats.print_stats(20)
    print(s.getvalue())

    # Profile individual components
    print("\n2. Profiling individual scoring components...")
    profiler = cProfile.Profile()
    profiler.enable()
    profile_individual_scores()
    profiler.disable()

    s = StringIO()
    stats = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    stats.print_stats(20)
    print(s.getvalue())

    # Profile composite scoring
    print("\n3. Profiling composite score analysis...")
    profiler = cProfile.Profile()
    profiler.enable()
    profile_composite_scoring()
    profiler.disable()

    s = StringIO()
    stats = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    stats.print_stats(20)
    print(s.getvalue())

    print("\n" + "=" * 80)
    print("PROFILING COMPLETE")
    print("=" * 80)
    print("\nKey insights:")
    print("- Look for functions with high 'cumtime' (cumulative time)")
    print("- High 'ncalls' with moderate time = good optimization target")
    print("- Consider caching, vectorization, or algorithm improvements")


if __name__ == "__main__":
    run_profiling()
