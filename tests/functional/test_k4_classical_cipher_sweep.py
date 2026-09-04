"""Tests for kryptos.k4.classical_cipher_sweep -- the real, crib-gated sweeps

for hypotheses.py's previously-orphaned Playfair/Four-Square/Bifid/Autokey
classes.
"""

from __future__ import annotations

import json

from kryptos.k4 import classical_cipher_sweep as ccs
from kryptos.k4.physical_grid import K4


class TestAllTestedKeywords:
    def test_excludes_the_standard_alphabet_label(self):
        # KNOWN_KEYED_ALPHABETS has a "STANDARD" entry for the identity
        # alphabet -- a label, not an actual candidate word.
        assert "STANDARD" not in ccs.ALL_TESTED_KEYWORDS

    def test_includes_words_from_every_known_source(self):
        # Spot-check one word from each existing keyword module this list
        # unions together.
        for expected in ("SANBORN", "WEBSTER", "ROSE", "VIRTUALLY", "KRYPTOS"):
            assert expected in ccs.ALL_TESTED_KEYWORDS

    def test_no_duplicates(self):
        assert len(ccs.ALL_TESTED_KEYWORDS) == len(set(ccs.ALL_TESTED_KEYWORDS))


class TestRunClassicalCipherSweep:
    def test_small_scope_runs_and_reports_a_verdict(self):
        r = ccs.run_classical_cipher_sweep(keywords=["KRYPTOS", "BERLIN"], bifid_periods=[5, 7])
        assert r["status"] in ("null_result", "hypothesis_found")
        assert r["run_params"]["total_tested"] > 0

    def test_writes_null_artifact(self, tmp_path):
        artifact = tmp_path / "null.json"
        r = ccs.run_classical_cipher_sweep(keywords=["KRYPTOS"], bifid_periods=[5], null_artifact_path=str(artifact))
        assert r["status"] == "null_result"
        data = json.loads(artifact.read_text(encoding="utf-8"))
        assert data["attack"] == "P21_classical_cipher_sweep"

    def test_total_tested_matches_playfair_foursquare_autokey_bifid_counts(self):
        # 2 keywords: Playfair=2, Four-Square pairs=2*3/2=3, Autokey=2,
        # Bifid=2 keywords * 2 periods = 4. Total = 11.
        r = ccs.run_classical_cipher_sweep(keywords=["KRYPTOS", "BERLIN"], bifid_periods=[5, 7])
        assert r["run_params"]["total_tested"] == 2 + 3 + 2 + 4

    def test_never_gates_on_the_hypothesis_classes_internal_score(self):
        # This module must score by positional_crib_hits/_keyword_hits
        # (this project's canonical crib gating), not by each hypothesis
        # class's own combined_plaintext_score -- best_candidates entries
        # must carry the canonical fields.
        r = ccs.run_classical_cipher_sweep(keywords=["KRYPTOS", "BERLIN", "CLOCK"], bifid_periods=[5])
        for hit in r["best_candidates"]:
            assert "positional_crib_hits" in hit
            assert "keyword_hits" in hit

    def test_real_k4_full_default_scope_completes_without_exception(self):
        # The actual, real run this project's docs cite: default keyword
        # list, default Bifid periods, real K4 ciphertext.
        r = ccs.run_classical_cipher_sweep(ciphertext=K4)
        assert r["status"] in ("null_result", "hypothesis_found")
        assert r["run_params"]["total_tested"] > 1000
