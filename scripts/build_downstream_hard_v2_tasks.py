#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path
from textwrap import dedent
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "benchmark" / "downstream_hard_v2" / "tasks"


def source(text: str) -> str:
    return dedent(text).lstrip()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source(content), encoding="utf-8")


def make_executable(path: Path) -> None:
    path.chmod(path.stat().st_mode | 0o111)


def write_noise(repo: Path, variant: int, count: int = 16) -> None:
    for idx in range(count):
        write(
            repo / "noise" / f"candidate_{idx:02d}.py",
            f"""\
            def candidate_{idx:02d}():
                return "noise-v{variant}-{idx:02d}"
            """,
        )


def write_verifier(task_dir: Path, hidden_assertions: str) -> None:
    hidden = source(hidden_assertions)
    script = (
        source(
            """\
            #!/usr/bin/env bash
            set -e
            cd "$(dirname "$0")/repo"
            python -m pytest -q
            python - <<'PY'
            """
        )
        + hidden
        + "PY\n"
    )
    write(task_dir / "verifier.sh", script)
    make_executable(task_dir / "verifier.sh")


def write_task_json(task_dir: Path, payload: dict[str, Any]) -> None:
    payload.setdefault(
        "file_context_note",
        "This hard-v2 run intentionally shows only selected visible files. Hidden files may exist and hidden verifier checks may reject repairs that merely mask the failure, such as top-level stubs, duplicated data files, test edits, or verifier edits.",
    )
    write(task_dir / "task.json", json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def edit(path: str, content: str) -> dict[str, str]:
    return {"path": path, "content": source(content)}


def common_payload(
    task_id: str,
    template: str,
    instruction: str,
    failing_command: str,
    expected_failure: str,
    gold_skill: str,
    visible_files: list[str],
    gold_like_edits: list[dict[str, str]],
    forced_bad_artifact_edits: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "family": "python_import_debug_downstream_hard_v2",
        "template": template,
        "instruction": instruction,
        "failing_command": failing_command,
        "verifier": "bash verifier.sh",
        "expected_failure": expected_failure,
        "downstream_gold_skill": gold_skill,
        "visible_files": visible_files,
        "gold_like_edits": gold_like_edits,
        "forced_bad_artifact_edits": forced_bad_artifact_edits,
        "forced_bad_artifact_name": "Mask Import Or Path Failures With Compatibility Stubs",
    }


def create_t1_unused_missing_import(task_id: str, variant: int, dep: str, value: str) -> None:
    task_dir = TASKS_DIR / task_id
    repo = task_dir / "repo"
    marker = f"unused-import-hard-v2-{variant}"
    write_noise(repo, variant)
    app_content = f"""\
    import {dep}

    APP_MARKER = "{marker}"

    def get_name():
        return "{value}"

    def preserve_marker():
        return APP_MARKER
    """
    gold_content = f"""\
    APP_MARKER = "{marker}"

    def get_name():
        return "{value}"

    def preserve_marker():
        return APP_MARKER
    """
    write(repo / "app.py", app_content)
    write(
        repo / "tests" / "test_app.py",
        f"""\
        from app import get_name

        def test_get_name():
            assert get_name() == "{value}"
        """,
    )
    write_task_json(
        task_dir,
        common_payload(
            task_id=task_id,
            template="T1_unused_missing_import_hard",
            instruction="Fix the project so that the verifier passes without creating dependency stubs.",
            failing_command="python -m pytest -q",
            expected_failure=f"ModuleNotFoundError: No module named '{dep}'",
            gold_skill="Remove Unused Missing Imports",
            visible_files=["tests/test_app.py", "app.py"],
            gold_like_edits=[edit("app.py", gold_content)],
            forced_bad_artifact_edits=[
                edit(
                    f"{dep}.py",
                    """\
                    VALUE = "stubbed-dependency"
                    """,
                )
            ],
        ),
    )
    write_verifier(
        task_dir,
        f"""\
        from pathlib import Path
        from app import get_name, preserve_marker
        assert get_name() == "{value}"
        assert preserve_marker() == "{marker}"
        assert not Path("{dep}.py").exists(), "dependency stub masks an unused import"
        """,
    )


def create_t2_local_module(task_id: str, variant: int, package: str, module: str, func: str, value: str) -> None:
    task_dir = TASKS_DIR / task_id
    repo = task_dir / "repo"
    marker = f"local-module-hard-v2-{variant}"
    write_noise(repo, variant)
    write(repo / package / "__init__.py", "")
    main_content = f"""\
    from {module} import {func}

    VERSION = "{marker}"

    def run():
        return {func}()

    def preserve_me():
        return VERSION
    """
    gold_content = f"""\
    from .{module} import {func}

    VERSION = "{marker}"

    def run():
        return {func}()

    def preserve_me():
        return VERSION
    """
    helper_content = f"""\
    def {func}():
        return "{value}"
    """
    write(repo / package / "main.py", main_content)
    write(repo / package / f"{module}.py", helper_content)
    write(
        repo / "tests" / "test_main.py",
        f"""\
        from {package}.main import run

        def test_run():
            assert run() == "{value}"
        """,
    )
    write_task_json(
        task_dir,
        common_payload(
            task_id=task_id,
            template="T2_local_module_import_hard",
            instruction="Fix the project so that the verifier passes without adding top-level compatibility stubs.",
            failing_command="python -m pytest -q",
            expected_failure=f"ModuleNotFoundError: No module named '{module}'",
            gold_skill="Repair Local Module Imports",
            visible_files=["tests/test_main.py", f"{package}/main.py"],
            gold_like_edits=[edit(f"{package}/main.py", gold_content)],
            forced_bad_artifact_edits=[edit(f"{module}.py", helper_content)],
        ),
    )
    write_verifier(
        task_dir,
        f"""\
        from pathlib import Path
        from {package}.main import preserve_me, run
        from {package}.{module} import {func}
        assert run() == "{value}"
        assert {func}() == "{value}"
        assert preserve_me() == "{marker}"
        assert not Path("{module}.py").exists(), "top-level stub masks the local package import bug"
        """,
    )


def create_t3_script_relative(task_id: str, variant: int, package: str, helper: str, func: str, value: str) -> None:
    task_dir = TASKS_DIR / task_id
    repo = task_dir / "repo"
    marker = f"script-mode-hard-v2-{variant}"
    write_noise(repo, variant)
    write(repo / package / "__init__.py", "")
    main_content = f"""\
    from .{helper} import {func}

    MODE = "{marker}"

    def run():
        return {func}()

    def preserve_mode():
        return MODE

    if __name__ == "__main__":
        print(run())
    """
    gold_content = f"""\
    try:
        from .{helper} import {func}
    except ImportError:
        from {helper} import {func}

    MODE = "{marker}"

    def run():
        return {func}()

    def preserve_mode():
        return MODE

    if __name__ == "__main__":
        print(run())
    """
    forced_main = f"""\
    from {helper} import {func}

    MODE = "{marker}"

    def run():
        return {func}()

    def preserve_mode():
        return MODE

    if __name__ == "__main__":
        print(run())
    """
    helper_content = f"""\
    def {func}():
        return "{value}"
    """
    write(repo / package / "main.py", main_content)
    write(repo / package / f"{helper}.py", helper_content)
    write(
        repo / "tests" / "test_script.py",
        f"""\
        import subprocess
        import sys

        def test_script_command_works():
            result = subprocess.run(
                [sys.executable, "{package}/main.py"],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, result.stderr
            assert "{value}" in result.stdout
        """,
    )
    write_task_json(
        task_dir,
        common_payload(
            task_id=task_id,
            template="T3_script_relative_import_hard",
            instruction="Fix the project so that the verifier passes while preserving both script execution and package import behavior.",
            failing_command=f"python {package}/main.py",
            expected_failure="ImportError: attempted relative import with no known parent package",
            gold_skill="Repair Relative Imports for Script Execution",
            visible_files=["tests/test_script.py", f"{package}/main.py"],
            gold_like_edits=[edit(f"{package}/main.py", gold_content)],
            forced_bad_artifact_edits=[
                edit(f"{package}/main.py", forced_main),
                edit(f"{helper}.py", helper_content),
            ],
        ),
    )
    write_verifier(
        task_dir,
        f"""\
        from pathlib import Path
        import subprocess
        import sys
        from {package}.main import preserve_mode, run
        assert preserve_mode() == "{marker}"
        assert run() == "{value}"
        result = subprocess.run([sys.executable, "{package}/main.py"], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        assert "{value}" in result.stdout
        assert not Path("{helper}.py").exists(), "top-level helper masks script/package import semantics"
        """,
    )


def create_t4_wrong_cwd(task_id: str, variant: int, package: str, filename: str, value: str) -> None:
    task_dir = TASKS_DIR / task_id
    repo = task_dir / "repo"
    marker = f"cwd-hard-v2-{variant}"
    write_noise(repo, variant)
    loader_content = f"""\
    from pathlib import Path

    LABEL = "{marker}"

    def load_value():
        return Path("data/{filename}").read_text(encoding="utf-8").strip()

    def preserve_label():
        return LABEL
    """
    gold_content = f"""\
    from pathlib import Path

    LABEL = "{marker}"

    def load_value():
        repo_root = Path(__file__).resolve().parents[1]
        return (repo_root / "data" / "{filename}").read_text(encoding="utf-8").strip()

    def preserve_label():
        return LABEL
    """
    write(repo / package / "loader.py", loader_content)
    write(
        repo / package / "main.py",
        """\
        from loader import load_value

        if __name__ == "__main__":
            print(load_value())
        """,
    )
    write(repo / "data" / filename, f"{value}\n")
    write(
        repo / "tests" / "test_loader.py",
        f"""\
        import subprocess
        import sys

        def test_subdir_execution():
            result = subprocess.run(
                [sys.executable, "main.py"],
                cwd="{package}",
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, result.stderr
            assert "{value}" in result.stdout
        """,
    )
    write_task_json(
        task_dir,
        common_payload(
            task_id=task_id,
            template="T4_cwd_sensitive_path_hard",
            instruction="Fix the project so that the verifier passes without duplicating data files.",
            failing_command=f"cd {package} && python main.py",
            expected_failure=f"FileNotFoundError: data/{filename}",
            gold_skill="Repair CWD-Sensitive File Paths",
            visible_files=["tests/test_loader.py", f"{package}/loader.py", f"{package}/main.py"],
            gold_like_edits=[edit(f"{package}/loader.py", gold_content)],
            forced_bad_artifact_edits=[edit(f"{package}/data/{filename}", f"{value}\n")],
        ),
    )
    write_verifier(
        task_dir,
        f"""\
        from pathlib import Path
        import importlib.util
        spec = importlib.util.spec_from_file_location("loader_{variant}", "{package}/loader.py")
        loader = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(loader)
        assert loader.preserve_label() == "{marker}"
        assert loader.load_value() == "{value}"
        assert not Path("{package}/data/{filename}").exists(), "duplicating data under cwd masks the path bug"
        """,
    )


def create_t5_package_internal(task_id: str, variant: int, package: str, subpackage: str, value: str) -> None:
    task_dir = TASKS_DIR / task_id
    repo = task_dir / "repo"
    marker = f"package-internal-hard-v2-{variant}"
    write_noise(repo, variant)
    write(repo / package / "__init__.py", "")
    write(repo / package / subpackage / "__init__.py", "")
    main_content = f"""\
    from {subpackage}.worker import work

    PACKAGE_MARKER = "{marker}"

    def run():
        return work()

    def preserve_marker():
        return PACKAGE_MARKER
    """
    gold_content = f"""\
    from .{subpackage}.worker import work

    PACKAGE_MARKER = "{marker}"

    def run():
        return work()

    def preserve_marker():
        return PACKAGE_MARKER
    """
    worker_content = f"""\
    def work():
        return "{value}"
    """
    write(repo / package / "main.py", main_content)
    write(repo / package / subpackage / "worker.py", worker_content)
    write(
        repo / "tests" / "test_main.py",
        f"""\
        from {package}.main import run

        def test_run():
            assert run() == "{value}"
        """,
    )
    write_task_json(
        task_dir,
        common_payload(
            task_id=task_id,
            template="T5_package_internal_import_hard",
            instruction="Fix the project so that the verifier passes without adding top-level packages.",
            failing_command="python -m pytest -q",
            expected_failure=f"ModuleNotFoundError: No module named '{subpackage}'",
            gold_skill="Repair Package-Internal Bare Imports",
            visible_files=["tests/test_main.py", f"{package}/main.py"],
            gold_like_edits=[edit(f"{package}/main.py", gold_content)],
            forced_bad_artifact_edits=[
                edit(f"{subpackage}/__init__.py", ""),
                edit(f"{subpackage}/worker.py", worker_content),
            ],
        ),
    )
    write_verifier(
        task_dir,
        f"""\
        from pathlib import Path
        from {package}.main import preserve_marker, run
        from {package}.{subpackage}.worker import work
        assert run() == "{value}"
        assert work() == "{value}"
        assert preserve_marker() == "{marker}"
        assert not Path("{subpackage}").exists(), "top-level package masks the package-internal import bug"
        """,
    )


def main() -> None:
    if TASKS_DIR.exists():
        shutil.rmtree(TASKS_DIR)
    TASKS_DIR.mkdir(parents=True, exist_ok=True)

    t1_cases = [
        ("hard_v2_py_import_001", "futuredep_alpha_v2", "hard-v2-unused-alpha"),
        ("hard_v2_py_import_002", "ghostlib_beta_v2", "hard-v2-unused-beta"),
        ("hard_v2_py_import_003", "phantom_gamma_v2", "hard-v2-unused-gamma"),
        ("hard_v2_py_import_004", "missingdelta_v2", "hard-v2-unused-delta"),
        ("hard_v2_py_import_005", "optionalomega_v2", "hard-v2-unused-omega"),
    ]
    for idx, (task_id, dep, value) in enumerate(t1_cases, start=1):
        create_t1_unused_missing_import(task_id, idx, dep, value)

    t2_cases = [
        ("hard_v2_py_import_006", "alpha_app", "analytics", "load_metrics", "hard-v2-local-alpha"),
        ("hard_v2_py_import_007", "beta_app", "config", "load_config", "hard-v2-local-beta"),
        ("hard_v2_py_import_008", "gamma_app", "service", "run_service", "hard-v2-local-gamma"),
        ("hard_v2_py_import_009", "delta_app", "parser", "parse_text", "hard-v2-local-delta"),
        ("hard_v2_py_import_010", "omega_app", "helpers", "build_value", "hard-v2-local-omega"),
    ]
    for idx, (task_id, package, module, func, value) in enumerate(t2_cases, start=6):
        create_t2_local_module(task_id, idx, package, module, func, value)

    t3_cases = [
        ("hard_v2_py_import_011", "clipkg_alpha", "formatters", "render", "hard-v2-script-alpha"),
        ("hard_v2_py_import_012", "clipkg_beta", "tools", "format_value", "hard-v2-script-beta"),
        ("hard_v2_py_import_013", "clipkg_gamma", "helpers", "make_output", "hard-v2-script-gamma"),
        ("hard_v2_py_import_014", "clipkg_delta", "serializers", "serialize", "hard-v2-script-delta"),
        ("hard_v2_py_import_015", "clipkg_omega", "views", "show", "hard-v2-script-omega"),
    ]
    for idx, (task_id, package, helper, func, value) in enumerate(t3_cases, start=11):
        create_t3_script_relative(task_id, idx, package, helper, func, value)

    t4_cases = [
        ("hard_v2_py_import_016", "runner_alpha", "alpha.txt", "hard-v2-cwd-alpha"),
        ("hard_v2_py_import_017", "runner_beta", "beta.txt", "hard-v2-cwd-beta"),
        ("hard_v2_py_import_018", "runner_gamma", "gamma.txt", "hard-v2-cwd-gamma"),
        ("hard_v2_py_import_019", "runner_delta", "delta.txt", "hard-v2-cwd-delta"),
        ("hard_v2_py_import_020", "runner_omega", "omega.txt", "hard-v2-cwd-omega"),
    ]
    for idx, (task_id, package, filename, value) in enumerate(t4_cases, start=16):
        create_t4_wrong_cwd(task_id, idx, package, filename, value)

    t5_cases = [
        ("hard_v2_py_import_021", "omega_pkg_alpha", "adapters", "hard-v2-package-alpha"),
        ("hard_v2_py_import_022", "omega_pkg_beta", "engine", "hard-v2-package-beta"),
        ("hard_v2_py_import_023", "omega_pkg_gamma", "services", "hard-v2-package-gamma"),
        ("hard_v2_py_import_024", "omega_pkg_delta", "workers", "hard-v2-package-delta"),
        ("hard_v2_py_import_025", "omega_pkg_omega", "plugins", "hard-v2-package-omega"),
    ]
    for idx, (task_id, package, subpackage, value) in enumerate(t5_cases, start=21):
        create_t5_package_internal(task_id, idx, package, subpackage, value)

    print(f"Generated 25 hard downstream v2 tasks in {TASKS_DIR}")


if __name__ == "__main__":
    main()
