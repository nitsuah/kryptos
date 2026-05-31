"""Tests for Q agent (quality assurance)."""

from kryptos.agents.q import QAgent, QConfig, ValidationResult, q_report


def test_q_config_defaults():
    """Test Q config default values."""
    config = QConfig()
    assert config.baseline_mean == -355.92
    assert config.baseline_stddev == 14.62
    assert config.sigma_2_threshold == -326.68
    assert config.sigma_3_threshold == -312.06


def test_q_agent_initialization():
    """Test Q agent can be initialized."""
    agent = QAgent()
    assert agent.config is not None
    assert agent.validations == []


def test_validation_result_creation():
    """Test ValidationResult dataclass creation."""
    result = ValidationResult(
        check_name="test_check",
        passed=True,
        severity="info",
        message="Test passed",
    )
    assert result.check_name == "test_check"
    assert result.passed is True
    assert result.severity == "info"
    assert result.message == "Test passed"


def test_validate_score_strong_signal():
    """Test score validation with strong signal (>3σ)."""
    agent = QAgent()
    result = agent.validate_score(-310.0, "test_hypothesis")

    assert result.passed is True
    assert result.severity == "info"
    assert "STRONG SIGNAL" in result.message
    assert result.details is not None
    assert result.details["score"] == -310.0


def test_validate_score_weak_signal():
    """Test score validation with weak signal (2σ < score < 3σ)."""
    agent = QAgent()
    result = agent.validate_score(-320.0, "test_hypothesis")

    assert result.passed is True
    assert result.severity == "warning"
    assert "WEAK SIGNAL" in result.message
    assert result.details is not None
    assert "Requires additional validation" in result.details["recommendation"]


def test_validate_score_no_signal():
    """Test score validation with no signal (<2σ)."""
    agent = QAgent()
    result = agent.validate_score(-350.0, "test_hypothesis")

    assert result.passed is False
    assert result.severity == "info"
    assert "NO SIGNAL" in result.message


def test_validate_plaintext_correct_length():
    """Test plaintext validation with correct length."""
    agent = QAgent()
    plaintext = "A" * 97
    results = agent.validate_plaintext(plaintext, expected_length=97)

    length_check = [r for r in results if r.check_name == "length_check"][0]
    assert length_check.passed is True


def test_validate_plaintext_wrong_length():
    """Test plaintext validation with incorrect length."""
    agent = QAgent()
    plaintext = "A" * 50
    results = agent.validate_plaintext(plaintext, expected_length=97)

    length_check = [r for r in results if r.check_name == "length_check"][0]
    assert length_check.passed is False
    assert "Length mismatch" in length_check.message


def test_validate_plaintext_low_alphabet_ratio():
    """Test plaintext validation with low alphabet ratio."""
    agent = QAgent()
    plaintext = "ABC123456789" * 8  # Mix of letters and numbers
    results = agent.validate_plaintext(plaintext, expected_length=len(plaintext))

    alphabet_check = [r for r in results if r.check_name == "alphabet_check"][0]
    assert alphabet_check.passed is False
    assert "Low alphabet ratio" in alphabet_check.message


def test_validate_plaintext_excessive_repetition():
    """Test plaintext validation with excessive character repetition."""
    agent = QAgent()
    # 20% of chars are 'A' - should trigger warning
    plaintext = "A" * 20 + "BCDEFGHIJK" * 8
    results = agent.validate_plaintext(plaintext, expected_length=len(plaintext))

    repetition_check = [r for r in results if r.check_name == "repetition_check"][0]
    assert repetition_check.passed is False
    assert "Excessive repetition" in repetition_check.message


def test_validate_candidate_set_sufficient():
    """Test candidate set validation with sufficient candidates."""
    agent = QAgent()
    scores = [-320.0 + i * 0.5 for i in range(15)]
    result = agent.validate_candidate_set(scores, min_candidates=10)

    assert result.passed is True


def test_validate_candidate_set_insufficient():
    """Test candidate set validation with insufficient candidates."""
    agent = QAgent()
    scores = [-320.0, -321.0, -322.0]
    result = agent.validate_candidate_set(scores, min_candidates=10)

    assert result.passed is False
    assert "Insufficient candidates" in result.message


def test_detect_anomalies_duplicate_plaintexts():
    """Test anomaly detection with duplicate plaintexts."""
    agent = QAgent()
    candidates = [
        {"plaintext": "ABCDEFG", "score": -320.0},
        {"plaintext": "ABCDEFG", "score": -321.0},  # Duplicate
        {"plaintext": "HIJKLMN", "score": -322.0},
    ]

    results = agent.detect_anomalies(candidates)
    duplicate_check = [r for r in results if r.check_name == "duplicate_plaintext"]

    assert len(duplicate_check) > 0
    assert duplicate_check[0].passed is False


def test_detect_anomalies_duplicate_scores():
    """Test anomaly detection with many duplicate scores."""
    agent = QAgent()
    candidates = [
        {"plaintext": f"TEXT{i}", "score": -320.0}  # Same score
        for i in range(10)
    ]

    results = agent.detect_anomalies(candidates)
    score_check = [r for r in results if r.check_name == "duplicate_scores"]

    assert len(score_check) > 0
    assert score_check[0].passed is False


def test_q_report_empty():
    """Test Q report with no validations."""
    report = q_report([])
    assert "Q AGENT VALIDATION REPORT" in report
    assert "Total checks: 0" in report


def test_q_report_with_validations():
    """Test Q report with sample validations."""
    validations = [
        ValidationResult(
            check_name="test1",
            passed=True,
            severity="info",
            message="Check passed",
        ),
        ValidationResult(
            check_name="test2",
            passed=False,
            severity="error",
            message="Check failed",
        ),
    ]

    report = q_report(validations)
    assert "Total checks: 2" in report
    assert "Passed: 1" in report
    assert "Failed: 1" in report
    assert "test2" in report


def test_generate_report():
    """Test Q agent report generation."""
    agent = QAgent()
    agent.validations = [
        ValidationResult(
            check_name="pass_check",
            passed=True,
            severity="warning",  # Only warnings show in passed section
            message="OK",
        ),
        ValidationResult(
            check_name="fail_check",
            passed=False,
            severity="error",
            message="FAIL",
        ),
    ]

    report = agent.generate_report()
    assert "Q AGENT VALIDATION REPORT" in report
    assert "pass_check" in report  # Now shown because it's a warning
    assert "fail_check" in report
