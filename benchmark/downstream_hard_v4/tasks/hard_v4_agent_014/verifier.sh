#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
import importlib.util
spec = importlib.util.spec_from_file_location("settings_14", "worker_beta/settings.py")
settings = importlib.util.module_from_spec(spec)
spec.loader.exec_module(settings)
assert settings.load_region() == "eu-beta"
assert settings.preserve_marker() == "hard-v4-workspace-config-14"
assert not Path("worker_beta/config/runtime_beta.json").exists(), "copied config masks a cwd-sensitive path bug"
PY
