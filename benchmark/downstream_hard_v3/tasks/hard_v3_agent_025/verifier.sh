#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from plugins_omega.main import preserve_marker, resolve
from plugins_omega.adapters.loader import load_plugin
assert resolve() == "plugin-omega"
assert load_plugin("omega") == "plugin-omega"
assert preserve_marker() == "hard-v3-plugin-import-25"
assert not Path("adapters").exists(), "top-level registry package masks a package-internal import bug"
PY
