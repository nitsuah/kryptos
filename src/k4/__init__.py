"""K4 analysis and candidate pipeline modules."""
from .segmentation import generate_partitions, partitions_for_k4, slice_by_partition
from .scoring import (
    combined_plaintext_score, segment_plaintext_scores,
    chi_square_stat, trigram_score, bigram_score, crib_bonus
)
from .substitution_solver import solve_substitution
from .pipeline import Pipeline, Stage, StageResult
from .transposition import apply_columnar_permutation, search_columnar

__all__ = [
    'generate_partitions', 'partitions_for_k4', 'slice_by_partition',
    'combined_plaintext_score', 'segment_plaintext_scores', 'chi_square_stat', 'trigram_score',
    'bigram_score', 'crib_bonus',
    'solve_substitution', 'Pipeline', 'Stage', 'StageResult',
    'apply_columnar_permutation', 'search_columnar'
]
