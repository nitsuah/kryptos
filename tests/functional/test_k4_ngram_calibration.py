"""The main scorer's n-gram terms must separate English from shuffled English.

The old data/ngrams tables held about ten entries each, so combined_plaintext_score barely
moved with language quality (Cohen's d about 4 on 97-letter texts, with overlap). The real
tables (data/ngrams/english_{2,3,4}grams.tsv) give d above 9 and no overlap.
"""

from __future__ import annotations

import random
import statistics as st

from kryptos.k4 import scoring
from kryptos.k4.english_model import reference_english


def test_scorer_uses_real_ngram_tables():
    assert scoring.NGRAM_SOURCE == "data/ngrams/english_{2,3,4}grams.tsv"
    assert len(scoring.QUADGRAMS) > 10_000


def test_combined_score_separates_english_from_shuffled_english():
    eng, rng, n = reference_english(), random.Random(0), 97
    starts = [rng.randrange(0, len(eng) - n) for _ in range(150)]
    english = [scoring.combined_plaintext_score(eng[s : s + n]) for s in starts]
    shuffled = [scoring.combined_plaintext_score("".join(rng.sample(eng[s : s + n], n))) for s in starts]
    d = (st.mean(english) - st.mean(shuffled)) / ((st.pstdev(english) + st.pstdev(shuffled)) / 2)
    assert d > 7
    assert max(shuffled) < min(english)
