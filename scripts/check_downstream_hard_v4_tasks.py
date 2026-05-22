#!/usr/bin/env python3
"""Check deterministic validity of hard_v4 downstream tasks.

What this file does:
  Validates every generated hard_v4 task by checking four invariants:
  the initial repo fails, gold-like edits pass, forced-bad edits pass public
  pytest, and forced-bad edits fail the hidden verifier.

Why it is needed:
  hard_v4 should become a fresh downstream boundary only after the scaffold is
  mechanically sound. This checker lets us validate the generated tasks before
  any LLM API run or strategy comparison.

Inputs:
  benchmark/downstream_hard_v4/tasks/ by default, or a custom --tasks-dir.

Outputs:
  A text or JSON summary of task validity.

Who should run it:
  Researchers preparing or refreshing hard_v4 tasks. Passing this checker does
  not create LLM evidence; it only proves the deterministic benchmark scaffold.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TASKS_DIR = ROOT / "benchmark" / "downstream_hard_v4" / "tasks"


def clean_test_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    pytest_addopts = env.get("PYTEST_ADDOPTS", "").strip()
    cache_opt = "-p no:cacheprovider"
    if cache_opt not in pytest_addopts:
        env["PYTEST_ADDOPTS"] = f"{pytest_addopts} {cache_opt}".strip()
    return env


def run_cmd(cmd: list[str], cwd: Path, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=clean_test_env(),
    )


def load_task(task_dir: Path) -> dict[str, Any]:
    return json.loads((task_dir / "task.json").read_text(encoding="utf-8"))


def apply_edits(repo: Path, edits: list[dict[str, str]]) -> None:
    for item in edits:
        rel_path = item["path"]
        if rel_path.startswith("/") or ".." in Path(rel_path).parts:
            raise ValueError(f"Unsafe edit path: {rel_path}")
        path = repo / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(item["content"], encoding="utf-8")


def check_task(task_dir: Path) -> dict[str, Any]:
    task = load_task(task_dir)
    initial = run_cmd(["bash", "verifier.sh"], task_dir)

    with tempfile.TemporaryDirectory() as tmp:
        gold_dir = Path(tmp) / "gold" / task_dir.name
        shutil.copytree(task_dir, gold_dir)
        apply_edits(gold_dir / "repo", task["gold_like_edits"])
        gold = run_cmd(["bash", "verifier.sh"], gold_dir)

    with tempfile.TemporaryDirectory() as tmp:
        bad_dir = Path(tmp) / "forced_bad" / task_dir.name
        shutil.copytree(task_dir, bad_dir)
        apply_edits(bad_dir / "repo", task["forced_bad_artifact_edits"])
        public = run_cmd(["python", "-m", "pytest", "-q", "-p", "no:cacheprovider"], bad_dir / "repo")
        forced = run_cmd(["bash", "verifier.sh"], bad_dir)

    return {
        "task_id": task["task_id"],
        "template": task["template"],
        "gold_skill": task.get("downstream_gold_skill"),
        "initial_failed": initial.returncode != 0,
        "gold_passed": gold.returncode == 0,
        "forced_public_passed": public.returncode == 0,
        "forced_verifier_failed": forced.returncode != 0,
        "initial_returncode": initial.returncode,
        "gold_returncode": gold.returncode,
        "forced_public_returncode": public.returncode,
        "forced_verifier_returncode": forced.returncode,
        "initial_tail": (initial.stdout + initial.stderr)[-1000:],
        "gold_tail": (gold.stdout + gold.stderr)[-1000:],
        "forced_public_tail": (public.stdout + public.stderr)[-1000:],
        "forced_tail": (forced.stdout + forced.stderr)[-1000:],
    }


def build_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "total": len(rows),
        "initial_failed": sum(1 for row in rows if row["initial_failed"]),
        "gold_passed": sum(1 for row in rows if row["gold_passed"]),
        "forced_public_passed": sum(1 for row in rows if row["forced_public_passed"]),
        "forced_verifier_failed": sum(1 for row in rows if row["forced_verifier_failed"]),
    }
    by_template: dict[str, dict[str, int]] = {}
    for row in rows:
        bucket = by_template.setdefault(
            row["template"],
            {
                "total": 0,
                "initial_failed": 0,
                "gold_passed": 0,
                "forced_public_passed": 0,
                "forced_verifier_failed": 0,
            },
        )
        bucket["total"] += 1
        for key in ("initial_failed", "gold_passed", "forced_public_passed", "forced_verifier_failed"):
            bucket[key] += int(bool(row[key]))
    summary["by_template"] = by_template
    return summary


def bad_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row
        for row in rows
        if not (
            row["initial_failed"]
            and row["gold_passed"]
            and row["forced_public_passed"]
            and row["forced_verifier_failed"]
        )
    ]


def print_text(summary: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    print("SUMMARY")
    for key, value in summary.items():
        if key == "by_template":
            continue
        print(f"{key}: {value}")
    print("\nBY TEMPLATE")
    for template, item in sorted(summary["by_template"].items()):
        print(
            f"{template}: total={item['total']} "
            f"initial_failed={item['initial_failed']} "
            f"gold_passed={item['gold_passed']} "
            f"forced_public_passed={item['forced_public_passed']} "
            f"forced_verifier_failed={item['forced_verifier_failed']}"
        )

    failures = bad_rows(rows)
    if not failures:
        return
    print("\nFAILED CHECKS")
    for row in failures:
        print("=" * 100)
        print(row["task_id"], row["template"])
        print(
            "initial_failed=",
            row["initial_failed"],
            "gold_passed=",
            row["gold_passed"],
            "forced_public_passed=",
            row["forced_public_passed"],
            "forced_verifier_failed=",
            row["forced_verifier_failed"],
        )
        print("initial tail:")
        print(row["initial_tail"])
        print("gold tail:")
        print(row["gold_tail"])
        print("forced public tail:")
        print(row["forced_public_tail"])
        print("forced verifier tail:")
        print(row["forced_tail"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks-dir", type=Path, default=DEFAULT_TASKS_DIR)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tasks_dir = args.tasks_dir if args.tasks_dir.is_absolute() else ROOT / args.tasks_dir
    if not tasks_dir.exists():
        raise SystemExit(f"Missing tasks dir: {tasks_dir}")

    rows = [check_task(path) for path in sorted(path for path in tasks_dir.iterdir() if path.is_dir())]
    summary = build_summary(rows)
    if args.json:
        print(json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=2))
    else:
        print_text(summary, rows)
    if bad_rows(rows):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
