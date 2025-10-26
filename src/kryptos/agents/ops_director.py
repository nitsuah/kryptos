"""OPS v2.0: LLM-Powered Strategic Director for K4 Cryptanalysis.

This is the "brain" that coordinates all agents and makes high-level strategic
decisions about which attacks to pursue, when to pivot, and how to allocate resources.

Philosophy: Don't just throw compute at the problem - think strategically about
what's working, what's not, and what we should try next.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from kryptos.paths import get_artifacts_root


class StrategyAction(Enum):
    CONTINUE = "continue"
    BOOST = "boost"
    REDUCE = "reduce"
    PIVOT = "pivot"
    STOP = "stop"
    START_NEW = "start_new"
    EMERGENCY_STOP = "emergency_stop"


@dataclass
class AttackProgress:
    attack_type: str
    attempts: int
    best_score: float
    time_elapsed_hours: float
    cpu_allocation: float
    improvement_rate: float
    last_improvement: datetime
    confidence_trend: list[float]


@dataclass
class AgentInsight:
    agent_name: str
    timestamp: datetime
    category: str
    description: str
    confidence: float
    actionable: bool
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategicDecision:
    timestamp: datetime
    action: StrategyAction
    reasoning: str
    affected_attacks: list[str]
    resource_changes: dict[str, float]
    success_criteria: str
    review_in_hours: float
    confidence: float


class OpsStrategicDirector:
    """LLM-powered strategic director for cryptanalysis operations.

    Key responsibilities:
    - Monitor attack progress and detect stagnation
    - Synthesize insights from multiple agents
    - Recommend strategic pivots when stuck
    - Optimize resource allocation
    - Generate human-readable reports
    - Update project roadmap based on discoveries
    """

    def __init__(self, llm_provider: str = "openai", model: str = "gpt-4", cache_dir: Path | None = None):
        self.llm_provider = llm_provider
        self.model = model
        self.cache_dir = cache_dir or (get_artifacts_root() / "ops_strategy")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.llm_client = self._init_llm_client()

        self.active_attacks: dict[str, AttackProgress] = {}

        self.recent_insights: list[AgentInsight] = []

        self.decision_history: list[StrategicDecision] = []
        self.strategy_kb = self._load_strategy_kb()

    def analyze_situation(self, force_decision: bool = False) -> StrategicDecision | None:
        situation = self._gather_situation_report()

        if not force_decision and not self._needs_decision(situation):
            return None

        decision = self._make_strategic_decision(situation)
        self.decision_history.append(decision)
        self._save_decision(decision)

        return decision

    def synthesize_agent_insights(self, insights: list[AgentInsight]) -> dict[str, Any]:
        by_category = {}
        for insight in insights:
            if insight.category not in by_category:
                by_category[insight.category] = []
            by_category[insight.category].append(insight)

        synthesis = {
            "timestamp": datetime.now(),
            "insight_count": len(insights),
            "categories": list(by_category.keys()),
            "key_findings": [],
            "recommendations": [],
            "confidence": 0.0,
        }

        linguistic_insights = by_category.get("linguistic", [])
        pattern_insights = by_category.get("pattern", [])

        if len(linguistic_insights) >= 2 or (linguistic_insights and pattern_insights):
            synthesis["key_findings"].append(
                {
                    "type": "linguistic_structure",
                    "description": "Multiple agents detect coherent linguistic patterns",
                    "confidence": sum(i.confidence for i in linguistic_insights + pattern_insights)
                    / len(linguistic_insights + pattern_insights),
                },
            )
            synthesis["recommendations"].append(
                "Focus on linguistically-validated candidates - they score higher on multiple metrics",
            )

        intel_insights = by_category.get("external_intel", [])
        if intel_insights:
            new_cribs = [i.metadata.get("cribs", []) for i in intel_insights if "cribs" in i.metadata]
            if new_cribs:
                synthesis["key_findings"].append(
                    {
                        "type": "new_cribs",
                        "description": f"Discovered {len(new_cribs)} new potential cribs",
                        "cribs": new_cribs,
                    },
                )
                synthesis["recommendations"].append("Integrate new cribs into known-plaintext attacks")

        synthesis["confidence"] = min(1.0, len(synthesis["key_findings"]) * 0.3)

        return synthesis

    def generate_daily_report(self) -> str:
        report_lines = [
            "# K4 CRYPTANALYSIS - STRATEGIC REPORT",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Executive Summary",
        ]

        total_attempts = sum(a.attempts for a in self.active_attacks.values())
        best_score = max((a.best_score for a in self.active_attacks.values()), default=0.0)

        report_lines.extend(
            [
                f"- **Total attempts (24h):** {total_attempts:,}",
                f"- **Best candidate score:** {best_score:.4f}",
                f"- **Active attacks:** {len(self.active_attacks)}",
                f"- **Recent insights:** {len(self.recent_insights)}",
                "",
                "## Active Attacks",
            ],
        )

        for name, progress in self.active_attacks.items():
            hours_since_improvement = (datetime.now() - progress.last_improvement).total_seconds() / 3600

            status_emoji = "🟢" if hours_since_improvement < 2 else "🟡" if hours_since_improvement < 6 else "🔴"

            report_lines.extend(
                [
                    f"### {status_emoji} {name}",
                    f"- Attempts: {progress.attempts:,}",
                    f"- Best score: {progress.best_score:.4f}",
                    f"- CPU allocation: {progress.cpu_allocation:.1f}%",
                    f"- Time since improvement: {hours_since_improvement:.1f}h",
                    f"- Improvement rate: {progress.improvement_rate:.4f}/hour",
                    "",
                ],
            )

        if self.recent_insights:
            report_lines.extend(["## Agent Insights (Last 24h)", ""])
            for insight in self.recent_insights[-10:]:
                report_lines.append(
                    f"- **[{insight.agent_name}]** {insight.description} " f"(confidence: {insight.confidence:.2f})",
                )
            report_lines.append("")

        if self.decision_history:
            report_lines.extend(["## Strategic Decisions", ""])
            for decision in self.decision_history[-5:]:
                report_lines.extend(
                    [
                        f"### {decision.action.value.upper()} - {decision.timestamp.strftime('%H:%M')}",
                        f"**Reasoning:** {decision.reasoning}",
                        f"**Success Criteria:** {decision.success_criteria}",
                        "",
                    ],
                )

        return "\n".join(report_lines)

    def update_attack_progress(self, attack_type: str, attempts: int, best_score: float):
        if attack_type not in self.active_attacks:
            self.active_attacks[attack_type] = AttackProgress(
                attack_type=attack_type,
                attempts=attempts,
                best_score=best_score,
                time_elapsed_hours=0.0,
                cpu_allocation=0.0,
                improvement_rate=0.0,
                last_improvement=datetime.now(),
                confidence_trend=[best_score],
            )
        else:
            progress = self.active_attacks[attack_type]
            progress.attempts = attempts

            if best_score > progress.best_score:
                progress.best_score = best_score
                progress.last_improvement = datetime.now()

            progress.confidence_trend.append(best_score)
            if len(progress.confidence_trend) > 100:
                progress.confidence_trend = progress.confidence_trend[-100:]

    def register_agent_insight(self, insight: AgentInsight):
        self.recent_insights.append(insight)

        if len(self.recent_insights) > 1000:
            self.recent_insights = self.recent_insights[-1000:]

    def _init_llm_client(self) -> Any:
        if self.llm_provider == "local":
            return None

        if self.llm_provider == "openai":
            try:
                import openai

                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    print("Warning: OPENAI_API_KEY not set, falling back to rule-based logic")
                    return None
                openai.api_key = api_key
                return openai
            except ImportError:
                print("Warning: openai package not installed, falling back to rule-based logic")
                return None

        if self.llm_provider == "anthropic":
            try:
                import anthropic

                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    print("Warning: ANTHROPIC_API_KEY not set, falling back to rule-based logic")
                    return None
                return anthropic.Anthropic(api_key=api_key)
            except ImportError:
                print("Warning: anthropic package not installed, falling back to rule-based logic")
                return None

        return None

    def _call_llm(self, prompt: str) -> str | None:
        if not self.llm_client:
            return None

        try:
            if self.llm_provider == "openai":
                response = self.llm_client.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=1000,
                )
                return response.choices[0].message.content

            if self.llm_provider == "anthropic":
                response = self.llm_client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.content[0].text

        except Exception as e:
            print(f"Warning: LLM call failed ({e}), falling back to rule-based logic")
            return None

        return None

    def _build_strategic_prompt(self, situation: dict[str, Any]) -> str:
        prompt_parts = [
            "You are OPS, the Strategic Director for Kryptos K4 cryptanalysis.",
            "Your role is to analyze progress, synthesize agent insights, and make strategic decisions.",
            "",
            "## CURRENT SITUATION",
            "",
            "### Active Attacks",
        ]

        for attack_name, attack_data in situation["active_attacks"].items():
            hours_since = (datetime.now() - attack_data["last_improvement"]).total_seconds() / 3600
            prompt_parts.extend(
                [
                    f"**{attack_name}:**",
                    f"- Attempts: {attack_data['attempts']:,}",
                    f"- Best score: {attack_data['best_score']:.4f}",
                    f"- Hours since improvement: {hours_since:.1f}",
                    f"- Improvement rate: {attack_data['improvement_rate']:.4f}/hour",
                    "",
                ],
            )

        if situation["recent_insights"]:
            prompt_parts.extend(["### Recent Agent Insights", ""])
            for insight in situation["recent_insights"][-10:]:
                prompt_parts.append(
                    f"- [{insight['agent_name']}] {insight['description']} "
                    f"(confidence: {insight['confidence']:.2f})",
                )
            prompt_parts.append("")

        prompt_parts.extend(
            [
                "## YOUR TASK",
                "",
                "Analyze the situation and make a strategic decision:",
                "- CONTINUE: Keep current approach (steady progress)",
                "- BOOST: Increase resources to current approach (showing promise)",
                "- REDUCE: Decrease resources (diminishing returns)",
                "- PIVOT: Switch to different approach (stagnant)",
                "- STOP: Abandon approach entirely (no progress)",
                "- START_NEW: Begin new attack type (insights suggest new direction)",
                "",
                "## RESPONSE FORMAT",
                "",
                "Provide your response as JSON:",
                "{",
                '  "action": "CONTINUE|BOOST|REDUCE|PIVOT|STOP|START_NEW",',
                '  "reasoning": "Brief explanation of your decision",',
                '  "affected_attacks": ["attack_name"],',
                '  "resource_changes": {"attack_name": 0.5},  // 0.0-1.0 CPU allocation',
                '  "success_criteria": "What success looks like for this decision",',
                '  "review_in_hours": 2.0,',
                '  "confidence": 0.8  // 0.0-1.0',
                "}",
            ],
        )

        return "\n".join(prompt_parts)

    def _parse_llm_decision(self, llm_response: str) -> StrategicDecision | None:
        try:
            json_start = llm_response.find("{")
            json_end = llm_response.rfind("}") + 1

            if json_start == -1 or json_end == 0:
                return None

            json_str = llm_response[json_start:json_end]
            data = json.loads(json_str)

            return StrategicDecision(
                timestamp=datetime.now(),
                action=StrategyAction(data["action"].lower()),
                reasoning=data["reasoning"],
                affected_attacks=data["affected_attacks"],
                resource_changes=data["resource_changes"],
                success_criteria=data["success_criteria"],
                review_in_hours=data["review_in_hours"],
                confidence=data["confidence"],
            )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Warning: Failed to parse LLM response ({e})")
            return None

    def _gather_situation_report(self) -> dict[str, Any]:
        return {
            "timestamp": datetime.now(),
            "active_attacks": {name: vars(progress) for name, progress in self.active_attacks.items()},
            "recent_insights": [vars(i) for i in self.recent_insights[-50:]],
            "decision_history": [vars(d) for d in self.decision_history[-10:]],
        }

    def _needs_decision(self, situation: dict[str, Any]) -> bool:
        for attack_data in situation["active_attacks"].values():
            hours_since = (datetime.now() - attack_data["last_improvement"]).total_seconds() / 3600
            if hours_since > 6:
                return True

        actionable_insights = [i for i in self.recent_insights if i.actionable]
        if len(actionable_insights) >= 3:
            return True

        return False

    def _make_strategic_decision(self, situation: dict[str, Any]) -> StrategicDecision:
        if self.llm_client:
            prompt = self._build_strategic_prompt(situation)
            llm_response = self._call_llm(prompt)

            if llm_response:
                llm_decision = self._parse_llm_decision(llm_response)
                if llm_decision:
                    return llm_decision

        return self._rule_based_decision(situation)

    def _rule_based_decision(self, situation: dict[str, Any]) -> StrategicDecision:
        for attack_name, attack_data in situation["active_attacks"].items():
            hours_since = (datetime.now() - attack_data["last_improvement"]).total_seconds() / 3600

            if hours_since > 8:
                reasoning = (
                    f"{attack_name} has not improved in {hours_since:.1f} hours. " f"Time to try different approach."
                )
                return StrategicDecision(
                    timestamp=datetime.now(),
                    action=StrategyAction.PIVOT,
                    reasoning=reasoning,
                    affected_attacks=[attack_name],
                    resource_changes={attack_name: 0.0},
                    success_criteria="New approach should improve score within 4 hours",
                    review_in_hours=4.0,
                    confidence=0.8,
                )

        return StrategicDecision(
            timestamp=datetime.now(),
            action=StrategyAction.CONTINUE,
            reasoning="All attacks making steady progress",
            affected_attacks=list(situation["active_attacks"].keys()),
            resource_changes={},
            success_criteria="Maintain improvement rate",
            review_in_hours=2.0,
            confidence=0.6,
        )

    def _load_strategy_kb(self) -> dict[str, Any]:
        kb_file = self.cache_dir / "strategy_kb.json"
        if kb_file.exists():
            with open(kb_file) as f:
                return json.load(f)
        return {"successful_strategies": [], "failed_strategies": [], "lessons_learned": []}

    def _save_decision(self, decision: StrategicDecision):
        decisions_file = self.cache_dir / "decisions.jsonl"
        with open(decisions_file, "a") as f:
            f.write(json.dumps(vars(decision), default=str) + "\n")


def demo_ops_director():
    print("=" * 80)
    print("OPS v2.0 STRATEGIC DIRECTOR DEMO")
    print("=" * 80)
    print()

    ops = OpsStrategicDirector(llm_provider="local", model="rule-based")

    ops.update_attack_progress("hill_3x3", attempts=1_000_000, best_score=0.15)
    ops.update_attack_progress("vigenere_period_14", attempts=500_000, best_score=0.28)

    ops.register_agent_insight(
        AgentInsight(
            agent_name="SPY",
            timestamp=datetime.now(),
            category="pattern",
            description="Found rhyme pattern in candidate #1247",
            confidence=0.85,
            actionable=True,
            metadata={"candidate_id": 1247},
        ),
    )

    ops.register_agent_insight(
        AgentInsight(
            agent_name="LINGUIST",
            timestamp=datetime.now(),
            category="linguistic",
            description="Detected iambic meter in candidate #1247",
            confidence=0.78,
            actionable=True,
        ),
    )

    print("📊 Analyzing current situation...")
    decision = ops.analyze_situation(force_decision=True)

    if decision:
        print(f"\n🎯 STRATEGIC DECISION: {decision.action.value.upper()}")
        print(f"Reasoning: {decision.reasoning}")
        print(f"Confidence: {decision.confidence:.2f}")
        print(f"Success Criteria: {decision.success_criteria}")
        print()

    print("\n" + "=" * 80)
    print("📈 DAILY REPORT")
    print("=" * 80)
    report = ops.generate_daily_report()
    print(report)


if __name__ == "__main__":
    demo_ops_director()
