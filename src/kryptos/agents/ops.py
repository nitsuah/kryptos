"""OPS Agent: Operations & Orchestration for Parallel Hypothesis Testing.

The OPS agent manages parallel execution of cryptanalysis hypotheses,
providing queue management, resource monitoring, and timeout enforcement
for scalable K4 cryptanalysis.
"""

from __future__ import annotations

import multiprocessing as mp
import time
from concurrent.futures import ProcessPoolExecutor, TimeoutError, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from kryptos.log_setup import setup_logging


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


class OpsAgent:
    """Operations orchestrator for parallel hypothesis execution.

    Manages parallel testing of multiple cryptanalysis hypotheses with:
    - Process pool execution
    - Timeout enforcement
    - Resource monitoring
    - Queue management
    - Result aggregation
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
                artifact_path=None,  # TODO: Add artifact saving
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
