"""Pytest conftest to centralize test environment setup.

This adds the repository root and the `src/` directory to `sys.path` so tests
can import project packages without per-file `sys.path` hacks.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Resolve project root (one level up from tests/)
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

for p in (str(ROOT), str(SRC)):
    if p not in sys.path:
        sys.path.insert(0, p)

# Ensure PYTHONPATH contains src for subprocesses
os.environ.setdefault("PYTHONPATH", os.environ.get("PYTHONPATH", ""))
if str(SRC) not in os.environ["PYTHONPATH"]:
    if os.environ["PYTHONPATH"]:
        os.environ["PYTHONPATH"] += os.pathsep + str(SRC)
    else:
        os.environ["PYTHONPATH"] = str(SRC)
