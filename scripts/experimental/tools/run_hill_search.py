#!/usr/bin/env python3
"""DEPRECATED: ad-hoc hill search harness.

All reusable Hill logic now lives in `kryptos/k4/hill_search.py` and `kryptos/k4/hill_constraints.py`.
Planned removal after hypothesis adapter lands.

Replacement usage:
    from kryptos.k4 import hill_search
    score_decryptions = hill_search.score_decryptions
    score_decryptions(ciphertext, keys, limit=1000)
"""

from __future__ import annotations

import argparse
import datetime
import random
from pathlib import Path


def mod_inv_det(mat):
    # compute determinant mod 26 and ensure gcd(det,26)==1
    a = mat
    det = (
        a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
        - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
        + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0])
    ) % 26
    return det


def random_invertible_matrix(size=3, max_tries=1000):
    for _ in range(max_tries):
        mat = [[random.randrange(0, 26) for _ in range(size)] for _ in range(size)]
        det = mod_inv_det(mat)
        # require gcd(det,26) == 1 for invertible in mod26
        if det % 2 != 0 and det % 13 != 0:
            return mat
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--cipher', type=str, default='data/ciphertext.txt')
    parser.add_argument('--tries', type=int, default=200)
    parser.add_argument('--out', type=str, default=None)
    args = parser.parse_args()

    from kryptos.k4 import hill_search  # type: ignore

    score_decryptions = hill_search.score_decryptions
    repo = Path.cwd()

    # read ciphertext
    cpath = Path(args.cipher)
    if cpath.exists():
        ciphertext = cpath.read_text(encoding='utf-8').strip()
    else:
        # fallback short test cipher (example)
        ciphertext = 'KHOORZRUOG'  # 'HELLOWORLD' shifted

    keys = []
    for _ in range(args.tries):
        m = random_invertible_matrix(3)
        if m:
            keys.append(m)

    results = score_decryptions(ciphertext, keys, limit=1000)
    ts = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    outp = Path(args.out) if args.out else (repo / 'artifacts' / 'reports' / f'hill_search_{ts}.md')
    outp.parent.mkdir(parents=True, exist_ok=True)
    with outp.open('w', encoding='utf-8') as fh:
        fh.write(f'# Hill search report {ts}\n\n')
        fh.write(f'ciphertext: {ciphertext[:80]}...\n\n')
        for i, r in enumerate(results[:10], start=1):
            fh.write(f'## Result {i}\n')
            fh.write(f'- score: {r["score"]}\n')
            fh.write(f'- text: "{r["text"]}"\n')
            fh.write(f'- key: {r["key"]}\n\n')

    print('Wrote hill search report to', outp)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
