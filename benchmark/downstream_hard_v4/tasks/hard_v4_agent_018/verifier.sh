#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
import importlib.util
spec = importlib.util.spec_from_file_location("render_18", "notice_beta/render.py")
render = importlib.util.module_from_spec(spec)
spec.loader.exec_module(render)
assert render.render_notice("Grace") == "notice-beta:Grace"
assert render.preserve_marker() == "hard-v4-resource-template-18"
assert not Path("notice_beta/resources/templates/notice_beta.txt").exists(), "copied template masks a cwd-sensitive resource bug"
PY
