#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
import importlib.util
spec = importlib.util.spec_from_file_location("renderer_27", "job_beta/renderer.py")
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
assert renderer.render_report("Grace") == "report-beta:Grace"
assert renderer.preserve_marker() == "hard-v3-template-path-27"
assert not Path("job_beta/assets/templates/summary_beta.txt").exists(), "copied template masks a cwd-sensitive resource bug"
PY
