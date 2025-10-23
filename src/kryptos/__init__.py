"""Public Kryptos API surface.

Stable, versioned exports only. Prefer section modules (`kryptos.k1`, `kryptos.k2`,
`kryptos.k3`, `kryptos.k4`) for new code. The direct classical helpers below remain
for compatibility but may be deprecated in a future minor release.
"""

from __future__ import annotations

from collections.abc import Iterable

__version__ = "0.0.1"

from .analysis import check_cribs as check_cribs  # noqa: F401
from .analysis import frequency_analysis as frequency_analysis  # noqa: F401
from .ciphers import (
    double_rotational_transposition as double_rotational_transposition,
)  # noqa: F401
from .ciphers import (
    kryptos_k3_decrypt as kryptos_k3_decrypt,
)
from .ciphers import (
    vigenere_decrypt as vigenere_decrypt,
)

__all__: list[str] = [
    "__version__",
    # Classical / sections primitives
    "vigenere_decrypt",
    "kryptos_k3_decrypt",
    "double_rotational_transposition",
    "frequency_analysis",
    "check_cribs",
]


def _export(iterable: Iterable[str]) -> None:
    for name in iterable:
        if name not in __all__:
            __all__.append(name)


# Optional convenience: expose section decrypt wrappers in root namespace (lightweight).
try:  # pragma: no cover
    from .k1 import decrypt as k1_decrypt  # noqa: F401
    from .k2 import decrypt as k2_decrypt  # noqa: F401
    from .k3 import decrypt as k3_decrypt  # noqa: F401
    from .k4 import decrypt_best as k4_decrypt_best  # noqa: F401

    _export(["k1_decrypt", "k2_decrypt", "k3_decrypt", "k4_decrypt_best"])
except Exception:  # pragma: no cover - keep import failures non-fatal
    pass
