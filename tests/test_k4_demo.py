from pathlib import Path


def test_run_k4_demo_smoke():
    # import and run demo in-process
    from scripts.demo.run_k4_demo import run_demo

    out = run_demo(limit=5)
    p = Path(out)
    assert p.exists() and p.is_dir()
    # expect a persist_attempt_logs output file (reports/...), at least one file present
    files = list(p.rglob('*'))
    assert files, 'Expected demo artifacts to be written'
