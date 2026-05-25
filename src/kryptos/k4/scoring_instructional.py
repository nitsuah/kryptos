"""InstructionalScorer — vocabulary-boosted plaintext scoring for K4.

Sanborn's confirmed clues (EAST, NORTHEAST, BERLIN, CLOCK) suggest K4's
plaintext contains spatial/instructional language. This scorer adds a bonus
for words in those semantic clusters, with Levenshtein ≤1 fuzzy matching
to handle deliberate misspellings (cf. IQLUSION, DESPARATLY in K1-K3).

Designed to be puzzle-agnostic: swap INSTRUCTIONAL_VECTORS for any
domain-specific vocabulary to use with K5 or other puzzles.
"""

from __future__ import annotations

INSTRUCTIONAL_VECTORS: frozenset[str] = frozenset({
    # Cardinal / ordinal directions (confirmed Sanborn theme)
    "NORTH", "SOUTH", "EAST", "WEST",
    "NORTHEAST", "NORTHWEST", "SOUTHEAST", "SOUTHWEST",
    "NORTHERN", "SOUTHERN", "EASTERN", "WESTERN",
    # Spatial / geometric
    "BETWEEN", "ACROSS", "ABOVE", "BELOW", "BEHIND",
    "UNDERGROUND", "BENEATH", "UNDER", "WITHIN", "INSIDE",
    "ALONG", "TOWARD", "BEYOND", "AROUND",
    "DEGREES", "ANGLE", "BEARING", "DIAGONAL",
    "LATITUDE", "LONGITUDE", "COORDINATES",
    # Measurement / magnitude
    "FEET", "METERS", "YARDS", "DISTANCE",
    "INCHES", "MILES", "DEPTH", "HEIGHT",
    # Imperative / action verbs (instructional register)
    "DIG", "FIND", "LOCATE", "FOLLOW", "PROCEED",
    "TURN", "MOVE", "ENTER", "PASS", "REACH",
    "MARK", "PLACE", "POINT", "FACE", "LOOK",
    # K4/Kryptos specific vocabulary
    "CLOCK", "BERLIN", "SHADOW", "LIGHT", "LAYER",
    "INVISIBLE", "VISIBLE", "LUCID", "SLOWLY",
    "VIRTUALLY", "COMPLETELY", "ENTIRELY",
    # Common English function words that signal real prose
    "THE", "AND", "THAT", "WITH", "FROM",
    "HAVE", "THIS", "WILL", "YOUR", "WHAT",
    "WHEN", "THEY", "BEEN", "MORE", "THAN",
})

# Per-word bonus weights (longer / more specific words score higher)
_WORD_BONUSES: dict[int, float] = {
    3: 1.0,
    4: 2.0,
    5: 4.0,
    6: 6.0,
    7: 8.0,
    8: 10.0,
}
_LONG_WORD_BONUS = 12.0  # for words ≥ 9 chars


def _word_bonus(word: str) -> float:
    n = len(word)
    return _WORD_BONUSES.get(n, _LONG_WORD_BONUS if n >= 9 else 0.0)


def levenshtein(a: str, b: str) -> int:
    """Standard dynamic-programming edit distance."""
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la
    # Use single-row rolling DP to keep memory O(min(la,lb))
    if la < lb:
        a, b, la, lb = b, a, lb, la
    prev = list(range(lb + 1))
    for i, ca in enumerate(a, 1):
        curr = [i] + [0] * lb
        for j, cb in enumerate(b, 1):
            curr[j] = min(
                prev[j] + 1,       # delete
                curr[j - 1] + 1,   # insert
                prev[j - 1] + (0 if ca == cb else 1),  # substitute
            )
        prev = curr
    return prev[lb]


def _fuzzy_match(word: str, vocabulary: frozenset[str], tol: int = 1) -> str | None:
    """Return the closest vocabulary word within edit distance `tol`, or None."""
    if word in vocabulary:
        return word
    if tol == 0:
        return None
    n = len(word)
    best_word: str | None = None
    for candidate in vocabulary:
        # Fast length filter: edit distance ≥ |len_a - len_b|
        if abs(len(candidate) - n) > tol:
            continue
        if levenshtein(word, candidate) <= tol:
            # Prefer exact-length match to reduce false positives
            if best_word is None or abs(len(candidate) - n) < abs(len(best_word) - n):
                best_word = candidate
    return best_word


def _extract_windows(text: str, min_len: int = 3, max_len: int = 12) -> list[str]:
    """Extract all alpha substrings of length [min_len, max_len] from text."""
    seq = "".join(c for c in text.upper() if c.isalpha())
    windows: list[str] = []
    for length in range(min_len, min(max_len + 1, len(seq) + 1)):
        for i in range(len(seq) - length + 1):
            windows.append(seq[i : i + length])
    return windows


def instructional_score(
    text: str,
    vocabulary: frozenset[str] | None = None,
    fuzzy_tol: int = 1,
    min_word: int = 3,
    max_word: int = 12,
) -> float:
    """Score text for instructional/spatial vocabulary presence.

    Args:
        text:       Candidate plaintext.
        vocabulary: Word set to match against (default: INSTRUCTIONAL_VECTORS).
        fuzzy_tol:  Max edit distance for fuzzy match (0 = exact only, 1 = default).
        min_word:   Minimum window length to check.
        max_word:   Maximum window length to check.

    Returns:
        Float score ≥ 0. Higher = more instructional vocabulary detected.
        Normalised per-character to be length-independent.
    """
    if vocabulary is None:
        vocabulary = INSTRUCTIONAL_VECTORS

    seq = "".join(c for c in text.upper() if c.isalpha())
    if len(seq) < min_word:
        return 0.0

    total_bonus = 0.0
    # Track matched positions to avoid double-counting overlapping hits
    matched_positions: set[int] = set()

    for length in range(max_word, min_word - 1, -1):  # longest first to prefer full words
        if length > len(seq):
            continue
        for i in range(len(seq) - length + 1):
            window = seq[i : i + length]
            match = _fuzzy_match(window, vocabulary, tol=fuzzy_tol)
            if match is not None:
                positions = set(range(i, i + length))
                if not positions & matched_positions:
                    matched_positions |= positions
                    total_bonus += _word_bonus(match)

    # Normalise by text length so short and long texts are comparable
    return total_bonus * 100.0 / len(seq)


def entropy_gate(text: str, min_entropy: float = 3.8, max_entropy: float = 4.6) -> bool:
    """Return True if text's letter entropy falls within the acceptable range.

    Real English prose has Shannon entropy ≈ 4.0–4.2 bits/char.
    Random ciphertext is ~4.7; simple Caesar is the same but IC differs.
    This gate filters out obvious gibberish before expensive scoring.
    """
    import math
    from collections import Counter

    seq = "".join(c for c in text.upper() if c.isalpha())
    if len(seq) < 10:
        return True  # don't gate very short texts
    counts = Counter(seq)
    total = len(seq)
    entropy = -sum((c / total) * math.log2(c / total) for c in counts.values() if c > 0)
    return min_entropy <= entropy <= max_entropy


def combined_instructional_score(
    text: str,
    base_scorer=None,
    vocabulary: frozenset[str] | None = None,
    fuzzy_tol: int = 1,
    gate_entropy: bool = True,
) -> float:
    """Base plaintext score + instructional vocabulary bonus.

    Args:
        text:          Candidate plaintext.
        base_scorer:   Callable(text) -> float. Defaults to combined_plaintext_score.
        vocabulary:    Custom vocabulary set (default: INSTRUCTIONAL_VECTORS).
        fuzzy_tol:     Fuzzy match tolerance (default 1).
        gate_entropy:  If True, return base score only when entropy gate fails.

    Returns:
        Combined score (base + instructional bonus, or just base if gated out).
    """
    if base_scorer is None:
        from .scoring import combined_plaintext_score
        base_scorer = combined_plaintext_score

    if gate_entropy and not entropy_gate(text):
        return base_scorer(text)

    return base_scorer(text) + instructional_score(text, vocabulary=vocabulary, fuzzy_tol=fuzzy_tol)


__all__ = [
    "INSTRUCTIONAL_VECTORS",
    "levenshtein",
    "instructional_score",
    "entropy_gate",
    "combined_instructional_score",
]
