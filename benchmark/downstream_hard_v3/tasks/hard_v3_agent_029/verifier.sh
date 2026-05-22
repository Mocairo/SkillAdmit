#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
import importlib.util
spec = importlib.util.spec_from_file_location("renderer_29", "job_delta/renderer.py")
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
assert renderer.render_report("Grace") == "report-delta:Grace"
assert renderer.preserve_marker() == "hard-v3-template-path-29"
assert not Path("job_delta/assets/templates/summary_delta.txt").exists(), "copied template masks a cwd-sensitive resource bug"
PY
