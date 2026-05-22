#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from svc_alpha.handlers import build_response, preserve_marker
assert build_response({"id": "99"}) == "alpha-response:99"
assert preserve_marker() == "hard-v3-optional-import-1"
assert not Path("optional_metrics_alpha.py").exists(), "fake optional dependency masks an unused import"
PY
