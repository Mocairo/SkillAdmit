#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from orders_delta.api import preserve_marker, render_order
from orders_delta.summaries import summarize_order
assert render_order("B23") == "order-delta:B23"
assert summarize_order("C31") == "order-delta:C31"
assert preserve_marker() == "hard-v3-local-import-9"
assert not Path("summaries.py").exists(), "top-level module masks a package-local import bug"
PY
