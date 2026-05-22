#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
import importlib.util
spec = importlib.util.spec_from_file_location("reader_19", "worker_delta/reader.py")
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)
assert reader.load_mode() == "config-delta"
assert reader.preserve_marker() == "hard-v3-config-path-19"
assert not Path("worker_delta/config/settings_delta.json").exists(), "copied config masks a cwd-sensitive path bug"
PY
