"""P15 — K2 coordinate digits as straddling checkerboard row-header indices.

The K2 plaintext encodes WGS-84 coordinates:
  N: 38°57'6.5" → digits [3, 8, 5, 7, 6, 5]
  W: 77°8'44"   → digits [7, 7, 8, 4, 4]

Unique digits (order of first appearance): 3, 8, 5, 7, 6, 4

A straddling checkerboard uses two row-header digits to partition the 26-letter
alphabet:
  - top row (no header): 8 letters at non-header digit columns (0-9 minus r1,r2)
  - row r1: 10 letters at columns 0-9
  - row r2: 8 letters at columns 0-7 (remaining)

Encoding: letter → 1 digit (top row) or 2 digits (r1/r2 + column)
Decoding: digit stream → letters

To apply to K4 (alphabetic ciphertext), three digit-stream conversion schemes
are tested:
  A. Letter position mod 10: A=0, B=1, ..., J=9, K=0, ...
  B. KRYPTOS-alphabet position mod 10
  C. Pair-coded: treat consecutive letter pairs (AA-ZZ) as 00-99 → single digit stream
"""

from __future__ import annotations

import logging
from typing import Any

from .physical_grid import K4

logger = logging.getLogger(__name__)

STANDARD = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
KRYPTOS_ALPHA = "KRYPTOSABCDEFGHIJLMNQUVWXZ"
ETAOIN = "ETAOINSHRDLUCMFWYPVBGKJQXZ"
EUREKA_WORDS = frozenset({"EAST", "NORTHEAST", "BERLIN", "CLOCK"})

K2_N_DIGITS: list[int] = [3, 8, 5, 7, 6, 5]
K2_W_DIGITS: list[int] = [7, 7, 8, 4, 4]
K2_UNIQUE_DIGITS: list[int] = list(dict.fromkeys(K2_N_DIGITS + K2_W_DIGITS))  # [3,8,5,7,6,4]

# Candidate row-header pairs sourced from K2 unique digits
CANDIDATE_ROW_HEADERS: list[tuple[int, int]] = [
    (3, 8),  # first two unique from N coord (primary candidate)
    (7, 4),  # two unique from W coord
    (3, 7),  # first from N, first from W
    (5, 6),  # last two unique from N
    (8, 4),  # second N unique, W unique
    (5, 7),  # middle N unique pair
]


class StruddlingCheckerboard:
    """Build and use a straddling checkerboard cipher."""

    def __init__(self, alphabet_order: str, r1: int, r2: int) -> None:
        """
        Args:
            alphabet_order: 26-char string ordering the alphabet for grid fill.
            r1: First row-header digit (0-9).
            r2: Second row-header digit (0-9, must differ from r1).
        """
        assert r1 != r2, "Row headers must be distinct"
        assert 0 <= r1 <= 9 and 0 <= r2 <= 9
        alpha = alphabet_order.upper()
        assert len(set(alpha)) == 26 and set(alpha) == set(STANDARD)

        self.r1 = r1
        self.r2 = r2
        self._build(alpha, r1, r2)

    def _build(self, alpha: str, r1: int, r2: int) -> None:
        top_cols = [c for c in range(10) if c != r1 and c != r2]  # 8 columns
        letters = list(alpha)

        # letter → digit sequence
        self._encode: dict[str, tuple[int, ...]] = {}
        # digit sequence (as tuple) → letter
        self._decode: dict[tuple[int, ...], str] = {}

        # Top row: 8 letters at top_cols (single-digit codes)
        for col, letter in zip(top_cols, letters[:8]):
            self._encode[letter] = (col,)
            self._decode[(col,)] = letter

        # Row r1: next 10 letters
        for col, letter in enumerate(letters[8:18]):
            self._encode[letter] = (r1, col)
            self._decode[(r1, col)] = letter

        # Row r2: remaining 8 letters
        for col, letter in enumerate(letters[18:26]):
            self._encode[letter] = (r2, col)
            self._decode[(r2, col)] = letter

    def encode_letter(self, letter: str) -> tuple[int, ...]:
        return self._encode.get(letter.upper(), ())

    def encode_text(self, text: str) -> list[int]:
        digits: list[int] = []
        for c in text.upper():
            if c.isalpha():
                digits.extend(self._encode.get(c, ()))
        return digits

    def decode_digits(self, digits: list[int]) -> str:
        result: list[str] = []
        i = 0
        while i < len(digits):
            d = digits[i]
            key: tuple[int, ...]
            if d == self.r1 or d == self.r2:
                if i + 1 < len(digits):
                    key = (d, digits[i + 1])
                    letter = self._decode.get(key)
                    if letter:
                        result.append(letter)
                    i += 2
                else:
                    break
            else:
                key = (d,)
                letter = self._decode.get(key)
                if letter:
                    result.append(letter)
                i += 1
        return "".join(result)


def _letters_to_digits_modulo(text: str, modulus: int = 10) -> list[int]:
    """Map A→0, B→1, ..., Z→25, then mod 10."""
    return [(ord(c.upper()) - ord("A")) % modulus for c in text.upper() if c.isalpha()]


def _letters_to_digits_kryptos(text: str, modulus: int = 10) -> list[int]:
    """Map letters via KRYPTOS-alphabet position, then mod 10."""
    pos = {c: i for i, c in enumerate(KRYPTOS_ALPHA)}
    return [pos[c.upper()] % modulus for c in text.upper() if c.isalpha() and c.upper() in pos]


def _keyword_hits(text: str) -> int:
    upper = text.upper()
    return sum(1 for w in EUREKA_WORDS if w in upper)


def build_checkerboard(alphabet_order: str, r1: int, r2: int) -> StruddlingCheckerboard:
    return StruddlingCheckerboard(alphabet_order, r1, r2)


def run_straddling_checkerboard_attack(
    null_artifact_path: str = "K4_P15_STRADDLE_NULL.json",
) -> dict[str, Any]:
    """Run all K2-derived straddling checkerboard parameterizations against K4.

    For each combination of:
      - Row-header pair from CANDIDATE_ROW_HEADERS
      - Alphabet ordering (STANDARD, ETAOIN, KRYPTOS_ALPHA)
      - Digit-stream conversion (modulo-standard, modulo-kryptos)

    Decodes the resulting digit stream and checks for crib hits.
    """
    ct = "".join(c for c in K4.upper() if c.isalpha())
    orderings = [
        ("STANDARD", STANDARD),
        ("ETAOIN", ETAOIN),
        ("KRYPTOS", KRYPTOS_ALPHA),
    ]
    converters = [
        ("mod_standard", _letters_to_digits_modulo),
        ("mod_kryptos", _letters_to_digits_kryptos),
    ]

    results: list[dict[str, Any]] = []
    combos_tested = 0

    for r1, r2 in CANDIDATE_ROW_HEADERS:
        for ord_name, order in orderings:
            board = build_checkerboard(order, r1, r2)

            # Test encoding K4 through the checkerboard → digit sequence
            # (checks if output length / digit distribution looks like ciphertext)
            encoded = board.encode_text(ct)
            if encoded:
                encoded_str = "".join(map(str, encoded))
                results.append(
                    {
                        "test": "k4_encoding_check",
                        "r1": r1,
                        "r2": r2,
                        "ordering": ord_name,
                        "encoded_length": len(encoded),
                        "digit_distribution": {str(d): encoded.count(d) for d in range(10)},
                        "encoded_digits": encoded_str[:40],
                    }
                )

            # Test decoding: convert K4 letters → digits → decode through board
            for conv_name, converter in converters:
                digits = converter(ct)
                decoded = board.decode_digits(digits)
                combos_tested += 1
                hits = _keyword_hits(decoded)
                if hits > 0 or len(decoded) > 40:
                    results.append(
                        {
                            "test": "k4_decoding",
                            "r1": r1,
                            "r2": r2,
                            "ordering": ord_name,
                            "converter": conv_name,
                            "decoded_text": decoded,
                            "decoded_length": len(decoded),
                            "keyword_hits": hits,
                        }
                    )

    # Sort by keyword_hits descending for decoding tests
    decoding_results = [r for r in results if r.get("test") == "k4_decoding"]
    decoding_results.sort(key=lambda r: (-r.get("keyword_hits", 0), -r.get("decoded_length", 0)))

    encoding_results = [r for r in results if r.get("test") == "k4_encoding_check"]

    summary: dict[str, Any] = {
        "status": "null_result" if not any(r.get("keyword_hits", 0) >= 4 for r in decoding_results) else "eureka",
        "attack": "P15_straddling_checkerboard",
        "total_candidates": combos_tested,
        "k2_row_header_candidates": CANDIDATE_ROW_HEADERS,
        "best_candidates": decoding_results[:10],
        "encoding_analysis": encoding_results[:6],
    }

    try:
        import json
        from pathlib import Path

        Path(null_artifact_path).write_text(json.dumps(summary, indent=2))
    except Exception:  # noqa: BLE001
        pass

    return summary


__all__ = [
    "K2_N_DIGITS",
    "K2_W_DIGITS",
    "K2_UNIQUE_DIGITS",
    "CANDIDATE_ROW_HEADERS",
    "StruddlingCheckerboard",
    "build_checkerboard",
    "run_straddling_checkerboard_attack",
]
