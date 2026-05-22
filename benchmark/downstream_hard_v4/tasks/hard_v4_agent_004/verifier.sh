#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from client_delta.client import format_event, preserve_marker
assert format_event({"id": "99", "kind": "hidden"}) == "evt-delta:99:hidden"
assert preserve_marker() == "hard-v4-optional-telemetry-4"
assert not Path("audit_sink_delta.py").exists(), "fake optional telemetry dependency masks an unused import"
PY
