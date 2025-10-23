import json
from pathlib import Path


def test_demo_writes_plan(tmp_path, monkeypatch):
    # Run the example demo script which writes artifacts to artifacts/demo/run_<ts>
    repo = Path(__file__).resolve().parents[1]
    demo_script = repo / 'scripts' / 'experimental' / 'examples' / 'run_autopilot_demo.py'
    assert demo_script.exists(), 'demo script must exist'

    # Run the script
    import subprocess
    import sys

    res = subprocess.run([sys.executable, str(demo_script)], capture_output=True, text=True)
    assert res.returncode == 0, f'demo failed: {res.stderr}'

    # find most recent demo dir
    demo_root = repo / 'artifacts' / 'demo'
    assert demo_root.exists()
    runs = sorted([p for p in demo_root.iterdir() if p.is_dir()], key=lambda p: p.stat().st_mtime, reverse=True)
    assert runs, 'no demo runs found'
    latest = runs[0]
    plan_file = latest / 'plan.json'
    assert plan_file.exists(), f'plan.json missing in {latest}'
    # validate basic structure
    with plan_file.open('r', encoding='utf-8') as fh:
        plan = json.load(fh)
    assert isinstance(plan, dict)
    assert 'persona' in plan or 'action' in plan or 'recommendation_text' in plan
