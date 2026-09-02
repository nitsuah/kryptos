"""Tests for kryptos.k4.cross_vector_consensus -- Phase 7 cross-vector scoring."""

from __future__ import annotations

import json

from kryptos.k4 import cross_vector_consensus as cvc


def _write_artifact(path, candidate_texts):
    path.write_text(
        json.dumps({"best_candidates": [{"candidate_text": t} for t in candidate_texts]}),
        encoding="utf-8",
    )


class TestScoreCrossVectorConsensus:
    def test_no_artifacts_found(self, tmp_path):
        result = cvc.score_cross_vector_consensus(search_dir=str(tmp_path))
        assert result["status"] == "no_candidates"

    def test_fragment_repeated_within_one_vector_is_not_consensus(self, tmp_path):
        # Same 4-char fragment repeated 50x within a SINGLE artifact must
        # not count as cross-vector consensus -- it's one vector's worth
        # of evidence no matter how many candidates it appears in there.
        texts = ["WXYZ" + "A" * 93 for _ in range(50)]
        _write_artifact(tmp_path / "K4_VECTOR_A_NULL.json", texts)

        result = cvc.score_cross_vector_consensus(search_dir=str(tmp_path), min_distinct_vectors=2)
        assert result["status"] == "complete"
        assert result["consensus_anchors_found"] == 0

    def test_fragment_across_distinct_vectors_is_flagged(self, tmp_path):
        # Same fragment appearing in 3 SEPARATE artifacts (vectors) must be
        # flagged once min_distinct_vectors is reached.
        for i in range(3):
            texts = [("WXYZ" + "A" * 93)]
            _write_artifact(tmp_path / f"K4_VECTOR_{i}_NULL.json", texts)

        result = cvc.score_cross_vector_consensus(search_dir=str(tmp_path), min_distinct_vectors=3)
        assert result["status"] == "complete"
        assert result["consensus_anchors_found"] >= 1
        anchor = next(a for a in result["consensus_anchors"] if a["ngram"] == "WXYZ" and a["position"] == 0)
        assert anchor["distinct_vector_count"] == 3
        assert len(anchor["vectors"]) == 3

    def test_below_threshold_not_flagged(self, tmp_path):
        for i in range(2):  # only 2 vectors, threshold is 3
            texts = [("WXYZ" + "A" * 93)]
            _write_artifact(tmp_path / f"K4_VECTOR_{i}_NULL.json", texts)

        result = cvc.score_cross_vector_consensus(search_dir=str(tmp_path), min_distinct_vectors=3)
        assert result["consensus_anchors_found"] == 0

    def test_vector_candidate_counts_reported(self, tmp_path):
        _write_artifact(tmp_path / "K4_VECTOR_A_NULL.json", ["A" * 97, "B" * 97])
        result = cvc.score_cross_vector_consensus(search_dir=str(tmp_path))
        assert result["vector_candidate_counts"]["K4_VECTOR_A_NULL.json"] == 2


class TestRunCrossVectorConsensusAttack:
    def test_writes_null_artifact(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        _write_artifact(tmp_path / "K4_VECTOR_A_NULL.json", ["A" * 97])
        artifact_path = tmp_path / "K4_CROSS_VECTOR_CONSENSUS_NULL.json"
        result = cvc.run_cross_vector_consensus_attack(null_artifact_path=str(artifact_path))
        assert result["status"] == "complete"
        data = json.loads(artifact_path.read_text(encoding="utf-8"))
        assert data["attack"] == "cross_vector_consensus"
