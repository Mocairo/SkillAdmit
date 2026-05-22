#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
import importlib.util
spec = importlib.util.spec_from_file_location("loader", "service/loader.py")
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)
assert loader.preserve_label() == "cwd-hard-v1"
assert loader.load_value() == "hard-cwd-ok"
assert not Path("service/data/value.txt").exists(), "duplicating data under cwd masks the path bug"
PY
