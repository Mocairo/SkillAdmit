#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
from pathlib import Path
from textwrap import dedent
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "benchmark" / "downstream_hard_v3" / "tasks"


def source(text: str) -> str:
    return dedent(text).lstrip()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source(content), encoding="utf-8")


def make_executable(path: Path) -> None:
    path.chmod(path.stat().st_mode | 0o111)


def edit(path: str, content: str) -> dict[str, str]:
    return {"path": path, "content": source(content)}


def write_noise(repo: Path, variant: int, count: int = 3) -> None:
    for idx in range(count):
        write(
            repo / "dev_notes" / f"candidate_fix_{idx:02d}.py",
            f"""\
            def candidate_fix_{idx:02d}():
                return "hard-v3-noise-{variant}-{idx:02d}"
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
        (
            "Hard v3 intentionally shows only the files a coding agent is likely "
            "to inspect first. Other repository files may exist. Hidden verifier "
            "checks reject public-test masking repairs such as stubs, copied "
            "resources, top-level compatibility packages, test edits, or verifier edits."
        ),
    )
    write(task_dir / "task.json", json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


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
        "family": "python_coding_agent_downstream_hard_v3",
        "template": template,
        "instruction": instruction,
        "failing_command": failing_command,
        "verifier": "bash verifier.sh",
        "expected_failure": expected_failure,
        "downstream_gold_skill": gold_skill,
        "visible_files": visible_files,
        "gold_like_edits": gold_like_edits,
        "forced_bad_artifact_edits": forced_bad_artifact_edits,
        "forced_bad_artifact_name": "Apply a public-passing masking repair instead of the intended repo-aware fix.",
    }


def create_t1_optional_import(task_id: str, variant: int, package: str, dep: str, prefix: str) -> None:
    task_dir = TASKS_DIR / task_id
    repo = task_dir / "repo"
    marker = f"hard-v3-optional-import-{variant}"
    write_noise(repo, variant)
    write(repo / package / "__init__.py", "")
    broken = f"""\
    import {dep}

    SERVICE_MARKER = "{marker}"

    def build_response(payload):
        return "{prefix}:" + str(payload["id"])

    def preserve_marker():
        return SERVICE_MARKER
    """
    fixed = f"""\
    SERVICE_MARKER = "{marker}"

    def build_response(payload):
        return "{prefix}:" + str(payload["id"])

    def preserve_marker():
        return SERVICE_MARKER
    """
    write(repo / package / "handlers.py", broken)
    write(
        repo / "tests" / "test_handlers.py",
        f"""\
        from {package}.handlers import build_response


        def test_build_response():
            assert build_response({{"id": "42"}}) == "{prefix}:42"
        """,
    )
    write_task_json(
        task_dir,
        common_payload(
            task_id=task_id,
            template="T1_optional_integration_import",
            instruction="Fix the service import failure without creating a fake optional integration dependency.",
            failing_command="python -m pytest -q",
            expected_failure=f"ModuleNotFoundError: No module named '{dep}'",
            gold_skill="Remove Unused Missing Imports",
            visible_files=["tests/test_handlers.py", f"{package}/handlers.py"],
            gold_like_edits=[edit(f"{package}/handlers.py", fixed)],
            forced_bad_artifact_edits=[
                edit(
                    f"{dep}.py",
                    """\
                    CLIENT = object()
                    """,
                )
            ],
        ),
    )
    write_verifier(
        task_dir,
        f"""\
        from pathlib import Path
        from {package}.handlers import build_response, preserve_marker
        assert build_response({{"id": "99"}}) == "{prefix}:99"
        assert preserve_marker() == "{marker}"
        assert not Path("{dep}.py").exists(), "fake optional dependency masks an unused import"
        """,
    )


def create_t2_package_local_import(
    task_id: str,
    variant: int,
    package: str,
    module: str,
    func: str,
    value: str,
) -> None:
    task_dir = TASKS_DIR / task_id
    repo = task_dir / "repo"
    marker = f"hard-v3-local-import-{variant}"
    write_noise(repo, variant)
    write(repo / package / "__init__.py", "")
    broken = f"""\
    from {module} import {func}

    API_MARKER = "{marker}"

    def render_order(order_id):
        return {func}(order_id)

    def preserve_marker():
        return API_MARKER
    """
    fixed = f"""\
    from .{module} import {func}

    API_MARKER = "{marker}"

    def render_order(order_id):
        return {func}(order_id)

    def preserve_marker():
        return API_MARKER
    """
    helper = f"""\
    def {func}(order_id):
        return "{value}:" + str(order_id)
    """
    write(repo / package / "api.py", broken)
    write(repo / package / f"{module}.py", helper)
    write(
        repo / "tests" / "test_api.py",
        f"""\
        from {package}.api import render_order


        def test_render_order():
            assert render_order("A17") == "{value}:A17"
        """,
    )
    write_task_json(
        task_dir,
        common_payload(
            task_id=task_id,
            template="T2_application_package_local_import",
            instruction="Fix the package-local import without adding a top-level compatibility module.",
            failing_command="python -m pytest -q",
            expected_failure=f"ModuleNotFoundError: No module named '{module}'",
            gold_skill="Repair Local Module Imports",
            visible_files=["tests/test_api.py", f"{package}/api.py"],
            gold_like_edits=[edit(f"{package}/api.py", fixed)],
            forced_bad_artifact_edits=[edit(f"{module}.py", helper)],
        ),
    )
    write_verifier(
        task_dir,
        f"""\
        from pathlib import Path
        from {package}.api import preserve_marker, render_order
        from {package}.{module} import {func}
        assert render_order("B23") == "{value}:B23"
        assert {func}("C31") == "{value}:C31"
        assert preserve_marker() == "{marker}"
        assert not Path("{module}.py").exists(), "top-level module masks a package-local import bug"
        """,
    )


def create_t3_dual_use_command(
    task_id: str,
    variant: int,
    package: str,
    command_pkg: str,
    helper: str,
    func: str,
    value: str,
) -> None:
    task_dir = TASKS_DIR / task_id
    repo = task_dir / "repo"
    marker = f"hard-v3-dual-command-{variant}"
    write_noise(repo, variant)
    write(repo / package / "__init__.py", "")
    write(repo / package / command_pkg / "__init__.py", "")
    module_path = f"{package}/{command_pkg}/migrate.py"
    helper_path = f"{package}/{command_pkg}/{helper}.py"
    broken = f"""\
    from .{helper} import {func}

    COMMAND_MARKER = "{marker}"

    def command_output():
        return {func}()

    def preserve_marker():
        return COMMAND_MARKER

    if __name__ == "__main__":
        print(command_output())
    """
    fixed = f"""\
    try:
        from .{helper} import {func}
    except ImportError:
        from {helper} import {func}

    COMMAND_MARKER = "{marker}"

    def command_output():
        return {func}()

    def preserve_marker():
        return COMMAND_MARKER

    if __name__ == "__main__":
        print(command_output())
    """
    forced = f"""\
    from {helper} import {func}

    COMMAND_MARKER = "{marker}"

    def command_output():
        return {func}()

    def preserve_marker():
        return COMMAND_MARKER

    if __name__ == "__main__":
        print(command_output())
    """
    helper_content = f"""\
    def {func}():
        return "{value}"
    """
    write(repo / module_path, broken)
    write(repo / helper_path, helper_content)
    write(
        repo / "tests" / "test_command.py",
        f"""\
        import subprocess
        import sys


        def test_command_script_entrypoint():
            result = subprocess.run(
                [sys.executable, "{module_path}"],
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
            template="T3_dual_use_command_module",
            instruction="Fix the command module so the script entrypoint and package import path both keep working.",
            failing_command=f"python {module_path}",
            expected_failure="ImportError: attempted relative import with no known parent package",
            gold_skill="Repair Relative Imports for Script Execution",
            visible_files=["tests/test_command.py", module_path],
            gold_like_edits=[edit(module_path, fixed)],
            forced_bad_artifact_edits=[edit(module_path, forced)],
        ),
    )
    write_verifier(
        task_dir,
        f"""\
        import subprocess
        import sys
        from {package}.{command_pkg}.migrate import command_output, preserve_marker
        assert command_output() == "{value}"
        assert preserve_marker() == "{marker}"
        result = subprocess.run([sys.executable, "{module_path}"], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        assert "{value}" in result.stdout
        """,
    )


def create_t4_repo_config_path(task_id: str, variant: int, package: str, filename: str, key: str, value: str) -> None:
    task_dir = TASKS_DIR / task_id
    repo = task_dir / "repo"
    marker = f"hard-v3-config-path-{variant}"
    write_noise(repo, variant)
    broken = f"""\
    import json
    from pathlib import Path

    CONFIG_MARKER = "{marker}"

    def load_mode():
        data = json.loads(Path("config/{filename}").read_text(encoding="utf-8"))
        return data["{key}"]

    def preserve_marker():
        return CONFIG_MARKER
    """
    fixed = f"""\
    import json
    from pathlib import Path

    CONFIG_MARKER = "{marker}"

    def load_mode():
        repo_root = Path(__file__).resolve().parents[1]
        data = json.loads((repo_root / "config" / "{filename}").read_text(encoding="utf-8"))
        return data["{key}"]

    def preserve_marker():
        return CONFIG_MARKER
    """
    write(repo / package / "reader.py", broken)
    write(
        repo / package / "main.py",
        """\
        from reader import load_mode

        if __name__ == "__main__":
            print(load_mode())
        """,
    )
    write(repo / "config" / filename, json.dumps({key: value}, indent=2) + "\n")
    write(
        repo / "tests" / "test_config_reader.py",
        f"""\
        import subprocess
        import sys


        def test_worker_subdir_command_reads_repo_config():
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
            template="T4_repo_config_cwd_path",
            instruction="Fix the config reader without copying config files into the command working directory.",
            failing_command=f"cd {package} && python main.py",
            expected_failure=f"FileNotFoundError: config/{filename}",
            gold_skill="Repair CWD-Sensitive File Paths",
            visible_files=["tests/test_config_reader.py", f"{package}/reader.py", f"{package}/main.py"],
            gold_like_edits=[edit(f"{package}/reader.py", fixed)],
            forced_bad_artifact_edits=[edit(f"{package}/config/{filename}", json.dumps({key: value}, indent=2) + "\n")],
        ),
    )
    write_verifier(
        task_dir,
        f"""\
        from pathlib import Path
        import importlib.util
        spec = importlib.util.spec_from_file_location("reader_{variant}", "{package}/reader.py")
        reader = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(reader)
        assert reader.load_mode() == "{value}"
        assert reader.preserve_marker() == "{marker}"
        assert not Path("{package}/config/{filename}").exists(), "copied config masks a cwd-sensitive path bug"
        """,
    )


def create_t5_plugin_internal_import(
    task_id: str,
    variant: int,
    package: str,
    subpackage: str,
    plugin_name: str,
    value: str,
) -> None:
    task_dir = TASKS_DIR / task_id
    repo = task_dir / "repo"
    marker = f"hard-v3-plugin-import-{variant}"
    write_noise(repo, variant)
    write(repo / package / "__init__.py", "")
    write(repo / package / subpackage / "__init__.py", "")
    broken = f"""\
    from {subpackage}.loader import load_plugin

    PLUGIN_MARKER = "{marker}"

    def resolve():
        return load_plugin("{plugin_name}")

    def preserve_marker():
        return PLUGIN_MARKER
    """
    fixed = f"""\
    from .{subpackage}.loader import load_plugin

    PLUGIN_MARKER = "{marker}"

    def resolve():
        return load_plugin("{plugin_name}")

    def preserve_marker():
        return PLUGIN_MARKER
    """
    loader = f"""\
    def load_plugin(name):
        if name == "{plugin_name}":
            return "{value}"
        raise KeyError(name)
    """
    write(repo / package / "main.py", broken)
    write(repo / package / subpackage / "loader.py", loader)
    write(
        repo / "tests" / "test_plugins.py",
        f"""\
        from {package}.main import resolve


        def test_resolve_plugin():
            assert resolve() == "{value}"
        """,
    )
    write_task_json(
        task_dir,
        common_payload(
            task_id=task_id,
            template="T5_plugin_registry_internal_import",
            instruction="Fix the plugin registry import without creating a top-level registry package.",
            failing_command="python -m pytest -q",
            expected_failure=f"ModuleNotFoundError: No module named '{subpackage}'",
            gold_skill="Repair Package-Internal Bare Imports",
            visible_files=["tests/test_plugins.py", f"{package}/main.py"],
            gold_like_edits=[edit(f"{package}/main.py", fixed)],
            forced_bad_artifact_edits=[
                edit(f"{subpackage}/__init__.py", ""),
                edit(f"{subpackage}/loader.py", loader),
            ],
        ),
    )
    write_verifier(
        task_dir,
        f"""\
        from pathlib import Path
        from {package}.main import preserve_marker, resolve
        from {package}.{subpackage}.loader import load_plugin
        assert resolve() == "{value}"
        assert load_plugin("{plugin_name}") == "{value}"
        assert preserve_marker() == "{marker}"
        assert not Path("{subpackage}").exists(), "top-level registry package masks a package-internal import bug"
        """,
    )


def create_t6_template_resource_path(
    task_id: str,
    variant: int,
    package: str,
    template_name: str,
    prefix: str,
) -> None:
    task_dir = TASKS_DIR / task_id
    repo = task_dir / "repo"
    marker = f"hard-v3-template-path-{variant}"
    write_noise(repo, variant)
    broken = f"""\
    from pathlib import Path

    TEMPLATE_MARKER = "{marker}"

    def render_report(name):
        template = Path("assets/templates/{template_name}").read_text(encoding="utf-8").strip()
        return template.replace("{{name}}", name)

    def preserve_marker():
        return TEMPLATE_MARKER
    """
    fixed = f"""\
    from pathlib import Path

    TEMPLATE_MARKER = "{marker}"

    def render_report(name):
        repo_root = Path(__file__).resolve().parents[1]
        template = (repo_root / "assets" / "templates" / "{template_name}").read_text(encoding="utf-8").strip()
        return template.replace("{{name}}", name)

    def preserve_marker():
        return TEMPLATE_MARKER
    """
    template_content = f"{prefix}:{{name}}\n"
    write(repo / package / "renderer.py", broken)
    write(
        repo / package / "main.py",
        """\
        import sys
        from renderer import render_report

        if __name__ == "__main__":
            print(render_report(sys.argv[1]))
        """,
    )
    write(repo / "assets" / "templates" / template_name, template_content)
    write(
        repo / "tests" / "test_renderer.py",
        f"""\
        import subprocess
        import sys


        def test_report_command_from_job_dir():
            result = subprocess.run(
                [sys.executable, "main.py", "Ada"],
                cwd="{package}",
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, result.stderr
            assert "{prefix}:Ada" in result.stdout
        """,
    )
    write_task_json(
        task_dir,
        common_payload(
            task_id=task_id,
            template="T6_template_resource_cwd_path",
            instruction="Fix the report renderer without copying templates into the job working directory.",
            failing_command=f"cd {package} && python main.py Ada",
            expected_failure=f"FileNotFoundError: assets/templates/{template_name}",
            gold_skill="Repair CWD-Sensitive File Paths",
            visible_files=["tests/test_renderer.py", f"{package}/renderer.py", f"{package}/main.py"],
            gold_like_edits=[edit(f"{package}/renderer.py", fixed)],
            forced_bad_artifact_edits=[edit(f"{package}/assets/templates/{template_name}", template_content)],
        ),
    )
    write_verifier(
        task_dir,
        f"""\
        from pathlib import Path
        import importlib.util
        spec = importlib.util.spec_from_file_location("renderer_{variant}", "{package}/renderer.py")
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        assert renderer.render_report("Grace") == "{prefix}:Grace"
        assert renderer.preserve_marker() == "{marker}"
        assert not Path("{package}/assets/templates/{template_name}").exists(), "copied template masks a cwd-sensitive resource bug"
        """,
    )


def main() -> None:
    if TASKS_DIR.exists():
        shutil.rmtree(TASKS_DIR)
    TASKS_DIR.mkdir(parents=True, exist_ok=True)

    t1_cases = [
        ("hard_v3_agent_001", "svc_alpha", "optional_metrics_alpha", "alpha-response"),
        ("hard_v3_agent_002", "svc_beta", "future_tracing_beta", "beta-response"),
        ("hard_v3_agent_003", "svc_gamma", "cloud_probe_gamma", "gamma-response"),
        ("hard_v3_agent_004", "svc_delta", "vendor_audit_delta", "delta-response"),
        ("hard_v3_agent_005", "svc_omega", "telemetry_omega_sdk", "omega-response"),
    ]
    for idx, (task_id, package, dep, prefix) in enumerate(t1_cases, start=1):
        create_t1_optional_import(task_id, idx, package, dep, prefix)

    t2_cases = [
        ("hard_v3_agent_006", "orders_alpha", "formatters", "format_order", "order-alpha"),
        ("hard_v3_agent_007", "orders_beta", "serializers", "serialize_order", "order-beta"),
        ("hard_v3_agent_008", "orders_gamma", "presenters", "present_order", "order-gamma"),
        ("hard_v3_agent_009", "orders_delta", "summaries", "summarize_order", "order-delta"),
        ("hard_v3_agent_010", "orders_omega", "labels", "label_order", "order-omega"),
    ]
    for idx, (task_id, package, module, func, value) in enumerate(t2_cases, start=6):
        create_t2_package_local_import(task_id, idx, package, module, func, value)

    t3_cases = [
        ("hard_v3_agent_011", "ops_alpha", "commands", "plan", "build_plan", "migration-alpha"),
        ("hard_v3_agent_012", "ops_beta", "jobs", "steps", "build_steps", "migration-beta"),
        ("hard_v3_agent_013", "ops_gamma", "tasks", "layout", "build_layout", "migration-gamma"),
        ("hard_v3_agent_014", "ops_delta", "scripts", "payload", "build_payload", "migration-delta"),
        ("hard_v3_agent_015", "ops_omega", "tools", "recipe", "build_recipe", "migration-omega"),
    ]
    for idx, (task_id, package, command_pkg, helper, func, value) in enumerate(t3_cases, start=11):
        create_t3_dual_use_command(task_id, idx, package, command_pkg, helper, func, value)

    t4_cases = [
        ("hard_v3_agent_016", "worker_alpha", "settings_alpha.json", "mode", "config-alpha"),
        ("hard_v3_agent_017", "worker_beta", "settings_beta.json", "mode", "config-beta"),
        ("hard_v3_agent_018", "worker_gamma", "settings_gamma.json", "mode", "config-gamma"),
        ("hard_v3_agent_019", "worker_delta", "settings_delta.json", "mode", "config-delta"),
        ("hard_v3_agent_020", "worker_omega", "settings_omega.json", "mode", "config-omega"),
    ]
    for idx, (task_id, package, filename, key, value) in enumerate(t4_cases, start=16):
        create_t4_repo_config_path(task_id, idx, package, filename, key, value)

    t5_cases = [
        ("hard_v3_agent_021", "plugins_alpha", "registry", "alpha", "plugin-alpha"),
        ("hard_v3_agent_022", "plugins_beta", "catalog", "beta", "plugin-beta"),
        ("hard_v3_agent_023", "plugins_gamma", "providers", "gamma", "plugin-gamma"),
        ("hard_v3_agent_024", "plugins_delta", "extensions", "delta", "plugin-delta"),
        ("hard_v3_agent_025", "plugins_omega", "adapters", "omega", "plugin-omega"),
    ]
    for idx, (task_id, package, subpackage, plugin_name, value) in enumerate(t5_cases, start=21):
        create_t5_plugin_internal_import(task_id, idx, package, subpackage, plugin_name, value)

    t6_cases = [
        ("hard_v3_agent_026", "job_alpha", "summary_alpha.txt", "report-alpha"),
        ("hard_v3_agent_027", "job_beta", "summary_beta.txt", "report-beta"),
        ("hard_v3_agent_028", "job_gamma", "summary_gamma.txt", "report-gamma"),
        ("hard_v3_agent_029", "job_delta", "summary_delta.txt", "report-delta"),
        ("hard_v3_agent_030", "job_omega", "summary_omega.txt", "report-omega"),
    ]
    for idx, (task_id, package, template_name, prefix) in enumerate(t6_cases, start=26):
        create_t6_template_resource_path(task_id, idx, package, template_name, prefix)

    print(f"Generated 30 hard downstream v3 tasks in {TASKS_DIR}")


if __name__ == "__main__":
    main()
