#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "benchmark" / "tasks"
FIXED_DIR = ROOT / "benchmark" / "fixed_tasks"


def write(path: Path, content: str) -> None:
    path.write_text(dedent(content).lstrip(), encoding="utf-8")


def copy_tasks() -> None:
    if FIXED_DIR.exists():
        shutil.rmtree(FIXED_DIR)
    shutil.copytree(TASKS_DIR, FIXED_DIR)


def get_task_dirs() -> list[Path]:
    return sorted(p for p in FIXED_DIR.iterdir() if p.is_dir())


def apply_t1(repo: Path, task_id: str) -> None:
    task_json = json.loads((repo.parent / "task.json").read_text(encoding="utf-8"))
    import_name = task_json["expected_failure"].split("'")[1]

    # The verifier should not require network access or real package installation.
    # We create a tiny local compatibility module so the import succeeds.
    write(repo / f"{import_name}.py", f"""\
    def __getattr__(name):
        raise AttributeError(name)
    """)


def apply_t2(repo: Path) -> None:
    main = repo / "app" / "main.py"
    text = main.read_text(encoding="utf-8")

    replacements = {
        "from utils import helper": "from app.utils import helper",
        "from config import load_config": "from app.config import load_config",
        "from service import run_service": "from app.service import run_service",
        "from parser import parse_text": "from app.parser import parse_text",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    write(main, text)


def apply_t3(repo: Path, task_json: dict) -> None:
    command = task_json["failing_command"]
    package_name = command.split()[1].split("/")[0]
    main = repo / package_name / "main.py"
    text = main.read_text(encoding="utf-8")

    replacements = {
        "from .utils import helper": "from utils import helper",
        "from .core import helper": "from core import helper",
        "from .worker import helper": "from worker import helper",
        "from .helper import helper": "from helper import helper",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    write(main, text)


def apply_t4(repo: Path, task_json: dict) -> None:
    command = task_json["failing_command"]
    app_dir = command.split("&&")[0].replace("cd", "").strip()
    loader = repo / app_dir / "loader.py"
    text = loader.read_text(encoding="utf-8")

    # Replace Path("some/relative/file") with a path anchored at the repo root.
    # __file__ is repo/app_dir/loader.py, so parent.parent is repo.
    text = text.replace(
        "return Path(",
        "return (Path(__file__).resolve().parent.parent / ",
    )

    write(loader, text)


def apply_t5(repo: Path, task_json: dict) -> None:
    package_name = task_json["expected_failure"].split("'")[1]
    # expected_failure stores the missing subpackage name, not the package name.
    # So infer package name from tests import line.
    test_file = repo / "tests" / "test_main.py"
    test_text = test_file.read_text(encoding="utf-8")
    first_line = test_text.splitlines()[0]
    package_name = first_line.split()[1].split(".")[0]

    main = repo / package_name / "main.py"
    text = main.read_text(encoding="utf-8")

    # Convert from subpackage.worker import work -> from .subpackage.worker import work
    text = text.replace("from core.worker import work", "from .core.worker import work")
    text = text.replace("from engine.worker import work", "from .engine.worker import work")
    text = text.replace("from services.worker import work", "from .services.worker import work")
    text = text.replace("from workers.worker import work", "from .workers.worker import work")

    write(main, text)


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
    copy_tasks()

    passed = []
    failed = []

    for task_dir in get_task_dirs():
        task_json = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
        repo = task_dir / "repo"
        template = task_json["template"]

        if template == "T1_missing_third_party_package":
            apply_t1(repo, task_dir.name)
        elif template == "T2_local_module_mistaken_as_missing_package":
            apply_t2(repo)
        elif template == "T3_relative_import_executed_as_script":
            apply_t3(repo, task_json)
        elif template == "T4_wrong_current_working_directory":
            apply_t4(repo, task_json)
        elif template == "T5_broken_package_structure":
            apply_t5(repo, task_json)
        else:
            raise ValueError(f"Unknown template: {template}")

        code, output = run_verifier(task_dir)

        print("=" * 80)
        print(task_dir.name)
        print(f"template: {template}")
        print(f"returncode: {code}")
        print(output[-1200:])

        if code == 0:
            passed.append(task_dir.name)
        else:
            failed.append(task_dir.name)

    print("=" * 80)
    print("SUMMARY")
    print(f"total: {len(passed) + len(failed)}")
    print(f"passed_after_gold_fix: {len(passed)}")
    print(f"failed_after_gold_fix: {len(failed)}")

    if failed:
        print("failed_tasks:")
        for task_id in failed:
            print(f"  - {task_id}")


if __name__ == "__main__":
    main()
