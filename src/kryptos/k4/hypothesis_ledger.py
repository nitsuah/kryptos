"""Machine-readable ledger of K4 hypothesis families and how firmly each is settled.

The narrative docs (K4_ACTIVE_RESEARCH.md, K4_CAPABILITY_TABLE.md) are written
for people. This module is the same picture as data, for the API
(``GET /api/k4/ledger``) and any frontend that wants to draw a coverage map.

Tiers:

- ``eliminated``: exhaustive over the stated parameter range. Checked against the
  24 crib letters, with a positive-control test proving the check can find a
  planted solution.
- ``statistical``: ruled out by statistical evidence (e.g. index of coincidence)
  rather than an exhaustive check. Very unlikely, not impossible.
- ``sampled_null``: specific parameter choices were decrypted and scored, and none
  matched. That rules out those choices only, not the family.
- ``open``: not yet tested in a way that covers the family.
"""

from __future__ import annotations

from typing import Any, Literal

Tier = Literal["eliminated", "statistical", "sampled_null", "open"]
TIERS: tuple[Tier, ...] = ("eliminated", "statistical", "sampled_null", "open")

LEDGER: list[dict[str, Any]] = [
    # ── eliminated ─────────────────────────────────────────────────────────
    {
        "id": "monoalphabetic_direct",
        "family": "Monoalphabetic substitution, no transposition",
        "tier": "eliminated",
        "scope": "any alphabet",
        "evidence": "8 of 9 plaintext letters that repeat within the cribs map to different ciphertext "
        "letters; a fixed substitution cannot do that",
        "module": "kryptos.k4.crib_constraints.monoalphabetic_conflicts",
        "test": "tests/functional/test_k4_crib_constraints.py",
    },
    {
        "id": "monoalphabetic_with_transposition",
        "family": "Monoalphabetic substitution combined with a transposition",
        "tier": "statistical",
        "scope": "any alphabet, any transposition",
        "evidence": "IC is unchanged by both steps, so English plaintext would give ~0.066; K4 gives 0.0361. Strong "
        "statistical evidence, not an exhaustive proof, because a transposition moves the crib positions",
        "module": "kryptos.k4.ic_profile",
        "test": "tests/functional/test_k4_documented_facts.py",
    },
    {
        "id": "direct_periodic",
        "family": "Periodic polyalphabetic, no transposition (Vigenère, Beaufort, Variant, Quagmire III KRYPTOS)",
        "tier": "eliminated",
        "scope": "periods 1-26",
        "evidence": "every period has at least one crib pair in the same key slot with different key values",
        "module": "kryptos.k4.key_csp.periodic_family_consistency",
        "test": "tests/functional/test_k4_documented_facts.py",
    },
    {
        "id": "dictionary_quagmire",
        "family": "Quagmire I / II / III with any dictionary word as the alphabet keyword",
        "tier": "eliminated",
        "scope": "231,933 distinct keyed alphabets (web2 + GCIDE), periods 1-25",
        "evidence": "zero survivors below period 26 (period 26 applies one constraint and passes by chance)",
        "module": "kryptos.k4.crib_constraints.keyword_alphabet_scan",
        "test": "tests/functional/test_k4_crib_constraints.py",
    },
    {
        "id": "ciphertext_autokey",
        "family": "Ciphertext autokey (key = earlier ciphertext letter + constant)",
        "tier": "eliminated",
        "scope": "lags 1-71, five families; lag 72 survives on two constraints (chance level)",
        "evidence": "no consistent constant offset at any tested lag",
        "module": "kryptos.k4.crib_constraints.ciphertext_autokey",
        "test": "tests/functional/test_k4_crib_constraints.py",
    },
    {
        "id": "plaintext_autokey",
        "family": "Plaintext autokey (key = earlier plaintext letter + constant)",
        "tier": "eliminated",
        "scope": "lags 1-11 and 31-51; lags 12, 30, 52 have one crib pair and 13-29, 53-96 have none, "
        "so those stay untestable",
        "evidence": "no consistent constant offset",
        "module": "kryptos.k4.crib_constraints.plaintext_autokey",
        "test": "tests/functional/test_k4_crib_constraints.py",
    },
    {
        "id": "arithmetic_keys",
        "family": "Linear (a*i + b) and progressive (K[i mod p] + d*floor(i/p)) keys",
        "tier": "eliminated",
        "scope": "all a, b; periods 1-26 with every step d; five families",
        "evidence": "no parameter set reproduces the 24 crib key values",
        "module": "kryptos.k4.crib_constraints.linear_key / progressive_key",
        "test": "tests/functional/test_k4_crib_constraints.py",
    },
    {
        "id": "digit_keys",
        "family": "Gronsfeld / Gromark digit keys (0-9) on a keyed alphabet",
        "tier": "eliminated",
        "scope": "15 Kryptos-related keyword alphabets, both directions",
        "evidence": "every alphabet needs a crib shift of 23 or more",
        "module": "kryptos.k4.crib_constraints.digit_key",
        "test": "tests/functional/test_k4_crib_constraints.py",
    },
    {
        "id": "sculpture_running_key",
        "family": "Running key from sculpture texts",
        "tier": "eliminated",
        "scope": "K1-K3 plaintexts and ciphertexts, K1-K4 ciphertext, KRYPTOS tableau rows, K0 Morse words, "
        "Weltzeituhr cities; forward and reversed; every alignment; any constant offset",
        "evidence": "best alignment agrees on 7-8 of 24, the same as a shuffled-text control",
        "module": "kryptos.k4.crib_constraints.running_key_scan",
        "test": "tests/functional/test_k4_crib_constraints.py",
    },
    {
        "id": "columnar_plus_periodic",
        "family": "Columnar transposition composed with a periodic key, either order",
        "tier": "eliminated",
        "scope": "widths 2-9 (all column orders; the default suite run), periods 1-22, five families; "
        "width 10 checked to period 20",
        "evidence": "zero survivors; the few at periods 23-26 are chance-level and decrypt to noise",
        "module": "kryptos.k4.crib_constraints.columnar_period_scan",
        "test": "tests/functional/test_k4_crib_constraints.py",
    },
    {
        "id": "geometry_plus_periodic",
        "family": "Phase 6-7 24-column geometric permutations composed with a periodic key, either order",
        "tier": "eliminated",
        "scope": "7,680 mappings (20 routes x 8 reflections x 24 rotations x 2 remainder modes), periods 1-22",
        "evidence": "zero survivors",
        "module": "kryptos.k4.crib_constraints.geometry_period_scan",
        "test": "tests/functional/test_k4_crib_constraints.py",
    },
    {
        "id": "double_periodic",
        "family": "Sum of two periodic keys (e.g. PALIMPSEST + ABSCISSA), any keywords",
        "tier": "eliminated",
        "scope": "every pair of periods with p1 + p2 <= 24, five families (pairs with p1 + p2 >= 25 have more "
        "unknowns than crib equations and stay untestable)",
        "evidence": "the 24 crib key values give a linear system with no solution over GF(2) or GF(13)",
        "module": "kryptos.k4.crib_constraints.double_periodic_consistency",
        "test": "tests/functional/test_k4_crib_constraints.py",
    },
    {
        "id": "quagmire4_anchor_dictionary",
        "family": "Quagmire IV with one keyword from Kryptos vocabulary and the other from the dictionary",
        "tier": "eliminated",
        "scope": "43 vocabulary words x 231,933 dictionary alphabets, both roles, periods 1-22",
        "evidence": "zero survivors",
        "module": "kryptos.k4.crib_constraints.quagmire4_scan",
        "test": "tests/functional/test_k4_crib_constraints.py",
    },
    {
        "id": "periodic_transposition_with_errors",
        "family": "Columnar / geometric transposition + periodic key, allowing up to 2 wrong crib letters",
        "tier": "statistical",
        "scope": "widths 2-9 and 7,680 geometric mappings, periods 1-22, five families",
        "evidence": "near-miss counts (columnar 368, geometric 325) sit inside the range of shuffled-ciphertext "
        "controls (249-365, 250-430); nothing below period 16 gets within 2 errors",
        "module": "kryptos.k4.crib_constraints.tolerance_study",
        "test": "tests/functional/test_k4_crib_constraints.py",
    },
    # ── sampled nulls ──────────────────────────────────────────────────────
    {
        "id": "berlin_clock_keys",
        "family": "Mengenlehreuhr (Set Theory Clock) lamp states as keys, alone or in composites",
        "tier": "sampled_null",
        "scope": "720 states single-layer; priority timestamps in 2- and 3-layer composites",
        "evidence": "crib shifts reach 17-25, above the clock's maximum row value of 11; Sanborn says BERLIN CLOCK "
        "means the Weltzeituhr",
        "module": "kryptos.k4.composite_sweep, kryptos.k4.three_layer_composite",
        "test": "tests/functional/test_k4_three_layer_composite.py",
    },
    {
        "id": "geometric_tableau_sweeps",
        "family": "Geometric permutations with keystreams read off the KRYPTOS tableau",
        "tier": "sampled_null",
        "scope": "~2.4M candidates across phases 6-7",
        "evidence": "no candidate matched a positional crib",
        "module": "kryptos.k4.geometry_combined_sweep",
        "test": "tests/functional/test_k4_geometry_combined_sweep.py",
    },
    {
        "id": "fractionating",
        "family": "ADFGVX, Nihilist, Trifid, Bifid, Playfair, Four-Square, straddling checkerboard",
        "tier": "sampled_null",
        "scope": "Kryptos-related keywords only",
        "evidence": "no crib hits",
        "module": "kryptos.k4.classical_cipher_sweep and per-cipher modules",
        "test": "tests/functional/test_k4_classical_cipher_sweep.py",
    },
    {
        "id": "hill",
        "family": "Hill cipher",
        "tier": "sampled_null",
        "scope": "2x2 and 3x3 keys derived from BERLIN/CLOCK crib pairs and clock states",
        "evidence": "no consistent matrix produced readable text",
        "module": "kryptos.k4.hill_constraints, kryptos.k4.clock_hill_attack",
        "test": "tests/functional/test_k4_clock_hill_attack.py",
    },
    {
        "id": "keyword_seeded_composites",
        "family": "Keyed alphabets from World Clock cities, K0 Morse, advisory names, Cyrillic Projector words",
        "tier": "sampled_null",
        "scope": "hand-assembled keyword lists inside 3-layer composites",
        "evidence": "no crib hits",
        "module": "kryptos.k4.world_clock_cities, k0_morse_keywords, advisory_keywords, cyrillic_projector",
        "test": "tests/functional/",
    },
    {
        "id": "physical_readings",
        "family": "Shadow angles, solar azimuth, topper rotation, bearings as route directions",
        "tier": "sampled_null",
        "scope": "computed angles and sourced timestamps",
        "evidence": "no crib hits",
        "module": "kryptos.k4.solar_geometry, clock_rotation, bearing_attack",
        "test": "tests/functional/",
    },
    # ── open ───────────────────────────────────────────────────────────────
    {
        "id": "quagmire4_dictionary_pairs",
        "family": "Quagmire IV with both keywords from the full dictionary",
        "tier": "open",
        "scope": "~5e10 pairs; needs pruning beyond the per-side constraints",
        "evidence": "",
        "module": "",
        "test": "",
    },
    {
        "id": "transposition_plus_nonperiodic",
        "family": "Transposition composed with a running or autokey key",
        "tier": "open",
        "scope": "combine columnar/geometric mappings with the autokey and running-key constraints",
        "evidence": "",
        "module": "",
        "test": "",
    },
    {
        "id": "k3_style_rotation",
        "family": "K3-style double rotational transposition (with padding, since 97 is prime) plus a key",
        "tier": "open",
        "scope": "",
        "evidence": "K3 used this method; never checked against the K4 cribs as a constraint",
        "module": "",
        "test": "",
    },
    {
        "id": "chaocipher_family",
        "family": "Self-modifying alphabets (Chaocipher, Alberti-style progressive disks)",
        "tier": "open",
        "scope": "",
        "evidence": "",
        "module": "",
        "test": "",
    },
    {
        "id": "nulls_and_masking_constrained",
        "family": "Null insertion / masking evaluated as crib constraints",
        "tier": "open",
        "scope": "masking was only sampled inside composites",
        "evidence": "",
        "module": "",
        "test": "",
    },
    {
        "id": "compass_rose_bearing",
        "family": "Route or key driven by the CIA compass-rose bearing",
        "tier": "open",
        "scope": "blocked on sourcing: the bearing has never been measured",
        "evidence": "",
        "module": "kryptos.k4.physical_geometry",
        "test": "",
    },
]


def ledger(tier: Tier | None = None) -> list[dict[str, Any]]:
    """Copies of the ledger entries, optionally filtered to one tier."""
    return [dict(e) for e in LEDGER if tier is None or e["tier"] == tier]


def ledger_summary() -> dict[str, Any]:
    """Per-tier counts plus every entry, as served by ``GET /api/k4/ledger``."""
    return {"counts": {t: sum(1 for e in LEDGER if e["tier"] == t) for t in TIERS}, "entries": ledger()}


__all__ = ["LEDGER", "TIERS", "ledger", "ledger_summary"]
