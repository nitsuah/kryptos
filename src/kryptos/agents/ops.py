"""OPS Agent: Operations & Orchestration for Parallel Hypothesis Testing.

The OPS agent manages parallel execution of cryptanalysis hypotheses,
providing queue management, resource monitoring, and timeout enforcement
for scalable K4 cryptanalysis.

Integrates with AttackGenerator for systematic attack queue generation
from Q-Research hints, coverage gaps, and literature analysis.
"""

from __future__ import annotations

import multiprocessing as mp
import time
from concurrent.futures import ProcessPoolExecutor, TimeoutError, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from kryptos.agents.spy import SpyAgent
from kryptos.ciphers import vigenere_decrypt
from kryptos.k4.hill_cipher import hill_decrypt
from kryptos.k4.transposition import apply_columnar_permutation
from kryptos.k4.vigenere_key_recovery import recover_key_by_frequency
from kryptos.log_setup import setup_logging
from kryptos.pipeline.attack_generator import AttackGenerator, AttackSpec
from kryptos.provenance.attack_log import AttackLogger, AttackResult


@dataclass
class JobResult:
    """Result from a hypothesis test job."""

    hypothesis_name: str
    success: bool
    duration_seconds: float
    candidates_count: int = 0
    best_score: float | None = None
    error: str | None = None
    artifact_path: Path | None = None


@dataclass
class OpsConfig:
    """Configuration for OPS agent orchestration."""

    max_workers: int | None = None  # None = CPU count
    job_timeout_seconds: int = 300  # 5 minutes per hypothesis
    retry_failed: bool = False
    save_artifacts: bool = True
    log_level: str = "INFO"
    enable_attack_generation: bool = True  # Enable AttackGenerator integration
    attack_log_dir: Path | None = None  # Directory for attack logs


class OpsAgent:
    """Operations orchestrator for parallel hypothesis execution.

    Manages parallel testing of multiple cryptanalysis hypotheses with:
    - Process pool execution
    - Timeout enforcement
    - Resource monitoring
    - Queue management
    - Result aggregation
    - Attack generation from Q-Research hints (Phase 5.1+)
    """

    def __init__(self, config: OpsConfig | None = None):
        """Initialize OPS agent.

        Args:
            config: Configuration for orchestration behavior
        """
        self.config = config or OpsConfig()
        self.log = setup_logging(
            level=self.config.log_level,
            logger_name="kryptos.agents.ops",
        )
        self.results: list[JobResult] = []

        # Phase 5.1: Attack generation integration
        if self.config.enable_attack_generation:
            self.attack_logger = AttackLogger(log_dir=self.config.attack_log_dir)
            self.attack_generator = AttackGenerator(
                attack_logger=self.attack_logger,
                log_level=self.config.log_level,
            )
        else:
            self.attack_logger = None
            self.attack_generator = None

    def run_hypothesis_job(
        self,
        hypothesis_name: str,
        hypothesis_class: type,
        ciphertext: str,
        **kwargs: Any,
    ) -> JobResult:
        """Execute a single hypothesis test (designed to run in worker process).

        Args:
            hypothesis_name: Name identifier for the hypothesis
            hypothesis_class: Hypothesis class to instantiate
            ciphertext: K4 ciphertext to test
            **kwargs: Additional parameters for hypothesis

        Returns:
            JobResult with test outcomes
        """
        start = time.time()
        try:
            # Instantiate hypothesis
            hypothesis = hypothesis_class(**kwargs)

            # Generate candidates
            candidates = list(hypothesis.generate_candidates(ciphertext, limit=10))

            duration = time.time() - start

            # Extract best score
            best_score = candidates[0].score if candidates else None

            return JobResult(
                hypothesis_name=hypothesis_name,
                success=True,
                duration_seconds=duration,
                candidates_count=len(candidates),
                best_score=best_score,
                artifact_path=None,
            )

        except Exception as e:
            duration = time.time() - start
            return JobResult(
                hypothesis_name=hypothesis_name,
                success=False,
                duration_seconds=duration,
                error=str(e),
            )

    def run_parallel(
        self,
        jobs: list[dict[str, Any]],
        ciphertext: str,
    ) -> list[JobResult]:
        """Run multiple hypothesis tests in parallel.

        Args:
            jobs: List of job specifications, each with:
                  - 'name': hypothesis identifier
                  - 'class': hypothesis class
                  - 'params': dict of parameters (optional)
            ciphertext: K4 ciphertext to test

        Returns:
            List of JobResults for all jobs
        """
        self.results = []
        max_workers = self.config.max_workers or mp.cpu_count()

        self.log.info(f"Starting parallel execution: {len(jobs)} jobs, {max_workers} workers")

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all jobs
            future_to_job = {}
            for job_spec in jobs:
                name = job_spec["name"]
                cls = job_spec["class"]
                params = job_spec.get("params", {})

                future = executor.submit(
                    self.run_hypothesis_job,
                    name,
                    cls,
                    ciphertext,
                    **params,
                )
                future_to_job[future] = name

            # Collect results as they complete
            for future in as_completed(
                future_to_job,
                timeout=self.config.job_timeout_seconds * len(jobs),
            ):
                job_name = future_to_job[future]
                try:
                    result = future.result(timeout=self.config.job_timeout_seconds)
                    self.results.append(result)

                    if result.success:
                        self.log.info(
                            f"✓ {job_name}: {result.candidates_count} candidates, "
                            f"best={result.best_score:.2f}, {result.duration_seconds:.2f}s",
                        )
                    else:
                        self.log.error(f"✗ {job_name}: FAILED - {result.error} " f"({result.duration_seconds:.2f}s)")

                except TimeoutError:
                    self.log.error(f"✗ {job_name}: TIMEOUT after {self.config.job_timeout_seconds}s")
                    self.results.append(
                        JobResult(
                            hypothesis_name=job_name,
                            success=False,
                            duration_seconds=self.config.job_timeout_seconds,
                            error="Job timeout exceeded",
                        ),
                    )

                except Exception as e:
                    self.log.error(f"✗ {job_name}: EXCEPTION - {e}")
                    self.results.append(
                        JobResult(
                            hypothesis_name=job_name,
                            success=False,
                            duration_seconds=0.0,
                            error=f"Executor exception: {e}",
                        ),
                    )

        return self.results

    def summarize(self) -> dict[str, Any]:
        """Generate summary statistics from completed jobs.

        Returns:
            Dictionary with execution statistics
        """
        if not self.results:
            return {"status": "no_jobs"}

        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]

        total_duration = sum(r.duration_seconds for r in self.results)
        total_candidates = sum(r.candidates_count for r in successful)

        best_result = max(successful, key=lambda r: r.best_score or float("-inf")) if successful else None

        return {
            "total_jobs": len(self.results),
            "successful": len(successful),
            "failed": len(failed),
            "total_duration_seconds": round(total_duration, 2),
            "total_candidates": total_candidates,
            "best_hypothesis": best_result.hypothesis_name if best_result else None,
            "best_score": round(best_result.best_score, 2) if best_result and best_result.best_score else None,
        }

    # ===== PHASE 5.1+: ATTACK GENERATION INTEGRATION =====

    def generate_attack_queue_from_q_hints(
        self,
        ciphertext: str,
        max_attacks: int = 50,
    ) -> list[AttackSpec]:
        """Generate attack queue from Q-Research cryptanalysis hints.

        This method bridges Q-Research insights with executable attacks.
        Converts Vigenère metrics, transposition hints, and strategy
        suggestions into prioritized AttackParameters.

        Args:
            ciphertext: Ciphertext to analyze and attack
            max_attacks: Maximum attacks to generate

        Returns:
            Prioritized list of attack specifications

        Raises:
            RuntimeError: If attack generation is not enabled
        """
        if not self.attack_generator:
            raise RuntimeError("Attack generation not enabled. Set enable_attack_generation=True in OpsConfig.")

        self.log.info("Generating attack queue from Q-Research hints")
        attacks = self.attack_generator.generate_from_q_hints(
            ciphertext=ciphertext,
            max_attacks=max_attacks,
        )

        self.log.info("Generated %d attacks from Q-Research", len(attacks))
        return attacks

    def generate_attack_queue_comprehensive(
        self,
        ciphertext: str,
        cipher_types: list[str] | None = None,
        max_attacks: int = 200,
    ) -> list[AttackSpec]:
        """Generate comprehensive attack queue from all sources.

        Combines:
        - Q-Research hints (Vigenère, transposition)
        - Coverage gap targeting
        - Literature recommendations (when available)

        Args:
            ciphertext: Ciphertext to attack
            cipher_types: Cipher types to consider
            max_attacks: Maximum total attacks

        Returns:
            Prioritized, deduplicated attack queue

        Raises:
            RuntimeError: If attack generation is not enabled
        """
        if not self.attack_generator:
            raise RuntimeError("Attack generation not enabled. Set enable_attack_generation=True in OpsConfig.")

        self.log.info("Generating comprehensive attack queue")
        attacks = self.attack_generator.generate_comprehensive_queue(
            ciphertext=ciphertext,
            cipher_types=cipher_types,
            max_total=max_attacks,
        )

        self.log.info("Generated %d attacks (comprehensive)", len(attacks))
        return attacks

    def execute_attack_queue(
        self,
        attack_queue: list[AttackSpec],
        ciphertext: str,
        batch_size: int = 10,
    ) -> dict[str, Any]:
        """Execute generated attack queue with logging and progress tracking.

        This is a placeholder that demonstrates the intended workflow.
        Full implementation requires cipher-specific execution logic.

        Args:
            attack_queue: Queue of attacks to execute
            ciphertext: Ciphertext to attack
            batch_size: Number of attacks to execute in parallel

        Returns:
            Execution summary with statistics

        Raises:
            RuntimeError: If attack logging is not enabled
        """
        if not self.attack_logger:
            raise RuntimeError("Attack logging not enabled.")

        self.log.info("Executing %d attacks in batches of %d", len(attack_queue), batch_size)

        executed = 0
        successful = 0
        best_score = float("-inf")
        best_attack = None

        # Process in batches
        for i in range(0, len(attack_queue), batch_size):
            batch = attack_queue[i : i + batch_size]
            batch_num = i // batch_size + 1
            self.log.info("Executing batch %d: %d attacks", batch_num, len(batch))

            for attack_spec in batch:
                # Execute attack with real cipher implementation
                # (vigenere, hill, transposition) and score with SPY agent
                result = self._execute_single_attack(attack_spec, ciphertext)

                # Log attack
                _attack_id, _is_duplicate = self.attack_logger.log_attack(
                    ciphertext=ciphertext,
                    parameters=attack_spec.parameters,
                    result=result,
                    tags=attack_spec.tags,
                )

                executed += 1

                if result.success:
                    successful += 1
                    if result.confidence_scores.get("spy", 0.0) > best_score:
                        best_score = result.confidence_scores["spy"]
                        best_attack = attack_spec

        summary = {
            "total_attacks": len(attack_queue),
            "executed": executed,
            "successful": successful,
            "best_score": best_score if best_score > float("-inf") else None,
            "best_attack_rationale": best_attack.rationale if best_attack else None,
            "attack_logger_stats": self.attack_logger.stats,
        }

        self.log.info("Execution complete: %d/%d successful", successful, executed)
        return summary

    def _execute_single_attack(
        self,
        attack_spec: AttackSpec,
        ciphertext: str,
    ) -> AttackResult:
        """Execute a single attack with real cipher implementation.

        Args:
            attack_spec: Attack specification
            ciphertext: Ciphertext to attack

        Returns:
            Attack result with decryption and SPY scoring
        """
        start_time = time.time()
        params = attack_spec.parameters
        cipher_type = params.cipher_type
        key_or_params = params.key_or_params

        try:
            # Execute cipher based on type
            plaintext_candidate = None

            if cipher_type == "vigenere":
                plaintext_candidate = self._execute_vigenere(ciphertext, key_or_params)
            elif cipher_type == "hill":
                plaintext_candidate = self._execute_hill(ciphertext, key_or_params)
            elif cipher_type == "transposition":
                plaintext_candidate = self._execute_transposition(ciphertext, key_or_params)
            else:
                # Unknown cipher type - return failure
                return AttackResult(
                    success=False,
                    plaintext_candidate=None,
                    confidence_scores={},
                    execution_time_seconds=time.time() - start_time,
                    error_message=f"Unknown cipher type: {cipher_type}",
                    metadata={"cipher_type": cipher_type},
                )

            # If decryption failed, return failure
            if plaintext_candidate is None:
                return AttackResult(
                    success=False,
                    plaintext_candidate=None,
                    confidence_scores={},
                    execution_time_seconds=time.time() - start_time,
                    error_message="Decryption returned None",
                    metadata={"cipher_type": cipher_type, "params": str(key_or_params)[:100]},
                )

            # Score with SPY agent
            spy = SpyAgent()
            analysis = spy.analyze_candidate(plaintext_candidate)

            # Extract confidence score
            # SPY returns dict with 'summary' containing 'overall_confidence'
            overall_confidence = 0.0
            if "summary" in analysis and "overall_confidence" in analysis["summary"]:
                overall_confidence = analysis["summary"]["overall_confidence"]

            # Determine success based on confidence threshold
            success = overall_confidence >= 0.3

            execution_time = time.time() - start_time

            return AttackResult(
                success=success,
                plaintext_candidate=plaintext_candidate,
                confidence_scores={"spy": overall_confidence},
                execution_time_seconds=execution_time,
                metadata={
                    "cipher_type": cipher_type,
                    "attack_source": attack_spec.source,
                    "attack_priority": attack_spec.priority,
                    "spy_insights_count": len(analysis.get("insights", [])),
                },
            )

        except Exception as e:
            # Handle execution errors gracefully
            execution_time = time.time() - start_time
            return AttackResult(
                success=False,
                plaintext_candidate=None,
                confidence_scores={},
                execution_time_seconds=execution_time,
                error_message=str(e),
                metadata={
                    "cipher_type": cipher_type,
                    "error_type": type(e).__name__,
                },
            )

    def _execute_vigenere(self, ciphertext: str, params: dict[str, Any]) -> str | None:
        """Execute Vigenère decryption.

        Args:
            ciphertext: Ciphertext to decrypt
            params: Dictionary with 'key_length' and optionally 'key'

        Returns:
            Decrypted plaintext or None
        """
        # If key is provided, use it directly
        if "key" in params and params["key"]:
            try:
                return vigenere_decrypt(ciphertext, params["key"])
            except Exception:
                return None

        # If only key_length provided, attempt key recovery
        if "key_length" in params:
            key_length = params["key_length"]
            try:
                # Attempt frequency-based key recovery
                candidate_keys = recover_key_by_frequency(ciphertext, key_length, top_n=1)
                if candidate_keys:
                    # Try the best candidate
                    return vigenere_decrypt(ciphertext, candidate_keys[0])
            except Exception:
                pass

        return None

    def _execute_hill(self, ciphertext: str, params: dict[str, Any]) -> str | None:
        """Execute Hill cipher decryption.

        Args:
            ciphertext: Ciphertext to decrypt
            params: Dictionary with 'key_matrix'

        Returns:
            Decrypted plaintext or None
        """
        if "key_matrix" not in params:
            return None

        try:
            return hill_decrypt(ciphertext, params["key_matrix"])
        except Exception:
            return None

    def _execute_transposition(self, ciphertext: str, params: dict[str, Any]) -> str | None:
        """Execute transposition cipher decryption.

        Args:
            ciphertext: Ciphertext to decrypt
            params: Dictionary with 'period' and 'permutation'

        Returns:
            Decrypted plaintext or None
        """
        # Columnar transposition
        if "period" in params and "permutation" in params:
            try:
                n_cols = params["period"]
                perm = tuple(params["permutation"])
                return apply_columnar_permutation(ciphertext, n_cols, perm)
            except Exception:
                return None

        # Other transposition methods would go here
        return None


def ops_report(results: list[JobResult]) -> str:
    """Generate human-readable report from OPS results.

    Args:
        results: List of job results

    Returns:
        Formatted report string
    """
    lines = ["=" * 80, "OPS AGENT EXECUTION REPORT", "=" * 80, ""]

    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    lines.append(f"Total jobs: {len(results)}")
    lines.append(f"Successful: {len(successful)}")
    lines.append(f"Failed: {len(failed)}")
    lines.append("")

    if successful:
        lines.append("Successful Hypotheses:")
        lines.append("-" * 80)
        for r in sorted(successful, key=lambda x: x.best_score or float("-inf"), reverse=True):
            lines.append(
                f"  {r.hypothesis_name:30s} | "
                f"score: {r.best_score:8.2f} | "
                f"candidates: {r.candidates_count:4d} | "
                f"time: {r.duration_seconds:6.2f}s",
            )
        lines.append("")

    if failed:
        lines.append("Failed Hypotheses:")
        lines.append("-" * 80)
        for r in failed:
            lines.append(f"  {r.hypothesis_name:30s} | {r.error}")
        lines.append("")

    lines.append("=" * 80)
    return "\n".join(lines)
