#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from omega_pkg_gamma.main import preserve_marker, run
from omega_pkg_gamma.services.worker import work
assert run() == "hard-v2-package-gamma"
assert work() == "hard-v2-package-gamma"
assert preserve_marker() == "package-internal-hard-v2-23"
assert not Path("services").exists(), "top-level package masks the package-internal import bug"
PY
