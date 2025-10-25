"""Test dictionary-based scoring vs n-gram scoring."""

from __future__ import annotations

import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / 'src'))

from kryptos.k4.transposition_analysis import (  # noqa: E402
    score_bigrams,
    score_combined,
    score_combined_with_words,
    score_trigrams,
    score_words,
)


def test_scoring_methods():
    """Compare different scoring methods on various texts."""
    print("=" * 80)
    print("SCORING METHOD COMPARISON")
    print("=" * 80)

    test_cases = [
        ("Good English", "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"),
        ("Real sentence", "ATTACKATDAWNWITHFULLFORCE"),
        ("K1 snippet", "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHT"),
        ("Scrambled", "ZQXJKVWYPBFGHMTRNLCDAOEIUS"),
        ("Random letters", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
        ("Partial words", "THEQZXJKVBROWNFOXJUMPS"),
    ]

    for name, text in test_cases:
        print(f"\n{name}: {text}")
        print("-" * 80)

        bigram = score_bigrams(text)
        trigram = score_trigrams(text)
        combined = score_combined(text)
        words = score_words(text)
        combined_words = score_combined_with_words(text)

        print(f"  Bigrams:           {bigram:.4f}")
        print(f"  Trigrams:          {trigram:.4f}")
        print(f"  Combined (n-gram): {combined:.4f}")
        print(f"  Words:             {words:.4f}")
        print(f"  Combined (+ words): {combined_words:.4f}")


def test_discrimination():
    """Test how well scoring discriminates plaintext from gibberish."""
    print("\n\n" + "=" * 80)
    print("DISCRIMINATION TEST: Plaintext vs Gibberish")
    print("=" * 80)

    plaintext = "SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRIS"
    gibberish = "SLWODLWSSSASEAYHLAPSATBPYRFGDLMYOTSYEESREAIN"  # Scrambled

    print(f"\nPlaintext: {plaintext}")
    print(f"Gibberish: {gibberish}")
    print()

    methods = {
        "Bigrams": score_bigrams,
        "Trigrams": score_trigrams,
        "Combined": score_combined,
        "Words": score_words,
        "Combined+Words": score_combined_with_words,
    }

    for name, score_func in methods.items():
        pt_score = score_func(plaintext)
        gb_score = score_func(gibberish)
        ratio = pt_score / gb_score if gb_score > 0 else float('inf')

        print(f"{name:15s}: PT={pt_score:.4f}, GB={gb_score:.4f}, Ratio={ratio:.2f}x")

    print("\n" + "=" * 80)
    print("Higher ratio = better discrimination")


def test_word_detection():
    """Test word detection on known plaintext."""
    print("\n\n" + "=" * 80)
    print("WORD DETECTION TEST")
    print("=" * 80)

    test_texts = [
        ("All words", "THECATANDTHEDOG", 1.0),  # Expect high score
        ("No words", "ZQXJKVWYPBFGHMT", 0.0),  # Expect low score
        ("Mixed", "THECATZQXDOG", 0.5),  # Expect medium
    ]

    for name, text, expected_min in test_texts:
        score = score_words(text)
        status = "PASS" if score >= expected_min else "FAIL"
        print(f"{name:15s}: {text:20s} -> {score:.3f} [{status}]")


if __name__ == "__main__":
    test_scoring_methods()
    test_discrimination()
    test_word_detection()

    print("\n" + "=" * 80)
    print("SCORING COMPARISON COMPLETE")
    print("=" * 80)
