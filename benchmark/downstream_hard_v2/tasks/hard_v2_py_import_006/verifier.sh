#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from alpha_app.main import preserve_me, run
from alpha_app.analytics import load_metrics
assert run() == "hard-v2-local-alpha"
assert load_metrics() == "hard-v2-local-alpha"
assert preserve_me() == "local-module-hard-v2-6"
assert not Path("analytics.py").exists(), "top-level stub masks the local package import bug"
PY
