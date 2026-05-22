import subprocess
import sys

def test_script_command_works():
    result = subprocess.run(
        [sys.executable, "flowpkg/main.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "script-step-ok" in result.stdout
