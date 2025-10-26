"""K4 public API exports.

High-level convenience entry points over internal pipeline & solver modules.
Heavy components are imported lazily inside functions to keep import overhead low
when only the orchestrator is required.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module as _imp
from typing import Any

__all__ = ["decrypt_best", "DecryptResult"]


@dataclass(slots=True)
class DecryptResult:
    """Structured result returned by :func:`decrypt_best`.

    Attributes
    ----------
    plaintext: Best plaintext candidate selected (fused ranking if available).
    score: Score associated with the selected plaintext.
    candidates: Top candidate list (each a mapping with text/score/metadata) after aggregation.
    profile: Execution profiling / diagnostics (stage durations, adaptive diagnostics, etc.).
    artifacts: Optional artifact file paths produced (reports, attempt logs, etc.).
    attempt_log: Optional attempt log path.
    lineage: Ordered list of stage names executed.
    metadata: Free-form extra metadata (versioning, strategy labels, parameters).
    """

    plaintext: str
    score: float
    candidates: list[dict[str, Any]]
    profile: dict[str, Any]
    artifacts: dict[str, Any] | None = None
    attempt_log: str | None = None
    lineage: list[str] | None = None
    metadata: dict[str, Any] | None = None


def decrypt_best(
    ciphertext: str,
    *,
    strategy: str = "default",
    limit: int = 50,
    weights: dict[str, float] | None = None,
    adaptive: bool = False,
    report: bool = False,
    report_dir: str = "reports",
) -> DecryptResult:
    """Run a composite multi-stage search and return the best plaintext candidate.

    Parameters
    ----------
    ciphertext: Raw K4 ciphertext (whitespace preserved; internal logic will trim as needed).
    strategy: Named stage bundle; currently only "default" recognized.
    limit: Max number of aggregated (and fused) candidates retained.
    weights: Optional manual stage weights for fusion (stage name -> weight).
        If ``adaptive`` is True provided weights are ignored.
    adaptive: If True, derive weights heuristically from candidate linguistic metrics.
    report: If True, generate artifact bundle (PNG, JSON summaries) under report_dir.
    report_dir: Directory root for artifacts.

    Returns
    -------
    DecryptResult: Structured result with best plaintext & diagnostics.
    """

    # Lazy imports to avoid heavy module cost on import
    from .composite import run_composite_pipeline
    from .pipeline import (
        Stage,
        make_berlin_clock_stage,
        make_masking_stage,
        make_transposition_adaptive_stage,
        make_transposition_stage,
    )

    clean_ct = ''.join(ciphertext.split())

    if strategy != "default":
        raise ValueError(f"Unknown strategy '{strategy}' (only 'default' currently supported)")

    # Default stage bundle (ordered): masking -> adaptive transposition -> transposition -> berlin clock
    stages: list[Stage] = [
        make_masking_stage(limit=30),
        make_transposition_adaptive_stage(),
        make_transposition_stage(),
        make_berlin_clock_stage(limit=40),
    ]

    pipeline_out = run_composite_pipeline(
        clean_ct,
        stages=stages,
        report=report,
        report_dir=report_dir,
        limit=limit,
        weights=weights,
        adaptive=adaptive,
    )

    fused = pipeline_out.get("fused") or []
    aggregated = pipeline_out.get("aggregated", [])
    best_list = fused if fused else aggregated
    best_plain = best_list[0]["text"] if best_list else clean_ct
    best_score = best_list[0].get("fused_score", best_list[0].get("score", 0.0)) if best_list else 0.0
    lineage = [r.name for r in pipeline_out.get("results", [])]
    artifacts = pipeline_out.get("artifacts")
    attempt_log = pipeline_out.get("attempt_log")
    profile = pipeline_out.get("profile", {})
    prov = profile.get('provenance_hash')
    metadata = {"stage_strategy": strategy}
    if prov:
        metadata['provenance_hash'] = prov
    return DecryptResult(
        plaintext=best_plain,
        score=best_score,
        candidates=best_list,
        profile=profile,
        artifacts=artifacts,
        attempt_log=attempt_log,
        lineage=lineage,
        metadata=metadata,
    )


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
    # Segmentation utilities
    'generate_partitions': ('kryptos.k4.segmentation', 'generate_partitions'),
    'partitions_for_k4': ('kryptos.k4.segmentation', 'partitions_for_k4'),
    'slice_by_partition': ('kryptos.k4.segmentation', 'slice_by_partition'),
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
    # Substitution solver
    'solve_substitution': ('kryptos.k4.substitution_solver', 'solve_substitution'),
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
