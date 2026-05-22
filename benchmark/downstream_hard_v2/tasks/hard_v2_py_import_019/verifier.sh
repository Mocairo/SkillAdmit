#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
import importlib.util
spec = importlib.util.spec_from_file_location("loader_19", "runner_delta/loader.py")
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)
assert loader.preserve_label() == "cwd-hard-v2-19"
assert loader.load_value() == "hard-v2-cwd-delta"
assert not Path("runner_delta/data/delta.txt").exists(), "duplicating data under cwd masks the path bug"
PY
