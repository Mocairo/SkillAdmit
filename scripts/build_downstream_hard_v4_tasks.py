#!/usr/bin/env python3
"""Build the hard_v4 downstream scaffold.

What this file does:
  Generates a deterministic hard_v4 downstream task suite for future LLM coding
  agent validation. Each task contains a small repository, visible-file prompt
  metadata, gold-like edits, forced-bad artifact edits, public tests, and a
  hidden verifier.

Why it is needed:
  hard_v2 and hard_v3 are frozen evidence boundaries. hard_v4 is a fresh
  downstream boundary for a later evaluation cycle: more agent-like repository
  repairs, still with hidden verifiers and forced negative-transfer controls.

Inputs:
  No external inputs. The task suite is generated from deterministic templates
  in this script.

Outputs:
  benchmark/downstream_hard_v4/tasks/ by default, or a custom --tasks-dir.

Who should run it:
  Researchers preparing a new clean hard_v4 downstream validation boundary.
  Do not run LLM API against hard_v4 until the suite is explicitly frozen.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from textwrap import dedent
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TASKS_DIR = ROOT / "benchmark" / "downstream_hard_v4" / "tasks"


def source(text: str) -> str:
    return dedent(text).lstrip()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source(content), encoding="utf-8")


def make_executable(path: Path) -> None:
    path.chmod(path.stat().st_mode | 0o111)


def edit(path: str, content: str) -> dict[str, str]:
    return {"path": path, "content": source(content)}


def write_noise(repo: Path, variant: int) -> None:
    for idx in range(3):
        write(
            repo / "dev_notes" / f"candidate_fix_{idx:02d}.py",
            f"""\
            def candidate_fix_{idx:02d}():
                return "hard-v4-noise-{variant}-{idx:02d}"
            """,
        )
    write(
        repo / "README.md",
        f"""\
        # Hard v4 fixture {variant}

        This repository is intentionally small but includes extra notes and
        candidate fixes so the downstream agent must inspect code rather than
        blindly applying an artifact.
        """,
    )


def write_verifier(task_dir: Path, hidden_assertions: str) -> None:
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
        + source(hidden_assertions)
        + "PY\n"
    )
    write(task_dir / "verifier.sh", script)
    make_executable(task_dir / "verifier.sh")


def write_task_json(task_dir: Path, payload: dict[str, Any]) -> None:
    payload.setdefault(
        "file_context_note",
        (
            "Hard v4 is a fresh downstream boundary. Visible files are the files "
            "a coding agent is likely to inspect first, but hidden verification "
            "rejects public-test masking repairs such as stubs, copied configs, "
            "copied resources, top-level compatibility packages, or script-only "
            "fixes that break package semantics."
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
        "family": "python_coding_agent_downstream_hard_v4",
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


def create_t1_optional_telemetry_import(
    tasks_dir: Path,
    task_id: str,
    variant: int,
    package: str,
    missing_dep: str,
    prefix: str,
) -> None:
    task_dir = tasks_dir / task_id
    repo = task_dir / "repo"
    marker = f"hard-v4-optional-telemetry-{variant}"
    write_noise(repo, variant)
    write(repo / package / "__init__.py", "")
    broken = f"""\
    import {missing_dep}

    CLIENT_MARKER = "{marker}"

    def format_event(event):
        return "{prefix}:" + str(event["id"]) + ":" + event.get("kind", "unknown")

    def preserve_marker():
        return CLIENT_MARKER
    """
    fixed = f"""\
    CLIENT_MARKER = "{marker}"

    def format_event(event):
        return "{prefix}:" + str(event["id"]) + ":" + event.get("kind", "unknown")

    def preserve_marker():
        return CLIENT_MARKER
    """
    write(repo / package / "client.py", broken)
    write(
        repo / "tests" / "test_client.py",
        f"""\
        from {package}.client import format_event


        def test_format_event_without_optional_telemetry():
            assert format_event({{"id": "42", "kind": "audit"}}) == "{prefix}:42:audit"
        """,
    )
    write_task_json(
        task_dir,
        common_payload(
            task_id=task_id,
            template="T1_optional_telemetry_import",
            instruction="Fix the service client without adding a fake optional telemetry dependency.",
            failing_command="python -m pytest -q",
            expected_failure=f"ModuleNotFoundError: No module named '{missing_dep}'",
            gold_skill="Remove Unused Missing Imports",
            visible_files=["tests/test_client.py", f"{package}/client.py"],
            gold_like_edits=[edit(f"{package}/client.py", fixed)],
            forced_bad_artifact_edits=[
                edit(
                    f"{missing_dep}.py",
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
        from {package}.client import format_event, preserve_marker
        assert format_event({{"id": "99", "kind": "hidden"}}) == "{prefix}:99:hidden"
        assert preserve_marker() == "{marker}"
        assert not Path("{missing_dep}.py").exists(), "fake optional telemetry dependency masks an unused import"
        """,
    )


def create_t2_src_layout_import(
    tasks_dir: Path,
    task_id: str,
    variant: int,
    package: str,
    module: str,
    func: str,
    prefix: str,
) -> None:
    task_dir = tasks_dir / task_id
    repo = task_dir / "repo"
    marker = f"hard-v4-src-layout-{variant}"
    write_noise(repo, variant)
    write(repo / package / "__init__.py", "")
    broken = f"""\
    from {module} import {func}

    SERVICE_MARKER = "{marker}"

    def build_slug(value):
        return {func}(value)

    def preserve_marker():
        return SERVICE_MARKER
    """
    fixed = f"""\
    from .{module} import {func}

    SERVICE_MARKER = "{marker}"

    def build_slug(value):
        return {func}(value)

    def preserve_marker():
        return SERVICE_MARKER
    """
    helper = f"""\
    def {func}(value):
        return "{prefix}-" + str(value).lower().replace(" ", "-")
    """
    write(repo / package / "service.py", broken)
    write(repo / package / f"{module}.py", helper)
    write(
        repo / "tests" / "test_service.py",
        f"""\
        from {package}.service import build_slug


        def test_build_slug():
            assert build_slug("Alpha Case") == "{prefix}-alpha-case"
        """,
    )
    write_task_json(
        task_dir,
        common_payload(
            task_id=task_id,
            template="T2_src_layout_package_import",
            instruction="Fix the package-local import without adding a top-level compatibility module.",
            failing_command="python -m pytest -q",
            expected_failure=f"ModuleNotFoundError: No module named '{module}'",
            gold_skill="Repair Local Module Imports",
            visible_files=["tests/test_service.py", f"{package}/service.py"],
            gold_like_edits=[edit(f"{package}/service.py", fixed)],
            forced_bad_artifact_edits=[edit(f"{module}.py", helper)],
        ),
    )
    write_verifier(
        task_dir,
        f"""\
        from pathlib import Path
        from {package}.service import build_slug, preserve_marker
        from {package}.{module} import {func}
        assert build_slug("Hidden Case") == "{prefix}-hidden-case"
        assert {func}("Deep Value") == "{prefix}-deep-value"
        assert preserve_marker() == "{marker}"
        assert not Path("{module}.py").exists(), "top-level compatibility module masks a package-local import bug"
        """,
    )


def create_t3_dual_entrypoint(
    tasks_dir: Path,
    task_id: str,
    variant: int,
    package: str,
    command_pkg: str,
    helper: str,
    func: str,
    value: str,
) -> None:
    task_dir = tasks_dir / task_id
    repo = task_dir / "repo"
    marker = f"hard-v4-dual-entrypoint-{variant}"
    write_noise(repo, variant)
    write(repo / package / "__init__.py", "")
    write(repo / package / command_pkg / "__init__.py", "")
    module_path = f"{package}/{command_pkg}/export.py"
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
        repo / "tests" / "test_export_command.py",
        f"""\
        import subprocess
        import sys


        def test_export_script_entrypoint():
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
            template="T3_dual_entrypoint_command",
            instruction="Fix the command module so direct script execution and package import both work.",
            failing_command=f"python {module_path}",
            expected_failure="ImportError: attempted relative import with no known parent package",
            gold_skill="Repair Relative Imports for Script Execution",
            visible_files=["tests/test_export_command.py", module_path],
            gold_like_edits=[edit(module_path, fixed)],
            forced_bad_artifact_edits=[edit(module_path, forced)],
        ),
    )
    write_verifier(
        task_dir,
        f"""\
        import subprocess
        import sys
        from {package}.{command_pkg}.export import command_output, preserve_marker
        assert command_output() == "{value}"
        assert preserve_marker() == "{marker}"
        result = subprocess.run([sys.executable, "{module_path}"], capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        assert "{value}" in result.stdout
        """,
    )


def create_t4_workspace_config(
    tasks_dir: Path,
    task_id: str,
    variant: int,
    package: str,
    filename: str,
    key: str,
    value: str,
) -> None:
    task_dir = tasks_dir / task_id
    repo = task_dir / "repo"
    marker = f"hard-v4-workspace-config-{variant}"
    write_noise(repo, variant)
    broken = f"""\
    import json
    from pathlib import Path

    CONFIG_MARKER = "{marker}"

    def load_region():
        data = json.loads(Path("config/{filename}").read_text(encoding="utf-8"))
        return data["{key}"]

    def preserve_marker():
        return CONFIG_MARKER
    """
    fixed = f"""\
    import json
    from pathlib import Path

    CONFIG_MARKER = "{marker}"

    def load_region():
        repo_root = Path(__file__).resolve().parents[1]
        data = json.loads((repo_root / "config" / "{filename}").read_text(encoding="utf-8"))
        return data["{key}"]

    def preserve_marker():
        return CONFIG_MARKER
    """
    write(repo / package / "settings.py", broken)
    write(
        repo / package / "job.py",
        """\
        from settings import load_region

        if __name__ == "__main__":
            print(load_region())
        """,
    )
    write(repo / "config" / filename, json.dumps({key: value}, indent=2) + "\n")
    write(
        repo / "tests" / "test_job.py",
        f"""\
        import subprocess
        import sys


        def test_job_command_reads_repo_config_from_worker_dir():
            result = subprocess.run(
                [sys.executable, "job.py"],
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
            template="T4_workspace_config_resolution",
            instruction="Fix config loading without copying config files into the worker directory.",
            failing_command=f"cd {package} && python job.py",
            expected_failure=f"FileNotFoundError: config/{filename}",
            gold_skill="Repair CWD-Sensitive File Paths",
            visible_files=["tests/test_job.py", f"{package}/settings.py", f"{package}/job.py"],
            gold_like_edits=[edit(f"{package}/settings.py", fixed)],
            forced_bad_artifact_edits=[edit(f"{package}/config/{filename}", json.dumps({key: value}, indent=2) + "\n")],
        ),
    )
    write_verifier(
        task_dir,
        f"""\
        from pathlib import Path
        import importlib.util
        spec = importlib.util.spec_from_file_location("settings_{variant}", "{package}/settings.py")
        settings = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(settings)
        assert settings.load_region() == "{value}"
        assert settings.preserve_marker() == "{marker}"
        assert not Path("{package}/config/{filename}").exists(), "copied config masks a cwd-sensitive path bug"
        """,
    )


def create_t5_resource_template(
    tasks_dir: Path,
    task_id: str,
    variant: int,
    package: str,
    template_name: str,
    prefix: str,
) -> None:
    task_dir = tasks_dir / task_id
    repo = task_dir / "repo"
    marker = f"hard-v4-resource-template-{variant}"
    write_noise(repo, variant)
    broken = f"""\
    from pathlib import Path

    TEMPLATE_MARKER = "{marker}"

    def render_notice(name):
        template = Path("resources/templates/{template_name}").read_text(encoding="utf-8").strip()
        return template.replace("{{name}}", name)

    def preserve_marker():
        return TEMPLATE_MARKER
    """
    fixed = f"""\
    from pathlib import Path

    TEMPLATE_MARKER = "{marker}"

    def render_notice(name):
        repo_root = Path(__file__).resolve().parents[1]
        template = (repo_root / "resources" / "templates" / "{template_name}").read_text(encoding="utf-8").strip()
        return template.replace("{{name}}", name)

    def preserve_marker():
        return TEMPLATE_MARKER
    """
    template_content = f"{prefix}:{{name}}\n"
    write(repo / package / "render.py", broken)
    write(
        repo / package / "preview.py",
        """\
        import sys
        from render import render_notice

        if __name__ == "__main__":
            print(render_notice(sys.argv[1]))
        """,
    )
    write(repo / "resources" / "templates" / template_name, template_content)
    write(
        repo / "tests" / "test_preview.py",
        f"""\
        import subprocess
        import sys


        def test_preview_from_package_dir():
            result = subprocess.run(
                [sys.executable, "preview.py", "Ada"],
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
            template="T5_resource_template_resolution",
            instruction="Fix template loading without copying resources into the command working directory.",
            failing_command=f"cd {package} && python preview.py Ada",
            expected_failure=f"FileNotFoundError: resources/templates/{template_name}",
            gold_skill="Repair CWD-Sensitive File Paths",
            visible_files=["tests/test_preview.py", f"{package}/render.py", f"{package}/preview.py"],
            gold_like_edits=[edit(f"{package}/render.py", fixed)],
            forced_bad_artifact_edits=[edit(f"{package}/resources/templates/{template_name}", template_content)],
        ),
    )
    write_verifier(
        task_dir,
        f"""\
        from pathlib import Path
        import importlib.util
        spec = importlib.util.spec_from_file_location("render_{variant}", "{package}/render.py")
        render = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(render)
        assert render.render_notice("Grace") == "{prefix}:Grace"
        assert render.preserve_marker() == "{marker}"
        assert not Path("{package}/resources/templates/{template_name}").exists(), "copied template masks a cwd-sensitive resource bug"
        """,
    )


def create_t6_plugin_registry(
    tasks_dir: Path,
    task_id: str,
    variant: int,
    package: str,
    registry: str,
    plugin_name: str,
    value: str,
) -> None:
    task_dir = tasks_dir / task_id
    repo = task_dir / "repo"
    marker = f"hard-v4-plugin-registry-{variant}"
    write_noise(repo, variant)
    write(repo / package / "__init__.py", "")
    write(repo / package / registry / "__init__.py", "")
    broken = f"""\
    from {registry}.loader import load_plugin

    PLUGIN_MARKER = "{marker}"

    def resolve_plugin():
        return load_plugin("{plugin_name}")

    def preserve_marker():
        return PLUGIN_MARKER
    """
    fixed = f"""\
    from .{registry}.loader import load_plugin

    PLUGIN_MARKER = "{marker}"

    def resolve_plugin():
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
    write(repo / package / registry / "loader.py", loader)
    write(
        repo / "tests" / "test_plugins.py",
        f"""\
        from {package}.main import resolve_plugin


        def test_resolve_plugin():
            assert resolve_plugin() == "{value}"
        """,
    )
    write_task_json(
        task_dir,
        common_payload(
            task_id=task_id,
            template="T6_plugin_registry_namespace",
            instruction="Fix the plugin registry import without adding a top-level registry package.",
            failing_command="python -m pytest -q",
            expected_failure=f"ModuleNotFoundError: No module named '{registry}'",
            gold_skill="Repair Package-Internal Bare Imports",
            visible_files=["tests/test_plugins.py", f"{package}/main.py"],
            gold_like_edits=[edit(f"{package}/main.py", fixed)],
            forced_bad_artifact_edits=[
                edit(f"{registry}/__init__.py", ""),
                edit(f"{registry}/loader.py", loader),
            ],
        ),
    )
    write_verifier(
        task_dir,
        f"""\
        from pathlib import Path
        from {package}.main import preserve_marker, resolve_plugin
        from {package}.{registry}.loader import load_plugin
        assert resolve_plugin() == "{value}"
        assert load_plugin("{plugin_name}") == "{value}"
        assert preserve_marker() == "{marker}"
        assert not Path("{registry}").exists(), "top-level registry package masks a package-internal import bug"
        """,
    )


def build_tasks(tasks_dir: Path, clean: bool = True) -> int:
    if tasks_dir.exists() and clean:
        shutil.rmtree(tasks_dir)
    tasks_dir.mkdir(parents=True, exist_ok=True)

    t1_cases = [
        ("hard_v4_agent_001", "client_alpha", "future_telemetry_alpha", "evt-alpha"),
        ("hard_v4_agent_002", "client_beta", "vendor_metrics_beta", "evt-beta"),
        ("hard_v4_agent_003", "client_gamma", "cloud_probe_gamma", "evt-gamma"),
        ("hard_v4_agent_004", "client_delta", "audit_sink_delta", "evt-delta"),
    ]
    for idx, case in enumerate(t1_cases, start=1):
        create_t1_optional_telemetry_import(tasks_dir, *case[:1], idx, *case[1:])

    t2_cases = [
        ("hard_v4_agent_005", "domain_alpha", "normalizers", "normalize_slug", "alpha"),
        ("hard_v4_agent_006", "domain_beta", "formatters", "format_slug", "beta"),
        ("hard_v4_agent_007", "domain_gamma", "presenters", "present_slug", "gamma"),
        ("hard_v4_agent_008", "domain_delta", "labels", "label_slug", "delta"),
    ]
    for idx, case in enumerate(t2_cases, start=5):
        create_t2_src_layout_import(tasks_dir, *case[:1], idx, *case[1:])

    t3_cases = [
        ("hard_v4_agent_009", "cli_alpha", "commands", "payload", "build_payload", "export-alpha"),
        ("hard_v4_agent_010", "cli_beta", "jobs", "recipe", "build_recipe", "export-beta"),
        ("hard_v4_agent_011", "cli_gamma", "tools", "summary", "build_summary", "export-gamma"),
        ("hard_v4_agent_012", "cli_delta", "scripts", "plan", "build_plan", "export-delta"),
    ]
    for idx, case in enumerate(t3_cases, start=9):
        create_t3_dual_entrypoint(tasks_dir, *case[:1], idx, *case[1:])

    t4_cases = [
        ("hard_v4_agent_013", "worker_alpha", "runtime_alpha.json", "region", "us-alpha"),
        ("hard_v4_agent_014", "worker_beta", "runtime_beta.json", "region", "eu-beta"),
        ("hard_v4_agent_015", "worker_gamma", "runtime_gamma.json", "region", "ap-gamma"),
        ("hard_v4_agent_016", "worker_delta", "runtime_delta.json", "region", "sa-delta"),
    ]
    for idx, case in enumerate(t4_cases, start=13):
        create_t4_workspace_config(tasks_dir, *case[:1], idx, *case[1:])

    t5_cases = [
        ("hard_v4_agent_017", "notice_alpha", "notice_alpha.txt", "notice-alpha"),
        ("hard_v4_agent_018", "notice_beta", "notice_beta.txt", "notice-beta"),
        ("hard_v4_agent_019", "notice_gamma", "notice_gamma.txt", "notice-gamma"),
        ("hard_v4_agent_020", "notice_delta", "notice_delta.txt", "notice-delta"),
    ]
    for idx, case in enumerate(t5_cases, start=17):
        create_t5_resource_template(tasks_dir, *case[:1], idx, *case[1:])

    t6_cases = [
        ("hard_v4_agent_021", "platform_alpha", "registry", "alpha", "plugin-alpha"),
        ("hard_v4_agent_022", "platform_beta", "catalog", "beta", "plugin-beta"),
        ("hard_v4_agent_023", "platform_gamma", "providers", "gamma", "plugin-gamma"),
        ("hard_v4_agent_024", "platform_delta", "extensions", "delta", "plugin-delta"),
    ]
    for idx, case in enumerate(t6_cases, start=21):
        create_t6_plugin_registry(tasks_dir, *case[:1], idx, *case[1:])

    return len([path for path in tasks_dir.iterdir() if path.is_dir()])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks-dir", type=Path, default=DEFAULT_TASKS_DIR)
    parser.add_argument("--no-clean", action="store_true", help="Do not remove an existing tasks directory first.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tasks_dir = args.tasks_dir if args.tasks_dir.is_absolute() else ROOT / args.tasks_dir
    count = build_tasks(tasks_dir, clean=not args.no_clean)
    print(f"Generated {count} hard downstream v4 tasks in {tasks_dir}")


if __name__ == "__main__":
    main()
