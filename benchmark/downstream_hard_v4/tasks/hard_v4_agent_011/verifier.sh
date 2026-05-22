#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
import subprocess
import sys
from cli_gamma.tools.export import command_output, preserve_marker
assert command_output() == "export-gamma"
assert preserve_marker() == "hard-v4-dual-entrypoint-11"
result = subprocess.run([sys.executable, "cli_gamma/tools/export.py"], capture_output=True, text=True)
assert result.returncode == 0, result.stderr
assert "export-gamma" in result.stdout
PY
