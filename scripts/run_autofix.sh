#!/usr/bin/env bash
set -euo pipefail
python "$(dirname "$0")/auto_fix_spacing.py"
pre-commit run --all-files || true
