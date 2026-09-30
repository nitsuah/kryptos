"""Index-of-coincidence profile of K4, with a significance test.

Single source of truth for the IC figures quoted in the docs. Earlier docs
reported K4's IC as ~0.062 ("near-English") and a local-IC table of
0.058 / 0.071 / 0.062, then built a "substitution happened before
transposition" argument on the unevenness. None of that matches the
ciphertext: K4's IC is 0.0361 (uniform random is 1/26 = 0.0385, English
~0.066), and the three segment ICs are 0.046 / 0.046 / 0.034.

Two consequences, both checkable here:

- IC is invariant under transposition and under monoalphabetic
  substitution, so any cipher built only from those would keep English's
  ~0.066. K4's near-random 0.036 means a polyalphabetic (or otherwise
  flattening) layer is present.
- The segment spread is no bigger than what random reshuffles of K4's own
  letters give (``segment_spread_p_value`` ~0.46), so local IC says nothing
  about the order of layers.
"""

from __future__ import annotations

import random

from .physical_grid import K4
from .scoring import index_of_coincidence

RANDOM_IC = 1 / 26
ENGLISH_IC = 0.0667


def segment_ics(text: str = K4, n_segments: int = 3) -> list[float]:
    """IC of ``n_segments`` near-equal contiguous slices (last slice takes the remainder)."""
    size = len(text) // n_segments
    bounds = [i * size for i in range(n_segments)] + [len(text)]
    return [index_of_coincidence(text[bounds[i] : bounds[i + 1]]) for i in range(n_segments)]


def segment_spread_p_value(text: str = K4, n_segments: int = 3, trials: int = 2000, seed: int = 0) -> float:
    """Fraction of random reshuffles of ``text`` whose segment-IC spread is >= the observed one.

    A large value means the observed unevenness is ordinary sampling noise.
    """
    observed = segment_ics(text, n_segments)
    spread = max(observed) - min(observed)
    rng = random.Random(seed)
    letters = list(text)
    hits = 0
    for _ in range(trials):
        rng.shuffle(letters)
        values = segment_ics("".join(letters), n_segments)
        if max(values) - min(values) >= spread:
            hits += 1
    return hits / trials


def ic_profile(text: str = K4) -> dict[str, object]:
    """Summary used by the docs: overall IC, segment ICs, and the reference values."""
    return {
        "ic": index_of_coincidence(text),
        "segment_ics": segment_ics(text),
        "random_ic": RANDOM_IC,
        "english_ic": ENGLISH_IC,
    }
