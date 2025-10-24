# Creating PRs from CI or locally

Two options to create PRs programmatically:

- Use GitHub CLI (`gh`) — convenient and interactive. Install from https://cli.github.com/ and run `gh auth login`.
- Use REST API with a token: set `GITHUB_TOKEN` environment variable (needs `repo` scope for private
repos) and use `scripts/dev/create_pr.py`.

Examples:

```powershell
# with gh (recommended locally):
gh pr create --fill --web

# with token (CI):
$env:GITHUB_TOKEN = 'ghp_...'
python .\scripts\dev\create_pr.py --head autopilot/triumverate-20251022T212638 --title "WIP: autopilot" --body "Creates autopilot branch"
```
