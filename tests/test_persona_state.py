import pytest

# NOTE: This test is for the legacy orchestrator (archived in docs/archive/legacy_orchestrator.py)
# The orchestrator has been superseded by autonomous_coordinator.py
pytestmark = pytest.mark.skip(reason="Legacy orchestrator archived - superseded by autonomous_coordinator.py")


def test_state_load_save_and_append(tmp_path):
    """Legacy test for archived orchestrator - skipped."""
    pass
