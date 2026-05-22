import subprocess
import sys


def test_command_script_entrypoint():
    result = subprocess.run(
        [sys.executable, "ops_gamma/tasks/migrate.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "migration-gamma" in result.stdout
