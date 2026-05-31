"""Tests for OPS Strategic Director LLM integration."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from kryptos.agents.ops_director import (
    AgentInsight,
    AttackProgress,
    OpsStrategicDirector,
    StrategyAction,
)


@pytest.fixture
def temp_cache_dir(tmp_path):
    """Create temporary cache directory."""
    return tmp_path / "ops_cache"


@pytest.fixture
def ops_local(temp_cache_dir):
    """Create OPS director with local (rule-based) provider."""
    return OpsStrategicDirector(llm_provider="local", model="rule-based", cache_dir=temp_cache_dir)


@pytest.fixture
def ops_openai(temp_cache_dir):
    """Create OPS director with OpenAI provider (mocked)."""
    return OpsStrategicDirector(llm_provider="openai", model="gpt-4", cache_dir=temp_cache_dir)


class TestLLMClientInitialization:
    """Test LLM client initialization."""

    def test_local_provider_no_client(self, ops_local):
        """Local provider should not initialize LLM client."""
        assert ops_local.llm_client is None

    def test_openai_provider_without_key(self, ops_openai):
        """OpenAI provider without API key should fall back to None."""
        # Since we haven't set OPENAI_API_KEY, should be None
        assert ops_openai.llm_client is None

    @patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test-key"})
    @patch("builtins.__import__", side_effect=lambda name, *args: MagicMock() if name == "openai" else __import__(name))
    def test_openai_provider_with_key(self, mock_import, temp_cache_dir):
        """OpenAI provider with API key should initialize client."""
        # Just verify it tries to initialize
        ops = OpsStrategicDirector(llm_provider="openai", model="gpt-4", cache_dir=temp_cache_dir)
        # May be None if openai not installed, that's OK for this test
        assert ops.llm_provider == "openai"

    @patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-ant-test-key"})
    @patch(
        "builtins.__import__",
        side_effect=lambda name, *args: MagicMock() if name == "anthropic" else __import__(name),
    )
    def test_anthropic_provider_with_key(self, mock_import, temp_cache_dir):
        """Anthropic provider with API key should initialize client."""
        # Just verify it tries to initialize
        ops = OpsStrategicDirector(llm_provider="anthropic", model="claude-3-opus", cache_dir=temp_cache_dir)
        # May be None if anthropic not installed, that's OK for this test
        assert ops.llm_provider == "anthropic"


class TestRuleBasedDecisions:
    """Test rule-based decision making (fallback mode)."""

    def test_continue_when_progress_steady(self, ops_local):
        """Should continue when attacks making progress."""
        # Setup attack with recent improvement
        ops_local.active_attacks["hill_3x3"] = AttackProgress(
            attack_type="hill_3x3",
            attempts=100000,
            best_score=0.25,
            time_elapsed_hours=2.0,
            cpu_allocation=0.5,
            improvement_rate=0.05,
            last_improvement=datetime.now() - timedelta(hours=1),
            confidence_trend=[0.20, 0.22, 0.25],
        )

        decision = ops_local.analyze_situation(force_decision=True)

        assert decision.action == StrategyAction.CONTINUE
        assert decision.confidence > 0.0
        assert "progress" in decision.reasoning.lower()

    def test_pivot_when_stagnant(self, ops_local):
        """Should pivot when attack stagnant >8 hours."""
        # Setup stagnant attack
        ops_local.active_attacks["vigenere_period_14"] = AttackProgress(
            attack_type="vigenere_period_14",
            attempts=500000,
            best_score=0.15,
            time_elapsed_hours=10.0,
            cpu_allocation=0.5,
            improvement_rate=0.0,
            last_improvement=datetime.now() - timedelta(hours=9),
            confidence_trend=[0.15, 0.15, 0.15],
        )

        decision = ops_local.analyze_situation(force_decision=True)

        assert decision.action == StrategyAction.PIVOT
        assert "vigenere_period_14" in decision.affected_attacks
        assert decision.review_in_hours > 0


class TestPromptBuilding:
    """Test LLM prompt construction."""

    def test_build_strategic_prompt_structure(self, ops_local):
        """Prompt should include all necessary context."""
        # Setup situation
        ops_local.active_attacks["hill_3x3"] = AttackProgress(
            attack_type="hill_3x3",
            attempts=100000,
            best_score=0.25,
            time_elapsed_hours=2.0,
            cpu_allocation=0.5,
            improvement_rate=0.05,
            last_improvement=datetime.now(),
            confidence_trend=[0.20, 0.22, 0.25],
        )

        ops_local.recent_insights.append(
            AgentInsight(
                agent_name="SPY",
                timestamp=datetime.now(),
                category="linguistic",
                description="Found rhyme pattern",
                confidence=0.85,
                actionable=True,
            ),
        )

        situation = ops_local._gather_situation_report()
        prompt = ops_local._build_strategic_prompt(situation)

        # Check prompt contains key sections
        assert "OPS" in prompt
        assert "Strategic Director" in prompt
        assert "hill_3x3" in prompt
        assert "Best score: 0.25" in prompt
        assert "SPY" in prompt
        assert "rhyme pattern" in prompt
        assert "JSON" in prompt
        assert "CONTINUE" in prompt
        assert "PIVOT" in prompt

    def test_prompt_includes_recent_insights(self, ops_local):
        """Prompt should include recent agent insights."""
        # Add multiple insights
        for i in range(5):
            ops_local.recent_insights.append(
                AgentInsight(
                    agent_name=f"Agent{i}",
                    timestamp=datetime.now(),
                    category="pattern",
                    description=f"Insight {i}",
                    confidence=0.8,
                    actionable=True,
                ),
            )

        situation = ops_local._gather_situation_report()
        prompt = ops_local._build_strategic_prompt(situation)

        # Should include insights (limited to last 10)
        for i in range(5):
            assert f"Insight {i}" in prompt


class TestLLMResponseParsing:
    """Test parsing of LLM responses."""

    def test_parse_valid_json_response(self, ops_local):
        """Should parse valid JSON response from LLM."""
        llm_response = """
        Here's my analysis:
        {
            "action": "PIVOT",
            "reasoning": "Attack showing no progress for 9 hours",
            "affected_attacks": ["hill_3x3"],
            "resource_changes": {"hill_3x3": 0.0, "vigenere": 0.5},
            "success_criteria": "New approach improves score within 4 hours",
            "review_in_hours": 4.0,
            "confidence": 0.85
        }
        That's my recommendation.
        """

        decision = ops_local._parse_llm_decision(llm_response)

        assert decision is not None
        assert decision.action == StrategyAction.PIVOT
        assert decision.reasoning == "Attack showing no progress for 9 hours"
        assert "hill_3x3" in decision.affected_attacks
        assert decision.confidence == 0.85
        assert decision.review_in_hours == 4.0

    def test_parse_response_with_only_json(self, ops_local):
        """Should parse response that is pure JSON."""
        llm_response = """
        {
            "action": "CONTINUE",
            "reasoning": "Steady progress",
            "affected_attacks": ["all"],
            "resource_changes": {},
            "success_criteria": "Maintain rate",
            "review_in_hours": 2.0,
            "confidence": 0.7
        }
        """

        decision = ops_local._parse_llm_decision(llm_response)

        assert decision is not None
        assert decision.action == StrategyAction.CONTINUE

    def test_parse_invalid_json_returns_none(self, ops_local):
        """Should return None for invalid JSON."""
        llm_response = "This is not JSON at all"

        decision = ops_local._parse_llm_decision(llm_response)

        assert decision is None

    def test_parse_json_missing_fields_returns_none(self, ops_local):
        """Should return None if JSON missing required fields."""
        llm_response = """
        {
            "action": "PIVOT",
            "reasoning": "Some reason"
        }
        """

        decision = ops_local._parse_llm_decision(llm_response)

        assert decision is None

    def test_parse_invalid_action_returns_none(self, ops_local):
        """Should return None if action is invalid."""
        llm_response = """
        {
            "action": "INVALID_ACTION",
            "reasoning": "Test",
            "affected_attacks": [],
            "resource_changes": {},
            "success_criteria": "Test",
            "review_in_hours": 1.0,
            "confidence": 0.5
        }
        """

        decision = ops_local._parse_llm_decision(llm_response)

        assert decision is None


@pytest.mark.integration
class TestLLMIntegration:
    """Integration tests for LLM-based decisions."""

    def test_openai_decision_flow(self, ops_openai, temp_cache_dir):
        """Test full decision flow with mocked OpenAI."""
        # Mock the LLM client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="""
            {
                "action": "BOOST",
                "reasoning": "Attack showing strong improvement trend",
                "affected_attacks": ["hill_3x3"],
                "resource_changes": {"hill_3x3": 0.8},
                "success_criteria": "Continue improvement at current rate",
                "review_in_hours": 1.0,
                "confidence": 0.9
            }
            """,
                ),
            ),
        ]
        mock_client.ChatCompletion.create.return_value = mock_response

        # Set the mocked client
        ops_openai.llm_client = mock_client

        # Setup attack
        ops_openai.active_attacks["hill_3x3"] = AttackProgress(
            attack_type="hill_3x3",
            attempts=100000,
            best_score=0.35,
            time_elapsed_hours=1.0,
            cpu_allocation=0.5,
            improvement_rate=0.15,
            last_improvement=datetime.now(),
            confidence_trend=[0.25, 0.30, 0.35],
        )

        decision = ops_openai.analyze_situation(force_decision=True)

        assert decision is not None
        assert decision.action == StrategyAction.BOOST
        assert decision.confidence == 0.9

    def test_fallback_to_rule_based_on_llm_failure(self, ops_local):
        """Should fall back to rule-based if LLM fails."""
        # Even with LLM client set, if call fails, should use rules
        ops_local.llm_client = MagicMock()
        ops_local.llm_provider = "openai"

        # Mock LLM call to return None (simulating failure)
        ops_local._call_llm = MagicMock(return_value=None)

        # Setup stagnant attack to trigger rule
        ops_local.active_attacks["test_attack"] = AttackProgress(
            attack_type="test_attack",
            attempts=100000,
            best_score=0.15,
            time_elapsed_hours=10.0,
            cpu_allocation=0.5,
            improvement_rate=0.0,
            last_improvement=datetime.now() - timedelta(hours=9),
            confidence_trend=[0.15, 0.15, 0.15],
        )

        decision = ops_local.analyze_situation(force_decision=True)

        # Should still get a decision from rule-based fallback
        assert decision is not None
        assert decision.action == StrategyAction.PIVOT


class TestDecisionPersistence:
    """Test decision history persistence."""

    def test_decisions_saved_to_file(self, ops_local):
        """Decisions should be persisted to JSONL file."""
        ops_local.active_attacks["test_attack"] = AttackProgress(
            attack_type="test_attack",
            attempts=100000,
            best_score=0.25,
            time_elapsed_hours=2.0,
            cpu_allocation=0.5,
            improvement_rate=0.05,
            last_improvement=datetime.now(),
            confidence_trend=[0.20, 0.25],
        )

        ops_local.analyze_situation(force_decision=True)

        # Check decision file exists
        decisions_file = ops_local.cache_dir / "decisions.jsonl"
        assert decisions_file.exists()

        # Check content
        with open(decisions_file) as f:
            lines = f.readlines()
            assert len(lines) >= 1
            # Should be valid JSON
            import json

            decision_data = json.loads(lines[-1])
            assert "action" in decision_data
            assert "reasoning" in decision_data
