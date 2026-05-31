"""Tests for Meta-Agent Coordinator."""

from __future__ import annotations

import json

from kryptos.meta_coordinator import (
    AgentStatus,
    MetaCoordinator,
    TaskPriority,
)


class TestMetaCoordinatorInitialization:
    """Test coordinator initialization."""

    def test_init_default(self, tmp_path):
        """Test default initialization."""
        coord = MetaCoordinator(cache_dir=tmp_path)
        assert coord.cache_dir == tmp_path
        assert len(coord.agents) == 5
        assert "SPY" in coord.agents
        assert "LINGUIST" in coord.agents
        assert len(coord.tasks) == 0
        assert len(coord.task_queue) == 0

    def test_agents_initialized(self, tmp_path):
        """Test all agents initialized correctly."""
        coord = MetaCoordinator(cache_dir=tmp_path)

        for agent_name in ["SPY", "LINGUIST", "K123_ANALYZER", "WEB_INTEL", "OPS"]:
            assert agent_name in coord.agents
            perf = coord.agents[agent_name]
            assert perf.agent_name == agent_name
            assert perf.tasks_assigned == 0
            assert perf.tasks_completed == 0
            assert perf.success_rate == 1.0

    def test_resources_allocated(self, tmp_path):
        """Test resource allocation initialized."""
        coord = MetaCoordinator(cache_dir=tmp_path)

        assert "SPY" in coord.resources.cpu_percent
        assert "LINGUIST" in coord.resources.memory_mb
        assert coord.resources.cpu_percent["SPY"] > 0
        assert coord.resources.memory_mb["LINGUIST"] > 0


class TestTaskAssignment:
    """Test task assignment."""

    def test_assign_basic_task(self, tmp_path):
        """Test assigning a basic task."""
        coord = MetaCoordinator(cache_dir=tmp_path)

        task = coord.assign_task(
            "SPY",
            "analyze",
            "Test analysis",
            priority=TaskPriority.HIGH,
        )

        assert task.agent_name == "SPY"
        assert task.task_type == "analyze"
        assert task.description == "Test analysis"
        assert task.priority == TaskPriority.HIGH
        assert task.status == AgentStatus.IDLE
        assert task.task_id in coord.tasks
        assert task in coord.task_queue

    def test_task_with_dependencies(self, tmp_path):
        """Test task with dependencies."""
        coord = MetaCoordinator(cache_dir=tmp_path)

        task1 = coord.assign_task("SPY", "analyze", "First task")
        task2 = coord.assign_task(
            "LINGUIST",
            "validate",
            "Second task",
            dependencies=[task1.task_id],
        )

        assert task1.task_id in task2.dependencies
        assert not coord._dependencies_met(task2)

        coord.complete_task(task1.task_id, {"score": 0.8}, success=True)
        assert coord._dependencies_met(task2)

    def test_task_with_metadata(self, tmp_path):
        """Test task with custom metadata."""
        coord = MetaCoordinator(cache_dir=tmp_path)

        metadata = {"candidate_id": 1234, "cipher": "K1"}
        task = coord.assign_task(
            "SPY",
            "analyze",
            "Test",
            metadata=metadata,
        )

        assert task.metadata["candidate_id"] == 1234
        assert task.metadata["cipher"] == "K1"

    def test_task_queue_sorting(self, tmp_path):
        """Test task queue sorted by priority."""
        coord = MetaCoordinator(cache_dir=tmp_path)

        coord.assign_task("SPY", "low", "Low priority", priority=TaskPriority.LOW)
        coord.assign_task("SPY", "critical", "Critical", priority=TaskPriority.CRITICAL)
        coord.assign_task("SPY", "medium", "Medium", priority=TaskPriority.MEDIUM)

        # Critical should be first
        assert coord.task_queue[0].priority == TaskPriority.CRITICAL
        assert coord.task_queue[-1].priority == TaskPriority.LOW


class TestTaskCompletion:
    """Test task completion."""

    def test_complete_successful_task(self, tmp_path):
        """Test completing a successful task."""
        coord = MetaCoordinator(cache_dir=tmp_path)

        task = coord.assign_task("SPY", "analyze", "Test")
        result = {"score": 0.85}

        coord.complete_task(task.task_id, result, success=True)

        assert task.status == AgentStatus.COMPLETE
        assert task.result == result
        assert task.completed_at is not None
        assert coord.agents["SPY"].tasks_completed == 1
        assert coord.agents["SPY"].tasks_failed == 0
        assert task not in coord.task_queue

    def test_complete_failed_task(self, tmp_path):
        """Test completing a failed task."""
        coord = MetaCoordinator(cache_dir=tmp_path)

        task = coord.assign_task("SPY", "analyze", "Test")
        coord.complete_task(task.task_id, None, success=False)

        assert task.status == AgentStatus.ERROR
        assert coord.agents["SPY"].tasks_completed == 0
        assert coord.agents["SPY"].tasks_failed == 1

    def test_success_rate_calculation(self, tmp_path):
        """Test success rate calculated correctly."""
        coord = MetaCoordinator(cache_dir=tmp_path)

        # Complete 3 successful, 1 failed
        for i in range(3):
            task = coord.assign_task("SPY", "test", f"Task {i}")
            coord.complete_task(task.task_id, {}, success=True)

        task = coord.assign_task("SPY", "test", "Failed task")
        coord.complete_task(task.task_id, {}, success=False)

        # Success rate should be 75% (3/4)
        assert coord.agents["SPY"].success_rate == 0.75

    def test_avg_completion_time(self, tmp_path):
        """Test average completion time tracked."""
        coord = MetaCoordinator(cache_dir=tmp_path)

        task = coord.assign_task("SPY", "test", "Task")
        coord.complete_task(task.task_id, {}, success=True)

        # Completion time should be >= 0 (might be 0 if very fast)
        assert coord.agents["SPY"].avg_completion_time >= 0


class TestTaskRetrieval:
    """Test task retrieval."""

    def test_get_next_task(self, tmp_path):
        """Test getting next task for agent."""
        coord = MetaCoordinator(cache_dir=tmp_path)

        coord.assign_task("SPY", "task1", "First")
        coord.assign_task("SPY", "task2", "Second")
        coord.assign_task("LINGUIST", "task3", "Third")

        next_task = coord.get_next_task("SPY")
        assert next_task is not None
        assert next_task.agent_name == "SPY"
        assert next_task.status == AgentStatus.WORKING

    def test_get_next_task_respects_dependencies(self, tmp_path):
        """Test task retrieval respects dependencies."""
        coord = MetaCoordinator(cache_dir=tmp_path)

        task1 = coord.assign_task("SPY", "first", "First")
        task2 = coord.assign_task("SPY", "second", "Second", dependencies=[task1.task_id])

        # Should get task1 first
        next_task = coord.get_next_task("SPY")
        assert next_task is not None
        assert next_task.task_id == task1.task_id

        # Should not get task2 yet (dependency not met)
        next_task = coord.get_next_task("SPY")
        assert next_task is None

        # Complete task1
        coord.complete_task(task1.task_id, {}, success=True)

        # Now should get task2
        next_task = coord.get_next_task("SPY")
        assert next_task is not None
        assert next_task.task_id == task2.task_id

    def test_get_next_task_no_tasks(self, tmp_path):
        """Test getting next task when none available."""
        coord = MetaCoordinator(cache_dir=tmp_path)

        next_task = coord.get_next_task("SPY")
        assert next_task is None


class TestResourceAllocation:
    """Test resource allocation."""

    def test_reallocate_resources(self, tmp_path):
        """Test reallocating resources to bottleneck."""
        coord = MetaCoordinator(cache_dir=tmp_path)

        old_cpu = coord.resources.cpu_percent["SPY"]
        coord.reallocate_resources("SPY", boost_percent=10.0)

        # SPY should get more CPU
        assert coord.resources.cpu_percent["SPY"] > old_cpu
        # Others should get less
        assert coord.resources.cpu_percent["LINGUIST"] < 30.0

    def test_identify_bottlenecks_queued_tasks(self, tmp_path):
        """Test identifying bottlenecks from queue size."""
        coord = MetaCoordinator(cache_dir=tmp_path)

        # Assign many tasks to SPY
        for i in range(10):
            coord.assign_task("SPY", "task", f"Task {i}")

        bottlenecks = coord.identify_bottlenecks()
        assert "SPY" in bottlenecks

    def test_identify_bottlenecks_low_success_rate(self, tmp_path):
        """Test identifying bottlenecks from low success rate."""
        coord = MetaCoordinator(cache_dir=tmp_path)

        # Many failed tasks
        for i in range(15):
            task = coord.assign_task("LINGUIST", "task", f"Task {i}")
            success = i % 3 != 0  # 2/3 success rate
            coord.complete_task(task.task_id, {}, success=success)

        bottlenecks = coord.identify_bottlenecks()
        assert "LINGUIST" in bottlenecks

    def test_optimize_allocation(self, tmp_path):
        """Test automatic optimization."""
        coord = MetaCoordinator(cache_dir=tmp_path)

        # Create bottleneck
        for i in range(10):
            coord.assign_task("K123_ANALYZER", "task", f"Task {i}")

        old_cpu = coord.resources.cpu_percent["K123_ANALYZER"]
        coord.optimize_allocation()

        # Should boost K123_ANALYZER
        assert coord.resources.cpu_percent["K123_ANALYZER"] > old_cpu


class TestReporting:
    """Test progress reporting."""

    def test_generate_progress_report(self, tmp_path):
        """Test generating progress report."""
        coord = MetaCoordinator(cache_dir=tmp_path)

        # Add some tasks
        task1 = coord.assign_task("SPY", "test", "Task 1")
        coord.assign_task("LINGUIST", "test", "Task 2")
        coord.complete_task(task1.task_id, {}, success=True)

        report = coord.generate_progress_report()

        assert "timestamp" in report
        assert "agents" in report
        assert "tasks" in report
        assert "resources" in report
        assert report["tasks"]["total"] == 2
        assert report["tasks"]["completed"] == 1
        assert report["agents"]["SPY"]["tasks_completed"] == 1

    def test_generate_human_report(self, tmp_path):
        """Test generating human-readable report."""
        coord = MetaCoordinator(cache_dir=tmp_path)

        task = coord.assign_task("SPY", "test", "Task")
        coord.complete_task(task.task_id, {}, success=True)

        report = coord.generate_human_report()

        assert "META-COORDINATOR STATUS REPORT" in report
        assert "AGENT STATUS" in report
        assert "TASK PROGRESS" in report
        assert "RESOURCE ALLOCATION" in report
        assert "SPY" in report

    def test_report_includes_emojis(self, tmp_path):
        """Test report includes status emojis."""
        coord = MetaCoordinator(cache_dir=tmp_path)

        # All successful
        for i in range(5):
            task = coord.assign_task("SPY", "test", f"Task {i}")
            coord.complete_task(task.task_id, {}, success=True)

        report = coord.generate_human_report()
        assert "✅" in report  # Should have checkmark for 100% success


class TestStatePersistence:
    """Test state persistence."""

    def test_save_state(self, tmp_path):
        """Test saving state to file."""
        coord = MetaCoordinator(cache_dir=tmp_path)

        task = coord.assign_task("SPY", "test", "Task")
        coord.complete_task(task.task_id, {}, success=True)

        filepath = tmp_path / "state.json"
        coord.save_state(filepath)

        assert filepath.exists()

        with open(filepath, encoding="utf-8") as f:
            state = json.load(f)

        assert "agents" in state
        assert "tasks" in state
        assert "resources" in state
        assert state["agents"]["SPY"]["tasks_completed"] == 1


class TestSynthesis:
    """Test result synthesis."""

    def test_synthesize_results(self, tmp_path):
        """Test synthesizing results from multiple agents."""
        coord = MetaCoordinator(cache_dir=tmp_path)

        result = coord.synthesize_results("BETWEEN SUBTLE SHADING")

        assert "text" in result
        assert "agent_scores" in result
        assert "consensus_score" in result
        assert "recommendation" in result
        assert result["text"] == "BETWEEN SUBTLE SHADING"


class TestIntegration:
    """Integration tests."""

    def test_full_workflow(self, tmp_path):
        """Test complete workflow."""
        coord = MetaCoordinator(cache_dir=tmp_path)

        # Assign tasks with dependencies
        task1 = coord.assign_task(
            "SPY",
            "analyze",
            "Analyze candidate #1",
            priority=TaskPriority.HIGH,
        )

        task2 = coord.assign_task(
            "LINGUIST",
            "validate",
            "Validate candidate #1",
            priority=TaskPriority.HIGH,
            dependencies=[task1.task_id],
        )

        task3 = coord.assign_task(
            "K123_ANALYZER",
            "check_patterns",
            "Check patterns",
            priority=TaskPriority.MEDIUM,
        )

        # Process tasks
        next_task = coord.get_next_task("SPY")
        assert next_task is not None
        assert next_task.task_id == task1.task_id
        coord.complete_task(task1.task_id, {"score": 0.8}, success=True)

        # Now LINGUIST can work
        next_task = coord.get_next_task("LINGUIST")
        assert next_task is not None
        assert next_task.task_id == task2.task_id
        coord.complete_task(task2.task_id, {"score": 0.75}, success=True)

        # K123 can work in parallel
        next_task = coord.get_next_task("K123_ANALYZER")
        assert next_task is not None
        assert next_task.task_id == task3.task_id
        coord.complete_task(task3.task_id, {"patterns": []}, success=True)

        # Check final state
        report = coord.generate_progress_report()
        assert report["tasks"]["completed"] == 3
        assert report["tasks"]["total"] == 3

    def test_bottleneck_handling(self, tmp_path):
        """Test handling bottlenecks automatically."""
        coord = MetaCoordinator(cache_dir=tmp_path)

        # Create bottleneck
        for i in range(8):
            coord.assign_task("WEB_INTEL", "search", f"Search {i}")

        # Optimize
        old_cpu = coord.resources.cpu_percent["WEB_INTEL"]
        coord.optimize_allocation()
        new_cpu = coord.resources.cpu_percent["WEB_INTEL"]

        assert new_cpu > old_cpu

        # Generate report
        report = coord.generate_human_report()
        assert "WEB_INTEL" in report
