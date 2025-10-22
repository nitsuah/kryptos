"""Kryptos cipher package."""

from .analysis import check_cribs, frequency_analysis
from .ciphers import (
    double_rotational_transposition,
    kryptos_k3_decrypt,
    polybius_decrypt,
    transposition_decrypt,
    vigenere_decrypt,
)
from .k4 import (
    Pipeline,
    Stage,
    StageResult,
    combined_plaintext_score,
    generate_partitions,
    partitions_for_k4,
    segment_plaintext_scores,
    slice_by_partition,
    solve_substitution,
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
    'generate_partitions',
    'partitions_for_k4',
    'slice_by_partition',
    'combined_plaintext_score',
    'segment_plaintext_scores',
    'solve_substitution',
    'Pipeline',
    'Stage',
    'StageResult',
]
