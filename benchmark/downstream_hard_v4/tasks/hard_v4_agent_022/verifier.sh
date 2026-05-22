#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from platform_beta.main import preserve_marker, resolve_plugin
from platform_beta.catalog.loader import load_plugin
assert resolve_plugin() == "plugin-beta"
assert load_plugin("beta") == "plugin-beta"
assert preserve_marker() == "hard-v4-plugin-registry-22"
assert not Path("catalog").exists(), "top-level registry package masks a package-internal import bug"
PY
