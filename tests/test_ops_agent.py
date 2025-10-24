"""Tests for OPS agent (orchestration)."""

from kryptos.agents.ops import JobResult, OpsAgent, OpsConfig, ops_report


def test_ops_config_defaults():
    """Test OPS config default values."""
    config = OpsConfig()
    assert config.max_workers is None
    assert config.job_timeout_seconds == 300
    assert config.retry_failed is False
    assert config.save_artifacts is True


def test_ops_agent_initialization():
    """Test OPS agent can be initialized."""
    agent = OpsAgent()
    assert agent.config is not None
    assert agent.results == []


def test_job_result_creation():
    """Test JobResult dataclass creation."""
    result = JobResult(
        hypothesis_name="test_hyp",
        success=True,
        duration_seconds=1.5,
        candidates_count=10,
        best_score=-320.5,
    )
    assert result.hypothesis_name == "test_hyp"
    assert result.success is True
    assert result.duration_seconds == 1.5
    assert result.candidates_count == 10
    assert result.best_score == -320.5
    assert result.error is None


def test_ops_report_empty():
    """Test OPS report with no results."""
    report = ops_report([])
    assert "OPS AGENT EXECUTION REPORT" in report
    assert "Total jobs: 0" in report


def test_ops_report_with_results():
    """Test OPS report with sample results."""
    results = [
        JobResult(
            hypothesis_name="hill_2x2",
            success=True,
            duration_seconds=2.5,
            candidates_count=158000,
            best_score=-329.45,
        ),
        JobResult(
            hypothesis_name="vigenere",
            success=False,
            duration_seconds=0.0,
            error="Timeout exceeded",
        ),
    ]

    report = ops_report(results)
    assert "Total jobs: 2" in report
    assert "Successful: 1" in report
    assert "Failed: 1" in report
    assert "hill_2x2" in report
    assert "vigenere" in report
    assert "-329.45" in report


def test_ops_agent_summarize_no_jobs():
    """Test summary with no jobs run."""
    agent = OpsAgent()
    summary = agent.summarize()
    assert summary["status"] == "no_jobs"


def test_ops_agent_summarize_with_results():
    """Test summary generation with results."""
    agent = OpsAgent()
    agent.results = [
        JobResult(
            hypothesis_name="test1",
            success=True,
            duration_seconds=1.0,
            candidates_count=100,
            best_score=-320.0,
        ),
        JobResult(
            hypothesis_name="test2",
            success=True,
            duration_seconds=2.0,
            candidates_count=50,
            best_score=-350.0,
        ),
        JobResult(
            hypothesis_name="test3",
            success=False,
            duration_seconds=0.5,
            error="Failed",
        ),
    ]

    summary = agent.summarize()
    assert summary["total_jobs"] == 3
    assert summary["successful"] == 2
    assert summary["failed"] == 1
    assert summary["total_duration_seconds"] == 3.5
    assert summary["total_candidates"] == 150
    assert summary["best_hypothesis"] == "test1"
    assert summary["best_score"] == -320.0


def test_ops_run_hypothesis_job_success(monkeypatch):
    """Test successful hypothesis job execution."""

    # Mock hypothesis class
    class MockHypothesis:
        def generate_candidates(self, ciphertext, limit=10):
            # Return mock candidates with scores
            Candidate = type("Candidate", (), {"score": -330.0, "plaintext": "MOCK"})
            return [Candidate() for _ in range(5)]

    agent = OpsAgent()
    result = agent.run_hypothesis_job(
        "mock_test",
        MockHypothesis,
        "ABCDEFGHIJ",
    )

    assert result.success is True
    assert result.hypothesis_name == "mock_test"
    assert result.candidates_count == 5
    assert result.best_score == -330.0
    assert result.error is None


def test_ops_run_hypothesis_job_failure():
    """Test hypothesis job that raises exception."""

    class FailingHypothesis:
        def generate_candidates(self, ciphertext, limit=10):
            raise ValueError("Mock failure")

    agent = OpsAgent()
    result = agent.run_hypothesis_job(
        "failing_test",
        FailingHypothesis,
        "ABCDEFGHIJ",
    )

    assert result.success is False
    assert result.hypothesis_name == "failing_test"
    assert result.error is not None
    assert "Mock failure" in result.error
