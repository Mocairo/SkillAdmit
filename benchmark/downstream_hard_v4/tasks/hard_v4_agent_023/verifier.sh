#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from platform_gamma.main import preserve_marker, resolve_plugin
from platform_gamma.providers.loader import load_plugin
assert resolve_plugin() == "plugin-gamma"
assert load_plugin("gamma") == "plugin-gamma"
assert preserve_marker() == "hard-v4-plugin-registry-23"
assert not Path("providers").exists(), "top-level registry package masks a package-internal import bug"
PY
