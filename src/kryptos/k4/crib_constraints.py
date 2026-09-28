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
    from .k0_morse_keywords import K0_MORSE_KEYWORDS
    from .running_key import K3_PLAINTEXT_FULL
    from .vigenere_stress_tests import K1_PLAINTEXT, K2_PLAINTEXT
    from .world_clock_cities import CONFIRMED_CITIES

    cfg = json.loads((Path(__file__).resolve().parents[3] / "config" / "config.json").read_text())
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


def _scan_mappings(
    cpos: np.ndarray,
    labels: list[Any],
    ciphertext: str,
    plain: dict[int, str],
    periods: Iterable[int],
    keyword: str,
    max_examples: int,
) -> dict[str, Any]:
    """cpos[row, t] = ciphertext position holding crib letter t under mapping ``row``."""
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
            **_scan_mappings(cpos, labels, ciphertext, plain, periods, keyword, max_examples),
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
    periods: Iterable[int] = range(1, 27), keyword: str = "KRYPTOS", max_examples: int = 5
) -> dict[str, Any]:
    """The phase 6-7 24-column geometric permutations (trailing/leading remainder, all 24 rotations)."""
    from . import reflection
    from .geometry_combined_sweep import DEFAULT_ORDER_NAMES, composed_flat_indices

    plain = crib_letters()
    positions = sorted(plain)
    rows, labels = [], []
    for order in DEFAULT_ORDER_NAMES:
        for refl in [*reflection.SHAPE_PRESERVING, *reflection.SHAPE_CHANGING]:
            for offset in range(24):
                for mode in ("trailing", "leading"):
                    flat = composed_flat_indices(order, refl, offset, mode)
                    if len(flat) != len(K4):
                        continue
                    # apply_inverse puts ciphertext[i] at pre-transposition position flat[i].
                    inv = {src: i for i, src in enumerate(flat)}
                    rows.append([inv[j] for j in positions])
                    labels.append({"order": order, "reflection": refl, "offset": offset, "remainder": mode})
    cpos = np.array(rows, dtype=np.int64)
    return {"mappings": len(rows), **_scan_mappings(cpos, labels, K4, plain, list(periods), keyword, max_examples)}


# ── Dictionary-scale keyed alphabets ───────────────────────────────────────


def dictionary_words(min_len: int = 3) -> list[str]:
    """English words for keyword tests: the MIT ``english-words`` package (web2 + GCIDE, ~340k)
    if installed, otherwise the small built-in scoring list."""
    try:
        from english_words import get_english_words_set

        words = get_english_words_set(["web2", "gcide"], alpha=True, lower=False)
    except ImportError:
        from .scoring import WORDLIST

        words = set(WORDLIST)
    return sorted({w.upper() for w in words if len(w) >= min_len and w.isalpha()})


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


def _summarize_keywords(scan: dict[str, Any]) -> dict[str, Any]:
    """Keep only periods with survivors so the suite artifact stays small."""
    out: dict[str, Any] = {"alphabets": scan["alphabets"]}
    for name in ("quagmire1", "quagmire2", "quagmire3"):
        if name in scan:
            out[name] = {p: v for p, v in scan[name].items() if v["survivors"]}
    return out


def run_crib_constraint_suite(
    widths: Iterable[int] = range(2, 9),
    artifact_path: str | Path | None = DEFAULT_ARTIFACT_PATH,
) -> dict[str, Any]:
    """Run every test, write one artifact, return the summary."""
    ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    widths = list(widths)
    columnar = columnar_period_scan(widths=widths)
    geometry = geometry_period_scan()
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
        "keyword_alphabets": _summarize_keywords(keyword_alphabet_scan(dictionary_words())),
        "run_params": {"widths": widths, "periods": [1, 26]},
    }
    if artifact_path:
        Path(artifact_path).write_text(json.dumps(summary, indent=2, default=str))
    return summary


__all__ = [
    "ciphertext_autokey",
    "columnar_period_scan",
    "crib_letters",
    "dictionary_words",
    "digit_key",
    "families",
    "geometry_period_scan",
    "key_values",
    "keyword_alphabet_scan",
    "keyed_alphabet",
    "linear_key",
    "plaintext_autokey",
    "progressive_key",
    "run_crib_constraint_suite",
    "running_key_scan",
    "sculpture_corpus",
]
