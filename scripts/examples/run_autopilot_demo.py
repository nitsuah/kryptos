"""Small demo to run the autopilot driver in dry-run mode and print the returned plan.

This script is intentionally conservative: it runs `ask_triumverate.py` as a module via
subprocess to avoid import-time side-effects or package layout assumptions. It writes
outputs to `artifacts/demo/run_<timestamp>/`.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEMO_DIR = ROOT / "artifacts" / "demo" / f"run_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}"
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
        # heuristic: plan dict has 'action' or 'recommendation_text'
        if isinstance(maybe, dict) and ('action' in maybe or 'recommendation_text' in maybe):
            plan = maybe
            break
    except Exception:
        continue

if plan is None:
    print('\nNo structured plan JSON found in stdout. See', DEMO_DIR / 'stdout.txt')
else:
    out = DEMO_DIR / 'plan.json'
    out.write_text(json.dumps(plan, indent=2))
    print('\nSaved plan to', out)
    print(json.dumps(plan, indent=2))
