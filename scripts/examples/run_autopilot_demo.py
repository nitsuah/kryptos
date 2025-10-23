"""Compatibility shim: execute the demo script moved into
`scripts/experimental/examples/run_autopilot_demo.py`.

This file keeps the original entrypoint path so tests and CI that call
`scripts/examples/run_autopilot_demo.py` continue to work after the tidy move.
"""

import runpy
import sys
from pathlib import Path

# Ensure we execute using the repository root (look for pyproject.toml as sentinel)
REPO_ROOT = Path(__file__).resolve().parents[1]
sentinel = REPO_ROOT / 'pyproject.toml'
if not sentinel.exists():
    # fallback one more level (monorepo case)
    maybe = REPO_ROOT.parent
    if (maybe / 'pyproject.toml').exists():
        REPO_ROOT = maybe

HERE = Path(__file__).resolve().parent
target = (HERE.parent / 'experimental' / 'examples' / 'run_autopilot_demo.py').resolve()
if REPO_ROOT not in target.parents:
    # Adjust if moved unexpectedly
    alt = REPO_ROOT / 'scripts' / 'experimental' / 'examples' / 'run_autopilot_demo.py'
    if alt.exists():
        target = alt
if not target.exists():
    print(f"Target demo script not found: {target}", file=sys.stderr)
    sys.exit(2)

# Run the moved script as __main__ so it behaves like a script invocation
runpy.run_path(str(target), run_name="__main__")
