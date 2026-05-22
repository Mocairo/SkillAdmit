import subprocess
import sys

def test_running_from_subdir_still_works():
    result = subprocess.run(
        [sys.executable, "main.py"],
        cwd="processor",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "cwd-data-ok" in result.stdout
