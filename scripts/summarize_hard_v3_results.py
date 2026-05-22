#!/usr/bin/env python3
"""Summarize hard_v3 downstream validation results.

What this file does:
  Builds an auditable hard_v3 strategy matrix from completed LLM downstream
  runs, including strategy-level results, template-level results, failure rows,
  derived comparisons, source hashes, and explicit claim boundaries.

Why it is needed:
  hard_v3 now has multiple executor settings. Reading individual `summary.json`
  files is too easy to over-interpret. This report keeps the tree-aware and
  strict visible-file settings separate and makes unsupported claims explicit.

Inputs:
  benchmark/downstream/llm_runs/*/{summary.json,trajectories.jsonl}

Outputs:
  benchmark/downstream/reports/hard_v3_strategy_matrix.json
  benchmark/downstream/reports/hard_v3_strategy_matrix.md

Who runs it:
  Researchers or Codex sessions after adding, resuming, or recomputing hard_v3
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
DEFAULT_JSON = REPORT_DIR / "hard_v3_strategy_matrix.json"
DEFAULT_MD = REPORT_DIR / "hard_v3_strategy_matrix.md"

RUN_METADATA = {
    "llm_downstream_hard_v3_tree_core_30x2": {
        "setting": "tree_aware",
        "order": 10,
        "paper_role": "tree-aware full strategy matrix after core extension",
    },
    "llm_downstream_hard_v3_strict_30x8": {
        "setting": "strict_visible_file",
        "order": 20,
        "paper_role": "strict visible-file and precondition-only matrix",
    },
}

EXPECTED_CURRENT = {
    ("llm_downstream_hard_v3_tree_core_30x2", "bad_dependency_rule"): (30, 30, 0),
    ("llm_downstream_hard_v3_tree_core_30x2", "distilled_skills_all"): (30, 30, 0),
    ("llm_downstream_hard_v3_tree_core_30x2", "forced_bad_artifact"): (0, 30, 30),
    ("llm_downstream_hard_v3_tree_core_30x2", "no_experience"): (29, 30, 0),
    ("llm_downstream_hard_v3_tree_core_30x2", "promoted_rules"): (29, 30, 1),
    ("llm_downstream_hard_v3_tree_core_30x2", "raw_memory"): (30, 30, 0),
    ("llm_downstream_hard_v3_tree_core_30x2", "skilladmit_selected"): (29, 30, 0),
    ("llm_downstream_hard_v3_tree_core_30x2", "skilladmit_selected_with_precondition_context"): (29, 30, 0),
    ("llm_downstream_hard_v3_strict_30x8", "bad_dependency_rule"): (30, 30, 0),
    ("llm_downstream_hard_v3_strict_30x8", "distilled_skills_all"): (29, 30, 1),
    ("llm_downstream_hard_v3_strict_30x8", "forced_bad_artifact"): (0, 30, 30),
    ("llm_downstream_hard_v3_strict_30x8", "no_experience"): (28, 30, 0),
    ("llm_downstream_hard_v3_strict_30x8", "promoted_rules"): (29, 30, 0),
    ("llm_downstream_hard_v3_strict_30x8", "raw_memory"): (30, 30, 0),
    ("llm_downstream_hard_v3_strict_30x8", "skilladmit_selected"): (29, 30, 0),
    ("llm_downstream_hard_v3_strict_30x8", "skilladmit_selected_with_precondition_only"): (30, 30, 0),
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


def hard_v3_run_dirs(run_root: Path) -> list[Path]:
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
    tree_no = find_strategy(matrix, "llm_downstream_hard_v3_tree_core_30x2", "no_experience")
    tree_selected = find_strategy(matrix, "llm_downstream_hard_v3_tree_core_30x2", "skilladmit_selected")
    tree_pre = find_strategy(
        matrix,
        "llm_downstream_hard_v3_tree_core_30x2",
        "skilladmit_selected_with_precondition_context",
    )
    tree_raw = find_strategy(matrix, "llm_downstream_hard_v3_tree_core_30x2", "raw_memory")
    tree_all = find_strategy(matrix, "llm_downstream_hard_v3_tree_core_30x2", "distilled_skills_all")
    strict_no = find_strategy(matrix, "llm_downstream_hard_v3_strict_30x8", "no_experience")
    strict_selected = find_strategy(matrix, "llm_downstream_hard_v3_strict_30x8", "skilladmit_selected")
    strict_pre = find_strategy(
        matrix,
        "llm_downstream_hard_v3_strict_30x8",
        "skilladmit_selected_with_precondition_only",
    )
    strict_raw = find_strategy(matrix, "llm_downstream_hard_v3_strict_30x8", "raw_memory")

    return {
        "tree_selected_success_delta_vs_no_experience": tree_selected["successes"] - tree_no["successes"],
        "tree_selected_token_delta_vs_no_experience": tree_selected["total_tokens"] - tree_no["total_tokens"],
        "tree_precondition_context_success_delta_vs_selected": tree_pre["successes"] - tree_selected["successes"],
        "tree_precondition_context_token_delta_vs_selected": tree_pre["total_tokens"] - tree_selected["total_tokens"],
        "tree_raw_memory_success_delta_vs_no_experience": tree_raw["successes"] - tree_no["successes"],
        "tree_raw_memory_token_delta_vs_no_experience": tree_raw["total_tokens"] - tree_no["total_tokens"],
        "tree_all_skills_success_delta_vs_selected": tree_all["successes"] - tree_selected["successes"],
        "tree_all_skills_token_delta_vs_selected": tree_all["total_tokens"] - tree_selected["total_tokens"],
        "strict_selected_success_delta_vs_no_experience": strict_selected["successes"] - strict_no["successes"],
        "strict_selected_token_delta_vs_no_experience": strict_selected["total_tokens"] - strict_no["total_tokens"],
        "strict_precondition_only_success_delta_vs_selected": strict_pre["successes"] - strict_selected["successes"],
        "strict_precondition_only_token_delta_vs_selected": strict_pre["total_tokens"] - strict_selected["total_tokens"],
        "strict_raw_memory_success_delta_vs_no_experience": strict_raw["successes"] - strict_no["successes"],
        "strict_raw_memory_token_delta_vs_no_experience": strict_raw["total_tokens"] - strict_no["total_tokens"],
    }


def claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "Hard v3 is a fresh 30-task downstream validation boundary with hidden verifiers.",
            "The completed hard_v3 runs contain no parse errors.",
            (
                "Forced bad artifacts produce systematic negative transfer in both settings: "
                "0/30 with 30 public-pass/hidden-fail cases."
            ),
            (
                "In the strict visible-file setting, selected + preconditions only reaches 30/30, "
                "while ordinary selected reaches 29/30 and no_experience reaches 28/30."
            ),
            (
                "In the tree-aware setting, all-skills, raw-memory, and bad-dependency-rule contexts "
                "reach 30/30, while selected, selected+precondition-context, and no_experience are 29/30."
            ),
        ],
        "not_supported": [
            "Hard v3 does not support a SkillAdmit-selected superiority claim.",
            "Hard v3 does not support a token-savings claim for SkillAdmit-selected.",
            "Hard v3 does not show that selected+precondition-context beats ordinary tree-aware selected.",
            "Hard v3 does not show that raw memory or bad dependency rule are safe admission policies.",
            (
                "The bad_dependency_rule LLM condition often succeeds because the model does not reliably "
                "adhere to the harmful artifact; the forced_bad_artifact condition is the negative-transfer control."
            ),
            "Do not tune prompts, strategy text, or task design from the observed hard_v3 failures.",
        ],
    }


def build_matrix(run_root: Path) -> dict[str, Any]:
    run_summaries = []
    strategies = []
    templates = []
    failures = []

    for run_dir in hard_v3_run_dirs(run_root):
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


def assert_current_hard_v3(matrix: dict[str, Any]) -> None:
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
        "# Hard v3 Strategy Matrix",
        "",
        f"Generated at UTC: `{matrix['generated_at_utc']}`",
        "",
        "This report snapshots hard_v3 downstream summaries and trajectory hashes.",
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
    parser.add_argument("--assert-current-hard-v3", action="store_true")
    args = parser.parse_args()

    run_root = args.run_root if args.run_root.is_absolute() else ROOT / args.run_root
    matrix = build_matrix(run_root)
    if args.assert_current_hard_v3:
        assert_current_hard_v3(matrix)

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
