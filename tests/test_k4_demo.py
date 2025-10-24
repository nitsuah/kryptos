from pathlib import Path


def test_run_k4_demo_smoke():
    from kryptos.examples import run_demo

    out_path = run_demo(limit=5)
    p = Path(out_path)
    assert p.exists() and p.is_dir()
    files = list(p.rglob('*'))
    assert files, "Expected demo artifacts to be written"
