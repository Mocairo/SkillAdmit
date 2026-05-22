import subprocess
import sys


def test_export_script_entrypoint():
    result = subprocess.run(
        [sys.executable, "cli_alpha/commands/export.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "export-alpha" in result.stdout
