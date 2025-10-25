"""Debug word detection to see what's being matched."""

from __future__ import annotations

import sys
from pathlib import Path

repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root / 'src'))

from kryptos.k4.scoring import WORDLIST  # noqa: E402


def debug_word_detection(text: str):
    """Show what words are being detected."""
    text = ''.join(c for c in text.upper() if c.isalpha())

    print(f"\nText: {text}")
    print(f"Length: {len(text)}")
    print("-" * 80)

    # Strategy 1: Non-overlapping longest match
    matched = [False] * len(text)
    found_words = []

    for word_len in range(7, 2, -1):
        for i in range(len(text) - word_len + 1):
            candidate = text[i : i + word_len]
            if candidate in WORDLIST and not any(matched[i : i + word_len]):
                found_words.append((i, candidate))
                for j in range(i, i + word_len):
                    matched[j] = True

    print("Strategy 1 (non-overlapping longest):")
    for pos, word in sorted(found_words):
        print(f"  Position {pos:2d}: {word}")

    matched_count = sum(matched)
    print(f"\nMatched: {matched_count}/{len(text)} chars ({matched_count/len(text):.1%})")

    # Show coverage
    coverage = ''.join(text[i] if matched[i] else '.' for i in range(len(text)))
    print(f"Coverage: {coverage}")

    # Strategy 2: Greedy left-to-right
    print("\nStrategy 2 (greedy left-to-right):")
    remaining = text
    pos = 0
    total_matched = 0

    while remaining:
        found = False
        for word_len in range(min(10, len(remaining)), 2, -1):
            if remaining[:word_len] in WORDLIST:
                word = remaining[:word_len]
                print(f"  Position {pos:2d}: {word}")
                total_matched += word_len
                remaining = remaining[word_len:]
                pos += word_len
                found = True
                break
        if not found:
            print(f"  Position {pos:2d}: . (skip)")
            remaining = remaining[1:]
            pos += 1

    print(f"\nMatched: {total_matched}/{len(text)} chars ({total_matched/len(text):.1%})")


if __name__ == "__main__":
    test_cases = [
        "THECATANDTHEDOG",
        "THEQUICKBROWNFOX",
        "SLOWLYDESPARATELY",
        "ATTACKATDAWN",
    ]

    print("=" * 80)
    print("WORD DETECTION DEBUG")
    print("=" * 80)

    for text in test_cases:
        debug_word_detection(text)

    # Check if specific words are in WORDLIST
    print("\n" + "=" * 80)
    print("WORDLIST CHECK")
    print("=" * 80)

    check_words = ["THE", "CAT", "AND", "DOG", "ATTACK", "DAWN", "SLOWLY", "DESPERATELY"]
    for word in check_words:
        status = "✓" if word in WORDLIST else "✗"
        print(f"{status} {word}")
