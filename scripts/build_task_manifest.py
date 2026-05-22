#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "benchmark" / "tasks"
MANIFEST = ROOT / "benchmark" / "task_manifest.jsonl"


def main() -> None:
    rows = []

    for task_dir in sorted(p for p in TASKS_DIR.iterdir() if p.is_dir()):
        task_json_path = task_dir / "task.json"
        task = json.loads(task_json_path.read_text(encoding="utf-8"))

        row = {
            "task_id": task["task_id"],
            "family": task["family"],
            "template": task["template"],
            "instruction": task["instruction"],
            "failing_command": task["failing_command"],
            "verifier": task["verifier"],
            "expected_failure": task["expected_failure"],
            "task_dir": str(task_dir.relative_to(ROOT)),
            "repo_dir": str((task_dir / "repo").relative_to(ROOT)),
        }
        rows.append(row)

    MANIFEST.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )

    print(f"Wrote {len(rows)} tasks to {MANIFEST}")


if __name__ == "__main__":
    main()
