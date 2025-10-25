"""Tests for OPS agent attack generation integration."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from kryptos.agents.ops import OpsAgent, OpsConfig
from kryptos.pipeline.attack_generator import AttackSpec

# ===== FIXTURES =====


@pytest.fixture
def temp_dir():
    """Temporary directory for test artifacts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def ops_agent(temp_dir):
    """OPS agent with attack generation enabled."""
    config = OpsConfig(
        enable_attack_generation=True,
        attack_log_dir=temp_dir / "attack_logs",
        log_level="DEBUG",
    )
    return OpsAgent(config=config)


@pytest.fixture
def ops_agent_no_generation():
    """OPS agent with attack generation disabled."""
    config = OpsConfig(enable_attack_generation=False)
    return OpsAgent(config=config)


@pytest.fixture
def k4_sample():
    """K4 ciphertext sample for testing."""
    return "OBKRUOXOGHULBSOLIFBBWFLRVQQPRNGKSSOTWTQSJQSSEKZZWATJKLUDIAWINFBNYPVTTMZFPKWGDKZXTJCDIGKUHUAUEKCAR"


# ===== CONFIGURATION TESTS =====


def test_ops_agent_configuration(ops_agent, ops_agent_no_generation):
    """Test OPS agent configuration with and without attack generation."""
    # With generation enabled
    assert ops_agent.attack_generator is not None
    assert ops_agent.attack_logger is not None

    # Without generation
    assert ops_agent_no_generation.attack_generator is None
    assert ops_agent_no_generation.attack_logger is None


# ===== ATTACK QUEUE GENERATION TESTS =====


def test_generate_attack_queues(ops_agent, ops_agent_no_generation, k4_sample):
    """Test attack queue generation from various sources."""
    # Q-Research hints
    q_attacks = ops_agent.generate_attack_queue_from_q_hints(
        ciphertext=k4_sample,
        max_attacks=20,
    )
    assert len(q_attacks) > 0
    assert len(q_attacks) <= 20
    assert all(isinstance(a, AttackSpec) for a in q_attacks)
    assert all(a.source == "q_research" for a in q_attacks)

    # Comprehensive queue
    comp_attacks = ops_agent.generate_attack_queue_comprehensive(
        ciphertext=k4_sample,
        cipher_types=["vigenere", "transposition"],
        max_attacks=50,
    )
    assert len(comp_attacks) > 0
    assert len(comp_attacks) <= 50
    sources = {a.source for a in comp_attacks}
    assert "q_research" in sources or "coverage_gap" in sources

    # Should fail when disabled
    with pytest.raises(RuntimeError, match="Attack generation not enabled"):
        ops_agent_no_generation.generate_attack_queue_from_q_hints(k4_sample)
    with pytest.raises(RuntimeError, match="Attack generation not enabled"):
        ops_agent_no_generation.generate_attack_queue_comprehensive(k4_sample)


# ===== ATTACK QUEUE EXECUTION TESTS =====


def test_execute_attack_queue(ops_agent, ops_agent_no_generation, k4_sample):
    """Test attack queue execution with logging and batching."""
    # Generate small queue
    attacks = ops_agent.generate_attack_queue_from_q_hints(k4_sample, max_attacks=5)
    initial_total = ops_agent.attack_logger.stats["total_attacks"]

    # Execute (placeholder implementation)
    summary = ops_agent.execute_attack_queue(
        attack_queue=attacks,
        ciphertext=k4_sample,
        batch_size=2,
    )

    # Check summary structure
    assert "total_attacks" in summary
    assert "executed" in summary
    assert "successful" in summary
    assert summary["total_attacks"] == len(attacks)
    assert summary["executed"] == len(attacks)

    # Should have logged attacks
    final_total = ops_agent.attack_logger.stats["total_attacks"]
    assert final_total == initial_total + len(attacks)

    # Should fail without logger
    with pytest.raises(RuntimeError, match="Attack logging not enabled"):
        ops_agent_no_generation.execute_attack_queue([], k4_sample)


# ===== INTEGRATION TESTS =====


def test_full_workflow_with_deduplication(ops_agent, k4_sample):
    """Test full workflow: generation → execution → deduplication."""
    # 1. Generate and execute from Q hints
    attacks1 = ops_agent.generate_attack_queue_from_q_hints(k4_sample, max_attacks=10)
    summary1 = ops_agent.execute_attack_queue(attacks1, k4_sample, batch_size=5)

    assert summary1["executed"] == len(attacks1)
    assert ops_agent.attack_logger.stats["total_attacks"] >= len(attacks1)

    # 2. Generate comprehensive queue
    attacks2 = ops_agent.generate_attack_queue_comprehensive(
        k4_sample,
        cipher_types=["vigenere"],
        max_attacks=15,
    )
    summary2 = ops_agent.execute_attack_queue(attacks2, k4_sample, batch_size=3)

    assert summary2["executed"] == len(attacks2)

    # 3. Re-execute first batch to test deduplication
    initial_unique = ops_agent.attack_logger.stats["unique_attacks"]
    ops_agent.execute_attack_queue(attacks1[:5], k4_sample)

    # Logger should prevent duplicates
    duplicates_prevented = ops_agent.attack_logger.stats["duplicates_prevented"]
    assert duplicates_prevented == 5, f"Should prevent 5 dupes, got {duplicates_prevented}"

    final_unique = ops_agent.attack_logger.stats["unique_attacks"]
    assert final_unique == initial_unique, "Unique count should not increase"

    # 4. Fresh generation should filter duplicates
    ops_agent.generate_attack_queue_from_q_hints(k4_sample, max_attacks=5)
    gen_stats = ops_agent.attack_generator.get_statistics()
    assert gen_stats["duplicates_filtered"] > 0, "Generator should filter duplicates"


# ===== STATISTICS TESTS =====


def test_statistics_tracking(ops_agent, k4_sample):
    """Test attack logger and generator statistics tracking."""
    # Generate and execute
    attacks = ops_agent.generate_attack_queue_from_q_hints(k4_sample, max_attacks=10)
    summary = ops_agent.execute_attack_queue(attacks, k4_sample)

    # Check logger stats in summary
    assert "attack_logger_stats" in summary
    logger_stats = summary["attack_logger_stats"]
    assert "total_attacks" in logger_stats
    assert "unique_attacks" in logger_stats
    assert "duplicates_prevented" in logger_stats

    # Check generator stats
    gen_stats = ops_agent.attack_generator.get_statistics()
    assert gen_stats["from_q_hints"] > 0
    assert gen_stats["generated"] > 0
    assert "deduplication_rate" in gen_stats


# ===== BATCHING TESTS =====


def test_batching_behavior(ops_agent, k4_sample):
    """Test that batch_size is respected during execution."""
    attacks = ops_agent.generate_attack_queue_from_q_hints(k4_sample, max_attacks=10)

    # Small batch size
    summary1 = ops_agent.execute_attack_queue(attacks[:5], k4_sample, batch_size=2)
    assert summary1["executed"] == 5

    # Large batch (all at once)
    summary2 = ops_agent.execute_attack_queue(attacks[5:], k4_sample, batch_size=100)
    assert summary2["executed"] == 5
