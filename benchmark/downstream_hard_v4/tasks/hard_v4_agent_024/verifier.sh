#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from platform_delta.main import preserve_marker, resolve_plugin
from platform_delta.extensions.loader import load_plugin
assert resolve_plugin() == "plugin-delta"
assert load_plugin("delta") == "plugin-delta"
assert preserve_marker() == "hard-v4-plugin-registry-24"
assert not Path("extensions").exists(), "top-level registry package masks a package-internal import bug"
PY
