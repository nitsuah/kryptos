"""Config checks for the Cloudflare Pages edge files in frontend/public."""

from pathlib import Path

PUBLIC = Path(__file__).resolve().parents[2] / "frontend" / "public"


def _blocks(text: str) -> dict[str, list[str]]:
    """Parse a Pages _headers file into {path pattern: [header lines]}."""
    blocks: dict[str, list[str]] = {}
    current = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw[0] not in " \t":
            current = raw.strip()
            blocks[current] = []
        elif current is not None:
            blocks[current].append(raw.strip())
    return blocks


def test_headers_set_hsts_for_every_path():
    blocks = _blocks((PUBLIC / "_headers").read_text(encoding="utf-8"))
    assert "Strict-Transport-Security: max-age=31536000; includeSubDomains" in blocks["/*"]


def test_hashed_assets_are_immutable():
    blocks = _blocks((PUBLIC / "_headers").read_text(encoding="utf-8"))
    assert "Cache-Control: public, max-age=31536000, immutable" in blocks["/assets/*"]


def test_unknown_paths_404_and_api_is_proxied():
    assert (PUBLIC / "404.html").is_file()
    rules = [
        line.split()
        for line in (PUBLIC / "_redirects").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    assert ["/api/*", "https://kryptos-kg8t.onrender.com/api/:splat", "200"] in rules
    assert not any(r[0] == "/*" for r in rules), "a catch-all rewrite would bring back SPA 200s"
