"""K4 hypothesis protocol and implementations.

A hypothesis generates candidate plaintext/key pairs for evaluation.
Each hypothesis encapsulates a specific cryptanalytic approach (Hill cipher,
transposition with constraints, Berlin Clock Vigenère, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .hill_cipher import invertible_2x2_keys
from .hill_search import score_decryptions
from .transposition import search_columnar


@dataclass(slots=True)
class Candidate:
    """A candidate decryption result from a hypothesis."""

    id: str  # unique identifier (e.g., "hill_2x2_key_5_12_7_8")
    plaintext: str  # decrypted text fragment
    key_info: dict  # hypothesis-specific key details
    score: float  # composite score (higher is better)


class Hypothesis(Protocol):
    """Protocol for K4 cryptanalytic hypotheses."""

    def generate_candidates(self, ciphertext: str, limit: int = 10) -> list[Candidate]:
        """Generate up to `limit` candidate decryptions.

        Args:
            ciphertext: The ciphertext to analyze (typically K4's 97 chars).
            limit: Maximum number of candidates to return.

        Returns:
            List of Candidate objects, ranked by score (highest first).
        """
        ...


class HillCipher2x2Hypothesis:
    """Exhaustive 2x2 Hill cipher hypothesis.

    Enumerates all ~158,000 invertible 2x2 matrices mod 26,
    decrypts K4 with each key, scores results, and returns top candidates.
    """

    def generate_candidates(self, ciphertext: str, limit: int = 10) -> list[Candidate]:
        """Generate candidates by exhaustive 2x2 Hill cipher search."""
        # Generate all invertible keys
        keys = invertible_2x2_keys()

        # Score all decryptions (this will test all ~158k keys)
        results = score_decryptions(ciphertext, keys, limit=len(keys))

        # Convert to Candidate objects
        candidates = []
        for i, result in enumerate(results[:limit]):
            key_matrix = result['key']
            candidates.append(
                Candidate(
                    id=f"hill_2x2_{i}_{key_matrix[0][0]}_{key_matrix[0][1]}_{key_matrix[1][0]}_{key_matrix[1][1]}",
                    plaintext=result['text'],
                    key_info={'matrix': key_matrix, 'size': 2},
                    score=result['score'],
                ),
            )

        return candidates


class BerlinClockTranspositionHypothesis:
    """Columnar transposition constrained by Berlin Clock periods.

    Tests column widths related to clock interpretation:
    - 1-12 (clock hours, 12-hour format)
    - 1-24 (military time hours)
    - Common small widths (5, 10, 15 for 5-min blocks)

    Uses adaptive pruning to avoid exhaustive factorial search.
    """

    def __init__(self, widths: list[int] | None = None, prune: bool = True, max_perms: int = 5000):
        """Initialize transposition hypothesis.

        Args:
            widths: Column widths to test (default: Berlin Clock periods)
            prune: Whether to use adaptive pruning (default: True)
            max_perms: Max permutations per width (default: 5000)
        """
        self.widths = widths or [5, 6, 7, 8, 10, 11, 12, 15, 24]
        self.prune = prune
        self.max_perms = max_perms

    def generate_candidates(self, ciphertext: str, limit: int = 10) -> list[Candidate]:
        """Generate candidates by Berlin Clock-constrained transposition search."""
        all_results = []
        for n_cols in self.widths:
            # Limit permutations to avoid factorial explosion
            max_perms_actual = min(self.max_perms, 720)  # 720 = 6! (reasonable upper bound)
            results = search_columnar(
                ciphertext,
                min_cols=n_cols,
                max_cols=n_cols,
                max_perms_per_width=max_perms_actual,
                prune=self.prune,
                partial_length=30,
                partial_min_score=-400.0,  # prune obviously bad candidates early
            )
            all_results.extend(results)  # Sort by score and deduplicate
        all_results.sort(key=lambda r: r['score'], reverse=True)
        seen_texts = set()
        unique_results = []
        for r in all_results:
            if r['text'] not in seen_texts:
                seen_texts.add(r['text'])
                unique_results.append(r)
                if len(unique_results) >= limit:
                    break

        # Convert to Candidate objects
        candidates = []
        for result in unique_results[:limit]:
            perm_str = '_'.join(str(p) for p in result['perm'])
            candidates.append(
                Candidate(
                    id=f"transposition_cols{result['cols']}_{perm_str[:50]}",  # truncate long perms
                    plaintext=result['text'],
                    key_info={'columns': result['cols'], 'permutation': result['perm']},
                    score=result['score'],
                ),
            )

        return candidates


class SimpleSubstitutionHypothesis:
    """Simple substitution ciphers: Caesar/ROT-N, Atbash, Reverse.

    These are trivial classical ciphers unlikely to be K4's method,
    but worth testing for completeness to definitively rule out.
    """

    def generate_candidates(self, ciphertext: str, limit: int = 10) -> list[Candidate]:
        """Generate candidates by testing all simple substitutions."""
        ct_clean = ''.join(c for c in ciphertext.upper() if c.isalpha())
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        candidates_list = []

        from .scoring import combined_plaintext_score

        # Caesar/ROT-N (26 rotations)
        for shift in range(26):
            plaintext = ''
            for c in ct_clean:
                idx = alphabet.index(c)
                plaintext += alphabet[(idx - shift) % 26]

            score = combined_plaintext_score(plaintext)

            candidates_list.append(
                Candidate(
                    id=f"caesar_rot{shift}",
                    plaintext=plaintext,
                    key_info={'type': 'caesar', 'shift': shift},
                    score=score,
                ),
            )

        # Atbash (A↔Z, B↔Y, etc.)
        plaintext_atbash = ''
        for c in ct_clean:
            idx = alphabet.index(c)
            plaintext_atbash += alphabet[25 - idx]

        score_atbash = combined_plaintext_score(plaintext_atbash)
        candidates_list.append(
            Candidate(
                id="atbash",
                plaintext=plaintext_atbash,
                key_info={'type': 'atbash'},
                score=score_atbash,
            ),
        )

        # Reverse
        plaintext_reverse = ct_clean[::-1]
        score_reverse = combined_plaintext_score(plaintext_reverse)
        candidates_list.append(
            Candidate(
                id="reverse",
                plaintext=plaintext_reverse,
                key_info={'type': 'reverse'},
                score=score_reverse,
            ),
        )

        # Sort by score and return top candidates
        candidates_list.sort(key=lambda c: c.score, reverse=True)
        return candidates_list[:limit]
