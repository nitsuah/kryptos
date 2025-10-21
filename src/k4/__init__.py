"""K4 analysis and candidate pipeline modules."""
from .segmentation import generate_partitions, partitions_for_k4, slice_by_partition
from .scoring import (
    combined_plaintext_score, segment_plaintext_scores,
    chi_square_stat, trigram_score, bigram_score, crib_bonus,
    index_of_coincidence, vowel_ratio, letter_coverage, baseline_stats,
    QUADGRAMS, quadgram_score, letter_entropy, repeating_bigram_fraction
)
from .substitution_solver import solve_substitution
from .pipeline import Pipeline, Stage, StageResult, make_hill_constraint_stage, make_berlin_clock_stage, make_transposition_stage, make_transposition_adaptive_stage, make_masking_stage
from .transposition import apply_columnar_permutation, search_columnar, search_columnar_adaptive
from .hill_cipher import (
    mod_inv, matrix_det, matrix_inv_mod,
    hill_encrypt_block, hill_decrypt_block, hill_encrypt, hill_decrypt
)
from .cribs import normalize_cipher, annotate_cribs
from .berlin_clock import berlin_clock_shifts, apply_clock_shifts, full_clock_state, encode_clock_state, full_berlin_clock_shifts, enumerate_clock_shift_sequences
from .transposition_constraints import invert_columnar, search_with_crib, search_with_crib_at_position
from .hill_search import score_decryptions
from .hill_constraints import KNOWN_CRIBS, derive_candidate_keys, decrypt_and_score
from .reporting import write_candidates_json, write_candidates_csv, generate_candidate_artifacts
from .composite import aggregate_stage_candidates, run_composite_pipeline, normalize_scores, fuse_scores_weighted
from .masking import DEFAULT_NULLS, mask_variants, score_mask_variants

__all__ = [
    'generate_partitions', 'partitions_for_k4', 'slice_by_partition',
    'combined_plaintext_score', 'segment_plaintext_scores', 'chi_square_stat', 'trigram_score',
    'bigram_score', 'crib_bonus',
    'solve_substitution', 'Pipeline', 'Stage', 'StageResult',
    'apply_columnar_permutation', 'search_columnar'
]

__all__ += [
    'mod_inv','matrix_det','matrix_inv_mod','hill_encrypt_block','hill_decrypt_block','hill_encrypt','hill_decrypt'
]

__all__ += ['normalize_cipher','annotate_cribs']

__all__ += ['berlin_clock_shifts','apply_clock_shifts']

__all__ += ['invert_columnar','search_with_crib','search_with_crib_at_position']

__all__ += ['index_of_coincidence','vowel_ratio','letter_coverage','baseline_stats','letter_entropy','repeating_bigram_fraction']

__all__ += ['score_decryptions']

__all__ += ['KNOWN_CRIBS','derive_candidate_keys','decrypt_and_score']

__all__ += ['make_hill_constraint_stage', 'make_berlin_clock_stage', 'make_transposition_stage', 'make_transposition_adaptive_stage', 'make_masking_stage']

__all__ += ['write_candidates_json','write_candidates_csv','generate_candidate_artifacts']

__all__ += ['full_clock_state','encode_clock_state','full_berlin_clock_shifts','enumerate_clock_shift_sequences']

__all__ += ['QUADGRAMS','quadgram_score']

__all__ += ['aggregate_stage_candidates','run_composite_pipeline']

__all__ += ['search_columnar_adaptive','normalize_scores','fuse_scores_weighted']

__all__ += ['DEFAULT_NULLS','mask_variants','score_mask_variants']
