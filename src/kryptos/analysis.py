"""
Module for performing frequency analysis and crib checking on text.
"""

from collections import Counter


def frequency_analysis(text):
    """Return normalized character frequency mapping.

    Returns an empty dict for empty input instead of dividing by zero.
    """
    if not text:
        return {}
    frequencies = Counter(text)
    total = sum(frequencies.values()) or 1  # safety fallback
    return {char: count / total for char, count in frequencies.items()}


def check_cribs(text, cribs):
    """Return list of crib substrings found in text.

    Skips processing if cribs list is empty.
    """
    if not cribs:
        return []
    matches = []
    for crib in cribs:
        if crib and crib in text:
            matches.append(crib)
    return matches
