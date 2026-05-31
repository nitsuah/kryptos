import json


def test_demo_writes_plan():
    from kryptos.examples import run_autopilot_demo

    demo_dir = run_autopilot_demo()
    assert demo_dir.exists()
    plan_file = demo_dir / "plan.json"
    assert plan_file.exists(), "plan.json missing"
    plan = json.loads(plan_file.read_text(encoding="utf-8"))
    assert "recommendation" in plan and "plan" in plan
