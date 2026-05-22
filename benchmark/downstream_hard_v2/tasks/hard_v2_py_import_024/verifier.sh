#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from omega_pkg_delta.main import preserve_marker, run
from omega_pkg_delta.workers.worker import work
assert run() == "hard-v2-package-delta"
assert work() == "hard-v2-package-delta"
assert preserve_marker() == "package-internal-hard-v2-24"
assert not Path("workers").exists(), "top-level package masks the package-internal import bug"
PY
