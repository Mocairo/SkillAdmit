#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from omega_pkg.main import preserve_marker, run
from omega_pkg.adapters.worker import work
assert run() == "hard-package-ok"
assert work() == "hard-package-ok"
assert preserve_marker() == "omega-hard-v1"
assert not Path("adapters").exists(), "top-level package masks the package-internal import bug"
PY
