"""Tests for kryptos.k4.plaintext_evidence -- confidence-tiered plaintext data."""

from __future__ import annotations

from kryptos.k4 import plaintext_evidence as pe
from kryptos.k4.keystream_validator import K4_CRIBS, K4_EXPECTED_KEYSTREAMS
from kryptos.k4.physical_grid import K4


class TestConfirmedPlaintext:
    def test_24_positions(self):
        confirmed = pe.confirmed_plaintext()
        assert len(confirmed) == 24

    def test_matches_k4_cribs_exactly(self):
        confirmed = pe.confirmed_plaintext()
        for word, start in K4_CRIBS.values():
            for i, ch in enumerate(word):
                assert confirmed[start + i] == ch


class TestReconstructedPlaintext:
    def test_full_length(self):
        recon = pe.reconstructed_plaintext()
        assert recon is not None
        assert len(recon) == len(K4)

    def test_unregistered_candidate_returns_none(self):
        assert pe.reconstructed_plaintext("not_a_real_candidate") is None


class TestEvidenceMap:
    def test_covers_all_positions(self):
        evidence = pe.evidence_map()
        assert set(evidence.keys()) == set(range(len(K4)))

    def test_confirmed_positions_tagged_correctly(self):
        evidence = pe.evidence_map()
        for pos in pe.confirmed_plaintext():
            assert evidence[pos]["confidence"] == pe.CONFIRMED

    def test_non_confirmed_positions_are_reconstructed_not_unknown(self):
        # solvekryptos_field_guide covers the full 97 chars, so every
        # non-confirmed position should be RECONSTRUCTED, not UNKNOWN.
        evidence = pe.evidence_map()
        confirmed_positions = set(pe.confirmed_plaintext())
        for pos, entry in evidence.items():
            if pos not in confirmed_positions:
                assert entry["confidence"] == pe.RECONSTRUCTED

    def test_unknown_when_no_candidate_registered(self):
        evidence = pe.evidence_map("not_a_real_candidate")
        confirmed_positions = set(pe.confirmed_plaintext())
        for pos, entry in evidence.items():
            if pos not in confirmed_positions:
                assert entry["confidence"] == pe.UNKNOWN
                assert entry["char"] is None


class TestConfidenceCounts:
    def test_sums_to_97(self):
        counts = pe.confidence_counts()
        assert sum(counts.values()) == len(K4)

    def test_24_confirmed(self):
        assert pe.confidence_counts()[pe.CONFIRMED] == 24


class TestDerivedShifts:
    def test_confirmed_shifts_match_keystream_validator(self):
        # The confirmed-position shifts here must exactly reproduce
        # K4_EXPECTED_KEYSTREAMS -- same data, different shape. If these
        # ever disagree, one of the two independent derivations has a bug.
        result = pe.derived_shifts()
        confirmed_shifts = result["confirmed_shifts"]
        for label, (word, start) in K4_CRIBS.items():
            expected = K4_EXPECTED_KEYSTREAMS[label]
            observed = [confirmed_shifts[start + i] for i in range(len(word))]
            assert observed == expected

    def test_reconstructed_shifts_present(self):
        result = pe.derived_shifts()
        assert len(result["reconstructed_shifts"]) == 73


class TestCandidateRepeatingPeriods:
    def test_returns_a_verdict_for_every_period_in_range(self):
        periods = pe.candidate_repeating_periods(period_range=range(2, 6))
        assert set(periods.keys()) == {2, 3, 4, 5}

    def test_empty_when_no_reconstructed_shifts(self):
        assert pe.candidate_repeating_periods("not_a_real_candidate") == {}
