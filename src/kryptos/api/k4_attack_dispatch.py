"""Dispatch table for K4 frontier attack background jobs.

Maps an incoming `RunAttackRequest.attack_id` to the corresponding attack
module and updates job state (via `kryptos.api.k4_jobs`) as it progresses.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from kryptos.api.k4_jobs import update_job

if TYPE_CHECKING:
    from kryptos.api.k4_attack_routes import RunAttackRequest


def run_attack_worker(job_id: str, req: RunAttackRequest) -> None:
    """Dispatch the correct attack module and update job state on completion."""
    attack_id = req.attack_id

    if attack_id == "p1_three_layer":
        from kryptos.k4.three_layer_composite import CIA_PRIORITY_TIMES, run_three_layer_composite

        clock_step = 86400 if req.priority_only else 3600

        def _progress(info: dict[str, Any]) -> None:
            pct = (info["clock_idx"] / info["total_clock"]) * 100
            update_job(
                job_id,
                progress_pct=round(pct, 1),
                clock_time=info["clock_time"],
                total_candidates=info["total_candidates"],
                top_candidates=info["top_candidates"],
            )

        summary = run_three_layer_composite(
            grid_sizes=req.grid_sizes,
            clock_step_seconds=clock_step,
            priority_clock_times=CIA_PRIORITY_TIMES,
            max_perms_per_grid=req.max_perms_per_grid,
            progress_cb=_progress,
        )

    elif attack_id == "p2_shadow_masking":
        from kryptos.k4.composite_sweep import run_composite_sweep
        from kryptos.k4.masking_v2 import all_masking_variants
        from kryptos.k4.vigenere_key_recovery import KNOWN_KEYED_ALPHABETS

        variants = all_masking_variants()
        best: list[dict[str, Any]] = []
        for i, (residue, meta) in enumerate(variants):
            pct = ((i + 1) / len(variants)) * 100
            update_job(job_id, progress_pct=round(pct, 1), clock_time=meta["mode"], total_candidates=i + 1)
            try:
                result = run_composite_sweep(
                    ciphertext=residue,
                    alphabets=KNOWN_KEYED_ALPHABETS,
                    grid_sizes=[7, 8],
                    clock_step_seconds=43200,
                    max_perms_per_grid=24,
                    null_artifact_path=f"K4_MASK_{meta['mode'].replace(':', '-')}_NULL.json",
                )
                for c in result.get("best_candidates", []):
                    c["mask_mode"] = meta["mode"]
                    best.append(c)
            except Exception:  # noqa: BLE001
                pass
        best.sort(key=lambda r: (-r.get("keyword_hits", 0), -r.get("instructional_score", 0)))
        summary = {
            "status": "null_result",
            "attack": "P2_shadow_masking",
            "variants_tested": len(variants),
            "best_candidates": best[:10],
        }

    elif attack_id == "p3_k2_coord_clock":
        from kryptos.k4.composite_sweep import K4, run_composite_sweep
        from kryptos.k4.k2_clock_states import get_k2_clock_states
        from kryptos.k4.vigenere_key_recovery import KNOWN_KEYED_ALPHABETS

        states = get_k2_clock_states(include_tz_offset=False)
        all_best: list[dict[str, Any]] = []
        for i, state in enumerate(states):
            pct = ((i + 1) / len(states)) * 100
            update_job(job_id, progress_pct=round(pct, 1), clock_time=state["time"], total_candidates=i + 1)
            try:
                from itertools import permutations as _perms

                from kryptos.k4.composite_sweep import _keyword_hits, _vigenere_decrypt
                from kryptos.k4.transposition_analysis import apply_columnar_permutation_reverse

                ct = "".join(c for c in K4.upper() if c.isalpha())
                for alpha_name, alphabet in KNOWN_KEYED_ALPHABETS.items():
                    stripped = _vigenere_decrypt(ct, state["shifts"], alphabet)
                    for n_cols in [7, 8, 10]:
                        for perm in list(_perms(range(n_cols)))[:120]:
                            candidate = apply_columnar_permutation_reverse(stripped, n_cols, list(perm))
                            hits = _keyword_hits(candidate)
                            if hits > 0:
                                all_best.append(
                                    {
                                        "candidate_text": candidate,
                                        "keyword_hits": hits,
                                        "clock_time": state["time"],
                                        "alpha": alpha_name,
                                        "source": state.get("source", ""),
                                    }
                                )
            except Exception:  # noqa: BLE001
                pass
        all_best.sort(key=lambda r: -r["keyword_hits"])
        summary = {
            "status": "null_result",
            "attack": "P3_k2_coord_clock",
            "states_tested": len(states),
            "best_candidates": all_best[:10],
        }

    elif attack_id == "p4_timezone_offset":
        from itertools import permutations as _perms

        from kryptos.k4.composite_sweep import K4, _keyword_hits, _vigenere_decrypt
        from kryptos.k4.k2_clock_states import (
            CIA_TIMESTAMP_TIMES,
            clock_state_for_time,
            get_k2_clock_states,
            get_tz_offset_states,
        )
        from kryptos.k4.transposition_analysis import apply_columnar_permutation_reverse
        from kryptos.k4.vigenere_key_recovery import KNOWN_KEYED_ALPHABETS

        base = [clock_state_for_time(t) for t, _ in CIA_TIMESTAMP_TIMES]
        states = get_tz_offset_states(base)
        ct = "".join(c for c in K4.upper() if c.isalpha())
        all_best = []
        for i, state in enumerate(states):
            pct = ((i + 1) / len(states)) * 100
            update_job(job_id, progress_pct=round(pct, 1), clock_time=state["time"], total_candidates=i + 1)
            for alpha_name, alphabet in KNOWN_KEYED_ALPHABETS.items():
                stripped = _vigenere_decrypt(ct, state["shifts"], alphabet)
                for n_cols in [7, 8, 10]:
                    for perm in list(_perms(range(n_cols)))[:120]:
                        candidate = apply_columnar_permutation_reverse(stripped, n_cols, list(perm))
                        hits = _keyword_hits(candidate)
                        if hits > 0:
                            all_best.append(
                                {
                                    "candidate_text": candidate,
                                    "keyword_hits": hits,
                                    "clock_time": state["time"],
                                    "alpha": alpha_name,
                                    "is_offset": state.get("is_offset", False),
                                }
                            )
        all_best.sort(key=lambda r: -r["keyword_hits"])
        summary = {
            "status": "null_result",
            "attack": "P4_timezone_offset",
            "states_tested": len(states),
            "best_candidates": all_best[:10],
        }

    elif attack_id == "p5_two_crib_filter":
        from kryptos.k4.three_layer_composite import CIA_PRIORITY_TIMES, run_three_layer_composite

        def _progress(info: dict[str, Any]) -> None:
            pct = (info["clock_idx"] / info["total_clock"]) * 100
            update_job(
                job_id,
                progress_pct=round(pct, 1),
                clock_time=info["clock_time"],
                total_candidates=info["total_candidates"],
                top_candidates=info["top_candidates"],
            )

        summary = run_three_layer_composite(
            keyword_eureka_threshold=2,  # relaxed to 2 cribs
            max_perms_per_grid=req.max_perms_per_grid or 120,
            progress_cb=_progress,
            null_artifact_path="K4_P5_2CRIB_NULL.json",
            eureka_snapshot_path="K4_P5_2CRIB_EUREKA.md",
        )
        summary["attack"] = "P5_two_crib_soft_filter"

    elif attack_id == "p6_k3_running_key":
        from kryptos.k4.running_key import run_k3_running_key_attack

        update_job(job_id, progress_pct=50.0, clock_time="running-key")
        summary = run_k3_running_key_attack()

    elif attack_id == "p7_gronsfeld":
        from kryptos.k4.gronsfeld import run_gronsfeld_sweep

        update_job(job_id, progress_pct=50.0, clock_time="gronsfeld")
        summary = run_gronsfeld_sweep()

    elif attack_id == "p14_bearing":
        from kryptos.k4.bearing_attack import run_bearing_attack

        update_job(job_id, progress_pct=25.0, clock_time="bearing-calc")
        summary = run_bearing_attack()

    elif attack_id == "p13_magnetic_declination":
        from itertools import permutations as _perms

        from kryptos.k4.composite_sweep import K4, _keyword_hits, _vigenere_decrypt
        from kryptos.k4.k2_clock_states import get_magnetic_declination_states
        from kryptos.k4.transposition_analysis import apply_columnar_permutation_reverse
        from kryptos.k4.vigenere_key_recovery import KNOWN_KEYED_ALPHABETS

        states = get_magnetic_declination_states()
        ct = "".join(c for c in K4.upper() if c.isalpha())
        all_best = []
        for i, state in enumerate(states):
            pct = ((i + 1) / len(states)) * 100
            update_job(job_id, progress_pct=round(pct, 1), clock_time=state["time"], total_candidates=i + 1)
            for alpha_name, alphabet in KNOWN_KEYED_ALPHABETS.items():
                stripped = _vigenere_decrypt(ct, state["shifts"], alphabet)
                for n_cols in [7, 8, 10]:
                    for perm in list(_perms(range(n_cols)))[:120]:
                        candidate = apply_columnar_permutation_reverse(stripped, n_cols, list(perm))
                        hits = _keyword_hits(candidate)
                        if hits > 0:
                            all_best.append(
                                {
                                    "candidate_text": candidate,
                                    "keyword_hits": hits,
                                    "clock_time": state["time"],
                                    "alpha": alpha_name,
                                    "source": state.get("source", ""),
                                }
                            )
        all_best.sort(key=lambda r: -r["keyword_hits"])
        summary = {
            "status": "null_result",
            "attack": "P13_magnetic_declination",
            "states_tested": len(states),
            "best_candidates": all_best[:10],
        }

    elif attack_id == "p12_misspelling":
        from kryptos.k4.misspelling_alphabets import run_misspelling_sweep

        def _progress_p12(info: dict[str, Any]) -> None:
            pct = (info["clock_idx"] / info["total_clock"]) * 100
            update_job(
                job_id,
                progress_pct=round(pct, 1),
                clock_time=info["clock_time"],
                total_candidates=info["total_candidates"],
                top_candidates=info["top_candidates"],
            )

        summary = run_misspelling_sweep(
            grid_sizes=req.grid_sizes,
            priority_only=req.priority_only,
            max_perms_per_grid=req.max_perms_per_grid or 120,
            progress_cb=_progress_p12,
        )

    elif attack_id == "p11_alt_keywords":
        from kryptos.k4.alt_keywords import run_alt_keyword_sweep

        def _progress_p11(info: dict[str, Any]) -> None:
            pct = (info["clock_idx"] / info["total_clock"]) * 100
            update_job(
                job_id,
                progress_pct=round(pct, 1),
                clock_time=info["clock_time"],
                total_candidates=info["total_candidates"],
                top_candidates=info["top_candidates"],
            )

        summary = run_alt_keyword_sweep(
            grid_sizes=req.grid_sizes,
            priority_only=req.priority_only,
            max_perms_per_grid=req.max_perms_per_grid or 120,
            progress_cb=_progress_p11,
        )

    elif attack_id == "p18_key_csp":
        from kryptos.k4.key_csp import run_key_csp_attack

        update_job(job_id, progress_pct=25.0, clock_time="csp-solving")
        summary = run_key_csp_attack()
        update_job(job_id, progress_pct=100.0)

    elif attack_id == "p21_crib_constraints":
        from kryptos.k4.crib_constraints import run_crib_constraint_suite

        update_job(job_id, progress_pct=10.0, clock_time="constraint-scan")
        summary = run_crib_constraint_suite(widths=range(2, 10))
        update_job(job_id, progress_pct=100.0)

    elif attack_id == "p15_straddling_checkerboard":
        from kryptos.k4.straddling_checkerboard import run_straddling_checkerboard_attack

        update_job(job_id, progress_pct=10.0, clock_time="checkerboard")
        summary = run_straddling_checkerboard_attack()
        update_job(job_id, progress_pct=100.0)

    elif attack_id == "p16_corpus_miner":
        from kryptos.k4.corpus_miner import run_corpus_miner_attack

        update_job(job_id, progress_pct=10.0, clock_time="mining-artifacts")
        summary = run_corpus_miner_attack()
        update_job(job_id, progress_pct=100.0)

    elif attack_id == "p19_advisory_keywords":
        from kryptos.k4.advisory_keywords import run_advisory_keyword_sweep

        def _progress_p19(info: dict[str, Any]) -> None:
            pct = (info["clock_idx"] / info["total_clock"]) * 100
            update_job(
                job_id,
                progress_pct=round(pct, 1),
                clock_time=info["clock_time"],
                total_candidates=info["total_candidates"],
                top_candidates=info["top_candidates"],
            )

        summary = run_advisory_keyword_sweep(
            grid_sizes=req.grid_sizes,
            priority_only=req.priority_only,
            max_perms_per_grid=req.max_perms_per_grid or 120,
            progress_cb=_progress_p19,
        )

    elif attack_id == "p20_cyrillic_projector":
        from kryptos.k4.cyrillic_projector import run_cyrillic_projector_sweep

        def _progress_p20(info: dict[str, Any]) -> None:
            pct = (info["clock_idx"] / info["total_clock"]) * 100
            update_job(
                job_id,
                progress_pct=round(pct, 1),
                clock_time=info["clock_time"],
                total_candidates=info["total_candidates"],
                top_candidates=info["top_candidates"],
            )

        summary = run_cyrillic_projector_sweep(
            grid_sizes=req.grid_sizes,
            priority_only=req.priority_only,
            max_perms_per_grid=req.max_perms_per_grid or 120,
            progress_cb=_progress_p20,
        )

    else:
        summary = {"status": "error", "error": f"Unknown attack: {attack_id}"}

    update_job(
        job_id,
        status="complete",
        progress_pct=100.0,
        summary=summary,
        total_candidates=summary.get(
            "total_candidates", summary.get("states_tested", summary.get("variants_tested", 0))
        ),
        top_candidates=summary.get("best_candidates", [])[:5],
    )
