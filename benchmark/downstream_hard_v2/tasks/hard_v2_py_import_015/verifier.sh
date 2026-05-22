#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
import subprocess
import sys
from clipkg_omega.main import preserve_mode, run
assert preserve_mode() == "script-mode-hard-v2-15"
assert run() == "hard-v2-script-omega"
result = subprocess.run([sys.executable, "clipkg_omega/main.py"], capture_output=True, text=True)
assert result.returncode == 0, result.stderr
assert "hard-v2-script-omega" in result.stdout
assert not Path("views.py").exists(), "top-level helper masks script/package import semantics"
PY
