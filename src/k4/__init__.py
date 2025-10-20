"""K4 analysis and candidate pipeline modules."""
from .segmentation import generate_partitions, partitions_for_k4, slice_by_partition
from .scoring import combined_plaintext_score, segment_plaintext_scores
from .substitution_solver import solve_substitution
from .pipeline import Pipeline, Stage, StageResult

__all__ = [
    'generate_partitions', 'partitions_for_k4', 'slice_by_partition',
    'combined_plaintext_score', 'segment_plaintext_scores',
    'solve_substitution', 'Pipeline', 'Stage', 'StageResult'
]
