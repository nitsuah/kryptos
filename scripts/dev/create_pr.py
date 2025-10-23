#!/usr/bin/env python3
"""Small helper to create a GitHub PR via REST API using a personal access token.

Usage:
  export GITHUB_TOKEN=ghp_...
  python scripts/dev/create_pr.py --head autopilot/branch --base main --title "WIP" --body "PR body"

This script is a fallback when the `gh` CLI isn't available. It requires a token with
`repo` scope for private repos or `public_repo` for public repos.
"""

from __future__ import annotations

import argparse
import os

import requests


def create_pr(
    owner: str,
    repo: str,
    head: str,
    base: str = 'main',
    title: str = '',
    body: str = '',
    token: str | None = None,
) -> dict:
    """Create a PR via GitHub REST API and return the parsed JSON response.

    Raises ValueError if token is not provided.
    Raises requests.HTTPError on non-2xx responses.
    """
    if not token:
        token = os.environ.get('GITHUB_TOKEN')
    if not token:
        raise ValueError('GITHUB_TOKEN required to create a PR programmatically')

    url = f'https://api.github.com/repos/{owner}/{repo}/pulls'
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
    }
    payload = {
        'title': title or f'PR: {head} -> {base}',
        'head': head,
        'base': base,
        'body': body,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=15)
    if not resp.ok:
        # raise with helpful message
        try:
            msg = resp.json()
        except Exception:
            msg = resp.text
        raise requests.HTTPError(f'Failed to create PR: {resp.status_code} {msg}')
    return resp.json()


def _parse_repo(origin_url: str) -> tuple[str, str]:
    # Normalize origin url into owner/repo
    if origin_url.endswith('.git'):
        origin_url = origin_url[:-4]
    if origin_url.startswith('git@'):
        # git@github.com:owner/repo.git
        origin_url = origin_url.replace(':', '/').replace('git@', 'https://')
    # now expect https://.../owner/repo
    parts = origin_url.rstrip('/').split('/')
    if len(parts) < 2:
        raise ValueError('Cannot parse origin url')
    return parts[-2], parts[-1]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--origin', type=str, default=None, help='origin URL (optional)')
    parser.add_argument('--head', type=str, required=True, help='head branch (owner:branch or branch)')
    parser.add_argument('--base', type=str, default='main', help='base branch')
    parser.add_argument('--title', type=str, default='', help='PR title')
    parser.add_argument('--body', type=str, default='', help='PR body')
    parser.add_argument(
        '--token',
        type=str,
        default=None,
        help=('GitHub token (optional, env GITHUB_TOKEN will be used if omitted)'),
    )
    args = parser.parse_args(argv)

    # try to infer owner/repo from git remote if not provided
    origin = args.origin or os.environ.get('GIT_REMOTE_ORIGIN')
    if not origin:
        # try to read via git command
        try:
            import subprocess

            origin = subprocess.check_output(['git', 'remote', 'get-url', 'origin'], encoding='utf-8').strip()
        except Exception:
            origin = None

    if not origin:
        print('Cannot determine repo owner/repo. Set --origin or GIT_REMOTE_ORIGIN environment variable.')
        return 2

    try:
        owner, repo = _parse_repo(origin)
    except Exception as e:
        print(f'Failed to parse origin URL: {e}')
        return 2

    try:
        res = create_pr(owner, repo, head=args.head, base=args.base, title=args.title, body=args.body, token=args.token)
        print('PR created:', res.get('html_url'))
        return 0
    except Exception as e:
        print('PR creation failed:', e)
        # print fallback compare URL
        compare = f"{origin}/compare/{args.base}...{args.head}?expand=1"
        print('Fallback compare URL:', compare)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
