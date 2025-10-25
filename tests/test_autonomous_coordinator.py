"""Tests for autonomous coordination system."""

from __future__ import annotations

import json
from datetime import datetime
from unittest.mock import patch

import pytest

from kryptos.autonomous_coordinator import (
    AutonomousCoordinator,
    AutonomousState,
    CoordinationMessage,
    MessageType,
)


@pytest.fixture
def temp_state_path(tmp_path):
    """Provide temporary state file path."""
    return tmp_path / "test_autonomous_state.json"


@pytest.fixture
def coordinator(temp_state_path):
    """Create coordinator with temporary state."""
    return AutonomousCoordinator(
        state_path=temp_state_path,
        ops_cycle_minutes=1,  # Fast for testing
        web_intel_check_hours=1,
    )


class TestCoordinationMessage:
    """Test coordination message functionality."""

    def test_message_creation(self):
        """Test creating coordination message."""
        msg = CoordinationMessage(
            msg_type=MessageType.INSIGHT,
            source="SPY",
            target="COORDINATOR",
            timestamp=datetime.now(),
            priority=8,
            content={"category": "linguistic", "confidence": 0.85},
            metadata={"test": True},
        )

        assert msg.msg_type == MessageType.INSIGHT
        assert msg.source == "SPY"
        assert msg.target == "COORDINATOR"
        assert msg.priority == 8
        assert msg.content["confidence"] == 0.85
        assert msg.metadata["test"] is True

    def test_message_serialization(self):
        """Test message to/from dict conversion."""
        original = CoordinationMessage(
            msg_type=MessageType.ALERT,
            source="OPS",
            target="COORDINATOR",
            timestamp=datetime(2025, 10, 25, 12, 0, 0),
            priority=10,
            content={"reason": "breakthrough"},
        )

        # Serialize
        data = original.to_dict()
        assert data["msg_type"] == "alert"
        assert data["source"] == "OPS"
        assert data["priority"] == 10

        # Deserialize
        restored = CoordinationMessage.from_dict(data)
        assert restored.msg_type == MessageType.ALERT
        assert restored.source == "OPS"
        assert restored.priority == 10
        assert restored.content["reason"] == "breakthrough"


class TestAutonomousState:
    """Test autonomous state management."""

    def test_state_creation(self):
        """Test creating new state."""
        state = AutonomousState(
            session_start=datetime.now(),
            total_runtime_hours=0.0,
            coordination_cycles=0,
            active_attacks={},
            agent_insights=[],
            strategic_decisions=[],
            k123_patterns_loaded=False,
            web_intel_last_check=None,
            last_ops_decision=None,
            best_score_ever=0.0,
            total_candidates_tested=0,
        )

        assert state.coordination_cycles == 0
        assert state.k123_patterns_loaded is False
        assert state.best_score_ever == 0.0

    def test_state_serialization(self):
        """Test state to/from dict conversion."""
        original = AutonomousState(
            session_start=datetime(2025, 10, 25, 10, 0, 0),
            total_runtime_hours=5.5,
            coordination_cycles=66,
            active_attacks={},
            agent_insights=[],
            strategic_decisions=[],
            k123_patterns_loaded=True,
            web_intel_last_check=datetime(2025, 10, 25, 12, 0, 0),
            last_ops_decision=datetime(2025, 10, 25, 11, 0, 0),
            best_score_ever=0.2847,
            total_candidates_tested=100000,
        )

        # Serialize
        data = original.to_dict()
        assert data["total_runtime_hours"] == 5.5
        assert data["coordination_cycles"] == 66
        assert data["k123_patterns_loaded"] is True
        assert data["best_score_ever"] == 0.2847

        # Deserialize
        restored = AutonomousState.from_dict(data)
        assert restored.coordination_cycles == 66
        assert restored.k123_patterns_loaded is True
        assert restored.total_candidates_tested == 100000


class TestAutonomousCoordinator:
    """Test autonomous coordinator functionality."""

    def test_coordinator_initialization(self, coordinator, temp_state_path):
        """Test coordinator initializes correctly."""
        assert coordinator.state_path == temp_state_path
        assert coordinator.ops_cycle_minutes == 1
        assert coordinator.web_intel_check_hours == 1
        assert coordinator.state.coordination_cycles == 0

    def test_state_persistence(self, coordinator):
        """Test state save/load cycle."""
        # Modify state
        coordinator.state.coordination_cycles = 5
        coordinator.state.best_score_ever = 0.25
        coordinator.state.k123_patterns_loaded = True

        # Save
        coordinator._save_state()

        # Create new coordinator with same path (should load)
        coordinator2 = AutonomousCoordinator(state_path=coordinator.state_path)

        # Verify loaded state
        assert coordinator2.state.coordination_cycles == 5
        assert coordinator2.state.best_score_ever == 0.25
        assert coordinator2.state.k123_patterns_loaded is True

    def test_load_k123_patterns(self, coordinator):
        """Test K123 pattern loading."""
        with patch.object(coordinator.k123_analyzer, "analyze_all") as mock_analyze:
            # Mock pattern data
            from kryptos.agents.k123_analyzer import SanbornPattern

            mock_patterns = [
                SanbornPattern(
                    category="THEME",
                    description="Location theme",
                    evidence=["north", "west", "degrees"],
                    k4_hypothesis="Try location cribs",
                    confidence=0.95,
                ),
            ]
            mock_analyze.return_value = mock_patterns

            # Load patterns
            coordinator._load_k123_patterns()

            # Verify
            assert coordinator.state.k123_patterns_loaded is True
            assert len(coordinator.state.agent_insights) > 0
            insight = coordinator.state.agent_insights[0]
            assert insight.agent_name == "K123_ANALYZER"
            assert "patterns" in insight.description.lower()

    def test_check_web_intelligence_throttling(self, coordinator):
        """Test web intel check respects time throttling."""
        # Set last check to recent
        coordinator.state.web_intel_last_check = datetime.now()

        with patch.object(coordinator.web_intel, "gather_intelligence") as mock_gather:
            # Should not call gather_intelligence due to throttling
            coordinator._check_web_intelligence()
            mock_gather.assert_not_called()

    @patch("kryptos.autonomous_coordinator.run_exchange")
    def test_coordination_cycle_basic(self, mock_exchange, coordinator):
        """Test basic coordination cycle execution."""
        with (
            patch.object(coordinator, "_load_k123_patterns") as mock_load,
            patch.object(coordinator, "_check_web_intelligence") as mock_web,
            patch.object(coordinator, "_run_ops_strategic_analysis") as mock_ops,
        ):
            # Run single cycle
            coordinator._coordination_cycle()

            # Verify all steps called
            mock_load.assert_called_once()
            mock_web.assert_called_once()
            mock_ops.assert_called_once()
            mock_exchange.assert_called_once()

            # Verify state updated
            assert coordinator.state.coordination_cycles == 1
            assert coordinator.state.total_runtime_hours > 0

    def test_generate_progress_report(self, coordinator):
        """Test progress report generation."""
        # Set up some state
        coordinator.state.coordination_cycles = 10
        coordinator.state.best_score_ever = 0.28
        coordinator.state.total_candidates_tested = 50000

        with patch.object(coordinator.ops_director, "generate_daily_report") as mock_report:
            mock_report.return_value = "# Daily Report\nTest content"

            report = coordinator._generate_progress_report()

            # Verify report contains coordination stats
            assert "coordination" in report.lower() or "cycles" in report.lower()
            assert "10" in report  # cycle count

    def test_execute_strategic_decision_continue(self, coordinator):
        """Test executing CONTINUE decision."""
        from kryptos.agents.ops_director import StrategyAction

        decision = {
            "action": StrategyAction.CONTINUE.value,
            "reasoning": "Making progress",
            "confidence": 0.75,
        }

        # Should execute without error
        coordinator._execute_strategic_decision(StrategyAction.CONTINUE, decision)

    def test_execute_strategic_decision_pivot(self, coordinator):
        """Test executing PIVOT decision."""
        from kryptos.agents.ops_director import StrategyAction

        decision = {
            "action": StrategyAction.PIVOT.value,
            "reasoning": "Stuck, trying new approach",
            "confidence": 0.80,
        }

        with patch("kryptos.autonomous_coordinator.run_exchange") as mock_exchange:
            coordinator._execute_strategic_decision(StrategyAction.PIVOT, decision)
            # Should trigger exchange with plan
            mock_exchange.assert_called_once()
            call_args = mock_exchange.call_args
            assert "PIVOT" in call_args.kwargs["plan_text"]

    def test_state_corrupted_recovery(self, temp_state_path):
        """Test coordinator handles corrupted state file."""
        # Write corrupted JSON
        temp_state_path.write_text("{ invalid json }", encoding="utf-8")

        # Should create new state instead of crashing
        coordinator = AutonomousCoordinator(state_path=temp_state_path)
        assert coordinator.state.coordination_cycles == 0


@pytest.mark.integration
class TestAutonomousIntegration:
    """Integration tests for autonomous system."""

    def test_full_cycle_integration(self, tmp_path):
        """Test complete coordination cycle with all components."""
        state_path = tmp_path / "integration_state.json"
        coordinator = AutonomousCoordinator(
            state_path=state_path,
            ops_cycle_minutes=0,  # No throttling
            web_intel_check_hours=0,
        )

        # Mock external dependencies
        with (
            patch.object(coordinator.k123_analyzer, "analyze_all") as mock_patterns,
            patch.object(coordinator.web_intel, "gather_intelligence") as mock_web,
            patch.object(coordinator.ops_director, "analyze_situation") as mock_ops,
            patch("kryptos.autonomous_coordinator.run_exchange") as mock_exchange,
        ):
            from kryptos.agents.k123_analyzer import SanbornPattern
            from kryptos.agents.ops_director import StrategicDecision, StrategyAction

            # Setup mocks
            mock_patterns.return_value = [
                SanbornPattern("THEME", "Test", ["evidence"], "hypothesis", 0.9),
            ]
            mock_web.return_value = []
            mock_ops.return_value = StrategicDecision(
                timestamp=datetime.now(),
                action=StrategyAction.CONTINUE,
                reasoning="Test reasoning",
                affected_attacks=[],
                resource_changes={},
                success_criteria="Test",
                review_in_hours=1.0,
                confidence=0.75,
            )

            # Run single cycle
            coordinator._coordination_cycle()

            # Verify all components called
            mock_patterns.assert_called_once()
            mock_web.assert_called_once()
            mock_ops.assert_called_once()
            mock_exchange.assert_called_once()

            # Verify state updated
            assert coordinator.state.coordination_cycles == 1
            assert coordinator.state.k123_patterns_loaded is True
            assert len(coordinator.state.strategic_decisions) == 1

            # Verify state persisted
            assert state_path.exists()
            saved_data = json.loads(state_path.read_text(encoding="utf-8"))
            assert saved_data["coordination_cycles"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
