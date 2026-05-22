#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
import subprocess
import sys
from ops_delta.scripts.migrate import command_output, preserve_marker
assert command_output() == "migration-delta"
assert preserve_marker() == "hard-v3-dual-command-14"
result = subprocess.run([sys.executable, "ops_delta/scripts/migrate.py"], capture_output=True, text=True)
assert result.returncode == 0, result.stderr
assert "migration-delta" in result.stdout
PY
