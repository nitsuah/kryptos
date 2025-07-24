from collections import Counter

def frequency_analysis(text):
    frequencies = Counter(text)
    total = sum(frequencies.values())
    return {char: count / total for char, count in frequencies.items()}

def check_cribs(text, cribs):
    """
    Checks if any of the given cribs (substrings) are present in the text.
    """
    matches = []
    for crib in cribs:
        if crib in text:
            matches.append(crib)
    return matches