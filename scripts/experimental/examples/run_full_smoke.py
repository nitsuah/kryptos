"""Run the demo, a tiny OPS sweep, then SPY extractor and print a short summary.

This is a convenience smoke script for reviewers / CI demo checks.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

# Resolve repository root by walking up until pyproject.toml is found
_here = Path(__file__).resolve()
ROOT = _here
for p in _here.parents:
    if (p / 'pyproject.toml').exists():
        ROOT = p
        break
print(f'[run_full_smoke] repo root resolved to {ROOT}')

steps = [
    (ROOT / 'scripts' / 'examples' / 'run_autopilot_demo.py', 'demo'),
    (ROOT / 'scripts' / 'examples' / 'run_ops_tiny_sweep.py', 'ops'),
    (ROOT / 'scripts' / 'dev' / 'spy_extractor.py', 'spy'),
]

for script, name in steps:
    print(f'--- Running {name} ({script}) ---')
    res = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, check=False)
    print('exit:', res.returncode)
    print(res.stdout)
    if res.stderr:
        print('--- stderr ---')
        print(res.stderr)

# generate condensed report and print a concise summary line
res = subprocess.run(
    [sys.executable, str(ROOT / 'scripts' / 'examples' / 'condensed_tuning_report.py')],
    capture_output=True,
    text=True,
    check=False,
)
if res.returncode == 0:
    # attempt to find the condensed_report.csv in the latest run dir
    run_root = Path('artifacts') / 'tuning_runs'
    runs = sorted([p for p in run_root.iterdir() if p.is_dir()], key=lambda p: p.stat().st_mtime, reverse=True)
    condensed = None
    if runs:
        cand = runs[0] / 'condensed_report.csv'
        if cand.exists():
            condensed = str(cand)

    summary_line = (
        f"SMOKE: demo={steps[0][1]} ops={steps[1][1]} spy={steps[2][1]} report={'ok' if condensed else 'missing'}"
    )
    if condensed:
        summary_line += f" condensed={condensed}"
    print(summary_line)
else:
    print('SMOKE: condensed report generation failed')

print('Smoke run completed.')
