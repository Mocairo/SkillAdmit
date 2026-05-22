#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from plugins_beta.main import preserve_marker, resolve
from plugins_beta.catalog.loader import load_plugin
assert resolve() == "plugin-beta"
assert load_plugin("beta") == "plugin-beta"
assert preserve_marker() == "hard-v3-plugin-import-22"
assert not Path("catalog").exists(), "top-level registry package masks a package-internal import bug"
PY
