"""Reporting utilities for K4 tuning runs.

This module centralizes logic previously found in ad-hoc experimental scripts
(`condensed_tuning_report.py`, `generate_top_candidates.py`). It provides
helpers to build a condensed summary from a crib weight sweep CSV and generate
top candidate markdown reports enriched with optional learned SPY phrase
matches.

Expected directory layout (produced by tuning sweep / artifacts):
  artifacts/tuning_runs/run_<ts>/crib_weight_sweep.csv
  artifacts/tuning_runs/run_<ts>/weight_<w>_details.csv (per weight)

Functions:
  build_condensed_rows(run_dir) -> list[dict]
  write_condensed_report(run_dir, out_path) -> Path
  write_top_candidates_markdown(run_dir, out_dir, top_n=3) -> Path

The condensed report aggregates the top delta per weight along with a sample
snippet. The markdown report lists the best N weights sorted by delta.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from kryptos.paths import get_repo_root  # use helper instead of manual parents ascent


@dataclass
class CondensedRow:
    weight: float
    top_delta: float
    sample_snippet: str

    def as_dict(self) -> dict:
        return {
            'weight': self.weight,
            'top_delta': self.top_delta,
            'sample_snippet': self.sample_snippet,
        }


def _parse_weight_details(path: Path) -> list[tuple[str, float]]:
    """Return list of (sample, delta) from a weight detail CSV."""
    rows: list[tuple[str, float]] = []
    if not path.exists():
        return rows
    with path.open('r', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            sample = (row.get('sample') or row.get('sample_snippet') or '').strip()
            raw_delta = row.get('delta', '')
            try:
                delta = float(raw_delta)
            except (TypeError, ValueError):
                continue
            rows.append((sample, delta))
    return rows


def build_condensed_rows(run_dir: Path) -> list[CondensedRow]:
    """Build condensed rows from all weight_* detail CSVs in a run directory.

    For each weight_<val>_details.csv file, pick the sample with the maximum delta.
    """
    condensed: list[CondensedRow] = []
    if not run_dir.exists():
        return condensed
    for child in run_dir.iterdir():
        if child.is_file() and child.name.startswith('weight_') and child.name.endswith('_details.csv'):
            # extract numeric weight (replace underscores back to dot for floats)
            try:
                weight_part = child.name[len('weight_') : -len('_details.csv')]
                weight_val = float(weight_part.replace('_', '.'))
            except ValueError:
                continue
            samples = _parse_weight_details(child)
            if not samples:
                continue
            # pick top delta sample
            top_sample, top_delta = max(samples, key=lambda r: r[1])
            condensed.append(CondensedRow(weight=weight_val, top_delta=top_delta, sample_snippet=top_sample[:120]))
    condensed.sort(key=lambda r: r.top_delta, reverse=True)
    return condensed


def write_condensed_report(run_dir: Path, out_path: Path | None = None) -> Path:
    """Write condensed_report.csv for a run and return its path."""
    rows = build_condensed_rows(run_dir)
    if out_path is None:
        out_path = run_dir / 'condensed_report.csv'
    with out_path.open('w', newline='', encoding='utf-8') as fh:
        writer = csv.writer(fh)
        writer.writerow(['weight', 'top_delta', 'sample_snippet'])
        for r in rows:
            writer.writerow([f'{r.weight}', f'{r.top_delta:.6f}', r.sample_snippet])
    return out_path


def _load_learned_lines(repo_root: Path) -> list[str]:
    learned = repo_root / 'agents' / 'LEARNED.md'
    if not learned.exists():
        return []
    return [ln.strip() for ln in learned.read_text(encoding='utf-8').splitlines() if ln.strip()]


def write_top_candidates_markdown(run_dir: Path, out_dir: Path | None = None, top_n: int = 3) -> Path:
    """Generate a top candidates markdown report from condensed_report.csv.

    Looks for learned lines referencing per-weight detail files and attaches them.
    """
    if out_dir is None:
        out_dir = run_dir.parent.parent / 'reports'
    out_dir.mkdir(parents=True, exist_ok=True)
    condensed_path = run_dir / 'condensed_report.csv'
    if not condensed_path.exists():
        # Attempt to build it if missing
        write_condensed_report(run_dir, condensed_path)
    rows: list[CondensedRow] = []
    with condensed_path.open('r', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            try:
                w = float(row.get('weight', '0'))
                delta = float(row.get('top_delta', '0'))
            except (TypeError, ValueError):
                continue
            snippet = row.get('sample_snippet', '')
            rows.append(CondensedRow(weight=w, top_delta=delta, sample_snippet=snippet))
    rows.sort(key=lambda r: r.top_delta, reverse=True)
    top = rows[:top_n]
    repo_root = get_repo_root()
    learned_lines = _load_learned_lines(repo_root)
    # map file names to learned lines
    file_to_learned: dict[str, list[str]] = {}
    for ln in learned_lines:
        for f in run_dir.iterdir():
            if f.is_file() and f.name in ln:
                file_to_learned.setdefault(f.name, []).append(ln)

    ts = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    out_md = out_dir / f'top_candidates_{ts}.md'
    with out_md.open('w', encoding='utf-8') as of:
        of.write('# Top K4 Candidates Report\n\n')
        of.write(f'Generated: {ts}\n\n')
        of.write(f'Run directory: {run_dir}\n\n')
        for i, cand in enumerate(top, start=1):
            of.write(f'## Candidate {i}\n')
            of.write(f'- weight: {cand.weight}\n')
            of.write(f'- top_delta: {cand.top_delta:.6f}\n')
            of.write(f'- sample_snippet: "{cand.sample_snippet}"\n')
            detail_name = f'weight_{str(cand.weight).replace(".", "_")}_details.csv'
            detail_path = run_dir / detail_name
            if detail_path.exists():
                of.write(f'- detail_file: {detail_path}\n')
                learns = file_to_learned.get(detail_name, [])
                if learns:
                    of.write('- SPY matches:\n')
                    for ln in learns:
                        of.write(f'  - {ln}\n')
            of.write('\n')
    return out_md


__all__ = [
    'CondensedRow',
    'build_condensed_rows',
    'write_condensed_report',
    'write_top_candidates_markdown',
]
