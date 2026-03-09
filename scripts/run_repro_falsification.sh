#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

if [[ ! -x ".venv/bin/python" ]]; then
  echo "NO-GO: missing pinned interpreter at .venv/bin/python" >&2
  echo "Bootstrap example:" >&2
  echo "  python3 -m venv .venv" >&2
  echo "  .venv/bin/python -m pip install --upgrade pip" >&2
  echo "  .venv/bin/python -m pip install -e \".[dev,validation]\"" >&2
  exit 1
fi

exec ".venv/bin/python" "scripts/repro_falsification_runner.py"
