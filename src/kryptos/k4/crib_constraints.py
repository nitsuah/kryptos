"""Crib-constraint engine: test whole cipher families against the 24 known letters.

Every sweep in phases 1-7 guessed a fully specified (transposition, key) pair,
decrypted all 97 letters and scored the result. This module works the other
way round. Each confirmed crib letter fixes the key *value* at one position
(for a given cipher family), so a family is only viable if some parameter
choice reproduces all 24 values. Checking that is exact, cheap, and covers
the whole family instead of a hand-picked sample.

Tests (each returns the parameter sets that survive):

- ``ciphertext_autokey`` / ``plaintext_autokey``: key_i = letter at i - lag, plus a constant.
- ``linear_key``: key_i = a*i + b (progressive / arithmetic keys).
- ``digit_key``: Gronsfeld / Gromark-style keys limited to 0-9 on a keyed alphabet.
- ``running_key_scan``: key_i = source_text[offset + i] (+ constant) over a sculpture corpus.
- ``columnar_period_scan``: periodic key composed with every columnar transposition of a
  given width, in both layer orders.
- ``geometry_period_scan``: the same, over the 24-column geometric permutations
  the phase 6-7 sweeps used.

Read "no survivors" as "this family, with these parameter ranges, cannot
produce the confirmed cribs". That is stronger than a null sweep, which
only says the sampled keys were wrong. Each test also reports how many
constraints it actually applied, so weak cases (a lag or period where
only one or two crib pairs interact) are visible rather than counted as
eliminations.
"""

from __future__ import annotations

import itertools
import json
import logging
import random
from collections.abc import Callable, Iterable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from .keystream_validator import K4_CRIBS
from .physical_grid import K4

logger = logging.getLogger(__name__)

STANDARD = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DEFAULT_ARTIFACT_PATH = "K4_CRIB_CONSTRAINTS_NULL.json"

KeyFn = Callable[[int, int], int]


def keyed_alphabet(keyword: str) -> str:
    """Keyword letters first (deduplicated), then the rest of A-Z, as on the Kryptos tableau."""
    seen: list[str] = []
    for c in keyword.upper() + STANDARD:
        if c.isalpha() and c not in seen:
            seen.append(c)
    return "".join(seen)


def families(keyword: str = "KRYPTOS") -> dict[str, tuple[str, KeyFn]]:
    """Cipher families as (alphabet, key_value(cipher_index, plain_index))."""
    ka = keyed_alphabet(keyword)
    tag = keyword.lower()
    return {
        "vigenere": (STANDARD, lambda c, p: (c - p) % 26),
        "beaufort": (STANDARD, lambda c, p: (c + p) % 26),
        "variant_beaufort": (STANDARD, lambda c, p: (p - c) % 26),
        f"quagmire3_{tag}": (ka, lambda c, p: (c - p) % 26),
        f"quagmire3_beaufort_{tag}": (ka, lambda c, p: (c + p) % 26),
    }


def crib_letters(cribs: dict[str, tuple[str, int]] | None = None) -> dict[int, str]:
    """0-indexed position -> known plaintext letter."""
    cribs = cribs if cribs is not None else K4_CRIBS
    out: dict[int, str] = {}
    for word, start in cribs.values():
        for i, ch in enumerate(word):
            out[start + i] = ch
    return out


def key_values(alphabet: str, fn: KeyFn, ciphertext: str = K4, plain: dict[int, str] | None = None) -> dict[int, int]:
    """Key value at each crib position for one family: fn(cipher index, plain index) in ``alphabet``."""
    plain = plain if plain is not None else crib_letters()
    return {i: fn(alphabet.index(ciphertext[i]), alphabet.index(p)) for i, p in sorted(plain.items())}


def _offset_consistent(pairs: list[tuple[int, int]]) -> int | None:
    """Given (source_value, key_value) pairs, return the constant b with key = source + b, if one exists."""
    if not pairs:
        return None
    b = (pairs[0][1] - pairs[0][0]) % 26
    return b if all((k - s) % 26 == b for s, k in pairs) else None


def monoalphabetic_conflicts(ciphertext: str = K4, plain: dict[int, str] | None = None) -> dict[str, list[str]]:
    """Plaintext letters that repeat in the cribs but map to more than one ciphertext letter.

    A fixed monoalphabetic substitution (no transposition) maps each plaintext letter to one
    ciphertext letter, so any entry here rules it out. K4 has 8.
    """
    plain = plain if plain is not None else crib_letters()
    seen: dict[str, set[str]] = {}
    for i, p in plain.items():
        seen.setdefault(p, set()).add(ciphertext[i])
    return {p: sorted(cs) for p, cs in sorted(seen.items()) if len(cs) > 1}


# ── Autokey ────────────────────────────────────────────────────────────────


def ciphertext_autokey(
    ciphertext: str = K4, plain: dict[int, str] | None = None, keyword: str = "KRYPTOS", min_constraints: int = 2
) -> dict[str, Any]:
    """key_i = alphabet.index(C[i-lag]) + b. Positions i < lag use an unknown primer and are skipped."""
    plain = plain if plain is not None else crib_letters()
    out: dict[str, Any] = {}
    for name, (alpha, fn) in families(keyword).items():
        kv = key_values(alpha, fn, ciphertext, plain)
        survivors, weak = [], []
        for lag in range(1, len(ciphertext)):
            pairs = [(alpha.index(ciphertext[i - lag]), k) for i, k in kv.items() if i - lag >= 0]
            b = _offset_consistent(pairs)
            if b is None:
                continue
            (survivors if len(pairs) >= min_constraints else weak).append(
                {"lag": lag, "offset": b, "constraints": len(pairs)}
            )
        out[name] = {"survivors": survivors, "untestable_lags": [w["lag"] for w in weak]}
    return out


def plaintext_autokey(
    ciphertext: str = K4, plain: dict[int, str] | None = None, keyword: str = "KRYPTOS", min_constraints: int = 2
) -> dict[str, Any]:
    """key_i = alphabet.index(P[i-lag]) + b, testable only where both i and i-lag are crib positions."""
    plain = plain if plain is not None else crib_letters()
    out: dict[str, Any] = {}
    for name, (alpha, fn) in families(keyword).items():
        kv = key_values(alpha, fn, ciphertext, plain)
        survivors, weak = [], []
        for lag in range(1, len(ciphertext)):
            pairs = [(alpha.index(plain[i - lag]), k) for i, k in kv.items() if (i - lag) in plain]
            b = _offset_consistent(pairs)
            if b is None:
                continue
            (survivors if len(pairs) >= min_constraints else weak).append(
                {"lag": lag, "offset": b, "constraints": len(pairs)}
            )
        out[name] = {"survivors": survivors, "untestable_lags": [w["lag"] for w in weak]}
    return out


# ── Arithmetic keys ────────────────────────────────────────────────────────


def linear_key(ciphertext: str = K4, plain: dict[int, str] | None = None, keyword: str = "KRYPTOS") -> dict[str, Any]:
    """key_i = (a*i + b) mod 26 for any a, b."""
    plain = plain if plain is not None else crib_letters()
    out: dict[str, Any] = {}
    for name, (alpha, fn) in families(keyword).items():
        kv = key_values(alpha, fn, ciphertext, plain)
        out[name] = [
            {"a": a, "b": b} for a in range(26) for b in range(26) if all((a * i + b) % 26 == k for i, k in kv.items())
        ]
    return out


def progressive_key(
    ciphertext: str = K4,
    plain: dict[int, str] | None = None,
    keyword: str = "KRYPTOS",
    periods: Iterable[int] = range(1, 27),
) -> dict[str, list[dict[str, int]]]:
    """Progressive key: key_i = K[i mod p] + d * floor(i / p). d = 0 is the plain periodic key."""
    plain = plain if plain is not None else crib_letters()
    out: dict[str, list[dict[str, int]]] = {}
    for name, (alpha, fn) in families(keyword).items():
        kv = key_values(alpha, fn, ciphertext, plain)
        hits = []
        for p in periods:
            for d in range(26):
                slots: dict[int, int] = {}
                if all(
                    slots.setdefault(i % p, (k - d * (i // p)) % 26) == (k - d * (i // p)) % 26 for i, k in kv.items()
                ):
                    hits.append({"period": p, "step": d})
        out[name] = hits
    return out


def digit_key(
    keywords: Iterable[str], ciphertext: str = K4, plain: dict[int, str] | None = None
) -> dict[str, dict[str, Any]]:
    """Gronsfeld / Gromark keys use digits 0-9. On a keyed alphabet every crib shift must then be <= 9.

    Tests both directions (cipher - plain, plain - cipher) for each keyword alphabet.
    """
    plain = plain if plain is not None else crib_letters()
    out: dict[str, dict[str, Any]] = {}
    for kw in keywords:
        alpha = keyed_alphabet(kw)
        for direction, fn in (("c_minus_p", lambda c, p: (c - p) % 26), ("p_minus_c", lambda c, p: (p - c) % 26)):
            vals = list(key_values(alpha, fn, ciphertext, plain).values())
            out[f"{kw}:{direction}"] = {
                "viable": max(vals) <= 9,
                "max_shift": max(vals),
                "digits_ok": sum(v <= 9 for v in vals),
            }
    return out


# ── Running key ────────────────────────────────────────────────────────────


def _best_alignment(text: str, kv: dict[int, int], alpha: str, lo: int, hi: int, allow_offset: bool) -> dict[str, Any]:
    """Best-scoring alignment of ``text`` against the crib key values (optionally with a free constant offset)."""
    best: dict[str, Any] = {"matches": -1}
    for start in range(-lo, len(text) - hi):
        src_vals = [(alpha.index(text[start + i]), k) for i, k in kv.items()]
        if allow_offset:
            counts = [0] * 26
            for sv, k in src_vals:
                counts[(k - sv) % 26] += 1
            b = max(range(26), key=counts.__getitem__)
            m = counts[b]
        else:
            b, m = 0, sum(1 for sv, k in src_vals if sv == k)
        if m > best["matches"]:
            best = {"matches": m, "start": start, "offset": b}
    return best


def running_key_scan(
    corpus: dict[str, str],
    ciphertext: str = K4,
    plain: dict[int, str] | None = None,
    keyword: str = "KRYPTOS",
    allow_offset: bool = True,
    control_seed: int | None = 0,
) -> dict[str, Any]:
    """key_i = alphabet.index(text[start + i]) (+ b). Reports the best alignment per source and family.

    ``start`` ranges over every alignment that covers all crib positions. An
    exact match needs all 24 crib values. With a free offset ``b``, the best of
    a few hundred alignments of *random* text typically agrees on 7-8, so each
    source also gets ``control_matches``: the same scan over a seeded shuffle
    of its own letters. A real key would sit far above its control.
    """
    plain = plain if plain is not None else crib_letters()
    positions = sorted(plain)
    lo, hi = positions[0], positions[-1]
    out: dict[str, Any] = {}
    for name, (alpha, fn) in families(keyword).items():
        kv = key_values(alpha, fn, ciphertext, plain)
        per_source = {}
        for src_name, raw in corpus.items():
            text = "".join(c for c in raw.upper() if c.isalpha())
            best = _best_alignment(text, kv, alpha, lo, hi, allow_offset)
            best["exact"] = best["matches"] == len(kv)
            best["alignments"] = max(0, len(text) - hi + lo)
            if control_seed is not None:
                shuffled = list(text)
                random.Random(control_seed).shuffle(shuffled)
                best["control_matches"] = _best_alignment("".join(shuffled), kv, alpha, lo, hi, allow_offset)["matches"]
            per_source[src_name] = best
        out[name] = per_source
    return out


def sculpture_corpus() -> dict[str, str]:
    """Texts physically on, or directly tied to, the sculpture. Each is also included reversed."""
    from kryptos.paths import get_repo_root

    from .k0_morse_keywords import K0_MORSE_KEYWORDS
    from .running_key import K3_PLAINTEXT_FULL
    from .vigenere_stress_tests import K1_PLAINTEXT, K2_PLAINTEXT
    from .world_clock_cities import CONFIRMED_CITIES

    cfg = json.loads((get_repo_root() / "config" / "config.json").read_text(encoding="utf-8"))
    cts = {k: "".join(c for c in v.upper() if c.isalpha()) for k, v in cfg["ciphertexts"].items()}
    base = {
        "K1_plaintext": K1_PLAINTEXT,
        "K2_plaintext": K2_PLAINTEXT,
        "K3_plaintext": K3_PLAINTEXT_FULL,
        "K1_K3_plaintext": K1_PLAINTEXT + K2_PLAINTEXT + K3_PLAINTEXT_FULL,
        "K1_ciphertext": cts["K1"],
        "K2_ciphertext": cts["K2"],
        "K3_ciphertext": cts["K3"],
        "K1_K4_ciphertext": cts["K1"] + cts["K2"] + cts["K3"] + cts["K4"],
        "kryptos_tableau_rows": "".join(
            keyed_alphabet("KRYPTOS")[i:] + keyed_alphabet("KRYPTOS")[:i] for i in range(26)
        ),
        "k0_morse_words": "".join(K0_MORSE_KEYWORDS),
        "world_clock_cities": "".join(CONFIRMED_CITIES),
    }
    corpus = dict(base)
    corpus.update({f"{k}_reversed": v[::-1] for k, v in base.items()})
    return corpus


# ── Transposition + periodic key ───────────────────────────────────────────


def _columnar_pt_to_ct(width: int, perms: np.ndarray, n: int) -> np.ndarray:
    """For a columnar transposition (write rows of ``width``, read columns in ``perm`` order),
    return start-of-column offsets, shape (len(perms), width). Plaintext position j = r*width + c
    lands at ciphertext position start[c] + r. Column lengths match
    ``transposition_analysis.apply_columnar_permutation_encrypt``.
    """
    col_len = np.array([(n - c + width - 1) // width for c in range(width)])
    count = len(perms)
    rank = np.empty_like(perms)
    rank[np.arange(count)[:, None], perms] = np.arange(width, dtype=perms.dtype)
    lens_in_order = col_len[perms]
    starts_by_rank = np.concatenate(
        [np.zeros((count, 1), dtype=np.int64), np.cumsum(lens_in_order, axis=1)[:, :-1]], axis=1
    )
    return np.take_along_axis(starts_by_rank, rank.astype(np.int64), axis=1)


def _period_survivors(key: np.ndarray, slots: np.ndarray) -> np.ndarray:
    """Rows where equal slots always carry equal key values."""
    ks = np.sort(slots * 26 + key, axis=1)
    ss = np.sort(slots, axis=1)
    return (np.diff(ks, axis=1) != 0).sum(1) == (np.diff(ss, axis=1) != 0).sum(1)


def _min_violations(key: np.ndarray, slots: np.ndarray, period: int, chunk: int = 20_000) -> np.ndarray:
    """Per row: the fewest crib letters to discard so that equal slots carry equal key values.

    0 means the row is exactly consistent; 1 means it is consistent if one crib letter
    is wrong (a deliberate error, a masking step, a misread plate).
    """
    rows_total, n = key.shape
    out = np.empty(rows_total, dtype=np.int16)
    width = period * 26
    for start in range(0, rows_total, chunk):
        k = np.asarray(key[start : start + chunk], dtype=np.int64)
        sl = np.asarray(slots[start : start + chunk], dtype=np.int64)
        rows = k.shape[0]
        idx = (np.arange(rows)[:, None] * width + sl * 26 + k).ravel()
        counts = np.bincount(idx, minlength=rows * width).reshape(rows, period, 26)
        out[start : start + rows] = n - counts.max(axis=2).sum(axis=1)
    return out


def _scan_mappings(
    cpos: np.ndarray,
    labels: list[Any],
    ciphertext: str,
    plain: dict[int, str],
    periods: Iterable[int],
    keyword: str,
    max_examples: int,
    tolerance: int = 0,
) -> dict[str, Any]:
    """cpos[row, t] = ciphertext position holding crib letter t under mapping ``row``.

    With ``tolerance`` > 0, each period also reports ``min_violations`` (best row) and
    ``within_tolerance`` (rows needing at most ``tolerance`` discarded crib letters).
    """
    positions = np.array(sorted(plain))
    letters = [plain[i] for i in sorted(plain)]
    result: dict[str, Any] = {}
    for model in ("sub_then_trans", "trans_then_sub"):
        per_family: dict[str, Any] = {}
        for name, (alpha, fn) in families(keyword).items():
            cvals = np.array([alpha.index(ch) for ch in ciphertext])[cpos]
            pvals = np.array([alpha.index(ch) for ch in letters])
            kv = np.vectorize(fn)(cvals, pvals) if cvals.size else cvals
            per_period = {}
            for p in periods:
                # sub_then_trans: key applied at plaintext position; trans_then_sub: at ciphertext position.
                slots = np.broadcast_to(positions % p, cpos.shape) if model == "sub_then_trans" else cpos % p
                ok = _period_survivors(kv, slots)
                equalities = int(len(positions) - len(np.unique(positions % p))) if model == "sub_then_trans" else None
                per_period[p] = {
                    "survivors": int(ok.sum()),
                    "examples": [labels[i] for i in np.flatnonzero(ok)[:max_examples]],
                    "equality_constraints": equalities,
                }
                if tolerance:
                    viol = _min_violations(kv, slots, p)
                    per_period[p]["min_violations"] = int(viol.min())
                    per_period[p]["within_tolerance"] = int((viol <= tolerance).sum())
            per_family[name] = per_period
        result[model] = per_family
    return result


def columnar_period_scan(
    widths: Iterable[int] = range(2, 9),
    periods: Iterable[int] = range(1, 27),
    ciphertext: str = K4,
    plain: dict[int, str] | None = None,
    keyword: str = "KRYPTOS",
    max_examples: int = 5,
    tolerance: int = 0,
) -> dict[int, Any]:
    """Every column order of every width, both layer orders, every period, every family."""
    plain = plain if plain is not None else crib_letters()
    positions = np.array(sorted(plain))
    periods = list(periods)
    out: dict[int, Any] = {}
    for w in widths:
        perms = np.array(list(itertools.permutations(range(w))), dtype=np.int16)
        start = _columnar_pt_to_ct(w, perms, len(ciphertext))
        cpos = start[:, positions % w] + positions // w
        labels = [list(map(int, p)) for p in perms] if len(perms) <= 50_000 else _LazyLabels(perms)
        out[w] = {
            "permutations": len(perms),
            **_scan_mappings(cpos, labels, ciphertext, plain, periods, keyword, max_examples, tolerance),
        }
        logger.info("columnar width %d: %d permutations scanned", w, len(perms))
    return out


class _LazyLabels:
    def __init__(self, perms: np.ndarray):
        """Wrap a large permutation array; labels are built on demand."""
        self._perms = perms

    def __getitem__(self, i: int) -> list[int]:
        """Column order ``i`` as a plain list of ints."""
        return list(map(int, self._perms[i]))


def geometry_period_scan(
    periods: Iterable[int] = range(1, 27),
    keyword: str = "KRYPTOS",
    max_examples: int = 5,
    ciphertext: str = K4,
    plain: dict[int, str] | None = None,
    tolerance: int = 0,
) -> dict[str, Any]:
    """The phase 6-7 24-column geometric permutations (trailing/leading remainder, all 24 rotations)."""
    from . import reflection
    from .geometry_combined_sweep import DEFAULT_ORDER_NAMES, composed_flat_indices

    plain = plain if plain is not None else crib_letters()
    positions = sorted(plain)
    rows, labels = [], []
    for order in DEFAULT_ORDER_NAMES:
        for refl in [*reflection.SHAPE_PRESERVING, *reflection.SHAPE_CHANGING]:
            for offset in range(24):
                for mode in ("trailing", "leading"):
                    flat = composed_flat_indices(order, refl, offset, mode)
                    if len(flat) != len(ciphertext):
                        continue
                    # apply_inverse puts ciphertext[i] at pre-transposition position flat[i].
                    inv = {src: i for i, src in enumerate(flat)}
                    rows.append([inv[j] for j in positions])
                    labels.append({"order": order, "reflection": refl, "offset": offset, "remainder": mode})
    cpos = np.array(rows, dtype=np.int64)
    return {
        "mappings": len(rows),
        **_scan_mappings(cpos, labels, ciphertext, plain, list(periods), keyword, max_examples, tolerance),
    }


# ── Dictionary-scale keyed alphabets ───────────────────────────────────────


def dictionary_source() -> tuple[str, list[str]]:
    """(source name, words): the MIT ``english-words`` package (web2 + GCIDE, ~260k usable words)
    if installed, otherwise the small built-in scoring list, with a logged warning."""
    try:
        from english_words import get_english_words_set

        words = get_english_words_set(["web2", "gcide"], alpha=True, lower=False)
        source = "english-words:web2+gcide"
    except ImportError:
        from .scoring import WORDLIST

        logger.warning(
            "english-words not installed; dictionary scan falls back to the %d-word scoring list", len(WORDLIST)
        )
        words = set(WORDLIST)
        source = "kryptos.k4.scoring.WORDLIST (fallback)"
    return source, sorted({w.upper() for w in words if len(w) >= 3 and w.isalpha()})


def dictionary_words(min_len: int = 3) -> list[str]:
    """English words for keyword tests (see :func:`dictionary_source`)."""
    return [w for w in dictionary_source()[1] if len(w) >= min_len]


def keyword_alphabet_scan(
    words: Iterable[str],
    periods: Iterable[int] = range(1, 27),
    ciphertext: str = K4,
    plain: dict[int, str] | None = None,
    max_examples: int = 10,
) -> dict[str, Any]:
    """Periodic Quagmire I/II/III with *every* word as the alphabet keyword (direct, no transposition).

    - Quagmire I:   plain alphabet keyed, cipher alphabet standard.
    - Quagmire II:  plain standard, cipher keyed.
    - Quagmire III: both keyed with the same keyword (K1/K2's construction).

    Words that produce the same keyed alphabet are tested once. Phases 1-7
    tried about 30 hand-picked keywords; this covers a dictionary.
    """
    plain = plain if plain is not None else crib_letters()
    positions = np.array(sorted(plain))
    c_letters = [ciphertext[i] for i in positions]
    p_letters = [plain[i] for i in positions]
    by_alphabet: dict[str, str] = {}
    for w in words:
        by_alphabet.setdefault(keyed_alphabet(w), w.upper())
    alphabets = list(by_alphabet)
    if not alphabets:
        return {"alphabets": 0, "words": 0}
    idx = np.array([[a.index(ch) for ch in STANDARD] for a in alphabets], dtype=np.int16)  # letter -> position
    c_std = np.array([STANDARD.index(ch) for ch in c_letters])
    p_std = np.array([STANDARD.index(ch) for ch in p_letters])
    c_key = idx[:, c_std]
    p_key = idx[:, p_std]
    variants = {
        "quagmire1": (c_std[None, :] - p_key) % 26,
        "quagmire2": (c_key - p_std[None, :]) % 26,
        "quagmire3": (c_key - p_key) % 26,
    }
    out: dict[str, Any] = {"alphabets": len(alphabets), "words": sum(1 for _ in by_alphabet.values())}
    for name, kv in variants.items():
        per_period = {}
        for p in periods:
            slots = np.broadcast_to(positions % p, kv.shape)
            ok = _period_survivors(kv.astype(np.int64), slots)
            per_period[p] = {
                "survivors": int(ok.sum()),
                "examples": [by_alphabet[alphabets[i]] for i in np.flatnonzero(ok)[:max_examples]],
                "equality_constraints": int(len(positions) - len(np.unique(positions % p))),
            }
        out[name] = per_period
    return out


# ── Two-key structures ─────────────────────────────────────────────────────


def _solvable_mod_prime(rows: list[list[int]], rhs: list[int], q: int) -> bool:
    """Is the linear system rows · x = rhs solvable over GF(q)? (Gaussian elimination.)"""
    m = [[v % q for v in r] + [b % q] for r, b in zip(rows, rhs, strict=True)]
    ncols = len(rows[0]) if rows else 0
    piv_row = 0
    for col in range(ncols):
        pr = next((r for r in range(piv_row, len(m)) if m[r][col]), None)
        if pr is None:
            continue
        m[piv_row], m[pr] = m[pr], m[piv_row]
        inv = pow(m[piv_row][col], q - 2, q)
        m[piv_row] = [(v * inv) % q for v in m[piv_row]]
        for r in range(len(m)):
            if r != piv_row and m[r][col]:
                f = m[r][col]
                m[r] = [(a - f * b) % q for a, b in zip(m[r], m[piv_row], strict=True)]
        piv_row += 1
    return all(any(r[:-1]) or r[-1] == 0 for r in m)


def double_periodic_consistency(
    max_period: int = 20,
    ciphertext: str = K4,
    plain: dict[int, str] | None = None,
    keyword: str = "KRYPTOS",
) -> dict[str, list[tuple[int, int]]]:
    """Key = A[i mod p1] + B[i mod p2] (two stacked periodic keys, e.g. PALIMPSEST + ABSCISSA).

    Exhaustive over *every* pair of keys with those lengths, not a keyword list: the 24
    crib key values give 24 linear equations in p1 + p2 unknowns, solvable over Z26 iff
    solvable over GF(2) and GF(13). Returns the (p1, p2) pairs, 1 <= p1 < p2 <= max_period,
    that stay consistent. Pairs with p1 + p2 near 24 have too few equations to mean much.
    """
    plain = plain if plain is not None else crib_letters()
    out: dict[str, list[tuple[int, int]]] = {}
    for name, (alpha, fn) in families(keyword).items():
        kv = key_values(alpha, fn, ciphertext, plain)
        hits = []
        for p1 in range(1, max_period + 1):
            for p2 in range(p1 + 1, max_period + 1):
                rows, rhs = [], []
                for i, k in kv.items():
                    row = [0] * (p1 + p2)
                    row[i % p1] = 1
                    row[p1 + i % p2] = 1
                    rows.append(row)
                    rhs.append(k)
                if _solvable_mod_prime(rows, rhs, 2) and _solvable_mod_prime(rows, rhs, 13):
                    hits.append((p1, p2))
        out[name] = hits
    return out


KRYPTOS_VOCABULARY: list[str] = sorted({
    "KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK", "SHADOW", "SANBORN", "SCHEIDT",
    "LODESTONE", "COMPASS", "WELTZEITUHR", "URANIA", "LANGLEY", "NORTHEAST", "LAYERTWO",
    "EAST", "IQLUSION", "UNDERGRUUND", "DESPARATLY", "ILLUSION", "UNDERGROUND", "LUCID",
    "MEMORY", "VIRTUALLY", "INVISIBLE", "DIGETAL", "INTERPRETATION", "POSITION", "SHADOWFORCES",
    "WEBSTER", "EGYPT", "CARTER", "TUTANKHAMUN", "ALEXANDERPLATZ", "MENGENLEHREUHR", "WALL",
    "NOVEMBER", "CIA", "LANGLEYVIRGINIA", "MAGNETIC", "NEEDLE", "BURIED", "ENIGMA"
})  # fmt: skip


def quagmire4_scan(
    words: Iterable[str],
    anchor_words: Iterable[str] = KRYPTOS_VOCABULARY,
    periods: Iterable[int] = range(1, 23),
    ciphertext: str = K4,
    plain: dict[int, str] | None = None,
    max_examples: int = 10,
) -> dict[str, Any]:
    """Quagmire IV: plain alphabet keyed by one word, cipher alphabet by another, periodic key.

    A full dictionary x dictionary scan is ~5e10 pairs, so one side is drawn from
    ``anchor_words`` (Kryptos vocabulary) and the other from ``words`` (e.g. the dictionary),
    in both assignments. Returns survivors per period for each assignment.
    """
    plain = plain if plain is not None else crib_letters()
    positions = np.array(sorted(plain))
    c_std = [ciphertext[i] for i in positions]
    p_std = [plain[i] for i in positions]
    by_alpha: dict[str, str] = {}
    for w in words:
        by_alpha.setdefault(keyed_alphabet(w), w.upper())
    alphabets = list(by_alpha)
    idx = np.array([[a.index(ch) for ch in STANDARD] for a in alphabets], dtype=np.int64)
    c_all = idx[:, [STANDARD.index(ch) for ch in c_std]]  # (N, 24) cipher-letter positions in each alphabet
    p_all = idx[:, [STANDARD.index(ch) for ch in p_std]]
    result: dict[str, Any] = {"alphabets": len(alphabets), "anchors": 0}
    anchors = sorted({keyed_alphabet(w): w.upper() for w in anchor_words}.items())
    result["anchors"] = len(anchors)
    for role in ("anchor_plain", "anchor_cipher"):
        per_period: dict[int, dict[str, Any]] = {p: {"survivors": 0, "examples": []} for p in periods}
        for a_alpha, a_word in anchors:
            a_idx = np.array([a_alpha.index(ch) for ch in STANDARD])
            if role == "anchor_plain":
                kv = (c_all - a_idx[[STANDARD.index(ch) for ch in p_std]][None, :]) % 26
            else:
                kv = (a_idx[[STANDARD.index(ch) for ch in c_std]][None, :] - p_all) % 26
            for p in periods:
                ok = _period_survivors(kv, np.broadcast_to(positions % p, kv.shape))
                hits = np.flatnonzero(ok)
                per_period[p]["survivors"] += int(hits.size)
                room = max_examples - len(per_period[p]["examples"])
                per_period[p]["examples"] += [(a_word, by_alpha[alphabets[h]]) for h in hits[:room]]
        result[role] = per_period
    return result


def tolerance_study(
    widths: Iterable[int] = range(2, 9),
    periods: Iterable[int] = range(1, 23),
    tolerance: int = 2,
    controls: int = 3,
    seed: int = 0,
    include_geometry: bool = True,
) -> dict[str, Any]:
    """Allow up to ``tolerance`` wrong crib letters and compare K4 with shuffled-ciphertext controls.

    Sanborn has used deliberate errors before (IQLUSION, DESPARATLY, the K2 "X"). An exact
    check would reject the true method if one crib letter were affected, so this reports
    how many (transposition, period, family) rows get within ``tolerance`` errors, for K4
    and for ``controls`` random reshuffles of K4's own letters. K4 well above its controls
    would be a signal; within their range is chance.

    2026-09-28 run (widths 2-9, periods 1-22, tolerance 2, 4 controls): columnar 368 rows vs
    controls 249-365; geometric 325 vs 250-430. Nothing below period 16 came within 2 errors.
    """
    periods = list(periods)
    widths = list(widths)

    def count(ct: str) -> dict[str, int]:
        out = {"columnar": 0, "geometry": 0}
        for r in columnar_period_scan(widths=widths, periods=periods, ciphertext=ct, tolerance=tolerance).values():
            for model in ("sub_then_trans", "trans_then_sub"):
                out["columnar"] += sum(v["within_tolerance"] for per in r[model].values() for v in per.values())
        if include_geometry:
            g = geometry_period_scan(periods=periods, ciphertext=ct, tolerance=tolerance)
            for model in ("sub_then_trans", "trans_then_sub"):
                out["geometry"] += sum(v["within_tolerance"] for per in g[model].values() for v in per.values())
        return out

    real = count(K4)
    ctl = []
    for i in range(controls):
        letters = list(K4)
        random.Random(seed + i).shuffle(letters)
        ctl.append(count("".join(letters)))
    return {
        "tolerance": tolerance,
        "widths": widths,
        "periods": [periods[0], periods[-1]],
        "k4": real,
        "controls": ctl,
        "above_all_controls": {k: real[k] > max(c[k] for c in ctl) for k in real},
    }


# ── Suite ──────────────────────────────────────────────────────────────────


DIGIT_KEYWORDS = [
    "KRYPTOS", "PALIMPSEST", "ABSCISSA", "BERLIN", "CLOCK", "SHADOW", "SANBORN", "SCHEIDT",
    "LODESTONE", "COMPASS", "WELTZEITUHR", "URANIA", "LANGLEY", "NORTHEAST", "LAYERTWO",
]  # fmt: skip


def _summarize_scan(scan: dict[str, Any]) -> dict[str, Any]:
    """Collapse to total survivors per model/family/period so the artifact stays small."""
    out: dict[str, Any] = {}
    for model in ("sub_then_trans", "trans_then_sub"):
        out[model] = {
            fam: {p: v["survivors"] for p, v in per.items() if v["survivors"]} for fam, per in scan[model].items()
        }
    return out


def _structural_summary() -> dict[str, Any]:
    """Cheap exact checks from :mod:`kryptos.k4.structural_checks` (a few seconds in total)."""
    from . import structural_checks as sc

    rot = sc.double_rotation_period_scan()
    auto = sc.transposition_autokey_scan(widths=range(2, 8))
    return {
        "output_alphabet": sc.output_alphabet_eliminations(),
        "null_gap_periodic": {f: len(v) for f, v in sc.null_gap_periodic().items()},
        "hill": sc.hill_consistency(),
        "double_rotation": {
            "mappings": rot["mappings"],
            **{
                m: {f: sum(v["survivors"] for v in per.values()) for f, per in rot[m].items()}
                for m in ("sub_then_trans", "trans_then_sub")
            },
        },
        "transposition_autokey": {
            w: {f: v["survivors"] for f, v in r.items() if f != "permutations"} for w, r in auto.items()
        },
        "chaocipher": sc.chaocipher_scan(KRYPTOS_VOCABULARY),
    }


def _summarize_keywords(scan: dict[str, Any]) -> dict[str, Any]:
    """Keep only periods with survivors so the suite artifact stays small."""
    out: dict[str, Any] = {"alphabets": scan["alphabets"]}
    for name in ("quagmire1", "quagmire2", "quagmire3"):
        if name in scan:
            out[name] = {p: v for p, v in scan[name].items() if v["survivors"]}
    return out


def run_crib_constraint_suite(
    widths: Iterable[int] = range(2, 10),
    artifact_path: str | Path | None = DEFAULT_ARTIFACT_PATH,
) -> dict[str, Any]:
    """Run every test, write one artifact, return the summary."""
    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    widths = list(widths)
    columnar = columnar_period_scan(widths=widths)
    geometry = geometry_period_scan()
    dict_source, dict_words = dictionary_source()
    summary: dict[str, Any] = {
        "status": "complete",
        "timestamp": ts,
        "ciphertext_autokey": ciphertext_autokey(),
        "plaintext_autokey": plaintext_autokey(),
        "linear_key": linear_key(),
        "progressive_key": progressive_key(),
        "digit_key": digit_key(DIGIT_KEYWORDS),
        "running_key": running_key_scan(sculpture_corpus()),
        "columnar_period": {w: {"permutations": r["permutations"], **_summarize_scan(r)} for w, r in columnar.items()},
        "geometry_period": {"mappings": geometry["mappings"], **_summarize_scan(geometry)},
        "keyword_alphabets": _summarize_keywords(keyword_alphabet_scan(dict_words)),
        "structural": _structural_summary(),
        "run_params": {
            "widths": widths,
            "periods": [1, 26],
            "dictionary_source": dict_source,
            "dictionary_words": len(dict_words),
        },
    }
    if artifact_path:
        Path(artifact_path).write_text(json.dumps(summary, indent=2, default=str))
    return summary


__all__ = [
    "tolerance_study",
    "quagmire4_scan",
    "double_periodic_consistency",
    "ciphertext_autokey",
    "columnar_period_scan",
    "crib_letters",
    "dictionary_source",
    "dictionary_words",
    "digit_key",
    "families",
    "geometry_period_scan",
    "key_values",
    "keyword_alphabet_scan",
    "keyed_alphabet",
    "linear_key",
    "monoalphabetic_conflicts",
    "plaintext_autokey",
    "progressive_key",
    "run_crib_constraint_suite",
    "running_key_scan",
    "sculpture_corpus",
]
