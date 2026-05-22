#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
import importlib.util
spec = importlib.util.spec_from_file_location("settings_15", "worker_gamma/settings.py")
settings = importlib.util.module_from_spec(spec)
spec.loader.exec_module(settings)
assert settings.load_region() == "ap-gamma"
assert settings.preserve_marker() == "hard-v4-workspace-config-15"
assert not Path("worker_gamma/config/runtime_gamma.json").exists(), "copied config masks a cwd-sensitive path bug"
PY
