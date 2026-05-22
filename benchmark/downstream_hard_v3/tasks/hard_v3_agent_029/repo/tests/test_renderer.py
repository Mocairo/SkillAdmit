import subprocess
import sys


def test_report_command_from_job_dir():
    result = subprocess.run(
        [sys.executable, "main.py", "Ada"],
        cwd="job_delta",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "report-delta:Ada" in result.stdout
