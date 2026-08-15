"""Tests for K4 Phase 2 frontier attacks: P15 (checkerboard), P16 (corpus), P19 (advisory), P20 (Cyrillic)."""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# P15 — Straddling checkerboard
# ---------------------------------------------------------------------------
class TestStraddlingCheckerboard:
    def test_k2_n_digits(self):
        from kryptos.k4.straddling_checkerboard import K2_N_DIGITS
        assert K2_N_DIGITS == [3, 8, 5, 7, 6, 5]

    def test_k2_w_digits(self):
        from kryptos.k4.straddling_checkerboard import K2_W_DIGITS
        assert K2_W_DIGITS == [7, 7, 8, 4, 4]

    def test_unique_digits_order(self):
        from kryptos.k4.straddling_checkerboard import K2_UNIQUE_DIGITS
        assert K2_UNIQUE_DIGITS == [3, 8, 5, 7, 6, 4]

    def test_candidate_row_headers_includes_primary(self):
        from kryptos.k4.straddling_checkerboard import CANDIDATE_ROW_HEADERS
        assert (3, 8) in CANDIDATE_ROW_HEADERS
        assert len(CANDIDATE_ROW_HEADERS) >= 4

    def test_build_checkerboard_alphabet_coverage(self):
        from kryptos.k4.straddling_checkerboard import build_checkerboard
        board = build_checkerboard("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 3, 8)
        # Every letter should be encodable
        encoded = {c: board.encode_letter(c) for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
        assert all(len(v) in (1, 2) for v in encoded.values()), "Some letters have empty encoding"

    def test_build_checkerboard_decode_round_trip(self):
        from kryptos.k4.straddling_checkerboard import build_checkerboard
        board = build_checkerboard("ETAOINSHRDLUCMFWYPVBGKJQXZ", 3, 8)
        test_text = "HELLO"
        digits = board.encode_text(test_text)
        decoded = board.decode_digits(digits)
        assert decoded == test_text

    def test_checkerboard_distinct_row_headers_required(self):
        from kryptos.k4.straddling_checkerboard import StruddlingCheckerboard
        with pytest.raises(AssertionError):
            StruddlingCheckerboard("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 3, 3)

    def test_encode_text_produces_digits(self):
        from kryptos.k4.straddling_checkerboard import build_checkerboard
        board = build_checkerboard("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 7, 4)
        digits = board.encode_text("KRYPTOS")
        assert all(0 <= d <= 9 for d in digits)
        assert len(digits) >= 7  # at least 7 digits for 7 letters

    def test_run_attack_returns_dict(self):
        from kryptos.k4.straddling_checkerboard import run_straddling_checkerboard_attack
        result = run_straddling_checkerboard_attack(null_artifact_path="K4_P15_TEST_NULL.json")
        assert isinstance(result, dict)
        assert "attack" in result
        assert result["attack"] == "P15_straddling_checkerboard"

    def test_run_attack_combos_tested(self):
        from kryptos.k4.straddling_checkerboard import run_straddling_checkerboard_attack, CANDIDATE_ROW_HEADERS
        result = run_straddling_checkerboard_attack(null_artifact_path="K4_P15_TEST2_NULL.json")
        # 6 row-headers × 3 orderings × 2 converters = 36
        expected = len(CANDIDATE_ROW_HEADERS) * 3 * 2
        assert result["combos_tested"] == expected

    def test_encoding_analysis_present(self):
        from kryptos.k4.straddling_checkerboard import run_straddling_checkerboard_attack
        result = run_straddling_checkerboard_attack(null_artifact_path="K4_P15_TEST3_NULL.json")
        assert "encoding_analysis" in result
        assert len(result["encoding_analysis"]) > 0


# ---------------------------------------------------------------------------
# P16 — Corpus fragment mining
# ---------------------------------------------------------------------------
class TestCorpusMiner:
    def test_module_importable(self):
        from kryptos.k4.corpus_miner import mine_candidate_corpus  # noqa: F401
        assert callable(mine_candidate_corpus)

    def test_constants_reasonable(self):
        from kryptos.k4.corpus_miner import NGRAM_RANGE, ANCHOR_WINDOW, MIN_FREQUENCY_PCT
        assert NGRAM_RANGE[0] >= 4
        assert NGRAM_RANGE[1] <= 8
        assert ANCHOR_WINDOW[0] == 0
        assert ANCHOR_WINDOW[1] <= 25
        assert 1.0 <= MIN_FREQUENCY_PCT <= 10.0

    def test_mine_no_artifacts_returns_status(self):
        from kryptos.k4.corpus_miner import mine_candidate_corpus
        result = mine_candidate_corpus(
            artifact_glob="K4_NONEXISTENT_*.json",
            search_dir=".",
        )
        assert isinstance(result, dict)
        assert result["status"] in ("no_candidates", "complete")

    def test_mine_with_synthetic_candidates(self, tmp_path):
        import json
        from kryptos.k4.corpus_miner import mine_candidate_corpus

        # Create a synthetic null artifact
        artifact = {
            "best_candidates": [
                {"candidate_text": "EASTBERLINCLOCKBETWEENOBKRUOXOGHULBSOLIFBB"},
                {"candidate_text": "EASTBERLINCLOCKBETWEENQPRNGKSSOTWTQSJQSSEK"},
                {"candidate_text": "EASTBERLINCLOCKBETWEENZXCVBNMLKJHGFDSAPOIU"},
                {"candidate_text": "NORTHEASTCLOCKBETWEENOBKRUOXOGHULBSOLIFBBW"},
            ]
        }
        fpath = tmp_path / "K4_SYNTHETIC_NULL.json"
        fpath.write_text(json.dumps(artifact))

        result = mine_candidate_corpus(
            artifact_glob="K4_SYNTHETIC_NULL.json",
            search_dir=str(tmp_path),
        )
        assert result["total_candidates"] == 4
        assert result["status"] == "complete"

    def test_mine_detects_east_ngram(self, tmp_path):
        import json
        from kryptos.k4.corpus_miner import mine_candidate_corpus

        # All candidates share EAST at position 0
        candidates = [
            {"candidate_text": f"EAST{i:02d}BERLINCLOCKZXCVBNMLKJHGFDSAPOIUQWERTY"}
            for i in range(10)
        ]
        artifact = {"best_candidates": candidates}
        fpath = tmp_path / "K4_EAST_NULL.json"
        fpath.write_text(json.dumps(artifact))

        result = mine_candidate_corpus(
            artifact_glob="K4_EAST_NULL.json",
            search_dir=str(tmp_path),
        )
        # EAST at position 0 should appear in english_anchors
        anchors = result.get("english_anchors", [])
        east_hits = [a for a in anchors if a["ngram"] == "EAST" and a["position"] == 0]
        assert len(east_hits) > 0, f"EAST at pos 0 not found in anchors: {anchors}"

    def test_run_attack_returns_dict(self):
        from kryptos.k4.corpus_miner import run_corpus_miner_attack
        result = run_corpus_miner_attack(
            artifact_glob="K4_NONEXISTENT_XXXXX_*.json",
            null_artifact_path="K4_P16_TEST_NULL.json",
        )
        assert isinstance(result, dict)
        assert "attack" in result


# ---------------------------------------------------------------------------
# P19 — Advisory keyword sweep
# ---------------------------------------------------------------------------
class TestAdvisoryKeywords:
    def test_advisory_keywords_list(self):
        from kryptos.k4.advisory_keywords import ADVISORY_KEYWORDS
        assert "SCHEIDT" in ADVISORY_KEYWORDS
        assert "WEBSTER" in ADVISORY_KEYWORDS
        assert "STUDEMAN" in ADVISORY_KEYWORDS
        assert len(ADVISORY_KEYWORDS) >= 5

    def test_all_alphabets_valid(self):
        from kryptos.k4.advisory_keywords import ADVISORY_KEYED_ALPHABETS
        for name, alpha in ADVISORY_KEYED_ALPHABETS.items():
            assert len(alpha) == 26, f"{name}: wrong length"
            assert len(set(alpha)) == 26, f"{name}: has duplicates"
            assert set(alpha) == set("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), f"{name}: missing letters"

    def test_scheidt_alpha_starts_correct(self):
        from kryptos.k4.advisory_keywords import ADVISORY_KEYED_ALPHABETS
        alpha = ADVISORY_KEYED_ALPHABETS["SCHEIDT"]
        # S,C,H,E,I,D,T come first (deduplicated)
        assert alpha.startswith("SCHEIDT"), f"SCHEIDT alpha starts: {alpha[:7]}"

    def test_webster_alpha_starts_correct(self):
        from kryptos.k4.advisory_keywords import ADVISORY_KEYED_ALPHABETS
        alpha = ADVISORY_KEYED_ALPHABETS["WEBSTER"]
        assert alpha.startswith("WEBSTR"), f"WEBSTER alpha starts: {alpha[:6]}"

    def test_build_keyed_alphabet_no_duplicates(self):
        from kryptos.k4.advisory_keywords import build_keyed_alphabet
        for kw in ["SCHEIDT", "ELONKA", "KRYPTOS", "STUDEMAN"]:
            alpha = build_keyed_alphabet(kw)
            assert len(alpha) == 26
            assert len(set(alpha)) == 26

    def test_run_sweep_callable(self):
        from kryptos.k4.advisory_keywords import run_advisory_keyword_sweep
        assert callable(run_advisory_keyword_sweep)


# ---------------------------------------------------------------------------
# P20 — Cyrillic Projector keywords
# ---------------------------------------------------------------------------
class TestCyrillicProjector:
    def test_cyrillic_keywords_list(self):
        from kryptos.k4.cyrillic_projector import CYRILLIC_PROJECTOR_KEYWORDS
        assert "AGENT" in CYRILLIC_PROJECTOR_KEYWORDS
        assert "REZIDENT" in CYRILLIC_PROJECTOR_KEYWORDS
        assert "RAZVEDKA" in CYRILLIC_PROJECTOR_KEYWORDS
        assert len(CYRILLIC_PROJECTOR_KEYWORDS) >= 10

    def test_all_alphabets_valid(self):
        from kryptos.k4.cyrillic_projector import CYRILLIC_KEYED_ALPHABETS
        for name, alpha in CYRILLIC_KEYED_ALPHABETS.items():
            assert len(alpha) == 26, f"{name}: wrong length"
            assert len(set(alpha)) == 26, f"{name}: has duplicates"

    def test_agent_alpha_starts_with_a(self):
        from kryptos.k4.cyrillic_projector import CYRILLIC_KEYED_ALPHABETS
        alpha = CYRILLIC_KEYED_ALPHABETS["AGENT"]
        assert alpha.startswith("AGENT"), f"AGENT alpha starts: {alpha[:5]}"

    def test_rezident_alpha_starts_correct(self):
        from kryptos.k4.cyrillic_projector import CYRILLIC_KEYED_ALPHABETS
        alpha = CYRILLIC_KEYED_ALPHABETS["REZIDENT"]
        assert alpha.startswith("REZIDN"), f"REZIDENT alpha starts: {alpha[:6]}"

    def test_all_keywords_produce_different_alphabets(self):
        from kryptos.k4.cyrillic_projector import CYRILLIC_KEYED_ALPHABETS
        alphas = list(CYRILLIC_KEYED_ALPHABETS.values())
        # AGENT and RAZVEDKA should produce different alphabets
        assert len(set(alphas)) > 1

    def test_run_sweep_callable(self):
        from kryptos.k4.cyrillic_projector import run_cyrillic_projector_sweep
        assert callable(run_cyrillic_projector_sweep)

    def test_keywords_alpha_only(self):
        from kryptos.k4.cyrillic_projector import CYRILLIC_PROJECTOR_KEYWORDS
        for kw in CYRILLIC_PROJECTOR_KEYWORDS:
            assert kw.isalpha(), f"{kw} contains non-alpha characters"

    def test_build_keyed_alphabet_covers_full_alphabet(self):
        from kryptos.k4.cyrillic_projector import build_keyed_alphabet
        for kw in ["AGENT", "RAZVEDKA", "KONSPIRATSIYA"]:
            alpha = build_keyed_alphabet(kw)
            assert set(alpha) == set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


# ---------------------------------------------------------------------------
# API route coverage: P15/P16/P19/P20 in FRONTIER_VECTORS
# ---------------------------------------------------------------------------
class TestFrontierVectorsP15P20:
    def test_all_new_attacks_in_frontier(self):
        from kryptos.api.k4_attack_routes import FRONTIER_VECTORS
        ids = {v["id"] for v in FRONTIER_VECTORS}
        assert "p15_straddling_checkerboard" in ids
        assert "p16_corpus_miner" in ids
        assert "p19_advisory_keywords" in ids
        assert "p20_cyrillic_projector" in ids

    def test_all_new_attacks_runnable(self):
        from kryptos.api.k4_attack_routes import FRONTIER_VECTORS
        new_ids = {"p15_straddling_checkerboard", "p16_corpus_miner",
                   "p19_advisory_keywords", "p20_cyrillic_projector"}
        for v in FRONTIER_VECTORS:
            if v["id"] in new_ids:
                assert v["runnable"], f"{v['id']} should be runnable"
                assert v["status"] == "Active", f"{v['id']} should be Active"

    def test_all_new_attacks_have_descriptions(self):
        from kryptos.api.k4_attack_routes import FRONTIER_VECTORS
        new_ids = {"p15_straddling_checkerboard", "p16_corpus_miner",
                   "p19_advisory_keywords", "p20_cyrillic_projector"}
        for v in FRONTIER_VECTORS:
            if v["id"] in new_ids:
                assert len(v.get("description", "")) > 30, f"{v['id']} needs a description"
