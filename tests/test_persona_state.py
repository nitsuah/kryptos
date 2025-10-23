import os
from pathlib import Path

from scripts.dev import orchestrator as orch


def test_state_load_save_and_append(tmp_path: Path):
    # Use a temporary agents dir and artifacts dir
    agents_dir = tmp_path / "agents"
    artifacts_dir = tmp_path / "artifacts"
    agents_dir.mkdir()
    (agents_dir / "LEARNED.md").write_text("")

    # Patch orchestrator paths
    old_agents = orch.AGENTS_DIR
    old_state_path = orch.STATE_PATH
    old_learned = orch.LEARNED_MD

    try:
        orch.AGENTS_DIR = str(agents_dir)
        orch.STATE_PATH = str(artifacts_dir / "state.json")
        orch.LEARNED_MD = str(agents_dir / "LEARNED.md")

        # Initial state should be empty
        s = orch._load_state()
        assert isinstance(s, dict)

        # Append two learn notes
        orch._append_learned("TEST1: note1")
        orch._append_learned("TEST2: note2")

        # Save a state dict (ensure artifacts dir exists)
        os.makedirs(os.path.dirname(orch.STATE_PATH), exist_ok=True)
        state = {"learned": [{"persona": "SPY", "note": "x"}]}
        orch._save_state(state)

        # Load back
        loaded = orch._load_state()
        assert loaded.get("learned")
        assert loaded["learned"][0]["persona"] == "SPY"

        # Ensure LEARNED.md appended lines
        txt = (agents_dir / "LEARNED.md").read_text()
        assert "TEST1: note1" in txt
        assert "TEST2: note2" in txt
    finally:
        orch.AGENTS_DIR = old_agents
        orch.STATE_PATH = old_state_path
        orch.LEARNED_MD = old_learned
