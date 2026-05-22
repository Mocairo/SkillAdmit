#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from domain_beta.service import build_slug, preserve_marker
from domain_beta.formatters import format_slug
assert build_slug("Hidden Case") == "beta-hidden-case"
assert format_slug("Deep Value") == "beta-deep-value"
assert preserve_marker() == "hard-v4-src-layout-6"
assert not Path("formatters.py").exists(), "top-level compatibility module masks a package-local import bug"
PY
