#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from plugins_alpha.main import preserve_marker, resolve
from plugins_alpha.registry.loader import load_plugin
assert resolve() == "plugin-alpha"
assert load_plugin("alpha") == "plugin-alpha"
assert preserve_marker() == "hard-v3-plugin-import-21"
assert not Path("registry").exists(), "top-level registry package masks a package-internal import bug"
PY
