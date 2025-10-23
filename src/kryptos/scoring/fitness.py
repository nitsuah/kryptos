from __future__ import annotations

import os


def load_ngram_data(source: str | None = None) -> dict[str, float]:
    if not source:
        return {}
    if not os.path.isfile(source):
        return {}
    data: dict[str, float] = {}
    try:
        with open(source, encoding="utf-8") as fh:
            for line in fh:
                part = line.strip()
                if not part:
                    continue
                pieces = part.split()
                if len(pieces) == 1:
                    token, weight = pieces[0], 1.0
                else:
                    token, weight = pieces[0], float(pieces[1])
                data[token] = weight
    except Exception:
        return {}
    return data
