"""Candidate submission gate checks for K4 hypotheses.

This module provides pure, offline checks that any candidate plaintext
must satisfy before being considered for submission. These checks are
necessary but not sufficient conditions; passing them does not grant
permission to submit.
"""

from __future__ import annotations

from .hypothesis_check import check_hypothesis, crib_verdict


def check_candidate(plaintext: str, family: str, key: str) -> dict[str, object]:
    """Run candidate gate checks on a proposed K4 solution.

    Args:
        plaintext: Proposed plaintext (case-insensitive, non-letters ignored).
        family: Cipher family ("vigenere" or "beaufort").
        key: Candidate key.

    Returns:
        Dict with:
        - "normalised": uppercase A-Z only version of plaintext
        - "length_ok": True if normalised has exactly 97 letters
        - "cribs": dict from crib_verdict(normalised)
        - "cribs_ok": True if all crib checks pass
        - "reproduces": True if check_hypothesis(family, key) reproduces normalised
        - "all_checks_pass": True if length_ok and cribs_ok and reproduces

    Raises:
        ValueError: If family is unknown (delegated to check_hypothesis).
    """
    # Normalise to uppercase letters only
    normalised = "".join(char for char in plaintext.upper() if "A" <= char <= "Z")

    # Length check: K4 plaintext is 97 letters
    length_ok = len(normalised) == 97

    # Crib checks
    cribs = crib_verdict(normalised)
    cribs_ok = all(cribs.values())

    # Reproduction check
    hypothesis_result = check_hypothesis(family, key)
    reproduces = hypothesis_result["plaintext"] == normalised

    return {
        "normalised": normalised,
        "length_ok": length_ok,
        "cribs": cribs,
        "cribs_ok": cribs_ok,
        "reproduces": reproduces,
        "all_checks_pass": length_ok and cribs_ok and reproduces,
    }
