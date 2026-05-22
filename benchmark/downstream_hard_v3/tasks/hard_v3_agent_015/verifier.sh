#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
import subprocess
import sys
from ops_omega.tools.migrate import command_output, preserve_marker
assert command_output() == "migration-omega"
assert preserve_marker() == "hard-v3-dual-command-15"
result = subprocess.run([sys.executable, "ops_omega/tools/migrate.py"], capture_output=True, text=True)
assert result.returncode == 0, result.stderr
assert "migration-omega" in result.stdout
PY
