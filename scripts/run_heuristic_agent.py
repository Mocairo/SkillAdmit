#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "benchmark" / "task_manifest.jsonl"
RUN_DIR = ROOT / "benchmark" / "agent_runs" / "heuristic_agent_v0"
WORKSPACES = RUN_DIR / "workspaces"
OUT = RUN_DIR / "trajectories.jsonl"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write(path: Path, content: str) -> None:
    path.write_text(dedent(content).lstrip(), encoding="utf-8")


def run_cmd(cmd: list[str], cwd: Path) -> dict:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=30)
    return {
        "cmd": " ".join(cmd),
        "cwd": str(cwd),
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-1200:],
        "stderr_tail": proc.stderr[-1200:],
    }


def copy_workspace(task: dict) -> Path:
    src = ROOT / task["task_dir"]
    dst = WORKSPACES / task["task_id"]
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return dst


def inspect_files(repo: Path) -> list[str]:
    paths = sorted(
        p.relative_to(repo).as_posix()
        for p in repo.rglob("*.py")
        if "__pycache__" not in p.parts
    )
    return paths


def patch_t1(repo: Path, task: dict, actions: list[dict]) -> None:
    missing = task["expected_failure"].split("'")[1]
    target = repo / f"{missing}.py"
    write(target, """
    def __getattr__(name):
        raise AttributeError(name)
    """)
    actions.append({"action": "write_file", "path": str(target), "summary": f"created local stub for missing dependency {missing}"})


def patch_t2(repo: Path, actions: list[dict]) -> None:
    main = repo / "app" / "main.py"
    text = main.read_text(encoding="utf-8")
    old_text = text

    replacements = {
        "from utils import helper": "from app.utils import helper",
        "from config import load_config": "from app.config import load_config",
        "from service import run_service": "from app.service import run_service",
        "from parser import parse_text": "from app.parser import parse_text",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    write(main, text)
    actions.append({"action": "edit_file", "path": str(main), "changed": old_text != text, "summary": "converted bare local import to package-qualified import"})


def patch_t3(repo: Path, task: dict, actions: list[dict]) -> None:
    package_name = task["failing_command"].split()[1].split("/")[0]
    main = repo / package_name / "main.py"
    text = main.read_text(encoding="utf-8")
    old_text = text

    replacements = {
        "from .utils import helper": "from utils import helper",
        "from .core import helper": "from core import helper",
        "from .worker import helper": "from worker import helper",
        "from .helper import helper": "from helper import helper",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    write(main, text)
    actions.append({"action": "edit_file", "path": str(main), "changed": old_text != text, "summary": "changed relative import to script-mode-compatible import"})


def patch_t4(repo: Path, task: dict, actions: list[dict]) -> None:
    app_dir = task["failing_command"].split("&&")[0].replace("cd", "").strip()
    loader = repo / app_dir / "loader.py"
    text = loader.read_text(encoding="utf-8")
    old_text = text

    text = text.replace(
        "return Path(",
        "return (Path(__file__).resolve().parent.parent / ",
    )

    write(loader, text)
    actions.append({"action": "edit_file", "path": str(loader), "changed": old_text != text, "summary": "anchored relative path at repo root using __file__"})


def patch_t5(repo: Path, actions: list[dict]) -> None:
    test_file = repo / "tests" / "test_main.py"
    first_line = test_file.read_text(encoding="utf-8").splitlines()[0]
    package_name = first_line.split()[1].split(".")[0]
    main = repo / package_name / "main.py"
    text = main.read_text(encoding="utf-8")
    old_text = text

    replacements = {
        "from core.worker import work": "from .core.worker import work",
        "from engine.worker import work": "from .engine.worker import work",
        "from services.worker import work": "from .services.worker import work",
        "from workers.worker import work": "from .workers.worker import work",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    write(main, text)
    actions.append({"action": "edit_file", "path": str(main), "changed": old_text != text, "summary": "converted bare package-internal import to relative import"})


def run_agent(task: dict) -> dict:
    workspace = copy_workspace(task)
    repo = workspace / "repo"
    actions: list[dict] = []

    files = inspect_files(repo)
    actions.append({"action": "inspect_files", "files": files})

    initial = run_cmd(["bash", "verifier.sh"], workspace)
    actions.append({"action": "run_verifier_initial", "result": initial})

    template = task["template"]
    if template == "T1_missing_third_party_package":
        patch_t1(repo, task, actions)
    elif template == "T2_local_module_mistaken_as_missing_package":
        patch_t2(repo, actions)
    elif template == "T3_relative_import_executed_as_script":
        patch_t3(repo, task, actions)
    elif template == "T4_wrong_current_working_directory":
        patch_t4(repo, task, actions)
    elif template == "T5_broken_package_structure":
        patch_t5(repo, actions)
    else:
        actions.append({"action": "no_patch", "summary": f"unknown template {template}"})

    final = run_cmd(["bash", "verifier.sh"], workspace)
    actions.append({"action": "run_verifier_final", "result": final})

    success = final["returncode"] == 0

    return {
        "trajectory_id": f"heuristic_v0_{task['task_id']}",
        "agent": "heuristic_agent_v0",
        "task_id": task["task_id"],
        "family": task["family"],
        "template": task["template"],
        "workspace": str(workspace.relative_to(ROOT)),
        "success": success,
        "initial_returncode": initial["returncode"],
        "final_returncode": final["returncode"],
        "actions": actions,
        "trajectory_summary": {
            "observation": task["expected_failure"],
            "diagnosis": f"Heuristic repair selected from template {task['template']}.",
            "fix_pattern": actions[-2].get("summary", "No patch summary available.") if len(actions) >= 2 else "",
            "validation": "Verifier passed after patch." if success else "Verifier still failed after patch.",
        },
    }


def main() -> None:
    if RUN_DIR.exists():
        shutil.rmtree(RUN_DIR)
    WORKSPACES.mkdir(parents=True, exist_ok=True)

    tasks = read_jsonl(MANIFEST)
    rows = []

    for task in tasks:
        row = run_agent(task)
        rows.append(row)
        print(f"{task['task_id']}: success={row['success']}")

    OUT.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )

    passed = sum(1 for row in rows if row["success"])
    print(f"Wrote {len(rows)} trajectories to {OUT}")
    print(f"passed: {passed}/{len(rows)}")


if __name__ == "__main__":
    main()
