#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
import subprocess
import sys
from clipkg.main import preserve_mode
assert preserve_mode() == "script-mode-required"
result = subprocess.run([sys.executable, "clipkg/main.py"], capture_output=True, text=True)
assert result.returncode == 0, result.stderr
assert "hard-script-ok" in result.stdout
PY
