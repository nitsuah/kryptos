"""Q-Research Integration: Academic cryptanalysis techniques for Kryptos.

This module implements advanced patterns and attack strategies from academic
research papers, including:
- Digraph frequency analysis
- Palindrome pattern detection
- Vigenère cryptanalysis strategies
- Transposition cipher techniques
- Statistical analysis for polyalphabetic ciphers

References:
- "The Kryptos Sculpture: Cracking K4" - Various research papers
- Classical cryptanalysis texts (Friedman, Gaines, Sinkov)
- Modern computational approaches
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DigraphAnalysis:
    """Results from digraph frequency analysis."""

    digraph_counts: dict[str, int] = field(default_factory=dict)
    total_digraphs: int = 0
    top_digraphs: list[tuple[str, int]] = field(default_factory=list)
    rare_digraphs: list[tuple[str, int]] = field(default_factory=list)
    expected_english: dict[str, float] = field(default_factory=dict)
    deviation_score: float = 0.0


@dataclass
class PalindromePattern:
    """Detected palindrome pattern."""

    text: str
    position: int
    length: int
    confidence: float
    pattern_type: str  # "exact", "approximate", "spaced"


@dataclass
class VigenereMetrics:
    """Metrics for Vigenère cipher analysis."""

    key_length_candidates: list[int] = field(default_factory=list)
    ic_values: dict[int, float] = field(default_factory=dict)
    kasiski_distances: list[int] = field(default_factory=list)
    likely_key_length: int = 0
    confidence: float = 0.0


@dataclass
class TranspositionHint:
    """Hint about possible transposition."""

    method: str  # "columnar", "rail_fence", "route", "etc"
    period: int
    evidence: str
    confidence: float


class QResearchAnalyzer:
    """Advanced cryptanalysis using academic research techniques.

    This analyzer implements patterns and strategies from research papers
    to enhance attack generation and candidate validation.
    """

    def __init__(self):
        """Initialize Q-Research analyzer."""
        # English digraph frequencies (top 20)
        self.english_digraphs = {
            "TH": 3.56,
            "HE": 3.07,
            "IN": 2.43,
            "ER": 2.05,
            "AN": 1.99,
            "RE": 1.85,
            "ON": 1.76,
            "AT": 1.49,
            "EN": 1.45,
            "ND": 1.35,
            "TI": 1.34,
            "ES": 1.34,
            "OR": 1.28,
            "TE": 1.20,
            "OF": 1.17,
            "ED": 1.17,
            "IS": 1.13,
            "IT": 1.12,
            "AL": 1.09,
            "AR": 1.07,
        }

        # English letter frequencies
        self.english_frequencies = {
            "E": 12.70,
            "T": 9.06,
            "A": 8.17,
            "O": 7.51,
            "I": 6.97,
            "N": 6.75,
            "S": 6.33,
            "H": 6.09,
            "R": 5.99,
            "D": 4.25,
            "L": 4.03,
            "C": 2.78,
            "U": 2.76,
            "M": 2.41,
            "W": 2.36,
            "F": 2.23,
            "G": 2.02,
            "Y": 1.97,
            "P": 1.93,
            "B": 1.29,
            "V": 0.98,
            "K": 0.77,
            "J": 0.15,
            "X": 0.15,
            "Q": 0.10,
            "Z": 0.07,
        }

    def analyze_digraphs(self, ciphertext: str) -> DigraphAnalysis:
        """Analyze digraph frequencies in ciphertext.

        Args:
            ciphertext: Text to analyze

        Returns:
            Digraph analysis results
        """
        # Clean text
        text = re.sub(r"[^A-Z]", "", ciphertext.upper())

        if len(text) < 2:
            return DigraphAnalysis()

        # Count digraphs
        digraphs = [text[i : i + 2] for i in range(len(text) - 1)]
        counts = Counter(digraphs)

        # Sort by frequency
        sorted_digraphs = counts.most_common()
        total = len(digraphs)

        # Calculate deviation from English
        deviation = 0.0
        for digraph, count in sorted_digraphs[:20]:
            observed_freq = (count / total) * 100
            expected_freq = self.english_digraphs.get(digraph, 0.1)
            deviation += abs(observed_freq - expected_freq)

        return DigraphAnalysis(
            digraph_counts=dict(counts),
            total_digraphs=total,
            top_digraphs=sorted_digraphs[:20],
            rare_digraphs=sorted_digraphs[-20:] if len(sorted_digraphs) > 20 else [],
            expected_english=self.english_digraphs,
            deviation_score=deviation,
        )

    def detect_palindromes(self, text: str, min_length: int = 3) -> list[PalindromePattern]:
        """Detect palindrome patterns in text.

        Palindromes might indicate:
        - Key reuse in polyalphabetic ciphers
        - Symmetric encryption patterns
        - Message boundaries

        Args:
            text: Text to search
            min_length: Minimum palindrome length

        Returns:
            List of detected palindrome patterns
        """
        text = re.sub(r"[^A-Z]", "", text.upper())
        palindromes = []

        # Exact palindromes
        for length in range(min_length, len(text) // 2 + 1):
            for i in range(len(text) - length + 1):
                substr = text[i : i + length]
                if substr == substr[::-1]:
                    palindromes.append(
                        PalindromePattern(
                            text=substr,
                            position=i,
                            length=length,
                            confidence=1.0,
                            pattern_type="exact",
                        ),
                    )

        # Approximate palindromes (allow 1-2 mismatches)
        for length in range(min_length + 2, min(len(text) // 2 + 1, 20)):
            for i in range(len(text) - length + 1):
                substr = text[i : i + length]
                reversed_substr = substr[::-1]
                mismatches = sum(1 for a, b in zip(substr, reversed_substr) if a != b)

                if 0 < mismatches <= 2:
                    confidence = 1.0 - (mismatches / length)
                    if confidence >= 0.7:
                        palindromes.append(
                            PalindromePattern(
                                text=substr,
                                position=i,
                                length=length,
                                confidence=confidence,
                                pattern_type="approximate",
                            ),
                        )

        return palindromes

    def vigenere_analysis(self, ciphertext: str, max_key_length: int = 20) -> VigenereMetrics:
        """Analyze text for Vigenère cipher characteristics.

        Uses:
        - Kasiski examination (repeated sequence distances)
        - Index of Coincidence (IC) for each key length
        - Statistical methods

        Args:
            ciphertext: Ciphertext to analyze
            max_key_length: Maximum key length to test

        Returns:
            Vigenère cipher metrics
        """
        text = re.sub(r"[^A-Z]", "", ciphertext.upper())

        if len(text) < 20:
            return VigenereMetrics()

        # Kasiski examination
        kasiski_distances = self._kasiski_examination(text)

        # Index of Coincidence for different key lengths
        ic_values = {}
        for key_len in range(1, min(max_key_length + 1, len(text) // 5)):
            ic_values[key_len] = self._calculate_ic_for_key_length(text, key_len)

        # Find most likely key length
        likely_key_length = 0
        best_ic = 0.0

        # English IC ≈ 0.067, random IC ≈ 0.038
        target_ic = 0.067

        for key_len, ic in ic_values.items():
            if abs(ic - target_ic) < abs(best_ic - target_ic):
                best_ic = ic
                likely_key_length = key_len

        # Confidence based on IC proximity to English
        confidence = 1.0 - min(abs(best_ic - target_ic) / target_ic, 1.0)

        # Prefer key lengths that match Kasiski distances
        key_length_candidates = self._rank_key_lengths(ic_values, kasiski_distances)

        return VigenereMetrics(
            key_length_candidates=key_length_candidates,
            ic_values=ic_values,
            kasiski_distances=kasiski_distances,
            likely_key_length=likely_key_length,
            confidence=confidence,
        )

    def detect_transposition_hints(self, ciphertext: str) -> list[TranspositionHint]:
        """Detect hints of transposition ciphers.

        Transposition ciphers:
        - Preserve letter frequencies (IC ≈ 0.067)
        - Disrupt digraph frequencies
        - May have periodic patterns

        Args:
            ciphertext: Ciphertext to analyze

        Returns:
            List of transposition hints
        """
        text = re.sub(r"[^A-Z]", "", ciphertext.upper())
        hints = []

        if len(text) < 20:
            return hints

        # Check letter frequency preservation
        ic = self._calculate_ic(text)
        letter_freq_score = self._compare_letter_frequencies(text)

        if ic > 0.060 and letter_freq_score > 0.7:
            # High IC + good letter freq = likely transposition
            hints.append(
                TranspositionHint(
                    method="unknown",
                    period=0,
                    evidence="High IC with preserved letter frequencies",
                    confidence=min(ic / 0.067, 1.0) * letter_freq_score,
                ),
            )

        # Check for columnar patterns (divisors of text length)
        length = len(text)
        for period in range(2, min(length // 2, 50)):
            if length % period == 0:
                # Test if columns show patterns
                columns = [text[i::period] for i in range(period)]
                column_ic = sum(self._calculate_ic(col) for col in columns) / period

                if column_ic < 0.050:  # Columns are more random = likely columnar
                    hints.append(
                        TranspositionHint(
                            method="columnar",
                            period=period,
                            evidence=f"Text length {length} divisible by {period}, low column IC",
                            confidence=0.6,
                        ),
                    )

        # Rail fence detection (diagonal patterns)
        for rails in range(2, min(length // 3, 10)):
            # Rail fence creates specific index patterns
            # This is a heuristic check
            if self._check_rail_fence_pattern(text, rails):
                hints.append(
                    TranspositionHint(
                        method="rail_fence",
                        period=rails,
                        evidence=f"Diagonal pattern consistent with {rails} rails",
                        confidence=0.5,
                    ),
                )

        return hints

    def suggest_attack_strategies(self, ciphertext: str) -> dict[str, Any]:
        """Suggest attack strategies based on analysis.

        Args:
            ciphertext: Ciphertext to analyze

        Returns:
            Dictionary of suggested strategies with priorities
        """
        strategies = {
            "substitution": {"priority": 0.0, "methods": []},
            "transposition": {"priority": 0.0, "methods": []},
            "polyalphabetic": {"priority": 0.0, "methods": []},
            "hybrid": {"priority": 0.0, "methods": []},
        }

        # Analyze characteristics
        digraphs = self.analyze_digraphs(ciphertext)
        vigenere = self.vigenere_analysis(ciphertext)
        transposition = self.detect_transposition_hints(ciphertext)
        ic = self._calculate_ic(re.sub(r"[^A-Z]", "", ciphertext.upper()))

        # Simple substitution (IC ≈ 0.067, digraphs preserved)
        if ic > 0.060 and digraphs.deviation_score < 50:
            strategies["substitution"]["priority"] = 0.8
            strategies["substitution"]["methods"] = ["frequency_analysis", "hill_climbing", "genetic"]

        # Polyalphabetic (IC < 0.050, periodic patterns)
        if ic < 0.050 and vigenere.confidence > 0.5:
            strategies["polyalphabetic"]["priority"] = 0.9
            strategies["polyalphabetic"]["methods"] = [f"vigenere_k{k}" for k in vigenere.key_length_candidates[:3]]

        # Transposition (IC ≈ 0.067, disrupted digraphs)
        if ic > 0.060 and digraphs.deviation_score > 50 and transposition:
            strategies["transposition"]["priority"] = 0.7
            strategies["transposition"]["methods"] = [
                h.method for h in sorted(transposition, key=lambda x: x.confidence, reverse=True)
            ]

        # Hybrid (medium IC, mixed signals)
        if 0.045 < ic < 0.060:
            strategies["hybrid"]["priority"] = 0.6
            strategies["hybrid"]["methods"] = ["vigenere_then_transpose", "transpose_then_substitute"]

        return strategies

    # Helper methods

    def _kasiski_examination(self, text: str, min_length: int = 3) -> list[int]:
        """Find repeated sequences and their distances (Kasiski method)."""
        distances = []

        for length in range(min_length, min(len(text) // 4, 10)):
            positions = defaultdict(list)

            for i in range(len(text) - length + 1):
                ngram = text[i : i + length]
                positions[ngram].append(i)

            for _ngram, pos_list in positions.items():
                if len(pos_list) > 1:
                    for i in range(len(pos_list) - 1):
                        distance = pos_list[i + 1] - pos_list[i]
                        distances.append(distance)

        return sorted(set(distances))

    def _calculate_ic(self, text: str) -> float:
        """Calculate Index of Coincidence."""
        if len(text) < 2:
            return 0.0

        counts = Counter(text)
        n = len(text)
        numerator = sum(count * (count - 1) for count in counts.values())
        denominator = n * (n - 1)

        return numerator / denominator if denominator > 0 else 0.0

    def _calculate_ic_for_key_length(self, text: str, key_length: int) -> float:
        """Calculate average IC for cosets of a given key length."""
        if key_length > len(text) // 5:
            return 0.0

        cosets = [text[i::key_length] for i in range(key_length)]
        ic_values = [self._calculate_ic(coset) for coset in cosets if len(coset) > 1]

        return sum(ic_values) / len(ic_values) if ic_values else 0.0

    def _compare_letter_frequencies(self, text: str) -> float:
        """Compare letter frequencies to English (0.0-1.0)."""
        if not text:
            return 0.0

        counts = Counter(text)
        total = len(text)

        # Chi-squared test
        chi_squared = 0.0
        for letter, expected_pct in self.english_frequencies.items():
            observed = counts.get(letter, 0)
            expected = (expected_pct / 100) * total

            if expected > 0:
                chi_squared += ((observed - expected) ** 2) / expected

        # Convert to 0-1 score (lower chi-squared = better match)
        # Typical chi-squared for random text ≈ 500-1000
        # For English text ≈ 20-50
        score = max(0.0, 1.0 - (chi_squared / 500))

        return score

    def _rank_key_lengths(self, ic_values: dict[int, float], kasiski_distances: list[int]) -> list[int]:
        """Rank key length candidates by IC and Kasiski evidence."""
        target_ic = 0.067
        scores = {}

        for key_len, ic in ic_values.items():
            # IC score
            ic_score = 1.0 - min(abs(ic - target_ic) / target_ic, 1.0)

            # Kasiski score (does key_len divide common distances?)
            kasiski_score = 0.0
            if kasiski_distances:
                divisor_count = sum(1 for d in kasiski_distances if d % key_len == 0)
                kasiski_score = divisor_count / len(kasiski_distances)

            # Combined score
            scores[key_len] = ic_score * 0.7 + kasiski_score * 0.3

        # Sort by score
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [key_len for key_len, score in ranked[:5]]

    def _check_rail_fence_pattern(self, text: str, rails: int) -> bool:
        """Heuristic check for rail fence pattern."""
        # Rail fence creates a specific reading order
        # This is a simplified check
        if len(text) < rails * 3:
            return False

        # Check if there are periodic patterns in IC across positions
        position_ics = []
        for i in range(rails):
            substring = text[i::rails]
            if len(substring) > 1:
                position_ics.append(self._calculate_ic(substring))

        if not position_ics:
            return False

        # If position ICs are similar, might be rail fence
        avg_ic = sum(position_ics) / len(position_ics)
        variance = sum((ic - avg_ic) ** 2 for ic in position_ics) / len(position_ics)

        return variance < 0.001  # Low variance = similar ICs


def demo_q_research():
    """Demonstrate Q-Research analyzer."""
    print("=" * 80)
    print("Q-RESEARCH ANALYZER DEMO")
    print("=" * 80)
    print()

    analyzer = QResearchAnalyzer()

    # Test with K4 (partial for demo)
    k4_sample = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

    print("## DIGRAPH ANALYSIS")
    digraphs = analyzer.analyze_digraphs(k4_sample)
    print(f"Total digraphs: {digraphs.total_digraphs}")
    print(f"Top 5: {digraphs.top_digraphs[:5]}")
    print(f"Deviation from English: {digraphs.deviation_score:.2f}")
    print()

    print("## PALINDROME DETECTION")
    palindromes = analyzer.detect_palindromes(k4_sample)
    print(f"Found {len(palindromes)} palindromes")
    for pal in palindromes[:3]:
        print(f"  {pal.text} at position {pal.position} ({pal.pattern_type})")
    print()

    print("## VIGENÈRE ANALYSIS")
    vigenere = analyzer.vigenere_analysis(k4_sample)
    print(f"Likely key length: {vigenere.likely_key_length} (confidence: {vigenere.confidence:.2f})")
    print(f"Candidates: {vigenere.key_length_candidates[:5]}")
    print()

    print("## TRANSPOSITION HINTS")
    trans_hints = analyzer.detect_transposition_hints(k4_sample)
    print(f"Found {len(trans_hints)} hints")
    for hint in trans_hints[:3]:
        print(f"  {hint.method}: {hint.evidence} ({hint.confidence:.2f})")
    print()

    print("## ATTACK STRATEGIES")
    strategies = analyzer.suggest_attack_strategies(k4_sample)
    for category, details in sorted(strategies.items(), key=lambda x: x[1]["priority"], reverse=True):
        if details["priority"] > 0:
            print(f"  {category.upper()}: priority {details['priority']:.2f}")
            print(f"    Methods: {', '.join(details['methods'][:3])}")


if __name__ == "__main__":
    demo_q_research()
