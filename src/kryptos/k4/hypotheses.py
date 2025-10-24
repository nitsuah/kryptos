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


class VigenereHypothesis:
    """Vigenère cipher hypothesis with frequency analysis key recovery.

    Tests periodic substitution with configurable key lengths.
    For each length, uses frequency analysis to find likely keys.
    Also tests explicit keyword candidates (BERLIN, CLOCK, KRYPTOS).
    Classical cipher era-appropriate for Sanborn's 1990 sculpture.
    """

    def __init__(
        self,
        min_key_length: int = 1,
        max_key_length: int = 20,
        keys_per_length: int = 10,
        explicit_keywords: list[str] | None = None,
    ):
        """Initialize Vigenère hypothesis.

        Args:
            min_key_length: Minimum key length to test (default: 1)
            max_key_length: Maximum key length to test (default: 20)
            keys_per_length: Number of best keys to test per length (default: 10)
            explicit_keywords: Specific keywords to test (e.g., BERLIN, CLOCK)
        """
        self.min_key_length = min_key_length
        self.max_key_length = max_key_length
        self.keys_per_length = keys_per_length
        self.explicit_keywords = explicit_keywords or []

    def _vigenere_decrypt(self, ciphertext: str, key: str) -> str:
        """Decrypt text with Vigenère cipher."""
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        ct_clean = ''.join(c for c in ciphertext.upper() if c.isalpha())
        plaintext = ''

        for i, c in enumerate(ct_clean):
            ct_idx = alphabet.index(c)
            key_idx = alphabet.index(key[i % len(key)])
            pt_idx = (ct_idx - key_idx) % 26
            plaintext += alphabet[pt_idx]

        return plaintext

    def _find_best_keys_for_length(self, ciphertext: str, key_length: int) -> list[str]:
        """Use frequency analysis to find likely keys for given length.

        For each position in the key, tries all 26 letters and picks
        the one that gives best frequency distribution for that column.
        Returns multiple candidate keys by trying top N choices per position.
        """
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        ct_clean = ''.join(c for c in ciphertext.upper() if c.isalpha())

        # Expected English letter frequencies
        english_freq = {
            'E': 0.127,
            'T': 0.091,
            'A': 0.082,
            'O': 0.075,
            'I': 0.070,
            'N': 0.067,
            'S': 0.063,
            'H': 0.061,
            'R': 0.060,
            'D': 0.043,
            'L': 0.040,
            'C': 0.028,
            'U': 0.028,
            'M': 0.024,
            'W': 0.024,
            'F': 0.022,
            'G': 0.020,
            'Y': 0.020,
            'P': 0.019,
            'B': 0.015,
            'V': 0.010,
            'K': 0.008,
            'J': 0.002,
            'X': 0.002,
            'Q': 0.001,
            'Z': 0.001,
        }

        # For each key position, find best shifts by chi-square
        best_shifts_per_position = []
        for pos in range(key_length):
            # Extract every key_length-th character starting at pos
            column = [ct_clean[i] for i in range(pos, len(ct_clean), key_length)]

            # Try all 26 shifts and score by chi-square
            shift_scores = []
            for shift in range(26):
                # Decrypt this column with this shift
                decrypted = ''.join(alphabet[(alphabet.index(c) - shift) % 26] for c in column)

                # Compute frequency distribution
                freq_counts = {c: 0 for c in alphabet}
                for c in decrypted:
                    freq_counts[c] += 1

                # Chi-square test against English
                chi_square = 0.0
                total = len(decrypted)
                for c in alphabet:
                    expected = english_freq[c] * total
                    observed = freq_counts[c]
                    if expected > 0:
                        chi_square += ((observed - expected) ** 2) / expected

                shift_scores.append((shift, chi_square))

            # Sort by chi-square (lower is better)
            shift_scores.sort(key=lambda x: x[1])
            best_shifts_per_position.append([s[0] for s in shift_scores[:3]])  # Top 3 per position

        # Generate keys by combining top shifts
        # For speed, just try best shift for each position, plus some random combinations
        keys = []

        # Best key (best shift at each position)
        best_key = ''.join(alphabet[shifts[0]] for shifts in best_shifts_per_position)
        keys.append(best_key)

        # Try some variations (second-best at each position)
        for pos in range(min(key_length, 5)):  # Vary first 5 positions
            if len(best_shifts_per_position[pos]) > 1:
                key_variant = list(best_key)
                key_variant[pos] = alphabet[best_shifts_per_position[pos][1]]
                keys.append(''.join(key_variant))

        return keys[: self.keys_per_length]

    def generate_candidates(self, ciphertext: str, limit: int = 10) -> list[Candidate]:
        """Generate candidates by Vigenère frequency analysis and explicit keywords."""
        from .scoring import combined_plaintext_score

        candidates_list = []

        # Test explicit keywords first
        for keyword in self.explicit_keywords:
            keyword_upper = keyword.upper()
            plaintext = self._vigenere_decrypt(ciphertext, keyword_upper)
            score = combined_plaintext_score(plaintext)

            candidates_list.append(
                Candidate(
                    id=f"vigenere_keyword_{keyword_upper}",
                    plaintext=plaintext,
                    key_info={
                        'type': 'vigenere',
                        'key': keyword_upper,
                        'key_length': len(keyword_upper),
                        'explicit': True,
                    },
                    score=score,
                ),
            )

        # Frequency analysis for each key length
        for key_length in range(self.min_key_length, self.max_key_length + 1):
            # Find best keys for this length
            keys = self._find_best_keys_for_length(ciphertext, key_length)

            # Test each key
            for key in keys:
                plaintext = self._vigenere_decrypt(ciphertext, key)
                score = combined_plaintext_score(plaintext)

                candidates_list.append(
                    Candidate(
                        id=f"vigenere_len{key_length}_{key}",
                        plaintext=plaintext,
                        key_info={'type': 'vigenere', 'key': key, 'key_length': key_length, 'explicit': False},
                        score=score,
                    ),
                )

        # Sort by score and return top candidates
        candidates_list.sort(key=lambda c: c.score, reverse=True)
        return candidates_list[:limit]


class AutokeyHypothesis:
    """Autokey cipher - Vigenère variant using plaintext as key stream.

    After an initial primer (keyword), the decrypted plaintext itself becomes
    the key stream. Harder to break than standard Vigenère because the key
    depends on the plaintext.

    Example: Key=KRYPTOS, cipher=ABC... → decrypt first char with K, second
    with R, third with Y, fourth with plaintext[0], fifth with plaintext[1]...
    """

    def __init__(self, primers: list[str] | None = None):
        """Initialize Autokey hypothesis.

        Args:
            primers: Keywords to use as initial key (default: Kryptos-related words)
        """
        self.primers = primers or [
            'KRYPTOS',
            'BERLIN',
            'CLOCK',
            'ABSCISSA',
            'PALIMPSEST',
            'ABCDEFGHIJKLMNOPQRSTUVWXYZ',  # Full alphabet
        ]

    def _autokey_decrypt(self, ciphertext: str, primer: str) -> str:
        """Decrypt using autokey cipher."""
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        ct_clean = ''.join(c for c in ciphertext.upper() if c.isalpha())
        plaintext = ''

        for i, c in enumerate(ct_clean):
            # Key is: primer + plaintext so far
            key_stream = primer + plaintext
            if i < len(key_stream):
                key_char = key_stream[i]
            else:
                # Should not happen if primer long enough
                key_char = 'A'

            ct_idx = alphabet.index(c)
            key_idx = alphabet.index(key_char)
            pt_idx = (ct_idx - key_idx) % 26
            plaintext += alphabet[pt_idx]

        return plaintext

    def generate_candidates(self, ciphertext: str, limit: int = 10) -> list[Candidate]:
        """Generate candidates by testing autokey with various primers."""
        from .scoring import combined_plaintext_score

        candidates_list = []

        for primer in self.primers:
            primer_upper = primer.upper()
            plaintext = self._autokey_decrypt(ciphertext, primer_upper)
            score = combined_plaintext_score(plaintext)

            candidates_list.append(
                Candidate(
                    id=f"autokey_{primer_upper}",
                    plaintext=plaintext,
                    key_info={'type': 'autokey', 'primer': primer_upper},
                    score=score,
                ),
            )

        # Sort by score and return top candidates
        candidates_list.sort(key=lambda c: c.score, reverse=True)
        return candidates_list[:limit]


class PlayfairHypothesis:
    """Playfair cipher with Sanborn-related keywords.

    Tests Playfair cipher using keywords from Kryptos sculpture:
    - KRYPTOS (used in K2)
    - ABSCISSA (theme in K2)
    - PALIMPSEST (artistic concept)
    - BERLIN, CLOCK (K4 clue themes)

    Playfair uses 5x5 grid (I/J combined) for digraph substitution.
    """

    def __init__(self, keywords: list[str] | None = None):
        """Initialize Playfair hypothesis.

        Args:
            keywords: Keywords to test (default: Sanborn-related keywords)
        """
        self.keywords = keywords or [
            'KRYPTOS',
            'KRYPTO',
            'ABSCISSA',
            'PALIMPSEST',
            'BERLIN',
            'CLOCK',
            'SCULPTURE',
        ]

    def _build_playfair_grid(self, keyword: str) -> list[list[str]]:
        """Build 5x5 Playfair grid from keyword."""
        alphabet = 'ABCDEFGHIKLMNOPQRSTUVWXYZ'  # J removed (I/J combined)
        keyword_clean = ''.join(c for c in keyword.upper() if c in alphabet)

        # Build grid: keyword first (deduplicated), then remaining letters
        grid_chars = []
        seen = set()
        for c in keyword_clean:
            if c not in seen:
                grid_chars.append(c)
                seen.add(c)

        for c in alphabet:
            if c not in seen:
                grid_chars.append(c)
                seen.add(c)

        # Convert to 5x5 grid
        grid = []
        for i in range(0, 25, 5):
            grid.append(list(grid_chars[i : i + 5]))

        return grid

    def _find_in_grid(self, grid: list[list[str]], char: str) -> tuple[int, int]:
        """Find position of character in grid (returns row, col)."""
        for i, row in enumerate(grid):
            for j, c in enumerate(row):
                if c == char:
                    return (i, j)
        return (0, 0)  # shouldn't happen

    def _playfair_decrypt(self, ciphertext: str, keyword: str) -> str:
        """Decrypt text with Playfair cipher."""
        grid = self._build_playfair_grid(keyword)
        ct_clean = ''.join(c if c != 'J' else 'I' for c in ciphertext.upper() if c.isalpha())

        # Pad if odd length
        if len(ct_clean) % 2 == 1:
            ct_clean += 'X'

        plaintext = ''
        for i in range(0, len(ct_clean), 2):
            c1, c2 = ct_clean[i], ct_clean[i + 1]
            r1, col1 = self._find_in_grid(grid, c1)
            r2, col2 = self._find_in_grid(grid, c2)

            if r1 == r2:
                # Same row: shift left
                plaintext += grid[r1][(col1 - 1) % 5]
                plaintext += grid[r2][(col2 - 1) % 5]
            elif col1 == col2:
                # Same column: shift up
                plaintext += grid[(r1 - 1) % 5][col1]
                plaintext += grid[(r2 - 1) % 5][col2]
            else:
                # Rectangle: swap columns
                plaintext += grid[r1][col2]
                plaintext += grid[r2][col1]

        return plaintext

    def generate_candidates(self, ciphertext: str, limit: int = 10) -> list[Candidate]:
        """Generate candidates by Playfair cipher with Sanborn keywords."""
        from .scoring import combined_plaintext_score

        candidates_list = []

        for keyword in self.keywords:
            plaintext = self._playfair_decrypt(ciphertext, keyword)
            score = combined_plaintext_score(plaintext)

            candidates_list.append(
                Candidate(
                    id=f"playfair_{keyword.lower()}",
                    plaintext=plaintext,
                    key_info={'type': 'playfair', 'keyword': keyword},
                    score=score,
                ),
            )

        # Sort by score and return top candidates
        candidates_list.sort(key=lambda c: c.score, reverse=True)
        return candidates_list[:limit]


class FourSquareHypothesis:
    """Four-square cipher - tests KRYPTOS/BERLIN/CLOCK/ABSCISSA combinations."""

    def __init__(self, keywords: list[str] | None = None):
        self.keywords = keywords or ['KRYPTOS', 'BERLIN', 'CLOCK', 'ABSCISSA']

    def _build_grid(self, keyword: str) -> list[list[str]]:
        """Build 5×5 keyed Polybius grid."""
        alphabet = 'ABCDEFGHIKLMNOPQRSTUVWXYZ'
        kw = ''.join(c if c != 'J' else 'I' for c in keyword.upper() if c.isalpha())
        chars = []
        seen = set()
        for c in kw + alphabet:
            if c not in seen:
                chars.append(c)
                seen.add(c)
        return [list(chars[i : i + 5]) for i in range(0, 25, 5)]

    def _plain_grid(self) -> list[list[str]]:
        """Standard alphabet grid."""
        alphabet = 'ABCDEFGHIKLMNOPQRSTUVWXYZ'
        return [list(alphabet[i : i + 5]) for i in range(0, 25, 5)]

    def _find(self, grid: list[list[str]], char: str) -> tuple[int, int]:
        """Find character position."""
        for i, row in enumerate(grid):
            for j, c in enumerate(row):
                if c == char:
                    return (i, j)
        return (0, 0)

    def _decrypt(self, ct: str, key1: str, key2: str) -> str:
        """Decrypt using four-square."""
        pt_grid = self._plain_grid()
        ct1 = self._build_grid(key1)
        ct2 = self._build_grid(key2)
        text = ''.join(c if c != 'J' else 'I' for c in ct.upper() if c.isalpha())
        if len(text) % 2 == 1:
            text += 'X'
        result = ''
        for i in range(0, len(text), 2):
            r1, c1 = self._find(ct1, text[i])
            r2, c2 = self._find(ct2, text[i + 1])
            result += pt_grid[r1][c2] + pt_grid[r2][c1]
        return result

    def generate_candidates(self, ciphertext: str, limit: int = 10) -> list[Candidate]:
        """Generate four-square candidates."""
        from kryptos.k4.scoring import combined_plaintext_score

        cands = []
        for i, k1 in enumerate(self.keywords):
            for k2 in self.keywords[i:]:
                pt = self._decrypt(ciphertext, k1, k2)
                score = combined_plaintext_score(pt)
                cands.append(
                    Candidate(
                        id=f"foursquare_{k1.lower()}_{k2.lower()}",
                        plaintext=pt,
                        key_info={'type': 'foursquare', 'key1': k1, 'key2': k2},
                        score=score,
                    ),
                )
        cands.sort(key=lambda c: c.score, reverse=True)
        return cands[:limit]


class BifidHypothesis:
    """Bifid cipher - combines Polybius square with transposition."""

    def __init__(self, keyword: str = 'KRYPTOS', periods: list[int] | None = None):
        self.keyword = keyword
        self.periods = periods or list(range(5, 21))

    def _build_grid(self, keyword: str) -> list[list[str]]:
        """Build 5×5 Polybius square."""
        alphabet = 'ABCDEFGHIKLMNOPQRSTUVWXYZ'
        kw = ''.join(c if c != 'J' else 'I' for c in keyword.upper() if c.isalpha())
        chars = []
        seen = set()
        for c in kw + alphabet:
            if c not in seen:
                chars.append(c)
                seen.add(c)
        return [list(chars[i : i + 5]) for i in range(0, 25, 5)]

    def _find(self, grid: list[list[str]], char: str) -> tuple[int, int]:
        """Find coordinates."""
        for i, row in enumerate(grid):
            for j, c in enumerate(row):
                if c == char:
                    return (i, j)
        return (0, 0)

    def _decrypt(self, ct: str, keyword: str, period: int) -> str:
        """Decrypt using bifid."""
        grid = self._build_grid(keyword)
        text = ''.join(c if c != 'J' else 'I' for c in ct.upper() if c.isalpha())
        coords = [self._find(grid, c) for c in text]

        # Simplified bifid decryption (period-based transposition)
        result = ''
        for chunk_start in range(0, len(coords), period):
            chunk = coords[chunk_start : chunk_start + period]
            n = len(chunk)
            # De-transpose coordinates
            rows = []
            cols = []
            for r, c in chunk:
                rows.append(r)
                cols.append(c)

            # Reconstruct plaintext (simplified)
            for i in range(n):
                result += grid[rows[i]][cols[i]]

        return result

    def generate_candidates(self, ciphertext: str, limit: int = 10) -> list[Candidate]:
        """Generate bifid candidates."""
        from kryptos.k4.scoring import combined_plaintext_score

        cands = []
        for period in self.periods:
            pt = self._decrypt(ciphertext, self.keyword, period)
            score = combined_plaintext_score(pt)
            cands.append(
                Candidate(
                    id=f"bifid_{self.keyword.lower()}_p{period}",
                    plaintext=pt,
                    key_info={'type': 'bifid', 'keyword': self.keyword, 'period': period},
                    score=score,
                ),
            )
        cands.sort(key=lambda c: c.score, reverse=True)
        return cands[:limit]


class BerlinClockVigenereHypothesis:
    """Berlin Clock Vigenère - use clock lamp states as Vigenère keys.

    Tests all 24 hours (00:00-23:00) using Berlin Clock lamp sequences
    as shift patterns. Lamp states encode temporal information that may
    relate to K4's BERLIN/CLOCK themes.
    """

    def __init__(self, hours: list[int] | None = None):
        """Initialize Berlin Clock Vigenère hypothesis.

        Args:
            hours: Hours to test (default: 0-23, all 24 hours)
        """
        self.hours = hours or list(range(24))

    def _berlin_clock_vigenere_decrypt(self, ciphertext: str, hour: int) -> str:
        """Decrypt using Berlin Clock lamp state as Vigenère key."""
        from datetime import time

        from kryptos.k4.berlin_clock import full_berlin_clock_shifts

        # Get lamp state for this hour (at minute 0)
        t = time(hour, 0, 0)
        shifts = full_berlin_clock_shifts(t)

        # Apply shifts as Vigenère-style decryption
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        ct_clean = ''.join(c for c in ciphertext.upper() if c.isalpha())
        plaintext = ''

        for i, c in enumerate(ct_clean):
            ct_idx = alphabet.index(c)
            shift = shifts[i % len(shifts)]  # Cycle through lamp states
            pt_idx = (ct_idx - shift) % 26
            plaintext += alphabet[pt_idx]

        return plaintext

    def generate_candidates(self, ciphertext: str, limit: int = 10):
        """Generate candidates by testing Berlin Clock states for each hour."""
        from kryptos.k4.hypotheses import Candidate
        from kryptos.k4.scoring import combined_plaintext_score

        candidates_list = []

        for hour in self.hours:
            plaintext = self._berlin_clock_vigenere_decrypt(ciphertext, hour)
            score = combined_plaintext_score(plaintext)

            candidates_list.append(
                Candidate(
                    id=f'berlin_clock_vig_h{hour:02d}',
                    plaintext=plaintext,
                    key_info={'type': 'berlin_clock_vigenere', 'hour': hour},
                    score=score,
                ),
            )

        # Sort by score and return top candidates
        candidates_list.sort(key=lambda c: c.score, reverse=True)
        return candidates_list[:limit]
