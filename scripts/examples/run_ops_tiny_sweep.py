"""Run a tiny deterministic OPS sweep (crib weight sweep) and print the produced run dir.

This is intentionally small and deterministic so it completes fast in CI/local checks.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SWEEP = ROOT / 'scripts' / 'tuning' / 'crib_weight_sweep.py'
if not SWEEP.exists():
    raise SystemExit('crib_weight_sweep.py not found')

cmd = [sys.executable, str(SWEEP), '--weights', '0.1,0.5']
print('Running tiny OPS sweep:', ' '.join(cmd))
res = subprocess.run(cmd, capture_output=True, text=True)
print('Exit code:', res.returncode)
print(res.stdout)
print(res.stderr, file=sys.stderr)

# try to parse the output line for run_dir
for ln in res.stdout.splitlines():
    if 'Wrote crib weight sweep artifacts to:' in ln:
        run_dir = ln.split(':', 1)[1].strip()
        print('Sweep run dir:', run_dir)
        break
