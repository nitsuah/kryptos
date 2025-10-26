"""Attack logging system for cryptanalysis provenance.

Tracks every attack attempt with full parameters, results, and metadata.
Enables deduplication, coverage analysis, and academic documentation.

Philosophy: "If it's not logged, it never happened. If we can't prove we tried it,
we might waste compute trying it again."
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from kryptos.paths import get_artifacts_root


@dataclass
class AttackParameters:
    """Parameters for a cryptanalysis attack."""

    cipher_type: str  # "vigenere", "hill", "transposition", "hybrid"
    key_or_params: dict[str, Any]  # Cipher-specific parameters
    crib_text: str | None = None
    crib_position: int | None = None
    additional_params: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def fingerprint(self) -> str:
        """Generate unique fingerprint for deduplication.

        Returns:
            SHA256 hash of canonical parameter representation
        """
        canonical = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()


@dataclass
class AttackResult:
    """Result of an attack attempt."""

    success: bool
    plaintext_candidate: str | None = None
    confidence_scores: dict[str, float] = field(default_factory=dict)  # SPY, LINGUIST, etc
    execution_time_seconds: float = 0.0
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class AttackRecord:
    """Complete record of a single attack attempt."""

    attack_id: str
    timestamp: datetime
    ciphertext: str
    parameters: AttackParameters
    result: AttackResult
    agent_involved: list[str] = field(default_factory=list)  # Which agents validated
    tags: list[str] = field(default_factory=list)  # "k4", "vigenere", "promising", etc

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "attack_id": self.attack_id,
            "timestamp": self.timestamp.isoformat(),
            "ciphertext": self.ciphertext,
            "parameters": self.parameters.to_dict(),
            "result": self.result.to_dict(),
            "agents_involved": self.agent_involved,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AttackRecord:
        """Create from dictionary."""
        return cls(
            attack_id=data["attack_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            ciphertext=data["ciphertext"],
            parameters=AttackParameters(**data["parameters"]),
            result=AttackResult(**data["result"]),
            agent_involved=data.get("agents_involved", []),
            tags=data.get("tags", []),
        )


class AttackLogger:
    """Logger for cryptanalysis attack attempts.

    Provides:
    - Structured logging of all attacks
    - Deduplication detection
    - Query interface
    - Export to various formats (JSON, LaTeX, CSV)
    """

    def __init__(self, log_dir: Path | None = None):
        """Initialize attack logger.

        Args:
            log_dir: Directory for storing attack logs
        """
        self.log_dir = log_dir or (get_artifacts_root() / "attack_logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # In-memory index for fast lookups
        self.attack_index: dict[str, AttackRecord] = {}  # fingerprint -> record
        self.chronological_index: list[AttackRecord] = []

        # Statistics
        self.stats = {
            "total_attacks": 0,
            "unique_attacks": 0,
            "duplicates_prevented": 0,
            "successful_attacks": 0,
        }

        # Load existing logs
        self._load_existing_logs()

    def log_attack(
        self,
        ciphertext: str,
        parameters: AttackParameters,
        result: AttackResult,
        agents_involved: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> tuple[str, bool]:
        """Log an attack attempt.

        Args:
            ciphertext: The ciphertext being attacked
            parameters: Attack parameters
            result: Attack result
            agents_involved: List of agents that validated
            tags: Descriptive tags

        Returns:
            Tuple of (attack_id, is_duplicate)
            is_duplicate=True if this exact attack was already tried
        """
        fingerprint = parameters.fingerprint()

        # Check for duplicate
        if fingerprint in self.attack_index:
            self.stats["duplicates_prevented"] += 1
            existing = self.attack_index[fingerprint]
            return existing.attack_id, True

        # Create new record
        attack_id = f"attack_{datetime.now().timestamp()}"
        record = AttackRecord(
            attack_id=attack_id,
            timestamp=datetime.now(),
            ciphertext=ciphertext,
            parameters=parameters,
            result=result,
            agent_involved=agents_involved or [],
            tags=tags or [],
        )

        # Update indexes
        self.attack_index[fingerprint] = record
        self.chronological_index.append(record)

        # Update statistics
        self.stats["total_attacks"] += 1
        self.stats["unique_attacks"] += 1
        if result.success:
            self.stats["successful_attacks"] += 1

        # Persist to disk
        self._save_record(record)

        return attack_id, False

    def is_duplicate(self, parameters: AttackParameters) -> bool:
        """Check if attack with these parameters was already tried.

        Args:
            parameters: Attack parameters to check

        Returns:
            True if attack already logged
        """
        fingerprint = parameters.fingerprint()
        return fingerprint in self.attack_index

    def get_attack(self, attack_id: str) -> AttackRecord | None:
        """Retrieve attack record by ID.

        Args:
            attack_id: Attack ID

        Returns:
            Attack record or None if not found
        """
        for record in self.chronological_index:
            if record.attack_id == attack_id:
                return record
        return None

    def query_attacks(
        self,
        cipher_type: str | None = None,
        success_only: bool = False,
        min_confidence: float | None = None,
        tags: list[str] | None = None,
        limit: int | None = None,
    ) -> list[AttackRecord]:
        """Query attack records with filters.

        Args:
            cipher_type: Filter by cipher type
            success_only: Only return successful attacks
            min_confidence: Minimum confidence score (any agent)
            tags: Filter by tags (must have all)
            limit: Maximum number of results

        Returns:
            List of matching attack records
        """
        results = []

        for record in self.chronological_index:
            # Apply filters
            if cipher_type and record.parameters.cipher_type != cipher_type:
                continue

            if success_only and not record.result.success:
                continue

            if min_confidence is not None:
                max_score = max(record.result.confidence_scores.values(), default=0.0)
                if max_score < min_confidence:
                    continue

            if tags and not all(tag in record.tags for tag in tags):
                continue

            results.append(record)

            if limit and len(results) >= limit:
                break

        return results

    def get_statistics(self) -> dict[str, Any]:
        """Get attack statistics.

        Returns:
            Dictionary of statistics
        """
        return {
            **self.stats,
            "success_rate": self.stats["successful_attacks"] / max(self.stats["total_attacks"], 1),
            "deduplication_rate": self.stats["duplicates_prevented"]
            / max(self.stats["total_attacks"] + self.stats["duplicates_prevented"], 1),
        }

    def export_to_json(self, filepath: Path | None = None) -> Path:
        """Export all attack records to JSON.

        Args:
            filepath: Output file path

        Returns:
            Path to exported file
        """
        filepath = filepath or (self.log_dir / f"attacks_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

        export_data = {
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "total_attacks": len(self.chronological_index),
                "statistics": self.get_statistics(),
            },
            "attacks": [record.to_dict() for record in self.chronological_index],
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2)

        return filepath

    def export_to_latex_table(self, filepath: Path | None = None, limit: int = 50) -> Path:
        """Export attack summary to LaTeX table format.

        Args:
            filepath: Output file path
            limit: Maximum number of attacks to include

        Returns:
            Path to exported file
        """
        filepath = filepath or (self.log_dir / f"attacks_table_{datetime.now().strftime('%Y%m%d')}.tex")

        lines = [
            r"\begin{table}[h]",
            r"\centering",
            r"\begin{tabular}{|l|l|l|c|c|}",
            r"\hline",
            r"\textbf{Timestamp} & \textbf{Cipher} & \textbf{Parameters} & \textbf{Success} & \textbf{Confidence} \\",
            r"\hline",
        ]

        for record in self.chronological_index[:limit]:
            timestamp = record.timestamp.strftime("%Y-%m-%d %H:%M")
            cipher = record.parameters.cipher_type
            params = str(record.parameters.key_or_params)[:30] + "..."
            success = "✓" if record.result.success else "✗"
            confidence = max(record.result.confidence_scores.values(), default=0.0)

            lines.append(f"{timestamp} & {cipher} & {params} & {success} & {confidence:.2f} \\\\")
            lines.append(r"\hline")

        lines.extend(
            [
                r"\end{tabular}",
                r"\caption{Kryptos K4 Attack Provenance Summary}",
                r"\label{tab:attacks}",
                r"\end{table}",
            ],
        )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return filepath

    def _load_existing_logs(self):
        """Load existing attack logs from disk."""
        log_file = self.log_dir / "attack_log.jsonl"
        if not log_file.exists():
            return

        with open(log_file, encoding="utf-8") as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    record = AttackRecord.from_dict(data)
                    fingerprint = record.parameters.fingerprint()

                    self.attack_index[fingerprint] = record
                    self.chronological_index.append(record)

                    self.stats["total_attacks"] += 1
                    self.stats["unique_attacks"] += 1
                    if record.result.success:
                        self.stats["successful_attacks"] += 1
                except Exception:
                    # Skip corrupted lines
                    continue

    def _save_record(self, record: AttackRecord):
        """Save attack record to disk (append to JSONL)."""
        log_file = self.log_dir / "attack_log.jsonl"

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_dict()) + "\n")


def demo_attack_logger():
    """Demonstrate attack logger."""
    print("=" * 80)
    print("ATTACK LOGGER DEMO")
    print("=" * 80)
    print()

    logger = AttackLogger()

    # Log some attacks
    params1 = AttackParameters(
        cipher_type="vigenere",
        key_or_params={"key_length": 8, "key": "KRYPTOS"},
        crib_text="BERLIN",
        crib_position=5,
    )

    result1 = AttackResult(
        success=False,
        plaintext_candidate="XYZABC...",
        confidence_scores={"SPY": 0.3, "LINGUIST": 0.2},
        execution_time_seconds=1.5,
    )

    attack_id, is_dup = logger.log_attack(
        ciphertext="OBKRUOXOGHULBSOLIFBBW...",
        parameters=params1,
        result=result1,
        agents_involved=["SPY", "LINGUIST"],
        tags=["k4", "vigenere"],
    )

    print(f"Logged attack: {attack_id}, duplicate={is_dup}")

    # Try duplicate
    attack_id2, is_dup2 = logger.log_attack(
        ciphertext="OBKRUOXOGHULBSOLIFBBW...",
        parameters=params1,  # Same parameters
        result=result1,
        agents_involved=["SPY"],
        tags=["k4"],
    )

    print(f"Logged attack: {attack_id2}, duplicate={is_dup2}")
    print()

    # Statistics
    print("Statistics:")
    stats = logger.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print()

    # Query
    print("Vigenere attacks:")
    attacks = logger.query_attacks(cipher_type="vigenere", limit=10)
    print(f"  Found {len(attacks)} attacks")


if __name__ == "__main__":
    demo_attack_logger()
