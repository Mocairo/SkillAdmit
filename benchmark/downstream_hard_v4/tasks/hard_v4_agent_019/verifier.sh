#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
import importlib.util
spec = importlib.util.spec_from_file_location("render_19", "notice_gamma/render.py")
render = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)
assert render.render_notice("Grace") == "notice-gamma:Grace"
assert render.preserve_marker() == "hard-v4-resource-template-19"
assert not Path("notice_gamma/resources/templates/notice_gamma.txt").exists(), "copied template masks a cwd-sensitive resource bug"
PY
