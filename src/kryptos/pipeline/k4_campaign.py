"""End-to-end K4 cryptanalysis campaign orchestrator."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from kryptos.ciphers import vigenere_decrypt
from kryptos.k4.transposition_analysis import (
    solve_columnar_permutation_exhaustive,
    solve_columnar_permutation_simulated_annealing_multi_start,
)
from kryptos.k4.vigenere_key_recovery import recover_key_by_frequency
from kryptos.log_setup import setup_logging
from kryptos.pipeline.attack_executor import AttackExecutor
from kryptos.pipeline.attack_generator import AttackGenerator
from kryptos.pipeline.validator import PlaintextValidator
from kryptos.provenance.attack_log import AttackLogger
from kryptos.provenance.search_space import SearchSpaceTracker


@dataclass
class CampaignResult:
    campaign_id: str
    start_time: datetime
    end_time: datetime
    total_attacks: int
    successful_attacks: int
    best_candidates: list[dict[str, Any]] = field(default_factory=list)
    coverage_report: dict[str, Any] = field(default_factory=dict)
    statistics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "campaign_id": self.campaign_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_seconds": (self.end_time - self.start_time).total_seconds(),
            "total_attacks": self.total_attacks,
            "successful_attacks": self.successful_attacks,
            "success_rate": self.successful_attacks / self.total_attacks if self.total_attacks > 0 else 0.0,
            "best_candidates": self.best_candidates,
            "coverage_report": self.coverage_report,
            "statistics": self.statistics,
        }


class K4CampaignOrchestrator:
    def __init__(
        self,
        workspace_dir: Path | None = None,
        log_level: str = "INFO",
    ):
        self.workspace_dir = workspace_dir or Path("./data/k4_campaign")
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.log = setup_logging(level=log_level, logger_name="kryptos.k4_campaign")

        self.attack_logger = AttackLogger(log_dir=self.workspace_dir / "attack_logs")
        self.search_space = SearchSpaceTracker(cache_dir=self.workspace_dir / "search_space")
        self.attack_generator = AttackGenerator(
            attack_logger=self.attack_logger,
            log_level=log_level,
        )
        self.attack_executor = AttackExecutor(log_dir=self.workspace_dir / "executor_logs")

        config_path = Path(__file__).parent.parent.parent.parent / "config" / "config.json"
        with open(config_path) as f:
            config = json.load(f)

        self.cribs = config.get("cribs", [])
        self.validator = PlaintextValidator(
            known_cribs=self.cribs,
            min_dictionary_score=0.5,
            min_confidence=0.7,
        )

    def execute_vigenere_attack(
        self,
        ciphertext: str,
        key_length: int,
    ) -> tuple[str | None, float]:
        try:
            candidate_keys = recover_key_by_frequency(ciphertext, key_length, top_n=1)
            if not candidate_keys:
                return None, 0.0

            best_key = candidate_keys[0]
            plaintext = vigenere_decrypt(ciphertext, best_key)
            confidence = 0.5
            return plaintext, confidence

        except Exception as e:
            self.log.warning(f"Vigenère attack failed for key_length={key_length}: {e}")
            return None, 0.0

    def execute_transposition_attack(
        self,
        ciphertext: str,
        period: int,
        method: str = "simulated_annealing",
    ) -> tuple[str | None, float]:
        try:
            if method == "exhaustive" and period <= 8:
                permutation, score = solve_columnar_permutation_exhaustive(ciphertext, period)
            else:
                permutation, score = solve_columnar_permutation_simulated_annealing_multi_start(ciphertext, period)

            plaintext = ciphertext

            return plaintext, score
        except Exception as e:
            self.log.warning(f"Transposition attack failed: {e}")
            return None, 0.0

    def execute_attack(
        self,
        ciphertext: str,
        attack_spec: Any,
    ) -> tuple[str | None, float]:
        cipher_type = attack_spec.parameters.cipher_type
        params = attack_spec.parameters.key_or_params

        if cipher_type == "vigenere":
            return self.execute_vigenere_attack(ciphertext, params.get("key_length"))
        elif cipher_type == "transposition":
            return self.execute_transposition_attack(
                ciphertext,
                params.get("period"),
                params.get("method", "simulated_annealing"),
            )
        else:
            return None, 0.0

    def run_campaign(
        self,
        ciphertext: str,
        max_attacks: int = 100,
        max_time_seconds: float | None = None,
    ) -> CampaignResult:
        campaign_id = f"k4_campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        start_time = datetime.now()

        attack_queue = self.attack_generator.generate_comprehensive_queue(
            ciphertext=ciphertext,
            max_total=max_attacks,
        )

        successful_attacks = 0
        best_candidates = []
        i = 0

        for i, attack_spec in enumerate(attack_queue, 1):
            if max_time_seconds:
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed > max_time_seconds:
                    break

            plaintext, confidence = self.execute_attack(ciphertext, attack_spec)

            if plaintext:
                validation = self.validator.validate(plaintext)
                if validation.is_valid:
                    successful_attacks += 1
                    best_candidates.append(
                        {
                            "attack_number": i,
                            "cipher_type": attack_spec.parameters.cipher_type,
                            "parameters": attack_spec.parameters.key_or_params,
                            "plaintext": plaintext[:100],
                            "confidence": validation.confidence,
                            "validation": validation.to_dict(),
                        },
                    )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        coverage_report = self.search_space.get_coverage_report()

        statistics = {
            "attacks_executed": i,
            "attacks_planned": len(attack_queue),
            "successful_validations": successful_attacks,
            "duration_seconds": duration,
            "attacks_per_second": i / duration if duration > 0 else 0,
        }

        result = CampaignResult(
            campaign_id=campaign_id,
            start_time=start_time,
            end_time=end_time,
            total_attacks=i,
            successful_attacks=successful_attacks,
            best_candidates=sorted(best_candidates, key=lambda x: x["confidence"], reverse=True),
            coverage_report=coverage_report,
            statistics=statistics,
        )

        result_path = self.workspace_dir / f"{campaign_id}_result.json"
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, indent=2)

        return result

    def print_summary(self, result: CampaignResult) -> None:
        print()
        print("=" * 80)
        print("K4 CAMPAIGN SUMMARY")
        print("=" * 80)
        print()
        print(f"Campaign ID: {result.campaign_id}")
        print(f"Duration: {result.statistics['duration_seconds']:.1f}s")
        print(f"Attacks executed: {result.total_attacks}")
        print(f"Valid candidates: {result.successful_attacks}")
        print(f"Success rate: {result.statistics['attacks_per_second']:.1f} attacks/sec")
        print()

        if result.best_candidates:
            print("TOP 5 CANDIDATES:")
            print()
            for i, candidate in enumerate(result.best_candidates[:5], 1):
                print(f"{i}. Confidence: {candidate['confidence']:.1%}")
                print(f"   Cipher: {candidate['cipher_type']}")
                print(f"   Parameters: {candidate['parameters']}")
                print(f"   Plaintext: {candidate['plaintext']}...")
                print()
        else:
            print("No valid candidates found.")
            print()

        print("=" * 80)


def demo_k4_campaign():
    import tempfile

    print("=" * 80)
    print("K4 CAMPAIGN DEMO")
    print("=" * 80)
    print()

    config_path = Path(__file__).parent.parent.parent.parent / "config" / "config.json"
    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)

    k4_cipher = config["ciphertexts"]["K4"]

    workspace = Path(tempfile.mkdtemp())
    orchestrator = K4CampaignOrchestrator(workspace_dir=workspace)

    result = orchestrator.run_campaign(
        ciphertext=k4_cipher,
        max_attacks=20,
        max_time_seconds=60,
    )

    orchestrator.print_summary(result)


if __name__ == "__main__":
    demo_k4_campaign()
