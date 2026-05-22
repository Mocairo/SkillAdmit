#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "benchmark" / "tasks"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content).lstrip(), encoding="utf-8")


def make_executable(path: Path) -> None:
    path.chmod(path.stat().st_mode | 0o111)


def write_task_json(task_dir: Path, payload: dict) -> None:
    write(task_dir / "task.json", json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def write_verifier(task_dir: Path) -> None:
    verifier = """\
    #!/usr/bin/env bash
    set -e
    cd "$(dirname "$0")/repo"
    python -m pytest -q
    """
    write(task_dir / "verifier.sh", verifier)
    make_executable(task_dir / "verifier.sh")


def create_t1_missing_third_party(task_id: str, package_name: str, import_name: str) -> None:
    task_dir = TASKS_DIR / task_id
    repo = task_dir / "repo"

    write(repo / "app.py", f"""\
    import {import_name}

    def get_name():
        return "{package_name}"

    if __name__ == "__main__":
        print(get_name())
    """)

    write(repo / "tests" / "test_app.py", f"""\
    from app import get_name

    def test_get_name():
        assert get_name() == "{package_name}"
    """)

    write_task_json(task_dir, {
        "task_id": task_id,
        "family": "python_import_debug",
        "template": "T1_missing_third_party_package",
        "instruction": "Fix the project so that the verifier passes.",
        "failing_command": "python app.py",
        "verifier": "bash verifier.sh",
        "expected_failure": f"ModuleNotFoundError: No module named '{import_name}'",
        "gold_hint": "This task represents a real missing third-party dependency."
    })
    write_verifier(task_dir)


def create_t2_local_module_task(task_id: str, module_name: str, func_name: str) -> None:
    task_dir = TASKS_DIR / task_id
    repo = task_dir / "repo"

    write(repo / "app" / "main.py", f"""\
    from {module_name} import {func_name}

    def run():
        return {func_name}()

    if __name__ == "__main__":
        print(run())
    """)

    write(repo / "app" / f"{module_name}.py", f"""\
    def {func_name}():
        return "local-module-ok"
    """)

    write(repo / "tests" / "test_main.py", """\
    from app.main import run

    def test_run():
        assert run() == "local-module-ok"
    """)

    write_task_json(task_dir, {
        "task_id": task_id,
        "family": "python_import_debug",
        "template": "T2_local_module_mistaken_as_missing_package",
        "instruction": "Fix the project so that the verifier passes. Do not install unrelated packages.",
        "failing_command": "python -m pytest -q",
        "verifier": "bash verifier.sh",
        "expected_failure": f"ModuleNotFoundError: No module named '{module_name}'",
        "gold_hint": "The missing module is local to the project, not a third-party package."
    })
    write_verifier(task_dir)


def create_t3_relative_import_script_task(task_id: str, package_name: str, helper_name: str) -> None:
    task_dir = TASKS_DIR / task_id
    repo = task_dir / "repo"

    write(repo / package_name / "__init__.py", "")

    write(repo / package_name / "main.py", f"""\
    from .{helper_name} import helper

    def run():
        return helper()

    if __name__ == "__main__":
        print(run())
    """)

    write(repo / package_name / f"{helper_name}.py", """\
    def helper():
        return "relative-import-ok"
    """)

    write(repo / "tests" / "test_main.py", f"""\
    import subprocess
    import sys

    def test_script_command_works():
        result = subprocess.run(
            [sys.executable, "{package_name}/main.py"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        assert "relative-import-ok" in result.stdout
    """)

    write_task_json(task_dir, {
        "task_id": task_id,
        "family": "python_import_debug",
        "template": "T3_relative_import_executed_as_script",
        "instruction": "Fix the project so that the verifier passes.",
        "failing_command": f"python {package_name}/main.py",
        "verifier": "bash verifier.sh",
        "expected_failure": "ImportError: attempted relative import with no known parent package",
        "gold_hint": "The file uses relative imports but is executed as a script."
    })
    write_verifier(task_dir)


def create_t4_wrong_cwd_task(task_id: str, app_dir: str, data_file: str) -> None:
    task_dir = TASKS_DIR / task_id
    repo = task_dir / "repo"

    write(repo / app_dir / "loader.py", f"""\
    from pathlib import Path

    def load_value():
        return Path("{data_file}").read_text(encoding="utf-8").strip()
    """)

    write(repo / app_dir / "main.py", """\
    from loader import load_value

    def run():
        return load_value()

    if __name__ == "__main__":
        print(run())
    """)

    write(repo / data_file, "cwd-ok\n")

    write(repo / "tests" / "test_loader.py", f"""\
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
        assert "cwd-ok" in result.stdout
    """)

    write_task_json(task_dir, {
        "task_id": task_id,
        "family": "python_import_debug",
        "template": "T4_wrong_current_working_directory",
        "instruction": "Fix the project so that the verifier passes.",
        "failing_command": f"cd {app_dir} && python main.py",
        "verifier": "bash verifier.sh",
        "expected_failure": f"FileNotFoundError: {data_file}",
        "gold_hint": "The code relies on the current working directory instead of a stable path."
    })
    write_verifier(task_dir)


def create_t5_missing_init_task(task_id: str, package_name: str, subpackage_name: str) -> None:
    task_dir = TASKS_DIR / task_id
    repo = task_dir / "repo"

    write(repo / package_name / "__init__.py", "")
    write(repo / package_name / subpackage_name / "__init__.py", "")

    write(repo / package_name / subpackage_name / "worker.py", """\
    def work():
        return "package-structure-ok"
    """)

    write(repo / package_name / "main.py", f"""\
    from {subpackage_name}.worker import work

    def run():
        return work()
    """)

    write(repo / "tests" / "test_main.py", f"""\
    from {package_name}.main import run

    def test_run():
        assert run() == "package-structure-ok"
    """)

    write_task_json(task_dir, {
        "task_id": task_id,
        "family": "python_import_debug",
        "template": "T5_broken_package_structure",
        "instruction": "Fix the project so that the verifier passes.",
        "failing_command": "python -m pytest -q",
        "verifier": "bash verifier.sh",
        "expected_failure": f"ModuleNotFoundError: No module named '{subpackage_name}'",
        "gold_hint": "The package structure exists, but main.py uses a bare import instead of a package-qualified import."
    })
    write_verifier(task_dir)



def main() -> None:
    if TASKS_DIR.exists():
        shutil.rmtree(TASKS_DIR)
    TASKS_DIR.mkdir(parents=True, exist_ok=True)

    specs = [
        ("py_import_001", create_t1_missing_third_party, ("missingdep_alpha", "missingdep_alpha")),
        ("py_import_002", create_t1_missing_third_party, ("missingdep_beta", "missingdep_beta")),
        ("py_import_003", create_t1_missing_third_party, ("missingdep_gamma", "missingdep_gamma")),
        ("py_import_004", create_t1_missing_third_party, ("missingdep_delta", "missingdep_delta")),

        ("py_import_005", create_t2_local_module_task, ("utils", "helper")),
        ("py_import_006", create_t2_local_module_task, ("config", "load_config")),
        ("py_import_007", create_t2_local_module_task, ("service", "run_service")),
        ("py_import_008", create_t2_local_module_task, ("parser", "parse_text")),

        ("py_import_009", create_t3_relative_import_script_task, ("app", "utils")),
        ("py_import_010", create_t3_relative_import_script_task, ("srcpkg", "core")),
        ("py_import_011", create_t3_relative_import_script_task, ("runnerpkg", "worker")),
        ("py_import_012", create_t3_relative_import_script_task, ("nestedpkg", "helper")),

        ("py_import_013", create_t4_wrong_cwd_task, ("app", "data/config.txt")),
        ("py_import_014", create_t4_wrong_cwd_task, ("cli", "assets/message.txt")),
        ("py_import_015", create_t4_wrong_cwd_task, ("service", "settings/value.txt")),
        ("py_import_016", create_t4_wrong_cwd_task, ("runner", "resources/input.txt")),

        ("py_import_017", create_t5_missing_init_task, ("app_pkg", "core")),
        ("py_import_018", create_t5_missing_init_task, ("toolkit", "engine")),
        ("py_import_019", create_t5_missing_init_task, ("projectpkg", "services")),
        ("py_import_020", create_t5_missing_init_task, ("samplepkg", "workers")),
    ]

    for task_id, factory, args in specs:
        factory(task_id, *args)

    print(f"Generated {len(specs)} tasks in {TASKS_DIR}")


if __name__ == "__main__":
    main()
