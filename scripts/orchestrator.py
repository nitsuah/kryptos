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
REPO_ROOT = os.path.dirname(AGENTS_DIR)
# Only keep artifact logs; avoid creating directories under scripts/ (agents dir)
LOG_DIR_ARTIFACTS = os.path.join(REPO_ROOT, 'artifacts', 'logs')
os.makedirs(LOG_DIR_ARTIFACTS, exist_ok=True)
# prefer a central artifacts state file if the user moved it; otherwise keep agents/state.json
ARTIFACTS_STATE = os.path.join(os.path.dirname(AGENTS_DIR), 'artifacts', 'state.json')
STATE_PATH = ARTIFACTS_STATE if os.path.exists(ARTIFACTS_STATE) else os.path.join(AGENTS_DIR, 'state.json')
LEARNED_MD = os.path.join(AGENTS_DIR, 'LEARNED.md')


def _load_state() -> dict:
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, encoding='utf-8') as fh:
            try:
                return json.load(fh)
            except json.JSONDecodeError:
                return {}
    return {}


def _save_state(state: dict) -> None:
    with open(STATE_PATH, 'w', encoding='utf-8') as fh:
        json.dump(state, fh, indent=2)


def _append_learned(note: str) -> None:
    with open(LEARNED_MD, 'a', encoding='utf-8') as fh:
        fh.write(f"- {datetime.utcnow().isoformat()} {note}\n")


def load_personas() -> dict[str, str]:
    """Load persona prompt texts from the agents directory.
    Returns mapping name->prompt-text.
    """
    mapping = {}
    state = _load_state()
    for fname in ('spy.prompt', 'q.prompt', 'ops.prompt'):
        path = os.path.join(AGENTS_DIR, fname)
        if os.path.exists(path):
            with open(path, encoding='utf-8') as fh:
                text = fh.read()
                # If Q and we have learned facts, append a short comment so Q can adapt
                if fname.startswith('q') and state.get('learned'):
                    notes = ' '.join([f"{n['persona']}:{n['note']}" for n in state.get('learned', [])])
                    text = text + f"\n\n# LEARNED_SUMMARY: {notes}\n"
                mapping[fname.split('.')[0].upper()] = text
    return mapping


def simulate_action(persona_name: str, persona_text: str) -> str:
    """Very small deterministic simulator: returns a short canned response
    based on persona role headers. This is a placeholder for human or LLM-run
    orchestration but is safe and offline.
    """
    # keep persona_text referenced to satisfy linters; future implementations may use it
    _ = persona_text
    if 'SPY' in persona_name:
        # example output may include LEARN: tokens that we can record
        # simulate that SPY sometimes reports zero extractions and that's a learning
        return "SPY_SUMMARY:\tExtracted 0 conservative crib candidates (placeholder). LEARN: no_cribs_found"
    if 'Q' in persona_name:
        return "Q_SUMMARY:\tPrepared tooling scaffold (placeholder). LEARN: tooling_ready"
    if 'OPS' in persona_name:
        return "OPS_SUMMARY:\tNo runs executed yet (placeholder)."
    return "UNKNOWN_PERSONA"


def run_exchange(personas: dict[str, str], rounds: int = 2):
    """Run a simple exchange loop where each persona emits a single line per round.
    Persist logs to `agents/logs/run_<ts>.jsonl`.
    """
    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    fname = f'run_{ts}.jsonl'
    out_path_artifacts = os.path.join(LOG_DIR_ARTIFACTS, fname)
    state = _load_state()
    # write only to artifact logs (avoid creating files under scripts/)
    with open(out_path_artifacts, 'w', encoding='utf-8') as out_art:
        for r in range(rounds):
            for name, text in personas.items():
                act = simulate_action(name, text)
                entry = {'round': r + 1, 'persona': name, 'action': act, 'time': datetime.utcnow().isoformat()}
                line = json.dumps(entry) + '\n'
                out_art.write(line)
                print(entry)
                # parse and persist simple LEARN: or key tokens from action
                if 'LEARN:' in act:
                    learn_text = act.split('LEARN:', 1)[1].strip()
                    state.setdefault('learned', []).append(
                        {'persona': name, 'note': learn_text, 'time': datetime.utcnow().isoformat()},
                    )
                    _append_learned(f"{name}: {learn_text}")
                # some persona outputs use tags like "EXTRACTED" or "PREPARED"; record timestamps
                if any(k in act for k in ('EXTRACTED', 'PREPARED', 'NO_RUNS')):
                    state.setdefault('events', []).append(
                        {'persona': name, 'event': act, 'time': datetime.utcnow().isoformat()},
                    )
    _save_state(state)
    # prefer artifact log path as the canonical returned path
    return out_path_artifacts


if __name__ == '__main__':
    p = load_personas()
    run_exchange(p, rounds=2)
