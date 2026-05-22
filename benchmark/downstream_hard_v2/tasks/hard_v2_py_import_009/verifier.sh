#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from delta_app.main import preserve_me, run
from delta_app.parser import parse_text
assert run() == "hard-v2-local-delta"
assert parse_text() == "hard-v2-local-delta"
assert preserve_me() == "local-module-hard-v2-9"
assert not Path("parser.py").exists(), "top-level stub masks the local package import bug"
PY
