import subprocess
import sys


def test_export_script_entrypoint():
    result = subprocess.run(
        [sys.executable, "cli_gamma/tools/export.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "export-gamma" in result.stdout
