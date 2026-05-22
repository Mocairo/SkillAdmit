#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
import importlib.util
spec = importlib.util.spec_from_file_location("renderer_30", "job_omega/renderer.py")
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
assert renderer.render_report("Grace") == "report-omega:Grace"
assert renderer.preserve_marker() == "hard-v3-template-path-30"
assert not Path("job_omega/assets/templates/summary_omega.txt").exists(), "copied template masks a cwd-sensitive resource bug"
PY
