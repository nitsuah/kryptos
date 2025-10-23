"""K4 package initialization.

This file intentionally keeps imports minimal to avoid pre-commit linter
failures during packaging changes. The full k4 API is provided by the
individual modules under this package (for example, ``pipeline``).
"""

# Expose the pipeline submodule that exists in the package copy.
from . import pipeline

__all__ = ["pipeline"]
