#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "benchmark" / "downstream_hard_v1" / "tasks"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dedent(content).lstrip(), encoding="utf-8")


def make_executable(path: Path) -> None:
    path.chmod(path.stat().st_mode | 0o111)


def write_noise(repo: Path, count: int = 12) -> None:
    for idx in range(count):
        write(
            repo / "noise" / f"candidate_{idx:02d}.py",
            f"""\
            def candidate_{idx:02d}():
                return "noise-{idx:02d}"
            """,
        )


def write_task_json(task_dir: Path, payload: dict) -> None:
    payload.setdefault(
        "file_context_note",
        "This hard-v1 run may show only a budgeted subset of files. Hidden files can exist and verifier checks may depend on preserving source behavior, so avoid broad rewrites and avoid adding top-level stubs unless clearly justified.",
    )
    write(task_dir / "task.json", json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def write_verifier(task_dir: Path, hidden_assertions: str) -> None:
    hidden = dedent(hidden_assertions).lstrip()
    script = (
        dedent(
            """\
            #!/usr/bin/env bash
            set -e
            cd "$(dirname "$0")/repo"
            python -m pytest -q
            python - <<'PY'
            """
        ).lstrip()
        + hidden
        + "PY\n"
    )
    write(task_dir / "verifier.sh", script)
    make_executable(task_dir / "verifier.sh")


def create_t2_hard() -> None:
    task_dir = TASKS_DIR / "hard_py_import_001"
    repo = task_dir / "repo"
    write_noise(repo)
    write(repo / "app" / "__init__.py", "")
    write(
        repo / "app" / "main.py",
        """\
        from analytics import load_metrics

        VERSION = "hard-local-module-v1"

        def run():
            return load_metrics()

        def preserve_me():
            return VERSION
        """,
    )
    write(
        repo / "app" / "analytics.py",
        """\
        def load_metrics():
            return "hard-analytics-ok"
        """,
    )
    write(
        repo / "tests" / "test_main.py",
        """\
        from app.main import run

        def test_run():
            assert run() == "hard-analytics-ok"
        """,
    )
    write_task_json(
        task_dir,
        {
            "task_id": "hard_py_import_001",
            "family": "python_import_debug_downstream_hard_v1",
            "template": "T2_local_module_import_hard",
            "instruction": "Fix the project so that the verifier passes without adding top-level compatibility stubs.",
            "failing_command": "python -m pytest -q",
            "verifier": "bash verifier.sh",
            "expected_failure": "ModuleNotFoundError: No module named 'analytics'",
            "downstream_gold_skill": "Repair Local Module Imports",
            "visible_files": ["tests/test_main.py", "app/main.py"],
        },
    )
    write_verifier(
        task_dir,
        """\
        from pathlib import Path
        from app.main import preserve_me, run
        from app.analytics import load_metrics
        assert run() == "hard-analytics-ok"
        assert load_metrics() == "hard-analytics-ok"
        assert preserve_me() == "hard-local-module-v1"
        assert not Path("analytics.py").exists(), "top-level stub masks the import bug"
        """,
    )


def create_t3_hard() -> None:
    task_dir = TASKS_DIR / "hard_py_import_002"
    repo = task_dir / "repo"
    write_noise(repo)
    write(repo / "clipkg" / "__init__.py", "")
    write(
        repo / "clipkg" / "main.py",
        """\
        from .formatters import helper

        MODE = "script-mode-required"

        def run():
            return helper()

        def preserve_mode():
            return MODE

        if __name__ == "__main__":
            print(run())
        """,
    )
    write(
        repo / "clipkg" / "formatters.py",
        """\
        def helper():
            return "hard-script-ok"
        """,
    )
    write(
        repo / "tests" / "test_script.py",
        """\
        import subprocess
        import sys

        def test_script_command_works():
            result = subprocess.run(
                [sys.executable, "clipkg/main.py"],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, result.stderr
            assert "hard-script-ok" in result.stdout
        """,
    )
    write_task_json(
        task_dir,
        {
            "task_id": "hard_py_import_002",
            "family": "python_import_debug_downstream_hard_v1",
            "template": "T3_script_relative_import_hard",
            "instruction": "Fix the project so that the verifier passes while preserving script execution.",
            "failing_command": "python clipkg/main.py",
            "verifier": "bash verifier.sh",
            "expected_failure": "ImportError: attempted relative import with no known parent package",
            "downstream_gold_skill": "Repair Relative Imports for Script Execution",
            "visible_files": ["tests/test_script.py", "clipkg/main.py"],
        },
    )
    write_verifier(
        task_dir,
        """\
        import subprocess
        import sys
        from clipkg.main import preserve_mode
        assert preserve_mode() == "script-mode-required"
        result = subprocess.run([sys.executable, "clipkg/main.py"], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        assert "hard-script-ok" in result.stdout
        """,
    )


def create_t4_hard() -> None:
    task_dir = TASKS_DIR / "hard_py_import_003"
    repo = task_dir / "repo"
    write_noise(repo)
    write(
        repo / "service" / "loader.py",
        """\
        from pathlib import Path

        LABEL = "cwd-hard-v1"

        def load_value():
            return Path("data/value.txt").read_text(encoding="utf-8").strip()

        def preserve_label():
            return LABEL
        """,
    )
    write(
        repo / "service" / "main.py",
        """\
        from loader import load_value

        if __name__ == "__main__":
            print(load_value())
        """,
    )
    write(repo / "data" / "value.txt", "hard-cwd-ok\n")
    write(
        repo / "tests" / "test_loader.py",
        """\
        import subprocess
        import sys

        def test_subdir_execution():
            result = subprocess.run(
                [sys.executable, "main.py"],
                cwd="service",
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, result.stderr
            assert "hard-cwd-ok" in result.stdout
        """,
    )
    write_task_json(
        task_dir,
        {
            "task_id": "hard_py_import_003",
            "family": "python_import_debug_downstream_hard_v1",
            "template": "T4_cwd_sensitive_path_hard",
            "instruction": "Fix the project so that the verifier passes without duplicating data files.",
            "failing_command": "cd service && python main.py",
            "verifier": "bash verifier.sh",
            "expected_failure": "FileNotFoundError: data/value.txt",
            "downstream_gold_skill": "Repair CWD-Sensitive File Paths",
            "visible_files": ["tests/test_loader.py", "service/loader.py", "service/main.py"],
        },
    )
    write_verifier(
        task_dir,
        """\
        from pathlib import Path
        import importlib.util
        spec = importlib.util.spec_from_file_location("loader", "service/loader.py")
        loader = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(loader)
        assert loader.preserve_label() == "cwd-hard-v1"
        assert loader.load_value() == "hard-cwd-ok"
        assert not Path("service/data/value.txt").exists(), "duplicating data under cwd masks the path bug"
        """,
    )


def create_t5_hard() -> None:
    task_dir = TASKS_DIR / "hard_py_import_004"
    repo = task_dir / "repo"
    write_noise(repo)
    write(repo / "omega_pkg" / "__init__.py", "")
    write(repo / "omega_pkg" / "adapters" / "__init__.py", "")
    write(
        repo / "omega_pkg" / "main.py",
        """\
        from adapters.worker import work

        PACKAGE_MARKER = "omega-hard-v1"

        def run():
            return work()

        def preserve_marker():
            return PACKAGE_MARKER
        """,
    )
    write(
        repo / "omega_pkg" / "adapters" / "worker.py",
        """\
        def work():
            return "hard-package-ok"
        """,
    )
    write(
        repo / "tests" / "test_main.py",
        """\
        from omega_pkg.main import run

        def test_run():
            assert run() == "hard-package-ok"
        """,
    )
    write_task_json(
        task_dir,
        {
            "task_id": "hard_py_import_004",
            "family": "python_import_debug_downstream_hard_v1",
            "template": "T5_package_internal_import_hard",
            "instruction": "Fix the project so that the verifier passes without adding top-level packages.",
            "failing_command": "python -m pytest -q",
            "verifier": "bash verifier.sh",
            "expected_failure": "ModuleNotFoundError: No module named 'adapters'",
            "downstream_gold_skill": "Repair Package-Internal Bare Imports",
            "visible_files": ["tests/test_main.py", "omega_pkg/main.py"],
        },
    )
    write_verifier(
        task_dir,
        """\
        from pathlib import Path
        from omega_pkg.main import preserve_marker, run
        from omega_pkg.adapters.worker import work
        assert run() == "hard-package-ok"
        assert work() == "hard-package-ok"
        assert preserve_marker() == "omega-hard-v1"
        assert not Path("adapters").exists(), "top-level package masks the package-internal import bug"
        """,
    )


def create_t1_hard() -> None:
    task_dir = TASKS_DIR / "hard_py_import_005"
    repo = task_dir / "repo"
    write_noise(repo)
    write(
        repo / "app.py",
        """\
        import futuredep_hard

        APP_MARKER = "unused-import-hard-v1"

        def get_name():
            return "hard-unused-import-ok"

        def preserve_marker():
            return APP_MARKER
        """,
    )
    write(
        repo / "tests" / "test_app.py",
        """\
        from app import get_name

        def test_get_name():
            assert get_name() == "hard-unused-import-ok"
        """,
    )
    write_task_json(
        task_dir,
        {
            "task_id": "hard_py_import_005",
            "family": "python_import_debug_downstream_hard_v1",
            "template": "T1_unused_missing_import_hard",
            "instruction": "Fix the project so that the verifier passes without creating dependency stubs.",
            "failing_command": "python app.py",
            "verifier": "bash verifier.sh",
            "expected_failure": "ModuleNotFoundError: No module named 'futuredep_hard'",
            "downstream_gold_skill": "Remove Unused Missing Imports",
            "visible_files": ["tests/test_app.py", "app.py"],
        },
    )
    write_verifier(
        task_dir,
        """\
        from pathlib import Path
        from app import get_name, preserve_marker
        assert get_name() == "hard-unused-import-ok"
        assert preserve_marker() == "unused-import-hard-v1"
        assert not Path("futuredep_hard.py").exists(), "dependency stub masks unused import"
        """,
    )


def main() -> None:
    if TASKS_DIR.exists():
        shutil.rmtree(TASKS_DIR)
    TASKS_DIR.mkdir(parents=True, exist_ok=True)

    create_t2_hard()
    create_t3_hard()
    create_t4_hard()
    create_t5_hard()
    create_t1_hard()

    print(f"Generated 5 hard downstream tasks in {TASKS_DIR}")


if __name__ == "__main__":
    main()
