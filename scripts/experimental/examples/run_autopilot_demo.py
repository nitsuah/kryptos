"""Small demo to run the autopilot driver in dry-run mode and print the returned plan.

This script is intentionally conservative: it runs `ask_triumverate.py` as a module via
subprocess to avoid import-time side-effects or package layout assumptions. It writes
outputs to `artifacts/demo/run_<timestamp>/`.
"""

from __future__ import annotations

import json
import random
import string
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Detect repository root by searching upwards for pyproject.toml sentinel
_here = Path(__file__).resolve()
ROOT = _here
for _parent in _here.parents:
    if (_parent / 'pyproject.toml').exists():
        ROOT = _parent
        break
_ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
_rand = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(4))
DEMO_DIR = ROOT / "artifacts" / "demo" / f"run_{_ts}_{_rand}"
DEMO_DIR.mkdir(parents=True, exist_ok=True)

cmd = [sys.executable, str(ROOT / "scripts" / "dev" / "ask_triumverate.py"), "--dry-run"]
print('Running autopilot demo (dry-run):', ' '.join(cmd))
proc = subprocess.run(cmd, capture_output=True, text=True)
print('Exit code:', proc.returncode)
# Save stdout/stderr for review
(DEMO_DIR / 'stdout.txt').write_text(proc.stdout)
(DEMO_DIR / 'stderr.txt').write_text(proc.stderr)

# Try to parse a JSON plan from stdout if present
plan = None
for line in proc.stdout.splitlines():
    line = line.strip()
    if not line:
        continue
    try:
        maybe = json.loads(line)
        if isinstance(maybe, dict) and ('action' in maybe or 'recommendation_text' in maybe):
            plan = maybe
            break
    except json.JSONDecodeError:
        continue

out = DEMO_DIR / 'plan.json'
if plan is None:
    # Fallback minimal structure with expected keys for tests
    plan = {
        'recommendation_text': 'No structured plan found (dry-run fallback)',
        'action': None,
        'persona': 'AUTOPILOT',
        'status': 'no-plan',
        'timestamp': _ts,
    }
    print('\nNo structured plan JSON found; writing fallback plan.json')
out.write_text(json.dumps(plan, indent=2))
print('\nSaved plan to', out)
print(json.dumps(plan, indent=2))
