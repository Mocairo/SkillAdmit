import subprocess
import sys

def test_script_command_works():
    result = subprocess.run(
        [sys.executable, "toolpkg/main.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "script-operation-ok" in result.stdout
