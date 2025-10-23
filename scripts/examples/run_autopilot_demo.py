"""Compatibility shim: execute the demo script moved into
`scripts/experimental/examples/run_autopilot_demo.py`.

This file keeps the original entrypoint path so tests and CI that call
`scripts/examples/run_autopilot_demo.py` continue to work after the tidy move.
"""

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
target = (HERE.parent / 'experimental' / 'examples' / 'run_autopilot_demo.py').resolve()
if not target.exists():
    print(f"Target demo script not found: {target}", file=sys.stderr)
    sys.exit(2)

# Run the moved script as __main__ so it behaves like a script invocation
runpy.run_path(str(target), run_name="__main__")
