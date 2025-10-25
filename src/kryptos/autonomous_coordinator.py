"""Autonomous Coordination Layer for K4 Cryptanalysis.

This module bridges the new agent system (SPY v2.0, OPS Strategic Director,
K123 Pattern Analyzer, Web Intelligence) with the existing autopilot infrastructure.

Philosophy: "Human expertise to build the system, machine endurance to run it."
The coordinator enables 24/7 autonomous operation with minimal human intervention.

Architecture:
    ┌──────────────────────────────────────────────┐
    │      Autonomous Coordinator (this file)      │
    │  - Main control loop                         │
    │  - Agent messaging                           │
    │  - Progress tracking                         │
    │  - Strategic decision execution              │
    └──────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
    │   SPY   │    │   OPS   │    │    Q    │
    │  v2.0   │    │Strategic│    │Research │
    │         │    │Director │    │Assistant│
    └─────────┘    └─────────┘    └─────────┘
         │               │               │
    ┌────▼────────────────▼───────────────▼─────┐
    │         Attack Execution Layer             │
    │  (autopilot.py, triumverate, cracking)     │
    └────────────────────────────────────────────┘

Key Components:
- CoordinationMessage: Inter-agent communication
- AutonomousState: Persistent state across sessions
- AutonomousCoordinator: Main orchestration loop

Usage:
    coordinator = AutonomousCoordinator()
    coordinator.run_autonomous_loop(max_hours=24)
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from kryptos.agents.k123_analyzer import K123Analyzer
from kryptos.agents.ops_director import (
    AgentInsight,
    AttackProgress,
    OpsStrategicDirector,
    StrategyAction,
)
from kryptos.agents.spy_nlp import SpyNLP
from kryptos.agents.spy_web_intel import SpyWebIntel
from kryptos.autopilot import run_exchange
from kryptos.logging import setup_logging
from kryptos.paths import get_artifacts_root, get_logs_dir


class MessageType(Enum):
    """Types of coordination messages."""

    # Agent → Coordinator
    INSIGHT = "insight"  # Agent discovered something interesting
    ALERT = "alert"  # Urgent finding requiring attention
    STATUS = "status"  # Routine status update
    REQUEST = "request"  # Agent needs something

    # Coordinator → Agent
    DIRECTIVE = "directive"  # Coordinator instructs agent
    QUERY = "query"  # Coordinator asks for information
    CONFIG = "config"  # Configuration update


@dataclass
class CoordinationMessage:
    """Message passed between coordinator and agents."""

    msg_type: MessageType
    source: str  # Agent name or 'COORDINATOR'
    target: str  # Agent name or 'COORDINATOR'
    timestamp: datetime
    priority: int  # 1-10, 10 = highest
    content: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize message to dictionary."""
        return {
            "msg_type": self.msg_type.value,
            "source": self.source,
            "target": self.target,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority,
            "content": self.content,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CoordinationMessage:
        """Deserialize message from dictionary."""
        return cls(
            msg_type=MessageType(data["msg_type"]),
            source=data["source"],
            target=data["target"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            priority=data["priority"],
            content=data["content"],
            metadata=data.get("metadata", {}),
        )


@dataclass
class AutonomousState:
    """Persistent state for autonomous operation."""

    session_start: datetime
    total_runtime_hours: float
    coordination_cycles: int
    active_attacks: dict[str, AttackProgress]
    agent_insights: list[AgentInsight]
    strategic_decisions: list[dict[str, Any]]
    k123_patterns_loaded: bool
    web_intel_last_check: datetime | None
    last_ops_decision: datetime | None
    best_score_ever: float
    total_candidates_tested: int
    checkpoints: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize state to dictionary."""
        return {
            "session_start": self.session_start.isoformat(),
            "total_runtime_hours": self.total_runtime_hours,
            "coordination_cycles": self.coordination_cycles,
            "active_attacks": {
                k: {
                    "attack_type": v.attack_type,
                    "attempts": v.attempts,
                    "best_score": v.best_score,
                    "time_elapsed_hours": v.time_elapsed_hours,
                    "cpu_allocation": v.cpu_allocation,
                    "improvement_rate": v.improvement_rate,
                    "last_improvement": v.last_improvement.isoformat(),
                    "confidence_trend": v.confidence_trend,
                }
                for k, v in self.active_attacks.items()
            },
            "agent_insights": [
                {
                    "agent_name": ins.agent_name,
                    "timestamp": ins.timestamp.isoformat(),
                    "category": ins.category,
                    "description": ins.description,
                    "confidence": ins.confidence,
                    "actionable": ins.actionable,
                    "metadata": ins.metadata,
                }
                for ins in self.agent_insights
            ],
            "strategic_decisions": self.strategic_decisions,
            "k123_patterns_loaded": self.k123_patterns_loaded,
            "web_intel_last_check": self.web_intel_last_check.isoformat() if self.web_intel_last_check else None,
            "last_ops_decision": self.last_ops_decision.isoformat() if self.last_ops_decision else None,
            "best_score_ever": self.best_score_ever,
            "total_candidates_tested": self.total_candidates_tested,
            "checkpoints": self.checkpoints,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AutonomousState:
        """Deserialize state from dictionary."""
        return cls(
            session_start=datetime.fromisoformat(data["session_start"]),
            total_runtime_hours=data["total_runtime_hours"],
            coordination_cycles=data["coordination_cycles"],
            active_attacks={
                k: AttackProgress(
                    attack_type=v["attack_type"],
                    attempts=v["attempts"],
                    best_score=v["best_score"],
                    time_elapsed_hours=v["time_elapsed_hours"],
                    cpu_allocation=v["cpu_allocation"],
                    improvement_rate=v["improvement_rate"],
                    last_improvement=datetime.fromisoformat(v["last_improvement"]),
                    confidence_trend=v["confidence_trend"],
                )
                for k, v in data["active_attacks"].items()
            },
            agent_insights=[
                AgentInsight(
                    agent_name=ins["agent_name"],
                    timestamp=datetime.fromisoformat(ins["timestamp"]),
                    category=ins["category"],
                    description=ins["description"],
                    confidence=ins["confidence"],
                    actionable=ins["actionable"],
                    metadata=ins.get("metadata", {}),
                )
                for ins in data["agent_insights"]
            ],
            strategic_decisions=data["strategic_decisions"],
            k123_patterns_loaded=data["k123_patterns_loaded"],
            web_intel_last_check=(
                datetime.fromisoformat(data["web_intel_last_check"]) if data.get("web_intel_last_check") else None
            ),
            last_ops_decision=(
                datetime.fromisoformat(data["last_ops_decision"]) if data.get("last_ops_decision") else None
            ),
            best_score_ever=data["best_score_ever"],
            total_candidates_tested=data["total_candidates_tested"],
            checkpoints=data.get("checkpoints", []),
        )


class AutonomousCoordinator:
    """Main coordinator for autonomous K4 cryptanalysis.

    Orchestrates multiple agents, executes strategic decisions, tracks progress,
    and enables 24/7 operation without human intervention.

    Key Features:
    - Load K123 patterns to guide attacks
    - Run OPS strategic analysis periodically
    - Collect web intelligence for new cribs
    - Validate candidates with SPY v2.0
    - Execute autopilot loops for attack execution
    - Persist state across sessions
    - Generate progress reports
    """

    def __init__(
        self,
        state_path: Path | None = None,
        ops_cycle_minutes: float = 0.5,
        web_intel_check_hours: float = 0.5,
    ):
        """Initialize autonomous coordinator.

        Args:
            state_path: Path to persistent state file
            ops_cycle_minutes: How often to run OPS strategic analysis (default: 30 sec)
            web_intel_check_hours: How often to check for new web intel (default: 30 min)
        """
        self.logger = setup_logging(logger_name="kryptos.autonomous")
        self.state_path = state_path or (get_artifacts_root() / "autonomous_state.json")
        self.ops_cycle_minutes = ops_cycle_minutes
        self.web_intel_check_hours = web_intel_check_hours

        # Initialize agents
        self.ops_director = OpsStrategicDirector()
        self.spy_nlp = SpyNLP()
        self.web_intel = SpyWebIntel()
        self.k123_analyzer = K123Analyzer()

        # Message queues
        self.inbox: list[CoordinationMessage] = []
        self.outbox: list[CoordinationMessage] = []

        # Load or initialize state
        self.state = self._load_state()

        self.logger.info("Autonomous coordinator initialized")
        self.logger.info(f"OPS cycle: every {ops_cycle_minutes} minutes")
        self.logger.info(f"Web intel check: every {web_intel_check_hours} hours")

    def _load_state(self) -> AutonomousState:
        """Load state from disk or create new."""
        if self.state_path.exists():
            try:
                data = json.loads(self.state_path.read_text(encoding="utf-8"))
                self.logger.info(f"Loaded state from {self.state_path}")
                return AutonomousState.from_dict(data)
            except (json.JSONDecodeError, ValueError, KeyError) as exc:
                self.logger.warning(f"Failed to load state: {exc}, starting fresh")

        # Create new state
        return AutonomousState(
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

    def _save_state(self) -> None:
        """Persist state to disk."""
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            self.state_path.write_text(
                json.dumps(self.state.to_dict(), indent=2),
                encoding="utf-8",
            )
            self.logger.debug(f"State saved to {self.state_path}")
        except (OSError, ValueError) as exc:
            self.logger.error(f"Failed to save state: {exc}")

    def create_checkpoint(
        self,
        attack_type: str,
        search_space_position: dict[str, Any],
        tested_keys: list[str] | None = None,
        promising_candidates: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Create a checkpoint for an attack's progress.

        This enables resuming exactly where we left off after interruption.

        Args:
            attack_type: Type of attack (e.g., 'vigenere_northeast')
            search_space_position: Current position in search space
                (e.g., {'key_length': 8, 'key_index': 12345, 'crib_position': 5})
            tested_keys: List of keys already tested (optional, can be large)
            promising_candidates: Candidates worth revisiting
            metadata: Additional checkpoint metadata
        """
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "attack_type": attack_type,
            "search_space_position": search_space_position,
            "tested_keys_count": len(tested_keys) if tested_keys else 0,
            "promising_candidates": promising_candidates or [],
            "metadata": metadata or {},
        }

        # Add to state checkpoints
        self.state.checkpoints.append(checkpoint)

        # Keep only last 50 checkpoints to prevent bloat
        if len(self.state.checkpoints) > 50:
            self.state.checkpoints = self.state.checkpoints[-50:]

        # Save tested keys to separate file if provided (can be huge)
        if tested_keys:
            self._save_tested_keys(attack_type, tested_keys)

        self._save_state()
        self.logger.info(
            f"💾 Checkpoint created for {attack_type} "
            f"(position: {search_space_position}, tested: {len(tested_keys) if tested_keys else 0})",
        )

    def _save_tested_keys(self, attack_type: str, tested_keys: list[str]) -> None:
        """Save tested keys to separate file to keep state file small."""
        keys_dir = self.state_path.parent / "tested_keys"
        keys_dir.mkdir(parents=True, exist_ok=True)

        keys_file = keys_dir / f"{attack_type}_tested_keys.json"
        try:
            # Load existing keys if file exists
            existing_keys = set()
            if keys_file.exists():
                existing_keys = set(json.loads(keys_file.read_text(encoding="utf-8")))

            # Add new keys
            all_keys = existing_keys.union(set(tested_keys))

            # Save back
            keys_file.write_text(json.dumps(list(all_keys), indent=2), encoding="utf-8")
            self.logger.debug(f"Saved {len(all_keys)} tested keys for {attack_type}")
        except (OSError, ValueError) as exc:
            self.logger.error(f"Failed to save tested keys: {exc}")

    def load_tested_keys(self, attack_type: str) -> set[str]:
        """Load previously tested keys for an attack.

        Args:
            attack_type: Type of attack

        Returns:
            Set of tested keys (empty if none found)
        """
        keys_file = self.state_path.parent / "tested_keys" / f"{attack_type}_tested_keys.json"
        if not keys_file.exists():
            return set()

        try:
            keys = json.loads(keys_file.read_text(encoding="utf-8"))
            self.logger.info(f"Loaded {len(keys)} previously tested keys for {attack_type}")
            return set(keys)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            self.logger.error(f"Failed to load tested keys: {exc}")
            return set()

    def get_latest_checkpoint(self, attack_type: str) -> dict[str, Any] | None:
        """Get the most recent checkpoint for an attack type.

        Args:
            attack_type: Type of attack

        Returns:
            Checkpoint dict or None if no checkpoint found
        """
        # Find most recent checkpoint for this attack type
        matching_checkpoints = [cp for cp in reversed(self.state.checkpoints) if cp["attack_type"] == attack_type]

        if not matching_checkpoints:
            return None

        checkpoint = matching_checkpoints[0]
        self.logger.info(
            f"📍 Found checkpoint for {attack_type} "
            f"from {checkpoint['timestamp']} "
            f"at position {checkpoint['search_space_position']}",
        )
        return checkpoint

    def _load_k123_patterns(self) -> None:
        """Load K123 pattern analysis to inform attack strategy."""
        if self.state.k123_patterns_loaded:
            self.logger.debug("K123 patterns already loaded")
            return

        self.logger.info("Loading K123 patterns...")
        patterns = self.k123_analyzer.analyze_all()

        # Extract actionable cribs from patterns
        cribs = []
        for pattern in patterns:
            if pattern.category == "THEME" and pattern.confidence >= 0.85:
                # Extract words from evidence (evidence is list)
                words = [w.strip() for item in pattern.evidence for w in str(item).split() if w.strip()]
                cribs.extend(words[:10])  # Top 10 words per theme

        # Send insight to OPS
        insight = AgentInsight(
            agent_name="K123_ANALYZER",
            timestamp=datetime.now(),
            category="pattern",
            description=f"Loaded {len(patterns)} patterns from K1-K3 analysis",
            confidence=0.95,
            actionable=True,
            metadata={"pattern_count": len(patterns), "cribs_extracted": len(cribs)},
        )
        self.state.agent_insights.append(insight)
        self.ops_director.register_agent_insight(insight)

        self.state.k123_patterns_loaded = True
        self.logger.info(f"K123 patterns loaded: {len(patterns)} patterns, {len(cribs)} cribs")

    def _check_web_intelligence(self) -> None:
        """Check for new web intelligence (cribs, Sanborn interviews, etc)."""
        now = datetime.now()
        if self.state.web_intel_last_check:
            hours_since = (now - self.state.web_intel_last_check).total_seconds() / 3600
            if hours_since < self.web_intel_check_hours:
                return

        self.logger.info("Gathering web intelligence...")
        try:
            intel_items = self.web_intel.gather_intelligence(max_sources=3, max_age_days=30)

            if intel_items:
                # Send insight to OPS
                top_cribs = self.web_intel.get_top_cribs(n=5)
                insight = AgentInsight(
                    agent_name="WEB_INTEL",
                    timestamp=now,
                    category="external_intel",
                    description=f"Found {len(intel_items)} intel items, {len(top_cribs)} high-confidence cribs",
                    confidence=0.80,
                    actionable=True,
                    metadata={"intel_count": len(intel_items), "top_cribs": [c.text for c in top_cribs]},
                )
                self.state.agent_insights.append(insight)
                self.ops_director.register_agent_insight(insight)

                self.logger.info(f"Web intel: {len(intel_items)} items, top cribs: {[c.text for c in top_cribs]}")

        except Exception as exc:
            self.logger.warning(f"Web intel check failed: {exc}")

        self.state.web_intel_last_check = now

    def _run_ops_strategic_analysis(self) -> None:
        """Run OPS strategic analysis and execute decisions."""
        now = datetime.now()
        if self.state.last_ops_decision:
            minutes_since = (now - self.state.last_ops_decision).total_seconds() / 60
            if minutes_since < self.ops_cycle_minutes:
                return

        self.logger.info("Running OPS strategic analysis...")

        # Update attack progress (placeholder - would read from actual attack runs)
        # For now, simulate progress
        if "vigenere_northeast" not in self.state.active_attacks:
            self.state.active_attacks["vigenere_northeast"] = AttackProgress(
                attack_type="vigenere_northeast",
                attempts=0,
                best_score=0.0,
                time_elapsed_hours=0.0,
                cpu_allocation=0.5,
                improvement_rate=0.0,
                last_improvement=now,
                confidence_trend=[],
            )

        for _attack_name, progress in self.state.active_attacks.items():
            self.ops_director.update_attack_progress(progress)

        # Get strategic decision
        decision = self.ops_director.analyze_situation()

        # Log decision
        decision_dict = {
            "timestamp": decision.timestamp.isoformat(),
            "action": decision.action.value,
            "reasoning": decision.reasoning,
            "affected_attacks": decision.affected_attacks,
            "resource_changes": decision.resource_changes,
            "success_criteria": decision.success_criteria,
            "confidence": decision.confidence,
        }
        self.state.strategic_decisions.append(decision_dict)
        self.state.last_ops_decision = now

        self.logger.info(f"🎯 OPS Decision: {decision.action.value}")
        self.logger.info(f"   Reasoning: {decision.reasoning}")
        self.logger.info(f"   Confidence: {decision.confidence:.2f}")

        # Execute decision
        self._execute_strategic_decision(decision.action, decision_dict)

    def _execute_strategic_decision(self, action: StrategyAction, decision: dict[str, Any]) -> None:
        """Execute a strategic decision from OPS.

        Args:
            action: The strategy action to execute
            decision: Full decision dictionary with details
        """
        if action == StrategyAction.CONTINUE:
            self.logger.info("✅ Continuing current approach")
            # Let autopilot continue running

        elif action == StrategyAction.PIVOT:
            self.logger.info("🔄 Pivoting to new approach")
            # Trigger autopilot with new plan
            plan = f"OPS recommends PIVOT: {decision['reasoning']}"
            run_exchange(plan_text=plan, autopilot=True)

        elif action == StrategyAction.BOOST:
            self.logger.info("⚡ Boosting current attack")
            # Increase resources (placeholder - would adjust CPU allocation)

        elif action == StrategyAction.STOP:
            self.logger.info("⛔ Stopping unproductive attack")
            # Stop attack (placeholder - would kill process)

        elif action == StrategyAction.START_NEW:
            self.logger.info("🚀 Starting new attack type")
            # Start new attack (placeholder - would launch new process)

        elif action == StrategyAction.EMERGENCY_STOP:
            self.logger.warning("🚨 EMERGENCY STOP - Human intervention needed")
            # Alert and pause (placeholder - would send notification)

    def _generate_progress_report(self) -> str:
        """Generate human-readable progress report."""
        report = self.ops_director.generate_daily_report()

        # Add coordination-specific stats
        runtime_hours = (datetime.now() - self.state.session_start).total_seconds() / 3600
        report += "\n## Coordination Statistics\n\n"
        report += f"- Session runtime: {runtime_hours:.2f} hours\n"
        report += f"- Coordination cycles: {self.state.coordination_cycles}\n"
        report += f"- K123 patterns: {'✅ Loaded' if self.state.k123_patterns_loaded else '❌ Not loaded'}\n"
        report += f"- Web intel checks: {len([i for i in self.state.agent_insights if i.agent_name == 'WEB_INTEL'])}\n"
        report += f"- Best score ever: {self.state.best_score_ever:.4f}\n"
        report += f"- Total candidates tested: {self.state.total_candidates_tested:,}\n"

        return report

    def _coordination_cycle(self) -> None:
        """Run one coordination cycle."""
        cycle_start = datetime.now()

        # 1. Load K123 patterns if not already loaded
        if not self.state.k123_patterns_loaded:
            self._load_k123_patterns()

        # 2. Check web intelligence periodically
        self._check_web_intelligence()

        # 3. Run OPS strategic analysis
        self._run_ops_strategic_analysis()

        # 4. Run autopilot exchange
        self.logger.info("Running autopilot exchange...")
        try:
            run_exchange(autopilot=True)
        except Exception as exc:
            self.logger.error(f"Autopilot exchange failed: {exc}")

        # 5. Update state
        self.state.coordination_cycles += 1
        cycle_duration = (datetime.now() - cycle_start).total_seconds() / 3600
        self.state.total_runtime_hours += cycle_duration

        # 6. Create checkpoint every 10 cycles
        if self.state.coordination_cycles % 10 == 0:
            for attack_name, attack_progress in self.state.active_attacks.items():
                self.create_checkpoint(
                    attack_type=attack_name,
                    search_space_position={
                        "attempts": attack_progress.attempts,
                        "best_score": attack_progress.best_score,
                        "time_elapsed_hours": attack_progress.time_elapsed_hours,
                    },
                    promising_candidates=[],
                    metadata={"cycle": self.state.coordination_cycles},
                )

        # 7. Save state
        self._save_state()

        self.logger.info(
            f"Coordination cycle {self.state.coordination_cycles} complete ({cycle_duration * 60:.1f} min)",
        )

    def run_autonomous_loop(
        self,
        max_hours: float | None = None,
        max_cycles: int | None = None,
        cycle_interval_minutes: int = 5,
    ) -> None:
        """Run autonomous coordination loop.

        Args:
            max_hours: Maximum runtime in hours (None = infinite)
            max_cycles: Maximum coordination cycles (None = infinite)
            cycle_interval_minutes: Time between cycles
        """
        self.logger.info("🚀 Starting autonomous coordination loop")
        self.logger.info(f"   Max runtime: {max_hours if max_hours else '∞'} hours")
        self.logger.info(f"   Max cycles: {max_cycles if max_cycles else '∞'}")
        self.logger.info(f"   Cycle interval: {cycle_interval_minutes} minutes")

        start_time = datetime.now()

        try:
            while True:
                # Check termination conditions
                runtime_hours = (datetime.now() - start_time).total_seconds() / 3600
                if max_hours and runtime_hours >= max_hours:
                    self.logger.info(f"⏰ Max runtime reached ({runtime_hours:.2f} hours)")
                    break
                if max_cycles and self.state.coordination_cycles >= max_cycles:
                    self.logger.info(f"🔄 Max cycles reached ({self.state.coordination_cycles})")
                    break

                # Run coordination cycle
                self._coordination_cycle()

                # Generate and save progress report
                report = self._generate_progress_report()
                report_path = get_logs_dir() / f"progress_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                report_path.write_text(report, encoding="utf-8")
                self.logger.info(f"📊 Progress report: {report_path}")

                # Sleep until next cycle
                self.logger.info(f"💤 Sleeping {cycle_interval_minutes} minutes until next cycle")
                time.sleep(cycle_interval_minutes * 60)

        except KeyboardInterrupt:
            self.logger.info("⚠️  Keyboard interrupt - shutting down gracefully")
        except Exception as exc:
            self.logger.exception(f"❌ Fatal error in coordination loop: {exc}")
        finally:
            # Final state save
            self._save_state()
            runtime_hours = (datetime.now() - start_time).total_seconds() / 3600
            self.logger.info(
                f"🏁 Autonomous coordination stopped after {runtime_hours:.2f} hours, "
                f"{self.state.coordination_cycles} cycles",
            )


def main() -> None:
    """Demo/test autonomous coordination."""
    coordinator = AutonomousCoordinator(
        ops_cycle_minutes=15,  # OPS analysis every 15 minutes for demo
        web_intel_check_hours=1,  # Web intel check every hour for demo
    )

    # Run for 1 hour with 5-minute cycles (12 cycles total)
    coordinator.run_autonomous_loop(
        max_hours=1.0,
        cycle_interval_minutes=5,
    )


if __name__ == "__main__":
    main()
