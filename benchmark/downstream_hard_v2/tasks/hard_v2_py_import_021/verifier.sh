#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/repo"
python -m pytest -q
python - <<'PY'
from pathlib import Path
from omega_pkg_alpha.main import preserve_marker, run
from omega_pkg_alpha.adapters.worker import work
assert run() == "hard-v2-package-alpha"
assert work() == "hard-v2-package-alpha"
assert preserve_marker() == "package-internal-hard-v2-21"
assert not Path("adapters").exists(), "top-level package masks the package-internal import bug"
PY
