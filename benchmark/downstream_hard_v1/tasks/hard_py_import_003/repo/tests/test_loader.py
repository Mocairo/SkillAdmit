import subprocess
import sys

def test_subdir_execution():
    result = subprocess.run(
        [sys.executable, "main.py"],
        cwd="service",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "hard-cwd-ok" in result.stdout
