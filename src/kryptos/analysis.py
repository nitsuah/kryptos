"""
Module for performing frequency analysis and crib checking on text.
"""

from collections import Counter


def frequency_analysis(text):
    if not text:
        return {}
    frequencies = Counter(text)
    total = sum(frequencies.values()) or 1
    return {char: count / total for char, count in frequencies.items()}


def check_cribs(text, cribs):
    if not cribs:
        return []
    matches = []
    for crib in cribs:
        if crib and crib in text:
            matches.append(crib)
    return matches
