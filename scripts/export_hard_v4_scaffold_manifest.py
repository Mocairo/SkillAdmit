#!/usr/bin/env python3
"""Export a manifest for the hard_v4 downstream scaffold.

What this file does:
  Reads the generated hard_v4 task directory and writes a compact manifest with
  task counts, template counts, file counts, hashes, source-script provenance,
  and optional deterministic checker results.

Why it is needed:
  hard_v4 is a new clean downstream boundary. Before any LLM run, the generated
  task files need an auditable freeze record so future runs can prove they used
  the same scaffold and did not tune from observed failures.

Inputs:
  benchmark/downstream_hard_v4/tasks/ by default.

Outputs:
  benchmark/downstream/reports/hard_v4_scaffold_manifest.json
  benchmark/downstream/reports/hard_v4_scaffold_manifest.md
  benchmark/downstream/reports/hard_v4_scaffold_manifest.tex

Who should run it:
  Researchers freezing or verifying the hard_v4 scaffold before any LLM API
  matrix run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from check_downstream_hard_v4_tasks import bad_rows, build_summary, check_task


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TASKS_DIR = ROOT / "benchmark" / "downstream_hard_v4" / "tasks"
REPORT_DIR = ROOT / "benchmark" / "downstream" / "reports"
DEFAULT_JSON = REPORT_DIR / "hard_v4_scaffold_manifest.json"
DEFAULT_MD = REPORT_DIR / "hard_v4_scaffold_manifest.md"
DEFAULT_TEX = REPORT_DIR / "hard_v4_scaffold_manifest.tex"

SOURCE_FILES = [
    ROOT / "scripts" / "build_downstream_hard_v4_tasks.py",
    ROOT / "scripts" / "check_downstream_hard_v4_tasks.py",
    ROOT / "scripts" / "export_hard_v4_scaffold_manifest.py",
    ROOT / "docs" / "llm_downstream_hard_v4.md",
]


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def display_path(path: Path) -> str:
    path = resolve(path)
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def sha256_tree(path: Path) -> str:
    hasher = hashlib.sha256()
    for item in sorted(p for p in path.rglob("*") if p.is_file()):
        rel = item.relative_to(path).as_posix()
        hasher.update(rel.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(item.read_bytes())
        hasher.update(b"\0")
    return hasher.hexdigest()


def load_task(task_dir: Path) -> dict[str, Any]:
    return json.loads((task_dir / "task.json").read_text(encoding="utf-8"))


def file_count(path: Path) -> int:
    return sum(1 for item in path.rglob("*") if item.is_file())


def size_bytes(path: Path) -> int:
    return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())


def task_dirs(tasks_dir: Path) -> list[Path]:
    return sorted(path for path in tasks_dir.iterdir() if path.is_dir())


def source_hashes() -> list[dict[str, Any]]:
    rows = []
    for path in SOURCE_FILES:
        rows.append(
            {
                "path": display_path(path),
                "exists": path.exists(),
                "sha256": sha256_file(path) if path.exists() else None,
            }
        )
    return rows


def build_task_rows(tasks_dir: Path) -> list[dict[str, Any]]:
    rows = []
    for task_dir in task_dirs(tasks_dir):
        task = load_task(task_dir)
        task_json = task_dir / "task.json"
        verifier = task_dir / "verifier.sh"
        rows.append(
            {
                "task_id": task["task_id"],
                "template": task["template"],
                "gold_skill": task.get("downstream_gold_skill"),
                "task_dir": display_path(task_dir),
                "visible_files_count": len(task.get("visible_files", [])),
                "gold_like_edits_count": len(task.get("gold_like_edits", [])),
                "forced_bad_artifact_edits_count": len(task.get("forced_bad_artifact_edits", [])),
                "repo_file_count": file_count(task_dir / "repo"),
                "task_file_count": file_count(task_dir),
                "task_size_bytes": size_bytes(task_dir),
                "task_json_sha256": sha256_file(task_json),
                "verifier_sha256": sha256_file(verifier),
                "task_tree_sha256": sha256_tree(task_dir),
            }
        )
    return rows


def run_checker(tasks_dir: Path) -> dict[str, Any]:
    rows = [check_task(path) for path in task_dirs(tasks_dir)]
    summary = build_summary(rows)
    return {
        "summary": summary,
        "failed_rows": bad_rows(rows),
    }


def build_manifest(tasks_dir: Path, run_check: bool) -> dict[str, Any]:
    task_rows = build_task_rows(tasks_dir)
    template_counts = Counter(row["template"] for row in task_rows)
    gold_skill_counts = Counter(row["gold_skill"] for row in task_rows)
    checker = run_checker(tasks_dir) if run_check else None
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "family": "python_coding_agent_downstream_hard_v4",
        "stage": "scaffold_frozen_no_llm_evidence",
        "tasks_dir": display_path(tasks_dir),
        "task_count": len(task_rows),
        "file_count": file_count(tasks_dir),
        "size_bytes": size_bytes(tasks_dir),
        "task_tree_sha256": sha256_tree(tasks_dir),
        "template_counts": dict(sorted(template_counts.items())),
        "gold_skill_counts": dict(sorted(gold_skill_counts.items())),
        "task_rows": task_rows,
        "source_hashes": source_hashes(),
        "checker": checker,
        "claim_boundary": {
            "supported": [
                "hard_v4 task scaffold is generated and hashable.",
                "hard_v4 deterministic checker can validate scaffold invariants.",
                "hard_v4 can be used as a future clean downstream boundary after explicit freeze.",
            ],
            "not_supported": [
                "hard_v4 does not provide LLM downstream evidence yet.",
                "hard_v4 does not support any SkillAdmit success claim yet.",
                "hard_v4 should not be prompt-tuned from observed failures while kept as clean evidence.",
            ],
        },
    }


def assert_manifest(manifest: dict[str, Any]) -> None:
    if manifest["task_count"] != 24:
        raise AssertionError(f"expected 24 tasks, got {manifest['task_count']}")
    if manifest["file_count"] != 244:
        raise AssertionError(f"expected 244 files, got {manifest['file_count']}")
    expected_templates = {
        "T1_optional_telemetry_import": 4,
        "T2_src_layout_package_import": 4,
        "T3_dual_entrypoint_command": 4,
        "T4_workspace_config_resolution": 4,
        "T5_resource_template_resolution": 4,
        "T6_plugin_registry_namespace": 4,
    }
    if manifest["template_counts"] != expected_templates:
        raise AssertionError(f"template counts changed: {manifest['template_counts']}")
    if len(manifest["task_rows"]) != 24:
        raise AssertionError("task row count changed")
    task_ids = [row["task_id"] for row in manifest["task_rows"]]
    if len(task_ids) != len(set(task_ids)):
        raise AssertionError("duplicate task ids")
    if task_ids[0] != "hard_v4_agent_001" or task_ids[-1] != "hard_v4_agent_024":
        raise AssertionError("unexpected hard_v4 task id range")
    if not all(row["task_tree_sha256"] for row in manifest["task_rows"]):
        raise AssertionError("missing per-task tree hash")
    for source in manifest["source_hashes"]:
        if not source["exists"] or not source["sha256"]:
            raise AssertionError(f"missing source hash: {source['path']}")
    checker = manifest.get("checker")
    if checker is not None:
        summary = checker["summary"]
        required = {
            "total": 24,
            "initial_failed": 24,
            "gold_passed": 24,
            "forced_public_passed": 24,
            "forced_verifier_failed": 24,
        }
        for key, expected in required.items():
            actual = summary[key]
            if actual != expected:
                raise AssertionError(f"checker {key}: expected {expected}, got {actual}")
        if checker["failed_rows"]:
            raise AssertionError("checker has failed rows")
    rendered = render_markdown(manifest)
    for phrase in [
        "scaffold_frozen_no_llm_evidence",
        "hard_v4 does not provide LLM downstream evidence yet",
        "T6_plugin_registry_namespace",
        "244",
    ]:
        if phrase not in rendered:
            raise AssertionError(f"missing manifest phrase: {phrase}")


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("\n", " ") for cell in row) + " |")
    return "\n".join(lines)


def render_markdown(manifest: dict[str, Any]) -> str:
    lines = [
        "# Hard v4 Scaffold Manifest",
        "",
        f"Generated at UTC: `{manifest['generated_at_utc']}`",
        "",
        f"Stage: `{manifest['stage']}`",
        "",
        "This is a scaffold freeze record, not an LLM downstream result.",
        "",
        "## Summary",
        "",
        md_table(
            ["field", "value"],
            [
                ["family", manifest["family"]],
                ["tasks_dir", f"`{manifest['tasks_dir']}`"],
                ["task_count", manifest["task_count"]],
                ["file_count", manifest["file_count"]],
                ["size_bytes", manifest["size_bytes"]],
                ["task_tree_sha256", f"`{manifest['task_tree_sha256']}`"],
            ],
        ),
        "",
        "## Template Counts",
        "",
        md_table(["template", "tasks"], [[key, value] for key, value in manifest["template_counts"].items()]),
        "",
        "## Gold Skill Counts",
        "",
        md_table(["gold_skill", "tasks"], [[key, value] for key, value in manifest["gold_skill_counts"].items()]),
        "",
        "## Task Rows",
        "",
    ]
    lines.append(
        md_table(
            [
                "task_id",
                "template",
                "gold_skill",
                "repo_files",
                "task_files",
                "task_tree_sha256",
            ],
            [
                [
                    row["task_id"],
                    row["template"],
                    row["gold_skill"],
                    row["repo_file_count"],
                    row["task_file_count"],
                    f"`{row['task_tree_sha256'][:16]}`",
                ]
                for row in manifest["task_rows"]
            ],
        )
    )
    if manifest.get("checker") is not None:
        summary = manifest["checker"]["summary"]
        lines.extend(
            [
                "",
                "## Checker Summary",
                "",
                md_table(
                    ["field", "value"],
                    [
                        ["total", summary["total"]],
                        ["initial_failed", summary["initial_failed"]],
                        ["gold_passed", summary["gold_passed"]],
                        ["forced_public_passed", summary["forced_public_passed"]],
                        ["forced_verifier_failed", summary["forced_verifier_failed"]],
                    ],
                ),
            ]
        )
    lines.extend(["", "## Claim Boundary", "", "Supported:"])
    lines.extend(f"- {item}" for item in manifest["claim_boundary"]["supported"])
    lines.extend(["", "Not supported:"])
    lines.extend(f"- {item}" for item in manifest["claim_boundary"]["not_supported"])
    lines.extend(["", "## Source Hashes", ""])
    lines.append(
        md_table(
            ["path", "exists", "sha256"],
            [
                [f"`{row['path']}`", row["exists"], f"`{row['sha256'][:16]}`" if row["sha256"] else ""]
                for row in manifest["source_hashes"]
            ],
        )
    )
    lines.append("")
    return "\n".join(lines)


def tex_escape(value: Any) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def render_latex(manifest: dict[str, Any]) -> str:
    lines = [
        "% Auto-generated by scripts/export_hard_v4_scaffold_manifest.py",
        "\\begin{tabular}{lr}",
        "\\hline",
        "Field & Value \\\\",
        "\\hline",
        f"Task count & {manifest['task_count']} \\\\",
        f"File count & {manifest['file_count']} \\\\",
        f"Size bytes & {manifest['size_bytes']} \\\\",
        f"Stage & {tex_escape(manifest['stage'])} \\\\",
        "\\hline",
        "\\end{tabular}",
        "",
        "% Template counts:",
    ]
    for key, value in manifest["template_counts"].items():
        lines.append(f"% {tex_escape(key)} = {value}")
    lines.append("")
    return "\n".join(lines)


def write_outputs(manifest: dict[str, Any], json_path: Path, md_path: Path, tex_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(manifest), encoding="utf-8")
    tex_path.write_text(render_latex(manifest), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks-dir", type=Path, default=DEFAULT_TASKS_DIR)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--tex-out", type=Path, default=DEFAULT_TEX)
    parser.add_argument("--run-checker", action="store_true", help="Run deterministic hard_v4 checker and embed summary.")
    parser.add_argument(
        "--assert-current-hard-v4-scaffold",
        action="store_true",
        help="Assert current hard_v4 scaffold values and no-LLM-evidence boundary.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tasks_dir = resolve(args.tasks_dir)
    if not tasks_dir.exists():
        raise SystemExit(f"Missing tasks dir: {tasks_dir}")
    manifest = build_manifest(tasks_dir, run_check=args.run_checker)
    if args.assert_current_hard_v4_scaffold:
        assert_manifest(manifest)
    write_outputs(manifest, resolve(args.json_out), resolve(args.md_out), resolve(args.tex_out))
    print(f"task_count: {manifest['task_count']}")
    print(f"file_count: {manifest['file_count']}")
    print(f"stage: {manifest['stage']}")
    if manifest.get("checker"):
        summary = manifest["checker"]["summary"]
        print(f"checker_total: {summary['total']}")
        print(f"checker_forced_verifier_failed: {summary['forced_verifier_failed']}")
    print(f"wrote_json: {display_path(args.json_out)}")
    print(f"wrote_md: {display_path(args.md_out)}")
    print(f"wrote_tex: {display_path(args.tex_out)}")


if __name__ == "__main__":
    main()
