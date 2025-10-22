"""K4 analysis and candidate pipeline modules."""

from .attempt_logging import persist_attempt_logs
from .berlin_clock import (
    apply_clock_shifts,
    berlin_clock_shifts,
    encode_clock_state,
    enumerate_clock_shift_sequences,
    full_berlin_clock_shifts,
    full_clock_state,
)
from .composite import (
    adaptive_fusion_weights,
    aggregate_stage_candidates,
    fuse_scores_weighted,
    normalize_scores,
    run_composite_pipeline,
)
from .cribs import annotate_cribs, normalize_cipher
from .hill_cipher import (
    hill_decrypt,
    hill_decrypt_block,
    hill_encrypt,
    hill_encrypt_block,
    matrix_det,
    matrix_inv_mod,
    mod_inv,
)
from .hill_constraints import KNOWN_CRIBS, decrypt_and_score, derive_candidate_keys
from .hill_search import score_decryptions
from .masking import DEFAULT_NULLS, mask_variants, score_mask_variants
from .pipeline import (
    Pipeline,
    Stage,
    StageResult,
    make_berlin_clock_stage,
    make_hill_constraint_stage,
    make_masking_stage,
    make_route_transposition_stage,
    make_transposition_adaptive_stage,
    make_transposition_multi_crib_stage,
    make_transposition_stage,
)
from .reporting import generate_candidate_artifacts, write_candidates_csv, write_candidates_json
from .scoring import (
    QUADGRAMS,
    baseline_stats,
    bigram_score,
    chi_square_stat,
    combined_plaintext_score,
    crib_bonus,
    index_of_coincidence,
    letter_coverage,
    letter_entropy,
    quadgram_score,
    repeating_bigram_fraction,
    segment_plaintext_scores,
    trigram_score,
    vowel_ratio,
)
from .segmentation import generate_partitions, partitions_for_k4, slice_by_partition
from .substitution_solver import solve_substitution
from .transposition import (
    apply_columnar_permutation,
    search_columnar,
    search_columnar_adaptive,
)
from .transposition_constraints import (
    invert_columnar,
    search_with_crib,
    search_with_crib_at_position,
)
from .transposition_routes import generate_route_variants

__all__ = [
    'generate_partitions',
    'partitions_for_k4',
    'slice_by_partition',
    'combined_plaintext_score',
    'segment_plaintext_scores',
    'chi_square_stat',
    'trigram_score',
    'bigram_score',
    'crib_bonus',
    'solve_substitution',
    'Pipeline',
    'Stage',
    'StageResult',
    'apply_columnar_permutation',
    'search_columnar',
    'search_columnar_adaptive',
    'mod_inv',
    'matrix_det',
    'matrix_inv_mod',
    'hill_encrypt_block',
    'hill_decrypt_block',
    'hill_encrypt',
    'hill_decrypt',
    'normalize_cipher',
    'annotate_cribs',
    'berlin_clock_shifts',
    'apply_clock_shifts',
    'full_clock_state',
    'encode_clock_state',
    'full_berlin_clock_shifts',
    'enumerate_clock_shift_sequences',
    'invert_columnar',
    'search_with_crib',
    'search_with_crib_at_position',
    'index_of_coincidence',
    'vowel_ratio',
    'letter_coverage',
    'baseline_stats',
    'letter_entropy',
    'repeating_bigram_fraction',
    'score_decryptions',
    'KNOWN_CRIBS',
    'derive_candidate_keys',
    'decrypt_and_score',
    'make_hill_constraint_stage',
    'make_berlin_clock_stage',
    'make_transposition_stage',
    'make_transposition_adaptive_stage',
    'make_masking_stage',
    'make_transposition_multi_crib_stage',
    'make_route_transposition_stage',
    'write_candidates_json',
    'write_candidates_csv',
    'generate_candidate_artifacts',
    'QUADGRAMS',
    'quadgram_score',
    'aggregate_stage_candidates',
    'run_composite_pipeline',
    'normalize_scores',
    'fuse_scores_weighted',
    'adaptive_fusion_weights',
    'DEFAULT_NULLS',
    'mask_variants',
    'score_mask_variants',
    'persist_attempt_logs',
    'generate_route_variants',
]
