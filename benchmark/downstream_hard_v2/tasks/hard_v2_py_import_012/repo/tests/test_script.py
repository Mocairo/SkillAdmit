import subprocess
import sys

def test_script_command_works():
    result = subprocess.run(
        [sys.executable, "clipkg_beta/main.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "hard-v2-script-beta" in result.stdout
