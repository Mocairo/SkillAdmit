#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from orders_gamma.api import preserve_marker, render_order
from orders_gamma.presenters import present_order
assert render_order("B23") == "order-gamma:B23"
assert present_order("C31") == "order-gamma:C31"
assert preserve_marker() == "hard-v3-local-import-8"
assert not Path("presenters.py").exists(), "top-level module masks a package-local import bug"
PY
