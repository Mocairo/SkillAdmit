#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUN_ROOT = ROOT / "benchmark" / "downstream" / "llm_runs"
REPORT_DIR = ROOT / "benchmark" / "downstream" / "reports"
DEFAULT_JSON = REPORT_DIR / "hard_v2_strategy_matrix.json"
DEFAULT_MD = REPORT_DIR / "hard_v2_strategy_matrix.md"

RUN_METADATA = {
    "llm_downstream_hard_v2_canary_5x2": {
        "setting": "canary_visible_file",
        "order": 10,
        "paper_role": "canary only",
    },
    "llm_downstream_hard_v2_forced_bad_25": {
        "setting": "forced_bad_standalone",
        "order": 20,
        "paper_role": "negative transfer control",
    },
    "llm_downstream_hard_v2_full_25x6": {
        "setting": "strict_visible_file",
        "order": 30,
        "paper_role": "strict visible-file comparison",
    },
    "llm_downstream_hard_v2_tree_25x2": {
        "setting": "tree_aware",
        "order": 40,
        "paper_role": "realistic coding-agent comparison",
    },
    "llm_downstream_hard_v2_precondition_only_25": {
        "setting": "strict_precondition_only",
        "order": 50,
        "paper_role": "precondition-text ablation",
    },
    "llm_downstream_hard_v2_selected_precondition_25": {
        "setting": "tree_aware_precondition_context",
        "order": 60,
        "paper_role": "selected skill plus tree and guardrail context",
    },
    "llm_downstream_hard_v2_replication_tree_selected_25": {
        "setting": "replication_tree_aware",
        "order": 70,
        "paper_role": "replication of tree-aware selected skill",
    },
    "llm_downstream_hard_v2_replication_selected_precondition_25": {
        "setting": "replication_tree_aware_precondition_context",
        "order": 80,
        "paper_role": "replication of selected skill plus tree and guardrail context",
    },
    "llm_downstream_hard_v2_replication_precondition_only_25": {
        "setting": "replication_strict_precondition_only",
        "order": 90,
        "paper_role": "replication of precondition-text ablation",
    },
}

STABILITY_GROUPS = [
    {
        "name": "tree_aware_skilladmit_selected",
        "interpretation": "Tree-aware selected skill condition.",
        "members": [
            ("llm_downstream_hard_v2_tree_25x2", "skilladmit_selected"),
            ("llm_downstream_hard_v2_replication_tree_selected_25", "skilladmit_selected"),
        ],
    },
    {
        "name": "tree_aware_selected_precondition_context",
        "interpretation": "Tree-aware selected skill plus explicit precondition context.",
        "members": [
            ("llm_downstream_hard_v2_selected_precondition_25", "skilladmit_selected_with_precondition_context"),
            (
                "llm_downstream_hard_v2_replication_selected_precondition_25",
                "skilladmit_selected_with_precondition_context",
            ),
        ],
    },
    {
        "name": "strict_precondition_only",
        "interpretation": "Strict visible-file selected skill plus preconditions, without repo tree.",
        "members": [
            ("llm_downstream_hard_v2_precondition_only_25", "skilladmit_selected_with_precondition_only"),
            ("llm_downstream_hard_v2_replication_precondition_only_25", "skilladmit_selected_with_precondition_only"),
        ],
    },
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_info(path: Path) -> dict[str, Any]:
    stat = path.stat()
    return {
        "path": path.relative_to(ROOT).as_posix(),
        "size_bytes": stat.st_size,
        "mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
        "sha256": sha256_file(path),
    }


def hard_v2_run_dirs(run_root: Path) -> list[Path]:
    return sorted(
        path
        for path in run_root.iterdir()
        if path.is_dir()
        and path.name.startswith("llm_downstream_hard_v2_")
        and (path / "summary.json").exists()
    )


def strategy_rows(run_dir: Path, summary: dict[str, Any], trajectories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    metadata = RUN_METADATA.get(
        run_dir.name,
        {"setting": "unknown", "order": 999, "paper_role": "unclassified"},
    )
    by_strategy: dict[str, list[dict[str, Any]]] = {}
    for row in trajectories:
        by_strategy.setdefault(row["strategy"], []).append(row)

    for strategy, item in sorted(summary.get("strategies", {}).items()):
        items = by_strategy.get(strategy, [])
        included_repo_tree = sum(1 for row in items if row.get("included_repo_tree"))
        used_task_visible_files = sum(1 for row in items if row.get("used_task_visible_files"))
        rows.append(
            {
                "run_name": run_dir.name,
                "setting": metadata["setting"],
                "setting_order": metadata["order"],
                "paper_role": metadata["paper_role"],
                "strategy": strategy,
                "tasks": item["tasks"],
                "successes": item["successes"],
                "success_rate": item["success_rate"],
                "negative_transfer": item["negative_transfer"],
                "public_passed_hidden_failed": item.get("public_passed_hidden_failed", 0),
                "artifact_adherence": item.get("artifact_adherence", 0),
                "parse_errors": item.get("parse_errors", 0),
                "total_tokens": item.get("total_tokens", 0),
                "avg_tokens": item.get("avg_tokens", 0.0),
                "included_repo_tree_rows": included_repo_tree,
                "visible_file_rows": used_task_visible_files,
            }
        )
    return rows


def template_rows(run_dir: Path, trajectories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metadata = RUN_METADATA.get(
        run_dir.name,
        {"setting": "unknown", "order": 999, "paper_role": "unclassified"},
    )
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in trajectories:
        grouped.setdefault((row["strategy"], row["template"]), []).append(row)

    rows = []
    for (strategy, template), items in sorted(grouped.items()):
        total_tokens = sum(int((row.get("model_usage") or {}).get("total_tokens") or 0) for row in items)
        rows.append(
            {
                "run_name": run_dir.name,
                "setting": metadata["setting"],
                "setting_order": metadata["order"],
                "strategy": strategy,
                "template": template,
                "tasks": len(items),
                "successes": sum(1 for row in items if row.get("success")),
                "negative_transfer": sum(1 for row in items if row.get("negative_transfer")),
                "public_passed_hidden_failed": sum(1 for row in items if row.get("public_passed_hidden_failed")),
                "total_tokens": total_tokens,
                "avg_tokens": total_tokens / len(items) if items else 0.0,
            }
        )
    return rows


def failure_rows(run_dir: Path, trajectories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metadata = RUN_METADATA.get(
        run_dir.name,
        {"setting": "unknown", "order": 999, "paper_role": "unclassified"},
    )
    rows = []
    for row in trajectories:
        if row.get("success"):
            continue
        patch = row.get("parsed_patch") or {}
        rows.append(
            {
                "run_name": run_dir.name,
                "setting": metadata["setting"],
                "setting_order": metadata["order"],
                "strategy": row.get("strategy"),
                "task_id": row.get("task_id"),
                "template": row.get("template"),
                "public_tests_passed": row.get("public_tests_passed"),
                "public_passed_hidden_failed": row.get("public_passed_hidden_failed"),
                "negative_transfer": row.get("negative_transfer"),
                "included_repo_tree": row.get("included_repo_tree"),
                "files_seen": row.get("files_seen", []),
                "used_artifact": patch.get("used_artifact"),
                "diagnosis": str(patch.get("diagnosis", "")).strip(),
                "notes": str(patch.get("notes", "")).strip(),
                "applied_paths": [edit.get("path") for edit in row.get("applied_edits", [])],
                "final_stdout_tail": str(row.get("final_verifier", {}).get("stdout_tail", "")).strip()[-1200:],
                "final_stderr_tail": str(row.get("final_verifier", {}).get("stderr_tail", "")).strip()[-1200:],
            }
        )
    return rows


def build_matrix(run_root: Path) -> dict[str, Any]:
    run_summaries = []
    strategies = []
    templates = []
    failures = []

    for run_dir in hard_v2_run_dirs(run_root):
        summary_path = run_dir / "summary.json"
        trajectories_path = run_dir / "trajectories.jsonl"
        summary = read_json(summary_path)
        trajectories = read_jsonl(trajectories_path) if trajectories_path.exists() else []
        metadata = RUN_METADATA.get(
            run_dir.name,
            {"setting": "unknown", "order": 999, "paper_role": "unclassified"},
        )
        run_summaries.append(
            {
                "run_name": run_dir.name,
                "setting": metadata["setting"],
                "setting_order": metadata["order"],
                "paper_role": metadata["paper_role"],
                "total_rows": summary.get("total_rows"),
                "trajectory_rows": len(trajectories),
                "source_files": {
                    "summary": source_info(summary_path),
                    "trajectories": source_info(trajectories_path) if trajectories_path.exists() else None,
                },
            }
        )
        strategies.extend(strategy_rows(run_dir, summary, trajectories))
        templates.extend(template_rows(run_dir, trajectories))
        failures.extend(failure_rows(run_dir, trajectories))

    strategies.sort(key=lambda row: (row["setting_order"], row["run_name"], row["strategy"]))
    templates.sort(key=lambda row: (row["setting_order"], row["run_name"], row["strategy"], row["template"]))
    failures.sort(key=lambda row: (row["setting_order"], row["run_name"], row["strategy"], row["task_id"]))
    run_summaries.sort(key=lambda row: (row["setting_order"], row["run_name"]))

    matrix = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_root": run_root.relative_to(ROOT).as_posix(),
        "run_summaries": run_summaries,
        "strategy_matrix": strategies,
        "template_matrix": templates,
        "failures": failures,
    }
    matrix["stability_groups"] = stability_groups(matrix)
    return matrix


def metric(matrix: dict[str, Any], run_name: str, strategy: str) -> dict[str, Any]:
    for row in matrix["strategy_matrix"]:
        if row["run_name"] == run_name and row["strategy"] == strategy:
            return row
    raise KeyError(f"Missing run/strategy: {run_name}/{strategy}")


def stability_groups(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for group in STABILITY_GROUPS:
        members = []
        success_values = []
        token_values = []
        failure_tasks: dict[str, list[str]] = {}
        missing = []
        for run_name, strategy in group["members"]:
            try:
                row = metric(matrix, run_name, strategy)
            except KeyError:
                missing.append({"run_name": run_name, "strategy": strategy})
                continue
            failures = [
                failure["task_id"]
                for failure in matrix["failures"]
                if failure["run_name"] == run_name and failure["strategy"] == strategy
            ]
            members.append(
                {
                    "run_name": run_name,
                    "strategy": strategy,
                    "successes": row["successes"],
                    "tasks": row["tasks"],
                    "total_tokens": row["total_tokens"],
                    "negative_transfer": row["negative_transfer"],
                    "public_passed_hidden_failed": row["public_passed_hidden_failed"],
                    "failure_tasks": failures,
                }
            )
            success_values.append(row["successes"])
            token_values.append(row["total_tokens"])
            failure_tasks[run_name] = failures

        rows.append(
            {
                "name": group["name"],
                "interpretation": group["interpretation"],
                "members": members,
                "missing_members": missing,
                "min_successes": min(success_values) if success_values else None,
                "max_successes": max(success_values) if success_values else None,
                "successes_values": success_values,
                "min_total_tokens": min(token_values) if token_values else None,
                "max_total_tokens": max(token_values) if token_values else None,
                "token_values": token_values,
                "failure_tasks_by_run": failure_tasks,
            }
        )
    return rows


def assert_current_hard_v2(matrix: dict[str, Any]) -> None:
    expected = [
        ("llm_downstream_hard_v2_full_25x6", "distilled_skills_all", 25, 25),
        ("llm_downstream_hard_v2_full_25x6", "skilladmit_selected", 23, 25),
        ("llm_downstream_hard_v2_tree_25x2", "no_experience", 23, 25),
        ("llm_downstream_hard_v2_tree_25x2", "skilladmit_selected", 25, 25),
        ("llm_downstream_hard_v2_precondition_only_25", "skilladmit_selected_with_precondition_only", 24, 25),
        ("llm_downstream_hard_v2_selected_precondition_25", "skilladmit_selected_with_precondition_context", 25, 25),
        ("llm_downstream_hard_v2_replication_tree_selected_25", "skilladmit_selected", 25, 25),
        (
            "llm_downstream_hard_v2_replication_selected_precondition_25",
            "skilladmit_selected_with_precondition_context",
            25,
            25,
        ),
        (
            "llm_downstream_hard_v2_replication_precondition_only_25",
            "skilladmit_selected_with_precondition_only",
            23,
            25,
        ),
    ]
    for run_name, strategy, successes, tasks in expected:
        row = metric(matrix, run_name, strategy)
        if row["successes"] != successes or row["tasks"] != tasks:
            raise AssertionError(
                f"{run_name}/{strategy}: expected {successes}/{tasks}, got {row['successes']}/{row['tasks']}"
            )

    precondition_only_failures = [
        row
        for row in matrix["failures"]
        if row["run_name"] == "llm_downstream_hard_v2_precondition_only_25"
        and row["strategy"] == "skilladmit_selected_with_precondition_only"
    ]
    if [row["task_id"] for row in precondition_only_failures] != ["hard_v2_py_import_012"]:
        raise AssertionError("precondition-only ablation should have exactly hard_v2_py_import_012 as its failure")

    t4_rows = [
        row
        for row in matrix["template_matrix"]
        if row["run_name"] == "llm_downstream_hard_v2_precondition_only_25"
        and row["strategy"] == "skilladmit_selected_with_precondition_only"
        and row["template"] == "T4_cwd_sensitive_path_hard"
    ]
    if not t4_rows or t4_rows[0]["successes"] != 5:
        raise AssertionError(
            "first precondition-only run should solve all five T4 cwd-sensitive tasks; "
            "replication T4 stability is checked separately"
        )

    replication_precondition_failures = [
        row
        for row in matrix["failures"]
        if row["run_name"] == "llm_downstream_hard_v2_replication_precondition_only_25"
        and row["strategy"] == "skilladmit_selected_with_precondition_only"
    ]
    if [row["task_id"] for row in replication_precondition_failures] != [
        "hard_v2_py_import_012",
        "hard_v2_py_import_018",
    ]:
        raise AssertionError(
            "replication precondition-only ablation should fail hard_v2_py_import_012 and hard_v2_py_import_018"
        )


def render_md(matrix: dict[str, Any]) -> str:
    lines = [
        "# Hard v2 Strategy Matrix",
        "",
        f"Generated at UTC: `{matrix['generated_at_utc']}`",
        "",
        "This report snapshots hard_v2 downstream summaries and trajectory hashes so updated run directories are detectable.",
        "",
        "## Strategy Matrix",
        "",
        "| setting | run | strategy | success | neg | public_hidden | adherence | parse | tokens | avg_tokens | tree_rows | visible_rows |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in matrix["strategy_matrix"]:
        lines.append(
            f"| {row['setting']} | `{row['run_name']}` | `{row['strategy']}` | "
            f"{row['successes']}/{row['tasks']} | {row['negative_transfer']} | "
            f"{row['public_passed_hidden_failed']} | {row['artifact_adherence']} | "
            f"{row['parse_errors']} | {row['total_tokens']} | {row['avg_tokens']:.1f} | "
            f"{row['included_repo_tree_rows']} | {row['visible_file_rows']} |"
        )

    lines.extend(
        [
            "",
            "## Template Matrix",
            "",
            "| setting | run | strategy | template | success | neg | public_hidden | tokens | avg_tokens |",
            "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in matrix["template_matrix"]:
        lines.append(
            f"| {row['setting']} | `{row['run_name']}` | `{row['strategy']}` | "
            f"{row['template']} | {row['successes']}/{row['tasks']} | "
            f"{row['negative_transfer']} | {row['public_passed_hidden_failed']} | "
            f"{row['total_tokens']} | {row['avg_tokens']:.1f} |"
        )

    lines.extend(
        [
            "",
            "## Failures",
            "",
            "| setting | run | strategy | task | template | public_hidden | used_artifact | short diagnosis |",
            "| --- | --- | --- | --- | --- | ---: | --- | --- |",
        ]
    )
    for row in matrix["failures"]:
        diagnosis = row["diagnosis"].replace("\n", " ")
        if len(diagnosis) > 160:
            diagnosis = diagnosis[:157] + "..."
        lines.append(
            f"| {row['setting']} | `{row['run_name']}` | `{row['strategy']}` | "
            f"{row['task_id']} | {row['template']} | {int(bool(row['public_passed_hidden_failed']))} | "
            f"{row.get('used_artifact') or ''} | {diagnosis} |"
        )

    lines.extend(
        [
            "",
            "## Stability Groups",
            "",
            "| group | success values | token values | failure tasks |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in matrix["stability_groups"]:
        failure_text = "; ".join(
            f"{run}: {','.join(tasks) if tasks else 'none'}"
            for run, tasks in row["failure_tasks_by_run"].items()
        )
        lines.append(
            f"| {row['name']} | {row['successes_values']} | {row['token_values']} | {failure_text} |"
        )

    lines.extend(
        [
            "",
            "## Source Hashes",
            "",
            "| run | summary_sha256 | trajectories_sha256 |",
            "| --- | --- | --- |",
        ]
    )
    for row in matrix["run_summaries"]:
        summary_hash = row["source_files"]["summary"]["sha256"][:16]
        traj = row["source_files"]["trajectories"]
        traj_hash = traj["sha256"][:16] if traj else ""
        lines.append(f"| `{row['run_name']}` | `{summary_hash}` | `{traj_hash}` |")

    lines.append("")
    return "\n".join(lines)


def write_outputs(matrix: dict[str, Any], output_json: Path, output_md: Path) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(render_md(matrix), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, default=RUN_ROOT)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--assert-current-hard-v2", action="store_true")
    args = parser.parse_args()

    run_root = args.run_root if args.run_root.is_absolute() else ROOT / args.run_root
    output_json = args.output_json if args.output_json.is_absolute() else ROOT / args.output_json
    output_md = args.output_md if args.output_md.is_absolute() else ROOT / args.output_md

    matrix = build_matrix(run_root)
    if args.assert_current_hard_v2:
        assert_current_hard_v2(matrix)
    write_outputs(matrix, output_json, output_md)

    print(f"runs: {len(matrix['run_summaries'])}")
    print(f"strategy_rows: {len(matrix['strategy_matrix'])}")
    print(f"template_rows: {len(matrix['template_matrix'])}")
    print(f"failures: {len(matrix['failures'])}")
    print(f"wrote_json: {output_json.relative_to(ROOT)}")
    print(f"wrote_md: {output_md.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
