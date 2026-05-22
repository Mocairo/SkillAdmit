#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
import importlib.util
spec = importlib.util.spec_from_file_location("reader_18", "worker_gamma/reader.py")
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)
assert reader.load_mode() == "config-gamma"
assert reader.preserve_marker() == "hard-v3-config-path-18"
assert not Path("worker_gamma/config/settings_gamma.json").exists(), "copied config masks a cwd-sensitive path bug"
PY
