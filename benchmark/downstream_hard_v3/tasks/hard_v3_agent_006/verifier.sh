#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from orders_alpha.api import preserve_marker, render_order
from orders_alpha.formatters import format_order
assert render_order("B23") == "order-alpha:B23"
assert format_order("C31") == "order-alpha:C31"
assert preserve_marker() == "hard-v3-local-import-6"
assert not Path("formatters.py").exists(), "top-level module masks a package-local import bug"
PY
