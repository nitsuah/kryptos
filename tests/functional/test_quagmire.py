"""Tests for kryptos.k4.quagmire and quagmire_sweep."""

from __future__ import annotations

import json
import random
import string

import pytest

from kryptos.ciphers import vigenere_decrypt
from kryptos.k4.eureka import EurekaSignal
from kryptos.k4.quagmire import (
    keyword_alphabet,
    quagmire1_decrypt,
    quagmire1_encrypt,
    quagmire2_decrypt,
    quagmire2_encrypt,
    quagmire3_decrypt,
    quagmire3_encrypt,
    quagmire4_decrypt,
    quagmire4_encrypt,
)
from kryptos.k4.quagmire_sweep import K4, clock_indicator_keys, positional_crib_hits, run_quagmire_sweep

# Verified K1/K2 ground truth (tests/smoke/test_k1_k2_k3_reliability.py)
K1_CIPHERTEXT = "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD"
K1_KEY = "PALIMPSEST"
K1_PLAINTEXT = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"

K2_CIPHERTEXT = (
    "VFPJUDEEHZWETZYVGWHKKQETGFQJNCEGGWHKKDQMCPFQZDQMMIAGPFXHQRLGTIM"
    "VMZJANQLVKQEDAGDVFRPJUNGEUNAQZGZLECGYUXUEENJTBJLBQCRTBJDFHRRYIZE"
    "TKZEMVDUFKSJHKFWHKUWQLSZFTIHHDDDUVHDWKBFUFPWNTDFIYCUQZEREEVLDKFE"
    "ZMOQQJLTTUGSYQPFEUNLAVIDXFLGGTEZFKZBSFDQVGOGIPUFXHHDRKFFHQNTGPUA"
    "ECNUVPDJMQCLQUMUNEDFQELZZVRRGKFFVOEEXBDMVPNFQXEZLGREDNQFCHOBSSPH"
    "FLLOXQRZXGZQAAVTTEXOLIQQTIVWHHMQAUQZMASMRVLQJNWB"
)
K2_KEY = "ABSCISSA"


class TestKeywordAlphabet:
    def test_kryptos_alphabet(self):
        assert keyword_alphabet("KRYPTOS") == "KRYPTOSABCDEFGHIJLMNQUVWXZ"

    def test_empty_keyword_is_standard(self):
        assert keyword_alphabet("") == string.ascii_uppercase

    def test_repeated_letters_deduplicated(self):
        assert keyword_alphabet("BERLINBERLIN").startswith("BERLIN")
        assert len(keyword_alphabet("BERLINBERLIN")) == 26


class TestKryptosGroundTruth:
    """Quagmire III with the KRYPTOS tableau must exactly reproduce K1/K2."""

    def test_k1_decrypt(self):
        assert quagmire3_decrypt(K1_CIPHERTEXT, K1_KEY, "KRYPTOS") == K1_PLAINTEXT

    def test_k1_encrypt(self):
        assert quagmire3_encrypt(K1_PLAINTEXT, K1_KEY, "KRYPTOS") == K1_CIPHERTEXT

    def test_k2_matches_canonical_vigenere(self):
        expected = vigenere_decrypt(K2_CIPHERTEXT, K2_KEY)
        assert quagmire3_decrypt(K2_CIPHERTEXT, K2_KEY, "KRYPTOS") == expected

    def test_k2_round_trip(self):
        plaintext = quagmire3_decrypt(K2_CIPHERTEXT, K2_KEY, "KRYPTOS")
        assert quagmire3_encrypt(plaintext, K2_KEY, "KRYPTOS") == K2_CIPHERTEXT


class TestVigenereReduction:
    def test_straight_alphabets_reduce_to_classic_vigenere(self):
        # Quagmire with straight alphabets and ACA base 'A' is plain Vigenere
        assert quagmire3_encrypt("ATTACKATDAWN", "LEMON", "", "A") == "LXFOPVEFRNHR"
        assert quagmire3_decrypt("LXFOPVEFRNHR", "LEMON", "", "A") == "ATTACKATDAWN"


class TestRoundTrips:
    @pytest.mark.parametrize("variant", ["q1", "q2", "q3"])
    def test_round_trip(self, variant):
        encrypt, decrypt = {
            "q1": (quagmire1_encrypt, quagmire1_decrypt),
            "q2": (quagmire2_encrypt, quagmire2_decrypt),
            "q3": (quagmire3_encrypt, quagmire3_decrypt),
        }[variant]
        rng = random.Random(99)
        for _ in range(5):
            plaintext = "".join(rng.choices(string.ascii_uppercase, k=60))
            for base in (None, "A"):
                ct = encrypt(plaintext, "SPRINGFIELD", "FLOWER", base)
                assert decrypt(ct, "SPRINGFIELD", "FLOWER", base) == plaintext

    def test_q4_round_trip(self):
        rng = random.Random(7)
        plaintext = "".join(rng.choices(string.ascii_uppercase, k=60))
        for base in (None, "A"):
            ct = quagmire4_encrypt(plaintext, "GRONSFELD", "PAINT", "BRUSH", base)
            assert quagmire4_decrypt(ct, "GRONSFELD", "PAINT", "BRUSH", base) == plaintext

    def test_variants_disagree(self):
        """Sanity: keyed alphabets actually change the output per variant."""
        plaintext = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG"
        outputs = {
            quagmire1_encrypt(plaintext, "KEY", "KRYPTOS"),
            quagmire2_encrypt(plaintext, "KEY", "KRYPTOS"),
            quagmire3_encrypt(plaintext, "KEY", "KRYPTOS"),
            quagmire4_encrypt(plaintext, "KEY", "KRYPTOS", "BERLIN"),
        }
        assert len(outputs) == 4

    def test_invalid_key_raises(self):
        with pytest.raises(ValueError, match="Indicator key"):
            quagmire3_encrypt("ABC", "123", "KRYPTOS")


class TestPositionalCribHits:
    def test_full_match(self):
        plaintext = list("X" * 97)
        plaintext[21:25] = "EAST"
        plaintext[25:34] = "NORTHEAST"
        plaintext[63:69] = "BERLIN"
        plaintext[69:74] = "CLOCK"
        assert positional_crib_hits("".join(plaintext)) == 4

    def test_no_match(self):
        assert positional_crib_hits("X" * 97) == 0


class TestClockIndicatorKeys:
    def test_minute_states(self):
        keys = clock_indicator_keys(keyword_alphabet("KRYPTOS"))
        assert len(keys) == 1440
        # 17:00 -> rows [3, 2, 0, 0] -> KRYPTOS-alphabet letters P, Y, K, K
        assert keys["17:00"] == "PYKK"
        assert all(len(k) == 4 for k in keys.values())

    def test_with_seconds(self):
        keys = clock_indicator_keys(keyword_alphabet("KRYPTOS"), include_seconds=True)
        assert all(len(k) == 5 for k in keys.values())


class TestQuagmireSweep:
    def test_null_result_artifact(self, tmp_path):
        artifact = tmp_path / "null.json"
        summary = run_quagmire_sweep(
            word_keys=["KRYPTOS", "BERLIN"],
            alphabet_keywords=["KRYPTOS"],
            null_artifact_path=artifact,
            eureka_snapshot_path=tmp_path / "snap.md",
        )
        assert summary["status"] == "null_result"
        assert summary["run_params"]["total_tested"] > 0
        data = json.loads(artifact.read_text(encoding="utf-8"))
        assert data["attack"] == "quagmire_sweep"

    def test_eureka_on_planted_solution(self, tmp_path):
        plaintext = list("A" * 97)
        plaintext[21:25] = "EAST"
        plaintext[25:34] = "NORTHEAST"
        plaintext[63:69] = "BERLIN"
        plaintext[69:74] = "CLOCK"
        planted_ct = quagmire3_encrypt("".join(plaintext), "BERLIN", "KRYPTOS")

        with pytest.raises(EurekaSignal) as excinfo:
            run_quagmire_sweep(
                ciphertext=planted_ct,
                word_keys=["BERLIN"],
                alphabet_keywords=["KRYPTOS"],
                null_artifact_path=tmp_path / "null.json",
                eureka_snapshot_path=tmp_path / "snap.md",
            )
        assert excinfo.value.result["positional_crib_hits"] == 4

    def test_k4_default_ciphertext_is_canonical(self):
        assert len(K4) == 97
        assert K4.startswith("OBKR")
