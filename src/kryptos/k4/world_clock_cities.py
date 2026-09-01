"""World Clock (Weltzeituhr, Alexanderplatz) city list as a keyed-alphabet source -- Frontier Phase 7.

Same category of research as P11/P19's keyword expansion: an untested
external word source tried as a K4 keyed-alphabet seed, rather than a new
cipher mechanism.

Sourced facts (Wikipedia "World Clock (Alexanderplatz)", checked
2026-09-01): the clock's 24-sided rotating cylinder displays 148 city
names across its 24 time-zone segments -- one segment per column of this
project's own 24-column grid, a genuine structural echo worth testing.

A complete city-by-city list is **not available** from any source checked
here -- Wikipedia and every other page fetched describe the count (148)
and the segment structure (24) but do not reproduce the full name list.
Fabricating the remaining ~139 names to pad this module's coverage would
violate this project's own sourcing discipline (see the lodestone-bearing
and K2-offset corrections in ``K4_ACTIVE_RESEARCH.md``), so this module
tests only the specific names individually confirmed in the sources
checked, plus the two sourced structural counts (148 cities, 24 segments)
as numeric parameters. If a complete, sourced city list is ever obtained,
extend ``CONFIRMED_CITIES`` -- do not invent entries.
"""

from __future__ import annotations

from typing import Any

from .advisory_keywords import build_keyed_alphabet

# Individually named in Wikipedia's "World Clock (Alexanderplatz)" article
# (checked 2026-09-01) -- either present since 1969 or added in the 1997
# restoration (noted where relevant).
CONFIRMED_CITIES: list[str] = [
    "NEWDELHI",  # Indian Standard Time segment
    "SAINTPETERSBURG",  # post-1997 (was LENINGRAD until then)
    "LENINGRAD",  # pre-1997 name for the same segment -- tested separately
    "ALMATY",  # post-1997 (was ALMAATA)
    "ALMAATA",  # pre-1997 name for the same segment
    "KYIV",  # moved to Eastern European Time in the 1997 restoration
    "TELAVIV",  # added 1997 (omitted originally for political reasons)
    "CAPETOWN",  # added 1997
    "SEOUL",  # added 1997
]

# Sourced structural counts, not fabricated details.
TOTAL_CITY_COUNT = 148
TOTAL_SEGMENTS = 24  # already this project's own grid column count

WORLD_CLOCK_KEYED_ALPHABETS: dict[str, str] = {city: build_keyed_alphabet(city) for city in CONFIRMED_CITIES}


def world_clock_rotation_offsets() -> dict[str, int]:
    """Numeric parameters derived from the two sourced structural counts.

    Both counts reduced mod the grid's own 24 columns -- the same
    treatment already given to every other geography-derived numeric
    fact in :func:`kryptos.k4.clock_rotation.geography_priority_offsets`.
    """
    return {
        "world_clock_total_cities_mod24": TOTAL_CITY_COUNT % TOTAL_SEGMENTS,
        "world_clock_segments": TOTAL_SEGMENTS % TOTAL_SEGMENTS,  # 0, kept for provenance/completeness
    }


def run_world_clock_city_sweep(
    grid_sizes: list[int] | None = None,
    clock_step_seconds: int = 86400,
    max_perms_per_grid: int = 120,
    priority_only: bool = True,
    progress_cb: Any = None,
    null_artifact_path: str = "K4_WORLD_CLOCK_CITIES_NULL.json",
) -> dict[str, Any]:
    """Run the 3-layer composite with World-Clock-city keyed alphabets.

    Mirrors :func:`kryptos.k4.advisory_keywords.run_advisory_keyword_sweep`
    exactly -- same composite pipeline, only the keyword source differs.
    """
    from .three_layer_composite import CIA_PRIORITY_TIMES, run_three_layer_composite

    clock_step = 86400 if priority_only else clock_step_seconds
    return run_three_layer_composite(
        subst_alphabets=WORLD_CLOCK_KEYED_ALPHABETS,
        grid_sizes=grid_sizes or [7, 8, 10],
        clock_step_seconds=clock_step,
        priority_clock_times=CIA_PRIORITY_TIMES,
        max_perms_per_grid=max_perms_per_grid,
        progress_cb=progress_cb,
        null_artifact_path=null_artifact_path,
        eureka_snapshot_path="K4_WORLD_CLOCK_CITIES_EUREKA.md",
    )


__all__ = [
    "CONFIRMED_CITIES",
    "TOTAL_CITY_COUNT",
    "TOTAL_SEGMENTS",
    "WORLD_CLOCK_KEYED_ALPHABETS",
    "run_world_clock_city_sweep",
    "world_clock_rotation_offsets",
]
