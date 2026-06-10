"""Monte Carlo validation of the K3 double-rotation brute-force solver.

This is the "K3 double-transposition Monte Carlo" item from ROADMAP.md
(Phase 4: Validation & hardening): for random (width, rotation) pairs per
stage, confirm that brute_force_double_rotation_solve recovers the true
plaintext among its top-ranked candidates.
"""

import os

import pytest

from kryptos.k3.double_rotation_solver import run_k3_double_rotation_monte_carlo

if os.getenv("KRYPTOS_RUN_SLOW_MONTE_CARLO") != "1":
    pytest.skip(
        "Set KRYPTOS_RUN_SLOW_MONTE_CARLO=1 to run this slow module",
        allow_module_level=True,
    )

K3_PLAINTEXT = (
    "SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHEL"
    "OWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHANDSIMADEATINYBREACHI"
    "NTHEUPPERLEFTHANDCORNERANDTHENWIDENINGTHEHOLEALITTLEIINSERTEDTHEC"
    "ANDLEANDPEEREDINTHEHOTAIRESCAPINGFROMTHECHAMBERCAUSEDTHEFLAMETOF"
    "LICKERBUTPRESENTLYDETAILSOFTHEROOMWITHINEMERGEDFROMTHEMISTXCANYO"
    "USEEANYTHINGQ"
)


@pytest.mark.slow
def test_k3_double_rotation_monte_carlo_20runs():
    """20-run Monte Carlo across random (width, rotation) pairs for both stages.

    Success = the true plaintext appears among the top-10 brute-force
    candidates with match_ratio >= 0.95 (~75% empirically with seed=42).
    Many failures involve 'identity' rotations or extreme-aspect-ratio
    grids whose score-tied cyclic rearrangements of the plaintext outrank
    the exact match -- see best_match_ratio vs top1_match_ratio in the
    recorded runs.
    """
    summary = run_k3_double_rotation_monte_carlo(
        K3_PLAINTEXT,
        num_runs=20,
        seed=42,
        results_path="artifacts/k3_double_rotation_monte_carlo.json",
    )

    print(f"\nstatus={summary['status']} success_rate={summary['success_rate']:.0%}")
    for run in summary["runs"]:
        symbol = "PASS" if run["success"] else "FAIL"
        print(
            f"  run {run['run']:2d}: {symbol} encrypt={run['encrypt_params']} "
            f"top1={run['top1_match_ratio']:.3f} best={run['best_match_ratio']:.3f}"
        )

    assert summary["success_rate"] >= 0.7, f"success rate too low: {summary['success_rate']:.1%}"
