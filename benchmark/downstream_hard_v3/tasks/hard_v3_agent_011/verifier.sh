#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
import subprocess
import sys
from ops_alpha.commands.migrate import command_output, preserve_marker
assert command_output() == "migration-alpha"
assert preserve_marker() == "hard-v3-dual-command-11"
result = subprocess.run([sys.executable, "ops_alpha/commands/migrate.py"], capture_output=True, text=True)
assert result.returncode == 0, result.stderr
assert "migration-alpha" in result.stdout
PY
