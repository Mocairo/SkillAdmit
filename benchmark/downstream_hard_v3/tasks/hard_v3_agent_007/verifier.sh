#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from orders_beta.api import preserve_marker, render_order
from orders_beta.serializers import serialize_order
assert render_order("B23") == "order-beta:B23"
assert serialize_order("C31") == "order-beta:C31"
assert preserve_marker() == "hard-v3-local-import-7"
assert not Path("serializers.py").exists(), "top-level module masks a package-local import bug"
PY
