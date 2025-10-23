"""Extract conservative quoted phrases from docs/ and docs/sources/.

Rules (conservative):
- Only extract text within double quotes "..." or single quotes '...'
- Only keep alphabetic tokens >=3 characters, uppercase them, and output unique entries
- Output TSV: CANDIDATE\tSOURCE_PATH\tEXCERPT\tCONFIDENCE
- Confidence: 'high' if the excerpt contains the word "said"/"stated"/"wrote" nearby, else 'med'

This is intentionally conservative and offline; no network calls.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / 'docs'
SOURCES = ROOT / 'docs' / 'sources'
OUT_DIR = ROOT / 'agents' / 'output'
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PATH = OUT_DIR / 'spy_cribs.tsv'

QUOTE_RE = re.compile(r'"([A-Za-z0-9 \-\.,;:!\'\(\)]+)"')
NEARBY_CTX_RE = re.compile(r'\b(said|stated|wrote|reported|noted)\b', re.I)
TOKEN_CLEAN_RE = re.compile(r'[^A-Z]')


def scan_file(path: Path):
    try:
        text = path.read_text(encoding='utf-8')
    except Exception:
        return []
    findings = []
    for m in QUOTE_RE.finditer(text):
        excerpt = m.group(1).strip()
        if not excerpt:
            continue
        # Heuristic: pick tokens separated by whitespace and punctuation
        tokens = [t.strip() for t in re.split(r'[,;:\-\s]+', excerpt) if t.strip()]
        for t in tokens:
            up = t.upper()
            clean = TOKEN_CLEAN_RE.sub('', up)
            if len(clean) >= 3 and clean.isalpha():
                # confidence: high if nearby indicators in surrounding 80 chars
                start = max(0, m.start() - 80)
                ctx = text[start : m.end() + 80]
                conf = 'high' if NEARBY_CTX_RE.search(ctx) else 'med'
                findings.append((clean, str(path.relative_to(ROOT)), excerpt, conf))
    return findings


def run_scan():
    files = []
    if DOCS.exists():
        for p in DOCS.rglob('*.md'):
            files.append(p)
        for p in (DOCS / 'sources').rglob('*') if (DOCS / 'sources').exists() else []:
            if p.is_file():
                files.append(p)
    # also scan README files at repo root
    for root_readme in ['README.md', 'README.txt']:
        p = ROOT / root_readme
        if p.exists():
            files.append(p)
    found = []
    for f in files:
        found.extend(scan_file(f))
    # deduplicate preserving first-seen
    seen = set()
    dedup = []
    for entry in found:
        key = (entry[0], entry[1])
        if key in seen:
            continue
        seen.add(key)
        dedup.append(entry)
    # write TSV
    with open(OUT_PATH, 'w', encoding='utf-8') as fh:
        for cand, src, excerpt, conf in dedup:
            fh.write(f"{cand}\t{src}\t{excerpt}\t{conf}\n")
    return OUT_PATH


if __name__ == '__main__':
    out = run_scan()
    print('Wrote', out)
