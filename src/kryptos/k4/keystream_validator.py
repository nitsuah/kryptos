"""Keystream validator for K4 crib-confirmed positions.

Computes Vigenère-equivalent shift keystreams at confirmed plaintext positions
without assuming a repeating key period. Serves as the gating predicate for
all structural attack strategies (inverse transposition sweep, keyed alphabet
realignment, composite sweep).

Puzzle-agnostic: pass any ciphertext + crib dict to use with future puzzles.
"""

from __future__ import annotations

STANDARD_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Confirmed K4 crib positions (0-indexed): label -> (plaintext_word, start_in_ciphertext)
K4_CRIBS: dict[str, tuple[str, int]] = {
    "EAST":      ("EAST",      22),
    "NORTHEAST": ("NORTHEAST", 26),
    "BERLIN":    ("BERLIN",    63),
    "CLOCK":     ("CLOCK",     69),
}

# Derived expected keystreams (shifts mod 26 under standard alphabet)
K4_EXPECTED_KEYSTREAMS: dict[str, list[int]] = {
    "EAST":      [7, 17, 3, 23],
    "NORTHEAST": [3, 1, 0, 20, 25, 6, 18, 0, 21],
    "BERLIN":    [12, 20, 24, 10, 11, 6],
    "CLOCK":     [10, 14, 17, 13, 0],
}


def compute_shifts_at_cribs(
    ciphertext: str,
    cribs: dict[str, tuple[str, int]],
    alphabet: str = STANDARD_ALPHABET,
) -> dict[str, list[int]]:
    """Compute shift keystream at each crib's confirmed position.

    Args:
        ciphertext: Raw ciphertext (non-alpha chars stripped automatically).
        cribs: Mapping of label -> (plaintext_word, start_index_0based).
        alphabet: Substitution alphabet (default: A-Z).

    Returns:
        Dict of label -> list of integer shifts mod len(alphabet).
    """
    ct = "".join(c for c in ciphertext.upper() if c.isalpha())
    n = len(alphabet)
    result: dict[str, list[int]] = {}
    for label, (plaintext, start) in cribs.items():
        plain = plaintext.upper()
        shifts: list[int] = []
        for i, p_char in enumerate(plain):
            ct_pos = start + i
            if ct_pos >= len(ct):
                break
            c_char = ct[ct_pos]
            if c_char not in alphabet or p_char not in alphabet:
                continue
            shift = (alphabet.index(c_char) - alphabet.index(p_char)) % n
            shifts.append(shift)
        result[label] = shifts
    return result


def validate_keystreams(
    observed: dict[str, list[int]],
    expected: dict[str, list[int]],
) -> dict[str, bool]:
    """Check observed keystreams against expected values.

    Returns dict of label -> True if exact match, False otherwise.
    """
    return {
        label: observed.get(label) == expected.get(label)
        for label in expected
    }


def validate_k4_cribs(
    ciphertext: str,
    alphabet: str = STANDARD_ALPHABET,
) -> dict[str, bool]:
    """Convenience wrapper: validate all four confirmed K4 cribs.

    Returns dict of crib label -> bool (True = keystream matches exactly).
    """
    observed = compute_shifts_at_cribs(ciphertext, K4_CRIBS, alphabet)
    return validate_keystreams(observed, K4_EXPECTED_KEYSTREAMS)


def crib_hit_count(
    ciphertext: str,
    cribs: dict[str, tuple[str, int]] | None = None,
    alphabet: str = STANDARD_ALPHABET,
    expected: dict[str, list[int]] | None = None,
) -> int:
    """Return how many cribs match exactly.

    Defaults to the four confirmed K4 cribs. Used as a fast filter: a
    candidate that scores 0 is uninteresting; 4 is a eureka event.
    """
    if cribs is None:
        cribs = K4_CRIBS
    if expected is None:
        expected = K4_EXPECTED_KEYSTREAMS
    observed = compute_shifts_at_cribs(ciphertext, cribs, alphabet)
    return sum(1 for label in expected if observed.get(label) == expected[label])


def keystream_summary(ciphertext: str, alphabet: str = STANDARD_ALPHABET) -> dict:
    """Full diagnostic: observed shifts, expected shifts, match status per crib."""
    observed = compute_shifts_at_cribs(ciphertext, K4_CRIBS, alphabet)
    matches = validate_keystreams(observed, K4_EXPECTED_KEYSTREAMS)
    return {
        label: {
            "observed_shifts": observed.get(label, []),
            "expected_shifts": K4_EXPECTED_KEYSTREAMS.get(label, []),
            "match": matches.get(label, False),
        }
        for label in K4_CRIBS
    }


__all__ = [
    "STANDARD_ALPHABET",
    "K4_CRIBS",
    "K4_EXPECTED_KEYSTREAMS",
    "compute_shifts_at_cribs",
    "validate_keystreams",
    "validate_k4_cribs",
    "crib_hit_count",
    "keystream_summary",
]
