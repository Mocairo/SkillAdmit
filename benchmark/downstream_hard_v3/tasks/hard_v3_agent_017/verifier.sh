#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
import importlib.util
spec = importlib.util.spec_from_file_location("reader_17", "worker_beta/reader.py")
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)
assert reader.load_mode() == "config-beta"
assert reader.preserve_marker() == "hard-v3-config-path-17"
assert not Path("worker_beta/config/settings_beta.json").exists(), "copied config masks a cwd-sensitive path bug"
PY
