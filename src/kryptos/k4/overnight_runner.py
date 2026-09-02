"""Scheduled/batch runner for K4's full-scope attack sweeps -- Frontier Phase 7.

Idea (ROADMAP.md, 2026-08-28): several full sweeps are sub-minute-to-low-
minutes runtime but still require someone to remember to trigger them
manually from the dashboard. This module is the reusable "run everything
overnight" logic (a thin CLI/script -- see ``scripts/run_k4_overnight_sweeps.py``
-- is the only other piece needed; no new scheduling infrastructure).

Each registered sweep is a zero-argument callable that follows this
project's own convention: returns a summary dict on a null result, or
raises :class:`kryptos.k4.eureka.EurekaSignal` on a genuine breakthrough.
:func:`run_all_pending_sweeps` runs every registered sweep in order and,
the moment any one of them raises, catches it, records it as the returned
summary's breakthrough result, and returns immediately without running
the remaining queued sweeps -- a breakthrough needs a human to look at the
snapshot next, not another sweep started on top of it.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from typing import Any

from .eureka import EurekaSignal

logger = logging.getLogger(__name__)

SweepFn = Callable[[], dict[str, Any]]


def _geometry_combined_default() -> dict[str, Any]:
    from .geometry_combined_sweep import run_geometry_combined_sweep

    return run_geometry_combined_sweep(null_artifact_path="K4_GEOMETRY_COMBINED_NULL.json")


def _geometry_combined_geo_offsets() -> dict[str, Any]:
    from . import clock_rotation
    from .geometry_combined_sweep import run_geometry_combined_sweep

    return run_geometry_combined_sweep(
        rotation_offsets=list(clock_rotation.geography_priority_offsets().values()),
        null_artifact_path="K4_GEOMETRY_COMBINED_GEO_NULL.json",
    )


def _geometry_combined_geo_bearing() -> dict[str, Any]:
    from .geometry_combined_sweep import GEO_BEARING_ORDER_NAMES, run_geometry_combined_sweep

    return run_geometry_combined_sweep(
        order_names=GEO_BEARING_ORDER_NAMES,
        null_artifact_path="K4_GEOMETRY_COMBINED_SOLAR_BEARING_NULL.json",
    )


def _geometry_combined_shape_changing() -> dict[str, Any]:
    from . import reflection
    from .geometry_combined_sweep import run_geometry_combined_sweep

    return run_geometry_combined_sweep(
        reflection_names=reflection.SHAPE_CHANGING,
        null_artifact_path="K4_GEOMETRY_COMBINED_SHAPECHANGING_NULL.json",
    )


def _geometry_combined_topper_rotation() -> dict[str, Any]:
    from . import solar_geometry
    from .geometry_combined_sweep import run_geometry_combined_sweep

    return run_geometry_combined_sweep(
        rotation_offsets=list(solar_geometry.topper_shadow_offsets().values()),
        null_artifact_path="K4_GEOMETRY_COMBINED_TOPPER_ROTATION_NULL.json",
    )


def _three_layer_composite_full() -> dict[str, Any]:
    from .three_layer_composite import run_three_layer_composite

    return run_three_layer_composite(null_artifact_path="K4_3LAYER_NULL.json")


def _three_layer_composite_geometric_full() -> dict[str, Any]:
    from .three_layer_composite import run_three_layer_composite_geometric

    return run_three_layer_composite_geometric(
        full_clock_sweep=True, null_artifact_path="K4_3LAYER_GEOMETRIC_FULL_NULL.json"
    )


def _three_layer_composite_geometric_shape_changing() -> dict[str, Any]:
    from . import reflection
    from .three_layer_composite import run_three_layer_composite_geometric

    return run_three_layer_composite_geometric(
        reflection_names=reflection.SHAPE_CHANGING,
        full_clock_sweep=True,
        null_artifact_path="K4_3LAYER_GEOMETRIC_SHAPECHANGING_NULL.json",
    )


def _world_clock_city_sweep() -> dict[str, Any]:
    from .world_clock_cities import run_world_clock_city_sweep

    return run_world_clock_city_sweep()


def _advisory_keyword_sweep() -> dict[str, Any]:
    from .advisory_keywords import run_advisory_keyword_sweep

    return run_advisory_keyword_sweep()


def _cross_vector_consensus() -> dict[str, Any]:
    # Must run last -- it scans the artifacts every sweep above just wrote.
    from .cross_vector_consensus import run_cross_vector_consensus_attack

    return run_cross_vector_consensus_attack()


# Order matters: cheapest/most-likely-informative first, consensus scoring
# last (it depends on every other sweep's artifact having been written).
PENDING_SWEEPS: dict[str, SweepFn] = {
    "geometry_combined_default": _geometry_combined_default,
    "geometry_combined_geo_offsets": _geometry_combined_geo_offsets,
    "geometry_combined_geo_bearing": _geometry_combined_geo_bearing,
    "geometry_combined_shape_changing": _geometry_combined_shape_changing,
    "geometry_combined_topper_rotation": _geometry_combined_topper_rotation,
    "three_layer_composite_full": _three_layer_composite_full,
    "three_layer_composite_geometric_full": _three_layer_composite_geometric_full,
    "three_layer_composite_geometric_shape_changing": _three_layer_composite_geometric_shape_changing,
    "world_clock_city_sweep": _world_clock_city_sweep,
    "advisory_keyword_sweep": _advisory_keyword_sweep,
    "cross_vector_consensus": _cross_vector_consensus,
}


def run_all_pending_sweeps(
    sweeps: dict[str, SweepFn] | None = None,
    progress_cb: Callable[[str, str], None] | None = None,
) -> dict[str, Any]:
    """Run every registered sweep in order; halt immediately on EurekaSignal.

    Args:
        sweeps: Name -> zero-arg callable registry (default: PENDING_SWEEPS).
        progress_cb: Optional callback(sweep_name, status) fired before/after each sweep.

    Returns:
        Summary dict: per-sweep status/timing, and an overall "status" that
        is "breakthrough" (with the raising sweep's name) if any sweep
        raised EurekaSignal, else "all_null".

    Raises:
        Nothing -- a EurekaSignal from an individual sweep is caught here
        (so the whole run doesn't crash) but recorded prominently and the
        remaining, not-yet-run sweeps are skipped rather than continued
        past an unvalidated breakthrough.
    """
    sweeps = sweeps if sweeps is not None else PENDING_SWEEPS
    results: dict[str, Any] = {}
    order: list[str] = []

    for name, fn in sweeps.items():
        if progress_cb:
            progress_cb(name, "starting")
        t0 = time.time()
        try:
            summary = fn()
            elapsed = time.time() - t0
            results[name] = {
                "status": summary.get("status", "unknown"),
                "elapsed_seconds": round(elapsed, 2),
            }
            order.append(name)
            if progress_cb:
                progress_cb(name, results[name]["status"])
        except EurekaSignal as e:
            elapsed = time.time() - t0
            logger.warning("overnight_runner: EurekaSignal raised by %s -- halting remaining sweeps", name)
            results[name] = {
                "status": "eureka",
                "elapsed_seconds": round(elapsed, 2),
                "snapshot_path": e.snapshot_path,
            }
            order.append(name)
            if progress_cb:
                progress_cb(name, "eureka")
            return {
                "status": "breakthrough",
                "breakthrough_sweep": name,
                "sweeps_run": order,
                "results": results,
            }

    return {"status": "all_null", "sweeps_run": order, "results": results}


__all__ = ["PENDING_SWEEPS", "run_all_pending_sweeps"]
