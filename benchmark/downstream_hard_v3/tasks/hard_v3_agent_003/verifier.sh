#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from svc_gamma.handlers import build_response, preserve_marker
assert build_response({"id": "99"}) == "gamma-response:99"
assert preserve_marker() == "hard-v3-optional-import-3"
assert not Path("cloud_probe_gamma.py").exists(), "fake optional dependency masks an unused import"
PY
