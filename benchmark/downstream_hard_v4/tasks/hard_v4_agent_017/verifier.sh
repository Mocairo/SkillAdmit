#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
import importlib.util
spec = importlib.util.spec_from_file_location("render_17", "notice_alpha/render.py")
render = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)
assert render.render_notice("Grace") == "notice-alpha:Grace"
assert render.preserve_marker() == "hard-v4-resource-template-17"
assert not Path("notice_alpha/resources/templates/notice_alpha.txt").exists(), "copied template masks a cwd-sensitive resource bug"
PY
