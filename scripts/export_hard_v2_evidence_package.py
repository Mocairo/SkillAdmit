#!/usr/bin/env python3
"""Export paper-facing hard_v2 downstream evidence.

What this file does:
  Builds a compact evidence package from the hard_v2 downstream run ledger:
  primary strategy table, stability table, failure taxonomy, provenance hashes,
  and explicit supported/unsupported paper claims.

Why it is needed:
  `summary.json` files are per-run artifacts and are easy to over-read in
  isolation. This script turns the full hard_v2 ledger into stable paper-facing
  tables while preserving the claim boundary between strict-visible,
  tree-aware, precondition-context, and negative-transfer settings.

Inputs:
  benchmark/downstream/llm_runs/*/{summary.json,trajectories.jsonl}
  via scripts/summarize_hard_v2_results.py

Outputs:
  benchmark/downstream/reports/hard_v2_evidence_package.json
  benchmark/downstream/reports/hard_v2_paper_tables.md
  benchmark/downstream/reports/hard_v2_paper_tables.tex

Who runs it:
  Researchers or Codex sessions after hard_v2 runs are added, resumed,
  recomputed, or before writing the downstream-validation section of a paper.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from summarize_hard_v2_results import (
    REPORT_DIR,
    RUN_ROOT,
    assert_current_hard_v2,
    build_matrix,
)


DEFAULT_JSON = REPORT_DIR / "hard_v2_evidence_package.json"
DEFAULT_MD = REPORT_DIR / "hard_v2_paper_tables.md"
DEFAULT_TEX = REPORT_DIR / "hard_v2_paper_tables.tex"

PRIMARY_ROWS = [
    ("strict visible", "llm_downstream_hard_v2_full_25x6", "no_experience"),
    ("strict visible", "llm_downstream_hard_v2_full_25x6", "skilladmit_selected"),
    ("strict visible", "llm_downstream_hard_v2_full_25x6", "raw_memory"),
    ("strict visible", "llm_downstream_hard_v2_full_25x6", "promoted_rules"),
    ("strict visible", "llm_downstream_hard_v2_full_25x6", "bad_dependency_rule"),
    ("strict visible", "llm_downstream_hard_v2_full_25x6", "distilled_skills_all"),
    ("tree-aware", "llm_downstream_hard_v2_tree_25x2", "no_experience"),
    ("tree-aware", "llm_downstream_hard_v2_tree_25x2", "skilladmit_selected"),
    (
        "tree-aware + preconditions",
        "llm_downstream_hard_v2_selected_precondition_25",
        "skilladmit_selected_with_precondition_context",
    ),
    (
        "strict + preconditions only",
        "llm_downstream_hard_v2_precondition_only_25",
        "skilladmit_selected_with_precondition_only",
    ),
    ("forced harmful artifact", "llm_downstream_hard_v2_forced_bad_25", "forced_bad_artifact"),
]

DISPLAY = {
    "no_experience": "No experience",
    "skilladmit_selected": "SkillAdmit-selected",
    "raw_memory": "Raw memory",
    "promoted_rules": "Promoted rules",
    "bad_dependency_rule": "Bad dependency rule",
    "distilled_skills_all": "All distilled skills",
    "skilladmit_selected_with_precondition_context": "Selected + tree + preconditions",
    "skilladmit_selected_with_precondition_only": "Selected + preconditions only",
    "forced_bad_artifact": "Forced bad artifact",
}

CLAIM_BOUNDARY = {
    "supported": [
        (
            "Hard v2 is a validated 25-task downstream suite with fail-first, "
            "gold-pass, forced-public-pass, and forced-hidden-fail checks."
        ),
        (
            "Forced harmful artifacts produce systematic negative transfer: "
            "0/25 success with 25 public-pass/hidden-fail cases."
        ),
        (
            "In the tree-aware coding-agent setting, SkillAdmit-selected reached "
            "25/25 while no_experience reached 23/25 in the original hard_v2 tree-aware run."
        ),
        (
            "Tree-aware SkillAdmit-selected is stable across the two completed "
            "full 25-task calls: 25/25 and 25/25."
        ),
        (
            "Tree-aware selected + precondition context is also stable across "
            "two completed calls: 25/25 and 25/25."
        ),
        (
            "Strict precondition-only is a weaker ablation, not a replacement "
            "for repo-tree context: 24/25 on the first run and 23/25 on replication."
        ),
    ],
    "not_supported": [
        "SkillAdmit-selected dominates every baseline under every prompt setting.",
        "SkillAdmit-selected has demonstrated token savings over no_experience on hard_v2.",
        "Selected + precondition context is more accurate than ordinary tree-aware selected.",
        "Precondition text alone can replace repository-tree context.",
        "Admission-label accuracy alone proves downstream utility.",
        "The current v7 admission set remains clean held-out evidence after error inspection or tuning.",
    ],
}


def find_strategy(matrix: dict[str, Any], run_name: str, strategy: str) -> dict[str, Any]:
    for row in matrix["strategy_matrix"]:
        if row["run_name"] == run_name and row["strategy"] == strategy:
            return row
    raise KeyError(f"Missing strategy row: {run_name}/{strategy}")


def ratio(successes: int, tasks: int) -> str:
    return f"{successes}/{tasks}"


def primary_strategy_table(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for setting, run_name, strategy in PRIMARY_ROWS:
        row = find_strategy(matrix, run_name, strategy)
        rows.append(
            {
                "setting": setting,
                "run_name": run_name,
                "strategy": strategy,
                "display_strategy": DISPLAY.get(strategy, strategy),
                "success": ratio(row["successes"], row["tasks"]),
                "successes": row["successes"],
                "tasks": row["tasks"],
                "negative_transfer": row["negative_transfer"],
                "public_passed_hidden_failed": row["public_passed_hidden_failed"],
                "total_tokens": row["total_tokens"],
                "avg_tokens": round(float(row["avg_tokens"]), 2),
                "included_repo_tree_rows": row["included_repo_tree_rows"],
                "visible_file_rows": row["visible_file_rows"],
            }
        )
    return rows


def stability_table(matrix: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for group in matrix["stability_groups"]:
        rows.append(
            {
                "group": group["name"],
                "interpretation": group["interpretation"],
                "success_values": group["successes_values"],
                "token_values": group["token_values"],
                "failure_tasks_by_run": group["failure_tasks_by_run"],
                "min_successes": group["min_successes"],
                "max_successes": group["max_successes"],
            }
        )
    return rows


def failure_taxonomy(matrix: dict[str, Any]) -> dict[str, Any]:
    by_setting_strategy_template: Counter[tuple[str, str, str]] = Counter()
    by_strategy: Counter[str] = Counter()
    public_hidden_by_strategy: Counter[str] = Counter()
    negative_by_strategy: Counter[str] = Counter()
    precondition_only_failures = []

    for row in matrix["failures"]:
        key = (row["setting"], row["strategy"], row["template"])
        by_setting_strategy_template[key] += 1
        by_strategy[row["strategy"]] += 1
        if row["public_passed_hidden_failed"]:
            public_hidden_by_strategy[row["strategy"]] += 1
        if row["negative_transfer"]:
            negative_by_strategy[row["strategy"]] += 1
        if row["strategy"] == "skilladmit_selected_with_precondition_only":
            precondition_only_failures.append(
                {
                    "run_name": row["run_name"],
                    "task_id": row["task_id"],
                    "template": row["template"],
                    "public_tests_passed": row["public_tests_passed"],
                    "public_passed_hidden_failed": row["public_passed_hidden_failed"],
                    "negative_transfer": row["negative_transfer"],
                    "diagnosis": row["diagnosis"],
                }
            )

    taxonomy_rows = [
        {
            "setting": setting,
            "strategy": strategy,
            "template": template,
            "failures": count,
        }
        for (setting, strategy, template), count in sorted(by_setting_strategy_template.items())
    ]
    return {
        "by_setting_strategy_template": taxonomy_rows,
        "by_strategy": dict(sorted(by_strategy.items())),
        "public_passed_hidden_failed_by_strategy": dict(sorted(public_hidden_by_strategy.items())),
        "negative_transfer_by_strategy": dict(sorted(negative_by_strategy.items())),
        "precondition_only_failures": precondition_only_failures,
    }


def source_hashes(matrix: dict[str, Any]) -> list[dict[str, str | None]]:
    hashes = []
    for run in matrix["run_summaries"]:
        summary = run["source_files"]["summary"]
        trajectories = run["source_files"]["trajectories"]
        hashes.append(
            {
                "run_name": run["run_name"],
                "summary_sha256": summary["sha256"],
                "trajectories_sha256": trajectories["sha256"] if trajectories else None,
            }
        )
    return hashes


def build_evidence_package(matrix: dict[str, Any]) -> dict[str, Any]:
    primary = primary_strategy_table(matrix)
    stability = stability_table(matrix)
    taxonomy = failure_taxonomy(matrix)
    package = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_matrix_generated_at_utc": matrix["generated_at_utc"],
        "primary_strategy_table": primary,
        "stability_table": stability,
        "failure_taxonomy": taxonomy,
        "claim_boundary": CLAIM_BOUNDARY,
        "source_hashes": source_hashes(matrix),
    }
    package["derived_comparisons"] = derived_comparisons(package)
    return package


def derived_comparisons(package: dict[str, Any]) -> dict[str, Any]:
    rows = {
        (row["run_name"], row["strategy"]): row
        for row in package["primary_strategy_table"]
    }
    tree_no = rows[("llm_downstream_hard_v2_tree_25x2", "no_experience")]
    tree_selected = rows[("llm_downstream_hard_v2_tree_25x2", "skilladmit_selected")]
    selected_precondition = rows[
        (
            "llm_downstream_hard_v2_selected_precondition_25",
            "skilladmit_selected_with_precondition_context",
        )
    ]
    all_skills = rows[("llm_downstream_hard_v2_full_25x6", "distilled_skills_all")]
    strict_selected = rows[("llm_downstream_hard_v2_full_25x6", "skilladmit_selected")]
    precondition_only = rows[
        (
            "llm_downstream_hard_v2_precondition_only_25",
            "skilladmit_selected_with_precondition_only",
        )
    ]
    return {
        "tree_aware_selected_success_delta_vs_no_experience": tree_selected["successes"] - tree_no["successes"],
        "tree_aware_selected_token_delta_vs_no_experience": tree_selected["total_tokens"] - tree_no["total_tokens"],
        "selected_precondition_token_delta_vs_tree_selected": (
            selected_precondition["total_tokens"] - tree_selected["total_tokens"]
        ),
        "selected_precondition_token_delta_vs_all_skills": (
            selected_precondition["total_tokens"] - all_skills["total_tokens"]
        ),
        "strict_precondition_only_success_delta_vs_strict_selected": (
            precondition_only["successes"] - strict_selected["successes"]
        ),
    }


def assert_evidence_package(package: dict[str, Any]) -> None:
    if len(package["primary_strategy_table"]) != len(PRIMARY_ROWS):
        raise AssertionError("primary strategy table row count changed")

    primary = {
        (row["run_name"], row["strategy"]): row
        for row in package["primary_strategy_table"]
    }
    expected_successes = {
        ("llm_downstream_hard_v2_full_25x6", "distilled_skills_all"): "25/25",
        ("llm_downstream_hard_v2_full_25x6", "skilladmit_selected"): "23/25",
        ("llm_downstream_hard_v2_tree_25x2", "no_experience"): "23/25",
        ("llm_downstream_hard_v2_tree_25x2", "skilladmit_selected"): "25/25",
        (
            "llm_downstream_hard_v2_selected_precondition_25",
            "skilladmit_selected_with_precondition_context",
        ): "25/25",
        (
            "llm_downstream_hard_v2_precondition_only_25",
            "skilladmit_selected_with_precondition_only",
        ): "24/25",
        ("llm_downstream_hard_v2_forced_bad_25", "forced_bad_artifact"): "0/25",
    }
    for key, expected in expected_successes.items():
        actual = primary[key]["success"]
        if actual != expected:
            raise AssertionError(f"{key}: expected {expected}, got {actual}")

    groups = {row["group"]: row for row in package["stability_table"]}
    if groups["tree_aware_skilladmit_selected"]["success_values"] != [25, 25]:
        raise AssertionError("tree-aware selected stability should be [25, 25]")
    if groups["tree_aware_selected_precondition_context"]["success_values"] != [25, 25]:
        raise AssertionError("selected+precondition stability should be [25, 25]")
    if groups["strict_precondition_only"]["success_values"] != [24, 23]:
        raise AssertionError("strict precondition-only stability should be [24, 23]")

    forced = primary[("llm_downstream_hard_v2_forced_bad_25", "forced_bad_artifact")]
    if forced["public_passed_hidden_failed"] != 25 or forced["negative_transfer"] != 25:
        raise AssertionError("forced_bad_artifact negative-transfer control changed")

    comparisons = package["derived_comparisons"]
    if comparisons["selected_precondition_token_delta_vs_all_skills"] >= 0:
        raise AssertionError("selected+precondition should remain cheaper than all-skills")
    if comparisons["selected_precondition_token_delta_vs_tree_selected"] <= 0:
        raise AssertionError("selected+precondition should not be claimed cheaper than tree-aware selected")

    precondition_failures = package["failure_taxonomy"]["precondition_only_failures"]
    failure_tasks = {(row["run_name"], row["task_id"]) for row in precondition_failures}
    required = {
        ("llm_downstream_hard_v2_precondition_only_25", "hard_v2_py_import_012"),
        ("llm_downstream_hard_v2_replication_precondition_only_25", "hard_v2_py_import_012"),
        ("llm_downstream_hard_v2_replication_precondition_only_25", "hard_v2_py_import_018"),
    }
    if not required.issubset(failure_tasks):
        raise AssertionError("precondition-only failure evidence changed")


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


def render_markdown(package: dict[str, Any]) -> str:
    primary_rows = [
        [
            row["setting"],
            row["display_strategy"],
            row["success"],
            row["negative_transfer"],
            row["public_passed_hidden_failed"],
            row["total_tokens"],
        ]
        for row in package["primary_strategy_table"]
    ]
    stability_rows = [
        [
            row["group"],
            row["success_values"],
            row["token_values"],
            "; ".join(
                f"{run}: {', '.join(tasks) if tasks else 'none'}"
                for run, tasks in row["failure_tasks_by_run"].items()
            ),
        ]
        for row in package["stability_table"]
    ]
    failure_rows = [
        [row["setting"], row["strategy"], row["template"], row["failures"]]
        for row in package["failure_taxonomy"]["by_setting_strategy_template"]
    ]
    supported = "\n".join(f"- {claim}" for claim in package["claim_boundary"]["supported"])
    not_supported = "\n".join(f"- {claim}" for claim in package["claim_boundary"]["not_supported"])
    comparisons = "\n".join(
        f"- `{key}`: {value}"
        for key, value in package["derived_comparisons"].items()
    )
    return "\n\n".join(
        [
            "# Hard v2 Evidence Package",
            f"Generated at: `{package['generated_at_utc']}`",
            "## Primary Strategy Table",
            md_table(
                ["setting", "strategy", "success", "negative_transfer", "public_hidden", "tokens"],
                primary_rows,
            ),
            "## Stability Table",
            md_table(["group", "successes", "tokens", "failure tasks"], stability_rows),
            "## Failure Taxonomy",
            md_table(["setting", "strategy", "template", "failures"], failure_rows),
            "## Derived Comparisons",
            comparisons,
            "## Supported Claims",
            supported,
            "## Unsupported Claims",
            not_supported,
        ]
    ) + "\n"


def tex_escape(value: Any) -> str:
    text = str(value)
    return (
        text.replace("\\", "\\textbackslash{}")
        .replace("_", "\\_")
        .replace("&", "\\&")
        .replace("%", "\\%")
        .replace("#", "\\#")
        .replace("{", "\\{")
        .replace("}", "\\}")
    )


def render_latex(package: dict[str, Any]) -> str:
    lines = [
        "% Auto-generated by scripts/export_hard_v2_evidence_package.py",
        "\\begin{tabular}{llrrrr}",
        "\\hline",
        "Setting & Strategy & Success & Neg. transfer & Public-hidden & Tokens \\\\",
        "\\hline",
    ]
    for row in package["primary_strategy_table"]:
        lines.append(
            " & ".join(
                [
                    tex_escape(row["setting"]),
                    tex_escape(row["display_strategy"]),
                    tex_escape(row["success"]),
                    tex_escape(row["negative_transfer"]),
                    tex_escape(row["public_passed_hidden_failed"]),
                    tex_escape(row["total_tokens"]),
                ]
            )
            + " \\\\"
        )
    lines.extend(["\\hline", "\\end{tabular}", ""])

    lines.extend(
        [
            "\\begin{tabular}{lrrl}",
            "\\hline",
            "Condition & Successes & Tokens & Failure tasks \\\\",
            "\\hline",
        ]
    )
    for row in package["stability_table"]:
        failures = "; ".join(
            f"{run}: {','.join(tasks) if tasks else 'none'}"
            for run, tasks in row["failure_tasks_by_run"].items()
        )
        lines.append(
            " & ".join(
                [
                    tex_escape(row["group"]),
                    tex_escape(row["success_values"]),
                    tex_escape(row["token_values"]),
                    tex_escape(failures),
                ]
            )
            + " \\\\"
        )
    lines.extend(["\\hline", "\\end{tabular}", ""])
    return "\n".join(lines)


def write_outputs(package: dict[str, Any], json_path: Path, md_path: Path, tex_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(package, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(package), encoding="utf-8")
    tex_path.write_text(render_latex(package), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    parser.add_argument("--tex-out", type=Path, default=DEFAULT_TEX)
    parser.add_argument(
        "--assert-current-hard-v2",
        action="store_true",
        help="Assert the current hard_v2 evidence values and paper-claim invariants.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    matrix = build_matrix(RUN_ROOT)
    if args.assert_current_hard_v2:
        assert_current_hard_v2(matrix)
    package = build_evidence_package(matrix)
    if args.assert_current_hard_v2:
        assert_evidence_package(package)
    write_outputs(package, args.json_out, args.md_out, args.tex_out)
    print(f"primary_rows: {len(package['primary_strategy_table'])}")
    print(f"stability_rows: {len(package['stability_table'])}")
    print(f"failure_taxonomy_rows: {len(package['failure_taxonomy']['by_setting_strategy_template'])}")
    print(f"wrote_json: {args.json_out.relative_to(Path.cwd())}")
    print(f"wrote_md: {args.md_out.relative_to(Path.cwd())}")
    print(f"wrote_tex: {args.tex_out.relative_to(Path.cwd())}")


if __name__ == "__main__":
    main()
