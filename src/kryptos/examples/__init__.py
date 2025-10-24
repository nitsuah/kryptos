"""Example / demo entrypoints for Kryptos.

These modules provide small, fast demonstrations suitable for CI smoke tests
and local exploration. They replace legacy scripts under `scripts/demo/` and
`scripts/experimental/examples/`.

Public functions:
    k4_demo.run_demo(limit:int=10) -> str | Path
    autopilot_demo.run_autopilot_demo() -> Path
"""

from .autopilot_demo import run_autopilot_demo  # type: ignore  # re-export
from .k4_demo import run_demo  # type: ignore  # re-export

__all__ = ["run_demo", "run_autopilot_demo"]
