"""English letter n-gram model built from a real corpus.

``data/ngrams/english_{3,4}grams.tsv`` are log10 probabilities from about 8.9 million letters
of public-domain English (see ``scripts/data/build_english_ngrams.py``). The older tables
in ``data/ngrams`` (``quadgrams.tsv`` and friends) hold only about ten illustrative entries
each, so they cannot tell English from noise; new checks use this module instead.

``mean_logp(text, n)`` is the average log10 probability per n-gram, which makes texts of
different lengths comparable. ``english_z(text)`` places a text between shuffled-letter noise
and real English of the same length (``z`` near 0 means random-like, near 1 English-like).
"""

from __future__ import annotations

import random
from functools import cache
from pathlib import Path

from kryptos.paths import get_repo_root

_STD = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


@cache
def table(n: int = 4) -> tuple[dict[str, float], float]:
    """(gram -> log10 probability, floor for unseen grams)."""
    path = Path(get_repo_root()) / "data" / "ngrams" / f"english_{n}grams.tsv"
    grams: dict[str, float] = {}
    floor = -10.0
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# floor"):
            floor = float(line.split("\t")[1])
        elif line and not line.startswith("#"):
            g, v = line.split("\t")
            grams[g] = float(v)
    return grams, floor


def mean_logp(text: str, n: int = 4) -> float:
    """Average log10 probability per n-gram (letters only)."""
    s = "".join(c for c in text.upper() if c in _STD)
    if len(s) < n:
        return 0.0
    grams, floor = table(n)
    return sum(grams.get(s[i : i + n], floor) for i in range(len(s) - n + 1)) / (len(s) - n + 1)


@cache
def reference_english() -> str:
    """Held-out English for calibration: K1-K3 plaintexts plus a fixed passage (not in the corpus)."""
    from .running_key import K3_PLAINTEXT_FULL

    k1 = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"
    k2 = (
        "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLETHEYUSEDTHEEARTHSMAGNETICFIELDXTHEINFORMATION"
        "WASGATHEREDANDTRANSMITTEDUNDERGRUUNDTOANUNKNOWNLOCATIONXDOESLANGLEYKNOWABOUTTHIS"
        "THEYSHOULDITSBURIEDOUTTHERESOMEWHEREXWHOKNOWSTHEEXACTLOCATIONONLYWWTHISWASHISLAST"
        "MESSAGEXTHIRTYEIGHTDEGREESFIFTYSEVENMINUTESSIXPOINTFIVESECONDSNORTHSEVENTYSEVEN"
        "DEGREESEIGHTMINUTESFORTYFOURSECONDSWESTXLAYERTWO"
    )
    extra = (
        "THESCULPTURESTANDSINTHECOURTYARDBETWEENTHEOLDANDNEWHEADQUARTERSBUILDINGSWHERE"
        "EMPLOYEESWALKPASTITEVERYDAYONTHEIRWAYTOLUNCHANDFEWOFTHEMEVERSTOPTOREADTHELETTERS"
    )
    return k1 + k2 + K3_PLAINTEXT_FULL + extra


@cache
def calibration(length: int, n: int = 4, samples: int = 400, seed: int = 0) -> tuple[float, float]:
    """(mean score of random text, mean score of English) for texts of ``length`` letters."""
    rng = random.Random(seed)
    eng = reference_english()
    rnd = [mean_logp("".join(rng.choice(_STD) for _ in range(length)), n) for _ in range(samples)]
    starts = [rng.randrange(0, len(eng) - length) for _ in range(samples)]
    en = [mean_logp(eng[s : s + length], n) for s in starts]
    return sum(rnd) / len(rnd), sum(en) / len(en)


def english_z(text: str, n: int = 4) -> float:
    """0 = typical random text of this length, 1 = typical English of this length."""
    s = "".join(c for c in text.upper() if c in _STD)
    lo, hi = calibration(len(s), n)
    return (mean_logp(s, n) - lo) / (hi - lo)
