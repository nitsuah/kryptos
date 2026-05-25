"""Shared solver configuration for deterministic and stochastic runs.

This module provides a lightweight cross-solver configuration surface so
callers can reuse one config object across Vigenere and transposition paths.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SolverConfig:
    """Optional knobs shared by K4 solver components.

    Attributes are optional so existing call sites can adopt this incrementally.
    """

    rng_seed: int | None = None

    # Vigenere recovery options
    vigenere_max_candidates: int | None = None

    # Transposition SA options
    sa_num_restarts: int | None = None
    sa_max_iterations: int | None = None
    sa_initial_temp: float | None = None
    sa_cooling_rate: float | None = None

    # Hill-climbing transposition option
    hc_max_iterations: int | None = None


def make_ci_solver_config(seed: int = 42) -> SolverConfig:
    """Create a deterministic, reproducible config suitable for CI checks."""
    return SolverConfig(
        rng_seed=seed,
        vigenere_max_candidates=100_000,
    )


def make_exploration_solver_config(seed: int | None = None) -> SolverConfig:
    """Create a higher-budget config for exploratory local/overnight runs."""
    return SolverConfig(
        rng_seed=seed,
        sa_num_restarts=20,
        sa_max_iterations=200_000,
        sa_initial_temp=75.0,
        sa_cooling_rate=0.9997,
        vigenere_max_candidates=500_000,
    )
