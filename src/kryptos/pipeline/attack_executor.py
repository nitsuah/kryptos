"""Attack execution wrappers with provenance logging.

Wraps common cryptanalysis functions to automatically log attacks via AttackLogger.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from kryptos.ciphers import vigenere_decrypt
from kryptos.k4.transposition_analysis import (
    solve_columnar_permutation_exhaustive,
    solve_columnar_permutation_simulated_annealing_multi_start,
)
from kryptos.provenance.attack_log import AttackLogger, AttackParameters, AttackRecord, AttackResult


class AttackExecutor:
    """Executes attacks with automatic provenance logging."""

    def __init__(self, logger: AttackLogger | None = None, log_dir: Path | None = None):
        """Initialize attack executor.

        Args:
            logger: Existing AttackLogger instance, or None to create new one
            log_dir: Directory for logs (if creating new logger)
        """
        self.logger = logger or AttackLogger(log_dir=log_dir)

    def vigenere_attack(
        self,
        ciphertext: str,
        key: str,
        crib_text: str | None = None,
        crib_position: int | None = None,
        tags: list[str] | None = None,
    ) -> tuple[str, AttackRecord]:
        """Execute Vigenère attack with logging.

        Args:
            ciphertext: Ciphertext to decrypt
            key: Vigenère key
            crib_text: Optional known plaintext crib
            crib_position: Position of crib in plaintext
            tags: Optional tags for this attack

        Returns:
            (plaintext, attack_record) tuple
        """
        params = AttackParameters(
            cipher_type="vigenere",
            key_or_params={"key": key, "key_length": len(key)},
            crib_text=crib_text,
            crib_position=crib_position,
        )

        start_time = time.time()

        try:
            plaintext = vigenere_decrypt(ciphertext, key)
            execution_time = time.time() - start_time

            # Basic success check: does it contain the crib?
            success = False
            if crib_text and plaintext:
                success = crib_text.upper() in plaintext.upper()
            else:
                # No crib - consider it tentative success if we got output
                success = bool(plaintext)

            result = AttackResult(
                success=success,
                plaintext_candidate=plaintext,
                confidence_scores={},  # Will be filled by validation agents
                execution_time_seconds=execution_time,
                metadata={"method": "vigenere_decrypt"},
            )

        except Exception as e:
            execution_time = time.time() - start_time
            result = AttackResult(
                success=False,
                plaintext_candidate=None,
                execution_time_seconds=execution_time,
                error_message=str(e),
            )
            plaintext = ""

        # Log the attack
        attack_id, is_duplicate = self.logger.log_attack(
            ciphertext=ciphertext,
            parameters=params,
            result=result,
            tags=tags or [],
        )

        # Get the logged record
        fingerprint = params.fingerprint()
        record = self.logger.attack_index[fingerprint]

        return plaintext, record

    def transposition_attack(
        self,
        ciphertext: str,
        period: int,
        method: str = "simulated_annealing",
        crib_text: str | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> tuple[tuple[list[int], float], AttackRecord]:
        """Execute columnar transposition attack with logging.

        Args:
            ciphertext: Ciphertext to analyze
            period: Transposition period
            method: "exhaustive" or "simulated_annealing"
            crib_text: Optional known plaintext crib
            tags: Optional tags
            **kwargs: Additional parameters for solver

        Returns:
            ((permutation, score), attack_record) tuple
        """
        params = AttackParameters(
            cipher_type="transposition",
            key_or_params={"period": period, "method": method},
            crib_text=crib_text,
            additional_params=kwargs,
        )

        start_time = time.time()

        try:
            if method == "exhaustive":
                permutation, score = solve_columnar_permutation_exhaustive(ciphertext, period, **kwargs)
            elif method == "simulated_annealing":
                permutation, score = solve_columnar_permutation_simulated_annealing_multi_start(
                    ciphertext,
                    period,
                    **kwargs,
                )
            else:
                raise ValueError(f"Unknown method: {method}")

            execution_time = time.time() - start_time

            # Decrypt to get plaintext candidate
            from kryptos.k4.transposition_analysis import apply_columnar_permutation_reverse

            plaintext = apply_columnar_permutation_reverse(ciphertext, period, permutation)

            # Success check: high score and/or crib match
            success = score > 0.15  # Reasonable English text threshold
            if crib_text and plaintext:
                if crib_text.upper() in plaintext.upper():
                    success = True

            result = AttackResult(
                success=success,
                plaintext_candidate=plaintext,
                confidence_scores={"transposition_score": score},
                execution_time_seconds=execution_time,
                metadata={
                    "method": method,
                    "permutation": permutation,
                    "period": period,
                },
            )

        except Exception as e:
            execution_time = time.time() - start_time
            result = AttackResult(
                success=False,
                plaintext_candidate=None,
                execution_time_seconds=execution_time,
                error_message=str(e),
            )
            permutation = list(range(period))
            score = 0.0

        # Log the attack
        attack_id, is_duplicate = self.logger.log_attack(
            ciphertext=ciphertext,
            parameters=params,
            result=result,
            tags=tags or [],
        )

        # Get the logged record
        fingerprint = params.fingerprint()
        record = self.logger.attack_index[fingerprint]

        return (permutation, score), record

    def hill_attack(
        self,
        ciphertext: str,
        matrix_size: int,
        key_matrix: list[list[int]],
        crib_text: str | None = None,
        tags: list[str] | None = None,
    ) -> tuple[str, AttackRecord]:
        """Execute Hill cipher attack with logging.

        Args:
            ciphertext: Ciphertext to decrypt
            matrix_size: Size of Hill cipher matrix (2 or 3)
            key_matrix: Hill cipher key matrix
            crib_text: Optional known plaintext crib
            tags: Optional tags

        Returns:
            (plaintext, attack_record) tuple
        """
        params = AttackParameters(
            cipher_type="hill",
            key_or_params={
                "matrix_size": matrix_size,
                "key_matrix": key_matrix,
            },
            crib_text=crib_text,
        )

        start_time = time.time()

        try:
            # Import Hill cipher function
            from kryptos.k4.hill_cipher import hill_decrypt

            plaintext_result = hill_decrypt(ciphertext, key_matrix)
            plaintext = plaintext_result if plaintext_result is not None else ""
            execution_time = time.time() - start_time

            # Success check
            success = False
            if crib_text and plaintext:
                success = crib_text.upper() in plaintext.upper()
            else:
                success = bool(plaintext)

            result = AttackResult(
                success=success,
                plaintext_candidate=plaintext,
                confidence_scores={},
                execution_time_seconds=execution_time,
                metadata={"method": "hill_decrypt", "matrix_size": matrix_size},
            )

        except Exception as e:
            execution_time = time.time() - start_time
            result = AttackResult(
                success=False,
                plaintext_candidate=None,
                execution_time_seconds=execution_time,
                error_message=str(e),
            )
            plaintext = ""

        # Log the attack
        attack_id, is_duplicate = self.logger.log_attack(
            ciphertext=ciphertext,
            parameters=params,
            result=result,
            tags=tags or [],
        )

        # Get the logged record
        fingerprint = params.fingerprint()
        record = self.logger.attack_index[fingerprint]

        return plaintext, record

    def get_statistics(self) -> dict[str, Any]:
        """Get attack statistics from logger.

        Returns:
            Dictionary with attack counts, success rates, etc.
        """
        return self.logger.get_statistics()

    def query_attacks(self, **kwargs: Any) -> list[AttackRecord]:
        """Query attack records.

        Args:
            **kwargs: Filter parameters (cipher_type, success_only, etc.)

        Returns:
            List of matching attack records
        """
        return self.logger.query_attacks(**kwargs)


__all__ = ["AttackExecutor"]
