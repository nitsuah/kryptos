"""Conservative SPY extractor: scan latest tuning run CSVs and extract quoted tokens
that appear in samples and in the docs crib list (sanborn_crib_candidates.txt).

Writes short summaries to `agents/LEARNED.md` and prints a small report.
"""

import csv
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO / 'agents'
LEARNED = AGENTS_DIR / 'LEARNED.md'
CRIBS = REPO / 'docs' / 'sources' / 'sanborn_crib_candidates.txt'


def load_cribs(path: Path) -> set[str]:
    out = set()
    if not path.exists():
        return out
    with path.open('r', encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            tok = line.split('\t')[0].strip().upper()
            if tok:
                out.add(tok)
    return out


def find_latest_run() -> Path | None:
    tr = REPO / 'artifacts' / 'tuning_runs'
    if not tr.exists():
        return None
    runs = [p for p in tr.iterdir() if p.is_dir() and p.name.startswith('run_')]
    if not runs:
        return None
    latest = max(runs, key=lambda p: p.stat().st_mtime)
    return latest


def scan_run(run_dir: Path, cribs: set[str]) -> list[tuple[str, str, float]]:
    """Scan per-weight detail CSVs and return tuples of (filename, matched_tokens, delta).

    Prefer tokens that appear inside quotes in the sample. If quoted tokens are present
    and match the crib list, prefer those. Dedupe matches per run by token.
    """
    results: list[tuple[str, str, float]] = []
    seen_tokens: set[str] = set()
    for csvf in run_dir.glob('weight_*_details.csv'):
        with csvf.open('r', encoding='utf-8') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                sample = row.get('sample', '')
                try:
                    delta = float(row.get('delta', '0'))
                except Exception:
                    delta = 0.0
                # only consider positive deltas
                if delta <= 0:
                    continue

                text = sample.upper()
                # find quoted uppercase tokens first
                quoted = re.findall(r'["\']([A-Z]{3,})["\']', text)
                if quoted:
                    tokens_to_check = quoted
                else:
                    tokens_to_check = re.findall(r'[A-Z]{3,}', text)

                matches = [t for t in tokens_to_check if t in cribs and t not in seen_tokens]
                for t in matches:
                    seen_tokens.add(t)

                if matches:
                    results.append((csvf.name, ','.join(matches), delta))
    return results


def append_learned(note: str) -> None:
    LEARNED.parent.mkdir(parents=True, exist_ok=True)
    with LEARNED.open('a', encoding='utf-8') as fh:
        fh.write(f"- {note}\n")


def main():
    cribs = load_cribs(CRIBS)
    run = find_latest_run()
    if not run:
        print('No tuning runs found')
        return 1
    res = scan_run(run, cribs)
    if not res:
        print('No conservative crib matches found in latest run')
        return 0

    # compute a simple confidence score relative to the max delta in this run
    max_delta = max((d for _, _, d in res), default=0.0)
    notes_written = 0
    for fname, matches, delta in res:
        conf = 0.0 if max_delta <= 0 else float(delta) / float(max_delta)
        note = f"SPY_MATCH {fname}: {matches} (delta={delta:.6f}, conf={conf:.2f})"
        append_learned(note)
        print(note)
        notes_written += 1

    print(f'Appended {notes_written} learned entries to {LEARNED}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
