"""Sample composite pipeline run producing artifacts & attempt logs.
Run this after installing dependencies. Generates reports/ folder outputs.
"""
from collections.abc import Sequence
from src.k4 import (
    make_hill_constraint_stage,
    make_transposition_adaptive_stage,
    make_transposition_multi_crib_stage,
    make_masking_stage,
    make_berlin_clock_stage,
    run_composite_pipeline,
    persist_attempt_logs,
)

CIPHER_K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"

_RAW_POSITIONAL: dict[str, list[int]] = {
    'EAST': [22],  # provisional; under investigation per strategy doc
    'NORTHEAST': [25],
    'BERLIN': [64],
    'CLOCK': [69],
}
# Treat as Dict[str, Sequence[int]] for stage factory
POSITIONAL_CRIBS: dict[str, Sequence[int]] = {k: tuple(v) for k, v in _RAW_POSITIONAL.items()}

stages = [
    make_hill_constraint_stage(partial_len=60, partial_min=-800.0),
    make_transposition_adaptive_stage(min_cols=5, max_cols=6, sample_perms=250, partial_length=50),
    make_transposition_multi_crib_stage(positional_cribs=POSITIONAL_CRIBS, min_cols=5, max_cols=6, window=5),
    make_masking_stage(limit=10),
    make_berlin_clock_stage(step_seconds=10800, limit=15),
]

WEIGHTS = {
    'hill-constraint': 2.0,
    'transposition-adaptive': 1.2,
    'transposition-pos-crib': 1.5,
    'masking': 1.0,
    'berlin-clock': 0.8,
}

if __name__ == "__main__":
    result = run_composite_pipeline(
        CIPHER_K4,
        stages,
        report=True,
        weights=None,  # disables manual weighting; enables adaptive weighting
        normalize=True,
        adaptive=True,  # enable adaptive weighting
        limit=40,
    )
    attempt_path = persist_attempt_logs(out_dir='reports', label='K4', clear=True)
    print("Artifacts written. Attempt log:", attempt_path)
    fused = result.get('fused', [])
    print("Adaptive weights diagnostics:")
    print(result.get('profile', {}).get('adaptive_diagnostics'))
    print("Top fused candidates:")
    for cand in fused[:5]:
        print(cand['stage'], round(cand['fused_score'], 2), cand['text'][:60])
