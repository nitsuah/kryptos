"""Deprecation utilities and example deprecated functions for test coverage."""

from __future__ import annotations

import warnings


def deprecated_example() -> None:
    """Example deprecated API that emits a DeprecationWarning.

    This function will be removed after deprecation window; tests assert warning emission.
    """
    warnings.warn(
        "deprecated_example is deprecated and will be removed in a future release",
        DeprecationWarning,
        stacklevel=2,
    )


__all__ = ["deprecated_example"]
