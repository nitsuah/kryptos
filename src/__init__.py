"""Kryptos cipher package."""
from .ciphers import (
    vigenere_decrypt,
    kryptos_k3_decrypt,
    double_rotational_transposition,
    transposition_decrypt,
    polybius_decrypt,
)
from .analysis import frequency_analysis, check_cribs
from .k4 import (
    generate_partitions,
    partitions_for_k4,
    slice_by_partition,
    combined_plaintext_score,
    segment_plaintext_scores,
    solve_substitution,
    Pipeline,
    Stage,
    StageResult,
)

__all__ = [
    'vigenere_decrypt',
    'kryptos_k3_decrypt',
    'double_rotational_transposition',
    'transposition_decrypt',
    'polybius_decrypt',
    'frequency_analysis',
    'check_cribs',
    # K4 exports
    'generate_partitions', 'partitions_for_k4', 'slice_by_partition',
    'combined_plaintext_score', 'segment_plaintext_scores',
    'solve_substitution', 'Pipeline', 'Stage', 'StageResult',
]
