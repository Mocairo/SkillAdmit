#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from omega_app.main import preserve_me, run
from omega_app.helpers import build_value
assert run() == "hard-v2-local-omega"
assert build_value() == "hard-v2-local-omega"
assert preserve_me() == "local-module-hard-v2-10"
assert not Path("helpers.py").exists(), "top-level stub masks the local package import bug"
PY
