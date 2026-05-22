#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from beta_app.main import preserve_me, run
from beta_app.config import load_config
assert run() == "hard-v2-local-beta"
assert load_config() == "hard-v2-local-beta"
assert preserve_me() == "local-module-hard-v2-7"
assert not Path("config.py").exists(), "top-level stub masks the local package import bug"
PY
