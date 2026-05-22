#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from domain_delta.service import build_slug, preserve_marker
from domain_delta.labels import label_slug
assert build_slug("Hidden Case") == "delta-hidden-case"
assert label_slug("Deep Value") == "delta-deep-value"
assert preserve_marker() == "hard-v4-src-layout-8"
assert not Path("labels.py").exists(), "top-level compatibility module masks a package-local import bug"
PY
