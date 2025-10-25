"""Tests for attack provenance logging system."""

from __future__ import annotations

from datetime import datetime

from kryptos.provenance.attack_log import (
    AttackLogger,
    AttackParameters,
    AttackRecord,
    AttackResult,
)


class TestAttackParameters:
    """Test attack parameters."""

    def test_create_parameters(self):
        """Test creating attack parameters."""
        params = AttackParameters(
            cipher_type="vigenere",
            key_or_params={"key_length": 8, "key": "KRYPTOS"},
            crib_text="BERLIN",
            crib_position=5,
        )

        assert params.cipher_type == "vigenere"
        assert params.key_or_params["key_length"] == 8
        assert params.crib_text == "BERLIN"
        assert params.crib_position == 5

    def test_parameters_to_dict(self):
        """Test converting parameters to dictionary."""
        params = AttackParameters(
            cipher_type="hill",
            key_or_params={"matrix_size": 2},
        )

        d = params.to_dict()
        assert d["cipher_type"] == "hill"
        assert d["key_or_params"]["matrix_size"] == 2

    def test_parameters_fingerprint(self):
        """Test fingerprint generation."""
        params1 = AttackParameters(
            cipher_type="vigenere",
            key_or_params={"key": "ABC"},
        )

        params2 = AttackParameters(
            cipher_type="vigenere",
            key_or_params={"key": "ABC"},
        )

        # Same parameters = same fingerprint
        assert params1.fingerprint() == params2.fingerprint()

    def test_different_parameters_different_fingerprint(self):
        """Test different parameters yield different fingerprints."""
        params1 = AttackParameters(
            cipher_type="vigenere",
            key_or_params={"key": "ABC"},
        )

        params2 = AttackParameters(
            cipher_type="vigenere",
            key_or_params={"key": "XYZ"},
        )

        assert params1.fingerprint() != params2.fingerprint()

    def test_fingerprint_order_independent(self):
        """Test fingerprint is order-independent for dict keys."""
        params1 = AttackParameters(
            cipher_type="vigenere",
            key_or_params={"a": 1, "b": 2},
        )

        params2 = AttackParameters(
            cipher_type="vigenere",
            key_or_params={"b": 2, "a": 1},
        )

        # Same content, different order = same fingerprint
        assert params1.fingerprint() == params2.fingerprint()


class TestAttackResult:
    """Test attack results."""

    def test_create_result(self):
        """Test creating attack result."""
        result = AttackResult(
            success=True,
            plaintext_candidate="HELLO WORLD",
            confidence_scores={"SPY": 0.85, "LINGUIST": 0.78},
            execution_time_seconds=2.5,
        )

        assert result.success is True
        assert result.plaintext_candidate == "HELLO WORLD"
        assert result.confidence_scores["SPY"] == 0.85
        assert result.execution_time_seconds == 2.5

    def test_result_to_dict(self):
        """Test converting result to dictionary."""
        result = AttackResult(
            success=False,
            error_message="Key not found",
        )

        d = result.to_dict()
        assert d["success"] is False
        assert d["error_message"] == "Key not found"


class TestAttackRecord:
    """Test attack records."""

    def test_create_record(self):
        """Test creating attack record."""
        params = AttackParameters("vigenere", {"key": "ABC"})
        result = AttackResult(success=True)

        record = AttackRecord(
            attack_id="test_001",
            timestamp=datetime.now(),
            ciphertext="XYZABC",
            parameters=params,
            result=result,
            agent_involved=["SPY"],
            tags=["k4"],
        )

        assert record.attack_id == "test_001"
        assert record.ciphertext == "XYZABC"
        assert "SPY" in record.agent_involved
        assert "k4" in record.tags

    def test_record_serialization(self):
        """Test record to/from dict."""
        params = AttackParameters("vigenere", {"key": "ABC"})
        result = AttackResult(success=True)

        record = AttackRecord(
            attack_id="test_001",
            timestamp=datetime.now(),
            ciphertext="XYZABC",
            parameters=params,
            result=result,
        )

        d = record.to_dict()
        reconstructed = AttackRecord.from_dict(d)

        assert reconstructed.attack_id == record.attack_id
        assert reconstructed.ciphertext == record.ciphertext


class TestAttackLogger:
    """Test attack logger."""

    def test_logger_initialization(self, tmp_path):
        """Test logger initializes correctly."""
        logger = AttackLogger(log_dir=tmp_path)

        assert logger.log_dir == tmp_path
        assert len(logger.attack_index) == 0
        assert logger.stats["total_attacks"] == 0

    def test_log_attack(self, tmp_path):
        """Test logging an attack."""
        logger = AttackLogger(log_dir=tmp_path)

        params = AttackParameters("vigenere", {"key": "ABC"})
        result = AttackResult(success=False)

        attack_id, is_dup = logger.log_attack(
            ciphertext="XYZABC",
            parameters=params,
            result=result,
        )

        assert attack_id is not None
        assert is_dup is False
        assert logger.stats["total_attacks"] == 1
        assert logger.stats["unique_attacks"] == 1

    def test_duplicate_detection(self, tmp_path):
        """Test duplicate attack detection."""
        logger = AttackLogger(log_dir=tmp_path)

        params = AttackParameters("vigenere", {"key": "ABC"})
        result = AttackResult(success=False)

        # Log first time
        id1, dup1 = logger.log_attack("XYZABC", params, result)
        assert dup1 is False

        # Log again with same parameters
        id2, dup2 = logger.log_attack("XYZABC", params, result)
        assert dup2 is True
        assert id1 == id2  # Same attack ID
        assert logger.stats["duplicates_prevented"] == 1

    def test_is_duplicate_check(self, tmp_path):
        """Test checking if parameters are duplicate."""
        logger = AttackLogger(log_dir=tmp_path)

        params = AttackParameters("vigenere", {"key": "ABC"})

        assert logger.is_duplicate(params) is False

        logger.log_attack("XYZABC", params, AttackResult(success=False))

        assert logger.is_duplicate(params) is True

    def test_get_attack_by_id(self, tmp_path):
        """Test retrieving attack by ID."""
        logger = AttackLogger(log_dir=tmp_path)

        params = AttackParameters("vigenere", {"key": "ABC"})
        result = AttackResult(success=False)

        attack_id, _ = logger.log_attack("XYZABC", params, result)

        retrieved = logger.get_attack(attack_id)
        assert retrieved is not None
        assert retrieved.attack_id == attack_id

    def test_query_by_cipher_type(self, tmp_path):
        """Test querying attacks by cipher type."""
        logger = AttackLogger(log_dir=tmp_path)

        # Log Vigenère attack
        params1 = AttackParameters("vigenere", {"key": "ABC"})
        logger.log_attack("XYZABC", params1, AttackResult(success=False))

        # Log Hill attack
        params2 = AttackParameters("hill", {"matrix": [[1, 2], [3, 4]]})
        logger.log_attack("XYZABC", params2, AttackResult(success=False))

        vigenere_attacks = logger.query_attacks(cipher_type="vigenere")
        assert len(vigenere_attacks) == 1
        assert vigenere_attacks[0].parameters.cipher_type == "vigenere"

    def test_query_success_only(self, tmp_path):
        """Test querying only successful attacks."""
        logger = AttackLogger(log_dir=tmp_path)

        params1 = AttackParameters("vigenere", {"key": "ABC"})
        logger.log_attack("XYZABC", params1, AttackResult(success=False))

        params2 = AttackParameters("vigenere", {"key": "XYZ"})
        logger.log_attack("XYZABC", params2, AttackResult(success=True))

        successful = logger.query_attacks(success_only=True)
        assert len(successful) == 1
        assert successful[0].result.success is True

    def test_query_by_confidence(self, tmp_path):
        """Test querying by minimum confidence."""
        logger = AttackLogger(log_dir=tmp_path)

        params1 = AttackParameters("vigenere", {"key": "ABC"})
        result1 = AttackResult(success=False, confidence_scores={"SPY": 0.3})
        logger.log_attack("XYZABC", params1, result1)

        params2 = AttackParameters("vigenere", {"key": "XYZ"})
        result2 = AttackResult(success=False, confidence_scores={"SPY": 0.8})
        logger.log_attack("XYZABC", params2, result2)

        high_confidence = logger.query_attacks(min_confidence=0.6)
        assert len(high_confidence) == 1
        assert max(high_confidence[0].result.confidence_scores.values()) >= 0.6

    def test_query_by_tags(self, tmp_path):
        """Test querying by tags."""
        logger = AttackLogger(log_dir=tmp_path)

        params1 = AttackParameters("vigenere", {"key": "ABC"})
        logger.log_attack("XYZABC", params1, AttackResult(success=False), tags=["k4", "promising"])

        params2 = AttackParameters("vigenere", {"key": "XYZ"})
        logger.log_attack("XYZABC", params2, AttackResult(success=False), tags=["k4"])

        promising = logger.query_attacks(tags=["k4", "promising"])
        assert len(promising) == 1

    def test_query_limit(self, tmp_path):
        """Test query result limit."""
        logger = AttackLogger(log_dir=tmp_path)

        for i in range(10):
            params = AttackParameters("vigenere", {"key": f"KEY{i}"})
            logger.log_attack("XYZABC", params, AttackResult(success=False))

        limited = logger.query_attacks(limit=5)
        assert len(limited) == 5

    def test_statistics(self, tmp_path):
        """Test getting statistics."""
        logger = AttackLogger(log_dir=tmp_path)

        # Log some attacks
        for i in range(5):
            params = AttackParameters("vigenere", {"key": f"KEY{i}"})
            success = i % 2 == 0
            logger.log_attack("XYZABC", params, AttackResult(success=success))

        stats = logger.get_statistics()
        assert stats["total_attacks"] == 5
        assert stats["successful_attacks"] == 3
        assert 0.0 <= stats["success_rate"] <= 1.0

    def test_export_to_json(self, tmp_path):
        """Test exporting attacks to JSON."""
        logger = AttackLogger(log_dir=tmp_path)

        params = AttackParameters("vigenere", {"key": "ABC"})
        logger.log_attack("XYZABC", params, AttackResult(success=False))

        export_path = logger.export_to_json()
        assert export_path.exists()
        assert export_path.suffix == ".json"

    def test_export_to_latex(self, tmp_path):
        """Test exporting to LaTeX table."""
        logger = AttackLogger(log_dir=tmp_path)

        params = AttackParameters("vigenere", {"key": "ABC"})
        logger.log_attack("XYZABC", params, AttackResult(success=False))

        export_path = logger.export_to_latex_table()
        assert export_path.exists()
        assert export_path.suffix == ".tex"

        # Check content
        content = export_path.read_text()
        assert r"\begin{table}" in content
        assert r"\end{table}" in content

    def test_persistence(self, tmp_path):
        """Test attack log persistence across sessions."""
        # First session
        logger1 = AttackLogger(log_dir=tmp_path)
        params = AttackParameters("vigenere", {"key": "ABC"})
        attack_id, _ = logger1.log_attack("XYZABC", params, AttackResult(success=False))

        # Second session (new logger instance)
        logger2 = AttackLogger(log_dir=tmp_path)

        # Should load previous attacks
        assert logger2.stats["total_attacks"] == 1
        retrieved = logger2.get_attack(attack_id)
        assert retrieved is not None
        assert retrieved.ciphertext == "XYZABC"


class TestIntegration:
    """Integration tests for attack logging."""

    def test_full_workflow(self, tmp_path):
        """Test complete workflow."""
        logger = AttackLogger(log_dir=tmp_path)

        # Log multiple attacks
        for i in range(10):
            params = AttackParameters(
                cipher_type="vigenere",
                key_or_params={"key_length": 8, "key": f"KRYPTOS{i}"},
                crib_text="BERLIN",
                crib_position=5,
            )
            result = AttackResult(
                success=i % 3 == 0,
                confidence_scores={"SPY": 0.5 + i * 0.05},
            )
            logger.log_attack(
                ciphertext="OBKRUOXOGHULBSOLIFBBW...",
                parameters=params,
                result=result,
                agents_involved=["SPY", "LINGUIST"],
                tags=["k4", "vigenere"],
            )

        # Query successful attacks
        successful = logger.query_attacks(success_only=True)
        assert len(successful) > 0

        # Check statistics
        stats = logger.get_statistics()
        assert stats["total_attacks"] == 10

        # Export
        json_path = logger.export_to_json()
        assert json_path.exists()
