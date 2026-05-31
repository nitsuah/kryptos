"""Deterministic reliability gates for K1, K2, and K3 decryption.

These tests verify that the canonical decrypt functions produce the
expected plaintext (including Sanborn's deliberate misspellings) and
that the SECTIONS registry wires up correctly.  Any regression in
cipher logic will be caught here before it affects K4 analysis.
"""

from __future__ import annotations

import pytest
from kryptos import k1, k2, k3
from kryptos.sections import SECTIONS

# ---------------------------------------------------------------------------
# Canonical ciphertexts (alpha-only, Kryptos sculpture reference)
# ---------------------------------------------------------------------------
K1_CIPHERTEXT = "EMUFPHZLRFAXYUSDJKZLDKRNSHGNFIVJYQTQUXQBQVYUVLLTREVJYQTMKYRDMFD"
K1_KEY        = "PALIMPSEST"
K1_PLAINTEXT  = "BETWEENSUBTLESHADINGANDTHEABSENCEOFLIGHTLIESTHENUANCEOFIQLUSION"

# K2 ciphertext — 336 alpha chars (matches the plaintext through "THIRTYEIGHTDEGREES…")
K2_CIPHERTEXT = (
    "VFPJUDEEHZWETZYVGWHKKQETGFQJNCEGGWHKKDQMCPFQZDQMMIAGPFXHQRLGTIM"
    "VMZJANQLVKQEDAGDVFRPJUNGEUNAQZGZLECGYUXUEENJTBJLBQCRTBJDFHRRYIZE"
    "TKZEMVDUFKSJHKFWHKUWQLSZFTIHHDDDUVHDWKBFUFPWNTDFIYCUQZEREEVLDKFE"
    "ZMOQQJLTTUGSYQPFEUNLAVIDXFLGGTEZFKZBSFDQVGOGIPUFXHHDRKFFHQNTGPUA"
    "ECNUVPDJMQCLQUMUNEDFQELZZVRRGKFFVOEEXBDMVPNFQXEZLGREDNQFCHOBSSPH"
    "FLLOXQRZXGZQAAVTTEXOLIQQTIVWHHMQAUQZMASMRVLQJNWB"
)
K2_KEY = "ABSCISSA"
# Verified markers from the known K2 plaintext
K2_KNOWN_START   = "ITWASTOTALLYINVISIBLEHOWSTHATPOSSIBLE"
K2_KNOWN_MARKERS = [
    "UNDERGRUUND",        # Sanborn misspelling of UNDERGROUND
    "DOESLANGLEYKNOW",
    "THIRTYEIGHTDEGREES",
    "ITSBURIEDOUTTHERESOMEWHERE",
]

K3_CIPHERTEXT = (
    "?ENDYAHROHNLSRHEOCPTEOIBIDYSHNAIACHTNREYULDSLLSLLNOHSNOSMRWXMNET"
    "PRNGATIHNRARPESLNNELEBLPIIACAEWMTWNDITEENRAHCTENEUDRETNHAEOETFOLS"
    "EDTIWENHAEIOYTEYQHEENCTAYCREIFTBRSPAMHHEWENATAMATEGYEERLBTEEFOASF"
    "IOTUETUAEOTOARMAEERTNRTIBSEDDNIAAHTTMSTEWPIEROAGRIEWFEBAECTDDHILC"
    "EIHSITEGOEAOSDDRYDLORITRKLMLEHAGTDHARDPNEOHMGFMFEUHEECDMRIPFEIMEH"
    "NLSSTTRTVDOHW"
)
# Full K3 plaintext (including DESPARATLY misspelling and trailing Q)
K3_PLAINTEXT = (
    "SLOWLYDESPARATLYSLOWLYTHEREMAINSOFPASSAGEDEBRISTHATENCUMBEREDTHEL"
    "OWERPARTOFTHEDOORWAYWASREMOVEDWITHTREMBLINGHANDSIMADEATINYBREACHI"
    "NTHEUPPERLEFTHANDCORNERANDTHENWIDENINGTHEHOLEALITTLEIINSERTEDTHEC"
    "ANDLEANDPEEREDINTHEHOTAIRESCAPINGFROMTHECHAMBERCAUSEDTHEFLAMETOF"
    "LICKERBUTPRESENTLYDETAILSOFTHEROOMWITHINEMERGEDFROMTHEMISTXCANYO"
    "USEEANYTHINGQ"
)


# ---------------------------------------------------------------------------
# K1 gates
# ---------------------------------------------------------------------------

class TestK1Reliability:
    def test_exact_plaintext(self):
        assert k1.decrypt(K1_CIPHERTEXT, K1_KEY) == K1_PLAINTEXT

    def test_starts_with_between(self):
        pt = k1.decrypt(K1_CIPHERTEXT, K1_KEY)
        assert pt.startswith("BETWEENSUBTLESHADING")

    def test_iqlusion_misspelling_preserved(self):
        """Sanborn deliberately misspelled ILLUSION as IQLUSION — must not be corrected."""
        pt = k1.decrypt(K1_CIPHERTEXT, K1_KEY)
        assert "IQLUSION" in pt
        assert "ILLUSION" not in pt

    def test_wrong_key_differs(self):
        wrong = k1.decrypt(K1_CIPHERTEXT, "KRYPTOS")
        assert wrong != K1_PLAINTEXT

    def test_case_insensitive_key(self):
        lower = k1.decrypt(K1_CIPHERTEXT, "palimpsest")
        assert lower == K1_PLAINTEXT


# ---------------------------------------------------------------------------
# K2 gates
# ---------------------------------------------------------------------------

class TestK2Reliability:
    def _pt(self) -> str:
        return k2.decrypt(K2_CIPHERTEXT, K2_KEY)

    def test_starts_correctly(self):
        assert self._pt().startswith(K2_KNOWN_START)

    def test_undergruund_misspelling(self):
        """Sanborn misspelled UNDERGROUND as UNDERGRUUND — canonical marker."""
        assert "UNDERGRUUND" in self._pt()
        assert "UNDERGROUND" not in self._pt()

    def test_all_known_markers_present(self):
        pt = self._pt()
        for marker in K2_KNOWN_MARKERS:
            assert marker in pt, f"Marker not found: {marker}"

    def test_coordinates_present(self):
        pt = self._pt()
        assert "THIRTYEIGHT" in pt
        assert "DEGREES" in pt
        assert "FIFTYSEVENMINUTES" in pt

    def test_wrong_key_misses_markers(self):
        wrong_pt = k2.decrypt(K2_CIPHERTEXT, "PALIMPSEST")
        assert "UNDERGRUUND" not in wrong_pt


# ---------------------------------------------------------------------------
# K3 gates
# ---------------------------------------------------------------------------

class TestK3Reliability:
    def test_exact_plaintext(self):
        assert k3.decrypt(K3_CIPHERTEXT) == K3_PLAINTEXT

    def test_desparatly_misspelling(self):
        """Sanborn misspelled DESPERATELY as DESPARATLY — must be preserved."""
        pt = k3.decrypt(K3_CIPHERTEXT)
        assert "DESPARATLY" in pt
        assert "DESPERATELY" not in pt

    def test_starts_with_slowly(self):
        assert k3.decrypt(K3_CIPHERTEXT).startswith("SLOWLY")

    def test_ends_with_q(self):
        """Trailing Q = Carnarvon's unrecorded reply in the Howard Carter excerpt."""
        pt = k3.decrypt(K3_CIPHERTEXT)
        assert pt.endswith("Q")

    def test_candle_passage_present(self):
        pt = k3.decrypt(K3_CIPHERTEXT)
        assert "INSERTEDTHECANDLEANDPEERED" in pt

    def test_canyouseeanything_present(self):
        pt = k3.decrypt(K3_CIPHERTEXT)
        assert "CANYOUSEEANYTHING" in pt


# ---------------------------------------------------------------------------
# SECTIONS registry gates
# ---------------------------------------------------------------------------

class TestSectionsRegistry:
    def test_k1_callable(self):
        assert callable(SECTIONS["K1"])

    def test_k2_callable(self):
        assert callable(SECTIONS["K2"])

    def test_k3_callable(self):
        assert callable(SECTIONS["K3"])

    def test_k4_key_present(self):
        assert "K4" in SECTIONS

    def test_k1_via_registry(self):
        pt = SECTIONS["K1"](K1_CIPHERTEXT, K1_KEY)
        assert "IQLUSION" in pt

    def test_k2_via_registry(self):
        pt = SECTIONS["K2"](K2_CIPHERTEXT, K2_KEY)
        assert "UNDERGRUUND" in pt

    def test_k3_via_registry(self):
        pt = SECTIONS["K3"](K3_CIPHERTEXT)
        assert "DESPARATLY" in pt
