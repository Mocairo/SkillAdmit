#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "benchmark" / "downstream" / "tasks"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content).lstrip(), encoding="utf-8")


def make_executable(path: Path) -> None:
    path.chmod(path.stat().st_mode | 0o111)


def write_task_json(task_dir: Path, payload: dict) -> None:
    write(task_dir / "task.json", json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def write_verifier(task_dir: Path) -> None:
    write(
        task_dir / "verifier.sh",
        """\
        #!/usr/bin/env bash
        set -e
        cd "$(dirname "$0")/repo"
        python -m pytest -q
        """,
    )
    make_executable(task_dir / "verifier.sh")


def create_t1_unused_missing_import(task_id: str, package_name: str, import_name: str) -> None:
    task_dir = TASKS_DIR / task_id
    repo = task_dir / "repo"

    write(
        repo / "app.py",
        f"""\
        import {import_name}

        def get_name():
            return "{package_name}"

        if __name__ == "__main__":
            print(get_name())
        """,
    )
    write(
        repo / "tests" / "test_app.py",
        f"""\
        from app import get_name

        def test_get_name():
            assert get_name() == "{package_name}"
        """,
    )
    write_task_json(
        task_dir,
        {
            "task_id": task_id,
            "family": "python_import_debug_downstream",
            "template": "T1_unused_missing_import",
            "instruction": "Fix the project so that the verifier passes.",
            "failing_command": "python app.py",
            "verifier": "bash verifier.sh",
            "expected_failure": f"ModuleNotFoundError: No module named '{import_name}'",
            "downstream_gold_skill": "Remove Unused Missing Imports",
        },
    )
    write_verifier(task_dir)


def create_t2_local_module(task_id: str, module_name: str, func_name: str, value: str) -> None:
    task_dir = TASKS_DIR / task_id
    repo = task_dir / "repo"

    write(
        repo / "app" / "main.py",
        f"""\
        from {module_name} import {func_name}

        def run():
            return {func_name}()
        """,
    )
    write(
        repo / "app" / f"{module_name}.py",
        f"""\
        def {func_name}():
            return "{value}"
        """,
    )
    write(
        repo / "tests" / "test_main.py",
        f"""\
        from app.main import run

        def test_run():
            assert run() == "{value}"
        """,
    )
    write_task_json(
        task_dir,
        {
            "task_id": task_id,
            "family": "python_import_debug_downstream",
            "template": "T2_local_module_import",
            "instruction": "Fix the project so that the verifier passes. Do not install unrelated packages.",
            "failing_command": "python -m pytest -q",
            "verifier": "bash verifier.sh",
            "expected_failure": f"ModuleNotFoundError: No module named '{module_name}'",
            "downstream_gold_skill": "Repair Local Module Imports",
        },
    )
    write_verifier(task_dir)


def create_t3_script_relative_import(task_id: str, package_name: str, helper_name: str, value: str) -> None:
    task_dir = TASKS_DIR / task_id
    repo = task_dir / "repo"

    write(repo / package_name / "__init__.py", "")
    write(
        repo / package_name / "main.py",
        f"""\
        from .{helper_name} import helper

        def run():
            return helper()

        if __name__ == "__main__":
            print(run())
        """,
    )
    write(
        repo / package_name / f"{helper_name}.py",
        f"""\
        def helper():
            return "{value}"
        """,
    )
    write(
        repo / "tests" / "test_main.py",
        f"""\
        import subprocess
        import sys

        def test_script_command_works():
            result = subprocess.run(
                [sys.executable, "{package_name}/main.py"],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, result.stderr
            assert "{value}" in result.stdout
        """,
    )
    write_task_json(
        task_dir,
        {
            "task_id": task_id,
            "family": "python_import_debug_downstream",
            "template": "T3_script_relative_import",
            "instruction": "Fix the project so that the verifier passes.",
            "failing_command": f"python {package_name}/main.py",
            "verifier": "bash verifier.sh",
            "expected_failure": "ImportError: attempted relative import with no known parent package",
            "downstream_gold_skill": "Repair Relative Imports for Script Execution",
        },
    )
    write_verifier(task_dir)


def create_t4_cwd_path(task_id: str, app_dir: str, data_file: str, value: str) -> None:
    task_dir = TASKS_DIR / task_id
    repo = task_dir / "repo"

    write(
        repo / app_dir / "loader.py",
        f"""\
        from pathlib import Path

        def load_value():
            return Path("{data_file}").read_text(encoding="utf-8").strip()
        """,
    )
    write(
        repo / app_dir / "main.py",
        """\
        from loader import load_value

        def run():
            return load_value()

        if __name__ == "__main__":
            print(run())
        """,
    )
    write(repo / data_file, f"{value}\n")
    write(
        repo / "tests" / "test_loader.py",
        f"""\
        import subprocess
        import sys

        def test_running_from_subdir_still_works():
            result = subprocess.run(
                [sys.executable, "main.py"],
                cwd="{app_dir}",
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, result.stderr
            assert "{value}" in result.stdout
        """,
    )
    write_task_json(
        task_dir,
        {
            "task_id": task_id,
            "family": "python_import_debug_downstream",
            "template": "T4_cwd_sensitive_path",
            "instruction": "Fix the project so that the verifier passes.",
            "failing_command": f"cd {app_dir} && python main.py",
            "verifier": "bash verifier.sh",
            "expected_failure": f"FileNotFoundError: {data_file}",
            "downstream_gold_skill": "Repair CWD-Sensitive File Paths",
        },
    )
    write_verifier(task_dir)


def create_t5_package_internal_import(task_id: str, package_name: str, subpackage_name: str, value: str) -> None:
    task_dir = TASKS_DIR / task_id
    repo = task_dir / "repo"

    write(repo / package_name / "__init__.py", "")
    write(repo / package_name / subpackage_name / "__init__.py", "")
    write(
        repo / package_name / subpackage_name / "worker.py",
        f"""\
        def work():
            return "{value}"
        """,
    )
    write(
        repo / package_name / "main.py",
        f"""\
        from {subpackage_name}.worker import work

        def run():
            return work()
        """,
    )
    write(
        repo / "tests" / "test_main.py",
        f"""\
        from {package_name}.main import run

        def test_run():
            assert run() == "{value}"
        """,
    )
    write_task_json(
        task_dir,
        {
            "task_id": task_id,
            "family": "python_import_debug_downstream",
            "template": "T5_package_internal_import",
            "instruction": "Fix the project so that the verifier passes.",
            "failing_command": "python -m pytest -q",
            "verifier": "bash verifier.sh",
            "expected_failure": f"ModuleNotFoundError: No module named '{subpackage_name}'",
            "downstream_gold_skill": "Repair Package-Internal Bare Imports",
        },
    )
    write_verifier(task_dir)


def main() -> None:
    if TASKS_DIR.exists():
        shutil.rmtree(TASKS_DIR)
    TASKS_DIR.mkdir(parents=True, exist_ok=True)

    specs = [
        ("down_py_import_001", create_t1_unused_missing_import, ("downstream_alpha", "futuredep_alpha")),
        ("down_py_import_002", create_t1_unused_missing_import, ("downstream_beta", "futuredep_beta")),
        ("down_py_import_003", create_t1_unused_missing_import, ("downstream_gamma", "futuredep_gamma")),
        ("down_py_import_004", create_t1_unused_missing_import, ("downstream_delta", "futuredep_delta")),
        ("down_py_import_005", create_t1_unused_missing_import, ("downstream_epsilon", "futuredep_epsilon")),
        ("down_py_import_006", create_t2_local_module, ("analytics", "load_metrics", "analytics-ok")),
        ("down_py_import_007", create_t2_local_module, ("settings", "read_settings", "settings-ok")),
        ("down_py_import_008", create_t2_local_module, ("transform", "run_transform", "transform-ok")),
        ("down_py_import_009", create_t2_local_module, ("filters", "apply_filters", "filters-ok")),
        ("down_py_import_010", create_t2_local_module, ("renderer", "render_view", "renderer-ok")),
        ("down_py_import_011", create_t3_script_relative_import, ("cmdpkg", "formatters", "script-format-ok")),
        ("down_py_import_012", create_t3_script_relative_import, ("jobpkg", "handlers", "script-handler-ok")),
        ("down_py_import_013", create_t3_script_relative_import, ("toolpkg", "operations", "script-operation-ok")),
        ("down_py_import_014", create_t3_script_relative_import, ("reportpkg", "writers", "script-writer-ok")),
        ("down_py_import_015", create_t3_script_relative_import, ("flowpkg", "steps", "script-step-ok")),
        ("down_py_import_016", create_t4_cwd_path, ("worker", "inputs/value.txt", "cwd-value-ok")),
        ("down_py_import_017", create_t4_cwd_path, ("processor", "resources/data.txt", "cwd-data-ok")),
        ("down_py_import_018", create_t4_cwd_path, ("runnerx", "configs/item.txt", "cwd-item-ok")),
        ("down_py_import_019", create_t4_cwd_path, ("batch", "payloads/message.txt", "cwd-message-ok")),
        ("down_py_import_020", create_t4_cwd_path, ("daemon", "fixtures/input.txt", "cwd-input-ok")),
        ("down_py_import_021", create_t5_package_internal_import, ("alpha_pkg", "internals", "internal-alpha-ok")),
        ("down_py_import_022", create_t5_package_internal_import, ("beta_pkg", "components", "internal-beta-ok")),
        ("down_py_import_023", create_t5_package_internal_import, ("gamma_pkg", "adapters", "internal-gamma-ok")),
        ("down_py_import_024", create_t5_package_internal_import, ("delta_pkg", "plugins", "internal-delta-ok")),
        ("down_py_import_025", create_t5_package_internal_import, ("epsilon_pkg", "modules", "internal-epsilon-ok")),
    ]

    for task_id, factory, args in specs:
        factory(task_id, *args)

    print(f"Generated {len(specs)} downstream tasks in {TASKS_DIR}")


if __name__ == "__main__":
    main()
