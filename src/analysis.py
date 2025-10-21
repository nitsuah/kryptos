"""
Module for performing frequency analysis and crib checking on text.
"""
from collections import Counter


def frequency_analysis(text):
    """Return frequency analysis of characters in the text."""
    frequencies = Counter(text)
    total = sum(frequencies.values())
    return {char: count / total for char, count in frequencies.items()}


def check_cribs(text, cribs):
    """Return list of crib substrings found in text."""
    matches = []
    for crib in cribs:
        if crib in text:
            matches.append(crib)
    return matches
