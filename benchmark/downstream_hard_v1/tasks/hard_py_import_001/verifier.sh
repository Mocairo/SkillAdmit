#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from app.main import preserve_me, run
from app.analytics import load_metrics
assert run() == "hard-analytics-ok"
assert load_metrics() == "hard-analytics-ok"
assert preserve_me() == "hard-local-module-v1"
assert not Path("analytics.py").exists(), "top-level stub masks the import bug"
PY
