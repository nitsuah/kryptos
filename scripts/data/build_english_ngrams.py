"""Build data/ngrams/english_{3,4}grams.tsv from a public-domain English corpus.

Source: the Project Gutenberg selection shipped as NLTK's ``gutenberg`` corpus (18 public
domain books: Austen, Carroll, Chesterton, Melville, Milton, Shakespeare, the KJV Bible,
Whitman and others). Letters only, upper-cased, word boundaries removed, so the tables
match how K4 plaintext is written.

    curl -L -o /tmp/g.zip https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/gutenberg.zip
    unzip -o /tmp/g.zip -d /tmp && python scripts/data/build_english_ngrams.py /tmp/gutenberg

Output: ``GRAM<TAB>log10 probability``, the most frequent ``--top`` grams, with a
``# floor`` header line giving the log10 probability to use for unseen grams.
"""

from __future__ import annotations

import argparse
import math
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def corpus_letters(src: Path) -> str:
    text = "".join(p.read_text(encoding="latin-1") for p in sorted(src.glob("*.txt")))
    return re.sub(r"[^A-Z]", "", text.upper())


def write_table(letters: str, n: int, top: int, out: Path) -> None:
    counts = Counter(letters[i : i + n] for i in range(len(letters) - n + 1))
    total = sum(counts.values())
    floor = math.log10(0.01 / total)
    lines = [
        f"# English {n}-grams, log10 probability. Source: NLTK Gutenberg selection (public domain), "
        f"{len(letters)} letters. Built by scripts/data/build_english_ngrams.py.",
        f"# floor\t{floor:.4f}",
    ]
    lines += [f"{g}\t{math.log10(c / total):.4f}" for g, c in counts.most_common(top)]
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus_dir", type=Path)
    ap.add_argument("--top", type=int, default=40_000)
    args = ap.parse_args()
    letters = corpus_letters(args.corpus_dir)
    for n in (3, 4):
        write_table(letters, n, args.top, ROOT / "data" / "ngrams" / f"english_{n}grams.tsv")


if __name__ == "__main__":
    main()
