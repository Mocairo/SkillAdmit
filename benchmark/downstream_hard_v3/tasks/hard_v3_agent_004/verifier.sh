#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from svc_delta.handlers import build_response, preserve_marker
assert build_response({"id": "99"}) == "delta-response:99"
assert preserve_marker() == "hard-v3-optional-import-4"
assert not Path("vendor_audit_delta.py").exists(), "fake optional dependency masks an unused import"
PY
