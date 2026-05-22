#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from app import get_name, preserve_marker
assert get_name() == "hard-unused-import-ok"
assert preserve_marker() == "unused-import-hard-v1"
assert not Path("futuredep_hard.py").exists(), "dependency stub masks unused import"
PY
