"""Multi-stage plaintext validation pipeline.

Validates decryption candidates through multiple stages:
1. Dictionary scoring (frequency-based)
2. Known crib matching (BERLIN, CLOCK, EASTNORTHEAST)
3. Linguistic validation (Q-Research agent)
4. Confidence scoring (0-100%)

Philosophy: "False positives kill research momentum. Use multiple independent
validators to ensure candidates are genuinely promising."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from kryptos.log_setup import setup_logging

# English letter frequencies (from large corpus)
ENGLISH_FREQ = {
    'E': 12.70,
    'T': 9.06,
    'A': 8.17,
    'O': 7.51,
    'I': 6.97,
    'N': 6.75,
    'S': 6.33,
    'H': 6.09,
    'R': 5.99,
    'D': 4.25,
    'L': 4.03,
    'C': 2.78,
    'U': 2.76,
    'M': 2.41,
    'W': 2.36,
    'F': 2.23,
    'G': 2.02,
    'Y': 1.97,
    'P': 1.93,
    'B': 1.29,
    'V': 0.98,
    'K': 0.77,
    'J': 0.15,
    'X': 0.15,
    'Q': 0.10,
    'Z': 0.07,
}


def simple_dictionary_score(text: str) -> float:
    """Calculate simple dictionary score based on letter frequencies.

    Args:
        text: Text to score

    Returns:
        Score 0.0-1.0 (higher is better)
    """
    if not text:
        return 0.0

    # Calculate letter frequencies in text
    normalized = "".join(c.upper() for c in text if c.isalpha())
    if not normalized:
        return 0.0

    freq = {}
    for c in normalized:
        freq[c] = freq.get(c, 0) + 1

    # Convert to percentages
    total = len(normalized)
    for c in freq:
        freq[c] = (freq[c] / total) * 100

    # Calculate chi-squared statistic (lower is better)
    chi_squared = 0.0
    for letter, expected in ENGLISH_FREQ.items():
        observed = freq.get(letter, 0.0)
        chi_squared += ((observed - expected) ** 2) / expected

    # Convert to 0-1 score (normalize chi-squared)
    # Typical chi-squared for English: 10-50, gibberish: 100-500+
    score = max(0.0, min(1.0, 1.0 - (chi_squared / 500)))

    return score


@dataclass
class ValidationResult:
    """Result of plaintext validation."""

    is_valid: bool
    confidence: float  # 0.0-1.0
    stage_results: dict[str, Any] = field(default_factory=dict)
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "confidence": self.confidence,
            "stage_results": self.stage_results,
            "reasons": self.reasons,
        }


class PlaintextValidator:
    """Multi-stage plaintext validator."""

    def __init__(
        self,
        known_cribs: list[str] | None = None,
        min_dictionary_score: float = 0.5,
        min_confidence: float = 0.7,
        log_level: str = "INFO",
    ):
        """Initialize validator.

        Args:
            known_cribs: Known crib words/phrases
            min_dictionary_score: Minimum dictionary score to pass
            min_confidence: Minimum confidence to mark as valid
            log_level: Logging level
        """
        self.known_cribs = [c.upper() for c in (known_cribs or [])]
        self.min_dictionary_score = min_dictionary_score
        self.min_confidence = min_confidence
        self.log = setup_logging(level=log_level, logger_name="kryptos.pipeline.validator")

    def normalize(self, text: str) -> str:
        """Normalize text for validation."""
        return "".join(c.upper() for c in text if c.isalpha())

    def stage1_dictionary_score(self, plaintext: str) -> dict[str, Any]:
        """Stage 1: Dictionary-based scoring.

        Args:
            plaintext: Plaintext to validate

        Returns:
            Dictionary with score and pass/fail
        """
        normalized = self.normalize(plaintext)

        try:
            score = simple_dictionary_score(normalized)
        except Exception as e:
            self.log.warning(f"Dictionary scoring failed: {e}")
            score = 0.0

        passed = score >= self.min_dictionary_score

        return {
            "score": score,
            "threshold": self.min_dictionary_score,
            "passed": passed,
            "reason": f"Dictionary score {score:.3f} {'>=' if passed else '<'} {self.min_dictionary_score}",
        }

    def stage2_crib_matching(self, plaintext: str) -> dict[str, Any]:
        """Stage 2: Check for known cribs.

        Args:
            plaintext: Plaintext to validate

        Returns:
            Dictionary with crib matches and pass/fail
        """
        normalized = self.normalize(plaintext)

        matches = []
        for crib in self.known_cribs:
            if crib in normalized:
                position = normalized.find(crib)
                matches.append(
                    {
                        "crib": crib,
                        "position": position,
                        "context": normalized[max(0, position - 5) : position + len(crib) + 5],
                    },
                )

        passed = len(matches) > 0

        return {
            "matches": matches,
            "match_count": len(matches),
            "passed": passed,
            "reason": f"Found {len(matches)} crib(s)" if passed else "No cribs found",
        }

    def stage3_linguistic_validation(self, plaintext: str) -> dict[str, Any]:
        """Stage 3: Linguistic validation.

        Checks for:
        - Reasonable letter frequencies
        - English word patterns
        - No excessive repetition
        - Vowel/consonant balance

        Args:
            plaintext: Plaintext to validate

        Returns:
            Dictionary with linguistic metrics and pass/fail
        """
        normalized = self.normalize(plaintext)

        if not normalized:
            return {
                "passed": False,
                "reason": "Empty plaintext",
                "metrics": {},
            }

        # Calculate metrics
        length = len(normalized)

        # Vowel ratio (English: ~40%)
        vowels = sum(1 for c in normalized if c in "AEIOUY")
        vowel_ratio = vowels / length if length > 0 else 0.0
        vowel_ok = 0.25 < vowel_ratio < 0.55

        # Check for excessive repetition
        max_repeat = max((len(list(group)) for char, group in __import__('itertools').groupby(normalized)), default=0)
        repetition_ok = max_repeat <= 4  # No more than 4 consecutive same chars

        # Check for common English digraphs
        common_digraphs = ["TH", "HE", "IN", "ER", "AN", "RE", "ON", "AT", "EN", "ND"]
        digraph_count = sum(1 for dg in common_digraphs if dg in normalized)
        digraph_ok = digraph_count >= 2 or length < 20  # At least 2 common digraphs (or short text)

        # Overall pass
        passed = vowel_ok and repetition_ok and digraph_ok

        reasons = []
        if not vowel_ok:
            reasons.append(f"Vowel ratio {vowel_ratio:.2%} outside 25-55%")
        if not repetition_ok:
            reasons.append(f"Excessive repetition ({max_repeat} consecutive chars)")
        if not digraph_ok:
            reasons.append(f"Too few common digraphs ({digraph_count} found)")

        return {
            "passed": passed,
            "metrics": {
                "vowel_ratio": vowel_ratio,
                "max_repetition": max_repeat,
                "common_digraphs": digraph_count,
            },
            "reason": " | ".join(reasons) if reasons else "Linguistic checks passed",
        }

    def stage4_confidence_scoring(self, stage_results: dict[str, dict[str, Any]]) -> dict[str, Any]:
        """Stage 4: Calculate overall confidence.

        Weighs different validation stages:
        - Dictionary score: 40%
        - Crib matching: 30%
        - Linguistic validation: 30%

        Args:
            stage_results: Results from previous stages

        Returns:
            Dictionary with confidence score and breakdown
        """
        # Extract scores (0.0-1.0)
        dict_score = stage_results["stage1_dictionary"]["score"]

        # Crib score: 1.0 if any match, 0.0 otherwise
        crib_score = 1.0 if stage_results["stage2_crib"]["passed"] else 0.0

        # Linguistic score: proportion of checks passed
        ling_metrics = stage_results["stage3_linguistic"]["metrics"]
        ling_checks = []
        if "vowel_ratio" in ling_metrics:
            ling_checks.append(0.25 < ling_metrics["vowel_ratio"] < 0.55)
        if "max_repetition" in ling_metrics:
            ling_checks.append(ling_metrics["max_repetition"] <= 4)
        if "common_digraphs" in ling_metrics:
            ling_checks.append(ling_metrics["common_digraphs"] >= 2)

        ling_score = sum(ling_checks) / len(ling_checks) if ling_checks else 0.0

        # Weighted confidence
        confidence = 0.40 * dict_score + 0.30 * crib_score + 0.30 * ling_score

        return {
            "confidence": confidence,
            "breakdown": {
                "dictionary": dict_score,
                "crib": crib_score,
                "linguistic": ling_score,
            },
            "weights": {
                "dictionary": 0.40,
                "crib": 0.30,
                "linguistic": 0.30,
            },
        }

    def validate(self, plaintext: str) -> ValidationResult:
        """Run full validation pipeline.

        Args:
            plaintext: Plaintext to validate

        Returns:
            ValidationResult with all stage results
        """
        self.log.debug(f"Validating plaintext: {plaintext[:50]}...")

        stage_results = {}
        reasons = []

        # Stage 1: Dictionary score
        stage1 = self.stage1_dictionary_score(plaintext)
        stage_results["stage1_dictionary"] = stage1
        reasons.append(stage1["reason"])
        self.log.debug(f"Stage 1 (Dictionary): {stage1['passed']}")

        # Stage 2: Crib matching
        stage2 = self.stage2_crib_matching(plaintext)
        stage_results["stage2_crib"] = stage2
        reasons.append(stage2["reason"])
        self.log.debug(f"Stage 2 (Crib): {stage2['passed']}")

        # Stage 3: Linguistic validation
        stage3 = self.stage3_linguistic_validation(plaintext)
        stage_results["stage3_linguistic"] = stage3
        reasons.append(stage3["reason"])
        self.log.debug(f"Stage 3 (Linguistic): {stage3['passed']}")

        # Stage 4: Confidence scoring
        stage4 = self.stage4_confidence_scoring(stage_results)
        stage_results["stage4_confidence"] = stage4
        confidence = stage4["confidence"]
        reasons.append(f"Overall confidence: {confidence:.1%}")
        self.log.debug(f"Stage 4 (Confidence): {confidence:.3f}")

        # Overall validation
        is_valid = confidence >= self.min_confidence

        if is_valid:
            self.log.info(f"✓ Plaintext VALID (confidence: {confidence:.1%})")
        else:
            self.log.info(f"✗ Plaintext INVALID (confidence: {confidence:.1%})")

        return ValidationResult(
            is_valid=is_valid,
            confidence=confidence,
            stage_results=stage_results,
            reasons=reasons,
        )

    def quick_validate(self, plaintext: str) -> tuple[bool, float]:
        """Quick validation (just pass/fail and confidence).

        Args:
            plaintext: Plaintext to validate

        Returns:
            Tuple of (is_valid, confidence)
        """
        result = self.validate(plaintext)
        return result.is_valid, result.confidence


def demo_validator():
    """Demonstrate validator on K1."""
    import json
    from pathlib import Path

    print("=" * 80)
    print("PLAINTEXT VALIDATOR DEMO")
    print("=" * 80)
    print()

    # Load config
    config_path = Path(__file__).parent.parent.parent.parent / "config" / "config.json"
    with open(config_path) as f:
        config = json.load(f)

    cribs = config["cribs"]

    # Create validator
    validator = PlaintextValidator(
        known_cribs=cribs,
        min_dictionary_score=0.5,
        min_confidence=0.7,
    )

    # Test cases
    test_cases = [
        ("BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION", "K1 correct plaintext"),
        ("ABCDEFGHIJKLMNOPQRSTUVWXYZABCDEFGHIJKLMNOPQRSTUVWXYZ", "Alphabet (gibberish)"),
        ("THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG", "Pangram (valid English)"),
        ("CLOCKTOWERBERLINEASTNORTHEAST", "Contains multiple cribs"),
        ("ZZZZZZZZZZZZZZZZZZZZZZZZZZZ", "All Z's (invalid)"),
    ]

    for plaintext, description in test_cases:
        print(f"\nTest: {description}")
        print(f"Text: {plaintext[:50]}{'...' if len(plaintext) > 50 else ''}")
        print()

        result = validator.validate(plaintext)

        print(f"Valid: {result.is_valid}")
        print(f"Confidence: {result.confidence:.1%}")
        print()

        print("Stage breakdown:")
        for stage_name, stage_data in result.stage_results.items():
            if "passed" in stage_data:
                print(f"  {stage_name}: {'✓' if stage_data['passed'] else '✗'} {stage_data.get('reason', '')}")
            elif "confidence" in stage_data:
                print(f"  {stage_name}: {stage_data['confidence']:.1%}")
                breakdown = stage_data.get("breakdown", {})
                for key, value in breakdown.items():
                    print(f"    - {key}: {value:.1%}")
        print()
        print("-" * 80)

    print()
    print("=" * 80)
    print("Validator ready for K4 campaign!")
    print("=" * 80)


if __name__ == "__main__":
    demo_validator()
