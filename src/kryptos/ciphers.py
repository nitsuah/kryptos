"""Re-export shim for the canonical top-level `ciphers` module.

This file intentionally delegates implementation to the top-level
`ciphers` module so we avoid duplicate code across the repository while
preserving imports that reference `kryptos.ciphers`.
"""

try:
    from ciphers import (
        double_rotational_transposition,
        kryptos_k3_decrypt,
        polybius_decrypt,
        transposition_decrypt,
        vigenere_decrypt,
    )
except ImportError as e:
    raise ImportError(
        "Could not import top-level 'ciphers' module; ensure 'src' is on PYTHONPATH." f" Original error: {e}",
    ) from e

__all__ = [
    'double_rotational_transposition',
    'kryptos_k3_decrypt',
    'polybius_decrypt',
    'transposition_decrypt',
    'vigenere_decrypt',
]
