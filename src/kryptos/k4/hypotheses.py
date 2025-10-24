"""K4 hypothesis protocol and initial stubs.

A hypothesis generates candidate plaintext/key pairs for evaluation.
Each hypothesis encapsulates a specific cryptanalytic approach (Hill cipher,
transposition with constraints, Berlin Clock Vigenère, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


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


class HillCipherHypothesisStub:
    """Minimal Hill cipher hypothesis stub for initial testing.

    Returns a single deterministic candidate using a simple 2x2 key.
    Real implementation would explore key space systematically.
    """

    def generate_candidates(self, ciphertext: str, limit: int = 10) -> list[Candidate]:  # noqa: ARG002
        """Generate stub candidate(s)."""
        # Deterministic stub: return one placeholder candidate
        # Real implementation would call hill_search or hill_constraints
        stub_plaintext = "STUBPLAINTEXTFORHILL"
        stub_key = {"matrix": [[5, 12], [7, 8]], "size": 2}
        return [
            Candidate(
                id="hill_2x2_stub_5_12_7_8",
                plaintext=stub_plaintext,
                key_info=stub_key,
                score=100.0,
            ),
        ]
