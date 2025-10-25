"""Tests for attack generation engine."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from kryptos.pipeline.attack_generator import AttackGenerator, AttackSpec
from kryptos.provenance.attack_log import AttackLogger, AttackResult
from kryptos.research.q_patterns import QResearchAnalyzer

# ===== FIXTURES =====


@pytest.fixture
def temp_dir():
    """Temporary directory for test artifacts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def attack_logger(temp_dir):
    """Attack logger with temp directory."""
    return AttackLogger(log_dir=temp_dir / "attack_logs")


@pytest.fixture
def coverage_analyzer(temp_dir):
    """Fresh coverage analyzer with temp directory."""
    from kryptos.analysis.strategic_coverage import StrategicCoverageAnalyzer
    from kryptos.provenance.search_space import SearchSpaceTracker

    tracker = SearchSpaceTracker(cache_dir=temp_dir / "search_space")
    return StrategicCoverageAnalyzer(tracker=tracker, history_dir=temp_dir / "coverage_history")


@pytest.fixture
def attack_generator(attack_logger, coverage_analyzer, temp_dir):
    """Attack generator with dependencies."""
    return AttackGenerator(
        attack_logger=attack_logger,
        coverage_analyzer=coverage_analyzer,
        log_level="DEBUG",
    )


@pytest.fixture
def k4_sample():
    """K4 ciphertext sample for testing."""
    return "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"


# ===== Q-RESEARCH HINT CONVERSION TESTS =====


def test_generate_from_q_hints_vigenere(attack_generator, k4_sample):
    """Test generating attacks from Vigenère hints."""
    attacks = attack_generator.generate_from_q_hints(k4_sample, max_attacks=20)

    # Should generate some attacks
    assert len(attacks) > 0

    # Check for Vigenère attacks
    vigenere_attacks = [a for a in attacks if a.parameters.cipher_type == "vigenere"]
    assert len(vigenere_attacks) > 0

    # Verify structure
    for attack in vigenere_attacks:
        assert isinstance(attack, AttackSpec)
        assert 0.0 <= attack.priority <= 1.0
        assert attack.source == "q_research"
        assert "vigenere" in attack.tags
        assert "key_length" in attack.parameters.key_or_params


def test_generate_from_q_hints_transposition(attack_generator, k4_sample):
    """Test generating attacks from transposition hints."""
    attacks = attack_generator.generate_from_q_hints(k4_sample)

    # Check for transposition attacks
    trans_attacks = [a for a in attacks if a.parameters.cipher_type == "transposition"]

    # May or may not have transposition hints depending on analysis
    # Just verify they have correct structure if present
    for attack in trans_attacks:
        assert "transposition" in attack.tags
        assert "method" in attack.parameters.key_or_params
        assert attack.source == "q_research"


def test_vigenere_hint_conversion(attack_generator, k4_sample):
    """Test Vigenère metrics to attack parameter conversion."""
    # Manually analyze to get metrics
    q_analyzer = QResearchAnalyzer()
    metrics = q_analyzer.vigenere_analysis(k4_sample)

    # Convert to attacks
    attacks = attack_generator._vigenere_hints_to_attacks(metrics, k4_sample)

    # Should generate attacks for top key length candidates
    assert len(attacks) > 0
    assert len(attacks) <= 5  # Top 5

    # Check priority calculation
    for attack in attacks:
        assert 0.0 <= attack.priority <= 1.0
        key_length = attack.parameters.key_or_params["key_length"]
        assert key_length in metrics.key_length_candidates


def test_transposition_hint_conversion(attack_generator, k4_sample):
    """Test transposition hint to attack parameter conversion."""
    q_analyzer = QResearchAnalyzer()
    hints = q_analyzer.detect_transposition_hints(k4_sample)

    # Convert to attacks
    attacks = attack_generator._transposition_hints_to_attacks(hints, k4_sample)

    # Verify conversion
    assert len(attacks) == len(hints[:10])  # Top 10

    for attack in attacks:
        assert attack.parameters.cipher_type == "transposition"
        assert "method" in attack.parameters.key_or_params
        assert "period" in attack.parameters.key_or_params


def test_strategy_conversion(attack_generator, k4_sample):
    """Test strategy suggestions to attack parameter conversion."""
    q_analyzer = QResearchAnalyzer()
    strategies = q_analyzer.suggest_attack_strategies(k4_sample)

    # Convert to attacks
    attacks = attack_generator._strategies_to_attacks(strategies, k4_sample)

    # Should generate some attacks from high-priority strategies
    assert len(attacks) > 0

    # Check that priorities match
    for attack in attacks:
        assert attack.source == "q_research"
        assert "strategy" in attack.tags


# ===== COVERAGE GAP TARGETING TESTS =====


def test_generate_from_coverage_gaps_seed(attack_generator, k4_sample):
    """Test gap generation when no coverage data exists (seed attacks)."""
    attacks = attack_generator.generate_from_coverage_gaps(
        cipher_type="vigenere",
        ciphertext=k4_sample,
        max_attacks=20,
    )

    # Should generate seed attacks
    assert len(attacks) > 0
    assert len(attacks) <= 20

    # All should be Vigenère
    for attack in attacks:
        assert attack.parameters.cipher_type == "vigenere"
        assert attack.source == "coverage_gap"


def test_generate_seed_attacks_vigenere(attack_generator, k4_sample):
    """Test seed attack generation for Vigenère."""
    attacks = attack_generator._generate_seed_attacks("vigenere", k4_sample, max_attacks=10)

    assert len(attacks) == 10

    # Should have key lengths 2-11
    key_lengths = [a.parameters.key_or_params["key_length"] for a in attacks]
    assert key_lengths == list(range(2, 12))

    # All should have medium priority
    for attack in attacks:
        assert attack.priority == 0.5
        assert "seed" in attack.tags


def test_generate_seed_attacks_transposition(attack_generator, k4_sample):
    """Test seed attack generation for transposition."""
    attacks = attack_generator._generate_seed_attacks("transposition", k4_sample, max_attacks=15)

    assert len(attacks) == 15

    # Should have periods 2-16
    periods = [a.parameters.key_or_params["period"] for a in attacks]
    assert periods == list(range(2, 17))


def test_parse_region_key_vigenere(attack_generator):
    """Test parsing region keys for Vigenère."""
    params = attack_generator._parse_region_key("key_length_5-10")
    assert params == {"key_min": 5, "key_max": 10}


def test_parse_region_key_transposition(attack_generator):
    """Test parsing region keys for transposition."""
    params = attack_generator._parse_region_key("period_8-16")
    assert params == {"period_min": 8, "period_max": 16}


def test_generate_gap_filling_attacks(attack_generator, k4_sample):
    """Test generation of gap-filling attacks."""
    attacks = attack_generator._generate_gap_filling_attacks(
        cipher_type="vigenere",
        region_key="key_length_5-10",
        current_coverage=30.0,
        ciphertext=k4_sample,
        max_attacks=5,
    )

    assert len(attacks) == 5

    # Should target key lengths 5-9
    key_lengths = [a.parameters.key_or_params["key_length"] for a in attacks]
    assert key_lengths == list(range(5, 10))

    # Priority should reflect gap size (70% gap = 0.7 priority * 0.7 = 0.49)
    for attack in attacks:
        assert 0.4 <= attack.priority <= 0.75
        assert "gap_filling" in attack.tags


# ===== DEDUPLICATION TESTS =====


def test_deduplication_within_batch(attack_generator, k4_sample):
    """Test deduplication within a single generation batch."""
    # Generate attacks twice
    attacks1 = attack_generator.generate_from_q_hints(k4_sample, max_attacks=50)
    attacks2 = attack_generator.generate_from_q_hints(k4_sample, max_attacks=50)

    # Combine and deduplicate
    combined = attacks1 + attacks2
    deduplicated = attack_generator._deduplicate_attacks(combined)

    # Should have same length as one batch
    assert len(deduplicated) == len(attacks1)

    # Check fingerprints are unique
    fingerprints = [a.fingerprint() for a in deduplicated]
    assert len(fingerprints) == len(set(fingerprints))


def test_deduplication_against_logger(attack_logger, attack_generator, k4_sample):
    """Test deduplication against AttackLogger history."""
    # Generate attacks
    attacks = attack_generator.generate_from_q_hints(k4_sample, max_attacks=10)

    # Log first 5 as executed
    for attack in attacks[:5]:
        attack_logger.log_attack(
            ciphertext=k4_sample,
            parameters=attack.parameters,
            result=AttackResult(success=False),
        )

    # Generate again
    new_attacks = attack_generator.generate_from_q_hints(k4_sample, max_attacks=10)

    # Should filter out the 5 already logged
    remaining_fingerprints = {a.fingerprint() for a in new_attacks}
    logged_fingerprints = {attacks[i].fingerprint() for i in range(5)}

    # No overlap
    assert len(remaining_fingerprints & logged_fingerprints) == 0


def test_deduplication_statistics(attack_generator, k4_sample):
    """Test deduplication tracking in statistics."""
    initial_filtered = attack_generator.stats["duplicates_filtered"]

    # Generate with duplicates
    attacks1 = attack_generator.generate_from_q_hints(k4_sample)
    attacks2 = attack_generator.generate_from_q_hints(k4_sample)

    combined = attacks1 + attacks2
    attack_generator._deduplicate_attacks(combined)

    # Should have counted duplicates
    assert attack_generator.stats["duplicates_filtered"] > initial_filtered


# ===== PRIORITY SCORING TESTS =====


def test_priority_ordering(attack_generator, k4_sample):
    """Test that attacks are properly ordered by priority."""
    attacks = attack_generator.generate_from_q_hints(k4_sample, max_attacks=50)

    # Verify descending priority order
    priorities = [a.priority for a in attacks]
    assert priorities == sorted(priorities, reverse=True)


def test_q_hints_have_higher_priority(attack_generator, k4_sample):
    """Test that Q-Research hints have higher priority than gap-filling."""
    q_attacks = attack_generator.generate_from_q_hints(k4_sample, max_attacks=10)
    gap_attacks = attack_generator.generate_from_coverage_gaps(
        cipher_type="vigenere",
        ciphertext=k4_sample,
        max_attacks=10,
    )

    # Q hints should generally have higher priority
    avg_q_priority = sum(a.priority for a in q_attacks) / len(q_attacks)
    avg_gap_priority = sum(a.priority for a in gap_attacks) / len(gap_attacks)

    assert avg_q_priority > avg_gap_priority


# ===== COMPREHENSIVE QUEUE TESTS =====


def test_generate_comprehensive_queue(attack_generator, k4_sample):
    """Test generation of comprehensive attack queue from all sources."""
    attacks = attack_generator.generate_comprehensive_queue(
        ciphertext=k4_sample,
        cipher_types=["vigenere", "transposition"],
        max_total=100,
    )

    # Should generate attacks from multiple sources
    assert len(attacks) > 0
    assert len(attacks) <= 100

    # Should have mix of sources
    sources = {a.source for a in attacks}
    assert "q_research" in sources
    assert "coverage_gap" in sources

    # Should be prioritized
    priorities = [a.priority for a in attacks]
    assert priorities == sorted(priorities, reverse=True)


def test_comprehensive_queue_deduplication(attack_generator, k4_sample):
    """Test that comprehensive queue is properly deduplicated."""
    attacks = attack_generator.generate_comprehensive_queue(
        ciphertext=k4_sample,
        max_total=200,
    )

    # All fingerprints should be unique
    fingerprints = [a.fingerprint() for a in attacks]
    assert len(fingerprints) == len(set(fingerprints))


# ===== EXPORT TESTS =====


def test_export_queue(attack_generator, k4_sample, temp_dir):
    """Test exporting attack queue to JSON."""
    attacks = attack_generator.generate_from_q_hints(k4_sample, max_attacks=10)

    output_path = temp_dir / "attack_queue.json"
    attack_generator.export_queue(attacks, output_path)

    # Verify file exists
    assert output_path.exists()

    # Verify content
    with open(output_path) as f:
        data = json.load(f)

    assert data["total_attacks"] == len(attacks)
    assert len(data["attacks"]) == len(attacks)

    # Check first attack structure
    first = data["attacks"][0]
    assert "priority" in first
    assert "source" in first
    assert "rationale" in first
    assert "tags" in first
    assert "parameters" in first
    assert "fingerprint" in first


# ===== STATISTICS TESTS =====


def test_statistics_tracking(attack_generator, k4_sample):
    """Test generation statistics tracking."""
    # Generate from different sources
    attack_generator.generate_from_q_hints(k4_sample, max_attacks=10)
    attack_generator.generate_from_coverage_gaps("vigenere", k4_sample, max_attacks=10)

    stats = attack_generator.get_statistics()

    assert stats["from_q_hints"] > 0
    assert stats["from_coverage_gaps"] > 0
    assert stats["generated"] > 0
    assert "deduplication_rate" in stats


def test_statistics_deduplication_rate(attack_generator, k4_sample):
    """Test deduplication rate calculation in statistics."""
    # Generate with known duplicates
    attacks1 = attack_generator.generate_from_q_hints(k4_sample, max_attacks=20)
    attacks2 = attack_generator.generate_from_q_hints(k4_sample, max_attacks=20)

    combined = attacks1 + attacks2
    attack_generator._deduplicate_attacks(combined)

    stats = attack_generator.get_statistics()

    # Should have ~50% deduplication rate
    assert 0.0 <= stats["deduplication_rate"] <= 1.0


# ===== INTEGRATION TESTS =====


def test_full_workflow(attack_logger, attack_generator, k4_sample):
    """Test full workflow: generate → execute → deduplicate → regenerate."""
    # 1. Generate initial queue
    queue1 = attack_generator.generate_comprehensive_queue(k4_sample, max_total=30)

    # 2. "Execute" first 10 attacks (log them)
    for attack in queue1[:10]:
        attack_logger.log_attack(
            ciphertext=k4_sample,
            parameters=attack.parameters,
            result=AttackResult(success=False, execution_time_seconds=1.0),
            tags=attack.tags,
        )

    # 3. Generate new queue
    queue2 = attack_generator.generate_comprehensive_queue(k4_sample, max_total=30)

    # Should have filtered out the 10 executed attacks
    # (May have generated new ones too, so just check no duplicates with executed)
    executed_fingerprints = {queue1[i].fingerprint() for i in range(10)}
    new_fingerprints = {a.fingerprint() for a in queue2}

    assert len(executed_fingerprints & new_fingerprints) == 0


def test_parse_strategy_method_vigenere(attack_generator, k4_sample):
    """Test parsing Vigenère strategy methods."""
    params = attack_generator._parse_strategy_method("polyalphabetic", "vigenere_k7", k4_sample)

    assert params is not None
    assert params.cipher_type == "vigenere"
    assert params.key_or_params["key_length"] == 7


def test_parse_strategy_method_hybrid(attack_generator, k4_sample):
    """Test parsing hybrid strategy methods."""
    params = attack_generator._parse_strategy_method("hybrid", "vigenere_then_transpose", k4_sample)

    assert params is not None
    assert params.cipher_type == "hybrid"
    assert params.key_or_params["first"] == "vigenere"
    assert params.key_or_params["second"] == "transpose"
