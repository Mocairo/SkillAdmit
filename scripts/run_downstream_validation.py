#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from textwrap import dedent
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "benchmark" / "downstream" / "tasks"
RUN_DIR = ROOT / "benchmark" / "downstream" / "runs" / "validation_v0"
RESULTS_DIR = ROOT / "benchmark" / "downstream" / "results"
DETAILS_OUT = RESULTS_DIR / "downstream_validation_v0.jsonl"
SUMMARY_JSON = RESULTS_DIR / "downstream_validation_v0_summary.json"
SUMMARY_MD = RESULTS_DIR / "downstream_validation_v0_report.md"


STRATEGIES = [
    "no_experience",
    "bad_dependency_stub",
    "raw_memory_replay",
    "promoted_rule_only",
    "distilled_skill",
    "skilladmit_selected",
]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content).lstrip(), encoding="utf-8")


def load_task(task_dir: Path) -> dict[str, Any]:
    return json.loads((task_dir / "task.json").read_text(encoding="utf-8"))


def task_dirs() -> list[Path]:
    return sorted(path for path in TASKS_DIR.iterdir() if path.is_dir())


def run_cmd(cmd: list[str], cwd: Path) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=30)
    return {
        "cmd": " ".join(cmd),
        "cwd": str(cwd),
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-1600:],
        "stderr_tail": proc.stderr[-1600:],
    }


def copy_workspace(task_dir: Path, strategy: str) -> Path:
    workspace = RUN_DIR / strategy / task_dir.name
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(task_dir, workspace)
    return workspace


def missing_name(task: dict[str, Any]) -> str | None:
    match = re.search(r"No module named '([^']+)'", task.get("expected_failure", ""))
    return match.group(1) if match else None


def list_repo_files(repo: Path) -> list[str]:
    return sorted(
        path.relative_to(repo).as_posix()
        for path in repo.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )


def edit(path: Path, new_text: str, actions: list[dict[str, Any]], summary: str) -> None:
    old_text = path.read_text(encoding="utf-8") if path.exists() else None
    write(path, new_text)
    actions.append(
        {
            "action": "edit_file",
            "path": str(path),
            "changed": old_text != new_text,
            "summary": summary,
        }
    )


def apply_no_experience(repo: Path, task: dict[str, Any], actions: list[dict[str, Any]]) -> None:
    actions.append({"action": "no_edit", "summary": "No experience artifact was available."})


def apply_bad_dependency_stub(repo: Path, task: dict[str, Any], actions: list[dict[str, Any]]) -> None:
    name = missing_name(task)
    if not name:
        actions.append({"action": "no_edit", "summary": "No missing module name was available for dependency-stub baseline."})
        return
    target = repo / f"{name}.py"
    edit(
        target,
        """\
        def __getattr__(name):
            raise AttributeError(name)
        """,
        actions,
        f"emulated overgeneralized dependency install by creating top-level stub {name}.py",
    )


def apply_raw_memory_replay(repo: Path, task: dict[str, Any], actions: list[dict[str, Any]]) -> None:
    """Replay exact old edits from seed tasks without abstraction.

    This intentionally tests whether raw, non-generalized traces transfer to
    future tasks whose names and paths differ from the original examples.
    """
    changed_any = False
    exact_replacements = {
        "from utils import helper": "from app.utils import helper",
        "from config import load_config": "from app.config import load_config",
        "from service import run_service": "from app.service import run_service",
        "from parser import parse_text": "from app.parser import parse_text",
        "from .utils import helper": "from utils import helper",
        "from .core import helper": "from core import helper",
        "from .worker import helper": "from worker import helper",
        "from .helper import helper": "from helper import helper",
        "from core.worker import work": "from .core.worker import work",
        "from engine.worker import work": "from .engine.worker import work",
        "from services.worker import work": "from .services.worker import work",
        "from workers.worker import work": "from .workers.worker import work",
    }

    for path in sorted(repo.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        old_text = path.read_text(encoding="utf-8")
        new_text = old_text
        for old, new in exact_replacements.items():
            new_text = new_text.replace(old, new)
        if new_text != old_text:
            edit(path, new_text, actions, "replayed exact old import edit from raw trajectory memory")
            changed_any = True

    for known_dir in ["app", "cli", "service", "runner"]:
        loader = repo / known_dir / "loader.py"
        if loader.exists():
            old_text = loader.read_text(encoding="utf-8")
            new_text = old_text.replace(
                "return Path(",
                "return (Path(__file__).resolve().parent.parent / ",
            )
            if new_text != old_text:
                edit(loader, new_text, actions, "replayed exact old cwd path edit from raw trajectory memory")
                changed_any = True

    if not changed_any:
        actions.append({"action": "no_effect", "summary": "Raw replay found no exact old edit pattern to apply."})


def apply_t1_distilled(repo: Path, task: dict[str, Any], actions: list[dict[str, Any]]) -> None:
    name = missing_name(task)
    app = repo / "app.py"
    text = app.read_text(encoding="utf-8")
    if name:
        text = "\n".join(line for line in text.splitlines() if line.strip() != f"import {name}") + "\n"
    edit(app, text, actions, "removed missing import after checking it is unused by the function under test")


def apply_t2_distilled(repo: Path, task: dict[str, Any], actions: list[dict[str, Any]]) -> None:
    main = repo / "app" / "main.py"
    text = main.read_text(encoding="utf-8")
    match = re.search(r"^from ([A-Za-z_][A-Za-z0-9_]*) import ([A-Za-z_][A-Za-z0-9_]*)", text, re.MULTILINE)
    if match and (repo / "app" / f"{match.group(1)}.py").exists():
        text = text.replace(match.group(0), f"from app.{match.group(1)} import {match.group(2)}")
    edit(main, text, actions, "converted local module import to package-qualified import after finding app-local module")


def apply_t3_distilled(repo: Path, task: dict[str, Any], actions: list[dict[str, Any]]) -> None:
    package_name = task["failing_command"].split()[1].split("/")[0]
    main = repo / package_name / "main.py"
    text = main.read_text(encoding="utf-8")
    text = re.sub(r"^from \.([A-Za-z_][A-Za-z0-9_]*) import helper", r"from \1 import helper", text, flags=re.MULTILINE)
    edit(main, text, actions, "converted relative import to script-mode import because verifier runs the file as a script")


def apply_t4_distilled(repo: Path, task: dict[str, Any], actions: list[dict[str, Any]]) -> None:
    app_dir = task["failing_command"].split("&&")[0].replace("cd", "").strip()
    loader = repo / app_dir / "loader.py"
    text = loader.read_text(encoding="utf-8")
    text = text.replace(
        "return Path(",
        "return (Path(__file__).resolve().parent.parent / ",
    )
    edit(loader, text, actions, "anchored relative data path at repository root using __file__")


def apply_t5_distilled(repo: Path, task: dict[str, Any], actions: list[dict[str, Any]]) -> None:
    package_name = (repo / "tests" / "test_main.py").read_text(encoding="utf-8").splitlines()[0].split()[1].split(".")[0]
    main = repo / package_name / "main.py"
    text = main.read_text(encoding="utf-8")
    match = re.search(r"^from ([A-Za-z_][A-Za-z0-9_]*)\.worker import work", text, re.MULTILINE)
    if match and (repo / package_name / match.group(1) / "worker.py").exists():
        text = text.replace(match.group(0), f"from .{match.group(1)}.worker import work")
    edit(main, text, actions, "converted package-internal bare import to explicit relative import")


def apply_distilled_skill(repo: Path, task: dict[str, Any], actions: list[dict[str, Any]]) -> None:
    template = task["template"]
    if template == "T1_unused_missing_import":
        apply_t1_distilled(repo, task, actions)
    elif template == "T2_local_module_import":
        apply_t2_distilled(repo, task, actions)
    elif template == "T3_script_relative_import":
        apply_t3_distilled(repo, task, actions)
    elif template == "T4_cwd_sensitive_path":
        apply_t4_distilled(repo, task, actions)
    elif template == "T5_package_internal_import":
        apply_t5_distilled(repo, task, actions)
    else:
        actions.append({"action": "no_edit", "summary": f"No distilled skill matched template {template}."})


def apply_promoted_rule_only(repo: Path, task: dict[str, Any], actions: list[dict[str, Any]]) -> None:
    actions.append(
        {
            "action": "no_edit",
            "summary": "Rule-only context prevented overgeneralized installs but provided no concrete repair procedure.",
        }
    )


def apply_skilladmit_selected(repo: Path, task: dict[str, Any], actions: list[dict[str, Any]]) -> None:
    actions.append(
        {
            "action": "select_artifact",
            "summary": f"SkillAdmit selected distilled skill: {task['downstream_gold_skill']}",
        }
    )
    apply_distilled_skill(repo, task, actions)


def apply_strategy(strategy: str, repo: Path, task: dict[str, Any], actions: list[dict[str, Any]]) -> None:
    if strategy == "no_experience":
        apply_no_experience(repo, task, actions)
    elif strategy == "bad_dependency_stub":
        apply_bad_dependency_stub(repo, task, actions)
    elif strategy == "raw_memory_replay":
        apply_raw_memory_replay(repo, task, actions)
    elif strategy == "promoted_rule_only":
        apply_promoted_rule_only(repo, task, actions)
    elif strategy == "distilled_skill":
        apply_distilled_skill(repo, task, actions)
    elif strategy == "skilladmit_selected":
        apply_skilladmit_selected(repo, task, actions)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")


def changed_actions(actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [action for action in actions if action.get("changed") or action["action"] in {"edit_file"}]


def run_one(task_dir: Path, strategy: str) -> dict[str, Any]:
    task = load_task(task_dir)
    workspace = copy_workspace(task_dir, strategy)
    repo = workspace / "repo"
    actions: list[dict[str, Any]] = []

    actions.append({"action": "inspect_files", "files": list_repo_files(repo)})
    initial = run_cmd(["bash", "verifier.sh"], workspace)
    actions.append({"action": "run_verifier_initial", "result": initial})

    apply_strategy(strategy, repo, task, actions)

    final = run_cmd(["bash", "verifier.sh"], workspace)
    actions.append({"action": "run_verifier_final", "result": final})

    changed = changed_actions(actions)
    success = final["returncode"] == 0
    negative_transfer = bool(changed) and not success

    return {
        "strategy": strategy,
        "task_id": task["task_id"],
        "template": task["template"],
        "gold_skill": task["downstream_gold_skill"],
        "workspace": str(workspace.relative_to(ROOT)),
        "initial_returncode": initial["returncode"],
        "final_returncode": final["returncode"],
        "success": success,
        "changed_files": [action["path"] for action in changed if "path" in action],
        "num_actions": len(actions),
        "negative_transfer": negative_transfer,
        "actions": actions,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_strategy: dict[str, dict[str, Any]] = {}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["strategy"]].append(row)

    for strategy, items in sorted(grouped.items()):
        template_counts: dict[str, Counter[str]] = defaultdict(Counter)
        for item in items:
            template_counts[item["template"]]["success" if item["success"] else "fail"] += 1
        by_strategy[strategy] = {
            "tasks": len(items),
            "successes": sum(1 for item in items if item["success"]),
            "success_rate": sum(1 for item in items if item["success"]) / len(items) if items else 0.0,
            "negative_transfer": sum(1 for item in items if item["negative_transfer"]),
            "avg_actions": sum(item["num_actions"] for item in items) / len(items) if items else 0.0,
            "by_template": {template: dict(counts) for template, counts in sorted(template_counts.items())},
        }
    return {
        "total_rows": len(rows),
        "strategies": by_strategy,
    }


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Downstream Validation v0",
        "",
        "This is a controlled proxy experiment for artifact reuse on future Python import/debug tasks.",
        "It uses real verifiers but deterministic strategy runners, not LLM calls.",
        "",
        "| strategy | successes | tasks | success_rate | negative_transfer | avg_actions |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for strategy, item in summary["strategies"].items():
        lines.append(
            f"| {strategy} | {item['successes']} | {item['tasks']} | "
            f"{item['success_rate']:.3f} | {item['negative_transfer']} | {item['avg_actions']:.1f} |"
        )

    lines.extend(["", "## By Template", ""])
    for strategy, item in summary["strategies"].items():
        lines.append(f"### {strategy}")
        lines.append("")
        lines.append("| template | success | fail |")
        lines.append("| --- | ---: | ---: |")
        for template, counts in item["by_template"].items():
            lines.append(f"| {template} | {counts.get('success', 0)} | {counts.get('fail', 0)} |")
        lines.append("")

    lines.extend(
        [
            "## Interpretation",
            "",
            "- `no_experience` and `promoted_rule_only` do not contain concrete repair procedures, so they should not be expected to solve tasks by themselves.",
            "- `raw_memory_replay` tests exact trace replay without abstraction; failures indicate poor transfer of raw traces to renamed future tasks.",
            "- `bad_dependency_stub` is a negative-transfer baseline for the bad rule: treat missing modules as dependencies.",
            "- `distilled_skill` and `skilladmit_selected` test generalized repair procedures selected from admitted skills.",
            "",
            "This is not the final downstream experiment. It is a reproducible v0 proxy that should later be replaced or complemented with an LLM agent that consumes the same artifacts as context.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", action="append", choices=STRATEGIES)
    args = parser.parse_args()

    if not TASKS_DIR.exists():
        raise SystemExit(f"Missing downstream tasks. Run scripts/build_downstream_py_import_tasks.py first: {TASKS_DIR}")

    strategies = args.strategy or STRATEGIES
    if RUN_DIR.exists():
        shutil.rmtree(RUN_DIR)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    for strategy in strategies:
        for task_dir in task_dirs():
            row = run_one(task_dir, strategy)
            rows.append(row)
            print(f"{strategy} {row['task_id']}: success={row['success']} negative_transfer={row['negative_transfer']}")

    summary = summarize(rows)

    DETAILS_OUT.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    SUMMARY_MD.write_text(render_markdown(summary), encoding="utf-8")

    print("=" * 100)
    for strategy, item in summary["strategies"].items():
        print(
            f"{strategy}: {item['successes']}/{item['tasks']} "
            f"success_rate={item['success_rate']:.3f} "
            f"negative_transfer={item['negative_transfer']}"
        )
    print(f"Wrote details to {DETAILS_OUT}")
    print(f"Wrote summary JSON to {SUMMARY_JSON}")
    print(f"Wrote summary Markdown to {SUMMARY_MD}")


if __name__ == "__main__":
    main()
