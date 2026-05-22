import subprocess
import sys


def test_worker_subdir_command_reads_repo_config():
    result = subprocess.run(
        [sys.executable, "main.py"],
        cwd="worker_omega",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "config-omega" in result.stdout
