import subprocess
import sys


def test_preview_from_package_dir():
    result = subprocess.run(
        [sys.executable, "preview.py", "Ada"],
        cwd="notice_gamma",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "notice-gamma:Ada" in result.stdout
