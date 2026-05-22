#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from omega_pkg_omega.main import preserve_marker, run
from omega_pkg_omega.plugins.worker import work
assert run() == "hard-v2-package-omega"
assert work() == "hard-v2-package-omega"
assert preserve_marker() == "package-internal-hard-v2-25"
assert not Path("plugins").exists(), "top-level package masks the package-internal import bug"
PY
