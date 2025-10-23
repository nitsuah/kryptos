"""Minimal offline orchestrator for persona prompts.

This small harness loads persona prompt files from `agents/` and provides a very
simple simulation API so we can run persona turns and log outputs. It is
intentionally lightweight and offline (no network calls).

Usage example:
    from agents.orchestrator import load_personas, run_exchange
    personas = load_personas()
    run_exchange(personas, rounds=3)

The orchestrator prints and persists logs to `agents/logs/`.
"""

from __future__ import annotations

import json
import os
from datetime import datetime

AGENTS_DIR = os.path.dirname(__file__)
LOG_DIR = os.path.join(AGENTS_DIR, 'logs')
os.makedirs(LOG_DIR, exist_ok=True)


def load_personas() -> dict[str, str]:
    """Load persona prompt texts from the agents directory.
    Returns mapping name->prompt-text.
    """
    mapping = {}
    for fname in ('spy.prompt', 'q.prompt', 'ops.prompt'):
        path = os.path.join(AGENTS_DIR, fname)
        if os.path.exists(path):
            with open(path, encoding='utf-8') as fh:
                mapping[fname.split('.')[0].upper()] = fh.read()
    return mapping


def simulate_action(persona_name: str, persona_text: str) -> str:
    """Very small deterministic simulator: returns a short canned response
    based on persona role headers. This is a placeholder for human or LLM-run
    orchestration but is safe and offline.
    """
    if 'SPY' in persona_name:
        return "SPY_SUMMARY:\tExtracted 0 conservative crib candidates (placeholder)."
    if 'Q' in persona_name:
        return "Q_SUMMARY:\tPrepared tooling scaffold (placeholder)."
    if 'OPS' in persona_name:
        return "OPS_SUMMARY:\tNo runs executed yet (placeholder)."
    return "UNKNOWN_PERSONA"


def run_exchange(personas: dict[str, str], rounds: int = 2):
    """Run a simple exchange loop where each persona emits a single line per round.
    Persist logs to `agents/logs/run_<ts>.jsonl`.
    """
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    out_path = os.path.join(LOG_DIR, f'run_{ts}.jsonl')
    with open(out_path, 'w', encoding='utf-8') as out:
        for r in range(rounds):
            for name, text in personas.items():
                act = simulate_action(name, text)
                entry = {'round': r + 1, 'persona': name, 'action': act, 'time': datetime.utcnow().isoformat()}
                out.write(json.dumps(entry) + '\n')
                print(entry)
    return out_path


if __name__ == '__main__':
    p = load_personas()
    run_exchange(p, rounds=2)
