import csv
import importlib.util
from pathlib import Path

from kryptos.spy import extractor as spy


def test_e2e_autopilot_dryrun(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    orch_path = repo / 'scripts' / 'dev' / 'orchestrator.py'
    spec = importlib.util.spec_from_file_location('orch_e2e', str(orch_path))
    assert spec and spec.loader, 'Failed to create module spec for orchestrator'
    orch = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(orch)  # type: ignore[attr-defined]

    learned = repo / 'agents' / 'LEARNED.md'
    backup = None
    if learned.exists():
        backup = tmp_path / 'LEARNED.bak'
        backup.write_bytes(learned.read_bytes())

    run_dir = orch.ops_run_tuning(weights=[0.1, 0.5, 1.0], dry_run=True)
    assert run_dir, 'ops_run_tuning did not produce a run directory'
    runp = Path(run_dir)
    assert (runp / 'crib_weight_sweep.csv').exists()

    # Create deterministic details file with positive delta if missing
    details_csv = runp / 'weight_0_999_details.csv'
    with details_csv.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(['sample', 'baseline', 'with_cribs', 'delta'])
        writer.writerow(["Observed 'MAGNETIC' anomaly", '0.0', '1.0', '2.5'])

    crib_file = tmp_path / 'cribs.txt'
    crib_file.write_text('MAGNETIC\n', encoding='utf-8')
    matches = spy.extract(min_conf=0.0, cribs_path=crib_file, run_dir=runp)
    assert matches, f'Expected at least one SPY match (files={list(runp.glob("weight_*_details.csv"))})'

    assert learned.exists(), 'agents/LEARNED.md was not created'
    text = learned.read_text(encoding='utf-8')
    assert 'SPY_MATCH' in text, 'No SPY_MATCH entries written to LEARNED.md'

    if backup and backup.exists():
        learned.write_bytes(backup.read_bytes())
    else:
        learned.write_text('', encoding='utf-8')
