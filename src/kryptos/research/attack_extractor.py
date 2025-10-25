"""Extract attack parameters from academic papers.

Analyzes cryptanalysis papers to extract:
- Cipher types mentioned
- Attack methods used
- Key parameters (lengths, cribs, positions)
- Success rates and computational costs
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .paper_search import Paper


@dataclass
class ExtractedAttack:
    """Attack parameters extracted from academic paper."""

    cipher_type: str
    attack_method: str  # "frequency analysis", "crib dragging", etc
    key_parameters: dict[str, Any] = field(default_factory=dict)
    crib_text: str | None = None
    crib_position: int | None = None
    success_rate: float | None = None  # If reported
    computational_cost: str | None = None  # e.g., "O(n^2)", "10^6 ops"
    source_paper: str | None = None  # Paper ID
    confidence: float = 0.0  # How confident extraction is (0-1)

    def to_attack_parameters(self) -> dict[str, Any]:
        """Convert to AttackParameters format for provenance logging."""
        return {
            "cipher_type": self.cipher_type,
            "key_or_params": self.key_parameters,
            "crib_text": self.crib_text,
            "crib_position": self.crib_position,
            "additional_params": {
                "attack_method": self.attack_method,
                "source": f"academic:{self.source_paper}",
            },
        }


class AttackExtractor:
    """Extract attack parameters from academic papers."""

    def __init__(self):
        """Initialize attack extractor."""
        # Patterns for detecting cipher types
        self.cipher_patterns = {
            "vigenere": [
                r"vigen[èe]re",
                r"polyalphabetic\s+substitution",
                r"periodic\s+key",
            ],
            "hill": [
                r"hill\s+cipher",
                r"matrix\s+cipher",
                r"linear\s+transformation",
            ],
            "transposition": [
                r"transposition",
                r"columnar",
                r"route\s+cipher",
                r"permutation\s+cipher",
            ],
            "substitution": [
                r"substitution",
                r"monoalphabetic",
                r"simple\s+substitution",
            ],
        }

        # Patterns for attack methods
        self.attack_patterns = {
            "frequency_analysis": [
                r"frequency\s+analysis",
                r"letter\s+distribution",
                r"statistical\s+analysis",
            ],
            "crib_dragging": [
                r"crib",
                r"known\s+plaintext",
                r"probable\s+word",
            ],
            "brute_force": [
                r"brute\s*force",
                r"exhaustive\s+search",
                r"key\s+space\s+search",
            ],
            "genetic_algorithm": [
                r"genetic\s+algorithm",
                r"evolutionary\s+algorithm",
                r"fitness\s+function",
            ],
            "simulated_annealing": [
                r"simulated\s+annealing",
                r"metropolis",
                r"temperature\s+schedule",
            ],
        }

        # Patterns for key lengths
        self.key_length_pattern = r"key\s+length\s+(?:of\s+)?(\d+)"
        self.key_range_pattern = r"key\s+lengths?\s+(?:from\s+)?(\d+)\s*(?:-|to)\s*(\d+)"

    def extract_from_paper(self, paper: Paper) -> list[ExtractedAttack]:
        """Extract all attacks mentioned in paper.

        Args:
            paper: Paper to analyze

        Returns:
            List of extracted attacks
        """
        attacks = []
        text = f"{paper.title} {paper.abstract}".lower()

        # Detect cipher types
        cipher_types = self._detect_cipher_types(text)

        # Detect attack methods
        attack_methods = self._detect_attack_methods(text)

        # Extract key parameters
        key_params = self._extract_key_parameters(text)

        # Extract cribs
        cribs = self._extract_cribs(text)

        # Generate attacks for each cipher+method combination
        for cipher in cipher_types:
            for method in attack_methods:
                attack = ExtractedAttack(
                    cipher_type=cipher,
                    attack_method=method,
                    key_parameters=key_params.get(cipher, {}),
                    crib_text=cribs[0] if cribs else None,
                    source_paper=paper.paper_id,
                    confidence=0.7,  # Medium confidence for automated extraction
                )
                attacks.append(attack)

        return attacks

    def extract_from_papers(self, papers: list[Paper]) -> list[ExtractedAttack]:
        """Extract attacks from multiple papers.

        Args:
            papers: List of papers

        Returns:
            Combined list of extracted attacks
        """
        all_attacks = []
        for paper in papers:
            attacks = self.extract_from_paper(paper)
            all_attacks.extend(attacks)
        return all_attacks

    def _detect_cipher_types(self, text: str) -> list[str]:
        """Detect cipher types mentioned in text."""
        detected = []
        for cipher_type, patterns in self.cipher_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    detected.append(cipher_type)
                    break
        return detected

    def _detect_attack_methods(self, text: str) -> list[str]:
        """Detect attack methods mentioned in text."""
        detected = []
        for method, patterns in self.attack_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    detected.append(method)
                    break
        return detected

    def _extract_key_parameters(self, text: str) -> dict[str, dict[str, Any]]:
        """Extract key parameters like lengths."""
        params = {}

        # Extract single key length
        match = re.search(self.key_length_pattern, text, re.IGNORECASE)
        if match:
            length = int(match.group(1))
            params["vigenere"] = {"key_length": length}

        # Extract key range
        match = re.search(self.key_range_pattern, text, re.IGNORECASE)
        if match:
            min_len = int(match.group(1))
            max_len = int(match.group(2))
            params["vigenere"] = {
                "key_length_min": min_len,
                "key_length_max": max_len,
            }

        return params

    def _extract_cribs(self, text: str) -> list[str]:
        """Extract potential crib words mentioned."""
        # Common crib patterns
        crib_pattern = r'(?:crib|known\s+(?:word|plaintext))\s+["\']([A-Za-z]+)["\']'
        matches = re.findall(crib_pattern, text, re.IGNORECASE)
        return [m.upper() for m in matches]


def demo_attack_extractor():
    """Demonstrate attack extraction."""
    print("=" * 80)
    print("ATTACK EXTRACTION DEMO")
    print("=" * 80)
    print()

    from .paper_search import Paper

    # Mock paper about Vigenère
    paper = Paper(
        paper_id="arxiv:1234.5678",
        title="Breaking Vigenère Ciphers with Frequency Analysis",
        authors=["Smith, J."],
        abstract="We present a method for breaking Vigenère ciphers with key lengths "
        "from 5 to 20 using frequency analysis and crib dragging. "
        'Our approach uses the known plaintext "BERLIN" to accelerate the search. '
        "Tested on 1000 ciphertexts with 95% success rate.",
        year=2020,
        venue="arXiv",
        keywords=["vigenere", "frequency analysis"],
        cipher_types=["vigenere"],
    )

    extractor = AttackExtractor()
    attacks = extractor.extract_from_paper(paper)

    print(f"Extracted {len(attacks)} attacks from paper:")
    print()
    for i, attack in enumerate(attacks, 1):
        print(f"Attack {i}:")
        print(f"  Cipher: {attack.cipher_type}")
        print(f"  Method: {attack.attack_method}")
        print(f"  Parameters: {attack.key_parameters}")
        print(f"  Crib: {attack.crib_text}")
        print(f"  Confidence: {attack.confidence}")
        print()


if __name__ == "__main__":
    demo_attack_extractor()
