"""Tests for Frontier attack modules P2–P7.

P2  — masking_v2 (shadow/null masking variants)
P3  — k2_clock_states (K2 coordinate-derived clock times)
P4  — k2_clock_states (±6-hour timezone offset variants)
P6  — running_key (K3 plaintext as running Vigenère key)
P7  — gronsfeld (K2 coordinate digit-keyed Vigenère)
"""

from __future__ import annotations

import unittest
from datetime import time


class TestMaskingV2Stride(unittest.TestCase):
    """P2 — stride masking variants."""

    def setUp(self):
        from kryptos.k4.masking_v2 import mask_stride
        self._fn = mask_stride

    def test_stride2_correct_length(self):
        residue, meta = self._fn("ABCDE", stride=2)
        # positions 0,2,4 removed → keep 1,3 → "BD"
        self.assertEqual(residue, "BD")
        self.assertEqual(meta["residue_len"], 2)

    def test_stride3_correct_chars(self):
        residue, meta = self._fn("ABCDEFGHI", stride=3)
        # positions 0,3,6 removed → keep 1,2,4,5,7,8 → "BCEFHI"
        self.assertEqual(residue, "BCEFHI")

    def test_stride4_metadata_keys(self):
        residue, meta = self._fn("ABCDEFGHIJKLMN", stride=4)
        for key in ("mode", "original_len", "residue_len", "cribs"):
            self.assertIn(key, meta)
        self.assertEqual(meta["mode"], "stride-4")

    def test_k4_stride2_length(self):
        K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
        residue, meta = self._fn(K4, stride=2)
        self.assertEqual(len(residue), meta["residue_len"])
        self.assertLess(len(residue), 97)

    def test_stride_preserves_alpha(self):
        residue, _ = self._fn("A1B2C3D4E5", stride=2)
        self.assertTrue(all(c.isalpha() for c in residue))


class TestMaskingV2BlockSkip(unittest.TestCase):
    """P2 — block-8 skip."""

    def setUp(self):
        from kryptos.k4.masking_v2 import mask_block_skip
        self._fn = mask_block_skip

    def test_every_8th_removed(self):
        ct = "ABCDEFGHIJKLMNOP"  # 16 chars → 8th (H) removed
        residue, meta = self._fn(ct, block=8)
        self.assertNotIn("H", residue)
        self.assertIn("G", residue)
        self.assertIn("I", residue)

    def test_metadata_mode(self):
        _, meta = self._fn("ABCDEFGH", block=8)
        self.assertEqual(meta["mode"], "block-8-skip")


class TestMaskingV2ClockShadow(unittest.TestCase):
    """P2 — clock-shadow masking."""

    def setUp(self):
        from kryptos.k4.masking_v2 import mask_clock_shadow
        self._fn = mask_clock_shadow

    def test_returns_shorter_or_equal(self):
        K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
        residue, meta = self._fn(K4, time(13, 0, 0))
        self.assertLessEqual(len(residue), 97)
        self.assertIn("clock-shadow", meta["mode"])

    def test_cribs_key_present(self):
        K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
        _, meta = self._fn(K4, time(19, 0, 0))
        self.assertIn("cribs", meta)
        self.assertIn("EAST", meta["cribs"])


class TestMaskingV2ArcFraction(unittest.TestCase):
    """P2 — arc-fraction masking."""

    def setUp(self):
        from kryptos.k4.masking_v2 import mask_arc_fraction
        self._fn = mask_arc_fraction

    def test_removes_neighborhood(self):
        K4 = "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"
        residue, meta = self._fn(K4, time(13, 0), neighborhood=4)
        self.assertLess(len(residue), 97)
        self.assertIn("arc-fraction", meta["mode"])


class TestAllMaskingVariants(unittest.TestCase):
    """P2 — full variant set."""

    def test_returns_eight_variants(self):
        from kryptos.k4.masking_v2 import all_masking_variants
        variants = all_masking_variants()
        self.assertEqual(len(variants), 8)

    def test_all_residues_alpha_only(self):
        from kryptos.k4.masking_v2 import all_masking_variants
        for residue, _ in all_masking_variants():
            self.assertTrue(all(c.isalpha() for c in residue), f"Non-alpha in: {residue!r}")

    def test_all_shorter_than_97(self):
        from kryptos.k4.masking_v2 import all_masking_variants
        for residue, meta in all_masking_variants():
            self.assertLessEqual(len(residue), 97, f"Too long: {meta['mode']}")


# ---------------------------------------------------------------------------
# P3 / P4 — k2_clock_states
# ---------------------------------------------------------------------------

class TestK2ClockStateParsing(unittest.TestCase):
    """P3 — basic time parsing and clock state generation."""

    def setUp(self):
        from kryptos.k4.k2_clock_states import clock_state_for_time, parse_hhmm
        self._clock = clock_state_for_time
        self._parse = parse_hhmm

    def test_parse_hhmm(self):
        t = self._parse("14:57")
        self.assertEqual(t.hour, 14)
        self.assertEqual(t.minute, 57)

    def test_parse_hhmmss(self):
        t = self._parse("13:00:00")
        self.assertEqual(t.hour, 13)
        self.assertEqual(t.minute, 0)
        self.assertEqual(t.second, 0)

    def test_clock_state_keys(self):
        state = self._clock("13:00")
        self.assertIn("time", state)
        self.assertIn("shifts", state)
        self.assertEqual(state["time"], "13:00")

    def test_clock_state_shifts_length(self):
        state = self._clock("19:00")
        self.assertIsInstance(state["shifts"], list)
        self.assertGreater(len(state["shifts"]), 0)


class TestOffsetTime(unittest.TestCase):
    """P4 — timezone offset arithmetic."""

    def setUp(self):
        from kryptos.k4.k2_clock_states import offset_time
        self._fn = offset_time

    def test_plus_6_hours(self):
        result = self._fn("13:00", 6)
        self.assertEqual(result, "19:00")

    def test_minus_6_hours(self):
        result = self._fn("19:00", -6)
        self.assertEqual(result, "13:00")

    def test_midnight_wrap(self):
        result = self._fn("22:00", 6)
        self.assertEqual(result, "04:00")

    def test_past_midnight_wrap(self):
        result = self._fn("01:00", -6)
        self.assertEqual(result, "19:00")


class TestGetK2ClockStates(unittest.TestCase):
    """P3 — full K2 clock state list."""

    def setUp(self):
        from kryptos.k4.k2_clock_states import get_k2_clock_states
        self._fn = get_k2_clock_states

    def test_returns_list(self):
        states = self._fn(include_tz_offset=False)
        self.assertIsInstance(states, list)
        self.assertGreater(len(states), 0)

    def test_each_state_has_shifts(self):
        for s in self._fn():
            self.assertIn("shifts", s)
            self.assertIn("time", s)
            self.assertIn("source", s)

    def test_tz_offset_doubles_count(self):
        base = self._fn(include_tz_offset=False)
        full = self._fn(include_tz_offset=True)
        self.assertGreater(len(full), len(base))

    def test_cia_times_included(self):
        times = [s["time"] for s in self._fn(include_tz_offset=False)]
        self.assertIn("13:00", times)
        self.assertIn("19:00", times)


class TestGetTzOffsetStates(unittest.TestCase):
    """P4 — TZ offset modifier."""

    def setUp(self):
        from kryptos.k4.k2_clock_states import get_tz_offset_states, clock_state_for_time
        self._fn = get_tz_offset_states
        self._base = [clock_state_for_time("13:00")]

    def test_offset_states_larger(self):
        result = self._fn(self._base)
        self.assertGreater(len(result), 1)

    def test_offset_states_contain_original(self):
        result = self._fn(self._base)
        times = [s["time"] for s in result]
        self.assertIn("13:00", times)

    def test_offset_states_flagged(self):
        result = self._fn(self._base)
        offset_states = [s for s in result if s.get("is_offset")]
        self.assertGreater(len(offset_states), 0)


# ---------------------------------------------------------------------------
# P6 — running_key
# ---------------------------------------------------------------------------

class TestRunningKeyDecrypt(unittest.TestCase):
    """P6 — basic running key decrypt/encrypt roundtrip."""

    def setUp(self):
        from kryptos.k4.running_key import running_key_decrypt
        self._fn = running_key_decrypt

    def test_zero_shift_key(self):
        # Key of all A's → no shift → plaintext = ciphertext
        result = self._fn("HELLO", "AAAAA")
        self.assertEqual(result, "HELLO")

    def test_single_shift(self):
        # Key = "B" (shift=1) → H(7) - 1 = G(6) = G
        result = self._fn("I", "B")  # I=8, B=1, 8-1=7=H
        self.assertEqual(result, "H")

    def test_roundtrip(self):
        from kryptos.k4.running_key import running_key_decrypt
        # Manually encrypt "EAST" with key "ABCD"
        # E+A=E, A+B=C, S+C=U, T+D=W → ciphertext ECUW
        # decrypt ECUW with key ABCD → EAST
        plaintext = "EAST"
        key = "ABCD"
        encrypted = "".join(
            chr((ord(p) - ord('A') + ord(k) - ord('A')) % 26 + ord('A'))
            for p, k in zip(plaintext, key)
        )
        result = self._fn(encrypted, key)
        self.assertEqual(result, plaintext)

    def test_key_exhausted_passthrough(self):
        # Key shorter than ciphertext → remaining chars pass through
        result = self._fn("ABCDE", "A")
        self.assertEqual(result[0], "A")  # A shifted by A = A
        # remaining chars are passed through unchanged
        self.assertEqual(result[1:], "BCDE")

    def test_alpha_only_output(self):
        result = self._fn("HELLO", "ABCDE")
        self.assertTrue(all(c.isalpha() for c in result))


class TestK3Key97(unittest.TestCase):
    """P6 — K3 key constant validation."""

    def test_k3_key_length(self):
        from kryptos.k4.running_key import K3_KEY_97
        self.assertEqual(len(K3_KEY_97), 97)

    def test_k3_key_alpha_only(self):
        from kryptos.k4.running_key import K3_KEY_97
        self.assertTrue(all(c.isalpha() for c in K3_KEY_97))

    def test_k3_key_starts_with_slowly(self):
        from kryptos.k4.running_key import K3_KEY_97
        self.assertTrue(K3_KEY_97.startswith("SLOWLYD"))


class TestRunK3RunningKeyAttack(unittest.TestCase):
    """P6 — run_k3_running_key_attack returns well-formed result."""

    def setUp(self):
        from kryptos.k4.running_key import run_k3_running_key_attack
        self._result = run_k3_running_key_attack()

    def test_returns_dict(self):
        self.assertIsInstance(self._result, dict)

    def test_status_null(self):
        self.assertEqual(self._result["status"], "null_result")

    def test_four_variants(self):
        self.assertEqual(len(self._result["best_candidates"]), 4)

    def test_variant_names(self):
        names = [c["variant"] for c in self._result["best_candidates"]]
        self.assertIn("standard_direct", names)
        self.assertIn("standard_reversed", names)
        self.assertIn("kryptos_direct", names)
        self.assertIn("kryptos_reversed", names)


# ---------------------------------------------------------------------------
# P7 — gronsfeld
# ---------------------------------------------------------------------------

class TestGronsfeldDecrypt(unittest.TestCase):
    """P7 — basic Gronsfeld decrypt."""

    def setUp(self):
        from kryptos.k4.gronsfeld import gronsfeld_decrypt, gronsfeld_encrypt
        self._dec = gronsfeld_decrypt
        self._enc = gronsfeld_encrypt

    def test_zero_digit_key(self):
        result = self._dec("HELLO", "00000")
        self.assertEqual(result, "HELLO")

    def test_single_digit_shift(self):
        # H(7) - 1 = G(6), E(4) - 1 = D(3)
        result = self._dec("HE", "1")
        self.assertEqual(result, "GD")

    def test_roundtrip(self):
        key = "123"
        original = "KRYPTOS"
        encrypted = self._enc(original, key)
        decrypted = self._dec(encrypted, key)
        self.assertEqual(decrypted, original)

    def test_wrap_around(self):
        # A(0) - 1 = Z(25)
        result = self._dec("A", "1")
        self.assertEqual(result, "Z")

    def test_non_alpha_passthrough(self):
        result = self._dec("A B", "1")
        self.assertEqual(result[1], " ")

    def test_empty_key_passthrough(self):
        result = self._dec("HELLO", "")
        self.assertEqual(result, "HELLO")


class TestGronsfeldK2Keys(unittest.TestCase):
    """P7 — K2 coordinate keys are digit-only strings."""

    def test_all_keys_are_digit_strings(self):
        from kryptos.k4.gronsfeld import K2_COORDINATE_KEYS
        for k in K2_COORDINATE_KEYS:
            self.assertTrue(all(c.isdigit() for c in k), f"Non-digit in key: {k!r}")

    def test_at_least_one_key(self):
        from kryptos.k4.gronsfeld import K2_COORDINATE_KEYS
        self.assertGreater(len(K2_COORDINATE_KEYS), 0)


class TestRunGronsfeldSweep(unittest.TestCase):
    """P7 — run_gronsfeld_sweep returns null result on K4."""

    def setUp(self):
        from kryptos.k4.gronsfeld import run_gronsfeld_sweep
        self._result = run_gronsfeld_sweep()

    def test_returns_dict(self):
        self.assertIsInstance(self._result, dict)

    def test_status_null(self):
        self.assertEqual(self._result["status"], "null_result")

    def test_total_candidates_positive(self):
        self.assertGreater(self._result["total_candidates"], 0)

    def test_result_keys(self):
        for key in ("keys_tested", "alphabets", "total_candidates", "best_candidates"):
            self.assertIn(key, self._result)

    def test_k2_keys_tested(self):
        from kryptos.k4.gronsfeld import K2_COORDINATE_KEYS
        tested = self._result["keys_tested"]
        for k in K2_COORDINATE_KEYS:
            self.assertIn(k, tested)


if __name__ == "__main__":
    unittest.main()
