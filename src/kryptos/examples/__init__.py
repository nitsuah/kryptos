"""Example / demo entrypoints for Kryptos.

These modules provide small, fast demonstrations suitable for CI smoke tests
and local exploration. They replace legacy scripts under `scripts/demo/` and
`scripts/experimental/examples/`.

Public functions:
    k4_demo.run_demo(limit:int=10) -> str | Path
    autopilot_demo.run_autopilot_demo() -> Path
    tiny_weight_sweep.run_tiny_weight_sweep(weights:Sequence[float]|None=None) -> Path
"""

from .autopilot_demo import run_autopilot_demo  # type: ignore  # re-export
from .k4_demo import run_demo  # type: ignore  # re-export
from .tiny_weight_sweep import run_tiny_weight_sweep  # type: ignore  # re-export


def run_composite_demo(limit: int = 12):  # pragma: no cover
    """Run a short composite K4 pipeline with mixed stages and return artifact dir.

    This is a *real* demo (replaces the earlier stub). It composes a couple of
    representative stages (Hill constraint + masking) using the same underlying
    helpers as :func:`kryptos.examples.k4_demo.run_demo` but allows a distinct
    entry for CI or docs that can evolve independently.

    Parameters
    ----------
    limit:
        Candidate limit passed to the composite pipeline.

    Returns
    -------
    str
        Path to the created artifact directory as a string.
    """
    import logging
    from datetime import datetime

    from kryptos.k4.attempt_logging import persist_attempt_logs
    from kryptos.k4.composite import run_composite_pipeline
    from kryptos.k4.pipeline import make_hill_constraint_stage, make_masking_stage
    from kryptos.logging import setup_logging
    from kryptos.paths import get_artifacts_root

    setup_logging(level=logging.INFO, logger_name="kryptos.demo.composite")
    log = logging.getLogger("kryptos.demo.composite")

    cipher = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTW"
    stages = [
        make_hill_constraint_stage(partial_len=25, partial_min=-150.0),
        make_masking_stage(limit=4),
    ]
    run_composite_pipeline(
        cipher,
        stages,
        report=False,
        weights=None,
        normalize=True,
        adaptive=False,
        limit=limit,
    )
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out_dir = get_artifacts_root() / "demo" / f"composite_run_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)
    persist_attempt_logs(out_dir=str(out_dir), label="K4-COMPOSITE", clear=False)
    log.info("Composite demo complete. Artifacts written to: %s", out_dir)
    return str(out_dir)


def run_sections_demo(include_k4: bool = False):  # pragma: no cover
    """Return structured info about section decrypt callables.

    Instead of just listing the keys this returns a data structure suitable for
    quick inspection or documentation generation. K4 is omitted by default
    because its pipeline entry may be heavy to import.

    Parameters
    ----------
    include_k4: bool (default False)
        Whether to include K4 entry (may trigger heavier imports).

    Returns
    -------
    list[dict]
        One dict per included section with name and callable reference.
    """
    from kryptos.sections import SECTIONS

    info = []
    for name, fn in SECTIONS.items():
        if name == "K4" and not include_k4:
            continue
        info.append({"name": name, "callable": fn})
    return info


__all__ = [
    "run_demo",
    "run_autopilot_demo",
    "run_tiny_weight_sweep",
    "run_composite_demo",
    "run_sections_demo",
]
