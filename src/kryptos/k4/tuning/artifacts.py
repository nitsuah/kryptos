"""Artifact post-processing utilities for tuning runs.

These functions operate on a single run directory produced by a crib weight sweep
or related tuning experiment. They are pure in the sense they only touch the
filesystem paths you explicitly pass (no global path discovery) and return
structured data for programmatic consumption. Writing / updating files is
explicit and documented.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MatchEntry:
    sample: str
    matched: str  # pipe-delimited crib tokens (deduplicated, sorted)


def find_match_files(run_dir: Path) -> list[Path]:
    return sorted(run_dir.glob('matches_weight_*.csv'))


def _clean_match_file(path: Path) -> list[MatchEntry]:
    """Return cleaned entries (deduped + sorted tokens) for a single match file.

    Overwrites the original file in-place with normalized content & header.
    """
    if not path.exists():
        return []
    out: list[MatchEntry] = []
    with path.open('r', encoding='utf-8') as fh:
        reader = csv.reader(fh)
        next(reader, None)  # skip header if present
        for row in reader:
            if not row:
                continue
            sample = row[0]
            matched_raw = row[1] if len(row) > 1 else ''
            if matched_raw:
                parts = [p for p in matched_raw.split('|') if p]
                uniq = sorted(set(parts))
                joined = '|'.join(uniq)
            else:
                joined = ''
            out.append(MatchEntry(sample=sample, matched=joined))
    # overwrite normalized
    with path.open('w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['sample', 'matched_cribs'])
        for e in out:
            w.writerow([e.sample, e.matched])
    return out


def clean_all_match_files(run_dir: Path) -> dict[str, list[MatchEntry]]:
    """Clean every matches_weight_*.csv file returning mapping weight->entries.

    Weight key extracted from filename suffix: matches_weight_<weight>.csv where
    '.' in weight is replaced by '_' in file naming convention.
    """
    cleaned: dict[str, list[MatchEntry]] = {}
    for f in find_match_files(run_dir):
        weight_key = f.stem.replace('matches_weight_', '')
        cleaned[weight_key] = _clean_match_file(f)
    return cleaned


def load_weight_sweep_csv(run_dir: Path) -> list[list[str]]:
    path = run_dir / 'crib_weight_sweep.csv'
    if not path.exists():
        return []
    rows: list[list[str]] = []
    with path.open('r', encoding='utf-8') as fh:
        r = csv.reader(fh)
        next(r, None)
        for row in r:
            if row:
                rows.append(row)
    return rows


def summarize_run(run_dir: Path) -> dict:
    """Produce an in-memory summary of a tuning run.

    Returns a dict with keys: run_dir, top_deltas (list), weight_stats (dict).
    Does not write to disk (call write_summary_text / write_summary_json).
    """
    sweep_rows = load_weight_sweep_csv(run_dir)
    # parse rows: weight, sample, baseline, with_cribs, delta
    parsed = []
    by_weight: dict[str, list[float]] = {}
    for row in sweep_rows:
        if len(row) < 5:
            continue
        w, sample, delta = row[0], row[1], row[4]
        try:
            d = float(delta)
        except ValueError:
            continue
        parsed.append((abs(d), d, w, sample))
        by_weight.setdefault(w, []).append(d)
    parsed.sort(reverse=True)
    top_deltas = [{"weight": w, "delta": d, "sample": sample[:120]} for _absd, d, w, sample in parsed[:10]]
    weight_stats = {
        w: {"mean_delta": (sum(vals) / len(vals)) if vals else 0.0, "count": len(vals)} for w, vals in by_weight.items()
    }
    return {"run_dir": run_dir.name, "top_deltas": top_deltas, "weight_stats": weight_stats}


def write_summary_text(run_dir: Path, summary: dict) -> Path:
    outp = run_dir / 'artifact_summary.txt'
    with outp.open('w', encoding='utf-8') as fh:
        fh.write(f"Artifact run: {summary['run_dir']}\n")
        fh.write('Summary of crib-weight deltas (top 10)\n\n')
        for td in summary['top_deltas']:
            fh.write(f"weight={td['weight']} delta={td['delta']:+.3f} sample=\"{td['sample']}\"\n")
        fh.write('\nMean delta per weight:\n')
        for w, meta in summary['weight_stats'].items():
            fh.write(f"{w}: mean_delta={meta['mean_delta']:.4f} n={meta['count']}\n")
    return outp


def crib_hit_counts(run_dir: Path) -> dict[str, int]:
    """Aggregate crib hit frequencies across all cleaned match files."""
    counts: dict[str, int] = {}
    for f in find_match_files(run_dir):
        if not f.exists():
            continue
        with f.open('r', encoding='utf-8') as fh:
            next(fh, None)  # header
            for line in fh:
                parts = line.rstrip('\n').split(',', 1)
                if len(parts) < 2:
                    continue
                matched = parts[1].strip()
                if not matched:
                    continue
                for crib in matched.split('|'):
                    c = crib.strip()
                    if not c:
                        continue
                    counts[c] = counts.get(c, 0) + 1
    return counts


def write_crib_hit_counts(run_dir: Path, counts: dict[str, int]) -> Path:
    out_json = run_dir / 'crib_hit_counts.json'
    out_json.write_text(json.dumps(counts, indent=2), encoding='utf-8')
    return out_json


def end_to_end_process(run_dir: Path, write: bool = True) -> dict:
    """Convenience: clean match files, summarize run, compute crib hit counts.

    If write=True, updates match files and writes summary + crib counts artifacts.
    Returns a combined dict with keys: summary, counts.
    """
    clean_all_match_files(run_dir)
    summary = summarize_run(run_dir)
    counts = crib_hit_counts(run_dir)
    if write:
        write_summary_text(run_dir, summary)
        write_crib_hit_counts(run_dir, counts)
    return {"summary": summary, "counts": counts}


__all__ = [
    'MatchEntry',
    'find_match_files',
    'clean_all_match_files',
    'summarize_run',
    'write_summary_text',
    'crib_hit_counts',
    'write_crib_hit_counts',
    'end_to_end_process',
]
