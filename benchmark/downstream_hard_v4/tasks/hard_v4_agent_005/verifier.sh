#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from domain_alpha.service import build_slug, preserve_marker
from domain_alpha.normalizers import normalize_slug
assert build_slug("Hidden Case") == "alpha-hidden-case"
assert normalize_slug("Deep Value") == "alpha-deep-value"
assert preserve_marker() == "hard-v4-src-layout-5"
assert not Path("normalizers.py").exists(), "top-level compatibility module masks a package-local import bug"
PY
