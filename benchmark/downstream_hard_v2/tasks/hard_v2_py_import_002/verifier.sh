#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from app import get_name, preserve_marker
assert get_name() == "hard-v2-unused-beta"
assert preserve_marker() == "unused-import-hard-v2-2"
assert not Path("ghostlib_beta_v2.py").exists(), "dependency stub masks an unused import"
PY
