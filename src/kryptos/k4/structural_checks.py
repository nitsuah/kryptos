"""Exact structural checks on K4 that need no key search.

Each function either proves a cipher family cannot have produced K4 (with the 24 confirmed
crib letters) or reports which parameter choices survive. Like
:mod:`kryptos.k4.crib_constraints`, every function takes a ciphertext and crib dict so it
can be run on a planted solution in tests.

- ``output_alphabet_eliminations``: families whose ciphertext alphabet has fewer than 26
  letters (5x5 squares, ADFGX/ADFGVX) cannot emit all 26 letters K4 contains. A
  transposition doesn't change the letter set, so this holds with or without one.
- ``null_gap_periodic``: a periodic key where some null letters sit between the two crib
  blocks (a "masking" step), shifting the key phase of BERLINCLOCK against EASTNORTHEAST.
- ``hill_consistency``: Hill n x n applied directly, for every block alignment, solved as a
  linear system from the crib blocks.
- ``double_rotation_period_scan``: K3's own method (two cascaded grid rotations), padded to a
  full grid because 97 is prime, composed with a periodic key in either order.
- ``transposition_autokey_scan``: columnar transposition composed with a ciphertext autokey.
- ``chaocipher_scan``: Chaocipher with keyed starting alphabets.
"""

from __future__ import annotations

import itertools
from collections.abc import Iterable
from typing import Any

import numpy as np

from .crib_constraints import (
    STANDARD,
    _columnar_pt_to_ct,
    _scan_mappings,
    _solvable_mod_prime,
    crib_letters,
    families,
    key_values,
    keyed_alphabet,
)
from .physical_grid import K4

# ── Output alphabet ─────────────────────────────────────────────────────────

OUTPUT_ALPHABET_SIZES: dict[str, int] = {
    "playfair": 25,
    "two_square": 25,
    "four_square": 25,
    "bifid_5x5": 25,
    "polybius_letters_5x5": 25,
    "adfgx": 5,
    "adfgvx": 6,
}


def output_alphabet_eliminations(ciphertext: str = K4) -> dict[str, Any]:
    """Families whose output alphabet is smaller than the set of letters in ``ciphertext``."""
    letters = sorted(set(ciphertext))
    return {
        "distinct_letters": len(letters),
        "eliminated": sorted(name for name, size in OUTPUT_ALPHABET_SIZES.items() if size < len(letters)),
    }


# ── Nulls between the crib blocks ───────────────────────────────────────────


def _crib_blocks(plain: dict[int, str]) -> list[list[int]]:
    blocks: list[list[int]] = []
    for i in sorted(plain):
        if blocks and i == blocks[-1][-1] + 1:
            blocks[-1].append(i)
        else:
            blocks.append([i])
    return blocks


def null_gap_periodic(
    max_period: int = 26,
    max_nulls: int | None = None,
    ciphertext: str = K4,
    plain: dict[int, str] | None = None,
    keyword: str = "KRYPTOS",
) -> dict[str, list[dict[str, int]]]:
    """Periodic key on the text with ``g`` null letters removed from the gap between crib blocks.

    Nulls before the first crib shift every slot equally, so only the nulls between the
    EAST-NORTHEAST block and the BERLIN-CLOCK block matter. Tests every ``g`` from 1 up to
    the gap length (29 letters for K4), every period, every family. ``g = 0`` is the plain
    periodic key, already covered by ``key_csp.periodic_family_consistency``.
    """
    plain = plain if plain is not None else crib_letters()
    blocks = _crib_blocks(plain)
    groups: list[list[int]] = [blocks[0]]
    for b in blocks[1:]:
        if b[0] == groups[-1][-1] + 1:
            groups[-1] += b
        else:
            groups.append(b)
    first_end, second_start = groups[0][-1], groups[1][0]
    gap = second_start - first_end - 1
    max_nulls = gap if max_nulls is None else min(max_nulls, gap)
    second = set(itertools.chain.from_iterable(groups[1:]))
    out: dict[str, list[dict[str, int]]] = {}
    for name, (alpha, fn) in families(keyword).items():
        kv = key_values(alpha, fn, ciphertext, plain)
        hits = []
        for g in range(1, max_nulls + 1):
            for p in range(1, max_period + 1):
                slots: dict[int, int] = {}
                ok = True
                for i, k in kv.items():
                    s = (i - g if i in second else i) % p
                    if slots.setdefault(s, k) != k:
                        ok = False
                        break
                if ok:
                    hits.append({"nulls": g, "period": p})
        out[name] = hits
    return out


# ── Hill ─────────────────────────────────────────────────────────────────────


def hill_consistency(
    sizes: Iterable[int] = (2, 3, 4, 5),
    ciphertext: str = K4,
    plain: dict[int, str] | None = None,
) -> dict[int, list[dict[str, Any]]]:
    """Hill n x n with no transposition: is there *any* matrix consistent with the crib blocks?

    For each block alignment (offset 0..n-1), every full n-letter block inside a crib gives
    n linear equations per matrix row, in both directions (C = K P and P = K C). Solvable
    over Z26 iff solvable over GF(2) and GF(13). Reports alignments that stay consistent,
    with how many blocks constrained them (fewer than n blocks is too few to mean anything).
    """
    plain = plain if plain is not None else crib_letters()
    out: dict[int, list[dict[str, Any]]] = {}
    for n in sizes:
        hits = []
        for offset in range(n):
            blocks = [b for b in range(offset, len(ciphertext) - n + 1, n) if all(i in plain for i in range(b, b + n))]
            if not blocks:
                continue
            for direction in ("encrypt", "decrypt"):
                ok = True
                for row in range(n):
                    rows, rhs = [], []
                    for b in blocks:
                        pv = [STANDARD.index(plain[i]) for i in range(b, b + n)]
                        cv = [STANDARD.index(ciphertext[i]) for i in range(b, b + n)]
                        src, dst = (pv, cv) if direction == "encrypt" else (cv, pv)
                        rows.append(src)
                        rhs.append(dst[row])
                    if not (_solvable_mod_prime(rows, rhs, 2) and _solvable_mod_prime(rows, rhs, 13)):
                        ok = False
                        break
                if ok:
                    hits.append({"offset": offset, "direction": direction, "blocks": len(blocks)})
        out[n] = hits
    return out


# ── K3-style double rotation ────────────────────────────────────────────────

ROTATIONS = ("identity", "90cw", "90ccw", "180", "flip_h", "flip_v")


def _rotate(tokens: list[int], width: int, rotation: str) -> list[int]:
    """Same grid convention as ``transposition_analysis.apply_rotation`` on a full grid."""
    height = len(tokens) // width
    grid = [tokens[r * width : (r + 1) * width] for r in range(height)]
    if rotation == "90cw":
        grid = [[grid[height - 1 - j][i] for j in range(height)] for i in range(width)]
    elif rotation == "90ccw":
        grid = [[grid[j][width - 1 - i] for j in range(height)] for i in range(width)]
    elif rotation == "180":
        grid = [[grid[height - 1 - i][width - 1 - j] for j in range(width)] for i in range(height)]
    elif rotation == "flip_h":
        grid = [row[::-1] for row in grid]
    elif rotation == "flip_v":
        grid = grid[::-1]
    return [t for row in grid for t in row]


def _divisors(n: int) -> list[int]:
    return [d for d in range(2, n) if n % d == 0]


def double_rotation_mappings(n_text: int = 97, max_pad: int = 11) -> tuple[list[list[int]], list[dict[str, Any]]]:
    """Plaintext-position -> ciphertext-position maps for K3-style double rotations.

    The text is padded with ``pad`` nulls (at the end or the start) to a length with
    non-trivial divisors, rotated twice as in K3, and the nulls are dropped from the output.
    """
    maps, labels = [], []
    for pad in range(0, max_pad + 1):
        total = n_text + pad
        widths = _divisors(total)
        if not widths:
            continue
        for where in ("end", "start") if pad else ("end",):
            tokens = list(range(total))
            is_null = (lambda t: t >= n_text) if where == "end" else (lambda t, pad=pad: t < pad)
            to_plain = (lambda t: t) if where == "end" else (lambda t, pad=pad: t - pad)
            for wa, ra, wb, rb in itertools.product(widths, ROTATIONS, widths, ROTATIONS):
                out = _rotate(_rotate(tokens, wa, ra), wb, rb)
                kept = [t for t in out if not is_null(t)]
                pos = [0] * n_text
                for ci, t in enumerate(kept):
                    pos[to_plain(t)] = ci
                maps.append(pos)
                labels.append({"pad": pad, "nulls_at": where, "width_a": wa, "rot_a": ra, "width_b": wb, "rot_b": rb})
    return maps, labels


def double_rotation_period_scan(
    periods: Iterable[int] = range(1, 23),
    max_pad: int = 11,
    ciphertext: str = K4,
    plain: dict[int, str] | None = None,
    keyword: str = "KRYPTOS",
    max_examples: int = 5,
) -> dict[str, Any]:
    """K3-style double rotation composed with a periodic key, both layer orders."""
    plain = plain if plain is not None else crib_letters()
    positions = sorted(plain)
    maps, labels = double_rotation_mappings(len(ciphertext), max_pad)
    # dedupe identical crib mappings to keep the scan small
    seen: dict[tuple[int, ...], int] = {}
    rows, keep_labels = [], []
    for m, lab in zip(maps, labels, strict=True):
        key = tuple(m[j] for j in positions)
        if key not in seen:
            seen[key] = len(rows)
            rows.append(list(key))
            keep_labels.append(lab)
    cpos = np.array(rows, dtype=np.int64)
    return {
        "mappings": len(maps),
        "distinct_crib_mappings": len(rows),
        **_scan_mappings(cpos, keep_labels, ciphertext, plain, list(periods), keyword, max_examples),
    }


# ── Transposition + autokey ─────────────────────────────────────────────────


def transposition_autokey_scan(
    widths: Iterable[int] = range(2, 8),
    ciphertext: str = K4,
    plain: dict[int, str] | None = None,
    keyword: str = "KRYPTOS",
    min_constraints: int = 4,
    max_examples: int = 5,
) -> dict[str, Any]:
    """Ciphertext autokey applied before a columnar transposition.

    The autokey runs on the pre-transposition text S (S = columnar-decrypt of the ciphertext):
    key_j = alphabet.index(S[j - lag]) + b. Every column order of each width, every lag, every
    constant b, five families. A mapping survives if all crib positions with j >= lag agree
    and at least ``min_constraints`` of them do.
    """
    plain = plain if plain is not None else crib_letters()
    n = len(ciphertext)
    positions = np.array(sorted(plain))
    letters = [plain[i] for i in positions]
    out: dict[str, Any] = {}
    for w in widths:
        perms = np.array(list(itertools.permutations(range(w))), dtype=np.int16)
        start = _columnar_pt_to_ct(w, perms, n)
        allpos = np.arange(n)
        full_map = start[:, allpos % w] + allpos // w  # (P, n): plaintext position -> ciphertext position
        per_family: dict[str, Any] = {}
        for name, (alpha, fn) in families(keyword).items():
            c_idx = np.array([alpha.index(ch) for ch in ciphertext])
            p_idx = np.array([alpha.index(ch) for ch in letters])
            kv = np.vectorize(fn)(c_idx[full_map[:, positions]], p_idx[None, :])  # (P, 24)
            hits, count = [], 0
            for lag in range(1, n):
                usable = positions >= lag
                if usable.sum() < min_constraints:
                    continue
                src = c_idx[full_map[:, positions[usable] - lag]]  # S[j - lag]
                diff = (kv[:, usable] - src) % 26
                ok = (diff == diff[:, :1]).all(axis=1)
                for r in np.flatnonzero(ok):
                    count += 1
                    if len(hits) < max_examples:
                        hits.append({"perm": list(map(int, perms[r])), "lag": lag, "offset": int(diff[r, 0])})
            per_family[name] = {"survivors": count, "examples": hits}
        out[w] = {"permutations": len(perms), **per_family}
    return out


def transposition_running_key_scan(
    corpus: dict[str, str],
    widths: Iterable[int] = range(2, 7),
    ciphertext: str = K4,
    plain: dict[int, str] | None = None,
    keyword: str = "KRYPTOS",
    control_seed: int | None = 0,
) -> dict[str, Any]:
    """Running key composed with a columnar transposition, either order.

    For every column order, source text, alignment and constant offset, counts how many of
    the 24 crib key values the running key reproduces. Reports the best count per width,
    model and family, next to the same scan over a seeded shuffle of each source (control).
    An exact solution scores 24; chance on this many trials is about 8.
    """
    from .crib_constraints import _min_violations

    plain = plain if plain is not None else crib_letters()
    positions = np.array(sorted(plain))
    letters = [plain[i] for i in positions]
    rng = np.random.default_rng(control_seed if control_seed is not None else 0)
    sources = {k: "".join(c for c in v.upper() if c.isalpha()) for k, v in corpus.items()}
    out: dict[str, Any] = {}
    for w in widths:
        perms = np.array(list(itertools.permutations(range(w))), dtype=np.int16)
        start = _columnar_pt_to_ct(w, perms, len(ciphertext))
        cpos = start[:, positions % w] + positions // w
        per: dict[str, Any] = {}
        for name, (alpha, fn) in families(keyword).items():
            c_idx = np.array([alpha.index(ch) for ch in ciphertext])
            kv = np.vectorize(fn)(c_idx[cpos], np.array([alpha.index(ch) for ch in letters])[None, :])
            best = {"sub_then_trans": 0, "trans_then_sub": 0}
            ctl = {"sub_then_trans": 0, "trans_then_sub": 0}
            for text in sources.values():
                arr = np.array([alpha.index(ch) for ch in text])
                shuffled = rng.permutation(arr) if control_seed is not None else None
                for model in best:
                    idx_base = positions[None, :] if model == "sub_then_trans" else cpos
                    lo, hi = int(idx_base.min()), int(idx_base.max())
                    for o in range(-lo, len(arr) - hi):
                        for target, src_arr in ((best, arr), (ctl, shuffled)):
                            if src_arr is None:
                                continue
                            src = src_arr[o + idx_base]
                            diff = (kv - src) % 26
                            m = len(positions) - int(_min_violations(diff, np.zeros_like(diff), 1).min())
                            target[model] = max(target[model], m)
            per[name] = {"best": best, "control": ctl}
        out[w] = {"permutations": len(perms), **per}
    return out


# ── Chaocipher ──────────────────────────────────────────────────────────────


def _chaocipher_decrypt(ct: str, left: str, right: str) -> str:
    """Byrne's Chaocipher (left = cipher alphabet, right = plain alphabet), decrypt direction."""
    left_l, right_l = list(left), list(right)
    out = []
    for ch in ct:
        i = left_l.index(ch)
        p = right_l[i]
        out.append(p)
        # permute left: rotate so ch at zenith, then move position 1 to nadir (13)
        left_l = left_l[i:] + left_l[:i]
        c1 = left_l.pop(1)
        left_l.insert(13, c1)
        # permute right: rotate so p at zenith, shift one more, then move position 2 to nadir
        j = right_l.index(p)
        right_l = right_l[j:] + right_l[:j]
        right_l = right_l[1:] + right_l[:1]
        c2 = right_l.pop(2)
        right_l.insert(13, c2)
    return "".join(out)


def _chaocipher_encrypt(pt: str, left: str, right: str) -> str:
    left_l, right_l = list(left), list(right)
    out = []
    for p in pt:
        j = right_l.index(p)
        c = left_l[j]
        out.append(c)
        i = j
        left_l = left_l[i:] + left_l[:i]
        c1 = left_l.pop(1)
        left_l.insert(13, c1)
        right_l = right_l[j:] + right_l[:j]
        right_l = right_l[1:] + right_l[:1]
        c2 = right_l.pop(2)
        right_l.insert(13, c2)
    return "".join(out)


def chaocipher_scan(
    words: Iterable[str],
    ciphertext: str = K4,
    plain: dict[int, str] | None = None,
    max_examples: int = 5,
) -> dict[str, Any]:
    """Chaocipher with every ordered pair of keyed starting alphabets from ``words``.

    Chaocipher's alphabets change after every letter, so the whole prefix must be decrypted;
    this is a sampled check over a keyword list, not an exhaustive one.
    """
    plain = plain if plain is not None else crib_letters()
    last = max(plain) + 1
    alphabets = sorted({keyed_alphabet(w): w.upper() for w in [*words, "A"]}.items())
    tested, best, hits = 0, 0, []
    for (la, lw), (ra, rw) in itertools.product(alphabets, repeat=2):
        tested += 1
        pt = _chaocipher_decrypt(ciphertext[:last], la, ra)
        m = sum(pt[i] == p for i, p in plain.items())
        best = max(best, m)
        if m == len(plain) and len(hits) < max_examples:
            hits.append({"left": lw, "right": rw})
    return {"pairs_tested": tested, "best_crib_matches": best, "exact": hits}


__all__ = [
    "OUTPUT_ALPHABET_SIZES",
    "chaocipher_scan",
    "double_rotation_mappings",
    "double_rotation_period_scan",
    "hill_consistency",
    "null_gap_periodic",
    "output_alphabet_eliminations",
    "transposition_autokey_scan",
    "transposition_running_key_scan",
]
