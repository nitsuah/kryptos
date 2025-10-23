#!/usr/bin/env python3
"""Minimal reproducible K3 double rotational transposition helper.

Usage:
    python scripts/tools/k3_double_rotation.py

Outputs the derived plaintext (with DESPARATLY) from config K3 ciphertext.
"""

import json
from pathlib import Path

_here = Path(__file__).resolve()
REPO_ROOT = _here
for p in _here.parents:
    if (p / 'pyproject.toml').exists():
        REPO_ROOT = p
        break
print(f'[k3_double_rotation] repo root resolved to {REPO_ROOT}')
CONFIG_PATH = REPO_ROOT / 'config' / 'config.json'


def load_k3():
    with open(CONFIG_PATH, encoding='utf-8') as f:
        cfg = json.load(f)
    ct = ''.join(cfg['ciphertexts']['K3'].split())
    if ct.startswith('?'):
        ct = ct[1:]
    return ct


def rotate_right(matrix):
    rows = len(matrix)
    cols = len(matrix[0])
    return [[matrix[r][c] for r in range(rows - 1, -1, -1)] for c in range(cols)]


def k3_double_rotation(ct: str) -> str:
    cols1, rows1 = 24, 14
    m1 = [list(ct[i * cols1 : (i + 1) * cols1]) for i in range(rows1)]
    m2 = rotate_right(m1)
    t1 = ''.join(''.join(r) for r in m2)
    cols2 = 8
    rows2 = len(t1) // cols2
    m3 = [list(t1[i * cols2 : (i + 1) * cols2]) for i in range(rows2)]
    m4 = rotate_right(m3)
    return ''.join(''.join(r) for r in m4)


def main():
    k3_ct = load_k3()
    pt = k3_double_rotation(k3_ct)
    print(pt)


if __name__ == '__main__':
    main()
