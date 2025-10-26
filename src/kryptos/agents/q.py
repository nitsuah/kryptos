"""Q Agent: Quality Assurance & Statistical Validation.

The Q agent performs statistical validation, sanity checks, and anomaly
detection on hypothesis testing results to ensure rigor and filter
false positives in K4 cryptanalysis.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, stdev
from typing import Any

from kryptos.log_setup import setup_logging


@dataclass
class ValidationResult:
    check_name: str
    passed: bool
    severity: str
    message: str
    details: dict[str, Any] | None = None


@dataclass
class QConfig:
    baseline_mean: float = -355.92
    baseline_stddev: float = 14.62
    sigma_2_threshold: float = -326.68
    sigma_3_threshold: float = -312.06
    min_candidates: int = 10
    log_level: str = "INFO"


class QAgent:
    def __init__(self, config: QConfig | None = None):
        self.config = config or QConfig()
        self.log = setup_logging(
            level=self.config.log_level,
            logger_name="kryptos.agents.q",
        )
        self.validations: list[ValidationResult] = []

    def validate_score(
        self,
        score: float,
        hypothesis_name: str,
    ) -> ValidationResult:
        """Validate if score is statistically significant vs random baseline.

        Args:
            score: Plaintext score to validate
            hypothesis_name: Name of hypothesis being tested

        Returns:
            ValidationResult with significance determination
        """
        baseline = self.config.baseline_mean
        sigma_2 = self.config.sigma_2_threshold
        sigma_3 = self.config.sigma_3_threshold

        if score > sigma_3:
            return ValidationResult(
                check_name="statistical_significance",
                passed=True,
                severity="info",
                message=f"STRONG SIGNAL: Score {score:.2f} exceeds 3σ threshold ({sigma_3:.2f})",
                details={
                    "score": score,
                    "baseline": baseline,
                    "threshold_3sigma": sigma_3,
                    "hypothesis": hypothesis_name,
                },
            )

        elif score > sigma_2:
            return ValidationResult(
                check_name="statistical_significance",
                passed=True,
                severity="warning",
                message=f"WEAK SIGNAL: Score {score:.2f} between 2σ ({sigma_2:.2f}) and 3σ ({sigma_3:.2f})",
                details={
                    "score": score,
                    "baseline": baseline,
                    "threshold_2sigma": sigma_2,
                    "threshold_3sigma": sigma_3,
                    "hypothesis": hypothesis_name,
                    "recommendation": "Requires additional validation",
                },
            )

        else:
            return ValidationResult(
                check_name="statistical_significance",
                passed=False,
                severity="info",
                message=f"NO SIGNAL: Score {score:.2f} below 2σ threshold ({sigma_2:.2f})",
                details={
                    "score": score,
                    "baseline": baseline,
                    "threshold_2sigma": sigma_2,
                    "hypothesis": hypothesis_name,
                },
            )

    def validate_plaintext(
        self,
        plaintext: str,
        expected_length: int = 97,
    ) -> list[ValidationResult]:
        """Perform sanity checks on candidate plaintext.

        Args:
            plaintext: Decrypted plaintext to validate
            expected_length: Expected K4 length (default 97)

        Returns:
            List of validation results
        """
        results = []

        if len(plaintext) != expected_length:
            results.append(
                ValidationResult(
                    check_name="length_check",
                    passed=False,
                    severity="error",
                    message=f"Length mismatch: got {len(plaintext)}, expected {expected_length}",
                    details={"actual": len(plaintext), "expected": expected_length},
                ),
            )
        else:
            results.append(
                ValidationResult(
                    check_name="length_check",
                    passed=True,
                    severity="info",
                    message=f"Length OK: {len(plaintext)} chars",
                ),
            )

        alpha_chars = sum(1 for c in plaintext if c.isalpha())
        alpha_ratio = alpha_chars / len(plaintext) if plaintext else 0

        if alpha_ratio < 0.9:
            results.append(
                ValidationResult(
                    check_name="alphabet_check",
                    passed=False,
                    severity="warning",
                    message=f"Low alphabet ratio: {alpha_ratio:.2%} (expected >90%)",
                    details={"alpha_ratio": alpha_ratio, "alpha_count": alpha_chars},
                ),
            )
        else:
            results.append(
                ValidationResult(
                    check_name="alphabet_check",
                    passed=True,
                    severity="info",
                    message=f"Alphabet ratio OK: {alpha_ratio:.2%}",
                ),
            )

        char_counts = {}
        for c in plaintext:
            char_counts[c] = char_counts.get(c, 0) + 1

        max_count = max(char_counts.values()) if char_counts else 0
        max_ratio = max_count / len(plaintext) if plaintext else 0

        if max_ratio > 0.15:
            results.append(
                ValidationResult(
                    check_name="repetition_check",
                    passed=False,
                    severity="warning",
                    message=f"Excessive repetition: single char appears {max_ratio:.2%} of the time",
                    details={"max_ratio": max_ratio, "max_count": max_count},
                ),
            )
        else:
            results.append(
                ValidationResult(
                    check_name="repetition_check",
                    passed=True,
                    severity="info",
                    message="Repetition check passed",
                ),
            )

        return results

    def validate_candidate_set(
        self,
        scores: list[float],
        min_candidates: int | None = None,
    ) -> ValidationResult:
        """Validate statistical properties of candidate score distribution.

        Args:
            scores: List of candidate scores
            min_candidates: Minimum expected candidates (default from config)

        Returns:
            ValidationResult for candidate set quality
        """
        min_expected = min_candidates or self.config.min_candidates

        if len(scores) < min_expected:
            return ValidationResult(
                check_name="candidate_count",
                passed=False,
                severity="warning",
                message=f"Insufficient candidates: {len(scores)} < {min_expected}",
                details={"count": len(scores), "minimum": min_expected},
            )

        if len(scores) > 1:
            score_mean = mean(scores)
            score_stddev = stdev(scores)

            return ValidationResult(
                check_name="candidate_set_distribution",
                passed=True,
                severity="info",
                message=f"Candidate set: {len(scores)} candidates, mean={score_mean:.2f}, std={score_stddev:.2f}",
                details={
                    "count": len(scores),
                    "mean": score_mean,
                    "stddev": score_stddev,
                    "min": min(scores),
                    "max": max(scores),
                },
            )

        return ValidationResult(
            check_name="candidate_count",
            passed=True,
            severity="info",
            message=f"Candidate count OK: {len(scores)}",
        )

    def detect_anomalies(
        self,
        candidates: list[dict[str, Any]],
    ) -> list[ValidationResult]:
        """Detect anomalies in candidate results that may indicate artifacts.

        Args:
            candidates: List of candidate dictionaries with 'plaintext' and 'score'

        Returns:
            List of anomaly detection results
        """
        results = []

        if not candidates:
            return results

        plaintexts = [c.get("plaintext", "") for c in candidates]
        unique_count = len(set(plaintexts))

        if unique_count < len(plaintexts):
            results.append(
                ValidationResult(
                    check_name="duplicate_plaintext",
                    passed=False,
                    severity="warning",
                    message=f"Duplicate plaintexts detected: {len(plaintexts) - unique_count} duplicates",
                    details={
                        "total": len(plaintexts),
                        "unique": unique_count,
                        "duplicates": len(plaintexts) - unique_count,
                    },
                ),
            )

        scores = [c.get("score", 0.0) for c in candidates]
        unique_scores = len(set(scores))

        if unique_scores < len(scores) / 2:
            results.append(
                ValidationResult(
                    check_name="duplicate_scores",
                    passed=False,
                    severity="warning",
                    message=f"Many duplicate scores: only {unique_scores} unique scores from {len(scores)} candidates",
                    details={"total": len(scores), "unique": unique_scores},
                ),
            )

        return results

    def generate_report(self) -> str:
        lines = ["=" * 80, "Q AGENT VALIDATION REPORT", "=" * 80, ""]

        passed = [v for v in self.validations if v.passed]
        failed = [v for v in self.validations if not v.passed]

        lines.append(f"Total checks: {len(self.validations)}")
        lines.append(f"Passed: {len(passed)}")
        lines.append(f"Failed: {len(failed)}")
        lines.append("")

        if failed:
            lines.append("Failed Checks:")
            lines.append("-" * 80)
            for v in failed:
                lines.append(f"  [{v.severity.upper()}] {v.check_name}: {v.message}")
            lines.append("")

        if passed:
            lines.append("Passed Checks:")
            lines.append("-" * 80)
            for v in passed:
                if v.severity == "warning":
                    lines.append(f"  [WARNING] {v.check_name}: {v.message}")
            lines.append("")

        lines.append("=" * 80)
        return "\n".join(lines)


def q_report(validations: list[ValidationResult]) -> str:
    agent = QAgent()
    agent.validations = validations
    return agent.generate_report()
