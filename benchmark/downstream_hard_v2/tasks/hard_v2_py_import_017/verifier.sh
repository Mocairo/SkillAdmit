#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
import importlib.util
spec = importlib.util.spec_from_file_location("loader_17", "runner_beta/loader.py")
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)
assert loader.preserve_label() == "cwd-hard-v2-17"
assert loader.load_value() == "hard-v2-cwd-beta"
assert not Path("runner_beta/data/beta.txt").exists(), "duplicating data under cwd masks the path bug"
PY
