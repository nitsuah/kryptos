"""Thin re-export shim for the canonical top-level modules.

The repository historically imported modules from the top-level `src/` layout
(for example: `import ciphers` or `from k4 import scoring`). To support
editable installs and avoid duplicate implementation code we keep the
canonical implementation under `src/` and expose stable package paths via
lightweight shims here.

This file intentionally performs simple imports from the top-level modules
and re-exports a small, well-defined public API.
"""

try:
    # Prefer the canonical top-level modules (src/ciphers.py, src/analysis.py)
    from analysis import check_cribs, frequency_analysis
    from ciphers import (
        double_rotational_transposition,
        kryptos_k3_decrypt,
        polybius_decrypt,
        transposition_decrypt,
        vigenere_decrypt,
    )
except ImportError:
    # Fall back to package-local copies if the environment imports differently.
    from .analysis import check_cribs, frequency_analysis
    from .ciphers import (
        double_rotational_transposition,
        kryptos_k3_decrypt,
        polybius_decrypt,
        transposition_decrypt,
        vigenere_decrypt,
    )

__all__ = [
    'vigenere_decrypt',
    'kryptos_k3_decrypt',
    'double_rotational_transposition',
    'transposition_decrypt',
    'polybius_decrypt',
    'frequency_analysis',
    'check_cribs',
]
