#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
import subprocess
import sys
from ops_beta.jobs.migrate import command_output, preserve_marker
assert command_output() == "migration-beta"
assert preserve_marker() == "hard-v3-dual-command-12"
result = subprocess.run([sys.executable, "ops_beta/jobs/migrate.py"], capture_output=True, text=True)
assert result.returncode == 0, result.stderr
assert "migration-beta" in result.stdout
PY
