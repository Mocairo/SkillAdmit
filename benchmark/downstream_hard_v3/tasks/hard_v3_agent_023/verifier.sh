#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from plugins_gamma.main import preserve_marker, resolve
from plugins_gamma.providers.loader import load_plugin
assert resolve() == "plugin-gamma"
assert load_plugin("gamma") == "plugin-gamma"
assert preserve_marker() == "hard-v3-plugin-import-23"
assert not Path("providers").exists(), "top-level registry package masks a package-internal import bug"
PY
