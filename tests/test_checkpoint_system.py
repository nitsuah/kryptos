"""Tests for OPS Checkpoint System."""

from datetime import datetime

import pytest

from kryptos.agents.ops_director import AttackProgress
from kryptos.autonomous_coordinator import AutonomousCoordinator


class TestCheckpointSystem:
    """Test checkpoint creation and recovery."""

    def test_create_checkpoint_basic(self, tmp_path):
        """Test basic checkpoint creation."""
        state_path = tmp_path / "state.json"
        coordinator = AutonomousCoordinator(state_path=state_path)

        # Create a checkpoint
        coordinator.create_checkpoint(
            attack_type="vigenere_northeast",
            search_space_position={"key_length": 8, "key_index": 1000, "crib_position": 0},
            promising_candidates=[{"key": "TESTKEY", "score": 0.25}],
            metadata={"note": "test checkpoint"},
        )

        # Verify checkpoint was added to state
        assert len(coordinator.state.checkpoints) == 1
        checkpoint = coordinator.state.checkpoints[0]
        assert checkpoint["attack_type"] == "vigenere_northeast"
        assert checkpoint["search_space_position"]["key_length"] == 8
        assert checkpoint["search_space_position"]["key_index"] == 1000
        assert len(checkpoint["promising_candidates"]) == 1
        assert checkpoint["metadata"]["note"] == "test checkpoint"

    def test_checkpoint_persistence(self, tmp_path):
        """Test that checkpoints persist across sessions."""
        state_path = tmp_path / "state.json"

        # Session 1: Create checkpoint
        coordinator1 = AutonomousCoordinator(state_path=state_path)
        coordinator1.create_checkpoint(
            attack_type="hill_2x2",
            search_space_position={"matrix_index": 5000},
            metadata={"session": 1},
        )

        # Session 2: Load and verify checkpoint exists
        coordinator2 = AutonomousCoordinator(state_path=state_path)
        assert len(coordinator2.state.checkpoints) == 1
        checkpoint = coordinator2.state.checkpoints[0]
        assert checkpoint["attack_type"] == "hill_2x2"
        assert checkpoint["search_space_position"]["matrix_index"] == 5000
        assert checkpoint["metadata"]["session"] == 1

    def test_get_latest_checkpoint(self, tmp_path):
        """Test retrieving the latest checkpoint for an attack."""
        state_path = tmp_path / "state.json"
        coordinator = AutonomousCoordinator(state_path=state_path)

        # Create multiple checkpoints for different attacks
        coordinator.create_checkpoint(
            attack_type="vigenere_northeast",
            search_space_position={"key_index": 1000},
        )
        coordinator.create_checkpoint(
            attack_type="hill_2x2",
            search_space_position={"matrix_index": 500},
        )
        coordinator.create_checkpoint(
            attack_type="vigenere_northeast",
            search_space_position={"key_index": 2000},
        )

        # Get latest checkpoint for vigenere
        checkpoint = coordinator.get_latest_checkpoint("vigenere_northeast")
        assert checkpoint is not None
        assert checkpoint["search_space_position"]["key_index"] == 2000

        # Get latest checkpoint for hill
        checkpoint = coordinator.get_latest_checkpoint("hill_2x2")
        assert checkpoint is not None
        assert checkpoint["search_space_position"]["matrix_index"] == 500

        # Non-existent attack
        checkpoint = coordinator.get_latest_checkpoint("nonexistent")
        assert checkpoint is None

    def test_tested_keys_storage(self, tmp_path):
        """Test saving and loading tested keys."""
        state_path = tmp_path / "state.json"
        coordinator = AutonomousCoordinator(state_path=state_path)

        # Create checkpoint with tested keys
        tested_keys = [f"KEY{i:04d}" for i in range(100)]
        coordinator.create_checkpoint(
            attack_type="vigenere_northeast",
            search_space_position={"key_index": 100},
            tested_keys=tested_keys,
        )

        # Verify tested keys were saved separately
        keys_file = tmp_path / "tested_keys" / "vigenere_northeast_tested_keys.json"
        assert keys_file.exists()

        # Load tested keys
        loaded_keys = coordinator.load_tested_keys("vigenere_northeast")
        assert len(loaded_keys) == 100
        assert "KEY0000" in loaded_keys
        assert "KEY0099" in loaded_keys

    def test_tested_keys_accumulate(self, tmp_path):
        """Test that tested keys accumulate across checkpoints."""
        state_path = tmp_path / "state.json"
        coordinator = AutonomousCoordinator(state_path=state_path)

        # First checkpoint
        coordinator.create_checkpoint(
            attack_type="vigenere_northeast",
            search_space_position={"key_index": 50},
            tested_keys=[f"KEY{i:04d}" for i in range(50)],
        )

        # Second checkpoint with more keys
        coordinator.create_checkpoint(
            attack_type="vigenere_northeast",
            search_space_position={"key_index": 100},
            tested_keys=[f"KEY{i:04d}" for i in range(50, 100)],
        )

        # Should have all 100 keys
        loaded_keys = coordinator.load_tested_keys("vigenere_northeast")
        assert len(loaded_keys) == 100

    def test_checkpoint_pruning(self, tmp_path):
        """Test that old checkpoints are pruned to prevent bloat."""
        state_path = tmp_path / "state.json"
        coordinator = AutonomousCoordinator(state_path=state_path)

        # Create 60 checkpoints (more than the 50 limit)
        for i in range(60):
            coordinator.create_checkpoint(
                attack_type="test_attack",
                search_space_position={"index": i},
            )

        # Should only keep last 50
        assert len(coordinator.state.checkpoints) == 50
        # Oldest should be checkpoint 10 (60 - 50 = 10)
        assert coordinator.state.checkpoints[0]["search_space_position"]["index"] == 10
        # Newest should be checkpoint 59
        assert coordinator.state.checkpoints[-1]["search_space_position"]["index"] == 59

    def test_resume_from_checkpoint(self, tmp_path):
        """Test resuming an attack from a checkpoint."""
        state_path = tmp_path / "state.json"
        coordinator = AutonomousCoordinator(state_path=state_path)

        # Simulate an attack that created checkpoints
        coordinator.create_checkpoint(
            attack_type="vigenere_northeast",
            search_space_position={
                "key_length": 8,
                "key_index": 5000,
                "crib": "NORTHEAST",
                "crib_position": 0,
            },
            tested_keys=[f"KEY{i}" for i in range(5000)],
            promising_candidates=[
                {"key": "PALIMPSE", "score": 0.22, "position": 10},
                {"key": "ABSCISSA", "score": 0.21, "position": 15},
            ],
            metadata={"interrupted": True, "reason": "system restart"},
        )

        # Simulate a new session that resumes
        coordinator2 = AutonomousCoordinator(state_path=state_path)
        checkpoint = coordinator2.get_latest_checkpoint("vigenere_northeast")

        # Verify we can resume from saved position
        assert checkpoint is not None
        assert checkpoint["search_space_position"]["key_index"] == 5000
        assert checkpoint["search_space_position"]["crib"] == "NORTHEAST"
        assert len(checkpoint["promising_candidates"]) == 2

        # Load tested keys to avoid retesting
        tested_keys = coordinator2.load_tested_keys("vigenere_northeast")
        assert len(tested_keys) == 5000
        assert "KEY0" in tested_keys
        assert "KEY4999" in tested_keys

    def test_checkpoint_metadata(self, tmp_path):
        """Test storing arbitrary metadata in checkpoints."""
        state_path = tmp_path / "state.json"
        coordinator = AutonomousCoordinator(state_path=state_path)

        # Create checkpoint with rich metadata
        coordinator.create_checkpoint(
            attack_type="custom_attack",
            search_space_position={"step": 1},
            metadata={
                "agent_insights": ["SPY recommends BERLIN", "OPS suggests pivot"],
                "performance": {"keys_per_second": 1000, "cpu_percent": 80.5},
                "notes": "Detected anomaly in scoring function",
            },
        )

        checkpoint = coordinator.get_latest_checkpoint("custom_attack")
        assert checkpoint["metadata"]["performance"]["keys_per_second"] == 1000
        assert len(checkpoint["metadata"]["agent_insights"]) == 2


@pytest.mark.integration
class TestCheckpointIntegration:
    """Integration tests for checkpoints with autonomous system."""

    def test_automatic_checkpoint_creation(self, tmp_path):
        """Test that checkpoints are created automatically during coordination."""
        from unittest.mock import patch

        state_path = tmp_path / "state.json"
        coordinator = AutonomousCoordinator(
            state_path=state_path,
            ops_cycle_minutes=0,
            web_intel_check_hours=0,
        )

        # Add an active attack to state
        coordinator.state.active_attacks["vigenere_northeast"] = AttackProgress(
            attack_type="vigenere_northeast",
            attempts=1000,
            best_score=0.15,
            time_elapsed_hours=0.5,
            cpu_allocation=0.5,
            improvement_rate=0.01,
            last_improvement=datetime.now(),
            confidence_trend=[0.1, 0.12, 0.15],
        )

        # Mock external dependencies
        with (
            patch.object(coordinator, "_load_k123_patterns"),
            patch.object(coordinator, "_check_web_intelligence"),
            patch.object(coordinator, "_run_ops_strategic_analysis"),
            patch("kryptos.autonomous_coordinator.run_exchange"),
        ):
            # Run 10 cycles to trigger checkpoint
            for _ in range(10):
                coordinator._coordination_cycle()

            # Should have created checkpoints on cycle 10
            assert len(coordinator.state.checkpoints) > 0
            checkpoint = coordinator.state.checkpoints[-1]
            assert checkpoint["attack_type"] == "vigenere_northeast"
            assert checkpoint["search_space_position"]["attempts"] == 1000
            assert checkpoint["metadata"]["cycle"] == 10
