"""Test that deprecated function emits DeprecationWarning."""

import warnings

from kryptos.deprecation import deprecated_example


def test_deprecated_example_emits_warning():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        deprecated_example()
        assert any(item.category is DeprecationWarning for item in w)
        assert any("deprecated_example" in str(item.message) for item in w)
