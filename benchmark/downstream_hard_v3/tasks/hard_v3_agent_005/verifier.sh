#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from svc_omega.handlers import build_response, preserve_marker
assert build_response({"id": "99"}) == "omega-response:99"
assert preserve_marker() == "hard-v3-optional-import-5"
assert not Path("telemetry_omega_sdk.py").exists(), "fake optional dependency masks an unused import"
PY
