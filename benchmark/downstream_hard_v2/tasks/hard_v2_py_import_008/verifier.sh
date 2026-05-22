#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from gamma_app.main import preserve_me, run
from gamma_app.service import run_service
assert run() == "hard-v2-local-gamma"
assert run_service() == "hard-v2-local-gamma"
assert preserve_me() == "local-module-hard-v2-8"
assert not Path("service.py").exists(), "top-level stub masks the local package import bug"
PY
