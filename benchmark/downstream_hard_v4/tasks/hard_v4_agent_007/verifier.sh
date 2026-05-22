#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from domain_gamma.service import build_slug, preserve_marker
from domain_gamma.presenters import present_slug
assert build_slug("Hidden Case") == "gamma-hidden-case"
assert present_slug("Deep Value") == "gamma-deep-value"
assert preserve_marker() == "hard-v4-src-layout-7"
assert not Path("presenters.py").exists(), "top-level compatibility module masks a package-local import bug"
PY
