"""Composite multi-stage pipeline runner and candidate aggregator for K4."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..ciphers import vigenere_decrypt
from ..paths import ensure_reports_dir, provenance_hash
from .attempt_logging import persist_attempt_logs
from .pipeline import Pipeline, Stage, StageResult
from .reporting import generate_candidate_artifacts
from .scoring import combined_plaintext_score_cached as combined_plaintext_score
from .scoring import trigram_entropy, wordlist_hit_rate
from .transposition import search_columnar
from .vigenere_key_recovery import recover_key_by_frequency


def aggregate_stage_candidates(results: list[StageResult]) -> list[dict[str, Any]]:
    agg: list[dict[str, Any]] = []
    for res in results:
        cands = res.metadata.get('candidates', [])
        for c in cands:
            agg.append(
                {
                    'stage': res.name,
                    'score': c.get('score', res.score),
                    'text': c.get('text', res.output),
                    'source': c.get('source', f'stage:{res.name}'),
                    'key': c.get('key'),
                    'time': c.get('time'),
                    'mode': c.get('mode'),
                    'shifts': c.get('shifts'),
                    'trace': c.get('trace'),
                },
            )
    agg.sort(key=lambda x: x.get('score', 0.0), reverse=True)
    return agg


def _min_max(values: list[float]) -> tuple[float, float]:
    return (min(values), max(values)) if values else (0.0, 0.0)


def normalize_scores(candidates: list[dict[str, Any]], key: str = 'score') -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for c in candidates:
        grouped.setdefault(c['stage'], []).append(c)
    out: list[dict[str, Any]] = []
    for group in grouped.values():
        vals = [g.get(key, 0.0) for g in group]
        mn, mx = _min_max(vals)
        span = mx - mn if mx != mn else 1.0
        all_equal = mx == mn
        for g in group:
            ns = 0.5 if all_equal else (g.get(key, 0.0) - mn) / span
            new = dict(g)
            new['norm_score'] = ns
            out.append(new)
    return out


def fuse_scores_weighted(
    candidates: list[dict[str, Any]],
    weights: dict[str, float],
    use_normalized: bool = True,
) -> list[dict[str, Any]]:
    """Fuse scores across stages using supplied weights.
    - If use_normalized True, use 'norm_score' (ensure normalize_scores called first).
    - Otherwise use raw 'score'.
    Returns new candidate list with 'fused_score' and sorted by it desc.
    """
    out: list[dict[str, Any]] = []
    for c in candidates:
        base = c.get('norm_score') if use_normalized else c.get('score')
        w = weights.get(c['stage'], 1.0)
        fused = (base or 0.0) * w
        new = dict(c)
        new['fused_score'] = fused
        out.append(new)
    out.sort(key=lambda x: x.get('fused_score', 0.0), reverse=True)
    return out


def run_composite_pipeline(
    ciphertext: str,
    stages: list[Stage],
    report: bool = True,
    report_dir: str | None = None,
    limit: int = 100,
    weights: dict[str, float] | None = None,
    normalize: bool = True,
    adaptive: bool = False,
    try_all_alphabets: bool = False,
) -> dict[str, Any]:
    """Run multiple stages, aggregate candidates, optionally write artifacts and apply
    weighted fusion.
    weights: mapping of stage name to multiplier; if provided fused ranking appended.
    normalize: apply per-stage min-max before fusion (balances different scoring scales).
    Returns dict with 'results', 'aggregated', optional 'fused', and optional 'artifacts'.
    """
    # If any stage is a composite chain executor, pass try_all_alphabets if supported
    # (This is a minimal patch; for full support, propagate to all relevant custom stages.)
    for stage in stages:
        if hasattr(stage.func, '__self__') and hasattr(stage.func.__self__, 'vigenere_then_transposition'):
            # Patch the method to use try_all_alphabets if present
            orig_func = stage.func
            def patched_func(ct, orig_func=orig_func):
                return orig_func(ct, try_all_alphabets=try_all_alphabets)
            stage.func = patched_func

    pipe = Pipeline(stages)
    stage_results = pipe.run(ciphertext)
    aggregated = aggregate_stage_candidates(stage_results)[:limit]
    prov = provenance_hash(
        ciphertext,
        {
            'stage_names': [r.name for r in stage_results],
            'limit': limit,
            'adaptive': adaptive,
            'weights_provided': bool(weights),
        },
    )
    out: dict[str, Any] = {
        'results': stage_results,
        'aggregated': aggregated,
        'profile': {
            'stage_durations_ms': {
                r.name: (
                    r.metadata.get('duration_ms')
                    if r.metadata.get('duration_ms') is not None
                    else (round(r.metadata['duration'] * 1000.0, 3) if r.metadata.get('duration') is not None else None)
                )
                for r in stage_results
            },
            'provenance_hash': prov,
        },
    }
    lineage = [r.name for r in stage_results]
    fused_candidates: list[dict[str, Any]] = []
    if adaptive:
        weights = adaptive_fusion_weights(aggregated)
        metrics_samples = [
            {
                'stage': c['stage'],
                'wl': wordlist_hit_rate(c['text']),
                'ent': trigram_entropy(c['text']),
            }
            for c in aggregated
        ]
        by_stage: dict[str, list[dict[str, float]]] = {}
        for m in metrics_samples:
            by_stage.setdefault(m['stage'], []).append(m)
        diag: dict[str, dict[str, float]] = {}
        for stage, arr in by_stage.items():
            if not arr:
                continue
            wls = sorted(v['wl'] for v in arr)
            ents = sorted(v['ent'] for v in arr)
            mid_wl = wls[len(wls) // 2]
            mid_ent = ents[len(ents) // 2]
            diag[stage] = {
                'median_wordlist_hit_rate': mid_wl,
                'median_trigram_entropy': mid_ent,
                'adaptive_weight': weights.get(stage, 1.0),
            }
        out['profile']['adaptive_diagnostics'] = diag
    if weights:
        candidates_for_fusion = normalize_scores(aggregated) if normalize else aggregated
        fused_candidates = fuse_scores_weighted(candidates_for_fusion, weights, use_normalized=normalize)
        out['fused'] = fused_candidates[:limit]
    if report:
        if report_dir is None or report_dir == 'reports':
            base = Path(ensure_reports_dir()).parent
            k4_root = base / 'k4_runs'
            k4_root.mkdir(parents=True, exist_ok=True)
            report_dir = str(k4_root)
        artifact_source = fused_candidates if fused_candidates else aggregated
        candidates_for_artifact = [
            {
                'text': c['text'],
                'score': c.get('fused_score', c['score']),
                'source': c.get('source'),
                'key': c.get('key'),
                'lineage': lineage,
                'trace': c.get('trace'),
            }
            for c in artifact_source
        ]
        paths = generate_candidate_artifacts(
            'composite',
            'K4',
            ciphertext,
            candidates_for_artifact,
            out_dir=report_dir,
            limit=limit,
            lineage=lineage,
        )
        out['artifacts'] = paths
        attempt_path = persist_attempt_logs(out_dir=report_dir, label='K4', clear=True)
        out['attempt_log'] = attempt_path
    return out


def adaptive_fusion_weights(candidates: list[dict[str, Any]]) -> dict[str, float]:
    if not candidates:
        return {}
    by_stage: dict[str, dict[str, Any]] = {}
    all_scores: list[float] = []
    for c in candidates:
        sc = c.get('score', 0.0)
        all_scores.append(sc)
        stage = c['stage']
        if stage not in by_stage or sc > by_stage[stage].get('score', -1e9):
            by_stage[stage] = c
    tops = list(by_stage.values())
    wl_rates = [wordlist_hit_rate(t['text']) for t in tops]
    median_wl = sorted(wl_rates)[len(wl_rates) // 2]
    all_scores.sort(reverse=True)
    top_cutoff_index = max(1, int(0.1 * len(all_scores))) - 1
    top_cutoff_score = all_scores[top_cutoff_index]
    weights: dict[str, float] = {}
    for stage, cand in by_stage.items():
        w = 1.0
        wl = wordlist_hit_rate(cand['text'])
        ent = trigram_entropy(cand['text'])
        raw_score = cand.get('score', 0.0)
        if wl > median_wl:
            w += 0.30
        if 3.0 <= ent <= 5.2:
            w += 0.20
        else:
            w -= 0.15
        if raw_score >= top_cutoff_score:
            w += 0.10
        if w < 0.3:
            w = 0.3
        if w > 2.5:
            w = 2.5
        weights[stage] = round(w, 3)
    return weights


class CompositeChainExecutor:
    @staticmethod
    def _finalize_candidates(
        candidates: list[dict[str, Any]],
        top_n: int,
        min_score_threshold: float | None,
    ) -> list[dict[str, Any]]:
        filtered = candidates
        if min_score_threshold is not None:
            filtered = [c for c in candidates if c.get('score', 0.0) >= min_score_threshold]

        # Deterministic ordering even when scores tie.
        filtered.sort(
            key=lambda x: (
                -float(x.get('score', 0.0)),
                str(x.get('plaintext', '')),
                str(x.get('vigenere_key', '')),
                int(x.get('transposition_cols', 0)),
                str(x.get('transposition_perm', '')),
            )
        )
        return filtered[:top_n]


    def vigenere_then_transposition(
        self,
        ciphertext: str,
        vigenere_key_length: int = 8,
        transposition_col_range: tuple[int, int] = (5, 8),
        top_n: int = 5,
        min_score_threshold: float | None = None,
        try_all_alphabets: bool = False,
    ) -> list[dict[str, Any]]:
        """V→T chain: Decrypt Vigenère first, then try transposition on result.

        Args:
            ciphertext: Original ciphertext
            vigenere_key_length: Expected Vigenère key length
            transposition_col_range: (min_cols, max_cols) for transposition
            top_n: Return top N results
            min_score_threshold: Optional minimum score filter applied before returning results
            try_all_alphabets: If True, try all candidate alphabets for Vigenère key recovery

        Returns:
            List of candidates with keys, scores, and plaintext
        """
        v_keys = recover_key_by_frequency(
            ciphertext,
            vigenere_key_length,
            top_n=top_n * 2,
            try_all_alphabets=try_all_alphabets,
        )

        candidates = []
        for v_key in v_keys[:top_n]:
            v_plaintext = vigenere_decrypt(ciphertext, v_key)

            min_cols, max_cols = transposition_col_range
            t_results = search_columnar(v_plaintext, min_cols=min_cols, max_cols=max_cols)
            for t_result in t_results[:3]:
                candidates.append(
                    {
                        'plaintext': t_result['text'],
                        'score': t_result['score'],
                        'vigenere_key': v_key,
                        'transposition_cols': t_result['cols'],
                        'transposition_perm': t_result['perm'],
                        'chain': 'V→T',
                        'threshold_applied': min_score_threshold,
                    },
                )

        return self._finalize_candidates(candidates, top_n, min_score_threshold)

    def transposition_then_vigenere(
        self,
        ciphertext: str,
        transposition_col_range: tuple[int, int] = (5, 8),
        vigenere_key_length: int = 8,
        top_n: int = 5,
        min_score_threshold: float | None = None,
        try_all_alphabets: bool = False,
    ) -> list[dict[str, Any]]:
        """T→V chain: Decrypt transposition first, then Vigenère.

        Args:
            ciphertext: Original ciphertext
            transposition_col_range: (min_cols, max_cols) for transposition
            vigenere_key_length: Expected Vigenère key length
            top_n: Return top N results
            min_score_threshold: Optional minimum score filter applied before returning results
            try_all_alphabets: If True, try all candidate alphabets for Vigenère key recovery

        Returns:
            List of candidates with keys, scores, and plaintext
        """
        candidates = []

        min_cols, max_cols = transposition_col_range
        t_results = search_columnar(ciphertext, min_cols=min_cols, max_cols=max_cols)

        for t_result in t_results[: top_n * 2]:
            t_plaintext = t_result['text']

            v_keys = recover_key_by_frequency(
                t_plaintext,
                vigenere_key_length,
                top_n=3,
                try_all_alphabets=try_all_alphabets,
            )
            for v_key in v_keys:
                v_plaintext = vigenere_decrypt(t_plaintext, v_key)
                score = combined_plaintext_score(v_plaintext)
                candidates.append(
                    {
                        'plaintext': v_plaintext,
                        'score': score,
                        'transposition_cols': t_result['cols'],
                        'transposition_perm': t_result['perm'],
                        'vigenere_key': v_key,
                        'chain': 'T→V',
                        'threshold_applied': min_score_threshold,
                    },
                )

        return self._finalize_candidates(candidates, top_n, min_score_threshold)

    def substitution_then_transposition_then_substitution(
        self,
        ciphertext: str,
        vigenere_key_length: int = 8,
        transposition_col_range: tuple[int, int] = (5, 8),
        second_key_length: int = 6,
        top_n: int = 5,
        min_score_threshold: float | None = None,
        try_all_alphabets: bool = False,
        eureka_snapshot_path: str | Path | None = None,
        eureka_score_threshold: float = 80.0,
    ) -> list[dict[str, Any]]:
        """S→T→S chain: Vigenère → columnar transposition → Vigenère.

        Models the hypothesis that K4 was produced by:
            plaintext → Vigenère₁(key₁) → columnar_transposition(P) → Vigenère₂(key₂) → K4

        The attack inverts each layer in reverse order:
            1. Recover key₂ via frequency analysis, decrypt first Vigenère layer
            2. Search columnar transpositions on each intermediate
            3. Recover key₁ from each transposed result, scoring final candidates

        Args:
            ciphertext:              K4 ciphertext.
            vigenere_key_length:     Length of the first (outer) Vigenère key.
            transposition_col_range: (min, max) column counts for transposition search.
            second_key_length:       Length of the second (inner) Vigenère key.
            top_n:                   Maximum candidates to return.
            min_score_threshold:     Optional minimum plaintext score filter.
            try_all_alphabets:       If True, try keyed alphabets for both Vigenère steps.
            eureka_snapshot_path:    If set, call eureka_check_and_capture on every
                                     candidate that exceeds eureka_score_threshold.
                                     Raises EurekaSignal immediately on a 4-keyword hit.
            eureka_score_threshold:  Instructional score floor before eureka check fires
                                     (avoids calling the heavier check on every candidate).

        Returns:
            List of candidate dicts sorted by score, each containing:
            plaintext, score, outer_vigenere_key, transposition_cols,
            transposition_perm, inner_vigenere_key, chain='S→T→S'.
        """
        # --- Layer 1: undo the outermost Vigenère ---
        outer_keys = recover_key_by_frequency(
            ciphertext,
            vigenere_key_length,
            top_n=top_n * 2,
            try_all_alphabets=try_all_alphabets,
        )

        candidates = []
        for outer_key in outer_keys[:top_n]:
            v1_stripped = vigenere_decrypt(ciphertext, outer_key)

            # --- Layer 2: undo the columnar transposition ---
            min_cols, max_cols = transposition_col_range
            t_results = search_columnar(v1_stripped, min_cols=min_cols, max_cols=max_cols)

            for t_result in t_results[:3]:
                t_stripped = t_result['text']

                # --- Layer 3: undo the innermost Vigenère ---
                inner_keys = recover_key_by_frequency(
                    t_stripped,
                    second_key_length,
                    top_n=3,
                    try_all_alphabets=try_all_alphabets,
                )
                for inner_key in inner_keys:
                    final_pt = vigenere_decrypt(t_stripped, inner_key)
                    score = combined_plaintext_score(final_pt)
                    candidate = {
                        'plaintext':          final_pt,
                        'score':              score,
                        'outer_vigenere_key': outer_key,
                        'transposition_cols': t_result['cols'],
                        'transposition_perm': t_result['perm'],
                        'inner_vigenere_key': inner_key,
                        'chain':              'S→T→S',
                        'threshold_applied':  min_score_threshold,
                    }
                    candidates.append(candidate)

                    # Eureka early-stop: if an optional snapshot path is configured
                    # and this candidate clears the score floor, run the full keyword
                    # check.  EurekaSignal propagates immediately to the caller.
                    if eureka_snapshot_path is not None and score >= eureka_score_threshold:
                        from .eureka import eureka_check_and_capture
                        from .scoring_instructional import combined_instructional_score
                        inst_score = combined_instructional_score(final_pt, gate_entropy=False)
                        key_info = {
                            'outer_vigenere_key': outer_key,
                            'inner_vigenere_key': inner_key,
                            'transposition_cols': t_result['cols'],
                            'transposition_perm': t_result['perm'],
                            'chain': 'S→T→S',
                        }
                        eureka_check_and_capture(
                            final_pt,
                            key_info,
                            extra={'instructional_score': inst_score, 'plaintext_score': score},
                            snapshot_path=eureka_snapshot_path,
                            raise_signal=True,
                        )

        return self._finalize_candidates(candidates, top_n, min_score_threshold)


__all__ = [
    'aggregate_stage_candidates',
    'run_composite_pipeline',
    'normalize_scores',
    'fuse_scores_weighted',
    'adaptive_fusion_weights',
    'CompositeChainExecutor',
]
