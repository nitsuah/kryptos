#!/usr/bin/env python3
"""Fetch a list of URLs and append a simple timeline entry to a target markdown file.

Usage:
    python scripts/collect_sanborn_sources.py urls.txt docs/sources/sanborn_timeline.md

Notes: requires `requests` and `beautifulsoup4` if run locally.
"""

import sys

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("This script requires requests and beautifulsoup4. Install them in your venv:")
    print("pip install requests beautifulsoup4")
    sys.exit(1)


def fetch_summary(url: str) -> tuple[str, str]:
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'html.parser')
    title = (soup.title.string or '').strip() if soup.title else url
    p = soup.find('p')
    excerpt = p.get_text().strip() if p else ''
    return title, excerpt


def main(urls_path: str, out_md: str) -> None:
    with open(urls_path, encoding='utf-8') as fh:
        urls = [line.strip() for line in fh if line.strip()]
    out_lines = []
    for u in urls:
        try:
            title, excerpt = fetch_summary(u)
            entry = [
                '---\n',
                '- Date: UNKNOWN\n',
                f'- Source: {u}\n',
                f'- Title: {title}\n',
                f'- Excerpt: {excerpt}\n',
                '- Notes: TBD\n',
                '\n',
            ]
            out_lines.extend(entry)
            print(f'Appended summary for {u}')
        except requests.RequestException as e:
            print(f'Failed to fetch {u}: {e}')
    if out_lines:
        with open(out_md, 'a', encoding='utf-8') as oh:
            oh.writelines(out_lines)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python scripts/collect_sanborn_sources.py urls.txt out.md')
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
