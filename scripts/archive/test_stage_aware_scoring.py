"""Quick test of composite_score_with_stage_analysis function."""

from __future__ import annotations

import sys
from pathlib import Path

from kryptos.k4.scoring import (
    combined_plaintext_score,
    composite_score_with_stage_analysis,
)

# Add src to path for local testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def test_stage_aware_scoring():
    """Test stage-aware scoring with sample texts."""

    # Test 1: Both stages random (no improvement)
    stage1_random = "ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZ"
    stage2_random = "ZYXWVUTSRQPONMLKJIHGFEDCBAZYXWVUTSRQPONMLKJIHGFEDCBA"

    stage1_score = combined_plaintext_score(stage1_random)
    stage2_score = combined_plaintext_score(stage2_random)

    result1 = composite_score_with_stage_analysis(stage1_random, stage2_random, stage1_score, stage2_score)

    print("Test 1: Random → Random")
    print(f"  Stage1 IOC: {result1['stage1_ioc']:.4f}")
    print(f"  Stage2 IOC: {result1['stage2_ioc']:.4f}")
    print(f"  IOC improvement: {result1['ioc_improvement']:.4f}")
    print(f"  IOC bonus: {result1['ioc_bonus']:.2f}")
    print(f"  Word bonus: {result1['word_bonus']:.2f}")
    print(f"  Freq bonus: {result1['freq_bonus']:.2f}")
    print(f"  Total bonus: {result1['total_bonus']:.2f}")
    print(f"  Base score: {result1['base_score']:.2f}")
    print(f"  Final score: {result1['final_score']:.2f}")
    print()

    # Test 2: Random → English-like (significant improvement)
    stage1_cipher = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
    stage2_english = (
        "ITWASFOUNDEDUNDERGROUNDYEARSLATERTHEYFOUNDTHECLOCKBURIEDNEARBERLINANDWASHINGTONTHEQUESTIONISWHEREDIDTHEYDIG"
    )

    stage1_score2 = combined_plaintext_score(stage1_cipher)
    stage2_score2 = combined_plaintext_score(stage2_english)

    result2 = composite_score_with_stage_analysis(stage1_cipher, stage2_english, stage1_score2, stage2_score2)

    print("Test 2: Cipher → English")
    print(f"  Stage1 IOC: {result2['stage1_ioc']:.4f}")
    print(f"  Stage2 IOC: {result2['stage2_ioc']:.4f}")
    print(f"  IOC improvement: {result2['ioc_improvement']:.4f}")
    print(f"  IOC bonus: {result2['ioc_bonus']:.2f}")
    print(f"  Word bonus: {result2['word_bonus']:.2f}")
    print(f"  Freq bonus: {result2['freq_bonus']:.2f}")
    print(f"  Total bonus: {result2['total_bonus']:.2f}")
    print(f"  Base score: {result2['base_score']:.2f}")
    print(f"  Final score: {result2['final_score']:.2f}")
    print()

    # Test 3: Partial improvement (some signals)
    stage1_partial = "QRSTUVWXYZABCDEFGHIJKLMNOPATHEEASTERLIGHTSQRSTUVWXYZABCDEF"
    stage2_better = "ITWASFOUNDUNDERGROUNDANDTHEEASTERNLIGHTSWEREVISIBLEFROMBERLIN"

    stage1_score3 = combined_plaintext_score(stage1_partial)
    stage2_score3 = combined_plaintext_score(stage2_better)

    result3 = composite_score_with_stage_analysis(stage1_partial, stage2_better, stage1_score3, stage2_score3)

    print("Test 3: Partial → Better")
    print(f"  Stage1 IOC: {result3['stage1_ioc']:.4f}")
    print(f"  Stage2 IOC: {result3['stage2_ioc']:.4f}")
    print(f"  IOC improvement: {result3['ioc_improvement']:.4f}")
    print(f"  IOC bonus: {result3['ioc_bonus']:.2f}")
    print(f"  Stage1 words: {result3['stage1_partial_words']}")
    print(f"  Stage2 words: {result3['stage2_partial_words']}")
    print(f"  Word bonus: {result3['word_bonus']:.2f}")
    print(f"  Freq bonus: {result3['freq_bonus']:.2f}")
    print(f"  Total bonus: {result3['total_bonus']:.2f}")
    print(f"  Base score: {result3['base_score']:.2f}")
    print(f"  Final score: {result3['final_score']:.2f}")
    print()

    print("✓ All tests completed successfully!")
    print()
    print("Expected behavior:")
    print("  - Test 1 should have minimal bonuses (both random)")
    print("  - Test 2 should have large bonuses (clear improvement)")
    print("  - Test 3 should have moderate bonuses (partial improvement)")


if __name__ == "__main__":
    test_stage_aware_scoring()
