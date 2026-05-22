#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from orders_omega.api import preserve_marker, render_order
from orders_omega.labels import label_order
assert render_order("B23") == "order-omega:B23"
assert label_order("C31") == "order-omega:C31"
assert preserve_marker() == "hard-v3-local-import-10"
assert not Path("labels.py").exists(), "top-level module masks a package-local import bug"
PY
