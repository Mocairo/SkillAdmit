import subprocess
import sys


def test_report_command_from_job_dir():
    result = subprocess.run(
        [sys.executable, "main.py", "Ada"],
        cwd="job_beta",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "report-beta:Ada" in result.stdout
