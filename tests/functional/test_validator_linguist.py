"""Tests for the optional LINGUIST integration in pipeline/validator.py stage 3."""

from __future__ import annotations

import sys

import pytest

from kryptos.pipeline.validator import PlaintextValidator


@pytest.fixture
def patched_data_root(tmp_path, monkeypatch):
    """Keep LINGUIST's on-disk cache under tmp_path instead of the repo's data/ dir."""
    monkeypatch.setattr("kryptos.paths.get_data_root", lambda: tmp_path)
    return tmp_path


class TestLinguistDisabledByDefault:
    def test_disabled_by_default(self):
        validator = PlaintextValidator()
        assert validator.linguist is None
        assert validator.linguist_available is False

    def test_stage3_has_no_linguist_key_by_default(self):
        validator = PlaintextValidator()
        result = validator.stage3_linguistic_validation("THECLOCKISINBERLIN")
        assert "linguist" not in result

    def test_batch_validate_linguist_returns_none_by_default(self):
        validator = PlaintextValidator()
        assert validator.batch_validate_linguist(["THECLOCKISINBERLIN"]) is None


class TestLinguistMissingDependencies:
    def test_init_linguist_returns_none_without_torch(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "torch", None)
        validator = PlaintextValidator(enable_linguist=True)
        assert validator.linguist is None
        assert validator.linguist_available is False


@pytest.fixture
def linguist_validator(patched_data_root, monkeypatch):
    """A validator with LINGUIST enabled and perplexity forced to the heuristic path."""
    validator = PlaintextValidator(enable_linguist=True)
    if validator.linguist is not None:
        monkeypatch.setattr(validator.linguist, "_init_perplexity_model", lambda: None)
    return validator


class TestLinguistEnabled:
    def test_linguist_agent_constructed(self, linguist_validator):
        if not linguist_validator.linguist_available:
            pytest.skip("torch/transformers not available")
        assert linguist_validator.linguist is not None

    def test_stage3_includes_linguist_score(self, linguist_validator):
        if not linguist_validator.linguist_available:
            pytest.skip("torch/transformers not available")

        result = linguist_validator.stage3_linguistic_validation("THECLOCKISINBERLIN")

        # Existing heuristic fields are unchanged.
        assert "passed" in result
        assert "metrics" in result
        assert "reason" in result

        ling = result["linguist"]
        assert ling is not None
        assert 0.0 <= ling["confidence"] <= 1.0
        assert ling["perplexity"] > 0
        assert 0.0 <= ling["coherence"] <= 1.0
        assert 0.0 <= ling["grammar_score"] <= 1.0
        assert "model_used" in ling
        assert isinstance(ling["passed"], bool)

    def test_stage3_empty_text_includes_linguist_score(self, linguist_validator):
        if not linguist_validator.linguist_available:
            pytest.skip("torch/transformers not available")

        result = linguist_validator.stage3_linguistic_validation("")
        assert result["passed"] is False
        assert result["linguist"] is not None

    def test_batch_validate_linguist(self, linguist_validator):
        if not linguist_validator.linguist_available:
            pytest.skip("torch/transformers not available")

        candidates = [
            "THE CLOCK IS HIDDEN IN BERLIN NEAR THE WALL",
            "XQZMWPVUTRSLKJIHGFEDCBA",
        ]
        ranked = linguist_validator.batch_validate_linguist(candidates, threshold=0.0, top_k=5)

        assert ranked is not None
        assert len(ranked) >= 1
        for text, score in ranked:
            assert text in candidates
            assert 0.0 <= score["confidence"] <= 1.0


class TestLinguistScoringFailure:
    def test_linguist_score_handles_exception(self, linguist_validator, monkeypatch):
        if not linguist_validator.linguist_available:
            pytest.skip("torch/transformers not available")

        def _raise(_text: str):
            raise RuntimeError("boom")

        monkeypatch.setattr(linguist_validator.linguist, "validate_candidate", _raise)

        result = linguist_validator.stage3_linguistic_validation("THECLOCKISINBERLIN")
        assert result["linguist"] is None

    def test_batch_validate_linguist_handles_exception(self, linguist_validator, monkeypatch):
        if not linguist_validator.linguist_available:
            pytest.skip("torch/transformers not available")

        def _raise(*args, **kwargs):
            raise RuntimeError("boom")

        monkeypatch.setattr(linguist_validator.linguist, "batch_validate", _raise)

        assert linguist_validator.batch_validate_linguist(["THECLOCKISINBERLIN"]) is None
