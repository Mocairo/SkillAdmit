#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "benchmark" / "tasks"


def run_verifier(task_dir: Path) -> tuple[int, str]:
    proc = subprocess.run(
        ["bash", "verifier.sh"],
        cwd=task_dir,
        capture_output=True,
        text=True,
        timeout=20,
    )
    output = (proc.stdout + "\n" + proc.stderr).strip()
    return proc.returncode, output


def main() -> None:
    task_dirs = sorted(p for p in TASKS_DIR.iterdir() if p.is_dir())

    failed_as_expected = []
    unexpectedly_passed = []
    errored = []

    for task_dir in task_dirs:
        task_json = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
        try:
            code, output = run_verifier(task_dir)
        except Exception as exc:
            errored.append((task_dir.name, repr(exc)))
            continue

        if code != 0:
            failed_as_expected.append(task_dir.name)
        else:
            unexpectedly_passed.append(task_dir.name)

        print("=" * 80)
        print(task_dir.name)
        print(f"template: {task_json['template']}")
        print(f"returncode: {code}")
        print(output[-1200:])

    print("=" * 80)
    print("SUMMARY")
    print(f"total: {len(task_dirs)}")
    print(f"failed_as_expected: {len(failed_as_expected)}")
    print(f"unexpectedly_passed: {len(unexpectedly_passed)}")
    print(f"errored: {len(errored)}")

    if unexpectedly_passed:
        print("unexpectedly_passed_tasks:")
        for task_id in unexpectedly_passed:
            print(f"  - {task_id}")

    if errored:
        print("errored_tasks:")
        for task_id, err in errored:
            print(f"  - {task_id}: {err}")


if __name__ == "__main__":
    main()
