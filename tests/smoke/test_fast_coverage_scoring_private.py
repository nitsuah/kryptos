from __future__ import annotations

import math
from pathlib import Path

from kryptos.k4 import scoring


def test_private_loader_letter_freq_and_ngrams(tmp_path: Path) -> None:
    letter_file = tmp_path / "letter.tsv"
    letter_file.write_text(
        "# comment\n"
        "BADROW\n"
        "AB\t9.9\n"
        "A\t12.5\n",
        encoding="utf-8",
    )
    freq = scoring._load_letter_freq(str(letter_file))
    assert freq == {"A": 12.5}
    assert scoring._load_letter_freq(str(tmp_path / "missing.tsv")) == {}

    ngram_file = tmp_path / "ngrams.tsv"
    ngram_file.write_text(
        "# comment\n"
        "BADROW\n"
        "AB\t1.5\n"
        "A1\t2.0\n",
        encoding="utf-8",
    )
    grams = scoring._load_ngrams(str(ngram_file))
    assert grams == {"AB": 1.5}
    assert scoring._load_ngrams(str(tmp_path / "missing2.tsv")) == {}


def test_private_loader_config_and_wordlist(tmp_path: Path) -> None:
    cfg_ok = tmp_path / "cfg.json"
    cfg_ok.write_text('{"cribs": ["berlin", 123, "CLOCK"]}', encoding="utf-8")
    assert scoring._load_config_cribs(str(cfg_ok)) == ["BERLIN", "CLOCK"]

    cfg_bad = tmp_path / "bad.json"
    cfg_bad.write_text("{not-json", encoding="utf-8")
    assert scoring._load_config_cribs(str(cfg_bad)) == []
    assert scoring._load_config_cribs(str(tmp_path / "nope.json")) == []

    words = tmp_path / "wordlist.txt"
    words.write_text("ab\nTHE\nC1A\nclock\n", encoding="utf-8")
    assert scoring._load_wordlist(str(words)) == {"THE", "CLOCK"}
    assert scoring._load_wordlist(str(tmp_path / "missing_words.txt")) == set()


def test_rarity_weighted_crib_bonus_branching(monkeypatch) -> None:
    monkeypatch.setattr(scoring, "_get_all_cribs", lambda: [])
    assert scoring.rarity_weighted_crib_bonus("ANY TEXT") == 0.0

    monkeypatch.setattr(scoring, "_get_all_cribs", lambda: ["BERLIN", "ZZZ"])
    assert scoring.rarity_weighted_crib_bonus("") == 0.0

    val = scoring.rarity_weighted_crib_bonus("BERLINBERLIN")
    assert isinstance(val, float)
    assert val > 0.0


def test_load_cribs_from_file_paths_and_decode(tmp_path: Path) -> None:
    assert scoring.load_cribs_from_file(None) == []
    assert scoring.load_cribs_from_file(tmp_path / "not_here.txt") == []

    cribs_file = tmp_path / "cribs.txt"
    cribs_file.write_text(
        "# comment\n"
        "ab\n"
        "berlin\textra\n"
        "C10CK\n"
        "CLOCK\n",
        encoding="utf-8",
    )
    assert scoring.load_cribs_from_file(cribs_file) == ["BERLIN", "CLOCK"]

    binary_file = tmp_path / "bad.bin"
    binary_file.write_bytes(b"\xff\xfe\xfd")
    assert scoring.load_cribs_from_file(binary_file) == []


def test_wordlist_hit_rate_hard_cap(monkeypatch) -> None:
    monkeypatch.setattr(scoring, "WORDLIST", {"A"})
    text = "A" * 350
    rate = scoring.wordlist_hit_rate(text, min_len=1, max_len=350)
    assert 0.0 <= rate <= 1.0


def test_positional_letter_deviation_expected_zero_branch(monkeypatch) -> None:
    monkeypatch.setattr(scoring, "LETTER_FREQ", {"A": 0.0})
    val = scoring.positional_letter_deviation_score("A" * 40, period=5)
    assert math.isclose(val, 1.0, rel_tol=1e-9)


def test_composite_stage_analysis_clamped_and_negative_bonus() -> None:
    improved = scoring.composite_score_with_stage_analysis(
        stage1_plaintext="AAAAAAAAAAAAAAAAAAAA",
        stage2_plaintext="THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG",
        stage1_score=-200.0,
        stage2_score=-120.0,
    )
    assert improved["ioc_bonus"] == 10.0
    assert 0.0 <= improved["word_bonus"] <= 5.0
    assert 0.0 <= improved["freq_bonus"] <= 8.0
    assert improved["final_score"] >= improved["base_score"]

    degraded = scoring.composite_score_with_stage_analysis(
        stage1_plaintext="THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG",
        stage2_plaintext="ZZZZZZZZZZZZZZZZZZZZ",
        stage1_score=-100.0,
        stage2_score=-150.0,
    )
    assert degraded["ioc_bonus"] >= 0.0
    assert degraded["word_bonus"] >= 0.0
    assert degraded["freq_bonus"] >= 0.0
    assert degraded["total_bonus"] >= 0.0
