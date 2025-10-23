"""K4 analysis namespace (lazy exports).

To keep import side-effects low and avoid circular initialization during
migration, heavy submodules are not imported eagerly. Public symbols are
exposed via ``__getattr__`` on first access.
"""

from importlib import import_module as _imp

_LAZY_MAP = {
    # Pipeline & stages
    'Pipeline': ('kryptos.k4.pipeline', 'Pipeline'),
    'Stage': ('kryptos.k4.pipeline', 'Stage'),
    'StageResult': ('kryptos.k4.pipeline', 'StageResult'),
    'make_hill_constraint_stage': ('kryptos.k4.pipeline', 'make_hill_constraint_stage'),
    'make_berlin_clock_stage': ('kryptos.k4.pipeline', 'make_berlin_clock_stage'),
    'make_transposition_stage': ('kryptos.k4.pipeline', 'make_transposition_stage'),
    'make_transposition_adaptive_stage': ('kryptos.k4.pipeline', 'make_transposition_adaptive_stage'),
    'make_masking_stage': ('kryptos.k4.pipeline', 'make_masking_stage'),
    'make_transposition_multi_crib_stage': ('kryptos.k4.pipeline', 'make_transposition_multi_crib_stage'),
    'make_route_transposition_stage': ('kryptos.k4.pipeline', 'make_route_transposition_stage'),
    'get_clock_attempt_log': ('kryptos.k4.pipeline', 'get_clock_attempt_log'),
    'get_hill_attempt_log': ('kryptos.k4.hill_constraints', 'get_hill_attempt_log'),
    # Hill cipher / constraints
    'KNOWN_CRIBS': ('kryptos.k4.hill_constraints', 'KNOWN_CRIBS'),
    'derive_candidate_keys': ('kryptos.k4.hill_constraints', 'derive_candidate_keys'),
    'decrypt_and_score': ('kryptos.k4.hill_constraints', 'decrypt_and_score'),
    # Scoring (subset; full module import via kryptos.k4.scoring)
    'combined_plaintext_score': ('kryptos.k4.scoring', 'combined_plaintext_score'),
    'baseline_stats': ('kryptos.k4.scoring', 'baseline_stats'),
    'quadgram_score': ('kryptos.k4.scoring', 'quadgram_score'),
    'crib_bonus': ('kryptos.k4.scoring', 'crib_bonus'),
    # Transposition core
    'apply_columnar_permutation': ('kryptos.k4.transposition', 'apply_columnar_permutation'),
    'search_columnar': ('kryptos.k4.transposition', 'search_columnar'),
    'search_columnar_adaptive': ('kryptos.k4.transposition', 'search_columnar_adaptive'),
    'generate_route_variants': ('kryptos.k4.transposition_routes', 'generate_route_variants'),
    # Composite runner
    'aggregate_stage_candidates': ('kryptos.k4.composite', 'aggregate_stage_candidates'),
    'run_composite_pipeline': ('kryptos.k4.composite', 'run_composite_pipeline'),
    # Attempt logs
    'persist_attempt_logs': ('kryptos.k4.attempt_logging', 'persist_attempt_logs'),
    # Legacy executor (to be deprecated after full Pipeline adoption)
    'PipelineConfig': ('kryptos.k4.executor', 'PipelineConfig'),
    'PipelineExecutor': ('kryptos.k4.executor', 'PipelineExecutor'),
    # Composite extras
    'fuse_scores_weighted': ('kryptos.k4.composite', 'fuse_scores_weighted'),
    'normalize_scores': ('kryptos.k4.composite', 'normalize_scores'),
    'adaptive_fusion_weights': ('kryptos.k4.composite', 'adaptive_fusion_weights'),
    # Hill cipher functions
    'hill_encrypt': ('kryptos.k4.hill_cipher', 'hill_encrypt'),
    'hill_decrypt': ('kryptos.k4.hill_cipher', 'hill_decrypt'),
    'matrix_inv_mod': ('kryptos.k4.hill_cipher', 'matrix_inv_mod'),
    'brute_force_crib': ('kryptos.k4.hill_cipher', 'brute_force_crib'),
    # Berlin clock functions
    'berlin_clock_shifts': ('kryptos.k4.berlin_clock', 'berlin_clock_shifts'),
    'enumerate_clock_shift_sequences': ('kryptos.k4.berlin_clock', 'enumerate_clock_shift_sequences'),
    'full_clock_state': ('kryptos.k4.berlin_clock', 'full_clock_state'),
    'full_berlin_clock_shifts': ('kryptos.k4.berlin_clock', 'full_berlin_clock_shifts'),
    # Masking helpers
    'mask_variants': ('kryptos.k4.masking', 'mask_variants'),
    'score_mask_variants': ('kryptos.k4.masking', 'score_mask_variants'),
    # Scoring extended surface
    'letter_entropy': ('kryptos.k4.scoring', 'letter_entropy'),
    'repeating_bigram_fraction': ('kryptos.k4.scoring', 'repeating_bigram_fraction'),
    'letter_coverage': ('kryptos.k4.scoring', 'letter_coverage'),
    'combined_plaintext_score_with_positions': ('kryptos.k4.scoring', 'combined_plaintext_score_with_positions'),
    'positional_crib_bonus': ('kryptos.k4.scoring', 'positional_crib_bonus'),
    'bigram_gap_variance': ('kryptos.k4.scoring', 'bigram_gap_variance'),
    'wordlist_hit_rate': ('kryptos.k4.scoring', 'wordlist_hit_rate'),
    'combined_plaintext_score_cached': ('kryptos.k4.scoring', 'combined_plaintext_score_cached'),
    # Transposition constraints functions
    'search_with_crib_at_position': ('kryptos.k4.transposition_constraints', 'search_with_crib_at_position'),
    'search_with_multiple_cribs_positions': (
        'kryptos.k4.transposition_constraints',
        'search_with_multiple_cribs_positions',
    ),
    'search_with_crib': ('kryptos.k4.transposition_constraints', 'search_with_crib'),
    'invert_columnar': ('kryptos.k4.transposition_constraints', 'invert_columnar'),
    # Cribs utilities
    'annotate_cribs': ('kryptos.k4.cribs', 'annotate_cribs'),
    'normalize_cipher': ('kryptos.k4.cribs', 'normalize_cipher'),
    # Module objects (allow `from kryptos.k4 import transposition` etc.)
    # (Handled by explicit module passthroughs below rather than lazy attr lookup.)
}

# Intentionally omit __all__ to allow linters that require concrete symbol presence
# to skip validation; lazy attribute loading supplies them on demand.


def __getattr__(name: str):  # pragma: no cover - import mechanism
    target = _LAZY_MAP.get(name)
    if not target:
        raise AttributeError(f"kryptos.k4 has no attribute {name!r}")
    mod_name, attr_name = target
    module = _imp(mod_name)
    return getattr(module, attr_name)


# Module passthroughs needed by tests / legacy code: expose full submodules as attributes.
try:  # pragma: no cover - defensive
    scoring = _imp('kryptos.k4.scoring')
    transposition = _imp('kryptos.k4.transposition')
    cribs = _imp('kryptos.k4.cribs')
except ImportError:  # pragma: no cover - do not crash import if optional
    pass
