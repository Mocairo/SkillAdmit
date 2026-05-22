#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from omega_pkg_beta.main import preserve_marker, run
from omega_pkg_beta.engine.worker import work
assert run() == "hard-v2-package-beta"
assert work() == "hard-v2-package-beta"
assert preserve_marker() == "package-internal-hard-v2-22"
assert not Path("engine").exists(), "top-level package masks the package-internal import bug"
PY
