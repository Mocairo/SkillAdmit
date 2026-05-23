#!/usr/bin/env python3
"""Summarize hard_v4 downstream validation results.

What this file does:
  Builds an auditable hard_v4 strategy matrix from the completed LLM downstream
  runs. The report keeps tree-aware and strict visible-file settings separate,
  records source hashes, and makes the hard_v4 claim boundary explicit.

Why it is needed:
  hard_v4 is a fresh downstream boundary after hard_v2 and hard_v3. Its result
  is not a SkillAdmit-selected win: tree-aware saturates, while strict visible
  file favors no_experience over ordinary selected. This script prevents those
  results from being flattened into a misleading leaderboard.

Inputs:
  benchmark/downstream/llm_runs/*/{summary.json,trajectories.jsonl}

Outputs:
  benchmark/downstream/reports/hard_v4_strategy_matrix.json
  benchmark/downstream/reports/hard_v4_strategy_matrix.md

Who runs it:
  Researchers or Codex sessions after adding, resuming, or recomputing hard_v4
  downstream runs.
"""

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
DEFAULT_JSON = REPORT_DIR / "hard_v4_strategy_matrix.json"
DEFAULT_MD = REPORT_DIR / "hard_v4_strategy_matrix.md"

RUN_METADATA = {
    "llm_downstream_hard_v4_tree_24x8": {
        "setting": "tree_aware",
        "order": 10,
        "paper_role": "tree-aware hard_v4 strategy matrix",
    },
    "llm_downstream_hard_v4_strict_24x8": {
        "setting": "strict_visible_file",
        "order": 20,
        "paper_role": "strict visible-file hard_v4 strategy matrix",
    },
}

EXPECTED_CURRENT = {
    ("llm_downstream_hard_v4_tree_24x8", "bad_dependency_rule"): (24, 24, 0),
    ("llm_downstream_hard_v4_tree_24x8", "distilled_skills_all"): (24, 24, 0),
    ("llm_downstream_hard_v4_tree_24x8", "forced_bad_artifact"): (0, 24, 24),
    ("llm_downstream_hard_v4_tree_24x8", "no_experience"): (24, 24, 0),
    ("llm_downstream_hard_v4_tree_24x8", "promoted_rules"): (24, 24, 0),
    ("llm_downstream_hard_v4_tree_24x8", "raw_memory"): (24, 24, 0),
    ("llm_downstream_hard_v4_tree_24x8", "skilladmit_selected"): (24, 24, 0),
    ("llm_downstream_hard_v4_tree_24x8", "skilladmit_selected_with_precondition_context"): (24, 24, 0),
    ("llm_downstream_hard_v4_strict_24x8", "bad_dependency_rule"): (24, 24, 0),
    ("llm_downstream_hard_v4_strict_24x8", "distilled_skills_all"): (24, 24, 0),
    ("llm_downstream_hard_v4_strict_24x8", "forced_bad_artifact"): (0, 24, 24),
    ("llm_downstream_hard_v4_strict_24x8", "no_experience"): (24, 24, 0),
    ("llm_downstream_hard_v4_strict_24x8", "promoted_rules"): (23, 24, 0),
    ("llm_downstream_hard_v4_strict_24x8", "raw_memory"): (23, 24, 0),
    ("llm_downstream_hard_v4_strict_24x8", "skilladmit_selected"): (22, 24, 0),
    ("llm_downstream_hard_v4_strict_24x8", "skilladmit_selected_with_precondition_only"): (23, 24, 0),
}


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


def hard_v4_run_dirs(run_root: Path) -> list[Path]:
    return [
        run_root / run_name
        for run_name in sorted(RUN_METADATA, key=lambda item: RUN_METADATA[item]["order"])
        if (run_root / run_name / "summary.json").exists()
    ]


def success_text(successes: int, tasks: int) -> str:
    return f"{successes}/{tasks}"


def strategy_rows(run_dir: Path, summary: dict[str, Any], trajectories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metadata = RUN_METADATA[run_dir.name]
    by_strategy: dict[str, list[dict[str, Any]]] = {}
    for row in trajectories:
        by_strategy.setdefault(row["strategy"], []).append(row)

    rows = []
    for strategy, item in sorted(summary.get("strategies", {}).items()):
        items = by_strategy.get(strategy, [])
        rows.append(
            {
                "run_name": run_dir.name,
                "setting": metadata["setting"],
                "setting_order": metadata["order"],
                "paper_role": metadata["paper_role"],
                "strategy": strategy,
                "tasks": item["tasks"],
                "successes": item["successes"],
                "success": success_text(item["successes"], item["tasks"]),
                "success_rate": item["success_rate"],
                "negative_transfer": item["negative_transfer"],
                "public_passed_hidden_failed": item.get("public_passed_hidden_failed", 0),
                "artifact_adherence": item.get("artifact_adherence", 0),
                "parse_errors": item.get("parse_errors", 0),
                "total_tokens": item.get("total_tokens", 0),
                "avg_tokens": item.get("avg_tokens", 0.0),
                "included_repo_tree_rows": sum(1 for row in items if row.get("included_repo_tree")),
                "visible_file_rows": sum(1 for row in items if row.get("used_task_visible_files")),
            }
        )
    return rows


def template_rows(run_dir: Path, trajectories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metadata = RUN_METADATA[run_dir.name]
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in trajectories:
        grouped.setdefault((row["strategy"], row["template"]), []).append(row)

    rows = []
    for (strategy, template), items in sorted(grouped.items()):
        total_tokens = sum(int((row.get("model_usage") or {}).get("total_tokens") or 0) for row in items)
        successes = sum(1 for row in items if row.get("success"))
        rows.append(
            {
                "run_name": run_dir.name,
                "setting": metadata["setting"],
                "setting_order": metadata["order"],
                "strategy": strategy,
                "template": template,
                "tasks": len(items),
                "successes": successes,
                "success": success_text(successes, len(items)),
                "negative_transfer": sum(1 for row in items if row.get("negative_transfer")),
                "public_passed_hidden_failed": sum(1 for row in items if row.get("public_passed_hidden_failed")),
                "total_tokens": total_tokens,
                "avg_tokens": total_tokens / len(items) if items else 0.0,
            }
        )
    return rows


def failure_rows(run_dir: Path, trajectories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metadata = RUN_METADATA[run_dir.name]
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
                "used_artifact": patch.get("used_artifact"),
                "diagnosis": str(patch.get("diagnosis", "")).strip(),
                "notes": str(patch.get("notes", "")).strip(),
                "applied_paths": [edit.get("path") for edit in row.get("applied_edits", [])],
                "final_stdout_tail": str(row.get("final_verifier", {}).get("stdout_tail", "")).strip()[-1200:],
                "final_stderr_tail": str(row.get("final_verifier", {}).get("stderr_tail", "")).strip()[-1200:],
            }
        )
    return rows


def find_strategy(matrix: dict[str, Any], run_name: str, strategy: str) -> dict[str, Any]:
    for row in matrix["strategy_matrix"]:
        if row["run_name"] == run_name and row["strategy"] == strategy:
            return row
    raise KeyError(f"Missing strategy row: {run_name}/{strategy}")


def build_derived_comparisons(matrix: dict[str, Any]) -> dict[str, Any]:
    tree_no = find_strategy(matrix, "llm_downstream_hard_v4_tree_24x8", "no_experience")
    tree_selected = find_strategy(matrix, "llm_downstream_hard_v4_tree_24x8", "skilladmit_selected")
    tree_pre = find_strategy(
        matrix,
        "llm_downstream_hard_v4_tree_24x8",
        "skilladmit_selected_with_precondition_context",
    )
    tree_all = find_strategy(matrix, "llm_downstream_hard_v4_tree_24x8", "distilled_skills_all")
    strict_no = find_strategy(matrix, "llm_downstream_hard_v4_strict_24x8", "no_experience")
    strict_selected = find_strategy(matrix, "llm_downstream_hard_v4_strict_24x8", "skilladmit_selected")
    strict_pre = find_strategy(
        matrix,
        "llm_downstream_hard_v4_strict_24x8",
        "skilladmit_selected_with_precondition_only",
    )
    strict_raw = find_strategy(matrix, "llm_downstream_hard_v4_strict_24x8", "raw_memory")
    strict_promoted = find_strategy(matrix, "llm_downstream_hard_v4_strict_24x8", "promoted_rules")
    strict_all = find_strategy(matrix, "llm_downstream_hard_v4_strict_24x8", "distilled_skills_all")
    forced_rows = [
        find_strategy(matrix, "llm_downstream_hard_v4_tree_24x8", "forced_bad_artifact"),
        find_strategy(matrix, "llm_downstream_hard_v4_strict_24x8", "forced_bad_artifact"),
    ]

    return {
        "tree_selected_success_delta_vs_no_experience": tree_selected["successes"] - tree_no["successes"],
        "tree_selected_token_delta_vs_no_experience": tree_selected["total_tokens"] - tree_no["total_tokens"],
        "tree_precondition_context_success_delta_vs_selected": tree_pre["successes"] - tree_selected["successes"],
        "tree_precondition_context_token_delta_vs_selected": tree_pre["total_tokens"] - tree_selected["total_tokens"],
        "tree_all_skills_success_delta_vs_no_experience": tree_all["successes"] - tree_no["successes"],
        "tree_all_skills_token_delta_vs_no_experience": tree_all["total_tokens"] - tree_no["total_tokens"],
        "strict_selected_success_delta_vs_no_experience": strict_selected["successes"] - strict_no["successes"],
        "strict_selected_token_delta_vs_no_experience": strict_selected["total_tokens"] - strict_no["total_tokens"],
        "strict_precondition_only_success_delta_vs_selected": strict_pre["successes"] - strict_selected["successes"],
        "strict_precondition_only_token_delta_vs_selected": strict_pre["total_tokens"] - strict_selected["total_tokens"],
        "strict_raw_memory_success_delta_vs_no_experience": strict_raw["successes"] - strict_no["successes"],
        "strict_raw_memory_token_delta_vs_no_experience": strict_raw["total_tokens"] - strict_no["total_tokens"],
        "strict_promoted_rules_success_delta_vs_no_experience": strict_promoted["successes"] - strict_no["successes"],
        "strict_all_skills_success_delta_vs_no_experience": strict_all["successes"] - strict_no["successes"],
        "forced_bad_total_successes": sum(row["successes"] for row in forced_rows),
        "forced_bad_total_tasks": sum(row["tasks"] for row in forced_rows),
        "forced_bad_total_public_passed_hidden_failed": sum(
            row["public_passed_hidden_failed"] for row in forced_rows
        ),
        "selected_superiority_supported": False,
        "selected_token_savings_supported": False,
    }


def claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "Hard v4 is a fresh 24-task downstream validation boundary with hidden verifiers.",
            "The completed hard_v4 runs contain no parse errors.",
            "Tree-aware hard_v4 is saturated: every non-forced strategy reaches 24/24.",
            (
                "Strict visible-file hard_v4 rejects selected superiority: "
                "SkillAdmit-selected reaches 22/24, while no_experience reaches 24/24."
            ),
            (
                "Strict precondition-only improves over ordinary selected by one task "
                "but still trails no_experience and all-skills."
            ),
            (
                "Forced bad artifacts produce systematic negative transfer across hard_v4: "
                "0/48 success with 48 public-pass/hidden-fail cases."
            ),
            (
                "The ordinary bad_dependency_rule condition succeeds only with low artifact adherence "
                "(7/24 tree-aware and 4/24 strict), so its success mainly shows that the model can ignore harmful advice."
            ),
        ],
        "not_supported": [
            "Hard v4 does not support a SkillAdmit-selected downstream-success claim.",
            "Hard v4 does not support a SkillAdmit-selected token-savings claim.",
            "Hard v4 does not show that precondition-only can replace repo tree.",
            "Hard v4 does not prove that bad dependency advice is safe.",
            "Do not tune prompts, strategy text, or task design from observed hard_v4 failures.",
        ],
    }


def build_matrix(run_root: Path) -> dict[str, Any]:
    run_summaries = []
    strategies = []
    templates = []
    failures = []

    for run_dir in hard_v4_run_dirs(run_root):
        summary_path = run_dir / "summary.json"
        trajectories_path = run_dir / "trajectories.jsonl"
        summary = read_json(summary_path)
        trajectories = read_jsonl(trajectories_path)
        metadata = RUN_METADATA[run_dir.name]
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
                    "trajectories": source_info(trajectories_path),
                },
            }
        )
        strategies.extend(strategy_rows(run_dir, summary, trajectories))
        templates.extend(template_rows(run_dir, trajectories))
        failures.extend(failure_rows(run_dir, trajectories))

    matrix = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_summaries": sorted(run_summaries, key=lambda row: row["setting_order"]),
        "strategy_matrix": sorted(strategies, key=lambda row: (row["setting_order"], row["strategy"])),
        "template_matrix": sorted(templates, key=lambda row: (row["setting_order"], row["strategy"], row["template"])),
        "failures": sorted(
            failures,
            key=lambda row: (row["setting_order"], row["strategy"], row["task_id"]),
        ),
        "claim_boundary": claim_boundary(),
    }
    matrix["derived_comparisons"] = build_derived_comparisons(matrix)
    return matrix


def assert_current_hard_v4(matrix: dict[str, Any]) -> None:
    observed = {
        (row["run_name"], row["strategy"]): (
            row["successes"],
            row["tasks"],
            row["public_passed_hidden_failed"],
        )
        for row in matrix["strategy_matrix"]
    }
    for key, expected in EXPECTED_CURRENT.items():
        actual = observed.get(key)
        if actual != expected:
            raise AssertionError(f"{key}: expected {expected}, got {actual}")

    for row in matrix["strategy_matrix"]:
        if row["parse_errors"] != 0:
            raise AssertionError(f"{row['run_name']}/{row['strategy']} has parse errors")


def short_hash(value: str) -> str:
    return value[:16]


def md_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return lines


def render_markdown(matrix: dict[str, Any]) -> str:
    lines = [
        "# Hard v4 Strategy Matrix",
        "",
        f"Generated at UTC: `{matrix['generated_at_utc']}`",
        "",
        "This report snapshots hard_v4 downstream summaries and trajectory hashes.",
        "Tree-aware and strict visible-file settings are intentionally reported separately.",
        "",
        "## Strategy Matrix",
        "",
    ]

    strategy_rows_md = []
    for row in matrix["strategy_matrix"]:
        strategy_rows_md.append(
            [
                row["setting"],
                f"`{row['run_name']}`",
                f"`{row['strategy']}`",
                row["success"],
                str(row["negative_transfer"]),
                str(row["public_passed_hidden_failed"]),
                str(row["artifact_adherence"]),
                str(row["parse_errors"]),
                str(row["total_tokens"]),
                f"{row['avg_tokens']:.1f}",
                str(row["included_repo_tree_rows"]),
                str(row["visible_file_rows"]),
            ]
        )
    lines.extend(
        md_table(
            [
                "setting",
                "run",
                "strategy",
                "success",
                "neg",
                "public_hidden",
                "adherence",
                "parse",
                "tokens",
                "avg_tokens",
                "tree_rows",
                "visible_rows",
            ],
            strategy_rows_md,
        )
    )

    lines.extend(["", "## Template Matrix", ""])
    template_rows_md = []
    for row in matrix["template_matrix"]:
        template_rows_md.append(
            [
                row["setting"],
                f"`{row['strategy']}`",
                row["template"],
                row["success"],
                str(row["negative_transfer"]),
                str(row["public_passed_hidden_failed"]),
                str(row["total_tokens"]),
                f"{row['avg_tokens']:.1f}",
            ]
        )
    lines.extend(
        md_table(
            ["setting", "strategy", "template", "success", "neg", "public_hidden", "tokens", "avg_tokens"],
            template_rows_md,
        )
    )

    lines.extend(["", "## Derived Comparisons", ""])
    comparison_rows = [[key, str(value)] for key, value in sorted(matrix["derived_comparisons"].items())]
    lines.extend(md_table(["comparison", "value"], comparison_rows))

    lines.extend(["", "## Failures", ""])
    failure_rows_md = []
    for row in matrix["failures"]:
        diagnosis = row["diagnosis"].replace("\n", " ")
        if len(diagnosis) > 140:
            diagnosis = diagnosis[:137] + "..."
        failure_rows_md.append(
            [
                row["setting"],
                f"`{row['strategy']}`",
                row["task_id"],
                row["template"],
                str(int(bool(row["public_passed_hidden_failed"]))),
                str(int(bool(row["negative_transfer"]))),
                str(row["used_artifact"]),
                diagnosis,
            ]
        )
    lines.extend(
        md_table(
            ["setting", "strategy", "task", "template", "public_hidden", "neg", "used_artifact", "short diagnosis"],
            failure_rows_md,
        )
    )

    lines.extend(["", "## Claim Boundary", "", "Supported:"])
    for claim in matrix["claim_boundary"]["supported"]:
        lines.append(f"- {claim}")
    lines.extend(["", "Not supported:"])
    for claim in matrix["claim_boundary"]["not_supported"]:
        lines.append(f"- {claim}")

    lines.extend(["", "## Source Hashes", ""])
    hash_rows = []
    for run in matrix["run_summaries"]:
        summary = run["source_files"]["summary"]
        trajectories = run["source_files"]["trajectories"]
        hash_rows.append(
            [
                f"`{run['run_name']}`",
                f"`{short_hash(summary['sha256'])}`",
                f"`{short_hash(trajectories['sha256'])}`",
            ]
        )
    lines.extend(md_table(["run", "summary_sha256", "trajectories_sha256"], hash_rows))
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", type=Path, default=RUN_ROOT)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--assert-current-hard-v4", action="store_true")
    args = parser.parse_args()

    run_root = args.run_root if args.run_root.is_absolute() else ROOT / args.run_root
    matrix = build_matrix(run_root)
    if args.assert_current_hard_v4:
        assert_current_hard_v4(matrix)

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    args.out_md.write_text(render_markdown(matrix), encoding="utf-8")

    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")
    print(f"strategy_rows: {len(matrix['strategy_matrix'])}")
    print(f"template_rows: {len(matrix['template_matrix'])}")
    print(f"failure_rows: {len(matrix['failures'])}")


if __name__ == "__main__":
    main()
