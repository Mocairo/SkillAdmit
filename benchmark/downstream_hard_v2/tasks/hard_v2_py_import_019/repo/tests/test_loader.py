import subprocess
import sys

def test_subdir_execution():
    result = subprocess.run(
        [sys.executable, "main.py"],
        cwd="runner_delta",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "hard-v2-cwd-delta" in result.stdout
