"""Meta-Agent Coordinator: High-level orchestration for Kryptos agents.

This coordinator sits above the agent triumvirate (SPY, LINGUIST, K123 Analyzer)
and manages their work allocation, progress monitoring, and result synthesis.

Philosophy: Individual agents are specialists. The meta-coordinator is the project
manager that ensures they work together efficiently toward the common goal.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class AgentStatus(Enum):
    """Status of an agent."""

    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    ERROR = "error"
    COMPLETE = "complete"


class TaskPriority(Enum):
    """Task priority levels."""

    CRITICAL = "critical"  # Must complete before anything else
    HIGH = "high"  # Important, do soon
    MEDIUM = "medium"  # Normal priority
    LOW = "low"  # Can wait
    BACKGROUND = "background"  # Do when nothing else to do


@dataclass
class AgentTask:
    """Task assigned to an agent."""

    task_id: str
    agent_name: str
    task_type: str
    description: str
    priority: TaskPriority
    assigned_at: datetime
    deadline: datetime | None = None
    dependencies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    status: AgentStatus = AgentStatus.IDLE
    result: Any = None
    completed_at: datetime | None = None


@dataclass
class AgentPerformance:
    """Performance metrics for an agent."""

    agent_name: str
    tasks_assigned: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    avg_completion_time: float = 0.0
    success_rate: float = 1.0
    last_activity: datetime | None = None
    total_uptime_hours: float = 0.0


@dataclass
class ResourceAllocation:
    """Resource allocation for agents."""

    cpu_percent: dict[str, float] = field(default_factory=dict)
    memory_mb: dict[str, int] = field(default_factory=dict)
    priority_weights: dict[str, float] = field(default_factory=dict)


class MetaCoordinator:
    """High-level coordinator for all Kryptos agents.

    Responsibilities:
    - Task assignment and scheduling
    - Resource allocation between agents
    - Progress monitoring and reporting
    - Result synthesis from multiple agents
    - Performance tracking and optimization
    - Human-readable status reports
    """

    def __init__(self, cache_dir: Path | None = None):
        """Initialize meta-coordinator.

        Args:
            cache_dir: Directory for storing state and reports
        """
        self.cache_dir = cache_dir or Path("./data/meta_coordinator")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Agent registry
        self.agents: dict[str, AgentPerformance] = {
            "SPY": AgentPerformance("SPY"),
            "LINGUIST": AgentPerformance("LINGUIST"),
            "K123_ANALYZER": AgentPerformance("K123_ANALYZER"),
            "WEB_INTEL": AgentPerformance("WEB_INTEL"),
            "OPS": AgentPerformance("OPS"),
        }

        # Task management
        self.tasks: dict[str, AgentTask] = {}
        self.task_queue: list[AgentTask] = []

        # Resource management
        self.resources = ResourceAllocation(
            cpu_percent={"SPY": 20.0, "LINGUIST": 30.0, "K123_ANALYZER": 10.0, "WEB_INTEL": 10.0, "OPS": 30.0},
            memory_mb={"SPY": 512, "LINGUIST": 1024, "K123_ANALYZER": 256, "WEB_INTEL": 512, "OPS": 256},
            priority_weights={"SPY": 1.0, "LINGUIST": 1.2, "K123_ANALYZER": 0.8, "WEB_INTEL": 0.6, "OPS": 1.5},
        )

        # State tracking
        self.start_time = datetime.now()
        self.total_cycles = 0

    def assign_task(
        self,
        agent_name: str,
        task_type: str,
        description: str,
        priority: TaskPriority = TaskPriority.MEDIUM,
        deadline: datetime | None = None,
        dependencies: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AgentTask:
        """Assign a task to an agent.

        Args:
            agent_name: Name of agent to assign to
            task_type: Type of task
            description: Task description
            priority: Task priority
            deadline: Optional deadline
            dependencies: Task IDs that must complete first
            metadata: Additional task metadata

        Returns:
            Created task
        """
        task_id = f"{agent_name}_{task_type}_{datetime.now().timestamp()}"

        task = AgentTask(
            task_id=task_id,
            agent_name=agent_name,
            task_type=task_type,
            description=description,
            priority=priority,
            assigned_at=datetime.now(),
            deadline=deadline,
            dependencies=dependencies or [],
            metadata=metadata or {},
        )

        self.tasks[task_id] = task
        self.task_queue.append(task)
        self.agents[agent_name].tasks_assigned += 1

        # Sort queue by priority
        self._sort_task_queue()

        return task

    def complete_task(self, task_id: str, result: Any, success: bool = True):
        """Mark a task as complete.

        Args:
            task_id: Task ID
            result: Task result
            success: Whether task succeeded
        """
        if task_id not in self.tasks:
            return

        task = self.tasks[task_id]
        task.completed_at = datetime.now()
        task.result = result
        task.status = AgentStatus.COMPLETE if success else AgentStatus.ERROR

        agent = self.agents[task.agent_name]
        agent.last_activity = datetime.now()

        if success:
            agent.tasks_completed += 1
        else:
            agent.tasks_failed += 1

        # Update success rate
        total = agent.tasks_completed + agent.tasks_failed
        agent.success_rate = agent.tasks_completed / total if total > 0 else 1.0

        # Update avg completion time
        if task.completed_at and task.assigned_at:
            completion_time = (task.completed_at - task.assigned_at).total_seconds()
            if agent.avg_completion_time == 0:
                agent.avg_completion_time = completion_time
            else:
                agent.avg_completion_time = agent.avg_completion_time * 0.9 + completion_time * 0.1

        # Remove from queue
        self.task_queue = [t for t in self.task_queue if t.task_id != task_id]

    def get_next_task(self, agent_name: str) -> AgentTask | None:
        """Get next task for an agent.

        Args:
            agent_name: Agent name

        Returns:
            Next task or None if no tasks available
        """
        for task in self.task_queue:
            if task.agent_name != agent_name:
                continue

            if task.status != AgentStatus.IDLE:
                continue

            # Check dependencies
            if not self._dependencies_met(task):
                continue

            # Found eligible task
            task.status = AgentStatus.WORKING
            return task

        return None

    def reallocate_resources(self, bottleneck_agent: str, boost_percent: float = 10.0):
        """Reallocate resources to prioritize a bottleneck agent.

        Args:
            bottleneck_agent: Agent that needs more resources
            boost_percent: How much to boost (percentage points)
        """
        if bottleneck_agent not in self.resources.cpu_percent:
            return

        # Boost target agent
        old_cpu = self.resources.cpu_percent[bottleneck_agent]
        self.resources.cpu_percent[bottleneck_agent] = min(100.0, old_cpu + boost_percent)

        # Reduce others proportionally
        others = [a for a in self.resources.cpu_percent if a != bottleneck_agent]
        total_reduction = boost_percent
        per_agent_reduction = total_reduction / len(others) if others else 0

        for agent in others:
            self.resources.cpu_percent[agent] = max(5.0, self.resources.cpu_percent[agent] - per_agent_reduction)

    def generate_progress_report(self) -> dict[str, Any]:
        """Generate comprehensive progress report.

        Returns:
            Progress report with agent statuses, task progress, resource usage
        """
        runtime = (datetime.now() - self.start_time).total_seconds() / 3600  # hours

        report = {
            "timestamp": datetime.now().isoformat(),
            "runtime_hours": runtime,
            "total_cycles": self.total_cycles,
            "agents": {},
            "tasks": {
                "total": len(self.tasks),
                "completed": len([t for t in self.tasks.values() if t.status == AgentStatus.COMPLETE]),
                "working": len([t for t in self.tasks.values() if t.status == AgentStatus.WORKING]),
                "queued": len([t for t in self.tasks.values() if t.status == AgentStatus.IDLE]),
                "failed": len([t for t in self.tasks.values() if t.status == AgentStatus.ERROR]),
            },
            "resources": {
                "cpu": self.resources.cpu_percent,
                "memory": self.resources.memory_mb,
            },
        }

        # Agent summaries
        for name, perf in self.agents.items():
            report["agents"][name] = {
                "tasks_assigned": perf.tasks_assigned,
                "tasks_completed": perf.tasks_completed,
                "tasks_failed": perf.tasks_failed,
                "success_rate": f"{perf.success_rate:.2%}",
                "avg_completion_time": f"{perf.avg_completion_time:.1f}s",
                "last_activity": perf.last_activity.isoformat() if perf.last_activity else None,
            }

        return report

    def generate_human_report(self) -> str:
        """Generate human-readable progress report.

        Returns:
            Formatted report string
        """
        report = self.generate_progress_report()
        lines = []

        lines.append("=" * 80)
        lines.append("KRYPTOS META-COORDINATOR STATUS REPORT")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Runtime: {report['runtime_hours']:.2f} hours")
        lines.append(f"Total Cycles: {report['total_cycles']}")
        lines.append("")

        lines.append("## AGENT STATUS")
        lines.append("")
        for name, stats in report["agents"].items():
            status_emoji = (
                "✅"
                if stats["success_rate"] == "100.00%"
                else "⚠️"
                if float(stats["success_rate"].rstrip("%")) > 80
                else "❌"
            )
            lines.append(f"### {status_emoji} {name}")
            lines.append(f"  Tasks: {stats['tasks_completed']}/{stats['tasks_assigned']} completed")
            lines.append(f"  Success Rate: {stats['success_rate']}")
            lines.append(f"  Avg Time: {stats['avg_completion_time']}")
            lines.append("")

        lines.append("## TASK PROGRESS")
        lines.append("")
        tasks = report["tasks"]
        total = tasks["total"]
        completed = tasks["completed"]
        progress = (completed / total * 100) if total > 0 else 0
        lines.append(f"Total: {total} | Completed: {completed} ({progress:.1f}%)")
        lines.append(f"Working: {tasks['working']} | Queued: {tasks['queued']} | Failed: {tasks['failed']}")
        lines.append("")

        lines.append("## RESOURCE ALLOCATION")
        lines.append("")
        for agent, cpu in report["resources"]["cpu"].items():
            memory = report["resources"]["memory"][agent]
            lines.append(f"{agent}: {cpu:.1f}% CPU, {memory}MB RAM")
        lines.append("")

        return "\n".join(lines)

    def synthesize_results(self, candidate_text: str) -> dict[str, Any]:
        """Synthesize results from multiple agents for a candidate.

        Args:
            candidate_text: Candidate plaintext to analyze

        Returns:
            Synthesized analysis from all agents
        """
        # Collect results from different agents
        synthesis = {
            "text": candidate_text,
            "timestamp": datetime.now().isoformat(),
            "agent_scores": {},
            "consensus_score": 0.0,
            "recommendation": "",
            "reasoning": [],
        }

        # This would be populated by actual agent analyses
        # For now, return structure for testing
        return synthesis

    def identify_bottlenecks(self) -> list[str]:
        """Identify bottleneck agents that need more resources.

        Returns:
            List of agent names that are bottlenecks
        """
        bottlenecks = []

        for name, perf in self.agents.items():
            # Check if agent has many queued tasks
            agent_queued = len([t for t in self.task_queue if t.agent_name == name])

            if agent_queued > 5:
                bottlenecks.append(name)
                continue

            # Check if agent has low success rate
            if perf.tasks_assigned > 10 and perf.success_rate < 0.7:
                bottlenecks.append(name)

        return bottlenecks

    def optimize_allocation(self):
        """Optimize resource allocation based on current workload."""
        bottlenecks = self.identify_bottlenecks()

        for agent in bottlenecks:
            self.reallocate_resources(agent, boost_percent=5.0)

    def save_state(self, filepath: Path | None = None):
        """Save coordinator state to file.

        Args:
            filepath: Output file path
        """
        filepath = filepath or (self.cache_dir / "coordinator_state.json")

        state = {
            "start_time": self.start_time.isoformat(),
            "total_cycles": self.total_cycles,
            "agents": {
                name: {
                    "tasks_assigned": perf.tasks_assigned,
                    "tasks_completed": perf.tasks_completed,
                    "tasks_failed": perf.tasks_failed,
                    "avg_completion_time": perf.avg_completion_time,
                    "success_rate": perf.success_rate,
                    "last_activity": perf.last_activity.isoformat() if perf.last_activity else None,
                }
                for name, perf in self.agents.items()
            },
            "resources": {
                "cpu": self.resources.cpu_percent,
                "memory": self.resources.memory_mb,
                "priorities": self.resources.priority_weights,
            },
            "tasks": {
                task_id: {
                    "agent": task.agent_name,
                    "type": task.task_type,
                    "status": task.status.value,
                    "priority": task.priority.value,
                    "assigned_at": task.assigned_at.isoformat(),
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                }
                for task_id, task in self.tasks.items()
            },
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

    def _sort_task_queue(self):
        """Sort task queue by priority."""
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3,
            TaskPriority.BACKGROUND: 4,
        }

        self.task_queue.sort(key=lambda t: (priority_order[t.priority], t.assigned_at))

    def _dependencies_met(self, task: AgentTask) -> bool:
        """Check if task dependencies are met.

        Args:
            task: Task to check

        Returns:
            True if all dependencies completed
        """
        for dep_id in task.dependencies:
            if dep_id not in self.tasks:
                return False
            if self.tasks[dep_id].status != AgentStatus.COMPLETE:
                return False
        return True


def demo_meta_coordinator():
    """Demonstrate meta-coordinator."""
    print("=" * 80)
    print("META-COORDINATOR DEMO")
    print("=" * 80)
    print()

    coord = MetaCoordinator()

    # Assign some tasks
    task1 = coord.assign_task(
        "SPY",
        "analyze_candidate",
        "Analyze candidate #1234",
        priority=TaskPriority.HIGH,
    )

    task2 = coord.assign_task(
        "LINGUIST",
        "validate_candidate",
        "Validate candidate #1234",
        priority=TaskPriority.HIGH,
        dependencies=[task1.task_id],
    )

    coord.assign_task(
        "K123_ANALYZER",
        "check_patterns",
        "Check Sanborn patterns",
        priority=TaskPriority.MEDIUM,
    )

    # Simulate task completion
    coord.complete_task(task1.task_id, {"score": 0.85}, success=True)
    coord.complete_task(task2.task_id, {"score": 0.78}, success=True)

    # Generate report
    print(coord.generate_human_report())

    # Check bottlenecks
    bottlenecks = coord.identify_bottlenecks()
    if bottlenecks:
        print(f"Bottlenecks detected: {', '.join(bottlenecks)}")
    else:
        print("No bottlenecks detected.")


if __name__ == "__main__":
    demo_meta_coordinator()
