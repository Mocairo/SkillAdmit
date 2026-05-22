import subprocess
import sys


def test_job_command_reads_repo_config_from_worker_dir():
    result = subprocess.run(
        [sys.executable, "job.py"],
        cwd="worker_gamma",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "ap-gamma" in result.stdout
